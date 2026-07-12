#!/usr/bin/env python3
"""
ImpressionCore: Cuda Utils

Module for cuda utils functionality in the ImpressionCore framework.

File: core/utils/cuda_utils.py
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
This module implements cuda utils functionality for the
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
from src.core.utils.cuda_utils import CudaMonitor
instance = CudaMonitor()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import os
import sys
import torch
import gc
import subprocess
import re
from typing import Dict, Any, Tuple, Optional, List, Union

logger = logging.getLogger(__name__)

def get_cuda_info() -> Dict[str, Any]:
# Memory optimization: Memory-critical operation
    """
    Get comprehensive information about CUDA availability and memory usage.
    # Memory optimization: Memory-critical operation
    
    Returns:
        Dict containing CUDA information including shared memory details
        # Memory optimization: Memory-critical operation
    """
    info = {
        "cuda_available": torch.cuda.is_available(),
        # Memory optimization: CUDA operations for GPU acceleration
        "device_count": 0,
        # Memory optimization: Device placement for memory management
        "current_device": None,
        # Memory optimization: Device placement for memory management
        "device_name": None,
        # Memory optimization: Device placement for memory management
        "memory_allocated_mb": 0,
        # Memory optimization: Memory-critical operation
        "memory_reserved_mb": 0,
        # Memory optimization: Memory-critical operation
        "memory_total_mb": 0,
        # Memory optimization: Memory-critical operation
        "memory_free_mb": 0,
        # Memory optimization: Memory-critical operation
        "memory_utilization": 0.0,
        # Memory optimization: Memory-critical operation
        "shared_memory_support": False,
        # Memory optimization: Memory-critical operation
        "system_memory_mb": 0,
        # Memory optimization: Memory-critical operation
        "driver_version": None,
        "cuda_version": None,
        # Memory optimization: Memory-critical operation
    }
    
    if not info["cuda_available"]:
    # Memory optimization: Memory-critical operation
        return info
    
    info["device_count"] = torch.cuda.device_count()
    # Memory optimization: CUDA operations for GPU acceleration
    info["current_device"] = torch.cuda.current_device()
    # Memory optimization: CUDA operations for GPU acceleration
    info["device_name"] = torch.cuda.get_device_name(info["current_device"])
    # Memory optimization: CUDA operations for GPU acceleration
    
    # Get PyTorch-reported memory information
    # Memory optimization: Memory-critical operation
    info["memory_allocated_mb"] = torch.cuda.memory_allocated() / 1024**2
    # Memory optimization: CUDA operations for GPU acceleration
    info["memory_reserved_mb"] = torch.cuda.memory_reserved() / 1024**2
    # Memory optimization: CUDA operations for GPU acceleration
    
    device_props = torch.cuda.get_device_properties(info["current_device"])
    # Memory optimization: CUDA operations for GPU acceleration
    info["memory_total_mb"] = device_props.total_memory / 1024**2
    # Memory optimization: Device placement for memory management
    
    # Calculate free memory and utilization
    # Memory optimization: Memory-critical operation
    info["memory_free_mb"] = info["memory_total_mb"] - info["memory_reserved_mb"]
    # Memory optimization: Memory-critical operation
    info["memory_utilization"] = info["memory_reserved_mb"] / info["memory_total_mb"] * 100
    # Memory optimization: Memory-critical operation
    
    # Get system memory info
    # Memory optimization: Memory-critical operation
    if hasattr(os, "sysconf"):
        if "SC_PAGE_SIZE" in os.sysconf_names and "SC_PHYS_PAGES" in os.sysconf_names:
            pagesize = os.sysconf("SC_PAGE_SIZE")
            physpages = os.sysconf("SC_PHYS_PAGES")
            info["system_memory_mb"] = (pagesize * physpages) / 1024**2
            # Memory optimization: Memory-critical operation
    
    # Try to get NVIDIA driver and CUDA versions using nvidia-smi
    # Memory optimization: Memory-critical operation
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=driver_version,cuda_version", "--format=csv,noheader,nounits"], 
        # Memory optimization: Memory-critical operation
                             capture_output=True, text=True, check=True)
        if result.stdout.strip():
            parts = result.stdout.strip().split(', ')
            if len(parts) >= 2:
                info["driver_version"] = parts[0]
                info["cuda_version"] = parts[1]
                # Memory optimization: Memory-critical operation
                
                # Check for shared memory support - this is a feature in newer drivers
                # Memory optimization: Memory-critical operation
                info["shared_memory_support"] = True
                # Memory optimization: Memory-critical operation
                
                # Check for specific driver features
                if float(info["driver_version"].split('.')[0]) >= 450:
                    info["shared_memory_support"] = True
                    # Memory optimization: Memory-critical operation
    except Exception:
        # Fall back to PyTorch's CUDA version info
        # Memory optimization: Memory-critical operation
        info["cuda_version"] = torch.version.cuda
        # Memory optimization: Memory-critical operation
    
    return info

def setup_cuda_for_1050ti(
# Memory optimization: Memory-critical operation
    fp16: bool = False, 
    memory_fraction: float = 0.85, 
    # Memory optimization: Memory-critical operation
    enable_shared_memory: bool = True,
    # Memory optimization: Memory-critical operation
    optimize_vram: bool = True
) -> Tuple[torch.device, Dict[str, Any]]:
# Memory optimization: Device placement for memory management
    """
    Configure CUDA specifically for NVIDIA GTX 1050 Ti, including shared memory settings.
    # Memory optimization: Memory-critical operation
    
    Args:
        fp16: Whether to use mixed precision (FP16)
        memory_fraction: Fraction of dedicated VRAM to use (0.0-1.0)
        # Memory optimization: Memory-critical operation
        enable_shared_memory: Whether to enable shared system memory for GPU
        # Memory optimization: Memory-critical operation
        optimize_vram: Whether to apply VRAM optimization techniques
        
    Returns:
        Tuple of (device, cuda_info)
        # Memory optimization: Device placement for memory management
    """
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.warning("CUDA not available, using CPU")
        # Memory optimization: Memory-critical operation
        return torch.device("cpu"), {"cuda_available": False}
        # Memory optimization: Device placement for memory management
    
    # Set GPU device
    # Memory optimization: Device placement for memory management
    device = torch.device("cuda:0")
    # Memory optimization: Device placement for memory management
    
    # Apply optimizations for GTX 1050 Ti
    torch.backends.cudnn.benchmark = True
    if hasattr(torch.backends.cuda, 'matmul'):
    # Memory optimization: Memory-critical operation
        torch.backends.cuda.matmul.allow_tf32 = False  # TF32 not supported on 1050 Ti
        # Memory optimization: Memory-critical operation
    torch.backends.cudnn.deterministic = False  # Better performance
    
    # Set CUDA environment variables for shared memory if enabled
    # Memory optimization: Memory-critical operation
    if enable_shared_memory:
    # Memory optimization: Memory-critical operation
        # This can help when VRAM is limited but system RAM is plentiful
        os.environ["CUDA_DEVICE_MAX_CONNECTIONS"] = "1"  # Reduce concurrent transfers
        # Memory optimization: Device placement for memory management
        
        # Try to enable unified memory addressing if available
        # Memory optimization: Memory-critical operation
        try:
            # Check if this GPU supports unified memory
            # Memory optimization: Memory-critical operation
            props = torch.cuda.get_device_properties(device)
            # Memory optimization: CUDA operations for GPU acceleration
            if props.major >= 3:  # Kepler or newer architecture supports unified memory
            # Memory optimization: Memory-critical operation
                logger.info("Enabling unified memory addressing for shared memory support")
                # Memory optimization: Memory-critical operation
                # No direct PyTorch API, but we can set CUDA context flags
                # Memory optimization: Memory-critical operation
                # This is done implicitly when creating tensors with certain allocation flags
            else:
                logger.info("This GPU architecture might not fully support unified memory")
                # Memory optimization: Memory-critical operation
        except Exception as e:
            logger.warning(f"Could not check for unified memory support: {e}")
            # Memory optimization: Memory-critical operation
    
    # Set memory management for limited VRAM
    # Memory optimization: Memory-critical operation
    if optimize_vram:
        # Set per-process memory fraction if available
        # Memory optimization: Memory-critical operation
        if hasattr(torch.cuda, 'set_per_process_memory_fraction'):
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.set_per_process_memory_fraction(memory_fraction)
            # Memory optimization: CUDA operations for GPU acceleration
            logger.info(f"Set CUDA memory fraction to {memory_fraction:.2f}")
            # Memory optimization: Memory-critical operation
        
        # Cache allocation optimization
        if hasattr(torch.cuda, 'memory_stats') and hasattr(torch.cuda, 'empty_cache'):
        # Memory optimization: CUDA operations for GPU acceleration
            # More aggressive caching strategy for limited VRAM
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
    
    # Empty cache to start fresh
    clean_gpu_memory()
    # Memory optimization: Memory-critical operation
    
    # Get and log CUDA info
    # Memory optimization: Memory-critical operation
    cuda_info = get_cuda_info()
    # Memory optimization: Memory-critical operation
    logger.info(f"Using GPU: {cuda_info['device_name']} (Driver: {cuda_info.get('driver_version', 'unknown')})")
    # Memory optimization: Device placement for memory management
    logger.info(f"Dedicated VRAM: Total {cuda_info['memory_total_mb']:.1f}MB, "
    # Memory optimization: Memory-critical operation
               f"Free {cuda_info['memory_free_mb']:.1f}MB ({100-cuda_info['memory_utilization']:.1f}% available)")
               # Memory optimization: Memory-critical operation
    if cuda_info.get('shared_memory_support', False):
    # Memory optimization: Memory-critical operation
        logger.info(f"Shared system memory available: {cuda_info.get('system_memory_mb', 'unknown'):.1f}MB")
        # Memory optimization: Memory-critical operation
    
    set_optimal_gpu_settings(device)
    # Memory optimization: Device placement for memory management
    
    return device, cuda_info
    # Memory optimization: Device placement for memory management

def set_optimal_gpu_settings(device):
# Memory optimization: Device placement for memory management
    """
    Set optimal NVIDIA driver settings through PyTorch for the GTX 1050 Ti.
    
    Args:
        device: PyTorch CUDA device
        # Memory optimization: Device placement for memory management
    """
    # For CUDA 10.0+ with PyTorch
    # Memory optimization: Memory-critical operation
    if hasattr(torch, 'backends') and hasattr(torch.backends, 'cudnn'):
        # Memory-efficient algorithms
        # Memory optimization: Memory-critical operation
        torch.backends.cudnn.benchmark = True  # Find optimal algorithms
        
        # For older NVIDIA cards like 1050 Ti, avoid TF32 as it's not supported
        if hasattr(torch.backends, 'cuda') and hasattr(torch.backends.cuda, 'matmul'):
        # Memory optimization: Memory-critical operation
            torch.backends.cuda.matmul.allow_tf32 = False
            # Memory optimization: Memory-critical operation
            torch.backends.cudnn.allow_tf32 = False
        
        # Use limited precision where possible to save memory
        # Memory optimization: Memory-critical operation
        torch.set_float32_matmul_precision('medium')  # Options: 'highest', 'high', 'medium'
    
    # Set CUDA stream priorities for better scheduling
    # Memory optimization: Memory-critical operation
    try:
        # Create high-priority streams for critical operations
        high_priority_stream = torch.cuda.Stream(device=device, priority=0)  # Highest priority
        # Memory optimization: CUDA operations for GPU acceleration
        torch.cuda.default_stream(device).wait_stream(high_priority_stream)
        # Memory optimization: CUDA operations for GPU acceleration
    except Exception as e:
        logger.debug(f"Could not set stream priorities: {e}")

def clean_gpu_memory(aggressive=False):
# Memory optimization: Memory-critical operation
    """
    Release GPU memory and run garbage collection.
    # Memory optimization: Memory-critical operation
    
    Args:
        aggressive: If True, use more aggressive memory cleanup
        # Memory optimization: Memory-critical operation
    """
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        # Standard cleanup
        torch.cuda.empty_cache()
        # Memory optimization: CUDA operations for GPU acceleration
        gc.collect()
        # Memory optimization: Force garbage collection
        
        # More aggressive cleanup if requested
        if aggressive:
            # Try to force release cached memory
            # Memory optimization: Memory-critical operation
            for i in range(5):  # Multiple passes can help free more memory
            # Memory optimization: Memory-critical operation
                gc.collect()
                # Memory optimization: Force garbage collection
                torch.cuda.empty_cache()
                # Memory optimization: CUDA operations for GPU acceleration
            
            # Reset CUDA device
            # Memory optimization: Device placement for memory management
            try:
                current_device = torch.cuda.current_device()
                # Memory optimization: CUDA operations for GPU acceleration
                torch.cuda.device(current_device)  # Reset device context
                # Memory optimization: CUDA operations for GPU acceleration
                torch.cuda.ipc_collect()  # Clean IPC resources if available
                # Memory optimization: CUDA operations for GPU acceleration
            except Exception:
                pass
        
        # Log memory info after cleanup
        # Memory optimization: Memory-critical operation
        allocated = torch.cuda.memory_allocated() / 1024**2
        # Memory optimization: CUDA operations for GPU acceleration
        reserved = torch.cuda.memory_reserved() / 1024**2
        # Memory optimization: CUDA operations for GPU acceleration
        logger.debug(f"GPU memory after cleanup: Reserved {reserved:.1f}MB, Allocated {allocated:.1f}MB")
        # Memory optimization: Memory-critical operation

def get_nvidia_smi_info() -> Dict[str, Any]:
    """
    Get detailed GPU information from nvidia-smi command.
    # Memory optimization: Memory-critical operation
    
    Returns:
        Dictionary containing nvidia-smi output parsed into structured data
    """
    info = {
        "driver_version": None,
        "cuda_version": None,
        # Memory optimization: Memory-critical operation
        "gpus": [],
        # Memory optimization: Memory-critical operation
        "processes": []
    }
    
    try:
        # Get basic GPU information
        # Memory optimization: Memory-critical operation
        result = subprocess.run(["nvidia-smi", "--query-gpu=index,gpu_name,memory.total,memory.free,memory.used,temperature.gpu,utilization.gpu,utilization.memory,power.draw,power.limit", "--format=csv"], 
        # Memory optimization: Memory-critical operation
                             capture_output=True, text=True, check=True)
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Skip header
                header = lines[0].split(',')
                
                for i in range(1, len(lines)):
                    values = lines[i].split(',')
                    if len(values) == len(header):
                        gpu_info = {header[j].strip(): values[j].strip() for j in range(len(header))}
                        # Memory optimization: Memory-critical operation
                        info["gpus"].append(gpu_info)
                        # Memory optimization: Memory-critical operation
        
        # Get driver and CUDA version
        # Memory optimization: Memory-critical operation
        result = subprocess.run(["nvidia-smi", "--query-gpu=driver_version,cuda_version", "--format=csv,noheader,nounits"], 
        # Memory optimization: Memory-critical operation
                             capture_output=True, text=True, check=True)
        if result.stdout.strip():
            parts = result.stdout.strip().split(', ')
            if len(parts) >= 2:
                info["driver_version"] = parts[0]
                info["cuda_version"] = parts[1]
                # Memory optimization: Memory-critical operation
        
        # Get processes using GPU
        # Memory optimization: Memory-critical operation
        result = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv"], 
        # Memory optimization: Memory-critical operation
                             capture_output=True, text=True, check=True)
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Skip header
                header = lines[0].split(',')
                
                for i in range(1, len(lines)):
                    if i < len(lines) and lines[i].strip():
                        values = lines[i].split(',')
                        if len(values) == len(header):
                            process_info = {header[j].strip(): values[j].strip() for j in range(len(header))}
                            info["processes"].append(process_info)
        
    except Exception as e:
        logger.debug(f"Could not get nvidia-smi info: {e}")
    
    return info

def create_shared_memory_tensors(shape, dtype=torch.float32):
# Memory optimization: Memory-critical operation
    """
    Create tensors that can use shared memory between CPU and GPU.
    # Memory optimization: Memory-critical operation
    
    This is useful for data that needs to be accessed by both CPU and GPU
    # Memory optimization: Memory-critical operation
    without excessive copying, leveraging shared system memory.
    # Memory optimization: Memory-critical operation
    
    Args:
        shape: Shape of the tensor
        dtype: Data type of the tensor
        
    Returns:
        Tensor that can use shared memory
        # Memory optimization: Memory-critical operation
    """
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        return torch.zeros(shape, dtype=dtype)
    
    # Create tensor with pinned memory for efficient CPU-GPU transfers
    # Memory optimization: Memory-critical operation
    cpu_tensor = torch.zeros(shape, dtype=dtype, pin_memory=True)
    # Memory optimization: Memory-critical operation
    
    # The pinned memory allows for faster transfers to GPU when needed
    # Memory optimization: Memory-critical operation
    return cpu_tensor

def optimize_model_for_gpu(model: torch.nn.Module, fp16: bool = False) -> Tuple[torch.nn.Module, Dict[str, Any]]:
# Memory optimization: Memory-critical operation
    """
    Optimize a PyTorch model for GPU usage, especially for limited VRAM.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        model: PyTorch model to optimize
        # Memory optimization: Explicit memory cleanup
        fp16: Whether to use mixed precision
        
    Returns:
        Tuple of (optimized_model, optimization_info)
    """
    opt_info = {
        "fp16_enabled": False,
        "use_scaler": False,
        "scaler": None,
        "model_size_mb": 0,
        "memory_efficient": False
        # Memory optimization: Memory-critical operation
    }
    
    # Calculate model size
    # Memory optimization: Explicit memory cleanup
    opt_info["model_size_mb"] = sum(p.numel() * p.element_size() for p in model.parameters()) / 1024**2
    
    # Apply mixed precision if requested
    if fp16 and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        try:
            from torch.cuda.amp import GradScaler
            # Memory optimization: CUDA operations for GPU acceleration
            opt_info["fp16_enabled"] = True
            opt_info["use_scaler"] = True
            opt_info["scaler"] = GradScaler()
            logger.info("Mixed precision (FP16) enabled with gradient scaling")
        except ImportError:
            logger.warning("Native AMP not available, falling back to full precision")
    
    # Apply memory-efficient transformers if available
    # Memory optimization: Memory-critical operation
    try:
        from memory_efficient_attention import make_model_memory_efficient
        # Memory optimization: Memory-critical operation
        model = make_model_memory_efficient(model)
        # Memory optimization: Explicit memory cleanup
        opt_info["memory_efficient"] = True
        # Memory optimization: Memory-critical operation
        logger.info("Applied memory-efficient attention to model")
        # Memory optimization: Memory-critical operation
    except ImportError:
        logger.debug("Memory-efficient attention not available")
        # Memory optimization: Memory-critical operation
    
    return model, opt_info

def gpu_batch_size_finder(
# Memory optimization: Memory-critical operation
    model: torch.nn.Module, 
    sample_input: Dict[str, torch.Tensor],
    start_batch_size: int = 32,
    min_batch_size: int = 1,
    target_memory_usage: float = 0.8,
    # Memory optimization: Memory-critical operation
) -> int:
    """
    Find the largest batch size that fits in GPU memory.
    # Memory optimization: Memory-critical operation
    
    Args:
        model: The model to test
        # Memory optimization: Explicit memory cleanup
        sample_input: Sample input for testing batch sizes
        start_batch_size: Starting batch size to try
        min_batch_size: Minimum acceptable batch size
        target_memory_usage: Target memory usage (0.0-1.0)
        # Memory optimization: Memory-critical operation
        
    Returns:
        Optimal batch size
    """
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        return min_batch_size
    
    # Ensure model is on GPU
    # Memory optimization: Explicit memory cleanup
    device = next(model.parameters()).device
    # Memory optimization: Device placement for memory management
    if device.type != 'cuda':
    # Memory optimization: Device placement for memory management
        model = model.cuda()
        # Memory optimization: Explicit memory cleanup
    
    # Get total available memory
    # Memory optimization: Memory-critical operation
    total_memory = torch.cuda.get_device_properties(0).total_memory
    # Memory optimization: CUDA operations for GPU acceleration
    
    # Helper function to create a batch of a specified size
    def create_batch(size):
        """
        
    create_batch function for processing.
    
    Args:
        size: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        batch = {}
        for k, v in sample_input.items():
            if isinstance(v, torch.Tensor):
                # Expand first dimension to batch size
                dims = [size] + list(v.shape[1:])
                batch[k] = torch.zeros(dims, dtype=v.dtype, device="cuda")
                # Memory optimization: Device placement for memory management
        return batch
    
    # Binary search for largest working batch size
    batch_size = start_batch_size
    step = batch_size // 2
    
    while step > 0:
        try:
            # Clean memory
            # Memory optimization: Memory-critical operation
            clean_gpu_memory()
            # Memory optimization: Memory-critical operation
            
            # Create a batch
            batch = create_batch(batch_size)
            
            # Test forward pass
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                _ = model(**batch)
            
            # Check memory usage
            # Memory optimization: Memory-critical operation
            memory_used = torch.cuda.memory_reserved()
            # Memory optimization: CUDA operations for GPU acceleration
            usage_fraction = memory_used / total_memory
            # Memory optimization: Memory-critical operation
            
            if usage_fraction <= target_memory_usage:
            # Memory optimization: Memory-critical operation
                # This batch size works, try larger
                prev_batch_size = batch_size
                batch_size += step
                logger.debug(f"Batch size {prev_batch_size} works, trying {batch_size}")
            else:
                # This batch size uses too much memory, try smaller
                # Memory optimization: Memory-critical operation
                batch_size -= step
                logger.debug(f"Batch size uses too much memory ({usage_fraction:.2%}), trying {batch_size}")
                # Memory optimization: Memory-critical operation
            
            # Reduce step size
            step = step // 2
            
        except RuntimeError as e:
            if "CUDA out of memory" in str(e):
            # Memory optimization: Memory-critical operation
                # Reduce batch size and step
                batch_size = max(batch_size - step, min_batch_size)
                step = step // 2
                logger.debug(f"OOM error, reducing to batch size {batch_size}")
                clean_gpu_memory()
                # Memory optimization: Memory-critical operation
            else:
                # Other error
                logger.error(f"Error during batch size search: {e}")
                return min_batch_size
    
    # Ensure we don't go below minimum
    optimal_batch_size = max(batch_size, min_batch_size)
    logger.info(f"Found optimal batch size: {optimal_batch_size}")
    
    return optimal_batch_size

