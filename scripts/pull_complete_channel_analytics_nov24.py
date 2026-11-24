"""Complete Live YouTube Channel & Video Analytics Extractor (Nov 24, 2026).

Pulls real-time channel statistics and video performance metrics across all
uploaded batches:
- 100 IShowSpeed Scheduled Waves (Up to 1:00 AM)
- Indian Creators Batch (CarryMinati, Triggered Insaan, Techno Gamerz)
- 5:00 PM 2K Wave Batch (Batch 1 & Batch 2)
- Initial Master Review Cuts
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from sources.youtube_source import get_oauth_token

token = get_oauth_token()
if not token:
    print("Error: Could not retrieve OAuth token!")
    sys.exit(1)

# 1. Channel Level Stats
print("\n" + "="*80)
print("FETCHING CHANNEL LEVEL STATISTICS...")
print("="*80)

ch_url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true"
ch_req = urllib.request.Request(ch_url, headers={"Authorization": f"Bearer {token}"})
channel_info = {}
try:
    with urllib.request.urlopen(ch_req, timeout=15) as resp:
        ch_data = json.loads(resp.read().decode("utf-8"))
        items = ch_data.get("items", [])
        if items:
            ch_item = items[0]
            snip = ch_item.get("snippet", {})
            st = ch_item.get("statistics", {})
            channel_info = {
                "title": snip.get("title", ""),
                "custom_url": snip.get("customUrl", ""),
                "published_at": snip.get("publishedAt", ""),
                "subscribers": int(st.get("subscriberCount", 0)),
                "total_views": int(st.get("viewCount", 0)),
                "total_videos": int(st.get("videoCount", 0)),
                "hidden_subscriber_count": st.get("hiddenSubscriberCount", False)
            }
            print(f"Channel: {channel_info['title']} ({channel_info['custom_url']})")
            print(f"Total Subscribers: {channel_info['subscribers']:,}")
            print(f"Total Views:       {channel_info['total_views']:,}")
            print(f"Total Videos:      {channel_info['total_videos']:,}")
except Exception as e:
    print(f"Error fetching channel stats: {e}")

# 2. Collect Video IDs from all manifests & storage files
all_clips = []
seen_ids = set()

# A. IShowSpeed 100 Clips
p_speed = BASE_DIR / "storage" / "ishowspeed_scheduled_progress.json"
if p_speed.exists():
    with open(p_speed, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            vid = item.get("video_id")
            if vid and vid not in seen_ids:
                all_clips.append({
                    "id": item.get("id", ""),
                    "video_id": vid,
                    "batch": f"Speed Wave {item.get('wave', '?')}",
                    "title": item.get("title", ""),
                    "scheduled_ist": item.get("publish_at_ist", "")
                })
                seen_ids.add(vid)

# B. Indian Creators
p_indian = BASE_DIR / "storage" / "indian_creators_upload_progress.json"
if p_indian.exists():
    with open(p_indian, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            vid = item.get("video_id")
            if vid and vid not in seen_ids:
                all_clips.append({
                    "id": item.get("id", ""),
                    "video_id": vid,
                    "batch": f"Indian Creators ({item.get('creator', 'Gaming')})",
                    "title": item.get("title", ""),
                    "scheduled_ist": item.get("publish_at_ist", "")
                })
                seen_ids.add(vid)

# C. 5:00 PM Batch
p_5pm = BASE_DIR / "storage" / "scheduled_5pm_upload_progress.json"
if p_5pm.exists():
    with open(p_5pm, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            vid = item.get("video_id")
            if vid and vid not in seen_ids:
                all_clips.append({
                    "id": item.get("id", ""),
                    "video_id": vid,
                    "batch": "5:00 PM Wave Batch",
                    "title": item.get("title", ""),
                    "scheduled_ist": item.get("publish_at_ist", "")
                })
                seen_ids.add(vid)

# D. Wave Uploader Batch 2
p_waves = BASE_DIR / "storage" / "wave_uploader_progress.json"
if p_waves.exists():
    with open(p_waves, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            vid = item.get("video_id")
            if vid and vid not in seen_ids:
                all_clips.append({
                    "id": item.get("id", ""),
                    "video_id": vid,
                    "batch": f"Batch 2 (Wave {item.get('wave', '?')})",
                    "title": item.get("title", ""),
                    "scheduled_ist": item.get("publish_at_ist", "")
                })
                seen_ids.add(vid)

# E. Initial Review Cuts
initial_cuts = [
    {"id": "cut_01", "video_id": "qB2lftPAU-M", "batch": "Initial Review Cuts", "title": "Fastest Supercar 160MPH Police Chase in GTA 6 💀"},
    {"id": "cut_02", "video_id": "zJ5jqdTBiT0", "batch": "Initial Review Cuts", "title": "When GTA 6 Police Roadblock FAILS Instantly 💀🚨"},
    {"id": "cut_03", "video_id": "iMpx6VRjb7w", "batch": "Initial Review Cuts", "title": "INSANE GTA 6 Traffic Weave Causes Massive Pileup 💀🚗"},
    {"id": "cut_04", "video_id": "GR_XhjJK4gY", "batch": "Initial Review Cuts", "title": "Can a TANK Survive 6-Star Police in GTA 6? 💀🚀"},
    {"id": "cut_05", "video_id": "ft7qumijpJs", "batch": "Initial Review Cuts", "title": "CaseOh RAGES at GTA 6 Truck Physics 💀🚗"}
]
for c in initial_cuts:
    if c["video_id"] not in seen_ids:
        all_clips.append(c)
        seen_ids.add(c["video_id"])

print(f"\nTotal unique uploaded video IDs collected: {len(all_clips)}")

# 3. Fetch Video Details & Statistics in Chunks of 50
video_ids = [c["video_id"] for c in all_clips]
stats_map = {}

for i in range(0, len(video_ids), 50):
    chunk = video_ids[i:i + 50]
    ids_str = ",".join(chunk)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,status,statistics,contentDetails&id={ids_str}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            for item in res_data.get("items", []):
                vid = item["id"]
                snip = item.get("snippet", {})
                st = item.get("status", {})
                stats = item.get("statistics", {})
                cd = item.get("contentDetails", {})
                
                pub_raw = snip.get("publishedAt", "")
                pub_ist = ""
                if pub_raw:
                    try:
                        dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
                        dt_ist = dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
                        pub_ist = dt_ist.strftime("%d-%b %I:%M %p")
                    except Exception:
                        pub_ist = pub_raw
                        
                stats_map[vid] = {
                    "title": snip.get("title", ""),
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "privacy_status": st.get("privacyStatus", "unknown"),
                    "definition": cd.get("definition", "unknown"),
                    "duration": cd.get("duration", ""),
                    "published_ist": pub_ist
                }
    except Exception as e:
        print(f"Error fetching chunk {i}: {e}")

# 4. Merge records
records = []
for c in all_clips:
    vid = c["video_id"]
    st = stats_map.get(vid, {})
    records.append({
        "video_id": vid,
        "batch": c.get("batch", "Other"),
        "title": st.get("title") or c.get("title", ""),
        "views": st.get("views", 0),
        "likes": st.get("likes", 0),
        "comments": st.get("comments", 0),
        "privacy": st.get("privacy_status", "unknown"),
        "definition": st.get("definition", "unknown"),
        "published_ist": st.get("published_ist", "N/A"),
        "url": f"https://www.youtube.com/shorts/{vid}"
    })

# Sort descending by views
records.sort(key=lambda x: (x["views"], x["likes"]), reverse=True)

# 5. Output Summary
tot_views = sum(r["views"] for r in records)
tot_likes = sum(r["likes"] for r in records)
tot_comments = sum(r["comments"] for r in records)
active_public = sum(1 for r in records if r["privacy"] == "public")
scheduled_count = sum(1 for r in records if r["privacy"] == "private")

print("\n" + "="*80)
print("AGGREGATE UPLOADED CLIPS PERFORMANCE (ALL BATCHES)")
print("="*80)
print(f"  • Total Videos Analyzed: {len(records)}")
print(f"  • Currently Public:      {active_public}")
print(f"  • Currently Scheduled:   {scheduled_count}")
print(f"  • Total Views:           {tot_views:,}")
print(f"  • Total Likes:           {tot_likes:,}")
print(f"  • Total Comments:        {tot_comments:,}")

# Top 25
print("\n" + "="*110)
print(f"{'#':<3} | {'Views':<6} | {'Likes':<5} | {'Status':<8} | {'Batch':<22} | {'Title':<40} | {'URL'}")
print("="*110)
for idx, r in enumerate(records[:25], 1):
    title_short = (r['title'][:37] + '...') if len(r['title']) > 40 else r['title']
    print(f"{idx:<3} | {r['views']:<6} | {r['likes']:<5} | {r['privacy']:<8} | {r['batch']:<22} | {title_short:<40} | {r['url']}")
print("="*110)

# Batch Breakdown
batch_summary = {}
for r in records:
    b = r["batch"]
    if b.startswith("Speed Wave"):
        group = "IShowSpeed 24-Wave Run"
    elif "Indian" in b:
        group = "Indian Creators Run"
    elif "5:00 PM" in b:
        group = "5:00 PM Batch"
    elif "Batch 2" in b:
        group = "Batch 2 Waves"
    else:
        group = "Initial Review Cuts"
        
    if group not in batch_summary:
        batch_summary[group] = {"count": 0, "views": 0, "likes": 0, "public": 0}
    batch_summary[group]["count"] += 1
    batch_summary[group]["views"] += r["views"]
    batch_summary[group]["likes"] += r["likes"]
    if r["privacy"] == "public":
        batch_summary[group]["public"] += 1

print("\n" + "="*80)
print("PERFORMANCE BREAKDOWN BY PRODUCTION RUN")
print("="*80)
for g, s in batch_summary.items():
    print(f"{g:<25} | Videos: {s['count']:<3} | Public: {s['public']:<3} | Views: {s['views']:<6} | Likes: {s['likes']}")

# Save full results to JSON
out_json = BASE_DIR / "storage" / "complete_channel_analytics_nov24.json"
out_data = {
    "extracted_at": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
    "channel_info": channel_info,
    "aggregate_stats": {
        "total_videos": len(records),
        "total_views": tot_views,
        "total_likes": tot_likes,
        "total_comments": tot_comments,
        "public_count": active_public,
        "scheduled_count": scheduled_count
    },
    "batch_breakdown": batch_summary,
    "videos": records
}
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(out_data, f, indent=2)

print(f"\nSaved full analytics to {out_json}")
