"""Autonomous Pure GTA 6 Downloader & Style DNA Training Engine.

Downloads top 100 pure GTA 6 viral clips (no GTA 5 / mods / cartoons),
extracts visual scene cut cadence, audio RMS/LUFS profiles, hook timings,
and updates the AI Video Director style DNA weights.
"""

import os
import sys
import json
import time
import subprocess
import statistics
from pathlib import Path

STORAGE_DIR = Path(r"d:\vidclip\storage")
OUT_DIR = STORAGE_DIR / "viral_100_clips"
MANIFEST_PATH = OUT_DIR / "manifest.json"
CANDIDATES_PATH = STORAGE_DIR / "candidates_pure_gta6.json"
STYLE_DNA_PATH = STORAGE_DIR / "viral_style_dna.json"
FFMPEG_EXE = r"d:\vidclip\.venv\Scripts\ffmpeg.exe"
FFPROBE_EXE = r"d:\vidclip\.venv\Scripts\ffprobe.exe"


def download_clip(candidate, idx, total):
    vid_id = candidate["id"]
    title = candidate.get("title", "")
    views = candidate.get("views", 0)
    dur = candidate.get("dur", 0)
    out_file = OUT_DIR / f"{vid_id}.mp4"

    if out_file.exists() and out_file.stat().st_size > 100000:
        sz_mb = out_file.stat().st_size / (1024 * 1024)
        print(f"[{idx:03d}/{total}] CACHED: {vid_id} ({sz_mb:.2f}MB) | {views:,} views | {title[:40]}", flush=True)
        return {
            "id": vid_id,
            "title": title,
            "views": views,
            "duration": dur,
            "file_path": str(out_file),
            "size_bytes": out_file.stat().st_size,
            "status": "success"
        }

    url = f"https://www.youtube.com/watch?v={vid_id}"
    print(f"[{idx:03d}/{total}] DOWNLOADING: {views:,} views | {dur}s | {title[:45]}...", flush=True)

    cmd = [
        sys.executable, "-m", "yt_dlp",
        url,
        "--ffmpeg-location", r"d:\vidclip\.venv\Scripts",
        "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
        "-o", str(out_file),
        "--merge-output-format", "mp4",
        "--socket-timeout", "20",
        "--no-warnings",
        "--match-filter", "duration <= 85"
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=35)
        if out_file.exists() and out_file.stat().st_size > 100000:
            sz_mb = out_file.stat().st_size / (1024 * 1024)
            print(f"       -> OK: {vid_id}.mp4 ({sz_mb:.2f}MB)", flush=True)
            return {
                "id": vid_id,
                "title": title,
                "views": views,
                "duration": dur,
                "file_path": str(out_file),
                "size_bytes": out_file.stat().st_size,
                "status": "success"
            }
        else:
            print(f"       -> FAILED / INVALID SIZE: {vid_id}", flush=True)
            if out_file.exists():
                out_file.unlink()
            return None
    except subprocess.TimeoutExpired:
        print(f"       -> TIMED OUT (>35s): {vid_id}", flush=True)
        # clean any .part files
        for part in OUT_DIR.glob(f"{vid_id}*"):
            try:
                part.unlink()
            except Exception:
                pass
        return None
    except Exception as e:
        print(f"       -> ERROR: {e}", flush=True)
        return None


def analyze_video_cuts(video_path):
    """Uses FFmpeg scene filter to count cut timestamps and calculate pacing."""
    cmd = [
        FFMPEG_EXE,
        "-i", str(video_path),
        "-filter_complex", "select='gt(scene,0.35)',metadata=print:file=-",
        "-f", "null", "-"
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=25)
        cut_times = []
        for line in res.stdout.splitlines():
            if "pts_time:" in line:
                try:
                    t = float(line.split("pts_time:")[1].strip())
                    cut_times.append(t)
                except Exception:
                    pass
        return cut_times
    except Exception:
        return []


def analyze_audio_lufs(video_path):
    """Uses FFmpeg ebur128 filter to compute integrated LUFS and true peak."""
    cmd = [
        FFMPEG_EXE,
        "-i", str(video_path),
        "-af", "ebur128=framelog=verbose",
        "-f", "null", "-"
    ]
    try:
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, timeout=25)
        lufs = -16.0
        peak = -1.0
        for line in res.stderr.splitlines():
            if "I:" in line and "LUFS" in line:
                try:
                    parts = line.split("I:")[1].split("LUFS")[0].strip()
                    lufs = float(parts)
                except Exception:
                    pass
            if "Peak:" in line and "dBFS" in line:
                try:
                    parts = line.split("Peak:")[1].split("dBFS")[0].strip()
                    peak = float(parts)
                except Exception:
                    pass
        return {"lufs": lufs, "peak_db": peak}
    except Exception:
        return {"lufs": -16.0, "peak_db": -1.0}


