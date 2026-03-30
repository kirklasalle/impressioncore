"""
Face Identity Manager
=====================
Facial recognition system for the Kinect Controller.
Uses dlib/face_recognition for face embeddings and identification.

Features:
- Face embedding extraction (128-dimensional vectors)
- Identity database with persistent storage
- Real-time face matching with confidence scores
- Multiple face tracking with identity assignment

Requirements:
- face_recognition (pip install face_recognition)
- OR dlib with shape predictor model
- numpy

Author: ImpressionCore Team
Created: January 2026
"""

import logging
import os
import pickle
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)

# Try to import face_recognition, fall back to dlib
try:
    import face_recognition
    FACE_LIB = "face_recognition"
except ImportError:
    try:
        import dlib  # noqa: F401
        FACE_LIB = "dlib"
    except ImportError:
        FACE_LIB = None
        logger.warning("No face recognition library available. Install face_recognition or dlib.")


@dataclass
class FaceEmbedding:
    """A face embedding with associated identity"""
    name: str
    embedding: np.ndarray
    created_at: str  # ISO timestamp

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "embedding": self.embedding.tolist(),
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FaceEmbedding":
        return cls(
            name=data["name"],
            embedding=np.array(data["embedding"]),
            created_at=data["created_at"]
        )


class FaceIdentityManager:
    """
    Manages face embeddings and identity recognition.

    Usage:
        manager = FaceIdentityManager("faces.db")

        # Register a new face
        embedding = manager.extract_embedding(face_image)
        manager.register_face("Alice", embedding)

        # Identify a face
        name, confidence = manager.identify(face_image)
    """

    # Recognition threshold (0.0 = exact match, 1.0 = no match)
    # Lower is more strict
    DEFAULT_THRESHOLD = 0.6

    def __init__(self, database_path: str = "face_identities.pkl"):
        """
        Initialize the Face Identity Manager.

        Args:
            database_path: Path to persistent face database
        """
        self.database_path = database_path
        self.identities: list[FaceEmbedding] = []
        self.threshold = self.DEFAULT_THRESHOLD

        # Load existing database
        self._load_database()

        logger.info(f"FaceIdentityManager initialized with {len(self.identities)} identities")

    def _load_database(self):
        """Load identities from persistent storage"""
        if os.path.exists(self.database_path):
            try:
                with open(self.database_path, 'rb') as f:
                    data = pickle.load(f)
                self.identities = [FaceEmbedding.from_dict(d) for d in data]
                logger.info(f"Loaded {len(self.identities)} identities from {self.database_path}")
            except Exception as e:
                logger.error(f"Failed to load identity database: {e}")
                self.identities = []

    def _save_database(self):
        """Save identities to persistent storage"""
        try:
            data = [emb.to_dict() for emb in self.identities]
            with open(self.database_path, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"Saved {len(self.identities)} identities to {self.database_path}")
        except Exception as e:
            logger.error(f"Failed to save identity database: {e}")

    def extract_embedding(self, face_image: np.ndarray) -> np.ndarray | None:
        """
        Extract a 128-dimensional face embedding from an image.

        Args:
            face_image: BGR image containing a face (ideally cropped to face region)

        Returns:
            128-D numpy array, or None if no face found
        """
        if FACE_LIB is None:
            logger.error("No face recognition library available")
            return None

        if FACE_LIB == "face_recognition":
            try:
                # face_recognition expects RGB
                rgb_image = face_image[:, :, ::-1]  # BGR to RGB

                # Get face locations and encodings
                face_locations = face_recognition.face_locations(rgb_image)
                if not face_locations:
                    return None

                encodings = face_recognition.face_encodings(rgb_image, face_locations)
                if encodings:
                    return encodings[0]
            except Exception as e:
                logger.error(f"Embedding extraction error: {e}")

        return None

    def register_face(self, name: str, embedding: np.ndarray) -> bool:
        """
        Register a new face identity.

        Args:
            name: Name/identifier for this face
            embedding: 128-D face embedding

        Returns:
            True if registration succeeded
        """
        if embedding is None or len(embedding) != 128:
            logger.error("Invalid embedding")
            return False

        from datetime import datetime

        face_emb = FaceEmbedding(
            name=name,
            embedding=embedding,
            created_at=datetime.now().isoformat()
        )

        self.identities.append(face_emb)
        self._save_database()

        logger.info(f"Registered new face: {name}")
        return True

    def register_from_image(self, name: str, face_image: np.ndarray) -> bool:
        """
        Register a face directly from an image.

        Args:
            name: Name for this identity
            face_image: BGR image containing the face

        Returns:
            True if registration succeeded
        """
        embedding = self.extract_embedding(face_image)
        if embedding is None:
            logger.warning(f"No face found in image for {name}")
            return False

        return self.register_face(name, embedding)

    def identify(self, face_image: np.ndarray) -> tuple[str, float]:
        """
        Identify a face from an image.

        Args:
            face_image: BGR image containing a face

        Returns:
            Tuple of (name, confidence) where confidence is 0-1
            Returns ("Unknown", 0.0) if no match
        """
        if not self.identities:
            return ("Unknown", 0.0)

        embedding = self.extract_embedding(face_image)
        if embedding is None:
            return ("Unknown", 0.0)

        return self.identify_by_embedding(embedding)

    def identify_by_embedding(self, embedding: np.ndarray) -> tuple[str, float]:
        """
        Identify a face by its embedding vector.

        Args:
            embedding: 128-D face embedding

        Returns:
            Tuple of (name, confidence)
        """
        if not self.identities:
            return ("Unknown", 0.0)

        best_match = None
        best_distance = float('inf')

        for identity in self.identities:
            # Euclidean distance
            distance = np.linalg.norm(embedding - identity.embedding)
            if distance < best_distance:
                best_distance = distance
                best_match = identity.name

        # Convert distance to confidence (0 = no match, 1 = perfect match)
        # Using formula: confidence = max(0, 1 - distance/threshold)
        if best_distance < self.threshold:
            confidence = max(0.0, min(1.0, 1.0 - best_distance / self.threshold))
            return (best_match, confidence)

        return ("Unknown", 0.0)

    def list_identities(self) -> list[str]:
        """Get list of all registered identity names"""
        return list(set(emb.name for emb in self.identities))

    def remove_identity(self, name: str) -> int:
        """
        Remove all embeddings for an identity.

        Args:
            name: Name to remove

        Returns:
            Number of embeddings removed
        """
        original_count = len(self.identities)
        self.identities = [emb for emb in self.identities if emb.name != name]
        removed = original_count - len(self.identities)

        if removed > 0:
            self._save_database()
            logger.info(f"Removed {removed} embeddings for {name}")

        return removed

    def clear_database(self):
        """Remove all identities"""
        self.identities = []
        self._save_database()
        logger.info("Cleared identity database")


