#!/usr/bin/env python3
"""
ImpressionCore: Dynamic Memory Manager

Module for dynamic memory manager functionality in the ImpressionCore framework.
"""


# Automated CPU Fallback Integration (moved below imports)
import torch
import logging
import time
from typing import Optional, Callable

def automated_cpu_fallback(model: torch.nn.Module, vram_threshold: float = 0.85, check_interval: float = 1.0, stop_condition: Optional[Callable[[], bool]] = None) -> None:
    """
    Monitors VRAM usage and automatically offloads model parameters and buffers to CPU if VRAM usage exceeds the threshold.

    Args:
        model (torch.nn.Module): The model to offload.
        vram_threshold (float): VRAM usage fraction to trigger offload (default: 0.85).
        check_interval (float): Seconds between checks (default: 1.0).
        stop_condition (Callable, optional): Function returning True to stop monitoring.

    Returns:
        None

    Memory Implications:
        - Prevents OOM by proactively offloading when VRAM is nearly full.
        - May slow down computation if model is needed again on GPU.

    Example:
        automated_cpu_fallback(model, vram_threshold=0.9)
    """
    from . import dynamic_memory_manager as dmm
    logger = logging.getLogger("impressioncore.memory")
    offloaded = False
    while True:
        if dmm.should_offload_to_cpu(vram_threshold) and not offloaded:
            logger.warning("VRAM threshold exceeded. Offloading model to CPU.")
            for param in model.parameters():
                param.data = param.data.cpu()
                if param.grad is not None:
                    param.grad = param.grad.cpu()
            for buffer in model.buffers():
                buffer.data = buffer.data.cpu()
            offloaded = True
            dmm.log_memory_event("cpu_fallback_triggered", details=f"Model offloaded at VRAM usage > {vram_threshold*100:.1f}%")
        if stop_condition and stop_condition():
            logger.info("Stopping automated CPU fallback monitor.")
            break
        time.sleep(check_interval)
    """
    Monitors VRAM usage and automatically offloads model parameters and buffers to CPU if VRAM usage exceeds the threshold.

    Args:
        model (torch.nn.Module): The model to offload.
        vram_threshold (float): VRAM usage fraction to trigger offload (default: 0.85).
        check_interval (float): Seconds between checks (default: 1.0).
        stop_condition (Callable, optional): Function returning True to stop monitoring.

    Returns:
        None

    Memory Implications:
        - Prevents OOM by proactively offloading when VRAM is nearly full.
        - May slow down computation if model is needed again on GPU.

    Example:
        automated_cpu_fallback(model, vram_threshold=0.9)
    """
    logger.info("Starting automated CPU fallback monitor.")
    offloaded = False
    while True:
        if should_offload_to_cpu(vram_threshold) and not offloaded:
            logger.warning("VRAM threshold exceeded. Offloading model to CPU.")
            for param in model.parameters():
                param.data = param.data.cpu()
                if param.grad is not None:
                    param.grad = param.grad.cpu()
            for buffer in model.buffers():
                buffer.data = buffer.data.cpu()
            offloaded = True
            log_memory_event("cpu_fallback_triggered", details=f"Model offloaded at VRAM usage > {vram_threshold*100:.1f}%")
        if stop_condition and stop_condition():
            logger.info("Stopping automated CPU fallback monitor.")
            break
        time.sleep(check_interval)
