"""
SignVision – Vercel Python Serverless Handler
Pure stdlib + fastapi only. No Mangum. No pydub. No uvicorn.
Vercel calls handler(request, response) directly.
"""
import json
import os
import re
from http.server import BaseHTTPRequestHandler

# ── Load sign mapping ─────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "sign_mapping.json"), "r") as f:
    SIGN_MAP = json.load(f)

WORD_SIGNS  = {k.lower(): v for k, v in SIGN_MAP.get("words",     {}).items()}
ALPHA_SIGNS = {k.upper(): v for k, v in SIGN_MAP.get("alphabets", {}).items()}
NUM_SIGNS   = {k:          v for k, v in SIGN_MAP.get("numbers",   {}).items()}

# ── Translation logic ─────────────────────────────────────────────────────────
def text_to_signs(text):
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

# ── Vercel native handler ─────────────────────────────────────────────────────
class handler(BaseHTTPRequestHandler):

    def _send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")

        if path in ("", "/health"):
            self._send_json(200, {"status": "ok", "service": "SignVision"})

        elif path in ("/api/mapping", "/mapping"):
            self._send_json(200, SIGN_MAP)

        else:
            self._send_json(404, {"error": "Not found", "path": path})

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")

        if path in ("/api/translate", "/translate"):
            try:
                body = json.loads(self._read_body())
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_json(400, {"detail": "Invalid JSON body."})
                return

            text = body.get("text", "")
            if not text or not text.strip():
                self._send_json(400, {"detail": "Text cannot be empty."})
                return
            if len(text) > 500:
                self._send_json(400, {"detail": "Text too long (max 500 chars)."})
                return

            signs = text_to_signs(text)
            self._send_json(200, {
                "input":      text,
                "sign_count": len([s for s in signs if s["type"] != "space"]),
                "signs":      signs,
            })

        elif path in ("/api/speech-to-text", "/speech-to-text"):
            # Speech-to-text via backend is not available on Vercel serverless.
            # The frontend uses the browser's Web Speech API directly — this
            # endpoint exists only to return a clear message.
            self._send_json(501, {
                "detail": "Backend speech recognition is not available on Vercel. "
                          "The app uses your browser's built-in Web Speech API instead — "
                          "no backend call is needed."
            })

        else:
            self._send_json(404, {"error": "Not found", "path": path})
