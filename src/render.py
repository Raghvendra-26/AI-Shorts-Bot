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

        # HARD LIMIT VIDEO LENGTH = VOICE LENGTH
        "-t", str(duration),

        # Background video (loop)
        "-stream_loop", "-1", "-i", bg_video,

        # Main voice (clock)
        "-i", audio_file,

        # Background music (loop)
        "-stream_loop", "-1", "-i", music_file,

        "-filter_complex",
        "[1:a]volume=1.0[a1];"
        "[2:a]volume=0.06[a2];"
        "[a1][a2]amix=inputs=2[aout]",

        "-map", "0:v",
        "-map", "[aout]",

        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",

        output_file
    ]

    subprocess.run(cmd, check=True)
