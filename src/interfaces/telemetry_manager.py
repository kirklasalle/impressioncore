
"""
ImpressionCore Telemetry Manager

Aggregates real-time metrics from:
- Hardware (CPU, RAM, GPU)
- Vision System (FPS, Active Cams, Detections)
- Audio System (Volume, Listen State)
- Agent0 (Thought Process, Token Usage - future)
- Network (Latency)

Broadcasts via WebSocket.
"""

import asyncio
import logging
import time
from typing import Any

import psutil
from fastapi import WebSocket

logger = logging.getLogger("Telemetry")

class TelemetryManager:
    def __init__(self, triad_instance=None):
        self.triad = triad_instance
        self.active_websockets: list[WebSocket] = []
        self.running = False
        self._loop_task = None
        self.last_broadcast = 0
        self.broadcast_interval = 0.05 # 20Hz updates (Biological smooth tracking)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_websockets.append(websocket)
        logger.info(f"Telemetry Client Connected. Total: {len(self.active_websockets)}")

        # Start loop if not running
        if not self.running:
            self.running = True
            if not self._loop_task:
                 self._loop_task = asyncio.create_task(self._broadcast_loop())

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_websockets:
            self.active_websockets.remove(websocket)
            logger.info(f"Telemetry Client Disconnected. Total: {len(self.active_websockets)}")

        if not self.active_websockets:
            self.running = False
            # We don't cancel the task aggressively to avoid errors, just let it idle or clean up

    async def _broadcast_loop(self):
        logger.info("Telemetry Broadcast Loop Started")
        while True:
            if not self.active_websockets:
                self.running = False
                logger.info("No clients, pausing telemetry loop.")
                self._loop_task = None
                break

            try:
                payload = self._gather_metrics()

                # Broadcast
                for ws in self.active_websockets[:]:
                    try:
                        await ws.send_json(payload)
                    except Exception as e:
                        # Stale connection
                        logger.warning(f"Failed to send telemetry, removing client: {e}")
                        if ws in self.active_websockets:
                            self.active_websockets.remove(ws)

                await asyncio.sleep(self.broadcast_interval)

            except Exception as e:
                logger.error(f"Telemetry Loop Error: {e}")
                await asyncio.sleep(1)

    def _gather_metrics(self) -> dict[str, Any]:
        """Collect all system metrics."""

        # 1. System Resources
        cpu_usage = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()

        # 2. Vision Metrics
        vision_stats = {
            "active": False,
            "fps": 0,
            "cameras": [],
            "inference_fps": 0
        }

        if self.triad and self.triad.vision:
            v = self.triad.vision
            vision_stats["active"] = getattr(self.triad, "vision_active", False)
            vision_stats["fps"] = getattr(v, "current_fps", 0) # Assumes prop exists or default
            vision_stats["inference_fps"] = getattr(v, "inference_fps_limit", 0)

            # Active cams
            for cam_id in v.caps:
                vision_stats["cameras"].append(str(cam_id))

            # Retrieve rich detections (including landmarks) from Vision layer
            detections = getattr(v, "latest_telemetry", {}).get("detections", {})
            vision_stats["detections"] = detections

            # Kinect fusion status is telemetry-safe and additive for UI/runtime monitors
            vision_stats["kinect_fusion"] = {
                "color_available": 98 in getattr(v, "caps", {}),
                "depth_available": bool(getattr(v, "depth_active", False)),
                "ir_available": bool(getattr(v, "ir_active", False)),
                "skeleton_available": getattr(v, "latest_skeleton", None) is not None,
            }

        # 3. Audio Metrics
        audio_stats = {
            "listening": False,
            "speaking": False
        }
        if self.triad:
             # Basic state checks if available
             pass

        runtime_modes = None
        if self.triad and hasattr(self.triad, "runtime_mode_controller"):
            controller = getattr(self.triad, "runtime_mode_controller")
            try:
                controller.refresh(self.triad)
                runtime_modes = controller.get_state()
            except Exception:
                runtime_modes = None

        return {
            "timestamp": time.time(),
            "system": {
                "cpu_percent": cpu_usage,
                "ram_percent": ram.percent,
                "ram_used_gb": round(ram.used / (1024**3), 2),
                "ram_total_gb": round(ram.total / (1024**3), 2)
            },
            "vision": vision_stats,
            "audio": audio_stats,
            "agent": {
                "status": "IDLE" # Placeholder for now
            },
            "runtime_modes": runtime_modes,
        }

# Global Instance
_telemetry_manager = None

def get_telemetry_manager(triad_instance=None):
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager(triad_instance)
    elif triad_instance and _telemetry_manager.triad is None:
        _telemetry_manager.triad = triad_instance
    return _telemetry_manager
