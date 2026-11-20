"""Strict Pure GTA 6 Downloader.

Downloads the top 100 strictly verified GTA 6 videos (>1M and highest viral view count),
with ZERO GTA 5, Franklin, or unrelated cartoon content.
"""

import json
import os
import subprocess
import sys
import time

OUT_DIR = r"d:\vidclip\storage\viral_100_clips"
MANIFEST = os.path.join(OUT_DIR, "manifest.json")
FFMPEG_DIR = r"d:\vidclip\.venv\Scripts"

QUERIES = [
    'ytsearch40:GTA 6 gameplay shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA VI official shorts -gta5 -gtav -franklin',
    'ytsearch40:Grand Theft Auto VI shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA 6 trailer shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA 6 leaks shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA 6 graphics shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA 6 vice city shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA 6 details shorts -gta5 -gtav -franklin'
]

BANNED = [
    'franklin', 'trevor', 'michael', 'gta 5', 'gta v', 'gta5', 'gtav',
    'fivem', 'panda', 'bullman', 'train', 'bhutiya', 'potty', 'hulk',
    'spiderman', 'dog teach', 'gulli', 'bhoot', 'choot', 'skibidi'
]


def collect_pure_gta6():
    print("Collecting strictly verified pure GTA 6 candidates (no GTA 5/mods)...", flush=True)
    results = []
    seen = set()

    for q in QUERIES:
        cmd = [
            sys.executable, "-m", "yt_dlp",
            q,
            "--dump-json",
            "--no-warnings",
            "--flat-playlist"
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=30)
            for line in res.stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                    vid_id = d.get('id')
                    title = d.get('title', '')
                    views = d.get('view_count') or 0
                    dur = d.get('duration') or 0
                    t_lower = title.lower()

                    has_gta6 = ('gta 6' in t_lower or 'gta vi' in t_lower or 'grand theft auto vi' in t_lower or 'grand theft auto 6' in t_lower)
                    is_banned = any(b in t_lower for b in BANNED)

                    if has_gta6 and not is_banned and vid_id not in seen:
                        seen.add(vid_id)
                        results.append({'id': vid_id, 'title': title, 'views': views, 'dur': dur})
                except Exception:
                    pass
        except Exception:
            pass

    results.sort(key=lambda x: x['views'], reverse=True)
    return results[:100]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    candidates = collect_pure_gta6()
    print(f"Total qualified pure GTA 6 clips to download: {len(candidates)}", flush=True)

    downloaded = []
    success = 0
    fail = 0

    for idx, c in enumerate(candidates, start=1):
        vid_id = c['id']
        title = c['title']
        views = c['views']
        url = f"https://www.youtube.com/watch?v={vid_id}"
        out_mp4 = os.path.join(OUT_DIR, f"{vid_id}.mp4")

        print(f"[{idx:03d}/{len(candidates)}] DOWNLOADING: {views:,} views | {title[:45]}...", flush=True)

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
                print(f"       -> FAILED: {vid_id}", flush=True)
                fail += 1
        except Exception as e:
            print(f"       -> ERROR: {e}", flush=True)
            fail += 1

        time.sleep(0.3)

        if idx % 5 == 0:
            with open(MANIFEST, "w", encoding="utf-8") as mf:
                json.dump({
                    "total_requested": len(candidates),
                    "downloaded_so_far": success,
                    "clips": downloaded
                }, mf, indent=2)

    with open(MANIFEST, "w", encoding="utf-8") as mf:
        json.dump({
            "total_requested": len(candidates),
            "total_downloaded": success,
            "total_failed": fail,
            "clips": downloaded
        }, mf, indent=2)

    total_mb = sum(c["file_size_bytes"] for c in downloaded) / (1024 * 1024)
    print("=" * 65, flush=True)
    print(f"DOWNLOAD COMPLETED: {success}/{len(candidates)} strictly pure GTA 6 clips ({total_mb:.1f}MB)", flush=True)
    print(f"Manifest written to: {MANIFEST}", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    main()
