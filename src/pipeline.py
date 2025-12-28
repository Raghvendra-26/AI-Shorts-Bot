# src/pipeline.py

import sys
import os
import subprocess
import json

from src.ollama_llm import generate_short_script
from src.tts_edge import text_to_speech
from src.captions_whisper import generate_word_level_srt
from src.text_utils import sanitize_for_tts, clean_llm_script
from src.bg_fetcher import fetch_background
from src.bg_query import bg_query_from_niche
from src.bg_music_fetcher import fetch_background_music
from src.render import render_video
from src.utils.srt_to_ass import srt_to_ass
from src.utils.logger import logger
from src.script_quality import (
    generate_multiple_scripts,
    select_best_script,
    regenerate_hook,
    rewrite_long_sentences
)



# ---------------- UTILS ---------------- #

def get_audio_duration(path: str) -> float:
    """Safe duration read for edge-tts output"""
    if not os.path.exists(path):
        raise RuntimeError("Audio file missing")

    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=duration",
        "-of", "json",
        path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if not result.stdout.strip():
        raise RuntimeError("ffprobe returned empty output")

    try:
        data = json.loads(result.stdout)
        duration = float(data["streams"][0]["duration"])
    except Exception:
        raise RuntimeError("Could not read audio duration")

    # 🔒 HARD CAP (shorts safe)
    return min(duration, 59.0)


# ---------------- MAIN PIPELINE ---------------- #

def generate_short(idea: str):
    logger.info(f"Using idea: {idea}")

    if len(idea.split()) < 4:
        raise RuntimeError("Idea too short")

    # 1️⃣ SCRIPT
    logger.info("Generating script")
    script_prompt = f"""
Write a 30–45 second YouTube Shorts spoken script.

Topic:
{idea}

Rules:
- Minimum 90 words
- Spoken dialogue only
- No emojis
- No headings
- End with ONE CTA

Return ONLY the script.
"""

    scripts = generate_multiple_scripts(script_prompt, n=3)
    script = select_best_script(scripts)

    script = regenerate_hook(script, idea)
    script = rewrite_long_sentences(script)

    script = clean_llm_script(script)


    wc = len(script.split())
    logger.info(f"Script word count: {wc}")

    if wc < 80:
        raise RuntimeError("Script too short")

    # 2️⃣ VOICE
    logger.info("Generating voice")
    clean_script = sanitize_for_tts(script).strip()

    if not clean_script:
        logger.warning("sanitize_for_tts empty → using raw script")
        clean_script = script.strip()

    voice_path = text_to_speech(clean_script)

    # 3️⃣ AUDIO DURATION
    duration = get_audio_duration(voice_path)
    logger.info(f"Audio duration: {duration:.2f}s")

    # 4️⃣ CAPTIONS → ASS
    logger.info("Generating captions")
    captions_srt = os.path.abspath("assets/captions.srt")

    generate_word_level_srt(
        audio_path=voice_path,
        output_srt=captions_srt
    )

    if not os.path.exists(captions_srt):
        raise RuntimeError("Captions generation failed")

    captions_ass = srt_to_ass(captions_srt)

    # 5️⃣ BACKGROUND VIDEO
    logger.info("Fetching background video")
    bg_video = fetch_background(bg_query_from_niche(idea))

    if not bg_video or not os.path.exists(bg_video):
        raise RuntimeError("Background video missing")

    # 6️⃣ MUSIC
    logger.info("Fetching background music")
    try:
        bg_music = fetch_background_music(idea)
    except Exception:
        bg_music = None

    if not bg_music:
        bg_music = os.path.abspath("assets/silence.mp3")
    else:
        bg_music = os.path.abspath(bg_music)

    # 7️⃣ RENDER
    logger.info("Rendering video")
    render_video(
        bg_video=os.path.abspath(bg_video),
        audio_file=os.path.abspath(voice_path),
        music_file=bg_music,
        output_file=os.path.abspath("outputs/final_short.mp4"),
        duration=duration
    )

    print("✅ Short video generated successfully!")
    logger.info("Short video generated successfully")


# ---------------- ENTRY ---------------- #

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError("Pass idea in quotes")

    generate_short(sys.argv[1])
