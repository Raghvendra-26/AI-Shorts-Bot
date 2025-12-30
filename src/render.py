# src/render.py
import subprocess
import os


def render_video(
    bg_video: str,
    audio_file: str,
    music_file: str,
    output_file: str,
    duration: float,
    subtitles_path: str | None = None
):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    filters = []

    # ---------------- VIDEO FILTER (LOCK TRUE PORTRAIT) ---------------- #
    video_filter = (
        "scale=1080:1920:"
        "force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "setsar=1,"
        "setdar=9/16"
    )

    if subtitles_path:
        # Windows-safe escaping for FFmpeg
        sub_path = subtitles_path.replace("\\", "/").replace(":", "\\:")
        video_filter += f",subtitles='{sub_path}'"

    filters.append(f"[0:v]{video_filter}[vout]")

    # ---------------- AUDIO FILTER ---------------- #
    filters.append(
        "[1:a]"
        "aformat=sample_fmts=fltp:"
        "sample_rates=44100:"
        "channel_layouts=stereo,"
        "highpass=f=80,"
        "lowpass=f=12000,"
        "alimiter=limit=0.97"
        "[voice]"
    )

    filters.append(
        "[2:a]"
        "aformat=sample_fmts=fltp:"
        "sample_rates=44100:"
        "channel_layouts=stereo,"
        "volume=0.20"
        "[music]"
    )

    filters.append("[voice][music]amix=inputs=2:normalize=0[aout]")

    filter_complex = ";".join(filters)

    cmd = [
        "ffmpeg", "-y",

        # Duration guard
        "-t", str(duration),

        # Background (loop)
        "-stream_loop", "-1", "-i", bg_video,

        # Voice
        "-i", audio_file,

        # Music (loop)
        "-stream_loop", "-1", "-i", music_file,

        "-filter_complex", filter_complex,

        "-map", "[vout]",
        "-map", "[aout]",

        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.2",
        "-crf", "18",
        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "192k",

        "-shortest",
        output_file
    ]

    subprocess.run(cmd, check=True)
