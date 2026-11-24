"""Scheduled Uploader for Indian Creators Clips (Techno Gamerz, CarryMinati, Triggered Insaan).

Key Rules:
1. Every video is uploaded as SCHEDULED on YouTube:
   - privacyStatus = "private"
   - publishAt = ISO 8601 UTC future timestamp
2. Each batch is delayed by 30 minutes:
   - Batch 1: Base time
   - Batch 2: Base time + 30 mins
   - Batch 3: Base time + 60 mins
   - Batch 4: Base time + 90 mins
   - Batch 5: Base time + 120 mins
   - Batch 6: Base time + 150 mins
3. Automatically sleeps and wakes up when daily quota resets if HTTP 429 is encountered.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from config.slices_indian_creators_manifest import SLICES_INDIAN_CREATORS
from sources.youtube_source import get_oauth_token
from rendering.thumbnail_generator import ThumbnailGenerator

OUT_DIR = BASE_DIR / "storage" / "batch_indian_creators"
THUMB_DIR = BASE_DIR / "storage" / "thumbnails_indian"
LOG_FILE = BASE_DIR / "storage" / "indian_creators_scheduled_progress.json"

BATCH_SIZE = 5
BATCH_DELAY_MINUTES = 30

def log(msg):
    print(msg, flush=True)

def upload_short_scheduled(file_path: str, title: str, description: str, tags: list, token: str, publish_at_iso: str) -> str:
    """Uploads YouTube video as scheduled (private + publishAt)."""
    file_size = os.path.getsize(file_path)
    init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "20",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at_iso,
            "selfDeclaredMadeForKids": False,
        },
    }

    init_req = urllib.request.Request(
        init_url,
        data=json.dumps(metadata).encode("utf-8"),
        method="POST"
    )
    init_req.add_header("Authorization", f"Bearer {token}")
    init_req.add_header("Content-Type", "application/json; charset=UTF-8")
    init_req.add_header("X-Upload-Content-Type", "video/mp4")
    init_req.add_header("X-Upload-Content-Length", str(file_size))

    with urllib.request.urlopen(init_req, timeout=30) as resp:
        upload_url = resp.headers.get("Location")

    if not upload_url:
        raise RuntimeError("No upload URL returned by YouTube resumable API")

    with open(file_path, "rb") as f:
        video_data = f.read()

    up_req = urllib.request.Request(
        upload_url,
        data=video_data,
        method="PUT"
    )
    up_req.add_header("Authorization", f"Bearer {token}")
    up_req.add_header("Content-Type", "video/mp4")
    up_req.add_header("Content-Length", str(file_size))

    with urllib.request.urlopen(up_req, timeout=120) as resp:
        resp_data = json.loads(resp.read().decode("utf-8"))
        return resp_data["id"]

def run_scheduled_pipeline(base_dt_utc: datetime):
    log("=" * 75)
    log("📅 YOUTUBE SCHEDULED UPLOADER: 30-MINUTE BATCH CADENCE")
    log(f"Base Scheduled Release Time: {base_dt_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    log(f"Batch Size: {BATCH_SIZE} videos")
    log(f"Delay Between Batches: {BATCH_DELAY_MINUTES} minutes")
    log("=" * 75)

    results = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                results = json.load(f)
        except Exception:
            results = []

    scheduled_ids = {r["id"] for r in results}
    thumb_gen = ThumbnailGenerator()
    token = get_oauth_token()

    # Split into batches
    batches = [SLICES_INDIAN_CREATORS[i:i + BATCH_SIZE] for i in range(0, len(SLICES_INDIAN_CREATORS), BATCH_SIZE)]

    for b_idx, batch in enumerate(batches, 1):
        batch_publish_dt = base_dt_utc + timedelta(minutes=(b_idx - 1) * BATCH_DELAY_MINUTES)
        publish_at_iso = batch_publish_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        publish_ist_str = (batch_publish_dt + timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y %I:%M %p IST")

        log(f"\n{'='*65}")
        log(f"📦 BATCH {b_idx}/{len(batches)} ({len(batch)} videos)")
        log(f"⏰ Scheduled YouTube Release Time: {publish_ist_str} ({publish_at_iso})")
        log(f"{'='*65}")

        for item in batch:
            cid = item["id"]
            if cid in scheduled_ids:
                log(f"  • Already scheduled: {cid}")
                continue

            vfile = OUT_DIR / f"{cid}_2k.mp4"
            tfile = THUMB_DIR / f"thumb_{cid}.jpg"
            title = item["title"]
            creator = item["creator"]
            desc = (
                f"{title}\n\n"
                f"🔥 Watch {creator} in this insane GTA 5 high-retention moment!\n"
                f"Subscribe for more daily Indian gaming highlights and viral clips.\n\n"
                f"#GTA5 #{creator.replace(' ', '')} #Shorts #IndianGaming #GamingHighlights"
            )
            tags = [
                creator.lower(), "gta 5", "shorts", "gaming", "indian gaming",
                "gta 5 funny moments", "gta 5 police chase", "techno gamerz",
                "carryminati", "triggered insaan"
            ]

            if not vfile.exists():
                log(f"  ❌ File missing: {vfile.name}, skipping.")
                continue

            log(f"  📤 Scheduling video: {vfile.name}")
            log(f"     Title: {title}")

            while True:
                try:
                    vid_id = upload_short_scheduled(str(vfile), title, desc, tags, token, publish_at_iso)
                    short_url = f"https://www.youtube.com/shorts/{vid_id}"
                    log(f"     ✅ SCHEDULED ON YOUTUBE: {short_url}")
                    log(f"        Will go Public at: {publish_ist_str}")

                    if tfile.exists():
                        ok = thumb_gen.upload_to_youtube(vid_id, str(tfile), token)
                        if ok:
                            log(f"        🎯 Thumbnail applied!")

                    results.append({
                        "id": cid,
                        "batch": b_idx,
                        "creator": creator,
                        "video_id": vid_id,
                        "url": short_url,
                        "title": title,
                        "publish_at_utc": publish_at_iso,
                        "publish_at_ist": publish_ist_str,
                        "scheduled_at": datetime.now(timezone.utc).isoformat()
                    })
                    scheduled_ids.add(cid)

                    with open(LOG_FILE, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=2)

                    time.sleep(3.0)
                    break

                except Exception as e:
                    err_str = str(e)
                    log(f"     ⚠️ Upload error: {err_str}")
                    if "429" in err_str or "rateLimitExceeded" in err_str or "uploadLimitExceeded" in err_str:
                        log("     🛑 YouTube Daily Upload Limit reached! Pausing until quota reset window...")
                        log("     Waiting 15 minutes before checking token & retrying...")
                        time.sleep(900)
                        token = get_oauth_token()
                    else:
                        time.sleep(5.0)
                        break

    log("\n" + "=" * 75)
    log(f"🎉 ALL BATCHES SCHEDULED! Total videos scheduled: {len(results)}")
    log("=" * 75)

if __name__ == "__main__":
    # Base scheduled time: Next reset at 1:30 PM IST (08:00 UTC tomorrow)
    # If today's reset is later or user wants immediate schedule, calculate from next day 08:00 UTC:
    now_utc = datetime.now(timezone.utc)
    target_utc = now_utc.replace(hour=8, minute=0, second=0, microsecond=0)
    if target_utc <= now_utc:
        target_utc += timedelta(days=1)
    
    run_scheduled_pipeline(target_utc)
