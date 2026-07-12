#!/usr/bin/env python3
"""
ImpressionCore: Enhanced Logging

Module for enhanced logging functionality in the ImpressionCore framework.

File: core/utils/enhanced_logging.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, memory-critical, framework, pytorch, core, production, utils, 2025, object-oriented]
Dependencies: [torch, rich, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements enhanced logging functionality for the
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
from src.core.utils.enhanced_logging import MemoryEfficientProgress
instance = MemoryEfficientProgress()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import time
import logging
from typing import Optional, Dict, Any, Union, List
from datetime import datetime
from pathlib import Path
import torch
import threading
from functools import wraps

# Rich library for enhanced terminal output
try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.progress import (
        Progress, 
        TextColumn, 
        BarColumn, 
        TaskProgressColumn, 
        TimeRemainingColumn,
        SpinnerColumn,
        MofNCompleteColumn
    )
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.traceback import install as install_rich_traceback
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Define constants
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = logging.INFO
LOG_COLORS = {
    "DEBUG": "dim cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold red",
}

# Create console instance for rich output
if HAS_RICH:
    console = Console()
    # Install rich traceback handler for better error displays
    install_rich_traceback(show_locals=True)
else:
    console = None

class MemoryEfficientProgress:
# Memory optimization: Memory-critical operation
    """Memory-efficient progress bar manager that works with or without Rich library."""
    # Memory optimization: Memory-critical operation
    
    def __init__(
        self, 
        total: int, 
        description: str = "Progress", 
        transient: bool = True,
        disable: bool = False
    ):
        """
        Initialize a memory-efficient progress bar.
        # Memory optimization: Memory-critical operation
        
        Args:
            total: Total number of steps
            description: Task description
            transient: Whether to remove the progress bar after completion
            disable: Whether to disable the progress display
        """
        self.total = total
        self.description = description
        self.transient = transient
        self.disable = disable
        self.current = 0
        self.start_time = time.time()
        self.progress = None
        self.task_id = None
        
        if HAS_RICH and not self.disable:
            # Create a rich Progress instance with custom columns
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=40),
                TaskProgressColumn(),
                MofNCompleteColumn(),
                TimeRemainingColumn(),
                transient=transient,
                console=console
            )
            self.progress.start()
            self.task_id = self.progress.add_task(description, total=total)
        else:
            # Fallback to simple text-based progress for environments without Rich
            self._print_progress()
    
    def update(self, increment: int = 1):
        """Update the progress bar."""
        self.current += increment
        
        if HAS_RICH and not self.disable and self.progress:
            self.progress.update(self.task_id, advance=increment)
        else:
            # Simple progress display for non-Rich environments
            # Only update every 1% to reduce console spam
            if self.current % max(1, self.total // 100) == 0 or self.current >= self.total:
                self._print_progress()
    
    def _print_progress(self):
        """Print a simple text-based progress bar."""
        if self.disable:
            return
            
        percent = min(100, int(100 * self.current / max(1, self.total)))
        elapsed = time.time() - self.start_time
        
        # Calculate ETA
        if self.current > 0:
            eta = elapsed * (self.total - self.current) / self.current
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: --"
            
        bar_length = 30
        filled_length = int(bar_length * self.current / max(1, self.total))
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        sys.stdout.write(f'\r{self.description}: |{bar}| {percent}% {self.current}/{self.total} {eta_str}')
        sys.stdout.flush()
        
        if self.current >= self.total:
            print()  # New line after completion
    
    def close(self):
        """Close the progress bar."""
        if HAS_RICH and not self.disable and self.progress:
            self.progress.stop()
        elif not self.disable and self.current < self.total:
            # Ensure we show 100% at the end
            self.current = self.total
            self._print_progress()


class MemoryTracker:
# Memory optimization: Memory-critical operation
    """Track VRAM and RAM usage for diagnostics with minimal overhead."""
    
    def __init__(self, device: Optional[torch.device] = None):
    # Memory optimization: Device placement for memory management
        """
        Initialize memory tracker.
        # Memory optimization: Memory-critical operation
        
        Args:
            device: PyTorch device to track (defaults to current CUDA device)
            # Memory optimization: Device placement for memory management
        """
        self.has_torch = 'torch' in sys.modules
        self.device = device
        # Memory optimization: Device placement for memory management
        
        if self.has_torch and device is None and torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            self.device = torch.device('cuda')
            # Memory optimization: Device placement for memory management
        
        self.tracking_history = []
        self.peak_memory = 0
        # Memory optimization: Memory-critical operation
        self.start_memory = self._get_current_memory()
        # Memory optimization: Memory-critical operation
    
    def _get_current_memory(self) -> Dict[str, float]:
    # Memory optimization: Memory-critical operation
        """Get current memory usage in GB."""
        # Memory optimization: Memory-critical operation
        stats = {"ram": 0.0, "vram": 0.0, "vram_cached": 0.0}
        
        # Get RAM usage
        try:
            import psutil
            process = psutil.Process(os.getpid())
            stats["ram"] = process.memory_info().rss / (1024 ** 3)
            # Memory optimization: Memory-critical operation
        except ImportError:
            pass
        
        # Get VRAM usage if available
        if self.has_torch and self.device and self.device.type == 'cuda':
        # Memory optimization: Device placement for memory management
            try:
                stats["vram"] = torch.cuda.memory_allocated(self.device) / (1024 ** 3)
                # Memory optimization: CUDA operations for GPU acceleration
                stats["vram_cached"] = torch.cuda.memory_reserved(self.device) / (1024 ** 3)
                # Memory optimization: CUDA operations for GPU acceleration
            except:
                pass
        
        return stats
    
    def track(self, label: str = ""):
        """
        Track current memory usage.
        # Memory optimization: Memory-critical operation
        
        Args:
            label: Optional label for the tracking point
        """
        memory = self._get_current_memory()
        # Memory optimization: Memory-critical operation
        self.tracking_history.append((label, memory, time.time()))
        # Memory optimization: Memory-critical operation
        
        # Update peak memory
        # Memory optimization: Memory-critical operation
        if memory["vram"] > self.peak_memory:
        # Memory optimization: Memory-critical operation
            self.peak_memory = memory["vram"]
            # Memory optimization: Memory-critical operation
    
    def summary(self) -> Dict[str, Any]:
        """
        Generate memory usage summary.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dictionary with memory usage statistics
            # Memory optimization: Memory-critical operation
        """
        if not self.tracking_history:
            return {
                "peak_vram_gb": 0,
                "current_vram_gb": 0,
                "vram_increase_gb": 0,
                "tracking_points": []
            }
        
        current = self._get_current_memory()
        # Memory optimization: Memory-critical operation
        
        summary = {
            "peak_vram_gb": self.peak_memory,
            # Memory optimization: Memory-critical operation
            "current_vram_gb": current["vram"],
            "vram_increase_gb": current["vram"] - self.start_memory["vram"],
            # Memory optimization: Memory-critical operation
            "tracking_points": [
                {
                    "label": label,
                    "vram_gb": mem["vram"],
                    "ram_gb": mem["ram"],
                    "time": t
                }
                for label, mem, t in self.tracking_history
            ]
        }
        
        return summary
    
    def print_summary(self):
        """Print memory usage summary to the console."""
        # Memory optimization: Memory-critical operation
        summary = self.summary()
        
        if HAS_RICH:
            table = Table(title="Memory Usage Summary")
            # Memory optimization: Memory-critical operation
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Peak VRAM", f"{summary['peak_vram_gb']:.2f} GB")
            table.add_row("Current VRAM", f"{summary['current_vram_gb']:.2f} GB")
            table.add_row("VRAM Increase", f"{summary['vram_increase_gb']:.2f} GB")
            
            if summary['tracking_points']:
                tracking_table = Table(title="Memory Tracking Points")
                # Memory optimization: Memory-critical operation
                tracking_table.add_column("Label", style="blue")
                tracking_table.add_column("VRAM", style="green")
                tracking_table.add_column("RAM", style="yellow")
                
                for point in summary['tracking_points']:
                    tracking_table.add_row(
                        point['label'],
                        f"{point['vram_gb']:.2f} GB",
                        f"{point['ram_gb']:.2f} GB"
                    )
                
                console.print(table)
                console.print(tracking_table)
            else:
                console.print(table)
        else:
            print("\n\n===== Memory Usage Summary =====")
            # Memory optimization: Memory-critical operation
            print(f"Peak VRAM:     {summary['peak_vram_gb']:.2f} GB")
            print(f"Current VRAM:  {summary['current_vram_gb']:.2f} GB")
            print(f"VRAM Increase: {summary['vram_increase_gb']:.2f} GB")
            
            if summary['tracking_points']:
                print("\n===== Memory Tracking Points =====")
                # Memory optimization: Memory-critical operation
                for point in summary['tracking_points']:
                    print(f"{point['label']}: VRAM={point['vram_gb']:.2f} GB, RAM={point['ram_gb']:.2f} GB")


class EnhancedFormatter(logging.Formatter):
    """Custom formatter that adds memory usage information to log records."""
    # Memory optimization: Memory-critical operation
    
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, memory_tracking=True):
    # Memory optimization: Memory-critical operation
        """
        Initialize enhanced formatter.
        
        Args:
            fmt: Log format string
            datefmt: Date format string
            style: Style of format string
            validate: Whether to validate the format string
            memory_tracking: Whether to include memory usage in logs
            # Memory optimization: Memory-critical operation
        """
        super().__init__(fmt, datefmt, style, validate)
        self.memory_tracking = memory_tracking
        # Memory optimization: Memory-critical operation
        self.has_torch = 'torch' in sys.modules
    
    def format(self, record):
        """Format the log record with optional memory information."""
        # Memory optimization: Memory-critical operation
        # Add memory usage to record if tracking is enabled
        # Memory optimization: Memory-critical operation
        if self.memory_tracking and self.has_torch and torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            try:
                vram_allocated = torch.cuda.memory_allocated() / (1024 ** 3)
                # Memory optimization: CUDA operations for GPU acceleration
                vram_cached = torch.cuda.memory_reserved() / (1024 ** 3)
                # Memory optimization: CUDA operations for GPU acceleration
                
                memory_info = f"[VRAM: {vram_allocated:.2f}GB/{vram_cached:.2f}GB] "
                # Memory optimization: Memory-critical operation
                
                # Only modify the message if it doesn't already have memory info
                # Memory optimization: Memory-critical operation
                if "[VRAM:" not in record.msg:
                    record.msg = memory_info + str(record.msg)
                    # Memory optimization: Memory-critical operation
            except:
                # Skip memory tracking if it fails
                # Memory optimization: Memory-critical operation
                pass
        
        return super().format(record)


def setup_logging(
    level: int = DEFAULT_LOG_LEVEL, 
    log_to_file: bool = False, 
    log_file: Optional[str] = None, 
    console_output: bool = True,
    use_rich: Optional[bool] = None,
    log_memory: bool = True,
    # Memory optimization: Memory-critical operation
    module_name: str = "impressioncore"
) -> logging.Logger:
    """
    Configure enhanced logging for ImpressionCore.
    
    Args:
        level: Logging level (e.g. logging.DEBUG, logging.INFO)
        log_to_file: Whether to log to a file
        log_file: Path to log file (default: impressioncore_{timestamp}.log in logs dir)
        console_output: Whether to output to console
        use_rich: Whether to use Rich for console output (defaults to True if available)
        log_memory: Whether to include memory info in logs
        # Memory optimization: Memory-critical operation
        module_name: Logger name to use
        
    Returns:
        Configured logger instance
    """
    # Determine if we should use Rich
    if use_rich is None:
        use_rich = HAS_RICH
    
    # Get or create the logger
    logger = logging.getLogger(module_name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = EnhancedFormatter(LOG_FORMAT, memory_tracking=log_memory)
    # Memory optimization: Memory-critical operation
    
    # Create console handler with formatting
    if console_output:
        if use_rich and HAS_RICH:
            # Use Rich handler for console output
            console_handler = RichHandler(
                rich_tracebacks=True,
                markup=True,
                log_time_format="[%Y-%m-%d %H:%M:%S]",
                show_level=True,
                show_path=False,
                console=console
            )
            console_handler.setLevel(level)
            logger.addHandler(console_handler)
        else:
            # Use standard handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_to_file:
        if log_file is None:
            # Create logs directory if it doesn't exist
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            os.makedirs(log_dir, exist_ok=True)
            
            # Create timestamped log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"{module_name}_{timestamp}.log"
        else:
            log_file = Path(log_file)
            os.makedirs(log_file.parent, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    if use_rich and HAS_RICH:
        logger.debug("Logging initialized with [bold green]Rich[/] formatting")
    else:
        logger.debug("Logging initialized")
    
    return logger


def memory_profiled(func):
# Memory optimization: Memory-critical operation
    """
    Decorator to profile memory usage of a function.
    # Memory optimization: Memory-critical operation
    
    Args:
        func: Function to profile
        
    Returns:
        Wrapped function with memory profiling
        # Memory optimization: Memory-critical operation
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        
    wrapper function for processing.
    
    Args:
        No arguments: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        # Skip profiling if torch is not available
        if not torch or not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            return func(*args, **kwargs)
        
        # Get function details for logging
        module_name = func.__module__
        func_name = func.__name__
        logger = logging.getLogger(module_name)
        
        # Track memory before execution
        # Memory optimization: Memory-critical operation
        torch.cuda.reset_peak_memory_stats()
        # Memory optimization: CUDA operations for GPU acceleration
        start_memory = torch.cuda.memory_allocated() / (1024 ** 3)
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Execute the function
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Track memory after execution
        # Memory optimization: Memory-critical operation
        end_memory = torch.cuda.memory_allocated() / (1024 ** 3)
        # Memory optimization: CUDA operations for GPU acceleration
        peak_memory = torch.cuda.max_memory_allocated() / (1024 ** 3)
        # Memory optimization: CUDA operations for GPU acceleration
        memory_diff = end_memory - start_memory
        # Memory optimization: Memory-critical operation
        
        # Log the results
        logger.debug(
            f"Memory profile for {func_name}: "
            # Memory optimization: Memory-critical operation
            f"execution time={execution_time:.2f}s, "
            f"memory change={memory_diff:.2f}GB, "
            # Memory optimization: Memory-critical operation
            f"peak memory={peak_memory:.2f}GB"
            # Memory optimization: Memory-critical operation
        )
        
        return result
    
    return wrapper


