"""
Face Recognition Engine

Core module for face encoding, recognition, and multi-face tracking.
Integrates with face_recognition library and provides identity matching.

Created: January 14, 2026
Author: ImpressionCore Team
"""

import threading
import time
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

# Import face_recognition if available
try:
    import face_recognition
    FACE_REC_AVAILABLE = True
except ImportError:
    FACE_REC_AVAILABLE = False
    print("[FACE_ENGINE] face_recognition not available. Recognition disabled.")

from .face_database import FaceDatabase, FaceIdentity, get_face_database


@dataclass
class RecognitionResult:
    """Result of face recognition on a single detected face."""

    # Location (x, y, w, h)
    bbox: tuple[int, int, int, int]

    # Recognition result
    identity: FaceIdentity | None = None
    confidence: float = 0.0  # 0.0 = unknown, 1.0 = certain match

    # Multi-face tracking
    track_id: int = -1  # Persistent ID across frames (-1 = untracked)

    # Quality metrics
    face_quality: float = 1.0

    # Landmarks & Pose
    landmarks: dict[str, list[tuple[int, int]]] | None = None
    head_pose: dict[str, float] | None = None # pitch, yaw, roll

    encoding: np.ndarray | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "bbox": list(self.bbox),
            "identity_id": self.identity.id if self.identity else None,
            "identity_name": self.identity.name if self.identity else "Unknown",
            "confidence": round(self.confidence, 3),
            "track_id": self.track_id,
            "face_quality": round(self.face_quality, 3),
            "role": self.identity.role if self.identity else "unknown",
            "landmarks": self.landmarks,
            "head_pose": self.head_pose,
            # [FIX] Add 'label' for standard frontend overlay compatibility
            "label": f"{self.identity.name} ({int(self.confidence * 100)}%)" if self.identity else f"Unknown ({int(self.confidence * 100)}%)"
        }


@dataclass
class TrackedFace:
    """Internal tracking state for a face across frames."""
    track_id: int
    last_bbox: tuple[int, int, int, int]
    last_seen: float
    identity: FaceIdentity | None = None
    confidence: float = 0.0
    encoding: np.ndarray | None = None
    landmarks: dict[str, list[tuple[int, int]]] | None = None
    head_pose: dict[str, float] | None = None
    miss_count: int = 0


