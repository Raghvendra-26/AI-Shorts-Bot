# 🎬 AI Shorts Generator

An end-to-end automated system that creates **YouTube Shorts / Instagram Reels** from a single idea.

This project takes an input idea, generates a high-quality spoken script using an LLM, scores and improves the script, generates natural voice-over, creates captions, fetches background video and music, and renders a final vertical short video — fully locally.

Built to be **fault-tolerant**, **rollback-safe**, and **production-oriented**.

---

## ✨ Key Features

### 🧠 Intelligent Script Generation
- Multi-prompt script generation
- Automatic script quality scoring
- Best script selection
- Hook strength optimization
- Sentence length normalization
- CTA enforcement

### 🎙️ Voice Generation
- Uses **Edge-TTS**
- Stable and natural narration
- Audio duration capped for Shorts safety

### 📝 Captions
- Word-level captions via **Whisper**
- SRT → ASS conversion (Windows-safe)
- Captions synchronized with narration

### 🎥 Background Video
- Automatically fetched based on idea
- Seamlessly looped to match audio length
- Vertical (9:16) optimized

### 🎵 Background Music
- Optional background music fetch
- Automatic fallback to silence if unavailable

### 🎬 Rendering
- FFmpeg-based rendering
- Correct audio mixing (voice + music)
- Output duration locked to narration length

### 🧯 Reliability & Safety
- Handles Ollama / CUDA crashes gracefully
- Fallbacks at every stage
- Structured logging for debugging
- Safe rollbacks using Git tags

---