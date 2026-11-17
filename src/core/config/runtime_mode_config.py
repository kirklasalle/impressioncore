import os
from dataclasses import dataclass


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_choice_env(name: str, default: str, allowed: set[str]) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip().lower()
    if value in allowed:
        return value
    return default


@dataclass
class RuntimeModeConfig:
    """Configuration for runtime mode arbitration and hybrid audio policy."""

    avatar_mode_default: str = "auto"  # auto|2d|video
    audio_mode_default: str = "hybrid"  # hybrid|cascaded|native
    native_audio_enabled: bool = False
    vram_switch_threshold_gb: float = 3.2
    fps_switch_threshold: float = 18.0



def load_runtime_mode_config() -> RuntimeModeConfig:
    """Load runtime mode config from environment variables with safe defaults."""
    return RuntimeModeConfig(
        avatar_mode_default=_get_choice_env(
            "IMPRESSIONCORE_AVATAR_MODE_DEFAULT",
            "auto",
            {"auto", "2d", "video"},
        ),
        audio_mode_default=_get_choice_env(
            "IMPRESSIONCORE_AUDIO_MODE_DEFAULT",
            "hybrid",
            {"hybrid", "cascaded", "native"},
        ),
        native_audio_enabled=_get_bool_env("IMPRESSIONCORE_NATIVE_AUDIO_ENABLED", False),
        vram_switch_threshold_gb=_get_float_env("IMPRESSIONCORE_VRAM_SWITCH_THRESHOLD_GB", 3.2),
        fps_switch_threshold=_get_float_env("IMPRESSIONCORE_FPS_SWITCH_THRESHOLD", 18.0),
    )
