from .fetch_videos import fetch_videos
from .fetch_shorts_analytics import fetch_shorts_analytics
from .fetch_engagement import fetch_engagement
from .scoring import score_video
from .classify import classify_hook


def merge_analytics(days=14):
    videos = fetch_videos()
    analytics_data = fetch_shorts_analytics(days=days)
    engagement_data = fetch_engagement()

    merged = {}

    for video_id, meta in videos.items():
        a = analytics_data.get(video_id)
        if not a:
            continue

        e = engagement_data.get(video_id, {})

        # --- base stats ---
        views = a["views"]
        avg_view_duration = a["avg_view_duration"]
        likes = e.get("likes", 0)
        comments = e.get("comments", 0)

        # --- scoring (single source of truth) ---
        scores = score_video({
            "views": views,
            "avg_view_duration": avg_view_duration,
            "likes": likes,
            "comments": comments,
        })

        retention_score = scores["retention_score"]

        merged[video_id] = {
            "title": meta["title"],
            "published_at": meta["published_at"],

            # raw metrics
            "views": views,
            "minutes_watched": a["minutes_watched"],
            "avg_view_duration": avg_view_duration,
            "likes": likes,
            "comments": comments,

            # scores
            "retention_score": retention_score,
            "engagement_score": scores["engagement_score"],
            "hook_strength": classify_hook(retention_score),
        }

    return merged


# 🔽 Run only when executed directly
if __name__ == "__main__":
    data = merge_analytics()

    print("\nMerged Analytics:\n")
    for vid, stats in data.items():
        print(
            f"{stats['title']} | "
            f"Views: {stats['views']} | "
            f"AVD: {stats['avg_view_duration']:.2f}s | "
            f"Likes: {stats['likes']} | "
            f"Comments: {stats['comments']} | "
            f"Retention: {stats['retention_score']} | "
            f"Engagement: {stats['engagement_score']} | "
            f"Hook: {stats['hook_strength']}"
        )

    print(f"\nMerged {len(data)} videos")
