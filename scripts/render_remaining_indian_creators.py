import sys
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import imageio_ffmpeg

BASE_DIR = Path("d:/vidclip")
sys.path.insert(0, str(BASE_DIR))

from config.slices_indian_creators_manifest import SLICES_INDIAN_CREATORS

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
OUT_DIR = BASE_DIR / "storage" / "batch_indian_creators"
THUMB_DIR = BASE_DIR / "storage" / "thumbnails_indian"

OUT_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)

for idx, item in enumerate(SLICES_INDIAN_CREATORS, 1):
    cid = item["id"]
    out_file = OUT_DIR / f"{cid}_2k.mp4"
    thumb_file = THUMB_DIR / f"thumb_{cid}.jpg"
    src_file = REVIEW_DIR / item["src"]

    if out_file.exists() and out_file.stat().st_size > 2_000_000:
        print(f"[{idx}/{len(SLICES_INDIAN_CREATORS)}] Already rendered: {out_file.name}", flush=True)
        continue

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

    print(f"[{idx}/{len(SLICES_INDIAN_CREATORS)}] 🎬 Rendering: {cid}...", flush=True)
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Thumbnail
    raw_frame = THUMB_DIR / f"raw_{cid}.jpg"
    subprocess.run([
        ffmpeg, "-y", "-ss", str(min(3.0, dur_s / 2)),
        "-i", str(out_file), "-vframes", "1", "-q:v", "2", str(raw_frame)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    if raw_frame.exists():
        im = Image.open(raw_frame).convert("RGB")
        im = ImageEnhance.Color(im).enhance(1.3)
        im = ImageEnhance.Contrast(im).enhance(1.2)
        im = ImageEnhance.Brightness(im).enhance(1.05)
        draw = ImageDraw.Draw(im)
        W, H = im.size

        font_path = "C:/Windows/Fonts/impact.ttf"
        font_title = ImageFont.truetype(font_path, 80)
        font_badge = ImageFont.truetype(font_path, 46)

        tag = item.get("streamer_tag", "INDIAN GAMING")
        draw.rounded_rectangle([(40, 50), (40 + len(tag) * 28, 120)], radius=15, fill=(230, 0, 70))
        draw.text((60, 60), tag, font=font_badge, fill=(255, 255, 255))

        badge = item.get("badge", "VIRAL")
        bb = draw.textbbox((0, 0), badge, font=font_badge)
        bw = bb[2] - bb[0]
        draw.rounded_rectangle([(W - bw - 90, 50), (W - 40, 120)], radius=15, fill=(0, 220, 255))
        draw.text((W - bw - 65, 60), badge, font=font_badge, fill=(0, 0, 0))

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
        raw_frame.unlink()
        print(f"[{idx}/{len(SLICES_INDIAN_CREATORS)}] 🎯 Thumbnail complete: {thumb_file.name}", flush=True)

print("🎉 ALL 27 INDIAN CREATOR CLIPS RENDERED & READY!")
