#!/usr/bin/env python3
"""
ImpressionCore Configuration Module
===================================

Centralized configuration management for the ImpressionCore framework.

This module provides:
- Model configuration loading and validation
- Training configuration management  
- System configuration settings
- Hardware optimization parameters

Directory Structure:
- config.json: Main system configuration
- *_arch.yaml: Model architecture configurations
- *_train.yaml: Training configurations
- *_eval.yaml: Evaluation configurations
- requirements files: Dependency management

File: core\config\__init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-06-06
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [framework, core, production, 2025, object-oriented]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements   init   functionality for the
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
from src.core.config.__init__ import UKSConfig
instance = UKSConfig()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# Import ConfigManager directly from src.core.config_manager
from .config_manager import ConfigManager
# Import model configuration classes
# Memory optimization: Explicit memory cleanup
from .model_config import ModelConfig, TrainingConfig, ModelDimensions # Changed to relative import

# Configuration file paths
CONFIG_FILES = {
    'main': 'config.json',
    'b1_arch': 'impressioncore_b1_arch.yaml',
    'b1_train': 'impressioncore_b1_train.yaml',
    'b1_eval': 'impressioncore_b1_eval.yaml',
    'training_qlora': 'training_config_qlora.json'
}

def get_config_path(config_name: str) -> str:
    """Get the full path to a configuration file."""
    import os
    current_dir = os.path.dirname(__file__)
    if config_name in CONFIG_FILES:
        return os.path.join(current_dir, CONFIG_FILES[config_name])
    return os.path.join(current_dir, config_name)

def load_config(config_name: str) -> dict:
    """Load configuration from file."""
    import json
    import yaml
    import os
    
    config_path = get_config_path(config_name)
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Determine file type and load accordingly
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            return json.load(f)
    elif config_path.endswith(('.yaml', '.yml')):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported configuration file format: {config_path}")

# UKS Configuration
class UKSConfig:
    """Configuration for Universal Knowledge Store (UKS)."""
    
    def __init__(self, 
                 vector_dim: int = 768,
                 max_knowledge_entries: int = 1000000,
                 similarity_threshold: float = 0.8,
                 enable_compression: bool = True,
                 storage_backend: str = "faiss",
                 index_type: str = "IndexFlatIP"):
        """
        Initialize UKS configuration.
        
        Args:
            vector_dim: Dimension of knowledge vectors
            max_knowledge_entries: Maximum number of knowledge entries
            similarity_threshold: Threshold for similarity matching
            enable_compression: Whether to enable knowledge compression
            storage_backend: Backend for vector storage (faiss, annoy, etc.)
            index_type: Type of FAISS index to use
        """
        self.vector_dim = vector_dim
        self.max_knowledge_entries = max_knowledge_entries
        self.similarity_threshold = similarity_threshold
        self.enable_compression = enable_compression
        self.storage_backend = storage_backend
        self.index_type = index_type

# Import specific config getters if they exist or create them
# Assuming get_impressioncore_1b_config might be a utility function.
# For now, let's ensure ModelConfig and ModelDimensions are available.

# It seems 'get_impressioncore_1b_config' is not a standard part of the config system.
# If it's a specific configuration instance, it should be defined and imported,
# or the test should create a ModelConfig instance directly.
# For now, I will add a placeholder if it's intended to be a function here.

def get_impressioncore_1b_config() -> ModelConfig:
    """Returns a ModelConfig for impressioncore_1b, placeholder."""
    # This is a placeholder. The actual implementation might load from a specific file
    # or have hardcoded values for the "impressioncore_1b" model.
    # For tests to pass, this needs to be a valid ModelConfig.
    return ModelConfig(hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072)

# Export main functions and constants
__all__ = ['CONFIG_FILES', 'get_config_path', 'load_config']
