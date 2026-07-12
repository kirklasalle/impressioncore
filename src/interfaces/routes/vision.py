import time
import asyncio
from typing import Any
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from src.interfaces import api_state
from src.orchestrator.system_logger import log_event
from src.orchestrator.sensory_intelligence import sensory_intel
from src.orchestrator.kinect_fusion_adapter import KinectFusionAdapter

try:
    import cv2
except ImportError:
    cv2 = None
import numpy as np

# Import face recognition modules
try:
    from src.orchestrator.emotion_analyzer import get_emotion_analyzer
    from src.orchestrator.face_database import FaceIdentity, get_face_database
    from src.orchestrator.face_recognition_engine import RecognitionResult, get_face_engine
    from src.orchestrator.liveness_detector import get_liveness_detector
    FACE_REC_MODULES_AVAILABLE = True
except ImportError as e:
    log_event("API", f"Face recognition modules not available: {e}", level="WARNING")
    FACE_REC_MODULES_AVAILABLE = False

router = APIRouter()

# Pydantic models
class KinectStreamToggle(BaseModel):
    stream: str
    enabled: bool

class KinectStreamUpdate(BaseModel):
    stream: str
    enabled: bool

class KinectParameterUpdate(BaseModel):
    smoothing: float = 0.5
    correction: float = 0.5
    prediction: float = 0.5
    jitter: float = 0.05
    deviation: float = 0.04

class FaceEnrollRequest(BaseModel):
    name: str
    role: str = "user"

class FaceUpdateRequest(BaseModel):
    name: str | None = None
    role: str | None = None
    metadata: dict[str, Any] | None = None

# WebSocket clients
_skeleton_ws_clients: list[WebSocket] = []

