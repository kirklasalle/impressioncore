"""
Vision Tool - Kinect/PS Eye Integration

Created: January 13, 2026
Author: ImpressionCore Team

Tool for Agent0Core to interact with ImpressionCore's vision systems.
Connects to real KinectConnector and FaceIdentityManager implementations.
"""

import logging
import sys
from pathlib import Path
from typing import Any

# Add ImpressionCore src to path for imports
_project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_project_root / "src"))

from ..face_interpreter import FaceInterpreter
from ..governance import require_law_compliance
from ..pose_interpreter import PoseInterpreter

logger = logging.getLogger("agent0core.tools.vision")


class VisionTool:
    """
    Tool for interacting with ImpressionCore's vision systems.

    Supports:
    - Kinect v1 (RGB, Depth, IR, Face Detection)
    - PlayStation Eye cameras
    - HCEP (Human Conversation Eye Points)
    - Face Identity Recognition
    """

    name = "vision_tool"
    description = "Control ImpressionCore's vision systems (Kinect, PS Eye, Face Recognition)"

    def __init__(self):
        """Initialize the vision tool."""
        self._kinect_connector = None
        self._face_manager = None
        self._kinect_recognizer = None
        self._pose_interpreter = PoseInterpreter()
        self._face_interpreter = FaceInterpreter()
        self._initialized = False
        logger.info("VisionTool initialized (lazy loading enabled)")

    def _lazy_load_kinect(self) -> bool:
        """Lazy load the Kinect connector."""
        if self._kinect_connector is not None:
            return True

        try:
            from orchestrator.kinect_connector import KinectConnector
            self._kinect_connector = KinectConnector()
            if self._kinect_connector.open():
                logger.info("Kinect connector loaded and opened")
                return True
            else:
                logger.warning("Kinect connector loaded but failed to open")
                return False
        except ImportError as e:
            logger.warning(f"Kinect connector not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Kinect: {e}")
            return False

    def _lazy_load_face_manager(self) -> bool:
        """Lazy load the face recognition engine."""
        if self._face_manager is not None:
            return True

        try:
            from orchestrator.face_recognition_engine import get_face_engine
            self._face_manager = get_face_engine()
            logger.info("FaceRecognitionEngine loaded via get_face_engine()")
            return True
        except ImportError as e:
            logger.warning(f"FaceRecognitionEngine not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize FaceRecognitionEngine: {e}")
            return False

    def _lazy_load_kinect_recognizer(self) -> bool:
        """Lazy load the Kinect face recognizer."""
        if self._kinect_recognizer is not None:
            return True

        if not self._lazy_load_kinect():
            return False

        try:
            from vision.face_identity import KinectFaceRecognizer
            self._kinect_recognizer = KinectFaceRecognizer(self._kinect_connector)
            logger.info("KinectFaceRecognizer loaded")
            return True
        except ImportError as e:
            logger.warning(f"KinectFaceRecognizer not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize KinectFaceRecognizer: {e}")
            return False

    @require_law_compliance
    async def execute(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a vision action.

        Args:
            action: The action to perform
            params: Optional parameters

        Returns:
            Result dictionary
        """
        params = params or {}

        if action == "list_cameras":
            return await self._list_cameras()
        elif action == "get_frame":
            return await self._get_frame(params.get("stream", "color"))
        elif action == "detect_faces":
            return await self._detect_faces()
        elif action == "identify_face":
            return await self._identify_face(params.get("image"))
        elif action == "register_face":
            return await self._register_face(
                params.get("name", "Unknown"),
                params.get("image")
            )
        elif action == "list_identities":
            return await self._list_identities()
        elif action == "start_stream":
            return await self._start_stream(params.get("stream", "color"))
        elif action == "stop_stream":
            return await self._stop_stream()
        elif action == "get_depth":
            return await self._get_depth(
                params.get("x"),
                params.get("y")
            )
        elif action == "set_tilt":
            return await self._set_tilt(params.get("angle", 0))
        elif action == "get_skeleton":
            return await self._get_skeleton()
        elif action == "get_body_pose":
            return await self._get_body_pose()
        elif action == "get_face_analysis":
            return await self._get_face_analysis()
        else:
            return {"error": f"Unknown action: {action}", "available_actions": [
                "list_cameras", "get_frame", "detect_faces", "identify_face",
                "register_face", "list_identities", "start_stream", "stop_stream",
                "get_depth", "set_tilt", "get_skeleton", "get_body_pose",
                "get_face_analysis"
            ]}

    async def _list_cameras(self) -> dict[str, Any]:
        """List available cameras."""
        cameras = []

        # Check for Kinect
        if self._lazy_load_kinect():
            cameras.append({
                "id": "kinect",
                "name": "Xbox 360 Kinect",
                "streams": ["color", "depth", "ir"],
                "status": "connected" if self._kinect_connector.isOpened() else "disconnected",
            })

        return {"cameras": cameras, "count": len(cameras)}

    async def _get_frame(self, stream: str = "color") -> dict[str, Any]:
        """Get a frame from a camera stream."""
        if not self._lazy_load_kinect():
            return {"error": "Kinect not available"}

        try:
            frames = self._kinect_connector.read()
            if frames:
                if stream == "color" and "color" in frames:
                    frame = frames["color"]
                    return {
                        "status": "success",
                        "stream": stream,
                        "shape": list(frame.shape),
                        "dtype": str(frame.dtype),
                    }
                elif stream in ["depth", "ir", "sub"] and "sub" in frames:
                    frame = frames["sub"]
                    return {
                        "status": "success",
                        "stream": stream,
                        "shape": list(frame.shape),
                        "dtype": str(frame.dtype),
                    }
                else:
                    return {"error": f"Stream '{stream}' not available in frames"}
            else:
                return {"error": "No frames available - sensor may be warming up"}
        except Exception as e:
            return {"error": str(e)}

    async def _detect_faces(self) -> dict[str, Any]:
        """Detect and identify faces using the new Face Engine."""
        if not self._lazy_load_face_manager():
            return {"error": "Face engine not available"}

        try:
            from orchestrator.orbcloud_vision import get_vision_layer
            vision = get_vision_layer()

            # Get latest frames from vision layer
            cam_id = 98 # Default to Kinect
            frame = vision._frames.get(cam_id)
            if frame is None:
                # Try fallback standard cam
                for cid in vision.caps:
                    frame = vision._frames.get(cid)
                    if frame is not None:
                        cam_id = cid
                        break

            if frame is not None:
                results = self._face_manager.process_frame(frame)

                from orchestrator.emotion_analyzer import get_emotion_analyzer
                from orchestrator.liveness_detector import get_liveness_detector
                emotion_analyzer = get_emotion_analyzer()
                liveness_detector = get_liveness_detector()

                faces = []
                for res in results:
                    face_data = res.to_dict()

                    # Optional emotion analysis
                    if emotion_analyzer.is_available():
                        emo_res = emotion_analyzer.analyze_face(frame, res.bbox, res.track_id)
                        if emo_res:
                            face_data["emotion"] = emo_res.to_dict()

                    # Liveness check
                    depth_frame = vision._frames.get(105) # Kinect depth
                    live_res = liveness_detector.check_liveness(frame, res.bbox, res.track_id, depth_frame)
                    face_data["liveness"] = live_res.to_dict()

                    # Social Analysis
                    face_data["social_tags"] = self._face_interpreter.analyze(face_data)
                    face_data["social_summary"] = self._face_interpreter.get_summary_string(
                        face_data["social_tags"],
                        face_data.get("identity_name", "the user")
                    )

                    faces.append(face_data)

                return {"faces": faces, "count": len(faces), "camera_id": cam_id}
            else:
                return {"faces": [], "count": 0, "error": "No camera frames available"}
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return {"error": str(e)}

    async def _identify_face(self, image=None) -> dict[str, Any]:
        """Identify a face from an image."""
        if not self._lazy_load_face_manager():
            return {"error": "FaceIdentityManager not available"}

        if image is None:
            # Try to get from Kinect
            if not self._lazy_load_kinect():
                return {"error": "No image provided and Kinect not available"}

            frames = self._kinect_connector.read()
            if frames and "color" in frames:
                image = frames["color"]
            else:
                return {"error": "No image available"}

        try:
            name, confidence = self._face_manager.identify(image)
            return {"name": name, "confidence": confidence}
        except Exception as e:
            return {"error": str(e)}

    async def _register_face(self, name: str, image=None) -> dict[str, Any]:
        """Register a new face identity."""
        if not self._lazy_load_face_manager():
            return {"error": "FaceIdentityManager not available"}

        if image is None:
            # Try to get from Kinect
            if not self._lazy_load_kinect():
                return {"error": "No image provided and Kinect not available"}

            frames = self._kinect_connector.read()
            if frames and "color" in frames:
                image = frames["color"]
            else:
                return {"error": "No image available"}

        try:
            success = self._face_manager.register_from_image(name, image)
            if success:
                return {"status": "success", "message": f"Registered face for '{name}'"}
            else:
                return {"status": "failed", "message": "Could not extract face from image"}
        except Exception as e:
            return {"error": str(e)}

    async def _list_identities(self) -> dict[str, Any]:
        """List all registered face identities."""
        if not self._lazy_load_face_manager():
            return {"error": "FaceIdentityManager not available"}

        try:
            identities = self._face_manager.list_identities()
            return {"identities": identities, "count": len(identities)}
        except Exception as e:
            return {"error": str(e)}

    async def _start_stream(self, stream: str = "color") -> dict[str, Any]:
        """Start a camera stream."""
        if not self._lazy_load_kinect():
            return {"error": "Kinect not available"}

        # Kinect is always "streaming" when opened
        return {
            "status": "success",
            "stream": stream,
            "message": "Kinect stream active"
        }

    async def _stop_stream(self) -> dict[str, Any]:
        """Stop and release camera resources."""
        if self._kinect_connector:
            self._kinect_connector.release()
            self._kinect_connector = None
            return {"status": "success", "message": "Kinect released"}
        return {"status": "success", "message": "No active streams"}

    async def _get_depth(self, x: int | None, y: int | None) -> dict[str, Any]:
        """Get depth value at a specific point."""
        if not self._lazy_load_kinect():
            return {"error": "Kinect not available"}

        try:
            # Switch to depth mode if needed
            self._kinect_connector.switch_sub_mode(4)  # NUI_IMAGE_TYPE_DEPTH

            frames = self._kinect_connector.read()
            if frames and "sub" in frames:
                depth_frame = frames["sub"]
                if x is not None and y is not None:
                    # Get specific point
                    distance = self._kinect_connector.get_distance_at(x, y, depth_frame)
                    return {"x": x, "y": y, "distance_mm": distance}
                else:
                    # Return frame info
                    return {
                        "status": "success",
                        "shape": list(depth_frame.shape),
                        "min_mm": int(depth_frame.min()),
                        "max_mm": int(depth_frame.max()),
                    }
            else:
                return {"error": "No depth frame available"}
        except Exception as e:
            return {"error": str(e)}

    async def _set_tilt(self, angle: float) -> dict[str, Any]:
        """Set Kinect tilt angle."""
        if not self._lazy_load_kinect():
            return {"error": "Kinect not available"}

        try:
            self._kinect_connector.set_tilt(angle)
            return {"status": "success", "angle": angle}
        except Exception as e:
            return {"error": str(e)}

    async def _get_skeleton(self) -> dict[str, Any]:
        """Get the current tracked skeleton data."""
        try:
            from orchestrator.orbcloud_vision import get_vision_layer
            vision = get_vision_layer()
            skeleton = getattr(vision, "latest_skeleton", None)

            if skeleton:
                return {"status": "success", "skeleton": skeleton}
            else:
                return {"status": "success", "skeleton": None, "message": "No skeleton currently tracked"}
        except Exception as e:
            logger.error(f"Failed to get skeleton: {e}")
            return {"error": str(e)}

    async def _get_body_pose(self) -> dict[str, Any]:
        """Get semantic body language/pose tags."""
        skel_res = await self._get_skeleton()
        if "error" in skel_res:
            return skel_res

        skeleton = skel_res.get("skeleton")
        if not skeleton:
            return {"status": "success", "poses": [], "summary": "No user detected in view."}

        try:
            poses = self._pose_interpreter.analyze(skeleton)
            summary = self._pose_interpreter.get_summary_string(poses)
            return {
                "status": "success",
                "poses": poses,
                "summary": summary,
                "confidence": 0.9 if skeleton.get("tracked") else 0.1
            }
        except Exception as e:
            logger.error(f"Pose analysis failed: {e}")
            return {"error": str(e)}

    async def _get_face_analysis(self) -> dict[str, Any]:
        """Get semantic analysis for all visible faces."""
        det_res = await self._detect_faces()
        if "error" in det_res:
            return det_res

        faces = det_res.get("faces", [])
        if not faces:
            return {"status": "success", "faces": [], "summary": "I don't see anyone right now."}

        # Compile a master summary
        summaries = [f.get("social_summary") for f in faces]
        return {
            "status": "success",
            "faces": faces,
            "summary": " ".join(summaries),
            "count": len(faces)
        }

    def cleanup(self):
        """Release all resources."""
        if self._kinect_connector:
            self._kinect_connector.release()
            self._kinect_connector = None
        logger.info("VisionTool resources released")
