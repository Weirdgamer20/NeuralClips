import os
import sys
import json
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_DIR = Path("d:/vidclip")
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from sources.youtube_source import get_oauth_token

# 1. Collect all video entries uploaded in our sessions
all_clips = []
seen_ids = set()

# Initial 1:30 PM cuts
initial_cuts = [
    {"id": "cut_01", "video_id": "qB2lftPAU-M", "batch": "1:30 PM Review Cuts", "title": "Fastest Supercar 160MPH Police Chase in GTA 6 💀"},
    {"id": "cut_02", "video_id": "zJ5jqdTBiT0", "batch": "1:30 PM Review Cuts", "title": "When GTA 6 Police Roadblock FAILS Instantly 💀🚨"},
    {"id": "cut_03", "video_id": "iMpx6VRjb7w", "batch": "1:30 PM Review Cuts", "title": "INSANE GTA 6 Traffic Weave Causes Massive Pileup 💀🚗"},
    {"id": "cut_04", "video_id": "GR_XhjJK4gY", "batch": "1:30 PM Review Cuts", "title": "Can a TANK Survive 6-Star Police in GTA 6? 💀🚀"},
    {"id": "cut_05", "video_id": "ft7qumijpJs", "batch": "1:30 PM Review Cuts", "title": "CaseOh RAGES at GTA 6 Truck Physics 💀🚗"}
]
for c in initial_cuts:
    all_clips.append(c)
    seen_ids.add(c["video_id"])

# 5:00 PM Batch (40 clips)
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
                    "batch": "5:00 PM 2K Batch (Batch 1)",
                    "title": item.get("title", "")
                })
                seen_ids.add(vid)

# Batch 2 (Wave Uploader 40 clips)
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
                    "title": item.get("title", "")
                })
                seen_ids.add(vid)

# Indian Creators Batch
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
                    "title": item.get("title", "")
                })
                seen_ids.add(vid)

print(f"Total unique uploaded video IDs collected: {len(all_clips)}")

# 2. Query YouTube API in chunks of 50
token = get_oauth_token()
video_ids = [c["video_id"] for c in all_clips]

stats_map = {}
for i in range(0, len(video_ids), 50):
    chunk = video_ids[i:i + 50]
    ids_str = ",".join(chunk)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={ids_str}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            for item in res_data.get("items", []):
                vid = item["id"]
                snip = item.get("snippet", {})
                stats = item.get("statistics", {})
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
                    "published_ist": pub_ist
                }
    except Exception as e:
        print(f"Error fetching chunk {i}: {e}")

# Merge stats with clip list
records = []
for c in all_clips:
    vid = c["video_id"]
    st = stats_map.get(vid, {})
    records.append({
        "video_id": vid,
        "batch": c["batch"],
        "title": st.get("title") or c["title"],
        "views": st.get("views", 0),
        "likes": st.get("likes", 0),
        "comments": st.get("comments", 0),
        "published_ist": st.get("published_ist", "N/A"),
        "url": f"https://www.youtube.com/shorts/{vid}"
    })

# Sort descending by views
records.sort(key=lambda x: x["views"], reverse=True)

# Save JSON output
out_json = BASE_DIR / "storage" / "all_uploaded_clips_analytics_latest.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2)

print(f"Successfully processed {len(records)} videos. Writing tables...")

# Print top 30 summary
print("\n" + "="*110)
print(f"{'#':<3} | {'Views':<6} | {'Likes':<5} | {'Batch':<22} | {'Title':<45} | {'URL'}")
print("="*110)
for idx, r in enumerate(records[:30], 1):
    title_short = (r['title'][:42] + '...') if len(r['title']) > 45 else r['title']
    print(f"{idx:<3} | {r['views']:<6} | {r['likes']:<5} | {r['batch']:<22} | {title_short:<45} | {r['url']}")
print("="*110)

tot_views = sum(r["views"] for r in records)
tot_likes = sum(r["likes"] for r in records)
print(f"\n📊 AGGREGATE TOTALS FOR OUR UPLOADED CLIPS:")
print(f"  • Total Videos Analyzed: {len(records)}")
print(f"  • Total Views Generated: {tot_views:,}")
print(f"  • Total Likes:          {tot_likes:,}")
