# src/bg_music_fetcher.py

import requests
import random
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PIXABAY_API_KEY")
MUSIC_DIR = "assets/music"


def fetch_background_music(query="ambient"):
    """
    Fetches a royalty-free background music track.
    Returns file path OR None (never crashes pipeline).
    """
    os.makedirs(MUSIC_DIR, exist_ok=True)

    url = "https://pixabay.com/api/music/"
    params = {
        "key": API_KEY,
        "q": query,
        "per_page": 20,
        "order": "popular"
    }

    try:
        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            print("⚠️ Background music skipped (API error)")
            return None

        tracks = r.json().get("hits", [])
        if not tracks:
            print("⚠️ No background music found for this query")
            return None

        track = random.choice(tracks)
        music_url = track["audio"]

        filename = f"bg_{track['id']}.mp3"
        filepath = os.path.join(MUSIC_DIR, filename)

        # Download only once (cache)
        if not os.path.exists(filepath):
            with requests.get(music_url, stream=True, timeout=10) as m:
                if m.status_code != 200:
                    print("⚠️ Failed to download background music")
                    return None

                with open(filepath, "wb") as f:
                    for chunk in m.iter_content(1024):
                        if chunk:
                            f.write(chunk)

        return filepath

    except Exception as e:
        print(f"⚠️ Background music skipped: {e}")
        return None