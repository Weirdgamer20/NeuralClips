"""Instagram Reels Publisher via Official Meta Graph API."""

import os
import time
import uuid
from typing import Any, Dict, Optional, Tuple
try:
    import requests
except ImportError:
    requests = None

from core.logging_config import setup_logger
from core.quota_manager import QuotaManager
from core.retry import RetryManager
from core.state_store import StateStore
from publishing.instagram_auth import InstagramAuth

logger = setup_logger("neuralclips.instagram_publisher")

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class InstagramPublisher:
    """Publishes validated clips as Instagram Reels using the Meta Graph API."""

    def __init__(
        self,
        auth: Optional[InstagramAuth] = None,
        quota_manager: Optional[QuotaManager] = None,
        retry_manager: Optional[RetryManager] = None,
        state_store: Optional[StateStore] = None,
    ):
        self.state_store = state_store or StateStore()
        self.auth = auth or InstagramAuth()
        self.quota_manager = quota_manager or QuotaManager(db_path=self.state_store.db_path)
        self.retry_manager = retry_manager or RetryManager(db_path=self.state_store.db_path)

    def publish_reel(
        self,
        pub_record: Dict[str, Any],
        media_public_url: Optional[str] = None,
        mock_mode: bool = False,
    ) -> Tuple[bool, str, Optional[str]]:
        """Executes the two-step Instagram Reels container creation and publishing workflow."""
        pub_id = pub_record["pub_id"]
        clip_id = pub_record["clip_id"]
        caption = pub_record.get("caption", "Epic Gaming Highlight! 🔥")

        # 1. Check account rate limits and daily publishing capacity
        can_pub, reason = self.quota_manager.can_publish_instagram()
        if not can_pub:
            logger.warning(f"Instagram publishing blocked for {pub_id}: {reason}")
            self.state_store.update_publication_status("INSTAGRAM", pub_id, "RATE_LIMITED", error_msg=reason)
            return False, reason, None

        # 2. Check mock mode or unconfigured credentials
        if mock_mode or not self.auth.is_configured():
            mock_media_id = f"ig_{uuid.uuid4().hex[:12]}"
            reel_url = f"https://www.instagram.com/reel/{mock_media_id}/"
            self.quota_manager.record_instagram_upload()
            self.state_store.update_publication_status("INSTAGRAM", pub_id, "PUBLISHED", video_id=mock_media_id, url=reel_url)
            self.retry_manager.mark_success("INSTAGRAM_PUB", pub_id)
            logger.info(f"[SIMULATED] Published Instagram Reel: {reel_url}")
            return True, "Published successfully", reel_url

        # 3. Resolve Public HTTPS URL for video file (required by Meta)
        video_url = media_public_url or os.getenv("MEDIA_PUBLIC_BASE_URL", "").rstrip("/") + f"/{clip_id}.mp4"
        if not video_url.startswith("http"):
            err = f"Instagram Reels requires a public HTTPS video URL, got: {video_url}"
            logger.error(err)
            self.state_store.update_publication_status("INSTAGRAM", pub_id, "FAILED", error_msg=err)
            return False, err, None

        account_id = self.auth.account_id
        headers = self.auth.get_headers()

        try:
            # Step A: Create Reels container
            create_url = f"{GRAPH_API_BASE}/{account_id}/media"
            create_payload = {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "share_to_feed": True,
            }

            resp = requests.post(create_url, headers=headers, json=create_payload, timeout=30)
            resp.raise_for_status()
            container_id = resp.json().get("id")
            if not container_id:
                raise RuntimeError(f"No container ID returned by Meta: {resp.text}")

            self.state_store.update_publication_status("INSTAGRAM", pub_id, "PROCESSING")

            # Step B: Poll container processing status
            status_url = f"{GRAPH_API_BASE}/{container_id}"
            max_polls = 30
            poll_interval = 10
            is_ready = False

            for _ in range(max_polls):
                time.sleep(poll_interval)
                status_resp = requests.get(status_url, headers=headers, params={"fields": "status_code"}, timeout=15)
                status_resp.raise_for_status()
                status_code = status_resp.json().get("status_code")

                if status_code == "FINISHED":
                    is_ready = True
                    break
                elif status_code in ["ERROR", "EXPIRED"]:
                    raise RuntimeError(f"Container processing failed with status: {status_code}")

            if not is_ready:
                raise TimeoutError("Meta container processing timed out after 300s.")

            # Step C: Publish Media Container
            publish_url = f"{GRAPH_API_BASE}/{account_id}/media_publish"
            pub_resp = requests.post(publish_url, headers=headers, json={"creation_id": container_id}, timeout=30)
            pub_resp.raise_for_status()
            media_id = pub_resp.json().get("id")

            # Query permalink
            media_info_url = f"{GRAPH_API_BASE}/{media_id}"
            media_info_resp = requests.get(media_info_url, headers=headers, params={"fields": "permalink"}, timeout=15)
            permalink = media_info_resp.json().get("permalink") if media_info_resp.ok else None
            reel_url = permalink or f"https://www.instagram.com/reel/{media_id}/"

            self.quota_manager.record_instagram_upload()
            self.state_store.update_publication_status("INSTAGRAM", pub_id, "PUBLISHED", video_id=media_id, url=reel_url)
            self.retry_manager.mark_success("INSTAGRAM_PUB", pub_id)
            logger.info(f"Published real Instagram Reel {media_id}: {reel_url}")
            return True, "Published successfully", reel_url

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Instagram publishing failed for {pub_id}: {err_msg}")
            can_retry = self.retry_manager.record_failure("INSTAGRAM_PUB", pub_id, e)
            status = "RETRY_REQUIRED" if can_retry else "FAILED"
            self.state_store.update_publication_status("INSTAGRAM", pub_id, status, error_msg=err_msg)
            return False, err_msg, None
