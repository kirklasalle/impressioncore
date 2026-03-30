#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October 15, 2024
**Updated:** August 10, 2025
**Author:** Kirk LaSalle
**Tags:** #memory_management #multimodal #python #source_code #src/core/utils/rich_logging_fixed.py #testing
**Category:** Core Implementation
**Status:** Active
"""


# Placeholder for future logging functions - currently imports from standard library
import logging
import sys


class RichLogger:
    """
    Rich logging implementation for ImpressionCore
    """

    def __init__(self, name: str | None = None, level: str = "INFO"):
        """
        Initialize RichLogger

        Args:
            name: Logger name
            level: Logging level
        """
        self.name = name or __name__
        self.level = level.upper()
        self.logger = self._setup_logger()

    def _supports_unicode_stream(self, stream) -> bool:
        try:
            enc = getattr(stream, "encoding", None) or ""
            return "UTF" in enc.upper()
        except Exception:
            return False

    def _reconfigure_stdout_utf8(self) -> None:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    def _sanitize_for_console(self, message: str) -> str:
        if self._supports_unicode_stream(sys.stdout):
            return message
        return message.encode("ascii", errors="ignore").decode("ascii", errors="ignore")

    def _setup_logger(self):
        """Set up the underlying logger"""
        logger = logging.getLogger(self.name)
        self._reconfigure_stdout_utf8()
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, self.level, logging.INFO))
        return logger

    def info(self, message: str):
        """Log info message"""
        self.logger.info(self._sanitize_for_console(message))

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(self._sanitize_for_console(message))

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(self._sanitize_for_console(message))

    def error(self, message: str):
        """Log error message"""
        self.logger.error(self._sanitize_for_console(message))

    def critical(self, message: str):
        """Log critical message"""
        prefix = "❗ " if self._supports_unicode_stream(sys.stdout) else "[CRITICAL] "
        self.logger.critical(self._sanitize_for_console(f"{prefix}{message}"))


def setup_rich_logging(name: str | None = None, level: str = "INFO") -> RichLogger:
    """
    Set up rich logging for ImpressionCore

    Args:
        name: Logger name
        level: Logging level

    Returns:
        RichLogger instance
    """
    return RichLogger(name, level)


def setup_rich_logger(name: str | None = None, level: str = "INFO") -> RichLogger:
    """
    Set up rich logger (alias for setup_rich_logging)

    Args:
        name: Logger name
        level: Logging level

    Returns:
        RichLogger instance
    """
    return setup_rich_logging(name, level)


def get_rich_logger(name: str | None = None, level: str = "INFO") -> RichLogger:
    """
    Get rich logger instance

    Args:
        name: Logger name
        level: Logging level

    Returns:
        RichLogger instance
    """
    return RichLogger(name, level)


# Export main functions
__all__ = [
    'RichLogger',
    'get_rich_logger',
    'setup_rich_logger',
    'setup_rich_logging'
]
