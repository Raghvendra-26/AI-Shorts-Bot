import sys
import os
import subprocess
import json
import uuid
import random
import re

# ---------------- IMPORTS ---------------- #

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
from src.metadata_utils import generate_metadata


# ---------------- CONSTANTS ---------------- #

CTA_FALLBACK_POOL = [
    "Follow for more!",
    "Subscribe for more shorts!",
    "Like and follow!",
    "Follow for daily facts!",
    "More amazing shorts coming!",
    "Hit follow now!",
    "Follow to stay inspired!",
    "Don’t miss the next one!",
]


# ---------------- AUDIO UTILS ---------------- #

def get_audio_duration(path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=duration",
        "-of", "json", path
    ]
    data = json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)
    return float(data["streams"][0]["duration"])


# ---------------- VIDEO PLANNING ---------------- #

def clip_count_for_duration(duration: float) -> int:
    if duration <= 30:
        return 3
    if duration <= 45:
        return 4
    return 5


def split_sentences(text: str) -> list[str]:
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if len(p.split()) >= 4]


def build_clip_plan(sentences: list[str], total_duration: float, expected: int) -> list[float]:
    if not sentences:
        return [total_duration / expected] * expected

    weights = [max(len(s.split()), 6) for s in sentences]
    total_weight = sum(weights)

    durations = [(w / total_weight) * total_duration for w in weights]

    if len(durations) > expected:
        durations = durations[:expected]
    elif len(durations) < expected:
        avg = total_duration / expected
        while len(durations) < expected:
            durations.append(avg)

    return durations


def reuse_no_adjacent(clips: list[str], target: int) -> list[str]:
    if not clips:
        raise RuntimeError("No background clips available")

    result = []
    i = 0
    while len(result) < target:
        candidate = clips[i % len(clips)]
        if not result or result[-1] != candidate:
            result.append(candidate)
        i += 1

    return result


# ---------------- CTA SAFETY ---------------- #

def is_tts_safe(text: str) -> bool:
    if not text or len(text.split()) < 3:
        return False
    if not re.search(r"[aeiouAEIOU]", text):
        return False
    return True


def try_attach_cta(text: str, body_duration: float):
    if not is_tts_safe(text):
        return None, None, 0.0

    try:
        audio = text_to_speech(sanitize_for_tts(text))
        duration = get_audio_duration(audio)
    except Exception:
        return None, None, 0.0

    if body_duration + duration <= 59:
        return text, audio, duration

    try:
        os.remove(audio)
    except OSError:
        pass

    return None, None, 0.0


# ---------------- MAIN PIPELINE ---------------- #

def generate_short(idea: str):
    logger.info(f"🎯 IDEA: {idea}")

    # Output folder (immutable per video)
    video_id = uuid.uuid4().hex[:8]
    output_dir = os.path.join("outputs", video_id)
    os.makedirs(output_dir, exist_ok=True)

    # -------------------------------------------------
    # 1️⃣ SCRIPT BODY
    # -------------------------------------------------
    script_prompt = f"""
Write a spoken YouTube Shorts script BODY (NO CTA).

Rules:
- 110–120 words
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

    sentences = split_sentences(script_body)

    # -------------------------------------------------
    # 2️⃣ BODY TTS
    # -------------------------------------------------
    body_audio = text_to_speech(sanitize_for_tts(script_body))
    body_duration = get_audio_duration(body_audio)

    # -------------------------------------------------
    # 3️⃣ CTA
    # -------------------------------------------------
    cta_text, cta_audio, cta_duration = None, None, 0.0

    cta_prompt = f"""
Write ONE energetic spoken CTA.
Max 6 words.
Commanding tone.

Topic:
{idea}

Return ONLY the sentence.
"""

    cta_candidates = generate_multiple_scripts(cta_prompt, n=1)

    if cta_candidates:
        cta_text, cta_audio, cta_duration = try_attach_cta(
            cta_candidates[0], body_duration
        )

    if not cta_text:
        fallback = random.choice(CTA_FALLBACK_POOL)
        cta_text, cta_audio, cta_duration = try_attach_cta(
            fallback, body_duration
        )

    # -------------------------------------------------
    # 4️⃣ MERGE VOICE
    # -------------------------------------------------
    final_voice = os.path.join(output_dir, "voice.wav")
    concat_list = os.path.join(output_dir, "voice_concat.txt")

    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{os.path.abspath(body_audio)}'\n")
        if cta_audio:
            f.write(f"file '{os.path.abspath(cta_audio)}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", final_voice],
        check=True
    )

    total_duration = min(get_audio_duration(final_voice), 59.0)

    # -------------------------------------------------
    # 5️⃣ CAPTIONS
    # -------------------------------------------------
    subtitles_path = None
    try:
        srt = os.path.join(output_dir, "captions.srt")
        generate_word_level_srt(final_voice, srt)
        ass = srt_to_ass(srt)
        if ass and os.path.exists(ass):
            subtitles_path = ass
    except Exception:
        pass

    # -------------------------------------------------
    # 6️⃣ BACKGROUND VIDEO
    # -------------------------------------------------
    expected = clip_count_for_duration(total_duration)
    fetched = fetch_background_clips(idea, expected)

    final_clips = reuse_no_adjacent(fetched, expected)
    clip_durations = build_clip_plan(sentences, total_duration, expected)

    merged_bg = concat_background_clips(final_clips, clip_durations)

    # -------------------------------------------------
    # 7️⃣ MUSIC
    # -------------------------------------------------
    bg_music = fetch_background_music(idea)

    # -------------------------------------------------
    # 8️⃣ METADATA (IDEA-DRIVEN)
    # -------------------------------------------------
    metadata = generate_metadata(
        idea=idea,
        script=script_body
    )

    with open(os.path.join(output_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------
    # 9️⃣ RENDER
    # -------------------------------------------------
    render_video(
        bg_video=merged_bg,
        audio_file=final_voice,
        music_file=bg_music,
        output_file=os.path.join(output_dir, "final_short.mp4"),
        duration=total_duration,
        subtitles_path=subtitles_path
    )

    logger.info(f"✅ SHORT GENERATED → {output_dir}")


# ---------------- ENTRY ---------------- #

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError("Pass idea in quotes")
    generate_short(sys.argv[1])
