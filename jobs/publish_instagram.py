"""JOB G: Instagram Reels Publisher.

Checks publishing queue, verifies Meta capacity, and publishes validated clips to Instagram.
"""

from typing import Dict, Optional
from core.logging_config import setup_logger
from publishing.publishing_queue import PublishingQueueCoordinator

logger = setup_logger("neuralclips.jobs.publish_instagram")


def run_instagram_publisher(max_uploads: int = 10, mock_mode: bool = False, db_path: Optional[str] = None) -> Dict[str, int]:
    coordinator = PublishingQueueCoordinator()
    if db_path:
        from core.job_manager import JobManager
        from core.state_store import StateStore
        from publishing.instagram_publisher import InstagramPublisher
        coordinator.job_manager = JobManager(db_path=db_path)
        coordinator.state_store = StateStore(db_path=db_path)
        coordinator.ig_publisher = InstagramPublisher(state_store=coordinator.state_store)

    stats = coordinator.process_instagram_queue(max_items=max_uploads, mock_mode=mock_mode)
    logger.info(f"Instagram publishing cycle finished: {stats}")
    return stats


if __name__ == "__main__":
    run_instagram_publisher()
