import os
import sys
import time
import torch
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.interfaces import api_state
from src.orchestrator.system_logger import log_event
from src.orchestrator.sensory_intelligence import sensory_intel

router = APIRouter()


def _find_kinect(vision):
    if not vision:
        return None
    caps = getattr(vision, "caps", {}) or {}
    kinect = caps.get(98) or caps.get("98")
    if kinect:
        return kinect
    return next((cap for cap in caps.values() if hasattr(cap, "get_stream_health")), None)


def _kinect_stream_health(vision):
    kinect = _find_kinect(vision)
    if not kinect or not hasattr(kinect, "get_stream_health"):
        return {
            "status": "NOT_DETECTED",
            "capture_active": False,
            "physical_sensor_count": None,
            "physical_sensor_identity": None,
            "logical_stream_count": 0,
            "streams": {},
        }
    return kinect.get_stream_health()


class RuntimeModeRequest(BaseModel):
    avatar_mode_preference: str | None = None
    audio_mode_preference: str | None = None
    native_audio_enabled: bool | None = None
    vram_switch_threshold_gb: float | None = None
    fps_switch_threshold: float | None = None

@router.get("/")
async def root():
    """Root endpoint to confirm API is running."""
    return {
        "status": "ONLINE",
        "system": "ImpressionCore B3-Triad",
        "version": "1.2.0",
        "endpoints": {
            "system": "/v1/system/status",
            "agent0": "/v1/agent0/status",
        }
    }

@router.get("/v1/hardware")
async def get_hardware_status():
    triad = api_state.triad_instance
    if not triad:
        return {"status": "ERROR", "detail": "Triad not initialized"}

    cameras = []
    health = "HEALTHY"
    kinect_health = _kinect_stream_health(getattr(triad, "vision", None))

    if triad.vision:
        try:
            diag = sensory_intel.get_diagnostics()
            health = diag["status"]

            for idx, cap in triad.vision.caps.items():
                meta = triad.vision.hardware_metadata.get(idx, {})
                label = meta.get("model", f"Camera {idx}")

                is_active = True
                if hasattr(cap, 'isOpened'):
                    is_active = cap.isOpened()

                cameras.append({
                    "id": idx,
                    "active": (
                        any(s.get("fresh") for s in kinect_health["streams"].values())
                        if str(idx) == "98" else is_active
                    ),
                    "backend": meta.get("backend", "cv2"),
                    "model": label,
                    "vid_pid": meta.get("vid_pid"),
                    "ptz_capabilities": meta.get("ptz_capabilities"),
                    "physical_sensor": True,
                    "stream_health": kinect_health if str(idx) == "98" else None,
                })
                log_event("API", f"HW Scan Cam {idx}: {label} | PTZ: {meta.get('ptz_capabilities')}")

            if 98 in triad.vision.caps or "98" in triad.vision.caps:
                cameras.append({
                    "id": 105,
                    "active": bool(kinect_health["streams"].get("depth", {}).get("fresh")),
                    "backend": "KINECT_DEPTH",
                    "model": "Xbox 360 Kinect [Depth Stream]",
                    "vid_pid": "045e_02ae",
                    "ptz_capabilities": {"pan": False, "tilt": True, "motor_control": True},
                    "logical_stream": True,
                    "physical_sensor_identity": kinect_health.get("physical_sensor_identity"),
                })
                cameras.append({
                    "id": 106,
                    "active": bool(kinect_health["streams"].get("ir", {}).get("fresh")),
                    "backend": "KINECT_IR",
                    "model": "Xbox 360 Kinect [Infrared Stream]",
                    "vid_pid": "045e_02ae",
                    "ptz_capabilities": {"pan": False, "tilt": True, "motor_control": True},
                    "logical_stream": True,
                    "physical_sensor_identity": kinect_health.get("physical_sensor_identity"),
                })
        except Exception as e:
            log_event("API", f"Hardware Probe Error: {e}", level="WARNING")

    return api_state.sanitize_numpy({
        "status": "OK",
        "vision_active": triad.vision_active,
        "vision_health": health,
        "detected_cameras": cameras,
        "physical_sensor_count": len(getattr(getattr(triad, "vision", None), "caps", {}) or {}),
        "kinect_physical_sensor_count": kinect_health["physical_sensor_count"],
        "logical_streams": kinect_health["streams"],
        "vram_mode": triad.simultaneous_load,
        "hardware_telemetry": triad.get_hardware_status()
    })

