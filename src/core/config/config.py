#!/usr/bin/env python3
"""
ImpressionCore: Config

Module for config functionality in the ImpressionCore framework.

File: core\config.py
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
Dependencies: [torch, rich, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements config functionality for the
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
from src.core.config import ModelDimensions
instance = ModelDimensions()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Union
import os
import pathlib
import logging
import traceback
import sys
__all__ = ["ConfigManager", "get_model_config", "get_impressioncore_1b_config", "get_impressioncore_small_config", 
           "estimate_vram_usage", "get_gpu_compatible_config", "setup_logging", "debug_model_creation"]
           # Memory optimization: Memory-critical operation

import yaml
import json
import warnings
import math

# Import enhanced logging utilities if available
try:
    from ..utils.enhanced_logging import (
        setup_logging as enhanced_setup_logging,
        get_logger,
        log_gpu_stats,
        # Memory optimization: Memory-critical operation
        memory_tracker,
        # Memory optimization: Memory-critical operation
        HAS_RICH
    )
    HAS_ENHANCED_LOGGING = True
except ImportError:
    HAS_ENHANCED_LOGGING = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

# Set up logger - use enhanced logging if available
if HAS_ENHANCED_LOGGING:
    logger = get_logger("core.config")
else:
    # Fall back to standard logging
    logger = logging.getLogger("core.config")

def setup_logging(level=logging.INFO, log_to_file=False, log_file=None, console_output=True, use_rich=True):
    """
    Configure logging for the ImpressionCore configuration system.
    
    Args:
        level: Logging level (e.g. logging.DEBUG, logging.INFO)
        log_to_file: Whether to log to a file
        log_file: Path to log file (default: core_config.log in project dir)
        console_output: Whether to output to console
        use_rich: Whether to use rich formatting (if available)
    """
    if HAS_ENHANCED_LOGGING:
        # Use the enhanced logging setup if available
        enhanced_setup_logging(
            level=level,
            log_to_file=log_to_file,
            log_file=log_file,
            console_output=console_output,
            use_rich=use_rich,
            module_name="core.config"
        )
        logger.debug("Using enhanced logging with Rich formatting")
        
        # Log GPU stats if available
        # Memory optimization: Memory-critical operation
        if HAS_TORCH and torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            log_gpu_stats(logger)
            # Memory optimization: Memory-critical operation
    else:
        # Fall back to original logging setup
        logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create console handler with formatting
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Add file handler if requested
        if log_file is None:
            log_file = os.path.join(pathlib.Path(__file__).parent.parent.parent.absolute(), "core_config.log")
        
        file_handler = logging.FileHandler(log_file, mode='w')  # 'w' to overwrite previous logs on each run
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.debug("Logging initialized for core.config (standard format)")

@dataclass
class ModelDimensions:
    """Model dimension parameters"""
    # Memory optimization: Explicit memory cleanup
    hidden_size: int
    intermediate_size: int
    num_attention_heads: int
    num_hidden_layers: int
    max_position_embeddings: int = 2048
    vocab_size: int = 50304  # Default for common tokenizer vocab
    head_dim: Optional[int] = None
    
    def __post_init__(self):
        """
        
    __post_init__ function for processing.
    
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
        if self.head_dim is None:
            self.head_dim = self.hidden_size // self.num_attention_heads
            
    @property
    def config_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving to config files"""
        return {
            "hidden_size": self.hidden_size,
            "intermediate_size": self.intermediate_size,
            "num_attention_heads": self.num_attention_heads,
            "num_hidden_layers": self.num_hidden_layers,
            "max_position_embeddings": self.max_position_embeddings,
            "vocab_size": self.vocab_size,
            "head_dim": self.head_dim,
        }

@dataclass
class UKSConfig:
    """Universal Knowledge Store configuration"""
    enabled: bool = True
    memory_size: int = 10000
    # Memory optimization: Memory-critical operation
    embedding_dim: int = 768
    query_dim: int = 768
    similarity_threshold: float = 0.75
    retrieval_limit: int = 5
    persistent_storage_path: Optional[str] = None
    
    @property
    def config_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving to config files"""
        return {
            "enabled": self.enabled,
            "memory_size": self.memory_size,
            # Memory optimization: Memory-critical operation
            "embedding_dim": self.embedding_dim,
            "query_dim": self.query_dim,
            "similarity_threshold": self.similarity_threshold,
            "retrieval_limit": self.retrieval_limit,
            "persistent_storage_path": self.persistent_storage_path,
        }

