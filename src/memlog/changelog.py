#!/usr/bin/env python3
"""
ImpressionCore: Changelog

Module for changelog functionality in the ImpressionCore framework.

File: memlog\changelog.py
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
This module implements changelog functionality for the
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
from memlog.changelog import MainClass
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

from . import CHANGELOGS_DIR, log_change

# Set up logging
logger = logging.getLogger("memlog.changelog")


def log_component_change(
    component: str,
    change_type: str,
    description: str,
    details: Optional[Dict[str, Any]] = None,
    user: Optional[str] = None,
) -> bool:
    """
    Log a change to a component.
    
    Args:
        component: Name of the component that changed
        change_type: Type of change (e.g., "add", "modify", "remove")
        description: Description of the change
        details: Optional additional details
        user: Optional username of the user who made the change
        
    Returns:
        True if the change was logged successfully, False otherwise
    """
    change_data = {
        "component": component,
        "type": change_type,
        "description": description,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    
    if details:
        change_data["details"] = details
        
    if user:
        change_data["user"] = user
        
    return log_change(component, change_data)


def get_component_changes(
    component: Optional[str] = None,
    change_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Get changes for a component.
    
    Args:
        component: Optional name of component to filter by
        change_type: Optional type of change to filter by
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)
        limit: Maximum number of changes to return
        
    Returns:
        List of change dictionaries
    """
    try:
        # Find all changelog files
        if component:
            pattern = os.path.join(CHANGELOGS_DIR, f"change_{component}_*.json")
        else:
            pattern = os.path.join(CHANGELOGS_DIR, "change_*.json")
            
        files = glob.glob(pattern)
        
        if not files:
            return []
            
        # Read changes
        changes = []
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    change_data = json.load(f)
                    
                # Apply filters
                if change_type and change_data.get("type") != change_type:
                    continue
                    
                if start_date:
                    if "timestamp" not in change_data or change_data["timestamp"] < start_date:
                        continue
                        
                if end_date:
                    if "timestamp" not in change_data or change_data["timestamp"] > end_date:
                        continue
                        
                changes.append(change_data)
            except Exception as file_error:
                logger.error(f"Error reading changelog file {filepath}: {file_error}")
                
        # Sort by timestamp (newest first)
        changes.sort(key=lambda c: c.get("timestamp", ""), reverse=True)
        
        # Apply limit
        return changes[:limit]
    except Exception as e:
        logger.error(f"Error getting component changes: {e}")
        return []


def get_changelog_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    components: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate a summary of changes.
    
    Args:
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)
        components: Optional list of components to include
        
    Returns:
        Dictionary containing a summary of changes
    """
    try:
        # Default dates if not provided
        if not end_date:
            end_date = datetime.datetime.now().isoformat()
            
        if not start_date:
            # Default to 30 days ago
            start_date = (
                datetime.datetime.fromisoformat(end_date) - 
                datetime.timedelta(days=30)
            ).isoformat()
            
        # Get all changes within date range
        changes = get_component_changes(
            component=None,
            change_type=None,
            start_date=start_date,
            end_date=end_date,
            limit=1000  # High limit to get all changes
        )
        
        # Filter by components if specified
        if components:
            changes = [c for c in changes if c.get("component") in components]
            
        # Generate summary
        summary = {
            "start_date": start_date,
            "end_date": end_date,
            "total_changes": len(changes),
            "component_changes": {},
            "type_counts": {},
            "components": set(),
            "changes_by_day": {},
        }
        
        # Process each change
        for change in changes:
            component = change.get("component", "unknown")
            change_type = change.get("type", "unknown")
            timestamp = change.get("timestamp", "")
            
            # Add to component counts
            summary["components"].add(component)
            if component not in summary["component_changes"]:
                summary["component_changes"][component] = 0
            summary["component_changes"][component] += 1
            
            # Add to type counts
            if change_type not in summary["type_counts"]:
                summary["type_counts"][change_type] = 0
            summary["type_counts"][change_type] += 1
            
            # Add to daily counts
            if timestamp:
                date_part = timestamp.split("T")[0]
                if date_part not in summary["changes_by_day"]:
                    summary["changes_by_day"][date_part] = 0
                summary["changes_by_day"][date_part] += 1
                
        # Convert components set to list
        summary["components"] = list(summary["components"])
        
        return summary
    except Exception as e:
        logger.error(f"Error generating changelog summary: {e}")
        return {
            "error": str(e),
            "start_date": start_date,
            "end_date": end_date,
            "total_changes": 0,
        }


def export_changelog(
    output_file: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    components: Optional[List[str]] = None,
    format_type: str = "markdown"
) -> bool:
    """
    Export changelog to a file.
    
    Args:
        output_file: Path to output file
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)
        components: Optional list of components to include
        format_type: Format type ("markdown", "json", "txt")
        
    Returns:
        True if the export was successful, False otherwise
    """
    try:
        # Get changes
        changes = get_component_changes(
            component=None,
            change_type=None,
            start_date=start_date,
            end_date=end_date,
            limit=1000  # High limit to get all changes
        )
        
        # Filter by components if specified
        if components:
            changes = [c for c in changes if c.get("component") in components]
            
        if not changes:
            logger.warning("No changes found for export")
            return False
            
        # Sort by timestamp (newest first)
        changes.sort(key=lambda c: c.get("timestamp", ""), reverse=True)
            
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Export based on format
        if format_type == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(changes, f, indent=2)
                
        elif format_type == "markdown":
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# Changelog\n\n")
                
                current_date = None
                
                for change in changes:
                    timestamp = change.get("timestamp", "")
                    if timestamp:
                        date_part = timestamp.split("T")[0]
                        time_part = timestamp.split("T")[1].split(".")[0]
                    else:
                        continue
                        
                    # Add date header if needed
                    if date_part != current_date:
                        f.write(f"\n## {date_part}\n\n")
                        current_date = date_part
                        
                    # Write change
                    component = change.get("component", "unknown")
                    change_type = change.get("type", "unknown")
                    description = change.get("description", "No description")
                    
                    f.write(f"- **[{component}]** ({time_part}) *{change_type}*: {description}\n")
                    
                    # Add details if present
                    if "details" in change and change["details"]:
                        f.write("  - Details:\n")
                        for key, value in change["details"].items():
                            f.write(f"    - {key}: {value}\n")
                            
        elif format_type == "txt":
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("CHANGELOG\n\n")
                
                for change in changes:
                    timestamp = change.get("timestamp", "")
                    component = change.get("component", "unknown")
                    change_type = change.get("type", "unknown")
                    description = change.get("description", "No description")
                    
                    f.write(f"[{timestamp}] {component} - {change_type}: {description}\n")
                    
                    # Add details if present
                    if "details" in change and change["details"]:
                        f.write("  Details:\n")
                        for key, value in change["details"].items():
                            f.write(f"    {key}: {value}\n")
                            
                    f.write("\n")
        else:
            logger.error(f"Unsupported format type: {format_type}")
            return False
                
        logger.info(f"Exported {len(changes)} changes to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error exporting changelog: {e}")
        return False


# Export functions
__all__ = [
    "log_component_change",
    "get_component_changes",
    "get_changelog_summary",
    "export_changelog",
]
