"""Master Uploader & Wave Scheduler for Speed 4K Vertical Master Clips.

Uploads all 4K vertical cuts to YouTube with:
- Staggered scheduled waves spaced 30 minutes apart starting at 3:30 PM IST.
- Scheduled release (privacyStatus: "private", publishAt: <ISO UTC>).
- Likes visibility DISABLED for public (publicStatsViewable: False).
- CategoryId: 20 (Gaming) with high-CTR titles and viral GTA 6 tags.
- Detailed progress tracking and automatic error recovery.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from sources.youtube_source import get_oauth_token

STORAGE_DIR = BASE_DIR / "storage"
CLIPS_DIR = STORAGE_DIR / "clips_4k"
MANIFEST_PATH = CLIPS_DIR / "speed_4k_master_manifest.json"
PROGRESS_FILE = STORAGE_DIR / "speed_4k_upload_progress.json"

IST = timezone(timedelta(hours=5, minutes=30))

WAVE_SCHEDULE = [
    {"wave": 1, "ist": "2026-11-26 15:30:00 IST", "utc": "2026-11-26T10:00:00.000Z"},
    {"wave": 2, "ist": "2026-11-26 16:00:00 IST", "utc": "2026-11-26T10:30:00.000Z"},
    {"wave": 3, "ist": "2026-11-26 16:30:00 IST", "utc": "2026-11-26T11:00:00.000Z"},
    {"wave": 4, "ist": "2026-11-26 17:00:00 IST", "utc": "2026-11-26T11:30:00.000Z"},
    {"wave": 5, "ist": "2026-11-26 17:30:00 IST", "utc": "2026-11-26T12:00:00.000Z"},
    {"wave": 6, "ist": "2026-11-26 18:00:00 IST", "utc": "2026-11-26T12:30:00.000Z"},
]

def log(msg):
    try:
        clean = str(msg).encode("ascii", "replace").decode("ascii")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {clean}", flush=True)
    except Exception:
        pass

def upload_scheduled(file_path: str, title: str, description: str, tags: list, token: str, publish_at_iso: str) -> str:
    """Uploads video as scheduled (private + publishAt) with likes turned off."""
    file_size = os.path.getsize(file_path)
    init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "20"
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at_iso,
            "selfDeclaredMadeForKids": False,
            "publicStatsViewable": False  # TURNS OFF LIKES FOR PUBLIC
        }
    }

    init_req = urllib.request.Request(init_url, data=json.dumps(metadata).encode("utf-8"), method="POST")
    init_req.add_header("Authorization", f"Bearer {token}")
    init_req.add_header("Content-Type", "application/json; charset=UTF-8")
    init_req.add_header("X-Upload-Content-Type", "video/mp4")
    init_req.add_header("X-Upload-Content-Length", str(file_size))

    with urllib.request.urlopen(init_req, timeout=30) as resp:
        upload_url = resp.headers.get("Location")

    if not upload_url:
        raise RuntimeError("No upload URL returned from YouTube!")

    with open(file_path, "rb") as vf:
        video_bytes = vf.read()

    upload_req = urllib.request.Request(upload_url, data=video_bytes, method="PUT")
    upload_req.add_header("Authorization", f"Bearer {token}")
    upload_req.add_header("Content-Type", "video/mp4")
    upload_req.add_header("Content-Length", str(file_size))

    with urllib.request.urlopen(upload_req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result.get("id", "")

def main():
    log("=" * 75)
    log("  SPEED 4K MASTER CLIP SCHEDULED WAVE UPLOADER")
    log("  - Quality: 2160x3840 @ 60 FPS (True 4K Vertical Canvas)")
    log("  - Waves: Spaced 30 minutes apart starting at 3:30 PM IST")
    log("  - Likes: Hidden from public (publicStatsViewable: False)")
    log("=" * 75)

    # 1. Clean swap for speed_4k_02 if needed
    clean_02 = CLIPS_DIR / "speed_4k_02_clean.mp4"
    master_02 = CLIPS_DIR / "speed_4k_02_4k_master.mp4"
    if clean_02.exists() and clean_02.stat().st_size > 10_000_000:
        try:
            if master_02.exists():
                master_02.unlink()
            clean_02.rename(master_02)
            log("Replaced speed_4k_02 with optimized clean master file.")
        except Exception as e:
            log(f"Notice swapping 02: {e}")

    # 2. Load manifest
    if not MANIFEST_PATH.exists():
        log(f"Error: Manifest {MANIFEST_PATH} not found!")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        clips = json.load(f)

    # Load existing progress
    uploaded = []
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                uploaded = json.load(f)
        except Exception:
            uploaded = []

    uploaded_ids = {u.get("clip_id") for u in uploaded if u.get("video_id")}
    log(f"Total 4K clips in manifest: {len(clips)}. Already uploaded: {len(uploaded_ids)}")

    token = get_oauth_token()
    if not token:
        log("Error: Could not retrieve OAuth token!")
        return

    for idx, item in enumerate(clips):
        clip_id = item["id"]
        if clip_id in uploaded_ids:
            log(f"Clip {clip_id} already uploaded. Skipping.")
            continue

        file_path = str(CLIPS_DIR / f"{clip_id}_4k_master.mp4")
        if not os.path.exists(file_path):
            log(f"File {file_path} not found! Skipping.")
            continue

        file_size_mb = os.path.getsize(file_path) / (1024 ** 2)
        sched = WAVE_SCHEDULE[idx % len(WAVE_SCHEDULE)]
        log(f"\n[{idx+1}/{len(clips)}] Uploading 4K Master: '{item['title']}' ({file_size_mb:.1f} MB)...")
        log(f"   -> Scheduled Wave {sched['wave']}: {sched['ist']} ({sched['utc']})")
        log("   -> Likes Visibility: False (Turned OFF for public)")

        # Refresh token every 3 uploads
        if idx % 3 == 0:
            token = get_oauth_token() or token

        try:
            vid_id = upload_scheduled(
                file_path=file_path,
                title=item["title"],
                description=item["desc"],
                tags=item["tags"],
                token=token,
                publish_at_iso=sched["utc"]
            )
            log(f"   SUCCESS! Uploaded Video ID: {vid_id}")
            log(f"   Direct Short Link: https://www.youtube.com/shorts/{vid_id}")

            record = {
                "clip_id": clip_id,
                "video_id": vid_id,
                "title": item["title"],
                "wave": sched["wave"],
                "publish_at_ist": sched["ist"],
                "publish_at_utc": sched["utc"],
                "file_path": file_path,
                "file_size_mb": round(file_size_mb, 2),
                "public_stats_viewable": False,
                "uploaded_at_ist": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST"),
                "url": f"https://www.youtube.com/shorts/{vid_id}"
            }
            uploaded.append(record)
            with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                json.dump(uploaded, pf, indent=2)

            # Polite pacing between 4K uploads
            time.sleep(5)

        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", errors="replace")
            log(f"   HTTP Error {he.code}: {err_body}")
            if "uploadLimitExceeded" in err_body:
                log("   YouTube daily upload quota limit reached for this project window!")
                break
        except Exception as e:
            log(f"   Upload error: {e}")

    log("\n" + "=" * 75)
    log(f"Batch completed! Total 4K clips scheduled: {len(uploaded)}/{len(clips)}")
    log(f"Progress recorded in: {PROGRESS_FILE}")
    log("=" * 75)

if __name__ == "__main__":
    main()
