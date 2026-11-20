"""JOB A: Daily Batch Intake Entrypoint.

Accepts five YouTube livestream URLs, verifies authorization, and initializes daily batch.
"""

import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import uuid
from datetime import datetime, timezone
from typing import List
from core.database import init_database
from core.logging_config import setup_logger
from core.state_store import StateStore
from permissions.permission_registry import PermissionRegistry
from sources.source_detector import SourceDetector

logger = setup_logger("neuralclips.jobs.daily_intake")


def run_intake(urls: List[str], db_path: str = None) -> str:
    """Processes five incoming URLs into a daily batch."""
    init_database(db_path)
    state_store = StateStore(db_path)
    perm_registry = PermissionRegistry(state_store=state_store)
    perm_registry.load_and_sync()

    detector = SourceDetector(permission_registry=perm_registry)

    # 1. Generate unique daily batch ID: NC-YYYY-MMDD-XXXX
    date_str = datetime.now(timezone.utc).strftime("%Y-%m%d")
    batch_id = f"NC-{date_str}-{uuid.uuid4().hex[:4].upper()}"

    state_store.create_batch(batch_id=batch_id, total_sources=len(urls))
    logger.info(f"Initialized daily batch: {batch_id} with {len(urls)} source URLs")

    valid_count = 0
    for idx, raw_url in enumerate(urls, start=1):
        url = raw_url.strip()
        classification = detector.classify_source(url)

        source_id = f"src_{batch_id}_{idx}"
        video_id = classification.get("video_id")

        # Check duplicate history
        prev = state_store.find_previous_source(video_id)
        if prev:
            logger.warning(f"Source {url} was previously processed under batch {prev['batch_id']}.")

        status = classification["status"]
        if classification.get("permission_verified"):
            valid_count += 1

        state_store.create_source_stream(
            source_id=source_id,
            batch_id=batch_id,
            original_url=url,
            canonical_video_id=video_id,
            channel_id=classification.get("channel_id"),
            title=classification.get("title", f"Source {idx}"),
            source_type=status,
            crop_profile=classification.get("crop_profile", "default_fallback"),
            permission_verified=classification.get("permission_verified", False),
        )

        logger.info(f"[{idx}/5] Source {source_id} -> {status} (Authorized: {classification.get('permission_verified')})")

    state_store.update_batch_status(batch_id, "PROCESSING", valid_sources=valid_count)
    print(f"Batch {batch_id} intake complete. {valid_count}/{len(urls)} sources authorized for processing.")
    return batch_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuralClips Daily Batch Intake")
    parser.add_argument("urls", nargs="+", help="Five YouTube livestream/VOD URLs")
    args = parser.parse_args()

    if len(args.urls) != 5:
        print(f"Warning: Expected 5 URLs, received {len(args.urls)}. Proceeding with provided URLs.")

    run_intake(args.urls)
