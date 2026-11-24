"""Scheduled YouTube API Uploader for 5:00 PM IST (17:00 IST).

Loads the 40 high-retention 2K clips and publishes them sequentially to YouTube Shorts
with custom 9:16 vertical thumbnails starting at 17:00 IST today.
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from config.slices_40_manifest import SLICES_CONFIG
from sources.youtube_source import get_oauth_token
from rendering.thumbnail_generator import ThumbnailGenerator
from scripts.publish_approved_2k_cuts import upload_short_public

BATCH_DIR = BASE_DIR / "storage" / "batch_40"
THUMB_DIR = BASE_DIR / "storage" / "thumbnails_40"

TARGET_HOUR = 17
TARGET_MINUTE = 0

def log(msg):
    print(msg, flush=True)

def run_5pm_scheduler():
    log("=" * 70)
    log(f"⏰ 5:00 PM IST SCHEDULED UPLOADER STARTED")
    log(f"Target upload time: Today at {TARGET_HOUR:02d}:{TARGET_MINUTE:02d} IST (5:00 PM)")
    log(f"Total clips to publish: {len(SLICES_CONFIG)}")
    log("=" * 70)

    while True:
        now = datetime.now()
        target_time = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)
        remaining = (target_time - now).total_seconds()

        if remaining > 0:
            hrs = int(remaining // 3600)
            mins = int((remaining % 3600) // 60)
            secs = int(remaining % 60)
            log(f"[{now.strftime('%H:%M:%S')}] ⏳ Waiting for 5:00 PM IST... ({hrs}h {mins}m {secs}s remaining)")
            sleep_time = min(300, max(5, remaining))
            time.sleep(sleep_time)
            continue

        log(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚀 5:00 PM IST REACHED! Starting 40-Clip API Upload Run...")
        token = get_oauth_token()
        if not token:
            log("❌ Could not get YouTube OAuth token. Retrying in 60s...")
            time.sleep(60)
            continue

        thumb_gen = ThumbnailGenerator()
        results = []
        total = len(SLICES_CONFIG)

        for idx, item in enumerate(SLICES_CONFIG, 1):
            cid = item["id"]
            video_file = BATCH_DIR / f"{cid}_2k.mp4"
            thumb_file = THUMB_DIR / f"thumb_{cid}.jpg"
            title = item["title"]
            desc = f"{item['title']}\nWatch until the end for the craziest moment!\n\n#GTA6 #Shorts #Gaming #GTA6Gameplay #ViceCity"
            tags = ["gta 6", "gta 6 gameplay", "shorts", "gaming", "gta 6 moments", "vice city"]

            if not video_file.exists():
                log(f"[{idx}/{total}] ⚠️ Video file not found: {video_file.name}, skipping.")
                continue

            log(f"\n[{idx}/{total}] Uploading: {video_file.name}")
            log(f"        Title: {title}")

            try:
                vid_id = upload_short_public(str(video_file), title, desc, tags, token)
                short_url = f"https://www.youtube.com/shorts/{vid_id}"
                log(f"        ✅ Published: {short_url}")

                # Apply custom thumbnail
                if thumb_file.exists():
                    ok = thumb_gen.upload_to_youtube(vid_id, str(thumb_file), token)
                    if ok:
                        log(f"        🎯 Thumbnail applied successfully!")

                results.append({
                    "id": cid,
                    "video_id": vid_id,
                    "url": short_url,
                    "title": title,
                    "published_at": datetime.now().isoformat()
                })
                # Spacing between API uploads to prevent quota burst errors
                time.sleep(4.0)

            except Exception as e:
                err_str = str(e)
                log(f"        ⚠️ Upload error: {err_str}")
                if "uploadLimitExceeded" in err_str:
                    log("🛑 YouTube Daily Upload Limit hit. Sleeping 15 minutes before retry...")
                    time.sleep(900)
                    token = get_oauth_token()
                else:
                    time.sleep(5.0)

            # Periodically write progress
            rec_file = BASE_DIR / "storage" / "scheduled_5pm_upload_progress.json"
            with open(rec_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)

        log("\n" + "=" * 70)
        log("🎉 5:00 PM UPLOAD RUN COMPLETE!")
        log(f"Total published: {len(results)}/{total}")
        log("=" * 70)
        break

if __name__ == "__main__":
    run_5pm_scheduler()
