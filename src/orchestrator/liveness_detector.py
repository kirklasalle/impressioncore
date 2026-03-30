"""
Liveness Detection Module

Anti-spoofing checks to detect real faces vs photos/videos/masks.
Uses multiple techniques including blink detection, texture analysis,
depth verification (when Kinect available), and micro-movement analysis.

Created: January 14, 2026
Author: ImpressionCore Team
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np

# Try to import dlib for landmark detection
DLIB_AVAILABLE = False
try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    pass


@dataclass
class LivenessResult:
    """Result of liveness detection."""

    is_live: bool
    confidence: float  # 0-1

    # Individual check results
    checks: dict[str, float] = field(default_factory=dict)

    # Tracking info
    track_id: int = -1
    bbox: tuple[int, int, int, int] = (0, 0, 0, 0)

    # Challenge-response (if used)
    challenge_passed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_live": self.is_live,
            "confidence": round(self.confidence, 3),
            "checks": {k: round(v, 3) for k, v in self.checks.items()},
            "track_id": self.track_id,
            "bbox": list(self.bbox),
            "challenge_passed": self.challenge_passed
        }


class LivenessDetector:
    """
    Multi-modal liveness detection to prevent spoofing.

    Detection methods:
    1. Texture Analysis - Detect printed photos via texture patterns
    2. Blink Detection - Verify natural eye blinking
    3. Head Movement - Check for micro-movements
    4. Depth Verification - Use Kinect depth camera
    5. Moiré Pattern - Detect screen display patterns
    """

    # Thresholds
    LIVENESS_THRESHOLD = 0.6  # Overall score threshold
    BLINK_THRESHOLD = 0.25  # Eye aspect ratio for blink
    MOVEMENT_THRESHOLD = 2.0  # Pixels of movement required

    def __init__(self, enable_depth: bool = True):
        """
        Initialize liveness detector.

        Args:
            enable_depth: Enable Kinect depth checking when available
        """
        self.enable_depth = enable_depth

        # Blink detection state per track_id
        self._blink_history: dict[int, deque] = {}

        # Movement detection state
        self._movement_history: dict[int, deque] = {}

        # Landmark detector (for blink detection)
        self._landmark_predictor = None
        self._face_detector = None

        if DLIB_AVAILABLE:
            try:
                # Try to load shape predictor
                predictor_path = "shape_predictor_68_face_landmarks.dat"
                import os
                if os.path.exists(predictor_path):
                    self._landmark_predictor = dlib.shape_predictor(predictor_path)
                    self._face_detector = dlib.get_frontal_face_detector()
            except Exception:
                pass

        self.stats = {
            "checks_performed": 0,
            "live_detected": 0,
            "spoof_detected": 0
        }

    def check_liveness(self, frame: np.ndarray,
                      bbox: tuple[int, int, int, int],
                      track_id: int = -1,
                      depth_frame: np.ndarray | None = None) -> LivenessResult:
        """
        Perform liveness check on a face region.

        Args:
            frame: BGR image
            bbox: (x, y, w, h) face region
            track_id: Tracking ID for temporal analysis
            depth_frame: Optional depth frame from Kinect

        Returns:
            LivenessResult with confidence score
        """
        self.stats["checks_performed"] += 1
        checks = {}

        x, y, w, h = bbox

        # Validate bbox
        h_frame, w_frame = frame.shape[:2]
        if x < 0 or y < 0 or x + w > w_frame or y + h > h_frame:
            return LivenessResult(is_live=False, confidence=0, bbox=bbox)

        face_img = frame[y:y+h, x:x+w]

        # 1. Texture Analysis
        checks["texture"] = self._check_texture(face_img)

        # 2. Color Distribution
        checks["color"] = self._check_color_distribution(face_img)

        # 3. Moiré Pattern Detection
        checks["moire"] = self._check_moire_pattern(face_img)

        # 4. Movement Analysis (requires tracking)
        if track_id >= 0:
            checks["movement"] = self._check_movement(bbox, track_id)

        # 5. Blink Detection (requires dlib)
        if self._landmark_predictor is not None:
            blink_score = self._check_blinks(frame, bbox, track_id)
            if blink_score is not None:
                checks["blink"] = blink_score

        # 6. Depth Verification (requires Kinect depth frame)
        if depth_frame is not None and self.enable_depth:
            checks["depth"] = self._check_depth(depth_frame, bbox)

        # Calculate overall score
        confidence = np.mean(list(checks.values())) if checks else 0.5

        is_live = confidence >= self.LIVENESS_THRESHOLD

        if is_live:
            self.stats["live_detected"] += 1
        else:
            self.stats["spoof_detected"] += 1

        return LivenessResult(
            is_live=is_live,
            confidence=confidence,
            checks=checks,
            track_id=track_id,
            bbox=bbox
        )

    def _check_texture(self, face_img: np.ndarray) -> float:
        """
        Analyze texture to detect printed photos.

        Real faces have more varied textures than printed materials.
        Uses Local Binary Pattern (LBP) variance.
        """
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)

        # Calculate Laplacian variance (sharpness/texture measure)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()

        # Real faces typically have variance > 100
        # Printed photos often have variance < 50 (smoother)
        score = min(1.0, variance / 200)

        return score

    def _check_color_distribution(self, face_img: np.ndarray) -> float:
        """
        Check color distribution for signs of screen/print.

        Real skin has natural color variance, screens have artificial patterns.
        """
        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(face_img, cv2.COLOR_BGR2HSV)

        # Check hue variance (skin has consistent hue)
        hue_std = np.std(hsv[:, :, 0])

        # Check saturation (screens often oversaturated)
        sat_mean = np.mean(hsv[:, :, 1])

        # Score: Real faces have low hue variance, moderate saturation
        hue_score = 1.0 - min(1.0, hue_std / 30)
        sat_score = 1.0 if 30 < sat_mean < 150 else 0.5

        return (hue_score + sat_score) / 2

    def _check_moire_pattern(self, face_img: np.ndarray) -> float:
        """
        Detect Moiré patterns typical of screen displays.

        Screens showing photos have interference patterns from pixel grid.
        """
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)

        # Apply FFT
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude = np.abs(fshift)

        # Check for periodic spikes (Moiré patterns)
        # Real faces have smooth frequency distribution
        center = magnitude[magnitude.shape[0]//2, magnitude.shape[1]//2]
        mean_mag = np.mean(magnitude)

        # High center-to-mean ratio suggests no Moiré
        ratio = center / (mean_mag + 1e-6)
        score = min(1.0, ratio / 1000)

        return score

    def _check_movement(self, bbox: tuple, track_id: int) -> float:
        """
        Check for natural micro-movements.

        Live faces have subtle movements, photos are static.
        """
        if track_id not in self._movement_history:
            self._movement_history[track_id] = deque(maxlen=30)

        # Record center point
        x, y, w, h = bbox
        center = (x + w/2, y + h/2)
        self._movement_history[track_id].append(center)

        history = self._movement_history[track_id]

        if len(history) < 10:
            return 0.5  # Not enough data

        # Calculate movement variance
        centers = np.array(list(history))
        variance = np.var(centers, axis=0)
        total_variance = np.sum(variance)

        # Live faces have some movement but not too much
        # Score: optimal movement between 2-50 pixels variance
        if total_variance < self.MOVEMENT_THRESHOLD:
            return 0.3  # Too static - likely photo
        elif total_variance > 1000:
            return 0.5  # Too much movement - unclear
        else:
            return 0.9  # Natural movement

    def _check_blinks(self, frame: np.ndarray, bbox: tuple,
                     track_id: int) -> float | None:
        """
        Detect eye blinks for liveness verification.

        Real faces blink naturally, photos don't.
        """
        if self._landmark_predictor is None:
            return None

        if track_id not in self._blink_history:
            self._blink_history[track_id] = deque(maxlen=90)  # ~3 seconds

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Create dlib rectangle from bbox
            x, y, w, h = bbox
            rect = dlib.rectangle(x, y, x + w, y + h)

            # Get landmarks
            shape = self._landmark_predictor(gray, rect)

            # Calculate Eye Aspect Ratio (EAR)
            # Left eye: points 36-41, Right eye: points 42-47
            left_ear = self._eye_aspect_ratio(shape, [36, 37, 38, 39, 40, 41])
            right_ear = self._eye_aspect_ratio(shape, [42, 43, 44, 45, 46, 47])
            ear = (left_ear + right_ear) / 2

            self._blink_history[track_id].append(ear)

            history = list(self._blink_history[track_id])

            if len(history) < 30:
                return 0.5

            # Count blinks (EAR drops below threshold)
            blinks = 0
            prev_ear = history[0]
            for current_ear in history[1:]:
                if prev_ear >= self.BLINK_THRESHOLD and current_ear < self.BLINK_THRESHOLD:
                    blinks += 1
                prev_ear = current_ear

            # Expect 1-3 blinks in 3 seconds for real face
            if blinks == 0:
                return 0.2  # No blinks - likely photo
            elif blinks > 10:
                return 0.3  # Too many - unusual
            else:
                return 0.95  # Natural blinking

        except Exception:
            return None

    def _eye_aspect_ratio(self, shape, eye_points: list[int]) -> float:
        """Calculate Eye Aspect Ratio from landmarks."""
        # Get eye landmark coordinates
        eye = np.array([(shape.part(i).x, shape.part(i).y) for i in eye_points])

        # Compute distances
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])

        # EAR formula
        ear = (A + B) / (2.0 * C) if C > 0 else 0
        return ear

    def _check_depth(self, depth_frame: np.ndarray,
                    bbox: tuple) -> float:
        """
        Verify 3D depth using Kinect depth camera.

        Real faces have 3D depth variation, photos are flat.
        """
        x, y, w, h = bbox

        # Validate bounds
        h_d, w_d = depth_frame.shape[:2]
        x = max(0, min(x, w_d - 1))
        y = max(0, min(y, h_d - 1))
        w = min(w, w_d - x)
        h = min(h, h_d - y)

        if w <= 0 or h <= 0:
            return 0.5

        face_depth = depth_frame[y:y+h, x:x+w]

        # Filter out invalid depth values
        valid_depth = face_depth[face_depth > 0]

        if len(valid_depth) < 100:
            return 0.5  # Not enough depth data

        # Real faces have depth variance (nose closer than ears)
        depth_variance = np.std(valid_depth)

        # Real faces typically have 50-300mm depth variance
        # Flat photos have < 20mm variance
        if depth_variance < 20:
            return 0.1  # Flat - likely photo
        elif depth_variance > 500:
            return 0.4  # Too much - noisy
        else:
            return 0.95  # Good 3D variance

    def clear_history(self, track_id: int | None = None) -> None:
        """Clear tracking history."""
        if track_id is not None:
            self._blink_history.pop(track_id, None)
            self._movement_history.pop(track_id, None)
        else:
            self._blink_history.clear()
            self._movement_history.clear()


# Global instance
_detector_instance: LivenessDetector | None = None


def get_liveness_detector() -> LivenessDetector:
    """Get global liveness detector instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = LivenessDetector()
    return _detector_instance
