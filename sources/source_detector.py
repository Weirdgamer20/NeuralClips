"""Source Detector and Classifier implementing Part 6 requirements."""

from typing import Any, Dict
from permissions.permission_registry import PermissionRegistry
from permissions.rights_validator import RightsValidator
from sources.url_validator import validate_youtube_url
from sources.youtube_source import YouTubeSourceInspector


class SourceDetector:
    """Classifies incoming URLs and validates source rights."""

    def __init__(
        self,
        inspector: YouTubeSourceInspector = None,
        permission_registry: PermissionRegistry = None,
    ):
        self.inspector = inspector or YouTubeSourceInspector()
        self.permission_registry = permission_registry or PermissionRegistry()

    def classify_source(self, url: str) -> Dict[str, Any]:
        """Classifies a URL into its pipeline status and verified metadata."""
        # 1. URL syntax validation
        valid_syntax, video_id, err_msg = validate_youtube_url(url)
        if not valid_syntax:
            return {
                "url": url,
                "video_id": None,
                "status": "UNAVAILABLE",
                "error": err_msg,
                "channel_id": None,
                "permission_verified": False,
            }

        # 2. Inspect YouTube metadata
        meta = self.inspector.inspect_video(video_id)
        if not meta.get("available"):
            code = meta.get("status_code", "UNAVAILABLE")
            return {
                "url": url,
                "video_id": video_id,
                "status": code,
                "error": meta.get("error", "Source unavailable"),
                "channel_id": None,
                "permission_verified": False,
            }

        channel_id = meta.get("channel_id")
        title = meta.get("title")

        # 3. Check rights authorization
        perm = self.permission_registry.get_permission(channel_id)
        has_rights, rights_reason = RightsValidator.validate_rights(perm)

        if not has_rights:
            return {
                "url": url,
                "video_id": video_id,
                "status": "PERMISSION_REQUIRED",
                "error": f"Rights check failed: {rights_reason}",
                "channel_id": channel_id,
                "channel_title": meta.get("channel_title"),
                "title": title,
                "permission_verified": False,
                "permission_record": perm,
            }

        # 4. Map broadcast state to pipeline status
        if meta.get("is_live"):
            status = "ACTIVE_LIVESTREAM"
        elif meta.get("is_upcoming"):
            status = "SCHEDULED_LIVESTREAM"
        elif meta.get("is_completed_vod"):
            status = "COMPLETED_VOD"
        else:
            status = "COMPLETED_VOD"

        return {
            "url": url,
            "video_id": video_id,
            "status": status,
            "channel_id": channel_id,
            "channel_title": meta.get("channel_title"),
            "title": title,
            "permission_verified": True,
            "scheduled_start_time": meta.get("scheduled_start_time"),
            "actual_start_time": meta.get("actual_start_time"),
            "crop_profile": perm.get("crop_profile", "default_fallback") if perm else "default_fallback",
            "error": None,
        }