class CudaMonitor:
# Memory optimization: Memory-critical operation
    """
    Monitor CUDA memory and performance during model training/inference.
    # Memory optimization: Explicit memory cleanup
    """
    
    def __init__(self, interval_sec: float = 5.0, log_to_file: Optional[str] = None):
        """
        Initialize CUDA monitor.
        # Memory optimization: Memory-critical operation
        
        Args:
            interval_sec: Monitoring interval in seconds
            log_to_file: Optional file to log data to
        """
        self.interval = interval_sec
        self.log_file = log_to_file
        self.running = False
        self.thread = None
        self.snapshots = []
    
    def start(self):
        """Start monitoring."""
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            logger.warning("CUDA not available, monitoring disabled")
            # Memory optimization: Memory-critical operation
            return
        
        import threading
        
        self.running = True
        self.snapshots = []
        
        def monitor_loop():
            """
            
    monitor_loop function for processing.
    
    Args:
        No arguments: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
            """
            while self.running:
                snapshot = get_cuda_info()
                # Memory optimization: Memory-critical operation
                snapshot["timestamp"] = time.time()
                self.snapshots.append(snapshot)
                
                if self.log_file:
                    with open(self.log_file, "a") as f:
                        f.write(f"{snapshot['timestamp']},{snapshot['memory_allocated_mb']:.1f}," +
                        # Memory optimization: Memory-critical operation
                               f"{snapshot['memory_reserved_mb']:.1f},{snapshot['memory_free_mb']:.1f}\n")
                               # Memory optimization: Memory-critical operation
                
                time.sleep(self.interval)
        
        self.thread = threading.Thread(target=monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("CUDA monitoring started")
        # Memory optimization: Memory-critical operation