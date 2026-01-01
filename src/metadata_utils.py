import re
from typing import Dict, List


# -------------------------
# Helpers
# -------------------------

def _clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", text.lower())


# -------------------------
# TITLE (IDEA → TITLE)
# -------------------------

def generate_title_from_idea(idea: str) -> str:
    """
    Converts idea into a Shorts-safe title.
    - Idea is source of truth
    - No clickbait
    - No hallucination
    """
    title = _clean(idea)

    # Capitalize first letter safely
    title = title[0].upper() + title[1:]

    # Hard limit for YouTube Shorts
    if len(title) > 60:
        title = title[:57].rsplit(" ", 1)[0] + "..."

    return title


# -------------------------
# DESCRIPTION
# -------------------------

def generate_description(idea: str, script: str) -> str:
    return (
        f"{idea.strip()}.\n\n"
        "👍 Like the video if you found this interesting\n"
        "🔔 Subscribe for more short facts and insights\n"
        "💬 Comment your thoughts below\n\n"
        "Daily shorts on facts, psychology, and self-improvement."
    )


# -------------------------
# HASHTAGS (IDEA + SCRIPT)
# -------------------------

def generate_hashtags(idea: str, script: str) -> List[str]:
    """
    Generates 10–12 YouTube-safe hashtags.
    Structured for Shorts discovery.
    """
    text = _normalize(idea + " " + script)

    hashtags: List[str] = []

    # 1️⃣ Mandatory platform tag
    hashtags.append("#shorts")

    # 2️⃣ Core topic tags (derived from idea/script)
    KEYWORD_TAGS = {
        "brain": "#brain",
        "mind": "#mind",
        "psychology": "#psychology",
        "habit": "#habits",
        "focus": "#focus",
        "sleep": "#sleep",
        "health": "#health",
        "money": "#money",
        "success": "#success",
        "motivation": "#motivation",
    }

    for key, tag in KEYWORD_TAGS.items():
        if key in text and tag not in hashtags:
            hashtags.append(tag)
        if len(hashtags) >= 6:  # cap topic tags
            break

    # 3️⃣ Niche / content-type tags
    NICHE_TAGS = [
        "#facts",
        "#selfimprovement",
        "#learning",
        "#knowledge",
    ]

    for tag in NICHE_TAGS:
        if len(hashtags) < 9:
            hashtags.append(tag)

    # 4️⃣ Discovery / reach tags
    DISCOVERY_TAGS = [
        "#viral",
        "#trending",
        "#foryou",
    ]

    for tag in DISCOVERY_TAGS:
        if len(hashtags) < 12:
            hashtags.append(tag)

    return hashtags


# -------------------------
# MAIN API
# -------------------------

def generate_metadata(idea: str, script: str) -> Dict:
    return {
        "title": generate_title_from_idea(idea),
        "description": generate_description(idea, script),
        "hashtags": generate_hashtags(idea, script),
    }
