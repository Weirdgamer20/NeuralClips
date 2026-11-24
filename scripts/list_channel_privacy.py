"""Lists all videos on the channel and categorizes by privacy status.
"""

import json
import urllib.request
import sys
from pathlib import Path
sys.path.insert(0, str(Path("d:/vidclip")))

from core.env_loader import load_env
load_env()
from sources.youtube_source import get_oauth_token

token = get_oauth_token()
next_page = None
all_items = []
while True:
    url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,status&playlistId=UUXO9foGJcaWJEZyCj_CIQgw&maxResults=50"
    if next_page:
        url += f"&pageToken={next_page}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    all_items.extend(data.get("items", []))
    next_page = data.get("nextPageToken")
    if not next_page:
        break

privates = [it for it in all_items if it.get("status", {}).get("privacyStatus") != "public"]
publics = [it for it in all_items if it.get("status", {}).get("privacyStatus") == "public"]
print(f"Total videos on channel: {len(all_items)}")
print(f"Public videos: {len(publics)}")
print(f"Private/Scheduled videos: {len(privates)}")
for p in privates:
    vid_id = p["snippet"]["resourceId"]["videoId"]
    print(f"  • {vid_id}: {p['snippet']['title'][:60]} | Status: {p.get('status', {}).get('privacyStatus')}")
