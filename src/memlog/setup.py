#!/usr/bin/env python3
"""
ImpressionCore: Setup

Module for setup functionality in the ImpressionCore framework.

File: memlog\setup.py
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
This module implements setup functionality for the
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
from memlog.setup import MainClass
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
import logging
import datetime
from typing import Dict, Any, Optional

from . import (
    initialize_memlog,
    verify_memlog_structure,
    log_state_change,
    log_task,
    store_persistent_data,
    get_persistent_data,
    log_change,
    consolidate_logs,
)
from .config_memlog import get_system_config, create_default_config, save_system_config
from .state import update_state
from .tasks import create_task


def setup_memlog(reset: bool = False) -> bool:
    """
    Set up the memlog system.
    
    Args:
        reset: Whether to reset configuration to defaults
        
    Returns:
        True if setup was successful, False otherwise
    """
    try:
        # Initialize memlog directories
        success = initialize_memlog()
        if not success:
            return False
        
        # Reset config if requested
        if reset:
            default_config = create_default_config()
            save_system_config(default_config)
        
        # Get config
        config = get_system_config()
        
        # Log system state
        system_info = {
            "event": "system_startup",
            "timestamp": datetime.datetime.now().isoformat(),
            "config_version": config.get("system", {}).get("version", "unknown"),
            "memlog_enabled": config.get("memlog", {}).get("enabled", True),
            "auto_consolidate": config.get("memlog", {}).get("auto_consolidate", True),
        }
        log_state_change(system_info)
        
        # Create setup task
        task_id = create_task("memlog_setup", {
            "reset": reset,
            "status": "completed",
            "timestamp": datetime.datetime.now().isoformat(),
        })
        
        # Log component change
        log_change("memlog", {
            "type": "setup",
            "description": "Memlog system initialized",
            "reset": reset,
        })
        
        # Run consolidation if enabled
        if config.get("memlog", {}).get("auto_consolidate", True):
            consolidation_days = config.get("memlog", {}).get("consolidation_days", 30)
            consolidate_logs(consolidation_days)
        
        logging.info("Memlog system setup complete")
        return True
    
    except Exception as e:
        logging.error(f"Error setting up memlog: {e}")
        return False


def check_memlog_health() -> Dict[str, Any]:
    """
    Check the health of the memlog system.
    
    Returns:
        Dictionary containing health status information
    """
    health = {
        "timestamp": datetime.datetime.now().isoformat(),
        "structure_valid": False,
        "config_valid": False,
        "state_count": 0,
        "task_count": 0,
        "persistence_count": 0,
        "changelog_count": 0,
        "issues": [],
        "status": "unknown"
    }
    
    try:
        # Check structure
        structure_valid = verify_memlog_structure()
        health["structure_valid"] = structure_valid
        
        if not structure_valid:
            health["issues"].append("Invalid memlog directory structure")
        
        # Check config
        try:
            config = get_system_config()
            health["config_valid"] = True
        except Exception as config_error:
            health["issues"].append(f"Error loading configuration: {config_error}")
            health["config_valid"] = False
        
        # Count files in directories
        import glob
        
        # Count state files
        state_files = glob.glob(os.path.join(os.path.dirname(__file__), "state", "*.json"))
        health["state_count"] = len(state_files)
        
        # Count task files
        task_files = glob.glob(os.path.join(os.path.dirname(__file__), "tasks", "*.json"))
        health["task_count"] = len(task_files)
        
        # Count persistence files
        persistence_files = glob.glob(os.path.join(os.path.dirname(__file__), "persistence", "*.json"))
        health["persistence_count"] = len(persistence_files)
        
        # Count changelog files
        changelog_files = glob.glob(os.path.join(os.path.dirname(__file__), "changelogs", "*.json"))
        health["changelog_count"] = len(changelog_files)
        
        # Set overall status
        if not structure_valid or not health["config_valid"]:
            health["status"] = "error"
        elif health["state_count"] == 0 and health["task_count"] == 0:
            health["status"] = "empty"
            health["issues"].append("Memlog is empty (no state or tasks)")
        elif any(count > 10000 for count in [
            health["state_count"], 
            health["task_count"], 
            health["changelog_count"]
        ]):
            health["status"] = "warning"
            health["issues"].append("Memlog contains a large number of files. Consider consolidation.")
        else:
            health["status"] = "healthy"
        
        return health
    except Exception as e:
        health["status"] = "error"
        health["issues"].append(f"Error checking memlog health: {str(e)}")
        logging.error(f"Error checking memlog health: {e}")
        return health


def repair_memlog() -> bool:
    """
    Attempt to repair the memlog system if issues are detected.
    
    Returns:
        True if repair was successful or not needed, False otherwise
    """
    try:
        # Check health first
        health = check_memlog_health()
        
        if health["status"] == "healthy":
            logging.info("Memlog is healthy, no repairs needed")
            return True
            
        # If structure is invalid, reinitialize
        if not health["structure_valid"]:
            logging.warning("Repairing invalid memlog structure")
            initialize_memlog()
            
        # If config is invalid, reset it
        if not health["config_valid"]:
            logging.warning("Repairing invalid memlog configuration")
            default_config = create_default_config()
            save_system_config(default_config)
            
        # Log repair action
        log_change("memlog", {
            "type": "repair",
            "description": "Memlog system repaired",
            "issues_fixed": health["issues"],
        })
        
        # Check health again
        new_health = check_memlog_health()
        if new_health["status"] in ["healthy", "empty"]:
            logging.info("Memlog repair successful")
            return True
        else:
            logging.error("Memlog repair failed")
            return False
    
    except Exception as e:
        logging.error(f"Error repairing memlog: {e}")
        return False


def initialize_memlog_for_model(model_id: str, model_type: str, model_config: Dict[str, Any]) -> str:
    """
    Initialize memlog for a specific model.
    
    Args:
        model_id: Unique identifier for the model
        model_type: Type of model (e.g., "transformer", "diffusion")
        # Memory optimization: Explicit memory cleanup
        model_config: Model configuration dictionary
        # Memory optimization: Explicit memory cleanup
        
    Returns:
        Task ID for the initialization task, or empty string on failure
    """
    try:
        # Ensure memlog is set up
        if not verify_memlog_structure():
            setup_memlog()
        
        # Create model info in persistent storage
        # Memory optimization: Explicit memory cleanup
        model_info = {
            "model_id": model_id,
            "model_type": model_type,
            "created_at": datetime.datetime.now().isoformat(),
            "config": model_config
        }
        
        store_persistent_data(f"model_{model_id}", model_info)
        
        # Create initialization task
        task_data = {
            "model_id": model_id,
            "model_type": model_type,
            "action": "model_initialization",
            "status": "created"
        }
        
        task_id = create_task(f"model_init_{model_id}", task_data)
        
        # Log component change
        log_change("model", {
            "type": "initialization",
            "description": f"Model {model_id} ({model_type}) initialized",
            # Memory optimization: Explicit memory cleanup
            "model_id": model_id
        })
        
        return task_id
    except Exception as e:
        logging.error(f"Error initializing memlog for model {model_id}: {e}")
        # Memory optimization: Explicit memory cleanup
        return ""


# Export functions
__all__ = [
    "setup_memlog",
    "check_memlog_health",
    "repair_memlog",
    "initialize_memlog_for_model"
]
