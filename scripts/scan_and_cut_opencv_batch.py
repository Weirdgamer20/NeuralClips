"""Scans sources with OpenCV retention engine and renders high-retention 2K cuts with exact facecam alignment and synchronized audio.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import imageio_ffmpeg
import cv2

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.opencv_retention_engine import OpenCVRetentionEngine

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
engine = OpenCVRetentionEngine()

review_dir = BASE_DIR / "storage" / "review_cuts"
out_dir = BASE_DIR / "storage" / "review_cuts"

def process_caseoh_clip():
    in_video = review_dir / "caseoh_full_crashes.mp4.mkv"
    if not in_video.exists():
        print("CaseOh video not found!")
        return None

    print("\n🔍 [1/3] Analyzing CaseOh with OpenCV...")
    fc = engine.detect_exact_facecam(str(in_video), max_check_seconds=30.0)
    print("  • Detected exact facecam box:", fc)

    peaks = engine.scan_motion_peaks_fast(str(in_video), clip_duration=30.0, sample_fps=2.0)
    top_peak = peaks[0] if peaks else {"start_sec": 15.0, "duration": 30.0}
    print(f"  • Top motion peak: {top_peak['start_sec']}s - {top_peak['end_sec']}s (Motion: {top_peak.get('motion_score')})")

    out_file = out_dir / "cut_05_caseoh_opencv_rage_2k.mp4"
    start_s = top_peak["start_sec"]
    dur_s = 30.0

    # Facecam box from OpenCV
    # If facecam detected at x, y, w, h
    # We create a floating card overlay or stacked layout.
    # CaseOh facecam is 420x280 at top-left.
    fx = fc["x"]
    fy = fc["y"]
    fw = fc["width"]
    fh = fc["height"]

    # Filtergraph:
    # 1. Gameplay: centered 9:16 crop from 1920x1080 (w=608, h=1080, x=656, y=0) scaled to 1080x1920 with Lanczos
    # 2. Facecam: crop from fx:fy:fw:fh, scale to 460x290, add 4px electric cyan border, overlay on top-left of gameplay
    vf = (
        f"[0:v]crop=608:1080:656:0,scale=1080:1920:flags=lanczos+accurate_rnd,setsar=1[bg];"
        f"[0:v]crop={fw}:{fh}:{fx}:{fy},scale=460:290:flags=lanczos+accurate_rnd,pad=468:298:4:4:color=0x00F0FF[cam];"
        f"[bg][cam]overlay=35:120:format=auto,unsharp=5:5:0.6:5:5:0.3,setsar=1[v_out]"
    )

    af = "aresample=async=1000:min_hard_comp=0.010000,volume=1.25"

    cmd = [
        ffmpeg, "-y",
        "-ss", str(start_s),
        "-i", str(in_video),
        "-t", str(dur_s),
        "-filter_complex", vf,
        "-map", "[v_out]",
        "-map", "0:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "15",
        "-pix_fmt", "yuv420p",
        "-b:v", "14M",
        "-maxrate", "22M",
        "-bufsize", "45M",
        "-c:a", "aac",
        "-b:a", "320k",
        "-af", af,
        "-avoid_negative_ts", "make_zero",
        "-async", "1",
        str(out_file)
    ]

    print("  • Rendering CaseOh cut...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print("  ✅ SUCCESS! Rendered:", out_file.name)
        return str(out_file)
    else:
        print("  ❌ FAILED:", res.stderr[-400:])
        return None

if __name__ == "__main__":
    res = process_caseoh_clip()
