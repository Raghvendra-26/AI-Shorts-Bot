import requests
import random
import os
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
HEADERS = {"Authorization": PEXELS_API_KEY}

OUTPUT_DIR = "assets/bg_cache"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_background(query: str) -> str:
    url = "https://api.pexels.com/videos/search"

    params = {
        "query": query,
        "orientation": "portrait",
        "size": "small",
        "per_page": 15
    }

    res = requests.get(url, headers=HEADERS, params=params)
    res.raise_for_status()

    videos = res.json()["videos"]
    if not videos:
        raise RuntimeError("No videos found from Pexels")

    video = random.choice(videos)
    file = max(
        video["video_files"],
        key=lambda x: x["height"]
    )

    video_url = file["link"]
    filename = os.path.join(
        OUTPUT_DIR, f"{video['id']}.mp4"
    )

    if not os.path.exists(filename):
        with requests.get(video_url, stream=True) as r:
            with open(filename, "wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    f.write(chunk)

    return filename
