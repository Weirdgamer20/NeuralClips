"""Generates high-CTR 1080x1920 cinema-grade vertical thumbnails for the 4 approved 2K master cuts.
"""

import sys, os
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
THUMB_DIR = BASE_DIR / "storage" / "thumbnails"
THUMB_DIR.mkdir(parents=True, exist_ok=True)

CUTS = [
    {
        "id": "cut_01",
        "file": REVIEW_DIR / "cut_01_supercar_pursuit_1440p60.mp4",
        "timestamp_sec": 15.0,
        "line1": "160 MPH POLICE CHASE",
        "line2": "IMPOSSIBLE ESCAPE!",
        "badge": "GTA 6 SUPERCAR PURSUIT",
        "color": (255, 230, 0),  # Electric yellow
    },
    {
        "id": "cut_02",
        "file": REVIEW_DIR / "cut_02_supercar_bridge_escape_1440p60.mp4",
        "timestamp_sec": 24.0,
        "line1": "ROADBLOCK SMASH",
        "line2": "TOTAL DESTRUCTION!",
        "badge": "GTA 6 5-STAR WANTED",
        "color": (0, 240, 255),  # Electric cyan
    },
    {
        "id": "cut_03",
        "file": REVIEW_DIR / "cut_03_supercar_traffic_weave_1440p60.mp4",
        "timestamp_sec": 24.5,
        "line1": "NEAR-MISS TRAFFIC SLALOM",
        "line2": "INSANE COP PILEUP!",
        "badge": "GTA 6 HIGHWAY MADNESS",
        "color": (255, 100, 50),  # Neon orange
    },
    {
        "id": "cut_04",
        "file": REVIEW_DIR / "cut_04_tank_6star_rampage_1440p60.mp4",
        "timestamp_sec": 14.5,
        "line1": "CAN A TANK SURVIVE",
        "line2": "6-STAR MILITARY CHASE?!",
        "badge": "GTA 6 TANK RAMPAGE",
        "color": (255, 220, 0),  # Bold yellow
    },
]

def make_thumbnail(info):
    cap = cv2.VideoCapture(str(info["file"]))
    cap.set(cv2.CAP_PROP_POS_MSEC, info["timestamp_sec"] * 1000)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print(f"Failed to read frame for {info['id']}")
        return

    # Resize to exact 1080x1920
    frame = cv2.resize(frame, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)

    # Convert to PIL
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(1.15)
    enhancer = ImageEnhance.Color(pil_img)
    pil_img = enhancer.enhance(1.2)

    draw = ImageDraw.Draw(pil_img)

    # Fonts
    font_path = "C:/Windows/Fonts/impact.ttf"
    font_main = ImageFont.truetype(font_path, 80)
    font_badge = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", 34)

    # Top gradient shadow for text readability
    gradient = Image.new("RGBA", (1080, 480), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)
    for y in range(480):
        alpha = int(220 * (1 - (y / 480) ** 1.5))
        g_draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
    pil_img.paste(gradient, (0, 0), gradient)

    # Draw badge pill at top
    badge_text = info["badge"]
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 40
    bh = bbox[3] - bbox[1] + 20
    bx = (1080 - bw) // 2
    by = 70
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(20, 20, 25), outline=info["color"], width=3)
    draw.text((bx + 20, by + 8), badge_text, fill=(255, 255, 255), font=font_badge)

    # Helper for outlined text
    def draw_text_stroke(text, y, color):
        bbox = font_main.getbbox(text)
        tw = bbox[2] - bbox[0]
        tx = (1080 - tw) // 2
        # Outline
        for dx in range(-6, 7):
            for dy in range(-6, 7):
                if dx*dx + dy*dy <= 36:
                    draw.text((tx + dx, y + dy), text, font=font_main, fill=(0, 0, 0))
        # Fill
        draw.text((tx, y), text, font=font_main, fill=color)

    draw_text_stroke(info["line1"], 170, (255, 255, 255))
    draw_text_stroke(info["line2"], 265, info["color"])

    out_file = THUMB_DIR / f"thumb_{info['id']}_approved.jpg"
    pil_img.save(out_file, "JPEG", quality=95)
    print(f"✅ Generated cinema thumbnail: {out_file.name}")

    # Copy to artifact dir for conversation link
    art_file = Path(f"C:/Users/thega/.gemini/antigravity/brain/cc9214c0-7f61-456a-b5aa-8cae3dbac8e4/thumb_{info['id']}_approved.jpg")
    pil_img.save(art_file, "JPEG", quality=92)

for c in CUTS:
    make_thumbnail(c)
print("All thumbnails ready!")
