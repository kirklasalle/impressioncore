"""Unit tests for src.core.config.config_manager.ConfigManager."""

import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.core.config.config_manager import ConfigManager


@pytest.fixture
def config_dir(tmp_path):
    """Create a temporary config directory with a preset file."""
    preset = {
        "memory_settings": {
            "memory_fraction": 0.75,
            "use_fp16": True,
            "enable_gradient_checkpointing": True,
            "max_batch_size": {"small_model": 16, "medium_model": 8, "large_model": 2},
        },
        "inference_settings": {"max_length": 512, "temperature": 0.7},
        "training_settings": {"lr": 3e-5, "epochs": 5},
    }
    preset_path = tmp_path / "test_preset.json"
    preset_path.write_text(json.dumps(preset))
    return tmp_path


class TestConfigManagerInit:
    def test_default_init(self):
        cm = ConfigManager()
        assert cm.config == {}
        assert cm.preset_name is None

    def test_custom_init(self, config_dir):
        cm = ConfigManager(config_path=config_dir, preset_name="test_preset.json")
        assert cm.config_path == config_dir
        assert cm.preset_name == "test_preset.json"


class TestLoadConfig:
    def test_loads_preset(self, config_dir):
        cm = ConfigManager(config_path=config_dir, preset_name="test_preset.json")
        result = cm.load_config()
        assert result["memory_settings"]["memory_fraction"] == 0.75
        assert result["inference_settings"]["max_length"] == 512

    def test_override_preset_name(self, config_dir):
        cm = ConfigManager(config_path=config_dir)
        result = cm.load_config("test_preset.json")
        assert cm.preset_name == "test_preset.json"
        assert "memory_settings" in result

    def test_missing_preset_returns_empty(self, tmp_path):
        cm = ConfigManager(config_path=tmp_path, preset_name="nonexistent.json")
        result = cm.load_config()
        assert result == {}


class TestGetSettings:
    def test_get_inference_settings(self, config_dir):
        cm = ConfigManager(config_path=config_dir, preset_name="test_preset.json")
        cm.load_config()
        settings = cm.get_inference_settings()
        assert settings["temperature"] == 0.7

    def test_get_training_settings(self, config_dir):
        cm = ConfigManager(config_path=config_dir, preset_name="test_preset.json")
        cm.load_config()
        settings = cm.get_training_settings()
        assert settings["lr"] == 3e-5
        assert settings["epochs"] == 5

    def test_auto_loads_on_first_access(self, config_dir):
        cm = ConfigManager(config_path=config_dir, preset_name="test_preset.json")
        # Don't call load_config first
        settings = cm.get_inference_settings()
        # Should auto-load and return settings
        assert isinstance(settings, dict)


class TestGetOptimalBatchSize:
    def test_returns_preset_value(self, config_dir):
        cm = ConfigManager(config_path=config_dir, preset_name="test_preset.json")
        cm.load_config()
        assert cm.get_optimal_batch_size("small_model") == 16
        assert cm.get_optimal_batch_size("medium_model") == 8
        assert cm.get_optimal_batch_size("large_model") == 2

    def test_returns_default_for_unknown_type(self, config_dir):
        cm = ConfigManager(config_path=config_dir, preset_name="test_preset.json")
        cm.load_config()
        assert cm.get_optimal_batch_size("unknown_model") == 1


class TestDetectHardware:
    @patch("torch.cuda.is_available", return_value=False)
    def test_cpu_fallback(self, _mock):
        cm = ConfigManager()
        assert cm.detect_hardware() == "cpu_preset.json"

    @patch("torch.cuda.is_available", return_value=True)
    @patch("torch.cuda.get_device_name", return_value="NVIDIA GeForce GTX 1050 Ti")
    def test_gtx_1050ti(self, _name, _avail):
        cm = ConfigManager()
        assert cm.detect_hardware() == "gtx_1050ti_preset.json"

    @patch("torch.cuda.is_available", return_value=True)
    @patch("torch.cuda.get_device_name", return_value="NVIDIA GeForce RTX 3090")
    def test_rtx_card(self, _name, _avail):
        cm = ConfigManager()
        assert cm.detect_hardware() == "rtx_preset.json"

    @patch("torch.cuda.is_available", return_value=True)
    @patch("torch.cuda.get_device_name", return_value="NVIDIA A100")
    def test_datacenter_gpu(self, _name, _avail):
        cm = ConfigManager()
        assert cm.detect_hardware() == "datacenter_preset.json"
