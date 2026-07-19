import contextlib
import json
import logging
import os
import struct
import tempfile
import threading
import time
import traceback
from collections import deque
from datetime import datetime
from typing import Any

try:
    import comtypes  # Required for threaded COM access (pygrabber)
    COMTYPES_AVAILABLE = True
except ImportError:
    comtypes = None
    COMTYPES_AVAILABLE = False
import cv2
import numpy as np
import torch
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    wmi = None
    WMI_AVAILABLE = False

from src.orchestrator.system_logger import log_event

from .calibration_manager import calibration_mgr
from .sensory_intelligence import sensory_intel

try:
    import face_recognition
    FACE_REC_AVAILABLE = True
    from .emotion_analyzer import get_emotion_analyzer
    from .face_recognition_engine import get_face_engine
    from .liveness_detector import get_liveness_detector
except ImportError:
    FACE_REC_AVAILABLE = False
    print("DEBUG: face_recognition not available. Falling back to Haar cascades only.", flush=True)

class MockHotswapManager:
    def report_state(self, component, state, metadata=None):
        log_event("HOTSWAP", f"State Report [{component}]: {state} | {metadata}")

hotswap_manager = MockHotswapManager()

try:
    from pseyepy import Camera as PSEyeCamera
    from pseyepy import Stream as PSEyeStream  # noqa: F401
    PSEYE_AVAILABLE = True
except ImportError as e:
    print(f"DEBUG: PSEYE IMPORT FAILED: {e}", flush=True)
    PSEYE_AVAILABLE = False

try:
    from pygrabber.dshow_graph import FilterGraph
    PYGRABBER_AVAILABLE = True
except ImportError:
    PYGRABBER_AVAILABLE = False


logger = logging.getLogger(__name__)

class PSEyeWrapper:
    """Wraps pseyepy Camera to mimic cv2.VideoCapture interface."""
    def __init__(self, eye_cam):
        self.eye = eye_cam

    def read(self):
        try:
            # pseyepy read() returns (frame, timestamp) tuple
            result = self.eye.read()
            if result is None:
                return False, None
            # Handle both single camera (direct values) and multi-camera (lists)
            if isinstance(result, tuple) and len(result) == 2:
                frame, timestamp = result
            else:
                frame = result
            # Verify frame is valid numpy array with content
            if isinstance(frame, np.ndarray) and frame.size > 0:
                # Convert from RGB to BGR for OpenCV compatibility
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return True, frame
            return False, None
        except Exception as e:
            print(f"DEBUG: PSEyeWrapper.read() exception: {e}", flush=True)
            return False, None

    def release(self):
        with contextlib.suppress(Exception):
            self.eye.close()

    def isOpened(self):  # noqa: N802
        return True

    def get(self, prop):
        # Map properties to PS Eye specific attributes
        if prop == cv2.CAP_PROP_FRAME_WIDTH:
            return 640
        if prop == cv2.CAP_PROP_FRAME_HEIGHT:
            return 480
        if prop == cv2.CAP_PROP_FPS:
            return 60

        # Read back current values (normalized)
        try:
            if prop == cv2.CAP_PROP_GAIN:
                 return self.eye.gain / 63.0
            if prop == cv2.CAP_PROP_EXPOSURE:
                 return self.eye.exposure / 255.0
        except Exception:
            pass
        return 0

    def set(self, prop, val):
        """Sets camera properties mapping standard CV2 props to PS Eye driver."""
        try:
            # PS Eye Ranges: Gain [0-63], Exposure [0-255]
            # Val is typically normalized 0.0-1.0 from the Logic Layer

            if prop == cv2.CAP_PROP_GAIN:
                with contextlib.suppress(Exception):
                    self.eye.auto_gain = False

                target = int(val * 63)
                self.eye.gain = max(0, min(63, target))
                return True

            if prop == cv2.CAP_PROP_EXPOSURE or prop == cv2.CAP_PROP_BRIGHTNESS:
                with contextlib.suppress(Exception):
                    self.eye.auto_exposure = False

                # Map brightness to exposure as PS Eye doesn't have brightness
                target = int(val * 255)
                self.eye.exposure = max(0, min(255, target))
                return True

            if prop == cv2.CAP_PROP_TEMPERATURE:
                with contextlib.suppress(Exception):
                    self.eye.auto_whitebalance = False

                # Map temperature (0.0-1.0) to White Balance (Blue -> Red)
                # Cool (0.0) = High Blue, Warm (1.0) = High Red
                r = int(val * 255)
                b = int((1.0 - val) * 255)
                g = 128 # Neutral Green
                # pseyepy expects [r, g, b] list or tuple
                self.eye.whitebalance = [r, g, b]
                return True

            # Contrast/Saturation not natively supported by standard pseyepy
            return False

        except Exception as e:
            print(f"DEBUG: PSEye set({prop}, {val}) failed: {e}", flush=True)
            return False

