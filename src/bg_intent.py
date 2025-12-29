# src/bg_intent.py

import re

# ---------- KEYWORDS ---------- #

SPORTS = {"football", "soccer", "goal", "messi", "ronaldo", "athlete", "training"}
MINDSET = {"mindset", "discipline", "confidence", "mental", "focus"}
PRODUCTIVITY = {"productive", "routine", "habits", "work", "practice"}
HEALTH = {"health", "dopamine", "addiction", "sleep", "exercise"}
TECH = {"ai", "technology", "future", "machine", "automation"}
MONEY = {"money", "rich", "wealth", "finance", "business"}

INTENSE = {"monster", "dominate", "destroy", "grind", "hard"}
CALM = {"peace", "calm", "slow", "balance", "healthy"}
ENERGETIC = {"fast", "energy", "power", "action"}
CINEMATIC = {"story", "journey", "legacy", "history"}

# ---------- HELPERS ---------- #

def _contains(words, text):
    return any(w in text for w in words)


# ---------- CORE LOGIC ---------- #

def detect_category(idea: str) -> str:
    text = idea.lower()

    if _contains(SPORTS, text):
        return "sports"
    if _contains(MINDSET, text):
        return "mindset"
    if _contains(PRODUCTIVITY, text):
        return "productivity"
    if _contains(HEALTH, text):
        return "health"
    if _contains(TECH, text):
        return "tech"
    if _contains(MONEY, text):
        return "money"

    return "generic"


def detect_mood(idea: str) -> str:
    text = idea.lower()

    if _contains(INTENSE, text):
        return "intense"
    if _contains(ENERGETIC, text):
        return "energetic"
    if _contains(CALM, text):
        return "calm"
    if _contains(CINEMATIC, text):
        return "cinematic"

    return "neutral"


def build_video_queries(idea: str) -> list[str]:
    category = detect_category(idea)
    mood = detect_mood(idea)

    queries = []

    # ---------- SPORTS ---------- #
    if category == "sports":
        queries.extend([
            "football training slow motion",
            "athlete training alone",
            "soccer practice cinematic",
        ])

    # ---------- MINDSET ---------- #
    elif category == "mindset":
        queries.extend([
            "focused man thinking",
            "person standing alone city night",
            "cinematic self improvement background",
        ])

    # ---------- PRODUCTIVITY ---------- #
    elif category == "productivity":
        queries.extend([
            "man working late desk",
            "daily routine lifestyle",
            "focused work cinematic",
        ])

    # ---------- HEALTH ---------- #
    elif category == "health":
        queries.extend([
            "healthy lifestyle morning routine",
            "man exercising sunrise",
            "mental health calm background",
        ])

    # ---------- TECH ---------- #
    elif category == "tech":
        queries.extend([
            "artificial intelligence abstract",
            "technology future cinematic",
            "coding dark room screen",
        ])

    # ---------- MONEY ---------- #
    elif category == "money":
        queries.extend([
            "business success cinematic",
            "city skyline night wealth",
            "entrepreneur working late",
        ])

    # ---------- FALLBACK ---------- #
    queries.append("cinematic motivational background")

    # ---------- MOOD BOOST ---------- #
    if mood == "intense":
        queries.insert(0, "intense cinematic background")
    elif mood == "calm":
        queries.insert(0, "calm cinematic background")
    elif mood == "energetic":
        queries.insert(0, "high energy cinematic background")

    # Remove duplicates, preserve order
    seen = set()
    final_queries = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            final_queries.append(q)

    return final_queries
