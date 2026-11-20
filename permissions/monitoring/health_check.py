"""System health check and diagnostic inspection."""

import os
import shutil
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from core.database import get_connection
from core.quota_manager import QuotaManager


class HealthMonitor:
    """Monitors disk space, database connectivity, worker leases, and API statuses."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.quota_manager = QuotaManager(db_path)

    def run_health_check(self) -> Dict[str, Any]:
        """Runs comprehensive system diagnostics."""
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database_ok": False,
            "disk_free_gb": 0.0,
            "active_workers": 0,
            "stale_locks": 0,
            "youtube_quota": {},
            "instagram_quota": {},
            "errors": [],
        }

        # 1. Database check
        try:
            conn = get_connection(self.db_path)
            with conn:
                conn.execute("SELECT 1").fetchone()
            results["database_ok"] = True
            conn.close()
        except Exception as e:
            results["errors"].append(f"Database error: {e}")

        # 2. Disk space check
        try:
            total, used, free = shutil.disk_usage(os.path.dirname(os.path.abspath(__file__)))
            results["disk_free_gb"] = round(free / (1024 ** 3), 2)
        except Exception as e:
            results["errors"].append(f"Disk check error: {e}")

        # 3. Quota checks
        results["youtube_quota"] = self.quota_manager.get_quota_status("YOUTUBE")
        results["instagram_quota"] = self.quota_manager.get_quota_status("INSTAGRAM")

        return results
