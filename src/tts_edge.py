# src/tts_edge.py
import asyncio
import edge_tts
import uuid
import os
import subprocess
import random
import time
from typing import Optional

# ---------------- CONFIG ---------------- #

RATE = "+0%"
PITCH = "+0Hz"

ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# 🎙️ Male voice pools (English-focused; Hindi handled via override)
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

MOOD_KEYWORDS = {
    "motivational": ["success", "discipline", "habits", "growth", "mindset", "goals"],
    "hype": ["win", "dominate", "beast", "champion", "grind"],
    "calm": ["calm", "focus", "peace", "clarity", "mindfulness"],
    "dark": ["fear", "dopamine", "addiction", "mistake", "dark"],
}

# ---------------- HELPERS ---------------- #

def detect_mood(text: str) -> str:
    t = text.lower()
    for mood, words in MOOD_KEYWORDS.items():
        if any(w in t for w in words):
            return mood
    return "neutral"


def split_text(text: str, max_chars: int = 800):
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


async def _tts_chunk(text: str, out_path: str, voice: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=RATE,
        pitch=PITCH,
    )
    await communicate.save(out_path)


# ---------------- PUBLIC API ---------------- #

def text_to_speech(
    text: str,
    voice: Optional[str] = None
) -> str:
    """
    Production-safe Edge-TTS

    Supports:
    - Optional explicit voice override (for language switching)
    - Mood-based voice selection
    - Voice rotation on failure
    - Padding retry
    - Silent failure detection
    - Final semantic simplification fallback
    """

    text = text.strip()

    # 🔒 Edge hard-fails on tiny input
    if len(text.split()) < 4:
        text = f"{text}. Stay tuned."

    text = (
        text.replace("—", " ")
            .replace("–", " ")
            .replace("…", ".")
            .replace("\n", " ")
    )

    chunks = split_text(text)
    if not chunks:
        raise RuntimeError("TTS received empty text")

    # ---------------- VOICE SELECTION ---------------- #

    if voice:
        # External override (language-aware)
        voices = [voice]
    else:
        # Existing intelligent mood-based logic
        mood = detect_mood(text)
        voices = VOICE_POOLS.get(mood, VOICE_POOLS["neutral"]).copy()
        random.shuffle(voices)

    temp_files = []

    for i, chunk in enumerate(chunks):
        success = False

        # ---------------- NORMAL VOICE ROTATION ---------------- #
        for v in voices:
            out = f"assets/tmp_{i}_{uuid.uuid4().hex}.wav"

            try:
                asyncio.run(_tts_chunk(chunk, out, v))
            except Exception:
                padded = f"Listen carefully. {chunk}"
                try:
                    asyncio.run(_tts_chunk(padded, out, v))
                except Exception:
                    continue

            if os.path.exists(out) and os.path.getsize(out) > 1500:
                temp_files.append(out)
                success = True
                break

            try:
                os.remove(out)
            except OSError:
                pass

        # ---------------- FINAL FAILSAFE ---------------- #
        if not success:
            simplified = (
                "Here is something interesting. "
                + chunk.replace(",", ".").replace(" and ", ". ")
            )

            fallback_voice = voice or "en-US-GuyNeural"
            out = f"assets/tmp_{i}_{uuid.uuid4().hex}.wav"

            try:
                asyncio.run(_tts_chunk(simplified, out, fallback_voice))
                if os.path.exists(out) and os.path.getsize(out) > 1500:
                    temp_files.append(out)
                    success = True
            except Exception:
                pass

        if not success:
            raise RuntimeError(
                "Edge-TTS backend rejected content after all fallbacks"
            )

        time.sleep(0.15)

    # ---------------- CONCAT ---------------- #

    list_file = f"assets/tts_list_{uuid.uuid4().hex}.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in temp_files:
            f.write(f"file '{os.path.abspath(p)}'\n")

    final_out = f"assets/voice_{uuid.uuid4().hex}.wav"

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

    # Cleanup
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
        raise RuntimeError("Final TTS audio invalid")

    return final_out
