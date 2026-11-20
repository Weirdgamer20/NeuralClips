"""Antigravity AI Video Editor Agent (AI Director).

Directs the video editing process by applying learned Viral Style DNA,
pinpointing exact cut moments, explaining the editorial rationale for each cut,
and choreographing dynamic FFmpeg filter effects and kinetic captions.
"""

import json
import math
import os
import random
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
from ai.cut_detector import CutDetector, CutMoment
from ai.style_dna_extractor import StyleDNAExtractor
from core.logging_config import setup_logger

logger = setup_logger("neuralclips.ai_director")


@dataclass
class EditorialCutDecision:
    """Detailed record of an editorial cut decision made by the AI Agent."""
    cut_index: int
    timestamp_seconds: float
    moment_type: str
    trigger_event: str
    editorial_reason: str
    visual_effect: str
    energy_rating: float


class AIVideoDirector:
    """The Antigravity AI Video Editor Agent.
    
    Transforms raw gaming stream highlights into viral 2K Shorts by determining
    optimal cut points, explaining the moment of each cut, and applying the
    learned Viral Style DNA.
    """

    def __init__(self, style_dna_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.style_dna_path = style_dna_path or os.path.join(base_dir, "storage", "viral_style_dna.json")
        self.cut_detector = CutDetector()
        self.style_dna = self._load_style_dna()

    def _load_style_dna(self) -> Dict[str, Any]:
        """Loads learned style DNA or extracts it if missing."""
        if os.path.exists(self.style_dna_path):
            try:
                with open(self.style_dna_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading style DNA: {e}")
        extractor = StyleDNAExtractor(self.style_dna_path)
        return extractor.extract_dna_from_corpus()

    def direct_clip_edit(
        self,
        video_path: str,
        highlight_title: str,
        highlight_category: str,
        target_duration: float = 30.0,
        creator_name: str = "streamer"
    ) -> Dict[str, Any]:
        """Directs the complete edit for a highlight, producing a Cut Manifest and rationale."""
        # Deep-coded: Clip length strictly 30s to 45s
        target_duration = round(min(45.0, max(30.0, float(target_duration))), 2)
        logger.info(f"[AI DIRECTOR] Formulating edit strategy for '{highlight_title}' ({highlight_category}) - {target_duration}s")

        # 1. Analyze video for cut moments and trigger points
        raw_moments = self.cut_detector.analyze_cut_moments(
            video_path=video_path,
            total_duration=target_duration
        )

        decisions: List[EditorialCutDecision] = []
        for idx, m in enumerate(raw_moments, start=1):
            decisions.append(EditorialCutDecision(
                cut_index=idx,
                timestamp_seconds=m.timestamp,
                moment_type=m.moment_type,
                trigger_event=m.reason.split(" at ")[0] if " at " in m.reason else m.moment_type,
                editorial_reason=m.reason,
                visual_effect=m.suggested_effect,
                energy_rating=m.energy_score
            ))

        # 2. Select optimal BGM based on mood and energy
        bgm_rec = self._select_bgm_track()

        # 3. Compile Director's Cut Manifest
        manifest = {
            "director_agent": "Antigravity AI Video Director v2.0",
            "highlight_title": highlight_title,
            "category": highlight_category,
            "target_duration_seconds": target_duration,
            "total_cuts_made": len(decisions),
            "average_seconds_between_cuts": round(target_duration / max(len(decisions), 1), 2),
            "applied_style_dna": {
                "layout": self.style_dna.get("visual_layout", {}),
                "caption_rules": self.style_dna.get("kinetic_typography", {}),
                "audio_mastering": self.style_dna.get("audio_mastering", {})
            },
            "selected_bgm": bgm_rec,
            "cut_timeline": [asdict(d) for d in decisions],
            "editorial_summary": self._generate_editorial_summary(decisions, target_duration)
        }

        logger.info(
            f"[AI DIRECTOR] Directed {len(decisions)} cuts across {target_duration}s "
            f"(Avg cut every {manifest['average_seconds_between_cuts']}s)"
        )
        return manifest

    def _select_bgm_track(self) -> Dict[str, Any]:
        """Selects an appropriate non-copyright background track from the music library."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        music_dir = os.path.join(base_dir, "assets", "music")
        if os.path.exists(music_dir):
            tracks = [f for f in os.listdir(music_dir) if f.endswith(".mp3")]
            if tracks:
                chosen = random.choice(tracks)
                return {
                    "filename": chosen,
                    "path": os.path.join(music_dir, chosen),
                    "volume": self.style_dna.get("audio_mastering", {}).get("bgm_gain", 0.30)
                }
        return {"filename": "none", "path": "", "volume": 0.30}

    def _generate_editorial_summary(self, decisions: List[EditorialCutDecision], duration: float) -> str:
        """Generates a human-readable editorial explanation of why each cut was positioned."""
        lines = [
            f"=== ANTIGRAVITY AI DIRECTOR: EDITORIAL CUT BREAKDOWN ({duration:.1f}s) ===",
            f"Total cuts choreographed: {len(decisions)}",
            ""
        ]
        for d in decisions:
            lines.append(
                f"[Cut #{d.cut_index:02d} @ {d.timestamp_seconds:05.2f}s] [{d.moment_type}] "
                f"Effect: {d.visual_effect.upper()} (Energy: {d.energy_rating:.0f}/100)"
            )
            lines.append(f"  -> Moment: {d.editorial_reason}")

        lines.append("")
        lines.append(
            f"Editorial Strategy: Retention locked at {decisions[0].timestamp_seconds:.1f}s hook punch-in; "
            f"maintained high-velocity gaming cadence with average cut every {duration / max(len(decisions), 1):.2f}s."
        )
        return "\n".join(lines)
