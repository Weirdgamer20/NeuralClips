"""JOB B: Source Status Monitor.

Checks active and scheduled streams, starts capture workers, and reconciles completed VODs.
"""

from typing import Optional
from core.database import get_connection
from core.logging_config import setup_logger
from core.state_store import StateStore
from sources.live_capture import LiveCaptureCoordinator
from sources.youtube_source import YouTubeSourceInspector

logger = setup_logger("neuralclips.jobs.monitor_sources")


def run_monitor(db_path: Optional[str] = None) -> int:
    state_store = StateStore(db_path)
    inspector = YouTubeSourceInspector()
    coordinator = LiveCaptureCoordinator(db_path=db_path)

    conn = get_connection(db_path)
    updated = 0
    try:
        with conn:
            # Query active or scheduled streams
            rows = conn.execute(
                """
                SELECT * FROM source_streams
                WHERE source_type IN ('SCHEDULED_LIVESTREAM', 'ACTIVE_LIVESTREAM')
                """
            ).fetchall()

            for row in rows:
                source_id = row["source_id"]
                vid_id = row["canonical_video_id"]
                current_type = row["source_type"]

                meta = inspector.inspect_video(vid_id)
                if not meta.get("available"):
                    continue

                if current_type == "SCHEDULED_LIVESTREAM" and meta.get("is_live"):
                    logger.info(f"Scheduled stream {source_id} is now live! Transitioning to ACTIVE_LIVESTREAM.")
                    state_store.update_source_status(source_id, "ACTIVE_LIVESTREAM")
                    coordinator.register_capture_job(source_id, row["original_url"])
                    updated += 1

                elif current_type == "ACTIVE_LIVESTREAM" and meta.get("is_completed_vod"):
                    logger.info(f"Active stream {source_id} has concluded. Transitioning to COMPLETED_VOD.")
                    state_store.update_source_status(source_id, "COMPLETED_VOD", stream_ended=1)
                    updated += 1

        logger.info(f"Source monitor checked {len(rows)} streams; updated {updated}.")
        return updated
    finally:
        conn.close()


if __name__ == "__main__":
    run_monitor()
