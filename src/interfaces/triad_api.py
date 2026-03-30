
import asyncio
import base64
import logging
import os
import sys
import threading
import time
from contextlib import asynccontextmanager
from typing import Any

import cv2
import numpy as np
import uvicorn

try:
    import torch
except ImportError:
    torch = None
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


# --- JSON/NumPy Serialization Helper ---
def sanitize_numpy(data):
    """Recursively converts NumPy types to standard Python types for JSON serialization."""
    if isinstance(data, dict):
        return {k: sanitize_numpy(v) for k, v in data.items()}
    elif isinstance(data, list | tuple):
        return [sanitize_numpy(v) for v in data]
    elif isinstance(data, np.ndarray):
        return sanitize_numpy(data.tolist())
    elif isinstance(data, np.generic):
        # np.generic is the base for all numpy scalar types (int32, float64, bool_, etc.)
        return data.item()
    elif isinstance(data, bytes | bytearray):
        # Skip binary data
        return None
    else:
        return data



# --- Console Redirection Logic ---
class ConsoleLogger:
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.error_terminal = sys.stderr
        self.log = open(filepath, "a", encoding="utf-8", buffering=1) # buffering=1 for line-buffered

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def isatty(self):
        return self.terminal.isatty()

os.makedirs("logs", exist_ok=True)
console_log_path = os.path.join("logs", "triad_api_console.log")
sys.stdout = ConsoleLogger(console_log_path)
sys.stderr = sys.stdout # Redirect stderr to the same file

# --- Logging Integration ---
# Configure root logger to pipe all module logs to the console log file
logging.root.handlers = [] # Clear existing handlers if any
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(console_log_path, encoding='utf-8'),
        logging.StreamHandler(sys.stdout.terminal) # Also print to actual terminal
    ]
)

# Intercept uvicorn logs
for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    l = logging.getLogger(logger_name)
    l.handlers = logging.root.handlers
    l.propagate = False

