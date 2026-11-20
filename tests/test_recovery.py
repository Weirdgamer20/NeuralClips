"""Tests for Part 19 Crash Recovery and Part 21 Daily Reporting."""

import os
import tempfile
from core.database import init_database
from core.state_store import StateStore
from monitoring.daily_report import DailyReporter
from monitoring.recovery import PipelineRecovery


def test_crash_recovery_and_daily_report():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name
    with tempfile.TemporaryDirectory() as rep_dir:
        try:
            init_database(db_path)
            store = StateStore(db_path)

            # Setup batch, source, and stuck rendering highlight
            store.create_batch("batch_recov", total_sources=1)
            store.create_source_stream("src_1", "batch_recov", "https://youtube.com/watch?v=123", source_type="COMPLETED_VOD")
            store.add_highlight_candidate({
                "candidate_id": "cand_1",
                "source_id": "src_1",
                "start_timestamp": 0.0,
                "end_timestamp": 30.0,
                "category": "clutch",
                "score": 88.0,
                "reason": "Great play",
                "suggested_duration": 30,
            })
            store.approve_highlight("hl_stuck", "cand_1", "src_1", 0.0, 30.0, 88.0, "clutch", "Stuck Highlight")
            # Mark highlight as stuck in RENDERING
            store.update_highlight_status("hl_stuck", "RENDERING")

            # Run recovery
            recovery = PipelineRecovery(db_path)
            recov_stats = recovery.recover_stale_jobs(timeout_minutes=0)
            assert recov_stats["recovered_highlights"] == 1

            # Verify highlight was reset to APPROVED
            hl = store.get_highlights_for_rendering(limit=5)
            assert any(h["highlight_id"] == "hl_stuck" for h in hl)

            # Generate Daily Report
            reporter = DailyReporter(db_path=db_path, reports_dir=rep_dir)
            report = reporter.generate_report("batch_recov")

            assert report["batch_id"] == "batch_recov"
            assert "NEURALCLIPS DAILY REPORT" in report["report_text"]
            assert os.path.exists(report["report_file"])
        finally:
            try:
                if os.path.exists(db_path):
                    os.remove(db_path)
            except Exception:
                pass
