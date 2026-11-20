"""JOB C: Media Processor.

Segments completed recordings and prepares footage for Gemini AI analysis.
"""

from typing import Optional
from core.database import get_connection
from core.logging_config import setup_logger
from core.state_store import StateStore
from sources.vod_processor import VODProcessor

logger = setup_logger("neuralclips.jobs.process_media")


def run_media_processor(db_path: Optional[str] = None) -> int:
    state_store = StateStore(db_path)
    vod_processor = VODProcessor(state_store=state_store)

    conn = get_connection(db_path)
    processed_count = 0
    try:
        with conn:
            # Find VOD sources ready for segmentation
            rows = conn.execute(
                """
                SELECT * FROM source_streams
                WHERE source_type = 'COMPLETED_VOD' AND permission_verified = 1
                LIMIT 5
                """
            ).fetchall()

            for row in rows:
                source_id = row["source_id"]
                url = row["original_url"]
                # Process VOD into 60-second segments
                res = vod_processor.process_vod(source_id=source_id, video_url_or_path=url)
                processed_count += res.get("segments_count", 0)

        logger.info(f"Media processor finished: {processed_count} segments generated.")
        return processed_count
    finally:
        conn.close()


if __name__ == "__main__":
    run_media_processor()
