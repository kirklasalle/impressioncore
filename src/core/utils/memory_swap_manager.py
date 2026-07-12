#!/usr/bin/env python3
"""
ImpressionCore: Memory Swap Manager

Module for memory swap manager functionality in the ImpressionCore framework.

File: core/utils/memory_swap_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, memory-critical, framework, pytorch, core, production, utils, 2025, object-oriented]
Dependencies: [torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements memory swap manager functionality for the
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
from src.core.utils.memory_swap_manager import MemorySwapManager
instance = MemorySwapManager()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import time
from typing import Dict, List, Optional, Set, Tuple, Union, Any
import weakref
import gc
from collections import defaultdict

import torch

# Configure logging
logger = logging.getLogger(__name__)

class MemorySwapManager:
# Memory optimization: Memory-critical operation
    """
    Memory manager for swapping tensors between GPU and CPU.
    # Memory optimization: Memory-critical operation
    
    Provides utilities for tracking and swapping tensors to optimize memory usage
    # Memory optimization: Memory-critical operation
    on limited VRAM devices like the GTX 1050 Ti.
    # Memory optimization: Device placement for memory management
    
    Args:
        vram_target_usage: Target VRAM usage as a fraction of total available (0-1)
        enable_monitoring: Whether to collect memory usage statistics
        # Memory optimization: Memory-critical operation
        device: Target CUDA device
        # Memory optimization: Device placement for memory management
        use_pinned_memory: Whether to use pinned memory for faster CPU-GPU transfers
        # Memory optimization: Memory-critical operation
        swap_immediately: Whether to start swapping immediately as tensors are registered
    """
    
    def __init__(
        self,
        vram_target_usage: float = 0.8,
        enable_monitoring: bool = False,
        device: torch.device = None,
        # Memory optimization: Device placement for memory management
        use_pinned_memory: bool = True,
        # Memory optimization: Memory-critical operation
        swap_immediately: bool = False
    ):
        self.vram_target_usage = min(max(0.1, vram_target_usage), 0.95)
        self.enable_monitoring = enable_monitoring
        self.use_pinned_memory = use_pinned_memory
        # Memory optimization: Memory-critical operation
        self.swap_immediately = swap_immediately
        
        # Set device
        # Memory optimization: Device placement for memory management
        self.has_cuda = torch.cuda.is_available()
        # Memory optimization: CUDA operations for GPU acceleration
        self.device = device if device else torch.device("cuda" if self.has_cuda else "cpu")
        # Memory optimization: Device placement for memory management
        
        # Statistics
        self.swap_count = 0
        self.restore_count = 0
        self.cpu_tensors_size_mb = 0.0
        self.managed_tensors_size_mb = 0.0
        
        # Track tensors
        self.tracked_tensors = {}  # name -> tensor
        self.tracked_grads = {}    # name -> requires_grad
        self.tracked_cpu_tensors = {}  # name -> tensor on CPU
        self.tensor_groups = defaultdict(set)  # group_name -> set of tensor names
        self.tensor_to_group = {}  # tensor_name -> group_name
        self.tensor_access_history = {}  # name -> last access time
        
        # Log initialization
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            device_name = torch.cuda.get_device_name(self.device)
            # Memory optimization: CUDA operations for GPU acceleration
            total_memory = torch.cuda.get_device_properties(self.device).total_memory / (1024 ** 2)
            # Memory optimization: CUDA operations for GPU acceleration
            logger.info(
                f"Initialized Memory Swap Manager: {device_name}, "
                # Memory optimization: Device placement for memory management
                f"Total VRAM: {total_memory:.2f}MB, "
                # Memory optimization: Memory-critical operation
                f"Target usage: {self.vram_target_usage * 100:.1f}%, "
                f"Pinned memory: {self.use_pinned_memory}"
                # Memory optimization: Memory-critical operation
            )
        else:
            logger.warning("CUDA not available, Memory Swap Manager will operate in limited mode")
            # Memory optimization: Memory-critical operation
    
    def register_tensor(self, tensor: torch.Tensor, name: str, group: str = "default") -> bool:
        """
        Register a tensor for memory management.
        # Memory optimization: Memory-critical operation
        
        Args:
            tensor: PyTorch tensor to manage
            name: Unique name for the tensor
            group: Group name for organizing tensors
            
        Returns:
            Boolean indicating if registration was successful
        """
        if name in self.tracked_tensors:
            logger.warning(f"Tensor '{name}' is already registered")
            return False
        
        # Store a reference to the tensor
        self.tracked_tensors[name] = tensor
        self.tracked_grads[name] = tensor.requires_grad
        self.tensor_access_history[name] = time.time()
        
        # Register with group
        self.tensor_groups[group].add(name)
        self.tensor_to_group[name] = group
        
        # Update statistics
        tensor_size_mb = tensor.element_size() * tensor.numel() / (1024 * 1024)
        self.managed_tensors_size_mb += tensor_size_mb
        
        logger.debug(f"Registered tensor '{name}' in group '{group}', size: {tensor_size_mb:.2f}MB")
        
        # Swap immediately if requested and on GPU
        # Memory optimization: Memory-critical operation
        if self.swap_immediately and tensor.device.type == "cuda":
        # Memory optimization: Device placement for memory management
            self.swap_to_cpu(name)
        
        return True
    
    def register_model_parameters(
        self, 
        model: torch.nn.Module, 
        group_by_layer: bool = True,
        prefix: str = "",
        exclude_patterns: List[str] = None
    ) -> int:
        """
        Register model parameters for memory management.
        # Memory optimization: Explicit memory cleanup
        
        Args:
            model: PyTorch model
            group_by_layer: Whether to group parameters by layer
            prefix: Name prefix for registered parameters
            exclude_patterns: List of parameter name patterns to exclude
            
        Returns:
            Number of registered parameters
        """
        count = 0
        exclude_patterns = exclude_patterns or []
        
        # Helper function to check if parameter should be excluded
        def should_exclude(name):
            """
            
    should_exclude function for processing.
    
    Args:
        name: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
            """
            return any(pattern in name for pattern in exclude_patterns)
        
        # Register named parameters
        for name, param in model.named_parameters():
            if should_exclude(name):
                continue
            
            # Determine group name
            if group_by_layer:
                # Extract the module name from parameter name
                parts = name.split('.')
                if len(parts) > 1:
                    group_name = parts[0]  # Use first part as group
                else:
                    group_name = "model_root"
            else:
                group_name = "model_params"
            
            # Create full parameter name
            full_name = f"{prefix}_{name}" if prefix else name
            
            # Register the parameter
            if self.register_tensor(param, full_name, group_name):
                count += 1
        
        logger.info(f"Registered {count} model parameters across {len(self.tensor_groups)} groups")
        # Memory optimization: Explicit memory cleanup
        return count
    
    def swap_to_cpu(self, tensor_name: str) -> bool:
        """
        Swap a tensor from GPU to CPU memory.
        # Memory optimization: Memory-critical operation
        
        Args:
            tensor_name: Name of the tensor to swap
            
        Returns:
            Boolean indicating if swap was successful
        """
        if tensor_name not in self.tracked_tensors:
            logger.warning(f"Tensor '{tensor_name}' is not registered")
            return False
        
        tensor = self.tracked_tensors[tensor_name]
        
        # Skip if already on CPU
        if tensor.device.type == "cpu":
        # Memory optimization: Device placement for memory management
            return True
        
        try:
            # Create CPU copy
            requires_grad = self.tracked_grads[tensor_name]
            if self.use_pinned_memory:
            # Memory optimization: Memory-critical operation
                cpu_tensor = tensor.cpu().pin_memory()
                # Memory optimization: Memory-critical operation
            else:
                cpu_tensor = tensor.cpu()
            
            # Store CPU copy
            self.tracked_cpu_tensors[tensor_name] = cpu_tensor
            
            # Update statistics
            tensor_size_mb = tensor.element_size() * tensor.numel() / (1024 * 1024)
            self.cpu_tensors_size_mb += tensor_size_mb
            self.swap_count += 1
            
            # Clear GPU tensor
            # Memory optimization: Memory-critical operation
            del self.tracked_tensors[tensor_name]
            # Memory optimization: Explicit memory cleanup
            
            # Force garbage collection if useful
            if tensor_size_mb > 100:  # Only for large tensors
                gc.collect()
                # Memory optimization: Force garbage collection
                if self.has_cuda:
                # Memory optimization: Memory-critical operation
                    torch.cuda.empty_cache()
                    # Memory optimization: CUDA operations for GPU acceleration
            
            logger.debug(f"Swapped tensor '{tensor_name}' to CPU, size: {tensor_size_mb:.2f}MB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to swap tensor '{tensor_name}' to CPU: {str(e)}")
            return False
    
    def restore_to_gpu(self, tensor_name: str) -> Optional[torch.Tensor]:
    # Memory optimization: Memory-critical operation
        """
        Restore a tensor from CPU to GPU memory.
        # Memory optimization: Memory-critical operation
        
        Args:
            tensor_name: Name of the tensor to restore
            
        Returns:
            Restored tensor or None if restoration failed
        """
        # Check if tensor is already on GPU
        # Memory optimization: Memory-critical operation
        if tensor_name in self.tracked_tensors:
            tensor = self.tracked_tensors[tensor_name]
            if tensor.device.type == "cuda":
            # Memory optimization: Device placement for memory management
                self.tensor_access_history[tensor_name] = time.time()
                return tensor
        
        # Check if tensor is in CPU storage
        if tensor_name not in self.tracked_cpu_tensors:
            logger.warning(f"Tensor '{tensor_name}' not found in CPU storage")
            return None
        
        try:
            # Move tensor back to GPU
            # Memory optimization: Memory-critical operation
            cpu_tensor = self.tracked_cpu_tensors[tensor_name]
            requires_grad = self.tracked_grads[tensor_name]
            gpu_tensor = cpu_tensor.to(self.device)
            # Memory optimization: Device placement for memory management
            
            # Update tracking
            self.tracked_tensors[tensor_name] = gpu_tensor
            # Memory optimization: Memory-critical operation
            self.tensor_access_history[tensor_name] = time.time()
            
            # Update statistics
            tensor_size_mb = gpu_tensor.element_size() * gpu_tensor.numel() / (1024 * 1024)
            # Memory optimization: Memory-critical operation
            self.cpu_tensors_size_mb -= tensor_size_mb
            self.restore_count += 1
            
            # Remove CPU tensor
            del self.tracked_cpu_tensors[tensor_name]
            # Memory optimization: Explicit memory cleanup
            
            logger.debug(f"Restored tensor '{tensor_name}' to GPU, size: {tensor_size_mb:.2f}MB")
            # Memory optimization: Memory-critical operation
            return gpu_tensor
            # Memory optimization: Memory-critical operation
            
        except Exception as e:
            logger.error(f"Failed to restore tensor '{tensor_name}' to GPU: {str(e)}")
            # Memory optimization: Memory-critical operation
            return None
    
    def ensure_group_on_gpu(self, group_name: str) -> bool:
    # Memory optimization: Memory-critical operation
        """
        Ensure all tensors in a group are on GPU.
        # Memory optimization: Memory-critical operation
        
        Args:
            group_name: Name of the group to restore
            
        Returns:
            Boolean indicating if all tensors were successfully moved to GPU
            # Memory optimization: Memory-critical operation
        """
        if group_name not in self.tensor_groups:
            logger.warning(f"Group '{group_name}' does not exist")
            return False
        
        # Check if we need to free up memory first
        # Memory optimization: Memory-critical operation
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            self._ensure_memory_available_for_group(group_name)
            # Memory optimization: Memory-critical operation
        
        # Move all tensors in the group to GPU
        # Memory optimization: Memory-critical operation
        success = True
        for tensor_name in self.tensor_groups[group_name]:
            tensor = self.restore_to_gpu(tensor_name)
            # Memory optimization: Memory-critical operation
            if tensor is None:
                success = False
        
        return success
    
    def _ensure_memory_available_for_group(self, group_name: str) -> None:
    # Memory optimization: Memory-critical operation
        """
        Ensure sufficient memory is available for a group by swapping out other tensors.
        # Memory optimization: Memory-critical operation
        
        Args:
            group_name: Name of the group that needs memory
            # Memory optimization: Memory-critical operation
        """
        if not self.has_cuda:
        # Memory optimization: Memory-critical operation
            return
        
        # Calculate group size
        group_size_mb = 0
        for tensor_name in self.tensor_groups[group_name]:
            if tensor_name in self.tracked_cpu_tensors:
                cpu_tensor = self.tracked_cpu_tensors[tensor_name]
                group_size_mb += cpu_tensor.element_size() * cpu_tensor.numel() / (1024 * 1024)
        
        # Calculate available memory
        # Memory optimization: Memory-critical operation
        device = torch.cuda.current_device()
        # Memory optimization: CUDA operations for GPU acceleration
        total_memory = torch.cuda.get_device_properties(device).total_memory / (1024 * 1024)
        # Memory optimization: CUDA operations for GPU acceleration
        allocated_memory = torch.cuda.memory_allocated(device) / (1024 * 1024)
        # Memory optimization: CUDA operations for GPU acceleration
        target_memory = total_memory * self.vram_target_usage
        # Memory optimization: Memory-critical operation
        
        # Calculate how much memory we need to free
        # Memory optimization: Memory-critical operation
        available_memory = target_memory - allocated_memory
        # Memory optimization: Memory-critical operation
        needed_memory = group_size_mb - available_memory
        # Memory optimization: Memory-critical operation
        
        if needed_memory <= 0:
        # Memory optimization: Memory-critical operation
            # We have enough memory already
            # Memory optimization: Memory-critical operation
            return
        
        logger.info(f"Need to free {needed_memory:.2f}MB for group '{group_name}'")
        # Memory optimization: Memory-critical operation
        
        # Find tensors to swap out (not in the target group)
        candidates = []
        for name, tensor in self.tracked_tensors.items():
            if name in self.tensor_to_group and self.tensor_to_group[name] != group_name:
                if tensor.device.type == "cuda":
                # Memory optimization: Device placement for memory management
                    tensor_size = tensor.element_size() * tensor.numel() / (1024 * 1024)
                    last_access = self.tensor_access_history.get(name, 0)
                    candidates.append((name, tensor_size, last_access))
        
        # Sort by last access time (oldest first)
        candidates.sort(key=lambda x: x[2])
        
        # Swap out tensors until we have enough memory
        # Memory optimization: Memory-critical operation
        freed_memory = 0
        # Memory optimization: Memory-critical operation
        for name, size, _ in candidates:
            if freed_memory >= needed_memory:
            # Memory optimization: Memory-critical operation
                break
                
            if self.swap_to_cpu(name):
                freed_memory += size
                # Memory optimization: Memory-critical operation
                logger.debug(f"Swapped out tensor '{name}' ({size:.2f}MB) to make room for group '{group_name}'")
        
        if freed_memory < needed_memory:
        # Memory optimization: Memory-critical operation
            logger.warning(
                f"Could only free {freed_memory:.2f}MB of the needed {needed_memory:.2f}MB "
                # Memory optimization: Memory-critical operation
                f"for group '{group_name}'"
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about memory management.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dictionary containing memory statistics
            # Memory optimization: Memory-critical operation
        """
        return {
            "swap_count": self.swap_count,
            "restore_count": self.restore_count,
            "tracked_tensors_count": len(self.tracked_tensors) + len(self.tracked_cpu_tensors),
            "gpu_tensors_count": len(self.tracked_tensors),
            # Memory optimization: Memory-critical operation
            "cpu_tensors_count": len(self.tracked_cpu_tensors),
            "total_managed_size_mb": self.managed_tensors_size_mb,
            "cpu_tensors_size_mb": self.cpu_tensors_size_mb,
            "group_count": len(self.tensor_groups)
        }
    
    def cleanup(self) -> None:
        """Clean up resources and release memory."""
        # Memory optimization: Memory-critical operation
        # Clear all tracked tensors
        self.tracked_tensors.clear()
        # Memory optimization: Memory-critical operation
        self.tracked_cpu_tensors.clear()
        # Memory optimization: Memory-critical operation
        self.tracked_grads.clear()
        # Memory optimization: Memory-critical operation
        self.tensor_groups.clear()
        # Memory optimization: Memory-critical operation
        self.tensor_to_group.clear()
        # Memory optimization: Memory-critical operation
        self.tensor_access_history.clear()
        # Memory optimization: Memory-critical operation
        
        # Force garbage collection
        gc.collect()
        # Memory optimization: Force garbage collection
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
        
        logger.info("Memory Swap Manager cleanup completed")
        # Memory optimization: Memory-critical operation

