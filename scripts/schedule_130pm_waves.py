"""1:30 PM Scheduled Wave Master Uploader.

Scheduled for 1:30 PM IST (13:30 IST) when YouTube daily API quota window resets.
Enforces:
- `privacyStatus`: "private"
- `publishAt`: Staggered wave schedule starting at 1:30 PM IST (30-minute intervals)
- `publicStatsViewable`: False (turns off likes visibility to public)
- High-CTR titles, tags, and categoryId 20 (Gaming).
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

QUEUE_DIR = BASE_DIR / "storage" / "ready_for_130pm_upload"
PROGRESS_FILE = BASE_DIR / "storage" / "scheduled_130pm_progress.json"
MANIFEST_ARTIFACT = Path(r"C:\Users\thega\.gemini\antigravity\brain\cc9214c0-7f61-456a-b5aa-8cae3dbac8e4\scheduled_130pm_manifest.md")

VIRAL_TITLES = [
    "Coringa Was NOT Expecting This in GTA 6 💀",
    "Fastest Supercar Drift Escape in Vice City 🏎️💨",
    "When a 6-Star Police Roadblock FAILS Instantly 🚨💀",
    "Military Tank Rampage Shuts Down the Entire Highway 💥💣",
    "INSANE Near-Miss Helicopter Stunt in GTA 6 💀🚁",
    "Secret Weapon Cache Discovered in Leonida County 😱",
    "Can Any Cop Car Survive a Head-On Collision?! 💀🚗",
    "Extreme 200MPH Highway Weave Through Heavy Traffic 🔥",
    "When Physics Break in GTA 6 at Top Speed 😭💀",
    "Undercover Swat Ambush Caught on Camera in GTA 6 🚔"
]

def log(msg):
    try:
        clean = str(msg).encode("ascii", "replace").decode("ascii")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {clean}", flush=True)
    except Exception:
        pass

def probe_upload_quota(token: str) -> bool:
    """Probes if the 100-video upload quota has cleared."""
    init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    metadata = {
        "snippet": {"title": "Quota Probe", "categoryId": "20"},
        "status": {"privacyStatus": "private"}
    }
    req = urllib.request.Request(init_url, data=json.dumps(metadata).encode("utf-8"), method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=UTF-8")
    req.add_header("X-Upload-Content-Type", "video/mp4")
    req.add_header("X-Upload-Content-Length", "1000")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 201)
    except urllib.error.HTTPError as e:
        if e.code == 429 or "uploadLimitExceeded" in e.read().decode("utf-8", "ignore"):
            return False
        return False
    except Exception:
        return False

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

def run_schedule_pipeline():
    log("==================================================================")
    log("1:30 PM SCHEDULED WAVE MASTER UPLOADER INITIATED")
    log("==================================================================")
    
    # 1. Gather all files in queue
    files = sorted([QUEUE_DIR / f for f in os.listdir(QUEUE_DIR) if f.endswith(".mp4")])
    log(f"Queued clips in {QUEUE_DIR.name}: {len(files)}")
    if not files:
        log("No clips found in queue directory!")
        return

    # Check progress
    uploaded_records = []
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                uploaded_records = json.load(f)
        except Exception:
            uploaded_records = []
    uploaded_names = set(r.get("filename") for r in uploaded_records)

    # Calculate scheduled wave times starting at 1:30 PM IST (today)
    now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    base_scheduled_ist = datetime(now_ist.year, now_ist.month, now_ist.day, 13, 30, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    if now_ist > base_scheduled_ist:
        base_scheduled_ist = now_ist + timedelta(minutes=5)

    token = get_oauth_token()
    
    # 2. Wait until 1:30 PM IST or quota reset
    log(f"Target Start Time: {base_scheduled_ist.strftime('%d-%b-%Y %I:%M %p IST')}")
    while True:
        curr_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
        rem_sec = (base_scheduled_ist - curr_ist).total_seconds()
        if rem_sec > 0:
            log(f"Waiting for 1:30 PM IST quota reset window... ({rem_sec/60:.1f} minutes remaining)")
            time.sleep(min(60, rem_sec))
            continue
        
        # Probe quota
        token = get_oauth_token()
        if probe_upload_quota(token):
            log("SUCCESS: Daily upload quota has reset! Commencing scheduled uploads...")
            break
        else:
            log("Quota still shows 429 rate limit. Waiting 60 seconds before next probe...")
            time.sleep(60)

    # 3. Upload loop with 30-minute wave spacing
    for idx, fpath in enumerate(files):
        if fpath.name in uploaded_names:
            log(f"Skipping already uploaded file: {fpath.name}")
            continue

        wave_num = (idx // 4) + 1
        wave_time_ist = base_scheduled_ist + timedelta(minutes=30 * (idx // 4) + (idx % 4) * 3)
        publish_at_utc = wave_time_ist.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        title = VIRAL_TITLES[idx % len(VIRAL_TITLES)]
        desc = (
            f"{title}\n\n"
            f"Watch the craziest moments from GTA 6 gameplay in 2K high-definition 60 FPS!\n\n"
            f"#Shorts #GTA6 #GrandTheftAuto #Gaming #Trending"
        )
        tags = ["GTA 6", "GTA 6 Gameplay", "Shorts", "Gaming", "Vice City", "GTA VI"]

        log(f"[{idx+1}/{len(files)}] Uploading: {fpath.name}")
        log(f"  Title: {title}")
        log(f"  Scheduled: {wave_time_ist.strftime('%I:%M %p IST')} (UTC: {publish_at_utc})")
        log(f"  Likes Disabled (publicStatsViewable: False)")

        try:
            token = get_oauth_token()
            vid_id = upload_scheduled(str(fpath), title, desc, tags, token, publish_at_utc)
            yt_url = f"https://www.youtube.com/shorts/{vid_id}"
            log(f"  SUCCESS! Video ID: {vid_id} -> {yt_url}")

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

        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", "ignore")
            log(f"  FAILED with HTTP {he.code}: {err_body}")
            if "uploadLimitExceeded" in err_body or he.code == 429:
                log("Upload limit encountered. Halting.")
                break
        except Exception as e:
            log(f"  FAILED: {e}")

        time.sleep(5)

    log(f"Pipeline complete! Total scheduled uploads: {len(uploaded_records)}")

if __name__ == "__main__":
    run_schedule_pipeline()
