"""Tests for Part 4 Daily Input System and URL validation."""

import os
import tempfile
from core.database import init_database
from jobs.daily_intake import run_intake
from sources.url_validator import extract_video_id, validate_youtube_url


def test_url_validation_formats():
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtube.com/live/dQw4w9WgXcQ?feature=share") == "dQw4w9WgXcQ"
    assert extract_video_id("https://invalid-url.com/watch?v=123") is None
    assert extract_video_id("not a url") is None


def test_five_urls_batch_intake():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    try:
        urls = [
            "https://www.youtube.com/watch?v=NINJA_VOD01",
            "https://www.youtube.com/watch?v=SHROUD_LIV1",
            "https://www.youtube.com/watch?v=TEST_SCHED01",
            "https://www.youtube.com/watch?v=TEST_VOD_002",
            "https://www.youtube.com/watch?v=TEST_VOD_003",
        ]

        batch_id = run_intake(urls, db_path=db_path)
        assert batch_id.startswith("NC-")

        from core.state_store import StateStore
        store = StateStore(db_path)
        batch = store.get_batch(batch_id)
        assert batch is not None
        assert batch["total_sources"] == 5

        sources = store.get_sources_by_batch(batch_id)
        assert len(sources) == 5
    finally:
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except Exception:
            pass
