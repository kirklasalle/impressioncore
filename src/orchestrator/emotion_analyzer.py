"""
Emotion Analyzer Module

Analyzes facial expressions to detect emotions.
Uses deepface or fer library for emotion classification.

Created: January 14, 2026
Author: ImpressionCore Team
"""

import time
from collections import deque
from dataclasses import dataclass
from typing import Any

import numpy as np

# Try to import emotion detection libraries
DEEPFACE_AVAILABLE = False
FER_AVAILABLE = False

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    pass

try:
    from fer import FER
    FER_AVAILABLE = True
except ImportError:
    pass

if not DEEPFACE_AVAILABLE and not FER_AVAILABLE:
    print("[EMOTION] No emotion detection library available.")
    print("[EMOTION] Install with: pip install fer  OR  pip install deepface")


# Emotion labels
EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


@dataclass
class EmotionResult:
    """Emotion analysis result for a single face."""

    # Primary emotion
    dominant_emotion: str
    dominant_confidence: float

    # All emotion scores
    emotions: dict[str, float]

    # Tracking
    track_id: int = -1
    bbox: tuple[int, int, int, int] = (0, 0, 0, 0)

    # Timestamp
    timestamp: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "dominant_emotion": self.dominant_emotion,
            "dominant_confidence": round(self.dominant_confidence, 3),
            "emotions": {k: round(v, 3) for k, v in self.emotions.items()},
            "track_id": self.track_id,
            "bbox": list(self.bbox),
            "emoji": EMOTION_EMOJIS.get(self.dominant_emotion, "😐"),
            "timestamp": self.timestamp
        }


# Emoji mapping for emotions
EMOTION_EMOJIS = {
    "angry": "😠",
    "disgust": "🤢",
    "fear": "😨",
    "happy": "😊",
    "sad": "😢",
    "surprise": "😲",
    "neutral": "😐"
}