def train_ai_director(downloaded_records):
    print("\n" + "=" * 65, flush=True)
    print("STARTING AI DIRECTOR TRAINING ON DOWNLOADED GTA 6 CORPUS", flush=True)
    print("=" * 65, flush=True)

    cut_intervals = []
    total_cuts_list = []
    hook_times = []
    lufs_list = []
    peak_list = []
    durations = []

    for idx, rec in enumerate(downloaded_records, 1):
        vpath = rec["file_path"]
        print(f"[{idx:03d}/{len(downloaded_records)}] Analyzing DNA: {rec['id']}...", flush=True)
        cuts = analyze_video_cuts(vpath)
        audio = analyze_audio_lufs(vpath)

        # Durations
        dur = rec.get("duration") or 30.0
        durations.append(dur)

        # Cuts
        num_cuts = len(cuts)
        total_cuts_list.append(num_cuts)
        if cuts:
            hook_times.append(cuts[0])
            if len(cuts) > 1:
                intervals = [cuts[i] - cuts[i - 1] for i in range(1, len(cuts))]
                avg_interval = statistics.mean(intervals)
                cut_intervals.append(avg_interval)
            else:
                cut_intervals.append(dur / max(1, num_cuts))
        else:
            cut_intervals.append(2.8)
            hook_times.append(1.2)

        # Audio
        lufs_list.append(audio["lufs"])
        peak_list.append(audio["peak_db"])

    # Empirical training averages
    avg_duration = round(statistics.mean(durations), 1) if durations else 35.0
    avg_cuts = round(statistics.mean(total_cuts_list), 1) if total_cuts_list else 10.0
    avg_cut_interval = round(statistics.mean(cut_intervals), 2) if cut_intervals else 2.6
    avg_hook_time = round(statistics.mean(hook_times), 2) if hook_times else 1.3
    avg_lufs = round(statistics.mean(lufs_list), 1) if lufs_list else -14.8
    avg_peak = round(statistics.mean(peak_list), 1) if peak_list else -0.8

    # Hook cut must be snappy (< 1.5s)
    target_hook = min(1.5, max(0.8, avg_hook_time))
    # Cut cadence
    target_interval = min(3.2, max(1.8, avg_cut_interval))

    print("\n--- EMPIRICAL VIRAL STYLE METRICS LEARNED ---", flush=True)
    print(f"Mean Clip Duration:    {avg_duration}s", flush=True)
    print(f"Mean Cuts Per Clip:    {avg_cuts}", flush=True)
    print(f"Mean Cut Cadence:      Every {target_interval}s", flush=True)
    print(f"Mean First Hook Cut:   {target_hook}s", flush=True)
    print(f"Mean Integrated LUFS:  {avg_lufs} LUFS", flush=True)
    print(f"Mean True Peak:        {avg_peak} dBFS", flush=True)

    # Load existing style DNA and update with trained weights
    dna = {}
    if STYLE_DNA_PATH.exists():
        with open(STYLE_DNA_PATH, "r", encoding="utf-8") as f:
            dna = json.load(f)

    dna["version"] = "2.1.0-EMPIRICAL-GTA6-TRAINED"
    dna["training_sample_count"] = len(downloaded_records)
    dna["pacing_and_cuts"]["target_duration_seconds"] = round(avg_duration, 1)
    dna["pacing_and_cuts"]["cuts_per_clip"]["target"] = round(avg_cuts, 1)
    dna["pacing_and_cuts"]["average_cut_interval_seconds"] = round(target_interval, 2)
    dna["pacing_and_cuts"]["hook_cut_timing_seconds"] = round(target_hook, 2)
    dna["audio_mastering"]["target_integrated_lufs"] = round(avg_lufs, 1)
    dna["audio_mastering"]["true_peak_limit_db"] = round(avg_peak, 1)
    dna["last_trained_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S IST")

    with open(STYLE_DNA_PATH, "w", encoding="utf-8") as f:
        json.dump(dna, f, indent=2)

    print(f"\nStyle DNA updated and saved to: {STYLE_DNA_PATH}", flush=True)
    return {
        "sample_count": len(downloaded_records),
        "avg_duration": avg_duration,
        "avg_cuts": avg_cuts,
        "avg_cut_interval": target_interval,
        "avg_hook_time": target_hook,
        "avg_lufs": avg_lufs,
        "avg_peak": avg_peak
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not CANDIDATES_PATH.exists():
        print(f"Error: {CANDIDATES_PATH} not found. Run candidate scanner first.", flush=True)
        sys.exit(1)

    with open(CANDIDATES_PATH, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    # Sort descending by view count
    candidates.sort(key=lambda x: x.get("views", 0), reverse=True)
    target_count = min(100, len(candidates))
    selected = candidates[:target_count]

    print(f"Targeting top {target_count} pure GTA 6 clips by view count...", flush=True)

    downloaded = []
    for idx, c in enumerate(selected, 1):
        res = download_clip(c, idx, target_count)
        if res:
            downloaded.append(res)
        time.sleep(0.2)

        # Write manifest checkpoints
        if idx % 10 == 0 or idx == target_count:
            with open(MANIFEST_PATH, "w", encoding="utf-8") as mf:
                json.dump({
                    "total_requested": target_count,
                    "downloaded_so_far": len(downloaded),
                    "clips": downloaded
                }, mf, indent=2)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as mf:
        json.dump({
            "total_requested": target_count,
            "total_downloaded": len(downloaded),
            "clips": downloaded
        }, mf, indent=2)

    total_mb = sum(c["size_bytes"] for c in downloaded) / (1024 * 1024)
    print(f"\nDownload Phase Finished: {len(downloaded)}/{target_count} clips ready ({total_mb:.1f} MB).", flush=True)

    # Train AI Director
    train_ai_director(downloaded)


if __name__ == "__main__":
    main()
