"""JOB H & I: Health Monitor, Crash Recovery, and Daily Reporting."""

import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from typing import Any, Dict, Optional
from core.database import get_connection
from core.logging_config import setup_logger
from monitoring.daily_report import DailyReporter
from monitoring.health_check import HealthMonitor
from monitoring.recovery import PipelineRecovery

logger = setup_logger("neuralclips.jobs.daily_maintenance")


def run_maintenance(batch_id: Optional[str] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    health_mon = HealthMonitor(db_path=db_path)
    recovery = PipelineRecovery(db_path=db_path)
    reporter = DailyReporter(db_path=db_path)

    # 1. Health check
    health_status = health_mon.run_health_check()
    logger.info(f"Health check status: DB={health_status['database_ok']}, FreeDisk={health_status['disk_free_gb']}GB")

    # 2. Crash & stale lease recovery
    recov_stats = recovery.recover_stale_jobs(timeout_minutes=15)

    # 3. Daily report generation
    report_res = None
    target_batch = batch_id
    if not target_batch:
        conn = get_connection(db_path)
        try:
            with conn:
                row = conn.execute(
                    "SELECT batch_id FROM daily_batches ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
                if row:
                    target_batch = row["batch_id"]
        finally:
            conn.close()

    if target_batch:
        report_res = reporter.generate_report(target_batch)
        logger.info(f"Daily report generated for batch {target_batch}:\n{report_res['report_file']}")
        print(report_res["report_text"])

    return {
        "health": health_status,
        "recovery": recov_stats,
        "report": report_res,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuralClips Maintenance & Report")
    parser.add_argument("--batch", dest="batch_id", help="Optional specific batch ID to report")
    args = parser.parse_args()
    run_maintenance(batch_id=args.batch_id)
