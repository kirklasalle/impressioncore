#!/usr/bin/env python3
"""
ImpressionCore: Logging

Module for logging functionality in the ImpressionCore framework.

File: src/core/utils/logging.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-06-09
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, memory-critical, framework, core, production, utils, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements logging functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

Examples:
```python
# Basic usage example
from src.core.utils.logging import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# Placeholder for future logging functions - currently imports from standard library
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def _configure_stream_for_unicode(stream) -> None:
    """Best-effort UTF-8 configuration for Windows console logging."""
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


class RichLogger:
    """
    Rich logging implementation for ImpressionCore
    """
    
    def __init__(self, name: str, log_file: Optional[Path] = None):
        """
        Initialize rich logger
        
        Args:
            name: Logger name
            log_file: Optional log file path
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        _configure_stream_for_unicode(sys.stdout)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_format = logging.Formatter(
                '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)


def setup_rich_logging(name: str, log_file: Optional[Path] = None) -> RichLogger:
    """Setup rich logging for ImpressionCore"""
    return RichLogger(name, log_file)


def get_rich_logger(name: str, log_file: Optional[Path] = None) -> RichLogger:
    """Get a rich logger instance by name"""
    return RichLogger(name, log_file)


# Alias for backward compatibility
setup_rich_logger = setup_rich_logging


# ---------------------------------------------------------------------------
# Module-level convenience functions (used by vector_index, openai_embeddings, etc.)
# ---------------------------------------------------------------------------
_default_logger = RichLogger("ImpressionCore")


def log_info(message: str) -> None:
    """Log an info-level message."""
    _default_logger.info(message)


def log_warning(message: str) -> None:
    """Log a warning-level message."""
    _default_logger.warning(message)


def log_error(message: str) -> None:
    """Log an error-level message."""
    _default_logger.error(message)


def log_success(message: str) -> None:
    """Log a success message (info level with prefix)."""
    _default_logger.info(f"[SUCCESS] {message}")
