"""Automated Batch Scheduled Uploader Daemon.

Continuously monitors the 20-Batch A/B Experiment Manifest.
Every 1 hour, as each batch's scheduled timestamp arrives, uploads its 5 videos to YouTube as Public Shorts.
Logs full performance and tracking metadata locally.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(r"d:\vidclip")
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from publishing.youtube_publisher import YouTubePublisher
from core.state_store import StateStore

STORAGE_DIR = BASE_DIR / "storage"
MANIFEST_PATH = STORAGE_DIR / "batch_experiment_manifest.json"
UPLOAD_LOG_PATH = STORAGE_DIR / "batch_upload_log.json"


def log(msg: str):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S IST]")
    line = f"{timestamp} {msg}"
    print(line, flush=True)


def parse_iso_to_utc(iso_str: str) -> datetime:
    # Example: 2026-11-21T14:00:00.000Z
    clean_str = iso_str.replace(".000Z", "+00:00").replace("Z", "+00:00")
    return datetime.fromisoformat(clean_str)


def upload_batch(batch_entry, publisher, store):
    batch_num = batch_entry["batch_number"]
    theme = batch_entry["internal_theme"]
    videos = batch_entry["videos"]

    log(f"\n{'='*65}")
    log(f"LAUNCHING BATCH [{batch_num:02d}/20] PUBLIC UPLOAD :: {theme}")
    log(f"Target Seed Audience: {batch_entry['target_seed_audience']}")
    log(f"{'='*65}")

    success_count = 0

    for v_idx, v_data in enumerate(videos, 1):
        global_num = v_data["video_number"]
        file_path = v_data["rendered_file"]
        title = v_data["title"]
        description = v_data["description"]
        pub_id = f"pub_batch_{batch_num:02d}_{v_idx}_{int(time.time())}"

        if not os.path.exists(file_path):
            log(f"  [{v_idx}/5] ERROR: Rendered file missing: {file_path}")
            continue

        log(f"  [{v_idx}/5] Uploading #{global_num:03d}: '{title}'...")

        pub_record = {
            "pub_id": pub_id,
            "clip_id": v_data["clip_id"],
            "file_path": file_path,
            "title": title,
            "description": description,
            "hashtags": "#GTA6 #Shorts #Gaming #GTA6Gameplay #ViceCity",
        }

        success, msg, yt_url = publisher.publish_short(
            pub_record=pub_record,
            mock_mode=False,
            publish_at=None,  # Direct public release
        )

        if success:
            log(f"        -> SUCCESS: {yt_url}")
            v_data["upload_status"] = "PUBLISHED"
            v_data["youtube_url"] = yt_url
            v_data["published_at"] = time.strftime("%Y-%m-%d %H:%M:%S IST")
            success_count += 1
        else:
            log(f"        -> FAILED: {msg}")
            v_data["upload_status"] = "FAILED"
            v_data["error"] = str(msg)

        # Brief pause between uploads in the same batch
        time.sleep(15)

    batch_entry["status"] = "PUBLISHED" if success_count > 0 else "FAILED"
    batch_entry["published_at"] = time.strftime("%Y-%m-%d %H:%M:%S IST")
    batch_entry["successful_uploads"] = success_count

    # Append to local tracking log
    upload_history = []
    if UPLOAD_LOG_PATH.exists():
        try:
            with open(UPLOAD_LOG_PATH, "r", encoding="utf-8") as f:
                upload_history = json.load(f)
        except Exception:
            upload_history = []

    upload_history.append({
        "batch_number": batch_num,
        "theme": theme,
        "seed_audience": batch_entry["target_seed_audience"],
        "published_at": time.strftime("%Y-%m-%d %H:%M:%S IST"),
        "successful_uploads": success_count,
        "videos": [
            {
                "num": v["video_number"],
                "title": v["title"],
                "url": v.get("youtube_url"),
                "status": v.get("upload_status")
            }
            for v in videos
        ]
    })

    with open(UPLOAD_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(upload_history, f, indent=2)

    return success_count


def run_scheduler_loop():
    log("Starting 20-Batch A/B Testing Upload Scheduler (Checking every 60s)...")
    store = StateStore()
    publisher = YouTubePublisher(state_store=store)

    while True:
        if not MANIFEST_PATH.exists():
            time.sleep(30)
            continue

        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        now_utc = datetime.now(timezone.utc)
        pending_batches = [b for b in manifest["batches"] if b["status"] == "SCHEDULED"]

        if not pending_batches:
            log("All 20 batches have been processed. Scheduler exiting.")
            break

        for batch in pending_batches:
            sched_utc = parse_iso_to_utc(batch["scheduled_release_time_iso"])
            if now_utc >= sched_utc:
                upload_batch(batch, publisher, store)
                # Update manifest checkpoint
                with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2)
                break  # Process one batch per cycle

        time.sleep(60)


if __name__ == "__main__":
    run_scheduler_loop()
