
# GenAI Shorts Generator 🚀

A **production-grade AI system** that generates YouTube Shorts end‑to‑end **and learns from real YouTube analytics**.

This project focuses on **engineering reliability**, not prompt demos.

---

## 🎯 What This Project Does

- Generates complete YouTube Shorts automatically
- Guarantees CTA inclusion with deterministic fallbacks
- Handles audio, video, captions, and music safely (≤ 59s)
- Fetches **real post‑publish YouTube analytics**
- Merges performance data for future decision‑making

---

## 🧠 Design Principles

- AI + deterministic fallbacks (no blind trust in LLMs)
- Modular, reusable components
- Defensive programming for failures
- Clear separation: **generation vs evaluation**
- Built like a real production system

---

## 🏗️ Architecture Diagram

```text
                ┌────────────────────┐
                │   User Idea Input   │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │   Script Generator  │
                │ (LLM + sanitizers)  │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │   Voice Narration   │
                │      (Edge TTS)     │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │   CTA Generator     │
                │ (LLM + fallback)    │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │  Captions (Whisper) │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │ Background Media    │
                │ (Video + Music)     │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │   Final Render      │
                │ (FFmpeg Pipeline)   │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │ YouTube Upload      │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │ YouTube Analytics   │
                │ (Views, Retention)  │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │ Analytics Merger    │
                │ (Retention + Eng.)  │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │ Future AI Decisions │
                │ (Hooks, Topics)     │
                └────────────────────┘
```

---

## ⚙️ Pipeline Summary

1. Script generation (body only, sanitized)
2. Voice narration (duration validated)
3. Guaranteed CTA attachment
4. Audio merge (≤ 59 seconds)
5. Captions via Whisper
6. Background video & music fetch
7. Final Shorts render
8. Post‑publish analytics collection
9. Analytics merge for learning

---

## 📊 Analytics Integration

Collected per video:
- Views
- Average View Duration
- Minutes Watched
- Likes
- Comments
- Video title & metadata

Analytics sources:
- **YouTube Analytics API** (retention, views)
- **YouTube Data API** (engagement)

Designed for:
- Ranking content
- Hook evaluation
- Topic performance analysis
- Future AI feedback loops

---

## 🛠️ Tech Stack

**Generation**
- Python
- Ollama (local LLMs)
- Edge TTS
- Whisper
- FFmpeg

**Media Sources**
- Pexels
- Pixabay

**Analytics**
- YouTube Analytics API
- YouTube Data API v3

---

## 📂 Project Structure

```text
ai-shorts-bot/
├── src/                 # Generation pipeline
├── yt_analytics/        # YouTube analytics system
├── assets/              # Static assets
├── outputs/             # Generated videos (ignored)
├── logs/                # Runtime logs
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Run

```bash
python main.py "Your video idea here"
```

Output:
```
outputs/final_short.mp4
```

---

## 👤 Author

**Raghvendra Singh**

---

## 🧠 Why This Project Matters

This is not a demo.

It demonstrates:
- Real GenAI system design
- Media pipeline engineering
- API‑constraint handling
- Feedback‑driven architecture

Built to **scale, learn, and evolve**.
