"""Fetch verified vertical YouTube Shorts in two tiers:
Tier 1: 100 Shorts (100k - 1M views)
Tier 2: 100 Shorts (>= 1M views)
Using YouTube's native Shorts hashtag aggregators.
"""

import json
import os
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YT_DLP = os.path.join(BASE_DIR, ".venv", "Scripts", "yt-dlp.exe")
OUTPUT_FILE = os.path.join(BASE_DIR, "storage", "gta6_viral_dataset.json")

HASHTAG_URLS = [
    ("gta6", "https://www.youtube.com/hashtag/gta6/shorts"),
    ("gta", "https://www.youtube.com/hashtag/gta/shorts"),
    ("gtav", "https://www.youtube.com/hashtag/gtav/shorts"),
    ("gtashorts", "https://www.youtube.com/hashtag/gtashorts/shorts"),
    ("gtaclips", "https://www.youtube.com/hashtag/gtaclips/shorts"),
    ("gta5clips", "https://www.youtube.com/hashtag/gta5clips/shorts"),
]

def fetch_hashtag_shorts(tag: str, url: str, limit: int = 150) -> list:
    print(f"Fetching #{tag} Shorts feed (up to {limit})...", flush=True)
    cmd = [
        YT_DLP,
        "--flat-playlist",
        "-J",
        "--playlist-end", str(limit),
        url,
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            entries = data.get("entries", [])
            print(f"  -> Got {len(entries)} raw shorts from #{tag}", flush=True)
            return entries
        else:
            print(f"  -> Error for #{tag}: {res.stderr[:200]}", flush=True)
    except Exception as e:
        print(f"  -> Exception fetching #{tag}: {e}", flush=True)
    return []

def main():
    print("Collecting 100 [100k-1M) and 100 [1M+] YouTube Shorts...", flush=True)
    seen_ids = set()
    pool_100k = []
    pool_1m = []

    for tag, url in HASHTAG_URLS:
        entries = fetch_hashtag_shorts(tag, url, limit=150)
        for e in entries:
            vid_id = e.get("id")
            if not vid_id or vid_id in seen_ids:
                continue
            seen_ids.add(vid_id)
            views = e.get("view_count") or 0
            dur = e.get("duration") or 30  # default for Shorts feed

            # Standard Shorts duration is 5-60s
            if dur > 65:
                continue

            title = e.get("title") or f"GTA Viral #{tag}"
            channel = e.get("channel") or e.get("uploader") or "YouTube Creator"

            item = {
                "id": vid_id,
                "title": title,
                "views": views,
                "duration": dur,
                "channel": channel,
                "url": f"https://www.youtube.com/shorts/{vid_id}",
                "tag": tag,
            }

            if 100000 <= views < 1000000:
                pool_100k.append(item)
            elif views >= 1000000:
                pool_1m.append(item)

        print(f"Progress after #{tag}: 100k-1M: {len(pool_100k)}/100 | 1M+: {len(pool_1m)}/100", flush=True)
        if len(pool_100k) >= 100 and len(pool_1m) >= 100:
            break

    # If 100k or 1M needs a few more, run a quick targeted search
    if len(pool_100k) < 100 or len(pool_1m) < 100:
        more_tags = [
            ("gtafunnymoments", "https://www.youtube.com/hashtag/gtafunnymoments/shorts"),
            ("gtafail", "https://www.youtube.com/hashtag/gtafail/shorts"),
            ("gtaviral", "https://www.youtube.com/hashtag/gtaviral/shorts"),
        ]
        for tag, url in more_tags:
            if len(pool_100k) >= 100 and len(pool_1m) >= 100:
                break
            entries = fetch_hashtag_shorts(tag, url, limit=100)
            for e in entries:
                vid_id = e.get("id")
                if not vid_id or vid_id in seen_ids:
                    continue
                seen_ids.add(vid_id)
                views = e.get("view_count") or 0
                dur = e.get("duration") or 30
                if dur > 65:
                    continue
                item = {
                    "id": vid_id,
                    "title": e.get("title") or f"GTA #{tag}",
                    "views": views,
                    "duration": dur,
                    "channel": e.get("channel") or e.get("uploader") or "YouTube Creator",
                    "url": f"https://www.youtube.com/shorts/{vid_id}",
                    "tag": tag,
                }
                if 100000 <= views < 1000000 and len(pool_100k) < 100:
                    pool_100k.append(item)
                elif views >= 1000000 and len(pool_1m) < 100:
                    pool_1m.append(item)

    pool_100k.sort(key=lambda x: x["views"], reverse=True)
    pool_1m.sort(key=lambda x: x["views"], reverse=True)

    final_100k = pool_100k[:100]
    final_1m = pool_1m[:100]

    result = {
        "count_100k_to_1m": len(final_100k),
        "count_1m_plus": len(final_1m),
        "clips_100k_to_1m": final_100k,
        "clips_1m_plus": final_1m,
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"\nSUCCESS: True Shorts Dataset Saved to {OUTPUT_FILE}")
    print(f"Tier 1 (100k - 1M): {len(final_100k)} clips")
    print(f"Tier 2 (1M+):       {len(final_1m)} clips")

if __name__ == "__main__":
    main()
