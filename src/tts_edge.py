# src/tts_edge.py
import asyncio
import edge_tts
import uuid
import os
import subprocess
import time
import random

# ---------------- CONFIG ---------------- #

RATE = "+0%"
PITCH = "+0Hz"

ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# 🎙️ Male voice pools (Edge-TTS)
VOICE_POOLS = {
    "motivational": [
        "en-IN-PrabhatNeural",
        "en-US-GuyNeural",
    ],
    "hype": [
        "en-US-GuyNeural",
        "en-GB-RyanNeural",
    ],
    "calm": [
        "en-US-DavisNeural",
        "en-GB-RyanNeural",
    ],
    "dark": [
        "en-US-DavisNeural",
    ],
    "neutral": [
        "en-IN-PrabhatNeural",
        "en-US-GuyNeural",
        "en-US-DavisNeural",
    ],
}

# Simple keyword-based mood detection (FAST & SAFE)
MOOD_KEYWORDS = {
    "motivational": ["success", "discipline", "habits", "growth", "mindset", "goals"],
    "hype": ["win", "dominate", "beast", "champion", "grind"],
    "calm": ["calm", "focus", "peace", "clarity", "mindfulness"],
    "dark": ["fear", "dopamine", "addiction", "mistake", "dark"],
}


# ---------------- MOOD DETECTION ---------------- #

def detect_mood(text: str) -> str:
    t = text.lower()
    for mood, words in MOOD_KEYWORDS.items():
        if any(w in t for w in words):
            return mood
    return "neutral"


# ---------------- TEXT CHUNKING ---------------- #

def split_text(text: str, max_chars: int = 800):
    """
    Split long text into safe chunks for Edge-TTS
    """
    sentences = text.replace("\n", " ").split(". ")
    chunks = []
    current = ""

    for s in sentences:
        s = s.strip()
        if not s:
            continue

        if len(current) + len(s) < max_chars:
            current += s + ". "
        else:
            chunks.append(current.strip())
            current = s + ". "

    if current.strip():
        chunks.append(current.strip())

    return chunks


# ---------------- EDGE TTS CORE ---------------- #

async def _tts_chunk(text: str, out_path: str, voice: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=RATE,
        pitch=PITCH,
    )
    await communicate.save(out_path)


# ---------------- PUBLIC API ---------------- #

def text_to_speech(text: str) -> str:
    """
    Robust Edge-TTS:
    - Detects mood
    - Selects ONE male voice per video
    - Splits text into chunks
    - Generates audio per chunk
    - Merges using ffmpeg
    """

    if not text.strip():
        raise RuntimeError("TTS received empty text")

    mood = detect_mood(text)
    voice_pool = VOICE_POOLS.get(mood, VOICE_POOLS["neutral"])
    voice = random.choice(voice_pool)

    print(f"🎙️ TTS mood: {mood}, voice selected: {voice}")

    chunks = split_text(text)
    if not chunks:
        raise RuntimeError("No valid TTS chunks generated")

    temp_files = []

    # 🔊 Generate audio per chunk
    for i, chunk in enumerate(chunks):
        out = f"{ASSETS_DIR}/tmp_{i}_{uuid.uuid4().hex}.wav"

        try:
            asyncio.run(_tts_chunk(chunk, out, voice))
        except Exception as e:
            raise RuntimeError(f"Edge-TTS failed on chunk {i}: {e}")

        if not os.path.exists(out) or os.path.getsize(out) < 1000:
            raise RuntimeError("Edge-TTS produced empty audio chunk")

        temp_files.append(out)

        # small delay avoids throttling
        time.sleep(0.2)

    # 🧩 Create concat list
    list_file = f"{ASSETS_DIR}/tts_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in temp_files:
            f.write(f"file '{os.path.abspath(p)}'\n")

    final_out = f"{ASSETS_DIR}/voice_{uuid.uuid4().hex}.wav"

    # 🎧 Merge chunks
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            final_out
        ],
        check=True
    )

    # 🧹 Cleanup
    for f in temp_files:
        try:
            os.remove(f)
        except OSError:
            pass

    try:
        os.remove(list_file)
    except OSError:
        pass

    if not os.path.exists(final_out) or os.path.getsize(final_out) < 2000:
        raise RuntimeError("Final Edge-TTS audio invalid")

    return final_out
