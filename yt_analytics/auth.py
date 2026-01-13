from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly"
]

TOKEN_PATH = "credentials/token.json"
CLIENT_SECRET = "credentials/client_secret.json"


def get_credentials():
    if os.path.exists(TOKEN_PATH):
        return Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET,
        SCOPES
    )
    creds = flow.run_local_server(port=0)

    with open(TOKEN_PATH, "w") as token:
        token.write(creds.to_json())

    return creds


def get_analytics_client():
    creds = get_credentials()
    return build("youtubeAnalytics", "v2", credentials=creds)


def get_youtube_client():
    creds = get_credentials()
    return build("youtube", "v3", credentials=creds)
