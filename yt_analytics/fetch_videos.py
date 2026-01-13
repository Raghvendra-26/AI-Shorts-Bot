from .auth import get_youtube_client
from .config import CHANNEL_ID


def fetch_videos(max_results=50):
    """
    Fetch recent videos from the channel.
    Returns dict keyed by video_id with title & published_at.
    """
    youtube = get_youtube_client()

    request = youtube.search().list(
        part="id,snippet",
        channelId=CHANNEL_ID,
        maxResults=max_results,
        order="date",
        type="video"
    )

    response = request.execute()

    videos = {}

    for item in response.get("items", []):
        vid = item["id"]["videoId"]
        videos[vid] = {
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"]
        }

    return videos


if __name__ == "__main__":
    data = fetch_videos()
    print(f"Fetched {len(data)} videos")
    for vid, meta in list(data.items()):
        print(vid, meta)
