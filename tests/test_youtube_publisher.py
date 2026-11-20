"""Tests for Part 12 YouTube Shorts Publishing."""

import os
import tempfile
from core.database import init_database
from core.quota_manager import QuotaManager
from core.state_store import StateStore
from publishing.youtube_publisher import YouTubePublisher


def test_youtube_publishing_mock():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    try:
        init_database(db_path)
        store = StateStore(db_path)
        quota = QuotaManager(db_path)
        publisher = YouTubePublisher(quota_manager=quota, state_store=store)

        pub_record = {
            "pub_id": "pub_yt_001",
            "clip_id": "clip_001",
            "file_path": "dummy.mp4",
            "title": "Insane Gaming Clutch #Shorts",
            "description": "Epic moment",
        }

        success, msg, url = publisher.publish_short(pub_record, mock_mode=True)
        assert success is True
        assert url is not None
        assert "youtube.com/shorts/" in url

        # Verify quota deduction (1600 units)
        status = quota.get_quota_status("YOUTUBE")
        assert status["used"] == 1600
    finally:
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except Exception:
            pass