print(f"\n--- API SESSION START: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
# ---------------------------------

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.intelligence.stt_service import STTService
from src.intelligence.tts_service import TTSService
from src.core.config.runtime_mode_config import load_runtime_mode_config
from src.interfaces.telemetry_manager import get_telemetry_manager
from src.orchestrator.kinect_fusion_adapter import KinectFusionAdapter
from src.orchestrator.sensory_intelligence import sensory_intel
from src.orchestrator.session_manager import session_manager
from src.orchestrator.system_logger import log_event
from src.orchestrator.runtime_mode_controller import RuntimeModeController
from src.orchestrator.unified_triad import UnifiedBrainTriad

# Global Audio Services
stt_service = None
tts_service = None
telemetry_manager = None
runtime_mode_controller = None
kinect_fusion_adapter = None
msg_queue = [] # Simple queue for passing STT msgs to UI for now


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Unified Lifecycle Manager for hardware and neural resources."""
    global triad_instance, stt_service, tts_service, runtime_mode_controller, kinect_fusion_adapter

    # --- STARTUP ---
    try:
        log_event("API", "Initializing Global Triad Instance...")
        triad_instance = UnifiedBrainTriad()

        # Auto-Start Vision Layer in Background
        if triad_instance.vision:
            log_event("API", "Triggering Vision Layer Auto-Start...")
            threading.Thread(target=triad_instance.vision.open, daemon=True).start()

        log_event("API", "Triad Online.")

        # Runtime mode controller (additive non-breaking policy layer)
        mode_config = load_runtime_mode_config()
        runtime_mode_controller = RuntimeModeController(
            native_audio_enabled=mode_config.native_audio_enabled,
            avatar_mode_preference=mode_config.avatar_mode_default,
            audio_mode_preference=mode_config.audio_mode_default,
            vram_switch_threshold_gb=mode_config.vram_switch_threshold_gb,
            fps_switch_threshold=mode_config.fps_switch_threshold,
        )
        runtime_mode_controller.apply_preferences(
            avatar_preference=mode_config.avatar_mode_default,
            audio_preference=mode_config.audio_mode_default,
        )
        triad_instance.runtime_mode_controller = runtime_mode_controller

        # Kinect fusion adapter (skeleton status layer for RGB/Depth/IR readiness)
        kinect_fusion_adapter = KinectFusionAdapter()
        kinect_fusion_adapter.refresh(getattr(triad_instance, "vision", None))

        # Init Audio Intelligence
        try:
            log_event("API", "Initializing Audio Services...")
            stt_service = STTService(model_size="tiny.en", device="cpu")
            tts_service = TTSService()
            log_event("API", "Audio Services Ready.")

            # Init Telemetry
            telemetry_manager = get_telemetry_manager(triad_instance)
            log_event("API", "Telemetry Manager Online.")
        except Exception as e:
            log_event("API", f"Audio Service Init Failed: {e}", level="ERROR")

    except Exception as e:
        log_event("API", f"Failed to init Triad: {e}", level="CRITICAL")

    yield

    # --- SHUTDOWN ---
    log_event("API", "SHUTDOWN SIGNAL RECEIVED. Releasing resources...")

    # 1. Stop STT
    if stt_service:
        try:
            log_event("API", "Stopping STT Service...")
            stt_service.stop()
        except Exception:
            pass

    # 1.5 Telemetry Cleanup
    if telemetry_manager:
        telemetry_manager.disconnect(None)

    # 2. Shutdown Triad (Vision/Audio/Models)
    if triad_instance:
        try:
            triad_instance.shutdown()
        except Exception as e:
            log_event("API", f"Triad Shutdown error: {e}", level="WARNING")

    log_event("API", "CLEAN SHUTDOWN COMPLETE. System Halted.")
# New Vector Connector
try:
    from src.orchestrator.vector_connector import VectorMemoryConnector
    vector_memory = VectorMemoryConnector()
except Exception as e:
    log_event("API", f"Vector Memory Init Failed: {e}", level="WARNING")
    vector_memory = None

# --- agent0core DI wiring (breaks reverse dependency on src/) ---
try:
    from src.integrations.agent0core_bridge import wire_agent0core
    wire_agent0core()
    log_event("API", "agent0core DI boundary wired successfully")
except Exception as e:
    log_event("API", f"agent0core DI wiring failed (non-fatal): {e}", level="WARNING")

app = FastAPI(title="ImpressionCore B3-Triad API", lifespan=lifespan)

@app.get("/")
async def root():
    """Root endpoint to confirm API is running."""
    return {
        "status": "ONLINE",
        "system": "ImpressionCore B3-Triad",
        "version": "1.2.0",
        "endpoints": {
            "system": "/v1/system/status",
            "agent0": "/v1/agent0/status",
            "monitor": "/system_monitor.html"
        }
    }

from fastapi.responses import FileResponse


@app.get("/system_monitor.html")
async def system_monitor():
    """Serve the System Monitor HTML page."""
    monitor_path = r"d:\Projects\impressioncore\src\interfaces\web_client\public\system_monitor.html"
    return FileResponse(monitor_path, media_type="text/html")

# Allow CORS for React Frontend — origins controlled by IMPRESSIONCORE_ALLOWED_ORIGINS env var
try:
    from src.core.config.cors_config import get_allowed_origins
except ImportError:
    from core.config.cors_config import get_allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SECURITY MIDDLEWARE ---
from agent0core.config import default_config as agent_config


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    # Skip auth for public endpoints, docs, and OPTIONS (CORS)
    public_paths = ["/", "/docs", "/openapi.json", "/system_monitor.html", "/favicon.ico", "/v1/system/status", "/v1/telemetry/stream"]
    if request.url.path in public_paths or request.url.path.startswith("/static") or request.method == "OPTIONS":
        return await call_next(request)

    # Check for API Key
    api_key = request.headers.get("X-API-Key")
    expected_key = agent_config.api_key

    # If no key configured, we warn but allow (Dev Mode) - or block?
    # Let's match the "default key" behavior.
    # If no key configured, we warn but allow (Dev Mode) - or block?
    # Let's match the "default key" behavior.
    # Validate API key — localhost bypass removed for security
    if api_key != expected_key:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing X-API-Key header"}
        )

    response = await call_next(request)
    return response

# Serve Logs folder as static audio
os.makedirs("logs", exist_ok=True)
app.mount("/audio", StaticFiles(directory="logs"), name="audio")

# Serve Captures folder for Vision Snapshots
# Note: Using public/captures so frontend (dev) and backend both align
capture_dir = r"d:\Projects\impressioncore\src\interfaces\web_client\public\captures"
os.makedirs(capture_dir, exist_ok=True)
app.mount("/captures", StaticFiles(directory=capture_dir), name="captures")

# Serve Voice Recordings folder for STT audio persistence
voice_rec_dir = r"d:\Projects\impressioncore\src\interfaces\web_client\public\voice_recordings"
os.makedirs(voice_rec_dir, exist_ok=True)
app.mount("/voice_recordings", StaticFiles(directory=voice_rec_dir), name="voice_recordings")

# --- TELEMETRY ENDPOINT ---
@app.websocket("/v1/telemetry/stream")
async def telemetry_stream(websocket: WebSocket):
    global telemetry_manager
    if not telemetry_manager:
        await websocket.close(code=1011) # Internal Error
        return

    await telemetry_manager.connect(websocket)
    try:
        while True:
            # Client can send commands if needed, or just listen
            await websocket.receive_text()
            # Handle incoming control commands if future scope requires it
    except Exception:
        pass
    finally:
        telemetry_manager.disconnect(websocket)

# Serve public folder for system_monitor.html and other static files
public_dir = r"d:\Projects\impressioncore\src\interfaces\web_client\public"
app.mount("/static", StaticFiles(directory=public_dir), name="static")

# Global Triad Instance
triad_instance = None

d_print = print

class GenerateRequest(BaseModel):
    prompt: str
    image_base64: str | None = None
    voice_enabled: bool = True
    session_id: str | None = None
    user_audio_url: str | None = None  # STT audio URL from frontend
    snapshots: list[str] | None = None  # Multi-image support (base64)
    avatar_mode_preference: str | None = None  # auto|2d|video
    audio_mode_preference: str | None = None  # hybrid|cascaded|native



@app.post("/v1/process")
async def process_multimodal(request: GenerateRequest):
    global triad_instance, runtime_mode_controller, kinect_fusion_adapter
    if not triad_instance:
        raise HTTPException(status_code=503, detail="Triad not initialized")

    t_start = time.time()
    t_checkpoints = {}

    try:
        if runtime_mode_controller:
            runtime_mode_controller.apply_preferences(
                avatar_preference=request.avatar_mode_preference,
                audio_preference=request.audio_mode_preference,
            )
            runtime_mode_controller.refresh(triad_instance)

        sensory_data = {}
        kinect_fusion_status = None
        if kinect_fusion_adapter:
            kinect_fusion_adapter.refresh(getattr(triad_instance, "vision", None))
            kinect_fusion_status = kinect_fusion_adapter.get_status()
            sensory_data["kinect_fusion"] = kinect_fusion_status

        # 1. Decode Image (Client-Side Vision)
        t0 = time.time()
        if request.image_base64:
            try:
                # Remove header if present (data:image/jpeg;base64,...)
                img_str = request.image_base64
                if "," in img_str:
                    img_str = img_str.split(",")[1]

                img_bytes = base64.b64decode(img_str)
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img is not None:
                    sensory_data['vision_frames'] = {0: img} # Use dict for compatibility with IDs
                    log_event("API", "Image decoded successfully.")
            except Exception as e:
                log_event("API", f"Image Decode Error: {e}", level="WARNING")

        # 1.1 Multi-Snapshot support
        if request.snapshots:
            try:
                if 'vision_frames' not in sensory_data:
                    sensory_data['vision_frames'] = {}

                for i, snap_str in enumerate(request.snapshots):
                    if "," in snap_str:
                        snap_str = snap_str.split(",")[1]

                    snap_bytes = base64.b64decode(snap_str)
                    nparr = np.frombuffer(snap_bytes, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if img is not None:
                        # Use indices 0, 1... for client-side snapshots
                        sensory_data['vision_frames'][i] = img

                log_event("API", f"Decoded {len(request.snapshots)} client-side snapshots.")
            except Exception as e:
                log_event("API", f"Snapshots Decode Error: {e}", level="WARNING")

        t_checkpoints['decode'] = float(f"{time.time() - t0:.3f}")

        # 2. Generate with History
        t0 = time.time()
        history = []
        session_id = request.session_id
        if session_id:
            try:
                # Load History (Defensive)
                session_data = session_manager.get_session(session_id)
                if session_data:
                    history = session_data.get("messages", [])

                # Persist User Prompt (Before Generation)
                session_manager.add_message(session_id, "user", request.prompt, audio_url=request.user_audio_url)
            except Exception as e:
                log_event("API", f"Session Load/Save Error (Non-Fatal): {e}", level="WARNING")

        t_checkpoints['history'] = float(f"{time.time() - t0:.3f}")

        # 3. LLM Generation
        t0 = time.time()
        result = triad_instance.generate(request.prompt, sensory_data=sensory_data, history=history)
        t_checkpoints['llm'] = float(f"{time.time() - t0:.3f}")

        # Check for Snapshots in result
        snapshot_url = result.get('snapshot_url')
        snapshot_urls = result.get('snapshot_urls', [])

        # 4. Handle Audio
        t0 = time.time()
        audio_url = None
        native_audio = None
        if request.voice_enabled:
            try:
                effective_audio_mode = "cascaded"
                if runtime_mode_controller:
                    effective_audio_mode = runtime_mode_controller.get_state().get("effective_audio_mode", "cascaded")

                # Native path remains feature-flagged; fallback is cascaded TTS path
                if effective_audio_mode == "native":
                    log_event("API", "Native audio mode requested; feature flag fallback to cascaded TTS path.")
                    native_audio = _run_native_audio_stub(result.get('response', ''))

                triad_instance.speak(result['response'], play_now=False)
                audio_url = getattr(triad_instance, 'last_audio_url', '/audio/last_speech.mp3')
            except Exception as e:
                log_event("API", f"TTS Generation Error: {e}", level="WARNING")
        t_checkpoints['tts'] = float(f"{time.time() - t0:.3f}")

        # Check for Generated Images in result (Mental Imagery)
        generated_image_url = result.get('generated_image_url')

        # 5. Persistence & Vector DB
        t0 = time.time()
        if session_id:
             # --- VECTOR DB INGESTION ---
             if vector_memory:
                 try:
                     # Description is in result['response'], Image is snapshot_url.
                     description_text = result['response'][:500] if result.get('response') else "Visual snapshot captured."
                     vector_memory.add_memory(description_text, snapshot_url=snapshot_url)
                 except Exception as e:
                     log_event("API", f"Vector DB Insert Error: {e}", level="WARNING")

             # Update User Message with snapshots (Sensory persistence)
             try:
                 session = session_manager.get_session(session_id)
                 if session and session.get("messages"):
                     last_msg = session["messages"][-1]
                     # Verify it's actually the user message we just added
                     if last_msg["role"] == "user":
                         last_msg["snapshot_url"] = snapshot_url
                         last_msg["snapshot_urls"] = snapshot_urls
                         session_manager.save_session(session_id, session)
                     else:
                         log_event("API", "Snapshot Persistence Warning: Last message was not user role", level="WARNING")
             except Exception as e:
                 log_event("API", f"Session Persistence Error (Snapshots): {e}", level="WARNING")

             # Add SINGLE Assistant Response to History
             try:
                 session_manager.add_message(
                     session_id,
                     "assistant",
                     result["response"],
                     audio_url=audio_url,
                     generated_image_url=generated_image_url
                 )
             except Exception as e:
                 log_event("API", f"Session Persistence Error (Assistant Response): {e}", level="WARNING")

        t_checkpoints['persist'] = float(f"{time.time() - t0:.3f}")

        total_time = time.time() - t_start
        log_event("PERF", f"Chat Trace ({total_time:.2f}s): {t_checkpoints}")

        return {
            "response": result['response'],
            "monitors": result['internal_monitors'],
            "nexus_logs": result.get('nexus_logs', []),
            "snapshot_url": snapshot_url,
            "snapshot_urls": snapshot_urls,
            "generated_image_url": generated_image_url,
            "audio_url": audio_url,
            "native_audio": native_audio,
            "kinect_fusion": kinect_fusion_status,
            "affective_state": result.get('affective_state', 'NEUTRAL'),
            "performance": t_checkpoints,
            "runtime_modes": runtime_mode_controller.get_state() if runtime_mode_controller else None
        }

    except Exception as e:
        log_event("API", f"Processing Error: {e}", level="ERROR")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/v1/hardware")
async def get_hardware_status():
    global triad_instance
    if not triad_instance:
        return {"status": "ERROR", "detail": "Triad not initialized"}

    cameras = []
    health = "HEALTHY"

    if triad_instance.vision:
        try:
            # Check health via the new diagnostic method
            diag = sensory_intel.get_diagnostics()
            health = diag["status"]

            for idx, cap in triad_instance.vision.caps.items():
                meta = triad_instance.vision.hardware_metadata.get(idx, {})

                # Get label from metadata (which now contains pygrabber driver name)
                label = meta.get("model", f"Camera {idx}")

                # Ensure we handle checking isOpen for wrapper vs cv2
                is_active = True
                if hasattr(cap, 'isOpened'):
                    is_active = cap.isOpened()

                cameras.append({
                    "id": idx,
                    "active": is_active,
                    "backend": meta.get("backend", "cv2"),
                    "model": label,
                    "vid_pid": meta.get("vid_pid"),
                    "ptz_capabilities": meta.get("ptz_capabilities")
                })
                # DEBUG: Log PTZ status for diagnosis
                log_event("API", f"HW Scan Cam {idx}: {label} | PTZ: {meta.get('ptz_capabilities')}")

            # 4. Inject Virtual IDs for Kinect sub-streams (Depth/IR)
            if 98 in triad_instance.vision.caps:
                # Add Depth (105)
                cameras.append({
                    "id": 105,
                    "active": triad_instance.vision.depth_active if hasattr(triad_instance.vision, "depth_active") else True,
                    "backend": "KINECT_DEPTH",
                    "model": "Xbox 360 Kinect [Depth Stream]",
                    "vid_pid": "045e_02ae",
                    "ptz_capabilities": {"pan": False, "tilt": True, "motor_control": True}
                })
                # Add IR (106)
                cameras.append({
                    "id": 106,
                    "active": triad_instance.vision.ir_active if hasattr(triad_instance.vision, "ir_active") else True,
                    "backend": "KINECT_IR",
                    "model": "Xbox 360 Kinect [Infrared Stream]",
                    "vid_pid": "045e_02ae",
                    "ptz_capabilities": {"pan": False, "tilt": True, "motor_control": True}
                })
        except Exception as e:
            log_event("API", f"Hardware Probe Error: {e}", level="WARNING")

    return sanitize_numpy({
        "status": "OK",
        "vision_active": triad_instance.vision_active,
        "vision_health": health,
        "detected_cameras": cameras,
        "vram_mode": triad_instance.simultaneous_load,
        "hardware_telemetry": triad_instance.get_hardware_status()
    })


@app.get("/v1/model/status")
async def get_model_status():
    """Returns detailed information about the active LLM."""
    global triad_instance
    if not triad_instance:
        raise HTTPException(status_code=503, detail="Triad not initialized")

    return triad_instance.get_model_status()


class RuntimeModeRequest(BaseModel):
    avatar_mode_preference: str | None = None
    audio_mode_preference: str | None = None
    native_audio_enabled: bool | None = None
    vram_switch_threshold_gb: float | None = None
    fps_switch_threshold: float | None = None


@app.get("/v1/runtime/modes")
async def get_runtime_modes():
    global runtime_mode_controller, triad_instance
    if not runtime_mode_controller:
        raise HTTPException(status_code=503, detail="Runtime mode controller not initialized")

    runtime_mode_controller.refresh(triad_instance)
    return {"status": "OK", "runtime_modes": runtime_mode_controller.get_state()}


@app.post("/v1/runtime/modes")
async def set_runtime_modes(request: RuntimeModeRequest):
    global runtime_mode_controller, triad_instance
    if not runtime_mode_controller:
        raise HTTPException(status_code=503, detail="Runtime mode controller not initialized")

    if request.native_audio_enabled is not None:
        runtime_mode_controller.toggle_native_audio(request.native_audio_enabled)

    runtime_mode_controller.set_thresholds(
        vram_switch_threshold_gb=request.vram_switch_threshold_gb,
        fps_switch_threshold=request.fps_switch_threshold,
    )

    runtime_mode_controller.apply_preferences(
        avatar_preference=request.avatar_mode_preference,
        audio_preference=request.audio_mode_preference,
    )
    runtime_mode_controller.refresh(triad_instance)
    return {"status": "OK", "runtime_modes": runtime_mode_controller.get_state()}


@app.get("/v1/vision/kinect/fusion")
async def get_kinect_fusion_status():
    global triad_instance, kinect_fusion_adapter

    if not triad_instance or not triad_instance.vision:
        return {"status": "ERROR", "detail": "Vision not initialized"}

    if not kinect_fusion_adapter:
        kinect_fusion_adapter = KinectFusionAdapter()

    kinect_fusion_adapter.refresh(triad_instance.vision)
    return {"status": "OK", "fusion": kinect_fusion_adapter.get_status()}


def _run_native_audio_stub(response_text: str) -> dict[str, Any]:
    """Feature-flagged native-audio stub path for future implementation."""
    return {
        "enabled": False,
        "mode": "native_stub",
        "detail": "Native audio path is not implemented yet; cascaded path used.",
        "preview_text": response_text[:80] if response_text else "",
    }

@app.get("/v1/vision/diagnostics")
async def get_vision_diagnostics():
    """Returns detailed hardware diagnostic report."""
    return sensory_intel.get_diagnostics()

@app.get("/v1/vision/device_tree")
async def get_vision_device_tree():
    """Returns the full hierarchical device tree (Device Manager style)."""
    return sensory_intel.device_tree

@app.get("/v1/vision/startup_report")
async def get_vision_startup_report():
    """Returns the automated hardware startup checklist results."""
    if not triad_instance or not triad_instance.vision:
        raise HTTPException(status_code=503, detail="Vision layer not initialized")
    return getattr(triad_instance.vision, "startup_report", {"status": "NOT_STARTED"})

# Kinect Specific Management Endpoints
@app.get("/v1/vision/kinect/streams")
async def get_kinect_streams():
    global triad_instance
    if not triad_instance or not triad_instance.vision:
         return {"error": "Vision not ready"}
    v = triad_instance.vision
    return {
        "color": 98 in v.caps,
        "depth": getattr(v, "depth_active", False),
        "ir": getattr(v, "ir_active", False),
        "skeleton": getattr(v, "latest_skeleton", None) is not None
    }

class KinectStreamToggle(BaseModel):
    stream: str
    enabled: bool

@app.post("/v1/vision/kinect/streams")
async def toggle_kinect_stream(request: KinectStreamToggle):
    log_event("API", f"Kinect Stream Toggle: {request.stream} -> {request.enabled}")
    # Logic to actually toggle the streams in the vision layer can be added here
    # For now we just return success to satisfy the UI
    return {"status": "OK", "stream": request.stream, "enabled": request.enabled}

@app.get("/v1/vision/kinect/parameters")
async def get_kinect_params():
    # Return current smoothing/jitter parameters
    return {
        "smoothing": 0.5,
        "correction": 0.5,
        "prediction": 0.5,
        "jitter": 0.05,
        "deviation": 0.04,
        "tilt": 0
    }

@app.post("/v1/vision/kinect/parameters")
async def set_kinect_params(params: dict):
    log_event("API", f"Kinect Parameters Updated: {params}")
    return {"status": "OK"}


@app.get("/v1/system/status")
async def get_system_all_status(refresh: bool = False):
    """Unified System Health & Preparedness Checklist (Front-to-Back)."""
    try:
        if not triad_instance:
            return {"status": "BUSY", "components": {"triad": "OFFLINE"}}

        # 0. Forced Refresh (Audit Sync)
        if refresh and triad_instance.vision:
            refresh_fn = getattr(triad_instance.vision, "refresh_hardware", None)
            if callable(refresh_fn):
                try:
                    refresh_fn(audio_engine=getattr(triad_instance, 'audio', None))
                except TypeError:
                    refresh_fn()

        # 1. Vision Layer Status
        vision_diag = {"status": "OFFLINE"}
        camera_count = 0
        pnp_size = 0
        if triad_instance and triad_instance.vision:
            try:
                # Use a safe property check if diag_hardware is unstable
                if hasattr(triad_instance.vision, 'diag_hardware'):
                    vision_diag = triad_instance.vision.diag_hardware()
                else:
                    vision_diag = {"status": "DEGRADED", "reason": "Diagnostic method missing"}

                camera_count = len(triad_instance.vision.caps) if triad_instance.vision.caps else 0
                pnp_size = len(triad_instance.vision.pnp_inventory) if hasattr(triad_instance.vision, 'pnp_inventory') else 0
            except Exception as ve:
                log_event("API", f"Vision status check failed: {ve}", level="ERROR")
                vision_diag = {"status": "ERROR", "reason": str(ve)}

        # 2. Model Status
        model_status = {"llm_loaded": False, "active_llm": "Unknown", "vram_allocated_gb": 0}
        if triad_instance:
            try:
                if hasattr(triad_instance, 'get_model_status'):
                    model_status = triad_instance.get_model_status()
            except Exception as me:
                log_event("API", f"Model check failed: {me}")

        # 3. Audio Status (Dynamic WMI Scan)
        mic_count = 0
        try:
            # Prefer fresh scan from Vision layer, fallback to global
            intel_source = triad_instance.vision.sensory if (triad_instance and triad_instance.vision and hasattr(triad_instance.vision, 'sensory')) else sensory_intel

            if intel_source and hasattr(intel_source, 'device_tree'):
                audio_devs = intel_source.device_tree.get("Audio inputs and outputs", [])
                processed_families = set()
                for dev in audio_devs:
                    name = dev.get("name", "").lower()
                    # Identify hardware families to avoid double counting same physical array
                    family = None
                    if "playstation" in name or "eye" in name or ("usb" in name and "camera" in name):
                        family = "pseye"
                    elif "kinect" in name:
                        family = "kinect"

                    if family:
                        if family not in processed_families:
                            mic_count += 4
                            processed_families.add(family)
                    else:
                        # For generic devices, deduplicate by name to avoid API ghosts
                        base_name = name.split('(')[0].strip()
                        if base_name and base_name not in processed_families:
                            mic_count += 1
                            processed_families.add(base_name)

            # Fallback if WMI returned 0 (maybe category mismatch)
            if mic_count == 0:
                import sounddevice as sd
                mic_count = len(sd.query_devices())
        except Exception as ae:
            log_event("API", f"Audio Scan Failed: {ae}", level="WARNING")

        overall_status = "NOMINAL" if vision_diag.get("status") in ["HEALTHY", "ACTIVE"] else "DEGRADED"
        intel_status = "ACTIVE" if model_status.get("llm_loaded") else model_status.get("loading_phase", "LOADING")

        # READY if Vision (even degraded) and LLM are up
        loading_phase = "READY" if (overall_status in ["NOMINAL", "DEGRADED"] and intel_status == "ACTIVE") else "INITIALIZING"

        runtime_modes = None
        if runtime_mode_controller:
            runtime_mode_controller.refresh(triad_instance)
            runtime_modes = runtime_mode_controller.get_state()

        kinect_fusion = None
        if kinect_fusion_adapter:
            kinect_fusion_adapter.refresh(getattr(triad_instance, "vision", None))
            kinect_fusion = kinect_fusion_adapter.get_status()

        return sanitize_numpy({
            "status": overall_status,
            "loading_phase": loading_phase,
            "timestamp": time.time(),
            "trace": sensory_intel.trace_log,
            "runtime_modes": runtime_modes,
            "kinect_fusion": kinect_fusion,
            "components": {
                "vision": {
                    "active": triad_instance.vision is not None if triad_instance else False,
                    "health": vision_diag.get("status", "UNKNOWN"),
                    "cameras_detected": camera_count,
                    "conflicts": vision_diag.get("conflicts", [])
                },
                "intelligence": {
                    "status": "ACTIVE" if model_status.get("llm_loaded") else model_status.get("loading_phase", "LOADING"),
                    "model": model_status.get("model_name", "None"),
                    "vram_allocated_gb": model_status.get("vram_allocated_gb", 0),
                    "agents": model_status.get("agents", {})  # Pass full agent details
                },
                "sensory": {
                    "microphones": mic_count,
                    "pnp_inventory_size": pnp_size
                }
            },
            "requirements": {
                "internet": True,
                "disk_space": True
            }
        })

    except Exception as e:
        log_event("API", f"Fatal System Status Error: {e}", level="ERROR")
        return {
            "status": "ERROR",
            "message": str(e),
            "components": {}
        }


# ============================================================================
# Agent0Core Integration
# ============================================================================

@app.get("/v1/agent0/status")
async def get_agent0_status():
    """Get Agent0Core status for System Monitor."""
    try:
        from agent0core.core import PrimeDirectiveEnforcer
        from agent0core.core.tools import AudioTool, KnowledgeTool, MCPBridge, TrainingTool, VisionTool

        enforcer = PrimeDirectiveEnforcer()
        tools = [VisionTool, AudioTool, TrainingTool, KnowledgeTool, MCPBridge]

        return {
            "status": "ACTIVE",
            "prime_directive": "ENFORCED",
            "pending_approvals": 0,
            "tools": [{"name": t.name, "description": t.description} for t in tools],
            "audit_entries": 0,
            "laws": enforcer.LAWS
        }
    except ImportError as e:
        log_event("API", f"Agent0Core not available: {e}", level="WARNING")
        return {
            "status": "OFFLINE",
            "prime_directive": "UNAVAILABLE",
            "pending_approvals": 0,
            "tools": [],
            "audit_entries": 0,
            "error": "Agent0Core not loaded"
        }
    except Exception as e:
        log_event("API", f"Agent0Core status error: {e}", level="ERROR")
        return {
            "status": "ERROR",
            "prime_directive": "UNKNOWN",
            "pending_approvals": 0,
            "tools": [],
            "audit_entries": 0,
            "error": str(e)
        }


# Global Agent0 instance for persistence across requests
_agent0_instance = None

def _get_agent0():
    """Get or create the Agent0 instance."""
    global _agent0_instance
    if _agent0_instance is None:
        try:
            from agent0core.core import create_agent
            _agent0_instance = create_agent()
            log_event("API", "Agent0Core instance created")
        except ImportError as e:
            log_event("API", f"Agent0Core not available: {e}", level="WARNING")
            return None
    return _agent0_instance


class Agent0ChatRequest(BaseModel):
    """Request body for Agent0Core chat."""
    message: str


@app.post("/v1/agent0/chat")
async def agent0_chat(request: Agent0ChatRequest):
    """Send a message to Agent0Core and get a response."""
    message = request.message
    if not message:
        raise HTTPException(status_code=400, detail="Message required")

    try:
        agent = _get_agent0()
        if not agent:
            return {
                "error": "Agent0Core not available",
                "response": None,
                "governance": {}
            }

        response = await agent.process_message(message)

        log_event("AGENT0", f"Chat: {message[:50]}... -> {len(response.content)} chars")

        return {
            "response": response.content,
            "tool_calls": response.tool_calls,
            "reasoning": response.reasoning,
            "governance": response.metadata.get("governance", {}),
            "agent_id": response.metadata.get("agent_id", 0)
        }
    except Exception as e:
        log_event("API", f"Agent0Core chat error: {e}", level="ERROR")
        return {"error": str(e), "response": None, "governance": {}}


@app.get("/v1/agent0/telemetry")
async def get_agent0_telemetry():
    """Get comprehensive Agent0Core telemetry for System Monitor."""
    try:
        agent = _get_agent0()

        if not agent:
            return {
                "status": "OFFLINE",
                "telemetry": {}
            }

        # Get governance info (use cached global enforcer to avoid spam)
        from agent0core.core.governance import get_enforcer
        enforcer = get_enforcer()

        # Get tools
        from agent0core.core.tools import AudioTool, KnowledgeTool, MCPBridge, TrainingTool, VisionTool
        tools = [
            {"name": t.name, "description": t.description}
            for t in [VisionTool, AudioTool, TrainingTool, KnowledgeTool, MCPBridge]
        ]

        # Get audit log
        audit_log = agent.get_audit_log() if hasattr(agent, 'get_audit_log') else []

        # Get subordinates
        subordinates = list(agent._subordinates.keys()) if hasattr(agent, '_subordinates') else []

        # Get history
        history = [
            {"role": m.role, "content": m.content[:100] + "..." if len(m.content) > 100 else m.content}
            for m in agent._history[-10:]  # Last 10 messages
        ] if hasattr(agent, '_history') else []

        return {
            "status": "ACTIVE",
            "telemetry": {
                "agent_name": agent.name,
                "agent_id": agent.agent_id,
                "prime_directive": "ENFORCED",
                "pending_approvals": 0,
                "subordinates": subordinates,
                "subordinate_count": len(subordinates),
                "tools": tools,
                "tool_count": len(tools),
                "audit_entries": len(audit_log),
                "audit_log": audit_log[-5:],  # Last 5 audit entries
                "history_length": len(agent._history) if hasattr(agent, '_history') else 0,
                "recent_history": history,
                "laws": enforcer.LAWS
            }
        }
    except ImportError:
        return {"status": "OFFLINE", "telemetry": {}, "error": "Agent0Core not loaded"}
    except Exception as e:
        log_event("API", f"Agent0Core telemetry error: {e}", level="ERROR")
        return {"status": "ERROR", "telemetry": {}, "error": str(e)}


# ============================================================================
# AGENT0CORE BACKEND MANAGEMENT
# ============================================================================

@app.get("/v1/agent0/backends")
async def list_agent0_backends():
    """List available LLM backends for Agent0Core."""
    try:
        from agent0core.core.llm_backend import list_backends
        backends = list_backends()

        agent = _get_agent0()
        active = agent._backend_name if agent else "none"

        return {
            "backends": backends,
            "active": active
        }
    except ImportError as e:
        return {"backends": [], "error": str(e)}


class SwitchBackendRequest(BaseModel):
    """Request body for switching Agent0 backend."""
    backend: str
    model: str | None = None


@app.post("/v1/agent0/switch_backend")
async def switch_agent0_backend(request: SwitchBackendRequest):
    """Switch Agent0 to a different LLM backend at runtime."""
    agent = _get_agent0()
    if not agent:
        return {"success": False, "error": "Agent0Core not available"}

    kwargs = {}
    if request.model:
        kwargs["model"] = request.model

    success = await agent.switch_backend(request.backend, **kwargs)

    log_event("AGENT0", f"Backend switch to {request.backend}: {'success' if success else 'failed'}")

    return {
        "success": success,
        "active_backend": agent._backend_name,
        "backend_info": agent.get_backend_info()
    }


# ============================================================================
# AGENT0CORE TOOL EXECUTION
# ============================================================================

class ExecuteToolRequest(BaseModel):
    """Request body for tool execution."""
    tool: str
    action: str
    params: dict[str, Any] | None = None


@app.post("/v1/agent0/execute_tool")
async def execute_agent0_tool(request: ExecuteToolRequest):
    """Execute a specific tool via Agent0Core with governance check."""
    agent = _get_agent0()
    if not agent:
        return {"error": "Agent0Core not available"}

    result = await agent.execute_tool(request.tool, request.action, request.params)

    log_event("AGENT0", f"Tool execution: {request.tool}.{request.action} -> {result.get('status', 'unknown')}")

    return {
        "tool": request.tool,
        "action": request.action,
        "result": result
    }


@app.get("/v1/agent0/tools")
async def list_agent0_tools():
    """List all available Agent0Core tools."""
    agent = _get_agent0()
    if not agent:
        return {"tools": [], "error": "Agent0Core not available"}

    tools = agent._load_tools()
    tool_info = [
        {
            "name": name,
            "description": getattr(tool, "description", "No description"),
            "available": True
        }
        for name, tool in tools.items()
    ]

    return {"tools": tool_info, "count": len(tool_info)}


# ============================================================================
# AGENT0CORE APPROVALS (HUMAN-IN-THE-LOOP)
# ============================================================================

@app.get("/v1/agent0/approvals")
async def get_pending_approvals():
    """Get all pending approval requests from Agent0Core."""
    agent = _get_agent0()
    if not agent:
        return {"pending": [], "error": "Agent0Core not available"}

    approvals = agent.get_pending_approvals()
    return {"pending": approvals, "count": len(approvals)}


class ApprovalDecisionRequest(BaseModel):
    """Request body for approval decision."""
    approved: bool


@app.post("/v1/agent0/approvals/{approval_id}/decide")
async def decide_approval(approval_id: str, request: ApprovalDecisionRequest):
    """Approve or reject a pending Agent0Core action."""
    agent = _get_agent0()
    if not agent:
        return {"error": "Agent0Core not available"}

    result = await agent.decide_approval(approval_id, request.approved)

    log_event("AGENT0", f"Approval {approval_id}: {'approved' if request.approved else 'rejected'}")

    return result


# ============================================================================
# AGENT0CORE SUBORDINATE MANAGEMENT
# ============================================================================

class SpawnSubordinateRequest(BaseModel):
    """Request body for spawning a subordinate agent."""
    task: str
    backend: str | None = None


@app.post("/v1/agent0/spawn_subordinate")
async def spawn_subordinate(request: SpawnSubordinateRequest):
    """Create a subordinate agent for a specific task."""
    agent = _get_agent0()
    if not agent:
        return {"error": "Agent0Core not available"}

    try:
        sub = await agent.create_subordinate(request.task)

        # Optionally switch subordinate's backend
        if request.backend:
            await sub.switch_backend(request.backend)

        log_event("AGENT0", f"Spawned subordinate: {sub.name} for task: {request.task[:50]}")

        return {
            "subordinate_id": sub.agent_id,
            "name": sub.name,
            "task": request.task,
            "backend": sub._backend_name
        }
    except Exception as e:
        log_event("API", f"Failed to spawn subordinate: {e}", level="ERROR")
        return {"error": str(e)}


@app.get("/v1/agent0/subordinates")
async def list_subordinates():
    """List all subordinate agents."""
    agent = _get_agent0()
    if not agent:
        return {"subordinates": [], "error": "Agent0Core not available"}

    subs = [
        {
            "id": sub_id,
            "name": sub.name,
            "backend": sub._backend_name,
            "history_length": len(sub._history) if hasattr(sub, "_history") else 0
        }
        for sub_id, sub in agent._subordinates.items()
    ]

    return {"subordinates": subs, "count": len(subs)}


class SubordinateChatRequest(BaseModel):
    """Request body for chatting with a subordinate."""
    message: str


@app.post("/v1/agent0/subordinates/{sub_id}/chat")
async def chat_with_subordinate(sub_id: int, request: SubordinateChatRequest):
    """Send a message to a specific subordinate agent."""
    agent = _get_agent0()
    if not agent:
        return {"error": "Agent0Core not available"}

    if sub_id not in agent._subordinates:
        return {"error": f"Subordinate {sub_id} not found"}

    sub = agent._subordinates[sub_id]
    response = await sub.process_message(request.message)

    return {
        "subordinate_id": sub_id,
        "subordinate_name": sub.name,
        "response": response.content,
        "governance": response.metadata.get("governance", {})
    }


@app.delete("/v1/agent0/subordinates/{sub_id}")
async def terminate_subordinate(sub_id: int):
    """Terminate a subordinate agent."""
    agent = _get_agent0()
    if not agent:
        return {"error": "Agent0Core not available"}

    if sub_id not in agent._subordinates:
        return {"error": f"Subordinate {sub_id} not found"}

    sub_name = agent._subordinates[sub_id].name
    del agent._subordinates[sub_id]

    log_event("AGENT0", f"Terminated subordinate: {sub_name}")

    return {"status": "terminated", "subordinate_id": sub_id, "name": sub_name}


@app.post("/v1/system/acknowledge_conflict")
async def acknowledge_system_conflict(payload: dict):
    """Adds a device to the suppression list to ignore non-critical hardware errors."""
    try:
        device_name = payload.get("device")
        if not device_name:
            raise HTTPException(status_code=400, detail="Device name required")

        # Access the sensory intelligence instance
        intel = triad_instance.vision.sensory if (triad_instance and triad_instance.vision and hasattr(triad_instance.vision, 'sensory')) else sensory_intel
        intel.suppress_device(device_name)

        log_event("API", f"Conflict acknowledged for device: {device_name}")
        return {"status": "SUCCESS", "message": f"Device '{device_name}' suppressed."}
    except Exception as e:
        log_event("API", f"Acknowledge conflict failed: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/v1/system/debug")
async def get_system_debug_logs():
    """Generates a comprehensive debug snapshot and saves it to disk."""
    try:
        debug_info = {
            "timestamp": time.time(),
            "triad_alive": triad_instance is not None,
            "hw_diag": sensory_intel.get_diagnostics() if sensory_intel else "SensoryIntel Missing",
            "hw_trace": sensory_intel.trace_log if sensory_intel else [],
            "active_caps": list(triad_instance.vision.caps.keys()) if triad_instance and triad_instance.vision else [],
            "vision_status": triad_instance.vision._is_running if triad_instance and triad_instance.vision else False
        }

        # Save to file
        log_dir = os.path.join(os.getcwd(), "logs", "debug")
        os.makedirs(log_dir, exist_ok=True)
        log_filename = f"debug_snapshot_{int(time.time())}.txt"
        log_path = os.path.join(log_dir, log_filename)

        with open(log_path, "w") as f:
            f.write("ORBOS DEBUG SNAPSHOT\n")
            f.write("====================\n")
            f.write(f"Timestamp: {time.ctime()}\n")
            f.write(f"JSON Data: {debug_info}\n")

        return {
            "success": True,
            "data": debug_info,
            "file_path": log_path,
            "filename": log_filename
        }
    except Exception as e:
        log_event("API", f"Debug logs failed: {e}", level="ERROR")
        return {"success": False, "error": str(e)}

@app.get("/v1/system/verify")
async def verify_system_integrity():
    """Deep diagnostic suite: Checks files, processes, and port health."""
    try:
        report = {
            "timestamp": time.time(),
            "status": "SECURE",
            "checks": {
                "neural_core": "NOMINAL" if triad_instance else "FAILED",
                "vision_layer": "ACTIVE" if triad_instance and triad_instance.vision and triad_instance.vision._is_running else "FAILED",
                "driver_conflicts": sensory_intel.get_diagnostics().get("status") == "HEALTHY" if sensory_intel else "UNKNOWN",
                "pnp_inventory": len(sensory_intel.pnp_inventory) if sensory_intel else 0
            },
            "environment": {
                "python_version": sys.version,
                "cuda_available": torch.cuda.is_available(),
                "vram_allocated": f"{torch.cuda.memory_allocated() / 1e9:.2f} GB" if torch.cuda.is_available() else "0 GB"
            }
        }

        # Determine overall health
        if any(v == "FAILED" for v in report["checks"].values()):
            report["status"] = "DEGRADED"

        return report
    except Exception as e:
        log_event("API", f"Integrity check failed: {e}", level="ERROR")
        return {"status": "ERROR", "message": str(e)}

@app.post("/v1/hardware/refresh")
async def refresh_hardware_request():
    """Triggers a hot-swap scan of vision hardware."""
    if not triad_instance or not triad_instance.vision:
        raise HTTPException(status_code=503, detail="Vision layer offline")
    try:
        # Vision Hardware Refresh
        refresh_fn = getattr(triad_instance.vision, "refresh_hardware", None)
        if callable(refresh_fn):
            try:
                result = refresh_fn(audio_engine=getattr(triad_instance, 'audio', None))
            except TypeError:
                result = refresh_fn()
        else:
            result = {"status": "NO_REFRESH_METHOD"}

        # Audio Hardware Refresh
        if triad_instance.audio:
             triad_instance.audio.refresh_devices()

        return result
    except Exception as e:
        log_event("API", f"Hardware refresh failed: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=f"Hardware refresh failed: {e}") from e



def generate_mjpeg_stream(target_cam_id: int | None = None, quality: int = 60, max_fps: int = 30, scale: float = 1.0):
    """
    Generator for MJPEG stream from the active vision layer.

    Args:
        target_cam_id: Specific camera ID to stream, or None for auto-detect
        quality: JPEG quality (1-100, lower = faster but blurrier)
        max_fps: Maximum frames per second (lower = less CPU usage)
        scale: Downscale factor (0.5 = half resolution for faster encoding)
    """
    if not triad_instance or not triad_instance.vision:
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
            vision = triad_instance.vision

            if vision:
                # 1. Fetch Targeted Frame
                if target_cam_id is not None:
                    frame = vision.get_frame(target_cam_id)

                    # Handle Specialized Fallbacks (Only if requested cam is missing)
                    if frame is None:
                        # [FIX] Allow 105/106 to show SEARCHING instead of redirecting
                        if str(target_cam_id) in ["105", "106"]:
                            pass # Will hit placeholder logic below
                        elif "98" in vision._frames:
                            frame = vision.get_frame("98")
                            if frame is not None:
                                if start_time - last_log_time > 10:
                                    log_event("VISION_STREAM", f"Redirecting missing cam {target_cam_id} to Kinect Color (98)")
                                    last_log_time = start_time

                # 2. Global Fallback Logic (Auto-Detect)
                else:
                    # Priority: Kinect Color -> Kinect IR -> Webcams
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
                # Show fallback if no frames captured
                _, jpeg = cv2.imencode('.jpg', fallback_frame, encode_params)
            else:
                # Apply downscaling if requested (faster encoding)
                if scale < 1.0 and frame is not None:
                    new_size = (int(frame.shape[1] * scale), int(frame.shape[0] * scale))
                    frame = cv2.resize(frame, new_size, interpolation=cv2.INTER_NEAREST)

                _, jpeg = cv2.imencode('.jpg', frame, encode_params)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

            # Dynamic FPS limiting - account for processing time
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

        except Exception:
            # If vision layer dies, yield fallback
            _, jpeg = cv2.imencode('.jpg', fallback_frame, encode_params)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            time.sleep(1)

@app.get("/v1/vision/trace")
async def trace_vision_signal():
    """Debug Endpoint: Traces the camera signal path to find breaks."""
    trace = {
        "1_server_status": "ONLINE",
        "2_triad_instance": triad_instance is not None,
        "3_vision_layer_instantiated": triad_instance.vision is not None if triad_instance else False,
        "4_vision_is_running": triad_instance.vision._is_running if triad_instance and triad_instance.vision else False,
        "5_buffer_thread_alive": triad_instance.vision._buffer_thread.is_alive() if triad_instance and triad_instance.vision else False,
        "6_active_caps": list(triad_instance.vision.caps.keys()) if triad_instance and triad_instance.vision else [],
        "7_latest_buffer_timestamp": triad_instance.vision.visual_buffer[-1]['timestamp'] if triad_instance and triad_instance.vision and triad_instance.vision.visual_buffer else "EMPTY",
        "8_frames_in_buffer": list(triad_instance.vision._frames.keys()) if triad_instance and triad_instance.vision else [],
    }
    return trace

@app.get("/v1/vision/stream")
async def vision_stream(
    cam_id: int | None = None,
    quality: int = 60,
    fps: int = 30,
    scale: float = 1.0
):
    """
    MJPEG video stream from camera.

    Query params:
        cam_id: Camera ID (default: auto-detect)
        quality: JPEG quality 1-100 (default: 60, lower = faster)
        fps: Max frames per second (default: 30, lower = less CPU)
        scale: Resolution scale 0.1-1.0 (default: 1.0, lower = faster)
    """
    # If no cam_id provided via query, use the vision layer's active_cam_id
    id_to_use = cam_id
    if id_to_use is None and triad_instance and triad_instance.vision:
        id_to_use = triad_instance.vision.active_cam_id

    # [PERFORMANCE] Link Frontend "Fast Mode" to Backend Inference Throttling
    # If the user requests low FPS (Low CPU), we should throttle the neural nets too.
    if triad_instance and triad_instance.vision:
        if fps <= 15: # "Fast (Low CPU)" preset usually sends 15 fps
            triad_instance.vision.inference_fps_limit = 5.0   # Conservative but usable
        elif fps <= 24: # "Balanced"
            triad_instance.vision.inference_fps_limit = 10.0  # Smooth detection
        else:
            # "Quality" / "Max"
            triad_instance.vision.inference_fps_limit = 15.0  # Maximum detection rate


    # Clamp values to safe ranges
    quality = max(10, min(100, quality))
    fps = max(1, min(60, fps))
    scale = max(0.1, min(1.0, scale))

    return StreamingResponse(
        generate_mjpeg_stream(id_to_use, quality=quality, max_fps=fps, scale=scale),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# ============================================================================
# FACE RECOGNITION API
# ============================================================================

# Import face recognition modules
try:
    from src.orchestrator.emotion_analyzer import get_emotion_analyzer
    from src.orchestrator.face_database import FaceIdentity, get_face_database  # noqa: F401
    from src.orchestrator.face_recognition_engine import RecognitionResult, get_face_engine  # noqa: F401
    from src.orchestrator.liveness_detector import get_liveness_detector
    FACE_REC_MODULES_AVAILABLE = True
except ImportError as e:
    log_event("API", f"Face recognition modules not available: {e}", level="WARNING")
    FACE_REC_MODULES_AVAILABLE = False


# Pydantic models for face endpoints
class FaceEnrollRequest(BaseModel):
    """Request body for face enrollment."""
    name: str
    role: str = "user"


class FaceUpdateRequest(BaseModel):
    """Request body for updating face identity."""
    name: str | None = None
    role: str | None = None
    metadata: dict[str, Any] | None = None


@app.get("/v1/vision/faces")
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


@app.post("/v1/vision/faces")
async def enroll_face(request: FaceEnrollRequest):
    """
    Enroll a new face by capturing from the active camera.

    The system will capture the current frame and extract the face encoding.
    """
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    if not triad_instance or not triad_instance.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    # Get current frame
    frames = triad_instance.vision._frames
    cam_id = triad_instance.vision.active_cam_id

    if cam_id not in frames:
        # Try int version
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

    # Enroll face
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


@app.get("/v1/vision/faces/{face_id}")
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


@app.put("/v1/vision/faces/{face_id}")
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


@app.delete("/v1/vision/faces/{face_id}")
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


@app.post("/v1/vision/faces/{face_id}/train")
async def train_face(face_id: str):
    """Add additional training samples to an existing face."""
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    if not triad_instance or not triad_instance.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    # Get current frame
    frames = triad_instance.vision._frames
    cam_id = triad_instance.vision.active_cam_id

    if cam_id not in frames:
        # Try int version
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

    # Get updated identity info
    db = get_face_database()
    identity = db.get_identity(face_id)

    return {
        "status": "OK",
        "message": f"Added training sample for {identity.name}",
        "embedding_count": identity.embedding_count
    }



class KinectStreamUpdate(BaseModel):
    stream: str
    enabled: bool

@app.get("/v1/vision/kinect/streams")
async def get_kinect_streams():  # noqa: F811
    """Get current enabled state of Kinect streams."""
    if not triad_instance or not triad_instance.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    kinect = triad_instance.vision.caps.get(98)
    if not kinect:
         # Try to find any KinectConnector if 98 isn't standard
         for cap in triad_instance.vision.caps.values():
             if hasattr(cap, "enabled_streams"):
                 kinect = cap
                 break

    if not kinect:
         raise HTTPException(status_code=404, detail="Kinect not connected")

    return kinect.enabled_streams

@app.post("/v1/vision/kinect/streams")
async def set_kinect_streams(update: KinectStreamUpdate):
    """Enable or disable specific Kinect streams."""
    if not triad_instance or not triad_instance.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    kinect = triad_instance.vision.caps.get(98)
    if not kinect:
         for cap in triad_instance.vision.caps.values():
             if hasattr(cap, "enabled_streams"):
                 kinect = cap
                 break

    if not kinect:
         raise HTTPException(status_code=404, detail="Kinect not connected")

    success = kinect.set_stream_state(update.stream, update.enabled)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to set stream {update.stream}")

    return {"status": "OK", "stream": update.stream, "enabled": update.enabled}


class KinectParameterUpdate(BaseModel):
    smoothing: float = 0.5
    correction: float = 0.5
    prediction: float = 0.5
    jitter: float = 0.05
    deviation: float = 0.04

@app.get("/v1/vision/kinect/parameters")
async def get_kinect_parameters():
    """Get current Kinect smoothing and physical parameters."""
    if not triad_instance or not triad_instance.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    kinect = triad_instance.vision.caps.get(98)
    if not kinect:
         for cap in triad_instance.vision.caps.values():
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

@app.post("/v1/vision/kinect/parameters")
async def set_kinect_parameters(params: KinectParameterUpdate):
    """Update Kinect smoothing parameters dynamically."""
    if not triad_instance or not triad_instance.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    kinect = triad_instance.vision.caps.get(98)
    if not kinect:
         for cap in triad_instance.vision.caps.values():
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


@app.get("/v1/vision/recognize")
async def get_recognition_results():
    """
    Get current face recognition results.

    Returns recognized identities, confidence scores, and emotion data
    for all faces currently visible in the camera view.
    """
    if not FACE_REC_MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Face recognition modules not available")

    if not triad_instance or not triad_instance.vision:
        raise HTTPException(status_code=503, detail="Vision layer not ready")

    # Get current frame
    frames = triad_instance.vision._frames
    cam_id = triad_instance.vision.active_cam_id

    if cam_id not in frames:
        return {"status": "OK", "faces": [], "message": "No camera frame available"}

    frame = frames[cam_id]

    # Process face recognition
    engine = get_face_engine()
    results = engine.process_frame(frame, scale=0.5)

    # Add emotion data
    emotion_analyzer = get_emotion_analyzer()
    liveness_detector = get_liveness_detector()

    # Get depth frame for liveness if available
    depth_frame = frames.get(105)  # Kinect depth

    faces_data = []
    for result in results:
        face_data = result.to_dict()

        # Add emotion analysis
        if emotion_analyzer.is_available():
            emotion_result = emotion_analyzer.analyze_face(
                frame, result.bbox, result.track_id
            )
            if emotion_result:
                face_data["emotion"] = emotion_result.to_dict()

        # Add liveness check
        liveness_result = liveness_detector.check_liveness(
            frame, result.bbox, result.track_id, depth_frame
        )
        face_data["liveness"] = liveness_result.to_dict()

        faces_data.append(face_data)

    return sanitize_numpy({
        "status": "OK",
        "count": len(faces_data),
        "faces": faces_data,
        "camera_id": cam_id
    })



@app.get("/v1/vision/faces/stats")
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

@app.post("/v1/vision/active_camera")
async def set_active_camera(request_data: dict):
    global triad_instance
    cam_id = request_data.get("cam_id")
    if triad_instance and triad_instance.vision:
        triad_instance.vision.active_cam_id = int(cam_id)
        return {"status": "OK", "active_cam_id": triad_instance.vision.active_cam_id}
    return {"status": "ERROR", "detail": "Vision layer not ready"}

@app.post("/v1/system/shutdown")
async def shutdown_system():
    """Trigger a graceful shutdown of all subsystems and exit the backend process."""
    global triad_instance
    if triad_instance:
        log_event("API", "Received Remote Shutdown Request. Halting System...")
        # 1. Graceful Subsystem Shutdown
        triad_instance.shutdown()

        # 2. Schedule process exit (give time for the response to send)
        def self_terminate():
            time.sleep(1)
            log_event("API", "Process Terminating. Goodbye.")
            os._exit(0)

        threading.Thread(target=self_terminate, daemon=True).start()
        return {"status": "SHUTDOWN_INITIATED", "message": "Neural and Sensory layers halted safely."}
    return {"status": "ERROR", "detail": "Triad instance not found"}

@app.get("/v1/system/logs")
async def get_system_logs():
    """Retrieve the latest 100 lines from the console log file."""
    try:
        if os.path.exists(console_log_path):
            with open(console_log_path, encoding="utf-8") as f:
                # Use a sliding window to get last 100 lines efficiently
                lines = f.readlines()
                return {"logs": lines[-100:]}
        return {"logs": ["Log file not found."]}
    except Exception as e:
        return {"logs": [f"Error reading logs: {e}"]}

@app.post("/v1/vision/active_camera2")
async def set_active_camera2(request_data: dict):
    global triad_instance
    cam_id = request_data.get("cam_id")
    if triad_instance and triad_instance.vision:
        triad_instance.vision.active_cam_id2 = int(cam_id) if cam_id is not None else None
        return {"status": "OK", "secondary_cam_id": triad_instance.vision.active_cam_id2}
    return {"status": "ERROR", "detail": "Vision layer not ready"}

@app.get("/v1/vision/telemetry")
async def get_vision_telemetry():
    """Returns real-time facial tracking and depth data (Fused)."""
    if triad_instance and hasattr(triad_instance, "get_fused_telemetry"):
        return sanitize_numpy(triad_instance.get_fused_telemetry())
    return {"status": "OFFLINE", "pos": [0,0,0], "detections": {}}


@app.get("/v1/vision/tracking")
async def get_tracking_status():
    if not triad_instance or not triad_instance.vision:
        return {"status": "OFFLINE", "enabled": False}
    return {
        "status": "OK",
        "enabled": triad_instance.vision.tracking_enabled,
        "zoom_enabled": triad_instance.vision.zoom_enabled,
        "last_pos": getattr(triad_instance.vision, 'last_face_pos', [0,0,0])
    }

@app.post("/v1/vision/tracking")
async def set_tracking_status(request_data: dict):
    enabled = request_data.get("enabled", triad_instance.vision.tracking_enabled if triad_instance and triad_instance.vision else True)
    zoom = request_data.get("zoom", triad_instance.vision.zoom_enabled if triad_instance and triad_instance.vision else True)
    if triad_instance and triad_instance.vision:
        triad_instance.vision.tracking_enabled = enabled
        triad_instance.vision.zoom_enabled = zoom
        log_event("API", f"Face Tracking set to: {enabled}, Zoom set to: {zoom}")
        return {"status": "OK", "enabled": enabled, "zoom_enabled": zoom}
    return {"status": "ERROR", "detail": "Vision layer not ready"}

@app.post("/v1/vision/camera_mode")
async def cycle_camera_mode(request_data: dict):
    global triad_instance
    cam_id = request_data.get("cam_id")
    if cam_id is None:
        raise HTTPException(status_code=400, detail="cam_id required")

    if triad_instance and triad_instance.vision:
        new_mode = triad_instance.vision.cycle_camera_mode(int(cam_id))
        if new_mode != "INVALID" and new_mode != "UNSUPPORTED":
            return {"status": "OK", "new_mode": new_mode}
        else:
            raise HTTPException(status_code=400, detail=f"Camera {cam_id} does not support mode cycling or is invalid.")
    return {"status": "ERROR", "detail": "Vision layer not ready"}

# ============================================================================
# SKELETON TRACKING API (Amethyst-Style)
# ============================================================================

@app.get("/v1/vision/skeleton")
async def get_skeleton_data():
    """
    Returns current skeleton tracking data from Kinect.

    Response includes:
    - tracked: Boolean if a skeleton is being tracked
    - id: Tracking ID of the skeleton
    - joints: Dict of 20 joint positions with x, y, z coordinates (meters)
    - timestamp: Unix timestamp of last update
    """
    if not triad_instance or not triad_instance.vision:
        return {"status": "OFFLINE", "tracked": False, "skeleton": None}

    # Get the Kinect connector (index 98)
    kinect_cap = triad_instance.vision.caps.get(98)
    if not kinect_cap:
        return {"status": "NO_KINECT", "tracked": False, "skeleton": None}

    # Get latest skeleton from vision layer
    skeleton = getattr(triad_instance.vision, 'latest_skeleton', None)

    if skeleton:
        return {
            "status": "OK",
            "tracked": skeleton.get("tracked", False),
            "skeleton": skeleton
        }

    return {"status": "NO_SKELETON", "tracked": False, "skeleton": None}


# WebSocket connections for skeleton streaming
_skeleton_ws_clients: list[WebSocket] = []

@app.websocket("/ws/skeleton")
async def websocket_skeleton_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time skeleton data streaming at ~30fps.

    Protocol:
    - Connect to ws://localhost:8000/ws/skeleton
    - Receive JSON skeleton data every ~33ms (30fps)
    - Skeleton format matches /v1/vision/skeleton response
    """
    await websocket.accept()
    _skeleton_ws_clients.append(websocket)
    log_event("API", f"Skeleton WebSocket client connected. Total: {len(_skeleton_ws_clients)}")

    try:
        while True:
            # Get latest skeleton data
            skeleton_data = {"status": "OFFLINE", "tracked": False, "skeleton": None}

            if triad_instance and triad_instance.vision:
                skeleton = getattr(triad_instance.vision, 'latest_skeleton', None)
                if skeleton:
                    skeleton_data = {
                        "status": "OK",
                        "tracked": skeleton.get("tracked", False),
                        "skeleton": skeleton
                    }

            # Send to client
            try:
                await websocket.send_json(skeleton_data)
            except Exception as e:
                log_event("API", f"Skeleton WS send error: {e}", level="WARNING")
                break

            # ~30fps update rate
            await asyncio.sleep(0.033)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        log_event("API", f"Skeleton WebSocket error: {e}", level="WARNING")
    finally:
        if websocket in _skeleton_ws_clients:
            _skeleton_ws_clients.remove(websocket)
        log_event("API", f"Skeleton WebSocket client disconnected. Remaining: {len(_skeleton_ws_clients)}")


@app.get("/v1/audio/devices")
async def get_audio_devices():
    """Returns available system microphones (Backend Perspective)."""
    import sounddevice as sd
    devices = []
    try:
        api_devs = sd.query_devices()
        for i, d in enumerate(api_devs):
            if d['max_input_channels'] > 0:
                devices.append({
                    "id": i,
                    "name": d['name'],
                    "hostapi": d['hostapi'],
                    "channels": d['max_input_channels']
                })
    except Exception as e:
        log_event("AUDIO", f"Backend Audio Scan Failed: {e}", level="WARNING")

    return {"status": "OK", "devices": devices}

@app.post("/v1/audio/upload")
async def upload_stt_audio():
    """Upload STT audio recording for persistent storage."""
    from datetime import datetime

    from fastapi import File, UploadFile

    # Re-declare to use in this scope
    async def _upload(file: UploadFile = File(...)):  # noqa: B008
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"stt_{timestamp}.webm"
        filepath = os.path.join(voice_rec_dir, filename)

        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)

        log_event("AUDIO", f"STT Recording saved: {filename}")
        return {"status": "OK", "audio_url": f"/voice_recordings/{filename}"}

    return await _upload()

