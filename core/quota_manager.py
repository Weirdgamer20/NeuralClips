"""API Quota and Rate Limit Manager for YouTube, Instagram, and Gemini."""

import os
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from core.database import get_connection

# YouTube Data API costs
YOUTUBE_UPLOAD_COST = 1600
YOUTUBE_DEFAULT_DAILY_LIMIT = 10000

# Instagram Graph API limits
INSTAGRAM_DEFAULT_DAILY_LIMIT = 50

# Gemini Flash API limits
GEMINI_DEFAULT_RPM = 60
GEMINI_DEFAULT_RPD = 1500


class QuotaManager:
    """Monitors and enforces daily API quotas and rolling publishing rate limits."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _today_str(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def get_quota_status(self, platform: str) -> Dict[str, int]:
        """Returns units used, daily limit, and remaining units for platform."""
        today = self._today_str()
        conn = get_connection(self.db_path)
        try:
            with conn:
                row = conn.execute(
                    "SELECT units_used, units_limit FROM api_quota_usage WHERE usage_date = ? AND platform = ?",
                    (today, platform.upper()),
                ).fetchone()

                if platform.upper() == "YOUTUBE":
                    env_limit = int(os.getenv("MAX_YOUTUBE_QUOTA_UNITS", YOUTUBE_DEFAULT_DAILY_LIMIT))
                elif platform.upper() == "INSTAGRAM":
                    env_limit = int(os.getenv("MAX_INSTAGRAM_UPLOADS_DAILY", INSTAGRAM_DEFAULT_DAILY_LIMIT))
                else:
                    env_limit = 1000

                if row:
                    used = row["units_used"]
                    limit = max(row["units_limit"], env_limit)
                else:
                    used = 0
                    limit = env_limit

                remaining = max(0, limit - used)
                return {"used": used, "limit": limit, "remaining": remaining}
        finally:
            conn.close()

    def can_publish_youtube(self) -> Tuple[bool, str]:
        """Checks if there is enough YouTube quota to publish a video (costs 1600 units)."""
        status = self.get_quota_status("YOUTUBE")
        if status["remaining"] < YOUTUBE_UPLOAD_COST:
            return False, f"Insufficient YouTube API quota ({status['remaining']}/{status['limit']} units remaining, requires {YOUTUBE_UPLOAD_COST})"
        return True, "Quota available"

    def record_youtube_upload(self) -> None:
        """Deducts 1600 units for YouTube upload."""
        self._record_usage("YOUTUBE", YOUTUBE_UPLOAD_COST, int(os.getenv("MAX_YOUTUBE_QUOTA_UNITS", YOUTUBE_DEFAULT_DAILY_LIMIT)))

    def can_publish_instagram(self) -> Tuple[bool, str]:
        """Checks if daily Instagram Reel limit has been reached."""
        status = self.get_quota_status("INSTAGRAM")
        if status["remaining"] < 1:
            return False, f"Instagram daily upload limit reached ({status['used']}/{status['limit']} uploads)"
        return True, "Capacity available"

    def record_instagram_upload(self) -> None:
        """Records an Instagram reel publication."""
        self._record_usage("INSTAGRAM", 1, int(os.getenv("MAX_INSTAGRAM_UPLOADS_DAILY", INSTAGRAM_DEFAULT_DAILY_LIMIT)))

    def _record_usage(self, platform: str, units: int, limit: int) -> None:
        today = self._today_str()
        now_iso = datetime.now(timezone.utc).isoformat()
        conn = get_connection(self.db_path)
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO api_quota_usage (usage_date, platform, units_used, units_limit, last_reset)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(usage_date, platform) DO UPDATE SET
                        units_used = units_used + excluded.units_used,
                        last_reset = excluded.last_reset
                    """,
                    (today, platform.upper(), units, limit, now_iso),
                )
        finally:
            conn.close()
