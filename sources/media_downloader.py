"""Media Downloader for YouTube stream slices via yt-dlp."""

import os
import shutil
from typing import Optional
import yt_dlp
from core.logging_config import setup_logger

logger = setup_logger("neuralclips.media_downloader")


class MediaDownloader:
    """Downloads target time ranges from YouTube streams using yt-dlp."""

    @staticmethod
    def download_range(
        url: str,
        output_path: str,
        start_sec: float,
        end_sec: float,
        ffmpeg_path: Optional[str] = None,
    ) -> bool:
        """Downloads exact time range [start_sec, end_sec] from a YouTube video/stream."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            return True

        ffmpeg_bin = ffmpeg_path or shutil.which("ffmpeg") or r"d:\vidclip\.venv\Scripts\ffmpeg.exe"
        ffmpeg_dir = os.path.dirname(ffmpeg_bin) if os.path.isfile(ffmpeg_bin) else ffmpeg_bin
        if ffmpeg_dir and ffmpeg_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

        ydl_opts = {
            "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": output_path,
            "download_ranges": yt_dlp.utils.download_range_func(None, [(start_sec, end_sec)]),
            "force_keyframes_at_cuts": True,
            "ffmpeg_location": ffmpeg_dir,
            "quiet": True,
            "no_warnings": True,
        }

        try:
            logger.info(f"Downloading stream range {start_sec}s-{end_sec}s from {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return os.path.exists(output_path) and os.path.getsize(output_path) > 100000
        except Exception as e:
            logger.error(f"Failed to download stream slice: {e}")
            return False
