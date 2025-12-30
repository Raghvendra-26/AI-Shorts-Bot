import sys
import os
import subprocess
import json
import uuid
import random

from src.tts_edge import text_to_speech
from src.captions_whisper import generate_word_level_srt
from src.text_utils import sanitize_for_tts, clean_llm_script, sanitize_spoken_script
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
from src.bg_fetcher import fetch_background_clips
from src.video_utils import concat_background_clips


# ---------------- CONSTANTS ---------------- #

CTA_FALLBACK_POOL = [
    "Follow for more!",
    "Subscribe for more shorts!",
    "Like and follow!",
    "Follow for daily facts!",
    "More amazing shorts coming!",
    "Hit follow now!",
    "Follow to stay inspired!",
    "Don’t miss the next one!"
]


# ---------------- UTILS ---------------- #

def get_audio_duration(path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=duration",
        "-of", "json", path
    ]
    data = json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)
    return float(data["streams"][0]["duration"])


def clip_count_for_duration(duration: float) -> int:
    if duration <= 30:
        return 3
    if duration <= 45:
        return 4
    return 5


def reuse_clips(clips: list[str], target: int) -> list[str]:
    if not clips:
        raise RuntimeError("No background clips available")

    if len(clips) >= target:
        return clips[:target]

    out = []
    i = 0
    while len(out) < target:
        out.append(clips[i % len(clips)])
        i += 1
    return out


# ---------------- CTA HANDLING ---------------- #

def try_attach_cta(
    text: str,
    body_duration: float
) -> tuple[str | None, str | None, float]:
    """
    Convert CTA text to audio and validate duration.
    Returns (cta_text, cta_audio_path, cta_duration) or (None, None, 0.0)
    """
    audio = text_to_speech(sanitize_for_tts(text))
    duration = get_audio_duration(audio)

    if body_duration + duration <= 59:
        return text, audio, duration

    try:
        os.remove(audio)
    except OSError:
        pass

    return None, None, 0.0


# ---------------- MAIN PIPELINE ---------------- #

def generate_short(idea: str):
    logger.info(f"Using idea: {idea}")

    # -------------------------------------------------
    # 1️⃣ SCRIPT BODY (NO CTA)
    # -------------------------------------------------
    script_prompt = f"""
Write a spoken YouTube Shorts script BODY (NO CTA).

Rules:
- Strictly between 130–150 words
- Conversational
- No meta language
- No CTA
- No emojis, lists, or headings

Topic:
{idea}

Return ONLY the spoken script body.
"""

    scripts = generate_multiple_scripts(script_prompt, n=2)
    script = select_best_script(scripts)
    original_script = script

    script = regenerate_hook(script, idea)
    script = rewrite_long_sentences(script)

    cleaned = sanitize_spoken_script(clean_llm_script(script))
    script_body = cleaned if cleaned.strip() else original_script

    # -------------------------------------------------
    # 2️⃣ BODY TTS
    # -------------------------------------------------
    logger.info("Generating narration (body)")
    body_audio = text_to_speech(sanitize_for_tts(script_body))
    body_duration = get_audio_duration(body_audio)

    if body_duration > 57:
        logger.warning(
            f"Body narration too long ({body_duration:.2f}s). CTA may be skipped."
        )

    # -------------------------------------------------
    # 3️⃣ CTA (LLM + FALLBACK GUARANTEED)
    # -------------------------------------------------
    cta_text = None
    cta_audio = None
    cta_duration = 0.0

    # ---- Try LLM CTA ----
    cta_prompt = f"""
Write ONE energetic spoken CTA.
Max 6 words.
Commanding tone.

Topic:
{idea}

Return ONLY the sentence.
"""

    cta_candidates = generate_multiple_scripts(cta_prompt, n=1)

    if cta_candidates and cta_candidates[0].strip():
        candidate = cta_candidates[0].strip()
        cta_text, cta_audio, cta_duration = try_attach_cta(
            candidate, body_duration
        )

        if cta_text:
            logger.info(f"LLM CTA added ({cta_duration:.2f}s): {cta_text}")

    # ---- Fallback CTA ----
    if not cta_text:
        fallback = random.choice(CTA_FALLBACK_POOL)
        cta_text, cta_audio, cta_duration = try_attach_cta(
            fallback, body_duration
        )

        if cta_text:
            logger.info(f"Fallback CTA added ({cta_duration:.2f}s): {cta_text}")
        else:
            logger.warning("CTA skipped due to duration constraints")

    # -------------------------------------------------
    # 4️⃣ MERGE BODY + CTA AUDIO
    # -------------------------------------------------
    final_voice = f"assets/voice_final_{uuid.uuid4().hex}.wav"
    concat_list = f"assets/voice_concat_{uuid.uuid4().hex}.txt"

    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{os.path.abspath(body_audio)}'\n")
        if cta_audio:
            f.write(f"file '{os.path.abspath(cta_audio)}'\n")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            final_voice
        ],
        check=True
    )

    total_duration = min(get_audio_duration(final_voice), 59.0)
    logger.info(f"Final narration duration: {total_duration:.2f}s")

    try:
        os.remove(concat_list)
    except OSError:
        pass

    # -------------------------------------------------
    # 5️⃣ CAPTIONS
    # -------------------------------------------------
    srt_path = f"assets/captions_{os.getpid()}.srt"
    generate_word_level_srt(final_voice, srt_path)
    ass_path = srt_to_ass(srt_path)

    if not ass_path or not os.path.exists(ass_path):
        raise RuntimeError("Subtitle generation failed")

    # -------------------------------------------------
    # 6️⃣ BACKGROUND CLIPS
    # -------------------------------------------------
    expected = clip_count_for_duration(total_duration)
    fetched = fetch_background_clips(idea, expected)

    if not fetched:
        raise RuntimeError("No background clips fetched")

    final_clips = reuse_clips(fetched, expected)
    per_clip_duration = total_duration / len(final_clips)
    merged_bg = concat_background_clips(final_clips, per_clip_duration)

    # -------------------------------------------------
    # 7️⃣ MUSIC
    # -------------------------------------------------
    bg_music = fetch_background_music(idea)

    # -------------------------------------------------
    # 8️⃣ RENDER
    # -------------------------------------------------
    render_video(
        bg_video=merged_bg,
        audio_file=final_voice,
        music_file=bg_music,
        output_file="outputs/final_short.mp4",
        duration=total_duration
    )

    logger.info("✅ Short video generated successfully")


# ---------------- ENTRY ---------------- #

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError("Pass idea in quotes")
    generate_short(sys.argv[1])
