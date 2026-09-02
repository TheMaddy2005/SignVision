"""
SignVision – Vercel Entrypoint (app.py)
Vercel auto-detects `app` (FastAPI ASGI instance).
Handles /api/* and /health only — no static file serving.
"""
import os, json, re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="SignVision API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Sign mapping — try multiple paths for Vercel compatibility ────────────────
def _load_map() -> dict:
    # Vercel CWD is /var/task (repo root). Try all possible locations.
    candidates = [
        os.path.join(os.getcwd(), "api", "sign_mapping.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "api", "sign_mapping.json"),
        os.path.join(os.getcwd(), "sign_mapping.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "sign_mapping.json"),
        "/var/task/api/sign_mapping.json",
        "/var/task/sign_mapping.json",
    ]
    for path in candidates:
        if os.path.isfile(path):
            with open(path, "r") as f:
                return json.load(f)
    # Fallback: return empty map rather than crash
    return {"alphabets": {}, "numbers": {}, "words": {}}

SIGN_MAP    = _load_map()
WORD_SIGNS  = {k.lower(): v for k, v in SIGN_MAP.get("words",     {}).items()}
ALPHA_SIGNS = {k.upper(): v for k, v in SIGN_MAP.get("alphabets", {}).items()}
NUM_SIGNS   = {k:          v for k, v in SIGN_MAP.get("numbers",   {}).items()}

# ── Translation logic ─────────────────────────────────────────────────────────
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
    """Health check — also exposes debug info to diagnose path issues."""
    cwd = os.getcwd()
    file_dir = os.path.dirname(os.path.abspath(__file__))
    map_loaded = bool(SIGN_MAP.get("alphabets"))
    # List files in cwd for debugging
    try:
        cwd_files = os.listdir(cwd)
    except Exception:
        cwd_files = []
    return {
        "status": "ok",
        "service": "SignVision",
        "sign_map_loaded": map_loaded,
        "sign_count": len(SIGN_MAP.get("alphabets", {})),
        "cwd": cwd,
        "file_dir": file_dir,
        "cwd_files": cwd_files[:20],
    }

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
