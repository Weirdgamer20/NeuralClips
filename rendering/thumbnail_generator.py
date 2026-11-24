"""High-CTR Vertical 9:16 Thumbnail Generator for YouTube Shorts.

Generates ultra-engaging, razor-sharp, 1080x1920 vertical thumbnails tailored
specifically for YouTube Shorts mobile shelf, search, and browse feeds:
1. Native 9:16 (1080x1920) aspect ratio (no letterboxing, no side crops).
2. Top 58% (1080x1110) high-octane GTA 6 action & heist moments.
3. Electric cyan (#00F0FF) neon divider with GTA VI Vice City pill badge.
4. Bottom 42% (1080x802) crystal-clear streamer reaction facecam (Speed, CaseOh, Kai, Typical Gamer, xQc).
5. Massive, high-contrast Impact typography with 18px black shadow & outline (clean ASCII, zero tofu boxes).
6. Direct upload to YouTube Data API v3 (thumbnails.set) preserving native 1080x1920 shortsAspectRatio.
"""

import os
import io
import re
import urllib.request
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2
import numpy as np


class ThumbnailGenerator:
    """Generates high-converting, 1080x1920 vertical thumbnails for YouTube Shorts."""

    CANVAS_W = 1080
    CANVAS_H = 1920
    GAME_H = 1110
    DIVIDER_H = 8
    FACE_H = 802  # 1110 + 8 + 802 = 1920 exact

    def __init__(self):
        self.font_impact = "C:/Windows/Fonts/impact.ttf"
        self.font_ariblk = "C:/Windows/Fonts/ariblk.ttf"

    def clean_text_for_font(self, text: str) -> str:
        """Removes non-ASCII characters / emojis that cause tofu [] boxes in standard fonts."""
        # Replace common emojis with empty or punctuation
        cleaned = re.sub(r"[^\x00-\x7F]+", "", text).strip()
        # Clean up double punctuation
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def create_vertical_short_thumbnail(
        self,
        gameplay_frame: np.ndarray,
        streamer_frame: np.ndarray,
        hook_line1: str,
        hook_line2: str,
        output_path: str,
        badge_text: str = "GTA VI  VICE CITY"
    ) -> str:
        """Assembles a pristine 1080x1920 vertical Short thumbnail."""
        # 1. Gameplay image (Top)
        game_resized = cv2.resize(gameplay_frame, (self.CANVAS_W, self.GAME_H), interpolation=cv2.INTER_LANCZOS4)
        game_pil = Image.fromarray(cv2.cvtColor(game_resized, cv2.COLOR_BGR2RGB))
        game_pil = ImageEnhance.Color(game_pil).enhance(1.25)
        game_pil = ImageEnhance.Contrast(game_pil).enhance(1.15)

        # 2. Streamer image (Bottom)
        face_resized = cv2.resize(streamer_frame, (self.CANVAS_W, self.FACE_H), interpolation=cv2.INTER_LANCZOS4)
        face_pil = Image.fromarray(cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB))
        face_pil = ImageEnhance.Color(face_pil).enhance(1.15)
        face_pil = ImageEnhance.Contrast(face_pil).enhance(1.15)
        face_pil = ImageEnhance.Brightness(face_pil).enhance(1.08)

        # 3. Canvas assembly
        canvas = Image.new("RGB", (self.CANVAS_W, self.CANVAS_H), (0, 0, 0))
        canvas.paste(game_pil, (0, 0))
        canvas.paste(face_pil, (0, self.GAME_H + self.DIVIDER_H))

        draw = ImageDraw.Draw(canvas)

        # 4. Electric neon divider bar
        draw.rectangle([0, self.GAME_H, self.CANVAS_W, self.GAME_H + self.DIVIDER_H], fill=(0, 240, 255))

        # 5. Top pill badge
        badge_w, badge_h = 420, 64
        bx = (self.CANVAS_W - badge_w) // 2
        by = 50
        draw.rounded_rectangle(
            [bx, by, bx + badge_w, by + badge_h],
            radius=16,
            fill=(10, 10, 15, 230),
            outline=(0, 240, 255),
            width=3
        )
        badge_font = ImageFont.truetype(self.font_ariblk, 30)
        draw.text((bx + 40, by + 14), badge_text, font=badge_font, fill="#00F0FF")

        # 6. Big Bold Hook Typography
        font_large = ImageFont.truetype(self.font_impact, 125)

        def draw_centered_hook(y: int, text: str, fill_color: str):
            clean_t = self.clean_text_for_font(text).upper()
            bbox = draw.textbbox((0, 0), clean_t, font=font_large)
            tw = bbox[2] - bbox[0]
            tx = (self.CANVAS_W - tw) // 2
            # 18px deep black drop shadow
            draw.text((tx + 6, y + 8), clean_t, font=font_large, fill="#000000", stroke_width=18, stroke_fill="#000000")
            # Foreground text with 12px black outline
            draw.text((tx, y), clean_t, font=font_large, fill=fill_color, stroke_width=12, stroke_fill="#000000")

        draw_centered_hook(160, hook_line1, "#FFE600")  # Neon Yellow
        draw_centered_hook(295, hook_line2, "#FFFFFF")  # Crisp White

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        canvas.save(output_path, "JPEG", quality=95, optimize=True)
        return output_path

    def upload_to_youtube(self, video_id: str, image_path: str, token: str) -> bool:
        """Uploads vertical 1080x1920 thumbnail to YouTube Data API v3."""
        if not os.path.exists(image_path):
            return False

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        url = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}"
        req = urllib.request.Request(url, data=image_bytes, method="POST")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "image/jpeg")

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return resp.status in (200, 201)
        except Exception as e:
            print(f"❌ Failed to upload thumbnail for {video_id}: {e}")
            return False
