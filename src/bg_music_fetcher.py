import os
import random
import requests
import time
from dotenv import load_dotenv
from src.utils.logger import logger

load_dotenv()

# Openverse PUBLIC audio endpoint (NO AUTH REQUIRED)
SEARCH_URL = "https://api.openverse.engineering/v1/audio/"

CACHE_DIR = "assets/music_cache"

# ---------------- SAFETY LIMITS ---------------- #
MIN_BYTES = 120_000                 # reject junk
MAX_BYTES = 4 * 1024 * 1024          # 4 MB cap (enough for Shorts)
MAX_DOWNLOAD_SECONDS = 12            # hard wall-clock cap
CHUNK_SIZE = 128 * 1024              # 128 KB

os.makedirs(CACHE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "ai-shorts-bot/1.0"
}

# ---------------- MOOD LOGIC ---------------- #

MOOD_KEYWORDS = {
    "motivational": [
        "success", "discipline", "habits", "growth", "mindset",
        "rich", "goals", "focus", "grind", "consistency"
    ],
    "dark": [
        "dopamine", "fear", "addiction", "mistake",
        "dark", "psychology", "regret"
    ],
    "calm": [
        "calm", "peace", "focus", "deep work",
        "silence", "clarity", "mindfulness"
    ],
    "hype": [
        "win", "dominate", "beast", "champion",
        "attack", "power", "killer instinct"
    ]
}

MOOD_MUSIC = {
    "motivational": ["cinematic", "uplifting", "inspiring"],
    "dark": ["dark ambient", "atmospheric", "dramatic"],
    "calm": ["ambient", "soft piano", "minimal"],
    "hype": ["energetic", "upbeat", "pulse"],
    "neutral": ["cinematic", "ambient"]
}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def _safe_name(s: str) -> str:
    return "".join(c for c in s if c.isalnum() or c in ("_", "-")).lower()[:50]


def detect_mood(text: str) -> str:
    text = text.lower()
    for mood, words in MOOD_KEYWORDS.items():
        if any(w in text for w in words):
            return mood
    return "neutral"


def _download(url: str, uid: str, tag: str) -> str:
    """
    BOUNDED download:
    - Time limited
    - Size limited
    - Partial download allowed
    """
    fname = f"{uid}_{_safe_name(tag)}.mp3"
    path = os.path.join(CACHE_DIR, fname)

    if os.path.exists(path) and os.path.getsize(path) >= MIN_BYTES:
        return path

    logger.info(f"⬇️ Downloading music (bounded): {url}")

    start = time.time()
    total = 0

    try:
        with requests.get(
            url,
            headers=HEADERS,
            stream=True,
            timeout=6
        ) as r:
            r.raise_for_status()

            with open(path, "wb") as f:
                for chunk in r.iter_content(CHUNK_SIZE):
                    if not chunk:
                        break

                    f.write(chunk)
                    total += len(chunk)

                    # 🚨 Size cap
                    if total >= MAX_BYTES:
                        logger.warning("🎵 Music too large — stopping early")
                        break

                    # 🚨 Time cap
                    if time.time() - start >= MAX_DOWNLOAD_SECONDS:
                        logger.warning("🎵 Music download timeout — stopping")
                        break

    except Exception as e:
        logger.warning(f"🎵 Music download failed: {e}")
        if os.path.exists(path):
            os.remove(path)
        raise

    # Validate
    if not os.path.exists(path) or os.path.getsize(path) < MIN_BYTES:
        if os.path.exists(path):
            os.remove(path)
        raise RuntimeError("Downloaded music invalid or too small")

    return path


def _random_cached() -> str | None:
    files = [
        os.path.join(CACHE_DIR, f)
        for f in os.listdir(CACHE_DIR)
        if f.endswith(".mp3") and os.path.getsize(os.path.join(CACHE_DIR, f)) >= MIN_BYTES
    ]
    return random.choice(files) if files else None


# --------------------------------------------------
# MAIN FETCHER
# --------------------------------------------------

def fetch_background_music(text: str) -> str:
    """
    Mood-aware Openverse music fetcher.
    FAST, BOUNDED, NO HANGS.
    Silence is IMPOSSIBLE.
    """

    mood = detect_mood(text)
    keywords = MOOD_MUSIC.get(mood, MOOD_MUSIC["neutral"]).copy()
    random.shuffle(keywords)

    logger.info(f"🎼 Music mood detected: {mood}")

    # 1️⃣ Mood-based search
    for kw in keywords:
        try:
            r = requests.get(
                SEARCH_URL,
                headers=HEADERS,
                params={
                    "q": kw,
                    "page_size": 20,
                    "license_type": "commercial",
                    "duration": "60",
                },
                timeout=8,
            )
            r.raise_for_status()

            results = r.json().get("results", [])
            random.shuffle(results)

            for item in results:
                url = item.get("url")
                uid = item.get("id")

                if not url or not uid:
                    continue

                try:
                    path = _download(url, uid, kw)
                    logger.info(
                        f"🎵 Music selected (mood='{mood}', keyword='{kw}')"
                    )
                    return path
                except Exception:
                    continue

        except Exception as e:
            logger.warning(f"🎵 Openverse search failed: {e}")
            continue

    # 2️⃣ Random Openverse fallback
    try:
        r = requests.get(
            SEARCH_URL,
            headers=HEADERS,
            params={
                "page_size": 40,
                "license_type": "commercial",
            },
            timeout=8,
        )
        r.raise_for_status()

        results = r.json().get("results", [])
        random.shuffle(results)

        for item in results:
            url = item.get("url")
            uid = item.get("id")

            if url and uid:
                logger.warning("🎵 Openverse random fallback used")
                return _download(url, uid, "random")

    except Exception:
        pass

    # 3️⃣ Cache fallback (absolute last resort)
    cached = _random_cached()
    if cached:
        logger.warning("🎵 Using cached music fallback")
        return cached

    # ❌ Silence NOT allowed
    raise RuntimeError("❌ No usable Openverse background music found")
