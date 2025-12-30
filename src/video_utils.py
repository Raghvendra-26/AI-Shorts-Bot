import subprocess
import os
import uuid
import random
import json


def _get_video_duration(path: str) -> float:
    """Get duration of a video using ffprobe"""
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


def concat_background_clips(clips: list[str], per_clip_duration: float) -> str:
    """
    Trims + concatenates background clips.
    Reuses clips safely by slicing DIFFERENT time segments.
    """

    temp_clips = []

    for clip in clips:
        clip_duration = _get_video_duration(clip)

        # 🎯 Choose a safe random start time
        max_start = max(0, clip_duration - per_clip_duration - 0.5)
        start_time = random.uniform(0, max_start) if max_start > 0 else 0

        out = f"assets/bg_cache/trim_{uuid.uuid4().hex}.mp4"

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(start_time),      # 🔑 THIS IS THE FIX
                "-i", clip,
                "-t", str(per_clip_duration),
                "-vf",
                (
                    "scale=1080:1920:"
                    "force_original_aspect_ratio=increase,"
                    "crop=1080:1920"
                ),
                "-an",
                out
            ],
            check=True
        )

        temp_clips.append(out)

    # ---------------- CONCAT ---------------- #

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
            "-c", "copy",
            merged
        ],
        check=True
    )

    # ---------------- CLEANUP ---------------- #

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
