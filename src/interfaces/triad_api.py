import asyncio
import base64
import logging
import os
import sys
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

# Compute paths
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
_WEB_CLIENT_PUBLIC = _THIS_DIR / "web_client" / "public"

# Add project root to path
sys.path.append(os.path.abspath(str(_PROJECT_ROOT)))

try:
    import cv2
except ImportError:
    cv2 = None
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.interfaces import api_state
from src.interfaces.runtime_access import RuntimeAccessMiddleware
from src.orchestrator.system_logger import log_event

# --- Console Redirection Logic ---
class ConsoleLogger:
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.error_terminal = sys.stderr
        self.log = open(filepath, "a", encoding="utf-8", buffering=1)

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
sys.stderr = sys.stdout

# --- Logging Integration ---
logging.root.handlers = []
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(console_log_path, encoding='utf-8'),
        logging.StreamHandler(sys.stdout.terminal)
    ]
)

for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    l = logging.getLogger(logger_name)
    l.handlers = logging.root.handlers
    l.propagate = False

print(f"\n--- API SESSION START: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")

# Imports for initialization
from src.intelligence.stt_service import STTService
from src.intelligence.tts_service import TTSService
from src.core.config.runtime_mode_config import load_runtime_mode_config
from src.interfaces.telemetry_manager import get_telemetry_manager
from src.orchestrator.kinect_fusion_adapter import KinectFusionAdapter
from src.orchestrator.session_manager import session_manager
from src.orchestrator.runtime_mode_controller import RuntimeModeController
from src.orchestrator.unified_triad import UnifiedBrainTriad

