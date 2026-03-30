#!/usr/bin/env python3
"""
ImpressionCore: Integration Test for Dynamic Memory Manager

File: tests/integration/test_dynamic_memory_manager_integration.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-27
Authors:
Kirk LaSalle - GitHub Copilot

Description:
Integration test to verify that the dynamic memory manager triggers offloading and logs memory events during a simulated memory-intensive inference run.

Test Scenario:
- Simulate inference with large tensors to approach VRAM threshold.
- Assert that the dynamic memory manager triggers offloading and logs the appropriate events.
- Optionally, simulate an OOM event and verify graceful handling.

Usage:
pytest src/tests/integration/test_dynamic_memory_manager_integration.py
"""

import pytest
import torch
from src.core.memory import dynamic_memory_manager as dmm
import logging

@pytest.fixture
def memory_manager_log(caplog):
    caplog.set_level(logging.INFO, logger="impressioncore.memory")
    return caplog


def test_dynamic_memory_manager_offload_and_logging(memory_manager_log):
    """
    Simulate memory-intensive inference and verify offload/logging.
    """
    # Simulate VRAM threshold (very low for test)
    vram_threshold = 0.0001  # MB, triggers offload immediately
    offload_triggered = []

    def fake_offload():
        offload_triggered.append(True)

    def fake_stop():
        return len(offload_triggered) > 0

    # Patch should_offload_to_cpu to always return True
    orig_should_offload = dmm.should_offload_to_cpu
    dmm.should_offload_to_cpu = lambda threshold: True

    try:
        dmm.monitor_and_manage_memory(
            check_interval=0.01,
            vram_threshold=vram_threshold,
            on_offload=fake_offload,
            stop_condition=fake_stop
        )
        assert offload_triggered, "Offload should have been triggered."
        # Check that log contains the offload event
        assert any("offload" in m.lower() for m in memory_manager_log.text.splitlines()), "Offload event should be logged."
    finally:
        dmm.should_offload_to_cpu = orig_should_offload


def test_dynamic_memory_manager_oom_logging(memory_manager_log):
    """
    Simulate an OOM event and verify logging.
    """
    dmm.log_memory_event("OOM error", details="Simulated OOM for integration test")
    assert any("oom error" in m.lower() for m in memory_manager_log.text.splitlines()), "OOM event should be logged."
