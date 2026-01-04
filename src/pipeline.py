import sys
import os
import json
import uuid
import subprocess

from src.services.script_service import generate_script
from src.services.tts_service import speak
from src.services.cta_service import generate_cta
from src.services.background_service import build_background
from src.services.metadata_service import build_metadata

from src.captions_whisper import generate_word_level_srt
from src.utils.srt_to_ass import srt_to_ass
from src.render import render_video
from src.bg_music_fetcher import fetch_background_music
from src.utils.logger import logger
from src.utils.audio_utils import get_audio_duration


def generate_short(idea: str, lang: str = "en"):
    logger.info(f"🎯 IDEA: {idea} | LANG: {lang}")

    # ---------------- SETUP ---------------- #
    video_id = uuid.uuid4().hex[:8]
    output_dir = os.path.join("outputs", video_id)
    os.makedirs(output_dir, exist_ok=True)

    # ---------------- SCRIPT ---------------- #
    script = generate_script(idea, lang)
    sentences = [s for s in script.split(".") if len(s.strip().split()) >= 4]

    # ---------------- BODY VOICE ---------------- #
    body_audio = speak(script, lang)
    body_duration = get_audio_duration(body_audio)

    # ---------------- CTA ---------------- #
    cta_text, cta_audio, cta_duration = generate_cta(
        idea=idea,
        body_duration=body_duration
    )

    # ---------------- MERGE AUDIO ---------------- #
    final_voice = os.path.join(output_dir, "voice.wav")
    concat_list = os.path.join(output_dir, "concat.txt")

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

    total_duration = min(
        get_audio_duration(final_voice),
        59.0
    )

    # ---------------- CAPTIONS ---------------- #
    subtitles_path = None
    try:
        srt = os.path.join(output_dir, "captions.srt")
        generate_word_level_srt(final_voice, srt)
        ass = srt_to_ass(srt)
        if ass and os.path.exists(ass):
            subtitles_path = ass
    except Exception as e:
        logger.warning(f"⚠️ Caption generation failed: {e}")

    # ---------------- BACKGROUND ---------------- #
    bg_video = build_background(
        idea=idea,
        sentences=sentences,
        duration=total_duration,
        output_dir=output_dir
    )

    # ---------------- MUSIC ---------------- #
    music = fetch_background_music(idea)

    # ---------------- METADATA ---------------- #
    metadata = build_metadata(idea, script)
    with open(os.path.join(output_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # ---------------- RENDER ---------------- #
    render_video(
        bg_video=bg_video,
        audio_file=final_voice,
        music_file=music,
        output_file=os.path.join(output_dir, "final_short.mp4"),
        duration=total_duration,
        subtitles_path=subtitles_path
    )

    logger.info(f"✅ SHORT GENERATED → {output_dir}")


# ---------------- ENTRY ---------------- #

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError("Pass idea in quotes")

    lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    generate_short(sys.argv[1], lang)
