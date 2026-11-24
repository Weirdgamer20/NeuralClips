"""Renders 3 truly high-quality, perfectly synced, high-energy Short cuts for user review.

DO NOT UPLOAD TO YOUTUBE.
Only renders local MP4s, preview snapshots, and inspection metadata.
"""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path("d:/vidclip")
REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
REVIEW_DIR.mkdir(parents=True, exist_ok=True)
FFMPEG = str(BASE_DIR / ".venv" / "Scripts" / "ffmpeg.exe")

def render_streamer_cut(
    input_video: str,
    output_mp4: str,
    start_sec: float,
    duration: float,
    fc_crop: dict,
    gp_crop: dict,
    hook_title: str
):
    """Renders 1080x1920 60FPS vertical Short with perfect audio-video sync."""
    cw, ch = 1080, 1920
    gp_h = 1180
    fc_h = 734
    div_h = 6

    # Video filtergraph:
    # 1. Gameplay crop (top 62%)
    gp_filter = (
        f"[0:v]crop={gp_crop['w']}:{gp_crop['h']}:{gp_crop['x']}:{gp_crop['y']},"
        f"scale={cw}:{gp_h}:force_original_aspect_ratio=increase,"
        f"crop={cw}:{gp_h},"
        f"eq=contrast=1.08:brightness=0.02:saturation=1.18[gameplay];"
    )

    # 2. Facecam crop (bottom 38%)
    fc_filter = (
        f"[0:v]crop={fc_crop['w']}:{fc_crop['h']}:{fc_crop['x']}:{fc_crop['y']},"
        f"scale={cw}:{fc_h}:force_original_aspect_ratio=increase,"
        f"crop={cw}:{fc_h},"
        f"eq=contrast=1.06:brightness=0.02:saturation=1.12[facecam];"
    )

    # 3. Glowing neon divider
    div_filter = f"color=c=0x00F0FF:s={cw}x{div_h}:d={duration}[div];"

    # 4. Vertical stack
    stack = f"[gameplay][div][facecam]vstack=inputs=3[stacked];"

    # 5. Clean, professional hook header badge (dark pill background + bold typography)
    # Box header: y=70, font size 64
    header = (
        f"[stacked]drawbox=x=40:y=60:w=1000:h=100:color=black@0.65:t=fill,"
        f"drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':text='{hook_title}':"
        f"fontsize=62:fontcolor=0xFFE600:borderw=5:bordercolor=black:"
        f"x=(w-text_w)/2:y=76[v_out];"
    )

    # Audio filter: STRICT PTS RESET AND ASYNC RESAMPLE TO ZERO OFFSET
    audio_filter = f"[0:a]aresample=async=1000:first_pts=0,asetpts=PTS-STARTPTS[a_out]"

    filter_complex = gp_filter + fc_filter + div_filter + stack + header + audio_filter

    cmd = [
        FFMPEG, "-y",
        "-ss", str(start_sec),
        "-t", str(duration),
        "-avoid_negative_ts", "make_zero",
        "-i", input_video,
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        output_mp4
    ]

    print(f"\n🎬 Rendering streamer cut: {Path(output_mp4).name}...")
    subprocess.run(cmd, check=True)
    print(f"✅ Rendered successfully: {output_mp4} ({os.path.getsize(output_mp4) // 1024} KB)")