# Utility functions
def get_tensor_memory_format(tensor: torch.Tensor) -> str:
# Memory optimization: Memory-critical operation
    """
    Get a string description of a tensor's memory format.
    # Memory optimization: Memory-critical operation
    
    Args:
        tensor: PyTorch tensor
        
    Returns:
        Description of memory format
        # Memory optimization: Memory-critical operation
    """
    if tensor.is_contiguous():
        return "contiguous"
    elif tensor.is_contiguous(memory_format=torch.channels_last):
    # Memory optimization: Memory-critical operation
        return "channels_last"
    else:
        return "non_contiguous"

def calculate_tensor_size_mb(tensor: torch.Tensor) -> float:
    """
    Calculate the size of a tensor in megabytes.
    
    Args:
        tensor: PyTorch tensor
        
    Returns:
        Size in megabytes
    """
    return tensor.element_size() * tensor.numel() / (1024 * 1024)

def calculate_model_size_mb(model: torch.nn.Module) -> Dict[str, float]:
    """
    Calculate the size of model parameters and buffers.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        model: PyTorch model
        
    Returns:
        Dictionary with parameter and buffer sizes in MB
    """
    result = {
        "total_mb": 0.0,
        "parameters_mb": 0.0,
        "buffers_mb": 0.0,
        "parameters_count": 0,
        "buffers_count": 0
    }
    
    # Calculate parameter sizes
    for name, param in model.named_parameters():
        size_mb = calculate_tensor_size_mb(param)
        result["parameters_mb"] += size_mb
        result["total_mb"] += size_mb
        result["parameters_count"] += 1
    
    # Calculate buffer sizes
    for name, buffer in model.named_buffers():
        size_mb = calculate_tensor_size_mb(buffer)
        result["buffers_mb"] += size_mb
        result["total_mb"] += size_mb
        result["buffers_count"] += 1
    
    return result

def tensor_to_cpu_with_grad(tensor: torch.Tensor, use_pinned: bool = False) -> torch.Tensor:
    """
    Move a tensor to CPU while preserving gradient information.
    
    Args:
        tensor: PyTorch tensor
        use_pinned: Whether to use pinned memory
        # Memory optimization: Memory-critical operation
        
    Returns:
        CPU tensor with gradient information preserved
    """
    if not tensor.requires_grad:
        # Simple case - just move to CPU
        cpu_tensor = tensor.cpu()
        if use_pinned:
            cpu_tensor = cpu_tensor.pin_memory()
            # Memory optimization: Memory-critical operation
        return cpu_tensor
    
    # Case with gradients - need to preserve them
    cpu_tensor = tensor.cpu()
    if use_pinned:
        cpu_tensor = cpu_tensor.pin_memory()
        # Memory optimization: Memory-critical operation
    
    # If original tensor had gradients, copy them
    if tensor.grad is not None:
        cpu_grad = tensor.grad.cpu()
        if use_pinned:
            cpu_grad = cpu_grad.pin_memory()
            # Memory optimization: Memory-critical operation
        cpu_tensor.grad = cpu_grad
    
    return cpu_tensor
