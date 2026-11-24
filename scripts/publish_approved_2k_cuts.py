"""Publishes the 4 approved 2K master cuts to YouTube as PUBLIC Shorts with custom 9:16 cinema thumbnails.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from sources.youtube_source import get_oauth_token
from rendering.thumbnail_generator import ThumbnailGenerator

REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
THUMB_DIR = BASE_DIR / "storage" / "thumbnails"

CUTS_TO_PUBLISH = [
    {
        "id": "cut_01",
        "file_path": str(REVIEW_DIR / "cut_01_supercar_pursuit_1440p60.mp4"),
        "thumb_path": str(THUMB_DIR / "thumb_cut_01_approved.jpg"),
        "title": "Fastest Supercar 160MPH Police Chase in GTA 6 💀 #Shorts",
        "description": "Fastest supercar in Vice City hits 160 MPH while dodging oncoming police cruisers!\nCan anything stop this car?\n\n#GTA6 #Shorts #Gaming #PoliceChase #ViceCity #GTAOnline",
        "tags": ["gta 6", "gta 6 police chase", "gta 6 supercar", "vice city", "gaming", "shorts", "gta 6 gameplay"],
    },
    {
        "id": "cut_02",
        "file_path": str(REVIEW_DIR / "cut_02_supercar_bridge_escape_1440p60.mp4"),
        "thumb_path": str(THUMB_DIR / "thumb_cut_02_approved.jpg"),
        "title": "When GTA 6 Police Roadblock FAILS Instantly 💀🚨 #Shorts",
        "description": "5-Star police set up a complete roadblock on the bridge, but the supercar hits the ramp at top speed!\nWatch the chain reaction crash.\n\n#GTA6 #Shorts #Gaming #GTA6Fails #ViceCity #CarCrash",
        "tags": ["gta 6", "gta 6 stunts", "gta 6 crash", "police roadblock", "gaming", "shorts", "gta 6 fails"],
    },
    {
        "id": "cut_03",
        "file_path": str(REVIEW_DIR / "cut_03_supercar_traffic_weave_1440p60.mp4"),
        "thumb_path": str(THUMB_DIR / "thumb_cut_03_approved.jpg"),
        "title": "INSANE GTA 6 Traffic Weave Causes Massive Pileup 💀🚗 #Shorts",
        "description": "Precision high-speed slalom through midday Vice City highway traffic!\nPolice cruisers try to keep up and trigger a 10-car pileup.\n\n#GTA6 #Shorts #Gaming #GTA6Gameplay #TrafficWeave #ViceCity",
        "tags": ["gta 6", "gta 6 traffic weave", "gta 6 chase", "gaming", "shorts", "vice city"],
    },
    {
        "id": "cut_04",
        "file_path": str(REVIEW_DIR / "cut_04_tank_6star_rampage_1440p60.mp4"),
        "thumb_path": str(THUMB_DIR / "thumb_cut_04_approved.jpg"),
        "title": "Can a TANK Survive 6-Star Police in GTA 6? 💀🚀 #Shorts",
        "description": "Testing the military tank against 6-Star wanted level police in GTA 6!\nCrushing SWAT APCs and blowing attack helicopters out of the sky.\n\n#GTA6 #Shorts #Gaming #TankRampage #GTA6Police #ViceCity",
        "tags": ["gta 6", "gta 6 tank", "6 star wanted", "military chase", "gaming", "shorts", "gta 6 gameplay"],
    },
]

def upload_short_public(file_path: str, title: str, description: str, tags: list, token: str) -> str:
    """Uploads public YouTube Short via resumable API."""
    file_size = os.path.getsize(file_path)
    init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "20",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    init_req = urllib.request.Request(
        init_url,
        data=json.dumps(metadata).encode("utf-8"),
        method="POST"
    )
    init_req.add_header("Authorization", f"Bearer {token}")
    init_req.add_header("Content-Type", "application/json; charset=UTF-8")
    init_req.add_header("X-Upload-Content-Type", "video/mp4")
    init_req.add_header("X-Upload-Content-Length", str(file_size))

    with urllib.request.urlopen(init_req, timeout=30) as init_resp:
        upload_url = init_resp.headers.get("Location")
        if not upload_url:
            raise RuntimeError("No upload URL returned by YouTube API.")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    upload_req = urllib.request.Request(upload_url, data=file_bytes, method="PUT")
    upload_req.add_header("Content-Type", "video/mp4")
    upload_req.add_header("Content-Length", str(len(file_bytes)))

    with urllib.request.urlopen(upload_req, timeout=180) as upload_resp:
        resp_data = json.loads(upload_resp.read().decode("utf-8"))
        vid_id = resp_data.get("id")
        if not vid_id:
            raise RuntimeError(f"No video ID in response: {resp_data}")
        return vid_id

def main():
    print("=" * 70)
    print("🚀 PUBLISHING 4 APPROVED 2K MASTER CUTS TO YOUTUBE")
    print("=" * 70)

    token = get_oauth_token()
    if not token:
        print("❌ Could not get YouTube OAuth token.")
        sys.exit(1)

    thumb_gen = ThumbnailGenerator()
    results = []

    for idx, cut in enumerate(CUTS_TO_PUBLISH, 1):
        f_path = cut["file_path"]
        t_path = cut["thumb_path"]
        title = cut["title"]
        desc = cut["description"]
        tags = cut["tags"]

        print(f"\n[{idx}/4] Publishing: {Path(f_path).name}")
        print(f"      Title: {title}")

        try:
            vid_id = upload_short_public(f_path, title, desc, tags, token)
            short_url = f"https://www.youtube.com/shorts/{vid_id}"
            print(f"      ✅ VIDEO PUBLISHED: {short_url}")

            # Upload thumbnail
            if os.path.exists(t_path):
                ok = thumb_gen.upload_to_youtube(vid_id, t_path, token)
                if ok:
                    print("      🎯 Custom thumbnail uploaded successfully!")
                else:
                    print("      ⚠️ Thumbnail upload returned non-200")

            results.append({
                "id": cut["id"],
                "video_id": vid_id,
                "short_url": short_url,
                "title": title,
                "status": "PUBLIC",
            })
            time.sleep(2.0)
        except Exception as e:
            print(f"      ❌ Upload failed: {e}")
            results.append({
                "id": cut["id"],
                "file_path": f_path,
                "title": title,
                "error": str(e),
                "status": "FAILED",
            })

    out_file = BASE_DIR / "storage" / "published_2k_approved_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    main()
