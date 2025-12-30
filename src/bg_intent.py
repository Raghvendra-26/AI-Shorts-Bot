# src/bg_intent.py

from src.visual_intent import build_visual_queries


def build_video_queries(idea: str) -> list[str]:
    """
    Unified entry point for background video intent.
    Delegates to visual_intent system.
    """
    return build_visual_queries(idea)
