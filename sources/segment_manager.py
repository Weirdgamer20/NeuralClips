"""Storage and indexing of media segments."""

import os
from typing import Dict, List, Optional
from core.state_store import StateStore


class SegmentManager:
    """Manages file storage, naming, and retrieval of media segments."""

    def __init__(self, storage_dir: Optional[str] = None, state_store: Optional[StateStore] = None):
        if not storage_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            storage_dir = os.path.join(base_dir, "storage", "segments")
        self.storage_dir = storage_dir
        self.state_store = state_store or StateStore()
        os.makedirs(self.storage_dir, exist_ok=True)

    def get_source_segment_dir(self, source_id: str) -> str:
        d = os.path.join(self.storage_dir, source_id)
        os.makedirs(d, exist_ok=True)
        return d

    def record_segment(
        self,
        source_id: str,
        segment_index: int,
        file_path: str,
        start_time: float,
        end_time: float,
    ) -> str:
        """Registers a completed media segment."""
        segment_id = f"seg_{source_id}_{segment_index:04d}"
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        self.state_store.add_segment(
            segment_id=segment_id,
            source_id=source_id,
            segment_index=segment_index,
            file_path=file_path,
            start_time=start_time,
            end_time=end_time,
            file_size_bytes=file_size,
        )
        return segment_id

    def list_unanalyzed_segments(self, limit: int = 50) -> List[Dict]:
        return self.state_store.get_unanalyzed_segments(limit)

    def mark_analyzed(self, segment_id: str) -> None:
        self.state_store.mark_segment_analyzed(segment_id)
