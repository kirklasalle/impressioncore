import logging
import json
import time
from typing import Dict, Any, Optional

try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

from .camera import get_active_camera, BaseCamera

# Setup logging
logger = logging.getLogger("OrbAgent")

class OrbAgent:
    """
    High-level API for AI/LLM agents to control OrbOS Camera hardware.
    Supports Orbit and Kinect backends via BaseCamera interface.
    """

    def __init__(self):
        self._cam: Optional[BaseCamera] = None
        self._connected = False
        # Do NOT initialize a default camera here. 
        # User must select one via the UI or API.

    def sync_camera(self, camera_type: Optional[str] = None):
        """Syncs the agent's camera handle with the global active camera."""
        try:
            self._cam = get_active_camera(camera_type)
            if self._cam:
                if not self._cam.is_open:
                    self._cam.open()
                self._connected = self._cam.is_open
            else:
                self._connected = False
            logger.info(f"OrbAgent: Synced to {camera_type or 'None'} camera.")
        except Exception as e:
            logger.error(f"OrbAgent: Failed to sync camera: {e}")
            self._connected = False

    def move(self, direction: str, amount: int = 10) -> Dict[str, Any]:
        if not self._connected or not self._cam:
            return {"success": False, "message": "Camera hardware not connected."}

        direction = direction.lower().strip()
        try:
            if direction == "left":
                # Digital pan relative
                if hasattr(self._cam, '_motor'): self._cam._motor.move_relative(100, 0)
            elif direction == "right":
                if hasattr(self._cam, '_motor'): self._cam._motor.move_relative(-100, 0)
            elif direction == "up":
                self._cam.tilt += amount
            elif direction == "down":
                self._cam.tilt -= amount
            else:
                return {"success": False, "message": f"Unknown direction '{direction}'."}
            
            return {"success": True, "message": f"Moved {direction} done."}
        except Exception as e:
            return {"success": False, "message": f"Error executing move: {e}"}

    def reset(self) -> Dict[str, Any]:
        if not self._connected or not self._cam:
            return {"success": False, "message": "Camera hardware not connected."}
        try:
            self._cam.pan = 0
            self._cam.tilt = 0
            if hasattr(self._cam, '_motor'): self._cam._motor.reset()
            return {"success": True, "message": "Camera reset."}
        except Exception as e:
             return {"success": False, "message": f"Error executing reset: {e}"}

    def listen(self, duration: float = 1.0) -> Dict[str, Any]:
        """Listens for audio, supporting both Orbit and Kinect microphones."""
        if not AUDIO_AVAILABLE:
            return {"success": False, "message": "Audio libraries not installed."}
            
        try:
            devices = sd.query_devices()
            target_id = None
            search_keywords = ['Kinect', 'Logitech', 'Orbit']
            
            for i, dev in enumerate(devices):
                name = dev.get('name', 'Unknown')
                if any(kw in name for kw in search_keywords) and dev['max_input_channels'] > 0:
                    target_id = i
                    if "Kinect" in name and "Kinect" in str(type(self._cam)):
                        break 
            
            if target_id is None:
                return {"success": False, "message": "No compatible microphone found."}

            logger.info(f"OrbAgent: Listening on Device {target_id} for {duration}s...")
            fs = 44100
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=target_id)
            sd.wait()
            
            amplitude = np.max(np.abs(recording))
            detected = amplitude > 0.001
            
            return {
                "success": True,
                "message": f"Audio captured via {devices[target_id]['name']}.",
                "max_amplitude": float(amplitude),
                "signal_detected": detected
            }

        except Exception as e:
            return {"success": False, "message": f"Audio capture error: {e}"}

    def status(self) -> Dict[str, Any]:
        cam_type = "Kinect" if "Kinect" in str(type(self._cam)) else "Orbit"
        return {
            "connected": self._connected,
            "can_move": self._connected,
            "camera_type": cam_type,
            "audio_available": AUDIO_AVAILABLE,
            "mode": f"{cam_type} Native" if cam_type == "Kinect" else "UVC"
        }
