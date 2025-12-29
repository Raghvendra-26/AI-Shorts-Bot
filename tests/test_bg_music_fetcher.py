import sys
import os
import subprocess
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.bg_music_fetcher import fetch_background_music


def ffprobe_duration(path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", path
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return -1
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        return -1


if __name__ == "__main__":
    idea = sys.argv[1] if len(sys.argv) > 1 else "cinematic"

    print("🧪 Testing Openverse music fetch")
    print("Idea:", idea)

    music = fetch_background_music(idea)

    size = os.path.getsize(music)
    duration = ffprobe_duration(music)

    print("\n✅ RESULT")
    print("Path:", music)
    print("Size:", size)
    print("Duration:", f"{duration:.2f}s" if duration > 0 else "unknown")

    if size < 100_000:
        raise RuntimeError("❌ File too small")

    print("\n🎵 Openverse music fetch SUCCESS")