def render_fullscreen_gameplay_cut(
    input_video: str,
    output_mp4: str,
    start_sec: float,
    duration: float,
    hook_title: str
):
    """Renders 1080x1920 60FPS fullscreen vertical gameplay cut with perfect audio sync."""
    cw, ch = 1080, 1920

    # Video filter: center 9:16 crop, color boost, hook banner
    filter_complex = (
        f"[0:v]scale=-1:{ch},"
        f"crop={cw}:{ch},"
        f"eq=contrast=1.12:brightness=0.02:saturation=1.20,"
        f"drawbox=x=40:y=60:w=1000:h=100:color=black@0.65:t=fill,"
        f"drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':text='{hook_title}':"
        f"fontsize=58:fontcolor=0xFFE600:borderw=5:bordercolor=black:"
        f"x=(w-text_w)/2:y=78[v_out];"
        f"[0:a]aresample=async=1000:first_pts=0,asetpts=PTS-STARTPTS[a_out]"
    )

    cmd = [
        FFMPEG, "-y",
        "-ss", str(start_sec),
        "-t", str(duration),
        "-avoid_negative_ts", "make_zero",
        "-i", input_video,
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        output_mp4
    ]

    print(f"\n🎬 Rendering fullscreen gameplay cut: {Path(output_mp4).name}...")
    subprocess.run(cmd, check=True)
    print(f"✅ Rendered successfully: {output_mp4} ({os.path.getsize(output_mp4) // 1024} KB)")


def main():
    print("=" * 75)
    print("🔥 RENDERING 3 GOD-TIER REVIEW CUTS (STRICTLY NO UPLOADS - FOR REVIEW)")
    print("=" * 75)

    # ----------------------------------------------------
    # CUT 1: CaseOh Car Crash Rage (Pure Comedy & Screaming)
    # ----------------------------------------------------
    # CaseOh webcam in source: x: 0 to 450, y: 150 to 520 (w: 450, h: 370)
    # Gameplay: centered x: 380, y: 0, w: 1280, h: 1080
    c1_in = str(REVIEW_DIR / "caseoh_full_crashes.mp4.mkv")
    c1_out = str(REVIEW_DIR / "cut_01_caseoh_crash_rage_1080p.mp4")
    render_streamer_cut(
        input_video=c1_in,
        output_mp4=c1_out,
        start_sec=1.0,
        duration=22.0,
        fc_crop={"x": 0, "y": 180, "w": 420, "h": 340},
        gp_crop={"x": 380, "y": 0, "w": 1280, "h": 1080},
        hook_title="CASEOH CANNOT DRIVE IN GTA 💀"
    )

    # ----------------------------------------------------
    # CUT 2: Red Arcade GTA 6 Insane Physics Fails & Explosion
    # ----------------------------------------------------
    c2_in = str(REVIEW_DIR / "redarcade_gta6_fails.mp4.webm")
    c2_out = str(REVIEW_DIR / "cut_02_gta6_insane_physics_stunt_1080p.mp4")
    render_fullscreen_gameplay_cut(
        input_video=c2_in,
        output_mp4=c2_out,
        start_sec=0.5,
        duration=18.0,
        hook_title="GTA 6 PHYSICS GONE WRONG 💀"
    )

    # ----------------------------------------------------
    # CUT 3: Kai Cenat 5-Star Police Chase & Car Explosion Jump
    # ----------------------------------------------------
    # Kai Cenat webcam at sec 80-102:
    # Webcam: x: 0 to 420, y: 350 to 650 (w: 420, h: 300)
    # Gameplay: x: 340, y: 0, w: 1280, h: 1080
    c3_in = str(REVIEW_DIR / "kai_cenat_funniest.mp4.webm")
    c3_out = str(REVIEW_DIR / "cut_03_kai_cenat_5star_escape_1080p.mp4")
    render_streamer_cut(
        input_video=c3_in,
        output_mp4=c3_out,
        start_sec=81.0,
        duration=21.0,
        fc_crop={"x": 0, "y": 320, "w": 420, "h": 320},
        gp_crop={"x": 340, "y": 0, "w": 1280, "h": 1080},
        hook_title="KAI CENAT 5-STAR POLICE CHASE 🚨"
    )

    print("\n🎉 ALL 3 GOD-TIER CUTS RENDERED AT FULL 1080x1920 60FPS WITH PERFECT SYNC!")
    print("ZERO UPLOADS EXECUTED.")

if __name__ == "__main__":
    main()
