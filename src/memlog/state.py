#!/usr/bin/env python3
"""
ImpressionCore: State

Module for state functionality in the ImpressionCore framework.

File: memlog\state.py
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
This module implements state functionality for the
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
from memlog.state import MainClass
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
import logging
import datetime
from typing import Dict, List, Any, Optional, Union

from . import STATE_DIR, log_state_change

# Set up logging
logger = logging.getLogger("memlog.state")


def get_current_state() -> Dict[str, Any]:
    """
    Get the current state of the system by retrieving the most recent state logs.
    
    Returns:
        Dictionary representing the current state
    """
    try:
        # Find all state files
        pattern = os.path.join(STATE_DIR, "state_*.json")
        files = glob.glob(pattern)
        
        if not files:
            logger.warning("No state files found")
            return {}
        
        # Sort by modification time (newest first)
        files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        
        # Read the most recent file
        with open(files[0], 'r', encoding='utf-8') as f:
            state = json.load(f)
            
        return state
    except Exception as e:
        logger.error(f"Error getting current state: {e}")
        return {}


def get_state_history(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the history of state changes.
    
    Args:
        limit: Maximum number of state changes to retrieve
        
    Returns:
        List of state change dictionaries
    """
    try:
        # Find all state files
        pattern = os.path.join(STATE_DIR, "state_*.json")
        files = glob.glob(pattern)
        
        if not files:
            logger.warning("No state files found")
            return []
        
        # Sort by modification time (newest first)
        files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        
        # Limit the number of files
        files = files[:limit]
        
        # Read each file
        history = []
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    history.append(state)
            except Exception as file_error:
                logger.error(f"Error reading state file {filepath}: {file_error}")
        
        return history
    except Exception as e:
        logger.error(f"Error getting state history: {e}")
        return []


def update_state(state_update: Dict[str, Any], event_name: str = "state_update") -> bool:
    """
    Update the system state.
    
    Args:
        state_update: Dictionary of state values to update
        event_name: Name of the event causing the state update
        
    Returns:
        True if the state was updated successfully, False otherwise
    """
    try:
        # Get current state
        current_state = get_current_state()
        
        # Apply updates
        current_state.update(state_update)
        
        # Add event information
        current_state["event"] = event_name
        current_state["timestamp"] = datetime.datetime.now().isoformat()
        
        # Log the state change
        success = log_state_change(current_state)
        
        if success:
            logger.info(f"State updated: {event_name}")
        else:
            logger.error(f"Failed to log state update: {event_name}")
            
        return success
    except Exception as e:
        logger.error(f"Error updating state: {e}")
        return False


def get_state_diff(previous_state: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the differences between two states.
    
    Args:
        previous_state: Previous state dictionary
        current_state: Current state dictionary
        
    Returns:
        Dictionary of changes between the states
    """
    diff = {}
    
    # Find added or changed keys
    for key, value in current_state.items():
        if key not in previous_state:
            diff[key] = {"action": "added", "value": value}
        elif previous_state[key] != value:
            diff[key] = {
                "action": "changed", 
                "from": previous_state[key], 
                "to": value
            }
    
    # Find removed keys
    for key in previous_state:
        if key not in current_state:
            diff[key] = {"action": "removed", "value": previous_state[key]}
    
    return diff


def rollback_state(target_timestamp: Optional[str] = None) -> bool:
    """
    Roll back the system state to a previous point.
    
    Args:
        target_timestamp: Timestamp to roll back to, or None for the previous state
        
    Returns:
        True if the rollback was successful, False otherwise
    """
    try:
        # Find all state files
        pattern = os.path.join(STATE_DIR, "state_*.json")
        files = glob.glob(pattern)
        
        if not files:
            logger.warning("No state files found for rollback")
            return False
        
        # Sort by modification time (newest first)
        files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        
        # Find the target state file
        target_file = None
        if target_timestamp:
            # Find file closest to target timestamp
            for filepath in files:
                with open(filepath, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    if "timestamp" in state and state["timestamp"] <= target_timestamp:
                        target_file = filepath
                        break
        else:
            # Use the second most recent file (rollback one step)
            if len(files) > 1:
                target_file = files[1]
        
        if not target_file:
            logger.warning("No suitable state file found for rollback")
            return False
            
        # Read the target state
        with open(target_file, 'r', encoding='utf-8') as f:
            target_state = json.load(f)
            
        # Add rollback information
        target_state["event"] = "state_rollback"
        target_state["timestamp"] = datetime.datetime.now().isoformat()
        target_state["rolled_back_from"] = datetime.datetime.fromtimestamp(
            os.path.getmtime(files[0])
        ).isoformat()
        
        # Log the state change
        success = log_state_change(target_state)
        
        if success:
            logger.info(f"State rolled back to {target_state.get('timestamp', 'unknown')}")
        else:
            logger.error("Failed to log state rollback")
            
        return success
    except Exception as e:
        logger.error(f"Error rolling back state: {e}")
        return False


# Export functions
__all__ = [
    "get_current_state",
    "get_state_history",
    "update_state",
    "get_state_diff",
    "rollback_state",
]
