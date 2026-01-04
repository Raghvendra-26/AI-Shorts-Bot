import subprocess
import json


def get_audio_duration(path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=duration",
        "-of", "json", path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data["streams"][0]["duration"])
