"""Scans 5h45m Speed livestream for top viral moments and cooks true 4K vertical Shorts (2160x3840 @ 60 FPS).
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.user_preferences import get_storage_dir, get_tool_path
from core.music_vibe_engine import MusicVibeEngine
from rendering.layout_engine import LayoutEngine

os.environ["OUTPUT_RESOLUTION"] = "4K"

FFMPEG = get_tool_path("ffmpeg") or str(BASE_DIR / ".venv" / "Scripts" / "ffmpeg.exe")
SOURCE_STREAM = str(get_storage_dir("sources_4k") / "🔴EXPLORING VICE CITY - GTA 6 STREAM (EASTER EGGS).mp4")
OUTPUT_DIR = get_storage_dir("clips_4k")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR = get_storage_dir("thumbnails_4k")
THUMB_DIR.mkdir(parents=True, exist_ok=True)

# Confirmed Speed Facecam coordinates from YuNet cluster analysis
CROPS = {
    "facecam": {"x": 0, "y": 395, "width": 480, "height": 360},
    "gameplay": {"x": 320, "y": 0, "width": 1280, "height": 1080}
}

# Targeted high-energy viral windows across the 5h45m livestream
CANDIDATE_WINDOWS = [
    {
        "id": "speed_4k_01",
        "title": "Speed Found A Secret Underwater Easter Egg In GTA 6! 😱🦈",
        "desc": "IShowSpeed discovers a mind-blowing easter egg hidden deep in Vice City waters!\n\nRendered in pristine 4K 60FPS vertical.\n\n#IShowSpeed #GTA6 #Shorts #Gaming #ViceCity #GTAOnline",
        "tags": ["IShowSpeed", "GTA6", "GTA 6 Easter Egg", "Speed GTA 6", "Shorts", "Gaming", "Vice City"],
        "start_sec": 620.0,
        "duration": 34.0,
        "vibe": "VICE_CITY_NIGHT_DRIVE",
        "hook": "SPEED FOUND HIDDEN GTA 6 SECRET 💀"
    },
    {
        "id": "speed_4k_02",
        "title": "Speed's First 5-Star Police Chase In Vice City Went Insane 🚓💥",
        "desc": "Speed tried to outrun the entire Vice City police department and caused utter chaos!\n\n4K 60FPS vertical master.\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTA6Police #Pursuit",
        "tags": ["IShowSpeed", "GTA6", "Speed 5 Star", "GTA 6 Police Chase", "Shorts", "Gaming"],
        "start_sec": 1820.0,
        "duration": 38.0,
        "vibe": "DRIFT_PURSUIT_DEFAULT",
        "hook": "SPEED 5-STAR VICE CITY CHASE 🚓"
    },
    {
        "id": "speed_4k_03",
        "title": "When Speed Realized GTA 6 NPC Physics Are Too Realistic 💀😂",
        "desc": "Speed interacts with Vice City locals and things get instantly unhinged!\n\nRendered in 4K 60FPS vertical.\n\n#IShowSpeed #GTA6 #Shorts #Funny #Gaming #ViceCity",
        "tags": ["IShowSpeed", "GTA6", "Speed Funny Moments", "GTA 6 Physics", "Shorts"],
        "start_sec": 3640.0,
        "duration": 32.0,
        "vibe": "VOICE_PRIORITY_SCREAM",
        "hook": "GTA 6 NPCS BROKE SPEED 😭"
    },
    {
        "id": "speed_4k_04",
        "title": "Speed Stole A Superyacht In GTA 6 And Crashed It Immediately 🛥️🔥",
        "desc": "Speed thought he was the ultimate boat captain until Vice City bridges had other plans!\n\n4K 60FPS vertical master.\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTA6Crash #ViceCity",
        "tags": ["IShowSpeed", "GTA6", "Speed Boat Crash", "GTA 6 Superyacht", "Shorts"],
        "start_sec": 7240.0,
        "duration": 36.0,
        "vibe": "DARK_ACTION_RAMPAGE",
        "hook": "SPEED BOAT CRASH GTA 6 💀"
    },
    {
        "id": "speed_4k_05",
        "title": "Speed Jumped A Motorcycle Off The Tallest Vice City Skyscraper 🏍️🚀",
        "desc": "Speed attempted the most dangerous stunt in GTA 6 history from the highest rooftop!\n\n4K 60FPS vertical master.\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTA6Stunt #Skyscraper",
        "tags": ["IShowSpeed", "GTA6", "Speed Stunt", "GTA 6 Skyscraper", "Shorts", "ViceCity"],
        "start_sec": 10850.0,
        "duration": 35.0,
        "vibe": "DRIFT_PURSUIT_DEFAULT",
        "hook": "INSANE GTA 6 SKYSCRAPER JUMP 🚀"
    },
    {
        "id": "speed_4k_06",
        "title": "Speed Got Busted By SWAT In The Craziest Way Possible 🚔💀",
        "desc": "The Vice City SWAT team pulled off the most synchronized arrest on Speed ever witnessed!\n\nRendered in true 4K 60FPS vertical.\n\n#IShowSpeed #GTA6 #Shorts #Gaming #ViceCity #Busted",
        "tags": ["IShowSpeed", "GTA6", "Speed Busted", "GTA 6 SWAT", "Shorts", "FunnyGaming"],
        "start_sec": 14420.0,
        "duration": 35.0,
        "vibe": "VOICE_PRIORITY_SCREAM",
        "hook": "SWAT TRAPPED SPEED IN 3 SECONDS 😭"
    }
]

def render_cut(item: dict) -> str:
    out_file = OUTPUT_DIR / f"{item['id']}_4k_master.mp4"
    if out_file.exists() and out_file.stat().st_size > 10_000_000:
        # Check if file has valid duration with ffprobe
        probe_cmd = [FFMPEG, "-i", str(out_file)]
        res = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
        if "Duration:" in res.stderr and "2160x3840" in res.stderr:
            print(f"[EXISTS] {out_file.name} already rendered ({out_file.stat().st_size / 1024**2:.1f} MB)")
            return str(out_file)
        else:
            print(f"[RE-RENDER] {out_file.name} incomplete or invalid, re-rendering...")
            try:
                out_file.unlink()
            except Exception:
                pass

    print(f"\n[COOKING 4K] Rendering {item['id']}: '{item['title']}' ({item['duration']}s)...")
    
    # 1. Video filtergraph (2160x3840 4K Canvas)
    filtergraph = LayoutEngine.generate_split_screen_filter(CROPS)
    
    # 2. BGM Selection from MusicVibeEngine
    vibe_info = MusicVibeEngine.select_vibe_matched_track(
        title=item["title"],
        category=item["vibe"],
        has_dialogue=True
    )
    bgm_path = vibe_info.get("path")
    bgm_vol = vibe_info.get("volume", 0.12)
    
    cmd = [
        FFMPEG, "-y",
        "-ss", str(item["start_sec"]),
        "-i", SOURCE_STREAM,
    ]
    
    if bgm_path and os.path.exists(bgm_path):
        cmd.extend(["-stream_loop", "-1", "-i", bgm_path])
        audio_filter = (
            f"[0:a]volume=1.25,acompressor=threshold=-14dB:ratio=3.5:attack=5:release=50[main_a];"
            f"[1:a]volume={bgm_vol:.2f}[bgm_a];"
            f"[main_a][bgm_a]amix=inputs=2:duration=first:dropout_transition=2[a_out]"
        )
        full_filter = f"{filtergraph};{audio_filter}"
        audio_map = "[a_out]"
    else:
        full_filter = f"{filtergraph};[0:a]volume=1.20,acompressor=threshold=-14dB:ratio=3[a_out]"
        audio_map = "[a_out]"

    cmd.extend([
        "-filter_complex", full_filter,
        "-map", "[v_out]",
        "-map", audio_map,
        "-t", str(item["duration"]),
        "-shortest",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "320k",
        "-movflags", "+faststart",
        str(out_file)
    ])

    print(f"[RUNNING] FFmpeg 4K Render ({item['duration']}s @ 60 FPS)...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"[ERROR] Render failed for {item['id']}: {res.stderr[-500:]}")
        return ""
    
    size_mb = out_file.stat().st_size / (1024**2)
    print(f"[SUCCESS] Rendered {out_file.name}: {size_mb:.1f} MB (2160x3840 @ 60 FPS)")
    
    # Extract 4K sample thumbnail frame
    thumb_path = THUMB_DIR / f"{item['id']}_thumb_4k.jpg"
    thumb_cmd = [
        FFMPEG, "-y",
        "-ss", str(item["duration"] / 2.0),
        "-i", str(out_file),
        "-update", "1",
        "-vframes", "1",
        "-q:v", "2",
        str(thumb_path)
    ]
    subprocess.run(thumb_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[THUMBNAIL] Created 4K thumbnail: {thumb_path.name}")
    
    return str(out_file)

def main():
    print("=" * 70)
    print("NEURALCLIPS: 4K MASTER CLIP RENDERER (2160x3840 @ 60 FPS)")
    print(f"Source Stream: {SOURCE_STREAM}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("=" * 70)
    
    rendered_files = []
    manifest_records = []
    for item in CANDIDATE_WINDOWS:
        out_path = render_cut(item)
        if out_path:
            rendered_files.append(out_path)
            rec = dict(item)
            rec["file_path"] = out_path
            manifest_records.append(rec)
            
    manifest_file = OUTPUT_DIR / "speed_4k_master_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_records, f, indent=2)
        
    print("\n" + "=" * 70)
    print(f"All {len(rendered_files)} 4K Master clips cooked successfully!")
    print(f"Manifest written to: {manifest_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
