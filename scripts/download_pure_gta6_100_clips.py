"""Strict GTA 6 Viral Clip Harvester & Downloader.

Downloads the top 100 strictly verified GTA 6 clips and Shorts by view count,
eliminating all non-GTA 6, mod, cartoon, and unrelated content.
"""

import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Set

OUTPUT_DIR = str(BASE_DIR / "storage" / "viral_100_clips")
MANIFEST_FILE = os.path.join(OUTPUT_DIR, "manifest.json")
FFMPEG_DIR = str(BASE_DIR / ".venv\Scripts")

SEARCH_QUERIES = [
    "https://www.youtube.com/hashtag/gta6/shorts",
    "https://www.youtube.com/hashtag/gtavi/shorts",
    "https://www.youtube.com/hashtag/grandtheftautovi/shorts",
    "ytsearch100:GTA 6 gameplay shorts",
    "ytsearch100:GTA 6 graphics shorts",
    "ytsearch100:GTA VI official shorts",
    "ytsearch100:GTA 6 details shorts",
    "ytsearch100:GTA 6 vice city shorts",
    "ytsearch100:GTA 6 police chase shorts",
    "ytsearch100:Grand Theft Auto VI shorts"
]

BANNED_KEYWORDS = [
    "hulk", "spiderman", "potty", "kiss or save", "kiss run",
    "dog teach", "gulli bulli", "cartoon", "bhoot", "choot",
    "spider-man", "superman", "ironman", "minecraft", "free fire",
    "skibidi", "toilet", "poop"
]

REQUIRED_KEYWORDS = [
    "gta 6", "gta vi", "grand theft auto vi", "grand theft auto 6",
    "lucia", "jason", "vice city 6"
]


def is_pure_gta6(title: str, duration: int, views: int) -> bool:
    t = title.lower()
    # Strictly Option B: must have at least 1,000,000 views
    if views < 1_000_000:
        return False
    # Must have at least one GTA 6 keyword
    if not any(req in t for req in REQUIRED_KEYWORDS):
        return False
    # Must not have banned spam keywords
    if any(ban in t for ban in BANNED_KEYWORDS):
        return False
    # Must be short format (under 90 seconds, ideally under 60)
    if duration > 90:
        return False
    return True


def collect_top_gta6_candidates(target_count: int = 100) -> List[Dict[str, Any]]:
    print(f"Collecting strictly verified GTA 6 candidates across {len(SEARCH_QUERIES)} search feeds...")
    candidates: Dict[str, Dict[str, Any]] = {}

    for q in SEARCH_QUERIES:
        print(f"  Searching: '{q}' ...")
        cmd = [
            sys.executable, "-m", "yt_dlp",
            q,
            "--dump-json",
            "--no-warnings",
            "--flat-playlist"
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=35)
            for line in res.stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                    vid_id = d.get("id")
                    title = d.get("title", "")
                    views = d.get("view_count") or 0
                    dur = d.get("duration") or 0

                    if vid_id and is_pure_gta6(title, dur, views):
                        if vid_id not in candidates or views > candidates[vid_id]["view_count"]:
                            candidates[vid_id] = {
                                "id": vid_id,
                                "url": f"https://www.youtube.com/shorts/{vid_id}",
                                "title": title,
                                "view_count": views,
                                "duration": dur,
                                "uploader": d.get("uploader", "Unknown")
                            }
                except Exception:
                    continue
            print(f"    Total pure GTA 6 clips found so far: {len(candidates)}")
        except Exception as e:
            print(f"    Search error: {e}")

    ranked = list(candidates.values())
    ranked.sort(key=lambda x: x.get("view_count") or 0, reverse=True)
    return ranked[:target_count]


def download_pure_clips(clips: List[Dict[str, Any]]):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 65)
    print(f"DOWNLOADING {len(clips)} PURE GTA 6 CLIPS TO: {OUTPUT_DIR}")
    print("=" * 65)

    downloaded = []
    success_count = 0
    fail_count = 0

    for idx, c in enumerate(clips, start=1):
        vid_id = c["id"]
        title = c["title"]
        views = c["view_count"]
        url = c["url"]
        out_mp4 = os.path.join(OUTPUT_DIR, f"{vid_id}.mp4")

        # Skip if already exists
        if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 100000:
            sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
            print(f"[{idx:03d}/{len(clips)}] (CACHED) {views:,} views | {vid_id}.mp4 ({sz_mb:.1f} MB) | {title[:40]}")
            downloaded.append({
                "index": idx,
                "id": vid_id,
                "title": title,
                "view_count": views,
                "file_path": out_mp4,
                "file_size_bytes": os.path.getsize(out_mp4),
                "url": url
            })
            success_count += 1
            continue

        print(f"[{idx:03d}/{len(clips)}] DOWNLOADING: {views:,} views | {title[:45]}...")
        cmd = [
            sys.executable, "-m", "yt_dlp",
            url,
            "--ffmpeg-location", FFMPEG_DIR,
            "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "-o", out_mp4,
            "--merge-output-format", "mp4",
            "--no-warnings",
            "--socket-timeout", "20"
        ]

        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=40)
            if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 100000:
                sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
                print(f"       -> SUCCESS: {vid_id}.mp4 ({sz_mb:.2f} MB)")
                downloaded.append({
                    "index": idx,
                    "id": vid_id,
                    "title": title,
                    "view_count": views,
                    "file_path": out_mp4,
                    "file_size_bytes": os.path.getsize(out_mp4),
                    "url": url
                })
                success_count += 1
            else:
                print(f"       -> FAILED to merge/download: {vid_id}")
                fail_count += 1
        except Exception as e:
            print(f"       -> ERROR: {e}")
            fail_count += 1

        time.sleep(0.4)

        if idx % 10 == 0:
            with open(MANIFEST_FILE, "w", encoding="utf-8") as mf:
                json.dump({
                    "total_requested": len(clips),
                    "downloaded_so_far": success_count,
                    "clips": downloaded
                }, mf, indent=2)

    with open(MANIFEST_FILE, "w", encoding="utf-8") as mf:
        json.dump({
            "total_requested": len(clips),
            "total_downloaded": success_count,
            "total_failed": fail_count,
            "clips": downloaded
        }, mf, indent=2)

    print("=" * 65)
    print(f"FINISHED: {success_count}/{len(clips)} strictly verified GTA 6 clips downloaded.")
    print("=" * 65)


def main():
    clips = collect_top_gta6_candidates(target_count=100)
    print(f"\nCollected {len(clips)} strictly verified GTA 6 candidates.")
    if clips:
        download_pure_clips(clips)


if __name__ == "__main__":
    main()
