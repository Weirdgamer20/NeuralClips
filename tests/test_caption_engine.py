"""Tests for Part 10 Animated Caption Engine."""

import os
import tempfile
from ai.transcript_engine import TranscriptEngine
from rendering.caption_engine import CaptionEngine, format_ass_time


def test_ass_time_formatting():
    assert format_ass_time(0.0) == "0:00:00.00"
    assert format_ass_time(65.5) == "0:01:05.50"
    assert format_ass_time(3600.0) == "1:00:00.00"


def test_caption_generation():
    engine = CaptionEngine()
    transcript = "WHAT AN INSANE CLUTCH PLAY"
    timed_words = TranscriptEngine.generate_timed_words(transcript, 0.0, 5.0)

    assert len(timed_words) == 5
    assert timed_words[0]["word"] == "WHAT"

    with tempfile.NamedTemporaryFile(suffix=".ass", delete=False) as tf:
        out_ass = tf.name

    try:
        engine.generate_ass_script(timed_words, out_ass)
        assert os.path.exists(out_ass)
        with open(out_ass, "r", encoding="utf-8") as f:
            content = f.read()
        assert "[Script Info]" in content
        assert "Style: Default" in content
        assert "Dialogue: 0," in content
        assert "\\c&H0000FFFF" in content  # Yellow highlight tag
    finally:
        if os.path.exists(out_ass):
            os.remove(out_ass)
