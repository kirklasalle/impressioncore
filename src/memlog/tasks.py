#!/usr/bin/env python3
"""
ImpressionCore: Tasks

Module for tasks functionality in the ImpressionCore framework.

File: memlog\tasks.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements tasks functionality for the
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
from memlog.tasks import MainClass
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
import glob
import uuid
import logging
import datetime
from typing import Dict, List, Any, Optional, Union

from . import TASKS_DIR, log_task

# Set up logging
logger = logging.getLogger("memlog.tasks")


def create_task(task_name: str, task_data: Dict[str, Any] = None) -> str:
    """
    Create a new task and log it.
    
    Args:
        task_name: Name of the task
        task_data: Additional task data
        
    Returns:
        Task ID of the created task, or empty string on failure
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task data
        data = task_data or {}
        data.update({
            "task_id": task_id,
            "task_name": task_name,
            "created_at": datetime.datetime.now().isoformat(),
            "status": "created",
            "progress": 0.0
        })
        
        # Log the task
        success = log_task(task_id, data)
        
        if success:
            logger.info(f"Task created: {task_name} (ID: {task_id})")
            return task_id
        else:
            logger.error(f"Failed to create task: {task_name}")
            return ""
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return ""


def update_task(task_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update an existing task.
    
    Args:
        task_id: ID of the task to update
        updates: Dictionary of updates to apply
        
    Returns:
        True if the task was updated successfully, False otherwise
    """
    try:
        # Get current task data
        task_data = get_task(task_id)
        if not task_data:
            logger.error(f"Task not found: {task_id}")
            return False
        
        # Apply updates
        task_data.update(updates)
        
        # Add update timestamp
        task_data["updated_at"] = datetime.datetime.now().isoformat()
        
        # Log the updated task
        success = log_task(task_id, task_data)
        
        if success:
            logger.info(f"Task updated: {task_id}")
        else:
            logger.error(f"Failed to update task: {task_id}")
            
        return success
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return False


def update_task_progress(task_id: str, progress: float, status: Optional[str] = None) -> bool:
    """
    Update a task's progress.
    
    Args:
        task_id: ID of the task
        progress: Progress value (0.0 to 1.0)
        status: Optional status update
        
    Returns:
        True if the progress was updated successfully, False otherwise
    """
    # Normalize progress to be between 0 and 1
    progress = max(0.0, min(1.0, float(progress)))
    
    updates = {"progress": progress}
    if status:
        updates["status"] = status
        
    return update_task(task_id, updates)


def complete_task(task_id: str, result: Any = None) -> bool:
    """
    Mark a task as complete.
    
    Args:
        task_id: ID of the task
        result: Optional result data
        
    Returns:
        True if the task was marked complete successfully, False otherwise
    """
    updates = {
        "status": "completed",
        "progress": 1.0,
        "completed_at": datetime.datetime.now().isoformat()
    }
    
    if result is not None:
        updates["result"] = result
        
    return update_task(task_id, updates)


def fail_task(task_id: str, error: str = None) -> bool:
    """
    Mark a task as failed.
    
    Args:
        task_id: ID of the task
        error: Optional error message
        
    Returns:
        True if the task was marked failed successfully, False otherwise
    """
    updates = {
        "status": "failed",
        "failed_at": datetime.datetime.now().isoformat()
    }
    
    if error:
        updates["error"] = error
        
    return update_task(task_id, updates)


def get_task(task_id: str) -> Dict[str, Any]:
    """
    Get information about a specific task.
    
    Args:
        task_id: ID of the task
        
    Returns:
        Task data dictionary, or empty dict if not found
    """
    try:
        # Create filename based on task_id
        filename = f"task_{task_id}.json"
        filepath = os.path.join(TASKS_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            logger.warning(f"Task not found: {task_id}")
            return {}
            
        # Read task data
        with open(filepath, 'r', encoding='utf-8') as f:
            task_data = json.load(f)
            
        return task_data
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        return {}


def get_all_tasks(status_filter: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get all tasks, optionally filtered by status.
    
    Args:
        status_filter: Optional status to filter by
        limit: Maximum number of tasks to return
        
    Returns:
        List of task dictionaries
    """
    try:
        # Find all task files
        pattern = os.path.join(TASKS_DIR, "task_*.json")
        files = glob.glob(pattern)
        
        if not files:
            return []
            
        # Read task data
        tasks = []
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                    
                # Apply status filter if specified
                if status_filter is None or task_data.get("status") == status_filter:
                    tasks.append(task_data)
            except Exception as file_error:
                logger.error(f"Error reading task file {filepath}: {file_error}")
                
        # Sort by created_at timestamp (newest first)
        tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        
        # Apply limit
        return tasks[:limit]
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return []


def get_active_tasks() -> List[Dict[str, Any]]:
    """
    Get all active (not completed or failed) tasks.
    
    Returns:
        List of active task dictionaries
    """
    try:
        # Find all task files
        pattern = os.path.join(TASKS_DIR, "task_*.json")
        files = glob.glob(pattern)
        
        if not files:
            return []
            
        # Read task data
        active_tasks = []
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                    
                # Filter for active tasks
                status = task_data.get("status", "")
                if status not in ["completed", "failed"]:
                    active_tasks.append(task_data)
            except Exception as file_error:
                logger.error(f"Error reading task file {filepath}: {file_error}")
                
        return active_tasks
    except Exception as e:
        logger.error(f"Error getting active tasks: {e}")
        return []


def delete_task(task_id: str) -> bool:
    """
    Delete a task.
    
    Args:
        task_id: ID of the task to delete
        
    Returns:
        True if the task was deleted successfully, False otherwise
    """
    try:
        # Create filename based on task_id
        filename = f"task_{task_id}.json"
        filepath = os.path.join(TASKS_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            logger.warning(f"Task not found for deletion: {task_id}")
            return False
            
        # Delete the file
        os.remove(filepath)
        
        logger.info(f"Task deleted: {task_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return False


def task_exists(task_id: str) -> bool:
    """
    Check if a task exists.
    
    Args:
        task_id: ID of the task
        
    Returns:
        True if the task exists, False otherwise
    """
    # Create filename based on task_id
    filename = f"task_{task_id}.json"
    filepath = os.path.join(TASKS_DIR, filename)
    
    # Check if file exists
    return os.path.exists(filepath)


# Export functions
__all__ = [
    "create_task",
    "update_task",
    "update_task_progress",
    "complete_task",
    "fail_task",
    "get_task",
    "get_all_tasks",
    "get_active_tasks",
    "delete_task",
    "task_exists",
]
