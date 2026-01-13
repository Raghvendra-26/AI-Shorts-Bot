from yt_analytics.auth import get_youtube_client

youtube = get_youtube_client()

response = youtube.channels().list(
    part="snippet,statistics",
    mine=True
).execute()

print("\nYour YouTube Channels:\n")

for item in response.get("items", []):
    print("Channel Name :", item["snippet"]["title"])
    print("Channel ID   :", item["id"])
    print("-" * 40)
