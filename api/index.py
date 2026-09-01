"""
SignVision – Vercel Serverless Entry Point
All API routes are handled here via FastAPI + Mangum (ASGI adapter for AWS Lambda / Vercel).

Vercel routes:
  /api/*           → this file
  /health          → this file
  everything else  → public/ static files (handled by vercel.json)
"""

import os, json, re
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from mangum import Mangum

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="SignVision API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load sign mapping ─────────────────────────────────────────────────────────
# On Vercel the file is deployed alongside this module inside the api/ bundle.
# We ship sign_mapping.json into api/ so it's always co-located.
_HERE = os.path.dirname(os.path.abspath(__file__))
_MAP_FILE = os.path.join(_HERE, "sign_mapping.json")

with open(_MAP_FILE, "r") as f:
    SIGN_MAP: dict = json.load(f)

WORD_SIGNS  = {k.lower(): v for k, v in SIGN_MAP.get("words",     {}).items()}
ALPHA_SIGNS = {k.upper(): v for k, v in SIGN_MAP.get("alphabets", {}).items()}
NUM_SIGNS   = {k:          v for k, v in SIGN_MAP.get("numbers",   {}).items()}

# ── Translation logic ─────────────────────────────────────────────────────────
def text_to_signs(text: str) -> list[dict]:
    text  = text.strip()
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    results = []
    i = 0
    while i < len(words):
        # Two-word phrase first (e.g. "thank you")
        if i + 1 < len(words):
            phrase = words[i] + " " + words[i + 1]
            if phrase in WORD_SIGNS:
                results.append({"type": "word",  "label": phrase.upper(), "url": WORD_SIGNS[phrase]})
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
                    results.append({"type": "number",   "label": ch,         "url": NUM_SIGNS[ch]})
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
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Serverless note: pydub/ffmpeg are not available on Vercel.
    The frontend uses the browser's Web Speech API directly for speech recognition,
    so this endpoint is a fallback only. It attempts Google Speech Recognition
    on uploaded WAV audio.
    """
    import tempfile
    try:
        import speech_recognition as sr
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Speech recognition library not available in this deployment. Use the browser's built-in speech input instead."
        )

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file.")

    suffix = ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
        try:
            transcript = recognizer.recognize_google(audio_data, language="en-IN")
        except sr.UnknownValueError:
            raise HTTPException(status_code=422, detail="Speech not recognized. Please speak clearly.")
        except sr.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Speech recognition service error: {e}")
        signs = text_to_signs(transcript)
        return {
            "transcript":  transcript,
            "sign_count":  len([s for s in signs if s["type"] != "space"]),
            "signs":       signs,
        }
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

# ── Mangum handler (Vercel / AWS Lambda ASGI adapter) ────────────────────────
handler = Mangum(app, lifespan="off")
