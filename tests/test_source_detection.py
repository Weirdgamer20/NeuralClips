"""Tests for Part 6 Mixed Livestream Processing Engine and Classification."""

import os
import tempfile
from core.database import init_database
from core.state_store import StateStore
from permissions.permission_registry import PermissionRegistry
from sources.source_detector import SourceDetector


def test_source_classification():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    try:
        init_database(db_path)
        store = StateStore(db_path)
        registry = PermissionRegistry(state_store=store)
        registry.load_and_sync()

        detector = SourceDetector(permission_registry=registry)

        # Test Completed VOD
        res_vod = detector.classify_source("https://www.youtube.com/watch?v=NINJA_VOD01")
        assert res_vod["status"] == "COMPLETED_VOD"
        assert res_vod["permission_verified"] is True

        # Test Active Livestream
        res_live = detector.classify_source("https://www.youtube.com/watch?v=SHROUD_LIVE")
        assert res_live["status"] == "ACTIVE_LIVESTREAM"
        assert res_live["permission_verified"] is True

        # Test Scheduled Livestream
        res_sched = detector.classify_source("https://www.youtube.com/watch?v=TEST_SCHED1")
        assert res_sched["status"] == "SCHEDULED_LIVESTREAM"
        assert res_sched["permission_verified"] is True

        # Test Unavailable URL
        res_unavail = detector.classify_source("https://www.youtube.com/watch?v=UNAVAIL_001")
        assert res_unavail["status"] == "UNAVAILABLE"
        assert res_unavail["permission_verified"] is False
    finally:
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except Exception:
            pass
