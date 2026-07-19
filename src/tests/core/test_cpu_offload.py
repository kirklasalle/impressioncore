"""Unit tests for CPU offloading functionality."""

from unittest.mock import MagicMock, patch
import pytest
import torch
import torch.nn as nn

from src.core.utils.memory_optimization.cpu_offload import (
    OffloadConfig,
    selective_cpu_offload,
    enable_sequential_cpu_offload,
    offload_text_encoder,
    fetch_layer_to_gpu,
)

class DummyPipeline:
    def __init__(self):
        self.text_encoder = nn.Linear(5, 5)
        self.unet = nn.Linear(5, 5)
        self.vae = nn.Linear(5, 5)
        
    def _encode_prompt(self, prompt):
        return "encoded_prompt"

def test_offload_config():
    config = OffloadConfig(
        modules_to_offload=["layer1"],
        keep_in_gpu=["classifier"],
        offload_buffers=False,
        pin_memory=False,
        force_eval_mode=True,
    )
    assert config.modules_to_offload == ["layer1"]
    assert config.keep_in_gpu == ["classifier"]
    assert config.offload_buffers is False
    assert config.pin_memory is False
    assert config.force_eval_mode is True

def test_selective_cpu_offload_non_cuda():
    # If device type is cpu, selective_cpu_offload returns the model unmodified
    model = nn.Linear(5, 5)
    device = torch.device("cpu")
    out_model = selective_cpu_offload(model, device=device)
    assert out_model is model

def test_selective_cpu_offload_cuda():
    # Patch torch.cuda.is_available to return True
    with patch("torch.cuda.is_available", return_value=True):
        # Create a mock device that acts like a cuda device
        device = MagicMock()
        device.type = "cuda"
        
        model = nn.Sequential(
            nn.Linear(5, 5),
            nn.ReLU()
        )
        
        # Mock module.to so that it doesn't try to move to a real GPU device
        # but keeps track of calls, or does nothing.
        original_to = nn.Module.to
        
        def mock_to(self, target_device, *args, **kwargs):
            # Just return self and do not actually change device if it's our mock cuda device
            if target_device is device or (isinstance(target_device, str) and target_device.startswith("cuda")):
                return self
            # For CPU/other targets, use original to
            return original_to(self, target_device, *args, **kwargs)
            
        with patch.object(nn.Module, "to", autospec=True, side_effect=mock_to):
            # Mock pin_memory method on Tensor
            with patch("torch.Tensor.pin_memory", side_effect=lambda: torch.empty(1)):
                config = OffloadConfig(pin_memory=False)
                optimized_model = selective_cpu_offload(model, device=device, config=config)
                
                # Forward pass should run on CPU because weights and inputs stay on CPU
                input_tensor = torch.randn(2, 5)
                # Run forward
                res = optimized_model(input_tensor)
                assert res is not None
                # Check restore method
                assert hasattr(optimized_model, "_restore_original_execution")
                optimized_model._restore_original_execution()

def test_enable_sequential_cpu_offload():
    with patch("torch.cuda.is_available", return_value=True):
        pipeline = DummyPipeline()
        device = torch.device("cuda:0")
        
        # Test with pin_memory=False
        optimized_pipeline = enable_sequential_cpu_offload(
            pipeline, device=device, module_sequence=["text_encoder", "unet"], pin_memory=False
        )
        
        assert hasattr(optimized_pipeline, "move_module_to_device")
        # Call moving text_encoder to device
        optimized_pipeline.move_module_to_device("text_encoder")
        assert optimized_pipeline._active_module == "text_encoder"
        
        # Move unet to device
        optimized_pipeline.move_module_to_device("unet")
        assert optimized_pipeline._active_module == "unet"

def test_offload_text_encoder():
    with patch("torch.cuda.is_available", return_value=True):
        pipeline = DummyPipeline()
        device = torch.device("cuda:0")
        
        optimized = offload_text_encoder(pipeline, device=device)
        assert optimized._encode_prompt != DummyPipeline._encode_prompt
        
        res = optimized._encode_prompt("hello")
        assert res == "encoded_prompt"

def test_fetch_layer_to_gpu():
    with patch("torch.cuda.is_available", return_value=True):
        model = nn.Linear(5, 5)
        # Verify it doesn't crash on cuda
        fetch_layer_to_gpu(model, device=torch.device("cuda:0"))
