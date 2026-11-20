"""Extract and analyze our 100 published Shorts from SQLite database."""

import json
import os
import sqlite3
import statistics

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "neuralclips.db")
OUTPUT_FILE = os.path.join(BASE_DIR, "storage", "our_100_shorts_analysis.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute("""
        SELECT 
            p.pub_id, p.clip_id, p.title, p.description, p.hashtags, 
            p.youtube_video_id, p.published_at,
            c.duration, c.width, c.height, c.aspect_ratio,
            h.category, h.score, h.transcript,
            s.title as stream_title, s.crop_profile
        FROM youtube_publications p
        JOIN rendered_clips c ON p.clip_id = c.clip_id
        JOIN approved_highlights h ON c.highlight_id = h.highlight_id
        LEFT JOIN source_streams s ON c.source_id = s.source_id
        WHERE p.status = 'PUBLISHED'
        ORDER BY p.published_at DESC
    """).fetchall()

    data = [dict(r) for r in rows]
    print(f"Total published clips in DB: {len(data)}")

    if not data:
        print("No clips found!")
        return

    durations = [d["duration"] for d in data if d.get("duration")]
    title_lengths = [len(d["title"]) for d in data if d.get("title")]
    scores = [d["score"] for d in data if d.get("score")]
    categories = {}
    for d in data:
        cat = d.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    summary = {
        "total_published": len(data),
        "avg_duration": round(statistics.mean(durations), 1) if durations else 0,
        "median_duration": round(statistics.median(durations), 1) if durations else 0,
        "min_duration": min(durations) if durations else 0,
        "max_duration": max(durations) if durations else 0,
        "avg_title_length": round(statistics.mean(title_lengths), 1) if title_lengths else 0,
        "avg_score": round(statistics.mean(scores), 1) if scores else 0,
        "category_distribution": categories,
        "sample_titles": [d["title"] for d in data[:15]],
        "clips": data,
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved analysis of {len(data)} published clips to {OUTPUT_FILE}")
    print(f"Avg Duration: {summary['avg_duration']}s")
    print(f"Avg Title Length: {summary['avg_title_length']} chars")
    print("Categories:", categories)

if __name__ == "__main__":
    main()
