import os
import sys
import json
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.env_loader import load_env
load_env()

from core.state_store import StateStore
from rendering.clip_extractor import ClipExtractor
from rendering.crop_detector import CropDetector
from publishing.youtube_publisher import YouTubePublisher

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("reprocess_and_upload")

def main():
    store = StateStore()
    extractor = ClipExtractor()
    detector = CropDetector()
    publisher = YouTubePublisher()

    clips_to_process = [
        {
            "num": 1,
            "channel": "IShowSpeed",
            "pub_id": "cde6369e-acc1-477d-8bbe-165111a0827b",
            "clip_id": "clip_hl_src_NC-REALTIME-GTA6-20261120-0717_1_1795139276",
            "hl_id": "hl_src_NC-REALTIME-GTA6-20261120-0717_1_1795139276",
            "raw_video": os.path.join(BASE_DIR, "storage", "raw", "live_src_NC-REALTIME-GTA6-20261120-0717_1.mp4"),
            "category": "multi_kill",
            "score": 85,
        },
        {
            "num": 2,
            "channel": "TheBurntPeanut",
            "pub_id": "26badd5e-b27e-4b6d-a2e8-5a4874fffce5",
            "clip_id": "clip_hl_src_NC-REALTIME-GTA6-20261120-0717_2_1795139325",
            "hl_id": "hl_src_NC-REALTIME-GTA6-20261120-0717_2_1795139325",
            "raw_video": os.path.join(BASE_DIR, "storage", "raw", "live_src_NC-REALTIME-GTA6-20261120-0717_2.mp4"),
            "category": "unexpected_victory",
            "score": 92,
        },
        {
            "num": 3,
            "channel": "Kai Cenat Live",
            "pub_id": "32a98750-1f69-45e2-9fd3-fec1da0ee06d",
            "clip_id": "clip_hl_src_NC-REALTIME-GTA6-20261120-0717_3_1795139357",
            "hl_id": "hl_src_NC-REALTIME-GTA6-20261120-0717_3_1795139357",
            "raw_video": os.path.join(BASE_DIR, "storage", "raw", "live_src_NC-REALTIME-GTA6-20261120-0717_3.mp4"),
            "category": "clutch",
            "score": 89,
        },
        {
            "num": 4,
            "channel": "LOUD Coringa",
            "pub_id": "ea6d4a11-ba59-434f-b7d3-b92e1871db11",
            "clip_id": "clip_hl_src_NC-REALTIME-GTA6-20261120-0717_4_1795139402",
            "hl_id": "hl_src_NC-REALTIME-GTA6-20261120-0717_4_1795139402",
            "raw_video": os.path.join(BASE_DIR, "storage", "raw", "live_src_NC-REALTIME-GTA6-20261120-0717_4.mp4"),
            "category": "multi_kill",
            "score": 85,
        },
        {
            "num": 5,
            "channel": "Typical Gamer",
            "pub_id": "5b897f3c-2d0a-4e78-9e55-5dd592958d63",
            "clip_id": "clip_hl_src_NC-REALTIME-GTA6-20261120-0717_5_1795139445",
            "hl_id": "hl_src_NC-REALTIME-GTA6-20261120-0717_5_1795139445",
            "raw_video": os.path.join(BASE_DIR, "storage", "raw", "live_src_NC-REALTIME-GTA6-20261120-0717_5.mp4"),
            "category": "multi_kill",
            "score": 85,
        },
    ]

    results = []

    for item in clips_to_process:
        logger.info(f"--- Re-rendering clip for [{item['channel']}] (Gameplay TOP, Facecam BOTTOM) ---")
        crop_name = item["channel"].lower().replace(" ", "_")
        hl_dict = {
            "highlight_id": item["hl_id"],
            "source_id": item["hl_id"].replace("hl_", "").split("_")[0],
            "start_timestamp": 0.0,
            "end_timestamp": 30.0,
            "duration": 30.0,
            "category": item["category"],
            "score": item["score"],
            "transcript": "INSANE GTA 6 PLAY",
            "source_crop_profile": crop_name,
        }

        # Render clip with gameplay on top, facecam on bottom
        render_res = extractor.produce_clip(hl_dict, source_media_path=item["raw_video"])
        clip_path = render_res.get("file_path")
        logger.info(f"Rendered: {clip_path} (size: {os.path.getsize(clip_path) if clip_path and os.path.exists(clip_path) else 0} bytes)")

        # Upload to YouTube
        pubs = store.get_pending_publications("YOUTUBE", limit=100)
        target_pub = next((p for p in pubs if p["pub_id"] == item["pub_id"]), None)
        if not target_pub:
            # fetch direct from DB
            with store._get_conn() as conn:
                r = conn.execute("SELECT p.*, c.file_path, c.duration, c.validated FROM youtube_publications p JOIN rendered_clips c ON p.clip_id = c.clip_id WHERE p.pub_id = ?", (item["pub_id"],)).fetchone()
                if r:
                    target_pub = dict(r)

        upload_ok = False
        upload_msg = "No publication found"
        yt_url = None
        if target_pub:
            logger.info(f"Uploading to YouTube: Title='{target_pub['title']}'...")
            upload_ok, upload_msg, yt_url = publisher.publish_short(target_pub)
            logger.info(f"Upload outcome: ok={upload_ok}, url={yt_url}, msg={upload_msg}")

        results.append({
            "channel": item["channel"],
            "clip_id": item["clip_id"],
            "file_path": clip_path,
            "upload_ok": upload_ok,
            "yt_url": yt_url,
            "message": upload_msg
        })

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
