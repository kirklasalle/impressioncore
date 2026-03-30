"""
OrbOS Logging System
=====================
Centralized logging configuration for the entire OrbOS system.

Features:
- File logging with rotation
- Console logging with colors
- Per-module loggers
- Debug log download endpoint
- Log level configuration
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Log directory
LOG_DIR = Path(os.getcwd()) / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file paths
MAIN_LOG = LOG_DIR / "orbcam.log"
DEBUG_LOG = LOG_DIR / "orbcam_debug.log"
ERROR_LOG = LOG_DIR / "orbcam_errors.log"


class ColorFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(level: str = "INFO", console: bool = True, file: bool = True) -> logging.Logger:
    """
    Configure the OrbOS logging system.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        console: Enable console output
        file: Enable file logging
    
    Returns:
        Root logger instance
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Formatter for files
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console formatter with colors
    console_formatter = ColorFormatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Main log file with rotation (10MB max, keep 5 backups)
    if file:
        file_handler = logging.handlers.RotatingFileHandler(
            MAIN_LOG,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Debug log (all levels)
        debug_handler = logging.handlers.RotatingFileHandler(
            DEBUG_LOG,
            maxBytes=20*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(file_formatter)
        root_logger.addHandler(debug_handler)
        
        # Error log (errors only)
        error_handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
    
    # Log startup
    root_logger.info(f"Logging initialized. Level: {level}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger for a specific module."""
    return logging.getLogger(name)


def get_all_logs() -> str:
    """Read and return all log content for debugging."""
    logs = []
    
    # Session header
    logs.append("=" * 60)
    logs.append(f"OrbOS Debug Logs - Generated: {datetime.now().isoformat()}")
    logs.append("=" * 60)
    
    # Main log
    if MAIN_LOG.exists():
        logs.append("\n### MAIN LOG ###\n")
        logs.append(MAIN_LOG.read_text(encoding='utf-8', errors='ignore')[-50000:])  # Last 50KB
    
    # Error log
    if ERROR_LOG.exists():
        logs.append("\n### ERROR LOG ###\n")
        logs.append(ERROR_LOG.read_text(encoding='utf-8', errors='ignore'))
    
    return "\n".join(logs)


def log_system_info():
    """Log system information for debugging."""
    logger = get_logger("orbcam.system")
    
    import platform
    logger.info(f"OS: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"Machine: {platform.machine()}")
    
    # Log USB status
    try:
        import usb.core
        logger.info("PyUSB: Available")
        
        # Check for Logitech devices
        dev = usb.core.find(idVendor=0x046d)
        if dev:
            logger.info(f"Logitech USB Device: Found (PID={dev.idProduct:04x})")
        else:
            logger.info("Logitech USB Device: Not found via PyUSB")
    except Exception as e:
        logger.warning(f"PyUSB: Not available - {e}")


# Auto-initialize on import
_initialized = False

def ensure_initialized():
    """Ensure logging is initialized."""
    global _initialized
    if not _initialized:
        setup_logging()
        _initialized = True


# Initialize on module load
ensure_initialized()
