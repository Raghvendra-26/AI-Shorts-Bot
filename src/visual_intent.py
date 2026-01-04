# src/visual_intent.py

import re
import random
from collections import Counter

# ---------------- BASIC FILTERS ---------------- #

STOPWORDS = {
    "the", "is", "are", "was", "were", "why", "how", "what",
    "you", "your", "they", "them", "this", "that", "these",
    "those", "and", "or", "but", "if", "then", "because",
    "to", "of", "in", "on", "with", "for", "as", "by",
}

# ---------------- VISUAL SEMANTICS ---------------- #

ABSTRACT_TO_CONCRETE = {
    "discipline": ["waking up early", "training alone", "daily routine"],
    "focus": ["deep work", "concentration", "thinking intensely"],
    "success": ["achievement moment", "winning", "goal reached"],
    "failure": ["disappointment", "exhaustion", "setback moment"],
    "growth": ["self improvement", "progress journey", "practice routine"],
    "money": ["financial thinking", "business work", "wealth lifestyle"],
    "brain": ["thinking", "mental process", "decision making"],
    "mind": ["thoughts", "overthinking", "inner conflict"],
    "life": ["real life moment", "daily routine", "human behavior"],
    "habit": ["repeated action", "morning routine", "night routine"],
    "sleep": ["tired person", "late night thinking", "restlessness"],
}

ACTIONS = [
    "thinking",
    "working",
    "walking",
    "training",
    "sitting alone",
    "looking at screen",
    "writing",
    "reflecting",
]

TIMES = [
    "night",
    "early morning",
    "sunrise",
    "late evening",
]

CAMERA_STYLES = [
    "cinematic",
    "slow motion",
    "close up",
    "wide shot",
    "handheld",
]

MOODS = [
    "moody lighting",
    "soft light",
    "dramatic shadows",
    "natural light",
]

GENERIC_FALLBACKS = [
    "cinematic abstract background motion",
    "soft bokeh cinematic lights",
    "slow motion abstract visuals",
]

# ---------------- TOPIC BIAS ---------------- #

def classify_topic_bias(idea: str) -> str:
    text = idea.lower()

    if any(k in text for k in ["brain", "mind", "psychology", "thinking"]):
        return "indoor"
    if any(k in text for k in ["focus", "habit", "study", "work"]):
        return "desk"
    if any(k in text for k in ["success", "win", "goal", "achieve"]):
        return "outdoor"
    if any(k in text for k in ["failure", "mistake", "loss", "dark"]):
        return "dark"
    if any(k in text for k in ["money", "business", "wealth"]):
        return "office"

    return "mixed"


SCENE_BIAS = {
    "indoor": ["dark room", "bedroom", "home interior"],
    "desk": ["desk setup", "workspace", "office desk"],
    "outdoor": ["city street", "outdoor urban", "open road"],
    "office": ["corporate office", "business workspace", "city office"],
    "dark": ["dark room", "low light interior", "moody indoor"],
    "mixed": [
        "dark room",
        "office",
        "city street",
        "home interior",
        "outdoor urban",
    ],
}

# ---------------- KEYWORD EXTRACTION ---------------- #

def extract_keywords(text: str, top_k: int = 5) -> list[str]:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    words = [w for w in words if w not in STOPWORDS]

    if not words:
        return []

    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_k)]


# ---------------- QUERY BUILDER ---------------- #

def _build_dynamic_query(base: str, bias: str) -> str:
    """
    Build a visually rich, topic-aware search query
    """
    scenes = SCENE_BIAS.get(bias, SCENE_BIAS["mixed"])

    parts = [
        base,
        random.choice(ACTIONS),
        random.choice(scenes),
        random.choice(TIMES),
        random.choice(CAMERA_STYLES),
        random.choice(MOODS),
    ]

    return " ".join(parts)


def build_visual_queries(idea: str, max_queries: int = 12) -> list[str]:
    """
    Convert idea → diverse, topic-connected visual queries
    """
    keywords = extract_keywords(idea)
    bias = classify_topic_bias(idea)

    queries: list[str] = []

    for kw in keywords:
        bases = ABSTRACT_TO_CONCRETE.get(kw, [kw])

        for base in bases:
            queries.append(_build_dynamic_query(base, bias))

    # Shuffle so same idea ≠ same order
    random.shuffle(queries)

    # Always add safe cinematic fallbacks
    queries.extend(GENERIC_FALLBACKS)

    # Deduplicate while preserving order
    seen = set()
    final = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            final.append(q)
        if len(final) >= max_queries:
            break

    return final
