#!/usr/bin/env python3
"""
ImpressionCore: Gpu Utils

Module for gpu utils functionality in the ImpressionCore framework.

File: core\gpu_utils.py
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
Dependencies: [torch, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements gpu utils functionality for the
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
from src.core.gpu_utils import MemoryTracker
instance = MemoryTracker()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import gc
import sys
import logging
import torch
import psutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, Union, Optional, Any, Tuple, List

# Configure logging
logger = logging.getLogger(__name__)

# Environment variable to force CPU usage even when CUDA is available
# Memory optimization: Memory-critical operation
CPU_FORCE_ENV = "IMPRESSIONCORE_FORCE_CPU"
# Legacy environment variable support for older code paths
LEGACY_CPU_FORCE_ENV = "CORE_FORCE_CPU"
# Environment variable to set memory fraction
# Memory optimization: Memory-critical operation
MEMORY_FRACTION_ENV = "CORE_GPU_MEMORY_FRACTION"
# Memory optimization: Memory-critical operation
# Default memory fraction (of available GPU memory)
# Memory optimization: Memory-critical operation
DEFAULT_MEMORY_FRACTION = 0.85
# Memory optimization: Memory-critical operation
# Environment variable for CUDA toolkit path
# Memory optimization: Memory-critical operation
CUDA_PATH_ENV = "CUDA_PATH"
# Memory optimization: Memory-critical operation
# Default CUDA paths to check
# Memory optimization: Memory-critical operation
DEFAULT_CUDA_PATHS = [
# Memory optimization: Memory-critical operation
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v11.8",  # Move v11.8 to top since it's installed
    # Memory optimization: Memory-critical operation
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.8",
    # Memory optimization: Memory-critical operation
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.0",
    # Memory optimization: Memory-critical operation
]

# Add specific settings for GTX 1050 Ti with shared memory
# Memory optimization: Memory-critical operation
IS_SHARED_MEMORY_GPU = True  # Set based on the detected configuration
# Memory optimization: Memory-critical operation
SHARED_MEMORY_SIZE_GB = 16.0  # Total shared system memory
# Memory optimization: Memory-critical operation
DEDICATED_VRAM_SIZE_GB = 4.0  # Dedicated VRAM size

def check_pytorch_cuda_build() -> Tuple[bool, str, str]:
# Memory optimization: Memory-critical operation
    """
    Check if PyTorch was built with CUDA support.
    # Memory optimization: Memory-critical operation
    
    Returns:
        Tuple of (has_cuda_build, pytorch_version, recommended_action)
        # Memory optimization: Memory-critical operation
    """
    # Check PyTorch version and CUDA info
    # Memory optimization: Memory-critical operation
    pytorch_version = torch.__version__
    cuda_build = torch.version.cuda is not None
    # Memory optimization: Memory-critical operation
    
    if not cuda_build:
    # Memory optimization: Memory-critical operation
        # PyTorch CPU-only build detected
        recommended_action = (
            "Reinstall PyTorch with CUDA support using:\n"
            # Memory optimization: Memory-critical operation
            "python tools/install_pytorch_cuda.py\n"
            # Memory optimization: Memory-critical operation
            "or manually with:\n"
            "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
        )
        return False, f"{pytorch_version} (CPU-only)", recommended_action
    
    return True, f"{pytorch_version} (CUDA {torch.version.cuda})", "PyTorch CUDA build detected"
    # Memory optimization: Memory-critical operation

def setup_cuda_environment():
# Memory optimization: Memory-critical operation
    """
    Set up CUDA environment variables to ensure PyTorch can find CUDA.
    # Memory optimization: Memory-critical operation
    Returns True if successful, False if failed.
    """
    # Skip if already forced to CPU
    if os.environ.get(CPU_FORCE_ENV, "").lower() in ("1", "true", "yes"):
        return False
    
    # Check if PyTorch is built with CUDA support first
    # Memory optimization: Memory-critical operation
    has_cuda_build, version, _ = check_pytorch_cuda_build()
    # Memory optimization: Memory-critical operation
    if not has_cuda_build:
    # Memory optimization: Memory-critical operation
        logger.warning(f"PyTorch {version} detected - missing CUDA support")
        # Memory optimization: Memory-critical operation
        logger.warning("Environment setup will proceed, but you need to reinstall PyTorch with CUDA")
        # Memory optimization: Memory-critical operation
    
    # Get CUDA path from environment or try default locations
    # Memory optimization: Memory-critical operation
    cuda_path = os.environ.get(CUDA_PATH_ENV)
    # Memory optimization: Memory-critical operation
    
    # If not set, try to find CUDA toolkit in default locations
    # Memory optimization: Memory-critical operation
    if not cuda_path:
    # Memory optimization: Memory-critical operation
        for path in DEFAULT_CUDA_PATHS:
        # Memory optimization: Memory-critical operation
            if os.path.exists(path):
                cuda_path = path
                # Memory optimization: Memory-critical operation
                logger.info(f"Found CUDA toolkit at: {cuda_path}")
                # Memory optimization: Memory-critical operation
                break
    
    if cuda_path:
    # Memory optimization: Memory-critical operation
        # Set required environment variables
        os.environ[CUDA_PATH_ENV] = cuda_path
        # Memory optimization: Memory-critical operation
        os.environ["CUDA_HOME"] = cuda_path
        # Memory optimization: Memory-critical operation
        
        # Add CUDA bin to PATH if not already present
        # Memory optimization: Memory-critical operation
        cuda_bin = os.path.join(cuda_path, "bin")
        # Memory optimization: Memory-critical operation
        if cuda_bin not in os.environ.get("PATH", ""):
        # Memory optimization: Memory-critical operation
            os.environ["PATH"] = cuda_bin + os.pathsep + os.environ.get("PATH", "")
            # Memory optimization: Memory-critical operation
        
        # Add CUDA lib to PATH or LD_LIBRARY_PATH
        # Memory optimization: Memory-critical operation
        cuda_lib = os.path.join(cuda_path, "lib64" if platform.system() == "Linux" else "lib")
        # Memory optimization: Memory-critical operation
        if platform.system() == "Windows":
            if cuda_lib not in os.environ.get("PATH", ""):
            # Memory optimization: Memory-critical operation
                os.environ["PATH"] = cuda_lib + os.pathsep + os.environ.get("PATH", "")
                # Memory optimization: Memory-critical operation
        else:
            if cuda_lib not in os.environ.get("LD_LIBRARY_PATH", ""):
            # Memory optimization: Memory-critical operation
                os.environ["LD_LIBRARY_PATH"] = cuda_lib + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
                # Memory optimization: Memory-critical operation
        
        logger.info(f"CUDA environment variables configured with toolkit at: {cuda_path}")
        # Memory optimization: Memory-critical operation
        return True
    else:
        logger.warning("CUDA toolkit not found, cannot configure environment variables")
        # Memory optimization: Memory-critical operation
        return False

def verify_cuda_installation() -> Tuple[bool, str]:
# Memory optimization: Memory-critical operation
    """
    Verify that CUDA is properly installed and accessible.
    # Memory optimization: Memory-critical operation
    
    Returns:
        Tuple of (is_cuda_working, message)
        # Memory optimization: Memory-critical operation
    """
    # First check if PyTorch was built with CUDA support
    # Memory optimization: Memory-critical operation
    has_cuda_build, version, recommended_action = check_pytorch_cuda_build()
    # Memory optimization: Memory-critical operation
    if not has_cuda_build:
    # Memory optimization: Memory-critical operation
        return False, f"PyTorch was not built with CUDA support. {recommended_action}"
        # Memory optimization: Memory-critical operation
    
    cuda_available = torch.cuda.is_available()
    # Memory optimization: CUDA operations for GPU acceleration
    if not cuda_available:
    # Memory optimization: Memory-critical operation
        # Check if NVIDIA driver is working
        try:
            if platform.system() == "Windows":
                # Windows - use nvidia-smi
                process = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if process.returncode != 0:
                    return False, "NVIDIA driver not working properly. Check nvidia-smi output."
            else:
                # Linux - use lspci
                process = subprocess.run(["lspci", "|", "grep", "-i", "nvidia"], stdout=subprocess.PIPE, shell=True, text=True)
                if not process.stdout:
                    return False, "NVIDIA driver not detected. Ensure drivers are installed."
        except Exception as e:
            return False, f"Error checking NVIDIA driver: {e}"
    
    # Suggest adding CUDA paths to environment variables if missing
    # Memory optimization: Memory-critical operation
    cuda_path = os.environ.get("CUDA_PATH") or os.environ.get("CUDA_HOME")
    # Memory optimization: Memory-critical operation
    if not cuda_path:
    # Memory optimization: Memory-critical operation
        return False, "CUDA toolkit not found. Add CUDA_PATH or CUDA_HOME to environment variables."
        # Memory optimization: Memory-critical operation

    return True, "CUDA is working properly."
    # Memory optimization: Memory-critical operation

def is_shared_memory_gpu() -> Tuple[bool, float, float]:
# Memory optimization: Memory-critical operation
    """
    Check if the GPU uses shared memory and get memory details.
    # Memory optimization: Memory-critical operation
    
    Returns:
        Tuple of (is_shared_memory, dedicated_vram_gb, total_shared_memory_gb)
        # Memory optimization: Memory-critical operation
    """
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        return False, 0.0, 0.0
        
    try:
        # Get GPU name and properties
        # Memory optimization: Memory-critical operation
        device_name = torch.cuda.get_device_name(0)
        # Memory optimization: CUDA operations for GPU acceleration
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Common shared memory GPUs
        # Memory optimization: Memory-critical operation
        shared_memory_keywords = [
        # Memory optimization: Memory-critical operation
            "1050", "MX", "integrated", "UHD", "Iris", "Vega", "Radeon"
        ]
        
        is_shared = any(keyword in device_name for keyword in shared_memory_keywords)
        # Memory optimization: Device placement for memory management
        
        # If it appears to be a shared memory GPU, get system RAM
        # Memory optimization: Memory-critical operation
        if is_shared:
            system_ram = psutil.virtual_memory().total / (1024**3)  # GB
            # Memory optimization: Memory-critical operation
            return True, total_memory, system_ram
            # Memory optimization: Memory-critical operation
        else:
            return False, total_memory, total_memory  # Not shared, dedicated = total
            # Memory optimization: Memory-critical operation
    except Exception as e:
        logger.warning(f"Error checking shared memory GPU: {e}")
        # Memory optimization: Memory-critical operation
        return False, 0.0, 0.0

def optimize_memory_settings():
# Memory optimization: Memory-critical operation
    """
    Set optimal memory settings for the detected GPU configuration.
    # Memory optimization: Memory-critical operation
    
    This is particularly important for GPUs with shared memory like the GTX 1050 Ti.
    # Memory optimization: Memory-critical operation
    """
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        return
        
    # Check if this is a shared memory GPU
    # Memory optimization: Memory-critical operation
    is_shared, dedicated_vram, total_shared = is_shared_memory_gpu()
    # Memory optimization: Memory-critical operation
    
    if is_shared:
        logger.info(f"Detected shared memory GPU with {dedicated_vram:.2f}GB dedicated VRAM")
        # Memory optimization: Memory-critical operation
        logger.info(f"System has {total_shared:.2f}GB total shared memory")
        # Memory optimization: Memory-critical operation
        
        # For shared memory GPUs, be more conservative with memory usage
        # Memory optimization: Memory-critical operation
        if "1050" in torch.cuda.get_device_name(0):
        # Memory optimization: CUDA operations for GPU acceleration
            # GTX 1050 Ti specific settings
            torch.cuda.set_per_process_memory_fraction(0.7)  # More conservative
            # Memory optimization: CUDA operations for GPU acceleration
            
            # Enable memory-efficient features
            # Memory optimization: Memory-critical operation
            if hasattr(torch.cuda, "amp") and hasattr(torch.cuda.amp, "autocast"):
            # Memory optimization: CUDA operations for GPU acceleration
                # Enable automatic mixed precision for memory efficiency
                # Memory optimization: Memory-critical operation
                torch.set_float32_matmul_precision('medium')
            
            # Set cuDNN to be memory efficient rather than speed focused
            # Memory optimization: Memory-critical operation
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True
            
            logger.info("Applied memory-optimized settings for GTX 1050 Ti")
            # Memory optimization: Memory-critical operation
        else:
            # Generic shared memory GPU settings
            # Memory optimization: Memory-critical operation
            torch.cuda.set_per_process_memory_fraction(0.8)
            # Memory optimization: CUDA operations for GPU acceleration
    else:
        # For dedicated GPUs, we can be more aggressive with memory usage
        # Memory optimization: Memory-critical operation
        torch.cuda.set_per_process_memory_fraction(0.95)
        # Memory optimization: CUDA operations for GPU acceleration
        torch.backends.cudnn.benchmark = True
        
    logger.info(f"GPU memory fraction set to {torch.cuda.get_per_process_memory_fraction()}")
    # Memory optimization: CUDA operations for GPU acceleration

def get_device() -> torch.device:
# Memory optimization: Device placement for memory management
    """
    Get the optimal device for computation (CUDA if available and not forced to CPU).
    # Memory optimization: Device placement for memory management
    First attempts to configure CUDA environment if needed.
    # Memory optimization: Memory-critical operation
    
    Returns:
        torch.device: The selected device
        # Memory optimization: Device placement for memory management
    """
    # Check if CPU is forced via environment variables
    force_cpu = os.environ.get(CPU_FORCE_ENV, "").lower() in ("1", "true", "yes")
    legacy_force_cpu = os.environ.get(LEGACY_CPU_FORCE_ENV, "").lower() in ("1", "true", "yes")
    if force_cpu or legacy_force_cpu:
        logger.info("Forced CPU usage via environment variable")
        return torch.device("cpu")
        # Memory optimization: Device placement for memory management
    
    # Try to set up CUDA environment if not already done
    # Memory optimization: Memory-critical operation
    setup_cuda_environment()
    # Memory optimization: Memory-critical operation
    
    # Check if CUDA is actually available after environment setup
    # Memory optimization: Memory-critical operation
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.warning("CUDA still not available after environment setup, falling back to CPU")
        # Memory optimization: Memory-critical operation
        is_working, message = verify_cuda_installation()
        # Memory optimization: Memory-critical operation
        logger.warning(f"CUDA verification: {message}")
        # Memory optimization: Memory-critical operation
        return torch.device("cpu")
        # Memory optimization: Device placement for memory management
    
    # CUDA is available, verify it's working
    # Memory optimization: Memory-critical operation
    is_working, message = verify_cuda_installation()
    # Memory optimization: Memory-critical operation
    if not is_working:
        logger.warning(f"CUDA verification failed: {message}")
        # Memory optimization: Memory-critical operation
        logger.warning("Falling back to CPU")
        return torch.device("cpu")
        # Memory optimization: Device placement for memory management
    
    # CUDA is working, configure it
    # Memory optimization: Memory-critical operation
    device_name = torch.cuda.get_device_name(0)
    # Memory optimization: CUDA operations for GPU acceleration
    vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
    # Memory optimization: CUDA operations for GPU acceleration
    logger.info(f"Using CUDA device: {device_name} with {vram_total:.2f} GB VRAM")
    # Memory optimization: Device placement for memory management
    
    # Apply optimized memory settings
    # Memory optimization: Memory-critical operation
    optimize_memory_settings()
    # Memory optimization: Memory-critical operation
    
    # Enable tensor cores for faster computation on supported hardware
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True  # For Ampere+ GPUs
        # Memory optimization: Memory-critical operation
        torch.backends.cudnn.allow_tf32 = True
    
    return torch.device("cuda")
    # Memory optimization: Device placement for memory management

def clear_gpu_memory() -> None:
# Memory optimization: Memory-critical operation
    """
    Clear GPU memory cache to free up resources.
    # Memory optimization: Memory-critical operation
    
    This helps prevent memory fragmentation and OOM errors with models 
    # Memory optimization: Memory-critical operation
    running on limited VRAM.
    """
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        # Empty CUDA cache to free up memory
        # Memory optimization: Memory-critical operation
        torch.cuda.empty_cache()
        # Memory optimization: CUDA operations for GPU acceleration
        # Force garbage collection
        gc.collect()
        # Memory optimization: Force garbage collection
        logger.debug("GPU memory cleared")
        # Memory optimization: Memory-critical operation


def get_memory_info() -> Dict[str, Union[float, Dict[str, float]]]:
# Memory optimization: Memory-critical operation
    """
    Get memory information for both system RAM and GPU VRAM (if available).
    # Memory optimization: Memory-critical operation
    
    Returns:
        Dict with memory information in GB
        # Memory optimization: Memory-critical operation
    """
    memory_info = {}
    # Memory optimization: Memory-critical operation
    
    # System RAM information
    ram = psutil.virtual_memory()
    # Memory optimization: Memory-critical operation
    memory_info["system_ram"] = {
    # Memory optimization: Memory-critical operation
        "total": ram.total / (1024**3),  # GB
        "available": ram.available / (1024**3),  # GB
        "used": ram.used / (1024**3),  # GB
        "percent": ram.percent
    }
    
    # GPU VRAM information (if available)
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        gpu_index = 0
        # Memory optimization: Memory-critical operation
        props = torch.cuda.get_device_properties(gpu_index)
        # Memory optimization: CUDA operations for GPU acceleration
        vram_total = props.total_memory / (1024**3)  # GB
        # Memory optimization: Memory-critical operation
        
        # Get current usage
        vram_allocated = torch.cuda.memory_allocated(gpu_index) / (1024**3)  # GB
        # Memory optimization: CUDA operations for GPU acceleration
        vram_reserved = torch.cuda.memory_reserved(gpu_index) / (1024**3)  # GB
        # Memory optimization: CUDA operations for GPU acceleration
        
        memory_info["gpu_vram"] = {
        # Memory optimization: Memory-critical operation
            "total": vram_total,
            "allocated": vram_allocated,
            "reserved": vram_reserved,
            "available": vram_total - vram_allocated,
            "device_name": props.name
            # Memory optimization: Device placement for memory management
        }
    
    return memory_info
    # Memory optimization: Memory-critical operation


def optimize_for_inference(model: torch.nn.Module) -> torch.nn.Module:
    """
    Optimize model for inference on limited VRAM environments.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        model: The PyTorch model to optimize
        # Memory optimization: Explicit memory cleanup
        
    Returns:
        Optimized model
    """
    # Set model to evaluation mode
    # Memory optimization: Explicit memory cleanup
    model.eval()
    
    # Use inference mode to disable gradient computation
    with torch.inference_mode():
        torch._C._jit_set_profiling_mode(False)
        
        try:
            # Try to use torch.jit.optimize_for_inference for extra performance
            model = torch.jit.optimize_for_inference(torch.jit.script(model))
            # Memory optimization: Explicit memory cleanup
            logger.info("Successfully optimized model using TorchScript")
            # Memory optimization: Explicit memory cleanup
        except Exception as e:
            logger.warning(f"Could not optimize with TorchScript: {e}")
    
    # For models running on GPU with limited memory (like GTX 1050 Ti 4GB)
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        try:
            # Try to use half-precision (FP16) for inference
            model = model.half()
            # Memory optimization: Explicit memory cleanup
            logger.info("Converted model to half precision (FP16)")
            # Memory optimization: Explicit memory cleanup
        except Exception as e:
            logger.warning(f"Could not convert to half precision: {e}")
    
    return model


def adaptive_batch_size(model_size_mb: int, max_batch_size: int = 16) -> int:
    """
    Calculate an appropriate batch size based on available VRAM.
    
    Args:
        model_size_mb: Estimated model size in MB
        # Memory optimization: Explicit memory cleanup
        max_batch_size: Maximum batch size to consider
        
    Returns:
        Recommended batch size
    """
    # Default conservative batch size for CPU
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        return 1
    
    # Get available memory in MB
    # Memory optimization: Memory-critical operation
    free_memory_mb = torch.cuda.get_device_properties(0).total_memory / (1024**2)
    # Memory optimization: CUDA operations for GPU acceleration
    allocated_memory_mb = torch.cuda.memory_allocated(0) / (1024**2)
    # Memory optimization: CUDA operations for GPU acceleration
    available_memory_mb = free_memory_mb - allocated_memory_mb
    # Memory optimization: Memory-critical operation
    
    # Safety factor: only use a portion of available memory
    # Memory optimization: Memory-critical operation
    safety_factor = 0.7
    usable_memory_mb = available_memory_mb * safety_factor
    # Memory optimization: Memory-critical operation
    
    # Estimate memory required per sample (model size + overhead)
    # Memory optimization: Explicit memory cleanup
    memory_per_sample_mb = model_size_mb * 1.5
    # Memory optimization: Memory-critical operation
    
    # Calculate batch size
    batch_size = max(1, min(max_batch_size, int(usable_memory_mb / memory_per_sample_mb)))
    # Memory optimization: Memory-critical operation
    
    logger.info(f"Adaptive batch size: {batch_size} (available memory: {available_memory_mb:.2f} MB)")
    # Memory optimization: Memory-critical operation
    return batch_size


def check_vram_requirements(model_size_gb: float) -> Tuple[bool, str]:
    """
    Check if there's enough VRAM for the model.
    
    Args:
        model_size_gb: Estimated model size in GB
        # Memory optimization: Explicit memory cleanup
        
    Returns:
        Tuple of (has_enough_vram, message)
    """
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        return False, "GPU not available"
        # Memory optimization: Memory-critical operation
    
    # Get total VRAM in GB
    vram_total_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    # Memory optimization: CUDA operations for GPU acceleration
    
    # Need at least 2x model size for safe operation (model + workspace)
    # Memory optimization: Explicit memory cleanup
    required_vram_gb = model_size_gb * 2.0
    
    if vram_total_gb >= required_vram_gb:
        return True, f"Sufficient VRAM: {vram_total_gb:.1f}GB available, {required_vram_gb:.1f}GB required"
    else:
        # If not enough VRAM, suggest options
        message = (
            f"Insufficient VRAM: {vram_total_gb:.1f}GB available, {required_vram_gb:.1f}GB required. "
            f"Consider using 8-bit quantization, a smaller model, or CPU inference."
        )
        return False, message


def get_gpu_info() -> Dict[str, Any]:
# Memory optimization: Memory-critical operation
    """
    Get detailed information about the GPU.
    # Memory optimization: Memory-critical operation

    Returns:
        Dictionary with GPU details
        # Memory optimization: Memory-critical operation
    """
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        return {"error": "CUDA not available"}
        # Memory optimization: Memory-critical operation

    try:
        info = {}

        # Basic device info
        # Memory optimization: Device placement for memory management
        device_count = torch.cuda.device_count()
        # Memory optimization: CUDA operations for GPU acceleration
        info["device_count"] = device_count
        # Memory optimization: Device placement for memory management

        # Detailed per-device info
        # Memory optimization: Device placement for memory management
        devices = []
        # Memory optimization: Device placement for memory management
        for i in range(device_count):
        # Memory optimization: Device placement for memory management
            device_props = torch.cuda.get_device_properties(i)
            # Memory optimization: CUDA operations for GPU acceleration
            device = {
            # Memory optimization: Device placement for memory management
                "name": device_props.name,
                # Memory optimization: Device placement for memory management
                "compute_capability": f"{device_props.major}.{device_props.minor}",
                # Memory optimization: Device placement for memory management
                "total_memory_gb": device_props.total_memory / (1024**3),
                # Memory optimization: Device placement for memory management
                "multi_processor_count": device_props.multi_processor_count,
                # Memory optimization: Device placement for memory management
            }

            # Safely access optional attributes
            device["max_threads_per_block"] = getattr(device_props, "max_threads_per_block", "N/A")
            # Memory optimization: Device placement for memory management

            devices.append(device)
            # Memory optimization: Device placement for memory management

        info["devices"] = devices
        # Memory optimization: Device placement for memory management
        return info

    except Exception as e:
        return {"error": f"Error retrieving GPU info: {e}"}
        # Memory optimization: Memory-critical operation

class MemoryTracker:
# Memory optimization: Memory-critical operation
    """
    Tracks memory usage for both GPU and system RAM.
    # Memory optimization: Memory-critical operation
    
    Useful for monitoring memory usage during intensive operations,
    # Memory optimization: Memory-critical operation
    especially on limited memory environments like the GTX 1050 Ti.
    # Memory optimization: Memory-critical operation
    """
    def __init__(self, log_interval_sec: float = 0.1):
        """
        
    __init__ function for processing.
    
    Args:
        self, log_interval_sec: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.log_interval_sec = log_interval_sec
        self.tracking = False
        self.samples = []
        self.peak_gpu_memory = 0
        # Memory optimization: Memory-critical operation
        self.peak_system_memory = 0
        # Memory optimization: Memory-critical operation
        self._thread = None
        
    def start(self):
        """Start tracking memory usage."""
        # Memory optimization: Memory-critical operation
        if self.tracking:
            return
            
        import threading
        import time
        
        self.tracking = True
        self.samples = []
        
        def _track_memory():
        # Memory optimization: Memory-critical operation
            """
            
    _track_memory function for processing.
    # Memory optimization: Memory-critical operation
    
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
            while self.tracking:
                if torch.cuda.is_available():
                # Memory optimization: CUDA operations for GPU acceleration
                    gpu_allocated = torch.cuda.memory_allocated() / (1024**2)  # MB
                    # Memory optimization: CUDA operations for GPU acceleration
                    gpu_reserved = torch.cuda.memory_reserved() / (1024**2)  # MB
                    # Memory optimization: CUDA operations for GPU acceleration
                    self.peak_gpu_memory = max(self.peak_gpu_memory, gpu_allocated)
                    # Memory optimization: Memory-critical operation
                else:
                    gpu_allocated = 0
                    # Memory optimization: Memory-critical operation
                    gpu_reserved = 0
                    # Memory optimization: Memory-critical operation
                    
                system_memory = psutil.virtual_memory()
                # Memory optimization: Memory-critical operation
                system_used = system_memory.used / (1024**2)  # MB
                # Memory optimization: Memory-critical operation
                self.peak_system_memory = max(self.peak_system_memory, system_used)
                # Memory optimization: Memory-critical operation
                
                self.samples.append({
                    'time': time.time(),
                    'gpu_allocated': gpu_allocated,
                    # Memory optimization: Memory-critical operation
                    'gpu_reserved': gpu_reserved,
                    # Memory optimization: Memory-critical operation
                    'system_used': system_used,
                    'system_percent': system_memory.percent
                    # Memory optimization: Memory-critical operation
                })
                
                time.sleep(self.log_interval_sec)
        
        self._thread = threading.Thread(target=_track_memory, daemon=True)
        # Memory optimization: Memory-critical operation
        self._thread.start()
        
    def stop(self) -> Dict[str, Any]:
        """
        Stop tracking memory usage and return statistics.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dict with memory usage statistics
            # Memory optimization: Memory-critical operation
        """
        self.tracking = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
            
        # Calculate statistics
        if not self.samples:
            return {
                'peak_gpu_mb': 0,
                # Memory optimization: Memory-critical operation
                'peak_system_mb': 0,
                'avg_gpu_mb': 0,
                # Memory optimization: Memory-critical operation
                'avg_system_mb': 0,
                'samples_count': 0
            }
            
        avg_gpu = sum(s['gpu_allocated'] for s in self.samples) / len(self.samples)
        # Memory optimization: Memory-critical operation
        avg_system = sum(s['system_used'] for s in self.samples) / len(self.samples)
        
        return {
            'peak_gpu_mb': self.peak_gpu_memory,
            # Memory optimization: Memory-critical operation
            'peak_system_mb': self.peak_system_memory,
            # Memory optimization: Memory-critical operation
            'avg_gpu_mb': avg_gpu,
            # Memory optimization: Memory-critical operation
            'avg_system_mb': avg_system,
            'samples_count': len(self.samples),
            'samples': self.samples
        }
        
    def __enter__(self):
        """
        
    __enter__ function for processing.
    
    Args:
        self: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        
    __exit__ function for processing.
    
    Args:
        self, exc_type, exc_val, exc_tb: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        return self.stop()

