"""Scheduled Task Coordinator and Pipeline Runner."""

import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import time
from typing import Dict, List, Optional
from core.database import init_database
from core.logging_config import setup_logger
from jobs.analyze_highlights import run_analyzer
from jobs.daily_intake import run_intake
from jobs.daily_maintenance import run_maintenance
from jobs.monitor_sources import run_monitor
from jobs.process_media import run_media_processor
from jobs.publish_instagram import run_instagram_publisher
from jobs.publish_youtube import run_youtube_publisher
from jobs.render_clips import run_renderer

logger = setup_logger("neuralclips.scheduler")


class PipelineScheduler:
    """Coordinates execution of the end-to-end NeuralClips pipeline stages."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        init_database(self.db_path)

    def run_full_pipeline_cycle(self, urls: Optional[List[str]] = None, mock_mode: bool = True) -> Dict[str, any]:
        """Runs an end-to-end execution of all pipeline jobs."""
        logger.info("=== STARTING FULL PIPELINE CYCLE ===")
        results = {}

        # 1. Intake if URLs provided
        if urls:
            batch_id = run_intake(urls, db_path=self.db_path)
            results["batch_id"] = batch_id
        else:
            batch_id = None

        # 2. Monitor sources
        results["sources_monitored"] = run_monitor(db_path=self.db_path)

        # 3. Process media
        results["media_segments"] = run_media_processor(db_path=self.db_path)

        # 4. Analyze highlights
        results["highlights"] = run_analyzer(min_score=75.0, max_clips=100, db_path=self.db_path)

        # 5. Render clips
        results["rendering"] = run_renderer(max_renders=100, db_path=self.db_path)

        # 6. Publish YouTube Shorts
        results["youtube"] = run_youtube_publisher(max_uploads=100, mock_mode=mock_mode, db_path=self.db_path)

        # 7. Publish Instagram Reels
        results["instagram"] = run_instagram_publisher(max_uploads=50, mock_mode=mock_mode, db_path=self.db_path)

        # 8. Maintenance & Report
        results["maintenance"] = run_maintenance(batch_id=batch_id, db_path=self.db_path)

        logger.info("=== PIPELINE CYCLE COMPLETED ===")
        return results

    @staticmethod
    def print_task_scheduler_instructions() -> None:
        """Prints Windows Task Scheduler instructions and commands for production deployment."""
        py = sys.executable
        wd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print("\n" + "=" * 60)
        print("WINDOWS TASK SCHEDULER DEPLOYMENT COMMANDS:")
        print("=" * 60)
        print(f"Working Directory: {wd}\n")
        tasks = [
            ("NeuralClips_MonitorSources", "MINUTE", "1", f'"{py}" -m jobs.monitor_sources'),
            ("NeuralClips_ProcessMedia", "MINUTE", "5", f'"{py}" -m jobs.process_media'),
            ("NeuralClips_AnalyzeHighlights", "MINUTE", "5", f'"{py}" -m jobs.analyze_highlights'),
            ("NeuralClips_RenderClips", "MINUTE", "5", f'"{py}" -m jobs.render_clips'),
            ("NeuralClips_PublishYouTube", "MINUTE", "5", f'"{py}" -m jobs.publish_youtube'),
            ("NeuralClips_PublishInstagram", "MINUTE", "5", f'"{py}" -m jobs.publish_instagram'),
            ("NeuralClips_DailyMaintenance", "MINUTE", "15", f'"{py}" -m jobs.daily_maintenance'),
        ]
        for name, schedule, modifier, cmd in tasks:
            print(f'schtasks /Create /SC {schedule} /MO {modifier} /TN "{name}" /TR "{cmd}" /F')
        print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuralClips Pipeline Scheduler")
    parser.add_argument("--run-cycle", action="store_true", help="Run full pipeline cycle")
    parser.add_argument("--urls", nargs="+", help="Five YouTube livestream/VOD URLs for intake")
    parser.add_argument("--print-tasks", action="store_true", help="Print Windows Task Scheduler commands")
    parser.add_argument("--live", action="store_true", help="Run live publishing instead of mock mode")
    args = parser.parse_args()

    sched = PipelineScheduler()

    if args.print_tasks:
        sched.print_task_scheduler_instructions()
    elif args.run_cycle:
        sched.run_full_pipeline_cycle(urls=args.urls, mock_mode=not args.live)
    else:
        parser.print_help()