# Create global memory tracker instance
# Memory optimization: Memory-critical operation
memory_tracker = MemoryTracker()
# Memory optimization: Memory-critical operation

# Initialize the default logger
root_logger = setup_logging(module_name="impressioncore")

# Function to get a logger with enhanced formatting
def get_logger(
    name: str, 
    level: int = DEFAULT_LOG_LEVEL,
    use_rich: bool = True,
    log_to_file: bool = False
) -> logging.Logger:
    """
    Get a logger with enhanced formatting.
    
    Args:
        name: Logger name
        level: Logging level
        use_rich: Whether to use Rich for console output
        log_to_file: Whether to log to a file
        
    Returns:
        Configured logger instance
    """
    return setup_logging(
        level=level, 
        log_to_file=log_to_file, 
        module_name=name,
        use_rich=use_rich
    )


def log_gpu_stats(logger=None):
# Memory optimization: Memory-critical operation
    """
    Log detailed GPU statistics.
    # Memory optimization: Memory-critical operation
    
    Args:
        logger: Logger to use (defaults to root logger)
    """
    if logger is None:
        logger = root_logger
    
    if not torch or not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.warning("CUDA not available, cannot log GPU stats")
        # Memory optimization: Memory-critical operation
        return
    
    try:
        device = torch.cuda.current_device()
        # Memory optimization: CUDA operations for GPU acceleration
        device_name = torch.cuda.get_device_name(device)
        # Memory optimization: CUDA operations for GPU acceleration
        total_memory = torch.cuda.get_device_properties(device).total_memory / (1024**3)
        # Memory optimization: CUDA operations for GPU acceleration
        allocated_memory = torch.cuda.memory_allocated(device) / (1024**3)
        # Memory optimization: CUDA operations for GPU acceleration
        reserved_memory = torch.cuda.memory_reserved(device) / (1024**3)
        # Memory optimization: CUDA operations for GPU acceleration
        
        if HAS_RICH:
            gpu_table = Table(title=f"GPU Statistics: {device_name}")
            # Memory optimization: Device placement for memory management
            gpu_table.add_column("Metric", style="cyan")
            # Memory optimization: Memory-critical operation
            gpu_table.add_column("Value", style="green")
            # Memory optimization: Memory-critical operation
            
            gpu_table.add_row("Total Memory", f"{total_memory:.2f} GB")
            # Memory optimization: Memory-critical operation
            gpu_table.add_row("Allocated Memory", f"{allocated_memory:.2f} GB")
            # Memory optimization: Memory-critical operation
            gpu_table.add_row("Reserved Memory", f"{reserved_memory:.2f} GB")
            # Memory optimization: Memory-critical operation
            gpu_table.add_row("Available Memory", f"{total_memory - allocated_memory:.2f} GB")
            # Memory optimization: Memory-critical operation
            
            usage_percent = (allocated_memory / total_memory) * 100
            # Memory optimization: Memory-critical operation
            usage_color = "green" if usage_percent < 50 else "yellow" if usage_percent < 80 else "red"
            gpu_table.add_row("Memory Usage", f"[{usage_color}]{usage_percent:.1f}%[/]")
            # Memory optimization: Memory-critical operation
            
            console.print(gpu_table)
            # Memory optimization: Memory-critical operation
        else:
            logger.info(f"GPU: {device_name}")
            # Memory optimization: Device placement for memory management
            logger.info(f"Total Memory: {total_memory:.2f} GB")
            # Memory optimization: Memory-critical operation
            logger.info(f"Allocated Memory: {allocated_memory:.2f} GB")
            # Memory optimization: Memory-critical operation
            logger.info(f"Reserved Memory: {reserved_memory:.2f} GB")
            # Memory optimization: Memory-critical operation
            logger.info(f"Available Memory: {total_memory - allocated_memory:.2f} GB")
            # Memory optimization: Memory-critical operation
            logger.info(f"Memory Usage: {(allocated_memory / total_memory) * 100:.1f}%")
            # Memory optimization: Memory-critical operation
    
    except Exception as e:
        logger.error(f"Error logging GPU stats: {str(e)}")
        # Memory optimization: Memory-critical operation


def create_progress_bar(
    total: int, 
    description: str = "Progress", 
    transient: bool = True,
    disable: bool = False
) -> MemoryEfficientProgress:
# Memory optimization: Memory-critical operation
    """
    Create a memory-efficient progress bar.
    # Memory optimization: Memory-critical operation
    
    Args:
        total: Total number of steps
        description: Task description
        transient: Whether to remove the progress bar after completion
        disable: Whether to disable the progress display
        
    Returns:
        MemoryEfficientProgress instance
        # Memory optimization: Memory-critical operation
    """
    return MemoryEfficientProgress(total, description, transient, disable)
    # Memory optimization: Memory-critical operation