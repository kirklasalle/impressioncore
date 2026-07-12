"""
Chat and Telemetry Stream routes for the ImpressionCore B3-Triad API.
"""
import asyncio
import base64
import time
from typing import Any
from fastapi import APIRouter, HTTPException, Request, WebSocket
from pydantic import BaseModel

try:
    import cv2
except ImportError:
    cv2 = None
import numpy as np

from src.interfaces import api_state
from src.orchestrator.system_logger import log_event
from src.orchestrator.session_manager import session_manager

router = APIRouter()

# --- TELEMETRY ENDPOINT ---
@router.websocket("/v1/telemetry/stream")
async def telemetry_stream(websocket: WebSocket):
    if not api_state.telemetry_manager:
        await websocket.close(code=1011)
        return

    await api_state.telemetry_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        api_state.telemetry_manager.disconnect(websocket)


class GenerateRequest(BaseModel):
    prompt: str
    image_base64: str | None = None
    voice_enabled: bool = True
    session_id: str | None = None
    user_audio_url: str | None = None
    snapshots: list[str] | None = None
    avatar_mode_preference: str | None = None
    audio_mode_preference: str | None = None


def _run_native_audio_stub(response_text: str) -> dict[str, Any]:
    """Feature-flagged native-audio stub path for future implementation."""
    return {
        "enabled": False,
        "mode": "native_stub",
        "detail": "Native audio path is not implemented yet; cascaded path used.",
        "preview_text": response_text[:80] if response_text else "",
    }


@router.post("/v1/process")
async def process_multimodal(request: GenerateRequest):
    if not api_state.triad_instance:
        raise HTTPException(status_code=503, detail="Triad not initialized")

    try:
        acquired = await asyncio.wait_for(
            api_state._gpu_semaphore.acquire(), timeout=30.0
        )
    except asyncio.TimeoutError:
        async with api_state._gpu_lock:
            api_state._gpu_total_rejected += 1
        raise HTTPException(
            status_code=503,
            detail="GPU concurrency limit reached — request timed out after 30s",
        )

    async with api_state._gpu_lock:
        api_state._gpu_active_count += 1

    t_start = time.time()
    t_checkpoints = {}

    try:
        if api_state.runtime_mode_controller:
            api_state.runtime_mode_controller.apply_preferences(
                avatar_preference=request.avatar_mode_preference,
                audio_preference=request.audio_mode_preference,
            )
            api_state.runtime_mode_controller.refresh(api_state.triad_instance)

        sensory_data = {}
        kinect_fusion_status = None
        if api_state.kinect_fusion_adapter:
            api_state.kinect_fusion_adapter.refresh(getattr(api_state.triad_instance, "vision", None))
            kinect_fusion_status = api_state.kinect_fusion_adapter.get_status()
            sensory_data["kinect_fusion"] = kinect_fusion_status

        # 1. Decode Image (Client-Side Vision)
        t0 = time.time()
        if request.image_base64 and cv2 is not None:
            try:
                img_str = request.image_base64
                if "," in img_str:
                    img_str = img_str.split(",")[1]

                img_bytes = base64.b64decode(img_str)
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img is not None:
                    sensory_data['vision_frames'] = {0: img}
                    log_event("API", "Image decoded successfully.")
            except Exception as e:
                log_event("API", f"Image Decode Error: {e}", level="WARNING")
        elif request.image_base64:
            log_event("API", "Skipping image decode because OpenCV is unavailable.", level="WARNING")

        # 1.1 Multi-Snapshot support
        if request.snapshots and cv2 is not None:
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
                        sensory_data['vision_frames'][i] = img

                log_event("API", f"Decoded {len(request.snapshots)} client-side snapshots.")
            except Exception as e:
                log_event("API", f"Snapshots Decode Error: {e}", level="WARNING")
        elif request.snapshots:
            log_event("API", "Skipping snapshot decode because OpenCV is unavailable.", level="WARNING")

        t_checkpoints['decode'] = float(f"{time.time() - t0:.3f}")

        # 2. Generate with History
        t0 = time.time()
        history = []
        session_id = request.session_id
        if session_id:
            try:
                session_data = session_manager.get_session(session_id)
                if session_data:
                    history = session_data.get("messages", [])

                session_manager.add_message(session_id, "user", request.prompt, audio_url=request.user_audio_url)
            except Exception as e:
                log_event("API", f"Session Load/Save Error (Non-Fatal): {e}", level="WARNING")

        t_checkpoints['history'] = float(f"{time.time() - t0:.3f}")

        # 3. LLM Generation
        t0 = time.time()
        result = api_state.triad_instance.generate(request.prompt, sensory_data=sensory_data, history=history)
        t_checkpoints['llm'] = float(f"{time.time() - t0:.3f}")

        snapshot_url = result.get('snapshot_url')
        snapshot_urls = result.get('snapshot_urls', [])

        # 4. Handle Audio
        t0 = time.time()
        audio_url = None
        native_audio = None
        if request.voice_enabled:
            try:
                effective_audio_mode = "cascaded"
                if api_state.runtime_mode_controller:
                    effective_audio_mode = api_state.runtime_mode_controller.get_state().get("effective_audio_mode", "cascaded")

                if effective_audio_mode == "native":
                    log_event("API", "Native audio mode requested; feature flag fallback to cascaded TTS path.")
                    native_audio = _run_native_audio_stub(result.get('response', ''))

                api_state.triad_instance.speak(result['response'], play_now=False)
                audio_url = getattr(api_state.triad_instance, 'last_audio_url', '/audio/last_speech.mp3')
            except Exception as e:
                log_event("API", f"TTS Generation Error: {e}", level="WARNING")
        t_checkpoints['tts'] = float(f"{time.time() - t0:.3f}")

        generated_image_url = result.get('generated_image_url')

        # 5. Persistence & Vector DB
        t0 = time.time()
        if session_id:
             if api_state.vector_memory:
                 try:
                     description_text = result['response'][:500] if result.get('response') else "Visual snapshot captured."
                     api_state.vector_memory.add_memory(description_text, snapshot_url=snapshot_url)
                 except Exception as e:
                     log_event("API", f"Vector DB Insert Error: {e}", level="WARNING")

             try:
                  session = session_manager.get_session(session_id)
                  if session and session.get("messages"):
                      last_msg = session["messages"][-1]
                      if last_msg["role"] == "user":
                          last_msg["snapshot_url"] = snapshot_url
                          last_msg["snapshot_urls"] = snapshot_urls
                          session_manager.save_session(session_id, session)
                      else:
                          log_event("API", "Snapshot Persistence Warning: Last message was not user role", level="WARNING")
             except Exception as e:
                  log_event("API", f"Session Persistence Error (Snapshots): {e}", level="WARNING")

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
            "runtime_modes": api_state.runtime_mode_controller.get_state() if api_state.runtime_mode_controller else None
        }

    except Exception as e:
        log_event("API", f"Processing Error: {e}", level="ERROR")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        api_state._gpu_semaphore.release()
        async with api_state._gpu_lock:
            api_state._gpu_active_count -= 1
            api_state._gpu_total_served += 1
