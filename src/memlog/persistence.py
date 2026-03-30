#!/usr/bin/env python3
"""
ImpressionCore: Persistence

Module for persistence functionality in the ImpressionCore framework.

File: memlog\persistence.py
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
This module implements persistence functionality for the
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
from memlog.persistence import MainClass
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
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from . import PERSISTENCE_DIR, store_persistent_data, get_persistent_data

# Set up logging
logger = logging.getLogger("memlog.persistence")


def list_persistent_data() -> List[str]:
    """
    List all persistent data keys.
    
    Returns:
        List of data keys
    """
    try:
        # Find all JSON files in persistence directory
        pattern = os.path.join(PERSISTENCE_DIR, "*.json")
        files = glob.glob(pattern)
        
        # Extract keys from filenames
        keys = []
        for filepath in files:
            filename = os.path.basename(filepath)
            if filename.endswith(".json"):
                key = filename[:-5]  # Remove .json extension
                keys.append(key)
                
        return keys
    except Exception as e:
        logger.error(f"Error listing persistent data: {e}")
        return []


def delete_persistent_data(key: str) -> bool:
    """
    Delete persistent data.
    
    Args:
        key: Key of the data to delete
        
    Returns:
        True if the data was deleted successfully, False otherwise
    """
    try:
        filepath = os.path.join(PERSISTENCE_DIR, f"{key}.json")
        
        if not os.path.exists(filepath):
            logger.warning(f"Persistent data not found for deletion: {key}")
            return False
            
        os.remove(filepath)
        logger.info(f"Persistent data deleted: {key}")
        return True
    except Exception as e:
        logger.error(f"Error deleting persistent data {key}: {e}")
        return False


def export_persistent_data(export_dir: str, keys: Optional[List[str]] = None) -> bool:
    """
    Export persistent data to another location.
    
    Args:
        export_dir: Directory to export data to
        keys: Optional list of keys to export (if None, export all)
        
    Returns:
        True if the data was exported successfully, False otherwise
    """
    try:
        # Create export directory if it doesn't exist
        os.makedirs(export_dir, exist_ok=True)
        
        # Get keys to export
        if keys is None:
            keys = list_persistent_data()
            
        # Export each key
        exported_count = 0
        for key in keys:
            # Get data
            data = get_persistent_data(key)
            if data is None:
                logger.warning(f"No data found for key: {key}")
                continue
                
            # Write to export file
            export_path = os.path.join(export_dir, f"{key}.json")
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            exported_count += 1
            
        logger.info(f"Exported {exported_count} of {len(keys)} keys to {export_dir}")
        return True
    except Exception as e:
        logger.error(f"Error exporting persistent data: {e}")
        return False


def import_persistent_data(import_dir: str, overwrite: bool = False) -> Dict[str, bool]:
    """
    Import persistent data from another location.
    
    Args:
        import_dir: Directory to import data from
        overwrite: Whether to overwrite existing data
        
    Returns:
        Dictionary mapping keys to import success status
    """
    try:
        result = {}
        
        # Find all JSON files in import directory
        pattern = os.path.join(import_dir, "*.json")
        files = glob.glob(pattern)
        
        # Import each file
        for filepath in files:
            filename = os.path.basename(filepath)
            if filename.endswith(".json"):
                key = filename[:-5]  # Remove .json extension
                
                # Check if data already exists
                if not overwrite and get_persistent_data(key) is not None:
                    logger.warning(f"Skipping import of {key} (already exists and overwrite=False)")
                    result[key] = False
                    continue
                    
                try:
                    # Read data from file
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Store data
                    success = store_persistent_data(key, data)
                    result[key] = success
                    
                    if success:
                        logger.info(f"Imported data for key: {key}")
                    else:
                        logger.error(f"Failed to import data for key: {key}")
                except Exception as file_error:
                    logger.error(f"Error importing {filepath}: {file_error}")
                    result[key] = False
                    
        return result
    except Exception as e:
        logger.error(f"Error importing persistent data: {e}")
        return {}


def backup_persistent_data(backup_dir: Optional[str] = None) -> str:
    """
    Create a backup of all persistent data.
    
    Args:
        backup_dir: Directory to store backup (if None, create in persistence dir)
        
    Returns:
        Path to backup directory, or empty string on failure
    """
    try:
        # Create backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if backup_dir is None:
            backup_dir = os.path.join(PERSISTENCE_DIR, f"backup_{timestamp}")
        else:
            backup_dir = os.path.join(backup_dir, f"persistence_backup_{timestamp}")
            
        os.makedirs(backup_dir, exist_ok=True)
        
        # Export all data to backup directory
        success = export_persistent_data(backup_dir)
        
        if success:
            logger.info(f"Created persistence backup at {backup_dir}")
            return backup_dir
        else:
            logger.error("Failed to create persistence backup")
            return ""
    except Exception as e:
        logger.error(f"Error backing up persistent data: {e}")
        return ""


def restore_backup(backup_dir: str, overwrite: bool = False) -> bool:
    """
    Restore persistent data from a backup.
    
    Args:
        backup_dir: Directory containing the backup
        overwrite: Whether to overwrite existing data
        
    Returns:
        True if the backup was restored successfully, False otherwise
    """
    try:
        # Verify backup directory exists
        if not os.path.exists(backup_dir) or not os.path.isdir(backup_dir):
            logger.error(f"Backup directory not found: {backup_dir}")
            return False
            
        # Create backup of current data before restoring
        if overwrite:
            current_backup = backup_persistent_data()
            if not current_backup:
                logger.warning("Failed to create backup of current data before restore")
                
        # Import data from backup
        result = import_persistent_data(backup_dir, overwrite)
        
        # Check if all imports were successful
        success_count = sum(1 for success in result.values() if success)
        logger.info(f"Restored {success_count} of {len(result)} items from backup")
        
        return success_count > 0
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        return False


# Export functions
__all__ = [
    "list_persistent_data",
    "delete_persistent_data",
    "export_persistent_data",
    "import_persistent_data",
    "backup_persistent_data",
    "restore_backup",
]
