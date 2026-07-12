import os
import json
import time
import asyncio
from fastapi import APIRouter, HTTPException, Request, File, UploadFile
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from src.interfaces import api_state
from src.orchestrator.system_logger import log_event
from src.orchestrator.session_manager import session_manager
from datetime import datetime

router = APIRouter()

class SpeakRequest(BaseModel):
    text: str
    emotion: str | None = "neutral"

class ListenRequest(BaseModel):
    enabled: bool

@router.get("/v1/audio/devices")
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

@router.post("/v1/audio/upload")
async def upload_stt_audio(file: UploadFile = File(...)):
    """Upload STT audio recording for persistent storage."""
    voice_rec_dir = str(api_state._WEB_CLIENT_PUBLIC / "voice_recordings")
    os.makedirs(voice_rec_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"stt_{timestamp}.webm"
    filepath = os.path.join(voice_rec_dir, filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    log_event("AUDIO", f"STT Recording saved: {filename}")
    return {"status": "OK", "audio_url": f"/voice_recordings/{filename}"}

@router.post("/v1/audio/upload_file")
async def upload_stt_audio_file(file: UploadFile = File(...)):
    """Upload STT audio recording for persistent storage."""
    voice_rec_dir = str(api_state._WEB_CLIENT_PUBLIC / "voice_recordings")
    os.makedirs(voice_rec_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"stt_{timestamp}.webm"
    filepath = os.path.join(voice_rec_dir, filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    log_event("AUDIO", f"STT Recording saved: {filename}")
    return {"status": "OK", "audio_url": f"/voice_recordings/{filename}"}

@router.get("/v1/sessions")
async def list_sessions():
    return session_manager.list_sessions()

@router.post("/v1/sessions")
async def create_session():
    return session_manager.create_session(title="New Neural Pathway")

@router.get("/v1/sessions/{session_id}")
async def get_session(session_id: str):
    return session_manager.get_session(session_id)

@router.delete("/v1/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_manager.delete_session(session_id):
        return {"status": "DELETED"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@router.get("/v1/audio/status")
async def get_audio_status():
    """Detailed Audio Array Telemetry."""
    triad = api_state.triad_instance
    stt_service = api_state.stt_service
    try:
        if not triad or not triad.audio:
            return {"status": "UNAVAILABLE", "devices": [], "stream": {}}

        audio_engine = triad.audio
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

        if hasattr(triad, 'get_fused_telemetry'):
            fused = triad.get_fused_telemetry()
            stream_data["target_lock"] = fused.get("target_lock", False)
            stream_data["angular_distance"] = fused.get("angular_distance", 0)
            stream_data["status_msg"] = fused.get("status_msg", "UNKNOWN")

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
        return api_state.sanitize_numpy(telemetry)
    except Exception as e:
        log_event("API", f"Audio Status Failed: {e}", level="ERROR")
        return {"status": "ERROR", "error": str(e)}

@router.post("/v1/audio/config")
async def set_audio_config(config: dict):
    """Control Audio Subsystem."""
    triad = api_state.triad_instance
    try:
        if not triad or not triad.audio:
             raise HTTPException(status_code=503, detail="Audio Engine Unavailable")

        if "active" in config:
            should_be_active = config["active"]
            api_state.AUDIO_CONFIG["active"] = should_be_active

            if should_be_active and not triad.audio.active:
                idx = config.get("device_index")
                if idx is None:
                    devs = triad.audio.devices
                    eye = next((d for d in devs if d["channels"] == 4), None)
                    if not eye:
                        eye = next((d for d in devs if d["is_eye"]), None)
                    idx = eye["index"] if eye else 0

                triad.audio.start_stream(idx)

            elif not should_be_active and triad.audio.active:
                triad.audio.stop_stream()

        if "gain" in config:
            api_state.AUDIO_CONFIG["gain_master"] = float(config["gain"])

        return {"status": "OK", "active": triad.audio.active}
    except Exception as e:
        log_event("API", f"Audio Config Failed: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.post("/v1/audio/speak")
async def speak_text(req: SpeakRequest):
    """Generates speech from text."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    triad = api_state.triad_instance
    tts_service = api_state.tts_service
    try:
        audio_url = None

        if tts_service and hasattr(tts_service, 'speak') and callable(tts_service.speak):
            try:
                audio_url = tts_service.speak(req.text, req.emotion)
            except Exception as tts_error:
                log_event("API", f"Primary TTS service failed: {tts_error}", level="WARNING")

        if not audio_url and triad and hasattr(triad, 'speak') and callable(triad.speak):
            try:
                audio_url = triad.speak(req.text, req.emotion)
            except Exception as triad_tts_error:
                log_event("API", f"Triad TTS fallback failed: {triad_tts_error}", level="WARNING")

        if not audio_url:
            raise RuntimeError("No TTS backend produced audio output")

        return {"status": "OK", "audio_url": audio_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/v1/audio/stt_stream")
async def stream_stt(request: Request):
    """Server-Sent Events (SSE) stream for real-time STT."""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            if api_state.msg_queue:
                msg = api_state.msg_queue.pop(0)
                data = {"text": msg["text"], "timestamp": msg["timestamp"]}
                yield f"data: {json.dumps(data)}\n\n"

            await asyncio.sleep(0.1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/v1/audio/listen")
async def toggle_listening(req: ListenRequest):
    """Toggle the STT listener."""
    stt_service = api_state.stt_service
    if not stt_service:
        raise HTTPException(status_code=503, detail="STT Service not available")

    try:
        if req.enabled:
            if not stt_service.running:
                started = stt_service.start_listening(
                    callback=lambda text: api_state.msg_queue.append({"text": text, "timestamp": time.time()})
                )
                if not started:
                    status_info = stt_service.get_status() if hasattr(stt_service, 'get_status') else {}
                    detail = status_info.get("last_error") if isinstance(status_info, dict) else None
                    raise HTTPException(status_code=503, detail=detail or "STT service cannot start")
                return {"status": "OK", "state": "LISTENING"}
            return {"status": "OK", "state": "LISTENING"}
        else:
            stt_service.stop()
            return {"status": "OK", "state": "STOPPED"}
    except Exception as e:
        log_event("AUDIO", f"Failed to toggle listening: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e)) from e