def generate_mjpeg_stream(target_cam_id: int | None = None, quality: int = 60, max_fps: int = 30, scale: float = 1.0):
    """Generator for MJPEG stream from the active vision layer."""
    if cv2 is None:
        log_event("VISION_STREAM", "OpenCV is unavailable; MJPEG streaming is disabled.", level="WARNING")
        return

    triad = api_state.triad_instance
    if not triad or not triad.vision:
        return

    # JPEG encoding parameters for speed
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]

    # Calculate sleep time based on target FPS
    frame_time = 1.0 / max_fps

    # Create fallback "NO SIGNAL" frame
    fallback_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(fallback_frame, "NO SIGNAL", (180, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    last_log_time = 0

    while True:
        try:
            start_time = time.time()
            frame = None
            vision = triad.vision

            if vision:
                # 1. Fetch Targeted Frame
                if target_cam_id is not None:
                    frame = vision.get_frame(target_cam_id)

                    # Handle Specialized Fallbacks (Only if requested cam is missing)
                    if frame is None:
                        if str(target_cam_id) in ["105", "106"]:
                            pass
                        elif "98" in vision._frames:
                            frame = vision.get_frame("98")
                            if frame is not None:
                                if start_time - last_log_time > 10:
                                    log_event("VISION_STREAM", f"Redirecting missing cam {target_cam_id} to Kinect Color (98)")
                                    last_log_time = start_time

                # 2. Global Fallback Logic (Auto-Detect)
                else:
                    for priority_id in ["98", "106", "105", "0", "1"]:
                        frame = vision.get_frame(priority_id)
                        if frame is not None:
                            break

                # 3. Placeholder Logic
                if frame is None and target_cam_id is not None:
                    blank = np.zeros((480, 640, 3), dtype=np.uint8)
                    label = f"SEARCHING FOR CAM {target_cam_id}..."
                    if str(target_cam_id) == "105":
                        label = "KINECT DEPTH STREAM SEARCHING..."
                    if str(target_cam_id) == "106":
                        label = "KINECT IR STREAM SEARCHING..."
                    cv2.putText(blank, label, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    frame = blank

            if frame is None:
                _, jpeg = cv2.imencode('.jpg', fallback_frame, encode_params)
            else:
                if scale < 1.0 and frame is not None:
                    new_size = (int(frame.shape[1] * scale), int(frame.shape[0] * scale))
                    frame = cv2.resize(frame, new_size, interpolation=cv2.INTER_NEAREST)

                _, jpeg = cv2.imencode('.jpg', frame, encode_params)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

        except Exception:
            _, jpeg = cv2.imencode('.jpg', fallback_frame, encode_params)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            time.sleep(1)

@router.get("/v1/vision/kinect/fusion")
async def get_kinect_fusion_status():
    triad = api_state.triad_instance
    if not triad or not triad.vision:
        return {"status": "ERROR", "detail": "Vision not initialized"}

    if not api_state.kinect_fusion_adapter:
        api_state.kinect_fusion_adapter = KinectFusionAdapter()

    api_state.kinect_fusion_adapter.refresh(triad.vision)
    return {"status": "OK", "fusion": api_state.kinect_fusion_adapter.get_status()}

@router.get("/v1/vision/diagnostics")
async def get_vision_diagnostics():
    return sensory_intel.get_diagnostics()

@router.get("/v1/vision/device_tree")
async def get_vision_device_tree():
    return sensory_intel.device_tree

@router.get("/v1/vision/startup_report")
async def get_vision_startup_report():
    triad = api_state.triad_instance
    if not triad or not triad.vision:
        raise HTTPException(status_code=503, detail="Vision layer not initialized")
    return getattr(triad.vision, "startup_report", {"status": "NOT_STARTED"})

@router.get("/v1/vision/kinect/streams")
async def get_kinect_streams():
    """Get current enabled state of Kinect streams."""
    triad = api_state.triad_instance
    if not triad or not triad.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    kinect = triad.vision.caps.get(98)
    if not kinect:
         for cap in triad.vision.caps.values():
             if hasattr(cap, "enabled_streams"):
                 kinect = cap
                 break

    if not kinect:
         raise HTTPException(status_code=404, detail="Kinect not connected")

    return kinect.enabled_streams

@router.post("/v1/vision/kinect/streams")
async def set_kinect_streams(update: KinectStreamUpdate):
    """Enable or disable specific Kinect streams."""
    triad = api_state.triad_instance
    if not triad or not triad.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    kinect = triad.vision.caps.get(98)
    if not kinect:
         for cap in triad.vision.caps.values():
             if hasattr(cap, "enabled_streams"):
                 kinect = cap
                 break

    if not kinect:
         raise HTTPException(status_code=404, detail="Kinect not connected")

    success = kinect.set_stream_state(update.stream, update.enabled)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to set stream {update.stream}")

    return {"status": "OK", "stream": update.stream, "enabled": update.enabled}

@router.get("/v1/vision/kinect/parameters")
async def get_kinect_parameters():
    """Get current Kinect smoothing and physical parameters."""
    triad = api_state.triad_instance
    if not triad or not triad.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    kinect = triad.vision.caps.get(98)
    if not kinect:
         for cap in triad.vision.caps.values():
             if hasattr(cap, "smooth_params"):
                 kinect = cap
                 break

    if not kinect:
         raise HTTPException(status_code=404, detail="Kinect not connected")

    p = kinect.smooth_params
    return {
        "smoothing": p.fSmoothing,
        "correction": p.fCorrection,
        "prediction": p.fPrediction,
        "jitter": p.fJitterRadius,
        "deviation": p.fMaxDeviationRadius
    }

@router.post("/v1/vision/kinect/parameters")
async def set_kinect_parameters(params: KinectParameterUpdate):
    """Update Kinect smoothing parameters dynamically."""
    triad = api_state.triad_instance
    if not triad or not triad.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    kinect = triad.vision.caps.get(98)
    if not kinect:
         for cap in triad.vision.caps.values():
             if hasattr(cap, "set_smoothing_parameters"):
                 kinect = cap
                 break

    if not kinect:
         raise HTTPException(status_code=404, detail="Kinect not connected")

    kinect.set_smoothing_parameters(
        params.smoothing, params.correction, params.prediction,
        params.jitter, params.deviation
    )
    return {"status": "OK", "params": params}

@router.get("/v1/vision/trace")
async def trace_vision_signal():
    """Debug Endpoint: Traces the camera signal path to find breaks."""
    triad = api_state.triad_instance
    trace = {
        "1_server_status": "ONLINE",
        "2_triad_instance": triad is not None,
        "3_vision_layer_instantiated": triad.vision is not None if triad else False,
        "4_vision_is_running": triad.vision._is_running if triad and triad.vision else False,
        "5_buffer_thread_alive": triad.vision._buffer_thread.is_alive() if triad and triad.vision else False,
        "6_active_caps": list(triad.vision.caps.keys()) if triad and triad.vision else [],
        "7_latest_buffer_timestamp": triad.vision.visual_buffer[-1]['timestamp'] if triad and triad.vision and triad.vision.visual_buffer else "EMPTY",
        "8_frames_in_buffer": list(triad.vision._frames.keys()) if triad and triad.vision else [],
    }
    return trace

@router.get("/v1/vision/stream")
async def vision_stream(
    cam_id: int | None = None,
    quality: int = 60,
    fps: int = 30,
    scale: float = 1.0
):
    """MJPEG video stream from camera."""
    if cv2 is None:
        raise HTTPException(status_code=503, detail="Vision streaming unavailable: OpenCV (cv2) is not installed")

    triad = api_state.triad_instance
    id_to_use = cam_id
    if id_to_use is None and triad and triad.vision:
        id_to_use = triad.vision.active_cam_id

    if triad and triad.vision:
        if fps <= 15:
            triad.vision.inference_fps_limit = 5.0
        elif fps <= 24:
            triad.vision.inference_fps_limit = 10.0
        else:
            triad.vision.inference_fps_limit = 15.0

    quality = max(10, min(100, quality))
    fps = max(1, min(60, fps))
    scale = max(0.1, min(1.0, scale))

    return StreamingResponse(
        generate_mjpeg_stream(id_to_use, quality=quality, max_fps=fps, scale=scale),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/v1/vision/faces")
async def list_faces():
    """List all enrolled face identities."""
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    db = get_face_database()
    identities = db.list_identities()

    return {
        "status": "OK",
        "count": len(identities),
        "faces": [
            {
                "id": identity.id,
                "name": identity.name,
                "role": identity.role,
                "embedding_count": identity.embedding_count,
                "created_at": identity.created_at,
                "updated_at": identity.updated_at
            }
            for identity in identities
        ]
    }

@router.post("/v1/vision/faces")
async def enroll_face(request: FaceEnrollRequest):
    """Enroll a new face by capturing from the active camera."""
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    triad = api_state.triad_instance
    if not triad or not triad.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    frames = triad.vision._frames
    cam_id = triad.vision.active_cam_id

    if cam_id not in frames:
        try:
            if int(cam_id) in frames:
                cam_id = int(cam_id)
        except Exception:
            pass
    if cam_id not in frames and str(cam_id) in frames:
        cam_id = str(cam_id)
    if cam_id not in frames:
        raise HTTPException(status_code=404, detail=f"No frame available from camera {cam_id}. Available: {list(frames.keys())}")

    frame = frames[cam_id]
    engine = get_face_engine()
    identity = engine.enroll_face(frame, request.name, request.role)

    if identity is None:
        raise HTTPException(status_code=400, detail="No face detected in frame. Please position face clearly in camera view.")

    log_event("FACE_REC", f"Enrolled face: {identity.name} (ID: {identity.id})")
    return {
        "status": "OK",
        "message": f"Successfully enrolled {identity.name}",
        "identity": {
            "id": identity.id,
            "name": identity.name,
            "role": identity.role,
            "created_at": identity.created_at
        }
    }

@router.get("/v1/vision/faces/{face_id}")
async def get_face(face_id: str):
    """Get details for a specific enrolled face."""
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    db = get_face_database()
    identity = db.get_identity(face_id)

    if identity is None:
        raise HTTPException(status_code=404, detail=f"Face ID {face_id} not found")

    return {
        "status": "OK",
        "identity": {
            "id": identity.id,
            "name": identity.name,
            "role": identity.role,
            "embedding_count": identity.embedding_count,
            "created_at": identity.created_at,
            "updated_at": identity.updated_at,
            "metadata": identity.metadata
        }
    }

@router.put("/v1/vision/faces/{face_id}")
async def update_face(face_id: str, request: FaceUpdateRequest):
    """Update an enrolled face's metadata."""
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    db = get_face_database()
    success = db.update_identity(
        face_id,
        name=request.name,
        role=request.role,
        metadata=request.metadata
    )

    if not success:
        raise HTTPException(status_code=404, detail=f"Face ID {face_id} not found")

    return {"status": "OK", "message": f"Updated face {face_id}"}

@router.delete("/v1/vision/faces/{face_id}")
async def delete_face(face_id: str):
    """Delete an enrolled face and all its embeddings."""
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    db = get_face_database()
    identity = db.get_identity(face_id)

    if identity is None:
        raise HTTPException(status_code=404, detail=f"Face ID {face_id} not found")

    name = identity.name
    db.delete_identity(face_id)

    log_event("FACE_REC", f"Deleted face: {name} (ID: {face_id})")
    return {"status": "OK", "message": f"Deleted face {name}"}

@router.post("/v1/vision/faces/{face_id}/train")
async def train_face(face_id: str):
    """Add additional training samples to an existing face."""
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    triad = api_state.triad_instance
    if not triad or not triad.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    frames = triad.vision._frames
    cam_id = triad.vision.active_cam_id

    if cam_id not in frames:
        try:
            if int(cam_id) in frames:
                cam_id = int(cam_id)
        except Exception:
            pass
    if cam_id not in frames and str(cam_id) in frames:
        cam_id = str(cam_id)
    if cam_id not in frames:
        raise HTTPException(status_code=404, detail=f"No frame available from camera {cam_id}. Available: {list(frames.keys())}")

    frame = frames[cam_id]
    engine = get_face_engine()
    success = engine.add_training_sample(face_id, frame)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to add training sample. Ensure face is visible.")

    db = get_face_database()
    identity = db.get_identity(face_id)
    return {
        "status": "OK",
        "message": f"Added training sample for {identity.name}",
        "embedding_count": identity.embedding_count
    }

@router.get("/v1/vision/recognize")
async def get_recognition_results():
    """Get current face recognition results (recognized identities, confidence, emotions)."""
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    triad = api_state.triad_instance
    if not triad or not triad.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    frames = triad.vision._frames
    cam_id = triad.vision.active_cam_id

    if cam_id not in frames:
        return {"status": "OK", "faces": [], "message": "No camera frame available"}

    frame = frames[cam_id]
    engine = get_face_engine()
    results = engine.process_frame(frame, scale=0.5)

    emotion_analyzer = get_emotion_analyzer()
    liveness_detector = get_liveness_detector()
    depth_frame = frames.get(105)

    faces_data = []
    for result in results:
        face_data = result.to_dict()

        if emotion_analyzer.is_available():
            emotion_result = emotion_analyzer.analyze_face(
                frame, result.bbox, result.track_id
            )
            if emotion_result:
                face_data["emotion"] = emotion_result.to_dict()

        liveness_result = liveness_detector.check_liveness(
            frame, result.bbox, result.track_id, depth_frame
        )
        face_data["liveness"] = liveness_result.to_dict()
        faces_data.append(face_data)

    return api_state.sanitize_numpy({
        "status": "OK",
        "count": len(faces_data),
        "faces": faces_data,
        "camera_id": cam_id
    })

@router.get("/v1/vision/faces/stats")
async def get_face_stats():
    """Get face recognition system statistics."""
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    db = get_face_database()
    engine = get_face_engine()

    return {
        "status": "OK",
        "database": db.get_stats(),
        "engine": engine.stats,
        "tracks": engine.get_tracks()
    }

@router.post("/v1/vision/active_camera")
async def set_active_camera(request_data: dict):
    triad = api_state.triad_instance
    cam_id = request_data.get("cam_id")
    if triad and triad.vision:
        triad.vision.active_cam_id = int(cam_id)
        return {"status": "OK", "active_cam_id": triad.vision.active_cam_id}
    return {"status": "ERROR", "detail": "Vision layer not ready"}

@router.post("/v1/vision/active_camera2")
async def set_active_camera2(request_data: dict):
    triad = api_state.triad_instance
    cam_id = request_data.get("cam_id")
    if triad and triad.vision:
        triad.vision.active_cam_id2 = int(cam_id) if cam_id is not None else None
        return {"status": "OK", "secondary_cam_id": triad.vision.active_cam_id2}
    return {"status": "ERROR", "detail": "Vision layer not ready"}

@router.get("/v1/vision/telemetry")
async def get_vision_telemetry():
    """Returns real-time facial tracking and depth data (Fused)."""
    triad = api_state.triad_instance
    if triad and hasattr(triad, "get_fused_telemetry"):
        return api_state.sanitize_numpy(triad.get_fused_telemetry())
    return {"status": "OFFLINE", "pos": [0,0,0], "detections": {}}

@router.get("/v1/vision/tracking")
async def get_tracking_status():
    triad = api_state.triad_instance
    if not triad or not triad.vision:
        return {"status": "OFFLINE", "enabled": False}
    return {
        "status": "OK",
        "enabled": triad.vision.tracking_enabled,
        "zoom_enabled": triad.vision.zoom_enabled,
        "last_pos": getattr(triad.vision, 'last_face_pos', [0,0,0])
    }

@router.post("/v1/vision/tracking")
async def set_tracking_status(request_data: dict):
    triad = api_state.triad_instance
    if not triad or not triad.vision:
        return {"status": "ERROR", "detail": "Vision layer not ready"}
        
    enabled = request_data.get("enabled", triad.vision.tracking_enabled)
    zoom = request_data.get("zoom", triad.vision.zoom_enabled)
    triad.vision.tracking_enabled = enabled
    triad.vision.zoom_enabled = zoom
    log_event("API", f"Face Tracking set to: {enabled}, Zoom set to: {zoom}")
    return {"status": "OK", "enabled": enabled, "zoom_enabled": zoom}

@router.post("/v1/vision/camera_mode")
async def cycle_camera_mode(request_data: dict):
    triad = api_state.triad_instance
    cam_id = request_data.get("cam_id")
    if cam_id is None:
        raise HTTPException(status_code=400, detail="cam_id required")

    if triad and triad.vision:
        new_mode = triad.vision.cycle_camera_mode(int(cam_id))
        if new_mode != "INVALID" and new_mode != "UNSUPPORTED":
            return {"status": "OK", "new_mode": new_mode}
        else:
            raise HTTPException(status_code=400, detail=f"Camera {cam_id} does not support mode cycling or is invalid.")
    return {"status": "ERROR", "detail": "Vision layer not ready"}

@router.get("/v1/vision/skeleton")
async def get_skeleton_data():
    """Returns current skeleton tracking data from Kinect."""
    triad = api_state.triad_instance
    if not triad or not triad.vision:
        return {"status": "OFFLINE", "tracked": False, "skeleton": None}

    kinect_cap = triad.vision.caps.get(98)
    if not kinect_cap:
        return {"status": "NO_KINECT", "tracked": False, "skeleton": None}

    skeleton = getattr(triad.vision, 'latest_skeleton', None)
    if skeleton:
        return {
            "status": "OK",
            "tracked": skeleton.get("tracked", False),
            "skeleton": skeleton
        }
    return {"status": "NO_SKELETON", "tracked": False, "skeleton": None}

@router.websocket("/ws/skeleton")
async def websocket_skeleton_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time skeleton data streaming at ~30fps."""
    await websocket.accept()
    _skeleton_ws_clients.append(websocket)
    log_event("API", f"Skeleton WebSocket client connected. Total: {len(_skeleton_ws_clients)}")

    try:
        while True:
            skeleton_data = {"status": "OFFLINE", "tracked": False, "skeleton": None}
            triad = api_state.triad_instance

            if triad and triad.vision:
                skeleton = getattr(triad.vision, 'latest_skeleton', None)
                if skeleton:
                    skeleton_data = {
                        "status": "OK",
                        "tracked": skeleton.get("tracked", False),
                        "skeleton": skeleton
                    }

            try:
                await websocket.send_json(skeleton_data)
            except Exception as e:
                log_event("API", f"Skeleton WS send error: {e}", level="WARNING")
                break

            await asyncio.sleep(0.033)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        log_event("API", f"Skeleton WebSocket error: {e}", level="WARNING")
    finally:
        if websocket in _skeleton_ws_clients:
            _skeleton_ws_clients.remove(websocket)
        log_event("API", f"Skeleton WebSocket client disconnected. Remaining: {len(_skeleton_ws_clients)}")
