"""
SignVision – FastAPI Backend
Endpoints:
  GET  /                        → serves React SPA (index.html)
  GET  /static/**               → serves static assets (SVGs, JS, CSS)
  POST /api/translate           → text → ISL sign sequence
  POST /api/speech-to-text      → audio (webm/wav) → transcript → ISL signs
  GET  /api/mapping             → full sign mapping JSON
  GET  /health                  → health check
"""

import os, json, re
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="SignVision API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR   = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
MAPPING_FILE = os.path.join(BASE_DIR, "sign_mapping.json")

# Load sign mapping once at startup
with open(MAPPING_FILE, "r") as f:
    SIGN_MAP: dict = json.load(f)

# Flatten word keys to lowercase for fast lookup
WORD_SIGNS   = {k.lower(): v for k, v in SIGN_MAP.get("words", {}).items()}
ALPHA_SIGNS  = {k.upper(): v for k, v in SIGN_MAP.get("alphabets", {}).items()}
NUM_SIGNS    = {k: v for k, v in SIGN_MAP.get("numbers", {}).items()}

# ── Helpers ───────────────────────────────────────────────────────────────────

def text_to_signs(text: str) -> list[dict]:
    """
    Converts a plain-text string into an ordered list of sign objects.
    Strategy:
      1. Try to match known multi-word phrases / single words first.
      2. Fall back to letter-by-letter fingerspelling.
    """
    text = text.strip()
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    results = []

    i = 0
    while i < len(words):
        # Check two-word phrase first (e.g. "thank you")
        if i + 1 < len(words):
            phrase = words[i] + " " + words[i + 1]
            if phrase in WORD_SIGNS:
                results.append({
                    "type": "word",
                    "label": phrase.upper(),
                    "url": WORD_SIGNS[phrase],
                })
                i += 2
                continue

        word = words[i]
        # Known word sign?
        if word in WORD_SIGNS:
            results.append({
                "type": "word",
                "label": word.upper(),
                "url": WORD_SIGNS[word],
            })
        else:
            # Fingerspell character by character
            for ch in word:
                if ch.upper() in ALPHA_SIGNS:
                    results.append({
                        "type": "alphabet",
                        "label": ch.upper(),
                        "url": ALPHA_SIGNS[ch.upper()],
                    })
                elif ch in NUM_SIGNS:
                    results.append({
                        "type": "number",
                        "label": ch,
                        "url": NUM_SIGNS[ch],
                    })
            # Add a space marker between words
            if i < len(words) - 1:
                results.append({"type": "space", "label": " ", "url": None})
        i += 1

    return results


# ── API Routes ────────────────────────────────────────────────────────────────

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
        "input": req.text,
        "sign_count": len([s for s in signs if s["type"] != "space"]),
        "signs": signs,
    }

@app.post("/api/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Receives audio blob from browser (WebM/WAV), transcribes it using
    SpeechRecognition + pocketsphinx (offline) or Google Web Speech (online).
    Falls back gracefully with a clear error message.
    """
    import tempfile, io

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file.")

    # Save to temp file
    suffix = ".webm" if "webm" in (audio.content_type or "") else ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()

        # Convert webm → wav using pydub if needed
        if suffix == ".webm":
            try:
                from pydub import AudioSegment
                wav_path = tmp_path.replace(".webm", ".wav")
                AudioSegment.from_file(tmp_path, format="webm").export(wav_path, format="wav")
                tmp_path = wav_path
            except Exception:
                raise HTTPException(
                    status_code=422,
                    detail="Audio conversion failed. Ensure ffmpeg is installed."
                )

        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)

        # Try Google (online), fallback to Sphinx (offline)
        transcript = None
        try:
            transcript = recognizer.recognize_google(audio_data, language="en-IN")
        except sr.UnknownValueError:
            raise HTTPException(status_code=422, detail="Speech not recognized. Please speak clearly.")
        except sr.RequestError:
            try:
                transcript = recognizer.recognize_sphinx(audio_data)
            except Exception:
                raise HTTPException(
                    status_code=503,
                    detail="Speech recognition unavailable (no internet + pocketsphinx not installed)."
                )

        signs = text_to_signs(transcript)
        return {
            "transcript": transcript,
            "sign_count": len([s for s in signs if s["type"] != "space"]),
            "signs": signs,
        }

    finally:
        for p in [tmp_path]:
            try:
                os.unlink(p)
            except Exception:
                pass


# ── Serve frontend (SPA) ─────────────────────────────────────────────────────
if os.path.isdir(STATIC_DIR):
    # Mount /static for SVG signs and assets
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Catch-all SPA route — must be AFTER API routes and static mount
@app.get("/{full_path:path}", include_in_schema=False)
def spa(full_path: str):
    index = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index):
        return FileResponse(index)
    return JSONResponse({"message": "SignVision API running. Frontend not built yet."})


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("=" * 52)
    print("  SIGNVISION – AI Sign Language Translator")
    print("  http://localhost:8000")
    print("  API docs: http://localhost:8000/docs")
    print("=" * 52)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True,
                app_dir=BASE_DIR)
