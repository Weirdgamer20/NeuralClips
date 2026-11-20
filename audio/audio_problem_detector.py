"""Audio Problem Detector for NeuralClips.

Detects clipping/distortion, inaudible volume levels, excessive dead air silence,
and dynamic range imbalances across audio tracks. Provides automated correction
filter strings.
"""

import os
import re
import subprocess
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
import imageio_ffmpeg
from core.logging_config import setup_logger

logger = setup_logger("neuralclips.audio_problem_detector")


@dataclass
class AudioProblemReport:
    """Comprehensive diagnosis of audio quality and defects."""
    has_problems: bool = False
    has_audio_track: bool = True
    integrated_lufs: float = -24.0
    max_volume_db: float = -6.0
    mean_volume_db: float = -20.0
    is_clipping: bool = False
    is_too_quiet: bool = False
    is_too_loud: bool = False
    has_excessive_silence: bool = False
    silence_intervals: List[Dict[str, float]] = field(default_factory=list)
    problems: List[str] = field(default_factory=list)
    recommended_filter: Optional[str] = None


class AudioProblemDetector:
    """Analyzes media files for audio defects and platform volume compliance."""

    # YouTube Shorts target: -14 LUFS, max true peak -1.0 dBFS
    TARGET_LUFS = -14.0
    MIN_ACCEPTABLE_LUFS = -28.0  # Quieter than this is hard to hear on phones
    MAX_ACCEPTABLE_LUFS = -9.0   # Louder than this sounds blown out/distorted
    MAX_PERMISSIBLE_PEAK_DB = -0.2  # 0 dBFS or near it indicates digital clipping
    MAX_ALLOWED_SILENCE_SEC = 3.5   # Silence longer than 3.5s hurts retention

    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg_path = ffmpeg_path or imageio_ffmpeg.get_ffmpeg_exe()

    def analyze_audio(self, media_path: str) -> AudioProblemReport:
        """Runs audio diagnostics on a video or audio file."""
        if not os.path.exists(media_path):
            return AudioProblemReport(
                has_problems=True,
                has_audio_track=False,
                problems=[f"File does not exist: {media_path}"]
            )

        # 1. Check volume stats (mean_volume, max_volume, clipping histogram)
        vol_stats = self._run_volume_detect(media_path)
        if not vol_stats.get("has_audio", True):
            return AudioProblemReport(
                has_problems=True,
                has_audio_track=False,
                problems=["No audio stream present in media file"]
            )

        # 2. Check EBU R128 integrated loudness (LUFS)
        lufs_val = self._run_ebur128(media_path)

        # 3. Check for prolonged dead-air silence
        silences = self._detect_silence(media_path)

        # 4. Formulate diagnostic report
        report = AudioProblemReport(
            has_audio_track=True,
            integrated_lufs=lufs_val,
            max_volume_db=vol_stats.get("max_volume", -6.0),
            mean_volume_db=vol_stats.get("mean_volume", -20.0),
            silence_intervals=silences
        )

        # Check clipping
        if vol_stats.get("max_volume", -6.0) >= self.MAX_PERMISSIBLE_PEAK_DB or vol_stats.get("clipping_samples", 0) > 0:
            report.is_clipping = True
            report.problems.append(
                f"Digital clipping / distortion detected (peak: {report.max_volume_db:.1f} dBFS, "
                f"samples at 0dB: {vol_stats.get('clipping_samples', 0)})"
            )

        # Check inaudible / too quiet
        if lufs_val < self.MIN_ACCEPTABLE_LUFS or vol_stats.get("mean_volume", -20.0) < -34.0:
            report.is_too_quiet = True
            report.problems.append(
                f"Audio is too quiet for mobile playback (Loudness: {lufs_val:.1f} LUFS, "
                f"mean: {report.mean_volume_db:.1f} dB; threshold: {self.MIN_ACCEPTABLE_LUFS} LUFS)"
            )

        # Check too loud / blown out
        if lufs_val > self.MAX_ACCEPTABLE_LUFS:
            report.is_too_loud = True
            report.problems.append(
                f"Audio is excessively loud / blown out ({lufs_val:.1f} LUFS; threshold: {self.MAX_ACCEPTABLE_LUFS} LUFS)"
            )

        # Check prolonged dead air
        long_silences = [s for s in silences if (s["end"] - s["start"]) >= self.MAX_ALLOWED_SILENCE_SEC]
        if long_silences:
            report.has_excessive_silence = True
            max_silence = max(s["end"] - s["start"] for s in long_silences)
            report.problems.append(
                f"Dead air detected: {len(long_silences)} silence gaps exceeding {self.MAX_ALLOWED_SILENCE_SEC}s "
                f"(longest: {max_silence:.1f}s)"
            )

        report.has_problems = len(report.problems) > 0

        # Suggest remedial filter
        if report.has_problems:
            filters = []
            if report.is_clipping:
                filters.append("alimiter=limit=-1.5dB:attack=5:release=50")
            if report.is_too_quiet or report.is_too_loud:
                filters.append("loudnorm=I=-14:TP=-1.5:LRA=7")
            report.recommended_filter = ",".join(filters) if filters else "loudnorm=I=-14:TP=-1.5:LRA=7"
            logger.warning(f"Audio problems identified in {os.path.basename(media_path)}: {report.problems}")
        else:
            logger.info(f"Audio clean for {os.path.basename(media_path)} ({lufs_val:.1f} LUFS, peak: {report.max_volume_db:.1f} dBFS)")

        return report

    def _run_volume_detect(self, file_path: str) -> Dict[str, Any]:
        """Runs FFmpeg volumedetect filter to extract max, mean, and 0dB clipping."""
        cmd = [
            self.ffmpeg_path,
            "-i", file_path,
            "-af", "volumedetect",
            "-f", "null",
            "-"
        ]
        try:
            res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, timeout=45)
            stderr = res.stderr
            if "Output file does not contain any stream" in stderr or "does not contain any audio" in stderr:
                return {"has_audio": False}

            max_vol = -6.0
            mean_vol = -20.0
            clip_0db = 0

            m_max = re.search(r"max_volume:\s*([-\d.]+)\s*dB", stderr)
            if m_max:
                max_vol = float(m_max.group(1))

            m_mean = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", stderr)
            if m_mean:
                mean_vol = float(m_mean.group(1))

            m_clip = re.search(r"histogram_0db:\s*(\d+)", stderr)
            if m_clip:
                clip_0db = int(m_clip.group(1))

            return {
                "has_audio": True,
                "max_volume": max_vol,
                "mean_volume": mean_vol,
                "clipping_samples": clip_0db
            }
        except Exception as e:
            logger.error(f"Failed volume detect on {file_path}: {e}")
            return {"has_audio": True, "max_volume": -6.0, "mean_volume": -20.0, "clipping_samples": 0}

    def _run_ebur128(self, file_path: str) -> float:
        """Measures EBU R128 integrated loudness in LUFS."""
        cmd = [
            self.ffmpeg_path,
            "-i", file_path,
            "-af", "ebur128",
            "-f", "null",
            "-"
        ]
        try:
            res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, timeout=45)
            stderr = res.stderr
            # Look for "I:\s+([-\d.]+)\s+LUFS" in the Summary block
            m = re.search(r"I:\s*([-\d.]+)\s*LUFS", stderr)
            if m:
                return float(m.group(1))
            return -22.0
        except Exception as e:
            logger.error(f"Failed ebur128 on {file_path}: {e}")
            return -22.0

    def _detect_silence(self, file_path: str, noise_thresh: str = "-38dB", min_dur: float = 2.0) -> List[Dict[str, float]]:
        """Finds silence intervals where audio drops below threshold."""
        cmd = [
            self.ffmpeg_path,
            "-i", file_path,
            "-af", f"silencedetect=noise={noise_thresh}:d={min_dur}",
            "-f", "null",
            "-"
        ]
        try:
            res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, timeout=45)
            silences = []
            cur_start = None
            for line in res.stderr.splitlines():
                if "silence_start:" in line:
                    m = re.search(r"silence_start:\s*([-\d.]+)", line)
                    if m:
                        cur_start = float(m.group(1))
                elif "silence_end:" in line and cur_start is not None:
                    m = re.search(r"silence_end:\s*([-\d.]+)", line)
                    if m:
                        cur_end = float(m.group(1))
                        silences.append({"start": round(cur_start, 2), "end": round(cur_end, 2)})
                        cur_start = None
            return silences
        except Exception as e:
            logger.error(f"Failed silence detect on {file_path}: {e}")
            return []
