"""Finds true 4K / 1440p 60FPS GTA 6 sources for ultra-sharp rendering.
"""

import json
import subprocess
import sys
import yt_dlp

def find_highres_videos(query, max_results=5):
    print(f"\n🔍 Searching for 4K/1440p: '{query}'")
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        res = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        entries = res.get("entries", [])
    
    results = []
    for e in entries:
        vid_id = e.get("id")
        title = e.get("title")
        dur = e.get("duration")
        url = f"https://www.youtube.com/watch?v={vid_id}"
        
        # Check available formats
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl2:
                info = ydl2.extract_info(url, download=False)
                formats = info.get("formats", [])
                heights = sorted(list(set(f.get("height") for f in formats if f.get("height"))))
                max_h = max(heights) if heights else 0
                results.append({
                    "id": vid_id,
                    "title": title,
                    "duration": dur,
                    "max_height": max_h,
                    "heights": heights,
                    "url": url,
                })
                print(f"  • [{max_h}p | {dur}s] {title[:55]} -> {url}")
        except Exception as err:
            pass
    return results

if __name__ == "__main__":
    find_highres_videos("GTA 6 4K 60FPS gameplay crazy moments", 4)
    find_highres_videos("GTA 6 4K 60FPS supercar police chase", 4)