@router.get("/v1/model/status")
async def get_model_status():
    """Returns detailed information about the active LLM."""
    triad = api_state.triad_instance
    if not triad:
        startup = getattr(api_state, "runtime_startup", {}) or {}
        phase = str(startup.get("phase", "INITIALIZING")).upper()
        error = startup.get("error")
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Triad not initialized",
                "phase": phase,
                "error": error,
            },
        )
    return triad.get_model_status()

@router.get("/v1/runtime/modes")
async def get_runtime_modes():
    controller = api_state.runtime_mode_controller
    triad = api_state.triad_instance
    if not controller:
        raise HTTPException(status_code=503, detail="Runtime mode controller not initialized")

    controller.refresh(triad)
    return {"status": "OK", "runtime_modes": controller.get_state()}

@router.post("/v1/runtime/modes")
async def set_runtime_modes(request: RuntimeModeRequest):
    controller = api_state.runtime_mode_controller
    triad = api_state.triad_instance
    if not controller:
        raise HTTPException(status_code=503, detail="Runtime mode controller not initialized")

    if request.native_audio_enabled is not None:
        controller.toggle_native_audio(request.native_audio_enabled)

    controller.set_thresholds(
        vram_switch_threshold_gb=request.vram_switch_threshold_gb,
        fps_switch_threshold=request.fps_switch_threshold,
    )
    if request.avatar_mode_preference is not None or request.audio_mode_preference is not None:
        controller.apply_preferences(
            avatar_preference=request.avatar_mode_preference,
            audio_preference=request.audio_mode_preference
        )
    return {"status": "OK", "runtime_modes": controller.get_state()}

