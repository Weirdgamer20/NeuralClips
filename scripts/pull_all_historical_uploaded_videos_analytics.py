"""Fetches real-time analytics for EVERY video uploaded to the channel.
Paginates through the entire channel uploads playlist via YouTube Data API v3.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from sources.youtube_source import get_oauth_token

IST = timezone(timedelta(hours=5, minutes=30))

def api_get(url: str, token: str):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    print("=" * 80)
    print("PULLING ANALYTICS FOR ALL VIDEOS UPLOADED TO THE CHANNEL")
    print("=" * 80)

    token = get_oauth_token()
    if not token:
        print("Error: Could not retrieve OAuth token!")
        return

    # 1. Channel Details & Uploads Playlist
    ch_url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails,statistics&mine=true"
    ch_data = api_get(ch_url, token)
    items = ch_data.get("items", [])
    if not items:
        print("Error: No channel found!")
        return

    ch = items[0]
    title = ch["snippet"]["title"]
    stats = ch.get("statistics", {})
    uploads_id = ch["contentDetails"]["relatedPlaylists"]["uploads"]

    print(f"Channel: {title}")
    print(f"Subscribers: {stats.get('subscriberCount', '0')}")
    print(f"Total Lifetime Views: {stats.get('viewCount', '0')}")
    print(f"Total Video Count: {stats.get('videoCount', '0')}")
    print(f"Uploads Playlist ID: {uploads_id}")
    print("-" * 80)

    # 2. Paginate through all videos in uploads playlist
    video_records = []
    next_page_token = None
    page = 1

    print("Fetching all uploaded video items...")
    while True:
        pl_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails,snippet&playlistId={uploads_id}&maxResults=50"
        if next_page_token:
            pl_url += f"&pageToken={next_page_token}"

        try:
            pl_data = api_get(pl_url, token)
        except Exception as e:
            print(f"Error fetching playlist page {page}: {e}")
            break

        pl_items = pl_data.get("items", [])
        if not pl_items:
            break

        for item in pl_items:
            vid = item["contentDetails"]["videoId"]
            snip = item.get("snippet", {})
            video_records.append({
                "video_id": vid,
                "title": snip.get("title", ""),
                "published_at": snip.get("publishedAt", "")
            })

        print(f"  Page {page}: retrieved {len(pl_items)} videos (total so far: {len(video_records)})")
        next_page_token = pl_data.get("nextPageToken")
        if not next_page_token:
            break
        page += 1

    print(f"\nTotal video IDs retrieved from uploads playlist: {len(video_records)}")
    print("-" * 80)

    # 3. Query video statistics in batches of 50
    detailed_videos = []
    for i in range(0, len(video_records), 50):
        batch = video_records[i:i+50]
        vids_str = ",".join(v["video_id"] for v in batch)
        v_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,status,contentDetails&id={vids_str}"
        try:
            v_data = api_get(v_url, token)
        except Exception as e:
            print(f"Error fetching stats for batch {i//50 + 1}: {e}")
            continue

        for v in v_data.get("items", []):
            vid_id = v["id"]
            snip = v.get("snippet", {})
            st = v.get("statistics", {})
            stat = v.get("status", {})

            pub_raw = snip.get("publishedAt", "")
            pub_ist = ""
            if pub_raw:
                try:
                    dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00")).astimezone(IST)
                    pub_ist = dt.strftime("%Y-%m-%d %H:%M:%S IST")
                except Exception:
                    pub_ist = pub_raw

            views = int(st.get("viewCount", 0))
            likes = int(st.get("likeCount", 0))
            comments = int(st.get("commentCount", 0))
            privacy = stat.get("privacyStatus", "unknown")
            likes_visible = stat.get("publicStatsViewable", True)

            detailed_videos.append({
                "video_id": vid_id,
                "title": snip.get("title", ""),
                "published_at_utc": pub_raw,
                "published_at_ist": pub_ist,
                "views": views,
                "likes": likes,
                "comments": comments,
                "privacy": privacy,
                "likes_visible": likes_visible,
                "url": f"https://www.youtube.com/shorts/{vid_id}"
            })

    # Sort all videos by views descending
    detailed_videos.sort(key=lambda x: (x["views"], x["likes"]), reverse=True)

    total_pipeline_views = sum(v["views"] for v in detailed_videos)
    total_pipeline_likes = sum(v["likes"] for v in detailed_videos)
    total_pipeline_comments = sum(v["comments"] for v in detailed_videos)

    print("\n" + "=" * 80)
    print("HISTORICAL PERFORMANCE SUMMARY ACROSS ALL UPLOADED VIDEOS")
    print("=" * 80)
    print(f"Total Videos Tracked:   {len(detailed_videos)}")
    print(f"Total Views:            {total_pipeline_views:,}")
    print(f"Total Likes:            {total_pipeline_likes:,}")
    print(f"Total Comments:         {total_pipeline_comments:,}")
    print("=" * 80)

    # Print top 40 videos
    print("\nTOP 40 PERFORMING VIDEOS OVERALL:")
    print(f"{'#':<3} | {'Views':<7} | {'Likes':<5} | {'Date (IST)':<19} | {'Title':<45} | {'URL'}")
    print("-" * 125)
    for idx, v in enumerate(detailed_videos[:40], 1):
        t = (v['title'][:42] + '...') if len(v['title']) > 45 else v['title']
        d = v['published_at_ist'][:19]
        print(f"{idx:<3} | {v['views']:<7} | {v['likes']:<5} | {d:<19} | {t:<45} | {v['url']}")

    # Save to JSON
    out_json = BASE_DIR / "storage" / "all_historical_videos_analytics.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "extracted_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST"),
            "channel": {
                "title": title,
                "subscribers": int(stats.get("subscriberCount", 0)),
                "total_views": int(stats.get("viewCount", 0)),
                "total_videos": int(stats.get("videoCount", 0)),
            },
            "summary": {
                "total_videos": len(detailed_videos),
                "total_views": total_pipeline_views,
                "total_likes": total_pipeline_likes,
                "total_comments": total_pipeline_comments,
            },
            "videos": detailed_videos
        }, f, indent=2)

    print(f"\nFull dataset saved to: {out_json}")

if __name__ == "__main__":
    main()
