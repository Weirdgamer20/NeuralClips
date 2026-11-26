"""Unlist All Videos with Under 3 Views via YouTube Data API v3.

Reads current video statistics from all_historical_videos_analytics.json (or live API),
filters for public videos with viewCount < 3, and updates privacyStatus to 'unlisted'.
Includes progress checkpointing, batch pacing, and detailed reporting.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
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

def log(msg):
    try:
        clean = str(msg).encode("ascii", "replace").decode("ascii")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {clean}", flush=True)
    except Exception:
        pass

def unlist_video(video_id: str, title: str, category_id: str, token: str) -> bool:
    """Updates video privacyStatus to unlisted."""
    update_url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,status"
    payload = {
        "id": video_id,
        "snippet": {
            "title": title,
            "categoryId": category_id or "20"
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
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("status", {}).get("privacyStatus") == "unlisted"

def main():
    log("=" * 80)
    log("UNLIST VIDEOS WITH UNDER 3 VIEWS")
    log("=" * 80)

    token = get_oauth_token()
    if not token:
        log("Error: Could not retrieve OAuth token!")
        return

    if not ANALYTICS_FILE.exists():
        log(f"Error: Analytics file {ANALYTICS_FILE} not found!")
        return

    with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_videos = data.get("videos", [])
    log(f"Loaded {len(all_videos)} total videos from analytics cache.")

    # Exclude videos that are already unlisted or private (e.g. future scheduled waves)
    # Only target public videos with views < 3
    candidates = [
        v for v in all_videos
        if v.get("privacy") == "public" and int(v.get("views", 0)) < 3
    ]

    log(f"Found {len(candidates)} public videos with under 3 views.")

    # Load existing unlisted progress
    progress = {}
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as pf:
                progress = json.load(pf)
        except Exception:
            progress = {}

    already_done = {k for k, v in progress.items() if v.get("status") == "unlisted"}
    remaining = [c for c in candidates if c["video_id"] not in already_done]

    log(f"Already unlisted in previous runs: {len(already_done)}")
    log(f"Remaining to process: {len(remaining)}")

    if not remaining:
        log("No remaining videos to unlist! All eligible videos have been unlisted.")
        return

    success_count = 0
    quota_exhausted = False

    for idx, item in enumerate(remaining, 1):
        vid = item["video_id"]
        title = item.get("title", "")
        views = item.get("views", 0)
        pub_ist = item.get("published_at_ist", "")

        log(f"[{idx}/{len(remaining)}] Unlisting: '{title[:45]}...' (ID: {vid}, Views: {views}, Date: {pub_ist[:10]})")

        # Refresh token every 20 videos
        if idx % 20 == 0:
            token = get_oauth_token() or token

        try:
            # We need categoryId; fetch snippet if not cached
            cat_id = item.get("categoryId", "20")
            ok = unlist_video(vid, title, cat_id, token)
            if ok:
                log(f"   SUCCESS -> Unlisted: https://www.youtube.com/shorts/{vid}")
                progress[vid] = {
                    "video_id": vid,
                    "title": title,
                    "views": views,
                    "published_at_ist": pub_ist,
                    "unlisted_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST"),
                    "status": "unlisted"
                }
                success_count += 1
            else:
                log(f"   FAILED to verify unlisted status for {vid}")
                progress[vid] = {"status": "failed", "video_id": vid}

            # Save progress incrementally
            with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                json.dump(progress, pf, indent=2)

            # Pacing to respect API rate limits
            time.sleep(0.5)

        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", errors="replace")
            log(f"   HTTP Error {he.code}: {err_body}")

            if "insufficientAuthenticationScopes" in err_body or "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in err_body:
                log("\n" + "!" * 80)
                log("CRITICAL ERROR: Insufficient OAuth Scopes!")
                log("The current refresh token only has readonly and upload permissions.")
                log("To unlist/edit existing videos, the 'https://www.googleapis.com/auth/youtube' scope is required.")
                log("!" * 80)
                break

            if "quotaExceeded" in err_body or "dailyLimitExceeded" in err_body:
                log("   YouTube API quota limit reached!")
                quota_exhausted = True
                break

            progress[vid] = {"status": "error", "error": err_body, "video_id": vid}
            with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                json.dump(progress, pf, indent=2)

        except Exception as e:
            log(f"   Unexpected error: {e}")
            progress[vid] = {"status": "error", "error": str(e), "video_id": vid}

    log("=" * 80)
    log(f"Process ended. Successfully unlisted in this run: {success_count}")
    log(f"Total unlisted recorded in progress: {len([k for k, v in progress.items() if v.get('status') == 'unlisted'])}")
    log("=" * 80)

if __name__ == "__main__":
    main()
