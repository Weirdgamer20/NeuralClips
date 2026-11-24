import os
import shutil
"""Scans downloaded videos for top high-energy windows using audio volume metrics.
"""

import cv2
import subprocess
import sys
from pathlib import Path

def get_peak_windows(file_path):
    results = []
    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = int(frames / fps)
    cap.release()
    
    # Check 20-second windows across the video
    step = 20
    for start in range(0, min(dur - 22, 350), step):
        cmd = [
            (shutil.which("ffmpeg") or os.getenv("FFMPEG_PATH") or str(Path(sys.prefix) / "Scripts" / "ffmpeg.exe")),
            "-ss", str(start),
            "-t", "22",
            "-i", file_path,
            "-af", "volumedetect",
            "-vn", "-sn", "-f", "null", "NUL"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        max_vol = -99.0
        mean_vol = -99.0
        for line in res.stderr.splitlines():
            if "max_volume:" in line:
                try:
                    max_vol = float(line.split("max_volume:")[1].replace("dB", "").strip())
                except Exception:
                    pass
            if "mean_volume:" in line:
                try:
                    mean_vol = float(line.split("mean_volume:")[1].replace("dB", "").strip())
                except Exception:
                    pass
        results.append({"start": start, "max_vol": max_vol, "mean_vol": mean_vol})
    
    # Sort by loudness (highest mean_vol and max_vol)
    results.sort(key=lambda x: (x["mean_vol"], x["max_vol"]), reverse=True)
    return results[:4]

if __name__ == "__main__":
    targets = [
        ("CaseOh", "storage/review_cuts/caseoh_full_crashes.mp4.mkv"),
        ("RedArcade", "storage/review_cuts/redarcade_gta6_fails.mp4.webm"),
        ("KaiCenat", "storage/review_cuts/kai_cenat_funniest.mp4.webm"),
    ]
    for name, f in targets:
        print(f"\n🔥 Scanning {name} ({f})...")
        top = get_peak_windows(f)
        for t in top:
            print(f"  • Start at {t['start']}s: Mean={t['mean_vol']} dB, Max={t['max_vol']} dB")
