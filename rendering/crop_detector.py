"""Crop profile resolver and facecam/gameplay coordinate manager with AI dynamic vision."""

import logging
import os
from typing import Any, Dict, List, Optional
from core.yaml_util import load_yaml

logger = logging.getLogger("neuralclips.crop_detector")


class CropDetector:
    """Resolves crop bounding boxes for stream facecam and gameplay regions."""

    def __init__(self, profiles_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not profiles_path:
            profiles_path = os.path.join(base_dir, "config", "crop_profiles.yaml")
        self.base_dir = base_dir
        self.profiles_path = profiles_path
        self._profiles = self._load_profiles()
        self.model_path = os.path.join(base_dir, "models", "face_detection_yunet.onnx")

    def _load_profiles(self) -> Dict[str, Any]:
        data = load_yaml(self.profiles_path)
        return data.get("profiles", {})

    def detect_facecam_from_video(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Dynamically detects a streamer's facecam box across time using YuNet face detection."""
        if not video_path or not os.path.exists(video_path) or not os.path.exists(self.model_path):
            return None

        try:
            import cv2
            detector = cv2.FaceDetectorYN_create(self.model_path, "", (1920, 1080), score_threshold=0.65)
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30

            sample_timestamps = [3, 8, 15, 22]
            candidate_faces = []

            for sec in sample_timestamps:
                frame_idx = int(sec * fps)
                if frame_idx >= total_frames:
                    continue
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret or frame is None:
                    continue

                h, w, _ = frame.shape
                detector.setInputSize((w, h))
                _, faces = detector.detect(frame)
                if faces is not None:
                    for f in faces:
                        x, y, fw, fh = map(int, f[:4])
                        score = float(f[-1])
                        # Streamer facecams are usually not full-screen; faces are 35-300px wide
                        if 35 <= fw <= 300 and 40 <= fh <= 350:
                            candidate_faces.append({"x": x, "y": y, "w": fw, "h": fh, "sec": sec, "conf": score})
            cap.release()

            if not candidate_faces:
                return None

            # Cluster faces across time to find static webcam position
            clusters: List[List[Dict[str, Any]]] = []
            for f in candidate_faces:
                matched = False
                for c in clusters:
                    cx = sum(item["x"] for item in c) / len(c)
                    cy = sum(item["y"] for item in c) / len(c)
                    if abs(f["x"] - cx) < 90 and abs(f["y"] - cy) < 90:
                        c.append(f)
                        matched = True
                        break
                if not matched:
                    clusters.append([f])

            if not clusters:
                return None

            def cluster_score(cl: List[Dict[str, Any]]) -> float:
                count = len(cl)
                avg_x = sum(f["x"] for f in cl) / count
                avg_y = sum(f["y"] for f in cl) / count
                dist_from_center = ((avg_x - 960) ** 2 + (avg_y - 540) ** 2) ** 0.5
                return count * 1000 + dist_from_center

            best_cluster = max(clusters, key=cluster_score)
            if len(best_cluster) < 2:
                # Require at least 2 temporal matches to avoid moving in-game characters
                return None

            avg_x = int(sum(f["x"] for f in best_cluster) / len(best_cluster))
            avg_y = int(sum(f["y"] for f in best_cluster) / len(best_cluster))
            avg_w = int(sum(f["w"] for f in best_cluster) / len(best_cluster))
            avg_h = int(sum(f["h"] for f in best_cluster) / len(best_cluster))

            # Expand face box to standard 16:9 webcam framing (440x280)
            cam_w = 440
            cam_h = 280
            box_x = max(0, min(1920 - cam_w, int(avg_x + avg_w / 2 - cam_w / 2)))
            box_y = max(0, min(1080 - cam_h, int(avg_y + avg_h / 2 - cam_h / 2 + 20)))

            # Centered gameplay crop
            gp_x = 320
            gp_w = 1280
            gp_y = 0
            gp_h = 1080

            logger.info(f"AI Facecam dynamically detected for stream at x={box_x}, y={box_y}, w={cam_w}, h={cam_h} (confidence across {len(best_cluster)} frames)")
            return {
                "facecam": {"x": box_x, "y": box_y, "width": cam_w, "height": cam_h},
                "gameplay": {"x": gp_x, "y": gp_y, "width": gp_w, "height": gp_h},
            }
        except Exception as e:
            logger.warning(f"Dynamic facecam detection error: {e}")
            return None

    def resolve_crop(self, profile_name: Optional[str] = None, video_path: Optional[str] = None) -> Dict[str, Any]:
        """Returns crop coordinates, attempting AI dynamic face detection first before falling back to profiles."""
        # 1. Try dynamic AI face detection if video is available
        if video_path and os.path.exists(video_path):
            detected = self.detect_facecam_from_video(video_path)
            if detected:
                return detected

        # 2. Known creator profile
        if profile_name:
            raw_key = str(profile_name).lower().strip().replace(" ", "_").replace("-", "_")

            if raw_key in self._profiles:
                return self._profiles[raw_key]

            key_mappings = {
                "speed": "ishowspeed",
                "peanut": "theburntpeanut",
                "kai": "kai_cenat",
                "cenat": "kai_cenat",
                "typical": "typical_gamer",
                "coringa": "loud_coringa",
                "shub": "beastboyshub",
                "mythpat": "mythpat",
                "carry": "carryislive",
            }
            for sub, mapped in key_mappings.items():
                if sub in raw_key and mapped in self._profiles:
                    return self._profiles[mapped]

        # 3. Default fallback
        return self._profiles.get("default_fallback", {
            "facecam": {"x": 10, "y": 390, "width": 440, "height": 280},
            "gameplay": {"x": 320, "y": 0, "width": 1280, "height": 1080},
        })
