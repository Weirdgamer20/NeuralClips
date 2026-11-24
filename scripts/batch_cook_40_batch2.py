"""Batch Renderer for Batch 2 (40 High-Retention 2K Clips).
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.slices_40_batch2_manifest import SLICES_BATCH2

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
OUT_DIR = BASE_DIR / "storage" / "batch_40_part2"
THUMB_DIR = BASE_DIR / "storage" / "thumbnails_batch2"

OUT_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)

def render_clip(item, index, total):
    cid = item["id"]
    src_file = REVIEW_DIR / item["src"]
    out_file = OUT_DIR / f"{cid}_2k.mp4"
    thumb_file = THUMB_DIR / f"thumb_{cid}.jpg"

    if out_file.exists() and out_file.stat().st_size > 2_000_000:
        print(f"[{index}/{total}] Already exists: {out_file.name}", flush=True)
        return str(out_file)

    if not src_file.exists():
        print(f"[{index}/{total}] ❌ Source missing: {src_file.name}", flush=True)
        return None

    start_s = item["start"]
    dur_s = item["dur"]
    ctype = item["type"]

    if ctype == "1440p":
        vf = "crop=810:1440:875:0,scale=1080:1920:flags=lanczos+accurate_rnd,unsharp=5:5:0.6:5:5:0.3,setsar=1"
    else:
        vf = "crop=608:1080:656:0,scale=1080:1920:flags=lanczos+accurate_rnd,unsharp=5:5:0.6:5:5:0.3,setsar=1"

    af = "aresample=async=1000:min_hard_comp=0.010000,volume=1.2"

    cmd = [
        ffmpeg, "-y",
        "-ss", str(start_s),
        "-i", str(src_file),
        "-t", str(dur_s),
        "-vf", vf,
        "-map", "0:v",
        "-map", "0:a?",
        "-r", "60",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "16",
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

    print(f"[{index}/{total}] 🎬 Rendering: {out_file.name} (from {src_file.name} @ {start_s}s)...", flush=True)
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"[{index}/{total}] ❌ Render failed: {res.stderr[-300:]}", flush=True)
        return None

    try:
        generate_thumbnail(str(out_file), str(thumb_file), item["hook"], item["title"])
    except Exception as e:
        print(f"  ⚠️ Thumbnail warning: {e}", flush=True)

    print(f"[{index}/{total}] ✅ Complete: {out_file.name}", flush=True)
    return str(out_file)

def generate_thumbnail(video_path, out_thumb, hook_text, title):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, 8000)
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        return

    frame = cv2.resize(frame, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    pil_img = ImageEnhance.Contrast(pil_img).enhance(1.15)
    pil_img = ImageEnhance.Color(pil_img).enhance(1.2)
    draw = ImageDraw.Draw(pil_img)

    font_main = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 76)
    font_badge = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", 34)

    gradient = Image.new("RGBA", (1080, 420), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)
    for y in range(420):
        alpha = int(220 * (1 - (y / 420) ** 1.5))
        g_draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
    pil_img.paste(gradient, (0, 0), gradient)

    draw.rounded_rectangle([320, 60, 760, 115], radius=12, fill=(20, 20, 25), outline=(0, 240, 255), width=3)
    draw.text((360, 68), "GTA VI VICE CITY", fill=(255, 255, 255), font=font_badge)

    bbox = font_main.getbbox(hook_text)
    tw = bbox[2] - bbox[0]
    tx = (1080 - tw) // 2
    for dx in range(-6, 7):
        for dy in range(-6, 7):
            if dx*dx + dy*dy <= 36:
                draw.text((tx + dx, 160 + dy), hook_text, font=font_main, fill=(0, 0, 0))
    draw.text((tx, 160), hook_text, font=font_main, fill=(255, 230, 0))

    pil_img.save(out_thumb, "JPEG", quality=95)

def main():
    print("=" * 70, flush=True)
    print(f"🚀 STARTING BATCH 2 COOK FOR {len(SLICES_BATCH2)} 2K CLIPS", flush=True)
    print("=" * 70, flush=True)

    rendered = []
    total = len(SLICES_BATCH2)
    t0 = time.time()

    for idx, item in enumerate(SLICES_BATCH2, 1):
        res = render_clip(item, idx, total)
        if res:
            rendered.append(res)

    elapsed = time.time() - t0
    print("\n" + "=" * 70, flush=True)
    print(f"🎉 BATCH 2 COMPLETE: {len(rendered)}/{total} clips rendered in {elapsed:.1f}s ({elapsed/60:.1f}m)", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
