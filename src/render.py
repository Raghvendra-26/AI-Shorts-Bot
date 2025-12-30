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

    # ---------------- VIDEO FILTER ---------------- #
    if subtitles_path:
        # IMPORTANT: escape path safely for Windows FFmpeg
        sub_path = subtitles_path.replace("\\", "/").replace(":", "\\:")
        filters.append(f"[0:v]subtitles='{sub_path}'[vout]")
    else:
        filters.append("[0:v]null[vout]")

    # ---------------- AUDIO FILTER ---------------- #
    filters.append(
        "[1:a]"
        "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,"
        "highpass=f=80,lowpass=f=12000,alimiter=limit=0.97[voice]"
    )

    filters.append(
        "[2:a]"
        "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,"
        "volume=0.15[music]"
    )

    filters.append("[voice][music]amix=inputs=2:normalize=0[aout]")

    filter_complex = ";".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-t", str(duration),

        # background loop
        "-stream_loop", "-1", "-i", bg_video,

        # voice
        "-i", audio_file,

        # music loop
        "-stream_loop", "-1", "-i", music_file,

        "-filter_complex", filter_complex,

        "-map", "[vout]",
        "-map", "[aout]",

        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",

        output_file
    ]

    subprocess.run(cmd, check=True)
