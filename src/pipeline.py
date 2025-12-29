import sys
import os
import subprocess
import json

from src.tts_edge import text_to_speech
from src.captions_whisper import generate_word_level_srt
from src.text_utils import (
    sanitize_for_tts,
    clean_llm_script,
    sanitize_spoken_script
)
from src.bg_fetcher import fetch_background
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

    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError("ffprobe failed – ensure ffmpeg is installed")

    try:
        data = json.loads(result.stdout)
        duration = float(data["streams"][0]["duration"])
    except Exception:
        raise RuntimeError("Could not parse audio duration")

    return duration


def has_cta(text: str) -> bool:
    endings = (
        "follow for more.",
        "subscribe for more.",
        "save this.",
        "share this.",
        "like and follow.",
    )
    return any(text.strip().lower().endswith(e) for e in endings)


# ---------------- MAIN PIPELINE ---------------- #

def generate_short(idea: str):
    logger.info(f"Using idea: {idea}")

    if len(idea.split()) < 3:
        raise RuntimeError("Idea too short")

    # 1️⃣ SCRIPT GENERATION
    logger.info("Generating script")

    script_prompt = f"""
Write a spoken YouTube Shorts script designed to fit naturally within 50–55 seconds.

Target length:
- Approximately 120–135 words when spoken
- Natural pacing, no rushing

Rules:
- Spoken dialogue only
- No meta language (do NOT mention script, video, or writing)
- No headings, lists, emojis, or formatting
- Conversational and engaging tone
- End with EXACTLY ONE short call-to-action sentence
- Do NOT add anything after the CTA

Topic:
{idea}

Return ONLY the spoken script text.
"""

    scripts = generate_multiple_scripts(script_prompt, n=2)
    script = select_best_script(scripts)

    original_script = script

    # 2️⃣ HOOK + SENTENCE OPTIMIZATION
    script = regenerate_hook(script, idea)
    script = rewrite_long_sentences(script)

    if not script or len(script.split()) < 60:
        logger.warning("Script degraded after optimization, reverting")
        script = original_script

    # 3️⃣ CLEANING
    cleaned = clean_llm_script(script)
    cleaned = sanitize_spoken_script(cleaned)

    if cleaned.strip():
        script = cleaned
    else:
        logger.warning("Cleaning wiped script — restoring original")
        script = original_script

    wc = len(script.split())
    logger.info(f"Script word count: {wc}")

    # 4️⃣ CTA VALIDATION (NON-HARDCODED)
    if not has_cta(script):
        logger.warning("CTA missing — regenerating CTA only")

        cta_prompt = f"""
Write ONE short spoken CTA sentence.

Rules:
- Max 6 words
- No emojis
- No meta language

Topic:
{idea}

Return ONLY the sentence.
"""
    cta_candidates = generate_multiple_scripts(cta_prompt, n=1)

    if cta_candidates and cta_candidates[0].strip():
        cta = cta_candidates[0].strip()
        script = script.rstrip(". ") + ". " + cta
    else:
        logger.warning("⚠️ CTA generation failed — keeping script unchanged")

    # 5️⃣ VOICE
    logger.info("Generating voice")

    tts_text = sanitize_for_tts(script)
    voice_path = text_to_speech(tts_text)

    raw_duration = get_audio_duration(voice_path)
    logger.info(f"Raw narration duration: {raw_duration:.2f}s")

    # 6️⃣ DURATION GUARD (CRITICAL)
    if raw_duration > 59.5:
        logger.warning(
            f"Narration too long ({raw_duration:.2f}s). Regenerating with stricter timing."
        )

        strict_prompt = script_prompt + """
IMPORTANT:
- MUST fit within 55 seconds when spoken
- Shorten explanations if needed
"""

        scripts = generate_multiple_scripts(strict_prompt, n=1)
        script = select_best_script(scripts)

        tts_text = sanitize_for_tts(script)
        voice_path = text_to_speech(tts_text)
        raw_duration = get_audio_duration(voice_path)

        logger.info(f"Regenerated narration duration: {raw_duration:.2f}s")

    duration = min(raw_duration, 59.0)

    # 7️⃣ CAPTIONS
    logger.info("Generating captions")

    captions_srt = os.path.abspath(f"assets/captions_{os.getpid()}.srt")
    generate_word_level_srt(voice_path, captions_srt)

    captions_ass = srt_to_ass(captions_srt)
    if not captions_ass or not os.path.exists(captions_ass):
        raise RuntimeError("Subtitle conversion failed")

    # 8️⃣ BACKGROUND VIDEO
    logger.info("Fetching background video")

    bg_video = fetch_background(idea)
    if not bg_video or not os.path.exists(bg_video):
        raise RuntimeError("Background video missing")

    # 9️⃣ BACKGROUND MUSIC
    logger.info("Fetching background music")

    bg_music = fetch_background_music(idea)
    if not bg_music or not os.path.exists(bg_music):
        raise RuntimeError("Background music missing")

    # 🔟 RENDER
    logger.info("Rendering final video")

    render_video(
        bg_video=os.path.abspath(bg_video),
        audio_file=os.path.abspath(voice_path),
        music_file=os.path.abspath(bg_music),
        output_file=os.path.abspath("outputs/final_short.mp4"),
        duration=duration
    )

    logger.info("Short video generated successfully")
    print("✅ Short video generated successfully!")


# ---------------- ENTRY ---------------- #

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError("Pass idea in quotes")

    generate_short(sys.argv[1])
