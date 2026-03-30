
import logging
import threading
import time
from collections.abc import Callable
from typing import Any

from src.orchestrator.system_logger import log_event

logger = logging.getLogger(__name__)

class SensoryHotSwapManager:
    """
    Central hub for hot-swappable hardware states.
    Monitors all sensory layers and manages device recovery.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_manager()
            return cls._instance

    def _init_manager(self):
        self.device_states = {
            "vision": "OFFLINE",
            "audio": "OFFLINE",
            "active_devices": {}
        }
        self.failure_counts = {"vision": 0, "audio": 0}
        self.callbacks: list[Callable[[str, str, dict[str, Any]], None]] = []
        self.learning_database_path = "logs/hardware_intelligence.json"

        # Ensure log directory exists
        import os
        os.makedirs("logs", exist_ok=True)

        log_event("HOTSWAP", "Sensory Hot-Swap Manager Initialized.")

    def register_callback(self, callback: Callable[[str, str, dict[str, Any]], None]):
        """Registers a function to be called on any hardware state change."""
        self.callbacks.append(callback)

    def report_state(self, layer: str, state: str, metadata: dict[str, Any] | None = None):
        """
        Sensory layers call this to report their current status.
        Triggers re-discovery if a critical layer goes OFFLINE.
        """
        old_state = self.device_states.get(layer)
        if old_state != state:
            self.device_states[layer] = state
            event_msg = f"Hardware State Change [{layer}]: {old_state} -> {state}"
            log_event("HOTSWAP", event_msg)

            # Update learning database
            self._update_learning_metadata(layer, state, metadata)

            # Notify Triad/Executive
            for cb in self.callbacks:
                cb(layer, state, metadata or {})

    def get_recovery_suggestion(self, layer: str) -> str:
        """Returns a learned suggestion based on failure history."""
        if self.failure_counts.get(layer, 0) > 3:
            return "recommend_sidelining"
        return "attempt_restart"

    def _update_learning_metadata(self, layer: str, state: str, metadata: dict[str, Any] | None):
        """Persists state change to the hardware database for future learning."""
        try:
            import json
            from pathlib import Path
            db_path = Path(self.learning_database_path)
            data = {}
            if db_path.exists():
                with open(db_path) as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}

            # Record the event in a historical log within the JSON
            # Legacy fix: If data is a list, convert to dict
            if isinstance(data, list):
                data = {"history": data}
            elif "history" not in data:
                data["history"] = []

            event = {
                "timestamp": time.time(),
                "layer": layer,
                "state": state,
                "metadata": metadata,
                "suggestion": self.get_recovery_suggestion(layer)
            }

            # Update failure counts logic (simple heuristic)
            if state in ["OFFLINE", "LOST"]:
                self.failure_counts[layer] = self.failure_counts.get(layer, 0) + 1
            elif state == "ACTIVE":
                self.failure_counts[layer] = 0 # Reset on success

            data["history"].append(event)
            # Keep history manageable
            data["history"] = data["history"][-100:]

            with open(db_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to update hardware learning database: {e}")

# Singleton Access
hotswap_manager = SensoryHotSwapManager()
