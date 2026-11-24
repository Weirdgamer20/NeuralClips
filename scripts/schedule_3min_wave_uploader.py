"""Upload Scheduler: Publishes 40 clips in waves of 5 videos at 3-minute intervals.

Features:
- Divides 40 clips into 8 waves of 5 videos.
- Uploads Wave 1 immediately once rendered.
- Sleeps 3 minutes between waves (180 seconds) to pace uploads perfectly for YouTube Shorts indexing.
- Applies custom 9:16 vertical thumbnails to each video.
- Real-time JSON logging and progress tracking.
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("d:/vidclip")
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from config.slices_40_batch2_manifest import SLICES_BATCH2
from sources.youtube_source import get_oauth_token
from rendering.thumbnail_generator import ThumbnailGenerator
from scripts.publish_approved_2k_cuts import upload_short_public

BATCH_DIR = BASE_DIR / "storage" / "batch_40_part2"
THUMB_DIR = BASE_DIR / "storage" / "thumbnails_batch2"
LOG_FILE = BASE_DIR / "storage" / "wave_uploader_progress.json"

WAVE_SIZE = 5
INTERVAL_SECONDS = 180  # 3 minutes

def log(msg):
    print(msg, flush=True)

def run_wave_uploader():
    log("=" * 70)
    log("🚀 3-MINUTE INTERVAL WAVE UPLOADER STARTED (5 VIDEOS PER WAVE)")
    log(f"Total videos to publish: {len(SLICES_BATCH2)}")
    log(f"Wave size: {WAVE_SIZE} videos")
    log(f"Interval between waves: {INTERVAL_SECONDS // 60} minutes ({INTERVAL_SECONDS}s)")
    log("=" * 70)

    token = get_oauth_token()
    if not token:
        log("❌ Failed to obtain YouTube OAuth token.")
        sys.exit(1)

    thumb_gen = ThumbnailGenerator()
    results = []

    # Divide into chunks of 5
    waves = [SLICES_BATCH2[i : i + WAVE_SIZE] for i in range(0, len(SLICES_BATCH2), WAVE_SIZE)]
    total_waves = len(waves)

    for w_idx, wave in enumerate(waves, 1):
        log(f"\n=======================================================")
        log(f"🌊 STARTING WAVE {w_idx}/{total_waves} ({len(wave)} VIDEOS)")
        log(f"=======================================================")

        for item in wave:
            cid = item["id"]
            video_file = BATCH_DIR / f"{cid}_2k.mp4"
            thumb_file = THUMB_DIR / f"thumb_{cid}.jpg"
            title = item["title"]
            desc = f"{title}\nWatch until the end for the craziest GTA 6 action!\n\n#GTA6 #Shorts #Gaming #GTA6Gameplay #ViceCity"
            tags = ["gta 6", "gta 6 gameplay", "shorts", "gaming", "vice city", "gta 6 moments"]

            # Wait if file is still rendering
            wait_attempts = 0
            while not video_file.exists() or video_file.stat().st_size < 2_000_000:
                log(f"⏳ Waiting for render to finish: {video_file.name} (attempt {wait_attempts+1})...")
                time.sleep(5)
                wait_attempts += 1
                if wait_attempts > 60:
                    break

            if not video_file.exists():
                log(f"❌ File missing after wait: {video_file.name}, skipping.")
                continue

            log(f"\n[Wave {w_idx}] Uploading: {video_file.name}")
            log(f"           Title: {title}")

            try:
                vid_id = upload_short_public(str(video_file), title, desc, tags, token)
                short_url = f"https://www.youtube.com/shorts/{vid_id}"
                log(f"           ✅ Published: {short_url}")

                # Thumbnail
                if thumb_file.exists():
                    ok = thumb_gen.upload_to_youtube(vid_id, str(thumb_file), token)
                    if ok:
                        log(f"           🎯 Thumbnail applied!")

                results.append({
                    "wave": w_idx,
                    "id": cid,
                    "video_id": vid_id,
                    "url": short_url,
                    "title": title,
                    "published_at": datetime.now().isoformat()
                })
                time.sleep(3.0)

            except Exception as e:
                err_str = str(e)
                log(f"           ⚠️ Upload error: {err_str}")
                if "uploadLimitExceeded" in err_str:
                    log("🛑 YouTube Daily API limit reached. Pausing 10 minutes...")
                    time.sleep(600)
                    token = get_oauth_token()
                else:
                    time.sleep(4.0)

            # Save progress
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)

        log(f"\n✅ Wave {w_idx}/{total_waves} complete ({len(results)} total videos published so far).")

        # If not the last wave, wait 3 minutes
        if w_idx < total_waves:
            log(f"⏳ Sleeping for {INTERVAL_SECONDS // 60} minutes before Wave {w_idx+1}...")
            for remaining in range(INTERVAL_SECONDS, 0, -30):
                log(f"   [{datetime.now().strftime('%H:%M:%S')}] Next wave in {remaining}s...")
                time.sleep(min(30, remaining))

    log("\n" + "=" * 70)
    log(f"🎉 ALL 8 WAVES COMPLETE: {len(results)}/{len(SLICES_BATCH2)} VIDEOS PUBLISHED!")
    log("=" * 70)

if __name__ == "__main__":
    run_wave_uploader()
