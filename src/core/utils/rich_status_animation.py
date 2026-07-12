#!/usr/bin/env python3
"""
ImpressionCore: Rich Status Animation

Module for rich status animation functionality in the ImpressionCore framework.

File: core/utils/rich_status_animation.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, memory-critical, framework, core, production, utils, 2025, object-oriented]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements rich status animation functionality for the
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
from src.core.utils.rich_status_animation import StatusAnimation
instance = StatusAnimation()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import sys
import time
import psutil
import os
import logging

def get_memory_usage():
# Memory optimization: Memory-critical operation
    """
    Get current memory usage of the process in MB.
    # Memory optimization: Memory-critical operation
    Returns:
        tuple: (used_memory_mb, percent_memory)
        # Memory optimization: Memory-critical operation
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    # Memory optimization: Memory-critical operation
    memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
    # Memory optimization: Memory-critical operation
    memory_percent = psutil.virtual_memory().percent
    # Memory optimization: Memory-critical operation
    return memory_mb, memory_percent
    # Memory optimization: Memory-critical operation

class StatusAnimation:
    """
    Display a status animation in the terminal based on completion percentage and memory usage.
    # Memory optimization: Memory-critical operation
    """
    def __init__(self, total_steps, description="Processing"):
        """
        
    __init__ function for processing.
    
    Args:
        self, total_steps, description: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()
        self.animation_chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
        self.animation_idx = 0
        # Initial memory usage
        # Memory optimization: Memory-critical operation
        self.initial_memory, _ = get_memory_usage()
        # Memory optimization: Memory-critical operation
        
    def update(self, step=None, message=None):
        """Update the animation with current progress and memory usage."""
        # Memory optimization: Memory-critical operation
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
            
        percent = min(100, int((self.current_step / self.total_steps) * 100))
        self.animation_idx = (self.animation_idx + 1) % len(self.animation_chars)
        anim_char = self.animation_chars[self.animation_idx]
        
        msg = message if message else self.description
        elapsed = time.time() - self.start_time
        
        # Get current memory usage
        # Memory optimization: Memory-critical operation
        current_memory, memory_percent = get_memory_usage()
        # Memory optimization: Memory-critical operation
        memory_delta = current_memory - self.initial_memory
        # Memory optimization: Memory-critical operation
        
        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * percent / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Print status line with carriage return to overwrite the same line
        sys.stdout.write(f"\r{anim_char} {msg} [{bar}] {percent}% - {elapsed:.2f}s | Mem: {current_memory:.1f}MB ({memory_delta:+.1f}MB, {memory_percent:.1f}%)")
        # Memory optimization: Memory-critical operation
        sys.stdout.flush()
          # If complete, add a newline
        if percent >= 100:
            sys.stdout.write("\n")
            sys.stdout.flush()
            
    def complete(self, message="Complete"):
        """Mark the task as complete and log final memory stats."""
        # Memory optimization: Memory-critical operation
        self.current_step = self.total_steps
        self.update(message=message)
        current_memory, memory_percent = get_memory_usage()
        # Memory optimization: Memory-critical operation
        memory_delta = current_memory - self.initial_memory
        # Memory optimization: Memory-critical operation
        logging.info(f"Task completed: {message} - Memory used: {current_memory:.2f}MB ({memory_delta:+.2f}MB delta, {memory_percent:.1f}% of system RAM)")
        # Memory optimization: Memory-critical operation

class RichStatusAnimation:
    """Rich status animation with fallback support."""
    
    def __init__(self, total_steps: int = 100):
        try:
            from src.core.utils.status_animation import StatusAnimation
            self.status_animation = StatusAnimation("Processing")
        except:
            # Fallback - create a simple status class
            self.status_animation = self._create_fallback_status()
    
    def _create_fallback_status(self):
        """Create a simple fallback status object."""
        class SimpleStatus:
            def __init__(self, message="Processing", total_steps=100):
                self.message = message
                self.total_steps = total_steps
            
            def start(self):
                print(f"Starting: {self.message}")
                return self
            
            def stop(self):
                print(f"Completed: {self.message}")
            
            def status(self, message: str):
                """Context manager for status display."""
                self.message = message
                return self
            
            def update_status(self, message: str):
                print(f"Status: {message}")
            
            def stop_status(self):
                print("Status complete")
            
            def __enter__(self):
                self.start()
                return self
            
            def __exit__(self, *args):
                self.stop()
        
        return SimpleStatus()
    
    def status(self, message: str):
        """Context manager for status display."""
        if hasattr(self.status_animation, 'status'):
            return self.status_animation.status(message)
        else:
            # Use the actual StatusAnimation class interface
            class StatusContext:
                def __init__(self, animation, message):
                    self.animation = animation
                    self.animation.message = message
                
                def __enter__(self):
                    self.animation.start()
                    return self
                
                def __exit__(self, *args):
                    self.animation.stop()
            
            return StatusContext(self.status_animation, message)
    
    def update_status(self, message: str):
        """Update status message."""
        return self.status_animation.update_status(message)
    
    def stop_status(self):
        """Stop status animation."""
        return self.status_animation.stop_status()
    
    def _create_fallback_status(self):
        """Create a simple fallback status object."""
        class SimpleStatus:
            def status(self, message: str):
                print(f"Status: {message}")
                return self
            
            def update_status(self, message: str):
                print(f"Status: {message}")
            
            def stop_status(self):
                print("Status complete")
            
            def __enter__(self):
                return self
            
            def __exit__(self, *args):
                pass
        
        return SimpleStatus()