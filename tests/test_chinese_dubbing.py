"""Unit and integration tests for Chinese content detection, Hindi dubbing, and animated subtitles."""

import os
import sys
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from audio.chinese_dubbing_engine import ChineseDubbingEngine
from rendering.ffmpeg_renderer import FFmpegRenderer


def test_chinese_content_detection():
    """Tests accurate detection of Chinese Hanzi characters and keywords."""
    # Positive cases
    assert ChineseDubbingEngine.is_chinese_content(title="【GTA6】实况直播 第一期 抢劫银行") is True
    assert ChineseDubbingEngine.is_chinese_content(channel_title="老番茄 Gaming") is True
    assert ChineseDubbingEngine.is_chinese_content(title="Bilibili GTA 6 Chinese Stream") is True
    assert ChineseDubbingEngine.is_chinese_content(description="侠盗猎车手6 中文解说") is True
    assert ChineseDubbingEngine.is_chinese_content(title="Douyu TV GTA 6 Highlights") is True

    # Negative cases
    assert ChineseDubbingEngine.is_chinese_content(title="Speed plays GTA 6 in Vice City") is False
    assert ChineseDubbingEngine.is_chinese_content(channel_title="Kai Cenat", title="Crazy GTA 6 Chase") is False
    assert ChineseDubbingEngine.is_chinese_content(title="Bhai ye kya gameplay hai") is False


def test_script_selection_and_localization():
    """Tests that category and keywords correctly pick contextual Hindi dialogue."""
    dubber = ChineseDubbingEngine()

    script_chase = dubber.select_script(category="gaming", title="Epic 5-Star Police Chase in Vice City")
    assert "पुलिस" in script_chase["hindi"]
    assert "POLICE" in script_chase["hinglish"]

    script_stunt = dubber.select_script(category="gaming", title="Crazy motorcycle jump from skyscraper")
    assert "छलांग" in script_stunt["hindi"]
    assert "STUNT" in script_stunt["hinglish"]

    script_physics = dubber.select_script(category="funny_reaction", title="Car crash glitch")
    assert "गाड़ी" in script_physics["hindi"]


def test_animated_ass_subtitle_generation():
    """Tests generation of valid ASS subtitle files with word-by-word animation."""
    dubber = ChineseDubbingEngine()
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_ass = os.path.join(tmp_dir, "test_chinese_subtitles.ass")
        caption_text = "BHAI YE DEKHO GTA 6 MEIN KYA HUA!"
        res_path = dubber.generate_animated_subtitles(
            caption_text=caption_text,
            output_ass_path=out_ass,
            duration=30.0,
            words_per_line=3
        )
        assert os.path.exists(res_path)
        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "[Script Info]" in content
        assert "[V4+ Styles]" in content
        assert "Dialogue: 0," in content
        assert "BHAI" in content


def test_hindi_audio_synthesis_and_package():
    """Tests complete dubbing package creation with neural voiceover synthesis."""
    dubber = ChineseDubbingEngine()
    with tempfile.TemporaryDirectory() as tmp_dir:
        pkg = dubber.prepare_dubbing_package(
            clip_id="test_chinese_01",
            category="police_chase",
            title="【GTA6】5星通缉逃亡实况",
            duration=15.0,
            output_dir=tmp_dir,
        )

        assert pkg["is_dubbed"] is True
        assert pkg["language"] == "hi"
        assert pkg["dubbed_audio_path"] is not None
        assert os.path.exists(pkg["dubbed_audio_path"])
        assert os.path.getsize(pkg["dubbed_audio_path"]) > 1000
        assert os.path.exists(pkg["ass_subtitle_path"])
        assert "police" in pkg["localized_title"].lower()


def test_ffmpeg_render_with_dubbed_audio_and_ducking():
    """Verifies that FFmpegRenderer mixes dubbed Hindi audio and burns animated subtitles."""
    dubber = ChineseDubbingEngine()
    renderer = FFmpegRenderer()

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_mp4 = os.path.join(tmp_dir, "rendered_dubbed_short.mp4")
        out_ass = os.path.join(tmp_dir, "dub_subs.ass")

        # Generate subtitles
        dubber.generate_animated_subtitles(
            caption_text="BHAI YE KYA HUA! 💀🔥",
            output_ass_path=out_ass,
            duration=5.0,
        )

        # Generate voiceover audio
        out_audio = os.path.join(tmp_dir, "hindi_dub.mp3")
        audio_path = dubber.synthesize_hindi_audio(
            text="भाई ये देखो क्या हो गया!",
            output_path=out_audio,
        )

        crop_config = {
            "gameplay": {"x": 320, "y": 0, "width": 1280, "height": 1080},
            "facecam": {"x": 0, "y": 395, "width": 480, "height": 360},
            "canvas": {"width": 1080, "height": 1920},
        }

        success, msg = renderer.render_split_screen(
            input_video_path="",  # triggers testsrc
            output_clip_path=out_mp4,
            start_seconds=0.0,
            duration_seconds=3.0,
            crop_config=crop_config,
            ass_subtitle_path=out_ass,
            dubbed_audio_path=audio_path,
            dubbed_volume=1.20,
            original_audio_ducking=0.25,
        )

        assert success is True, f"Render failed: {msg}"
        assert os.path.exists(out_mp4)
        assert os.path.getsize(out_mp4) > 10000
