# GenAI Shorts Generator 🚀

An end-to-end **AI-powered YouTube Shorts generation pipeline** that converts an idea into a fully rendered short video with:
- AI-generated script
- Natural voice narration
- Word-level captions
- Relevant background video clips
- Background music
- **Guaranteed Call-To-Action (CTA)**

This project is built with a **production-first mindset**, focusing on reliability, fallback mechanisms, and clean system design rather than prompt-only experimentation.

---

## 🎯 Project Goal
- Automatically generate high-quality YouTube Shorts
- Ensure consistent engagement elements (CTAs)
- Build a robust, fault-tolerant GenAI media pipeline
- Demonstrate real-world Applied GenAI engineering skills

---

## 🧠 System Design Philosophy
- **AI + deterministic fallbacks** (never rely fully on LLMs)
- Clear separation of responsibilities
- Defensive programming for edge cases
- Duration-aware audio/video handling
- Modular, extensible pipeline structure

This mirrors how **real GenAI content systems** are built in production.

---

## ⚙️ Pipeline Overview

1. **Idea Input**
   - User provides a topic or idea

2. **Script Generation (Body Only)**
   - LLM generates a conversational script (130–150 words)
   - No CTA included in body
   - Hook regeneration and sentence rewriting applied
   - Strong sanitization to remove meta or unsafe text

3. **Narration (TTS)**
   - Script body converted to speech using Edge TTS
   - Duration validated for YouTube Shorts constraints

4. **CTA Generation (Guaranteed)**
   - LLM attempts to generate a short spoken CTA
   - If missing, invalid, or too long:
     - A **hardcoded CTA fallback pool** is used
   - CTA is only attached if total duration ≤ 59 seconds
   - Ensures consistent engagement across all videos

5. **Audio Merge**
   - Script body + CTA audio concatenated safely
   - Final narration duration capped at 59 seconds

6. **Captions**
   - Word-level subtitles generated via Whisper
   - Converted from SRT to ASS for styling

7. **Background Video**
   - Relevant clips fetched based on idea
   - Clips reused intelligently if insufficient count
   - Concatenated to match narration duration

8. **Background Music**
   - Music fetched with retries and guaranteed fallback
   - Mixed during final render

9. **Final Render**
   - Background video + narration + music + captions
   - Exported as a ready-to-upload YouTube Short

---

## ✅ Key Engineering Features

- **Guaranteed CTA logic**
  - LLM-generated when possible
  - Deterministic fallback when not
- Duration-safe pipeline (≤ 59s)
- Strong text sanitization
- GPU → CPU fallback handling (for LLM/TTS stability)
- No orphan temp files
- Modular, readable codebase

---

## 🛠️ Tech Stack

- Python
- Large Language Models (via local/remote inference)
- Edge TTS
- Whisper (captions)
- FFmpeg / FFprobe
- Pexels (background video)
- Pixabay (background music)
- Git & GitHub (versioned milestones)

---

## 🏷️ Versioning & Milestones

This project uses **semantic Git tags** to mark stable milestones.

### Current Stable Tag
- **`v0.3.0-cta-fallback`**
  - Guaranteed CTA using LLM + deterministic fallback
  - Production-safe duration handling
  - Fully reliable Shorts generation

---

## 📂 Project Structure (High-Level)

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
│   ├── bg_intent.py              # Background video intent finder 
│   ├── bg_music_fetcher.py       # Background music downloader
│   ├── bg_query.py               # Niche-based background search
│   ├── text_utils.py             # Script cleanup & TTS safety
│   ├── video_utils.py            # utility fuction for video
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

## 🚀 How to Run

python main.py "Your video idea here"

---

## Output
- outputs/final_short.mp4

---

# Credits
- By Raghvendra Singh

---

## 🧠 Mentor Note (Important)

This README now:
- Reads like a **real product**
- Shows **engineering maturity**
- Clearly explains **why design choices exist**
- Supports your **Applied GenAI positioning**

You’ve crossed from:
> *“learning GenAI”*  
to  
> **“building GenAI systems”**

If you want next:
- GitHub Releases page content
- Changelog.md
- Architecture diagram
- Or prep interview explanations from this project

Just tell me 👊
