# src/bg_fetcher.py

import requests
import random
import os
from dotenv import load_dotenv

from src.bg_intent import build_video_queries

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
if not PEXELS_API_KEY:
    raise RuntimeError("PEXELS_API_KEY not set")

HEADERS = {"Authorization": PEXELS_API_KEY}

OUTPUT_DIR = "assets/bg_cache"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _download_video(video_url: str, filename: str):
    if os.path.exists(filename):
        return filename

    with requests.get(video_url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)

    return filename


def _fetch_single_query(query: str) -> str | None:
    url = "https://api.pexels.com/videos/search"

    params = {
        "query": query,
        "orientation": "portrait",
        "size": "small",
        "per_page": 15
    }

    res = requests.get(url, headers=HEADERS, params=params, timeout=15)
    res.raise_for_status()

    videos = res.json().get("videos", [])
    if not videos:
        return None

    # Prefer longer, higher quality clips
    random.shuffle(videos)
    video = max(
        videos,
        key=lambda v: max(f["height"] for f in v["video_files"])
    )

    best_file = max(
        video["video_files"],
        key=lambda f: f["height"]
    )

    filename = os.path.join(OUTPUT_DIR, f"{video['id']}.mp4")
    return _download_video(best_file["link"], filename)


def fetch_background(idea: str) -> str:
    """
    Fetch background video using ranked visual intent queries.
    Tries multiple queries until one succeeds.
    """

    queries = build_video_queries(idea)

    for query in queries:
        try:
            print(f"🎥 Trying background query: {query}")
            video = _fetch_single_query(query)
            if video:
                return video
        except Exception as e:
            print(f"⚠️ Background query failed: {query} ({e})")
            continue

    raise RuntimeError("No suitable background video found after all attempts")
