"""Searches YouTube for true viral GTA streamer moments with peak comedy/action.
"""

import json
import subprocess
import sys

def search_moments(query, max_results=6):
    print(f"\n🔍 Searching for: {query}")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        f"ytsearch{max_results}:{query}",
        "--dump-json",
        "--flat-playlist",
        "--no-warnings"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    results = []
    for line in res.stdout.strip().split("\n"):
        if not line:
            continue
        try:
            d = json.loads(line)
            results.append({
                "title": d.get("title"),
                "id": d.get("id"),
                "url": d.get("url") or f"https://www.youtube.com/watch?v={d.get('id')}",
                "duration": d.get("duration"),
                "view_count": d.get("view_count"),
                "channel": d.get("uploader") or d.get("channel"),
            })
        except Exception:
            pass
    return results

if __name__ == "__main__":
    queries = [
        "GTA 6 funny moments fails",
        "IShowSpeed GTA 6 funny stream moments",
        "Kai Cenat GTA funniest moments",
        "CaseOh GTA best fails",
        "GTA 6 insane stunt fails compilation",
    ]
    for q in queries:
        items = search_moments(q, 4)
        for it in items:
            v_val = it['view_count']
            views = f"{v_val:,}" if v_val else "N/A"
            dur = f"{it['duration']}s" if it['duration'] else "N/A"
            print(f"  • [{views} views | {dur}] {it['title']} ({it['channel']}) -> {it['url']}")
