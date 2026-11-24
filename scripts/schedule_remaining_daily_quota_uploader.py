"""Master Uploader for Remaining Daily Quota (75+ 2K Vertical Clips).

Enforces:
- Scheduled waves spaced 20 minutes apart from 2:15 PM IST up to 1:00 AM IST.
- Direct Scheduled uploads (privacyStatus: "private", publishAt: <ISO UTC>).
- Likes visibility disabled for public (publicStatsViewable: False).
- CategoryId: 20 (Gaming) with high-CTR titles and viral GTA 6 tags.
- Automatic resume & quota management.
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

from sources.youtube_source import get_oauth_token

CLIPS_DIR = BASE_DIR / "storage" / "clips"
PROGRESS_FILE = BASE_DIR / "storage" / "scheduled_today_master_progress.json"
MANIFEST_FILE = Path(r"C:\Users\thega\.gemini\antigravity\brain\cc9214c0-7f61-456a-b5aa-8cae3dbac8e4\scheduled_remaining_quota_manifest.md")

VIRAL_TITLE_TEMPLATES = [
    "When a 6-Star Police Roadblock FAILS in GTA 6 💀🚨",
    "Fastest Supercar 170MPH Highway Drift in Vice City 🏎️💨",
    "Military Tank Shuts Down Entire SWAT Convoy 💥💣",
    "INSANE Helicopter Near-Miss Stunt in GTA 6 💀🚁",
    "Secret Weapon Cache Discovered in Leonida County 😱",
    "Speed Accidentally Crashed a $3M Hypercar in GTA 6 💀🏎️",
    "When Physics Break at 200 MPH in GTA 6 😭💀",
    "Can Any Vehicle Stop the GTA 6 Tank?! 💀🚀",
    "Undercover Vice City Ambush Caught on Camera 🚔💥",
    "Impossible Highway Weave Causes Massive 50-Car Pileup 💀🚗",
    "He Really Tried Running From 6-Star Cops in GTA 6 💀",
    "Best GTA 6 Escape You Will See Today 🎯🔥",
    "GTA 6 Drawbridge Jump Went Horribly Wrong 😭🏎️",
    "Military Tank vs 10 SWAT APCs in GTA 6 💣💥",
    "Stealing an Attack Helicopter in GTA 6 🚁🚨",
    "When You Accidentally Launch Your Car Into the Ocean 💀🌊",
    "Craziest Cop Chase in Vice City Downtown 🏎️🚔",
    "Testing Ragdoll Physics From Max Altitude in GTA 6 💀🪂",
    "GTA 6 Train Collision Test With 50 Supercars 🚂💥",
    "When You Find a Secret Underground Bunker in GTA 6 😱"
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
        res_data = json.loads(resp.read().decode("utf-8"))
        return res_data.get("id")

def generate_markdown_manifest(records):
    """Generates a comprehensive markdown report for the user."""
    lines = [
        "# Remaining Quota Scheduled 2K Upload Manifest",
        f"**Last Updated:** {datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d-%b-%Y %I:%M %p IST')}  ",
        f"**Total Videos Scheduled in Run:** {len(records)}  ",
        "**Privacy Status:** Scheduled (`private` with `publishAt`)  ",
        "**Likes Viewable:** Disabled (`publicStatsViewable: False`)  ",
        "",
        "---",
        "",
        "## Scheduled Clips Schedule",
        "",
        "| # | Video ID | Wave | Scheduled Time (IST) | Likes Viewable | Title | Shorts Link |",
        "| :-: | :--- | :-: | :--- | :-: | :--- | :--- |"
    ]
    for idx, r in enumerate(records, 1):
        lines.append(
            f"| **{idx}** | `{r['video_id']}` | Wave {r['wave']} | **{r['publish_at_ist']}** | ❌ Disabled | {r['title']} | [Watch Short]({r['url']}) |"
        )
    with open(MANIFEST_FILE, "w", encoding="utf-8") as mf:
        mf.write("\n".join(lines))

def run_batch_upload():
    log("==================================================================")
    log("REMAINING QUOTA 2K MASTER SCHEDULED UPLOADER STARTED")
    log("==================================================================")

    # 1. Collect valid clips
    already_uploaded = set()
    uploaded_records = []
    
    # Check 1:30 PM progress file
    p_130 = BASE_DIR / "storage" / "scheduled_130pm_progress.json"
    if p_130.exists():
        try:
            with open(p_130, "r", encoding="utf-8") as f:
                for r in json.load(f):
                    already_uploaded.add(r.get("filename"))
        except Exception:
            pass

    # Check master progress file
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                uploaded_records = json.load(f)
                for r in uploaded_records:
                    already_uploaded.add(r.get("filename"))
        except Exception:
            uploaded_records = []

    all_files = sorted([f for f in os.listdir(CLIPS_DIR) if f.endswith(".mp4")])
    valid_queue = []
    for f in all_files:
        if f in already_uploaded:
            continue
        p = CLIPS_DIR / f
        if p.stat().st_size > 5_000_000:
            valid_queue.append(p)

    log(f"Total clips found: {len(all_files)}")
    log(f"Already uploaded: {len(already_uploaded)}")
    log(f"Pending upload queue: {len(valid_queue)} clips")

    if not valid_queue:
        log("No new clips to upload!")
        return

    # Calculate wave distribution: Waves spaced 20 mins apart from 2:15 PM IST
    now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    base_time_ist = datetime(now_ist.year, now_ist.month, now_ist.day, 14, 15, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    if now_ist > base_time_ist:
        base_time_ist = now_ist + timedelta(minutes=5)

    token = get_oauth_token()
    if not token:
        log("ERROR: Could not get OAuth token!")
        return

    success_count = 0
    for idx, fpath in enumerate(valid_queue):
        wave_index = idx // 3  # 3 videos per wave
        slot_in_wave = idx % 3
        wave_num = wave_index + 1
        
        # Space waves 20 minutes apart, and clips within wave 2 minutes apart
        wave_time_ist = base_time_ist + timedelta(minutes=20 * wave_index + 2 * slot_in_wave)
        publish_at_utc = wave_time_ist.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        title = VIRAL_TITLE_TEMPLATES[idx % len(VIRAL_TITLE_TEMPLATES)]
        desc = (
            f"{title}\n\n"
            f"Watch the craziest 2K moments from GTA 6 gameplay in 60 FPS!\n\n"
            f"#Shorts #GTA6 #GrandTheftAuto #Gaming #Trending"
        )
        tags = ["GTA 6", "GTA 6 Gameplay", "Shorts", "Gaming", "Vice City", "GTA VI"]

        log(f"[{idx+1}/{len(valid_queue)}] Uploading: {fpath.name}")
        log(f"  Title: {title}")
        log(f"  Wave {wave_num} -> Scheduled: {wave_time_ist.strftime('%I:%M %p IST')} (UTC: {publish_at_utc})")
        log(f"  Likes Disabled (publicStatsViewable: False)")

        try:
            token = get_oauth_token()
            vid_id = upload_scheduled(str(fpath), title, desc, tags, token, publish_at_utc)
            yt_url = f"https://www.youtube.com/shorts/{vid_id}"
            log(f"  SUCCESS! Video ID: {vid_id} -> {yt_url}")
            success_count += 1

            rec = {
                "filename": fpath.name,
                "video_id": vid_id,
                "url": yt_url,
                "title": title,
                "wave": wave_num,
                "publish_at_ist": wave_time_ist.strftime("%d-%b-%Y %I:%M %p IST"),
                "publish_at_utc": publish_at_utc,
                "likes_disabled": True,
                "status": "SCHEDULED",
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }
            uploaded_records.append(rec)
            
            with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                json.dump(uploaded_records, pf, indent=2)

            # Update markdown manifest every 5 uploads
            if success_count % 5 == 0 or idx == len(valid_queue) - 1:
                generate_markdown_manifest(uploaded_records)

        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", "ignore")
            log(f"  FAILED with HTTP {he.code}: {err_body}")
            if "uploadLimitExceeded" in err_body or he.code == 429:
                log("DAILY UPLOAD QUOTA REACHED (100/100 limit exhausted). Stopping uploader.")
                break
        except Exception as e:
            log(f"  FAILED: {e}")

        time.sleep(3)  # Brief pause between resumable uploads

    generate_markdown_manifest(uploaded_records)
    log(f"Batch completed! Successfully scheduled {success_count} new uploads today.")

if __name__ == "__main__":
    run_batch_upload()
