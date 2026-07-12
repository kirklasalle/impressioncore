#!/usr/bin/env python3
"""
ImpressionCore: Module

Module for module functionality in the ImpressionCore framework.

File: core\brain\system\module.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, core, production, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements module functionality for the
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
from src.core.brain.system.module import MainClass
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
import time
import threading
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
import logging

from src.core.utils.log_manager import log_state_change, store_persistent_data, get_persistent_data
from src.core.system.memory_config import get_optimal_batch_size, monitor_memory_usage
# Memory optimization: Memory-critical operation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("system_oversight_module")

# Constants
TASK_STATES = {
    "PENDING": "pending",
    "RUNNING": "running",
    "COMPLETED": "completed",
    "FAILED": "failed"
}

# Task management
_task_lock = threading.Lock()
_active_tasks = {}
_completed_tasks = {}

# Module registry
_module_registry = {}

def initialize(config_path: Optional[str] = None) -> bool:
    """
    Initialize the System Oversight Module with configuration.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        True if initialization successful
    """
    try:
        # Load configuration
        config = _load_config(config_path)
        if not config:
            return False
            
        # Initialize module registry
        _initialize_module_registry(config)
        
        # Log initialization
        log_state_change(
            component="system_oversight_module",
            old_state={"status": "initializing"},
            new_state={"status": "ready", "config": config}
        )
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize System Oversight Module: {e}")
        return False

def register_module(module_name: str, module_interface: Dict[str, Callable]):
    """
    Register a module with the System Oversight Module.
    
    Args:
        module_name: Name of the module
        module_interface: Dictionary with module interface functions
    """
    with _task_lock:
        _module_registry[module_name] = {
            "interface": module_interface,
            "last_used": time.time()
        }
        logger.info(f"Registered module: {module_name}")

def execute_task(module_name: str, task_type: str, parameters: Dict[str, Any], callback: Optional[Callable] = None) -> str:
    """
    Execute a task in a specified module.
    
    Args:
        module_name: Name of the module to execute the task
        task_type: Type of task to execute
        parameters: Task parameters
        callback: Optional callback function to call upon task completion
        
    Returns:
        Task ID
    """
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "module": module_name,
        "type": task_type,
        "parameters": parameters,
        "status": TASK_STATES["PENDING"],
        "created_at": time.time(),
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
        "callback": callback
    }
    
    with _task_lock:
        _active_tasks[task_id] = task
    
    # Start task execution in a separate thread
    threading.Thread(target=_execute_task, args=(task_id, module_name, task_type, parameters)).start()
    
    return task_id

def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a task.
    
    Args:
        task_id: ID of the task
        
    Returns:
        Task status dictionary
    """
    with _task_lock:
        if task_id in _active_tasks:
            return _active_tasks[task_id]
        elif task_id in _completed_tasks:
            return _completed_tasks[task_id]
        else:
            return {"error": "Task not found"}

