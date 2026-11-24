import json
from pathlib import Path

path = Path("storage/youtube_analytics_yesterday_to_tonight.json")
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

vids = data.get("videos", [])
vids.sort(key=lambda x: int(x.get("views", 0)), reverse=True)

print(f"Total videos analyzed: {len(vids)}")
print("\n🔥 TOP 15 PERFORMING VIDEOS:")
for i, v in enumerate(vids[:15], 1):
    views = v.get("views", 0)
    likes = v.get("likes", 0)
    title = v.get("title", "")[:50]
    url = v.get("url", "")
    print(f"#{i:02d} | {views:>5} views | {likes:>3} likes | {title:<50} | {url}")

b_1k = [v for v in vids if int(v.get("views", 0)) >= 1000]
b_500 = [v for v in vids if 500 <= int(v.get("views", 0)) < 1000]
b_100 = [v for v in vids if 100 <= int(v.get("views", 0)) < 500]
b_10 = [v for v in vids if 10 <= int(v.get("views", 0)) < 100]
b_under10 = [v for v in vids if int(v.get("views", 0)) < 10]

print(f"\n📊 VIEW DISTRIBUTION:")
print(f"  • 1,000+ views (Viral Tier):       {len(b_1k)} videos")
print(f"  • 500 - 999 views (High Momentum): {len(b_500)} videos")
print(f"  • 100 - 499 views (Moderate):      {len(b_100)} videos")
print(f"  • 10 - 99 views (Seed Stage):      {len(b_10)} videos")
print(f"  • <10 views (Fresh/Unindexed):     {len(b_under10)} videos")

tot_views = sum(int(v.get("views", 0)) for v in vids)
tot_likes = sum(int(v.get("likes", 0)) for v in vids)
tot_comments = sum(int(v.get("comments", 0)) for v in vids)
print(f"\n📈 AGGREGATE TOTALS:")
print(f"  • Total Views:    {tot_views:,}")
print(f"  • Total Likes:    {tot_likes:,}")
print(f"  • Total Comments: {tot_comments:,}")
print(f"  • Like Ratio:     {(tot_likes/tot_views*100) if tot_views>0 else 0:.2f}%")
