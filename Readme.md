# 🎬 AI Shorts Bot

An end-to-end **automated YouTube Shorts / Instagram Reels generator** powered by:
- Local LLMs (Ollama)
- Edge-TTS (voice)
- Whisper (captions)
- FFmpeg (video rendering)

This project converts a **single idea** into a **fully rendered vertical short video** with:
- High-quality spoken script
- AI voiceover
- Auto captions
- Background video
- Background music
- Shorts-safe duration control

---

## 🚀 Features

- 🧠 **Local LLM scripting** (Ollama – GPU/CPU fallback)
- 🏆 **Multi-script generation & scoring**
- 🎯 **Semantic hook scoring** (no keyword hacks)
- 🔁 **Safe hook regeneration** (minimal LLM calls)
- ✍️ **Sentence length optimization**
- 🎙️ **Edge-TTS voice generation**
- 📝 **Word-level captions using Whisper**
- 🎥 **Automatic background video selection**
- 🎵 **Optional background music**
- ⏱️ **Hard duration cap (Shorts-safe)**
- 🧱 **Production-grade error handling**
- 📜 **Structured logging**

---

## 📂 Project Structure

```text
ai-shorts-bot/
│
├── src/
│   ├── pipeline.py              # Main orchestration pipeline
│   ├── ollama_llm.py             # Local LLM interface (GPU → CPU fallback)
│   ├── script_quality.py         # Script scoring & optimization logic
│   ├── tts_edge.py               # Edge-TTS voice generation
│   ├── captions_whisper.py       # Word-level caption generation
│   ├── render.py                 # FFmpeg video rendering
│   ├── bg_fetcher.py             # Background video downloader
│   ├── bg_music_fetcher.py       # Background music downloader
│   ├── bg_query.py               # Niche-based background search
│   ├── text_utils.py             # Script cleanup & TTS safety
│   └── utils/
│       └── srt_to_ass.py         # Caption format conversion
│
├── assets/
│   └── silence.mp3               # Fallback silent audio
│
├── outputs/
│   └── final_short.mp4            # Generated video (runtime)
│
├── logs/
│   └── app.log                   # Runtime logs
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Python dependencies
- pip install -r requirements.txt

---

## Ollama models
- ollama pull llama3.2:3b
- ollama pull llama3.1:8b

---

## How to run 
- python -m src.pipeline "your idea"

---

## Output
- outputs/final_short.mp4


---

# Credits
- By Raghvendra Singh
