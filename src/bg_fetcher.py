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

# 🧠 Session-level memory (prevents duplicates per run)
USED_VIDEO_IDS: set[int] = set()


# --------------------------------------------------
# INTERNAL HELPERS
# --------------------------------------------------

def _download_video(video_url: str, vid: int) -> str:
    filename = os.path.join(OUTPUT_DIR, f"{vid}.mp4")

    if os.path.exists(filename):
        return filename

    with requests.get(video_url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)

    return filename


def _search_pexels(query: str) -> list[dict]:
    url = "https://api.pexels.com/videos/search"

    params = {
        "query": query,
        "orientation": "portrait",
        "size": "small",
        "per_page": 15,
    }

    res = requests.get(url, headers=HEADERS, params=params, timeout=15)
    res.raise_for_status()
    return res.json().get("videos", [])


def _fetch_single_query(query: str) -> str | None:
    """
    Fetch ONE unique background video for a query.
    Uses session memory to avoid duplicates.
    """

    videos = _search_pexels(query)
    if not videos:
        return None

    random.shuffle(videos)

    for video in videos:
        vid = video.get("id")
        if vid in USED_VIDEO_IDS:
            continue  # 🚫 already used in this run

        best_file = max(
            video["video_files"],
            key=lambda f: f["height"]
        )

        path = _download_video(best_file["link"], vid)
        USED_VIDEO_IDS.add(vid)

        return path

    return None


# --------------------------------------------------
# PUBLIC API (LEGACY – DO NOT CHANGE)
# --------------------------------------------------

def fetch_background(idea: str) -> str:
    """
    Fetch a SINGLE background video (legacy behavior).
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

    raise RuntimeError("No suitable background video found after all attempts")


# --------------------------------------------------
# MULTI-CLIP FETCHER (USED BY PIPELINE)
# --------------------------------------------------

def fetch_background_clips(idea: str, n: int) -> list[str]:
    """
    Fetch MULTIPLE DISTINCT background video clips.
    Guarantees no duplicates in a single run.
    """

    queries = build_video_queries(idea)
    clips: list[str] = []

    print(f"🎬 Fetching {n} background clips")

    for query in queries:
        if len(clips) >= n:
            break

        try:
            print(f"🎥 Trying background query: {query}")
            video = _fetch_single_query(query)
            if video:
                clips.append(video)
        except Exception as e:
            print(f"⚠️ Background query failed: {query} ({e})")

    print(f"✅ Background clips fetched: {len(clips)}")
    return clips


# --------------------------------------------------
# OPTIONAL MONTAGE FETCHER (UNCHANGED API)
# --------------------------------------------------

def fetch_multiple_backgrounds(idea: str, count: int = 5) -> list[str]:
    """
    Fetch multiple distinct background videos for montage-style shorts.
    """

    queries = build_video_queries(idea)
    collected = []

    for query in queries:
        if len(collected) >= count:
            break

        try:
            videos = _search_pexels(query)
            random.shuffle(videos)

            for video in videos:
                vid = video["id"]
                if vid in USED_VIDEO_IDS:
                    continue

                best_file = max(
                    video["video_files"],
                    key=lambda f: f["height"]
                )

                path = _download_video(best_file["link"], vid)
                USED_VIDEO_IDS.add(vid)
                collected.append(path)

                if len(collected) >= count:
                    break

        except Exception:
            continue

    return collected
