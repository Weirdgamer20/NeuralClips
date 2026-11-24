"""Direct Fast Downloader for Top 100 Pure GTA 6 Clips (>1M Views).

Uses pre-indexed verified GTA 6 dataset from storage/scraped_top300_gta6_shorts.json
to download directly to storage/viral_100_clips/ without search delays.
"""

import json
import os
import subprocess
import sys
import time

DATASET = str(BASE_DIR / "storage" / "scraped_top300_gta6_shorts.json")
OUT_DIR = str(BASE_DIR / "storage" / "viral_100_clips")
MANIFEST = os.path.join(OUT_DIR, "manifest.json")
FFMPEG_DIR = str(BASE_DIR / ".venv\Scripts")

BANNED = [
    "hulk", "spiderman", "spider-man", "potty", "kiss or save", "kiss run",
    "dog teach", "gulli bulli", "cartoon", "bhoot", "poop", "superman", "ironman"
]
REQUIRED = [
    "gta 6", "gta vi", "grand theft auto vi", "grand theft auto 6",
    "lucia", "jason", "vice city", "gta"
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(DATASET, "r", encoding="utf-8") as f:
        data = json.load(f)

    over_1m = [s for s in data.get("all_shorts_summary", []) if (s.get("view_count") or 0) >= 1_000_000]

    pure = []
    for s in over_1m:
        t = s.get("title", "").lower()
        if any(req in t for req in REQUIRED) and not any(ban in t for ban in BANNED):
            pure.append(s)

    pure.sort(key=lambda x: x.get("view_count") or 0, reverse=True)
    target_clips = pure[:100]

    print(f"Total qualified pure GTA 6 clips (>1M views): {len(pure)}", flush=True)
    print(f"Starting batch download of top {len(target_clips)} clips...", flush=True)

    downloaded = []
    success = 0
    fail = 0

    for idx, c in enumerate(target_clips, start=1):
        vid_id = c["id"]
        title = c.get("title", "")
        views = c.get("view_count", 0)
        url = c.get("url", f"https://www.youtube.com/shorts/{vid_id}")
        out_mp4 = os.path.join(OUT_DIR, f"{vid_id}.mp4")

        # Skip if already downloaded
        if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 100000:
            sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
            print(f"[{idx:03d}/{len(target_clips)}] [CACHED] {views:,} views | {vid_id}.mp4 ({sz_mb:.1f}MB) | {title[:35]}", flush=True)
            downloaded.append({
                "index": idx,
                "id": vid_id,
                "title": title,
                "view_count": views,
                "file_path": out_mp4,
                "file_size_bytes": os.path.getsize(out_mp4),
                "url": url
            })
            success += 1
            continue

        print(f"[{idx:03d}/{len(target_clips)}] DOWNLOADING: {views:,} views | {title[:40]}...", flush=True)

        cmd = [
            sys.executable, "-m", "yt_dlp",
            url,
            "--ffmpeg-location", FFMPEG_DIR,
            "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "-o", out_mp4,
            "--merge-output-format", "mp4",
            "--no-warnings",
            "--socket-timeout", "25"
        ]

        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=45)
            if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 100000:
                sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
                print(f"       -> SUCCESS: {vid_id}.mp4 ({sz_mb:.2f}MB)", flush=True)
                downloaded.append({
                    "index": idx,
                    "id": vid_id,
                    "title": title,
                    "view_count": views,
                    "file_path": out_mp4,
                    "file_size_bytes": os.path.getsize(out_mp4),
                    "url": url
                })
                success += 1
            else:
                err = res.stderr.strip()[:80] if res.stderr else "Unknown error"
                print(f"       -> FAILED: {err}", flush=True)
                fail += 1
        except Exception as e:
            print(f"       -> ERROR: {e}", flush=True)
            fail += 1

        time.sleep(0.3)

        if idx % 5 == 0:
            with open(MANIFEST, "w", encoding="utf-8") as mf:
                json.dump({
                    "total_requested": len(target_clips),
                    "downloaded_so_far": success,
                    "clips": downloaded
                }, mf, indent=2)

    with open(MANIFEST, "w", encoding="utf-8") as mf:
        json.dump({
            "total_requested": len(target_clips),
            "total_downloaded": success,
            "total_failed": fail,
            "clips": downloaded
        }, mf, indent=2)

    total_mb = sum(c["file_size_bytes"] for c in downloaded) / (1024 * 1024)
    print("=" * 65, flush=True)
    print(f"DOWNLOAD FINISHED: {success}/{len(target_clips)} clips ({total_mb:.1f}MB)", flush=True)
    print(f"Manifest saved to: {MANIFEST}", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    main()
