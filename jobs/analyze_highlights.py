"""JOB D: Gemini Analyzer and Highlight Evaluator.

Analyzes footage, identifies gaming moments, scores candidates, and approves highlights.
"""

from typing import Dict, Optional
from ai.video_analyzer import VideoAnalyzer
from core.logging_config import setup_logger
from core.state_store import StateStore

logger = setup_logger("neuralclips.jobs.analyze_highlights")


def run_analyzer(min_score: float = 75.0, max_clips: int = 100, db_path: Optional[str] = None) -> Dict[str, int]:
    state_store = StateStore(db_path)
    analyzer = VideoAnalyzer(state_store=state_store)

    # 1. Process unanalyzed segments
    candidates_count = analyzer.process_pending_segments(batch_size=50)

    # 2. Run ranking and selection
    approved = analyzer.rank_approved_highlights(min_score=min_score, max_clips=max_clips)

    logger.info(f"Analyzer step completed: {candidates_count} candidates detected, {len(approved)} approved.")
    return {"candidates_detected": candidates_count, "approved_highlights": len(approved)}


if __name__ == "__main__":
    run_analyzer()
