"""Highlight Detector orchestrating segment analysis."""

from typing import Any, Dict, List, Optional
from ai.gemini_client import GeminiClient
from core.logging_config import setup_logger
from core.state_store import StateStore

logger = setup_logger("neuralclips.highlight_detector")


class HighlightDetector:
    """Dispatches media segments to Gemini AI and records candidates."""

    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        state_store: Optional[StateStore] = None,
    ):
        self.client = gemini_client or GeminiClient()
        self.state_store = state_store or StateStore()

    def process_segment(self, segment: Dict[str, Any]) -> List[str]:
        """Analyzes a single media segment and records detected highlight candidates."""
        candidates = self.client.analyze_segment(
            source_id=segment["source_id"],
            segment_id=segment["segment_id"],
            start_offset=float(segment["start_time"]),
            duration=float(segment["duration"]),
            video_path=segment.get("file_path"),
        )

        candidate_ids = []
        for cand in candidates:
            # Validate duration boundaries 30 to 60 seconds
            dur = cand["end_timestamp"] - cand["start_timestamp"]
            if dur < 30.0 or dur > 60.0:
                logger.debug(f"Candidate duration {dur}s outside [30, 60]s window; skipping.")
                continue

            cand_id = self.state_store.add_highlight_candidate(cand)
            candidate_ids.append(cand_id)

        # Mark segment analyzed
        self.state_store.mark_segment_analyzed(segment["segment_id"])
        return candidate_ids
