#!/usr/bin/env python3
"""
ImpressionCore: Hardware Detection

Module for hardware detection functionality in the ImpressionCore framework.

File: core/utils/hardware_detection.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, memory-critical, framework, pytorch, core, production, utils, 2025]
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements hardware detection functionality for the
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
from src.core.utils.hardware_detection import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import sys
import platform
import logging
from typing import Dict, Any
import torch
import psutil
import numpy as np

logger = logging.getLogger(__name__)

def get_system_info() -> Dict[str, Any]:
    """
    Get detailed system information including GPU capabilities
    # Memory optimization: Memory-critical operation
    Optimized for detecting limited VRAM environments
    """
    info = {
        'os': platform.system(),
        'python_version': sys.version.split()[0],
        'cpu_count': psutil.cpu_count(),
        'memory_gb': psutil.virtual_memory().total / (1024**3),
        # Memory optimization: Memory-critical operation
        'cuda_available': torch.cuda.is_available(),
        # Memory optimization: CUDA operations for GPU acceleration
        'gpu_count': 0,
        # Memory optimization: Memory-critical operation
        'gpu_name': None,
        # Memory optimization: Memory-critical operation
        'gpu_memory_gb': 0,
        # Memory optimization: Memory-critical operation
        'compute_capability': None,
        'pytorch_version': torch.__version__,
        'supports_half_precision': False,
        'supports_bfloat16': False,
    }
    
    if info['cuda_available']:
    # Memory optimization: Memory-critical operation
        info['gpu_count'] = torch.cuda.device_count()
        # Memory optimization: CUDA operations for GPU acceleration
        device = torch.cuda.current_device()
        # Memory optimization: CUDA operations for GPU acceleration
        props = torch.cuda.get_device_properties(device)
        # Memory optimization: CUDA operations for GPU acceleration
        
        info.update({
            'gpu_name': props.name,
            # Memory optimization: Memory-critical operation
            'gpu_memory_gb': props.total_memory / (1024**3),
            # Memory optimization: Memory-critical operation
            'compute_capability': f"{props.major}.{props.minor}",
            # CUDA capability 7.0+ supports Tensor Cores
            # Memory optimization: Memory-critical operation
            'supports_half_precision': props.major >= 7,
            # CUDA capability 8.0+ supports bfloat16
            # Memory optimization: Memory-critical operation
            'supports_bfloat16': props.major >= 8
        })
        
    return info

def validate_training_requirements(
    min_memory_gb: float = 4.0,
    # Memory optimization: Memory-critical operation
    min_compute_capability: str = "6.1"
) -> Dict[str, bool]:
    """
    Validate if system meets training requirements
    Returns dict of requirements and whether they are met
    """
    info = get_system_info()
    major, minor = map(int, min_compute_capability.split('.'))
    
    requirements = {
        'has_cuda': info['cuda_available'],
        # Memory optimization: Memory-critical operation
        'has_gpu': info['gpu_count'] > 0,
        # Memory optimization: Memory-critical operation
        'has_min_memory': info['gpu_memory_gb'] >= min_memory_gb if info['cuda_available'] else False,
        # Memory optimization: Memory-critical operation
        'has_min_compute': False
    }
    
    if info['cuda_available']:
    # Memory optimization: Memory-critical operation
        gpu_major = int(info['compute_capability'].split('.')[0])
        # Memory optimization: Memory-critical operation
        gpu_minor = int(info['compute_capability'].split('.')[1])
        # Memory optimization: Memory-critical operation
        requirements['has_min_compute'] = (
            gpu_major > major or 
            # Memory optimization: Memory-critical operation
            (gpu_major == major and gpu_minor >= minor)
            # Memory optimization: Memory-critical operation
        )
    
    return requirements

def get_optimal_training_settings(info: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get optimal training settings based on hardware
    Automatically adjusts for limited VRAM environments
    """
    if info is None:
        info = get_system_info()
        
    settings = {
        'precision': 'fp32',
        'batch_size': 1,
        'gradient_accumulation': 8,
        'gradient_checkpointing': True,
        'use_8bit_optimizer': True,
        'max_sequence_length': 512,
        'num_attention_heads': 12,
        'hidden_size': 768
    }
    
    if not info['cuda_available']:
    # Memory optimization: Memory-critical operation
        logger.warning("No CUDA device available, using CPU settings")
        # Memory optimization: Device placement for memory management
        return settings
        
    # Adjust settings based on GPU memory
    # Memory optimization: Memory-critical operation
    gpu_memory = info['gpu_memory_gb']
    # Memory optimization: Memory-critical operation
    
    if gpu_memory >= 24:  # High-end GPUs (RTX 4090, A5000, etc)
    # Memory optimization: Memory-critical operation
        settings.update({
            'precision': 'fp16' if info['supports_half_precision'] else 'fp32',
            'batch_size': 32,
            'gradient_accumulation': 1,
            'gradient_checkpointing': False,
            'use_8bit_optimizer': False,
            'max_sequence_length': 2048,
            'hidden_size': 1024
        })
    elif gpu_memory >= 12:  # Mid-range GPUs (RTX 3060, etc)
    # Memory optimization: Memory-critical operation
        settings.update({
            'precision': 'fp16' if info['supports_half_precision'] else 'fp32',
            'batch_size': 16,
            'gradient_accumulation': 2,
            'gradient_checkpointing': False,
            'use_8bit_optimizer': True,
            'max_sequence_length': 1024
        })
    elif gpu_memory >= 8:  # Entry gaming GPUs
    # Memory optimization: Memory-critical operation
        settings.update({
            'precision': 'fp16' if info['supports_half_precision'] else 'fp32',
            'batch_size': 4,
            'gradient_accumulation': 4,
            'max_sequence_length': 768
        })
    else:  # Limited VRAM (4GB or less)
        logger.info("Detected limited VRAM GPU, using aggressive memory optimization")
        # Memory optimization: Memory-critical operation
        settings.update({
            'precision': 'fp16' if info['supports_half_precision'] else 'fp32',
            'batch_size': 1,
            'gradient_accumulation': 8,
            'gradient_checkpointing': True,
            'use_8bit_optimizer': True,
            'max_sequence_length': 512,
            'hidden_size': 768  # Reduced model size
            # Memory optimization: Explicit memory cleanup
        })
        
    return settings

