def bg_query_from_niche(niche: str) -> str:
    mapping = {
        "football": "cinematic sports",
        "self improvement": "ambient motivational",
        "technology": "futuristic ambient",
        "finance": "calm corporate",
        "psychology": "dark ambient",
        "default": "ambient"
    }

    return mapping.get(niche.lower(), mapping["default"])