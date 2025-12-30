# src/video_utils.py

import subprocess
import os
import uuid
import random
import json


def _get_video_duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=duration",
            "-of", "json",
            path
        ],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    return float(data["streams"][0]["duration"])


def concat_background_clips(
    clips: list[str],
    clip_durations: list[float]
) -> str:
    """
    Portrait-safe background merger.

    ✔ TRUE 1080x1920 at source
    ✔ Random segment per reuse
    ✔ No zoompan before concat
    ✔ Stream-identical clips
    ✔ Lossless concat
    """

    if len(clips) != len(clip_durations):
        raise ValueError("clips and clip_durations length mismatch")

    temp_clips = []

    for clip, duration in zip(clips, clip_durations):
        clip_duration = _get_video_duration(clip)

        max_start = max(0, clip_duration - duration - 0.5)
        start_time = random.uniform(0, max_start) if max_start > 0 else 0

        out = f"assets/bg_cache/trim_{uuid.uuid4().hex}.mp4"

        # 🔒 NORMALIZE EVERYTHING HERE (ONCE)
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", f"{start_time:.2f}",
                "-i", clip,
                "-t", f"{duration:.2f}",
                "-vf",
                (
                    "scale=1080:1920:force_original_aspect_ratio=increase,"
                    "crop=1080:1920,"
                    "setsar=1,setdar=9/16"
                ),
                "-r", "30",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-profile:v", "high",
                "-level", "4.1",
                "-crf", "18",
                "-preset", "slow",
                "-an",
                out
            ],
            check=True
        )

        temp_clips.append(out)

    # ---------------- CONCAT (NO FILTERS, NO RE-ENCODE) ----------------

    concat_file = "assets/bg_cache/concat_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for c in temp_clips:
            f.write(f"file '{os.path.abspath(c)}'\n")

    merged = "assets/bg_cache/merged_background.mp4"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",   # 🔥 THIS IS CRITICAL
            merged
        ],
        check=True
    )

    # ---------------- CLEANUP ----------------

    for f in temp_clips:
        try:
            os.remove(f)
        except OSError:
            pass

    try:
        os.remove(concat_file)
    except OSError:
        pass

    return merged
