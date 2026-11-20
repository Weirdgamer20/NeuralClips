"""Scrapes the Top 300 GTA 6 Shorts by views from YouTube hashtag and search feeds,
extracting real metadata, upload dates, comments, and audio details.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

OUTPUT_FILE = r"d:\vidclip\storage\scraped_top300_gta6_shorts.json"

FEEDS = [
    "https://www.youtube.com/hashtag/gta6/shorts",
    "https://www.youtube.com/hashtag/gta/shorts",
    "https://www.youtube.com/hashtag/gtashorts/shorts",
    "https://www.youtube.com/hashtag/gta5/shorts",
    "https://www.youtube.com/hashtag/gtav/shorts",
]


def harvest_shorts(target_count: int = 300) -> List[Dict[str, Any]]:
    print(f"Starting harvest of top {target_count} GTA Shorts across feeds...")
    collected: Dict[str, Dict[str, Any]] = {}

    for feed_url in FEEDS:
        if len(collected) >= target_count:
            break
        print(f"Querying feed: {feed_url} ...")
        cmd = [
            sys.executable, "-m", "yt_dlp",
            feed_url,
            "--dump-json",
            "--no-warnings",
            "--flat-playlist",
            "--playlist-end", "100"
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=45)
            for line in res.stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                    vid_id = d.get("id")
                    if vid_id and vid_id not in collected:
                        views = d.get("view_count") or 0
                        collected[vid_id] = {
                            "id": vid_id,
                            "url": f"https://www.youtube.com/shorts/{vid_id}",
                            "title": d.get("title", ""),
                            "view_count": views,
                            "uploader": d.get("uploader", "Unknown"),
                            "uploader_id": d.get("uploader_id", ""),
                            "duration": d.get("duration"),
                            "feed_source": feed_url
                        }
                        if len(collected) >= target_count:
                            break
                except Exception:
                    continue
            print(f"  Total unique collected so far: {len(collected)}")
        except Exception as e:
            print(f"  Feed query error: {e}")

    shorts_list = list(collected.values())
    # Sort strictly by view count descending
    shorts_list.sort(key=lambda x: x.get("view_count") or 0, reverse=True)
    return shorts_list[:target_count]


def enrich_top_videos_with_details(top_videos: List[Dict[str, Any]], count_to_enrich: int = 8) -> None:
    """Enriches the top viral videos with full comments, tags, and music."""
    print(f"\nFetching deep details and top comments for top {count_to_enrich} viral videos...")
    for i, v in enumerate(top_videos[:count_to_enrich], start=1):
        vid_id = v["id"]
        url = v["url"]
        print(f"[{i}/{count_to_enrich}] Inspecting: {v['title'][:45]}... ({v['view_count']:,} views)")

        cmd = [
            sys.executable, "-m", "yt_dlp",
            url,
            "--dump-json",
            "--no-warnings",
            "--write-comments",
            "--extractor-args", "youtube:max_comments=10"
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=25)
            if res.stdout.strip():
                full_info = json.loads(res.stdout)
                v["upload_date"] = full_info.get("upload_date")
                v["timestamp"] = full_info.get("timestamp")
                v["tags"] = full_info.get("tags", [])
                v["like_count"] = full_info.get("like_count")
                v["channel_follower_count"] = full_info.get("channel_follower_count")
                v["track"] = full_info.get("track")
                v["artist"] = full_info.get("artist")

                # Extract comments
                raw_comments = full_info.get("comments") or []
                v["top_comments"] = [
                    {
                        "author": c.get("author", "User"),
                        "text": c.get("text", "")[:140],
                        "like_count": c.get("like_count", 0)
                    }
                    for c in raw_comments[:5]
                ]
        except Exception as e:
            print(f"  Enrich error for {vid_id}: {e}")


def main():
    shorts = harvest_shorts(target_count=300)
    print(f"\nHarvested {len(shorts)} top GTA Shorts.")

    # Enrich top 8 with deep metadata and real viewer comments
    enrich_top_videos_with_details(shorts, count_to_enrich=8)

    # Statistical Breakdown
    views = [s.get("view_count") or 0 for s in shorts]
    over_1m = sum(1 for v in views if v >= 1_000_000)
    over_10m = sum(1 for v in views if v >= 10_000_000)
    avg_views = sum(views) // len(views) if views else 0

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_scraped": len(shorts),
        "shorts_over_1m_views": over_1m,
        "shorts_over_10m_views": over_10m,
        "average_views": avg_views,
        "highest_views": max(views) if views else 0,
        "top_viral_shorts": shorts[:15],
        "all_shorts_summary": [
            {
                "id": s["id"],
                "title": s["title"],
                "view_count": s["view_count"],
                "url": s["url"]
            }
            for s in shorts
        ]
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nSaved complete report to {OUTPUT_FILE}")
    print(f"Clips >= 1M views: {over_1m}/{len(shorts)}")
    print(f"Clips >= 10M views: {over_10m}/{len(shorts)}")
    print(f"Average views: {avg_views:,}")


if __name__ == "__main__":
    main()
