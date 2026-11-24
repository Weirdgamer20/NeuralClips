import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cv2
from pathlib import Path
from core.opencv_retention_engine import OpenCVRetentionEngine

vpath = str(BASE_DIR / "storage" / "review_cuts/indian_triggered_insaan.mp4")
engine = OpenCVRetentionEngine()
facecam_box = engine.detect_exact_facecam(vpath, max_check_seconds=90.0)

print("Exact Facecam Detection for Triggered Insaan:")
print(facecam_box)

# Extract test frames to inspect
cap = cv2.VideoCapture(vpath)
for sec in [30, 60, 90]:
    cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(f"C:/Users/thega/.gemini/antigravity/brain/cc9214c0-7f61-456a-b5aa-8cae3dbac8e4/triggered_frame_{sec}.jpg", frame)
        print(f"Saved test frame at {sec}s")

cap.release()
