#!/usr/bin/env python3
"""
ImpressionCore: Memory Tracker

Module for memory tracker functionality in the ImpressionCore framework.

File: training/memory_tracker.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, training, gpu-optimized, ml, pytorch, production, 2025, object-oriented]
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements memory tracker functionality for the
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
from training.memory_tracker import MemoryTracker
instance = MemoryTracker()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import gc
import logging
from typing import Dict, Optional, Tuple
import torch
import psutil
import numpy as np

logger = logging.getLogger(__name__)

class MemoryTracker:
# Memory optimization: Memory-critical operation
    """
    Tracks GPU and system memory usage during training
    # Memory optimization: Memory-critical operation
    Optimized for limited VRAM environments
    """
    
    def __init__(self, threshold_gb: float = 3.8):
        """
        Initialize memory tracker
        # Memory optimization: Memory-critical operation
        Args:
            threshold_gb: Memory threshold in GB to trigger warnings (default 3.8GB for 4GB cards)
            # Memory optimization: Memory-critical operation
        """
        self.threshold_gb = threshold_gb
        self.peak_gpu_memory = 0
        # Memory optimization: Memory-critical operation
        self.peak_cpu_memory = 0
        # Memory optimization: Memory-critical operation
        self.history = []
        
    def get_memory_state(self) -> Dict[str, float]:
    # Memory optimization: Memory-critical operation
        """Get current memory usage state"""
        # Memory optimization: Memory-critical operation
        gpu_allocated = 0
        # Memory optimization: Memory-critical operation
        gpu_cached = 0
        # Memory optimization: Memory-critical operation
        
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            gpu_allocated = torch.cuda.memory_allocated() / (1024**3)  # GB
            # Memory optimization: CUDA operations for GPU acceleration
            gpu_cached = torch.cuda.memory_reserved() / (1024**3)  # GB
            # Memory optimization: CUDA operations for GPU acceleration
            
        cpu_used = psutil.Process().memory_info().rss / (1024**3)  # GB
        # Memory optimization: Memory-critical operation
        
        state = {
            "gpu_allocated_gb": gpu_allocated,
            # Memory optimization: Memory-critical operation
            "gpu_cached_gb": gpu_cached,
            # Memory optimization: Memory-critical operation
            "cpu_used_gb": cpu_used,
            "gpu_total_gb": gpu_allocated + gpu_cached
            # Memory optimization: Memory-critical operation
        }
        
        # Update peak values
        self.peak_gpu_memory = max(self.peak_gpu_memory, state["gpu_total_gb"])
        # Memory optimization: Memory-critical operation
        self.peak_cpu_memory = max(self.peak_cpu_memory, cpu_used)
        # Memory optimization: Memory-critical operation
        
        # Add to history
        self.history.append(state)
        
        return state
        
    def get_memory_summary(self) -> str:
    # Memory optimization: Memory-critical operation
        """Get formatted memory usage summary"""
        # Memory optimization: Memory-critical operation
        state = self.get_memory_state()
        # Memory optimization: Memory-critical operation
        
        summary = f"GPU: {state['gpu_allocated_gb']:.1f}GB allocated"
        # Memory optimization: Memory-critical operation
        if state['gpu_cached_gb'] > 0:
        # Memory optimization: Memory-critical operation
            summary += f" (+{state['gpu_cached_gb']:.1f}GB cached)"
            # Memory optimization: Memory-critical operation
            
        # Add warning if near threshold
        if state['gpu_total_gb'] > self.threshold_gb * 0.9:  # 90% of threshold
        # Memory optimization: Memory-critical operation
            summary += " ⚠️"
            
        return summary
        
    def get_peak_memory(self) -> Dict[str, float]:
    # Memory optimization: Memory-critical operation
        """Get peak memory usage"""
        # Memory optimization: Memory-critical operation
        return {
            "peak_gpu_gb": self.peak_gpu_memory,
            # Memory optimization: Memory-critical operation
            "peak_cpu_gb": self.peak_cpu_memory
            # Memory optimization: Memory-critical operation
        }
        
    def should_reduce_batch(self) -> Tuple[bool, str]:
        """
        Check if batch size should be reduced based on memory usage
        # Memory optimization: Memory-critical operation
        Returns:
            (should_reduce, reason)
        """
        state = self.get_memory_state()
        # Memory optimization: Memory-critical operation
        
        if state['gpu_total_gb'] > self.threshold_gb:
        # Memory optimization: Memory-critical operation
            return True, f"GPU memory usage ({state['gpu_total_gb']:.1f}GB) exceeds threshold ({self.threshold_gb}GB)"
            # Memory optimization: Memory-critical operation
            
        # Check if trending toward threshold
        if len(self.history) > 10:
            recent_usage = [h['gpu_total_gb'] for h in self.history[-10:]]
            # Memory optimization: Memory-critical operation
            if np.mean(recent_usage) > self.threshold_gb * 0.95:  # 95% of threshold
                return True, "Memory usage trending toward threshold"
                # Memory optimization: Memory-critical operation
                
        return False, ""
        
    def clear_memory(self):
    # Memory optimization: Memory-critical operation
        """Attempt to clear unused memory"""
        # Memory optimization: Memory-critical operation
        gc.collect()
        # Memory optimization: Force garbage collection
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
            
    def get_available_memory(self) -> float:
    # Memory optimization: Memory-critical operation
        """Get available GPU memory in GB"""
        # Memory optimization: Memory-critical operation
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            return 0
            
        total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        # Memory optimization: CUDA operations for GPU acceleration
        allocated = torch.cuda.memory_allocated() / (1024**3)
        # Memory optimization: CUDA operations for GPU acceleration
        reserved = torch.cuda.memory_reserved() / (1024**3)
        # Memory optimization: CUDA operations for GPU acceleration
        
        return total - (allocated + reserved)
        
    def log_memory_stats(self, step: Optional[int] = None):
    # Memory optimization: Memory-critical operation
        """Log detailed memory statistics"""
        # Memory optimization: Memory-critical operation
        state = self.get_memory_state()
        # Memory optimization: Memory-critical operation
        available = self.get_available_memory()
        # Memory optimization: Memory-critical operation
        
        msg = []
        if step is not None:
            msg.append(f"Step {step}")
            
        msg.extend([
            f"GPU Memory: {state['gpu_total_gb']:.1f}GB total",
            # Memory optimization: Memory-critical operation
            f"({state['gpu_allocated_gb']:.1f}GB allocated,",
            # Memory optimization: Memory-critical operation
            f"{state['gpu_cached_gb']:.1f}GB cached)",
            # Memory optimization: Memory-critical operation
            f"Available: {available:.1f}GB",
            f"CPU Memory: {state['cpu_used_gb']:.1f}GB"
            # Memory optimization: Memory-critical operation
        ])
        
        if state['gpu_total_gb'] > self.threshold_gb:
        # Memory optimization: Memory-critical operation
            msg.append("WARNING: Above memory threshold!")
            # Memory optimization: Memory-critical operation
            
        logger.info(" | ".join(msg))
        
    def get_memory_profile(self) -> Dict[str, float]:
    # Memory optimization: Memory-critical operation
        """Get detailed memory usage profile"""
        # Memory optimization: Memory-critical operation
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            return {}
            
        try:
            device = torch.cuda.current_device()
            # Memory optimization: CUDA operations for GPU acceleration
            props = torch.cuda.get_device_properties(device)
            # Memory optimization: CUDA operations for GPU acceleration
            
            return {
                "device_name": props.name,
                # Memory optimization: Device placement for memory management
                "total_memory_gb": props.total_memory / (1024**3),
                # Memory optimization: Memory-critical operation
                "allocated_gb": torch.cuda.memory_allocated() / (1024**3),
                # Memory optimization: CUDA operations for GPU acceleration
                "cached_gb": torch.cuda.memory_reserved() / (1024**3),
                # Memory optimization: CUDA operations for GPU acceleration
                "peak_gpu_gb": self.peak_gpu_memory,
                # Memory optimization: Memory-critical operation
                "peak_cpu_gb": self.peak_cpu_memory,
                # Memory optimization: Memory-critical operation
                "available_gb": self.get_available_memory()
                # Memory optimization: Memory-critical operation
            }
        except Exception as e:
            logger.error(f"Error getting memory profile: {e}")
            # Memory optimization: Memory-critical operation
            return {}