"""Download at least 30 non-copyright tracks from official NCS channel."""

import os
import re
import sys
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC_DIR = os.path.join(BASE_DIR, "assets", "music")
FFMPEG_PATH = os.path.join(BASE_DIR, ".venv", "Scripts", "ffmpeg.EXE")
PYTHON_PATH = sys.executable

os.makedirs(MUSIC_DIR, exist_ok=True)

# Curated iconic NCS all-time gaming classics
ICONIC_TRACKS = [
    ("Alan Walker - Fade", "bM7SZ5SBzyY"),
    ("Warriyo - Mortals", "yJg-Y5byMMw"),
    ("Lost Sky - Where We Started", "U9pGr6KMdyg"),
    ("Janji - Heroes Tonight", "3nQNiWdeH2Q"),
    ("Different Heaven - My Heart", "jK2aIUmmdP4"),
    ("RetroVision - Puzzle", "TN_8L-xWpss"),
    ("Jim Yosef - Firefly", "x_OwcYTNbHs"),
    ("Tobu - Hope", "EP625xQIGzs"),
    ("Tobu - Candyland", "IIrCDAV3EgI"),
    ("Julius Dreisig - Invisible", "QglaLzo_aPk"),
    ("Unknown Brain - Superhero", "LHvYrn3FAgI"),
    ("Elektronomia - Energy", "fzNMd3Tu1Zw"),
    ("Culture Code - Make Me Move", "vBGiFtb8Rpw"),
    ("Disfigure - Blank VIP", "jAMRM5K2k1M"),
    ("Aero Chord - Time Leap", "beDFqlUSZuw"),
]


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"[-\s]+", "_", name)


def get_existing_tracks() -> list:
    if not os.path.exists(MUSIC_DIR):
        return []
    return [
        f for f in os.listdir(MUSIC_DIR)
        if f.lower().endswith(".mp3") and os.path.getsize(os.path.join(MUSIC_DIR, f)) > 100000
    ]


def download_track(title: str, video_id: str) -> bool:
    clean_name = f"ncs_{sanitize_filename(title)}"
    out_tmpl = os.path.join(MUSIC_DIR, f"{clean_name}.%(ext)s")
    final_mp3 = os.path.join(MUSIC_DIR, f"{clean_name}.mp3")

    if os.path.exists(final_mp3) and os.path.getsize(final_mp3) > 100000:
        print(f"Skipping (already exists): {clean_name}")
        return True

    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Downloading: {title} ({url})...")
    cmd = [
        PYTHON_PATH, "-m", "yt_dlp",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "5",
        "--ffmpeg-location", FFMPEG_PATH,
        "--no-playlist",
        "-o", out_tmpl,
        url,
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
        if res.returncode == 0 and os.path.exists(final_mp3) and os.path.getsize(final_mp3) > 100000:
            print(f"Successfully downloaded: {clean_name}.mp3 ({os.path.getsize(final_mp3)} bytes)")
            return True
        else:
            print(f"Failed to download {title}: {res.stderr[:200]}")
            return False
    except Exception as e:
        print(f"Error downloading {title}: {e}")
        return False


def fetch_official_ncs_channel_releases(limit: int = 35) -> list:
    print(f"Fetching latest {limit} releases from @NoCopyrightSounds...")
    cmd = [
        PYTHON_PATH, "-m", "yt_dlp",
        "--flat-playlist", "-J",
        "--playlist-end", str(limit),
        "https://www.youtube.com/@NoCopyrightSounds/videos",
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            entries = data.get("entries", [])
            results = []
            for e in entries:
                t = e.get("title", "")
                vid = e.get("id", "")
                # Clean title (remove " | NCS - Copyright Free Music" etc)
                clean_title = re.sub(r"\|.*$", "", t).strip()
                if vid:
                    results.append((clean_title, vid))
            return results
    except Exception as ex:
        print("Error fetching channel entries:", ex)
    return []


def main():
    existing = get_existing_tracks()
    print(f"Currently have {len(existing)} valid tracks in {MUSIC_DIR}.")

    # Gather candidate list
    candidates = list(ICONIC_TRACKS)
    channel_tracks = fetch_official_ncs_channel_releases(limit=35)
    for ct in channel_tracks:
        if not any(c[1] == ct[1] for c in candidates):
            candidates.append(ct)

    print(f"Total candidate tracks queued: {len(candidates)}")

    target_total = 32
    for title, vid in candidates:
        existing = get_existing_tracks()
        if len(existing) >= target_total:
            print(f"Target of {target_total} tracks reached! Total: {len(existing)}")
            break
        download_track(title, vid)

    final_tracks = get_existing_tracks()
    print("==================================================================")
    print(f"COMPLETED: Total NCS Non-Copyright Tracks in Library: {len(final_tracks)}")
    print("==================================================================")
    for i, t in enumerate(final_tracks):
        print(f"{i+1:02d}. {t}")


if __name__ == "__main__":
    main()
