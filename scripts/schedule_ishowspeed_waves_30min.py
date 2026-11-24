"""Scheduled Master Uploader for 100 IShowSpeed 90-Second Clips across 24 Waves (Up to 1:00 AM).

Features:
- Enforces 24 waves spaced 30 minutes apart from 01:30 PM IST (Nov 23) to 01:00 AM IST (Nov 24).
- Total 100 videos (exactly maxing out YouTube Data API rolling daily quota).
- Direct Scheduled uploads (`privacyStatus: "private"`, `publishAt: <ISO 8601 UTC>`).
- Uploads custom high-CTR vertical 1080x1920 thumbnails.
- Automatically handles YouTube daily API quota reset window (13:30 IST).
- Saves progress to `storage/ishowspeed_scheduled_progress.json` and updates markdown manifest.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path("d:/vidclip")
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from config.slices_ishowspeed_24waves_manifest import WAVES, OUTPUT_DIR, THUMB_DIR
from sources.youtube_source import get_oauth_token
from rendering.thumbnail_generator import ThumbnailGenerator

PROGRESS_FILE = BASE_DIR / "storage" / "ishowspeed_scheduled_progress.json"
MANIFEST_ARTIFACT = Path(r"C:\Users\thega\.gemini\antigravity\brain\cc9214c0-7f61-456a-b5aa-8cae3dbac8e4\ishowspeed_scheduled_waves_manifest.md")


def log(msg):
    try:
        clean = str(msg).encode("ascii", "replace").decode("ascii")
        print(clean, flush=True)
    except Exception:
        pass


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
            "publicStatsViewable": False,
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

    try:
        with urllib.request.urlopen(init_req, timeout=30) as resp:
            upload_url = resp.headers.get("Location")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTPError {e.code}: {err_body}")

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

    try:
        with urllib.request.urlopen(up_req, timeout=120) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            return resp_data["id"]
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTPError {e.code}: {err_body}")


def update_artifact(results: list):
    """Updates markdown artifact tracking all scheduled waves."""
    try:
        md = "# ⚡ IShowSpeed GTA Stream: Master 24-Wave Scheduled Manifest (Up to 1:00 AM)\n\n"
        md += f"**Updated:** {datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d-%b-%Y %I:%M:%S %p IST')}\n"
        md += f"**Total Schedule Slots:** 24 Waves (30 minutes apart from 01:30 PM to 01:00 AM)\n"
        md += f"**Total Clips Target:** 100 Clips (90 seconds each | 100% Daily API Quota Max)\n"
        md += f"**Successfully Scheduled:** {len(results)} of 100\n\n"
        md += "| # | Wave | Video ID | Scheduled IST | Scheduled UTC | YouTube Link | Status |\n"
        md += "|---|---|---|---|---|---|---|\n"

        for idx, r in enumerate(results, start=1):
            url_link = f"[{r['video_id']}]({r['url']})" if r.get("url") else "Pending"
            md += f"| {idx:03d} | Wave {r['wave']:02d} | `{r['id']}` | {r['publish_at_ist']} | `{r['publish_at_utc']}` | {url_link} | {r.get('status', 'SCHEDULED')} |\n"

        with open(MANIFEST_ARTIFACT, "w", encoding="utf-8") as f:
            f.write(md)
    except Exception as e:
        log(f"Artifact update error: {e}")


def run_waves_uploader():
    log("=" * 75)
    log("🔥 ISHOWSPEED 24-WAVE SCHEDULED UPLOADER LAUNCHED (UP TO 1:00 AM)")
    log("=" * 75)

    results = []
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                results = json.load(f)
        except Exception:
            results = []

    scheduled_ids = {r["id"] for r in results}
    thumb_gen = ThumbnailGenerator()
    token = get_oauth_token()

    total_vids = sum(len(w["videos"]) for w in WAVES)
    log(f"Total Waves: {len(WAVES)} | Total Videos to Schedule: {total_vids}")

    # Precise sleep until 13:30:05 IST if before window
    now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    target_reset_ist = now_ist.replace(hour=13, minute=30, second=5, microsecond=0)
    if now_ist < target_reset_ist:
        wait_secs = int((target_reset_ist - now_ist).total_seconds())
        log(f"⏰ Pausing {wait_secs}s until exact 13:30:05 IST YouTube daily quota reset window...")
        time.sleep(wait_secs)
        log("🚀 13:30:05 IST REACHED! Refreshing OAuth token and beginning scheduled wave uploads...")
        token = get_oauth_token()

    for wave in WAVES:
        w_id = wave["wave_id"]
        w_name = wave["wave_name"]
        pub_utc = wave["publish_at_utc"]
        pub_ist = wave["publish_at_ist"]

        # Ensure publishAt is strictly in the future (at least 3 minutes ahead)
        now_utc = datetime.now(timezone.utc)
        target_dt_utc = datetime.fromisoformat(pub_utc.replace("Z", "+00:00"))
        if target_dt_utc <= now_utc + timedelta(minutes=2):
            safe_dt_utc = now_utc + timedelta(minutes=5)
            pub_utc = safe_dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            safe_dt_ist = safe_dt_utc + timedelta(hours=5, minutes=30)
            pub_ist = safe_dt_ist.strftime("%d-%b-%Y %I:%M %p IST")

        log(f"\n{'='*70}")
        log(f"🌊 WAVE {w_id:02d}: {w_name}")
        log(f"⏰ Scheduled YouTube Release Time: {pub_ist} ({pub_utc})")
        log(f"🎯 Target: {len(wave['videos'])} videos (90s each)")
        log(f"{'='*70}")

        for vid in wave["videos"]:
            cid = vid["id"]
            if cid in scheduled_ids:
                log(f"  • Already scheduled: {cid}")
                continue

            vfile = Path(OUTPUT_DIR) / f"{cid}.mp4"
            tfile = Path(THUMB_DIR) / f"{cid}.jpg"

            # Wait if file is still being rendered
            retry_count = 0
            while not (vfile.exists() and vfile.stat().st_size > 10_000_000):
                if retry_count % 6 == 0:
                    log(f"  ⏳ Waiting for {vfile.name} to finish rendering...")
                time.sleep(5.0)
                retry_count += 1
                if retry_count > 120:
                    break

            if not (vfile.exists() and vfile.stat().st_size > 10_000_000):
                log(f"  ❌ File render timeout: {vfile.name}, skipping.")
                continue

            log(f"  📤 Scheduling video: {vfile.name} ({vfile.stat().st_size // (1024*1024)} MB)")
            log(f"     Title: {vid['title']}")

            attempt = 0
            while True:
                attempt += 1
                try:
                    if not token:
                        token = get_oauth_token()

                    vid_id = upload_short_scheduled(
                        str(vfile),
                        vid["title"],
                        vid["description"],
                        vid["tags"],
                        token,
                        pub_utc
                    )
                    short_url = f"https://www.youtube.com/shorts/{vid_id}"
                    log(f"     ✅ SCHEDULED ON YOUTUBE: {short_url}")
                    log(f"        Will go Public at: {pub_ist}")

                    if tfile.exists():
                        try:
                            ok = thumb_gen.upload_to_youtube(vid_id, str(tfile), token)
                            if ok:
                                log(f"        🎨 Custom thumbnail applied!")
                        except Exception as te:
                            log(f"        Thumbnail note: {te}")

                    res_entry = {
                        "id": cid,
                        "wave": w_id,
                        "video_id": vid_id,
                        "url": short_url,
                        "title": vid["title"],
                        "publish_at_utc": pub_utc,
                        "publish_at_ist": pub_ist,
                        "status": "SCHEDULED",
                        "scheduled_at": datetime.now(timezone.utc).isoformat()
                    }
                    results.append(res_entry)
                    scheduled_ids.add(cid)

                    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=2)

                    update_artifact(results)
                    time.sleep(3.0)
                    break

                except Exception as e:
                    err_str = str(e)
                    log(f"     ⚠️ Upload attempt {attempt} error: {err_str[:200]}")
                    if "429" in err_str or "rateLimitExceeded" in err_str or "uploadLimitExceeded" in err_str or "exceeded the number of videos" in err_str:
                        now_utc = datetime.now(timezone.utc)
                        reset_utc = now_utc.replace(hour=8, minute=0, second=0, microsecond=0)
                        if reset_utc <= now_utc:
                            reset_utc += timedelta(days=1)
                        seconds_left = max(60, int((reset_utc - now_utc).total_seconds()))
                        mins_left = seconds_left // 60
                        log(f"     🛑 YouTube Daily Upload Limit reached! Approx {mins_left}m until quota reset window (13:30 IST).")
                        log("     Sleeping 5 minutes before checking token & retrying...")
                        time.sleep(300)
                        token = get_oauth_token()
                    else:
                        time.sleep(10.0)
                        token = get_oauth_token()

    log("\n" + "=" * 75)
    log(f"🎉 ALL 24 WAVES PROCESSED! Total videos scheduled: {len(results)}")
    log("=" * 75)


if __name__ == "__main__":
    run_waves_uploader()
