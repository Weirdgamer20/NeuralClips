"""High-Speed Concurrent Unlister for ALL YouTube Videos with Under 3 Views.

Targets every video on the channel with viewCount < 3 (0, 1, or 2 views)
that is not already unlisted. Uses ThreadPoolExecutor for rapid, safe execution.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from sources.youtube_source import get_oauth_token

IST = timezone(timedelta(hours=5, minutes=30))
ANALYTICS_FILE = BASE_DIR / "storage" / "all_historical_videos_analytics.json"
PROGRESS_FILE = BASE_DIR / "storage" / "unlisted_clips_progress.json"

progress_lock = threading.Lock()

def log(msg):
    try:
        clean = str(msg).encode("ascii", "replace").decode("ascii")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {clean}", flush=True)
    except Exception:
        pass

def unlist_single(item: dict, token: str) -> tuple:
    vid = item["video_id"]
    title = item.get("title", "")
    cat_id = item.get("categoryId", "20")

    update_url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,status"
    payload = {
        "id": vid,
        "snippet": {
            "title": title,
            "categoryId": cat_id
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        update_url,
        data=data_bytes,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="PUT"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            ok = res.get("status", {}).get("privacyStatus") == "unlisted"
            return vid, ok, None
    except urllib.error.HTTPError as he:
        err = he.read().decode("utf-8", errors="replace")
        return vid, False, f"HTTP {he.code}: {err}"
    except Exception as e:
        return vid, False, str(e)

def main():
    log("=" * 80)
    log("FAST CONCURRENT UNLISTER FOR ALL VIDEOS UNDER 3 VIEWS")
    log("=" * 80)

    token = get_oauth_token()
    if not token:
        log("Error: Could not retrieve OAuth token!")
        return

    if not ANALYTICS_FILE.exists():
        log(f"Error: {ANALYTICS_FILE} not found!")
        return

    with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_videos = data.get("videos", [])
    
    # Target ALL videos with < 3 views whose current status is NOT unlisted
    all_under_3 = [
        v for v in all_videos
        if int(v.get("views", 0)) < 3 and v.get("privacy") != "unlisted"
    ]

    log(f"Total videos with < 3 views needing unlisting: {len(all_under_3)}")

    # Load existing progress
    progress = {}
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as pf:
                progress = json.load(pf)
        except Exception:
            progress = {}

    already_done = {k for k, v in progress.items() if v.get("status") == "unlisted"}
    remaining = [v for v in all_under_3 if v["video_id"] not in already_done]

    log(f"Already unlisted previously: {len(already_done)}")
    log(f"Remaining to process right now: {len(remaining)}")

    if not remaining:
        log("All qualifying videos are ALREADY unlisted!")
        return

    success_count = len(already_done)
    total_target = len(all_under_3)
    completed_now = 0

    # Execute with 5 worker threads
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(unlist_single, item, token): item
            for item in remaining
        }

        for future in as_completed(futures):
            item = futures[future]
            vid = item["video_id"]
            title = item.get("title", "")
            views = item.get("views", 0)

            vid_ret, ok, err = future.result()
            completed_now += 1

            if ok:
                success_count += 1
                log(f"[{success_count}/{total_target}] UNLISTED ({views} views): '{title[:45]}...' (ID: {vid})")
                with progress_lock:
                    progress[vid] = {
                        "video_id": vid,
                        "title": title,
                        "views": views,
                        "status": "unlisted",
                        "unlisted_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")
                    }
                    with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                        json.dump(progress, pf, indent=2)
            else:
                log(f"[FAIL] {vid}: {err}")
                with progress_lock:
                    progress[vid] = {"status": "failed", "video_id": vid, "error": err}
                    with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                        json.dump(progress, pf, indent=2)

    log("\n" + "=" * 80)
    log(f"COMPLETE! Total videos under 3 views now UNLISTED: {success_count}/{total_target}")
    log("=" * 80)

if __name__ == "__main__":
    main()
