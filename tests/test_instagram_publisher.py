"""Tests for Part 13 Instagram Reels Publishing."""

import os
import tempfile
from core.database import init_database
from core.quota_manager import QuotaManager
from core.state_store import StateStore
from publishing.instagram_publisher import InstagramPublisher


def test_instagram_publishing_mock():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    try:
        init_database(db_path)
        store = StateStore(db_path)
        quota = QuotaManager(db_path)
        publisher = InstagramPublisher(quota_manager=quota, state_store=store)

        pub_record = {
            "pub_id": "pub_ig_001",
            "clip_id": "clip_001",
            "file_path": "dummy.mp4",
            "caption": "Incredible clutch play! 🔥 #gaming",
        }

        success, msg, url = publisher.publish_reel(pub_record, mock_mode=True)
        assert success is True
        assert url is not None
        assert "instagram.com/reel/" in url

        # Verify rate limit increment
        status = quota.get_quota_status("INSTAGRAM")
        assert status["used"] == 1
    finally:
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except Exception:
            pass
