# src/bg_fetcher.py

import requests
import random
import os
from dotenv import load_dotenv

from src.bg_intent import build_video_queries

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

if not PEXELS_API_KEY:
    raise RuntimeError("PEXELS_API_KEY not set")

if not PIXABAY_API_KEY:
    raise RuntimeError("PIXABAY_API_KEY not set")

PEXELS_HEADERS = {"Authorization": PEXELS_API_KEY}

OUTPUT_DIR = "assets/bg_cache"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🧠 Prevent duplicates in a single run (cross-provider)
USED_VIDEO_IDS: set[str] = set()


# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

def _download_video(url: str, uid: str) -> str:
    path = os.path.join(OUTPUT_DIR, f"{uid}.mp4")

    if os.path.exists(path):
        return path

    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)

    return path


# --------------------------------------------------
# PEXELS
# --------------------------------------------------

def _search_pexels(query: str) -> list[dict]:
    url = "https://api.pexels.com/videos/search"
    params = {
        "query": query,
        "orientation": "portrait",
        "per_page": 15,
        "size": "small",
    }

    res = requests.get(url, headers=PEXELS_HEADERS, params=params, timeout=15)
    res.raise_for_status()
    return res.json().get("videos", [])


def _fetch_from_pexels(query: str) -> str | None:
    videos = _search_pexels(query)
    random.shuffle(videos)

    for v in videos:
        vid = f"pexels_{v['id']}"
        if vid in USED_VIDEO_IDS:
            continue

        best = max(v["video_files"], key=lambda f: f["height"])
        path = _download_video(best["link"], vid)
        USED_VIDEO_IDS.add(vid)
        return path

    return None


# --------------------------------------------------
# PIXABAY
# --------------------------------------------------

def _search_pixabay(query: str) -> list[dict]:
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "orientation": "vertical",
        "per_page": 15,
        "safesearch": "true",
    }

    res = requests.get(url, params=params, timeout=15)
    res.raise_for_status()
    return res.json().get("hits", [])


def _fetch_from_pixabay(query: str) -> str | None:
    videos = _search_pixabay(query)
    random.shuffle(videos)

    for v in videos:
        vid = f"pixabay_{v['id']}"
        if vid in USED_VIDEO_IDS:
            continue

        files = v.get("videos", {})
        if not files:
            continue

        # ✅ FIX 1: only vertical / portrait videos
        candidates = [
            f for f in files.values()
            if f["height"] >= f["width"]
        ]

        if not candidates:
            continue

        best = max(candidates, key=lambda f: f["height"])

        path = _download_video(best["url"], vid)
        USED_VIDEO_IDS.add(vid)
        return path

    return None


# --------------------------------------------------
# SINGLE FETCH (LEGACY)
# --------------------------------------------------

def fetch_background(idea: str) -> str:
    queries = build_video_queries(idea)

    for query in queries:
        for fetcher in (_fetch_from_pexels, _fetch_from_pixabay):
            try:
                provider_query = query

                # ✅ FIX 2: Pixabay performs better with abstract / cinematic terms
                if fetcher == _fetch_from_pixabay:
                    provider_query = f"{query} abstract cinematic"

                print(f"🎥 Trying {fetcher.__name__}: {provider_query}")
                video = fetcher(provider_query)
                if video:
                    return video
            except Exception as e:
                print(f"⚠️ Failed ({provider_query}): {e}")

    raise RuntimeError("No background video found")


# --------------------------------------------------
# MULTI-CLIP FETCHER (PIPELINE)
# --------------------------------------------------

def fetch_background_clips(idea: str, n: int) -> list[str]:
    """
    Fetch MULTIPLE DISTINCT background clips
    from BOTH Pexels + Pixabay.
    """

    queries = build_video_queries(idea)
    random.shuffle(queries)

    providers = [_fetch_from_pexels, _fetch_from_pixabay]
    clips: list[str] = []

    print(f"🎬 Fetching {n} background clips")

    for query in queries:
        if len(clips) >= n:
            break

        random.shuffle(providers)

        for fetcher in providers:
            if len(clips) >= n:
                break

            try:
                provider_query = query

                # ✅ FIX 2 applied here as well
                if fetcher == _fetch_from_pixabay:
                    provider_query = f"{query} abstract cinematic"

                print(f"🎥 {fetcher.__name__}: {provider_query}")
                video = fetcher(provider_query)
                if video:
                    clips.append(video)
            except Exception as e:
                print(f"⚠️ Fetch failed ({provider_query}): {e}")

    print(f"✅ Background clips fetched: {len(clips)}")
    return clips


# --------------------------------------------------
# OPTIONAL MONTAGE FETCHER
# --------------------------------------------------

def fetch_multiple_backgrounds(idea: str, count: int = 5) -> list[str]:
    return fetch_background_clips(idea, count)