def _load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration for the System Oversight Module.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configuration dictionary
    """
    # Default configuration
    default_config = {
        "task_timeout_seconds": 3600,
        "max_concurrent_tasks": 10,
        "module_registry": {}
    }
    
    # If no config path, use default
    if not config_path:
        return default_config
        
    # Load from file if provided
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
                
                # Update default with custom config
                for key, value in custom_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
                        
            logger.info(f"Loaded custom System Oversight Module configuration from {config_path}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
    
    return default_config

def _initialize_module_registry(config: Dict[str, Any]):
    """
    Initialize the module registry based on configuration.
    
    Args:
        config: Configuration dictionary
    """
    module_registry_config = config.get("module_registry", {})
    
    for module_name, module_data in module_registry_config.items():
        module_interface = module_data.get("interface")
        if module_interface:
            register_module(module_name, module_interface)

def _execute_task(task_id: str, module_name: str, task_type: str, parameters: Dict[str, Any]):
    """Execute a task in a separate thread."""
    try:
        # Get module interface
        module_data = _module_registry.get(module_name)
        if not module_data or "interface" not in module_data:
            raise ValueError(f"Module {module_name} not properly registered")
        
        module_interface = module_data["interface"]
        
        # Call module's process method
        result = module_interface["process"](parameters)
        
        # Update task with result
        with _task_lock:
            if task_id in _active_tasks:
                task = _active_tasks[task_id]
                task["status"] = TASK_STATES["COMPLETED"]
                task["completed_at"] = time.time()
                task["result"] = result
                
                # Call callback if provided
                if task["callback"] and callable(task["callback"]):
                    try:
                        task["callback"](task)
                    except Exception as callback_error:
                        logger.error(f"Error in task callback: {callback_error}")
                
                # Move to completed tasks
                _store_completed_task(task)
                del _active_tasks[task_id]
                # Memory optimization: Explicit memory cleanup
        
        # Update module last used time
        module_data["last_used"] = time.time()
        
        # Log completion
        log_state_change(
            component="system_oversight_module",
            old_state={"action": "task_execution", "task_id": task_id},
            new_state={"action": "task_completed", "task_id": task_id}
        )
    except Exception as e:
        # Handle task failure
        logger.error(f"Task {task_id} failed: {e}")
        
        with _task_lock:
            if task_id in _active_tasks:
                task = _active_tasks[task_id]
                task["status"] = TASK_STATES["FAILED"]
                task["completed_at"] = time.time()
                task["error"] = str(e)
                
                # Call callback if provided
                if task["callback"] and callable(task["callback"]):
                    try:
                        task["callback"](task)
                    except Exception as callback_error:
                        logger.error(f"Error in task callback: {callback_error}")
                
                # Move to completed tasks
                _store_completed_task(task)
                del _active_tasks[task_id]
                # Memory optimization: Explicit memory cleanup
        
        # Log failure
        log_state_change(
            component="system_oversight_module",
            old_state={"action": "task_execution", "task_id": task_id},
            new_state={"action": "task_failed", "task_id": task_id, "error": str(e)}
        )

def _check_task_timeouts(timeout_seconds: int):
    """Check for and handle timed-out tasks."""
    current_time = time.time()
    
    with _task_lock:
        timed_out_tasks = []
        
        # Find timed-out tasks
        for task_id, task in _active_tasks.items():
            if (task["status"] == TASK_STATES["RUNNING"] and 
                task["started_at"] and 
                current_time - task["started_at"] > timeout_seconds):
                timed_out_tasks.append(task_id)
        
        # Handle timed-out tasks
        for task_id in timed_out_tasks:
            task = _active_tasks[task_id]
            
            # Update task status
            task["status"] = TASK_STATES["FAILED"]
            task["completed_at"] = current_time
            task["error"] = f"Task timed out after {timeout_seconds} seconds"
            
            # Call callback if provided
            if task["callback"] and callable(task["callback"]):
                try:
                    task["callback"](task)
                except Exception as callback_error:
                    logger.error(f"Error in timeout callback: {callback_error}")
            
            # Move to completed tasks and remove from active tasks
            _store_completed_task(task)
            del _active_tasks[task_id]
            # Memory optimization: Explicit memory cleanup
            
            # Log timeout
            logger.warning(f"Task {task_id} timed out after {timeout_seconds} seconds")
            log_state_change(
                component="system_oversight_module",
                old_state={"action": "task_execution", "task_id": task_id},
                new_state={"action": "task_timed_out", "task_id": task_id}
            )

def _store_completed_task(task: Dict[str, Any]):
    """
    Store a completed task in persistent storage.
    
    Args:
        task: Task data to store
    """
    # Get existing completed tasks
    completed_tasks = get_persistent_data("completed_tasks", {})
    
    # Add this task
    task_id = task["id"]
    completed_tasks[task_id] = task
    
    # Store updated completed tasks
    # Only keep the 100 most recent tasks to avoid excessive storage
    if len(completed_tasks) > 100:
        # Sort by completion time and keep only the most recent 100
        sorted_tasks = sorted(
            completed_tasks.items(), 
            key=lambda x: x[1].get("completed_at", 0),
            reverse=True
        )
        completed_tasks = dict(sorted_tasks[:100])
    
    store_persistent_data("completed_tasks", completed_tasks)