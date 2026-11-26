import json
from datetime import datetime

with open('storage/all_historical_videos_analytics.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

videos = data['videos']

# NeuralClips started operating on Nov 20, 2026
pipeline_vids = []
for v in videos:
    pub = v.get('published_at_utc', '')
    if pub >= '2026-11-20':
        pipeline_vids.append(v)

total_views = sum(v['views'] for v in pipeline_vids)
total_likes = sum(v['likes'] for v in pipeline_vids)
total_comments = sum(v['comments'] for v in pipeline_vids)

print(f"Total NeuralClips Videos Uploaded by Pipeline: {len(pipeline_vids)}")
print(f"Total Pipeline Views:   {total_views:,}")
print(f"Total Pipeline Likes:   {total_likes:,}")
print(f"Total Pipeline Comments: {total_comments:,}")
print("=" * 80)
print("Top 35 Pipeline Videos Overall:")
for i, v in enumerate(pipeline_vids[:35], 1):
    t = v['title'][:45]
    print(f"{i:2d}. [{v['views']:4d} views | {v['likes']:2d} likes] {v['published_at_ist'][:16]} | {t:<45} | {v['url']}")
