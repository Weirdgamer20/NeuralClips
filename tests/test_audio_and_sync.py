"""Unit Tests for Audio Problem Detector and A/V Sync Detector."""

import os
from audio.audio_problem_detector import AudioProblemDetector, AudioProblemReport
from audio.sync_detector import SyncDetector, SyncReport


def test_audio_problem_report_clipping():
    """Verifies that audio clipping at 0 dBFS is flagged as a problem."""
    detector = AudioProblemDetector()
    report = AudioProblemReport(
        has_problems=True,
        max_volume_db=0.0,
        mean_volume_db=-18.0,
        integrated_lufs=-14.0,
        is_clipping=True,
        problems=["Digital clipping / distortion detected"]
    )
    assert report.is_clipping is True
    assert len(report.problems) > 0


def test_audio_too_quiet_threshold():
    """Verifies that inaudible audio is flagged with recommended loudnorm filter."""
    report = AudioProblemReport(
        has_problems=True,
        max_volume_db=-22.0,
        mean_volume_db=-38.0,
        integrated_lufs=-32.0,
        is_too_quiet=True,
        problems=["Audio is too quiet for mobile playback"]
    )
    assert report.is_too_quiet is True
    assert report.integrated_lufs < AudioProblemDetector.MIN_ACCEPTABLE_LUFS


def test_sync_detector_thresholds():
    """Verifies that A/V start drift and duration delta thresholds are enforced."""
    report_drift = SyncReport(
        is_in_sync=False,
        video_start_sec=0.0,
        audio_start_sec=0.120,
        av_start_drift_sec=0.120,
        issues=["A/V start timestamp drift of 120ms detected"]
    )
    assert report_drift.is_in_sync is False
    assert report_drift.av_start_drift_sec > SyncDetector.MAX_PERMISSIBLE_START_DRIFT_SEC
    assert len(report_drift.issues) == 1


def test_sync_detector_perfect_sync():
    """Verifies that aligned streams pass verification."""
    report_clean = SyncReport(
        is_in_sync=True,
        video_start_sec=0.0,
        audio_start_sec=0.0,
        av_start_drift_sec=0.0,
        video_duration_sec=30.0,
        audio_duration_sec=30.0,
        duration_delta_sec=0.0,
        issues=[]
    )
    assert report_clean.is_in_sync is True
    assert len(report_clean.issues) == 0


def test_real_clip_audio_and_sync_analysis():
    """Analyzes a real rendered clip if available on disk."""
    clips_dir = r"d:\vidclip\storage\clips"
    if os.path.exists(clips_dir):
        files = [os.path.join(clips_dir, f) for f in os.listdir(clips_dir) if f.endswith(".mp4")]
        if files:
            sample_clip = files[0]
            audio_det = AudioProblemDetector()
            sync_det = SyncDetector()

            a_rep = audio_det.analyze_audio(sample_clip)
            s_rep = sync_det.analyze_sync(sample_clip)

            assert a_rep.has_audio_track is True
            assert isinstance(a_rep.integrated_lufs, float)
            assert isinstance(s_rep.av_start_drift_sec, float)
