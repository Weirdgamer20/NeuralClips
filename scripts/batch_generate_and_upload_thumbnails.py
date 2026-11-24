"""Batch High-CTR Thumbnail Generator and YouTube Uploader.

Generates and applies high-converting viral thumbnails for top live GTA 6 Shorts:
1. High-saturation, S-curve gameplay action background
2. Streamer facecam badge with glowing neon border
3. Bold, punchy 2-4 word hook text with thick drop shadow
4. Visual curiosity indicators: glowing target circle + directional arrow
5. Real-time upload to YouTube Data API v3 (thumbnails.set)
"""

import os
import sys
import json
import time
from pathlib import Path

BASE_DIR = Path("d:/vidclip")
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from sources.youtube_source import get_oauth_token
from rendering.thumbnail_generator import ThumbnailGenerator

STORAGE_DIR = BASE_DIR / "storage"
THUMBNAILS_DIR = STORAGE_DIR / "thumbnails"
RAW_DIR = STORAGE_DIR / "raw_streamer_chunks"
MANIFEST_PATH = STORAGE_DIR / "famous_streamers_manifest.json"

STREAMER_DEFAULT_RAW = {
    "IShowSpeed": "raw_ishowspeed.mp4",
    "Kai Cenat": "raw_kai_cenat.mp4",
    "Typical Gamer": "raw_typical_gamer.mp4",
    "CaseOh": "raw_caseoh.mp4",
    "xQc": "raw_xqc.mp4",
}

# High-CTR hooks tailored for top live videos
CUSTOM_HOOKS = {
    "ZyZwgMLRrKA": ("IMPOSSIBLE ESCAPE?! 🚨", (860, 360)),
    "rrt64eu1m_I": ("SECRET SUPERCAR?! 🏎️💨", (820, 380)),
    "xlv7U2-OPLo": ("250 MPH HIGHWAY CRASH 💀", (850, 350)),
    "r7kbKWkfWPA": ("THROUGH THE WINDSHIELD! 😂", (840, 370)),
    "3DpGGtfEHF4": ("VICE CITY GRAPHICS! 🌴🔥", (880, 340)),
    "wyfLBHQWGk0": ("5-STAR POLICE BUST 🚨", (850, 360)),
    "ws96x0om7BE": ("HE ALMOST DIED! 😱", (860, 380)),
    "rMSxklEL-OM": ("5-STAR COP CHASE 🔥", (830, 350)),
    "q4NlSmY94w8": ("MISSION FAILED BRO 💀", (850, 360)),
    "VF76TH7pwww": ("WORST CRASH EVER! 🚙💥", (840, 370)),
}


def main():
    print("=" * 75)
    print("🔥 BATCH HIGH-CTR THUMBNAIL GENERATOR & YOUTUBE UPLOADER")
    print("=" * 75)

    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    token = get_oauth_token()
    if not token:
        print("❌ Could not obtain YouTube OAuth token.")
        return

    print("✅ Authorized with YouTube Data API v3.")

    gen = ThumbnailGenerator()

    # Load manifest to get all live/scheduled videos
    if not MANIFEST_PATH.exists():
        print("❌ Manifest not found.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Flatten videos
    all_videos = []
    for b in manifest.get("batches", []):
        for v in b.get("videos", []):
            y_url = v.get("youtube_url", "")
            if y_url:
                vid_id = y_url.split("/")[-1].split("?")[0]
                v["video_id"] = vid_id
                all_videos.append(v)

    print(f"📊 Loaded {len(all_videos)} total published/scheduled videos from manifest.")

    # Target the top 15 priority live videos first
    priority_ids = list(CUSTOM_HOOKS.keys())
    target_videos = [v for v in all_videos if v["video_id"] in priority_ids]

    # Add next 15 live videos to make 25-30 total
    for v in all_videos:
        if v not in target_videos and len(target_videos) < 25:
            target_videos.append(v)

    print(f"🎯 Processing {len(target_videos)} priority video thumbnails...\n")

    success_count = 0

    for idx, v in enumerate(target_videos, 1):
        vid_id = v["video_id"]
        streamer = v.get("streamer", "Gaming")
        title = v.get("title", "")
        
        hook_info = CUSTOM_HOOKS.get(vid_id)
        hook_text = hook_info[0] if hook_info else None
        target_circle = hook_info[1] if hook_info else None

        # Find best video chunk for this streamer
        raw_name = STREAMER_DEFAULT_RAW.get(streamer, "raw_xqc.mp4")
        video_path = RAW_DIR / raw_name

        if not video_path.exists():
            # Find any raw chunk for this streamer
            candidates = list(RAW_DIR.glob(f"*{streamer.lower().replace(' ', '_')}*.mp4"))
            video_path = candidates[0] if candidates else (RAW_DIR / "raw_xqc.mp4")

        thumb_output = THUMBNAILS_DIR / f"thumb_{streamer.lower().replace(' ', '_')}_{vid_id}.jpg"

        print(f"[{idx:02d}/{len(target_videos)}] Video: {vid_id} | Streamer: {streamer}")
        print(f"       Title: {title[:50]}")
        print(f"       Hook:  {hook_text or 'Auto-derived'}")

        # 1. Generate Thumbnail
        try:
            gen.create_thumbnail(
                video_path=str(video_path),
                streamer_name=streamer,
                title=title,
                output_path=str(thumb_output),
                hook_text=hook_text,
                target_circle=target_circle,
                draw_arrow=True
            )
            print(f"       ✅ Thumbnail created: {thumb_output.name} ({thumb_output.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"       ❌ Error creating thumbnail: {e}")
            continue

        # 2. Upload to YouTube
        try:
            ok = gen.upload_to_youtube(vid_id, str(thumb_output), token)
            if ok:
                print(f"       🚀 UPLOADED TO YOUTUBE: 200 OK (https://www.youtube.com/shorts/{vid_id})")
                success_count += 1
            else:
                print(f"       ⚠️ Upload returned False")
        except Exception as e:
            print(f"       ❌ Upload failed: {e}")

        # Rate limit spacing
        time.sleep(1.0)
        print("-" * 65)

    print("\n" + "=" * 75)
    print(f"🎉 COMPLETED: Successfully generated and uploaded {success_count}/{len(target_videos)} high-CTR thumbnails!")
    print("=" * 75)


if __name__ == "__main__":
    main()
