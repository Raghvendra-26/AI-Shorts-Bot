# src/render.py
import subprocess
import os

def render_video(bg_video, audio_file, music_file, output_file, duration):
    bg_video = os.path.abspath(bg_video).replace("\\", "/")
    audio_file = os.path.abspath(audio_file).replace("\\", "/")
    music_file = os.path.abspath(music_file).replace("\\", "/")
    output_file = os.path.abspath(output_file).replace("\\", "/")

    cmd = [
        "ffmpeg", "-y",

        # Cap output duration
        "-t", str(duration),

        # Background video (loop)
        "-stream_loop", "-1", "-i", bg_video,

        # Narration (MAIN)
        "-i", audio_file,

        # Background music (loop)
        "-stream_loop", "-1", "-i", music_file,

        "-filter_complex",

        # ---------------- AUDIO GRAPH ----------------

        # Narration: clean, stable, dominant
        "[1:a]"
        "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,"
        "highpass=f=80,"
        "lowpass=f=12000,"
        "alimiter=limit=0.98"
        "[voice];"

        # Music: fixed LOW volume, no dynamics
        "[2:a]"
        "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,"
        "volume=0.08"
        "[music];"

        # Mix WITHOUT normalization
        "[voice][music]"
        "amix=inputs=2:normalize=0"
        "[aout]",

        # ---------------- OUTPUT ----------------
        "-map", "0:v",
        "-map", "[aout]",

        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",

        output_file
    ]

    subprocess.run(cmd, check=True)