def get_optimal_batch_size(
    model_size_mb: int, 
    sequence_length: int = 512, 
    dtype: torch.dtype = torch.float32,
    safety_factor: float = 0.8
) -> int:
    """
    Calculate optimal batch size based on available VRAM and model parameters.
    # Memory optimization: Explicit memory cleanup
    
    Specifically optimized for shared memory GPUs like GTX 1050 Ti.
    # Memory optimization: Memory-critical operation
    
    Args:
        model_size_mb: Size of model parameters in MB
        # Memory optimization: Explicit memory cleanup
        sequence_length: Length of input sequences
        dtype: Data type for calculations
        safety_factor: Factor to avoid using all available memory
        # Memory optimization: Memory-critical operation
        
    Returns:
        Optimal batch size
    """
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        return 1
        
    # Get available memory
    # Memory optimization: Memory-critical operation
    total_memory = torch.cuda.get_device_properties(0).total_memory
    # Memory optimization: CUDA operations for GPU acceleration
    allocated_memory = torch.cuda.memory_allocated()
    # Memory optimization: CUDA operations for GPU acceleration
    reserved_memory = torch.cuda.memory_reserved()
    # Memory optimization: CUDA operations for GPU acceleration
    
    # Use reserved memory if it's larger than allocated
    # Memory optimization: Memory-critical operation
    used_memory = max(allocated_memory, reserved_memory)
    # Memory optimization: Memory-critical operation
    available_memory = total_memory - used_memory
    # Memory optimization: Memory-critical operation
    
    # Apply safety factor
    usable_memory = available_memory * safety_factor
    # Memory optimization: Memory-critical operation
    
    # Calculate memory needed per sample
    # Memory optimization: Memory-critical operation
    dtype_size = {
        torch.float32: 4,
        torch.float16: 2,
        torch.int8: 1,
        torch.int32: 4
    }.get(dtype, 4)  # Default to float32 size
    
    # For transformers, need memory for:
    # Memory optimization: Memory-critical operation
    # - Input ids
    # - Attention mask
    # - Position ids
    # - KV cache (grows with sequence length)
    # - Activations (proportional to model size)
    # Memory optimization: Explicit memory cleanup
    # - Output logits
    
    # Estimate memory per sample
    # Memory optimization: Memory-critical operation
    memory_per_token = 13 * dtype_size  # Empirical value for transformer models
    # Memory optimization: Memory-critical operation
    memory_per_sample = sequence_length * memory_per_token
    # Memory optimization: Memory-critical operation
    
    # Add overhead for model activations
    # Memory optimization: Explicit memory cleanup
    activation_overhead = model_size_mb * 0.4 * 1024 * 1024  # Convert to bytes
    
    # Calculate batch size
    if memory_per_sample > 0:
    # Memory optimization: Memory-critical operation
        max_batch_size = int((usable_memory - activation_overhead) / memory_per_sample)
        # Memory optimization: Memory-critical operation
        batch_size = max(1, max_batch_size)
    else:
        batch_size = 1
        
    # Adjust batch size for GTX 1050 Ti with shared memory
    # Memory optimization: Memory-critical operation
    device_name = torch.cuda.get_device_name(0).lower()
    # Memory optimization: CUDA operations for GPU acceleration
    if "1050" in device_name:
    # Memory optimization: Device placement for memory management
        # Be more conservative with GTX 1050 Ti
        batch_size = min(batch_size, 8)
        
        # Adjust based on sequence length
        if sequence_length > 1024:
            batch_size = min(batch_size, 4)
        if sequence_length > 2048:
            batch_size = min(batch_size, 2)
            
    logger.info(f"Calculated optimal batch size: {batch_size} for sequence length {sequence_length}")
    return batch_size
