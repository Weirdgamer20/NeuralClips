"""Pipeline crash recovery and stale lease reconciliation."""

from datetime import datetime, timezone
from typing import Dict, Optional
from core.database import get_connection
from core.logging_config import setup_logger

logger = setup_logger("neuralclips.recovery")


class PipelineRecovery:
    """Recovers stranded jobs and cleans stale locks after worker crashes."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def recover_stale_jobs(self, timeout_minutes: int = 15) -> Dict[str, int]:
        """Finds items stuck in progress and resets them to pending state."""
        now_iso = datetime.now(timezone.utc).isoformat()
        conn = get_connection(self.db_path)
        recovered = {
            "recovered_highlights": 0,
            "recovered_youtube_pubs": 0,
            "recovered_instagram_pubs": 0,
            "cleared_locks": 0,
        }

        try:
            with conn:
                # 1. Recover stale RENDERING highlights
                cur = conn.execute(
                    """
                    UPDATE approved_highlights
                    SET status = 'APPROVED'
                    WHERE status = 'RENDERING'
                    """
                )
                recovered["recovered_highlights"] = cur.rowcount

                # 2. Recover stale UPLOADING publications
                cur_yt = conn.execute(
                    """
                    UPDATE youtube_publications
                    SET status = 'RETRY_REQUIRED'
                    WHERE status = 'UPLOADING'
                    """
                )
                recovered["recovered_youtube_pubs"] = cur_yt.rowcount

                cur_ig = conn.execute(
                    """
                    UPDATE instagram_publications
                    SET status = 'RETRY_REQUIRED'
                    WHERE status = 'UPLOADING'
                    """
                )
                recovered["recovered_instagram_pubs"] = cur_ig.rowcount

                # 3. Clean expired locks
                cur_locks = conn.execute(
                    "DELETE FROM job_locks WHERE expires_at < ?", (now_iso,)
                )
                recovered["cleared_locks"] = cur_locks.rowcount

            logger.info(f"Pipeline recovery completed: {recovered}")
            return recovered
        finally:
            conn.close()
