import json

with open(str(BASE_DIR / "storage" / "famous_streamers_manifest.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

batches = data.get("batches", [])
all_videos = []
for b in batches:
    for v in b.get("videos", []):
        if v.get("youtube_url"):
            all_videos.append(v)

print(f"Total Uploaded Videos: {len(all_videos)}")

# Group by creator
by_creator = {}
for v in all_videos:
    by_creator.setdefault(v["streamer"], []).append(v)

for creator, v_list in by_creator.items():
    print(f"\n{'='*60}")
    print(f"🔥 {creator.upper()} ({len(v_list)} Links)")
    print(f"{'='*60}")
    for item in v_list:
        print(f"• {item['youtube_url']} — {item['title']} (Batch {item.get('batch_number', 'N/A')})")
