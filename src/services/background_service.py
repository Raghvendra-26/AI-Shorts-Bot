# src/services/background_service.py
import os
import uuid

from src.bg_fetcher import fetch_background_clips
from src.video_utils import concat_background_clips
from src.utils.fallback_background import create_fallback_background
from src.utils.logger import logger


def _expected_clip_count(duration: float) -> int:
    if duration <= 30:
        return 3
    if duration <= 45:
        return 4
    return 5


def build_background(
    idea: str,
    sentences: list[str],
    duration: float,
    output_dir: str
) -> str:
    """
    Builds a portrait-safe background video.

    Guarantees:
    - Always returns a valid video path
    - Falls back to generated background if fetch fails
    """

    try:
        expected = _expected_clip_count(duration)

        clips = fetch_background_clips(idea, expected)
        if not clips:
            raise RuntimeError("No background clips fetched")

        clip_duration = duration / expected
        durations = [clip_duration] * expected

        bg_video = concat_background_clips(clips, durations)
        return bg_video

    except Exception as e:
        logger.warning(f"⚠️ Background fetch failed, using fallback: {e}")

        fallback_path = os.path.join(
            output_dir,
            f"fallback_bg_{uuid.uuid4().hex[:6]}.mp4"
        )

        create_fallback_background(
            duration=duration,
            output_path=fallback_path
        )

        return fallback_path
