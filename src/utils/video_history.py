import json
import os
import time
from typing import Set

HISTORY_PATH = "assets/video_history.json"
MAX_AGE_SECONDS = 7 * 24 * 3600  # 7 days


def _load_history() -> dict:
    if not os.path.exists(HISTORY_PATH):
        return {}
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_history(data: dict):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_recent_video_ids(platform: str) -> Set[str]:
    data = _load_history()
    now = time.time()

    entries = data.get(platform, {})
    return {
        vid for vid, ts in entries.items()
        if now - ts < MAX_AGE_SECONDS
    }


def mark_video_used(platform: str, video_id: str):
    data = _load_history()
    data.setdefault(platform, {})
    data[platform][video_id] = time.time()
    _save_history(data)