class OrbCloudVision:
    """
    Universal Vision Interface (OrbCloud).
    Supports multiple UVC webcams for 3D triangulation and hardware-aware tracking.
    """

    def __init__(self, device_indices: list[int] | None = None, simulated: bool = False):
        if device_indices is None:
            device_indices = [0, 1]
        self.device_indices = device_indices
        self.simulated = simulated
        self.caps = {}
        self.hardware_metadata = {}
        self._lock = threading.Lock()
        self._frames = {}
        self.active_cam_id: str = "98"  # Default to Kinect
        self.latest_skeleton = None

        # Landmark Throttling State
        self.landmark_throttle_counter = 0
        self.landmark_throttle_limit = 5 # Run landmarks every 5th frame per face (~6 FPS)

        # Temporal Visual Buffer (Long-term visual context)
        self.visual_buffer = deque(maxlen=30)
        self._buffer_thread = None
        self._stop_buffer = threading.Event()

        # Detection logic (Refined Haar with Temporal Confirmation)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.detection_history = {i: deque(maxlen=5) for i in range(10)} # Track last 5 frames for stability
        self.confirmed_faces = {} # Persistent confirmed detections

        # Hardware Intelligence State
        self.hw_intel_file = "logs/hardware_intelligence.json"
        os.makedirs("logs", exist_ok=True)
        self.wmi = wmi.WMI() if WMI_AVAILABLE and wmi is not None else None

        # Tracking & Smoothing State
        self.tracking_enabled = True # Always-on background tracking
        self.zoom_enabled = True     # Digital zoom (scale) toggle
        self.active_cam_id2 = None   # Secondary camera for dual-monitoring
        self.last_face_pos = [0.0, 0.0, 1.0] # X, Y, Z
        self.pan_tilt_buffer = deque(maxlen=5) # Smoothing for motors
        self.digital_crop = {idx: {"cx": 0.5, "cy": 0.5, "scale": 1.0} for idx in range(11)}
        self.digital_crop[99] = {"cx": 0.5, "cy": 0.5, "scale": 1.0} # PS Eye index
        self.pnp_inventory = []
        self.last_known_detections = {} # Cache for overlays

        # HCEP Oculomotor State (Human Conversation Eye Points)
        self.hcep_state = {
            "gaze_target_type": "FACE_CENTER", # FACE_CENTER, LEFT_EYE, RIGHT_EYE, MOUTH, AMBIENT
            "target_pos": [0.5, 0.5, 1.0],     # Target in viewport space
            "last_saccade": time.time(),
            "saccade_interval": 3.0,           # Dynamic interval
            "micro_jitter": [0.0, 0.0],        # Bio-tremor
            "interest_score": 0.0,             # 0.0 to 1.0
            "lock_stability": 0.0,             # How steady the gaze is on current target
            "user_gaze": "UNKNOWN",            # SCREEN, CHAT_UI, AMBIENT
            "user_attention": 0.0              # Derived Focus (0.0 - 1.0)
        }

        self.spatial_fusion = {
            "audio_beam": 0.0,
            "audio_source": 0.0,
            "audio_confidence": 0.0,
            "fused_node_pos": [0, 0, 1.0],
            "fusion_confidence": 0.0
        }



        # Telemetry State
        self.latest_telemetry = {
            "status": "INITIALIZING",
            "pos": [0, 0, 0],
            "detections": {},
            "active_voices": 0
        }

        # Performance Metrics
        self.performance_stats = {
            "fps": {},
            "latency_ms": 0,
            "global_fps": 0
        }
        self._fps_counters = {}
        self._last_perf_check = time.time()
        self._frame_count_total = 0
        self._frame_count_global = 0

        # Neural Throttling (Inference FPS Cap)
        self.last_inference_time = {} # cam_id -> float
        self.inference_fps_limit = 10.0  # [PERF] Increased from 5.0 for smoother detection

        # Pineal Memory (Persistence)
        self.memory_file = "logs/pineal_memory.json"
        self._load_memory()



    def _load_memory(self):
        """Loads persistent state (Pineal Memory)."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file) as f:
                    data = json.load(f)
                    self.active_cam_id = data.get('active_cam_id', 98)
                    log_event("VISION", f"Pineal Memory Restored: Active Camera = {self.active_cam_id}")
            except Exception as e:
                logger.error(f"Failed to load Pineal Memory: {e}")

    def _save_memory(self):
        """Saves persistent state."""
        try:
            data = {'active_cam_id': self.active_cam_id}
            with open(self.memory_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to save Pineal Memory: {e}")

    def refresh_hardware(self, audio_engine=None):
        """Forces a hardware re-scan and updates metadata/caps."""
        log_event("VISION", f"Refreshing hardware sync (AudioProbe={'Yes' if audio_engine else 'No'})...")
        sensory_intel.log_trace("Triggered OrbCloudVision hardware refresh.")

        # Release existing caps to ensure they can be re-acquired if they moved
        # However, to be "hot-swap" friendly, we only release if we need to.
        # For now, let's keep it simple: Release all, Re-scan.
        with self._lock:
            for idx, cap in self.caps.items():
                try:
                    cap.release()
                    sensory_intel.log_trace(f"Released Camera Index {idx} for re-probing.")
                except Exception:
                    pass
            self.caps = {}
            self.hardware_metadata = {}
            self._frames = {} # Clear stale frames

        # Re-run full discovery with force=True
        self.open(audio_engine=audio_engine)
        sensory_intel.log_trace("Hardware refresh cycle complete.")
        return True

    def open(self, audio_engine=None):
        """Initializes all detected cameras using Sensory Intelligence Discovery."""
        # Fix for "CoInitialize has not been called" in threaded context
        if COMTYPES_AVAILABLE and comtypes is not None:
            try:
                comtypes.CoInitialize()
            except Exception as e:
                sensory_intel.log_trace(f"CoInitialize warning: {e}", level="WARNING")

        sensory_intel.log_trace("Opening vision layer (Sensory Discovery Mode)...")

        # Run centralized hierarchical scan (Forced if refresh)
        self.device_tree = sensory_intel.run_discovery(force=True, audio_engine=audio_engine)
        self.pnp_inventory = sensory_intel.inventory

        # Check for conflicts
        diag = sensory_intel.get_diagnostics()
        if diag["status"] != "HEALTHY":
            for conflict in diag["conflicts"]:
                msg = f"Hardware Advisory: {conflict['device']} - {conflict['reason']}"
                log_event("VISION", msg, level="WARNING")
                sensory_intel.log_trace(msg, level="WARNING")

        if self.simulated:
            log_event("VISION", "Hardware sidelined. Initialization in SIMULATION mode.")
            self._is_running = True
            return True

        # 1. Kinect v1 Discovery (FIRST - uses index 98)
        self._scan_kinect()

        # 2. Specialized High-Speed Scan (PS Eye via LibUSB) - uses index 99+
        # Both can coexist since they use different indices
        if PSEYE_AVAILABLE:
            if "98" in self.caps:
                log_event("VISION", "Kinect detected at index 98, PS Eye scan will use index 99+")
            self._scan_pseyepy()

        # Backends to try in order of preference for Windows
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

        # Exhaustive probe (Indices 0-10)
        # [OPTIMIZATION] If specialized hardware is found, treat as 'found_any' to avoid long probe if not needed
        has_kinect = "98" in self.caps
        has_specialized = has_kinect or any((str(idx).isdigit() and int(idx) >= 99) for idx in self.caps)
        found_any = has_specialized

        pnp_count = len(self.pnp_inventory)
        sensory_intel.log_trace(f"Starting optimized camera probe (Indices 0-10) | PnP Inventory: {pnp_count} devices.")

        # Get friendly names from pygrabber if available
        friendly_names = []
        if PYGRABBER_AVAILABLE:
            try:
                friendly_names = FilterGraph().get_input_devices()
                sensory_intel.log_trace(f"PyGrabber discovered {len(friendly_names)} friendly names: {friendly_names}")
            except Exception as e:
                sensory_intel.log_trace(f"PyGrabber error: {e}", level="WARNING")

        for idx in range(32):
            # Only stop if we have found a large number of cameras (12+) or probed well beyond common indices
            if len(self.caps) >= 12 and idx > 16:
                 sensory_intel.log_trace(f"Found {len(self.caps)} cameras, stopping exhaustive probe at index {idx}.")
                 break

            # [PERF OPT] If we've had 10 consecutive failed probes and found specialized hardware, skip remaining
            if not hasattr(self, '_probe_failures'):
                self._probe_failures = 0
            if self._probe_failures >= 10 and has_specialized:
                sensory_intel.log_trace("Stopping probe: 10 consecutive failures + specialized hardware detected")
                break

            # ... (rest of the loop is unchanged, proceeding with probing) ...
            sensory_intel.log_trace(f"Probing Index {idx}...")
            for backend in backends:
                backend_name = "DSHOW" if backend == cv2.CAP_DSHOW else "MSMF" if backend == cv2.CAP_MSMF else "ANY"

                try:
                    cap = cv2.VideoCapture(idx, backend)
                    if cap.isOpened():
                        # Double check if we can actually grab a frame
                        ret, _ = cap.read()
                        if ret:
                            # Resolve Label from PyGrabber friendly name (authoritative)
                            label = "GENERIC Camera"
                            friendly_name = ""
                            if idx < len(friendly_names):
                                friendly_name = friendly_names[idx]
                                label = friendly_name

                            sensory_intel.log_trace(f"[SUCCESS] Index {idx} ({label}) opened with {backend_name}")
                            ptz = self._probe_ptz(cap)

                            # Enhance label with Neural prefix based on friendly name matching
                            # Only use PTZ model name if the friendly name suggests it's that device
                            friendly_lower = friendly_name.lower()

                            # QuickCam Orbit/Sphere detection patterns
                            is_quickcam = (
                                "orbit" in friendly_lower or
                                "sphere" in friendly_lower or
                                "quickcam" in friendly_lower or
                                "logitech usb camera" in friendly_lower or
                                "usb camera-b4" in friendly_lower  # QuickCam firmware identifier
                            )

                            if is_quickcam:
                                log_event("VISION", f"QuickCam Orbit/Sphere Detected at Index {idx} ({friendly_name})")
                                label = f"[Neural] QuickCam Orbit/Sphere MP [{backend_name}]"
                                ptz["hardware"] = "ORBIT"
                                ptz["pan"] = True
                                ptz["tilt"] = True
                                ptz["motor_control"] = True
                            elif "playstation" in friendly_lower or "ps3 eye" in friendly_lower or "ps eye" in friendly_lower or "usb camera-b4" in friendly_lower:
                                label = f"[Neural] PlayStation Eye [{backend_name}]"
                                ptz["hardware"] = "PSEYE"
                            elif "kinect" in friendly_lower:
                                label = f"[Neural] Kinect [{backend_name}]"
                                ptz["hardware"] = "KINECT"
                            elif "video camera" in friendly_lower:
                                # Safe lookup in inventory for Microsoft VID 045E (Xbox Vision)
                                is_xbox = False
                                for d in self.pnp_inventory:
                                    # Use case-insensitive stripped comparison to handle trailing spaces from pygrabber
                                    if d.get("name", "").strip().lower() == friendly_name.strip().lower():
                                        hw_id = str(d.get("hw_id", "")).lower()
                                        if "vid_045e" in hw_id and "pid_0294" in hw_id:
                                            is_xbox = True
                                            break
                                if is_xbox:
                                    label = f"[Neural] Xbox Live Vision [{backend_name}]"
                                    ptz["hardware"] = "XBOX_VISION"
                                else:
                                    label = f"[Neural] {friendly_name} [{backend_name}]"
                            elif "camera" in friendly_lower or friendly_name != "":
                                # Fallback for other generic or named cameras
                                label = f"[Neural] {friendly_name} [{backend_name}]"
                            elif friendly_name == "" or "GENERIC" in label:
                                # Fallback to PTZ probe model if no friendly name
                                if ptz.get("model"):
                                    label = ptz["model"]

                            self.caps[idx] = cap
                            self.hardware_metadata[idx] = {
                                "width": cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                                "height": cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
                                "fps": cap.get(cv2.CAP_PROP_FPS),
                                "ptz_capabilities": ptz,
                                "backend": backend_name,
                                "status": "ACTIVE",
                                "model": label,
                                "friendly_name": friendly_name
                            }
                            found_any = True
                            self._probe_failures = 0  # Reset failure counter on success
                            break # Move to next index if one backend works
                        else:
                            sensory_intel.log_trace(f"[BLOCK] Index {idx} with {backend_name} busy or no signal.", level="WARNING")
                            cap.release()
                    else:
                        cap.release()
                except Exception as e:
                    sensory_intel.log_trace(f"[ERROR] Index {idx} with {backend_name} crashed: {e}", level="ERROR")
                    if 'cap' in locals() and cap is not None:
                        cap.release()
            else:
                # No backends succeeded for this index
                self._probe_failures += 1

        if not self.caps:
            # Check if we have specialized hardware instead (Kinect or PS Eye)
            if 98 in self.caps or any(idx >= 99 for idx in self.caps):
                sensory_intel.log_trace("Standard probe failed, but specialized hardware (Kinect/PSEye) is active.")
            else:
                msg = "Exhaustive probe failed: No live cameras detected."
                log_event("VISION", msg, level="WARNING")
                sensory_intel.log_trace(msg, level="WARNING")
                self.hardware_metadata = {
                    -1: {
                        "status": "OFFLINE",
                        "ptz_capabilities": {"pan": False, "tilt": False, "zoom": False, "digital": False}
                    }
                }
                self._is_running = False
                self.status = "OFFLINE"
                hotswap_manager.report_state("vision", "OFFLINE", {"reason": "No cameras found"})
                return True # Allow system to proceed in text-only mode

        self._is_running = True

        # [AUTOCONFIG] Ensure active camera is valid
        if self.active_cam_id not in self.caps:
             if 98 in self.caps:
                 log_event("VISION", f"Stored Active Camera {self.active_cam_id} missing. Failing over to Kinect (98).")
                 self.active_cam_id = 98
             elif len(self.caps) > 0:
                 new_id = sorted(list(self.caps.keys()))[0]
                 log_event("VISION", f"Stored Active Camera {self.active_cam_id} missing. Failing over to Index {new_id}.")
                 self.active_cam_id = new_id

        log_event("VISION", f"Vision layer active with {len(self.caps)} camera(s).")
        hotswap_manager.report_state("vision", "ACTIVE", {"camera_count": len(self.caps)})

        # 5. Final Hardware Intelligence Record
        self._repair_hw_intel_file()
        self._record_hardware_intel()

        # 6. Run Hardware Startup Checklist (Calibration & Health Audit)
        self.startup_report = calibration_mgr.run_startup_checklist(self)

        # Start background buffer loop
        self.start_buffer_loop()

        return True
    def start_buffer_loop(self, interval: float = 0.033):
        """Starts the background temporal capture thread. Default 30FPS (0.033s) for legacy stability."""
        if self._buffer_thread and self._buffer_thread.is_alive():
            return
        self._stop_buffer.clear()
        self._buffer_thread = threading.Thread(target=self._buffer_loop, args=(interval,), daemon=True)
        self._buffer_thread.start()
        log_event("VISION", f"Temporal Visual Buffer thread started (Interval: {interval}s)")

    def _buffer_loop(self, interval: float):
        """Background thread filling the visual buffer and fresh frame state."""
        # COM Initialization for this thread
        try:
            import pythoncom
            pythoncom.CoInitialize()
            log_event("VISION", "COM Initialized for Capture Thread.")
        except Exception as e:
            log_event("VISION", f"COM Initialization failed in Capture Thread: {e}", level="WARNING")

        last_buffer_time = 0
        last_track_time = 0
        while not self._stop_buffer.is_set():
            loop_start = time.time()
            if self._is_running and self.caps:
                try:
                    fresh_frames = {}
                    # Standardize to STRING keys for consistency with API
                    # 1. Start with a copy of CURRENT frames to ensure persistence of virtual streams (105, 106)
                    # during round-robin skips.
                    with self._lock:
                        fresh_frames = {str(k): v for k, v in self._frames.items()}

                    # Also copy detections
                    fresh_detections = {str(k): v for k, v in self.last_known_detections.items()} if self.last_known_detections else {}

                    # [OPTIMIZATION] Global Frame Counter for Round-Robin Polling
                    self._frame_count_global = getattr(self, "_frame_count_global", 0) + 1

                    for idx in list(self.caps.keys()):
                        cap = self.caps[idx]
                        # [OPTIMIZATION] Dynamic Polling Rate
                        # Always poll Active Camera & Kinect (98). Poll others every 10th frame (was 5th).
                        # This significantly reduces USB bus contention.
                        is_priority = (idx == self.active_cam_id or idx == 98)
                        if not is_priority and (self._frame_count_global % 10 != 0):
                            # Keep old frame if available
                            if idx in self._frames:
                                fresh_frames[idx] = self._frames[idx]
                            continue

                        time.time()
                        ret, raw_frame = cap.read()
                        if ret:
                            # Performance Tracking
                            self._fps_counters[idx] = self._fps_counters.get(idx, 0) + 1
                            self._frame_count_total += 1

                            # 1. Kinect Multi-Stream Handling
                            if str(idx) == "98" and isinstance(raw_frame, dict):
                                k_frame = raw_frame.get("color")
                                if k_frame is None and "ir" in raw_frame:
                                    k_frame = raw_frame["ir"]

                                if k_frame is not None:
                                    s_idx = "98"
                                    # Throttling: Check if we should run inference
                                    now = time.time()
                                    last_inf = self.last_inference_time.get(s_idx, 0)
                                    should_infer = self.tracking_enabled and (now - last_inf >= 1.0/self.inference_fps_limit)

                                    if should_infer:
                                        self.last_inference_time[s_idx] = now
                                        try:
                                            depth_frame = raw_frame.get("sub")
                                            det_list = []
                                            face_tracked = False

                                            # 1. Try Native Kinect SDK Face Tracking (K2VR-style) - HIGHEST PRIORITY
                                            if hasattr(cap, 'face_tracking_enabled') and cap.face_tracking_enabled:
                                                face_result = cap.process_face(k_frame, depth_frame)
                                                if face_result.get('success'):
                                                    # Calculate approximate bbox from head position
                                                    h, w = k_frame.shape[:2]
                                                    cx = int((face_result['tx'] / face_result['tz'] * 320) + w/2) if face_result['tz'] != 0 else w//2
                                                    cy = int((face_result['ty'] / face_result['tz'] * 240) + h/2) if face_result['tz'] != 0 else h//2
                                                    face_size = int(face_result['scale'] * 150)  # Approximate face size from scale
                                                    x = max(0, cx - face_size//2)
                                                    y = max(0, cy - face_size//2)

                                                    mesh_points = []
                                                    if hasattr(cap, 'get_face_mesh'):
                                                        mesh_points = cap.get_face_mesh()
                                                        # Normalize points to 0..1 based on 640x480 (standard Kinect color Res)
                                                        # Kinect SDK returns points in meters. We need to project them.
                                                        # For now, we pass them as-is or use a simple projection if tx/ty/tz available.
                                                        # Actually, let's keep them as 3D if frontend can handle, but NeuralFaceMesh wants 0..1.
                                                        # We'll project to 2D for NeuralFaceMesh.
                                                        projected_points = []
                                                        for p in mesh_points:
                                                            # Simple pinhole projection
                                                            # x_img = (x / z) * f + cx
                                                            # y_img = (y / z) * f + cy
                                                            # F is approx 531 for 640x480
                                                            pz = p[2] if p[2] != 0 else 1.0
                                                            px = (p[0] / pz * 531.0 + 320.0) / 640.0
                                                            py = (p[1] / pz * 531.0 + 240.0) / 480.0
                                                            projected_points.append([px, py])
                                                        mesh_points = projected_points

                                                    det_list.append({
                                                        "bbox": (x, y, face_size, face_size),
                                                        "score": 0.99,
                                                        "pose": {
                                                            "pitch": face_result['pitch'],
                                                            "yaw": face_result['yaw'],
                                                            "roll": face_result['roll']
                                                        },
                                                        "landmarks": mesh_points,
                                                        "native_kinect": True
                                                    })

                                                    # [ENHANCEMENT] Perform Recognition & Analysis on Native Tracking Result
                                                    if FACE_REC_AVAILABLE and k_frame is not None:
                                                        try:
                                                            engine = get_face_engine()
                                                            rec_results = engine.process_frame(k_frame, scale=0.5)

                                                            emotion_analyzer = get_emotion_analyzer()
                                                            liveness_detector = get_liveness_detector()

                                                            if rec_results:
                                                                res = rec_results[0]
                                                                identity = res.identity
                                                                if identity:
                                                                    det_list[0]["identity_name"] = identity.name
                                                                    det_list[0]["identity_id"] = identity.id

                                                                    # Preserve Neural Landmarks if native failed or empty
                                                                    if not det_list[0].get("landmarks") and hasattr(res, 'landmarks'):
                                                                        # Normalize landmarks (res.landmarks is usually in pixels)
                                                                        raw_landmarks = res.landmarks
                                                                        norm_landmarks = {}
                                                                        h_img, w_img = k_frame.shape[:2]
                                                                        for feature, pts in raw_landmarks.items():
                                                                            norm_landmarks[feature] = [[p[0]/w_img, p[1]/h_img] for p in pts]
                                                                        det_list[0]["landmarks"] = norm_landmarks
                                                                    det_list[0]["confidence"] = res.confidence
                                                                    # [FIX] Frontend expects 'label' for the overlay name
                                                                    det_list[0]["label"] = f"{identity.name} ({int(res.confidence * 100)}%)"

                                                                # Emotion & Liveness
                                                                if emotion_analyzer.is_available():
                                                                    emo_res = emotion_analyzer.analyze_face(k_frame, det_list[0]["bbox"], res.track_id)
                                                                    if emo_res:
                                                                        det_list[0]["emotion"] = emo_res.to_dict()

                                                                live_res = liveness_detector.check_liveness(k_frame, det_list[0]["bbox"], res.track_id, depth_frame)
                                                                det_list[0]["liveness"] = live_res.to_dict()

                                                                if identity:
                                                                    log_event("VISION", f"Recognized User: {identity.name} [Native Pose + Neural Analysis]")
                                                        except Exception as rec_err:
                                                            logger.debug(f"Recognition analysis failed: {rec_err}")

                                                    face_tracked = True

                                            # 4. SpatialSense Fusion (Audio + Visual)
                                            if hasattr(cap, 'get_audio_spatial_data'):
                                                audio_data = cap.get_audio_spatial_data()
                                                if audio_data:
                                                    self.spatial_fusion.update(audio_data)

                                            # Cross-reference audio source with detected faces
                                            if face_tracked and self.spatial_fusion['audio_confidence'] > 0.4:
                                                h, w = k_frame.shape[:2]
                                                # Map Source Angle (radians -0.5..0.5) to viewport 0..1
                                                audio_cx = 0.5 + (self.spatial_fusion['audio_source'] / 0.8) # Heuristic FOV map

                                                for d in det_list:
                                                    bbox = d['bbox']
                                                    face_cx = (bbox[0] + bbox[2]/2) / w
                                                    if abs(face_cx - audio_cx) < 0.2:
                                                        d['fused'] = True
                                                        self.spatial_fusion['fusion_confidence'] = min(1.0, self.spatial_fusion['fusion_confidence'] + 0.2)
                                                        self.spatial_fusion['fused_node_pos'] = [face_cx, (bbox[1] + bbox[3]/2) / h, 1.0]

                                            # Store results
                                            self.last_known_detections[s_idx] = det_list
                                            if face_tracked:
                                                # Update HCEP
                                                d = det_list[0]
                                                bbox = d['bbox']
                                                h, w = k_frame.shape[:2]
                                                # Use Z from native pose if available, else 1.0
                                                fz = d.get("pose", {}).get("tz", 1.0) if "pose" in d else 1.0
                                                self._update_hcep([(bbox[0]+bbox[2]/2)/w, (bbox[1]+bbox[3]/2)/h, fz], {int(s_idx): det_list})

                                        except Exception as e:
                                            logger.error(f"Kinect Inference Fail: {e}")
                                            traceback.print_exc()
                                            # 2. Fallback: Python face_recognition (if native failed and available)
                                            if not face_tracked and FACE_REC_AVAILABLE:
                                                try:
                                                    # Convert to RGB for face_recognition
                                                    # [ROBUSTNESS] Check if frame is valid and has correct dimensions
                                                    if k_frame is not None and len(k_frame.shape) == 3 and k_frame.shape[2] == 3:
                                                        if k_frame.dtype != np.uint8:
                                                            k_frame = k_frame.astype(np.uint8)
                                                        rgb_frame = cv2.cvtColor(k_frame, cv2.COLOR_BGR2RGB)
                                                    else:
                                                        log_event("VISION", f"Invalid k_frame for face_recognition: {k_frame.shape if k_frame is not None else 'None'}", level="WARNING")
                                                        continue
                                                    engine = get_face_engine()
                                                    recognition_results = engine.process_frame(rgb_frame, scale=0.25)

                                                    emotion_analyzer = get_emotion_analyzer()
                                                    liveness_detector = get_liveness_detector()

                                                    for res in recognition_results:
                                                        face_data = res.to_dict()
                                                        if emotion_analyzer.is_available():
                                                            emo_res = emotion_analyzer.analyze_face(k_frame, res.bbox, res.track_id)
                                                            if emo_res:
                                                                face_data["emotion"] = emo_res.to_dict()

                                                        live_res = liveness_detector.check_liveness(k_frame, res.bbox, res.track_id, depth_frame)
                                                        face_data["liveness"] = live_res.to_dict()

                                                        # Normalize landmarks
                                                        if face_data.get("landmarks"):
                                                            raw_landmarks = face_data["landmarks"]
                                                            norm_landmarks = {}
                                                            h_img, w_img = k_frame.shape[:2]
                                                            if isinstance(raw_landmarks, dict):
                                                                for feature, pts in raw_landmarks.items():
                                                                    norm_landmarks[feature] = [[p[0]/w_img, p[1]/h_img] for p in pts]
                                                            elif isinstance(raw_landmarks, list):
                                                                norm_landmarks = [[p[0]/w_img, p[1]/h_img] for p in raw_landmarks]
                                                            face_data["landmarks"] = norm_landmarks

                                                        det_list.append(face_data)

                                                    if det_list:
                                                        face_tracked = True
                                                except Exception as face_rec_err:
                                                    log_event("VISION", f"[KINECT] face_recognition fallback error: {face_rec_err}", level="DEBUG")

                                            # 3. Final fallback: Haar cascades (basic detection)
                                            if not face_tracked:
                                                gray = cv2.cvtColor(k_frame, cv2.COLOR_BGR2GRAY)
                                                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                                                det_list = [{"bbox": (x, y, w_box, h_box), "score": 0.80} for (x, y, w_box, h_box) in faces]

                                            fresh_detections["98"] = det_list
                                        except Exception as e:  # noqa: B025
                                            log_event("VISION", f"[KINECT] Face detection error: {e}", level="DEBUG")

                                        # Update Tracking Markers (Overlay)
                                        if self.active_cam_id == 98:
                                            tx = int(self.last_face_pos[0] * k_frame.shape[1])
                                            ty = int(self.last_face_pos[1] * k_frame.shape[0])
                                            cv2.drawMarker(k_frame, (tx, ty), (255, 0, 0), cv2.MARKER_CROSS, 30, 2)

                                    fresh_frames["98"] = k_frame

                                # Preserve virtual streams (105, 106)
                                if "sub" in raw_frame:
                                    fresh_frames["105"] = raw_frame["sub"]
                                    self.depth_active = True
                                if "ir" in raw_frame:
                                    fresh_frames["106"] = raw_frame["ir"]
                                    self.ir_active = True

                                # Process Skeleton
                                if "skeleton" in raw_frame:
                                    skel_raw = raw_frame["skeleton"]
                                    try:
                                        if hasattr(cap, 'serialize_skeleton'):
                                            skel_json = cap.serialize_skeleton(skel_raw)
                                            if skel_json:
                                                self.latest_skeleton = skel_json
                                    except Exception as e:
                                        logger.error(f"Skeleton serialization error: {e}")
                                continue

                            # 2. Digital PTZ (Crop) for Standard Frames
                            if idx in self.digital_crop:
                                crop = self.digital_crop[idx]
                                if hasattr(raw_frame, "shape"):
                                    h, w = raw_frame.shape[:2]
                                    cw, ch = int(w / crop["scale"]), int(h / crop["scale"])
                                    x1 = max(0, int(w * crop["cx"] - cw / 2))
                                    y1 = max(0, int(h * crop["cy"] - ch / 2))
                                    x2 = min(w, x1 + cw)
                                    y2 = min(h, y1 + ch)
                                    frame = raw_frame[y1:y2, x1:x2]
                                    frame = cv2.resize(frame, (w, h))
                                else:
                                    frame = raw_frame
                            else:
                                frame = raw_frame

                            s_idx = str(idx)
                            if s_idx in self.caps: # Standard Cams
                                frame = self._apply_software_controls(frame, s_idx)

                            # 2b. Standard Face Detection (Throttled)
                            now = time.time()
                            last_inf = self.last_inference_time.get(s_idx, 0)
                            should_infer = self.tracking_enabled and idx == self.active_cam_id and (now - last_inf >= 1.0/self.inference_fps_limit)

                            if should_infer:
                                self.last_inference_time[s_idx] = now
                                try:
                                    det_list = []
                                    if FACE_REC_AVAILABLE:
                                        # Use the new Face Engine
                                        engine = get_face_engine()
                                        recognition_results = engine.process_frame(frame, scale=0.5)

                                        emotion_analyzer = get_emotion_analyzer()
                                        liveness_detector = get_liveness_detector()

                                        for res in recognition_results:
                                            face_data = res.to_dict()

                                            # Analytics
                                            if emotion_analyzer.is_available():
                                                emo_res = emotion_analyzer.analyze_face(frame, res.bbox, res.track_id)
                                                if emo_res:
                                                    face_data["emotion"] = emo_res.to_dict()

                                            # Standard cams don't have depth, but we can do texture/blink checks
                                            live_res = liveness_detector.check_liveness(frame, res.bbox, res.track_id, None)
                                            face_data["liveness"] = live_res.to_dict()

                                            # Normalize landmarks if present
                                            if face_data.get("landmarks"):
                                                raw_landmarks = face_data["landmarks"]
                                                norm_landmarks = {}
                                                h_img, w_img = frame.shape[:2]
                                                if isinstance(raw_landmarks, dict):
                                                    for feature, pts in raw_landmarks.items():
                                                        norm_landmarks[feature] = [[p[0]/w_img, p[1]/h_img] for p in pts]
                                                elif isinstance(raw_landmarks, list):
                                                    norm_landmarks = [[p[0]/w_img, p[1]/h_img] for p in raw_landmarks]
                                                face_data["landmarks"] = norm_landmarks

                                            det_list.append(face_data)
                                    else:
                                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                                        for (x, y, w, h) in faces:
                                            det_list.append({"bbox": (x, y, w, h)})

                                    fresh_detections[idx] = det_list

                                    # Update Global Tracking Target if Primary
                                    if idx == self.active_cam_id and len(det_list) > 0:
                                        # Use center of first detection for tracking markers
                                        x, y, w, h = det_list[0]["bbox"]
                                        cx = (x + w/2) / frame.shape[1]
                                        cy = (y + h/2) / frame.shape[0]
                                        self.last_face_pos = (cx, cy)
                                except Exception as e:
                                    logger.debug(f"Face detection error on cam {idx}: {e}")

                            # 3. Dynamic Tracking Overlays
                            # REMOVED: Frontend (App.jsx) now handles all bounding boxes and landmarks.
                            # cv2.rectangle / cv2.drawMarker calls deleted to prevent "ghost" boxes.

                            fresh_frames[s_idx] = frame

                    if fresh_frames:
                        with self._lock:
                            self._frames = fresh_frames

                        now = time.time()

                        # 2. Background Face Triangulation (Higher Frequency)
                        if self.tracking_enabled and (now - last_track_time >= 0.1):
                            # Use high-quality detections for triangulation if available
                            tracking_pos = self.triangulate_position(provided_detections=fresh_detections)
                            if tracking_pos["status"] != "NO_FRAMES":
                                self.last_face_pos = tracking_pos["pos"]
                                # [FIX] Ensure the high-quality detections are persisted even if Haar finds nothing
                                if "detections" in tracking_pos:
                                    self.last_known_detections = tracking_pos["detections"]
                            last_track_time = now

                        # 3. Temporal Buffer (Slower Frequency)
                        if now - last_buffer_time >= 2.0:
                            self.visual_buffer.append({"timestamp": now, "frames": fresh_frames})
                            last_buffer_time = now

                            # Periodic Integrity Check
                            self.frame_counter = getattr(self, 'frame_counter', 0) + 1
                            if self.frame_counter % 15 == 0:
                                for idx, f in fresh_frames.items():
                                    avg_brightness = np.mean(f)
                                    log_event("VISION", f"Camera {idx} Signal Integrity: Brightness={avg_brightness:.1f}")

                        # --- Telemetry Update & Labeling ---
                        labeled_detections = {}
                        final_pos = self.last_face_pos

                        # [FIX] Use ALL available detections from the persistent store for telemetry
                        # This ensures the frontend doesn't lose faces between frames.
                        source_detections = fresh_detections if fresh_detections else self.last_known_detections

                        for cam_id_raw, det_list in source_detections.items():
                            cam_id = str(cam_id_raw)
                            labeled_list = []
                            for i, det in enumerate(det_list):
                                # Assign Label
                                label = det.get("identity_name", f"Face {i+1}")
                                if label == "Unknown" or not label:
                                    label = f"Face {i+1}"

                                if cam_id == str(self.active_cam_id) and i == 0:
                                    label = f"Primary: {label}"

                                # Augment detection dict
                                det_aug = det.copy()
                                if "label" not in det_aug:
                                    det_aug["label"] = label
                                det_aug["id"] = f"{cam_id}-{i}"
                                det_aug["score"] = det.get("score", 0.95)
                                labeled_list.append(det_aug)

                            if labeled_list:
                                labeled_detections[cam_id] = labeled_list

                        # Update Thread-Safe Telemetry State
                        with self._lock:
                            self.latest_telemetry = {
                                "status": "TRACKING" if labeled_detections else "SEARCHING",
                                "pos": [final_pos[0], final_pos[1], 1.0], # Z-depth stub
                                "detections": labeled_detections,
                                "active_voices": 0, # Placeholder for audio fusion
                                "hcep": self.hcep_state.copy(), # Inject Oculomotor state directly from Vision layer
                                "ir_active": getattr(self, "ir_active", False),
                                "depth_active": getattr(self, "depth_active", False),
                                "timestamp": now,
                                "performance": self.performance_stats.copy(), # Include FPS stats
                                "confidence": 100 if labeled_detections else 0
                            }

                except Exception as e:
                    logger.error(f"Visual buffer loop error: {e}")
                    log_event("VISION", f"Visual Bug Trace: {traceback.format_exc()}", level="DEBUG")

            # [PERFORMANCE] Periodic Metrics Calculation
            now_perf = time.time()
            if now_perf - self._last_perf_check >= 1.0:
                elapsed_perf = now_perf - self._last_perf_check
                self.performance_stats["global_fps"] = round(self._frame_count_total / elapsed_perf, 1)

                new_fps = {}
                for cid, count in self._fps_counters.items():
                    new_fps[str(cid)] = round(count / elapsed_perf, 1)
                self.performance_stats["fps"] = new_fps
                self.performance_stats["latency_ms"] = round((time.time() - loop_start) * 1000, 1)

                # Reset counters
                self._fps_counters = {}
                self._frame_count_total = 0
                self._last_perf_check = now_perf

            # [OPTIMIZATION] Dynamic Throttling for 30FPS
            # Ensures we don't drift if processing takes too long.
            elapsed = time.time() - loop_start
            time.sleep(max(0.001, interval - elapsed))

    def get_buffer_summary(self) -> np.ndarray | None:
        """Creates a grid visualization (contact sheet) of recent frames for temporal context."""
        if not self.visual_buffer:
            return None

        # Extract the last 4 snapshots for a 2x2 grid
        snapshots = list(self.visual_buffer)[-4:]
        frames = []
        for s in snapshots:
            # Use the first available camera's frame for the summary
            if s["frames"]:
                idx = next(iter(s["frames"].keys()))
                frame = s["frames"][idx]
                small = cv2.resize(frame, (320, 240))

                # Add timestamp overlay
                ts_str = datetime.fromtimestamp(s["timestamp"]).strftime("%H:%M:%S")
                cv2.putText(small, ts_str, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                frames.append(small)

        if not frames:
            return None

        # Padding if less than 4
        while len(frames) < 4:
            frames.append(np.zeros((240, 320, 3), dtype=np.uint8))

        top_row = np.hstack((frames[0], frames[1]))
        bottom_row = np.hstack((frames[2], frames[3]))
        grid = np.vstack((top_row, bottom_row))
        return grid

    def _probe_ptz(self, cap) -> dict[str, bool]:
        """Probes for physical PTZ capabilities and special hardware (Orbit/PS Eye)."""
        # USB Constants
        ORBIT_PIDS = [0x08c2, 0x0892, 0x0870, 0x08cc]
        PSEYE_VID = 0x1415
        PSEYE_PIDS = [0x2000]

        self.usb_dev = None

        try:
            import usb.core
            # Try Logitech Orbit
            dev = usb.core.find(idVendor=0x046d)
            if dev and dev.idProduct in ORBIT_PIDS:
                self.usb_dev = dev
                log_event("VISION", f"Logitech Orbit detected (PID: {dev.idProduct:04x})")
                return {"pan": True, "tilt": True, "zoom": False, "digital": False, "hardware": "ORBIT", "model": "[Neural] QuickCam Orbit [DSHOW]"}

            # Try PlayStation Eye
            dev = usb.core.find(idVendor=PSEYE_VID)
            if dev and dev.idProduct in PSEYE_PIDS:
                self.usb_dev = dev
                log_event("VISION", f"PlayStation Eye detected (PID: {dev.idProduct:04x})")
                self.usb_dev = dev
                log_event("VISION", f"PlayStation Eye detected (PID: {dev.idProduct:04x})")
                return {"pan": False, "tilt": False, "zoom": False, "digital": True, "hardware": "PSEYE", "model": "[Neural] PlayStation Eye [LIBUSB]"}

        except ImportError:
            log_event("VISION", "PyUSB not installed, physical PTZ disabled", level="DEBUG")
        except Exception as e:
            log_event("VISION", f"USB Probe failed: {e}", level="DEBUG")

        return {"pan": False, "tilt": False, "zoom": False, "digital": True, "hardware": "GENERIC"}

    def get_frame(self, cam_id: int | str) -> np.ndarray | None:
        """Targeted fetch of a specific camera frame."""
        s_id = str(cam_id)
        with self._lock:
            return self._frames.get(s_id)

    def capture_all_frames(self) -> dict[str, np.ndarray]:
        """
        Retrieves the latest frames from the background buffer.
        """
        if self.simulated:
            return {}

        with self._lock:
            # Return a shallow copy of the dictionary (String keys guaranteed)
            return {str(k): v for k, v in self._frames.items()}

    def diag_hardware(self):
        """
        Runs a comprehensive diagnostic on all expected sensory hardware.
        Reports issues like driver conflicts (LibUSB vs UVC) or initialization failures.
        """
    def diag_hardware(self):  # noqa: F811
        """Hierarchical hardware diagnostic via Sensory Intelligence."""
        return sensory_intel.get_diagnostics()

    def _scan_pseyepy(self):
        """Attempts to initialize all PS Eye cameras using the native pseyepy driver (libusb)."""
        log_event("VISION", "Scanning for multiple PS Eye cameras (Native LibUSB Mode)...")
        try:
            # Probe up to 5 potential PS Eye cameras
            for i in range(5):
                try:
                    # Initialize Camera(i)
                    eye = PSEyeCamera(i, resolution=PSEyeCamera.RES_LARGE, fps=60)
                    wrapper = PSEyeWrapper(eye)

                    # Test read a frame to verify it works
                    ret, test_frame = wrapper.read()
                    if ret:
                        # Map to a special index (99, 100, 101...)
                        v_idx = 99 + i
                        self.caps[v_idx] = wrapper

                        # Try to find a specific name from PnP inventory if possible
                        label = f"PlayStation Eye #{i+1} [LIBUSB]"

                        self.hardware_metadata[v_idx] = {
                            "width": 640,
                            "height": 480,
                            "fps": 60,
                            "ptz_capabilities": {"pan": False, "tilt": False, "zoom": False, "digital": True},
                            "backend": "LIBUSB_PSEYEPY",
                            "status": "ACTIVE",
                            "model": label
                        }
                        log_event("VISION", f"[SUCCESS] PS Eye {i} Acquired at Virtual ID {v_idx}", level="SUCCESS")
                    else:
                        wrapper.release()
                except Exception:
                    # Likely no more cameras or index busy
                    break
        except Exception as e:
            log_event("VISION", f"PS Eye multi-scan failure: {e}")

    def _repair_hw_intel_file(self):
        """Attempts to repair the hardware intelligence JSON file if it is corrupted (e.g., truncated)."""
        if not os.path.exists(self.hw_intel_file):
            return

        try:
            with open(self.hw_intel_file) as f:
                json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            log_event("VISION", f"Hardware Intelligence log corrupted: {e}. Attempting repair...", level="WARNING")
            try:
                # 1. Read the raw text
                with open(self.hw_intel_file) as f:
                    content = f.read().strip()

                # 2. Basic repair: If it ends abruptly, try to close the array and objects
                # This is a bit of a hack, but better than losing everything.
                # If it's too far gone, we'll just rename it and start fresh.
                if not content.endswith("]"):
                    repaired = False
                    # Try appending closures to see if it becomes valid
                    for suffix in ["]", "}]", "}]}]"]:
                        try:
                            json.loads(content + suffix)
                            with open(self.hw_intel_file, "a") as f:
                                f.write(suffix)
                            log_event("VISION", f"Successfully repaired JSON with suffix: {suffix}")
                            repaired = True
                            break
                        except Exception:
                            continue

                    if not repaired:
                        # Rename corrupted file and start fresh
                        corrupted_path = self.hw_intel_file + ".corrupted_" + str(int(time.time()))
                        os.rename(self.hw_intel_file, corrupted_path)
                        log_event("VISION", f"JSON beyond repair. Moved to {corrupted_path}", level="ERROR")
            except Exception as repair_err:
                log_event("VISION", f"Repair logic failed: {repair_err}", level="ERROR")

    def _record_hardware_intel(self):
        """Records device capabilities and health to the permanent 'Hardware Intelligence' database using atomic writes."""
        ptz_avail = False
        for idx, meta in self.hardware_metadata.items():
            if not isinstance(meta, dict):
                continue

            friendly = meta.get("friendly_name", "").lower()
            if friendly:
                match = next((d for d in self.pnp_inventory if d.get("name", "").lower() == friendly), None)
                if match:
                    hw_id = match.get("hw_id", "")
                    vid, pid = sensory_intel._parse_vid_pid(hw_id)
                    if vid and pid:
                        meta["vid_pid"] = f"{vid}_{pid}".lower()

                if "vid_pid" not in meta:
                    if any(k in friendly for k in ["orbit", "sphere", "orb mp"]):
                        meta["vid_pid"] = "046d_08c2" # Standard Orb/Sphere PID
                        meta["ptz_capabilities"] = {"pan": True, "tilt": True, "motor_control": True}
                    elif "kinect" in friendly:
                        meta["vid_pid"] = "045e_02ae"
                        meta["ptz_capabilities"] = {"pan": False, "tilt": True, "motor_control": True}

            if idx == 98 and "vid_pid" not in meta:
                meta["vid_pid"] = "045e_02ae"
                meta["ptz_capabilities"] = {"pan": False, "tilt": True, "motor_control": True}

            caps = meta.get("ptz_capabilities", {})
            if isinstance(caps, dict) and caps.get("pan"):
                ptz_avail = True

        intel_data = {
            "timestamp": time.time(),
            "pnp_inventory": self.pnp_inventory,
            "device_tree": getattr(self, "device_tree", {}),
            "diagnostics": sensory_intel.get_diagnostics(),
            "system_profile": {
                "total_eyes": len(self.caps),
                "ptz_available": ptz_avail,
                "driver_health": "PROBED_OK" if self.caps else "HARDWARE_NOT_OPEN"
            }
        }

        try:
            # Atomic Write Implementation
            data = []
            if os.path.exists(self.hw_intel_file):
                try:
                    with open(self.hw_intel_file) as f:
                        data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]
                except (json.JSONDecodeError, ValueError):
                    log_event("VISION", "JSON check failed during record. File likely corrupt.", level="WARNING")
                    # We might have just repaired it in open(), or it corrupted in between.
                    # Best to start a list if it's broken here.
                    data = []

            data.append(intel_data)

            # Use a temporary file for atomic update
            temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(self.hw_intel_file), prefix="hw_intel_", suffix=".tmp")
            try:
                with os.fdopen(temp_fd, 'w') as f:
                    json.dump(data, f, indent=4)
                # Successful write, now replace the original
                os.replace(temp_path, self.hw_intel_file)
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e from e

        except Exception as e:
            log_event("VISION", f"Hardware Intelligence log failed: {e}", level="WARNING")

    def detect_faces(self, frames: dict[int, np.ndarray]) -> dict[int, list[dict[str, Any]]]:
        """Detect faces using refined Haar logic with Temporal Confirmation."""
        detections = {}
        for idx, frame in frames.items():
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Higher neighborhood requirement (14) and larger minSize (80x80) to kill false positives (like couches)
            faces = self.face_cascade.detectMultiScale(gray, 1.15, 14, minSize=(80, 80))

            # Temporal Consistency Check
            has_detection = len(faces) > 0

            # Ensure history deque exists for this camera index
            if idx not in self.detection_history:
                self.detection_history[idx] = deque(maxlen=8) # Slightly longer history for stability

            self.detection_history[idx].append(has_detection)

            # Only "confirm" if seen in 5 of the last 8 frames (more conservative)
            is_confirmed = sum(self.detection_history[idx]) >= 5

            detected_list = []
            if is_confirmed and has_detection:
                # Use the largest detected face
                f_list = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
                f = f_list[0]

                # --- EXTRACT LANDMARKS (Throttled) ---
                landmarks = []
                # Only process landmarks periodically to save CPU, unless we have none
                if self.landmark_throttle_counter % self.landmark_throttle_limit == 0:
                    try:
                        # Convert to RGB for dlib
                        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                        # We already have the bounding box 'f' (x, y, w, h).
                        # face_recognition expects (top, right, bottom, left)
                        # but we can pass the raw image and location list to face_landmarks

                        top = f[1]
                        right = f[0] + f[2]
                        bottom = f[1] + f[3]
                        left = f[0]
                        face_locations = [(top, right, bottom, left)]

                        raw_landmarks = face_recognition.face_landmarks(rgb_small, face_locations)

                        if raw_landmarks:
                            # Flatten the dict values into a list of [x, y] points
                            # Default model returns keys: chin, left_eyebrow, right_eyebrow, nose_bridge, nose_tip, left_eye, right_eye, top_lip, bottom_lip
                            # We normalize them to 0..1 relative to the face bbox for easier frontend rendering
                            lm = raw_landmarks[0]
                            all_points = []
                            for feature in lm.values():
                                all_points.extend(feature)

                            # Normalize relative to frame (0..1)
                            h, w = small_frame.shape[:2]
                            landmarks = [[p[0]/w, p[1]/h] for p in all_points]

                    except Exception as e:
                        log_event("VISION", f"Landmark Extraction Error: {e}", level="WARNING")

                # If no fresh landmarks, maybe use cached ones from previous frame (TODO: Implement cache if jittery)

                detected_list.append({
                    "bbox": f.tolist(),
                    "score": 1.0, # Binary confirmation
                    "landmarks": landmarks
                })
            detections[idx] = detected_list

        # Increment throttle
        self.landmark_throttle_counter += 1

        return detections

    def triangulate_position(self, provided_detections: dict | None = None) -> dict[str, Any]:
        """Calculates 3D positioning using disparity from confirmed faces."""
        with self._lock:
            if not self._frames:
                return {"status": "NO_FRAMES"}
            frames = self._frames.copy()

        face_detections = provided_detections if provided_detections is not None else self.detect_faces(frames)
        centroids = {}

        for idx, faces in face_detections.items():
            if faces:
                # Sort by area (widest face first)
                f_data = sorted(faces, key=lambda d: d["bbox"][2]*d["bbox"][3], reverse=True)[0]
                f = f_data["bbox"]
                cx = f[0] + f[2]/2
                cy = f[1] + f[3]/2
                # Ensure we handle string/int keys and missing metadata safely
                try:
                    meta = self.hardware_metadata.get(idx, self.hardware_metadata.get(str(idx)))
                    if not meta:
                         mw, mh = 640, 480 # Fallback default
                    else:
                        mw, mh = meta["width"], meta["height"]
                except Exception:
                    mw, mh = 640, 480

                # mw, mh = self.hardware_metadata[idx]["width"], self.hardware_metadata[idx]["height"]
                centroids[idx] = (cx/mw, cy/mh)

        if len(centroids) == 0:
            return {"status": "NO_FACES", "pos": [0, 0, 0]}

        if len(centroids) == 1:
            # Single camera fallback (2D Tracking)
            idx = next(iter(centroids.keys()))
            cx, cy = centroids[idx]
            # Estimate depth based on face size ratio if available, else default
            # For now, we just return the 2D pos mapped to -1..1 space
            # cx is 0..1, map to -1..1
            x_mapped = (cx - 0.5) * 2
            y_mapped = (cy - 0.5) * 2
            return {"status": "2D_TRACKING", "pos": [x_mapped, y_mapped, 1.0]}

        if len(centroids) < 2:
            return {"status": "INSUFFICIENT_VIEWS", "pos": [0, 0, 0]}

        # Robust N-Camera Triangulation
        depths = []
        xs = []
        ys = []

        indices = list(centroids.keys())
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                idx0, idx1 = indices[i], indices[j]
                c0, c1 = centroids[idx0], centroids[idx1]

                disparity = abs(c0[0] - c1[0])
                depth = 1.0 / (disparity + 0.001)

                depths.append(depth)
                xs.append((c0[0] + c1[0]) / 2)
                ys.append((c0[1] + c1[1]) / 2)

        if not depths:
            return {"status": "FACE_LOST", "pos": [0, 0, 0]}

        pos = [float(np.mean(xs)), float(np.mean(ys)), float(np.mean(depths))]
        self.last_face_pos = pos
        log_event("VISION", f"N-Camera Sync Lock: {pos}", level="DEBUG", payload={"view_count": len(centroids)})

        # 1. Update HCEP Oculomotor Dynamics
        self._update_hcep(pos, face_detections)

        # 2. Auto-Track using HCEP target instead of raw face center
        hcep_target = self.hcep_state["target_pos"]
        self.move_ptz(hcep_target[0] - 0.5, hcep_target[1] - 0.5)

        # Update Telemetry Layer (SpatialSense Standard)
        # [FIX] Only update detections if we actually found faces with the conservative detector
        # Otherwise preserve the richer detection data from the face recognition engine
        existing_detections = getattr(self, 'latest_telemetry', {}).get('detections', {})
        use_detections = face_detections if any(len(v) > 0 for v in face_detections.values()) else existing_detections

        self.latest_telemetry = {
            "status": "TRACKING" if len(centroids) > 0 else "SEARCHING",
            "pos": pos,
            "detections": use_detections, # Preserve rich detection data if Haar found nothing
            "hcep": self.hcep_state.copy(), # Inject Oculomotor state
            "ir_active": getattr(self, "ir_active", False),
            "depth_active": getattr(self, "depth_active", False),
            "timestamp": time.time()
        }

        return self.latest_telemetry

    def get_telemetry(self) -> dict[str, Any]:
        """Returns the latest telemetry data safely."""
        with self._lock:
            # Add spatial intelligence to telemetry
            self.latest_telemetry["hcep"] = self.hcep_state.copy()
            self.latest_telemetry["spatial_fusion"] = self.spatial_fusion.copy()
            return self.latest_telemetry.copy()

    def _update_hcep(self, face_pos: list[float], detections: dict[int, list[dict[str, Any]]]):
        """Updates the Human Conversation Eye Points (HCEP) state machine."""
        now = time.time()

        # 0. User Gaze Inference (Where is the human looking?)
        # -----------------------------------------------------------------
        native_pose = None
        for _idx, det_list in detections.items():
            for d in det_list:
                if d.get("native_kinect") and "pose" in d:
                    native_pose = d["pose"]
                    break
            if native_pose:
                break

        if native_pose:
            self.hcep_state["user_pose"] = native_pose
            pitch, yaw = native_pose.get("pitch", 0), native_pose.get("yaw", 0)
            # Heuristic: If head is within 15 degrees of center (yaw) and 10 degrees (pitch), they are "looking at screen"
            is_looking_at_screen = abs(yaw) < 0.25 and abs(pitch) < 0.20 # Radians appx

            if is_looking_at_screen:
                self.hcep_state["user_gaze"] = "SCREEN"
                self.hcep_state["user_attention"] = min(1.0, self.hcep_state["user_attention"] + 0.1)
            else:
                self.hcep_state["user_gaze"] = "AMBIENT"
                self.hcep_state["user_attention"] = max(0.0, self.hcep_state["user_attention"] - 0.05)

        # 1. Saccade Logic: Shift interest points periodically
        # -----------------------------------------------------------------
        # Dynamic saccade interval based on user attention (Faster shifts if not paying attention?)
        current_interval = self.hcep_state["saccade_interval"]
        if self.hcep_state["user_attention"] < 0.3:
            current_interval *= 0.5 # Look around more if bored

        if now - self.hcep_state["last_saccade"] > current_interval:
            # Shift gaze target
            targets = ["FACE_CENTER", "LEFT_EYE", "RIGHT_EYE", "MOUTH"]
            weights = [0.4, 0.25, 0.25, 0.1] # Probability weights
            self.hcep_state["gaze_target_type"] = np.random.choice(targets, p=weights)

            # Reset saccade timer
            self.hcep_state["saccade_interval"] = 2.0 + np.random.random() * 3.0
            self.hcep_state["last_saccade"] = now
            self.hcep_state["lock_stability"] = 0.0
            log_event("HCEP", f"Saccade Shift -> {self.hcep_state['gaze_target_type']} (User Gaze={self.hcep_state['user_gaze']})")

        # 2. Jitter Logic: Natural micro-oculomotor tremor
        self.hcep_state["micro_jitter"] = [
            (np.random.random() - 0.5) * 0.01,
            (np.random.random() - 0.5) * 0.01
        ]

        # 3. Calculate Target Position based on gaze type and face geometry
        fx, fy, fz = face_pos
        base_target = [fx, fy]

        # [ENHANCEMENT] Use real landmarks if available
        active_landmarks = None
        for det_list in detections.values():
            if det_list and "landmarks" in det_list[0]:
                active_landmarks = det_list[0]["landmarks"]
                break

        target_point = None
        if active_landmarks:
            gtype = self.hcep_state["gaze_target_type"]
            # Handle Dictionary (Neural)
            if isinstance(active_landmarks, dict):
                if gtype == "LEFT_EYE" and "left_eye" in active_landmarks:
                    pts = active_landmarks["left_eye"]
                    target_point = [np.mean([p[0] for p in pts]), np.mean([p[1] for p in pts])]
                elif gtype == "RIGHT_EYE" and "right_eye" in active_landmarks:
                    pts = active_landmarks["right_eye"]
                    target_point = [np.mean([p[0] for p in pts]), np.mean([p[1] for p in pts])]
                elif gtype == "MOUTH" and ("top_lip" in active_landmarks or "bottom_lip" in active_landmarks):
                    pts = active_landmarks.get("top_lip", []) + active_landmarks.get("bottom_lip", [])
                    target_point = [np.mean([p[0] for p in pts]), np.mean([p[1] for p in pts])]
                elif gtype == "FACE_CENTER" and "nose_tip" in active_landmarks:
                    pts = active_landmarks["nose_tip"]
                    target_point = [np.mean([p[0] for p in pts]), np.mean([p[1] for p in pts])]

            # Handle Array (Kinect 87)
            elif isinstance(active_landmarks, list) and len(active_landmarks) == 87:
                if gtype == "LEFT_EYE":
                    target_point = active_landmarks[24]
                elif gtype == "RIGHT_EYE":
                    target_point = active_landmarks[50]
                elif gtype == "MOUTH":
                    target_point = active_landmarks[5]
                elif gtype == "FACE_CENTER":
                    target_point = active_landmarks[40]

        if target_point:
            base_target = [float(target_point[0]), float(target_point[1])]
        else:
            # Fallback to Heuristic if landmarks missing
            if self.hcep_state["gaze_target_type"] == "LEFT_EYE":
                base_target[0] -= 0.05 / fz
                base_target[1] -= 0.05 / fz
            elif self.hcep_state["gaze_target_type"] == "RIGHT_EYE":
                base_target[0] += 0.05 / fz
                base_target[1] -= 0.05 / fz
            elif self.hcep_state["gaze_target_type"] == "MOUTH":
                base_target[1] += 0.08 / fz

        # Apply jitter
        base_target[0] += self.hcep_state["micro_jitter"][0]
        base_target[1] += self.hcep_state["micro_jitter"][1]

        # Smoothly interpolate current gaze toward new target
        alpha = 0.15
        self.hcep_state["target_pos"][0] += (base_target[0] - self.hcep_state["target_pos"][0]) * alpha
        self.hcep_state["target_pos"][1] += (base_target[1] - self.hcep_state["target_pos"][1]) * alpha
        self.hcep_state["lock_stability"] = min(1.0, self.hcep_state["lock_stability"] + 0.05)

        # 4. Interest Score
        # Stable lock on eyes increases score
        engagement_map = {"FACE_CENTER": 0.5, "LEFT_EYE": 0.9, "RIGHT_EYE": 0.9, "MOUTH": 0.7}
        base_engagement = engagement_map.get(self.hcep_state["gaze_target_type"], 0.2)
        self.hcep_state["interest_score"] = float(base_engagement * self.hcep_state["lock_stability"])

        # 5. Affective Analysis (Smile Detection)
        self.hcep_state["smile_score"] = self._analyze_smile(active_landmarks)

    def _analyze_smile(self, landmarks) -> float:
        """Lightweight geometric smile detection without heavy models."""
        if not landmarks:
            return 0.0

        try:
            # Handle Dictionary (Neural)
            if isinstance(landmarks, dict):
                # Using Dlib/FaceRec standard keys if present
                # 48(left), 54(right) for mouth corners in 68-pt
                # 36(left), 45(right) for eyes
                if 'left_eye' in landmarks and 'right_eye' in landmarks and ('top_lip' in landmarks or 'bottom_lip' in landmarks):
                    l_eye = np.mean(landmarks['left_eye'], axis=0)
                    r_eye = np.mean(landmarks['right_eye'], axis=0)
                    eye_dist = np.linalg.norm(l_eye - r_eye)

                    # For simplicity, if we have mouth corners we use them.
                    # Dlib landmarks usually grouped under 'mouth' or similar.
                    # If not, we heuristic from lips.
                    mouth_pts = landmarks.get('top_lip', []) + landmarks.get('bottom_lip', [])
                    if len(mouth_pts) >= 2:
                        m_xs = [p[0] for p in mouth_pts]
                        mouth_width = max(m_xs) - min(m_xs)
                        # Ratio of mouth width to eye distance increases during smile
                        # Normal ~0.4-0.5, Smile > 0.6
                        ratio = mouth_width / eye_dist if eye_dist > 0 else 0
                        return float(max(0.0, min(1.0, (ratio - 0.45) / 0.2)))

            # Handle Array (Kinect 87)
            elif isinstance(landmarks, list) and len(landmarks) == 87:
                # 24(L-Eye), 50(R-Eye), 5(L-Mouth), 6(R-Mouth)
                eye_dist = np.linalg.norm(np.array(landmarks[24]) - np.array(landmarks[50]))
                mouth_dist = np.linalg.norm(np.array(landmarks[5]) - np.array(landmarks[6]))
                ratio = mouth_dist / eye_dist if eye_dist > 0 else 0
                # Kinect 87-pt ratio is slightly different
                return float(max(0.0, min(1.0, (ratio - 0.5) / 0.25)))

        except Exception:
            pass
        return 0.0

    def _scan_kinect(self):
        """Specifically prober for Kinect v1 via dedicated connector (Index 98)."""
        log_event("VISION", "Scanning for Xbox 360 Kinect hardware...")
        try:
            # 1. PnP Verification: Is it in the inventory?
            is_present = False
            for dev in self.pnp_inventory:
                dev_name = dev.get("name", "").lower()
                hw_id = dev.get("hw_id", "").lower()
                if "kinect" in dev_name or "045e" in hw_id:
                    is_present = True
                    break

            if not is_present:
                sensory_intel.log_trace("Kinect PnP not found. Skipping specialized initialization.")
                return

            # 2. Initialization
            from src.orchestrator.kinect_connector import KinectConnector
            k_conn = KinectConnector(index=0) # Primary Kinect
            if k_conn.open():
                k_conn.set_stream_state('face', True)
                log_event("VISION", "[SUCCESS] Kinect v1 Linked (Index 98, 105, 106)")
                self.caps["98"] = k_conn
                self.hardware_metadata["98"] = {
                    "width": 640,
                    "height": 480,
                    "fps": 30,
                    "ptz_capabilities": {"pan": False, "tilt": True, "motor_control": True, "digital": True},
                    "backend": "KINECT_SDK_18",
                    "status": "ACTIVE",
                    "model": "[Neural] Xbox 360 Kinect [Legacy]",
                    "vid_pid": "045e_02ae"
                }
            else:
                last_hr = getattr(k_conn, "last_hr", 0)
                sensory_intel.log_trace(f"Kinect NUI initialization failed (HRESULT: {hex(last_hr)}).", level="WARNING")
        except Exception as e:
            log_event("VISION", f"Kinect scan crash: {e}", level="ERROR")

    def _check_kinect(self):
        """Heuristic check/refresh for Kinect (Alias for scan)."""
        if "98" not in self.caps:
            self._scan_kinect()



    def cycle_camera_mode(self, device_idx: int) -> str:
        """Cycles through available video modes for supported hardware (e.g. Kinect)."""
        # ONLY allows cycling if we are clicking on the SUB-SENSOR ID (99)
        # Clicking Color (98) should NOT affect the sub-sensor mode (Crosstalk Fix)
        if device_idx != 99:
            return "UNSUPPORTED"

        # Redirect to parent device 98
        if "98" not in self.caps:
            return "INVALID"

        cap = self.caps["98"]
        if hasattr(cap, 'sub_mode') and hasattr(cap, 'switch_sub_mode'):
            # Specific to Kinect (SDK 1.8)
            # Toggle between Depth and IR for the Sub-Stream
            from src.orchestrator.kinect_connector import NUI_IMAGE_TYPE_COLOR_INFRARED, NUI_IMAGE_TYPE_DEPTH
            current = cap.sub_mode
            next_mode = NUI_IMAGE_TYPE_COLOR_INFRARED if current == NUI_IMAGE_TYPE_DEPTH else NUI_IMAGE_TYPE_DEPTH

            if cap.switch_sub_mode(next_mode):
                label = "DEPTH" if next_mode == NUI_IMAGE_TYPE_DEPTH else "INFRARED"
                log_event("VISION", f"Kinect Sub-Stream (ID 99) cycled to {label}")
                return label

        return "UNSUPPORTED"


    def steer_to_angle(self, angle: float):
        """
        Steers the digital crop to an absolute angle (e.g. from Audio DoA).
        Angle is in degrees (-90 to +90).
        """
        # Map -90..90 to 0.0..1.0 for cx
        target_cx = 0.5 + (angle / 180.0) # -90 -> 0.0, 90 -> 1.0
        # Call move_ptz with high alpha/override to jump or drift
        self.move_ptz(pan_delta=0, tilt_delta=0, absolute_cx=target_cx)

    def move_ptz(self, pan_delta: float, tilt_delta: float, device_idx: int = 0, absolute_cx: float | None = None):
        """
        Moves PTZ for a specific device.
        Supports digital cropping and (deferred) physical motors.
        """
        # Threshold to ignore minor jitter
        if abs(pan_delta) < 0.05 and abs(tilt_delta) < 0.05:
            return

        # Smoothing (Moving Average)
        self.pan_tilt_buffer.append((pan_delta, tilt_delta))
        p_avg = sum(p for p, t in self.pan_tilt_buffer) / len(self.pan_tilt_buffer)
        t_avg = sum(t for p, t in self.pan_tilt_buffer) / len(self.pan_tilt_buffer)

        # Apply to all relevant hardware
        for idx in self.caps:
            meta = self.hardware_metadata.get(idx, {})
            caps = meta.get("ptz_capabilities", {})

            # 1. Physical motor control bypassed (Digital Preferred)
            if caps.get("pan") or caps.get("tilt"):
                pass

            # 2. Digital Tracking
            current = self.digital_crop.get(idx, {"cx": 0.5, "cy": 0.5, "scale": 1.0})

            # Logic: If absolute_cx is provided (Audio/Fusion), we drift toward it.
            # If p_avg is provided (Face Tracking), it adds delta.
            alpha = 0.1
            if absolute_cx is not None:
                # Use absolute target with gentle smoothing
                target_cx = current["cx"] + (absolute_cx - current["cx"]) * 0.08
            else:
                target_cx = 0.5 if not self.zoom_enabled else current["cx"] + p_avg * alpha

            target_cy = 0.5 if not self.zoom_enabled else current["cy"] + t_avg * alpha

            new_cx = max(0.2, min(0.8, target_cx))
            new_cy = max(0.2, min(0.8, target_cy))

            # Transition to target scale
            if self.zoom_enabled:
                # Zoom in to 1.5x if a face is relatively close/stable
                target_scale = 1.5 if (self.last_face_pos[2] < 2.5) else 1.0
            else:
                # Force 100% view when zoom is disabled
                target_scale = 1.0

            # Smoothly interpolate scale
            scale_alpha = 0.2
            new_scale = current["scale"] + (target_scale - current["scale"]) * scale_alpha

            self.digital_crop[idx] = {"cx": new_cx, "cy": new_cy, "scale": new_scale}

            # 3. Physical Motor Movement (Autonomous tracking)
            meta = self.hardware_metadata.get(idx, {})
            caps = meta.get("ptz_capabilities", {})
            if caps.get("motor_control"):
                # We send motorized pulses if the error is significant enough to warrant physical movement.
                # Threshold to prevent motor jitter (mm or pixels normalized)
                px_error = abs(p_avg) if p_avg is not None else 0
                tx_error = abs(t_avg) if t_avg is not None else 0

                if px_error > 0.05 or tx_error > 0.05:
                    vid_pid = meta.get("vid_pid", "")
                    if vid_pid:
                        # Use a small gain for auto-tracking
                        m_pan = int(p_avg * 100) if p_avg else 0
                        m_tilt = int(t_avg * 100) if t_avg else 0
                        self.hardware_ptz_control(vid_pid, pan=m_pan, tilt=m_tilt)

    def hardware_ptz_control(self, vid_pid: str, pan: int = 0, tilt: int = 0, reset: bool = False):
        """
        Routes manual hardware PTZ commands to specific device drivers.
        Supports Logitech QuickCam Orbit and Xbox 360 Kinect.
        """
        vid_pid = vid_pid.lower()
        log_event("VISION", f"Hardware PTZ Request: {vid_pid}", payload={"pan": pan, "tilt": tilt, "reset": reset})

        # 1. Logitech QuickCam Orbit Family
        orbit_pids = ["046d_08c2", "046d_0892", "046d_0870", "046d_08cc", "046d_0994"]

        # Fallback: if vid_pid search fails, check if the string contains "orbit" or "sphere"
        is_orbit = any(pid in vid_pid for pid in orbit_pids)
        if not is_orbit and any(k in vid_pid for k in ["orbit", "sphere", "orb-mp"]):
            is_orbit = True
            log_event("VISION", f"Name-based routing fallback for: {vid_pid} -> Using 046d_08c2")

        if is_orbit:
            try:
                from src.orchestrator.quickcam_driver import quickcam_driver
                if not quickcam_driver.connected:
                    # Get model name for Windows Native selector
                    meta = next((m for m in self.hardware_metadata.values() if m.get("vid_pid") == vid_pid), {})
                    model_name = meta.get("model", "")
                    quickcam_driver.connect(friendly_name=model_name)

                if reset:
                    quickcam_driver.reset_position()
                else:
                    if pan != 0:
                        quickcam_driver.pan(pan)
                    if tilt != 0:
                        quickcam_driver.tilt(tilt)

                pos = quickcam_driver.get_position()
                return {"status": "OK", "driver": "quickcam_driver", "position": pos}
            except Exception as e:
                log_event("VISION", f"QuickCam PTZ Error: {e}", level="ERROR")
                return {"status": "ERROR", "detail": str(e)}

        # 2. Microsoft Kinect v1 (Tilt Only)
        if "045e_02ae" in vid_pid:
            try:
                kinect = self.caps.get(98) # Special index for Kinect
                if not kinect:
                    # Attempt to re-probe if missing
                    self._check_kinect()
                    kinect = self.caps.get(98)

                if kinect and hasattr(kinect, 'set_tilt'):
                    if reset:
                        kinect.set_tilt(0)
                        current_tilt = 0
                    else:
                        # Kinect tilt is absolute degrees.
                        # We treat 'tilt' as a delta if it's large, but here let's try to track it.
                        # For simplicity, we'll map the UI's 'LARGE_MOVE' (800) to ~5 degrees.
                        delta_deg = tilt / 160.0
                        # We need to know current tilt. KinectConnector doesn't store it yet.
                        # I'll add a simple tracker or just use absolute for now if provided.
                        # Actually, let's just use absolute if 'pan' is 0 and 'tilt' is specified.
                        # But the UI sends deltas.

                        # Let's assume the user wants to nudge it.
                        # I'll add a 'current_tilt' to OrbCloudVision for Kinect.
                        if not hasattr(self, '_kinect_tilt'):
                            self._kinect_tilt = 0
                        self._kinect_tilt = max(-27, min(27, self._kinect_tilt + delta_deg))
                        kinect.set_tilt(self._kinect_tilt)
                        current_tilt = self._kinect_tilt

                    return {"status": "OK", "driver": "kinect_connector", "position": [0, current_tilt]}
                else:
                    return {"status": "ERROR", "detail": "Kinect motor control not available"}
            except Exception as e:
                log_event("VISION", f"Kinect PTZ Error: {e}", level="ERROR")
                return {"status": "ERROR", "detail": str(e)}

        return {"status": "ERROR", "detail": f"Device {vid_pid} does not support motorized control or is not initialized."}

    def _send_usb_ctrl(self, pan: float, tilt: float):
        """Sends raw XU control pulses to the physical motor (Legacy / Auto-track)."""
        if not hasattr(self, 'usb_dev') or self.usb_dev is None:
            return

        try:
            # Pack as little-endian signed 16-bit integers (XU_PT_RELATIVE)
            # Scaling normalized -1..1 to motor speed units
            p_val = max(-32768, min(32767, int(pan * 640)))
            t_val = max(-32768, min(32767, int(tilt * 640)))
            data = struct.pack("<hh", p_val, t_val)

            # bmRequestType, bRequest=SET_CUR(1), wValue=(SEL_PT_REL(1) << 8), wIndex=(UNIT_ID(9) << 8) | INTF(2)
            self.usb_dev.ctrl_transfer(0x21, 0x01, 0x0100, 0x0902, data)
            log_event("VISION", "Physical PTZ command sent", level="DEBUG", payload={"p": p_val, "t": t_val})
        except Exception as e:
            log_event("VISION", f"Physical PTZ failed: {e}", level="WARNING")

    def capture_frame(self) -> np.ndarray | None:
        """Legacy support for single frame capture (primary camera)."""
        all_frames = self.capture_all_frames()
        if self.device_indices[0] in all_frames:
            return all_frames[self.device_indices[0]]
        return None

    def set_active_camera(self, cam_id: int):
        """Sets the primary camera ID for synchronization."""
        if cam_id in self.caps:
            self.active_cam_id = cam_id
            self._save_memory()  # Persist immediately
            log_event("VISION", f"Active Camera Context Switched: {cam_id}")
            return True
        return False



    def get_latent_features(self) -> torch.Tensor:
        """
        Stub for vision-to-vector projection.
        In a full implementation, this would pass the frame through a Vision Encoder.
        """
        # Returning dummy 128d vector for 'image_embed_dim' compatibility
        return torch.randn(1, 128)

    def close(self):
        """Releases resources."""
        self._is_running = False
        self._stop_buffer.set()
        if self._buffer_thread:
            with contextlib.suppress(Exception):
                self._buffer_thread.join(timeout=1.0)

        for cid, cap in self.caps.items():
            try:
                log_event("VISION", f"Releasing Hardware ID: {cid}")
                cap.release()
            except Exception as e:
                log_event("VISION", f"Failed to release ID {cid}: {e}", level="WARNING")

        self.caps.clear()
        log_event("VISION", "OrbCloud Vision resources purged.")

    def get_hardware_intelligence(self) -> dict[str, Any]:
        """Returns collected device capabilities and PnP inventory."""
        return {
            "metadata": self.hardware_metadata,
            "pnp_inventory": self.pnp_inventory
        }

# Singleton instance for high-level tools
_vision_instance: OrbCloudVision | None = None

def get_vision_layer() -> OrbCloudVision:
    """Returns the global OrbCloudVision singleton instance."""
    global _vision_instance
    if _vision_instance is None:
        _vision_instance = OrbCloudVision()
    return _vision_instance

if __name__ == "__main__":
    # Test Universal capture (Requires camera)
    import torch
    vision = OrbCloudVision()
    if vision.open():
        frame = vision.capture_frame()
        if frame is not None:
            print(f"Captured frame: {frame.shape}")
            features = vision.get_latent_features()
            print(f"Latent Features: {features.shape}")
        vision.close()
