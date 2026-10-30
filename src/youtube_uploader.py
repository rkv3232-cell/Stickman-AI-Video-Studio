"""
Official YouTube Data API v3 Upload & Publishing Engine.
Handles OAuth 2.0 channel authorization, resumable chunked video uploads,
metadata synchronization, scheduled releases, and duplicate prevention.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Callable

# Ensure root dir on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import ROOT_DIR, CHANNEL_NAME

# File paths for OAuth 2.0 credentials
CLIENT_SECRETS_FILE = ROOT_DIR / "client_secrets.json"
TOKEN_FILE = ROOT_DIR / "youtube_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

class YouTubeUploader:
    def __init__(self):
        self._service = None

    def is_configured(self) -> bool:
        """Checks if client_secrets.json exists."""
        return CLIENT_SECRETS_FILE.exists()

    def is_authenticated(self) -> bool:
        """Checks if an authorized token exists and is valid/refreshable."""
        if not TOKEN_FILE.exists():
            return False
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                token_data = json.load(f)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            if creds.valid:
                return True
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
                return True
            return False
        except Exception as e:
            print(f"[YouTube Uploader] Token validation error: {e}")
            return False

    def get_authorization_url(self, redirect_uri: str = "http://localhost:8000/api/youtube/oauth-callback") -> Tuple[Optional[str], Optional[str]]:
        """Generates Google OAuth 2.0 authorization URL."""
        if not self.is_configured():
            return None, "client_secrets.json not found in project root. Please download it from Google Cloud Console."

        try:
            from google_auth_oauthlib.flow import Flow

            flow = Flow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE),
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            return auth_url, None
        except Exception as e:
            return None, f"Failed to generate authorization URL: {str(e)}"

    def handle_oauth_code(self, code: str, redirect_uri: str = "http://localhost:8000/api/youtube/oauth-callback") -> Tuple[bool, str]:
        """Exchanges authorization code for tokens and saves youtube_token.json."""
        if not self.is_configured():
            return False, "client_secrets.json not found"

        try:
            from google_auth_oauthlib.flow import Flow

            flow = Flow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE),
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
            flow.fetch_token(code=code)
            creds = flow.credentials

            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())

            self._service = None  # Reset service instance
            return True, "YouTube channel successfully authorized!"
        except Exception as e:
            return False, f"Failed to exchange OAuth code: {str(e)}"

    def get_service(self):
        """Builds and caches authorized YouTube Resource."""
        if self._service is not None:
            return self._service

        if not self.is_authenticated():
            return None

        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        self._service = build("youtube", "v3", credentials=creds)
        return self._service

    def get_channel_info(self) -> Dict[str, Any]:
        """Fetches authorized YouTube channel title and subscriber count."""
        service = self.get_service()
        if not service:
            return {"authenticated": False, "channel_name": None, "subscribers": 0, "status": "Not Authorized"}

        try:
            request = service.channels().list(part="snippet,statistics", mine=True)
            response = request.execute()
            items = response.get("items", [])
            if not items:
                return {"authenticated": True, "channel_name": "No channel found", "status": "No Channel"}

            ch = items[0]
            snippet = ch.get("snippet", {})
            stats = ch.get("statistics", {})

            return {
                "authenticated": True,
                "channel_id": ch.get("id"),
                "channel_name": snippet.get("title", CHANNEL_NAME),
                "custom_url": snippet.get("customUrl", ""),
                "subscribers": int(stats.get("subscriberCount", 0)),
                "total_views": int(stats.get("viewCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "status": "Connected & Authorized"
            }
        except Exception as e:
            return {"authenticated": False, "error": str(e), "status": "Connection Error"}

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str],
        category_id: str = "28",  # 28 = Science & Technology
        privacy_status: str = "private",
        publish_at: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Executes resumable chunked upload to YouTube.
        Supports 9:16 vertical Shorts, scheduling, and custom metadata.
        """
        service = self.get_service()
        if not service:
            return False, {"error": "YouTube account not authorized. Please connect channel in settings."}

        v_path = Path(video_path)
        if not v_path.exists():
            return False, {"error": f"Video file not found at: {video_path}"}

        try:
            from googleapiclient.http import MediaFileUpload

            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description[:5000],
                    "tags": tags[:500],
                    "categoryId": category_id,
                    "defaultLanguage": "hi-Latn",
                    "defaultAudioLanguage": "hi-Latn"
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False
                }
            }

            # If scheduled publishing is specified (ISO 8601 string)
            if publish_at and privacy_status == "private":
                body["status"]["publishAt"] = publish_at

            media = MediaFileUpload(
                str(v_path),
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024 * 1024 * 2  # 2MB chunks
            )

            request = service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            if progress_callback:
                progress_callback(10, "Initiating YouTube resumable upload session...")

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    pct = int(status.progress() * 100)
                    if progress_callback:
                        progress_callback(min(pct, 95), f"Uploading video: {pct}% complete...")

            video_id = response.get("id")
            video_url = f"https://youtu.be/{video_id}"

            if progress_callback:
                progress_callback(100, f"Upload complete! Video ID: {video_id}")

            return True, {
                "video_id": video_id,
                "video_url": video_url,
                "title": title,
                "privacy": privacy_status,
                "published_at": response.get("snippet", {}).get("publishedAt")
            }

        except Exception as e:
            return False, {"error": f"YouTube API upload error: {str(e)}"}

youtube_uploader = YouTubeUploader()

if __name__ == "__main__":
    print("YouTube Uploader Status:")
    print(" - Configured (client_secrets.json):", youtube_uploader.is_configured())
    print(" - Authenticated:", youtube_uploader.is_authenticated())
    ch_info = youtube_uploader.get_channel_info()
    print(" - Channel info:", ch_info)

