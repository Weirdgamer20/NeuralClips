"""Fetch real-time analytics for all YouTube videos published from yesterday to tonight.

Uses direct OAuth2 Bearer token with urllib.request (no google-api-python-client dependency needed).
Queries YouTube Data API v3 channels, playlistItems, and videos endpoints.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_DIR = Path("d:/vidclip")
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from sources.youtube_source import get_oauth_token

STORAGE_DIR = BASE_DIR / "storage"
MANIFEST_PATH = STORAGE_DIR / "famous_streamers_manifest.json"
ANALYTICS_OUTPUT_JSON = STORAGE_DIR / "youtube_analytics_yesterday_to_tonight.json"

IST = timezone(timedelta(hours=5, minutes=30))


def api_get(url: str, token: str):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print("=" * 75)
    print("  NEURALCLIPS: YOUTUBE REAL-TIME ANALYTICS (YESTERDAY TO TONIGHT)")
    print("=" * 75)

    token = get_oauth_token()
    if not token:
        print("❌ Error: Could not obtain OAuth token from YouTube credentials.")
        return

    print("✅ OAuth token successfully generated.")

    # 1. Inspect authenticated channel
    ch_url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails,statistics&mine=true"
    try:
        ch_data = api_get(ch_url, token)
    except Exception as e:
        print(f"❌ Error fetching channel info: {e}")
        return

    items = ch_data.get("items", [])
    if not items:
        print("❌ No YouTube channel found for authenticated account.")
        return

    ch = items[0]
    ch_title = ch["snippet"]["title"]
    ch_stats = ch.get("statistics", {})
    uploads_id = ch["contentDetails"]["relatedPlaylists"]["uploads"]

    print(f"📺 Channel Name:          {ch_title}")
    print(f"👥 Channel Subscribers:   {ch_stats.get('subscriberCount', '0')}")
    print(f"👁️ Channel Total Views:   {ch_stats.get('viewCount', '0')}")
    print(f"🎬 Channel Video Count:   {ch_stats.get('videoCount', '0')}")
    print(f"📂 Uploads Playlist ID:   {uploads_id}")
    print("-" * 75)

    # 2. Collect video IDs from uploads playlist
    channel_video_ids = []
    next_page_token = None
    print("⏳ Fetching recent videos from channel upload playlist...")

    while True:
        pl_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails,snippet&playlistId={uploads_id}&maxResults=50"
        if next_page_token:
            pl_url += f"&pageToken={next_page_token}"

        try:
            pl_data = api_get(pl_url, token)
        except Exception as e:
            print(f"⚠️ Warning fetching playlist items: {e}")
            break

        for item in pl_data.get("items", []):
            vid_id = item["contentDetails"]["videoId"]
            pub_at = item["snippet"]["publishedAt"]
            channel_video_ids.append((vid_id, pub_at))

        next_page_token = pl_data.get("nextPageToken")
        if not next_page_token or len(channel_video_ids) >= 300:
            break

    print(f"✅ Found {len(channel_video_ids)} total videos in channel upload playlist.")

    # Also collect video IDs from famous_streamers_manifest.json
    manifest_vids = {}
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            for b in manifest.get("batches", []):
                for v in b.get("videos", []):
                    y_id = v.get("youtube_video_id")
                    if y_id and not y_id.startswith("mock_"):
                        manifest_vids[y_id] = {
                            "batch_number": b.get("batch_number"),
                            "streamer": v.get("streamer"),
                            "scheduled_time_ist": v.get("scheduled_release_time_ist"),
                            "title": v.get("title")
                        }
            print(f"✅ Found {len(manifest_vids)} published video IDs in famous_streamers_manifest.json.")
        except Exception as e:
            print(f"⚠️ Error reading manifest: {e}")

    # Combine all video IDs
    all_video_ids = list(dict.fromkeys([v[0] for v in channel_video_ids] + list(manifest_vids.keys())))
    print(f"📊 Total unique video IDs to query: {len(all_video_ids)}")
    print("-" * 75)

    # 3. Query video statistics in chunks of 50
    video_details = []
    chunk_size = 50
    for i in range(0, len(all_video_ids), chunk_size):
        chunk = all_video_ids[i:i + chunk_size]
        v_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,status&id={','.join(chunk)}"
        try:
            v_data = api_get(v_url, token)
            video_details.extend(v_data.get("items", []))
        except Exception as e:
            print(f"⚠️ Error fetching video details for chunk {i}: {e}")

    print(f"✅ Received real-time API details for {len(video_details)} videos.")
    print("-" * 75)

    # 4. Filter for videos from yesterday (2026-11-20 00:00 UTC) to tonight (2026-11-21 23:59 UTC / IST)
    # Define time window: Yesterday (start of 2026-11-20 IST = 2026-11-19 18:30 UTC) to current / end of today
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc.astimezone(IST)
    
    # Yesterday 00:00:00 IST
    yesterday_ist_start = (now_ist - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_utc_start = yesterday_ist_start.astimezone(timezone.utc)

    # Parse and enrich video data
    filtered_videos = []
    
    for v in video_details:
        vid_id = v["id"]
        snippet = v.get("snippet", {})
        stats = v.get("statistics", {})
        status = v.get("status", {})

        title = snippet.get("title", "Untitled")
        published_at_str = snippet.get("publishedAt", "")
        publish_at_str = status.get("publishAt", "")
        privacy_status = status.get("privacyStatus", "unknown")

        # Parse publication timestamp
        try:
            pub_dt = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
        except Exception:
            pub_dt = now_utc

        pub_dt_ist = pub_dt.astimezone(IST)

        # Check manifest data
        m_info = manifest_vids.get(vid_id, {})
        streamer = m_info.get("streamer", "N/A")
        batch_num = m_info.get("batch_number", "N/A")

        # View, like, comment counts
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        # Check if video was published or scheduled within yesterday to tonight
        # If in manifest, it was uploaded in the current session (yesterday/today)
        is_in_manifest = vid_id in manifest_vids
        is_in_date_range = pub_dt >= yesterday_utc_start

        if is_in_manifest or is_in_date_range:
            video_obj = {
                "id": vid_id,
                "title": title,
                "url": f"https://www.youtube.com/shorts/{vid_id}",
                "streamer": streamer,
                "batch": batch_num,
                "published_at_utc": published_at_str,
                "published_at_ist": pub_dt_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
                "scheduled_publish_at": publish_at_str,
                "privacy_status": privacy_status,
                "views": views,
                "likes": likes,
                "comments": comments,
                "is_public_now": privacy_status == "public"
            }
            filtered_videos.append(video_obj)

    # Sort: highest views first, then public first, then newest
    filtered_videos.sort(key=lambda x: (x["views"], x["likes"], x["is_public_now"]), reverse=True)

    # Aggregate stats
    total_views = sum(v["views"] for v in filtered_videos)
    total_likes = sum(v["likes"] for v in filtered_videos)
    total_comments = sum(v["comments"] for v in filtered_videos)
    public_count = sum(1 for v in filtered_videos if v["is_public_now"])
    scheduled_count = sum(1 for v in filtered_videos if v["privacy_status"] == "private" and v["scheduled_publish_at"])

    print("\n" + "=" * 75)
    print(f"📈 ANALYTICS SUMMARY (Yesterday {yesterday_ist_start.strftime('%d-%b')} to Tonight {now_ist.strftime('%d-%b-%Y %H:%M IST')})")
    print("=" * 75)
    print(f"🎯 Total Videos Analyzed:      {len(filtered_videos)}")
    print(f"🌐 Public / Live Right Now:    {public_count}")
    print(f"⏳ Scheduled (Rolling Unlocks): {scheduled_count}")
    print(f"👀 Total Aggregate Views:      {total_views:,}")
    print(f"👍 Total Aggregate Likes:      {total_likes:,}")
    print(f"💬 Total Aggregate Comments:   {total_comments:,}")
    print("=" * 75)

    print("\n🔥 TOP PERFORMING / LIVE VIDEOS:")
    print(f"{'#':<3} | {'Views':<6} | {'Likes':<5} | {'Status':<10} | {'Streamer':<14} | {'Title':<45} | {'URL'}")
    print("-" * 135)
    for idx, v in enumerate(filtered_videos[:35], 1):
        status_disp = "🟢 PUBLIC" if v["is_public_now"] else ("⏳ SCHED" if v["scheduled_publish_at"] else "🔒 PRIV")
        print(f"{idx:<3} | {v['views']:<6} | {v['likes']:<5} | {status_disp:<10} | {v['streamer']:<14} | {v['title'][:43]:<45} | {v['url']}")

    if len(filtered_videos) > 35:
        print(f"\n... and {len(filtered_videos) - 35} more scheduled / uploaded videos.")

    # Save to JSON
    report_data = {
        "fetched_at_utc": now_utc.isoformat(),
        "fetched_at_ist": now_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
        "channel": {
            "title": ch_title,
            "subscribers": ch_stats.get("subscriberCount", "0"),
            "total_channel_views": ch_stats.get("viewCount", "0"),
            "total_channel_videos": ch_stats.get("videoCount", "0"),
        },
        "period": {
            "from_ist": yesterday_ist_start.strftime("%Y-%m-%d %H:%M:%S IST"),
            "to_ist": now_ist.strftime("%Y-%m-%d %H:%M:%S IST")
        },
        "summary": {
            "total_videos": len(filtered_videos),
            "public_live_count": public_count,
            "scheduled_count": scheduled_count,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments
        },
        "videos": filtered_videos
    }

    with open(ANALYTICS_OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print(f"\n💾 Full JSON analytics report written to: {ANALYTICS_OUTPUT_JSON}")


if __name__ == "__main__":
    main()
