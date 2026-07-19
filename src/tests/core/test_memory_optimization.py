"""Unit tests for memory optimization utilities (dynamic precision and monitoring)."""

import gc
import logging
from unittest.mock import MagicMock, patch

import pytest
import torch

from src.core.utils.memory_optimization.dynamic_precision import (
    _adjust_model_precision,
    disable_dynamic_precision,
    enable_dynamic_precision,
    setup_dynamic_precision,
)
from src.core.utils.memory_optimization.monitoring import (
    CPUMemoryMonitor,
    GPUMemoryMonitor,
    MemoryMonitor,
    estimate_memory_requirements,
    monitor_memory_usage,
)


@pytest.fixture
def mock_model():
    model = torch.nn.Linear(10, 10)
    # Mock named_modules
    mock_module = torch.nn.Linear(5, 5)
    model.add_module("classifier", mock_module)
    return model


def test_estimate_memory_requirements():
    res = estimate_memory_requirements(
        model_size=1000000,
        batch_size=32,
        sequence_length=128,
        dtype=torch.float16,
        include_optimizer=True,
        optimizer_type="adam",
    )
    assert "model_memory_mb" in res
    assert "total_estimated_memory_mb" in res
    assert res["model_memory_mb"] == pytest.approx(1.9073, rel=1e-2)


def test_monitor_memory_usage():
    with patch("psutil.Process") as mock_proc:
        mock_proc.return_value.memory_info.return_value.rss = 100 * 1024 * 1024
        mock_proc.return_value.cpu_percent.return_value = 5.0
        
        with patch("psutil.virtual_memory") as mock_vm:
            mock_vm.return_value.percent = 50.0
            
            stats = monitor_memory_usage(device="cpu")
            assert stats["cpu_memory_mb"] == 100.0
            assert stats["system_memory_percent"] == 50.0


def test_memory_monitor_class():
    callback_called = False
    def alert_callback(stats):
        nonlocal callback_called
        callback_called = True

    monitor = MemoryMonitor(
        monitoring_interval=0.05,
        alert_threshold=80.0,
        alert_callback=alert_callback,
    )
    
    # Mock _monitor_memory
    monitor._monitor_memory = MagicMock(return_value={"percent": 85.0})
    
    with monitor:
        # Let it run once
        import time
        time.sleep(0.1)
        
    assert callback_called
    assert len(monitor.get_memory_history()) > 0


def test_gpu_memory_monitor():
    # Mock cuda for testing VRAM monitoring on systems without GPU / during test run
    with patch("torch.cuda.is_available", return_value=True):
        with patch("torch.cuda.device_count", return_value=1):
            with patch("torch.cuda.empty_cache") as mock_empty:
                with patch("torch.cuda.synchronize") as mock_sync:
                    with patch("torch.cuda.memory_allocated", return_value=1024*1024*512):
                        with patch("torch.cuda.memory_reserved", return_value=1024*1024*1024):
                            with patch("torch.cuda.get_device_name", return_value="GeForce GTX 1050 Ti"):
                                with patch("torch.cuda.get_device_properties") as mock_props:
                                    mock_props.return_value.total_memory = 1024*1024*1024*4
                                    
                                    monitor = GPUMemoryMonitor(device_id=0)
                                    stats = monitor.get_memory_stats()
                                    assert stats["allocated_mb"] == 512.0
                                    assert stats["total_mb"] == 4096.0
                                    assert stats["device_name"] == "GeForce GTX 1050 Ti"


def test_cpu_memory_monitor():
    with patch("psutil.Process") as mock_proc:
        mock_proc.return_value.memory_info.return_value.rss = 200 * 1024 * 1024
        mock_proc.return_value.memory_percent.return_value = 10.0
        
        monitor = CPUMemoryMonitor(include_system_memory=False)
        stats = monitor.get_memory_stats()
        assert stats["process"]["rss_mb"] == 200.0
        assert stats["process"]["percent"] == 10.0


def test_setup_dynamic_precision(mock_model):
    model = setup_dynamic_precision(
        mock_model,
        target_memory_usage=0.7,
        precision_hierarchy=[torch.float16, torch.float32],
        critical_modules=["classifier"],
    )
    
    assert hasattr(model, "_dynamic_precision_config")
    assert model._dynamic_precision_config["target_memory_usage"] == 0.7
    assert model._dynamic_precision_config["enabled"] is True
    
    # Disable and enable
    disable_dynamic_precision(model)
    assert model._dynamic_precision_config["enabled"] is False
    
    enable_dynamic_precision(model)
    assert model._dynamic_precision_config["enabled"] is True


def test_adjust_model_precision(mock_model):
    model = setup_dynamic_precision(
        mock_model,
        precision_hierarchy=[torch.float16, torch.float32],
        critical_modules=["classifier"],
    )
    
    # classifier should be kept in float32 when model is adjusted to float16
    _adjust_model_precision(model, torch.float16)
    
    assert model.weight.dtype == torch.float16
    assert model.classifier.weight.dtype == torch.float32