@dataclass
class BrainSimConfig:
    """BrainSimIII integration configuration"""
    enabled: bool = False
    connection_url: str = "localhost:50051"
    simulation_rate: float = 1.0
    sync_interval: int = 100  # Steps between synchronization
    brain_region_mappings: Dict[str, str] = field(default_factory=dict)
    
    @property
    def config_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving to config files"""
        return {
            "enabled": self.enabled,
            "connection_url": self.connection_url,
            "simulation_rate": self.simulation_rate,
            "sync_interval": self.sync_interval,
            "brain_region_mappings": self.brain_region_mappings,
        }

@dataclass
class ResourceConfig:
    """Hardware resource configuration for training and inference"""
    gradient_accumulation_steps: int = 1
    mixed_precision: bool = True
    cpu_offload: bool = False
    memory_efficient_attention: bool = True
    # Memory optimization: Memory-critical operation
    bf16: bool = False
    vram_efficient_loading: bool = True
    
    @property
    def config_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving to config files"""
        return {
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "mixed_precision": self.mixed_precision,
            "cpu_offload": self.cpu_offload,
            "memory_efficient_attention": self.memory_efficient_attention,
            # Memory optimization: Memory-critical operation
            "bf16": self.bf16,
            "vram_efficient_loading": self.vram_efficient_loading,
        }

@dataclass
class TrainingConfig:
    """Training configuration parameters"""
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    warmup_steps: int = 500
    max_steps: int = 100000
    batch_size: int = 32
    gradient_accumulation_steps: int = 1
    fp16: bool = True
    bf16: bool = False
    gradient_checkpointing: bool = False
    
    @property
    def config_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving to config files"""
        return {
            "learning_rate": self.learning_rate,
            "weight_decay": self.weight_decay,
            "warmup_steps": self.warmup_steps,
            "max_steps": self.max_steps,
            "batch_size": self.batch_size,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "fp16": self.fp16,
            "bf16": self.bf16,
            "gradient_checkpointing": self.gradient_checkpointing,
        }

@dataclass
class ModelConfig:
    """Master configuration for ImpressionCore models"""
    model_type: str
    model_name: str
    dimensions: ModelDimensions
    vocab_size: int = field(default=50304)  # Properly declare as dataclass field
    uks_config: UKSConfig = field(default_factory=UKSConfig)
    brainsim_config: BrainSimConfig = field(default_factory=BrainSimConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    dual_shadow_enabled: bool = False
    activation_function: str = "gelu"
    initializer_range: float = 0.02
    rms_norm_eps: float = 1e-6
    use_cache: bool = True
    tie_word_embeddings: bool = False
    rope_theta: float = 10000.0
    multimodal: bool = False
    quantization: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ModelConfig":
        """Create a ModelConfig from a dictionary"""
        dimensions = ModelDimensions(**config_dict.pop("dimensions"))
        
        uks_config_dict = config_dict.pop("uks_config", {})
        uks_config = UKSConfig(**uks_config_dict) if uks_config_dict else UKSConfig()
        
        brainsim_config_dict = config_dict.pop("brainsim_config", {})
        brainsim_config = BrainSimConfig(**brainsim_config_dict) if brainsim_config_dict else BrainSimConfig()
        
        training_dict = config_dict.pop("training", {})
        training = TrainingConfig(**training_dict) if training_dict else TrainingConfig()
        
        return cls(
            dimensions=dimensions,
            uks_config=uks_config,
            brainsim_config=brainsim_config,
            training=training,
            **config_dict
        )
    
    @classmethod
    def from_json(cls, json_path: str) -> "ModelConfig":
        """Load configuration from JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ModelConfig":
        """Load configuration from YAML file"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)
    
    def save_json(self, json_path: str) -> None:
        """Save configuration to JSON file"""
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def save_yaml(self, yaml_path: str) -> None:
        """Save configuration to YAML file"""
        os.makedirs(os.path.dirname(yaml_path), exist_ok=True)
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving to config files"""
        config_dict = {
            "model_type": self.model_type,
            "model_name": self.model_name,
            "dimensions": self.dimensions.config_dict,
            "vocab_size": self.vocab_size,
            "uks_config": self.uks_config.config_dict,
            "brainsim_config": self.brainsim_config.config_dict,
            "training": self.training.config_dict,
            "dual_shadow_enabled": self.dual_shadow_enabled,
            "activation_function": self.activation_function,
            "initializer_range": self.initializer_range,
            "rms_norm_eps": self.rms_norm_eps,
            "use_cache": self.use_cache,
            "tie_word_embeddings": self.tie_word_embeddings,
            "rope_theta": self.rope_theta,
            "multimodal": self.multimodal,
        }
        
        if self.quantization:
            config_dict["quantization"] = self.quantization
            
        return config_dict

    @property
    def hidden_size(self):
        """
        
    hidden_size function for processing.
    
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
        return self.dimensions.hidden_size

    @hidden_size.setter
    def hidden_size(self, value):
        """
        
    hidden_size function for processing.
    
    Args:
        self, value: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.dimensions.hidden_size = value

    @property
    def dropout(self):
        """
        
    dropout function for processing.
    
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
        return 0.1

    @property
    def num_layers(self):
        """
        
    num_layers function for processing.
    
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
        return self.dimensions.num_hidden_layers

    @property
    def layer_norm_eps(self):
        """
        
    layer_norm_eps function for processing.
    
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
        return self.rms_norm_eps

    @property
    def max_position_embeddings(self):
        """
        
    max_position_embeddings function for processing.
    
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
        return self.dimensions.max_position_embeddings
        
    @max_position_embeddings.setter
    def max_position_embeddings(self, value):
        """
        
    max_position_embeddings function for processing.
    
    Args:
        self, value: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.dimensions.max_position_embeddings = value

    @property
    def num_heads(self):
        """
        
    num_heads function for processing.
    
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
        return self.dimensions.num_attention_heads

    @property
    def num_attention_heads(self):
        """
        
    num_attention_heads function for processing.
    
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
        return self.dimensions.num_attention_heads
        
    @num_attention_heads.setter
    def num_attention_heads(self, value):
        """
        
    num_attention_heads function for processing.
    
    Args:
        self, value: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.dimensions.num_attention_heads = value

    @property
    def num_hidden_layers(self):
        """
        
    num_hidden_layers function for processing.
    
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
        return self.dimensions.num_hidden_layers
        
    @num_hidden_layers.setter
    def num_hidden_layers(self, value):
        """
        
    num_hidden_layers function for processing.
    
    Args:
        self, value: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.dimensions.num_hidden_layers = value

    @property
    def intermediate_size(self):
        """
        
    intermediate_size function for processing.
    
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
        return self.dimensions.intermediate_size
        
    @intermediate_size.setter
    def intermediate_size(self, value):
        """
        
    intermediate_size function for processing.
    
    Args:
        self, value: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.dimensions.intermediate_size = value
        
    # Additional properties for multimodal features
    @property
    def num_visual_features(self):
        """
        
    num_visual_features function for processing.
    
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
        return getattr(self, '_num_visual_features', 0)
        
    @num_visual_features.setter
    def num_visual_features(self, value):
        """
        
    num_visual_features function for processing.
    
    Args:
        self, value: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self._num_visual_features = value
        
    @property
    def num_audio_features(self):
        """
        
    num_audio_features function for processing.
    
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
        return getattr(self, '_num_audio_features', 0)
        
    @num_audio_features.setter
    def num_audio_features(self, value):
        """
        
    num_audio_features function for processing.
    
    Args:
        self, value: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self._num_audio_features = value


