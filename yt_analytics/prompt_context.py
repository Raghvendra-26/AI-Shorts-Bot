from yt_analytics.prompt_insights import derive_prompt_insights


def build_prompt_with_insights(base_prompt: str) -> str:
    """
    Safely enrich the generation prompt with analytics-based insights.
    Falls back silently if analytics is unavailable.
    """
    try:
        insights = derive_prompt_insights()

        strong = insights.get("strong_hook_examples", [])
        weak = insights.get("weak_hook_examples", [])

        if not strong and not weak:
            return base_prompt

        insight_block = "\n\n".join([
            "Channel performance insights:",
            (
                "High-retention hook examples:\n"
                + "\n".join(f"- {t}" for t in strong)
                if strong else ""
            ),
            (
                "Low-retention hook examples to avoid:\n"
                + "\n".join(f"- {t}" for t in weak)
                if weak else ""
            ),
            "Guidelines:",
            "- Strong hook in first 2 seconds",
            "- Direct second-person address",
            "- Short, punchy sentences",
        ])

        return insight_block + "\n\n" + base_prompt

    except Exception:
        # ⚠️ Analytics should NEVER break generation
        return base_prompt
