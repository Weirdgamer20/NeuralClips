"""Failure classification and bounded exponential backoff manager."""

import random
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from core.database import get_connection


class ErrorCategory(str, Enum):
    TRANSIENT = "TRANSIENT"
    PERMANENT = "PERMANENT"


TRANSIENT_KEYWORDS = [
    "timeout", "timed out", "connection reset", "econnreset", "rate limit",
    "429", "500", "502", "503", "504", "temporary failure", "network unreachable",
    "deadlock", "database is locked", "busy", "quota exceeded", "quotaExceeded",
    "server error", "try again", "resource temporarily unavailable"
]

PERMANENT_KEYWORDS = [
    "invalid url", "access denied", "permission denied", "unauthorized",
    "401", "403", "404", "not found", "forbidden", "copyright", "revoked",
    "bad request", "invalid_grant", "unsupported video format"
]


def classify_error(exception_or_msg: Exception | str) -> ErrorCategory:
    """Classifies an error message or exception as TRANSIENT or PERMANENT."""
    msg = str(exception_or_msg).lower()
    for kw in PERMANENT_KEYWORDS:
        if kw in msg:
            return ErrorCategory.PERMANENT
    for kw in TRANSIENT_KEYWORDS:
        if kw in msg:
            return ErrorCategory.TRANSIENT
    # Default to transient for unexpected exceptions to allow safe retry bounded by max_attempts
    return ErrorCategory.TRANSIENT


def compute_backoff_seconds(attempt: int, base_seconds: float = 30.0, max_seconds: float = 900.0, jitter: bool = True) -> float:
    """Calculates exponential backoff with full jitter."""
    delay = min(max_seconds, base_seconds * (2 ** (attempt - 1)))
    if jitter:
        delay = random.uniform(base_seconds, delay)
    return round(delay, 2)


class RetryManager:
    """Records and evaluates retry policies for pipeline jobs."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def record_failure(
        self,
        job_type: str,
        job_id: str,
        error: Exception | str,
        max_attempts: int = 3,
        base_backoff_seconds: float = 30.0,
    ) -> bool:
        """Records a job failure. Returns True if job can be retried, False if permanent or max attempts reached."""
        category = classify_error(error)
        conn = get_connection(self.db_path)

        try:
            with conn:
                row = conn.execute(
                    "SELECT attempt FROM retry_records WHERE job_type = ? AND job_id = ? AND resolved = 0",
                    (job_type, job_id),
                ).fetchone()

                current_attempt = (row["attempt"] + 1) if row else 1

                if category == ErrorCategory.PERMANENT or current_attempt > max_attempts:
                    # Mark permanent failure
                    if row:
                        conn.execute(
                            "UPDATE retry_records SET attempt = ?, last_error = ?, resolved = 1 WHERE job_type = ? AND job_id = ?",
                            (current_attempt, str(error), job_type, job_id),
                        )
                    return False

                # Schedule next retry
                backoff = compute_backoff_seconds(current_attempt, base_seconds=base_backoff_seconds)
                next_retry_epoch = time.time() + backoff
                next_retry_iso = datetime.fromtimestamp(next_retry_epoch, timezone.utc).isoformat()

                if row:
                    conn.execute(
                        """
                        UPDATE retry_records
                        SET attempt = ?, last_error = ?, next_retry_at = ?, error_type = ?
                        WHERE job_type = ? AND job_id = ? AND resolved = 0
                        """,
                        (current_attempt, str(error), next_retry_iso, category.value, job_type, job_id),
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO retry_records (retry_id, job_type, job_id, attempt, max_attempts, error_type, last_error, next_retry_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (f"retry_{job_type}_{job_id}_{current_attempt}", job_type, job_id, current_attempt, max_attempts, category.value, str(error), next_retry_iso),
                    )
                return True
        finally:
            conn.close()

    def mark_success(self, job_type: str, job_id: str) -> None:
        """Marks any pending retry records for this job as resolved."""
        conn = get_connection(self.db_path)
        try:
            with conn:
                conn.execute(
                    "UPDATE retry_records SET resolved = 1 WHERE job_type = ? AND job_id = ?",
                    (job_type, job_id),
                )
        finally:
            conn.close()
