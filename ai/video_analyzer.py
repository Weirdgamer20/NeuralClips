"""Video analysis orchestrator."""

from typing import Dict, List, Optional
from ai.highlight_detector import HighlightDetector
from ai.highlight_ranker import HighlightRanker
from core.logging_config import setup_logger
from core.state_store import StateStore

logger = setup_logger("neuralclips.video_analyzer")


class VideoAnalyzer:
    """Orchestrates video segment analysis and highlight ranking."""

    def __init__(
        self,
        detector: Optional[HighlightDetector] = None,
        ranker: Optional[HighlightRanker] = None,
        state_store: Optional[StateStore] = None,
    ):
        self.detector = detector or HighlightDetector()
        self.ranker = ranker or HighlightRanker()
        self.state_store = state_store or StateStore()

    def process_pending_segments(self, batch_size: int = 20) -> int:
        """Finds unanalyzed segments, runs Gemini detection, and marks them analyzed."""
        segments = self.state_store.get_unanalyzed_segments(limit=batch_size)
        if not segments:
            logger.info("No unanalyzed media segments found.")
            return 0

        total_candidates = 0
        for seg in segments:
            candidate_ids = self.detector.process_segment(seg)
            total_candidates += len(candidate_ids)

        logger.info(f"Analyzed {len(segments)} segments; detected {total_candidates} candidates.")
        return total_candidates

    def rank_approved_highlights(self, min_score: float = 75.0, max_clips: int = 100) -> List[Dict]:
        """Runs global ranking on all pending highlight candidates."""
        return self.ranker.rank_and_select(min_score=min_score, max_daily_clips=max_clips)
