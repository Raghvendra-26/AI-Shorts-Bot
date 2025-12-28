# src/captions_whisper.py
import whisper
import re
import os

# Load once (important!)
_MODEL = whisper.load_model("base")


def seconds_to_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def clean_word(word: str) -> str:
    word = re.sub(r"[^\w\s']", "", word)
    return word.strip()


def generate_word_level_srt(audio_path: str, output_srt: str):
    """
    Generates word-accurate captions using Whisper
    """
    result = _MODEL.transcribe(
        audio_path,
        word_timestamps=True,
        verbose=False
    )

    index = 1
    srt_lines = []

    for segment in result.get("segments", []):
        words = segment.get("words")
        if not words:
            continue

        for w in words:
            word = clean_word(w.get("word", ""))
            if not word:
                continue

            start_sec = w.get("start")
            end_sec = w.get("end")

            # Prevent zero-duration captions
            if start_sec is None or end_sec is None or end_sec <= start_sec:
                continue

            start = seconds_to_srt_time(start_sec)
            end = seconds_to_srt_time(end_sec)

            srt_lines.append(
                f"{index}\n{start} --> {end}\n{word}\n"
            )
            index += 1

    if not srt_lines:
        raise RuntimeError("Whisper produced no valid word captions")

    with open(output_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
