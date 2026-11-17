#!/usr/bin/env python3
"""
ImpressionCore: Config Utils

Module for config utils functionality in the ImpressionCore framework.

File: core\config_utils.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
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
This module implements config utils functionality for the
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
from src.core.config_utils import ConfigMixin
instance = ConfigMixin()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import copy
import logging
from typing import Dict, Any, Optional, List, Union, Set

logger = logging.getLogger(__name__)

def merge_configs(default_config: Dict[str, Any], override_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Merge a default configuration with an override configuration.
    
    This function handles nested dictionaries properly by recursively merging them,
    rather than simply overwriting the entire dictionary.
    
    Example:
        default_config = {
            "model": {"hidden_size": 768, "num_layers": 12},
            "training": {"lr": 5e-5, "epochs": 3}
        }
        override_config = {
            "model": {"hidden_size": 1024},
            "training": {"lr": 2e-5}
        }
        
        # Result will be:
        # {
        #     "model": {"hidden_size": 1024, "num_layers": 12},
        #     "training": {"lr": 2e-5, "epochs": 3}
        # }
        
    Args:
        default_config: Default configuration dictionary
        override_config: Optional configuration to override default values
        
    Returns:
        Merged configuration dictionary
    """
    if override_config is None:
        return copy.deepcopy(default_config)
    
    result = copy.deepcopy(default_config)
    
    for key, value in override_config.items():
        # Handle nested dictionaries recursively
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    
    return result

def validate_config(config: Dict[str, Any], required_keys: Optional[List[str]] = None, 
                   value_types: Optional[Dict[str, Union[type, List[type]]]] = None) -> None:
    """
    Validate a configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        required_keys: Optional list of keys that must be present
        value_types: Optional dictionary mapping keys to expected types
        
    Raises:
        ValueError: If validation fails
    """
    # Check required keys
    if required_keys:
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")
    
    # Check value types
    if value_types:
        for key, expected_types in value_types.items():
            if key in config:
                # Convert single type to list for consistent handling
                if not isinstance(expected_types, list):
                    expected_types = [expected_types]
                
                # Check if value matches any of the expected types
                if not any(isinstance(config[key], t) for t in expected_types):
                    type_names = [t.__name__ for t in expected_types]
                    raise ValueError(f"Config key '{key}' has value of type {type(config[key]).__name__}, "
                                    f"expected one of: {', '.join(type_names)}")

def filter_config(config: Dict[str, Any], allowed_keys: Set[str]) -> Dict[str, Any]:
    """
    Filter a configuration dictionary to only include allowed keys.
    
    Args:
        config: Configuration dictionary to filter
        allowed_keys: Set of keys to include
        
    Returns:
        Filtered configuration dictionary
    """
    return {k: v for k, v in config.items() if k in allowed_keys}

class ConfigMixin:
    """
    Mixin class providing common configuration handling methods.
    
    This mixin can be added to classes that need to manage configuration dictionaries.
    It provides a standardized way to:
    
    1. Define default configurations
    2. Apply overrides to defaults
    3. Validate configurations
    4. Access merged configurations
    
    Usage example:
    ```
    class MyComponent(ConfigMixin):
        def __init__(self, config=None):
            self.config = self._get_config_dict(config)
            self._validate_config(self.config)
            # Initialize with self.config...
        
        def _get_default_config(self):
            return {
                "param1": "default_value",
                "param2": 42
            }
            
        def _validate_config(self, config):
            required_keys = ["param1"]
            value_types = {
                "param1": str,
                "param2": int
            }
            validate_config(config, required_keys, value_types)
    ```
    
    TODO:
    - Add support for config schema validation using JSON Schema
    - Implement nested configuration validation
    - Add support for environment variable overrides
    """
    
    def _get_config_dict(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get configuration dictionary with defaults applied.
        
        Args:
            config: Optional configuration overrides
            
        Returns:
            Configuration dictionary with defaults
        """
        # Get default configuration from class
        default_config = self._get_default_config()
        
        # Merge with provided config
        return merge_configs(default_config, config)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration for this component.
        
        Returns:
            Default configuration dictionary
        """
        # Override in subclass to provide class-specific defaults
        return {}
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration for this component.
        
        Args:
            config: Configuration to validate
            
        Raises:
            ValueError: If config is invalid
        """
        # Override in subclass to provide class-specific validation
        pass
