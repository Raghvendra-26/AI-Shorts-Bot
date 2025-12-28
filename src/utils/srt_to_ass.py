import subprocess
import os

def srt_to_ass(srt_path: str) -> str:
    ass_path = srt_path.replace(".srt", ".ass")

    cmd = [
        "ffmpeg", "-y",
        "-i", srt_path,
        ass_path
    ]

    subprocess.run(cmd, check=True)

    if not os.path.exists(ass_path):
        raise RuntimeError("Failed to convert SRT to ASS")

    return ass_path
