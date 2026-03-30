#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #python #source_code #src/core/utils/rich_logging_minimal.py
**Category:** Core Implementation
**Status:** Active
"""



import logging


def setup_rich_logging(name: str | None = None, level: str = "INFO") -> logging.Logger:
    """Set up rich logging with standard configuration."""
    return setup_rich_logger(name, level)

def setup_rich_logger(name: str | None = None, level: str = "INFO") -> logging.Logger:
    """Set up a rich logger instance."""
    if name is None:
        name = __name__

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    return logger

def get_rich_logger(name: str | None = None, level: str = "INFO") -> logging.Logger:
    """Get a rich logger instance."""
    return setup_rich_logger(name, level)

class RichLogger:
    """Rich logger wrapper class."""
    def __init__(self, name: str | None = None, level: str = "INFO"):
        self.logger = setup_rich_logger(name, level)

    def __getattr__(self, name):
        return getattr(self.logger, name)

# Export main functions
__all__ = [
    'RichLogger',
    'get_rich_logger',
    'setup_rich_logger',
    'setup_rich_logging'
]
