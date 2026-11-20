"""Tests for Part 9 Video Rendering Engine and Specifications."""

import os
import tempfile
from rendering.crop_detector import CropDetector
from rendering.layout_engine import LayoutEngine
from rendering.render_validator import RenderValidator


def test_crop_detector_and_layout():
    detector = CropDetector()
    crop = detector.resolve_crop("standard_top_left_cam")

    assert "facecam" in crop
    assert "gameplay" in crop
    assert crop["facecam"]["width"] > 0
    assert crop["facecam"]["height"] > 0

    filtergraph = LayoutEngine.generate_split_screen_filter(crop)
    assert "vstack=inputs=3" in filtergraph
    assert f"crop={LayoutEngine.CANVAS_WIDTH}:{LayoutEngine.FACECAM_HEIGHT}" in filtergraph
    assert f"crop={LayoutEngine.CANVAS_WIDTH}:{LayoutEngine.GAMEPLAY_HEIGHT}" in filtergraph


def test_render_validator():
    validator = RenderValidator()

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
        tf.write(b"MOCK_MP4_CONTENT")
        dummy_path = tf.name

    try:
        # Valid test (2K or 1080p)
        ok, msg, meta = validator.validate_clip(
            dummy_path,
            mock_override={
                "width": 1440,
                "height": 2560,
                "duration": 45.0,
                "video_codec": "h264",
                "audio_codec": "aac",
                "has_audio": True,
            }
        )
        assert ok is True

        # Invalid resolution test
        bad_res, msg, _ = validator.validate_clip(
            dummy_path,
            mock_override={"width": 1920, "height": 1080, "duration": 45.0, "has_audio": True}
        )
        assert bad_res is False
        assert "Invalid resolution" in msg

        # Invalid duration test (too short, e.g. 10.0s < 15.0s)
        bad_dur, msg, _ = validator.validate_clip(
            dummy_path,
            mock_override={"width": 1080, "height": 1920, "duration": 10.0, "has_audio": True}
        )
        assert bad_dur is False
        assert "Duration" in msg
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)


def test_bgm_and_narration_audio_mix():
    from rendering.ffmpeg_renderer import FFmpegRenderer
    renderer = FFmpegRenderer()
    if not renderer.ffmpeg_path:
        return

    crop_detector = CropDetector()
    crop = crop_detector.resolve_crop("standard_top_left_cam")

    bgm_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "music", "ncs_invincible.mp3")

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
        out_clip = tf.name

    try:
        ok, msg = renderer.render_split_screen(
            input_video_path="dummy_nonexistent.mp4",
            output_clip_path=out_clip,
            start_seconds=0.0,
            duration_seconds=5.0,
            crop_config=crop,
            bgm_music_path=bgm_path if os.path.exists(bgm_path) else None,
            bgm_volume=0.30,
            narration_volume=1.20,
        )
        assert ok is True, f"Render failed: {msg}"
        assert os.path.exists(out_clip)
        assert os.path.getsize(out_clip) > 1000
    finally:
        if os.path.exists(out_clip):
            os.remove(out_clip)
