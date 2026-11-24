import subprocess
import imageio_ffmpeg
from pathlib import Path

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = str(Path(ffmpeg_exe).parent)

targets = [
    ("https://www.youtube.com/watch?v=vRuW2WG8AnA", "d:/vidclip/storage/review_cuts/indian_techno_gamerz.mp4"),
    ("https://www.youtube.com/watch?v=r4PmiWxkXJ8", "d:/vidclip/storage/review_cuts/indian_carryminati.mp4")
]

for url, out_path in targets:
    if Path(out_path).exists() and Path(out_path).stat().st_size > 10_000_000:
        print(f"Already exists: {out_path}", flush=True)
        continue
    print(f"Downloading: {url} -> {out_path}", flush=True)
    cmd = [
        "d:/vidclip/.venv/Scripts/yt-dlp.exe",
        "--ffmpeg-location", ffmpeg_dir,
        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "--merge-output-format", "mp4",
        "-o", out_path,
        url
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ Finished: {out_path}", flush=True)

print("🎉 ALL DOWNLOADS COMPLETE!", flush=True)
