"""Dual-Platform Publishing Queue Coordinator."""

import os
from typing import Any, Dict, List, Optional
from core.job_manager import JobManager
from core.logging_config import setup_logger
from core.state_store import StateStore
from core.yaml_util import load_yaml
from publishing.instagram_publisher import InstagramPublisher
from publishing.youtube_publisher import YouTubePublisher

logger = setup_logger("neuralclips.publishing_queue")


def is_instagram_enabled() -> bool:
    """Checks whether Instagram publishing is enabled in config or env."""
    env_val = os.getenv("INSTAGRAM_ENABLED")
    if env_val is not None:
        return env_val.lower() in ("true", "1", "yes")
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.yaml")
    settings = load_yaml(config_path)
    return settings.get("publishing", {}).get("instagram", {}).get("enabled", False)


class PublishingQueueCoordinator:
    """Orchestrates independent publishing queues for YouTube and Instagram."""

    def __init__(
        self,
        youtube_publisher: Optional[YouTubePublisher] = None,
        instagram_publisher: Optional[InstagramPublisher] = None,
        job_manager: Optional[JobManager] = None,
        state_store: Optional[StateStore] = None,
    ):
        self.yt_publisher = youtube_publisher or YouTubePublisher()
        self.ig_publisher = instagram_publisher or InstagramPublisher()
        self.job_manager = job_manager or JobManager()
        self.state_store = state_store or StateStore()

    def process_youtube_queue(self, max_items: int = 10, mock_mode: bool = False) -> Dict[str, int]:
        """Processes pending items in YouTube publication queue."""
        processed = 0
        succeeded = 0
        failed = 0

        for _ in range(max_items):
            item = self.job_manager.claim_publication("YOUTUBE")
            if not item:
                break

            processed += 1
            success, msg, url = self.yt_publisher.publish_short(item, mock_mode=mock_mode)
            if success:
                succeeded += 1
            else:
                failed += 1

        return {"processed": processed, "succeeded": succeeded, "failed": failed}

    def process_instagram_queue(self, max_items: int = 10, mock_mode: bool = False) -> Dict[str, int]:
        """Processes pending items in Instagram publication queue."""
        if not is_instagram_enabled() and not mock_mode:
            logger.info("Instagram publishing is disabled in configuration. Skipping.")
            return {"processed": 0, "succeeded": 0, "failed": 0, "status": "DISABLED"}

        processed = 0
        succeeded = 0
        failed = 0

        for _ in range(max_items):
            item = self.job_manager.claim_publication("INSTAGRAM")
            if not item:
                break

            processed += 1
            success, msg, url = self.ig_publisher.publish_reel(item, mock_mode=mock_mode)
            if success:
                succeeded += 1
            else:
                failed += 1

        return {"processed": processed, "succeeded": succeeded, "failed": failed}
