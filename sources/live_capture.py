"""Active Livestream Capture Pipeline and Worker Coordination."""

import os
import time
import uuid
from typing import Any, Dict, Optional
from core.database import get_connection
from core.logging_config import setup_logger
from core.state_store import StateStore
from sources.segment_manager import SegmentManager

logger = setup_logger("neuralclips.live_capture")


class LiveCaptureCoordinator:
    """Coordinates persistent capture workers for ongoing YouTube livestreams."""

    def __init__(
        self,
        segment_manager: Optional[SegmentManager] = None,
        state_store: Optional[StateStore] = None,
        db_path: Optional[str] = None,
    ):
        self.db_path = db_path
        self.segment_manager = segment_manager or SegmentManager()
        self.state_store = state_store or StateStore()

    def register_capture_job(self, source_id: str, stream_url: str) -> str:
        """Registers a new capture job for an active livestream."""
        job_id = f"cap_{source_id}_{int(time.time())}"
        conn = get_connection(self.db_path)
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO capture_jobs (
                        capture_job_id, source_id, status, stream_url,
                        last_captured_timestamp, total_segments_captured
                    ) VALUES (?, ?, 'PENDING', ?, 0.0, 0)
                    """,
                    (job_id, source_id, stream_url),
                )
            logger.info(f"Registered capture job {job_id} for stream {source_id}")
            return job_id
        finally:
            conn.close()

    def simulate_capture_step(
        self,
        capture_job_id: str,
        chunk_seconds: float = 60.0,
        stream_is_live: bool = True,
    ) -> Dict[str, Any]:
        """Simulates one incremental capture chunk from the persistent capture worker."""
        conn = get_connection(self.db_path)
        try:
            with conn:
                row = conn.execute(
                    "SELECT * FROM capture_jobs WHERE capture_job_id = ?",
                    (capture_job_id,),
                ).fetchone()

                if not row:
                    raise ValueError(f"Capture job {capture_job_id} not found")

                source_id = row["source_id"]
                last_ts = float(row["last_captured_timestamp"])
                total_segs = int(row["total_segments_captured"])

                if not stream_is_live:
                    # Stream has terminated
                    conn.execute(
                        "UPDATE capture_jobs SET status = 'COMPLETED', updated_at = CURRENT_TIMESTAMP WHERE capture_job_id = ?",
                        (capture_job_id,),
                    )
                    self.state_store.update_source_status(source_id, "COMPLETED_VOD", stream_ended=1)
                    logger.info(f"Stream {source_id} ended. Finalized {total_segs} segments.")
                    return {"status": "STREAM_ENDED", "total_segments": total_segs}

                # Create next segment
                start_ts = last_ts
                end_ts = start_ts + chunk_seconds
                seg_dir = self.segment_manager.get_source_segment_dir(source_id)
                seg_path = os.path.join(seg_dir, f"live_segment_{total_segs:04d}.mp4")

                if not os.path.exists(seg_path):
                    with open(seg_path, "wb") as f:
                        f.write(f"LIVE_CHUNK_{total_segs}\n".encode())

                seg_id = self.segment_manager.record_segment(
                    source_id=source_id,
                    segment_index=total_segs,
                    file_path=seg_path,
                    start_time=start_ts,
                    end_time=end_ts,
                )

                new_total = total_segs + 1
                conn.execute(
                    """
                    UPDATE capture_jobs
                    SET status = 'ACTIVE',
                        last_captured_timestamp = ?,
                        total_segments_captured = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE capture_job_id = ?
                    """,
                    (end_ts, new_total, capture_job_id),
                )

                return {
                    "status": "CAPTURING",
                    "segment_id": seg_id,
                    "start_time": start_ts,
                    "end_time": end_ts,
                    "total_segments": new_total,
                }
        finally:
            conn.close()

    def handle_unexpected_termination(self, capture_job_id: str, error_reason: str) -> None:
        """Preserves captured segments when stream drops or crashes unexpectedly."""
        conn = get_connection(self.db_path)
        try:
            with conn:
                conn.execute(
                    """
                    UPDATE capture_jobs
                    SET status = 'TERMINATED', error_message = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE capture_job_id = ?
                    """,
                    (error_reason, capture_job_id),
                )
            logger.warning(f"Capture job {capture_job_id} terminated unexpectedly: {error_reason}. Preserved prior segments.")
        finally:
            conn.close()
