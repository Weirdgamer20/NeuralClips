import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import json
import urllib.request
from core.env_loader import load_env
load_env()
from sources.youtube_source import get_oauth_token

token = get_oauth_token()
with open("storage/speed_4k_upload_progress.json", "r", encoding="utf-8") as f:
    items = json.load(f)

ids = ",".join([x["video_id"] for x in items])
url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id={ids}"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))

for it in data.get("items", []):
    vid = it["id"]
    st = it["status"]
    sn = it["snippet"]
    print(f"{vid} | privacy: {st.get('privacyStatus')} | publishAt: {st.get('publishAt')} | publicStatsViewable: {st.get('publicStatsViewable')} | title: {sn.get('title')[:45]}")
