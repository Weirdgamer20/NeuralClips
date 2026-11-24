"""Renders 3 pristine, full 1080x1920 60FPS vertical Short cuts for user review.

DO NOT UPLOAD TO YOUTUBE.
Only renders local MP4s, keyframe snapshots, and native 9:16 vertical thumbnails.
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path("d:/vidclip")
sys.path.insert(0, str(BASE_DIR))

REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
FFMPEG = str(BASE_DIR / ".venv" / "Scripts" / "ffmpeg.exe")


def render_cut(
    input_video: str,
    output_mp4: str,
    duration: float,
    fc_crop: dict,
    gp_crop: dict,
    hook_title: str
):
    """Executes FFmpeg split-screen render in 1080x1920 60FPS."""
    # Top 60% = 1080x1148, Divider = 1080x8, Bottom 40% = 1080x764
    cw, ch = 1080, 1920
    gp_h = 1148
    fc_h = 764
    div_h = 8

    # Filtergraph
    # 1. Facecam crop (from input 0)
    fc_filter = (
        f"[0:v]crop={fc_crop['w']}:{fc_crop['h']}:{fc_crop['x']}:{fc_crop['y']},"
        f"scale={cw}:{fc_h}:force_original_aspect_ratio=increase,"
        f"crop={cw}:{fc_h},"
        f"eq=contrast=1.12:brightness=0.04:saturation=1.18[facecam];"
    )

    # 2. Gameplay crop (from input 0)
    gp_filter = (
        f"[0:v]crop={gp_crop['w']}:{gp_crop['h']}:{gp_crop['x']}:{gp_crop['y']},"
        f"scale={cw}:{gp_h}:force_original_aspect_ratio=increase,"
        f"crop={cw}:{gp_h},"
        f"eq=contrast=1.14:brightness=0.02:saturation=1.22[gameplay];"
    )

    # 3. Stack with divider
    div_filter = f"color=c=0x00F0FF:s={cw}x{div_h}:d={duration}[div];"
    stack_filter = f"[gameplay][div][facecam]vstack=inputs=3[v_stacked];"

    # 4. Clean bold title hook overlay
    drawtext = (
        f"[v_stacked]drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        f"text='{hook_title}':fontsize=72:fontcolor=0xFFE600:"
        f"borderw=8:bordercolor=black:x=(w-text_w)/2:y=65[v_out]"
    )

    filter_complex = fc_filter + gp_filter + div_filter + stack_filter + drawtext

    cmd = [
        FFMPEG, "-y",
        "-t", str(duration),
        "-i", input_video,
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        output_mp4
    ]

    print(f"🎬 Rendering: {Path(output_mp4).name}...")
    subprocess.run(cmd, check=True)
    print(f"✅ Rendered successfully: {output_mp4} ({os.path.getsize(output_mp4) // 1024} KB)")


def main():
    print("=" * 70)
    print("🔥 RENDERING 3 HIGH-QUALITY REVIEW CUTS (NO UPLOAD - FOR APPROVAL)")
    print("=" * 70)

    # CUT 1: IShowSpeed - Fleeca Bank Mission
    # Input: 1920x1080. Speed facecam: x: 0, y: 410, w: 390, h: 260. Gameplay: x: 380, y: 0, w: 1280, h: 1080
    c1_in = str(REVIEW_DIR / "raw_speed_action_3420.mp4.webm")
    c1_out = str(REVIEW_DIR / "cut_01_speed_bank_heist_1080p.mp4")
    render_cut(
        input_video=c1_in,
        output_mp4=c1_out,
        duration=25.0,
        fc_crop={"x": 0, "y": 410, "w": 390, "h": 260},
        gp_crop={"x": 380, "y": 0, "w": 1280, "h": 1080},
        hook_title="SPEED FLEECA BANK HEIST"
    )

    # CUT 2: Typical Gamer - Night Crosstown Drive
    # Input: 1920x1080. TG facecam: x: 10, y: 390, w: 430, h: 280. Gameplay: x: 340, y: 0, w: 1260, h: 1080
    c2_in = str(REVIEW_DIR / "raw_typical_supercar_2220.mp4.webm")
    c2_out = str(REVIEW_DIR / "cut_02_typical_night_chase_1080p.mp4")
    render_cut(
        input_video=c2_in,
        output_mp4=c2_out,
        duration=25.0,
        fc_crop={"x": 10, "y": 390, "w": 430, "h": 280},
        gp_crop={"x": 340, "y": 0, "w": 1260, "h": 1080},
        hook_title="FASTEST SUPERCAR IN GTA 6"
    )

    # CUT 3: Mythpat - Live Broadcast Vice City Tower
    # Input: 1920x1080. Mythpat facecam: x: 1450, y: 130, w: 460, h: 320. Gameplay: x: 100, y: 0, w: 1280, h: 1080
    c3_in = str(REVIEW_DIR / "raw_mythpat_live.mp4")
    c3_out = str(REVIEW_DIR / "cut_03_mythpat_live_tower_1080p.mp4")
    render_cut(
        input_video=c3_in,
        output_mp4=c3_out,
        duration=22.0,
        fc_crop={"x": 1450, "y": 130, "w": 460, "h": 320},
        gp_crop={"x": 100, "y": 0, "w": 1280, "h": 1080},
        hook_title="MYTHPAT EXPLORING GTA 6"
    )

    print("\n🎉 ALL 3 CUTS COOKED AT 1080x1920 60FPS! ZERO UPLOADS PERFORMED.")


if __name__ == "__main__":
    main()
