"""Gemini AI Client for Multimodal Video Highlight Detection."""

import json
import os
from typing import Any, Dict, List, Optional
from ai.agent_evaluator import AgentEvaluator
from core.logging_config import setup_logger

logger = setup_logger("neuralclips.gemini_client")

HIGHLIGHT_CATEGORIES = [
    "kills_eliminations", "clutch", "multi_kill", "unexpected_victory",
    "funny_gameplay", "funny_reaction", "high_skill_play", "impressive_movement",
    "rare_event", "exciting_fight", "unexpected_failure", "memorable_interaction",
    "dramatic_comeback", "unusual_moment", "engaging_gameplay"
]

ANALYSIS_PROMPT = """You are an expert esports and gaming video editor for NEURALCLIPS.
Analyze the provided gaming footage segment and detect high-energy, entertaining, or clutch highlights.

EVALUATION CRITERIA:
- Entertainment value
- Gameplay significance
- Visual clarity
- Audio & player reaction quality
- Completeness of the event (clear beginning, buildup, climax, reaction)
- Uniqueness and viral potential

RULES:
- Ordinary or repetitive gameplay must NOT be classified as a highlight.
- Score each candidate from 0 to 100.
- Suggested duration MUST be 30, 45, or 60 seconds.
- Provide clean, word-level or sentence-level transcription of player audio if audible.

Return a JSON array of highlight candidates adhering strictly to this schema:
[
  {
    "start_timestamp": float,
    "end_timestamp": float,
    "category": string (one of the 15 categories),
    "score": int (0-100),
    "confidence": float (0.0-1.0),
    "reason": string,
    "transcript": string,
    "suggested_duration": int (30, 45, or 60),
    "suggested_title": string
  }
]
"""


class GeminiClient:
    """Interfaces with Antigravity Agent AI or Google Gemini for video analysis."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        ai_provider: Optional[str] = None,
    ):
        self.ai_provider = (ai_provider or os.getenv("AI_PROVIDER", "agent")).lower()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.agent_evaluator = AgentEvaluator()

    def analyze_segment(
        self,
        source_id: str,
        segment_id: str,
        start_offset: float,
        duration: float,
        video_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Analyzes segment using Antigravity AI Agent or Gemini API."""
        # 1. Preferred Agent AI Mode (no API key required)
        if self.ai_provider == "agent" or not self.api_key:
            logger.info(f"Analyzing segment {segment_id} using Antigravity Agent AI Engine.")
            return self.agent_evaluator.evaluate_segment(
                source_id=source_id,
                segment_id=segment_id,
                start_offset=start_offset,
                duration=duration,
                video_path=video_path,
            )

        # 2. Remote Gemini API Fallback
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            m = genai.GenerativeModel(self.model)

            response = m.generate_content(
                [
                    ANALYSIS_PROMPT,
                    f"Source ID: {source_id}, Offset: {start_offset}s, Duration: {duration}s"
                ],
                generation_config={"response_mime_type": "application/json"}
            )
            raw_text = response.text
            items = json.loads(raw_text)
            candidates = []
            for item in items:
                item["source_id"] = source_id
                item["segment_id"] = segment_id
                candidates.append(item)
            return candidates
        except Exception as e:
            logger.warning(f"Remote Gemini API failed ({e}); falling back to Antigravity Agent AI.")
            return self.agent_evaluator.evaluate_segment(
                source_id=source_id,
                segment_id=segment_id,
                start_offset=start_offset,
                duration=duration,
                video_path=video_path,
            )

    def _mock_analyze(
        self,
        source_id: str,
        segment_id: str,
        start_offset: float,
        duration: float,
    ) -> List[Dict[str, Any]]:
        """Deterministic mock generator for offline tests and validation."""
        candidates = []
        # Simulate highlight if segment is long enough
        if duration >= 30.0:
            suggested_dur = 45 if duration >= 45.0 else 30
            # Alternate scores to produce both passing (>=75) and failing (<75) test candidates
            score = 88 if int(start_offset) % 2 == 0 else 72
            candidates.append({
                "source_id": source_id,
                "segment_id": segment_id,
                "start_timestamp": round(start_offset + 5.0, 1),
                "end_timestamp": round(start_offset + 5.0 + suggested_dur, 1),
                "category": "clutch",
                "score": score,
                "confidence": 0.94,
                "reason": "1v3 clutch situation with clean headshots and excited creator reaction",
                "transcript": "No way! One more left, he is behind the box... YES! LET'S GO!",
                "suggested_duration": suggested_dur,
                "suggested_title": "INSANE 1v3 Clutch Moment! 🔥",
            })
        return candidates
