"""Discovers top viewed active GTA 6 livestreams on YouTube in real time."""

import json
import os
import sys
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from typing import Any, Dict, List
from core.env_loader import load_env
from core.logging_config import setup_logger
from sources.youtube_source import get_oauth_token

logger = setup_logger("neuralclips.find_top_streams")

_CACHE_FILE = os.path.join(BASE_DIR, "storage", "cached_streams.json")
_CACHE_TTL_SECONDS = 900  # 15 minutes


def get_top_gta6_livestreams(limit: int = 5) -> List[Dict[str, Any]]:
    load_env()
    token = get_oauth_token()
    if not token:
        logger.error("No OAuth access token available to query YouTube Data API.")
        return []

    # Check cache first to preserve "Search Queries per day" quota (Limit: 100/day)
    import time
    if os.path.exists(_CACHE_FILE):
        try:
            with open(_CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            if time.time() - cached.get("timestamp", 0) < _CACHE_TTL_SECONDS and cached.get("streams"):
                logger.info(f"Using cached top livestreams (age: {int(time.time() - cached['timestamp'])}s, preserving Search Quota)")
                return cached["streams"][:limit]
        except Exception:
            pass

    # 1. Search active livestreams with query GTA 6
    search_params = {
        "part": "snippet",
        "eventType": "live",
        "type": "video",
        "q": "GTA 6 live",
        "order": "viewCount",
        "maxResults": max(10, limit * 2),
    }
    search_url = "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(search_params)
    req = urllib.request.Request(search_url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("items", [])
    except Exception as e:
        logger.error(f"Failed to query YouTube live search: {e}")
        return []

    video_ids = [it["id"]["videoId"] for it in items if "videoId" in it.get("id", {})]
    if not video_ids:
        logger.warning("No active GTA 6 livestreams found.")
        return []

    # 2. Get live viewer statistics
    v_url = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode({
        "part": "snippet,liveStreamingDetails,statistics",
        "id": ",".join(video_ids),
    })
    v_req = urllib.request.Request(v_url)
    v_req.add_header("Authorization", f"Bearer {token}")
    v_req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(v_req, timeout=15) as v_resp:
            v_data = json.loads(v_resp.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"Failed to get video statistics: {e}")
        return []

    streams = []
    for v in v_data.get("items", []):
        vid = v["id"]
        snippet = v.get("snippet", {})
        title = snippet.get("title", "")
        ch_title = snippet.get("channelTitle", "")
        ch_id = snippet.get("channelId", "")
        lsd = v.get("liveStreamingDetails", {})
        concurrent = int(lsd.get("concurrentViewers", 0)) if lsd.get("concurrentViewers") else 0
        stats = v.get("statistics", {})
        total_views = int(stats.get("viewCount", 0))

        streams.append({
            "video_id": vid,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "title": title,
            "channel_title": ch_title,
            "channel_id": ch_id,
            "concurrent_viewers": concurrent,
            "view_count": total_views,
        })

    # Sort descending by concurrent viewers, then view count
    streams.sort(key=lambda x: (x["concurrent_viewers"], x["view_count"]), reverse=True)

    # Save to cache to protect the 100 Search Queries/day limit
    try:
        os.makedirs(os.path.dirname(_CACHE_FILE), exist_ok=True)
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"timestamp": time.time(), "streams": streams}, f)
    except Exception:
        pass

    return streams[:limit]


if __name__ == "__main__":
    top = get_top_gta6_livestreams(5)
    print(f"Discovered {len(top)} top active GTA 6 livestreams:")
    for idx, s in enumerate(top, 1):
        print(f"{idx}. [{s['concurrent_viewers']} concurrent, {s['view_count']} views] {s['channel_title']}: {s['title']}")
        print(f"   URL: {s['url']}")
