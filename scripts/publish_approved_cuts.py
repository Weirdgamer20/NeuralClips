"""Publishes the 3 approved high-quality review cuts to YouTube as PUBLIC Shorts.

Also generates and sets high-CTR 9:16 vertical thumbnails for each video.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path("d:/vidclip")
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from sources.youtube_source import get_oauth_token
from rendering.thumbnail_generator import ThumbnailGenerator
from core.state_store import StateStore

REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
THUMBNAILS_DIR = BASE_DIR / "storage" / "thumbnails"
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

CUTS_TO_PUBLISH = [
    {
        "file_path": str(REVIEW_DIR / "cut_01_caseoh_crash_rage_1080p.mp4"),
        "title": "CaseOh CANNOT Drive in GTA 6 💀 (HE RAGED)",
        "description": "CaseOh tries driving a truck in GTA 6 and immediately breaks the physics engine! 💀\nWatch until the end for the insane car flip rage.\n\n#GTA6 #CaseOh #Shorts #Gaming #FunnyMoments #GTAV",
        "tags": ["caseoh", "gta 6", "gta 6 gameplay", "caseoh funny moments", "gta 6 fails", "shorts", "gaming"],
        "streamer": "CaseOh",
        "hook_text": "HE DESTROYED HIS CAR! 💀",
    },
    {
        "file_path": str(REVIEW_DIR / "cut_02_gta6_insane_physics_stunt_1080p.mp4"),
        "title": "When GTA 6 Physics BREAK Mid-Air 💀🚀 #Shorts",
        "description": "Fastest supercar hits an invisible barrier on the Vice City highway and launches 500 feet into the clouds!\n30 barrel rolls into a police helicopter explosion.\n\n#GTA6 #Shorts #Gaming #GTA6Fails #ViceCity #GTAOnline",
        "tags": ["gta 6", "gta 6 stunts", "gta 6 physics", "gta 6 gameplay", "gaming", "shorts", "vice city"],
        "streamer": "Typical Gamer",
        "hook_text": "500FT AIRTIME CRASH! 🏎️💨",
    },
    {
        "file_path": str(REVIEW_DIR / "cut_03_kai_cenat_5star_escape_1080p.mp4"),
        "title": "Kai Cenat ESCAPES 5-Star Police Roadblock 🚨💀 #Shorts",
        "description": "Kai Cenat gets 5 stars in GTA and smashes through a police barricade at 150 MPH!\nCar bursts into flames and he bails out right before the explosion.\n\n#KaiCenat #GTA6 #Shorts #Gaming #GTA5 #FunnyMoments",
        "tags": ["kai cenat", "gta 6", "kai cenat gta", "5 star wanted", "gaming", "shorts", "police chase"],
        "streamer": "Kai Cenat",
        "hook_text": "5-STAR POLICE BUST! 🚨",
    },
]

def upload_short_public(file_path: str, title: str, description: str, tags: list, token: str) -> str:
    """Executes direct resumable upload of public YouTube Short."""
    file_size = os.path.getsize(file_path)
    init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "20",  # Gaming
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

    # Upload video data in chunks or full binary
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
    print("=" * 75)
    print("🚀 PUBLISHING 3 APPROVED HIGH-QUALITY CUTS TO YOUTUBE (PUBLIC)")
    print("=" * 75)

    token = get_oauth_token()
    if not token:
        print("❌ FATAL: Could not obtain OAuth token from YouTube credentials.")
        sys.exit(1)

    thumb_gen = ThumbnailGenerator()
    store = StateStore()

    results = []

    for idx, cut in enumerate(CUTS_TO_PUBLISH, 1):
        f_path = cut["file_path"]
        title = cut["title"]
        desc = cut["description"]
        tags = cut["tags"]
        streamer = cut["streamer"]
        hook_text = cut["hook_text"]

        print(f"\n[{idx}/3] Uploading: {Path(f_path).name}")
        print(f"      Title: {title}")
        print(f"      Visibility: PUBLIC")

        try:
            vid_id = upload_short_public(f_path, title, desc, tags, token)
            short_url = f"https://www.youtube.com/shorts/{vid_id}"
            watch_url = f"https://www.youtube.com/watch?v={vid_id}"
            print(f"      ✅ VIDEO PUBLISHED: {short_url}")

            # Generate and upload custom thumbnail
            thumb_path = THUMBNAILS_DIR / f"thumb_pub_{vid_id}.jpg"
            try:
                thumb_gen.create_thumbnail(
                    video_path=f_path,
                    streamer_name=streamer,
                    title=title,
                    output_path=str(thumb_path),
                    hook_text=hook_text,
                    target_circle=(850, 400),
                    draw_arrow=True,
                )
                print(f"      🖼️ Created thumbnail: {thumb_path.name}")
                thumb_ok = thumb_gen.upload_to_youtube(vid_id, str(thumb_path), token)
                if thumb_ok:
                    print(f"      🎯 Thumbnail uploaded successfully to YouTube!")
                else:
                    print(f"      ⚠️ Thumbnail upload returned non-200")
            except Exception as te:
                print(f"      ⚠️ Thumbnail error: {te}")

            results.append({
                "video_id": vid_id,
                "short_url": short_url,
                "watch_url": watch_url,
                "title": title,
                "streamer": streamer,
                "status": "PUBLIC",
                "file_path": f_path,
            })

            # Small 2-second rate-limit spacing
            time.sleep(2.0)

        except Exception as e:
            print(f"      ❌ Upload failed: {e}")
            results.append({
                "file_path": f_path,
                "title": title,
                "error": str(e),
                "status": "FAILED",
            })

    # Save summary
    out_record = BASE_DIR / "storage" / "published_cuts_v2.json"
    with open(out_record, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 75)
    print("🎉 PUBLISHING RUN FINISHED")
    print("=" * 75)
    for r in results:
        if r.get("status") == "PUBLIC":
            print(f"  • {r['title']} -> {r['short_url']}")
        else:
            print(f"  • {r['title']} -> FAILED: {r.get('error')}")

if __name__ == "__main__":
    main()
