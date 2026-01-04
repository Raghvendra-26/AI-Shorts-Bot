# src/utils/fallback_background.py
import subprocess
import os


def create_fallback_background(
    duration: float,
    output_path: str,
    color: str = "black",
    fps: int = 30
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c={color}:s=1080x1920:r={fps}",
        "-t", str(duration),
        output_path
    ]

    subprocess.run(cmd, check=True)
