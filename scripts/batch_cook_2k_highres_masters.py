import sys
import shutil
"""Batch Cooker for True 2K Vertical Masters (1440x2560 @ 60 FPS) from 4K / 1440p Sources.

Features:
- Enforces True 2K Vertical canvas: 1440x2560.
- Strict 60.0 FPS, yuv420p, libx264 High Profile 5.1.
- Strict 1:1 SAR (setsar=1) to prevent aspect ratio distortion.
- Multi-tap Lanczos resampling + Unsharp mask for razor-sharp visual fidelity.
- Audio: 320 kbps AAC stereo 48000 Hz, time-aligned (aresample=async=1000:first_pts=0).
- High-CTR dynamic HUD title styling with black pill container.
"""

import os
import subprocess
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "storage" / "2k_master_cuts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = (shutil.which("ffmpeg") or os.getenv("FFMPEG_PATH") or str(Path(sys.prefix) / "Scripts" / "ffmpeg.exe"))

CLIPS = [
    {
        "id": "2k_master_01",
        "source": str(BASE_DIR / "storage" / "review_cuts/speed_gta6_trailer_4k.webm"),
        "crop": "1215:2160:(in_w-1215)/2:0",
        "ss": "10",
        "t": "35",
        "title": "SPEED IN GTA 6 IS INSANE! 4K",
        "out_name": "2k_master_01_speed_gta6_insane.mp4"
    },
    {
        "id": "2k_master_02",
        "source": str(BASE_DIR / "storage" / "review_cuts/speed_gta6_trailer_4k.webm"),
        "crop": "1215:2160:(in_w-1215)/2:0",
        "ss": "35",
        "t": "30",
        "title": "SPEED REACTS TO GTA 6 ENDING 4K",
        "out_name": "2k_master_02_speed_ending_reaction.mp4"
    },
    {
        "id": "2k_master_03",
        "source": str(BASE_DIR / "storage" / "review_cuts/full_4k_supercar_chase.mp4.webm"),
        "crop": "810:1440:(in_w-810)/2:0",
        "ss": "115",
        "t": "30",
        "title": "FASTEST 2K SUPERCAR ESCAPE",
        "out_name": "2k_master_03_supercar_escape.mp4"
    },
    {
        "id": "2k_master_04",
        "source": str(BASE_DIR / "storage" / "review_cuts/full_4k_supercar_chase.mp4.webm"),
        "crop": "810:1440:(in_w-810)/2:0",
        "ss": "190",
        "t": "30",
        "title": "IMPOSSIBLE 5-STAR HIGHWAY WEAVE",
        "out_name": "2k_master_04_highway_weave.mp4"
    },
    {
        "id": "2k_master_05",
        "source": str(BASE_DIR / "storage" / "review_cuts/full_4k_supercar_chase.mp4.webm"),
        "crop": "810:1440:(in_w-810)/2:0",
        "ss": "410",
        "t": "30",
        "title": "VICE CITY NIGHT PURSUIT 2K",
        "out_name": "2k_master_05_vice_city_pursuit.mp4"
    },
    {
        "id": "2k_master_06",
        "source": str(BASE_DIR / "storage" / "review_cuts/tank_6star_1440p.webm"),
        "crop": "810:1440:(in_w-810)/2:0",
        "ss": "75",
        "t": "30",
        "title": "MILITARY TANK 6-STAR RAMPAGE",
        "out_name": "2k_master_06_tank_rampage.mp4"
    },
    {
        "id": "2k_master_07",
        "source": str(BASE_DIR / "storage" / "review_cuts/tank_6star_1440p.webm"),
        "crop": "810:1440:(in_w-810)/2:0",
        "ss": "250",
        "t": "30",
        "title": "CRUSHING EVERY POLICE CAR 2K",
        "out_name": "2k_master_07_crushing_police_cars.mp4"
    },
    {
        "id": "2k_master_08",
        "source": str(BASE_DIR / "storage" / "review_cuts/source_leonida_chase.webm"),
        "crop": "810:1440:(in_w-810)/2:0",
        "ss": "90",
        "t": "30",
        "title": "SWAT ROADBLOCK BREACH 2K",
        "out_name": "2k_master_08_swat_breach.mp4"
    },
    {
        "id": "2k_master_09",
        "source": str(BASE_DIR / "storage" / "review_cuts/source_leonida_chase.webm"),
        "crop": "810:1440:(in_w-810)/2:0",
        "ss": "310",
        "t": "30",
        "title": "LEONIDA COUNTY DRIFT ESCAPE",
        "out_name": "2k_master_09_leonida_drift.mp4"
    },
    {
        "id": "2k_master_10",
        "source": str(BASE_DIR / "storage" / "review_cuts/source_realism_4k_sample.mp4"),
        "crop": "810:1440:(in_w-810)/2:0",
        "ss": "20",
        "t": "30",
        "title": "GTA 6 ULTRA GRAPHICS REALISM 2K",
        "out_name": "2k_master_10_ultra_graphics_realism.mp4"
    }
]

def render_clip(clip_meta):
    out_path = OUTPUT_DIR / clip_meta["out_name"]
    print(f"\n==================================================")
    print(f"Rendering: {clip_meta['id']} -> {clip_meta['title']}")
    print(f"Output: {out_path}")
    
    crop_filter = clip_meta["crop"]
    title_text = clip_meta["title"].replace("'", "\\'")
    
    filter_complex = (
        f"[0:v]crop={crop_filter},scale=1440:2560:flags=lanczos,"
        f"unsharp=5:5:0.8:5:5:0.0,eq=contrast=1.08:brightness=0.01:saturation=1.15,setsar=1,"
        f"drawbox=x=60:y=120:w=1320:h=150:color=black@0.75:t=fill,"
        f"drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':text='{title_text}':"
        f"fontsize=72:fontcolor=0xFFE600:borderw=6:bordercolor=black:"
        f"x=(w-text_w)/2:y=155[v_out];"
        f"[0:a]aresample=async=1000:first_pts=0,asetpts=PTS-STARTPTS[a_out]"
    )
    
    cmd = [
        FFMPEG, "-y",
        "-ss", clip_meta["ss"],
        "-t", clip_meta["t"],
        "-avoid_negative_ts", "make_zero",
        "-i", clip_meta["source"],
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        str(out_path)
    ]
    
    subprocess.run(cmd, check=True)
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"SUCCESS: Rendered {out_path.name} ({size_mb:.1f} MB)")
    return {
        "id": clip_meta["id"],
        "title": clip_meta["title"],
        "file": str(out_path),
        "size_mb": round(size_mb, 2),
        "resolution": "1440x2560",
        "fps": 60,
        "crf": 16,
        "sar": "1:1"
    }

if __name__ == "__main__":
    results = []
    manifest_file = BASE_DIR / "storage" / "2k_master_cuts_manifest.json"
    for c in CLIPS:
        try:
            res = render_clip(c)
            results.append(res)
        except Exception as e:
            print(f"Error rendering {c['id']}: {e}")
    with open(manifest_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nAll done! Successfully rendered {len(results)}/{len(CLIPS)} cuts to {OUTPUT_DIR}")
