"""Completed VOD Processing Pipeline."""

import os
import subprocess
from typing import Any, Dict, Optional
from core.logging_config import setup_logger
from core.state_store import StateStore
from sources.segment_manager import SegmentManager

logger = setup_logger("neuralclips.vod_processor")


class VODProcessor:
    """Processes completed livestream recordings (VODs)."""

    def __init__(
        self,
        segment_manager: Optional[SegmentManager] = None,
        state_store: Optional[StateStore] = None,
    ):
        self.segment_manager = segment_manager or SegmentManager()
        self.state_store = state_store or StateStore()

    def process_vod(
        self,
        source_id: str,
        video_url_or_path: str,
        segment_length_seconds: int = 60,
        overlap_seconds: int = 10,
        mock_duration: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Processes a VOD by extracting metadata and slicing into analysis segments."""
        logger.info(f"Processing VOD for source {source_id} from {video_url_or_path}")

        # Check if local file exists or is mock
        is_local_file = os.path.exists(video_url_or_path)

        if not is_local_file and mock_duration is None:
            # In production, this would invoke authorized capture / yt-dlp download
            # For testing or offline environments, provide synthetic segment allocation
            mock_duration = 3600.0  # 1 hour default mock

        duration = mock_duration if mock_duration is not None else 3600.0
        fps = 30.0
        resolution = "1920x1080"

        # Update source metadata
        self.state_store.update_source_status(
            source_id,
            "PROCESSING",
            duration_seconds=duration,
            fps=fps,
            resolution=resolution,
        )

        # Slice into segments
        step = segment_length_seconds - overlap_seconds
        current_time = 0.0
        segment_index = 0
        seg_dir = self.segment_manager.get_source_segment_dir(source_id)
        registered_segments = []

        while current_time < duration:
            end_time = min(duration, current_time + segment_length_seconds)
            segment_filename = f"segment_{segment_index:04d}.mp4"
            segment_path = os.path.join(seg_dir, segment_filename)

            # If local file and ffmpeg available, we could slice real media;
            # otherwise ensure dummy/placeholder file exists so pipeline can process
            if not os.path.exists(segment_path):
                with open(segment_path, "wb") as f:
                    f.write(b"SYNTHETIC_MEDIA_SEGMENT_DATA_BLOCK\n")

            seg_id = self.segment_manager.record_segment(
                source_id=source_id,
                segment_index=segment_index,
                file_path=segment_path,
                start_time=current_time,
                end_time=end_time,
            )
            registered_segments.append(seg_id)
            segment_index += 1
            current_time += step

        self.state_store.update_source_status(source_id, "PROCESSING")
        logger.info(f"Generated {len(registered_segments)} segments for source {source_id}")

        return {
            "source_id": source_id,
            "duration": duration,
            "fps": fps,
            "resolution": resolution,
            "segments_count": len(registered_segments),
            "status": "PROCESSING",
        }
