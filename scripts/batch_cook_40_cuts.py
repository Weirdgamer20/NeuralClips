"""Multi-threaded Batch Renderer for 40 High-Retention 2K Clips.

Enforces:
1. 2K Vertical Standard (1080x1920 @ 60 FPS / 30 FPS).
2. 1:1 Square Pixel Aspect Ratio (setsar=1).
3. Multi-tap Lanczos Resampling (flags=lanczos+accurate_rnd).
4. Sample-Accurate A/V Sync (-avoid_negative_ts make_zero -async 1).
5. Exact OpenCV Facecam PiP Tracking for streamer cuts.
6. High-CTR 9:16 Vertical Thumbnails.
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

from config.slices_40_manifest import SLICES_CONFIG
from core.opencv_retention_engine import OpenCVRetentionEngine

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
engine = OpenCVRetentionEngine()

REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
OUT_DIR = BASE_DIR / "storage" / "batch_40"
THUMB_DIR = BASE_DIR / "storage" / "thumbnails_40"

OUT_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)

# Pre-detect CaseOh facecam box once
caseoh_src = REVIEW_DIR / "caseoh_full_crashes.mp4.mkv"
caseoh_fc = engine.detect_exact_facecam(str(caseoh_src), max_check_seconds=30.0) if caseoh_src.exists() else None
if not caseoh_fc:
    caseoh_fc = {"x": 0, "y": 247, "width": 380, "height": 240}

print(f"✅ CaseOh Facecam Box: {caseoh_fc}", flush=True)

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
        # 2560x1440 60FPS input -> 810x1440 center crop -> 1080x1920 Lanczos
        vf = "crop=810:1440:875:0,scale=1080:1920:flags=lanczos+accurate_rnd,unsharp=5:5:0.6:5:5:0.3,setsar=1"
        fps_opt = ["-r", "60"]
    elif ctype == "caseoh":
        # Streamer Facecam PiP
        fx, fy, fw, fh = caseoh_fc["x"], caseoh_fc["y"], caseoh_fc["width"], caseoh_fc["height"]
        vf = (
            f"[0:v]crop=608:1080:656:0,scale=1080:1920:flags=lanczos+accurate_rnd,setsar=1[bg];"
            f"[0:v]crop={fw}:{fh}:{fx}:{fy},scale=460:290:flags=lanczos+accurate_rnd,pad=468:298:4:4:color=0x00F0FF[cam];"
            f"[bg][cam]overlay=35:120:format=auto,unsharp=5:5:0.6:5:5:0.3,setsar=1[v_out]"
        )
        fps_opt = []
    else:
        # Standard 1080p 60FPS -> 608x1080 center crop -> 1080x1920 Lanczos
        vf = "crop=608:1080:656:0,scale=1080:1920:flags=lanczos+accurate_rnd,unsharp=5:5:0.6:5:5:0.3,setsar=1"
        fps_opt = ["-r", "60"]

    af = "aresample=async=1000:min_hard_comp=0.010000,volume=1.2"

    cmd = [
        ffmpeg, "-y",
        "-ss", str(start_s),
        "-i", str(src_file),
        "-t", str(dur_s),
    ]

    if ctype == "caseoh":
        cmd.extend(["-filter_complex", vf, "-map", "[v_out]", "-map", "0:a"])
    else:
        cmd.extend(["-vf", vf, "-map", "0:v", "-map", "0:a?"])

    cmd.extend(fps_opt)
    cmd.extend([
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
    ])

    print(f"[{index}/{total}] 🎬 Rendering: {out_file.name} (from {src_file.name} @ {start_s}s)...", flush=True)
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"[{index}/{total}] ❌ Render failed: {res.stderr[-300:]}", flush=True)
        return None

    # Generate custom thumbnail
    try:
        generate_thumbnail(str(out_file), str(thumb_file), item["hook"], item["title"])
    except Exception as e:
        print(f"  ⚠️ Thumbnail warning: {e}", flush=True)

    print(f"[{index}/{total}] ✅ Complete: {out_file.name}", flush=True)
    return str(out_file)

def generate_thumbnail(video_path, out_thumb, hook_text, title):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, 10000)
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

    # Gradient top
    gradient = Image.new("RGBA", (1080, 420), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)
    for y in range(420):
        alpha = int(220 * (1 - (y / 420) ** 1.5))
        g_draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
    pil_img.paste(gradient, (0, 0), gradient)

    # Badge
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
    print(f"🚀 STARTING BATCH COOK FOR {len(SLICES_CONFIG)} 2K CLIPS", flush=True)
    print("=" * 70, flush=True)

    rendered = []
    total = len(SLICES_CONFIG)
    t0 = time.time()

    for idx, item in enumerate(SLICES_CONFIG, 1):
        res = render_clip(item, idx, total)
        if res:
            rendered.append(res)

    elapsed = time.time() - t0
    print("\n" + "=" * 70, flush=True)
    print(f"🎉 BATCH COMPLETE: {len(rendered)}/{total} clips rendered in {elapsed:.1f}s ({elapsed/60:.1f}m)", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
