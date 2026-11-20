import json

with open(r"d:\vidclip\storage\scraped_top300_gta6_shorts.json", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 60)
print(f"TOTAL SHORTS SCRAPED: {data['total_scraped']}")
print(f"SHORTS OVER 1M VIEWS: {data['shorts_over_1m_views']}")
print(f"SHORTS OVER 10M VIEWS: {data['shorts_over_10m_views']}")
print(f"AVERAGE VIEWS: {data['average_views']:,}")
print(f"HIGHEST VIEWS: {data['highest_views']:,}")
print("=" * 60)

print("\n--- TOP 8 VIRAL SHORTS BREAKDOWN ---")
for i, s in enumerate(data["top_viral_shorts"][:8], 1):
    print(f"\n#{i} | {s['view_count']:,} Views | URL: {s['url']}")
    print(f"    Title: {s['title']}")
    print(f"    Channel: {s['uploader']}")
    if "upload_date" in s:
        likes = s.get('like_count') or 0
        print(f"    Upload Date: {s.get('upload_date')} | Likes: {likes:,}")
        track = s.get('track') or s.get('artist') or "Raw In-Game Audio / Trend Sound"
        print(f"    Audio/Music: {track}")
        if s.get("tags"):
            print(f"    Tags: {', '.join(s['tags'][:6])}")
    if s.get("top_comments"):
        print("    Top Comments (What Viewers Are Saying):")
        for c in s["top_comments"][:3]:
            txt = c['text'].replace('\n', ' ')[:110]
            print(f"      💬 \"{txt}\" [👍 {c.get('like_count', 0):,}]")
