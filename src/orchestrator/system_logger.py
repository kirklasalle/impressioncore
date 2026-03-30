import json
import logging
import os
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class LogEntry:
    timestamp: str = field(default_factory=lambda: datetime.isoformat(datetime.now()))
    component: str = "GENERIC"
    level: str = "INFO"
    message: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    modality: str | None = None
    confidence: float = 1.0

class SystemLogManager:
    """
    World-class centralized logging system for ImpressionCore.
    Singleton-style management of system-wide observability.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.buffer: list[LogEntry] = []
        self.max_buffer_size = 1000
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, f"system_{int(time.time())}.jsonl")

        # Configure standard python logger to pipe through here
        logging.basicConfig(level=logging.INFO)
        self.py_logger = logging.getLogger("ImpressionCore")
        self.current_log_file = self.log_file # Keep reference for accessibility

    def log(self, component: str, message: str, level: str = "INFO",
            payload: dict[str, Any] | None = None, modality: str | None = None, confidence: float = 1.0):
        """Unified logging entry point."""
        entry = LogEntry(
            component=component.upper(),
            level=level.upper(),
            message=message,
            payload=payload or {},
            modality=modality,
            confidence=confidence
        )

        # 1. Internal Buffer
        with self._lock:
            self.buffer.append(entry)
            if len(self.buffer) > self.max_buffer_size:
                self.buffer.pop(0)

        # 2. Console Output (Standard format)
        log_str = f"[{entry.timestamp}] [{entry.component}] {entry.level}: {entry.message}"
        try:
            if entry.level == "ERROR":
                self.py_logger.error("%s", log_str)
            elif entry.level == "WARNING":
                self.py_logger.warning("%s", log_str)
            else:
                self.py_logger.info("%s", log_str)
        except Exception as e:
            # Fallback to direct print if logger crashes to avoid killing the thread
            print(f"INTERNAL LOGGER ERROR (FALLBACK): {log_str} | Error: {e}")

        # 3. Persistent Storage (JSONL)
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(asdict(entry)) + "\n")
        except Exception as e:
            print(f"CRITICAL LOG FAILURE: {e}")

    def get_logs(self, component: str | None = None, level: str | None = None) -> list[dict[str, Any]]:
        """Retrieve and manipulate log data."""
        with self._lock:
            filtered = [asdict(e) for e in self.buffer]

        if component:
            filtered = [e for e in filtered if e["component"] == component.upper()]
        if level:
            filtered = [e for e in filtered if e["level"] == level.upper()]

        return filtered

    def clear_buffer(self):
        with self._lock:
            self.buffer = []

# Global Access Instance
sys_logger = SystemLogManager()

def log_event(component: str, message: str, **kwargs):
    sys_logger.log(component, message, **kwargs)

if __name__ == "__main__":
    # Test
    log_event("TRIAD", "System initialized", payload={"vram": "1.2GB"})
    log_event("NEXUS", "Command executed: (LOG 'Hello')", level="INFO")

    print(f"Current Logs: {len(sys_logger.get_logs())}")
    print(f"Log Archive: {sys_logger.log_file}")
