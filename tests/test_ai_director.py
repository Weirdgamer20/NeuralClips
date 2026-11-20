"""Unit Tests for Antigravity AI Video Director and Cut Detector."""

from ai.ai_video_director import AIVideoDirector
from ai.cut_detector import CutDetector
from ai.style_dna_extractor import StyleDNAExtractor


def test_synthesized_viral_cuts():
    """Verifies that the cut detector creates structured viral cuts with reasons."""
    detector = CutDetector()
    silences = [{"start": 7.4, "end": 7.8}, {"start": 18.2, "end": 18.6}]
    cuts = detector._synthesize_viral_cuts(duration=30.0, silences=silences)

    assert len(cuts) >= 5, f"Expected >= 5 cuts, got {len(cuts)}"
    assert cuts[0].moment_type == "HOOK_PUNCH_IN", f"Expected HOOK_PUNCH_IN, got {cuts[0].moment_type}"
    assert cuts[0].timestamp == 1.4, f"Expected 1.4s hook cut, got {cuts[0].timestamp}"
    assert "hook" in cuts[0].reason.lower()

    for c in cuts:
        assert len(c.reason) > 5, "Cut reason too short"
        assert c.moment_type in [
            "HOOK_PUNCH_IN", "ACTION_SPIKE", "SPEECH_TRIM", "REACTION_BEAT", "CLIMAX_DROP", "RESOLUTION_CUT"
        ]


def test_director_manifest_creation():
    """Verifies that the AI Director produces an actionable Cut Decision Manifest."""
    director = AIVideoDirector()
    manifest = director.direct_clip_edit(
        video_path="dummy_video.mp4",
        highlight_title="UNBELIEVABLE 1v4 Clutch! 🔥",
        highlight_category="clutch",
        target_duration=30.0,
        creator_name="typical_gamer"
    )

    assert "cut_timeline" in manifest
    assert "editorial_summary" in manifest
    assert manifest["total_cuts_made"] >= 5
    moment_types = [c["moment_type"] for c in manifest["cut_timeline"]]
    assert "HOOK_PUNCH_IN" in moment_types

    first_cut = manifest["cut_timeline"][0]
    assert first_cut["moment_type"] == "HOOK_PUNCH_IN"
    assert "hook" in first_cut["editorial_reason"].lower()


def test_style_dna_loading():
    """Verifies that Style DNA holds all Part 7 & 2K vertical styling rules."""
    director = AIVideoDirector()
    dna = director.style_dna
    assert "visual_layout" in dna
    assert dna["visual_layout"]["canvas_resolution"] == [1440, 2560]
    assert dna["visual_layout"]["divider_color_hex"] == "#00F0FF"
    assert dna["kinetic_typography"]["font_size_px"] == 72
    assert dna["kinetic_typography"]["words_per_line"] == 3
