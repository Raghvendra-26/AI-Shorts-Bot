# src/visual_intent.py

import re
from collections import Counter

# Words that add no visual meaning
STOPWORDS = {
    "the", "is", "are", "was", "were", "why", "how", "what",
    "you", "your", "they", "them", "this", "that", "these",
    "those", "and", "or", "but", "if", "then", "because",
    "to", "of", "in", "on", "with", "for", "as", "by",
}

# Map abstract ideas → concrete visuals
VISUAL_EXPANSIONS = {
    "discipline": [
        "man waking up early dark room",
        "athlete training alone sunrise",
        "person resisting temptation cinematic",
    ],
    "focus": [
        "man concentrating desk night",
        "deep focus work dark room",
        "focused eyes cinematic close up",
    ],
    "success": [
        "athlete winning slow motion",
        "business success city night",
        "man standing alone mountain top",
    ],
    "failure": [
        "man sitting alone defeated",
        "athlete exhausted after loss",
        "dark room emotional moment",
    ],
    "growth": [
        "man improving daily routine",
        "training progress montage",
        "sunrise journey cinematic",
    ],
    "money": [
        "city skyline night wealth",
        "entrepreneur working late office",
        "luxury lifestyle cinematic",
    ],
    "life": [
        "real life moments cinematic",
        "people walking city slow motion",
        "human behavior documentary style",
    ],
}

GENERIC_VISUALS = [
    "cinematic abstract motion background",
    "moody cinematic lighting",
    "cinematic bokeh light motion",
]


def extract_keywords(text: str, top_k: int = 5) -> list[str]:
    """
    Extract most important words from idea
    """
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    words = [w for w in words if w not in STOPWORDS]

    if not words:
        return []

    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_k)]


def build_visual_queries(idea: str) -> list[str]:
    """
    Convert idea → high-quality visual search queries
    """
    keywords = extract_keywords(idea)
    queries: list[str] = []

    # Expand abstract ideas into visuals
    for kw in keywords:
        if kw in VISUAL_EXPANSIONS:
            queries.extend(VISUAL_EXPANSIONS[kw])
        else:
            # Generic semantic fallback
            queries.append(f"{kw} cinematic background")
            queries.append(f"{kw} real life footage")

    # Always add safe cinematic fallbacks
    queries.extend(GENERIC_VISUALS)

    # Deduplicate (preserve order)
    seen = set()
    final = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            final.append(q)

    return final
