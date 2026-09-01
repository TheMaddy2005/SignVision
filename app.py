"""
SignVision – Vercel Entrypoint
Vercel detects `app` (FastAPI instance) in app.py automatically.
No Mangum, no BaseHTTPRequestHandler, no builds config needed.
"""
import os, json, re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="SignVision API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Sign mapping ──────────────────────────────────────────────────────────────
# Vercel CWD is the project root, so path is relative to root
_MAP = os.path.join(os.path.dirname(__file__), "api", "sign_mapping.json")
with open(_MAP, "r") as f:
    SIGN_MAP = json.load(f)

WORD_SIGNS  = {k.lower(): v for k, v in SIGN_MAP.get("words",     {}).items()}
ALPHA_SIGNS = {k.upper(): v for k, v in SIGN_MAP.get("alphabets", {}).items()}
NUM_SIGNS   = {k:          v for k, v in SIGN_MAP.get("numbers",   {}).items()}

# ── Translation ───────────────────────────────────────────────────────────────
def text_to_signs(text: str) -> list:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    results = []
    i = 0
    while i < len(words):
        if i + 1 < len(words):
            phrase = words[i] + " " + words[i + 1]
            if phrase in WORD_SIGNS:
                results.append({"type": "word", "label": phrase.upper(), "url": WORD_SIGNS[phrase]})
                i += 2
                continue
        word = words[i]
        if word in WORD_SIGNS:
            results.append({"type": "word", "label": word.upper(), "url": WORD_SIGNS[word]})
        else:
            for ch in word:
                if ch.upper() in ALPHA_SIGNS:
                    results.append({"type": "alphabet", "label": ch.upper(), "url": ALPHA_SIGNS[ch.upper()]})
                elif ch in NUM_SIGNS:
                    results.append({"type": "number", "label": ch, "url": NUM_SIGNS[ch]})
            if i < len(words) - 1:
                results.append({"type": "space", "label": " ", "url": None})
        i += 1
    return results

# ── Routes ────────────────────────────────────────────────────────────────────
class TranslateRequest(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "SignVision"}

@app.get("/api/mapping")
def get_mapping():
    return JSONResponse(SIGN_MAP)

@app.post("/api/translate")
def translate(req: TranslateRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if len(req.text) > 500:
        raise HTTPException(status_code=400, detail="Text too long (max 500 chars).")
    signs = text_to_signs(req.text)
    return {
        "input":      req.text,
        "sign_count": len([s for s in signs if s["type"] != "space"]),
        "signs":      signs,
    }

@app.post("/api/speech-to-text")
def speech_to_text():
    raise HTTPException(
        status_code=501,
        detail="Backend speech recognition is not available on Vercel. "
               "Use your browser's built-in Web Speech API instead."
    )

# ── Serve static files (SVG signs + frontend) ────────────────────────────────
_PUBLIC = os.path.join(os.path.dirname(__file__), "public")
if os.path.isdir(_PUBLIC):
    app.mount("/signs", StaticFiles(directory=os.path.join(_PUBLIC, "signs")), name="signs")

@app.get("/{full_path:path}", include_in_schema=False)
def spa(full_path: str):
    index = os.path.join(_PUBLIC, "index.html")
    if os.path.isfile(index):
        return FileResponse(index)
    return JSONResponse({"message": "SignVision API is running."})
