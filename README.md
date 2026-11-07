# 🤟 SignVision – AI-Based Sign Language Translator

> Improving accessibility by converting text and speech into **Indian Sign Language (ISL)** visual representations in real time.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-JavaScript-E34F26?style=flat&logo=html5&logoColor=white)
![ISL](https://img.shields.io/badge/Indian%20Sign%20Language-ISL-e94560?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 🌐 Live Demo

**https://sign-vision-tau.vercel.app** - hosted free on Vercel (FastAPI serverless functions + static frontend, deployed from this repo's `main` branch).

---

## 📌 Project Overview

SignVision is a full-stack web application that bridges the communication gap for the hearing-impaired community. It accepts **text or spoken voice input** and translates it into a sequence of **Indian Sign Language (ISL)** sign cards displayed visually in the browser.

The translation pipeline:
```
User types text  ──┐
                   ├──► FastAPI backend ──► ISL sign cards on screen
User speaks aloud ─┘  (speech → text → signs)
```

> **Note:** SignVision is a *text/speech → sign* translator. It does not use a webcam or perform sign recognition from video.

---

## ✨ Features

| Feature | Description |
|---|---|
| ✍️ **Text Input** | Type any word, sentence, or phrase and get the ISL sign sequence instantly |
| 🎤 **Speech Input** | Speak in Indian English — real-time transcription via Web Speech API, then translated to ISL |
| 🖐️ **Fingerspell Live** | Type any word and see each letter signed character-by-character in real time |
| ▶️ **Animated Playback** | Step through signs one at a time at Slow / Normal / Fast speed |
| 💬 **Quick Phrases** | One-click common ISL phrases (Namaste, Thank you, I love you, etc.) |
| 📊 **Stats Bar** | Live count of alphabets (26), ISL words (24), and session translation total |
| 🔊 **Waveform Visualiser** | Animated audio waveform displayed during speech recording |
| 🌐 **Single Link** | Entire app (frontend + API) served from `http://localhost:8000` |

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Speech Recognition:** Browser Web Speech API (primary) + SpeechRecognition library (fallback)
- **Sign Assets:** 60 SVG sign cards generated programmatically (26 alphabets, 10 numbers, 24 ISL words)
- **API:** RESTful JSON endpoints

---

## 📁 Project Structure

```
SignVision/
├── backend/
│   ├── main.py                  # FastAPI app — API routes + static file serving
│   ├── sign_mapping.json        # Maps letters/words to SVG file paths
│   └── static/
│       ├── index.html           # Full single-page frontend
│       └── signs/
│           ├── alphabets/       # A.svg … Z.svg
│           ├── numbers/         # 0.svg … 9.svg
│           └── words/           # hello.svg, namaste.svg, thank_you.svg …
├── generate_signs.py            # Script to regenerate all SVG sign assets
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or later
- pip

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/SignVision.git
cd SignVision
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Regenerate SVG sign assets

The SVG files are already committed, so this step is only needed if you modify `generate_signs.py`:

```bash
python generate_signs.py
```

### 4. Run the server

```bash
python backend/main.py
```

### 5. Open in browser

```
http://localhost:8000
```

API documentation (Swagger UI):

```
http://localhost:8000/docs
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health check |
| `GET` | `/api/mapping` | Full sign mapping JSON (all 60 signs) |
| `POST` | `/api/translate` | Translate text to ISL sign sequence |
| `POST` | `/api/speech-to-text` | Upload audio → transcript + ISL signs |
| `GET` | `/static/signs/**` | Serve SVG sign assets |

### Example — Translate Text

**Request:**
```bash
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "namaste"}'
```

**Response:**
```json
{
  "input": "namaste",
  "sign_count": 1,
  "signs": [
    {
      "type": "word",
      "label": "NAMASTE",
      "url": "/static/signs/words/namaste.svg"
    }
  ]
}
```

---

## 🧠 Translation Logic

The `text_to_signs()` function processes input using a priority cascade:

1. **Two-word phrase match** — checks if consecutive words form a known ISL phrase (e.g. "thank you")
2. **Single word match** — checks if the word has a dedicated ISL word sign (e.g. "hello", "india")
3. **Fingerspelling** — unknown words are spelled out letter by letter using alphabet signs

---

## 🗂️ ISL Sign Vocabulary

**Words (24):**
hello, thank you, sorry, please, yes, no, help, water, food, love, good, bad, home, school, work, name, india, namaste, come, go, stop, welcome, friend, family

**Alphabets:** A – Z (26 signs)

**Numbers:** 0 – 9 (10 signs)

---

## 🌐 Browser Compatibility

| Browser | Text Input | Speech Input |
|---|---|---|
| Chrome | ✅ | ✅ |
| Edge | ✅ | ✅ |
| Firefox | ✅ | ❌ (no Web Speech API) |
| Safari | ✅ | ⚠️ Partial |

> Speech input uses the browser's built-in Web Speech API. An internet connection is required for Google's speech recognition service. Offline fallback requires `pocketsphinx` installed separately.

---

## 🤝 Contributing

Contributions are welcome — especially:
- Additional ISL word signs
- Improved SVG hand shape illustrations
- Offline speech recognition support
- Animated GIF signs

Please open an issue before submitting a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Built with ♥ as part of an AI accessibility project.

**SignVision** — Making communication barrier-free through technology.
