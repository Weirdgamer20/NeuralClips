"""Scheduled API Uploader for 1:30 PM (13:30 IST).

Monitors local time and automatically triggers the YouTube API upload of approved 2K cuts
as soon as the 1:30 PM quota window opens, applying custom thumbnails and titles.
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from sources.youtube_source import get_oauth_token
from rendering.thumbnail_generator import ThumbnailGenerator
from scripts.publish_approved_2k_cuts import upload_short_public

REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
THUMB_DIR = BASE_DIR / "storage" / "thumbnails"

CLIPS_QUEUE = [
    {
        "id": "cut_01",
        "file": REVIEW_DIR / "cut_01_supercar_pursuit_1440p60.mp4",
        "thumb": THUMB_DIR / "thumb_cut_01_approved.jpg",
        "title": "Fastest Supercar 160MPH Police Chase in GTA 6 💀 #Shorts",
        "description": "160 MPH highway police chase in Vice City!\nWatch until the end for the insane near-miss.\n\n#GTA6 #Shorts #Gaming #ViceCity #PoliceChase",
        "tags": ["gta 6", "gta 6 police chase", "gta 6 supercar", "shorts", "gaming"],
    },
    {
        "id": "cut_02",
        "file": REVIEW_DIR / "cut_02_supercar_bridge_escape_1440p60.mp4",
        "thumb": THUMB_DIR / "thumb_cut_02_approved.jpg",
        "title": "When GTA 6 Police Roadblock FAILS Instantly 💀🚨 #Shorts",
        "description": "5-Star police set up a roadblock on the bridge, but the supercar hits the ramp!\nWatch the chain reaction smash.\n\n#GTA6 #Shorts #Gaming #GTA6Fails #ViceCity",
        "tags": ["gta 6", "gta 6 stunts", "gta 6 crash", "shorts", "gaming"],
    },
    {
        "id": "cut_03",
        "file": REVIEW_DIR / "cut_03_supercar_traffic_weave_1440p60.mp4",
        "thumb": THUMB_DIR / "thumb_cut_03_approved.jpg",
        "title": "INSANE GTA 6 Traffic Weave Causes Massive Pileup 💀🚗 #Shorts",
        "description": "Precision high-speed slalom through midday traffic!\nPolice try to follow and trigger a 10-car pileup.\n\n#GTA6 #Shorts #Gaming #TrafficWeave #ViceCity",
        "tags": ["gta 6", "gta 6 traffic weave", "shorts", "gaming"],
    },
    {
        "id": "cut_04",
        "file": REVIEW_DIR / "cut_04_tank_6star_rampage_1440p60.mp4",
        "thumb": THUMB_DIR / "thumb_cut_04_approved.jpg",
        "title": "Can a TANK Survive 6-Star Police in GTA 6? 💀🚀 #Shorts",
        "description": "Testing the military tank against 6-Star wanted level police in GTA 6!\nCrushing SWAT APCs and blowing helicopters.\n\n#GTA6 #Shorts #Gaming #TankRampage #GTA6Police",
        "tags": ["gta 6", "gta 6 tank", "6 star wanted", "shorts", "gaming"],
    },
    {
        "id": "cut_05",
        "file": REVIEW_DIR / "cut_05_caseoh_opencv_rage_2k.mp4",
        "thumb": THUMB_DIR / "thumb_cut_05_approved.jpg",
        "title": "CaseOh RAGES at GTA 6 Truck Physics 💀🚗 #Shorts",
        "description": "CaseOh tries driving a truck in GTA 6 and flips across the highway!\nReal-time facecam reaction and rage.\n\n#CaseOh #GTA6 #Shorts #Gaming #FunnyMoments",
        "tags": ["caseoh", "gta 6", "caseoh gta", "shorts", "gaming", "funny"],
    },
]

TARGET_HOUR = 13
TARGET_MINUTE = 30

def log(msg):
    print(msg, flush=True)

def run_scheduler():
    log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Scheduler started.")
    log(f"Target upload time: Today at {TARGET_HOUR:02d}:{TARGET_MINUTE:02d} IST (1:30 PM)")
    log(f"Total clips queued: {len(CLIPS_QUEUE)}")

    while True:
        now = datetime.now()
        # Check if we have reached or passed target time today
        target_time = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)
        
        remaining = (target_time - now).total_seconds()
        if remaining > 0:
            hrs = int(remaining // 3600)
            mins = int((remaining % 3600) // 60)
            secs = int(remaining % 60)
            log(f"[{now.strftime('%H:%M:%S')}] ⏳ Waiting for 1:30 PM reset window... ({hrs}h {mins}m {secs}s remaining)")
            sleep_time = min(300, max(5, remaining))
            time.sleep(sleep_time)
            continue

        log(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚀 1:30 PM REACHED! Starting YouTube API upload run...")
        token = get_oauth_token()
        if not token:
            print("❌ Failed to obtain OAuth token. Retrying in 60s...")
            time.sleep(60)
            continue

        thumb_gen = ThumbnailGenerator()
        uploaded_results = []
        quota_blocked = False

        for clip in CLIPS_QUEUE:
            if clip.get("published"):
                continue

            f_path = str(clip["file"])
            t_path = str(clip["thumb"])
            title = clip["title"]
            desc = clip["description"]
            tags = clip["tags"]

            print(f"\nUploading: {Path(f_path).name}")
            print(f"Title: {title}")

            try:
                vid_id = upload_short_public(f_path, title, desc, tags, token)
                short_url = f"https://www.youtube.com/shorts/{vid_id}"
                print(f"✅ Published: {short_url}")
                clip["published"] = True

                if os.path.exists(t_path):
                    ok = thumb_gen.upload_to_youtube(vid_id, t_path, token)
                    if ok:
                        print(f"🎯 Thumbnail applied to {vid_id}")

                uploaded_results.append({
                    "id": clip["id"],
                    "video_id": vid_id,
                    "url": short_url,
                    "title": title,
                    "published_at": datetime.now().isoformat()
                })
                time.sleep(3.0)

            except Exception as e:
                err_str = str(e)
                print(f"⚠️ Upload exception: {err_str}")
                if "uploadLimitExceeded" in err_str:
                    print("🛑 Quota limit still active on YouTube. Will retry in 10 minutes...")
                    quota_blocked = True
                    break
                else:
                    print(f"❌ Error for {clip['id']}: {e}")

        # Save record
        if uploaded_results:
            rec_file = BASE_DIR / "storage" / "scheduled_130_published_records.json"
            with open(rec_file, "w", encoding="utf-8") as f:
                json.dump(uploaded_results, f, indent=2)

        if all(c.get("published") for c in CLIPS_QUEUE):
            print("\n🎉 ALL QUEUED CLIPS SUCCESSFULLY UPLOADED!")
            break

        if quota_blocked:
            time.sleep(600)  # Wait 10 minutes and retry

if __name__ == "__main__":
    run_scheduler()
