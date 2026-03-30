#!/usr/bin/env python3
"""
ImpressionCore: Test Memory Utilities

Utility module for memory profiling and monitoring during tests.

File: tests/utils/memory_utils.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-01
Modified: 2025-06-01
Version: 1.0.0

Authors:
- GitHub Copilot
- Development Team

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, utilities, memory, profiling, 2025]
Dependencies: [torch, psutil, tracemalloc]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Utility functions for memory profiling and monitoring during tests.
Provides tools for tracking memory usage, GPU memory, and detecting leaks.
"""

import torch
import psutil
import tracemalloc
import gc
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class MemorySnapshot:
    """Memory usage snapshot."""
    cpu_memory_mb: float
    gpu_memory_mb: float
    gpu_allocated_mb: float
    gpu_cached_mb: float
    process_memory_mb: float
    timestamp: float


class MemoryProfiler:
    """Memory profiler for testing."""
    
    def __init__(self):
        """Initialize memory profiler."""
        self.snapshots = []
        self.baseline_snapshot = None
        self._start_tracing = False
    
    def start_profiling(self) -> None:
        """Start memory profiling."""
        if not self._start_tracing:
            tracemalloc.start()
            self._start_tracing = True
        
        self.baseline_snapshot = self.take_snapshot()
    
    def stop_profiling(self) -> None:
        """Stop memory profiling."""
        if self._start_tracing:
            tracemalloc.stop()
            self._start_tracing = False
    
    def take_snapshot(self) -> MemorySnapshot:
        """Take a memory usage snapshot."""
        import time
        
        # CPU memory
        process = psutil.Process()
        process_memory_mb = process.memory_info().rss / (1024 * 1024)
        
        # System memory
        cpu_memory = psutil.virtual_memory()
        cpu_memory_mb = (cpu_memory.total - cpu_memory.available) / (1024 * 1024)
        
        # GPU memory
        gpu_memory_mb = 0
        gpu_allocated_mb = 0
        gpu_cached_mb = 0
        
        if torch.cuda.is_available():
            gpu_memory_mb = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
            gpu_allocated_mb = torch.cuda.memory_allocated(0) / (1024 * 1024)
            gpu_cached_mb = torch.cuda.memory_reserved(0) / (1024 * 1024)
        
        snapshot = MemorySnapshot(
            cpu_memory_mb=cpu_memory_mb,
            gpu_memory_mb=gpu_memory_mb,
            gpu_allocated_mb=gpu_allocated_mb,
            gpu_cached_mb=gpu_cached_mb,
            process_memory_mb=process_memory_mb,
            timestamp=time.time()
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage."""
        snapshot = self.take_snapshot()
        return {
            'cpu_memory_mb': snapshot.cpu_memory_mb,
            'gpu_memory_mb': snapshot.gpu_memory_mb,
            'gpu_allocated_mb': snapshot.gpu_allocated_mb,
            'gpu_cached_mb': snapshot.gpu_cached_mb,
            'process_memory_mb': snapshot.process_memory_mb
        }
    
    def get_memory_delta(self) -> Optional[Dict[str, float]]:
        """Get memory usage delta since baseline."""
        if self.baseline_snapshot is None or not self.snapshots:
            return None
        
        current = self.snapshots[-1]
        baseline = self.baseline_snapshot
        
        return {
            'cpu_memory_delta_mb': current.cpu_memory_mb - baseline.cpu_memory_mb,
            'gpu_allocated_delta_mb': current.gpu_allocated_mb - baseline.gpu_allocated_mb,
            'gpu_cached_delta_mb': current.gpu_cached_mb - baseline.gpu_cached_mb,
            'process_memory_delta_mb': current.process_memory_mb - baseline.process_memory_mb
        }
    
    def check_memory_leak(self, threshold_mb: float = 100.0) -> bool:
        """Check for potential memory leaks."""
        delta = self.get_memory_delta()
        if delta is None:
            return False
        
        # Check if any memory metric increased beyond threshold
        return any(
            abs(value) > threshold_mb 
            for key, value in delta.items() 
            if 'delta' in key
        )
    
    def get_peak_memory_usage(self) -> Dict[str, float]:
        """Get peak memory usage across all snapshots."""
        if not self.snapshots:
            return {}
        
        peak_cpu = max(s.cpu_memory_mb for s in self.snapshots)
        peak_gpu_allocated = max(s.gpu_allocated_mb for s in self.snapshots)
        peak_gpu_cached = max(s.gpu_cached_mb for s in self.snapshots)
        peak_process = max(s.process_memory_mb for s in self.snapshots)
        
        return {
            'peak_cpu_memory_mb': peak_cpu,
            'peak_gpu_allocated_mb': peak_gpu_allocated,
            'peak_gpu_cached_mb': peak_gpu_cached,
            'peak_process_memory_mb': peak_process
        }
    
    def clear_gpu_cache(self) -> None:
        """Clear GPU cache and run garbage collection."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
    
    def reset(self) -> None:
        """Reset profiler state."""
        self.snapshots.clear()
        self.baseline_snapshot = None


@contextmanager
def memory_profiled(threshold_mb: float = 100.0):
    """Context manager for memory profiling."""
    profiler = MemoryProfiler()
    profiler.start_profiling()
    
    try:
        yield profiler
    finally:
        profiler.take_snapshot()
        profiler.stop_profiling()
        
        # Check for memory leaks
        if profiler.check_memory_leak(threshold_mb):
            delta = profiler.get_memory_delta()
            import warnings
            warnings.warn(
                f"Potential memory leak detected: {delta}",
                ResourceWarning
            )


def estimate_tensor_memory(tensor_shape: Tuple[int, ...], dtype: torch.dtype = torch.float32) -> int:
    """Estimate memory usage for a tensor in bytes."""
    element_count = 1
    for dim in tensor_shape:
        element_count *= dim
    
    # Get bytes per element for different dtypes
    dtype_sizes = {
        torch.float32: 4,
        torch.float16: 2,
        torch.bfloat16: 2,
        torch.int64: 8,
        torch.int32: 4,
        torch.int16: 2,
        torch.int8: 1,
        torch.uint8: 1,
        torch.bool: 1
    }
    
    bytes_per_element = dtype_sizes.get(dtype, 4)  # Default to float32
    return element_count * bytes_per_element


def get_model_memory_footprint(model: torch.nn.Module) -> Dict[str, int]:
    """Get detailed memory footprint of a model."""
    param_memory = 0
    buffer_memory = 0
    
    for param in model.parameters():
        param_memory += param.numel() * param.element_size()
    
    for buffer in model.buffers():
        buffer_memory += buffer.numel() * buffer.element_size()
    
    total_memory = param_memory + buffer_memory
    
    return {
        'parameter_memory_bytes': param_memory,
        'buffer_memory_bytes': buffer_memory,
        'total_memory_bytes': total_memory,
        'parameter_memory_mb': param_memory / (1024 * 1024),
        'buffer_memory_mb': buffer_memory / (1024 * 1024),
        'total_memory_mb': total_memory / (1024 * 1024)
    }


def check_gpu_memory_available(required_mb: float) -> bool:
    """Check if required GPU memory is available."""
    if not torch.cuda.is_available():
        return False
    
    total_memory = torch.cuda.get_device_properties(0).total_memory
    allocated_memory = torch.cuda.memory_allocated(0)
    available_memory = total_memory - allocated_memory
    
    available_mb = available_memory / (1024 * 1024)
    return available_mb >= required_mb


def optimize_memory_for_testing():
    """Optimize memory usage for testing."""
    # Clear GPU cache
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # Run garbage collection
    gc.collect()
    
    # Set memory growth for GPU (if available)
    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(0.8)  # Use only 80% of GPU memory


class MemoryBudget:
    """Memory budget manager for tests."""
    
    def __init__(self, max_cpu_mb: float = 1000, max_gpu_mb: float = 3500):
        """
        Initialize memory budget.
        
        Args:
            max_cpu_mb: Maximum CPU memory in MB
            max_gpu_mb: Maximum GPU memory in MB (default for GTX 1050 Ti)
        """
        self.max_cpu_mb = max_cpu_mb
        self.max_gpu_mb = max_gpu_mb
        self.profiler = MemoryProfiler()
    
    def check_budget(self) -> bool:
        """Check if current usage is within budget."""
        usage = self.profiler.get_memory_usage()
        
        cpu_ok = usage['process_memory_mb'] <= self.max_cpu_mb
        gpu_ok = True
        
        if torch.cuda.is_available():
            gpu_ok = usage['gpu_allocated_mb'] <= self.max_gpu_mb
        
        return cpu_ok and gpu_ok
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get detailed budget status."""
        usage = self.profiler.get_memory_usage()
        
        cpu_usage_pct = (usage['process_memory_mb'] / self.max_cpu_mb) * 100
        gpu_usage_pct = 0
        
        if torch.cuda.is_available():
            gpu_usage_pct = (usage['gpu_allocated_mb'] / self.max_gpu_mb) * 100
        
        return {
            'within_budget': self.check_budget(),
            'cpu_usage_mb': usage['process_memory_mb'],
            'cpu_budget_mb': self.max_cpu_mb,
            'cpu_usage_percent': cpu_usage_pct,
            'gpu_usage_mb': usage['gpu_allocated_mb'],
            'gpu_budget_mb': self.max_gpu_mb,
            'gpu_usage_percent': gpu_usage_pct,
            'gpu_available': torch.cuda.is_available()
        }
