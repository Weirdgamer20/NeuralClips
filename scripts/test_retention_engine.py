import sys
sys.path.insert(0, "d:/vidclip")
from core.opencv_retention_engine import OpenCVRetentionEngine

engine = OpenCVRetentionEngine()

print("--- CaseOh Video ---")
fc_caseoh = engine.detect_exact_facecam("storage/review_cuts/caseoh_full_crashes.mp4.mkv", max_check_seconds=40.0)
print("CaseOh facecam box:", fc_caseoh)
peaks_caseoh = engine.scan_motion_peaks_fast("storage/review_cuts/caseoh_full_crashes.mp4.mkv", clip_duration=30.0, sample_fps=2.0)
for p in peaks_caseoh[:3]:
    print(f"  • {p['start_sec']}s - {p['end_sec']}s: Motion={p['motion_score']}, Peak={p['peak_motion']}")

print("\n--- Tank Video ---")
peaks_tank = engine.scan_motion_peaks_fast("storage/review_cuts/tank_6star_1440p.webm", clip_duration=30.0, sample_fps=2.0)
for p in peaks_tank[:3]:
    print(f"  • {p['start_sec']}s - {p['end_sec']}s: Motion={p['motion_score']}, Peak={p['peak_motion']}")
