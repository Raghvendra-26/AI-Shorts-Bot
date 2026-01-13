from .fetch_videos import fetch_videos
from .fetch_shorts_analytics import fetch_shorts_analytics
from .fetch_engagement import fetch_engagement


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

        views = a["views"]
        avg_view_duration = a["avg_view_duration"]

        retention_score = avg_view_duration / 60 if views > 0 else 0

        merged[video_id] = {
            "title": meta["title"],                       # ✅ NEW
            "published_at": meta["published_at"],
            "views": views,
            "minutes_watched": a["minutes_watched"],
            "avg_view_duration": avg_view_duration,
            "likes": e.get("likes", 0),
            "comments": e.get("comments", 0),
            "retention_score": round(retention_score, 3)
        }

    return merged


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
            f"Retention: {stats['retention_score']}"
        )

    print(f"\nMerged {len(data)} videos")
