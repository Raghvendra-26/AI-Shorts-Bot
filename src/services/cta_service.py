import random
import re
import os

from src.tts_edge import text_to_speech
from src.text_utils import sanitize_for_tts
from src.utils.audio_utils import get_audio_duration


CTA_FALLBACK_POOL = [
    "Follow for more!",
    "Subscribe for more shorts!",
    "Like and follow!",
    "Follow for daily facts!",
]


def is_tts_safe(text: str) -> bool:
    if not text or len(text.split()) < 3:
        return False
    if not re.search(r"[aeiouAEIOU]", text):
        return False
    return True


def generate_cta(idea: str, body_duration: float):
    fallback = random.choice(CTA_FALLBACK_POOL)

    try:
        audio = text_to_speech(sanitize_for_tts(fallback))
        duration = get_audio_duration(audio)

        if body_duration + duration <= 59:
            return fallback, audio, duration

    except Exception:
        pass

    return None, None, 0.0
