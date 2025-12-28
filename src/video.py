import subprocess

def create_background(duration, output_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1080x1920:r=30",
        "-t", str(duration),
        output_path
    ]
    subprocess.run(cmd, check=True)
