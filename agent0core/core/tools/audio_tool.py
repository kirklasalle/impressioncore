"""
Audio Tool - Neural Triad Integration

Created: January 13, 2026
Author: ImpressionCore Team

Tool for Agent0Core to interact with ImpressionCore's audio systems.
Connects to real AudioEngine and speech processing implementations.
"""

import logging
import sys
from pathlib import Path
from typing import Any

# Add ImpressionCore src to path for imports
_project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_project_root / "src"))

from ..governance import require_law_compliance

logger = logging.getLogger("agent0core.tools.audio")


class AudioTool:
    """
    Tool for interacting with ImpressionCore's audio systems.

    Supports:
    - 4-microphone array (beamforming)
    - Direction of Arrival (DOA) detection
    - Voice Activity Detection (VAD)
    - Audio device management
    - RMS level monitoring
    """

    name = "audio_tool"
    description = "Control ImpressionCore's audio systems (Neural Triad Audio Engine)"

    def __init__(self):
        """Initialize the audio tool."""
        self._audio_engine = None
        self._initialized = False
        logger.info("AudioTool initialized (lazy loading enabled)")

    def _lazy_load_audio_engine(self) -> bool:
        """Lazy load the audio engine."""
        if self._audio_engine is not None:
            return True

        try:
            from orchestrator.audio_engine import AudioEngine
            self._audio_engine = AudioEngine()
            logger.info("AudioEngine loaded")
            return True
        except ImportError as e:
            logger.warning(f"AudioEngine not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize AudioEngine: {e}")
            return False

    @require_law_compliance
    async def execute(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute an audio action.

        Args:
            action: The action to perform
            params: Optional parameters

        Returns:
            Result dictionary
        """
        params = params or {}

        if action == "list_devices":
            return await self._list_devices()
        elif action == "refresh_devices":
            return await self._refresh_devices()
        elif action == "start_stream":
            return await self._start_stream(params.get("device_index", 0))
        elif action == "stop_stream":
            return await self._stop_stream()
        elif action == "get_telemetry":
            return await self._get_telemetry()
        elif action == "get_doa":
            return await self._get_doa()
        elif action == "verify_device":
            return await self._verify_device(params.get("device_index", 0))
        else:
            return {"error": f"Unknown action: {action}", "available_actions": [
                "list_devices", "refresh_devices", "start_stream", "stop_stream",
                "get_telemetry", "get_doa", "verify_device"
            ]}

    async def _list_devices(self) -> dict[str, Any]:
        """List available audio devices."""
        if not self._lazy_load_audio_engine():
            return {"error": "AudioEngine not available"}

        try:
            devices = self._audio_engine.devices
            return {
                "devices": [
                    {
                        "index": dev.get("index"),
                        "name": dev.get("name"),
                        "channels": dev.get("input_channels"),
                        "sample_rate": dev.get("sample_rate"),
                    }
                    for dev in devices
                ],
                "count": len(devices),
            }
        except Exception as e:
            return {"error": str(e)}

    async def _refresh_devices(self) -> dict[str, Any]:
        """Force refresh of audio device list."""
        if not self._lazy_load_audio_engine():
            return {"error": "AudioEngine not available"}

        try:
            self._audio_engine.refresh_devices()
            devices = self._audio_engine.devices
            return {
                "status": "success",
                "message": "Device list refreshed",
                "count": len(devices),
            }
        except Exception as e:
            return {"error": str(e)}

    async def _start_stream(self, device_index: int) -> dict[str, Any]:
        """Start audio stream from a device."""
        if not self._lazy_load_audio_engine():
            return {"error": "AudioEngine not available"}

        try:
            success = self._audio_engine.start_stream(device_index)
            if success:
                return {
                    "status": "success",
                    "device_index": device_index,
                    "message": "Audio stream started",
                }
            else:
                return {
                    "status": "failed",
                    "device_index": device_index,
                    "message": "Failed to start stream",
                }
        except Exception as e:
            return {"error": str(e)}

    async def _stop_stream(self) -> dict[str, Any]:
        """Stop active audio stream."""
        if not self._lazy_load_audio_engine():
            return {"error": "AudioEngine not available"}

        try:
            self._audio_engine.stop_stream()
            return {"status": "success", "message": "Audio stream stopped"}
        except Exception as e:
            return {"error": str(e)}

    async def _get_telemetry(self) -> dict[str, Any]:
        """Get current audio telemetry (DOA, VAD, RMS)."""
        if not self._lazy_load_audio_engine():
            return {"error": "AudioEngine not available"}

        try:
            telemetry = self._audio_engine.get_telemetry()
            return {
                "status": telemetry.get("status", "UNKNOWN"),
                "angle": telemetry.get("angle", 0),
                "vad": telemetry.get("vad", False),
                "rms": telemetry.get("rms", []),
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_doa(self) -> dict[str, Any]:
        """Get Direction of Arrival for audio source."""
        if not self._lazy_load_audio_engine():
            return {"error": "AudioEngine not available"}

        try:
            telemetry = self._audio_engine.get_telemetry()
            return {
                "angle": telemetry.get("angle", 0),
                "vad_active": telemetry.get("vad", False),
            }
        except Exception as e:
            return {"error": str(e)}

    async def _verify_device(self, device_index: int) -> dict[str, Any]:
        """Verify a device is working by capturing test audio."""
        if not self._lazy_load_audio_engine():
            return {"error": "AudioEngine not available"}

        try:
            is_healthy = self._audio_engine.verify_device_health(device_index)
            return {
                "device_index": device_index,
                "healthy": is_healthy,
                "message": "Device verified" if is_healthy else "Device verification failed",
            }
        except Exception as e:
            return {"error": str(e)}

    def cleanup(self):
        """Release all audio resources."""
        if self._audio_engine:
            self._audio_engine.close()
            self._audio_engine = None
        logger.info("AudioTool resources released")
