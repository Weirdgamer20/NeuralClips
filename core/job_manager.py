"""Atomic Job Manager and Worker Lease Coordination."""

import os
import sqlite3
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from core.database import get_connection


class JobManager:
    """Manages worker leases and atomic claiming of queue items."""

    def __init__(self, db_path: Optional[str] = None, worker_id: Optional[str] = None):
        self.db_path = db_path
        self.worker_id = worker_id or f"worker_{os.getpid()}_{int(time.time())}"

    def register_heartbeat(self, worker_type: str = "processor", status: str = "HEARTBEAT") -> None:
        """Records a heartbeat timestamp for this worker."""
        now_iso = datetime.now(timezone.utc).isoformat()
        conn = get_connection(self.db_path)
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO worker_status (worker_id, worker_type, status, last_heartbeat)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(worker_id) DO UPDATE SET
                        status = excluded.status,
                        last_heartbeat = excluded.last_heartbeat
                    """,
                    (self.worker_id, worker_type, status, now_iso),
                )
        finally:
            conn.close()

    def claim_approved_highlight(self, lease_duration_seconds: int = 300) -> Optional[Dict[str, Any]]:
        """Atomically claims one approved highlight for rendering."""
        conn = get_connection(self.db_path)
        try:
            with conn:
                # Find eligible highlight
                row = conn.execute(
                    """
                    SELECT h.*, s.original_url
                    FROM approved_highlights h
                    JOIN source_streams s ON h.source_id = s.source_id
                    WHERE h.status = 'APPROVED'
                    ORDER BY h.score DESC
                    LIMIT 1
                    """
                ).fetchone()

                if not row:
                    return None

                highlight_id = row["highlight_id"]
                cursor = conn.execute(
                    """
                    UPDATE approved_highlights
                    SET status = 'RENDERING'
                    WHERE highlight_id = ? AND status = 'APPROVED'
                    """,
                    (highlight_id,),
                )

                if cursor.rowcount == 1:
                    return dict(row)
                return None
        finally:
            conn.close()

    def claim_publication(self, platform: str) -> Optional[Dict[str, Any]]:
        """Atomically claims one pending publication item for YouTube or Instagram."""
        table = "youtube_publications" if platform.upper() == "YOUTUBE" else "instagram_publications"
        conn = get_connection(self.db_path)
        try:
            with conn:
                row = conn.execute(
                    f"""
                    SELECT p.*, c.file_path, c.duration
                    FROM {table} p
                    JOIN rendered_clips c ON p.clip_id = c.clip_id
                    WHERE p.status IN ('PENDING', 'RETRY_REQUIRED') AND c.validated = 1 AND c.file_size_bytes > 100000
                    ORDER BY p.upload_attempts ASC, p.created_at ASC
                    LIMIT 1
                    """
                ).fetchone()

                if not row:
                    return None

                pub_id = row["pub_id"]
                cursor = conn.execute(
                    f"""
                    UPDATE {table}
                    SET status = 'UPLOADING'
                    WHERE pub_id = ? AND status IN ('PENDING', 'RETRY_REQUIRED')
                    """,
                    (pub_id,),
                )

                if cursor.rowcount == 1:
                    return dict(row)
                return None
        finally:
            conn.close()
