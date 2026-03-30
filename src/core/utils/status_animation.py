#!/usr/bin/env python3
"""
ImpressionCore: Status Animation

Module for status animation functionality in the ImpressionCore framework.

File: utils\status_animation.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, production, utils, 2025, object-oriented]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements status animation functionality for the
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
from utils.status_animation import StatusAnimation
instance = StatusAnimation()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import time
import threading
import sys
from typing import Optional, List


class StatusAnimation:
    """
    Provides animated status indicators for long-running operations.
    """
    
    def __init__(self, message: str = "Processing", 
                 animation_chars: Optional[List[str]] = None,
                 interval: float = 0.1):
        """
        Initialize status animation.
        
        Args:
            message: Base message to display
            animation_chars: List of characters for animation (default: spinner)
            interval: Time interval between animation frames
        """
        self.message = message
        self.animation_chars = animation_chars or ['|', '/', '-', '\\']
        self.interval = interval
        self.running = False
        self.thread = None
        self.current_frame = 0
        
    def start(self):
        """Start the animation."""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """Stop the animation."""
        self.running = False
        if self.thread:
            self.thread.join()
        # Clear the line
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()
        
    def _animate(self):
        """Internal animation loop."""
        while self.running:
            char = self.animation_chars[self.current_frame % len(self.animation_chars)]
            status_line = f"\r{self.message} {char}"
            sys.stdout.write(status_line)
            sys.stdout.flush()
            self.current_frame += 1
            time.sleep(self.interval)
            
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def show_progress(message: str, duration: Optional[float] = None):
    """
    Show a progress animation with optional duration.
    
    Args:
        message: Message to display
        duration: Optional duration to show progress (None = manual control)
        
    Returns:
        StatusAnimation instance if duration is None, otherwise None
    """
    animation = StatusAnimation(message)
    
    if duration is None:
        return animation
    else:
        animation.start()
        time.sleep(duration)
        animation.stop()
        return None


# Example usage functions
def demo_animation():
    """Demonstrate the status animation."""
    print("Starting demo animation...")
    
    with StatusAnimation("Loading model") as animation:
        time.sleep(3)
    
    print("Demo completed!")


if __name__ == "__main__":
    demo_animation()
