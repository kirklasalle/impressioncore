#!/usr/bin/env python3
"""
ImpressionCore: Integration Test for Automated CPU Fallback

File: tests/integration/test_cpu_fallback_integration.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-27
Authors:
Kirk LaSalle - GitHub Copilot

Description:
Integration test to verify that automated CPU fallback offloads all model parameters and buffers to CPU when VRAM usage exceeds the threshold.

Usage:
pytest src/tests/integration/test_cpu_fallback_integration.py
"""

import pytest
import torch
from src.core.memory import dynamic_memory_manager as dmm
import logging

class DummyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = torch.nn.Linear(4, 4)
        self.register_buffer('dummy_buffer', torch.ones(4, 4))

@pytest.fixture
def dummy_model_cuda():
    model = DummyModel()
    if torch.cuda.is_available():
        model = model.cuda()
    return model

@pytest.fixture
def memory_manager_log(caplog):
    caplog.set_level(logging.INFO, logger="impressioncore.memory")
    return caplog

def test_automated_cpu_fallback_triggers_and_offloads(dummy_model_cuda, memory_manager_log):
    """
    Simulate VRAM threshold and verify all model params/buffers are offloaded to CPU.
    """
    vram_threshold = 0.0001  # triggers fallback immediately
    stop_flag = [False]

    def stop_condition():
        return stop_flag[0]

    # Patch should_offload_to_cpu to always return True
    orig_should_offload = dmm.should_offload_to_cpu
    dmm.should_offload_to_cpu = lambda threshold: True

    try:
        dmm.automated_cpu_fallback(
            dummy_model_cuda,
            vram_threshold=vram_threshold,
            check_interval=0.01,
            stop_condition=lambda: True
        )
        # All params and buffers should be on CPU
        for param in dummy_model_cuda.parameters():
            assert not param.is_cuda, "Parameter should be on CPU after fallback."
        for buffer in dummy_model_cuda.buffers():
            assert not buffer.is_cuda, "Buffer should be on CPU after fallback."
        # Log should contain fallback event
        assert any("cpu_fallback_triggered" in m.lower() for m in memory_manager_log.text.splitlines()), "CPU fallback event should be logged."
    finally:
        dmm.should_offload_to_cpu = orig_should_offload