class FaceRecognitionEngine:
    """
    Core face recognition and tracking engine.

    Features:
    - Face encoding (128-dim vectors)
    - Identity matching against enrolled faces
    - Multi-face tracking with persistent IDs
    - Configurable recognition threshold
    """

    # Recognition threshold (distance)
    # Lower = stricter matching, higher = more permissive
    DEFAULT_TOLERANCE = 0.5  # Adjust based on testing

    # Tracking parameters
    MAX_TRACK_AGE = 2.0  # Seconds before track is deleted
    MAX_MISS_COUNT = 10  # Frames before track is deleted
    IOU_THRESHOLD = 0.3  # Intersection-over-Union for matching

    def __init__(self,
                 database: FaceDatabase | None = None,
                 tolerance: float = DEFAULT_TOLERANCE,
                 enable_tracking: bool = True):
        """
        Initialize the face recognition engine.

        Args:
            database: Face database for enrolled identities
            tolerance: Recognition distance threshold (lower = stricter)
            enable_tracking: Enable multi-face tracking
        """
        self.db = database or get_face_database()
        self.tolerance = tolerance
        self.enable_tracking = enable_tracking

        # Tracking state
        self._tracks: dict[int, TrackedFace] = {}
        self._next_track_id = 1
        self._lock = threading.Lock()

        # Cache enrolled encodings for fast matching
        self._enrolled_cache: list[tuple[FaceIdentity, list[np.ndarray]]] = []
        self._cache_timestamp = 0
        self._cache_ttl = 30.0  # Refresh cache every 30 seconds

        # Stats
        self.stats = {
            "frames_processed": 0,
            "faces_detected": 0,
            "faces_recognized": 0,
            "cache_hits": 0
        }

    def _refresh_cache(self) -> None:
        """Refresh enrolled face cache from database."""
        now = time.time()
        if now - self._cache_timestamp > self._cache_ttl:
            self._enrolled_cache = self.db.get_all_embeddings()
            self._cache_timestamp = now

    def encode_face(self, frame: np.ndarray,
                   face_location: tuple[int, int, int, int] | None = None
                   ) -> tuple[np.ndarray | None, tuple | None]:
        """
        Encode a single face from frame.

        Args:
            frame: BGR image (OpenCV format)
            face_location: Optional (x, y, w, h) bbox. If None, detect first face.

        Returns:
            (encoding, face_location) tuple, or (None, None) if no face found
        """
        if not FACE_REC_AVAILABLE:
            return None, None

        # Convert BGR to RGB for face_recognition
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if face_location is None:
            # Detect faces
            locations = face_recognition.face_locations(rgb, model="hog")
            if not locations:
                return None, None
            # Use first face, convert from (top, right, bottom, left) to (x, y, w, h)
            top, right, bottom, left = locations[0]
            face_location = (left, top, right - left, bottom - top)
            fr_location = [locations[0]]
        else:
            # Convert (x, y, w, h) to face_recognition format (top, right, bottom, left)
            x, y, w, h = face_location
            fr_location = [(y, x + w, y + h, x)]

        # Get encoding
        encodings = face_recognition.face_encodings(rgb, fr_location)
        if encodings:
            return encodings[0], face_location

        return None, face_location

    def recognize(self, encoding: np.ndarray) -> tuple[FaceIdentity | None, float]:
        """
        Recognize a face encoding against enrolled faces.

        Args:
            encoding: 128-dim face encoding

        Returns:
            (identity, confidence) tuple. Identity is None if no match.
        """
        if not FACE_REC_AVAILABLE:
            return None, 0.0

        self._refresh_cache()

        if not self._enrolled_cache:
            return None, 0.0

        best_match: FaceIdentity | None = None
        best_distance = float('inf')

        for identity, embeddings in self._enrolled_cache:
            # Compare against all embeddings for this identity
            distances = face_recognition.face_distance(embeddings, encoding)
            min_distance = np.min(distances)

            if min_distance < best_distance:
                best_distance = min_distance
                best_match = identity

        # Convert distance to confidence (inverse relationship)
        # distance of 0 = confidence 1.0, distance of tolerance = confidence 0.5
        if best_distance <= self.tolerance:
            confidence = max(0, 1.0 - (best_distance / self.tolerance) * 0.5)
            self.stats["faces_recognized"] += 1
            return best_match, confidence

        return None, 0.0

    def process_frame(self, frame: np.ndarray,
                     scale: float = 0.5) -> list[RecognitionResult]:
        """
        Process a frame: detect faces, recognize identities, update tracks.

        Args:
            frame: BGR image (OpenCV format)
            scale: Downscale factor for faster detection (0.5 = half size)

        Returns:
            List of RecognitionResult for each detected face
        """
        if not FACE_REC_AVAILABLE:
            return []

        self.stats["frames_processed"] += 1
        results = []

        # Downscale for faster processing
        small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small, model="hog")

        if not face_locations:
            self._age_tracks()
            return []

        self.stats["faces_detected"] += len(face_locations)

        # Get encodings and landmarks for all faces
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
        face_landmarks_list = face_recognition.face_landmarks(rgb_small, face_locations)

        # Process each detected face
        scale_inv = 1.0 / scale
        detected_faces = []

        for (top, right, bottom, left), encoding, landmarks in zip(face_locations, face_encodings, face_landmarks_list):
            # Scale bbox back to original size
            x = int(left * scale_inv)
            y = int(top * scale_inv)
            w = int((right - left) * scale_inv)
            h = int((bottom - top) * scale_inv)

            # [FIX] Expand bbox upward to include forehead/top of head.
            # The HOG detector returns tight bboxes starting at ~eyebrow level,
            # which causes the bounding box to appear too low on the face.
            # Expand upward by 40% of face height to cover full head.
            expand_up = int(h * 0.40)
            y = max(0, y - expand_up)
            h = h + expand_up
            bbox = (x, y, w, h)

            # Scale landmarks back to original size
            scaled_landmarks = {}
            for feature, points in landmarks.items():
                scaled_landmarks[feature] = [(int(pt[0] * scale_inv), int(pt[1] * scale_inv)) for pt in points]

            # Estimate Head Pose (Simplified)
            head_pose = self._estimate_head_pose(scaled_landmarks, bbox)

            # Recognize
            identity, confidence = self.recognize(encoding)

            # Calculate face quality (simple brightness/contrast check)
            face_quality = self._estimate_quality(frame, bbox)

            detected_faces.append({
                "bbox": bbox,
                "encoding": encoding,
                "identity": identity,
                "confidence": confidence,
                "quality": face_quality,
                "landmarks": scaled_landmarks,
                "head_pose": head_pose,
                # [FIX] Add 'label' for standard frontend overlay compatibility
                "label": f"{identity.name} ({int(confidence * 100)}%)" if identity else f"Unknown ({int(confidence * 100)}%)"
            })

        # Update tracking
        if self.enable_tracking:
            results = self._update_tracks(detected_faces)
        else:
            # No tracking - return raw results
                results.append(RecognitionResult(
                    bbox=face["bbox"],
                    identity=face["identity"],
                    confidence=face["confidence"],
                    face_quality=face["quality"],
                    encoding=face["encoding"],
                    landmarks=face["landmarks"],
                    head_pose=face["head_pose"]
                ))

        return results

    def _update_tracks(self, detected_faces: list[dict]) -> list[RecognitionResult]:
        """Update multi-face tracking with new detections."""
        now = time.time()
        results = []

        with self._lock:
            used_tracks = set()

            for face in detected_faces:
                bbox = face["bbox"]

                # Find best matching track
                best_track_id = None
                best_iou = 0

                for track_id, track in self._tracks.items():
                    if track_id in used_tracks:
                        continue
                    iou = self._calculate_iou(bbox, track.last_bbox)
                    if iou > best_iou and iou > self.IOU_THRESHOLD:
                        best_iou = iou
                        best_track_id = track_id

                if best_track_id is not None:
                    # Update existing track
                    track = self._tracks[best_track_id]
                    track.last_bbox = bbox
                    track.last_seen = now
                    track.miss_count = 0
                    track.encoding = face["encoding"]
                    track.landmarks = face["landmarks"]
                    track.head_pose = face["head_pose"]

                    # Update identity if new recognition is more confident
                    if face["confidence"] > track.confidence:
                        track.identity = face["identity"]
                        track.confidence = face["confidence"]

                    used_tracks.add(best_track_id)
                else:
                    # Create new track
                    track_id = self._next_track_id
                    self._next_track_id += 1

                    self._tracks[track_id] = TrackedFace(
                        track_id=track_id,
                        last_bbox=bbox,
                        last_seen=now,
                        identity=face["identity"],
                        confidence=face["confidence"],
                        encoding=face["encoding"],
                        landmarks=face["landmarks"],
                        head_pose=face["head_pose"]
                    )
                    best_track_id = track_id

                # Build result
                track = self._tracks[best_track_id]
                results.append(RecognitionResult(
                    bbox=bbox,
                    identity=track.identity,
                    confidence=track.confidence,
                    track_id=track.track_id,
                    face_quality=face["quality"],
                    encoding=face["encoding"],
                    landmarks=track.landmarks,
                    head_pose=track.head_pose
                ))

            # Age tracks that weren't matched
            self._age_tracks()

        return results

    def _age_tracks(self) -> None:
        """Remove stale tracks."""
        now = time.time()
        stale = []

        for track_id, track in self._tracks.items():
            track.miss_count += 1
            age = now - track.last_seen

            if age > self.MAX_TRACK_AGE or track.miss_count > self.MAX_MISS_COUNT:
                stale.append(track_id)

        for track_id in stale:
            del self._tracks[track_id]

    def _calculate_iou(self, bbox1: tuple, bbox2: tuple) -> float:
        """Calculate Intersection over Union between two bboxes."""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2

        # Calculate intersection
        xi1 = max(x1, x2)
        yi1 = max(y1, y2)
        xi2 = min(x1 + w1, x2 + w2)
        yi2 = min(y1 + h1, y2 + h2)

        if xi2 <= xi1 or yi2 <= yi1:
            return 0.0

        intersection = (xi2 - xi1) * (yi2 - yi1)
        union = w1 * h1 + w2 * h2 - intersection

        return intersection / union if union > 0 else 0.0

    def _estimate_quality(self, frame: np.ndarray, bbox: tuple) -> float:
        """Estimate face image quality (0-1)."""
        x, y, w, h = bbox

        # Clamp to frame bounds
        h_frame, w_frame = frame.shape[:2]
        x = max(0, min(x, w_frame - 1))
        y = max(0, min(y, h_frame - 1))
        w = min(w, w_frame - x)
        h = min(h, h_frame - y)

        if w <= 0 or h <= 0:
            return 0.0

        face_roi = frame[y:y+h, x:x+w]

        # Simple quality metrics
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

        # Brightness (0-255, ideal around 127)
        brightness = np.mean(gray)
        brightness_score = 1.0 - abs(brightness - 127) / 127

        # Contrast (higher is better)
        contrast = np.std(gray)
        contrast_score = min(1.0, contrast / 60)

        # Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        sharpness_score = min(1.0, sharpness / 500)

        # Size penalty (smaller faces = lower quality)
        size = w * h
        min_size = 64 * 64
        size_score = min(1.0, size / min_size)

        # Combined score
        quality = (brightness_score * 0.2 +
                  contrast_score * 0.3 +
                  sharpness_score * 0.3 +
                  size_score * 0.2)

        return max(0, min(1, quality))

    def _estimate_head_pose(self, landmarks: dict, bbox: tuple) -> dict[str, float]:
        """Simplified head pose estimation (Pitch, Yaw, Roll) from landmarks."""
        try:
            # Requirements: eyes, nose, chin
            left_eye = landmarks.get("left_eye")
            right_eye = landmarks.get("right_eye")
            landmarks.get("nose_bridge")
            nose_tip = landmarks.get("nose_tip")
            chin = landmarks.get("chin")

            if not all([left_eye, right_eye, nose_tip, chin]):
                return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}

            # 1. Roll (Rotation in image plane)
            # Calculated from eye centers
            le_c = np.mean(left_eye, axis=0)
            re_c = np.mean(right_eye, axis=0)
            roll = np.degrees(np.arctan2(re_c[1] - le_c[1], re_c[0] - le_c[0]))

            # 2. Yaw (Side to side rotation)
            # Calculated by nose tip relative to eye horizontal span
            nose_c = nose_tip[0] # Take first nose tip point
            mid_eyes = (le_c[0] + re_c[0]) / 2
            eye_dist = re_c[0] - le_c[0]
            yaw = ((nose_c[0] - mid_eyes) / eye_dist) * 90.0

            # 3. Pitch (Up and down rotation)
            # Calculated by nose tip relative to eye-chin vertical span
            eye_y = (le_c[1] + re_c[1]) / 2
            chin_y = chin[8][1] # Chin center
            face_height = chin_y - eye_y
            nose_y = nose_tip[0][1]
            # Ideal nose-to-eye vs height ratio is approx 0.35
            pitch = ((nose_y - eye_y) / face_height - 0.35) * 180.0

            return {
                "pitch": round(float(pitch), 2),
                "yaw": round(float(yaw), 2),
                "roll": round(float(roll), 2)
            }
        except Exception:
            return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}

    # ========================
    # Enrollment Methods
    # ========================

    def enroll_face(self, frame: np.ndarray, name: str,
                   role: str = "user",
                   face_location: tuple | None = None) -> FaceIdentity | None:
        """
        Enroll a new face from a frame.

        Args:
            frame: BGR image containing the face
            name: Name for the identity
            role: Role (user, admin, guest)
            face_location: Optional (x, y, w, h) bbox

        Returns:
            Created FaceIdentity, or None if enrollment failed
        """
        encoding, bbox = self.encode_face(frame, face_location)

        if encoding is None:
            return None

        # Check if name already exists
        existing = self.db.get_identity_by_name(name)
        if existing:
            # Add embedding to existing identity
            self.db.add_embedding(existing.id, encoding)
            self._cache_timestamp = 0  # Force cache refresh
            return existing

        # Create new identity
        identity = self.db.create_identity(name, role)
        self.db.add_embedding(identity.id, encoding)
        self._cache_timestamp = 0  # Force cache refresh

        return identity

    def add_training_sample(self, identity_id: str, frame: np.ndarray,
                           face_location: tuple | None = None) -> bool:
        """
        Add additional training sample to existing identity.

        Args:
            identity_id: UUID of identity to train
            frame: BGR image containing the face
            face_location: Optional (x, y, w, h) bbox

        Returns:
            True if sample added successfully
        """
        encoding, _ = self.encode_face(frame, face_location)

        if encoding is None:
            return False

        result = self.db.add_embedding(identity_id, encoding)
        if result:
            self._cache_timestamp = 0  # Force cache refresh

        return result is not None

    def get_tracks(self) -> dict[int, dict[str, Any]]:
        """Get current active tracks."""
        with self._lock:
            return {
                track_id: {
                    "bbox": track.last_bbox,
                    "identity_name": track.identity.name if track.identity else "Unknown",
                    "identity_id": track.identity.id if track.identity else None,
                    "confidence": track.confidence,
                    "age": time.time() - track.last_seen
                }
                for track_id, track in self._tracks.items()
            }

    def clear_tracks(self) -> None:
        """Clear all tracking state."""
        with self._lock:
            self._tracks.clear()
            self._next_track_id = 1


# Global engine instance
_engine_instance: FaceRecognitionEngine | None = None


def get_face_engine() -> FaceRecognitionEngine:
    """Get global face recognition engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = FaceRecognitionEngine()
    return _engine_instance
