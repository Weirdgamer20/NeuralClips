"""Global Highlight Ranker and Deduplication Engine."""

import uuid
from typing import Any, Dict, List, Optional
from core.logging_config import setup_logger
from core.state_store import StateStore

logger = setup_logger("neuralclips.highlight_ranker")


def calculate_overlap_seconds(start1: float, end1: float, start2: float, end2: float) -> float:
    """Calculates temporal overlap between two intervals."""
    overlap = max(0.0, min(end1, end2) - max(start1, start2))
    return overlap


class HighlightRanker:
    """Ranks candidates globally across all sources and filters duplicates."""

    def __init__(self, state_store: Optional[StateStore] = None):
        self.state_store = state_store or StateStore()

    def rank_and_select(
        self,
        min_score: float = 75.0,
        max_daily_clips: int = 100,
        max_overlap_seconds: float = 15.0,
    ) -> List[Dict[str, Any]]:
        """Selects up to max_daily_clips globally ranked candidates."""
        candidates = self.state_store.get_unapproved_candidates(min_score=min_score)
        if not candidates:
            return []

        # Sort globally by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)

        selected_candidates: List[Dict[str, Any]] = []

        for cand in candidates:
            # Check overlap against already selected candidates from the same source
            overlap_detected = False
            for sel in selected_candidates:
                if sel["source_id"] == cand["source_id"]:
                    overlap = calculate_overlap_seconds(
                        cand["start_timestamp"],
                        cand["end_timestamp"],
                        sel["start_timestamp"],
                        sel["end_timestamp"],
                    )
                    if overlap > max_overlap_seconds:
                        overlap_detected = True
                        break

            if not overlap_detected:
                selected_candidates.append(cand)

            if len(selected_candidates) >= max_daily_clips:
                break

        # Register approved highlights in database
        approved_list = []
        for rank, cand in enumerate(selected_candidates, start=1):
            highlight_id = f"hl_{cand['source_id']}_{int(cand['start_timestamp'])}_{uuid.uuid4().hex[:6]}"
            self.state_store.approve_highlight(
                highlight_id=highlight_id,
                candidate_id=cand["candidate_id"],
                source_id=cand["source_id"],
                start_ts=cand["start_timestamp"],
                end_ts=cand["end_timestamp"],
                score=cand["score"],
                category=cand["category"],
                title=cand.get("suggested_title", "Gaming Highlight"),
                transcript=cand.get("transcript", ""),
                rank_order=rank,
            )
            approved_list.append({"highlight_id": highlight_id, "score": cand["score"], "rank": rank})

        logger.info(f"Approved {len(approved_list)} highlights (threshold: {min_score}, cap: {max_daily_clips})")
        return approved_list
