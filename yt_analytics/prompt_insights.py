from .merge_analytics import merge_analytics


def derive_prompt_insights(days=14):
    """
    Derive prompt conditioning insights from analytics.
    """
    data = merge_analytics(days=days)

    strong_hooks = []
    weak_hooks = []

    for video in data.values():
        if video["hook_strength"] == "strong":
            strong_hooks.append(video["title"])
        elif video["hook_strength"] == "weak":
            weak_hooks.append(video["title"])

    return {
        "strong_hook_examples": strong_hooks[:5],
        "weak_hook_examples": weak_hooks[:5],
    }
