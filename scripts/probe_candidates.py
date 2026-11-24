import subprocess
import json
from pathlib import Path
import imageio_ffmpeg

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

files = [
    str(BASE_DIR / "storage" / "raw\live_src_NC-REALTIME-GTA6-20261120-201800_1.mp4"),
    str(BASE_DIR / "storage" / "raw\live_src_NC-REALTIME-GTA6-20261120-201800_2.mp4"),
    str(BASE_DIR / "storage" / "raw\live_src_NC-REALTIME-GTA6-20261120-201800_3.mp4"),
    str(BASE_DIR / "storage" / "raw\live_src_NC-REALTIME-GTA6-20261120-202739_1.mp4"),
    str(BASE_DIR / "storage" / "raw\live_src_NC-REALTIME-GTA6-20261120-202739_2.mp4"),
    str(BASE_DIR / "storage" / "viral_100_clips\2BRL4ALMCyA.mp4"),
    str(BASE_DIR / "storage" / "viral_100_clips\LphAOQ6wMm4.mp4"),
    str(BASE_DIR / "storage" / "viral_100_clips\PbSvLZld-iU.mp4"),
    str(BASE_DIR / "storage" / "viral_100_clips\AvWKUJhPTiQ.mp4")
]

for fp in files:
    if not Path(fp).exists():
        continue
    cmd = [ffmpeg, '-i', fp]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stderr
    dur = "unknown"
    res_info = "unknown"
    has_audio = "Audio:" in out
    for line in out.splitlines():
        if "Duration:" in line:
            dur = line.split("Duration:")[1].split(",")[0].strip()
        if "Video:" in line:
            res_info = line.split("Video:")[1].strip()
    print(f"{Path(fp).name} | Dur: {dur} | Audio: {has_audio} | Size: {Path(fp).stat().st_size/(1024*1024):.1f}MB")