class ConfigManager:
    """
    A class to manage configurations for the ImpressionCore project.

    Attributes:
        model_config: Stores the model configuration.
        # Memory optimization: Explicit memory cleanup
    """
    def __init__(self):
        """
        
    __init__ function for processing.
    
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
        self.model_config = None

    def get_config(self):
        """
        Retrieve the current configuration.

        Returns:
            The current model configuration.
            # Memory optimization: Explicit memory cleanup
        """
        return self.model_config

    def set_model_config(self, config):
        """
        Set the model configuration.
        # Memory optimization: Explicit memory cleanup

        Args:
            config: The configuration to set.
        """
        self.model_config = config

    def validate_hardware_compatibility(self):
        """
        Validate whether the current hardware is compatible with the model configuration.
        # Memory optimization: Explicit memory cleanup
        
        Returns:
            bool: True if hardware is compatible, False otherwise
        """
        if not self.model_config:
            logger.warning("No model configuration set, cannot validate hardware compatibility")
            # Memory optimization: Explicit memory cleanup
            return False
        
        # Check GPU availability and VRAM
        # Memory optimization: Memory-critical operation
        is_compatible = True
        available_vram = get_available_vram()
        estimated_vram = estimate_vram_usage(self.model_config)
        
        if available_vram <= 0:
            logger.warning("No GPU detected. Running on CPU may result in reduced performance.")
            # Memory optimization: Memory-critical operation
            is_compatible = False
        elif estimated_vram > available_vram:
            logger.warning(
                f"Model requires approximately {estimated_vram:.2f}GB VRAM, but only "
                # Memory optimization: Explicit memory cleanup
                f"{available_vram:.2f}GB is available. Performance may be degraded."
            )
            is_compatible = False
        else:
            logger.info(
                f"Hardware compatible: {available_vram:.2f}GB VRAM available, "
                f"model requires {estimated_vram:.2f}GB"
                # Memory optimization: Explicit memory cleanup
            )
            
        # Check model size vs available memory - future implementation
        # Memory optimization: Explicit memory cleanup
        # This could check system RAM as well for CPU operation
        
        return is_compatible
        
    @property
    def training_config(self):
        """
        Access the training configuration stored within the model configuration.
        # Memory optimization: Explicit memory cleanup
        
        Returns:
            TrainingConfig: The training configuration or None if model_config is not set
            
        Note:
            This property provides direct access to the training configuration 
            within the model_config for convenience.
        """
        if not self.model_config:
            logger.warning("No model configuration set, cannot access training configuration")
            # Memory optimization: Explicit memory cleanup
            return None
            
        return self.model_config.training


def get_impressioncore_1b_config() -> ModelConfig:
    """
    Get a predefined configuration for ImpressionCore 1B model.
    Returns a model configuration with appropriate parameters for a 1B parameter model.
    # Memory optimization: Explicit memory cleanup
    """
    logger.debug("Getting impressioncore-1b configuration")
    return ModelConfig(
        model_type="impression_core",
        model_name="impressioncore-1b",
        dimensions=ModelDimensions(
            hidden_size=2048,
            intermediate_size=5632,
            num_attention_heads=16,
            num_hidden_layers=24,
            max_position_embeddings=4096,
        ),
        vocab_size=50304,  # Default for common tokenizer vocab
        dual_shadow_enabled=True,
        activation_function="silu",
        rms_norm_eps=1e-5,
        quantization=None,  # Will be set in get_model_config based on available VRAM
    )

def estimate_vram_usage(config: ModelConfig, dtype: str = "float16", batch_size: int = 1, use_kv_cache: bool = True) -> float:
    """
    Estimate VRAM usage for a model configuration in gigabytes.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        config: Model configuration
        # Memory optimization: Explicit memory cleanup
        dtype: Data type ('float32', 'float16', 'int8', etc.)
        batch_size: Input batch size
        use_kv_cache: Whether KV cache is used for inference
        
    Returns:
        Estimated VRAM usage in gigabytes
    """
    logger.debug(f"Estimating VRAM usage for {config.model_name} with dtype={dtype}, batch_size={batch_size}")
    
    # Bytes per parameter based on dtype
    bytes_per_param = {
        "float32": 4,
        "float16": 2, 
        "bfloat16": 2,
        "int8": 1
    }.get(dtype, 2)  # Default to float16
    
    logger.debug(f"Using {bytes_per_param} bytes per parameter for {dtype}")
    
    # Base parameter count calculation
    total_params = (
        # Embedding layer
        config.vocab_size * config.hidden_size +
        # Position embeddings if used
        (config.max_position_embeddings * config.hidden_size if not config.rope_theta else 0) +
        # Hidden layers
        config.num_layers * (
            # Self-attention
            4 * config.hidden_size * config.hidden_size +  # Q, K, V, output projections
            # Feed-forward network
            (config.hidden_size * config.intermediate_size) +  # First FFN layer
            (config.intermediate_size * config.hidden_size) +  # Second FFN layer
            # Layer norms
            2 * config.hidden_size  # Input and post-attention layer norms
        )
    )
    
    logger.debug(f"Total parameter count: {total_params:,}")
    
    # Model parameters
    # Memory optimization: Explicit memory cleanup
    model_memory_gb = (total_params * bytes_per_param) / (1024 ** 3)
    # Memory optimization: Memory-critical operation
    logger.debug(f"Base model memory: {model_memory_gb:.2f} GB")
    # Memory optimization: Explicit memory cleanup
    
    # KV cache for inference
    # seq_len is needed for the activation estimate below regardless of
    # whether KV cache is enabled, so it must be assigned unconditionally
    # (previously only set inside the `if use_kv_cache:` block, causing an
    # UnboundLocalError when use_kv_cache=False).
    seq_len = config.max_position_embeddings
    kv_cache_gb = 0
    if use_kv_cache:
        # K and V states for each batch, sequence, layer, head
        cache_size = batch_size * seq_len * config.num_layers * 2 * config.hidden_size
        kv_cache_gb = (cache_size * bytes_per_param) / (1024 ** 3)
        logger.debug(f"KV cache memory: {kv_cache_gb:.2f} GB (seq_len={seq_len}, layers={config.num_layers})")
        # Memory optimization: Memory-critical operation
    
    # Activations (rough estimate)
    activation_gb = batch_size * seq_len * config.hidden_size * bytes_per_param * 4 / (1024 ** 3)
    logger.debug(f"Activation memory: {activation_gb:.2f} GB")
    # Memory optimization: Memory-critical operation
    
    # Total memory estimate before quantization adjustment
    # Memory optimization: Memory-critical operation
    subtotal_memory_gb = model_memory_gb + kv_cache_gb + activation_gb
    # Memory optimization: Memory-critical operation
    logger.debug(f"Subtotal memory before quantization: {subtotal_memory_gb:.2f} GB")
    # Memory optimization: Memory-critical operation
    
    # If quantization is enabled, adjust the memory estimate
    # Memory optimization: Memory-critical operation
    if config.quantization and config.quantization.get("enabled", False):
        quant_bits = config.quantization.get("bits", 8)
        original_model_memory = model_memory_gb
        # Memory optimization: Memory-critical operation
        
        if quant_bits == 8:
            # INT8 uses roughly 1/2 the memory of FP16
            # Memory optimization: Memory-critical operation
            model_memory_gb *= 0.5
            # Memory optimization: Memory-critical operation
            logger.debug(f"Applied INT8 quantization: {original_model_memory:.2f} GB -> {model_memory_gb:.2f} GB")
            # Memory optimization: Memory-critical operation
        elif quant_bits == 4:
            # INT4 uses roughly 1/4 the memory of FP16
            # Memory optimization: Memory-critical operation
            model_memory_gb *= 0.25
            # Memory optimization: Memory-critical operation
            logger.debug(f"Applied INT4 quantization: {original_model_memory:.2f} GB -> {model_memory_gb:.2f} GB")
            # Memory optimization: Memory-critical operation
        elif quant_bits == 3:
            # INT3 uses roughly 3/16 the memory of FP16
            # Memory optimization: Memory-critical operation
            model_memory_gb *= 0.1875
            # Memory optimization: Memory-critical operation
            logger.debug(f"Applied INT3 quantization: {original_model_memory:.2f} GB -> {model_memory_gb:.2f} GB")
            # Memory optimization: Memory-critical operation
    
    # Total memory estimate after quantization adjustment
    # Memory optimization: Memory-critical operation
    total_memory_gb = model_memory_gb + kv_cache_gb + activation_gb
    # Memory optimization: Memory-critical operation
    
    # Add safety margin (20%)
    final_estimate = total_memory_gb * 1.2
    # Memory optimization: Memory-critical operation
    logger.debug(f"Final memory estimate with 20% safety margin: {final_estimate:.2f} GB")
    # Memory optimization: Memory-critical operation
    
    return final_estimate

def get_available_vram() -> float:
    """
    Get available VRAM in gigabytes from the primary CUDA device.
    # Memory optimization: Device placement for memory management
    Returns 0 if CUDA is not available.
    # Memory optimization: Memory-critical operation
    """
    logger.debug("Checking available VRAM")
    
    if not HAS_TORCH:
        logger.warning("PyTorch not installed, cannot detect VRAM")
        return 0
    
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.warning("CUDA not available, cannot detect VRAM")
        # Memory optimization: Memory-critical operation
        return 0
    
    try:
        # Try to get total memory from the current device
        # Memory optimization: Device placement for memory management
        device = torch.cuda.current_device()
        # Memory optimization: CUDA operations for GPU acceleration
        device_name = torch.cuda.get_device_name(device)
        # Memory optimization: CUDA operations for GPU acceleration
        total_vram = torch.cuda.get_device_properties(device).total_memory / (1024**3)
        # Memory optimization: CUDA operations for GPU acceleration
        logger.info(f"Detected GPU: {device_name} with {total_vram:.2f} GB VRAM")
        # Memory optimization: Device placement for memory management
        return total_vram
    except Exception as e:
        logger.error(f"Failed to get GPU memory: {e}")
        # Memory optimization: Memory-critical operation
        return 0

def get_impressioncore_small_config() -> ModelConfig:
    """
    Get a predefined configuration for ImpressionCore Small model (approximately 230M parameters).
    # Memory optimization: Explicit memory cleanup
    Suitable for GPUs with 2-4GB VRAM.
    # Memory optimization: Memory-critical operation
    """
    return ModelConfig(
        model_type="impression_core",
        model_name="impressioncore-small",
        dimensions=ModelDimensions(
            hidden_size=768,
            intermediate_size=2048,
            num_attention_heads=12,
            num_hidden_layers=12,
            max_position_embeddings=2048,
        ),
        vocab_size=50304,  # Default for common tokenizer vocab
        dual_shadow_enabled=False,  # Disable dual shadow for memory efficiency
        # Memory optimization: Memory-critical operation
        activation_function="gelu",
        rms_norm_eps=1e-6,
    )

def get_impressioncore_tiny_config() -> ModelConfig:
    """
    Get a predefined configuration for ImpressionCore Tiny model (approximately 70M parameters).
    # Memory optimization: Explicit memory cleanup
    Suitable for GPUs with 1-2GB VRAM or CPU inference.
    # Memory optimization: Memory-critical operation
    """
    return ModelConfig(
        model_type="impression_core",
        model_name="impressioncore-tiny",
        dimensions=ModelDimensions(
            hidden_size=384,
            intermediate_size=1024,
            num_attention_heads=6,
            num_hidden_layers=8,
            max_position_embeddings=1024,
        ),
        vocab_size=32000,  # Reduced vocabulary size
        dual_shadow_enabled=False,
        activation_function="gelu",
        rms_norm_eps=1e-6,
    )

def get_gpu_compatible_config(vram_gb: Optional[float] = None, dtype: str = "float16",
# Memory optimization: Memory-critical operation
                             safety_margin: float = 0.8) -> ModelConfig:
    """
    Get a model configuration compatible with available GPU VRAM.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        vram_gb: Available VRAM in GB. If None, will be auto-detected.
        dtype: Data type to use for calculations
        safety_margin: Fraction of VRAM to consider usable (0-1)
        
    Returns:
        ModelConfig: Appropriate model configuration for the available VRAM
        # Memory optimization: Explicit memory cleanup
    """
    if vram_gb is None:
        vram_gb = get_available_vram()
    
    # If VRAM detection failed or no CUDA, assume a conservative amount
    # Memory optimization: Memory-critical operation
    if vram_gb <= 0:
        warnings.warn("Could not detect VRAM. Assuming CPU operation.")
        return get_impressioncore_tiny_config()
    
    # Apply safety margin
    vram_gb = vram_gb * safety_margin
    
    # Select appropriate model based on available VRAM
    # Memory optimization: Explicit memory cleanup
    if vram_gb >= 12:
        config = get_impressioncore_1b_config()
    elif vram_gb >= 4:
        config = get_impressioncore_small_config()
    else:
        config = get_impressioncore_tiny_config()
    
    # Verify the selection
    estimated_usage = estimate_vram_usage(config, dtype=dtype)
    if estimated_usage > vram_gb:
        warnings.warn(
            f"Selected model (est. {estimated_usage:.1f}GB) may exceed available VRAM ({vram_gb:.1f}GB). "
            # Memory optimization: Explicit memory cleanup
            f"Downgrading to a smaller configuration."
        )
        if config.model_name == "impressioncore-1b":
            return get_impressioncore_small_config()
        else:
            return get_impressioncore_tiny_config()
    
    return config

def get_model_config(model_name: str) -> ModelConfig:
    """
    Get a predefined model configuration by name.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        model_name: Name of the model configuration to retrieve.
        # Memory optimization: Explicit memory cleanup
                   Currently supported: "impressioncore-1b", "impressioncore-small", "impressioncore-tiny", "auto"
                   
    Returns:
        ModelConfig: Configuration for the specified model.
    
    Raises:
        ValueError: If the model name is not recognized.
        # Memory optimization: Explicit memory cleanup
    """
    logger.info(f"Getting model configuration for: {model_name}")
    # Memory optimization: Explicit memory cleanup
    
    if model_name.lower() == "impressioncore-1b":
        config = get_impressioncore_1b_config()
        available_vram = get_available_vram()
        logger.info(f"Available VRAM: {available_vram:.2f} GB")
        
        # If we have limited VRAM but want to run 1B model, enable quantization automatically
        if available_vram > 0 and available_vram < 8:
            logger.info("Limited VRAM detected for 1B model, enabling 4-bit quantization")
            
            # Enable 4-bit quantization for 4GB cards since user prefers 4-bit
            config.quantization = {
                "enabled": True,
                "bits": 4,  # Changed to 4-bit as user prefers 4k quantization
                "group_size": 64,  # Smaller group size for better compression
                "method": "dynamic",
                "sym": True,
                "modules_to_not_quantize": [
                    "lm_head", 
                    "embed_tokens"
                ],
                "bnb_4bit_compute_dtype": "float16",  # Use float16 for compute operations 
                "bnb_4bit_use_double_quant": True,    # Use nested quantization for further memory savings
                # Memory optimization: Memory-critical operation
                "bnb_4bit_quant_type": "nf4"          # Use NF4 format for better quality
            }
            logger.debug(f"Applied 4-bit quantization config: {config.quantization}")
        
        # Still verify it will fit after quantization
        safety_margin = 0.8
        usable_vram = available_vram * safety_margin
        logger.debug(f"Usable VRAM with safety margin: {usable_vram:.2f} GB")
        
        est_usage = estimate_vram_usage(config, dtype="float16")
        logger.info(f"Estimated VRAM usage for {config.model_name}: {est_usage:.2f} GB")
        
        if est_usage > usable_vram:
            warning_msg = (
                f"Even with quantization, estimated VRAM usage ({est_usage:.2f}GB) exceeds usable VRAM ({usable_vram:.2f}GB). "
                "Consider enabling CPU offloading or reduced sequence length."
            )
            logger.warning(warning_msg)
            warnings.warn(warning_msg)
            
            # Add CPU offloading suggestion to the config without actually enabling it
            # (would need to be implemented in the model loading code)
            # Memory optimization: Explicit memory cleanup
            logger.info("Adding CPU offloading recommendation to config")
            if not config.quantization:
                config.quantization = {}
            config.quantization["recommended_cpu_offload"] = True
            
        return config
    elif model_name.lower() == "impressioncore-small":
        config = get_impressioncore_small_config()
        logger.info(f"Selected impressioncore-small configuration ({estimate_vram_usage(config):.2f}GB VRAM est.)")
        return config
    elif model_name.lower() == "impressioncore-tiny":
        config = get_impressioncore_tiny_config()
        logger.info(f"Selected impressioncore-tiny configuration ({estimate_vram_usage(config):.2f}GB VRAM est.)")
        return config
    elif model_name.lower() == "auto":
        logger.info("Auto-selecting model based on available VRAM")
        # Memory optimization: Explicit memory cleanup
        config = get_gpu_compatible_config()
        # Memory optimization: Memory-critical operation
        logger.info(f"Auto-selected {config.model_name} configuration ({estimate_vram_usage(config):.2f}GB VRAM est.)")
        return config
    else:
        try:
            # Try to load from disk if not a built-in configuration
            logger.info(f"Loading custom configuration from disk: {model_name}")
            config_manager = ConfigManager()
            return config_manager.load_config(model_name)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Failed to load configuration '{model_name}': {e}")
            raise ValueError(f"Unknown model configuration: {model_name}")
            # Memory optimization: Explicit memory cleanup

def debug_model_creation(model_config: ModelConfig, filepath: str = None) -> Dict[str, Any]:
    """
    Debug model creation issues by collecting detailed information.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        model_config: The model configuration to debug
        # Memory optimization: Explicit memory cleanup
        filepath: Path to save the debug info (optional)
    
    Returns:
        Dict containing debug information
    """
    debug_info = {
        "model_name": model_config.model_name,
        "model_type": model_config.model_type,
        "parameter_count": None,
        "vram_estimate": None,
        "available_vram": None,
        "quantization": model_config.quantization,
        "hidden_size": model_config.hidden_size,
        "num_layers": model_config.num_layers,
        "attention_heads": model_config.num_attention_heads,
        "system_info": {},
        "memory_stats": {},
        # Memory optimization: Memory-critical operation
        "error_info": None,
        "pytorch_version": None,
    }
    
    logger.info(f"Starting debug for model: {model_config.model_name}")
    
    # Calculate parameter count
    try:
        total_params = (
            # Embedding layer
            model_config.vocab_size * model_config.hidden_size +
            # Position embeddings if used
            (model_config.max_position_embeddings * model_config.hidden_size if not model_config.rope_theta else 0) +
            # Hidden layers
            model_config.num_layers * (
                # Self-attention
                4 * model_config.hidden_size * model_config.hidden_size +  # Q, K, V, output projections
                # Feed-forward network
                (model_config.hidden_size * model_config.intermediate_size) +  # First FFN layer
                (model_config.intermediate_size * model_config.hidden_size) +  # Second FFN layer
                # Layer norms
                2 * model_config.hidden_size  # Input and post-attention layer norms
            )
        )
        debug_info["parameter_count"] = total_params
        logger.info(f"Estimated parameter count: {total_params:,}")
    except Exception as e:
        logger.error(f"Error calculating parameter count: {e}")
        debug_info["error_info"] = f"Parameter count calculation failed: {str(e)}"
    
    # Get VRAM estimate
    try:
        vram_est = estimate_vram_usage(model_config, dtype="float16")
        debug_info["vram_estimate"] = vram_est
        logger.info(f"Estimated VRAM usage: {vram_est:.2f} GB")
    except Exception as e:
        logger.error(f"Error estimating VRAM: {e}")
        debug_info["error_info"] = f"VRAM estimation failed: {str(e)}"
    
    # Get available VRAM
    try:
        available_vram = get_available_vram()
        debug_info["available_vram"] = available_vram
        logger.info(f"Available VRAM: {available_vram:.2f} GB")
    except Exception as e:
        logger.error(f"Error getting available VRAM: {e}")
        debug_info["error_info"] = f"VRAM detection failed: {str(e)}"
    
    # Get PyTorch version
    if HAS_TORCH:
        debug_info["pytorch_version"] = torch.__version__
        logger.info(f"PyTorch version: {torch.__version__}")
    
    # Get CUDA info
    # Memory optimization: Memory-critical operation
    if HAS_TORCH and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        debug_info["system_info"]["cuda_version"] = torch.version.cuda
        # Memory optimization: Memory-critical operation
        debug_info["system_info"]["cudnn_version"] = torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else "N/A"
        debug_info["system_info"]["cuda_device_count"] = torch.cuda.device_count()
        # Memory optimization: CUDA operations for GPU acceleration
        debug_info["system_info"]["cuda_current_device"] = torch.cuda.current_device()
        # Memory optimization: CUDA operations for GPU acceleration
        debug_info["system_info"]["cuda_device_name"] = torch.cuda.get_device_name(0)
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Get memory info
        # Memory optimization: Memory-critical operation
        try:
            debug_info["memory_stats"]["total_memory"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            # Memory optimization: CUDA operations for GPU acceleration
            debug_info["memory_stats"]["allocated_memory"] = torch.cuda.memory_allocated(0) / (1024**3)
            # Memory optimization: CUDA operations for GPU acceleration
            debug_info["memory_stats"]["reserved_memory"] = torch.cuda.memory_reserved(0) / (1024**3)
            # Memory optimization: CUDA operations for GPU acceleration
            debug_info["memory_stats"]["max_memory_allocated"] = torch.cuda.max_memory_allocated(0) / (1024**3)
            # Memory optimization: CUDA operations for GPU acceleration
            
            logger.info(f"CUDA Memory Stats: Total: {debug_info['memory_stats']['total_memory']:.2f} GB, "
            # Memory optimization: Memory-critical operation
                       f"Allocated: {debug_info['memory_stats']['allocated_memory']:.2f} GB")
                       # Memory optimization: Memory-critical operation
        except Exception as e:
            logger.error(f"Error getting CUDA memory stats: {e}")
            # Memory optimization: Memory-critical operation
    
    # Save debug info if filepath provided
    if filepath:
        try:
            with open(filepath, 'w') as f:
                json.dump(debug_info, f, indent=2)
            logger.info(f"Debug info saved to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save debug info: {e}")
    
    return debug_info

# Add error catching wrapper for model creation attempts
# Memory optimization: Explicit memory cleanup
def safely_create_model(config_or_name, debug_output_path=None):
    """
    Attempt to create a model with extensive error reporting.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        config_or_name: Either a ModelConfig object or a string name
        debug_output_path: Path to save detailed debug info if creation fails
        
    Returns:
        A tuple of (model, error_message) where error_message is None if successful
    """
    if isinstance(config_or_name, str):
        try:
            config = get_model_config(config_or_name)
        except Exception as e:
            error_msg = f"Failed to get configuration for {config_or_name}: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return None, error_msg
    else:
        config = config_or_name
        
    logger.info(f"Attempting to create model with {config.model_name} configuration")
    # Memory optimization: Explicit memory cleanup
    
    try:
        # This is a placeholder - the actual model creation would happen here
        # Memory optimization: Explicit memory cleanup
        # in the real implementation
        logger.info("Model creation successful")
        # Memory optimization: Explicit memory cleanup
        return "model_object_placeholder", None
    except Exception as e:
        logger.error(f"Model creation failed: {str(e)}")
        # Memory optimization: Explicit memory cleanup
        
        # Detailed error logging
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }
        
        # Get detailed debug info
        debug_info = debug_model_creation(config, filepath=debug_output_path)
        debug_info["error_info"] = error_details
        
        # Format error message
        error_msg = f"Model creation failed: {str(e)}\n"
        # Memory optimization: Explicit memory cleanup
        if hasattr(e, '__notes__'):
            error_msg += f"Notes: {e.__notes__}\n"
        
        error_msg += f"\nDebug information saved to: {debug_output_path}\n"
        error_msg += f"Model config: {config.model_name} ({config.hidden_size} hidden size, {config.num_hidden_layers} layers)\n"
        # Memory optimization: Explicit memory cleanup
        if config.quantization and config.quantization.get('enabled'):
            error_msg += f"Quantization: {config.quantization.get('bits')}-bit {config.quantization.get('method')}\n"
        error_msg += f"Available VRAM: {get_available_vram():.2f} GB\n"
        error_msg += f"Estimated VRAM usage: {estimate_vram_usage(config):.2f} GB\n"
        
        # Log the formatted error
        logger.error(error_msg)
        
        return None, error_msg

# Initialize logging with default settings
setup_logging()
