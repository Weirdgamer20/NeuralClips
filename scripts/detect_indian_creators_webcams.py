import cv2
import subprocess
import imageio_ffmpeg
from pathlib import Path

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

sources = {
    "techno_gamerz": str(BASE_DIR / "storage" / "review_cuts/indian_techno_gamerz.mp4"),
    "carryminati": str(BASE_DIR / "storage" / "review_cuts/indian_carryminati.mp4"),
    "triggered_insaan": str(BASE_DIR / "storage" / "review_cuts/indian_triggered_insaan.mp4")
}

detector = cv2.FaceDetectorYN_create(str(BASE_DIR / "models/face_detection_yunet.onnx"), "", (1920, 1080), score_threshold=0.55)

for name, path in sources.items():
    print(f"\n=======================================================")
    print(f"Analyzing {name}: {path}")
    print(f"=======================================================")
    for sec in [30, 90, 150, 240, 360]:
        out_img = f"C:/Users/thega/.gemini/antigravity/brain/cc9214c0-7f61-456a-b5aa-8cae3dbac8e4/{name}_frame_{sec}.jpg"
        cmd = [ffmpeg, "-y", "-ss", str(sec), "-i", path, "-vframes", "1", out_img]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        img = cv2.imread(out_img)
        if img is None:
            continue
        h, w = img.shape[:2]
        detector.setInputSize((w, h))
        _, faces = detector.detect(img)
        if faces is not None:
            for idx, f in enumerate(faces):
                fx, fy, fw, fh = map(int, f[:4])
                conf = float(f[-1])
                print(f"  [{sec}s] Face #{idx}: x={fx}, y={fy}, w={fw}, h={fh}, conf={conf:.2f}")
        else:
            print(f"  [{sec}s] No face")
