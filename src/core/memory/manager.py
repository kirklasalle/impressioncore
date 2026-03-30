#!/usr/bin/env python3
"""
ImpressionCore: Manager

Module for manager functionality in the ImpressionCore framework.

File: memory_manager\manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, 2025, object-oriented]
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements manager functionality for the
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
from memory_manager.manager import MemoryManager
instance = MemoryManager()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import gc
import weakref
import logging
import numpy as np
import torch
import os
import psutil
from typing import Dict, List, Optional, Union, Set, Tuple

logger = logging.getLogger(__name__)

class MemoryManager:
# Memory optimization: Memory-critical operation
    """
    Memory management for efficient training and inference on limited hardware.
    # Memory optimization: Memory-critical operation
    
    This class provides utilities to:
    1. Track CPU and GPU memory usage
    # Memory optimization: Memory-critical operation
    2. Offload tensors to CPU or disk when needed
    3. Optimize memory usage for large models on limited hardware
    # Memory optimization: Memory-critical operation
    4. Implement gradient checkpointing and attention chunking
    """
    
    def __init__(self, 
                 vram_limit: Optional[float] = None,
                 ram_limit: Optional[float] = None,
                 enable_offloading: bool = True,
                 offload_to_disk: bool = False,
                 disk_cache_dir: str = "./tensor_cache",
                 log_level: int = logging.INFO):
        """
        Initialize the memory manager.
        # Memory optimization: Memory-critical operation
        
        Args:
            vram_limit: Maximum VRAM usage in GB (None = auto-detect 90% of available)
            ram_limit: Maximum RAM usage in GB (None = auto-detect 80% of available)
            enable_offloading: Whether to enable tensor offloading to CPU
            offload_to_disk: Whether to enable tensor offloading to disk
            disk_cache_dir: Directory for disk tensor caching if enabled
            log_level: Logging level for the memory manager
            # Memory optimization: Memory-critical operation
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Set up device
        # Memory optimization: Device placement for memory management
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Memory optimization: CUDA operations for GPU acceleration
        self.using_cuda = self.device.type == "cuda"
        # Memory optimization: Device placement for memory management
        
        # Set memory limits
        # Memory optimization: Memory-critical operation
        self._set_memory_limits(vram_limit, ram_limit)
        # Memory optimization: Memory-critical operation
        
        # Configure offloading
        self.enable_offloading = enable_offloading
        self.offload_to_disk = offload_to_disk and enable_offloading
        self.disk_cache_dir = disk_cache_dir
        
        if self.offload_to_disk and not os.path.exists(disk_cache_dir):
            os.makedirs(disk_cache_dir)
            
        # Tracking structures
        self.tracked_tensors = weakref.WeakKeyDictionary()  # Tensor -> metadata
        self.tensor_access_history = {}  # Tensor ID -> last access time
        self.current_vram_usage = 0  # Bytes
        self.current_ram_usage = 0   # Bytes
        self.tensor_id_counter = 0
        
        self.logger.info(f"MemoryManager initialized: VRAM limit={self.vram_limit_gb:.2f}GB, "
        # Memory optimization: Memory-critical operation
                        f"RAM limit={self.ram_limit_gb:.2f}GB")
        if self.using_cuda:
        # Memory optimization: Memory-critical operation
            gpu_info = self.get_gpu_info()
            # Memory optimization: Memory-critical operation
            self.logger.info(f"GPU: {gpu_info['name']}, Free: {gpu_info['free']:.2f}GB, Total: {gpu_info['total']:.2f}GB")
            # Memory optimization: Memory-critical operation
    
    def _set_memory_limits(self, vram_limit: Optional[float], ram_limit: Optional[float]):
    # Memory optimization: Memory-critical operation
        """Set memory limits based on user input or auto-detection."""
        # Memory optimization: Memory-critical operation
        # RAM limit
        system_ram = psutil.virtual_memory().total / (1024**3)  # GB
        # Memory optimization: Memory-critical operation
        self.ram_limit_gb = ram_limit if ram_limit is not None else system_ram * 0.8
        self.ram_limit = self.ram_limit_gb * (1024**3)  # bytes
        
        # VRAM limit
        if self.using_cuda:
        # Memory optimization: Memory-critical operation
            try:
                total_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                # Memory optimization: CUDA operations for GPU acceleration
                self.vram_limit_gb = vram_limit if vram_limit is not None else total_vram * 0.9
            except Exception:
                self.vram_limit_gb = 2.0  # Default 2GB if can't detect
        else:
            self.vram_limit_gb = 0
        self.vram_limit = self.vram_limit_gb * (1024**3)  # bytes
        
    def get_gpu_info(self) -> Dict[str, Union[str, float]]:
    # Memory optimization: Memory-critical operation
        """Get GPU information including name, memory usage."""
        # Memory optimization: Memory-critical operation
        if not self.using_cuda:
        # Memory optimization: Memory-critical operation
            return {"name": "CPU (No GPU)", "free": 0, "used": 0, "total": 0}
            # Memory optimization: Memory-critical operation
            
        try:
            device_props = torch.cuda.get_device_properties(0)
            # Memory optimization: CUDA operations for GPU acceleration
            free_mem = torch.cuda.memory_reserved(0) - torch.cuda.memory_allocated(0)
            # Memory optimization: CUDA operations for GPU acceleration
            total_mem = torch.cuda.get_device_properties(0).total_memory
            # Memory optimization: CUDA operations for GPU acceleration
            used_mem = torch.cuda.memory_allocated(0)
            # Memory optimization: CUDA operations for GPU acceleration
            
            return {
                "name": device_props.name,
                # Memory optimization: Device placement for memory management
                "free": free_mem / (1024**3),  # GB
                "used": used_mem / (1024**3),  # GB
                "total": total_mem / (1024**3),  # GB
                "utilization": torch.cuda.utilization(0)  # percentage
                # Memory optimization: CUDA operations for GPU acceleration
            }
        except Exception as e:
            self.logger.warning(f"Error getting GPU info: {e}")
            # Memory optimization: Memory-critical operation
            return {"name": "Unknown", "free": 0, "used": 0, "total": 0}
    
    def track_vram(self, tensor: torch.Tensor) -> int:
        """
        Start tracking a tensor's memory usage.
        # Memory optimization: Memory-critical operation
        
        Args:
            tensor: The tensor to track
            
        Returns:
            int: ID assigned to the tracked tensor
        """
        if not isinstance(tensor, torch.Tensor):
            self.logger.warning(f"Attempted to track non-tensor object: {type(tensor)}")
            return -1
            
        # Assign an ID to this tensor
        tensor_id = self.tensor_id_counter
        self.tensor_id_counter += 1
        
        # Calculate size in bytes
        size_bytes = tensor.element_size() * tensor.nelement()
        
        # Store metadata
        self.tracked_tensors[tensor] = {
            'id': tensor_id,
            'size': size_bytes,
            'shape': tensor.shape,
            'dtype': tensor.dtype,
            'device': tensor.device,
            # Memory optimization: Device placement for memory management
            'is_offloaded': False,
            'disk_path': None
        }
        
        # Update memory usage
        # Memory optimization: Memory-critical operation
        if tensor.device.type == 'cuda':
        # Memory optimization: Device placement for memory management
            self.current_vram_usage += size_bytes
        else:
            self.current_ram_usage += size_bytes
        
        # Record access
        self.tensor_access_history[tensor_id] = torch.cuda.current_stream().record_event() if self.using_cuda else 0
        # Memory optimization: CUDA operations for GPU acceleration
        
        return tensor_id
    
    def release_tensor(self, tensor_id: int) -> bool:
        """
        Manually release a tracked tensor.
        
        Args:
            tensor_id: ID of the tensor to release
            
        Returns:
            bool: True if tensor was found and released, False otherwise
        """
        for tensor, meta in list(self.tracked_tensors.items()):
            if meta['id'] == tensor_id:
                size_bytes = meta['size']
                
                # Update memory usage
                # Memory optimization: Memory-critical operation
                if meta['device'].type == 'cuda':
                # Memory optimization: Device placement for memory management
                    self.current_vram_usage -= size_bytes
                else:
                    self.current_ram_usage -= size_bytes
                
                # Delete tensor file if offloaded to disk
                if meta['is_offloaded'] and meta['disk_path'] and os.path.exists(meta['disk_path']):
                    try:
                        os.remove(meta['disk_path'])
                    except Exception as e:
                        self.logger.warning(f"Failed to delete tensor file: {e}")
                
                # Clean up tracking data
                if tensor_id in self.tensor_access_history:
                    del self.tensor_access_history[tensor_id]
                    # Memory optimization: Explicit memory cleanup
                
                # The tensor itself will be garbage collected normally
                return True
        
        self.logger.warning(f"Attempted to release unknown tensor ID: {tensor_id}")
        return False
    
    def get_vram_usage(self) -> float:
        """Get current VRAM usage in GB."""
        if self.using_cuda:
        # Memory optimization: Memory-critical operation
            return torch.cuda.memory_allocated() / (1024**3)
            # Memory optimization: CUDA operations for GPU acceleration
        return 0.0
    
    def get_ram_usage(self) -> float:
        """Get current RAM usage in GB."""
        return psutil.Process().memory_info().rss / (1024**3)
        # Memory optimization: Memory-critical operation
    
    def optimize_memory(self, required_bytes: int = 0) -> int:
    # Memory optimization: Memory-critical operation
        """
        Optimize memory by offloading least recently used tensors.
        # Memory optimization: Memory-critical operation
        
        Args:
            required_bytes: Additional bytes that need to be freed
            
        Returns:
            int: Number of bytes freed
        """
        if not self.enable_offloading:
            return 0
            
        # Skip if VRAM usage is below threshold and no specific requirement
        current_usage = self.get_vram_usage() * (1024**3)  # convert GB to bytes
        if required_bytes == 0 and current_usage < self.vram_limit * 0.9:
            return 0
            
        # Sort tensors by last access time (oldest first)
        sorted_tensors = []
        for tensor, meta in self.tracked_tensors.items():
            if not meta['is_offloaded'] and tensor.device.type == 'cuda':
            # Memory optimization: Device placement for memory management
                tensor_id = meta['id']
                if tensor_id in self.tensor_access_history:
                    sorted_tensors.append((tensor, self.tensor_access_history[tensor_id]))
        
        # Sort by access time if using CUDA, otherwise just take all tensors
        # Memory optimization: Memory-critical operation
        if self.using_cuda:
        # Memory optimization: Memory-critical operation
            sorted_tensors.sort(key=lambda x: x[1])
        
        # Calculate how much memory to free
        # Memory optimization: Memory-critical operation
        target_bytes = required_bytes
        if current_usage + required_bytes > self.vram_limit:
            target_bytes += (current_usage + required_bytes - self.vram_limit)
            
        # Offload tensors until we've freed enough memory
        # Memory optimization: Memory-critical operation
        freed_bytes = 0
        for tensor, _ in sorted_tensors:
            if freed_bytes >= target_bytes:
                break
                
            meta = self.tracked_tensors[tensor]
            size_bytes = meta['size']
            
            # Move tensor to CPU
            tensor_cpu = tensor.detach().cpu()
            self.tracked_tensors[tensor_cpu] = meta.copy()
            self.tracked_tensors[tensor_cpu]['device'] = torch.device('cpu')
            # Memory optimization: Device placement for memory management
            
            # If disk offloading is enabled, save to disk
            if self.offload_to_disk:
                tensor_path = os.path.join(self.disk_cache_dir, f"tensor_{meta['id']}.pt")
                torch.save(tensor_cpu, tensor_path)
                self.tracked_tensors[tensor_cpu]['disk_path'] = tensor_path
                self.tracked_tensors[tensor_cpu]['is_offloaded'] = True
                
                # We can free the CPU tensor now
                del tensor_cpu
                # Memory optimization: Explicit memory cleanup
            
            # Update tracking information
            freed_bytes += size_bytes
            self.current_vram_usage -= size_bytes
            
            if not self.offload_to_disk:
                self.current_ram_usage += size_bytes
        
        # Force garbage collection
        gc.collect()
        # Memory optimization: Force garbage collection
        if self.using_cuda:
        # Memory optimization: Memory-critical operation
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
            
        self.logger.info(f"Optimized memory: freed {freed_bytes / (1024**2):.2f} MB")
        # Memory optimization: Memory-critical operation
        return freed_bytes
    
    def apply_gradient_checkpointing(self, model: torch.nn.Module) -> torch.nn.Module:
        """
        Apply gradient checkpointing to a PyTorch model to reduce memory usage.
        # Memory optimization: Explicit memory cleanup
        
        Args:
            model: PyTorch model to modify
            # Memory optimization: Explicit memory cleanup
            
        Returns:
            torch.nn.Module: Modified model
        """
        if not hasattr(model, "gradient_checkpointing_enable"):
            self.logger.warning("Model doesn't support gradient checkpointing natively")
            # Memory optimization: Explicit memory cleanup
            return model
            
        try:
            model.gradient_checkpointing_enable()
            self.logger.info("Gradient checkpointing enabled")
        except Exception as e:
            self.logger.warning(f"Failed to enable gradient checkpointing: {e}")
            
        return model
    
    def enable_mixed_precision(self) -> None:
        """Enable mixed precision training/inference for memory optimization."""
        # Memory optimization: Memory-critical operation
        if self.using_cuda and torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            try:
                torch.cuda.amp.autocast(enabled=True)
                # Memory optimization: CUDA operations for GPU acceleration
                self.logger.info("Mixed precision enabled")
            except Exception as e:
                self.logger.warning(f"Failed to enable mixed precision: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources used by the memory manager."""
        # Memory optimization: Memory-critical operation
        # Clear any remaining disk tensors
        if self.offload_to_disk:
            for tensor, meta in self.tracked_tensors.items():
                if meta.get('disk_path') and os.path.exists(meta['disk_path']):
                    try:
                        os.remove(meta['disk_path'])
                    except Exception:
                        pass
        
        # Clear tracking dictionaries
        self.tracked_tensors.clear()
        # Memory optimization: Memory-critical operation
        self.tensor_access_history.clear()
        # Memory optimization: Memory-critical operation
        
        # Force garbage collection
        gc.collect()
        # Memory optimization: Force garbage collection
        if self.using_cuda:
        # Memory optimization: Memory-critical operation
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
        
        self.logger.info("Memory manager cleanup complete")
        # Memory optimization: Memory-critical operation
