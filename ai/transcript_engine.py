"""Transcript and word-level alignment engine for animated captions."""

from typing import Any, Dict, List


class TranscriptEngine:
    """Processes dialogue transcripts into word-level timed caption chunks."""

    @staticmethod
    def generate_timed_words(transcript: str, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """Splits transcript dialogue into word-level intervals evenly spaced across clip."""
        words = transcript.strip().split()
        if not words:
            return []

        total_duration = max(0.1, end_time - start_time)
        word_duration = total_duration / len(words)

        timed_words = []
        for i, word in enumerate(words):
            w_start = start_time + (i * word_duration)
            w_end = w_start + word_duration
            timed_words.append({
                "word": word,
                "start": round(w_start, 2),
                "end": round(w_end, 2),
                "duration": round(word_duration, 2),
            })
        return timed_words
