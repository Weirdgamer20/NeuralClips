"""JOB E: Clip Renderer.

Claims approved highlights, extracts 30-60s footage, renders split-screen vertical video, and validates.
"""

from typing import Dict, Optional
from core.job_manager import JobManager
from core.logging_config import setup_logger
from core.state_store import StateStore
from rendering.clip_extractor import ClipExtractor

logger = setup_logger("neuralclips.jobs.render_clips")


def run_renderer(max_renders: int = 10, db_path: Optional[str] = None) -> Dict[str, int]:
    state_store = StateStore(db_path)
    job_manager = JobManager(db_path=db_path)
    extractor = ClipExtractor(state_store=state_store)

    rendered_count = 0
    failures = 0

    for _ in range(max_renders):
        highlight = job_manager.claim_approved_highlight()
        if not highlight:
            break

        res = extractor.produce_clip(highlight)
        if res.get("success"):
            rendered_count += 1
        else:
            failures += 1

    logger.info(f"Render job finished: {rendered_count} clips rendered, {failures} failures.")
    return {"rendered": rendered_count, "failures": failures}


if __name__ == "__main__":
    run_renderer()
