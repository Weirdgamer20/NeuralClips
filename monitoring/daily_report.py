"""Consolidated Daily Report Generator adhering to Part 21 requirements."""

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from core.database import get_connection
from core.quota_manager import QuotaManager


class DailyReporter:
    """Compiles truthful production and publication reports from database records."""

    def __init__(self, db_path: Optional[str] = None, reports_dir: Optional[str] = None):
        self.db_path = db_path
        if not reports_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            reports_dir = os.path.join(base_dir, "storage", "reports")
        self.reports_dir = reports_dir
        self.quota_manager = QuotaManager(db_path)
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_report(self, batch_id: str) -> Dict[str, Any]:
        """Queries actual database records for batch and produces report text."""
        conn = get_connection(self.db_path)
        try:
            with conn:
                # Batch info
                batch = conn.execute(
                    "SELECT * FROM daily_batches WHERE batch_id = ?", (batch_id,)
                ).fetchone()

                # Sources
                sources = conn.execute(
                    "SELECT * FROM source_streams WHERE batch_id = ?", (batch_id,)
                ).fetchall()

                # Candidates & Highlights
                source_ids = [s["source_id"] for s in sources]
                placeholders = ",".join("?" for _ in source_ids) if source_ids else "''"

                all_cands = conn.execute(
                    f"SELECT * FROM highlight_candidates WHERE source_id IN ({placeholders})",
                    source_ids,
                ).fetchall() if source_ids else []

                approved_hls = conn.execute(
                    f"SELECT * FROM approved_highlights WHERE source_id IN ({placeholders})",
                    source_ids,
                ).fetchall() if source_ids else []

                # Rendered Clips
                clips = conn.execute(
                    f"SELECT * FROM rendered_clips WHERE source_id IN ({placeholders})",
                    source_ids,
                ).fetchall() if source_ids else []

                # Publications
                clip_ids = [c["clip_id"] for c in clips]
                c_placeholders = ",".join("?" for _ in clip_ids) if clip_ids else "''"

                yt_pubs = conn.execute(
                    f"SELECT * FROM youtube_publications WHERE clip_id IN ({c_placeholders})",
                    clip_ids,
                ).fetchall() if clip_ids else []

                ig_pubs = conn.execute(
                    f"SELECT * FROM instagram_publications WHERE clip_id IN ({c_placeholders})",
                    clip_ids,
                ).fetchall() if clip_ids else []

            # Compute actual counts
            total_sources = len(sources)
            completed_vods = sum(1 for s in sources if s["source_type"] == "COMPLETED_VOD")
            active_streams = sum(1 for s in sources if s["source_type"] == "ACTIVE_LIVESTREAM")
            processed_sources = sum(1 for s in sources if s["source_type"] in ["COMPLETED", "PROCESSING", "COMPLETED_VOD"])

            total_duration_hours = sum(float(s["duration_seconds"] or 0) for s in sources) / 3600.0

            total_cands = len(all_cands)
            approved_count = len(approved_hls)
            rejected_count = total_cands - approved_count

            clips_rendered = len(clips)
            validated_clips = sum(1 for c in clips if c["validated"])
            render_failures = sum(1 for h in approved_hls if h["status"] == "FAILED")

            yt_published = [p for p in yt_pubs if p["status"] == "PUBLISHED"]
            yt_pending = [p for p in yt_pubs if p["status"] in ["PENDING", "UPLOADING", "RETRY_REQUIRED"]]
            yt_failed = [p for p in yt_pubs if p["status"] == "FAILED"]

            ig_published = [p for p in ig_pubs if p["status"] == "PUBLISHED"]
            ig_pending = [p for p in ig_pubs if p["status"] in ["PENDING", "UPLOADING", "RETRY_REQUIRED"]]
            ig_failed = [p for p in ig_pubs if p["status"] == "FAILED"]

            yt_quota = self.quota_manager.get_quota_status("YOUTUBE")
            ig_quota = self.quota_manager.get_quota_status("INSTAGRAM")

            # Format report text
            report_lines = [
                "=" * 60,
                "NEURALCLIPS DAILY REPORT",
                "=" * 60,
                f"Batch ID: {batch_id}",
                f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                "",
                "SOURCES:",
                f"- Submitted: {total_sources}",
                f"- Completed VODs: {completed_vods}",
                f"- Active livestreams: {active_streams}",
                f"- Successfully processed: {processed_sources}",
                "",
                "ANALYSIS:",
                f"- Total footage analyzed: {total_duration_hours:.2f} hours",
                f"- Highlights detected: {total_cands}",
                f"- Rejected highlights: {rejected_count}",
                f"- Approved highlights: {approved_count}",
                "",
                "PRODUCTION:",
                f"- Clips rendered: {clips_rendered}",
                f"- Rendering failures: {render_failures}",
                f"- Validated clips: {validated_clips}",
                "",
                "YOUTUBE:",
                f"- Published: {len(yt_published)}",
                f"- Pending: {len(yt_pending)}",
                f"- Failed: {len(yt_failed)}",
            ]

            if yt_published:
                report_lines.append("  Published Shorts URLs:")
                for p in yt_published[:10]:
                    report_lines.append(f"    - {p['youtube_url']}")

            report_lines.extend([
                "",
                "INSTAGRAM:",
                f"- Published: {len(ig_published)}",
                f"- Pending: {len(ig_pending)}",
                f"- Failed: {len(ig_failed)}",
            ])

            if ig_published:
                report_lines.append("  Published Reels URLs:")
                for p in ig_published[:10]:
                    report_lines.append(f"    - {p['instagram_reel_url']}")

            report_lines.extend([
                "",
                "API QUOTA & CAPACITY STATUS:",
                f"- YouTube Data API: {yt_quota['used']}/{yt_quota['limit']} units used ({yt_quota['remaining']} remaining)",
                f"- Instagram Graph API: {ig_quota['used']}/{ig_quota['limit']} reels uploaded ({ig_quota['remaining']} remaining)",
                "=" * 60,
            ])

            report_text = "\n".join(report_lines)

            # Save report to file
            report_file = os.path.join(self.reports_dir, f"report_{batch_id}.txt")
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_text)

            return {
                "batch_id": batch_id,
                "report_text": report_text,
                "report_file": report_file,
                "validated_clips": validated_clips,
                "youtube_published_count": len(yt_published),
                "instagram_published_count": len(ig_published),
            }
        finally:
            conn.close()
