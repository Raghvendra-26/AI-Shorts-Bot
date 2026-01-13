from datetime import date, timedelta

from .auth import get_analytics_client
from .config import CHANNEL_ID
from .fetch_videos import fetch_videos   # assumes this returns video_ids


def fetch_video_analytics(video_id, start_date, end_date, analytics):
    response = analytics.reports().query(
        ids=f"channel=={CHANNEL_ID}",
        startDate=start_date,
        endDate=end_date,
        metrics="views,estimatedMinutesWatched,averageViewDuration",
        filters=f"video=={video_id}"
    ).execute()

    rows = response.get("rows", [])
    if not rows:
        return None

    views, minutes_watched, avg_view_duration = rows[0]

    return {
        "video_id": video_id,
        "views": views,
        "minutes_watched": minutes_watched,
        "avg_view_duration": avg_view_duration,
    }


# inside fetch_shorts_analytics.py

def fetch_shorts_analytics(days=14):
    analytics = get_analytics_client()

    start_date = (date.today() - timedelta(days=days)).isoformat()
    end_date = date.today().isoformat()

    videos = fetch_videos()
    video_ids = list(videos.keys())

    results = {}

    for vid in video_ids:
        response = analytics.reports().query(
            ids=f"channel=={CHANNEL_ID}",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched,averageViewDuration",
            filters=f"video=={vid}"
        ).execute()

        rows = response.get("rows", [])
        if not rows:
            continue

        views, minutes_watched, avg_view_duration = rows[0]

        results[vid] = {
            "views": views,
            "minutes_watched": minutes_watched,
            "avg_view_duration": avg_view_duration
        }

    return results


if __name__ == "__main__":
    fetch_shorts_analytics()


# TODO: filter shorts using duration < 60s when long-form videos exist