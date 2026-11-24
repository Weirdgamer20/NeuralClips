"""Autonomous Pipeline: Renders and Publishes Indian Creators Gaming Clips (Techno Gamerz, CarryMinati, Triggered Insaan).

Uploads as many videos as YouTube daily API quota allows.
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import imageio_ffmpeg

BASE_DIR = Path("d:/vidclip")
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

from config.slices_indian_creators_manifest import SLICES_INDIAN_CREATORS
from sources.youtube_source import get_oauth_token
from rendering.thumbnail_generator import ThumbnailGenerator
from scripts.publish_approved_2k_cuts import upload_short_public

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
OUT_DIR = BASE_DIR / "storage" / "batch_indian_creators"
THUMB_DIR = BASE_DIR / "storage" / "thumbnails_indian"
LOG_FILE = BASE_DIR / "storage" / "indian_creators_upload_progress.json"

OUT_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(msg, flush=True)

def render_clip(item, idx, total):
    cid = item["id"]
    src_file = REVIEW_DIR / item["src"]
    out_file = OUT_DIR / f"{cid}_2k.mp4"
    thumb_file = THUMB_DIR / f"thumb_{cid}.jpg"

    if out_file.exists() and out_file.stat().st_size > 2_000_000:
        log(f"[{idx}/{total}] Video already rendered: {out_file.name}")
        return str(out_file), str(thumb_file)

    if not src_file.exists():
        log(f"[{idx}/{total}] ❌ Source missing: {src_file.name}")
        return None, None

    start_s = item["start"]
    dur_s = item["dur"]
    crop_top = item["crop_top"]
    crop_bot = item["crop_bot"]

    filter_complex = f"[0:v]{crop_top}[top];[0:v]{crop_bot}[bot];[top][bot]vstack[v];[v]setsar=1,unsharp=5:5:0.5:5:5:0.2[vout]"
    af = "aresample=async=1000:min_hard_comp=0.010000,volume=1.25"

    cmd = [
        ffmpeg, "-y",
        "-ss", str(start_s),
        "-i", str(src_file),
        "-t", str(dur_s),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "0:a?",
        "-r", "60",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-b:v", "14M",
        "-maxrate", "22M",
        "-bufsize", "45M",
        "-c:a", "aac",
        "-b:a", "256k",
        "-af", af,
        "-avoid_negative_ts", "make_zero",
        "-async", "1",
        str(out_file)
    ]

    log(f"[{idx}/{total}] 🎬 Rendering {item['creator']} clip: {cid} (from {src_file.name} @ {start_s}s)...")
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        log(f"[{idx}/{total}] ❌ Render error on {cid}: {res.stderr[-400:]}")
        return None, None

    # Generate custom thumbnail
    try:
        raw_frame = THUMB_DIR / f"raw_{cid}.jpg"
        subprocess.run([
            ffmpeg, "-y",
            "-ss", str(min(3.0, dur_s / 2)),
            "-i", str(out_file),
            "-vframes", "1",
            "-q:v", "2",
            str(raw_frame)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        if raw_frame.exists():
            im = Image.open(raw_frame).convert("RGB")
            im = ImageEnhance.Color(im).enhance(1.3)
            im = ImageEnhance.Contrast(im).enhance(1.2)
            im = ImageEnhance.Brightness(im).enhance(1.05)

            draw = ImageDraw.Draw(im)
            W, H = im.size

            font_path = "C:/Windows/Fonts/impact.ttf"
            if not os.path.exists(font_path):
                font_path = "C:/Windows/Fonts/arialbd.ttf"
            font_title = ImageFont.truetype(font_path, 80)
            font_badge = ImageFont.truetype(font_path, 46)

            # Draw Streamer Pill at top
            tag = item.get("streamer_tag", "INDIAN GAMING")
            draw.rounded_rectangle([(40, 50), (40 + len(tag) * 28, 120)], radius=15, fill=(230, 0, 70))
            draw.text((60, 60), tag, font=font_badge, fill=(255, 255, 255))

            # Draw Action Badge
            badge = item.get("badge", "VIRAL")
            bb = draw.textbbox((0, 0), badge, font=font_badge)
            bw = bb[2] - bb[0]
            draw.rounded_rectangle([(W - bw - 90, 50), (W - 40, 120)], radius=15, fill=(0, 220, 255))
            draw.text((W - bw - 65, 60), badge, font=font_badge, fill=(0, 0, 0))

            # Headline Text at bottom
            headline = item.get("title", "").split(" #")[0]
            words = headline.split()
            lines = []
            cur = ""
            for w in words:
                if len(cur + " " + w) > 18:
                    lines.append(cur)
                    cur = w
                else:
                    cur = (cur + " " + w).strip()
            if cur:
                lines.append(cur)

            y_pos = H - 340
            for line in lines[-2:]:
                for ox in [-3, 0, 3]:
                    for oy in [-3, 0, 3]:
                        draw.text((60 + ox, y_pos + oy), line, font=font_title, fill=(0, 0, 0))
                draw.text((60, y_pos), line, font=font_title, fill=(255, 235, 0))
                y_pos += 95

            im.save(thumb_file, "JPEG", quality=95)
            if raw_frame.exists():
                raw_frame.unlink()

        log(f"[{idx}/{total}] 🎯 Thumbnail generated: {thumb_file.name}")
    except Exception as e:
        log(f"[{idx}/{total}] ⚠️ Thumbnail error: {e}")

    return str(out_file), str(thumb_file)

def main():
    log("=" * 75)
    log("🚀 AUTONOMOUS INDIAN CREATORS GAMING PIPELINE STARTED")
    log("Creators: Techno Gamerz | CarryMinati | Triggered Insaan")
    log(f"Total target clips: {len(SLICES_INDIAN_CREATORS)}")
    log("=" * 75)

    results = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                results = json.load(f)
        except Exception:
            results = []

    published_ids = {r["id"] for r in results}
    log(f"Already published from previous runs: {len(published_ids)}")

    token = get_oauth_token()
    thumb_gen = ThumbnailGenerator()

    for idx, item in enumerate(SLICES_INDIAN_CREATORS, 1):
        cid = item["id"]
        if cid in published_ids:
            log(f"[{idx}/{len(SLICES_INDIAN_CREATORS)}] Already published: {cid}, skipping.")
            continue

        # Render clip
        video_path, thumb_path = render_clip(item, idx, len(SLICES_INDIAN_CREATORS))
        if not video_path:
            continue

        title = item["title"]
        creator = item["creator"]
        desc = (
            f"{title}\n\n"
            f"🔥 Watch {creator} in this insane GTA 5 high-retention moment!\n"
            f"Subscribe for more daily Indian gaming highlights and viral clips.\n\n"
            f"#GTA5 #{creator.replace(' ', '')} #Shorts #IndianGaming #GamingHighlights"
        )
        tags = [
            creator.lower(), "gta 5", "shorts", "gaming", "indian gaming",
            "gta 5 funny moments", "gta 5 police chase", "techno gamerz",
            "carryminati", "triggered insaan"
        ]

        log(f"\n[{idx}/{len(SLICES_INDIAN_CREATORS)}] 📤 Uploading to YouTube: {title}")
        try:
            vid_id = upload_short_public(video_path, title, desc, tags, token)
            short_url = f"https://www.youtube.com/shorts/{vid_id}"
            log(f"[{idx}/{len(SLICES_INDIAN_CREATORS)}] ✅ PUBLISHED: {short_url}")

            # Upload thumbnail
            if Path(thumb_path).exists():
                ok = thumb_gen.upload_to_youtube(vid_id, thumb_path, token)
                if ok:
                    log(f"[{idx}/{len(SLICES_INDIAN_CREATORS)}] 🎯 Thumbnail uploaded to YouTube!")

            results.append({
                "id": cid,
                "creator": creator,
                "video_id": vid_id,
                "url": short_url,
                "title": title,
                "published_at": datetime.now().isoformat()
            })
            published_ids.add(cid)

            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)

            time.sleep(3.0)

        except Exception as e:
            err_str = str(e)
            log(f"[{idx}/{len(SLICES_INDIAN_CREATORS)}] ⚠️ Upload error: {err_str}")
            if "uploadLimitExceeded" in err_str:
                log("🛑 Daily YouTube API upload limit reached! Quota exhausted for today.")
                log("All remaining clips are preserved on disk and will resume on next quota reset.")
                break
            else:
                time.sleep(5.0)

    log("\n" + "=" * 75)
    log(f"🎉 PIPELINE SESSION COMPLETE! Total Indian creator clips published: {len(results)}")
    log("=" * 75)

if __name__ == "__main__":
    main()
