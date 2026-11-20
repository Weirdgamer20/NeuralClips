"""JOB F: YouTube Shorts Publisher.

Checks publishing queue, verifies quota, and uploads validated clips to YouTube.
"""

from typing import Dict, Optional
from core.logging_config import setup_logger
from publishing.publishing_queue import PublishingQueueCoordinator

logger = setup_logger("neuralclips.jobs.publish_youtube")


def run_youtube_publisher(max_uploads: int = 10, mock_mode: bool = False, db_path: Optional[str] = None) -> Dict[str, int]:
    coordinator = PublishingQueueCoordinator()
    if db_path:
        from core.job_manager import JobManager
        from core.state_store import StateStore
        from publishing.youtube_publisher import YouTubePublisher
        coordinator.job_manager = JobManager(db_path=db_path)
        coordinator.state_store = StateStore(db_path=db_path)
        coordinator.yt_publisher = YouTubePublisher(state_store=coordinator.state_store)

    stats = coordinator.process_youtube_queue(max_items=max_uploads, mock_mode=mock_mode)
    logger.info(f"YouTube publishing cycle finished: {stats}")
    return stats


if __name__ == "__main__":
    run_youtube_publisher()