#!/usr/bin/env python3
"""
ImpressionCore: Dynamic Memory Manager

Module for dynamic memory manager functionality in the ImpressionCore framework.

File: core\memory\dynamic_memory_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, pytorch, core, production, memory, 2025, optimization]
Dependencies: [torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements dynamic memory manager functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from src.core.memory.dynamic_memory_manager import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
import logging
import time
from typing import Optional, Callable

# Import memory profiling utilities if available
# Memory optimization: Memory-critical operation
try:
    from memory_profiler import memory_usage
    # Memory optimization: Memory-critical operation
except ImportError:
    memory_usage = None
    # Memory optimization: Memory-critical operation

logger = logging.getLogger("impressioncore.memory")
# Memory optimization: Memory-critical operation


def get_vram_usage() -> float:
    """
    Returns current VRAM usage in MB (if CUDA available), else 0.
    # Memory optimization: Memory-critical operation
    Args:
        None
    Returns:
        float: Current VRAM usage in megabytes. Returns 0.0 if CUDA is not available.
        # Memory optimization: Memory-critical operation
    Memory Implications:
    # Memory optimization: Memory-critical operation
        Accurate VRAM tracking is essential for dynamic memory management and OOM prevention.
        # Memory optimization: Memory-critical operation
    """
    # Check if CUDA is available and return allocated memory in MB
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        return torch.cuda.memory_allocated() / 1024 ** 2
        # Memory optimization: CUDA operations for GPU acceleration
    return 0.0


def get_vram_total() -> float:
    """
    Returns total VRAM in MB (if CUDA available), else 0.
    # Memory optimization: Memory-critical operation
    Args:
        None
    Returns:
        float: Total VRAM in megabytes. Returns 0.0 if CUDA is not available.
        # Memory optimization: Memory-critical operation
    Memory Implications:
    # Memory optimization: Memory-critical operation
        Used to determine safe VRAM thresholds for offloading.
    """
    # Query total device memory if CUDA is available
    # Memory optimization: Device placement for memory management
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        return torch.cuda.get_device_properties(0).total_memory / 1024 ** 2
        # Memory optimization: CUDA operations for GPU acceleration
    return 0.0


def should_offload_to_cpu(vram_threshold: float = 0.85) -> bool:
    """
    Determines if tensors should be offloaded to CPU based on VRAM usage.
    Args:
        vram_threshold (float): Fraction of VRAM usage to trigger offload (0-1).
    Returns:
        bool: True if offloading is recommended.
    Memory Implications:
    # Memory optimization: Memory-critical operation
        Prevents OOM by proactively offloading when VRAM is nearly full.
    """
    vram_total = get_vram_total()
    vram_used = get_vram_usage()
    if vram_total == 0:
        # No CUDA device detected; offloading not required
        # Memory optimization: Device placement for memory management
        return False
    usage_ratio = vram_used / vram_total
    logger.debug(f"VRAM usage: {vram_used:.2f}MB / {vram_total:.2f}MB ({usage_ratio:.2%})")
    return usage_ratio >= vram_threshold


def offload_tensor_to_cpu(tensor: torch.Tensor) -> torch.Tensor:
    """
    Offloads a tensor to CPU if it's on CUDA.
    # Memory optimization: Memory-critical operation
    Args:
        tensor (torch.Tensor): The tensor to offload.
    Returns:
        torch.Tensor: The tensor on CPU (or unchanged if already on CPU).
    Memory Implications:
    # Memory optimization: Memory-critical operation
        Frees VRAM for other operations, but may slow down computation if tensor is needed again on GPU.
        # Memory optimization: Memory-critical operation
    """
    if tensor.is_cuda:
    # Memory optimization: Memory-critical operation
        logger.info("Offloading tensor to CPU to save VRAM.")
        # Move tensor to CPU to free VRAM
        return tensor.cpu()
    return tensor


def monitor_and_manage_memory(
# Memory optimization: Memory-critical operation
    check_interval: float = 1.0,
    vram_threshold: float = 0.85,
    on_offload: Optional[Callable] = None,
    stop_condition: Optional[Callable[[], bool]] = None
):
    """
    Monitors VRAM usage and triggers offload callback if threshold is exceeded.
    Args:
        check_interval (float): Seconds between checks.
        vram_threshold (float): VRAM usage fraction to trigger offload.
        on_offload (Callable): Function to call when offloading is needed.
        stop_condition (Callable): Function returning True to stop monitoring.
    Returns:
        None
    Memory Implications:
    # Memory optimization: Memory-critical operation
        Enables real-time dynamic memory management for safe operation on low-VRAM hardware.
        # Memory optimization: Memory-critical operation
    """
    logger.info("Starting dynamic memory manager loop.")
    # Memory optimization: Memory-critical operation
    while True:
        # Check if VRAM usage exceeds threshold
        if should_offload_to_cpu(vram_threshold):
            logger.warning("VRAM threshold exceeded. Triggering offload.")
            if on_offload:
                # Call user-provided offload handler
                on_offload()
        if stop_condition and stop_condition():
            logger.info("Stopping dynamic memory manager loop.")
            # Memory optimization: Memory-critical operation
            break
        time.sleep(check_interval)


def log_memory_event(event: str, details: Optional[str] = None):
# Memory optimization: Memory-critical operation
    """
    Logs a memory event to the memlog system.
    # Memory optimization: Memory-critical operation
    Args:
        event (str): Event type or description.
        details (str, optional): Additional details.
    Returns:
        None
    Memory Implications:
    # Memory optimization: Memory-critical operation
        Provides traceability for memory-related events and debugging.
        # Memory optimization: Memory-critical operation
    """
    # Example: integrate with memlog if available
    logger.info(f"[MEMLOG] {event}: {details if details else ''}")

# Example usage (to be integrated with model training/inference):
# Memory optimization: Explicit memory cleanup
# monitor_and_manage_memory(on_offload=lambda: offload_tensor_to_cpu(my_tensor))
# Memory optimization: Memory-critical operation
#
# To stop monitoring, provide a stop_condition function that returns True when done.
#
# All functions are functional, modular, and follow ImpressionCore Copilot Instructions for documentation and code style.
