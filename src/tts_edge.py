# src/tts_edge.py
import asyncio
import edge_tts
import uuid
import os
import subprocess
import time

VOICE = "en-US-AriaNeural"
RATE = "+0%"


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

async def _tts_chunk(text: str, out_path: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=RATE
    )
    await communicate.save(out_path)


# ---------------- PUBLIC API ---------------- #

def text_to_speech(text: str) -> str:
    """
    Robust Edge-TTS:
    - Splits text into chunks
    - Generates audio per chunk
    - Merges using ffmpeg
    """
    os.makedirs("assets", exist_ok=True)

    chunks = split_text(text)
    if not chunks:
        raise RuntimeError("TTS received empty text")

    temp_files = []

    # 🔊 Generate audio per chunk
    for i, chunk in enumerate(chunks):
        out = f"assets/tmp_{i}_{uuid.uuid4().hex}.wav"

        try:
            asyncio.run(_tts_chunk(chunk, out))
        except Exception as e:
            raise RuntimeError(f"Edge-TTS failed on chunk {i}: {e}")

        # ⛔ Validate audio actually exists
        if not os.path.exists(out) or os.path.getsize(out) < 1000:
            raise RuntimeError("Edge-TTS produced empty audio chunk")

        temp_files.append(out)

        # small delay avoids throttling
        time.sleep(0.2)

    # 🧩 Create concat list
    list_file = "assets/tts_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in temp_files:
            f.write(f"file '{os.path.abspath(p)}'\n")

    final_out = f"assets/voice_{uuid.uuid4().hex}.wav"

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
