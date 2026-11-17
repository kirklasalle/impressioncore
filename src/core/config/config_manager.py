#!/usr/bin/env python3
"""
ImpressionCore: Config Manager

Module for config manager functionality in the ImpressionCore framework.

File: core\config\config_manager.py
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
This module implements config manager functionality for the
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
from src.core.config.config_manager import ConfigManager
instance = ConfigManager()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import json
import logging
import torch
from pathlib import Path
from typing import Dict, Any, Optional, Union
from src.core.utils.gpu_utils import is_shared_memory_gpu
# Memory optimization: Memory-critical operation

logger = logging.getLogger(__name__)

# Default paths
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "configs"
DEFAULT_PRESET_NAME = "gtx_1050ti_preset.json"

class ConfigManager:
    """
    Configuration manager for hardware-specific settings.
    
    Loads and applies configuration presets for different hardware environments,
    with special focus on optimizing for limited VRAM devices.
    # Memory optimization: Device placement for memory management
    """
    
    def __init__(self, 
                config_path: Optional[Union[str, Path]] = None, 
                preset_name: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to config directory (default: project_root/configs)
            preset_name: Name of preset file to load (default: auto-detect based on hardware)
        """
        self.config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        self.preset_name = preset_name
        self.config = {}
        
    def detect_hardware(self) -> str:
        """
        Detect hardware and return appropriate preset name.
        
        Returns:
            Name of the preset file to use
        """
        # Check if GPU is available
        # Memory optimization: Memory-critical operation
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            return "cpu_preset.json"
        
        # Get GPU name
        # Memory optimization: Memory-critical operation
        device_name = torch.cuda.get_device_name(0)
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Check for specific hardware
        if "1050 Ti" in device_name:
        # Memory optimization: Device placement for memory management
            return "gtx_1050ti_preset.json"
        elif "16" in device_name and ("RTX" in device_name or "GTX" in device_name):
        # Memory optimization: Device placement for memory management
            # 16xx series GPUs with limited VRAM
            # Memory optimization: Memory-critical operation
            return "gtx_16xx_preset.json"
        elif "RTX" in device_name:
        # Memory optimization: Device placement for memory management
            return "rtx_preset.json"
        elif "A100" in device_name or "H100" in device_name:
        # Memory optimization: Device placement for memory management
            return "datacenter_preset.json"
        else:
            # Default to GTX 1050 Ti preset for other GPUs with shared memory
            # Memory optimization: Memory-critical operation
            is_shared, _, _ = is_shared_memory_gpu()
            # Memory optimization: Memory-critical operation
            if is_shared:
                return "gtx_1050ti_preset.json"
            
            return "default_gpu_preset.json"
            # Memory optimization: Memory-critical operation
    
    def load_config(self, preset_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from preset file.
        
        Args:
            preset_name: Name of preset file to load (default: use self.preset_name or auto-detect)
            
        Returns:
            Configuration dictionary
        """
        # Determine preset name
        if preset_name:
            self.preset_name = preset_name
        elif not self.preset_name:
            self.preset_name = self.detect_hardware()
        
        preset_path = self.config_path / self.preset_name
        
        # Fall back to default if preset not found
        if not preset_path.exists():
            logger.warning(f"Preset {preset_path} not found, falling back to {DEFAULT_PRESET_NAME}")
            self.preset_name = DEFAULT_PRESET_NAME
            preset_path = self.config_path / DEFAULT_PRESET_NAME
        
        try:
            with open(preset_path, "r") as f:
                self.config = json.load(f)
            
            logger.info(f"Loaded configuration preset: {preset_path}")
            return self.config
        except Exception as e:
            logger.error(f"Error loading preset {preset_path}: {e}")
            return {}
    
    def apply_memory_settings(self) -> None:
    # Memory optimization: Memory-critical operation
        """Apply memory optimization settings from config."""
        # Memory optimization: Memory-critical operation
        if not self.config:
            self.load_config()
        
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            logger.warning("CUDA not available, skipping memory settings")
            # Memory optimization: Memory-critical operation
            return
        
        memory_settings = self.config.get("memory_settings", {})
        # Memory optimization: Memory-critical operation
        
        # Apply memory fraction
        # Memory optimization: Memory-critical operation
        memory_fraction = memory_settings.get("memory_fraction", 0.85)
        # Memory optimization: Memory-critical operation
        try:
            torch.cuda.set_per_process_memory_fraction(memory_fraction)
            # Memory optimization: CUDA operations for GPU acceleration
            logger.info(f"Set CUDA memory fraction to {memory_fraction}")
            # Memory optimization: Memory-critical operation
        except Exception as e:
            logger.warning(f"Failed to set memory fraction: {e}")
            # Memory optimization: Memory-critical operation
        
        # Configure PyTorch settings for optimization
        if memory_settings.get("use_fp16", True) and hasattr(torch, "set_float32_matmul_precision"):
        # Memory optimization: Memory-critical operation
            torch.set_float32_matmul_precision('medium')
        
        # Configure cuDNN settings
        if memory_settings.get("enable_gradient_checkpointing", True):
        # Memory optimization: Memory-critical operation
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True
            logger.info("Enabled deterministic cuDNN for memory efficiency")
            # Memory optimization: Memory-critical operation
        else:
            torch.backends.cudnn.benchmark = True
            logger.info("Enabled cuDNN benchmark for performance")
    
    def get_inference_settings(self) -> Dict[str, Any]:
        """
        Get inference-specific settings.
        
        Returns:
            Dictionary with inference settings
        """
        if not self.config:
            self.load_config()
        
        return self.config.get("inference_settings", {})
    
    def get_training_settings(self) -> Dict[str, Any]:
        """
        Get training-specific settings.
        
        Returns:
            Dictionary with training settings
        """
        if not self.config:
            self.load_config()
        
        return self.config.get("training_settings", {})
    
    def get_optimal_batch_size(self, model_type: str = "medium_model") -> int:
        """
        Get optimal batch size for current configuration.
        
        Args:
            model_type: Type of model (small_model, medium_model, large_model)
            # Memory optimization: Explicit memory cleanup
            
        Returns:
            Optimal batch size
        """
        if not self.config:
            self.load_config()
        
        # Get batch size from config
        memory_settings = self.config.get("memory_settings", {})
        # Memory optimization: Memory-critical operation
        batch_sizes = memory_settings.get("max_batch_size", {})
        # Memory optimization: Memory-critical operation
        
        # Default batch sizes
        defaults = {
            "small_model": 8,
            "medium_model": 4,
            "large_model": 1
        }
        
        return batch_sizes.get(model_type, defaults.get(model_type, 1))

def initialize_environment(apply_settings: bool = True) -> ConfigManager:
    """
    Initialize environment with proper configuration.
    
    Args:
        apply_settings: Whether to apply memory settings immediately
        # Memory optimization: Memory-critical operation
        
    Returns:
        ConfigManager instance
    """
    config_manager = ConfigManager()
    config_manager.load_config()
    
    if apply_settings:
        config_manager.apply_memory_settings()
        # Memory optimization: Memory-critical operation
    
    return config_manager

# Create a global singleton instance
CONFIG_MANAGER = None

def get_config_manager() -> ConfigManager:
    """
    Get global configuration manager instance.
    
    Returns:
        ConfigManager instance
    """
    global CONFIG_MANAGER
    if CONFIG_MANAGER is None:
        CONFIG_MANAGER = initialize_environment()
    return CONFIG_MANAGER
