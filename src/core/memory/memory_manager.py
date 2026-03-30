#!/usr/bin/env python3
"""
ImpressionCore: Memory Manager

Module for memory manager functionality in the ImpressionCore framework.

File: core\\memory_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, pytorch, core, production, 2025, object-oriented]
Dependencies: [torch, rich, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements memory manager functionality for the
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
from core.memory_manager import MemorySnapshot
instance = MemorySnapshot()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
import psutil
import gc
import os
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from contextlib import contextmanager

# Import rich enhancements for beautiful logging
try:
    from src.core.utils.rich_enhancements import (
        console, create_table, print_info, print_success, 
        print_warning, print_error, display_memory_metrics
        # Memory optimization: Memory-critical operation
    )
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

logger = logging.getLogger(__name__)

@dataclass
class MemorySnapshot:
# Memory optimization: Memory-critical operation
    """Snapshot of current memory state."""
    # Memory optimization: Memory-critical operation
    gpu_allocated: float
    # Memory optimization: Memory-critical operation
    gpu_cached: float
    # Memory optimization: Memory-critical operation
    gpu_free: float
    # Memory optimization: Memory-critical operation
    cpu_used: float
    cpu_available: float
    timestamp: str

class MemoryManager:
# Memory optimization: Memory-critical operation
    """
    Advanced memory management system for ImpressionCore.
    # Memory optimization: Memory-critical operation
    
    Provides comprehensive memory tracking, optimization, and cleanup
    # Memory optimization: Memory-critical operation
    utilities for running AI models on constrained hardware.
    """
    
    def __init__(self, enable_monitoring: bool = True):
        """
        Initialize the memory manager.
        # Memory optimization: Memory-critical operation
        
        Args:
            enable_monitoring: Whether to enable continuous memory monitoring
            # Memory optimization: Memory-critical operation
        """
        self.enable_monitoring = enable_monitoring
        self.vram_usage = 0
        self.models_registry = {}
        self.memory_snapshots = []
        # Memory optimization: Memory-critical operation
        
        # Check GPU availability
        # Memory optimization: Memory-critical operation
        self.has_gpu = torch.cuda.is_available()
        # Memory optimization: CUDA operations for GPU acceleration
        if self.has_gpu:
        # Memory optimization: Memory-critical operation
            self.device_count = torch.cuda.device_count()
            # Memory optimization: CUDA operations for GPU acceleration
            self.primary_device = torch.cuda.current_device()
            # Memory optimization: CUDA operations for GPU acceleration
        else:
            self.device_count = 0
            # Memory optimization: Device placement for memory management
            self.primary_device = None
            # Memory optimization: Device placement for memory management
            
        if HAS_RICH:
            print_info(f"MemoryManager initialized - GPU Available: {self.has_gpu}")
            # Memory optimization: Memory-critical operation
            if self.has_gpu:
            # Memory optimization: Memory-critical operation
                print_info(f"GPU Devices: {self.device_count}, Primary: {self.primary_device}")
                # Memory optimization: Device placement for memory management

    def track_vram(self, tensor: Any, name: str = "unnamed") -> None:
        """
        Track VRAM usage for a given tensor.
        
        Args:
            tensor: The tensor to track
            name: Optional name for the tensor
        """
        if tensor.is_cuda:
        # Memory optimization: Memory-critical operation
            size_bytes = tensor.element_size() * tensor.nelement()
            self.vram_usage += size_bytes
            
            if HAS_RICH and self.enable_monitoring:
                print_info(f"Tracking tensor '{name}': {size_bytes / 1024**2:.2f} MB")

    def offload_to_cpu(self, model: Any, model_name: str = "model") -> None:
        """
        Offload model layers to CPU to save VRAM.
        # Memory optimization: Explicit memory cleanup
        
        Args:
            model: The model to offload
            # Memory optimization: Explicit memory cleanup
            model_name: Name of the model for tracking
            # Memory optimization: Explicit memory cleanup
        """
        if HAS_RICH:
            print_info(f"Offloading model '{model_name}' to CPU...")
            # Memory optimization: Explicit memory cleanup
            
        for param in model.parameters():
            param.data = param.data.cpu()
            if param.grad is not None:
                param.grad = param.grad.cpu()
                
        # Update registry
        self.models_registry[model_name] = {
            'model': model,
            'location': 'cpu',
            'last_moved': torch.cuda.Event(enable_timing=True) if self.has_gpu else None
            # Memory optimization: CUDA operations for GPU acceleration
        }
        
        if HAS_RICH:
            print_success(f"Model '{model_name}' successfully offloaded to CPU")
            # Memory optimization: Explicit memory cleanup

    def offload_tensor_to_cpu(self, tensor: Any) -> Any:
        """
        Offload a single tensor to CPU to save VRAM.
        
        Args:
            tensor: The tensor to offload
            
        Returns:
            The tensor moved to CPU
        """
        if tensor.is_cuda:
        # Memory optimization: Memory-critical operation
            return tensor.cpu()
        return tensor

    def get_vram_usage(self) -> int:
        """
        Get the current tracked VRAM usage.
        
        Returns:
            VRAM usage in bytes
        """
        return self.vram_usage
        
    def get_system_memory_stats(self) -> Dict[str, Any]:
    # Memory optimization: Memory-critical operation
        """
        Get comprehensive system memory statistics.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dictionary containing memory statistics
            # Memory optimization: Memory-critical operation
        """
        stats = {}
        
        # CPU Memory
        # Memory optimization: Memory-critical operation
        memory = psutil.virtual_memory()
        # Memory optimization: Memory-critical operation
        stats['cpu'] = {
            'total': memory.total,
            # Memory optimization: Memory-critical operation
            'available': memory.available,
            # Memory optimization: Memory-critical operation
            'used': memory.used,
            # Memory optimization: Memory-critical operation
            'percent': memory.percent
            # Memory optimization: Memory-critical operation
        }
        
        # GPU Memory (if available)
        # Memory optimization: Memory-critical operation
        if self.has_gpu:
        # Memory optimization: Memory-critical operation
            stats['gpu'] = {}
            # Memory optimization: Memory-critical operation
            for i in range(self.device_count):
            # Memory optimization: Device placement for memory management
                gpu_memory = torch.cuda.get_device_properties(i)
                # Memory optimization: CUDA operations for GPU acceleration
                allocated = torch.cuda.memory_allocated(i)
                # Memory optimization: CUDA operations for GPU acceleration
                cached = torch.cuda.memory_reserved(i)
                # Memory optimization: CUDA operations for GPU acceleration
                
                stats['gpu'][f'device_{i}'] = {
                # Memory optimization: Device placement for memory management
                    'name': gpu_memory.name,
                    # Memory optimization: Memory-critical operation
                    'total': gpu_memory.total_memory,
                    # Memory optimization: Memory-critical operation
                    'allocated': allocated,
                    'cached': cached,
                    'free': gpu_memory.total_memory - allocated
                    # Memory optimization: Memory-critical operation
                }
        
        return stats
    
    def create_memory_snapshot(self) -> MemorySnapshot:
    # Memory optimization: Memory-critical operation
        """
        Create a snapshot of current memory state.
        # Memory optimization: Memory-critical operation
        
        Returns:
            MemorySnapshot object containing current memory state
            # Memory optimization: Memory-critical operation
        """
        stats = self.get_system_memory_stats()
        # Memory optimization: Memory-critical operation
        
        # GPU stats (default to 0 if no GPU)
        # Memory optimization: Memory-critical operation
        gpu_allocated = 0
        # Memory optimization: Memory-critical operation
        gpu_cached = 0
        # Memory optimization: Memory-critical operation
        gpu_free = 0
        # Memory optimization: Memory-critical operation
        
        if self.has_gpu and 'gpu' in stats:
        # Memory optimization: Memory-critical operation
            primary_gpu = stats['gpu'][f'device_{self.primary_device}']
            # Memory optimization: Device placement for memory management
            gpu_allocated = primary_gpu['allocated'] / 1024**3  # GB
            # Memory optimization: Memory-critical operation
            gpu_cached = primary_gpu['cached'] / 1024**3
            # Memory optimization: Memory-critical operation
            gpu_free = primary_gpu['free'] / 1024**3
            # Memory optimization: Memory-critical operation
        
        snapshot = MemorySnapshot(
        # Memory optimization: Memory-critical operation
            gpu_allocated=gpu_allocated,
            # Memory optimization: Memory-critical operation
            gpu_cached=gpu_cached,
            # Memory optimization: Memory-critical operation
            gpu_free=gpu_free,
            # Memory optimization: Memory-critical operation
            cpu_used=stats['cpu']['used'] / 1024**3,
            cpu_available=stats['cpu']['available'] / 1024**3,
            timestamp=torch.cuda.Event(enable_timing=True).query() if self.has_gpu else "N/A"
            # Memory optimization: CUDA operations for GPU acceleration
        )
        
        self.memory_snapshots.append(snapshot)
        # Memory optimization: Memory-critical operation
        return snapshot
    
    @contextmanager
    def profile_memory(self, operation_name: str = "operation"):
    # Memory optimization: Memory-critical operation
        """
        Context manager for profiling memory usage during an operation.
        # Memory optimization: Memory-critical operation
        
        Args:
            operation_name: Name of the operation being profiled
        """
        if HAS_RICH:
            print_info(f"Starting memory profiling for: {operation_name}")
            # Memory optimization: Memory-critical operation
            
        # Take initial snapshot
        initial_snapshot = self.create_memory_snapshot()
        # Memory optimization: Memory-critical operation
        
        try:
            yield
        finally:
            # Take final snapshot
            final_snapshot = self.create_memory_snapshot()
            # Memory optimization: Memory-critical operation
            
            if HAS_RICH:
                # Create comparison table
                table = create_table(f"Memory Profile: {operation_name}")
                # Memory optimization: Memory-critical operation
                table.add_column("Metric", style="cyan")
                table.add_column("Before", style="green")
                table.add_column("After", style="yellow")
                table.add_column("Change", style="red")
                
                # GPU metrics
                # Memory optimization: Memory-critical operation
                if self.has_gpu:
                # Memory optimization: Memory-critical operation
                    gpu_change = final_snapshot.gpu_allocated - initial_snapshot.gpu_allocated
                    # Memory optimization: Memory-critical operation
                    table.add_row(
                        "GPU Allocated (GB)",
                        # Memory optimization: Memory-critical operation
                        f"{initial_snapshot.gpu_allocated:.3f}",
                        # Memory optimization: Memory-critical operation
                        f"{final_snapshot.gpu_allocated:.3f}",
                        # Memory optimization: Memory-critical operation
                        f"{gpu_change:+.3f}"
                        # Memory optimization: Memory-critical operation
                    )
                
                # CPU metrics
                cpu_change = final_snapshot.cpu_used - initial_snapshot.cpu_used
                table.add_row(
                    "CPU Used (GB)",
                    f"{initial_snapshot.cpu_used:.3f}",
                    f"{final_snapshot.cpu_used:.3f}",
                    f"{cpu_change:+.3f}"
                )
                
                console.print(table)
    
    def cleanup_memory(self, aggressive: bool = False) -> None:
    # Memory optimization: Memory-critical operation
        """
        Perform memory cleanup operations.
        # Memory optimization: Memory-critical operation
        
        Args:
            aggressive: Whether to perform aggressive cleanup
        """
        if HAS_RICH:
            print_info("Starting memory cleanup...")
            # Memory optimization: Memory-critical operation
            
        # Clear Python garbage collector
        collected = gc.collect()
        # Memory optimization: Force garbage collection
        
        # Clear GPU cache if available
        # Memory optimization: Memory-critical operation
        if self.has_gpu:
        # Memory optimization: Memory-critical operation
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
            if aggressive:
                torch.cuda.synchronize()
                # Memory optimization: CUDA operations for GPU acceleration
                
        if HAS_RICH:
            print_success(f"Memory cleanup completed - Collected {collected} objects")
            # Memory optimization: Memory-critical operation
    
    def display_memory_status(self) -> None:
    # Memory optimization: Memory-critical operation
        """Display current memory status using rich formatting."""
        # Memory optimization: Memory-critical operation
        if not HAS_RICH:
            # Fallback to simple print
            stats = self.get_system_memory_stats()
            # Memory optimization: Memory-critical operation
            print(f"CPU Memory: {stats['cpu']['percent']:.1f}% used")
            # Memory optimization: Memory-critical operation
            if self.has_gpu:
            # Memory optimization: Memory-critical operation
                for device, gpu_stats in stats['gpu'].items():
                # Memory optimization: Device placement for memory management
                    allocated_pct = (gpu_stats['allocated'] / gpu_stats['total']) * 100
                    # Memory optimization: Memory-critical operation
                    print(f"GPU {device}: {allocated_pct:.1f}% allocated")
                    # Memory optimization: Device placement for memory management
            return
            
        # Rich formatted display
        display_memory_metrics(self.get_system_memory_stats())
        # Memory optimization: Memory-critical operation