# ============================================================================
# KINECT INTEGRATION HELPER
# ============================================================================

class KinectFaceRecognizer:
    """
    Helper class to integrate face recognition with KinectController.
    Combines head tracking with facial recognition.
    """

    def __init__(self, controller, database_path: str = "kinect_faces.pkl"):
        """
        Args:
            controller: KinectController instance
            database_path: Path to face database
        """
        self.controller = controller
        self.identity_manager = FaceIdentityManager(database_path)
        self.current_identities: dict[int, tuple[str, float]] = {}  # skeleton_id -> (name, confidence)

    def process_frame(self, color_frame: np.ndarray) -> dict[int, tuple[str, float]]:
        """
        Process a frame and identify all visible faces.
        Links identified faces to skeleton tracking IDs.

        Args:
            color_frame: BGR color frame from Kinect

        Returns:
            Dict mapping skeleton tracking ID to (name, confidence)
        """
        results = {}

        # Get all tracked skeletons
        skeletons = self.controller.get_skeleton_frame()

        for skeleton in skeletons:
            # Get head joint position
            if len(skeleton.joints) > 3:  # HEAD is joint 3
                head = skeleton.joints[3]

                # Extract face region (approximate)
                # This would be enhanced with actual face detection
                face_region = self._extract_face_region(color_frame, head)

                if face_region is not None:
                    name, confidence = self.identity_manager.identify(face_region)
                    results[skeleton.tracking_id] = (name, confidence)

        self.current_identities = results
        return results

    def _extract_face_region(self, frame: np.ndarray, head_joint) -> np.ndarray | None:
        """
        Extract face region from frame based on skeleton head position.

        This is a simplified version - proper implementation would use
        depth data and camera intrinsics for accurate projection.
        """
        if head_joint.z <= 0:
            return None

        h, w = frame.shape[:2]

        # Approximate projection (simplified)
        focal_length = 580.0  # Approximate Kinect focal length
        cx, cy = w / 2, h / 2

        x_screen = int((head_joint.x / head_joint.z) * focal_length + cx)
        y_screen = int(-(head_joint.y / head_joint.z) * focal_length + cy)

        # Face region size based on distance
        face_size = int(200 / head_joint.z)  # Approximate face size
        face_size = max(50, min(200, face_size))

        # Extract region
        x1 = max(0, x_screen - face_size // 2)
        y1 = max(0, y_screen - face_size // 2)
        x2 = min(w, x_screen + face_size // 2)
        y2 = min(h, y_screen + face_size // 2)

        if x2 - x1 < 30 or y2 - y1 < 30:
            return None

        return frame[y1:y2, x1:x2]


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)

    print("Face Identity Manager Test")
    print(f"Face recognition library: {FACE_LIB or 'None (install face_recognition)'}")

    manager = FaceIdentityManager("test_faces.pkl")
    print(f"Registered identities: {manager.list_identities()}")
