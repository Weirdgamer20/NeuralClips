"""Batch Downloader for Top 100 Viral GTA Shorts (>1,000,000 Views).

Downloads the top 100 viral video files to storage/viral_100_clips/ for real
pattern training and feature extraction.
"""

import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, List

DATASET_FILE = r"d:\vidclip\storage\scraped_top300_gta6_shorts.json"
OUTPUT_DIR = r"d:\vidclip\storage\viral_100_clips"
MANIFEST_FILE = os.path.join(OUTPUT_DIR, "manifest.json")
FFMPEG_DIR = r"d:\vidclip\.venv\Scripts"


def download_100_viral_clips(max_clips: int = 100):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(DATASET_FILE):
        print(f"Error: dataset file not found: {DATASET_FILE}")
        return

    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter for videos with at least 1,000,000 views
    viral_candidates = [
        s for s in data.get("all_shorts_summary", [])
        if (s.get("view_count") or 0) >= 1_000_000
    ]
    # Sort strictly descending by views
    viral_candidates.sort(key=lambda x: x.get("view_count") or 0, reverse=True)
    target_clips = viral_candidates[:max_clips]

    print("=" * 65)
    print(f"STARTING BATCH DOWNLOAD: TOP {len(target_clips)} VIRAL CLIPS (>1M VIEWS)")
    print(f"Target Directory: {OUTPUT_DIR}")
    print("=" * 65)

    downloaded_records: List[Dict[str, Any]] = []
    success_count = 0
    fail_count = 0

    for i, clip in enumerate(target_clips, start=1):
        vid_id = clip["id"]
        title = clip.get("title", "")
        views = clip.get("view_count", 0)
        url = clip.get("url", f"https://www.youtube.com/shorts/{vid_id}")
        target_mp4 = os.path.join(OUTPUT_DIR, f"{vid_id}.mp4")

        # Skip if already downloaded
        if os.path.exists(target_mp4) and os.path.getsize(target_mp4) > 100000:
            sz_mb = os.path.getsize(target_mp4) / (1024 * 1024)
            print(f"[{i:03d}/{len(target_clips)}] (ALREADY CACHED) {views:,} views | {vid_id}.mp4 ({sz_mb:.1f} MB) | {title[:35]}...")
            downloaded_records.append({
                "index": i,
                "id": vid_id,
                "file_path": target_mp4,
                "file_size_bytes": os.path.getsize(target_mp4),
                "view_count": views,
                "title": title,
                "url": url
            })
            success_count += 1
            continue

        print(f"[{i:03d}/{len(target_clips)}] DOWNLOADING: {views:,} views | {title[:35]}... ({url})")

        cmd = [
            sys.executable, "-m", "yt_dlp",
            url,
            "--ffmpeg-location", FFMPEG_DIR,
            "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "-o", target_mp4,
            "--merge-output-format", "mp4",
            "--no-warnings",
            "--socket-timeout", "20"
        ]

        try:
            p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=45)
            if os.path.exists(target_mp4) and os.path.getsize(target_mp4) > 100000:
                sz_mb = os.path.getsize(target_mp4) / (1024 * 1024)
                print(f"       -> SUCCESS: {vid_id}.mp4 ({sz_mb:.2f} MB)")
                downloaded_records.append({
                    "index": i,
                    "id": vid_id,
                    "file_path": target_mp4,
                    "file_size_bytes": os.path.getsize(target_mp4),
                    "view_count": views,
                    "title": title,
                    "url": url
                })
                success_count += 1
            else:
                err_msg = p.stderr.strip()[:100] if p.stderr else "Unknown error"
                print(f"       -> FAILED: {err_msg}")
                fail_count += 1
        except subprocess.TimeoutExpired:
            print(f"       -> TIMEOUT (skipped): {vid_id}")
            fail_count += 1
        except Exception as e:
            print(f"       -> EXCEPTION: {e}")
            fail_count += 1

        # Small pause between downloads to prevent YouTube IP throttling
        time.sleep(0.5)

        # Write intermediate manifest every 10 downloads
        if i % 10 == 0:
            with open(MANIFEST_FILE, "w", encoding="utf-8") as mf:
                json.dump({
                    "total_requested": len(target_clips),
                    "downloaded_so_far": success_count,
                    "clips": downloaded_records
                }, mf, indent=2)

    # Final manifest
    manifest_data = {
        "total_requested": len(target_clips),
        "total_downloaded": success_count,
        "total_failed": fail_count,
        "target_directory": OUTPUT_DIR,
        "clips": downloaded_records
    }
    with open(MANIFEST_FILE, "w", encoding="utf-8") as mf:
        json.dump(manifest_data, mf, indent=2)

    total_mb = sum(c["file_size_bytes"] for c in downloaded_records) / (1024 * 1024)
    print("=" * 65)
    print(f"DOWNLOAD COMPLETE: {success_count}/{len(target_clips)} clips downloaded ({total_mb:.1f} MB total).")
    print(f"Manifest written to: {MANIFEST_FILE}")
    print("=" * 65)


if __name__ == "__main__":
    download_100_viral_clips(max_clips=100)