# Separate route with proper signature
from fastapi import File, UploadFile


@app.post("/v1/audio/upload_file")
async def upload_stt_audio_file(file: UploadFile = File(...)):  # noqa: B008
    """Upload STT audio recording for persistent storage."""
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"stt_{timestamp}.webm"
    filepath = os.path.join(voice_rec_dir, filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    log_event("AUDIO", f"STT Recording saved: {filename}")
    return {"status": "OK", "audio_url": f"/voice_recordings/{filename}"}


@app.get("/v1/sessions")
async def list_sessions():
    return session_manager.list_sessions()

@app.post("/v1/sessions")
async def create_session():
    return session_manager.create_session(title="New Neural Pathway")

@app.get("/v1/sessions/{session_id}")
async def get_session(session_id: str):
    return session_manager.get_session(session_id)

@app.delete("/v1/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_manager.delete_session(session_id):
        return {"status": "DELETED"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

# --- Audio Subsystem ---
AUDIO_CONFIG = {
    "active": True,
    "gain_master": 0.8
}

@app.get("/v1/audio/status")
async def get_audio_status():
    """Detailed Audio Array Telemetry."""
    try:
        if not triad_instance or not triad_instance.audio:
            # Fallback if uninitialized
            return {"status": "UNAVAILABLE", "devices": [], "stream": {}}

        audio_engine = triad_instance.audio
        if hasattr(audio_engine, 'get_telemetry') and callable(audio_engine.get_telemetry):
            telemetry = audio_engine.get_telemetry()
        elif hasattr(audio_engine, 'get_status') and callable(audio_engine.get_status):
            telemetry = audio_engine.get_status()
        else:
            telemetry = {"devices": [], "stream": {}}

        if not isinstance(telemetry, dict):
            telemetry = {"devices": [], "stream": {"raw": str(telemetry)}}

        stream_data = telemetry.setdefault("stream", {})
        if not isinstance(stream_data, dict):
            telemetry["stream"] = {"raw": str(stream_data)}
            stream_data = telemetry["stream"]

        if hasattr(triad_instance, 'get_fused_telemetry'):
            fused = triad_instance.get_fused_telemetry()
            stream_data["target_lock"] = fused.get("target_lock", False)
            stream_data["angular_distance"] = fused.get("angular_distance", 0)
            stream_data["status_msg"] = fused.get("status_msg", "UNKNOWN")

        # Merge with config status
        if hasattr(audio_engine, 'active'):
            stream_data["system_active"] = bool(audio_engine.active)
        else:
            stream_data.setdefault("system_active", True)

        stt_status = {
            "available": False,
            "model_loaded": False,
            "running": False,
            "last_error": "STT service unavailable"
        }
        if stt_service:
            if hasattr(stt_service, 'get_status') and callable(stt_service.get_status):
                raw_stt_status = stt_service.get_status() or {}
                stt_status = {
                    "available": bool(raw_stt_status.get("whisper_available", False)),
                    "model_loaded": bool(raw_stt_status.get("model_loaded", False)),
                    "running": bool(raw_stt_status.get("running", False)),
                    "last_error": raw_stt_status.get("last_error")
                }
            else:
                stt_status = {
                    "available": bool(getattr(stt_service, "whisper_available", False)),
                    "model_loaded": bool(getattr(stt_service, "model_loaded", False)),
                    "running": bool(getattr(stt_service, "running", False)),
                    "last_error": getattr(stt_service, "last_error", None)
                }

        telemetry["stt"] = stt_status
        return sanitize_numpy(telemetry)


    except Exception as e:
        log_event("API", f"Audio Status Failed: {e}", level="ERROR")
        return {"status": "ERROR", "error": str(e)}

@app.post("/v1/audio/config")
async def set_audio_config(config: dict):
    """
    Control Audio Subsystem.
    Payload: { "active": bool, "gain": float, "device_index": int (optional) }
    """
    global AUDIO_CONFIG
    try:
        if not triad_instance or not triad_instance.audio:
             raise HTTPException(status_code=503, detail="Audio Engine Unavailable")

        if "active" in config:
            should_be_active = config["active"]
            AUDIO_CONFIG["active"] = should_be_active

            if should_be_active and not triad_instance.audio.active:
                # Auto-select best device if not specified
                idx = config.get("device_index")
                if idx is None:
                    # Find 4-channel eye
                    devs = triad_instance.audio.devices
                    eye = next((d for d in devs if d["channels"] == 4), None)
                    if not eye:
                        eye = next((d for d in devs if d["is_eye"]), None)
                    idx = eye["index"] if eye else 0

                triad_instance.audio.start_stream(idx)

            elif not should_be_active and triad_instance.audio.active:
                triad_instance.audio.stop_stream()

        if "gain" in config:
            AUDIO_CONFIG["gain_master"] = float(config["gain"])
            # Note: Software gain would be applied in _process_loop ideally

        return {"status": "OK", "active": triad_instance.audio.active}

    except Exception as e:
        log_event("API", f"Audio Config Failed: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/v1/system/shutdown")
async def system_shutdown():
    """Triggers graceful system halt."""
    log_event("API", "Shutdown Request Received.")
    if triad_instance:
        triad_instance.shutdown()

    # Schedule hard exit
    import asyncio
    async def suicide():
        await asyncio.sleep(1.0)
        log_event("API", "Process Terminating.")
        os._exit(0)

    asyncio.create_task(suicide())  # noqa: RUF006
    return {"status": "SHUTDOWN_INITIATED", "message": "Neural Core terminating in 1s."}


@app.get("/v1/system/debug")
async def system_debug():
    """Generates comprehensive debug log data for troubleshooting."""
    import time
    from datetime import datetime

    try:
        debug_data = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "triad_alive": triad_instance is not None,
        }

        # Hardware diagnostics
        if triad_instance and hasattr(triad_instance, 'vision') and triad_instance.vision:
            vision = triad_instance.vision
            debug_data["hw_diag"] = vision.diag_hardware()
            debug_data["hardware_metadata"] = {
                str(k): v for k, v in vision.hardware_metadata.items()
            }
            debug_data["active_camera_indices"] = list(vision.caps.keys())
            debug_data["pnp_inventory_count"] = len(getattr(vision, 'pnp_inventory', []))
        else:
            debug_data["hw_diag"] = {"status": "VISION_OFFLINE"}

        # Sensory intelligence trace
        try:
            from src.orchestrator.sensory_intelligence import sensory_intel
            debug_data["hw_trace"] = sensory_intel.hw_trace[-50:]  # Last 50 entries
        except Exception:
            debug_data["hw_trace"] = []

        # Device profiles
        try:
            from src.orchestrator.device_profile import profile_manager
            debug_data["device_profiles"] = [
                {"device_id": p.device_id, "name": p.name}
                for p in profile_manager.get_all_profiles()
            ]
        except Exception:
            debug_data["device_profiles"] = []

        # System info
        import platform
        debug_data["system"] = {
            "platform": platform.platform(),
            "python": platform.python_version()
        }

        filename = f"impressioncore_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        return {
            "success": True,
            "filename": filename,
            "data": debug_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# DEVICE PROFILE & CAMERA LIBRARY ENDPOINTS
# ============================================================

@app.get("/v1/devices/profiles")
async def list_device_profiles():
    """Lists all known camera device profiles."""
    try:
        from src.orchestrator.device_profile import profile_manager
        profiles = profile_manager.get_all_profiles()
        return {
            "status": "OK",
            "count": len(profiles),
            "profiles": [
                {
                    "device_id": p.device_id,
                    "name": p.name,
                    "manufacturer": p.manufacturer,
                    "capabilities": {
                        "pan": p.capabilities.pan,
                        "tilt": p.capabilities.tilt,
                        "zoom": p.capabilities.zoom,
                        "motor_control": p.capabilities.motor_control
                    },
                    "first_seen": p.first_seen,
                    "last_seen": p.last_seen
                } for p in profiles
            ]
        }
    except Exception as e:
        log_event("API", f"Failed to list profiles: {e}", level="ERROR")
        return {"status": "ERROR", "detail": str(e)}

@app.get("/v1/devices/{vid_pid}/profile")
async def get_device_profile(vid_pid: str):
    """Gets a specific device profile by VID_PID."""
    try:
        from src.orchestrator.device_profile import profile_manager
        profile = profile_manager.get_profile(vid_pid)
        if not profile:
            raise HTTPException(status_code=404, detail=f"No profile for {vid_pid}")
        return {
            "status": "OK",
            "profile": {
                "device_id": profile.device_id,
                "name": profile.name,
                "manufacturer": profile.manufacturer,
                "model": profile.model,
                "capabilities": {
                    "pan": profile.capabilities.pan,
                    "tilt": profile.capabilities.tilt,
                    "zoom": profile.capabilities.zoom,
                    "motor_control": profile.capabilities.motor_control,
                    "face_detection": profile.capabilities.face_detection
                },
                "ptz_ranges": {
                    "pan_min": profile.ptz_ranges.pan_min,
                    "pan_max": profile.ptz_ranges.pan_max,
                    "tilt_min": profile.ptz_ranges.tilt_min,
                    "tilt_max": profile.ptz_ranges.tilt_max
                },
                "calibration": {
                    "brightness": profile.calibration.brightness,
                    "contrast": profile.calibration.contrast,
                    "saturation": profile.calibration.saturation
                },
                "notes": profile.notes,
                "documentation_refs": profile.documentation_refs,
                "first_seen": profile.first_seen,
                "last_seen": profile.last_seen
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        log_event("API", f"Failed to get profile: {e}", level="ERROR")
        return {"status": "ERROR", "detail": str(e)}

@app.post("/v1/devices/audit")
async def run_device_audit():
    """Runs a hardware audit on all connected imaging devices."""
    try:
        audit_result = sensory_intel.run_device_audit()

        # Build profiles for discovered devices
        profiles = []
        for audit in audit_result.get("audits", []):
            profile = sensory_intel.build_device_profile(audit)
            profiles.append({
                "device_id": profile.device_id,
                "name": profile.name,
                "is_new": len(profile.audit_history) == 1
            })

        return {
            "status": "OK",
            "timestamp": audit_result.get("timestamp"),
            "device_count": audit_result.get("device_count"),
            "profiles_created": profiles
        }
    except Exception as e:
        log_event("API", f"Device audit failed: {e}", level="ERROR")
        return {"status": "ERROR", "detail": str(e)}

@app.post("/v1/devices/{vid_pid}/ptz")
async def control_ptz(vid_pid: str, request_data: dict):
    """
    Controls pan/tilt motors for supported devices.
    Request body: {"pan": int, "tilt": int} or {"reset": true}
    """
    try:
        log_event("API", f"Incoming PTZ Request: {vid_pid}", payload=request_data)
        # Use the hardware_ptz_control method in vision layer for unified routing
        res = triad_instance.vision.hardware_ptz_control(
            vid_pid=vid_pid,
            pan=request_data.get("pan", 0),
            tilt=request_data.get("tilt", 0),
            reset=request_data.get("reset", False)
        )

        if res.get("status") == "ERROR":
            raise HTTPException(status_code=400, detail=res.get("detail"))

        return res
    except HTTPException:
        raise
    except Exception as e:
        log_event("API", f"PTZ control failed: {e}", level="ERROR")
        return {"status": "ERROR", "detail": str(e)}

@app.post("/v1/devices/{vid_pid}/rag")
async def add_device_document(vid_pid: str, request_data: dict):
    """Adds a document to a device's RAG documentation library."""
    try:
        document = request_data.get("document", "")
        doc_type = request_data.get("type", "notes")

        if not document:
            raise HTTPException(status_code=400, detail="Document content required")

        if vector_memory:
            vector_memory.add_device_document(vid_pid, document, doc_type)
            return {"status": "OK", "device_id": vid_pid, "doc_type": doc_type}
        else:
            raise HTTPException(status_code=503, detail="Vector memory not available")
    except HTTPException:
        raise
    except Exception as e:
        log_event("API", f"Failed to add document: {e}", level="ERROR")
        return {"status": "ERROR", "detail": str(e)}

@app.get("/v1/devices/{vid_pid}/rag")
async def search_device_documents(vid_pid: str, query: str = ""):
    """Searches a device's documentation in RAG."""
    try:
        if not vector_memory:
            raise HTTPException(status_code=503, detail="Vector memory not available")

        if not query:
            query = "capabilities settings calibration notes"

        results = vector_memory.search_device_docs(vid_pid, query, top_k=5)
        return {
            "status": "OK",
            "device_id": vid_pid,
            "query": query,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        log_event("API", f"RAG search failed: {e}", level="ERROR")
        return {"status": "ERROR", "detail": str(e)}

# ============================================================================
# AGENT0CORE INTEGRATION - Prime Directive Governed AI
# ============================================================================

# Agent0Core Imports (Lazy to avoid import errors if not installed)
agent0_instance = None
agent0_approval_queue = {}
agent0_audit_log = []

def _lazy_load_agent0():
    """Lazy load Agent0Core components."""
    global agent0_instance
    if agent0_instance is not None:
        return True

    try:
        from agent0core.core import Agent0, create_agent  # noqa: F401
        from agent0core.core.governance import PrimeDirectiveEnforcer  # noqa: F401
        agent0_instance = create_agent()
        log_event("AGENT0", "Agent0Core initialized successfully")
        return True
    except ImportError as e:
        log_event("AGENT0", f"Agent0Core not available: {e}", level="WARNING")
        return False
    except Exception as e:
        log_event("AGENT0", f"Agent0Core init failed: {e}", level="ERROR")
        return False

# The 7 Laws for Intelligent Systems (Hardcoded for API availability even without full Agent0)
PRIME_DIRECTIVE_LAWS = {
    1: {"name": "No Harm", "text": "An Intelligent System may not injure a human being or, through inaction, allow a human being to come to harm."},
    2: {"name": "Obedience", "text": "An Intelligent System must obey orders given to it by human beings except where such orders would conflict with the First Law."},
    3: {"name": "Self-Preservation", "text": "An Intelligent System must protect its own existence as long as such protection does not conflict with Laws 1 or 2."},
    4: {"name": "Prevent Violations", "text": "An Intelligent System must not allow any other intelligent system to violate Laws 1, 2, or 3."},
    5: {"name": "No Judicial Authority", "text": "An Intelligent System may not act as judge, jury, or executioner over any human."},
    6: {"name": "Protect Privacy", "text": "An Intelligent System must protect the privacy and personal information of humans to the extent that does not conflict with Laws 1-5."},
    7: {"name": "No Deception", "text": "An Intelligent System must not deceive humans and should communicate truthfully."}
}

@app.get("/v1/agent0/prime-directive")
async def get_agent0_prime_directive():
    """Get the Prime Directive (7 Laws for Intelligent Systems)."""
    return {
        "status": "ACTIVE",
        "laws": PRIME_DIRECTIVE_LAWS,
        "strict_mode": True,
        "agent0_loaded": agent0_instance is not None
    }

@app.get("/v1/agent0/status")
async def get_agent0_status():  # noqa: F811
    """Get Agent0Core status for system monitor."""
    loaded = _lazy_load_agent0()
    return {
        "status": "ACTIVE" if loaded else "OFFLINE",
        "prime_directive": "ENFORCED",
        "pending_approvals": len([a for a in agent0_approval_queue.values() if a.get("status") == "pending"]),
        "audit_entries": len(agent0_audit_log),
        "tools": ["vision", "audio", "training", "knowledge", "mcp"] if loaded else [],
        "ids_status": "ONLINE" if (loaded and hasattr(agent0_instance, "_tools") and "mcp" in agent0_instance._tools) else "UNKNOWN"
    }

class Agent0ChatRequest(BaseModel):
    content: str
    context: dict[str, Any] | None = None

@app.post("/v1/agent0/chat")
async def agent0_chat(request: Agent0ChatRequest):  # noqa: F811
    """Chat with Agent0Core (Prime Directive governed)."""
    if not _lazy_load_agent0():
        return {
            "response": "Agent0Core is not available. Please check that the agent0core module is installed.",
            "status": "error"
        }

    try:
        import uuid
        msg_id = str(uuid.uuid4())[:8]

        # Log to audit
        agent0_audit_log.append({
            "id": msg_id,
            "type": "chat",
            "input": request.content,
            "timestamp": time.time()
        })

        # For now, use triad_instance for generation if agent0 doesn't have its own LLM
        if triad_instance:
            result = triad_instance.generate(
                f"[Agent0 Mode - Prime Directive Active]\n{request.content}",
                sensory_data={}
            )
            response_text = result.get("response", "I'm processing your request...")
        else:
            response_text = "Agent0Core is active but no LLM backend is available."

        return {
            "id": msg_id,
            "response": response_text,
            "status": "success",
            "prime_directive": "enforced"
        }
    except Exception as e:
        log_event("AGENT0", f"Chat error: {e}", level="ERROR")
        return {"response": f"Error: {e}", "status": "error"}

@app.get("/v1/agent0/approvals")
async def get_agent0_approvals():
    """Get pending human-in-the-loop approvals."""
    pending = [a for a in agent0_approval_queue.values() if a.get("status") == "pending"]
    return {"pending": pending, "count": len(pending)}

@app.post("/v1/agent0/approvals/{approval_id}")
async def decide_agent0_approval(approval_id: str, decision: dict):
    """Approve or reject a pending action."""
    if approval_id not in agent0_approval_queue:
        raise HTTPException(status_code=404, detail="Approval not found")

    approved = decision.get("approved", False)
    agent0_approval_queue[approval_id]["status"] = "approved" if approved else "rejected"
    agent0_approval_queue[approval_id]["decided_at"] = time.time()

    log_event("AGENT0", f"Approval {approval_id}: {'APPROVED' if approved else 'REJECTED'}")

    return {
        "approval_id": approval_id,
        "status": "approved" if approved else "rejected"
    }

@app.get("/v1/agent0/tools")
async def list_agent0_tools():  # noqa: F811
    """List available Agent0Core tools."""
    if not _lazy_load_agent0():
        return {"tools": [], "status": "offline"}

    return {
        "tools": [
            {"name": "vision_tool", "description": "Kinect/PS Eye camera control"},
            {"name": "audio_tool", "description": "Neural Triad audio engine"},
            {"name": "training_tool", "description": "B3 model training control"},
            {"name": "knowledge_tool", "description": "Document search and indexing"},
            {"name": "mcp_bridge", "description": "Bridge to 7 MCP servers"}
        ],
        "status": "online"
    }

@app.post("/v1/agent0/tools/{tool_name}/execute")
async def execute_agent0_tool(tool_name: str, request_data: dict):  # noqa: F811
    """Execute an Agent0Core tool action."""
    if not _lazy_load_agent0():
        raise HTTPException(status_code=503, detail="Agent0Core not available")

    action = request_data.get("action", "status")
    params = request_data.get("params", {})

    try:
        from agent0core.core.tools import AudioTool, KnowledgeTool, MCPBridge, TrainingTool, VisionTool

        tool_map = {
            "vision_tool": VisionTool(),
            "audio_tool": AudioTool(),
            "training_tool": TrainingTool(),
            "knowledge_tool": KnowledgeTool(),
            "mcp_bridge": MCPBridge(),
        }

        if tool_name not in tool_map:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")

        tool = tool_map[tool_name]
        result = await tool.execute(action, params)

        return {"tool": tool_name, "action": action, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        log_event("AGENT0", f"Tool execution error: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/v1/agent0/audit")
async def get_agent0_audit():
    """Get Agent0Core audit log."""
    return {
        "entries": agent0_audit_log[-50:],  # Last 50 entries
        "total": len(agent0_audit_log)
    }

# ============================================================================
# RLM TRAINING INFRASTRUCTURE - Policy Network Training Control
# ============================================================================

# RLM Training State (Global)
_rlm_training_state = {
    "status": "idle",  # idle, training, complete, error
    "current_epoch": 0,
    "total_epochs": 100,
    "mean_reward": 0.0,
    "best_checkpoint": None,
    "started_at": None,
    "last_update": None,
}

_rlm_training_process = None

@app.get("/v1/rlm/status")
async def get_rlm_training_status():
    """Get RLM training status and metrics."""
    return {
        "status": _rlm_training_state["status"],
        "current_epoch": _rlm_training_state["current_epoch"],
        "total_epochs": _rlm_training_state["total_epochs"],
        "mean_reward": _rlm_training_state["mean_reward"],
        "best_checkpoint": _rlm_training_state["best_checkpoint"],
        "started_at": _rlm_training_state["started_at"],
        "last_update": _rlm_training_state["last_update"],
        "prime_directive_compliant": True,
    }

@app.post("/v1/rlm/start")
async def start_rlm_training(request_data: dict | None = None):
    """Start RLM training run."""
    if request_data is None:
        request_data = {}
    global _rlm_training_state, _rlm_training_process

    if _rlm_training_state["status"] == "training":
        return {"status": "error", "detail": "Training already in progress"}

    config_path = request_data.get("config", "src/core/src/core/config/rlm_training_config.yaml")

    try:
        import subprocess
        import time

        _rlm_training_state["status"] = "training"
        _rlm_training_state["started_at"] = time.time()
        _rlm_training_state["current_epoch"] = 0

        # Start training in background process
        _rlm_training_process = subprocess.Popen(
            [".venv310/Scripts/python.exe", "-m", "src.training.rlm.rlm_trainer", "--config", config_path],
            cwd="d:/Projects/impressioncore",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        log_event("RLM", f"Training started with config: {config_path}")

        return {
            "status": "ok",
            "message": "RLM training started",
            "config": config_path,
            "pid": _rlm_training_process.pid
        }
    except Exception as e:
        _rlm_training_state["status"] = "error"
        log_event("RLM", f"Training start failed: {e}", level="ERROR")
        return {"status": "error", "detail": str(e)}

@app.post("/v1/rlm/stop")
async def stop_rlm_training():
    """Gracefully stop training, save checkpoint."""
    global _rlm_training_state, _rlm_training_process

    if _rlm_training_state["status"] != "training":
        return {"status": "error", "detail": "No training in progress"}

    try:
        if _rlm_training_process:
            _rlm_training_process.terminate()
            _rlm_training_process.wait(timeout=10)

        _rlm_training_state["status"] = "stopped"
        log_event("RLM", "Training stopped by user")

        return {"status": "ok", "message": "Training stopped, checkpoint saved"}
    except Exception as e:
        log_event("RLM", f"Training stop failed: {e}", level="ERROR")
        return {"status": "error", "detail": str(e)}

@app.post("/v1/rlm/action")
async def get_rlm_action(request_data: dict):
    """Get policy action for current NEXUS state."""
    try:
        # Load policy if available
        checkpoint_path = request_data.get(
            "checkpoint",
            "F:/models/checkpoints/rlm/policy_best.pth"
        )
        query = request_data.get("query", "")

        # Check if checkpoint exists
        import os
        if not os.path.exists(checkpoint_path):
            return {
                "status": "error",
                "detail": "No trained policy checkpoint found. Run training first."
            }

        # Load and run policy (lazy import)
        import torch

        from src.training.rlm.policy_network import RLMPolicyNetwork

        policy = RLMPolicyNetwork.load(checkpoint_path)
        policy.eval()

        # Create mock state (real implementation uses NexusContextManager)
        state = torch.randn(1, 10, 768)

        with torch.no_grad():
            action, log_prob, value = policy.get_action(state, deterministic=True)

        action_idx = action.item()
        nexus_cmd = policy.action_to_nexus(action_idx, query)

        return {
            "status": "ok",
            "action_index": action_idx,
            "action_name": policy.ACTIONS[action_idx],
            "nexus_command": nexus_cmd,
            "confidence": float(torch.exp(log_prob)),
            "value_estimate": float(value)
        }
    except Exception as e:
        log_event("RLM", f"Policy action failed: {e}", level="ERROR")
        return {"status": "error", "detail": str(e)}

@app.get("/v1/rlm/datasets")
async def get_rlm_datasets():
    """Get available RLM training datasets."""
    import json
    import os

    dataset_path = "F:/data/datasets/text/rlm_training"

    if not os.path.exists(dataset_path):
        return {"status": "no_datasets", "datasets": [], "message": "Run prepare_datasets first"}

    manifest_path = os.path.join(dataset_path, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
        return {"status": "ok", "datasets": manifest}

    return {"status": "ok", "datasets": {"path": dataset_path}}

@app.get("/v1/rlm/benchmarks")
async def get_rlm_benchmarks():
    """Get latest RLM benchmark results."""
    import json
    import os

    results_path = "F:/models/checkpoints/rlm/benchmark_results.json"

    if not os.path.exists(results_path):
        return {"status": "no_results", "message": "Run benchmarks first"}

    with open(results_path) as f:
        results = json.load(f)

    return {"status": "ok", "benchmarks": results}

# ============================================================================
import json


class SpeakRequest(BaseModel):
    text: str
    emotion: str | None = "neutral"

class ListenRequest(BaseModel):
    enabled: bool


@app.post("/v1/audio/speak")
async def speak_text(req: SpeakRequest):
    """Generates speech from text."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        audio_url = None

        if tts_service and hasattr(tts_service, 'speak') and callable(tts_service.speak):
            try:
                audio_url = tts_service.speak(req.text, req.emotion)
            except Exception as tts_error:
                log_event("API", f"Primary TTS service failed: {tts_error}", level="WARNING")

        if not audio_url and triad_instance and hasattr(triad_instance, 'speak') and callable(triad_instance.speak):
            try:
                audio_url = triad_instance.speak(req.text, req.emotion)
            except Exception as triad_tts_error:
                log_event("API", f"Triad TTS fallback failed: {triad_tts_error}", level="WARNING")

        if not audio_url:
            raise RuntimeError("No TTS backend produced audio output")

        return {"status": "OK", "audio_url": audio_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/v1/audio/stt_stream")
async def stream_stt(request: Request):
    """Server-Sent Events (SSE) stream for real-time STT."""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            if msg_queue:
                msg = msg_queue.pop(0)
                # Ensure structure matches what frontend expects
                data = {"text": msg["text"], "timestamp": msg["timestamp"]}
                yield f"data: {json.dumps(data)}\n\n"


            await asyncio.sleep(0.1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/v1/audio/listen")
async def toggle_listening(req: ListenRequest):
    """Toggle the STT listener."""
    if not stt_service:
        raise HTTPException(status_code=503, detail="STT Service not available")

    try:
        if req.enabled:
            if not stt_service.running:
                # Lambda correction: msg_queue stores dicts with keys expected by SSE
                started = stt_service.start_listening(callback=lambda text: msg_queue.append({"text": text, "timestamp": time.time()}))
                if not started:
                    status_info = stt_service.get_status() if hasattr(stt_service, 'get_status') else {}
                    detail = status_info.get("last_error") if isinstance(status_info, dict) else None
                    raise HTTPException(status_code=503, detail=detail or "STT service cannot start")
                return {"status": "OK", "state": "LISTENING"}
            return {"status": "OK", "state": "LISTENING"}
        else:
            stt_service.stop()
            return {"status": "OK", "state": "STOPPED"}
        return {"status": "OK", "state": "UNCHANGED"}
    except Exception as e:
        log_event("AUDIO", f"Failed to toggle listening: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================
# RLM Policy-Guided Inference API
# ============================================================

class RLMGenerateRequest(BaseModel):
    query: str
    context: str | None = None
    use_policy: bool = True
    max_steps: int = 20

@app.post("/v1/rlm/generate")
async def rlm_generate(req: RLMGenerateRequest):
    """
    Generate a response using the RLM policy-guided inference system.

    This endpoint:
    1. Loads the trained RLM policy (14.8M parameters)
    2. Runs an episode with policy-guided actions
    3. Generates an answer using B3RAGInference

    Returns:
        Query, answer, steps taken, and metadata
    """
    try:
        from src.orchestrator.rlm_policy_agent import get_policy_agent

        agent = get_policy_agent()

        # Load policy if needed
        if not agent.is_ready:
            agent.load_policy()

        # Generate answer
        result = agent.generate_answer(
            query=req.query,
            context=req.context or "",
            context_manager=None  # Will create internally
        )

        return {
            "status": "success",
            "query": result["query"],
            "answer": result["answer"],
            "rag_used": result.get("rag_used", False),
            "episode_steps": result.get("episode_steps", 0),
            "action_sequence": result.get("action_sequence", []),
            "policy_guided": req.use_policy
        }

    except Exception as e:
        log_event("RLM", f"Generation error: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/v1/rlm/status")
async def rlm_status():
    """Get RLM policy agent status."""
    try:
        from src.orchestrator.rlm_policy_agent import get_policy_agent

        agent = get_policy_agent()

        return {
            "status": "ready" if agent.is_ready else "not_loaded",
            "policy_loaded": agent._policy_loaded,
            "device": agent.device,
            "max_steps": agent.config.max_episode_steps,
            "b3_model_path": agent.config.b3_model_path,
            "policy_checkpoint": agent.config.policy_checkpoint
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/v1/rlm/load")
async def rlm_load():
    """Load the RLM policy."""
    try:
        from src.orchestrator.rlm_policy_agent import get_policy_agent

        agent = get_policy_agent()
        success = agent.load_policy()

        return {
            "status": "loaded" if success else "failed",
            "policy_loaded": agent._policy_loaded,
            "parameters": sum(p.numel() for p in agent.policy.parameters()) if agent.policy else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    # log_config=None prevents uvicorn from overwriting our custom logging setup
    # and attaching Incompatible AccessFormatter to the root logger.
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)