def initialize_runtime() -> None:
    """Initialize heavyweight resources off the HTTP event loop."""
    # Enforce data drive availability on startup
    from src.core.config.data_paths import enforce_data_drive
    try:
        enforce_data_drive()
    except Exception as e:
        log_event("API", f"CRITICAL: Boot aborted due to missing data drive: {e}", level="CRITICAL")
        api_state.runtime_startup.update(phase="FAILED", error=str(e))
        return

    try:
        log_event("API", "Initializing Global Triad Instance...")
        api_state.runtime_startup.update(phase="LOADING_MODEL", error=None)
        api_state.triad_instance = UnifiedBrainTriad()

        # Capture starts only through the explicit operator control.
        api_state.triad_instance.vision_active = False
        log_event("API", "Triad Online.")

        # --- agent0core DI wiring (subsystems injection) ---
        try:
            from src.integrations.agent0core_bridge import wire_agent0core
            wire_agent0core(api_state.triad_instance)
            log_event("API", "agent0core DI boundary wired successfully")
        except Exception as e:
            log_event("API", f"agent0core DI wiring failed (non-fatal): {e}", level="WARNING")

        # Runtime mode controller
        mode_config = load_runtime_mode_config()
        api_state.runtime_mode_controller = RuntimeModeController(
            native_audio_enabled=mode_config.native_audio_enabled,
            avatar_mode_preference=mode_config.avatar_mode_default,
            audio_mode_preference=mode_config.audio_mode_default,
            vram_switch_threshold_gb=mode_config.vram_switch_threshold_gb,
            fps_switch_threshold=mode_config.fps_switch_threshold,
        )
        api_state.runtime_mode_controller.apply_preferences(
            avatar_preference=mode_config.avatar_mode_default,
            audio_preference=mode_config.audio_mode_default,
        )
        api_state.triad_instance.runtime_mode_controller = api_state.runtime_mode_controller

        # Kinect fusion adapter
        api_state.kinect_fusion_adapter = KinectFusionAdapter()
        api_state.kinect_fusion_adapter.refresh(getattr(api_state.triad_instance, "vision", None))

        # Init Audio Intelligence
        try:
            log_event("API", "Initializing Audio Services...")
            api_state.stt_service = STTService(model_size="tiny.en", device="cpu")
            api_state.tts_service = TTSService()
            if api_state.stt_service.model_loaded:
                log_event("API", "Speech model ready; microphone listening remains off.")
            else:
                log_event("API", f"Speech transcription unavailable: {api_state.stt_service.last_error}", level="WARNING")

            # Init Telemetry
            api_state.telemetry_manager = get_telemetry_manager(api_state.triad_instance)
            log_event("API", "Telemetry Manager Online.")
        except Exception as e:
            log_event("API", f"Audio Service Init Failed: {e}", level="ERROR")

    except Exception as e:
        log_event("API", f"Failed to init Triad: {e}", level="CRITICAL")
        api_state.runtime_startup.update(phase="FAILED", error=str(e))
        return

    # New Vector Connector
    try:
        from src.orchestrator.vector_connector import VectorMemoryConnector
        api_state.vector_memory = VectorMemoryConnector()
    except Exception as e:
        log_event("API", f"Vector Memory Init Failed: {e}", level="WARNING")
        api_state.vector_memory = None

    api_state.runtime_startup.update(phase="READY", error=None)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Serve liveness immediately while model initialization runs in a worker."""
    api_state.runtime_startup.update(phase="INITIALIZING", error=None)
    async def initialize():
        try:
            await asyncio.to_thread(initialize_runtime)
        except Exception as error:
            api_state.runtime_startup.update(phase="FAILED", error=str(error))
            logging.getLogger(__name__).exception("Runtime initialization failed")

    initialization = asyncio.create_task(initialize())
    app.state.initialization = initialization
    yield

    # A worker cannot be cancelled safely while it owns native/GPU resources.
    await initialization
    # --- SHUTDOWN ---
    log_event("API", "SHUTDOWN SIGNAL RECEIVED. Releasing resources...")

    if api_state.stt_service:
        try:
            log_event("API", "Stopping STT Service...")
            api_state.stt_service.stop()
        except Exception:
            pass

    if api_state.telemetry_manager:
        api_state.telemetry_manager.disconnect(None)

    if api_state.triad_instance:
        try:
            api_state.triad_instance.shutdown()
        except Exception as e:
            log_event("API", f"Triad Shutdown error: {e}", level="WARNING")

    log_event("API", "CLEAN SHUTDOWN COMPLETE. System Halted.")

# Instantiate FastAPI App
app = FastAPI(title="ImpressionCore B3-Triad API", lifespan=lifespan)

# Allow CORS for React Frontend
try:
    from src.core.config.cors_config import get_allowed_origins
except ImportError:
    from src.core.config.cors_config import get_allowed_origins

from agent0core.config import default_config as agent_config

app.add_middleware(RuntimeAccessMiddleware, key_provider=lambda: agent_config.api_key)
# Last added is outermost: even rejected requests get the configured CORS policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health/live")
async def liveness():
    return {"status": "ALIVE"}


@app.get("/health/ready")
async def readiness():
    state = api_state.runtime_startup
    ready = state["phase"] == "READY" and bool(
        api_state.triad_instance and api_state.triad_instance.get_model_status()["llm_loaded"]
    )
    return JSONResponse(
        {"ready": ready, "phase": state["phase"]},
        status_code=200 if ready else 503,
    )

# Serve static mounts
app.mount("/audio", StaticFiles(directory="logs"), name="audio")

capture_dir = str(_WEB_CLIENT_PUBLIC / "captures")
os.makedirs(capture_dir, exist_ok=True)
app.mount("/captures", StaticFiles(directory=capture_dir), name="captures")

voice_rec_dir = str(_WEB_CLIENT_PUBLIC / "voice_recordings")
os.makedirs(voice_rec_dir, exist_ok=True)
app.mount("/voice_recordings", StaticFiles(directory=voice_rec_dir), name="voice_recordings")

public_dir = str(_WEB_CLIENT_PUBLIC)
app.mount("/static", StaticFiles(directory=public_dir), name="static")

@app.get("/system_monitor.html")
async def system_monitor():
    """Serve the System Monitor HTML page."""
    monitor_path = _WEB_CLIENT_PUBLIC / "system_monitor.html"
    return FileResponse(str(monitor_path), media_type="text/html")

# --- Import and Include Domain Routers ---
from src.interfaces.routes import system, agent0, vision, audio, rlm, chat

app.include_router(system.router)
app.include_router(agent0.router)
app.include_router(vision.router)
app.include_router(audio.router)
app.include_router(rlm.router)
app.include_router(chat.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None, access_log=False)
