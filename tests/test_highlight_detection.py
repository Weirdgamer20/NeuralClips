"""Tests for Part 7 Gemini AI Highlight Detection and Scoring."""

import os
import tempfile
from core.database import init_database
from core.state_store import StateStore
from ai.highlight_ranker import HighlightRanker, calculate_overlap_seconds


def test_overlap_calculation():
    # Full overlap
    assert calculate_overlap_seconds(10, 50, 10, 50) == 40
    # Partial overlap
    assert calculate_overlap_seconds(10, 40, 30, 60) == 10
    # No overlap
    assert calculate_overlap_seconds(10, 20, 30, 40) == 0


def test_highlight_ranking_and_score_threshold():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    try:
        init_database(db_path)
        store = StateStore(db_path)
        store.create_batch("batch_test")
        store.create_source_stream("src_1", "batch_test", "https://youtube.com/watch?v=123")

        # Candidate 1: High score (92)
        store.add_highlight_candidate({
            "source_id": "src_1",
            "start_timestamp": 10.0,
            "end_timestamp": 45.0,
            "category": "clutch",
            "score": 92.0,
            "reason": "Epic 1v3",
            "suggested_duration": 35,
        })

        # Candidate 2: Low score (68 - below 75 threshold)
        store.add_highlight_candidate({
            "source_id": "src_1",
            "start_timestamp": 60.0,
            "end_timestamp": 90.0,
            "category": "kills_eliminations",
            "score": 68.0,
            "reason": "Standard single kill",
            "suggested_duration": 30,
        })

        # Candidate 3: Duplicate/overlapping high score (85 overlapping Candidate 1)
        store.add_highlight_candidate({
            "source_id": "src_1",
            "start_timestamp": 15.0,
            "end_timestamp": 50.0,
            "category": "clutch",
            "score": 85.0,
            "reason": "Same clutch different window",
            "suggested_duration": 35,
        })

        ranker = HighlightRanker(store)
        approved = ranker.rank_and_select(min_score=75.0, max_daily_clips=10)

        # Candidate 2 (68) rejected for score < 75
        # Candidate 3 (85) rejected for overlap > 15s with Candidate 1
        # Only Candidate 1 should be approved
        assert len(approved) == 1
        assert approved[0]["score"] == 92.0
    finally:
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except Exception:
            pass
