"""Unit tests for src.core.config.runtime_mode_config."""

import os
from unittest.mock import patch

from src.core.config.runtime_mode_config import (
    _get_bool_env,
    _get_float_env,
    _get_choice_env,
    RuntimeModeConfig,
    load_runtime_mode_config,
)


class TestGetBoolEnv:
    def test_default_when_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            assert _get_bool_env("NONEXISTENT", True) is True
            assert _get_bool_env("NONEXISTENT", False) is False

    def test_truthy_values(self):
        for val in ("1", "true", "yes", "on", "TRUE", " True "):
            with patch.dict(os.environ, {"TEST_VAR": val}):
                assert _get_bool_env("TEST_VAR", False) is True

    def test_falsy_values(self):
        for val in ("0", "false", "no", "off", "anything"):
            with patch.dict(os.environ, {"TEST_VAR": val}):
                assert _get_bool_env("TEST_VAR", True) is False


class TestGetFloatEnv:
    def test_default_when_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            assert _get_float_env("NONEXISTENT", 3.14) == 3.14

    def test_valid_float(self):
        with patch.dict(os.environ, {"TEST_VAR": "2.5"}):
            assert _get_float_env("TEST_VAR", 0.0) == 2.5

    def test_invalid_float_returns_default(self):
        with patch.dict(os.environ, {"TEST_VAR": "not_a_number"}):
            assert _get_float_env("TEST_VAR", 9.9) == 9.9


class TestGetChoiceEnv:
    def test_default_when_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            assert _get_choice_env("NONEXISTENT", "auto", {"auto", "2d"}) == "auto"

    def test_valid_choice(self):
        with patch.dict(os.environ, {"TEST_VAR": "2d"}):
            assert _get_choice_env("TEST_VAR", "auto", {"auto", "2d"}) == "2d"

    def test_invalid_choice_returns_default(self):
        with patch.dict(os.environ, {"TEST_VAR": "invalid"}):
            assert _get_choice_env("TEST_VAR", "auto", {"auto", "2d"}) == "auto"


class TestRuntimeModeConfig:
    def test_defaults(self):
        cfg = RuntimeModeConfig()
        assert cfg.avatar_mode_default == "auto"
        assert cfg.audio_mode_default == "hybrid"
        assert cfg.native_audio_enabled is False
        assert cfg.vram_switch_threshold_gb == 3.2
        assert cfg.fps_switch_threshold == 18.0


class TestLoadRuntimeModeConfig:
    def test_loads_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = load_runtime_mode_config()
            assert cfg.avatar_mode_default == "auto"
            assert cfg.audio_mode_default == "hybrid"

    def test_env_overrides(self):
        env = {
            "IMPRESSIONCORE_AVATAR_MODE_DEFAULT": "2d",
            "IMPRESSIONCORE_AUDIO_MODE_DEFAULT": "native",
            "IMPRESSIONCORE_NATIVE_AUDIO_ENABLED": "true",
            "IMPRESSIONCORE_VRAM_SWITCH_THRESHOLD_GB": "2.0",
            "IMPRESSIONCORE_FPS_SWITCH_THRESHOLD": "30.0",
        }
        with patch.dict(os.environ, env):
            cfg = load_runtime_mode_config()
            assert cfg.avatar_mode_default == "2d"
            assert cfg.audio_mode_default == "native"
            assert cfg.native_audio_enabled is True
            assert cfg.vram_switch_threshold_gb == 2.0
            assert cfg.fps_switch_threshold == 30.0
