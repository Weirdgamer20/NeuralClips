"""Tests for Part 14 Dual-Platform Distribution and Platform Isolation."""

import os
import tempfile
from core.database import init_database
from core.state_store import StateStore


def test_independent_platform_status():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    try:
        init_database(db_path)
        store = StateStore(db_path)

        # Setup mock batch and clip
        store.create_batch("batch_dp")
        store.create_source_stream("src_1", "batch_dp", "https://youtube.com/watch?v=123")
        store.add_highlight_candidate({
            "candidate_id": "cand_1",
            "source_id": "src_1",
            "start_timestamp": 0.0,
            "end_timestamp": 45.0,
            "category": "clutch",
            "score": 90.0,
            "reason": "Epic win",
            "suggested_duration": 45,
        })
        store.approve_highlight("hl_1", "cand_1", "src_1", 0.0, 45.0, 90.0, "clutch", "Epic Win")
        store.register_rendered_clip({
            "clip_id": "clip_master_1",
            "highlight_id": "hl_1",
            "source_id": "src_1",
            "file_path": "clip.mp4",
            "duration": 45.0,
            "file_size_bytes": 1024,
            "validated": True,
        })

        # Fetch initial pending records
        yt_pending = store.get_pending_publications("YOUTUBE")
        ig_pending = store.get_pending_publications("INSTAGRAM")

        assert len(yt_pending) == 1
        assert len(ig_pending) == 1

        yt_pub_id = yt_pending[0]["pub_id"]
        ig_pub_id = ig_pending[0]["pub_id"]

        # Case 1: YouTube succeeds, Instagram fails
        store.update_publication_status("YOUTUBE", yt_pub_id, "PUBLISHED", video_id="yt_vid_123", url="https://youtube.com/shorts/yt_vid_123")
        store.update_publication_status("INSTAGRAM", ig_pub_id, "RETRY_REQUIRED", error_msg="Network timeout")

        # Verify YouTube is no longer pending
        yt_pending_after = store.get_pending_publications("YOUTUBE")
        assert len(yt_pending_after) == 0

        # Verify Instagram is still pending retry
        ig_pending_after = store.get_pending_publications("INSTAGRAM")
        assert len(ig_pending_after) == 1
        assert ig_pending_after[0]["pub_id"] == ig_pub_id
        assert ig_pending_after[0]["upload_attempts"] == 1
    finally:
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except Exception:
            pass