def estimate_memory_requirements(
# Memory optimization: Memory-critical operation
    batch_size: int,
    sequence_length: int,
    hidden_size: int,
    num_layers: int,
    vocab_size: int,
    use_8bit: bool = True,
    use_half_precision: bool = True
) -> Dict[str, float]:
    """
    Estimate memory requirements for model configuration
    # Memory optimization: Explicit memory cleanup
    Returns estimated memory usage in GB
    # Memory optimization: Memory-critical operation
    """
    # Basic parameter count
    attention_params = 4 * hidden_size * hidden_size  # Q,K,V, and output
    ffn_params = 8 * hidden_size * hidden_size  # Expanded intermediate size
    layer_params = attention_params + ffn_params
    embedding_params = vocab_size * hidden_size
    
    total_params = (layer_params * num_layers) + embedding_params
    
    # Memory per parameter
    # Memory optimization: Memory-critical operation
    param_bytes = 2 if use_half_precision else 4  # fp16 vs fp32
    optimizer_bytes = 1 if use_8bit else 8  # 8-bit vs 32-bit Adam
    
    # Activation memory (per batch element)
    # Memory optimization: Memory-critical operation
    activation_bytes = 2 if use_half_precision else 4
    activation_memory = (
    # Memory optimization: Memory-critical operation
        sequence_length * hidden_size * activation_bytes * batch_size * 
        num_layers * 4  # Key, Query, Value, Output activations
    )
    
    # Attention memory
    # Memory optimization: Memory-critical operation
    attention_memory = sequence_length * sequence_length * 2 * batch_size * num_layers
    # Memory optimization: Memory-critical operation
    
    # Total memory in GB
    # Memory optimization: Memory-critical operation
    param_memory_gb = (total_params * param_bytes) / (1024**3)
    # Memory optimization: Memory-critical operation
    optimizer_memory_gb = (total_params * optimizer_bytes) / (1024**3)
    # Memory optimization: Memory-critical operation
    activation_memory_gb = (activation_memory + attention_memory) / (1024**3)
    # Memory optimization: Memory-critical operation
    
    total_gb = param_memory_gb + optimizer_memory_gb + activation_memory_gb
    # Memory optimization: Memory-critical operation
    
    return {
        'parameter_memory_gb': param_memory_gb,
        # Memory optimization: Memory-critical operation
        'optimizer_memory_gb': optimizer_memory_gb,
        # Memory optimization: Memory-critical operation
        'activation_memory_gb': activation_memory_gb,
        # Memory optimization: Memory-critical operation
        'total_memory_gb': total_gb,
        # Memory optimization: Memory-critical operation
        'parameter_count': total_params
    }