class EmotionAnalyzer:
    """
    Analyzes facial expressions to detect emotions.

    Features:
    - Multi-backend support (deepface, fer)
    - Temporal smoothing to reduce flickering
    - Per-face emotion tracking
    """

    # Smoothing parameters
    SMOOTHING_WINDOW = 5  # Number of frames to average
    CONFIDENCE_THRESHOLD = 0.3  # Minimum confidence to report emotion

    def __init__(self, backend: str = "auto"):
        """
        Initialize emotion analyzer.

        Args:
            backend: "deepface", "fer", or "auto" (use best available)
        """
        self.backend = self._select_backend(backend)
        self._fer_detector = None

        if self.backend == "fer":
            self._fer_detector = FER(mtcnn=False)  # Use faster detection

        # Temporal smoothing state per track_id
        self._history: dict[int, deque] = {}

        # Stats
        self.stats = {
            "frames_analyzed": 0,
            "faces_analyzed": 0,
            "backend": self.backend
        }

    def _select_backend(self, preference: str) -> str:
        """Select the best available backend."""
        if preference == "deepface" and DEEPFACE_AVAILABLE:
            return "deepface"
        elif preference == "fer" and FER_AVAILABLE:
            return "fer"
        elif preference == "auto":
            if FER_AVAILABLE:
                return "fer"  # FER is faster
            elif DEEPFACE_AVAILABLE:
                return "deepface"
        return "none"

    def analyze_face(self, frame: np.ndarray,
                    bbox: tuple[int, int, int, int],
                    track_id: int = -1) -> EmotionResult | None:
        """
        Analyze emotions for a single face region.

        Args:
            frame: Full BGR image
            bbox: (x, y, w, h) of face region
            track_id: Tracking ID for temporal smoothing

        Returns:
            EmotionResult or None if analysis failed
        """
        if self.backend == "none":
            return None

        x, y, w, h = bbox

        # Validate bbox
        h_frame, w_frame = frame.shape[:2]
        if x < 0 or y < 0 or x + w > w_frame or y + h > h_frame:
            return None
        if w < 32 or h < 32:  # Too small
            return None

        # Extract face region
        face_img = frame[y:y+h, x:x+w]

        try:
            if self.backend == "fer":
                result = self._analyze_fer(face_img)
            elif self.backend == "deepface":
                result = self._analyze_deepface(face_img)
            else:
                return None

            if result is None:
                return None

            self.stats["faces_analyzed"] += 1

            # Apply temporal smoothing
            if track_id >= 0:
                result = self._smooth_result(result, track_id)

            result.track_id = track_id
            result.bbox = bbox
            result.timestamp = time.time()

            return result

        except Exception:
            # Silently fail - emotion detection is optional
            return None

    def _analyze_fer(self, face_img: np.ndarray) -> EmotionResult | None:
        """Analyze using FER library."""
        # FER expects BGR
        emotions = self._fer_detector.detect_emotions(face_img)

        if not emotions:
            return None

        # Get first face result
        emotion_scores = emotions[0].get("emotions", {})

        if not emotion_scores:
            return None

        # Find dominant
        dominant = max(emotion_scores, key=emotion_scores.get)

        return EmotionResult(
            dominant_emotion=dominant,
            dominant_confidence=emotion_scores[dominant],
            emotions=emotion_scores
        )

    def _analyze_deepface(self, face_img: np.ndarray) -> EmotionResult | None:
        """Analyze using DeepFace library."""
        result = DeepFace.analyze(
            face_img,
            actions=["emotion"],
            enforce_detection=False,
            silent=True
        )

        if isinstance(result, list):
            result = result[0]

        emotion_scores = result.get("emotion", {})
        dominant = result.get("dominant_emotion", "neutral")

        # Normalize scores to 0-1
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v / 100 for k, v in emotion_scores.items()}

        return EmotionResult(
            dominant_emotion=dominant,
            dominant_confidence=emotion_scores.get(dominant, 0),
            emotions=emotion_scores
        )

    def _smooth_result(self, result: EmotionResult, track_id: int) -> EmotionResult:
        """Apply temporal smoothing to reduce flickering."""
        if track_id not in self._history:
            self._history[track_id] = deque(maxlen=self.SMOOTHING_WINDOW)

        self._history[track_id].append(result.emotions)

        # Average emotions over window
        if len(self._history[track_id]) < 2:
            return result

        avg_emotions = {}
        for emotion in EMOTIONS:
            values = [h.get(emotion, 0) for h in self._history[track_id]]
            avg_emotions[emotion] = np.mean(values)

        # Find new dominant
        dominant = max(avg_emotions, key=avg_emotions.get)

        return EmotionResult(
            dominant_emotion=dominant,
            dominant_confidence=avg_emotions[dominant],
            emotions=avg_emotions
        )

    def analyze_frame(self, frame: np.ndarray,
                     faces: list[dict]) -> list[EmotionResult]:
        """
        Analyze emotions for all faces in a frame.

        Args:
            frame: Full BGR image
            faces: List of face dicts with "bbox" and optional "track_id"

        Returns:
            List of EmotionResult for each face
        """
        self.stats["frames_analyzed"] += 1
        results = []

        for face in faces:
            bbox = face.get("bbox")
            if bbox is None:
                continue

            track_id = face.get("track_id", -1)
            result = self.analyze_face(frame, tuple(bbox), track_id)

            if result:
                results.append(result)

        return results

    def clear_history(self, track_id: int | None = None) -> None:
        """Clear smoothing history."""
        if track_id is not None:
            self._history.pop(track_id, None)
        else:
            self._history.clear()

    def is_available(self) -> bool:
        """Check if emotion analysis is available."""
        return self.backend != "none"


# Global instance
_analyzer_instance: EmotionAnalyzer | None = None


def get_emotion_analyzer() -> EmotionAnalyzer:
    """Get global emotion analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = EmotionAnalyzer()
    return _analyzer_instance
