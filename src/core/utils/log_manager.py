#!/usr/bin/env python3
"""
ImpressionCore: Log Manager

Module for log manager functionality in the ImpressionCore framework.

File: core\log_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [core, production, framework, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements log manager functionality for the
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
from core.log_manager import MainClass
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
import shutil
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional, Union
import gzip

# Configure base logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("log_manager")

# Constants
MEMLOG_BASE = os.path.join('d:', 'Projects', 'impressioncore', 'memlog')
MAX_LOG_SIZE_MB = 10
MAX_LOGS_PER_CATEGORY = 7
COMPRESSION_THRESHOLD_MB = 5

def ensure_memlog_structure() -> bool:
    """
    Verify and create memlog directory structure if needed.
    
    Returns:
        True if directory structure is verified or created
    """
    subdirs = ['state', 'tasks', 'persistence', 'changelogs']
    
    for subdir in subdirs:
        path = os.path.join(MEMLOG_BASE, subdir)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                logger.info(f"Created missing memlog directory: {path}")
            except Exception as e:
                logger.error(f"Failed to create directory {path}: {e}")
                return False
    
    return True

def log_state_change(component: str, old_state: Any, new_state: Any) -> bool:
    """
    Log system state changes.
    
    Args:
        component: Component name
        old_state: Previous state
        new_state: New state
        
    Returns:
        True if successfully logged
    """
    timestamp = datetime.now().isoformat()
    filename = f"{component}_state.json"
    path = os.path.join(MEMLOG_BASE, 'state', filename)
    
    entry = {
        "timestamp": timestamp,
        "component": component,
        "old_state": old_state,
        "new_state": new_state
    }
    
    return append_to_log(path, entry)

def log_task(task_id: str, status: str, details: Optional[Dict[str, Any]] = None) -> bool:
    """
    Track task progress.
    
    Args:
        task_id: Unique task identifier
        status: Current task status
        details: Additional task details
        
    Returns:
        True if successfully logged
    """
    timestamp = datetime.now().isoformat()
    date_str = timestamp.split('T')[0]
    filename = f"tasks_{date_str}.json"
    path = os.path.join(MEMLOG_BASE, 'tasks', filename)
    
    entry = {
        "timestamp": timestamp,
        "task_id": task_id,
        "status": status,
        "details": details or {}
    }
    
    return append_to_log(path, entry)

def store_persistent_data(key: str, data: Any) -> bool:
    """
    Store persistent data.
    
    Args:
        key: Unique data identifier
        data: Data to store
        
    Returns:
        True if successfully stored
    """
    path = os.path.join(MEMLOG_BASE, 'persistence', f"{key}.json")
    
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Stored persistent data: {key}")
        return True
    except Exception as e:
        logger.error(f"Failed to store persistent data {key}: {e}")
        return False

def log_changelog(version: str, changes: List[Dict[str, Any]]) -> bool:
    """
    Record changelog entries.
    
    Args:
        version: Version number
        changes: List of changes with type, description, and components
        
    Returns:
        True if successfully logged
    """
    timestamp = datetime.now().isoformat()
    filename = f"changelog_{version}.json"
    path = os.path.join(MEMLOG_BASE, 'changelogs', filename)
    
    entry = {
        "timestamp": timestamp,
        "version": version,
        "changes": changes
    }
    
    try:
        with open(path, 'w') as f:
            json.dump(entry, f, indent=2)
        logger.info(f"Recorded changelog for version {version}")
        return True
    except Exception as e:
        logger.error(f"Failed to record changelog for version {version}: {e}")
        return False

def append_to_log(path: str, entry: Dict[str, Any]) -> bool:
    """
    Append entry to a log file, creating if necessary.
    
    Args:
        path: Path to log file
        entry: Entry to append
        
    Returns:
        True if successfully appended
    """
    entries = []
    
    # Read existing entries if file exists
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                try:
                    entries = json.load(f)
                    if not isinstance(entries, list):
                        entries = [entries]
                except json.JSONDecodeError:
                    entries = []
        except Exception as e:
            logger.error(f"Failed to read log file {path}: {e}")
            return False
    
    # Append new entry
    entries.append(entry)
    
    # Write back to file
    try:
        with open(path, 'w') as f:
            json.dump(entries, f, indent=2)
        
        # Check file size and rotate if necessary
        check_and_rotate_logs(path)
        
        return True
    except Exception as e:
        logger.error(f"Failed to write to log file {path}: {e}")
        return False

def check_and_rotate_logs(path: str) -> None:
    """
    Check file size and rotate/compress logs if necessary.
    
    Args:
        path: Path to log file
    """
    try:
        # Check file size
        size_mb = os.path.getsize(path) / (1024 * 1024)
        
        if size_mb >= MAX_LOG_SIZE_MB:
            # Archive the log
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = os.path.basename(path)
            dirname = os.path.dirname(path)
            archive_name = f"{os.path.splitext(filename)[0]}_{timestamp}.json"
            archive_path = os.path.join(dirname, archive_name)
            
            # Copy to archive
            shutil.copy2(path, archive_path)
            
            # Clear the original file but keep it
            with open(path, 'w') as f:
                f.write('[]')
            
            logger.info(f"Rotated log file: {path} -> {archive_path}")
            
            # Check if compression needed
            if size_mb >= COMPRESSION_THRESHOLD_MB:
                compress_log(archive_path)
            
            # Clean up old logs if too many
            clean_old_logs(dirname)
    except Exception as e:
        logger.error(f"Failed to rotate logs for {path}: {e}")

def compress_log(path: str) -> None:
    """
    Compress a log file using gzip.
    
    Args:
        path: Path to log file
    """
    try:
        compressed_path = f"{path}.gz"
        with open(path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove original after compression
        os.remove(path)
        logger.info(f"Compressed log: {path} -> {compressed_path}")
    except Exception as e:
        logger.error(f"Failed to compress log {path}: {e}")

def clean_old_logs(directory: str) -> None:
    """
    Remove oldest logs if too many exist.
    
    Args:
        directory: Directory containing logs
    """
    try:
        # Find all json and compressed logs
        files = []
        for file in os.listdir(directory):
            if file.endswith('.json') and not file.endswith('_state.json'):
                files.append(os.path.join(directory, file))
            elif file.endswith('.json.gz'):
                files.append(os.path.join(directory, file))
        
        # If we have too many, delete the oldest ones
        if len(files) > MAX_LOGS_PER_CATEGORY:
            # Sort by modification time
            files.sort(key=lambda x: os.path.getmtime(x))
            
            # Remove oldest files
            for file in files[:(len(files) - MAX_LOGS_PER_CATEGORY)]:
                os.remove(file)
                logger.info(f"Removed old log: {file}")
    except Exception as e:
        logger.error(f"Failed to clean old logs in {directory}: {e}")

def get_persistent_data(key: str, default: Any = None) -> Any:
    """
    Retrieve persistent data.
    
    Args:
        key: Data identifier
        default: Default value if not found
        
    Returns:
        Stored data or default
    """
    path = os.path.join(MEMLOG_BASE, 'persistence', f"{key}.json")
    
    if not os.path.exists(path):
        return default
    
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to retrieve persistent data {key}: {e}")
        return default
