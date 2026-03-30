import time
from dataclasses import asdict, dataclass
from typing import Any

import psutil

from src.orchestrator.system_logger import log_event


@dataclass
class RuntimeModeState:
    """Tracks runtime mode preferences and active selections for 4GB operation."""

    avatar_mode_preference: str = "auto"  # auto|2d|video
    current_avatar_mode: str = "2d"  # 2d|video
    audio_mode_preference: str = "hybrid"  # hybrid|cascaded|native
    effective_audio_mode: str = "cascaded"  # cascaded|native
    native_audio_enabled: bool = False
    vram_switch_threshold_gb: float = 3.2
    fps_switch_threshold: float = 18.0
    last_update_ts: float = 0.0


class RuntimeModeController:
    """Chooses safe runtime modes based on user preference and live hardware pressure."""

    def __init__(
        self,
        native_audio_enabled: bool = False,
        avatar_mode_preference: str = "auto",
        audio_mode_preference: str = "hybrid",
        vram_switch_threshold_gb: float = 3.2,
        fps_switch_threshold: float = 18.0,
    ):
        self.state = RuntimeModeState(
            avatar_mode_preference=avatar_mode_preference,
            audio_mode_preference=audio_mode_preference,
            native_audio_enabled=native_audio_enabled,
            vram_switch_threshold_gb=vram_switch_threshold_gb,
            fps_switch_threshold=fps_switch_threshold,
        )

    def _normalize_avatar_preference(self, value: str | None) -> str:
        if value in {"auto", "2d", "video"}:
            return value
        return self.state.avatar_mode_preference

    def _normalize_audio_preference(self, value: str | None) -> str:
        if value in {"hybrid", "cascaded", "native"}:
            return value
        return self.state.audio_mode_preference

    def apply_preferences(self, avatar_preference: str | None = None, audio_preference: str | None = None) -> None:
        self.state.avatar_mode_preference = self._normalize_avatar_preference(avatar_preference)
        self.state.audio_mode_preference = self._normalize_audio_preference(audio_preference)
        log_event(
            "RUNTIME",
            (
                f"Runtime preferences updated: avatar={self.state.avatar_mode_preference}, "
                f"audio={self.state.audio_mode_preference}"
            ),
        )

    def refresh(self, triad_instance: Any = None) -> None:
        """Refreshes active modes using VRAM/FPS pressure and feature availability."""
        model_status = {}
        fps = 0.0
        if triad_instance and hasattr(triad_instance, "get_model_status"):
            try:
                model_status = triad_instance.get_model_status() or {}
            except Exception:
                model_status = {}

        vram_gb = float(model_status.get("vram_allocated_gb", 0.0) or 0.0)

        if triad_instance and getattr(triad_instance, "vision", None):
            try:
                # Prefer measured global fps if available
                perf = getattr(triad_instance.vision, "performance_stats", {}) or {}
                fps = float(perf.get("global_fps", 0.0) or 0.0)
                if fps <= 0.0:
                    fps = float(getattr(triad_instance.vision, "current_fps", 0.0) or 0.0)
            except Exception:
                fps = 0.0

        # Avatar arbitration
        pref = self.state.avatar_mode_preference
        if pref == "2d":
            self.state.current_avatar_mode = "2d"
        elif pref == "video":
            self.state.current_avatar_mode = "video"
        else:
            pressure_high = vram_gb >= self.state.vram_switch_threshold_gb
            perf_low = fps > 0.0 and fps < self.state.fps_switch_threshold
            self.state.current_avatar_mode = "2d" if pressure_high or perf_low else "video"

        # Audio policy
        audio_pref = self.state.audio_mode_preference
        if audio_pref == "cascaded":
            self.state.effective_audio_mode = "cascaded"
        elif audio_pref == "native":
            self.state.effective_audio_mode = "native" if self.state.native_audio_enabled else "cascaded"
        else:  # hybrid
            # Hybrid defaults to cascaded for reliability; can switch when native is enabled
            self.state.effective_audio_mode = "native" if self.state.native_audio_enabled else "cascaded"

        self.state.last_update_ts = time.time()

    def toggle_native_audio(self, enabled: bool) -> None:
        self.state.native_audio_enabled = bool(enabled)
        log_event("RUNTIME", f"Native audio feature set to: {self.state.native_audio_enabled}")

    def set_thresholds(self, vram_switch_threshold_gb: float | None = None, fps_switch_threshold: float | None = None) -> None:
        """Update arbitration thresholds used by auto avatar switching."""
        if vram_switch_threshold_gb is not None:
            self.state.vram_switch_threshold_gb = max(0.1, float(vram_switch_threshold_gb))
        if fps_switch_threshold is not None:
            self.state.fps_switch_threshold = max(1.0, float(fps_switch_threshold))

        log_event(
            "RUNTIME",
            (
                "Runtime thresholds updated: "
                f"vram_switch_threshold_gb={self.state.vram_switch_threshold_gb}, "
                f"fps_switch_threshold={self.state.fps_switch_threshold}"
            ),
        )

    def get_state(self) -> dict[str, Any]:
        snapshot = asdict(self.state)
        snapshot["ram_percent"] = psutil.virtual_memory().percent
        return snapshot
