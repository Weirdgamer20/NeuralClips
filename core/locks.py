"""Distributed locking mechanism using database leases for NeuralClips."""

import os
import sqlite3
import time
from datetime import datetime, timezone
from typing import Optional
from core.database import get_connection


def now_epoch() -> float:
    return time.time()


class JobLock:
    """Acquires and releases named locks backed by database state."""

    def __init__(self, lock_name: str, owner_id: Optional[str] = None, timeout_seconds: int = 300, db_path: Optional[str] = None):
        self.lock_name = lock_name
        self.owner_id = owner_id or f"pid_{os.getpid()}_{int(time.time())}"
        self.timeout_seconds = timeout_seconds
        self.db_path = db_path
        self._acquired = False

    def acquire(self) -> bool:
        """Attempts to atomically acquire the lock."""
        conn = get_connection(self.db_path)
        now_iso = datetime.now(timezone.utc).isoformat()
        expires_at_iso = datetime.fromtimestamp(now_epoch() + self.timeout_seconds, timezone.utc).isoformat()

        try:
            with conn:
                # Purge expired locks
                conn.execute(
                    "DELETE FROM job_locks WHERE lock_name = ? AND expires_at < ?",
                    (self.lock_name, now_iso),
                )
                # Attempt to insert lock
                conn.execute(
                    """
                    INSERT INTO job_locks (lock_name, owner_id, acquired_at, expires_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (self.lock_name, self.owner_id, now_iso, expires_at_iso),
                )
                self._acquired = True
                return True
        except sqlite3.IntegrityError:
            # Lock is currently held by someone else
            self._acquired = False
            return False
        finally:
            conn.close()

    def release(self) -> None:
        """Releases the lock if owned."""
        if not self._acquired:
            return
        conn = get_connection(self.db_path)
        try:
            with conn:
                conn.execute(
                    "DELETE FROM job_locks WHERE lock_name = ? AND owner_id = ?",
                    (self.lock_name, self.owner_id),
                )
                self._acquired = False
        finally:
            conn.close()

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"Could not acquire lock for {self.lock_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
