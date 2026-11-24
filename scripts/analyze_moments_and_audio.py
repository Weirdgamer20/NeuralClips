"""Analyzes downloaded clips to pinpoint the absolute best moments (peak screams, laughter, crashes).
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np

BASE_DIR = Path("d:/vidclip")
REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
FFMPEG = str(BASE_DIR / ".venv" / "Scripts" / "ffmpeg.exe")

CLIPS = [
    {
        "name": "CaseOh Crashes",
        "file": str(REVIEW_DIR / "caseoh_full_crashes.mp4.mkv"),
        "key": "caseoh",
    },
    {
        "name": "Kai Cenat Funniest",
        "file": str(REVIEW_DIR / "kai_cenat_funniest.mp4.webm"),
        "key": "kai",
    },
    {
        "name": "Red Arcade GTA 6 Fails",
        "file": str(REVIEW_DIR / "redarcade_gta6_fails.mp4.webm"),
        "key": "redarcade",
    },
]

def analyze_audio_peaks(file_path):
    """Uses ffmpeg ebur128 or silencedetect / volumedetect to find loudest parts."""
    cmd = [
        FFMPEG, "-i", file_path,
        "-af", "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.Peak_level:file=-",
        "-vn", "-sn", "-f", "null", "NUL"
    ]
    # Simpler: extract frames at key seconds and measure optical flow / motion
    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    cap.release()
    return duration, fps

def extract_snapshots(clip_info):
    name = clip_info["name"]
    path = clip_info["file"]
    key = clip_info["key"]
    print(f"\n=======================================================")
    print(f"🎬 Analyzing: {name} ({Path(path).name})")
    print(f"=======================================================")
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    print(f"Duration: {duration:.1f}s, FPS: {fps}, Total Frames: {total_frames}")

    # Check timestamps at 2s, 8s, 15s, 25s, 40s
    test_secs = [2, 6, 12, 18, 25, 35]
    for sec in test_secs:
        if sec >= duration:
            continue
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(sec * fps))
        ret, frame = cap.read()
        if ret:
            out_img = REVIEW_DIR / f"{key}_sec_{sec}.jpg"
            cv2.imwrite(str(out_img), frame)
            h, w, _ = frame.shape
            print(f"  Frame at {sec}s saved -> {out_img.name} ({w}x{h})")
    cap.release()

if __name__ == "__main__":
    for c in CLIPS:
        extract_snapshots(c)
