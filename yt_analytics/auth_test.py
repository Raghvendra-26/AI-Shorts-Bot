from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly"
]

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials/client_secret.json",
    SCOPES
)

credentials = flow.run_local_server(port=0)

youtube_analytics = build(
    "youtubeAnalytics", "v2", credentials=credentials
)

print("YouTube Analytics API connected successfully ✅")
