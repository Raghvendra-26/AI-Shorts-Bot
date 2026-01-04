# src/bg_fetcher.py

import requests
import random
import os
from dotenv import load_dotenv

from src.visual_intent import build_visual_queries
from src.utils.video_history import get_recent_video_ids, mark_video_used

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

# Prevent duplicates in a single run (cross-provider)
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
        "per_page": 20,
        "size": "small",
    }

    res = requests.get(url, headers=PEXELS_HEADERS, params=params, timeout=15)
    res.raise_for_status()
    return res.json().get("videos", [])


def _fetch_from_pexels(query: str) -> str | None:
    recent = get_recent_video_ids("pexels")
    videos = _search_pexels(query)
    random.shuffle(videos)

    for v in videos:
        vid = f"pexels_{v['id']}"

        # Hard dedup
        if vid in USED_VIDEO_IDS or vid in recent:
            continue

        files = v.get("video_files", [])
        if not files:
            continue

        # Highest vertical resolution
        best = max(files, key=lambda f: f["height"])

        path = _download_video(best["link"], vid)
        USED_VIDEO_IDS.add(vid)
        mark_video_used("pexels", vid)
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
        "per_page": 20,
        "safesearch": "true",
    }

    res = requests.get(url, params=params, timeout=15)
    res.raise_for_status()
    return res.json().get("hits", [])


def _fetch_from_pixabay(query: str) -> str | None:
    recent = get_recent_video_ids("pixabay")
    videos = _search_pixabay(query)
    random.shuffle(videos)

    for v in videos:
        vid = f"pixabay_{v['id']}"

        if vid in USED_VIDEO_IDS or vid in recent:
            continue

        files = v.get("videos", {})
        if not files:
            continue

        # Only vertical videos
        candidates = [
            f for f in files.values()
            if f["height"] >= f["width"]
        ]

        if not candidates:
            continue

        best = max(candidates, key=lambda f: f["height"])

        path = _download_video(best["url"], vid)
        USED_VIDEO_IDS.add(vid)
        mark_video_used("pixabay", vid)
        return path

    return None


# --------------------------------------------------
# MULTI-CLIP FETCHER (PIPELINE)
# --------------------------------------------------

def fetch_background_clips(idea: str, n: int) -> list[str]:
    """
    Fetch MULTIPLE DISTINCT background clips
    from BOTH Pexels + Pixabay with history protection.
    """

    queries = build_visual_queries(idea)
    random.shuffle(queries)

    providers = [_fetch_from_pexels, _fetch_from_pixabay]
    clips: list[str] = []

    for query in queries:
        if len(clips) >= n:
            break

        random.shuffle(providers)

        for fetcher in providers:
            if len(clips) >= n:
                break

            try:
                provider_query = query

                # Provider tuning
                if fetcher == _fetch_from_pixabay:
                    provider_query = f"{query} abstract cinematic"

                video = fetcher(provider_query)
                if video:
                    clips.append(video)

            except Exception:
                continue

    if not clips:
        raise RuntimeError("No background clips found")

    return clips


# --------------------------------------------------
# LEGACY SINGLE FETCH (OPTIONAL)
# --------------------------------------------------

def fetch_background(idea: str) -> str:
    clips = fetch_background_clips(idea, 1)
    return clips[0]
