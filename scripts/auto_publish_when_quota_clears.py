"""Auto-Publish Watcher: Monitors YouTube rolling 24h upload quota and publishes the 4 approved 2K cuts as public.
"""

import json
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from scripts.publish_approved_2k_cuts import CUTS_TO_PUBLISH, upload_short_public
from sources.youtube_source import get_oauth_token
from rendering.thumbnail_generator import ThumbnailGenerator

def check_and_publish():
    token = get_oauth_token()
    if not token:
        print("[WATCHER] Waiting for valid OAuth token...")
        return False

    thumb_gen = ThumbnailGenerator()
    published_any = False
    all_done = True

    for cut in CUTS_TO_PUBLISH:
        if cut.get("published"):
            continue

        f_path = cut["file_path"]
        t_path = cut["thumb_path"]
        title = cut["title"]
        desc = cut["description"]
        tags = cut["tags"]

        try:
            print(f"[WATCHER] Attempting upload for: {title}...")
            vid_id = upload_short_public(f_path, title, desc, tags, token)
            short_url = f"https://www.youtube.com/shorts/{vid_id}"
            print(f"🎉 [WATCHER] Successfully published: {short_url}")
            cut["published"] = True
            published_any = True

            # Set thumbnail
            if os.path.exists(t_path):
                thumb_gen.upload_to_youtube(vid_id, t_path, token)
                print(f"🎯 [WATCHER] Uploaded custom thumbnail for {vid_id}")
        except Exception as e:
            all_done = False
            if "uploadLimitExceeded" in str(e):
                print(f"[WATCHER] Quota still locked by YouTube (uploadLimitExceeded). Rolling window clearing...")
                break
            else:
                print(f"[WATCHER] Error: {e}")

    return all_done

if __name__ == "__main__":
    check_and_publish()
