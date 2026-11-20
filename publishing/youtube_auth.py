"""YouTube OAuth 2.0 Authentication and Token Management."""

import os
from typing import Any, Optional
from core.logging_config import setup_logger

logger = setup_logger("neuralclips.youtube_auth")


class YouTubeAuth:
    """Manages YouTube Data API v3 OAuth2 credentials and token refreshing."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        self.client_id = client_id or os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("YOUTUBE_CLIENT_SECRET")
        self.refresh_token = refresh_token or os.getenv("YOUTUBE_REFRESH_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.refresh_token)

    def get_authorized_service(self) -> Any:
        """Returns an authorized Google API Client resource for YouTube Data API."""
        if not self.is_configured():
            logger.warning("YouTube OAuth credentials not fully configured; using mock service.")
            return None

        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            creds = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=["https://www.googleapis.com/auth/youtube.upload"],
            )

            # Refresh token if needed
            creds.refresh(Request())
            service = build("youtube", "v3", credentials=creds)
            return service
        except Exception as e:
            logger.error(f"Failed to build YouTube service: {e}")
            raise
