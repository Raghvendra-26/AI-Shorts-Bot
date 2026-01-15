def score_video(stats, short_duration=60):
    """
    Compute retention & engagement scores for a video.
    """
    views = stats.get("views", 0)
    avg_view_duration = stats.get("avg_view_duration", 0)
    likes = stats.get("likes", 0)
    comments = stats.get("comments", 0)

    retention_score = (
        avg_view_duration / short_duration
        if short_duration > 0 else 0
    )

    engagement_score = (
        (likes + comments) / views
        if views > 0 else 0
    )   

    return {
        "retention_score": round(retention_score, 3),
        "engagement_score": round(engagement_score, 3)
    }
