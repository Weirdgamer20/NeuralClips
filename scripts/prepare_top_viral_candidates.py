"""Downloads seconds 0-35 from the top viral GTA / streamer moments with frame-accurate sync.
"""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path("d:/vidclip")
REVIEW_DIR = BASE_DIR / "storage" / "review_cuts"
REVIEW_DIR.mkdir(parents=True, exist_ok=True)
FFMPEG = str(BASE_DIR / ".venv" / "Scripts" / "ffmpeg.exe")

CANDIDATES = [
    {
        "id": "cand_speed",
        "url": "https://www.youtube.com/watch?v=QjDbRdBzD3k",
        "title": "Speed GTA 6 Top Moment",
        "time_range": "*0-32",
        "raw_out": str(REVIEW_DIR / "raw_cand_speed.mp4"),
    },
    {
        "id": "cand_caseoh",
        "url": "https://www.youtube.com/watch?v=HatdPY0Tl1k",
        "title": "CaseOh Car Crash Rage",
        "time_range": "*0-32",
        "raw_out": str(REVIEW_DIR / "raw_cand_caseoh.mp4"),
    },
    {
        "id": "cand_fails",
        "url": "https://www.youtube.com/watch?v=4ggwTEKq9MA",
        "title": "Red Arcade GTA 6 Godtier Fail",
        "time_range": "*0-32",
        "raw_out": str(REVIEW_DIR / "raw_cand_fails.mp4"),
    },
]

def download_candidate(c):
    print(f"\n=======================================================")
    print(f"📥 Downloading: {c['title']} ({c['url']}) [{c['time_range']}]")
    print(f"=======================================================")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        c["url"],
        "--ffmpeg-location", str(BASE_DIR / ".venv" / "Scripts"),
        "--download-sections", c["time_range"],
        "--force-keyframes-at-cuts",
        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        "-o", c["raw_out"],
        "--no-warnings"
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ Downloaded raw: {c['raw_out']}")

if __name__ == "__main__":
    for cand in CANDIDATES:
        download_candidate(cand)
