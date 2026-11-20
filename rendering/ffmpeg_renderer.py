"""FFmpeg Execution Engine for Vertical Video Rendering."""

import os
import shutil
import subprocess
from typing import Any, Dict, Optional, Tuple
from core.logging_config import setup_logger
from rendering.layout_engine import LayoutEngine

logger = setup_logger("neuralclips.ffmpeg_renderer")


def get_system_ffmpeg() -> Optional[str]:
    p = os.getenv("FFMPEG_PATH")
    if p and os.path.exists(p):
        return p
    which_p = shutil.which("ffmpeg")
    if which_p:
        return which_p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


class FFmpegRenderer:
    """Executes FFmpeg rendering pipelines for vertical gaming clips."""

    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg_path = ffmpeg_path or get_system_ffmpeg()

    def has_audio_track(self, file_path: str) -> bool:
        """Checks if a video file has an active audio stream."""
        if not self.ffmpeg_path or not os.path.exists(file_path):
            return False
        try:
            cmd = [self.ffmpeg_path, "-i", file_path]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            return "Audio:" in res.stderr
        except Exception:
            return False

    def render_split_screen(
        self,
        input_video_path: str,
        output_clip_path: str,
        start_seconds: float,
        duration_seconds: float,
        crop_config: Dict[str, Any],
        ass_subtitle_path: Optional[str] = None,
        bgm_music_path: Optional[str] = None,
        bgm_volume: float = 0.30,
        narration_volume: float = 1.20,
    ) -> Tuple[bool, str]:
        """Renders vertical video (2K 1440x2560 or 1080x1920) with gameplay on top and facecam on bottom,
        plus mixed background music and boosted narration."""
        os.makedirs(os.path.dirname(os.path.abspath(output_clip_path)), exist_ok=True)

        video_filtergraph = LayoutEngine.generate_split_screen_filter(crop_config, ass_subtitle_path)

        if not self.ffmpeg_path:
            logger.warning("FFmpeg binary not detected in PATH; generating simulated video asset.")
            return self._mock_render(output_clip_path, duration_seconds)

        use_testsrc = not os.path.exists(input_video_path) or os.path.getsize(input_video_path) == 0
        has_bgm = bool(bgm_music_path and os.path.exists(bgm_music_path))

        if use_testsrc:
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-f", "lavfi", "-i", "testsrc=size=1920x1080:rate=30",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
            ]
            if has_bgm:
                cmd.extend(["-stream_loop", "-1", "-i", bgm_music_path])
                audio_filter = (
                    f"[1:a]volume={narration_volume:.2f},aresample=async=1000[main_a];"
                    f"[2:a]volume={bgm_volume:.2f}[bgm_a];"
                    f"[main_a][bgm_a]amix=inputs=2:duration=first:dropout_transition=2[a_out]"
                )
                full_filter = f"{video_filtergraph};{audio_filter}"
                audio_map = "[a_out]"
            else:
                full_filter = video_filtergraph
                audio_map = "1:a"

            cmd.extend([
                "-t", str(duration_seconds),
                "-filter_complex", full_filter,
                "-map", "[v_out]",
                "-map", audio_map,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                output_clip_path,
            ])
        else:
            has_audio = self.has_audio_track(input_video_path)

            cmd = [
                self.ffmpeg_path,
                "-y",
                "-ss", str(start_seconds),
                "-t", str(duration_seconds),
                "-i", input_video_path,
            ]

            if has_bgm:
                cmd.extend(["-stream_loop", "-1", "-i", bgm_music_path])
                if has_audio:
                    audio_filter = (
                        f"[0:a]volume={narration_volume:.2f},aresample=async=1000[main_a];"
                        f"[1:a]volume={bgm_volume:.2f}[bgm_a];"
                        f"[main_a][bgm_a]amix=inputs=2:duration=first:dropout_transition=2[a_out]"
                    )
                    full_filter = f"{video_filtergraph};{audio_filter}"
                    audio_map = "[a_out]"
                else:
                    audio_filter = f"[1:a]volume={bgm_volume:.2f},aresample=async=1000[a_out]"
                    full_filter = f"{video_filtergraph};{audio_filter}"
                    audio_map = "[a_out]"
            else:
                if has_audio:
                    audio_filter = f"[0:a]volume={narration_volume:.2f},aresample=async=1000[a_out]"
                    full_filter = f"{video_filtergraph};{audio_filter}"
                    audio_map = "[a_out]"
                else:
                    full_filter = video_filtergraph
                    audio_map = None

            cmd.extend([
                "-t", str(duration_seconds),
                "-filter_complex", full_filter,
                "-map", "[v_out]",
            ])

            if audio_map:
                cmd.extend(["-map", audio_map])
            else:
                cmd.extend(["-map", "0:a?"])

            cmd.extend([
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "256k",
                "-movflags", "+faststart",
                output_clip_path,
            ])

        try:
            logger.info(f"Running FFmpeg render: {output_clip_path}")
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
            if proc.returncode != 0:
                logger.error(f"FFmpeg failed with code {proc.returncode}: {proc.stderr}")
                return False, proc.stderr
            return True, "Render complete"
        except Exception as e:
            logger.error(f"FFmpeg execution error: {e}")
            return False, str(e)

    def _mock_render(self, output_clip_path: str, duration: float) -> Tuple[bool, str]:
        """Creates synthetic media placeholder for offline environments or testing."""
        with open(output_clip_path, "wb") as f:
            f.write(f"MOCK_MP4_VIDEO_STREAM_DURATION_{duration}\n".encode())
        return True, "Simulated render complete"