@router.get("/v1/system/status")
async def get_system_all_status(refresh: bool = False):
    """Unified System Health & Preparedness Checklist (Front-to-Back)."""
    triad = api_state.triad_instance
    controller = api_state.runtime_mode_controller
    kinect_adapter = api_state.kinect_fusion_adapter
    try:
        if not triad:
            startup = getattr(api_state, "runtime_startup", {}) or {}
            phase = str(startup.get("phase", "INITIALIZING")).upper()
            error = startup.get("error")
            status = "FAILED" if phase == "FAILED" or error else "INITIALIZING"
            return JSONResponse(
                status_code=503,
                content=api_state.sanitize_numpy({
                    "status": status,
                    "loading_phase": phase,
                    "initialization_error": error,
                    "timestamp": time.time(),
                    "components": {"triad": status},
                }),
            )

        if refresh and triad.vision:
            refresh_fn = getattr(triad.vision, "refresh_hardware", None)
            if callable(refresh_fn):
                try:
                    refresh_fn(audio_engine=getattr(triad, 'audio', None))
                except TypeError:
                    refresh_fn()

        vision_diag = {"status": "OFFLINE"}
        camera_count = 0
        pnp_size = 0
        if triad.vision:
            try:
                if hasattr(triad.vision, 'diag_hardware'):
                    vision_diag = triad.vision.diag_hardware()
                else:
                    vision_diag = {"status": "DEGRADED", "reason": "Diagnostic method missing"}

                camera_count = len(triad.vision.caps) if triad.vision.caps else 0
                pnp_size = len(triad.vision.pnp_inventory) if hasattr(triad.vision, 'pnp_inventory') else 0
            except Exception as ve:
                log_event("API", f"Vision status check failed: {ve}", level="ERROR")
                vision_diag = {"status": "ERROR", "reason": str(ve)}

        model_status = {"llm_loaded": False, "active_llm": "Unknown", "vram_allocated_gb": 0}
        try:
            if hasattr(triad, 'get_model_status'):
                model_status = triad.get_model_status()
        except Exception as me:
            log_event("API", f"Model check failed: {me}")

        audio_inventory = []
        mic_count = 0
        try:
            from src.orchestrator.audio_engine import audio_device_identity, summarize_audio_devices

            audio_engine = getattr(triad, "audio", None)
            input_endpoints = list(getattr(audio_engine, "devices", None) or [])
            if not input_endpoints:
                import sounddevice as sd
                for index, device in enumerate(sd.query_devices()):
                    channels = int(device.get("max_input_channels") or 0)
                    if channels <= 0:
                        continue
                    name = device.get("name", "")
                    input_endpoints.append({
                        "name": name,
                        "channels": channels,
                        "provider": device.get("hostapi", "unknown"),
                        "index": index,
                        "device_identity": audio_device_identity(name),
                        "is_kinect": "kinect" in name.lower(),
                        "is_eye": (
                            "playstation" in name.lower()
                            or "ps eye" in name.lower()
                            or "eye toy" in name.lower()
                        ),
                    })
            audio_inventory = summarize_audio_devices(input_endpoints)
            mic_count = len(audio_inventory)
        except Exception as ae:
            log_event("API", f"Audio Scan Failed: {ae}", level="WARNING")

        overall_status = "NOMINAL" if vision_diag.get("status") in ["HEALTHY", "ACTIVE"] else "DEGRADED"
        intel_status = "ACTIVE" if model_status.get("llm_loaded") else model_status.get("loading_phase", "LOADING")
        loading_phase = "READY" if (overall_status in ["NOMINAL", "DEGRADED"] and intel_status == "ACTIVE") else "INITIALIZING"

        runtime_modes = None
        if controller:
            controller.refresh(triad)
            runtime_modes = controller.get_state()

        kinect_fusion = None
        if kinect_adapter:
            kinect_adapter.refresh(getattr(triad, "vision", None))
            kinect_fusion = kinect_adapter.get_status()
        kinect_health = _kinect_stream_health(getattr(triad, "vision", None))

        return api_state.sanitize_numpy({
            "status": overall_status,
            "loading_phase": loading_phase,
            "timestamp": time.time(),
            "trace": sensory_intel.trace_log,
            "runtime_modes": runtime_modes,
            "kinect_fusion": kinect_fusion,
            "components": {
                "vision": {
                    "active": triad.vision is not None,
                    "health": vision_diag.get("status", "UNKNOWN"),
                    "cameras_detected": camera_count,
                    "physical_sensor_count": camera_count,
                    "kinect_physical_sensor_count": kinect_health["physical_sensor_count"],
                    "kinect_streams": kinect_health,
                    "conflicts": vision_diag.get("conflicts", [])
                },
                "intelligence": {
                    "status": intel_status,
                    "model": model_status.get("model_name", "None"),
                    "vram_allocated_gb": model_status.get("vram_allocated_gb", 0),
                    "agents": model_status.get("agents", {})
                },
                "sensory": {
                    "microphones": mic_count,
                    "audio_input_devices": audio_inventory,
                    "microphone_identity_basis": "normalized provider/name; endpoint aliases may share an identity",
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

@router.post("/v1/system/acknowledge_conflict")
async def acknowledge_system_conflict(payload: dict):
    """Adds a device to the suppression list to ignore non-critical hardware errors."""
    triad = api_state.triad_instance
    try:
        device_name = payload.get("device")
        if not device_name:
            raise HTTPException(status_code=400, detail="Device name required")

        intel = triad.vision.sensory if (triad and triad.vision and hasattr(triad.vision, 'sensory')) else sensory_intel
        intel.suppress_device(device_name)

        log_event("API", f"Conflict acknowledged for device: {device_name}")
        return {"status": "SUCCESS", "message": f"Device '{device_name}' suppressed."}
    except Exception as e:
        log_event("API", f"Acknowledge conflict failed: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/v1/system/debug")
async def get_system_debug_logs():
    """Generates a comprehensive debug snapshot and saves it to disk."""
    triad = api_state.triad_instance
    try:
        debug_info = {
            "timestamp": time.time(),
            "triad_alive": triad is not None,
            "hw_diag": sensory_intel.get_diagnostics() if sensory_intel else "SensoryIntel Missing",
            "hw_trace": sensory_intel.trace_log if sensory_intel else [],
            "active_caps": list(triad.vision.caps.keys()) if triad and triad.vision else [],
            "vision_status": triad.vision._is_running if triad and triad.vision else False
        }

        log_dir = os.path.join(os.getcwd(), "logs", "debug")
        os.makedirs(log_dir, exist_ok=True)
        log_filename = f"debug_snapshot_{int(time.time())}.txt"
        log_path = os.path.join(log_dir, log_filename)

        with open(log_path, "w", encoding="utf-8") as f:
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

@router.get("/v1/system/verify")
async def verify_system_integrity():
    """Deep diagnostic suite: Checks files, processes, and port health."""
    triad = api_state.triad_instance
    try:
        report = {
            "timestamp": time.time(),
            "status": "SECURE",
            "checks": {
                "neural_core": "NOMINAL" if triad else "FAILED",
                "vision_layer": "ACTIVE" if triad and triad.vision and triad.vision._is_running else "FAILED",
                "driver_conflicts": sensory_intel.get_diagnostics().get("status") == "HEALTHY" if sensory_intel else "UNKNOWN",
                "pnp_inventory": len(sensory_intel.pnp_inventory) if sensory_intel else 0
            },
            "environment": {
                "python_version": sys.version,
                "cuda_available": torch.cuda.is_available(),
                "vram_allocated": f"{torch.cuda.memory_allocated() / 1e9:.2f} GB" if torch.cuda.is_available() else "0 GB"
            }
        }

        if any(v == "FAILED" for v in report["checks"].values()):
            report["status"] = "DEGRADED"

        return report
    except Exception as e:
        log_event("API", f"Integrity check failed: {e}", level="ERROR")
        return {"status": "ERROR", "message": str(e)}

@router.post("/v1/hardware/refresh")
async def refresh_hardware_request():
    """Triggers a hot-swap scan of vision hardware."""
    triad = api_state.triad_instance
    if not triad or not triad.vision:
        raise HTTPException(status_code=503, detail="Vision layer offline")
    try:
        refresh_fn = getattr(triad.vision, "refresh_hardware", None)
        if callable(refresh_fn):
            try:
                result = refresh_fn(audio_engine=getattr(triad, 'audio', None))
            except TypeError:
                result = refresh_fn()
        else:
            result = {"status": "NO_REFRESH_METHOD"}

        if triad.audio:
             triad.audio.refresh_devices()

        return result
    except Exception as e:
        log_event("API", f"Hardware refresh failed: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=f"Hardware refresh failed: {e}") from e

@router.post("/v1/system/shutdown")
async def system_shutdown():
    """Triggers graceful system halt."""
    log_event("API", "Shutdown Request Received.")
    triad = api_state.triad_instance
    if triad:
        triad.shutdown()

    import asyncio
    async def suicide():
        await asyncio.sleep(1.0)
        log_event("API", "Process Terminating.")
        os._exit(0)

    asyncio.create_task(suicide())
    return {"status": "SHUTDOWN_INITIATED", "message": "Neural Core terminating in 1s."}

@router.get("/v1/system/logs")
async def get_system_logs():
    """Retrieve the latest 100 lines from the console log file."""
    console_log_path = os.path.join("logs", "triad_api_console.log")
    try:
        if os.path.exists(console_log_path):
            with open(console_log_path, encoding="utf-8") as f:
                lines = f.readlines()
                return {"logs": lines[-100:]}
        return {"logs": ["Log file not found."]}
    except Exception as e:
        return {"logs": [f"Error reading logs: {e}"]}

@router.get("/v1/system/concurrency")
async def get_concurrency_status():
    """Live GPU concurrency metrics for the triad inference pipeline."""
    return {
        "status": "OK",
        "gpu_concurrency_limit": api_state._GPU_CONCURRENCY_LIMIT,
        "active_requests": api_state._gpu_active_count,
        "total_served": api_state._gpu_total_served,
        "total_rejected": api_state._gpu_total_rejected,
        "headroom": api_state._GPU_CONCURRENCY_LIMIT - api_state._gpu_active_count,
    }

@router.post("/v1/system/memory/clear")
async def clear_system_memory():
    """Clear GPU VRAM cache and trigger garbage collection."""
    try:
        from src.core.utils.gpu_utils import clear_gpu_memory
        clear_gpu_memory()
        log_event("API", "GPU memory cache cleared via API endpoint.")
        return {"status": "SUCCESS", "message": "GPU memory cleared."}
    except Exception as e:
        log_event("API", f"Failed to clear GPU memory: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e))
