import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_DIR = Path("d:/vidclip")
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from publishing.youtube_auth import YouTubeAuth

def fetch_analytics():
    print("=" * 65)
    print("📊 FETCHING REAL-TIME YOUTUBE ANALYTICS (Yesterday to Today)")
    print("=" * 65)

    auth = YouTubeAuth()
    yt = auth.get_authorized_service()
    if not yt:
        print("❌ Could not authorize YouTube service.")
        return

    # 1. Get channel's uploads playlist
    ch_res = yt.channels().list(part="contentDetails,statistics,snippet", mine=True).execute()
    items = ch_res.get("items", [])
    if not items:
        print("❌ No channel found for authenticated user.")
        return

    channel = items[0]
    ch_title = channel["snippet"]["title"]
    ch_stats = channel["statistics"]
    uploads_playlist_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

    print(f"📺 Channel: {ch_title}")
    print(f"👥 Channel Total Subscribers: {ch_stats.get('subscriberCount', '0')}")
    print(f"👁️ Channel Lifetime Views: {ch_stats.get('viewCount', '0')}")
    print(f"🎬 Channel Total Videos: {ch_stats.get('videoCount', '0')}")
    print("-" * 65)

    # 2. Fetch all videos from uploads playlist
    video_ids = []
    next_page = None
    print("⏳ Retrieving uploaded videos from channel...")

    while True:
        pl_res = yt.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page
        ).execute()

        for item in pl_res.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        next_page = pl_res.get("nextPageToken")
        if not next_page or len(video_ids) >= 200:
            break

    print(f"Found {len(video_ids)} total videos on channel. Fetching stats...\n")

    # 3. Batch query video stats in chunks of 50
    video_data = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        v_res = yt.videos().list(
            part="snippet,statistics,status",
            id=",".join(chunk)
        ).execute()

        for v in v_res.get("items", []):
            snippet = v.get("snippet", {})
            stats = v.get("statistics", {})
            status = v.get("status", {})

            video_data.append({
                "id": v["id"],
                "title": snippet.get("title", ""),
                "published_at": snippet.get("publishedAt", ""),
                "publish_at": status.get("publishAt", ""),
                "privacy_status": status.get("privacyStatus", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "url": f"https://www.youtube.com/shorts/{v['id']}"
            })

    # 4. Filter for yesterday (20-Nov-2026) and today (21-Nov-2026)
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(timezone.utc).astimezone(ist_tz)
    yesterday_ist = now_ist - timedelta(days=1)

    recent_videos = []
    for v in video_data:
        # Check published_at
        p_str = v["published_at"]
        if p_str:
            dt = datetime.fromisoformat(p_str.replace("Z", "+00:00")).astimezone(ist_tz)
            if dt.date() >= (yesterday_ist.date() - timedelta(days=1)):
                v["dt_ist"] = dt
                recent_videos.append(v)

    print(f"📈 Total Videos Analyzed (Yesterday to Tonight): {len(recent_videos)}")
    
    total_views = sum(v["views"] for v in recent_videos)
    total_likes = sum(v["likes"] for v in recent_videos)
    total_comments = sum(v["comments"] for v in recent_videos)

    print(f"🔥 Aggregate Stats Across Uploads:")
    print(f"   • Total Views:    {total_views:,}")
    print(f"   • Total Likes:    {total_likes:,}")
    print(f"   • Total Comments: {total_comments:,}\n")

    # Sort by views descending
    recent_videos.sort(key=lambda x: x["views"], reverse=True)

    print("🏆 Top 10 Most Viewed Videos:")
    for i, v in enumerate(recent_videos[:10], 1):
        print(f"  {i}. [{v['views']} views | {v['likes']} likes] {v['title'][:48]}...")
        print(f"     URL: {v['url']}")
        print(f"     Privacy: {v['privacy_status']} (Published: {v['dt_ist'].strftime('%d-%b %I:%M %p IST')})")

    # Save to file
    out_file = BASE_DIR / "storage" / "channel_analytics_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": now_ist.isoformat(),
            "channel_title": ch_title,
            "total_recent_videos": len(recent_videos),
            "aggregate_views": total_views,
            "aggregate_likes": total_likes,
            "aggregate_comments": total_comments,
            "videos": [{k: v if k != "dt_ist" else str(v) for k, v in item.items()} for item in recent_videos]
        }, f, indent=2)

    print(f"\nSaved full analytics report to {out_file}")

if __name__ == "__main__":
    fetch_analytics()
