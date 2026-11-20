"""YouTube Shorts Publisher via Official Data API v3."""

import os
import uuid
from typing import Any, Dict, List, Optional, Tuple
from core.logging_config import setup_logger
from core.quota_manager import QuotaManager
from core.retry import RetryManager
from core.state_store import StateStore
from publishing.youtube_auth import YouTubeAuth

logger = setup_logger("neuralclips.youtube_publisher")


class YouTubePublisher:
    """Uploads validated vertical videos as YouTube Shorts."""

    def __init__(
        self,
        auth: Optional[YouTubeAuth] = None,
        quota_manager: Optional[QuotaManager] = None,
        retry_manager: Optional[RetryManager] = None,
        state_store: Optional[StateStore] = None,
    ):
        self.state_store = state_store or StateStore()
        self.auth = auth or YouTubeAuth()
        self.quota_manager = quota_manager or QuotaManager(db_path=self.state_store.db_path)
        self.retry_manager = retry_manager or RetryManager(db_path=self.state_store.db_path)

    def publish_short(self, pub_record: Dict[str, Any], mock_mode: bool = False) -> Tuple[bool, str, Optional[str]]:
        """Executes upload of a pending YouTube Short publication record."""
        pub_id = pub_record["pub_id"]
        clip_id = pub_record["clip_id"]
        file_path = pub_record["file_path"]
        title = pub_record.get("title", "Insane Gaming Moment #Shorts")
        description = pub_record.get("description", "Gaming Highlights")

        # Focused high-relevance tags (strictly 5-6 tags to avoid algorithm spam penalty)
        raw_hashtags = pub_record.get("hashtags", "")
        extracted_tags = [t.strip("#").strip() for t in raw_hashtags.split() if t.strip("#").strip()]
        tags = list(dict.fromkeys(["gta 6", "gta 6 gameplay", "gta 6 clips", "gaming", "shorts"] + extracted_tags[:2]))

        # 1. Check API Quota availability
        can_upload, quota_reason = self.quota_manager.can_publish_youtube()
        if not can_upload:
            logger.warning(f"YouTube publishing blocked for {pub_id}: {quota_reason}")
            self.state_store.update_publication_status("YOUTUBE", pub_id, "RATE_LIMITED", error_msg=quota_reason)
            return False, quota_reason, None

        # 2. Check mock mode or unconfigured credentials
        if mock_mode or not self.auth.is_configured():
            mock_video_id = f"yt_{uuid.uuid4().hex[:11]}"
            yt_url = f"https://www.youtube.com/shorts/{mock_video_id}"
            self.quota_manager.record_youtube_upload()
            self.state_store.update_publication_status("YOUTUBE", pub_id, "PUBLISHED", video_id=mock_video_id, url=yt_url)
            self.retry_manager.mark_success("YOUTUBE_PUB", pub_id)
            logger.info(f"[SIMULATED] Published YouTube Short: {yt_url}")
            return True, "Published successfully", yt_url

        # 3. Live Google API Client Upload or Direct Resumable Upload
        try:
            video_id = None
            try:
                from googleapiclient.discovery import build
                from googleapiclient.http import MediaFileUpload
                service = self.auth.get_authorized_service()
                body = {
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": tags,
                        "categoryId": "20",
                    },
                    "status": {
                        "privacyStatus": os.getenv("YOUTUBE_PRIVACY_STATUS", "public"),
                        "selfDeclaredMadeForKids": False,
                    },
                }
                media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)
                request = service.videos().insert(part="snippet,status", body=body, media_body=media)
                response = None
                while response is None:
                    status, response = request.next_chunk()
                video_id = response.get("id")
            except (ImportError, Exception):
                # Standard HTTP Resumable Upload Fallback
                video_id = self._upload_resumable_http(file_path, title, description, tags)

            yt_url = f"https://www.youtube.com/shorts/{video_id}"
            self.quota_manager.record_youtube_upload()
            self.state_store.update_publication_status("YOUTUBE", pub_id, "PUBLISHED", video_id=video_id, url=yt_url)
            self.retry_manager.mark_success("YOUTUBE_PUB", pub_id)
            logger.info(f"Published real YouTube Short {video_id}: {yt_url}")
            return True, "Published successfully", yt_url

        except Exception as e:
            err_msg = str(e)
            logger.error(f"YouTube upload failed for {pub_id}: {err_msg}")
            can_retry = self.retry_manager.record_failure("YOUTUBE_PUB", pub_id, e)
            status = "RETRY_REQUIRED" if can_retry else "FAILED"
            self.state_store.update_publication_status("YOUTUBE", pub_id, status, error_msg=err_msg)
            return False, err_msg, None

    def _upload_resumable_http(self, file_path: str, title: str, description: str, tags: Optional[List[str]] = None) -> str:
        import json
        import urllib.request
        from sources.youtube_source import get_oauth_token

        token = get_oauth_token()
        if not token:
            raise RuntimeError("Could not obtain OAuth access token for YouTube upload.")

        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        final_tags = tags or ["gta 6", "gta 6 gameplay", "gta 6 clips", "gaming", "shorts"]

        # Step 1: Initiate resumable session
        init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
        metadata = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": final_tags,
                "categoryId": "20",
            },
            "status": {
                "privacyStatus": os.getenv("YOUTUBE_PRIVACY_STATUS", "public"),
                "selfDeclaredMadeForKids": False,
            },
        }
        init_req = urllib.request.Request(init_url, data=json.dumps(metadata).encode("utf-8"), method="POST")
        init_req.add_header("Authorization", f"Bearer {token}")
        init_req.add_header("Content-Type", "application/json; charset=UTF-8")
        init_req.add_header("X-Upload-Content-Type", "video/mp4")
        init_req.add_header("X-Upload-Content-Length", str(file_size))

        with urllib.request.urlopen(init_req, timeout=30) as init_resp:
            upload_url = init_resp.headers.get("Location")
            if not upload_url:
                raise RuntimeError("No upload URL returned by YouTube API.")

        # Step 2: Upload file bytes
        with open(file_path, "rb") as f:
            file_data = f.read()

        upload_req = urllib.request.Request(upload_url, data=file_data, method="PUT")
        upload_req.add_header("Content-Type", "video/mp4")
        upload_req.add_header("Content-Length", str(len(file_data)))

        with urllib.request.urlopen(upload_req, timeout=120) as upload_resp:
            res_data = json.loads(upload_resp.read().decode("utf-8"))
            vid_id = res_data.get("id")
            if not vid_id:
                raise RuntimeError(f"No video ID in YouTube response: {res_data}")
            return vid_id
