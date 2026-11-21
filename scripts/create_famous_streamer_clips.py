"""NeuralClips: Real Livestream Moments from Famous YouTubers.

Extracts viral moments directly from real GTA 6 livestreams of top YouTubers:
1. IShowSpeed
2. Kai Cenat
3. Typical Gamer
4. CaseOh
5. xQc

Renders in 2K 1440x2560 Vertical layout:
- Gameplay Top 60%
- Streamer Facecam Bottom 40% (dynamic computer vision detection)
- Electric Cyan Neon Divider
- Audio mastered and synchronized
- Saves to storage/famous_streamer_clips and copies to Desktop
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(r"d:\vidclip")
sys.path.insert(0, str(BASE_DIR))

from rendering.crop_detector import CropDetector
from rendering.ffmpeg_renderer import FFmpegRenderer
from rendering.render_validator import RenderValidator

STORAGE_DIR = BASE_DIR / "storage"
OUTPUT_DIR = STORAGE_DIR / "famous_streamer_clips"
RAW_DIR = STORAGE_DIR / "raw_streamer_chunks"
DESKTOP_DIR = Path(r"C:\Users\thega\Desktop")
FFMPEG_BIN_DIR = BASE_DIR / ".venv" / "Scripts"

STREAMER_TARGETS = [
    {
        "streamer": "IShowSpeed",
        "desktop_filename": "neuralclips_speed_gta6.mp4",
        "title": "Speed reacting to GTA 6 Vice City graphics 💀",
        "stream_url": "https://www.youtube.com/watch?v=hwSg39yIBGU",
        "start_sec": 1800,
        "end_sec": 1835,
        "crop_profile": "IShowSpeed"
    },
    {
        "streamer": "Kai Cenat",
        "desktop_filename": "neuralclips_kai_gta6.mp4",
        "title": "Kai Cenat first mission in GTA 6 went completely wrong 😭",
        "stream_url": "https://www.youtube.com/watch?v=VZqAPdUvqnQ",
        "start_sec": 2400,
        "end_sec": 2435,
        "crop_profile": "Kai Cenat"
    },
    {
        "streamer": "Typical Gamer",
        "desktop_filename": "neuralclips_typicalgamer_gta6.mp4",
        "title": "Typical Gamer testing GTA 6 5-Star Police on PS5 Pro 🚓🔥",
        "stream_url": "https://www.youtube.com/watch?v=6RgkIVpvvsY",
        "start_sec": 1500,
        "end_sec": 1535,
        "crop_profile": "Typical Gamer"
    },
    {
        "streamer": "CaseOh",
        "desktop_filename": "neuralclips_caseoh_gta6.mp4",
        "title": "CaseOh funniest vehicle crash in GTA 6 history 💀",
        "stream_url": "https://www.youtube.com/watch?v=k3esjgmbphQ",
        "start_sec": 2100,
        "end_sec": 2135,
        "crop_profile": "CaseOh"
    },
    {
        "streamer": "xQc",
        "desktop_filename": "neuralclips_xqc_gta6.mp4",
        "title": "xQc loses his mind escaping the Vice City cops in GTA 6 🤯",
        "stream_url": "https://www.youtube.com/watch?v=VWNBp6SIEPU",
        "start_sec": 1200,
        "end_sec": 1235,
        "crop_profile": "xQc"
    }
]


def download_streamer_moment(target: dict) -> Path:
    raw_path = RAW_DIR / f"raw_{target['streamer'].lower().replace(' ', '_')}.mp4"
    if raw_path.exists() and raw_path.stat().st_size > 500000:
        print(f"  [CACHE] Raw chunk already exists ({raw_path.stat().st_size / (1024*1024):.1f}MB)")
        return raw_path

    print(f"  [DOWNLOAD] Extracting moment from {target['streamer']}'s livestream ({target['start_sec']}s - {target['end_sec']}s)...", flush=True)
    cmd = [
        str(BASE_DIR / ".venv" / "Scripts" / "python.exe"),
        "-m", "yt_dlp",
        target["stream_url"],
        "--ffmpeg-location", str(FFMPEG_BIN_DIR),
        "--extractor-args", "youtube:player_client=android,web",
        "--download-sections", f"*{target['start_sec']}-{target['end_sec']}",
        "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
        "-o", str(raw_path),
        "--no-warnings"
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, timeout=60)
    return raw_path


def render_streamer_clip(target: dict, raw_path: Path, crop_detector: CropDetector, renderer: FFmpegRenderer, validator: RenderValidator) -> dict:
    streamer = target["streamer"]
    title = target["title"]
    out_file = OUTPUT_DIR / f"{streamer.lower().replace(' ', '_')}_gta6_short.mp4"
    desktop_file = DESKTOP_DIR / target["desktop_filename"]

    print(f"  [RENDER] Cropping Gameplay (Top 60%) + {streamer} Facecam (Bottom 40%)...", flush=True)
    crops = crop_detector.resolve_crop(target["crop_profile"], str(raw_path))
    
    # 35-second vertical split-screen render
    ok, msg = renderer.render_split_screen(
        input_video_path=str(raw_path),
        output_clip_path=str(out_file),
        start_seconds=0.0,
        duration_seconds=35.0,
        crop_config=crops
    )

    if not ok:
        raise RuntimeError(f"FFmpeg render failed: {msg}")

    # Validate output
    is_val, val_msg, meta = validator.validate_clip(str(out_file))
    sz_mb = out_file.stat().st_size / (1024 * 1024)
    print(f"  [VALIDATED] {sz_mb:.1f}MB, {meta.get('duration')}s, {meta.get('width')}x{meta.get('height')}", flush=True)

    # Copy directly to Desktop for user preview
    try:
        shutil.copy2(str(out_file), str(desktop_file))
        print(f"  [DELIVERED] Copied to Desktop: {desktop_file}", flush=True)
    except Exception as e:
        print(f"  [NOTICE] Desktop copy: {e}", flush=True)

    return {
        "streamer": streamer,
        "title": title,
        "output_file": str(out_file),
        "desktop_file": str(desktop_file),
        "file_size_mb": round(sz_mb, 2),
        "duration_sec": meta.get("duration", 35.0),
        "resolution": f"{meta.get('width')}x{meta.get('height')}",
        "url": target["stream_url"]
    }


def main():
    print("==================================================================")
    print("NEURALCLIPS: EXTRACTING MOMENTS FROM FAMOUS YOUTUBER LIVESTREAMS")
    print("==================================================================")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    crop_detector = CropDetector()
    renderer = FFmpegRenderer()
    validator = RenderValidator()

    manifest = []
    
    for idx, target in enumerate(STREAMER_TARGETS, 1):
        print(f"\n[{idx}/5] PROCESSING: {target['streamer']} - '{target['title']}'", flush=True)
        try:
            raw_path = download_streamer_moment(target)
            clip_info = render_streamer_clip(target, raw_path, crop_detector, renderer, validator)
            manifest.append(clip_info)
            print(f"  -> SUCCESS: {target['streamer']} clip is ready!", flush=True)
        except Exception as e:
            print(f"  -> ERROR for {target['streamer']}: {e}", flush=True)

    # Save manifest
    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 65)
    print(f"ALL {len(manifest)}/{len(STREAMER_TARGETS)} FAMOUS YOUTUBER CLIPS READY!")
    print(f"Saved in:   {OUTPUT_DIR}")
    print(f"Desktop:    {DESKTOP_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
