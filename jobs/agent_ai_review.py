"""JOB D-AGENT: Direct Antigravity Agent AI Review and Ingestion."""

import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from typing import Any, Dict, List
from ai.agent_evaluator import AgentEvaluator
from ai.video_analyzer import VideoAnalyzer
from core.database import init_database
from core.logging_config import setup_logger
from core.state_store import StateStore

logger = setup_logger("neuralclips.jobs.agent_ai_review")


def export_segments_for_agent(output_file: str = "data/agent_review_input.json") -> int:
    """Exports all unanalyzed segments for direct review by Antigravity."""
    state_store = StateStore()
    segments = state_store.get_unanalyzed_segments(limit=100)
    out_path = os.path.join(BASE_DIR, output_file)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([dict(s) for s in segments], f, indent=2)

    logger.info(f"Exported {len(segments)} unanalyzed segments to {out_path} for Agent AI analysis.")
    print(f"Exported {len(segments)} segments to {out_path}")
    return len(segments)


def import_agent_highlights(input_file: str = "data/agent_review_results.json") -> int:
    """Ingests highlights created or reviewed directly by Antigravity."""
    in_path = os.path.join(BASE_DIR, input_file)
    if not os.path.exists(in_path):
        print(f"Input file not found: {in_path}")
        return 0

    with open(in_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    state_store = StateStore()
    inserted = 0
    for cand in candidates:
        if cand.get("score", 0) >= 75:
            state_store.add_highlight_candidate(cand)
            inserted += 1

    logger.info(f"Imported {inserted} qualifying highlight candidates from Agent AI review.")
    print(f"Imported {inserted} qualifying highlight candidates.")
    return inserted


def run_agent_auto_analysis(min_score: float = 75.0, max_clips: int = 100) -> Dict[str, int]:
    """Runs autonomous Agent AI highlight evaluation on all pending segments."""
    init_database()
    analyzer = VideoAnalyzer()
    cands = analyzer.process_pending_segments(batch_size=100)
    approved = analyzer.rank_approved_highlights(min_score=min_score, max_clips=max_clips)
    print(f"Agent AI Analysis Complete: {cands} candidates evaluated, {len(approved)} approved (score >= {min_score}).")
    return {"candidates": cands, "approved": len(approved)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Agent AI Review")
    parser.add_argument("--export", action="store_true", help="Export unanalyzed segments to JSON for Agent inspection")
    parser.add_argument("--import-file", dest="import_file", help="Import evaluated highlights JSON into database")
    parser.add_argument("--auto", action="store_true", help="Run automated Agent AI evaluation directly")
    args = parser.parse_args()

    if args.export:
        export_segments_for_agent()
    elif args.import_file:
        import_agent_highlights(args.import_file)
    else:
        run_agent_auto_analysis()
