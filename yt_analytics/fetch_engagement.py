from .auth import get_youtube_client
from .fetch_videos import fetch_videos


def fetch_engagement():
    """
    Fetch likes & comments for recent videos of the channel.
    Returns a dict keyed by video_id.
    """
    youtube = get_youtube_client()

    videos = fetch_videos()
    video_ids = list(videos.keys())

    if not video_ids:
        return {}

    response = youtube.videos().list(
        part="statistics,contentDetails",
        id=",".join(video_ids)
    ).execute()

    stats = {}

    for item in response.get("items", []):
        vid = item["id"]
        s = item["statistics"]

        stats[vid] = {
            "likes": int(s.get("likeCount", 0)),
            "comments": int(s.get("commentCount", 0))
        }

    return stats


# 🔽 Runs ONLY when file is executed directly
if __name__ == "__main__":
    data = fetch_engagement()

    print("\nEngagement Metrics:\n")
    for vid, stats in data.items():
        print(
            f"Video: {vid} | "
            f"Likes: {stats['likes']} | "
            f"Comments: {stats['comments']}"
        )

    print(f"\nFetched engagement for {len(data)} videos")