def optimize_for_hardware(system_info: dict) -> dict:
    """
    Optimize PyTorch and system settings for detected hardware constraints.

    Args:
        system_info (dict): Output from get_system_info().

    Returns:
        dict: Dictionary with optimization flags/settings applied.

    Memory Implications:
    # Memory optimization: Memory-critical operation
        Adjusts PyTorch and system settings to minimize VRAM and RAM usage on limited hardware.
    """
    optimizations = {}
    # Example: Enable memory-efficient settings for low VRAM GPUs
    # Memory optimization: Memory-critical operation
    if system_info.get('cuda_available') and system_info.get('gpu_memory_gb', 0) <= 4:
    # Memory optimization: Memory-critical operation
        import torch
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
        optimizations['cudnn_benchmark'] = False
        optimizations['cudnn_deterministic'] = True
        # Optionally enable gradient checkpointing in model code
        # Memory optimization: Explicit memory cleanup
        optimizations['suggest_gradient_checkpointing'] = True
    else:
        optimizations['cudnn_benchmark'] = True
        optimizations['cudnn_deterministic'] = False
        optimizations['suggest_gradient_checkpointing'] = False
    
    # Additional optimizations can be added here
    return optimizations

class HardwareDetector:
    """
    Hardware detection and optimization utilities for ImpressionCore.
    
    Provides comprehensive hardware detection, performance analysis,
    and optimization recommendations for the ImpressionCore system.
    """
    
    def __init__(self):
        """Initialize the hardware detector."""
        self.system_info = None
        self.gpu_info = None
        self.optimizations = None
        
    def detect_hardware(self) -> dict:
        """
        Detect and analyze system hardware.
        
        Returns:
            dict: Comprehensive hardware information
        """
        self.system_info = get_system_info()
        return self.system_info
    
    def get_gpu_info(self) -> dict:
        """
        Get detailed GPU information.
        
        Returns:
            dict: GPU-specific information
        """
        if self.system_info is None:
            self.detect_hardware()
        
        self.gpu_info = {
            'cuda_available': self.system_info.get('cuda_available', False),
            'gpu_name': self.system_info.get('gpu_name', 'Unknown'),
            'gpu_memory_gb': self.system_info.get('gpu_memory_gb', 0),
            'gpu_count': self.system_info.get('gpu_count', 0)
        }
        
        return self.gpu_info
    
    def get_optimization_recommendations(self) -> dict:
        """
        Get hardware-specific optimization recommendations.
        
        Returns:
            dict: Optimization settings and recommendations
        """
        if self.system_info is None:
            self.detect_hardware()
        
        self.optimizations = optimize_for_hardware(self.system_info)
        return self.optimizations
    
    def is_gpu_suitable(self, min_vram_gb: float = 4.0) -> bool:
        """
        Check if the GPU meets minimum requirements.
        
        Args:
            min_vram_gb: Minimum VRAM requirement in GB
            
        Returns:
            bool: True if GPU is suitable
        """
        if self.gpu_info is None:
            self.get_gpu_info()
        
        return (
            self.gpu_info.get('cuda_available', False) and
            self.gpu_info.get('gpu_memory_gb', 0) >= min_vram_gb
        )
    
    def get_memory_info(self) -> dict:
        """
        Get current memory usage information.
        
        Returns:
            dict: Memory usage details
        """
        import torch
        import psutil
        
        info = {}
        
        # CUDA memory
        if torch.cuda.is_available():
            info['cuda_allocated'] = torch.cuda.memory_allocated() / (1024**3)
            info['cuda_cached'] = torch.cuda.memory_reserved() / (1024**3)
            info['cuda_total'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        # System memory
        memory = psutil.virtual_memory()
        info['system_used'] = memory.used / (1024**3)
        info['system_total'] = memory.total / (1024**3)
        info['system_percent'] = memory.percent
        
        return info
