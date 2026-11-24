"""Automated Scheduled Publisher for Clip 4.

File: C:\\Users\\thega\\Desktop\\neuralclips_gta6_clip_04.mp4
Scheduled Public Release Time: 2026-11-21 at 2:00 PM IST
Target Platform: YouTube Shorts (Public)
"""

import os
import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from publishing.youtube_publisher import YouTubePublisher
from core.state_store import StateStore

DESKTOP_CLIP_4 = Path(r"C:\Users\thega\Desktop\neuralclips_gta6_clip_04.mp4")
LOG_FILE = BASE_DIR / "storage" / "clip4_upload.log"


def log(msg: str):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S IST]")
    line = f"{timestamp} {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def main():
    log("==================================================================")
    log("NEURALCLIPS: SCHEDULED YOUTUBE SHORT UPLOADER EXECUTING")
    log(f"Target Video: {DESKTOP_CLIP_4}")
    log("Release Mode: PUBLIC (Peak Afternoon Engagement Slot)")
    log("==================================================================")

    if not DESKTOP_CLIP_4.exists():
        log(f"ERROR: Video file not found at {DESKTOP_CLIP_4}")
        # Try fallback in storage/clips
        fallback = BASE_DIR / "storage" / "clips" / "clip_hl_neuralclips_gta6_clip_04_1795188548.mp4"
        if fallback.exists():
            import shutil
            shutil.copy2(fallback, DESKTOP_CLIP_4)
            log(f"Restored video from internal storage cache to {DESKTOP_CLIP_4}")
        else:
            log("FATAL: Cannot locate Clip 4 video asset.")
            sys.exit(1)

    store = StateStore()
    publisher = YouTubePublisher(state_store=store)

    with store._get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM youtube_publications WHERE clip_id LIKE '%clip_04%' ORDER BY created_at DESC LIMIT 1"
        ).fetchone()

    pub_id = row["pub_id"] if row else f"pub_clip4_{int(time.time())}"
    clip_id = row["clip_id"] if row else "clip_neuralclips_gta6_clip_04"
    title = "IShowSpeed x GTA 6 OFFICIAL MOMENT 💀 #Shorts"
    description = (
        "IShowSpeed experiences the insanity of GTA 6 Vice City!\n\n"
        "Rendered in 2K Vertical Split-Screen with NeuralClips AI Video Director.\n\n"
        "#GTA6 #IShowSpeed #Shorts #Gaming #GTA6Gameplay #ViceCity"
    )
    hashtags = "#GTA6 #IShowSpeed #Shorts #Gaming #GTA6Gameplay"

    pub_record = {
        "pub_id": pub_id,
        "clip_id": clip_id,
        "file_path": str(DESKTOP_CLIP_4),
        "title": title,
        "description": description,
        "hashtags": hashtags,
    }

    max_retries = 3
    retry_delay_sec = 60

    for attempt in range(1, max_retries + 1):
        log(f"\n[Attempt {attempt}/{max_retries}] Uploading to YouTube as Public Short...")
        success, msg, yt_url = publisher.publish_short(
            pub_record=pub_record,
            mock_mode=False,
            publish_at=None,  # Direct public release at scheduled execution time
        )

        if success:
            log("=" * 65)
            log("YOUTUBE PUBLICATION SUCCESSFUL!")
            log(f"Short URL:       {yt_url}")
            log(f"Status:          PUBLIC")
            log(f"Uploaded File:   {DESKTOP_CLIP_4.name} ({DESKTOP_CLIP_4.stat().st_size / (1024*1024):.2f} MB)")
            log("=" * 65)
            return
        else:
            log(f"Upload attempt {attempt} failed: {msg}")
            if "uploadLimitExceeded" in str(msg) or "429" in str(msg):
                log(f"Quota window still clearing. Waiting {retry_delay_sec}s before next attempt...")
                time.sleep(retry_delay_sec)
            else:
                log("Non-quota error encountered.")
                time.sleep(10)

    log("ERROR: All upload attempts failed. Please verify YouTube quota window.")
    sys.exit(1)


if __name__ == "__main__":
    main()
