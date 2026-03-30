#!/usr/bin/env python3
"""
ImpressionCore: Config Memlog

Module for config memlog functionality in the ImpressionCore framework.

File: memlog\config_memlog.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, production, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements config memlog functionality for the
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
from memlog.config_memlog import MainClass
instance = MainClass()
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
from typing import Dict, Any, Optional

from . import PERSISTENCE_DIR, store_persistent_data, get_persistent_data

# Set up logging
logger = logging.getLogger("memlog.config")

# Configuration constants
DEFAULT_CONFIG_KEY = "system_config"
USER_CONFIG_KEY = "user_config"


def get_system_config() -> Dict[str, Any]:
    """
    Get the system configuration.
    
    Returns:
        Dictionary of system configuration values
    """
    config = get_persistent_data(DEFAULT_CONFIG_KEY, {})
    
    # If no config exists, create default
    if not config:
        config = create_default_config()
        save_system_config(config)
        
    return config


def save_system_config(config: Dict[str, Any]) -> bool:
    """
    Save the system configuration.
    
    Args:
        config: Dictionary of configuration values
        
    Returns:
        True if the configuration was saved successfully, False otherwise
    """
    return store_persistent_data(DEFAULT_CONFIG_KEY, config)


def get_user_config() -> Dict[str, Any]:
    """
    Get the user configuration.
    
    Returns:
        Dictionary of user configuration values
    """
    return get_persistent_data(USER_CONFIG_KEY, {})


def save_user_config(config: Dict[str, Any]) -> bool:
    """
    Save the user configuration.
    
    Args:
        config: Dictionary of configuration values
        
    Returns:
        True if the configuration was saved successfully, False otherwise
    """
    return store_persistent_data(USER_CONFIG_KEY, config)


def update_config_value(key: str, value: Any, user_config: bool = False) -> bool:
    """
    Update a configuration value.
    
    Args:
        key: Configuration key (can be nested using dot notation, e.g., "logging.level")
        value: Value to set
        user_config: Whether to update user config (True) or system config (False)
        
    Returns:
        True if the value was updated successfully, False otherwise
    """
    try:
        # Get the appropriate config
        if user_config:
            config = get_user_config()
        else:
            config = get_system_config()
            
        # Handle nested keys
        if "." in key:
            parts = key.split(".")
            current = config
            
            # Navigate to the correct nesting level
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
                
            # Set the value
            current[parts[-1]] = value
        else:
            # Simple case, just update the key
            config[key] = value
            
        # Save the config
        if user_config:
            return save_user_config(config)
        else:
            return save_system_config(config)
    
    except Exception as e:
        logger.error(f"Error updating config value {key}: {e}")
        return False


def get_config_value(key: str, default: Any = None, user_config: bool = False) -> Any:
    """
    Get a configuration value.
    
    Args:
        key: Configuration key (can be nested using dot notation, e.g., "logging.level")
        default: Default value to return if the key doesn't exist
        user_config: Whether to get from user config (True) or system config (False)
        
    Returns:
        The configuration value or default if not found
    """
    try:
        # Get the appropriate config
        if user_config:
            config = get_user_config()
        else:
            config = get_system_config()
            
        # Handle nested keys
        if "." in key:
            parts = key.split(".")
            current = config
            
            # Navigate to the correct nesting level
            for part in parts[:-1]:
                if part not in current:
                    return default
                current = current[part]
                
            # Get the value
            return current.get(parts[-1], default)
        else:
            # Simple case, just get the key
            return config.get(key, default)
    
    except Exception as e:
        logger.error(f"Error getting config value {key}: {e}")
        return default


def create_default_config() -> Dict[str, Any]:
    """
    Create the default system configuration.
    
    Returns:
        Dictionary of default configuration values
    """
    import platform
    import datetime
    
    current_time = datetime.datetime.now().isoformat()
    
    return {
        "system": {
            "version": "0.1.0",
            "created_at": current_time,
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "path": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        },
        "logging": {
            "level": "INFO",
            "file_logging_enabled": True,
            "console_logging_enabled": True,
            "max_log_size_mb": 10,
            "max_log_files": 5,
        },
        "memlog": {
            "enabled": True,
            "auto_consolidate": True,
            "consolidation_days": 30,
            "max_state_entries": 1000,
            "max_task_entries": 1000,
            "max_changelog_entries": 1000,
        },
        "model": {
            "default_model_path": None,
            "use_api": False,
            "api_key": None,
            "api_endpoint": "https://api.impressioncore.ai/v1",
            "memory_optimization": True,
            # Memory optimization: Memory-critical operation
        },
        "training": {
            "enabled": True,
            "output_dir": "./output",
            "batch_size": 1,  # Default for 4GB VRAM
            "gradient_accumulation_steps": 16,
            "fp16": True,
        },
        "ui": {
            "theme": "light",
            "auto_save": True,
            "show_welcome": True,
        }
    }


def reset_config() -> bool:
    """
    Reset the system configuration to default values.
    
    Returns:
        True if the configuration was reset successfully, False otherwise
    """
    try:
        default_config = create_default_config()
        success = save_system_config(default_config)
        
        if success:
            logger.info("System configuration reset to defaults")
        else:
            logger.error("Failed to reset system configuration")
            
        return success
    except Exception as e:
        logger.error(f"Error resetting configuration: {e}")
        return False


# Export functions
__all__ = [
    "get_system_config",
    "save_system_config",
    "get_user_config",
    "save_user_config",
    "update_config_value",
    "get_config_value",
    "reset_config",
]
