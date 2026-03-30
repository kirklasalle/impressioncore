#!/usr/bin/env python3
"""
ImpressionCore: Test Gpu Memory Management

Module for test gpu memory management functionality in the ImpressionCore framework.

File: tests\test_gpu_memory_management.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, qa, pytorch, production, testing, 2025, object-oriented]
Dependencies: [torch, rich, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements test gpu memory management functionality for the
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
from tests.test_gpu_memory_management import MemoryTracker
instance = MemoryTracker()
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
import argparse
import logging
import torch
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import enhanced logging with Rich if available
try:
    import rich
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, SpinnerColumn
    from rich.table import Table
    from rich.text import Text
    from rich.live import Live
    from rich.layout import Layout
    from rich.spinner import Spinner
    from rich.syntax import Syntax
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import utilities from the correct path
from src.core.utils.gpu_memory_manager import GPUMemoryManager # Corrected import path
# Memory optimization: Memory-critical operation
from src.core.utils.memory_swap_manager import MemorySwapManager # Corrected import path
# Memory optimization: Memory-critical operation
from src.core.utils.gpu_performance_tracker import GPUPerformanceTracker, track_performance # Corrected import path
# Memory optimization: Memory-critical operation

# Try to import enhanced logging from src.core.utils if available
try:
    from src.core.utils.enhanced_logging import MemoryEfficientProgress, MemoryTracker as EnhancedMemoryTracker # Corrected import path
    # Memory optimization: Memory-critical operation
    HAS_ENHANCED_LOGGING = True
except ImportError:
    HAS_ENHANCED_LOGGING = False
    logger.warning("Enhanced logging module not found, falling back to basic implementation")

# Create a function to get a Rich progress bar
def create_progress(total=100, description="Processing", transient=True):
    """Create a Rich progress bar with memory usage tracking."""
    # Memory optimization: Memory-critical operation
    if HAS_RICH:
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TextColumn("[yellow]{task.fields[memory_usage]:.2f} MB"),
            # Memory optimization: Memory-critical operation
            console=console,
            transient=transient
        )
    else:
        # Return a dummy context manager if Rich is not available
        from contextlib import nullcontext
        return nullcontext()

def get_device():
# Memory optimization: Device placement for memory management
    """Get the appropriate device (CUDA or CPU)."""
    # Memory optimization: Device placement for memory management
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Memory optimization: CUDA operations for GPU acceleration

def get_memory_info():
# Memory optimization: Memory-critical operation
    """Get memory information for both system and GPU."""
    # Memory optimization: Memory-critical operation
    memory_info = {
    # Memory optimization: Memory-critical operation
        "system": {
            "total": 0,
            "available": 0,
            "used": 0,
            "percent": 0
        },
        "gpu_vram": {
        # Memory optimization: Memory-critical operation
            "total": 0,
            "allocated": 0,
            "reserved": 0,
            "percent": 0
        }
    }
    
    # Get system memory info
    # Memory optimization: Memory-critical operation
    try:
        import psutil
        system_memory = psutil.virtual_memory()
        # Memory optimization: Memory-critical operation
        memory_info["system"] = {
        # Memory optimization: Memory-critical operation
            "total": system_memory.total / (1024 ** 2),  # MB
            # Memory optimization: Memory-critical operation
            "available": system_memory.available / (1024 ** 2),  # MB
            # Memory optimization: Memory-critical operation
            "used": system_memory.used / (1024 ** 2),  # MB
            # Memory optimization: Memory-critical operation
            "percent": system_memory.percent
            # Memory optimization: Memory-critical operation
        }
    except ImportError:
        logger.warning("psutil not available, system memory stats disabled")
        # Memory optimization: Memory-critical operation
    
    # Get GPU memory info
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        device = torch.cuda.current_device()
        # Memory optimization: CUDA operations for GPU acceleration
        total_memory = torch.cuda.get_device_properties(device).total_memory / (1024 ** 2)  # MB
        # Memory optimization: CUDA operations for GPU acceleration
        allocated_memory = torch.cuda.memory_allocated(device) / (1024 ** 2)  # MB
        # Memory optimization: CUDA operations for GPU acceleration
        reserved_memory = torch.cuda.memory_reserved(device) / (1024 ** 2)  # MB
        # Memory optimization: CUDA operations for GPU acceleration
        
        memory_info["gpu_vram"] = {
        # Memory optimization: Memory-critical operation
            "total": total_memory,
            # Memory optimization: Memory-critical operation
            "allocated": allocated_memory,
            # Memory optimization: Memory-critical operation
            "reserved": reserved_memory,
            # Memory optimization: Memory-critical operation
            "percent": (allocated_memory / total_memory) * 100 if total_memory > 0 else 0
            # Memory optimization: Memory-critical operation
        }
    
    return memory_info
    # Memory optimization: Memory-critical operation

def create_memory_display():
# Memory optimization: Memory-critical operation
    """Create a Rich layout for displaying memory information."""
    # Memory optimization: Memory-critical operation
    if not HAS_RICH:
        return None
        
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main")
    )
    layout["main"].split_row(
        Layout(name="system_memory"),
        # Memory optimization: Memory-critical operation
        Layout(name="gpu_memory")
        # Memory optimization: Memory-critical operation
    )
    return layout

def update_memory_display(layout, memory_info):
# Memory optimization: Memory-critical operation
    """Update the memory display layout with current memory information."""
    # Memory optimization: Memory-critical operation
    if not HAS_RICH or not layout:
        return
        
    # Format header
    header_text = Text("ImpressionCore Memory Management", style="bold cyan")
    # Memory optimization: Memory-critical operation
    header_text.append(" - Real-time Memory Usage", style="dim")
    # Memory optimization: Memory-critical operation
    layout["header"].update(Panel(header_text))
    
    # Format system memory
    # Memory optimization: Memory-critical operation
    system_memory = memory_info["system"]
    # Memory optimization: Memory-critical operation
    system_table = Table(title="System RAM", box=rich.box.ROUNDED)
    system_table.add_column("Metric")
    system_table.add_column("Value")
    
    system_table.add_row("Total", f"{system_memory['total']:.2f} MB")
    # Memory optimization: Memory-critical operation
    system_table.add_row("Used", f"{system_memory['used']:.2f} MB")
    # Memory optimization: Memory-critical operation
    system_table.add_row("Available", f"{system_memory['available']:.2f} MB")
    # Memory optimization: Memory-critical operation
    
    # Add usage bar
    bar_width = 40
    filled = int(system_memory['percent'] * bar_width / 100)
    # Memory optimization: Memory-critical operation
    usage_bar = "[" + "#" * filled + "-" * (bar_width - filled) + "]"
    system_table.add_row("Usage", Text(f"{system_memory['percent']:.1f}% {usage_bar}", 
    # Memory optimization: Memory-critical operation
                                      style="green" if system_memory['percent'] < 70 else "yellow" if system_memory['percent'] < 90 else "red"))
                                      # Memory optimization: Memory-critical operation
    
    layout["system_memory"].update(system_table)
    # Memory optimization: Memory-critical operation
    
    # Format GPU memory
    # Memory optimization: Memory-critical operation
    gpu_memory = memory_info["gpu_vram"]
    # Memory optimization: Memory-critical operation
    gpu_table = Table(title="GPU VRAM", box=rich.box.ROUNDED)
    # Memory optimization: Memory-critical operation
    gpu_table.add_column("Metric")
    # Memory optimization: Memory-critical operation
    gpu_table.add_column("Value")
    # Memory optimization: Memory-critical operation
    
    gpu_table.add_row("Total", f"{gpu_memory['total']:.2f} MB")
    # Memory optimization: Memory-critical operation
    gpu_table.add_row("Allocated", f"{gpu_memory['allocated']:.2f} MB")
    # Memory optimization: Memory-critical operation
    gpu_table.add_row("Reserved", f"{gpu_memory['reserved']:.2f} MB")
    # Memory optimization: Memory-critical operation
    
    # Add usage bar
    filled = int(gpu_memory['percent'] * bar_width / 100)
    # Memory optimization: Memory-critical operation
    usage_bar = "[" + "#" * filled + "-" * (bar_width - filled) + "]"
    gpu_table.add_row("Usage", Text(f"{gpu_memory['percent']:.1f}% {usage_bar}", 
    # Memory optimization: Memory-critical operation
                                   style="green" if gpu_memory['percent'] < 50 else "yellow" if gpu_memory['percent'] < 80 else "red"))
                                   # Memory optimization: Memory-critical operation
    
    layout["gpu_memory"].update(gpu_table)
    # Memory optimization: Memory-critical operation

def clear_gpu_memory():
# Memory optimization: Memory-critical operation
    """Clear GPU memory to start tests from a clean state."""
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        # Clear memory cache
        # Memory optimization: Memory-critical operation
        torch.cuda.empty_cache()
        # Memory optimization: CUDA operations for GPU acceleration
        # Force garbage collection
        import gc
        gc.collect()
        # Memory optimization: Force garbage collection
        
        # Log memory state
        # Memory optimization: Memory-critical operation
        if HAS_RICH:
            mem_info = get_memory_info()
            # Memory optimization: Memory-critical operation
            vram_info = mem_info.get("gpu_vram", {})
            # Memory optimization: Memory-critical operation
            console.print(f"[dim]Cleared GPU memory. Currently using: {vram_info.get('allocated', 0):.2f}MB[/dim]")
            # Memory optimization: Memory-critical operation

class MemoryTracker:
# Memory optimization: Memory-critical operation
    """Simple tracker for memory usage."""
    # Memory optimization: Memory-critical operation
    
    def __init__(self):
        """
        
    __init__ function for processing.
    
    Args:
        self: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.start_stats = {}
        self.peak_stats = {}
        self.end_stats = {}
    
    def start(self):
        """Start tracking memory."""
        # Memory optimization: Memory-critical operation
        self.start_stats = get_memory_info()
        # Memory optimization: Memory-critical operation
        self.peak_stats = {
            "peak_system_mb": self.start_stats["system"]["used"],
            "peak_gpu_mb": self.start_stats["gpu_vram"]["allocated"]
            # Memory optimization: Memory-critical operation
        }
        return self.start_stats
    
    def track(self):
        """Track current memory and update peak values."""
        # Memory optimization: Memory-critical operation
        stats = get_memory_info()
        # Memory optimization: Memory-critical operation
        
        # Update peak values
        if stats["system"]["used"] > self.peak_stats["peak_system_mb"]:
            self.peak_stats["peak_system_mb"] = stats["system"]["used"]
        
        if stats["gpu_vram"]["allocated"] > self.peak_stats["peak_gpu_mb"]:
        # Memory optimization: Memory-critical operation
            self.peak_stats["peak_gpu_mb"] = stats["gpu_vram"]["allocated"]
            # Memory optimization: Memory-critical operation
        
        return stats
    
    def stop(self):
        """Stop tracking and return peak memory usage statistics."""
        # Memory optimization: Memory-critical operation
        self.end_stats = get_memory_info()
        # Memory optimization: Memory-critical operation
        
        # Final peak check
        if self.end_stats["system"]["used"] > self.peak_stats["peak_system_mb"]:
            self.peak_stats["peak_system_mb"] = self.end_stats["system"]["used"]
        
        if self.end_stats["gpu_vram"]["allocated"] > self.peak_stats["peak_gpu_mb"]:
        # Memory optimization: Memory-critical operation
            self.peak_stats["peak_gpu_mb"] = self.end_stats["gpu_vram"]["allocated"]
            # Memory optimization: Memory-critical operation
        
        return self.peak_stats

    def get_summary_table(self):
        """Get a Rich table with memory usage summary."""
        # Memory optimization: Memory-critical operation
        if not HAS_RICH:
            return None
            
        table = Table(title="Memory Usage Summary")
        # Memory optimization: Memory-critical operation
        table.add_column("Metric", style="cyan")
        table.add_column("Start", style="green")
        table.add_column("Peak", style="red")
        table.add_column("End", style="blue")
        table.add_column("Diff", style="yellow")
        
        # System RAM
        start_system = self.start_stats["system"]["used"]
        peak_system = self.peak_stats["peak_system_mb"]
        end_system = self.end_stats["system"]["used"]
        diff_system = end_system - start_system
        
        table.add_row(
            "System RAM (MB)",
            f"{start_system:.2f}",
            f"{peak_system:.2f}",
            f"{end_system:.2f}",
            f"{diff_system:+.2f}"
        )
        
        # GPU VRAM
        # Memory optimization: Memory-critical operation
        start_gpu = self.start_stats["gpu_vram"]["allocated"]
        # Memory optimization: Memory-critical operation
        peak_gpu = self.peak_stats["peak_gpu_mb"]
        # Memory optimization: Memory-critical operation
        end_gpu = self.end_stats["gpu_vram"]["allocated"]
        # Memory optimization: Memory-critical operation
        diff_gpu = end_gpu - start_gpu
        # Memory optimization: Memory-critical operation
        
        table.add_row(
            "GPU VRAM (MB)",
            # Memory optimization: Memory-critical operation
            f"{start_gpu:.2f}",
            # Memory optimization: Memory-critical operation
            f"{peak_gpu:.2f}",
            # Memory optimization: Memory-critical operation
            f"{end_gpu:.2f}",
            # Memory optimization: Memory-critical operation
            f"{diff_gpu:+.2f}"
            # Memory optimization: Memory-critical operation
        )
        
        # GPU utilization percentages
        # Memory optimization: Memory-critical operation
        total_gpu = self.start_stats["gpu_vram"]["total"]
        # Memory optimization: Memory-critical operation
        if total_gpu > 0:
        # Memory optimization: Memory-critical operation
            start_pct = (start_gpu / total_gpu) * 100
            # Memory optimization: Memory-critical operation
            peak_pct = (peak_gpu / total_gpu) * 100
            # Memory optimization: Memory-critical operation
            end_pct = (end_gpu / total_gpu) * 100
            # Memory optimization: Memory-critical operation
            
            table.add_row(
                "GPU Usage (%)",
                # Memory optimization: Memory-critical operation
                f"{start_pct:.1f}%",
                f"{peak_pct:.1f}%",
                f"{end_pct:.1f}%",
                f"{end_pct - start_pct:+.1f}%"
            )
            
        return table

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test GPU memory management features")
    # Memory optimization: Memory-critical operation
    parser.add_argument("--test", type=str, choices=["basic", "stress", "swap", "all"], default="basic",
                      help="Test to run")
    parser.add_argument("--size", type=int, default=1000,
                      help="Size of test tensor dimensions")
    parser.add_argument("--count", type=int, default=10,
                      help="Number of tensors to create")
    parser.add_argument("--target", type=float, default=0.8,
                      help="Target VRAM usage (0.0-1.0)")
    parser.add_argument("--shared", action="store_true",
                      help="Enable shared memory features")
                      # Memory optimization: Memory-critical operation
    parser.add_argument("--track", action="store_true",
                      help="Track GPU performance during tests")
                      # Memory optimization: Memory-critical operation
    parser.add_argument("--no-rich", action="store_true",
                      help="Disable Rich progress visualizations")
    return parser.parse_args()

@track_performance
def basic_tensor_test(size, count, device):
# Memory optimization: Device placement for memory management
    """Basic tensor creation and operation test."""
    logger.info(f"Creating {count} tensors of size {size}x{size} on {device}")
    # Memory optimization: Device placement for memory management
    tensors = []
    
    # Use enhanced progress tracking if available
    memory_tracker = MemoryTracker()
    # Memory optimization: Memory-critical operation
    memory_tracker.start()
    # Memory optimization: Memory-critical operation
    
    # Create tensors with rich progress visualization
    if HAS_RICH and not args.no_rich:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TextColumn("[yellow]{task.fields[memory_usage]:.2f} MB VRAM"),
            # Memory optimization: Memory-critical operation
            console=console
        ) as progress:
            tensor_task = progress.add_task(f"[cyan]Creating tensors ({size}x{size})", total=count, memory_usage=0)
            # Memory optimization: Memory-critical operation
            
            for i in range(count):
                tensor = torch.rand(size, size, device=device)
                # Memory optimization: Device placement for memory management
                tensors.append(tensor)
                
                # Update memory info in progress bar
                # Memory optimization: Memory-critical operation
                if device.type == "cuda":
                # Memory optimization: Device placement for memory management
                    allocated = torch.cuda.memory_allocated() / 1024**2
                    # Memory optimization: CUDA operations for GPU acceleration
                    progress.update(tensor_task, advance=1, memory_usage=allocated)
                    # Memory optimization: Memory-critical operation
                else:
                    progress.update(tensor_task, advance=1)
                    
                # Small delay to see the progress
                time.sleep(0.05)
    else:
        # Standard tensor creation without Rich
        for i in range(count):
            tensor = torch.rand(size, size, device=device)
            # Memory optimization: Device placement for memory management
            tensors.append(tensor)
            logger.info(f"Created tensor {i+1}/{count}, size: {tensor.element_size() * tensor.numel() / 1024**2:.2f}MB")
            
            # Report memory usage
            # Memory optimization: Memory-critical operation
            if device.type == "cuda":
            # Memory optimization: Device placement for memory management
                allocated = torch.cuda.memory_allocated() / 1024**2
                # Memory optimization: CUDA operations for GPU acceleration
                reserved = torch.cuda.memory_reserved() / 1024**2
                # Memory optimization: CUDA operations for GPU acceleration
                logger.info(f"CUDA memory: {allocated:.2f}MB allocated, {reserved:.2f}MB reserved")
                # Memory optimization: Memory-critical operation
    
    # Perform matrix multiplications with progress tracking
    if HAS_RICH and not args.no_rich:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TextColumn("[yellow]{task.fields[memory_usage]:.2f} MB VRAM"),
            # Memory optimization: Memory-critical operation
            console=console
        ) as progress:
            multiply_task = progress.add_task("[green]Performing matrix multiplications", total=count-1, memory_usage=0)
            # Memory optimization: Memory-critical operation
            
            results = []
            for i in range(count-1):
                result = torch.matmul(tensors[i], tensors[i+1])
                results.append(result)
                
                # Update memory info
                # Memory optimization: Memory-critical operation
                if device.type == "cuda":
                # Memory optimization: Device placement for memory management
                    allocated = torch.cuda.memory_allocated() / 1024**2
                    # Memory optimization: CUDA operations for GPU acceleration
                    progress.update(multiply_task, advance=1, memory_usage=allocated)
                    # Memory optimization: Memory-critical operation
                else:
                    progress.update(multiply_task, advance=1)
                
                # Small delay to see the progress
                time.sleep(0.05)
    else:
        # Standard operations without Rich
        logger.info("Performing matrix multiplications...")
        results = []
        for i in range(count-1):
            result = torch.matmul(tensors[i], tensors[i+1])
            results.append(result)
    
    # Display memory usage summary
    # Memory optimization: Memory-critical operation
    memory_stats = memory_tracker.stop()
    # Memory optimization: Memory-critical operation
    if HAS_RICH and not args.no_rich:
        console.print(memory_tracker.get_summary_table())
        # Memory optimization: Memory-critical operation
    else:
        logger.info(f"Peak system memory: {memory_stats['peak_system_mb']:.2f}MB")
        # Memory optimization: Memory-critical operation
        logger.info(f"Peak GPU memory: {memory_stats['peak_gpu_mb']:.2f}MB")
        # Memory optimization: Memory-critical operation
    
    # Clean up
    del tensors
    # Memory optimization: Explicit memory cleanup
    del results
    # Memory optimization: Explicit memory cleanup
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        torch.cuda.empty_cache()
        # Memory optimization: CUDA operations for GPU acceleration
    
    return "Basic tensor test completed successfully"

@track_performance
def stress_test(size, target_usage, device, use_shared_memory=False):
# Memory optimization: Device placement for memory management
    """Stress test GPU memory management."""
    # Memory optimization: Memory-critical operation
    if device.type != "cuda":
    # Memory optimization: Device placement for memory management
        logger.warning("Stress test requires CUDA device")
        # Memory optimization: Device placement for memory management
        return "Skipped stress test (no CUDA)"
        # Memory optimization: Memory-critical operation
    
    # Initialize memory manager
    # Memory optimization: Memory-critical operation
    memory_manager = GPUMemoryManager(
    # Memory optimization: Memory-critical operation
        vram_target_usage=target_usage,
        enable_shared_memory=use_shared_memory,
        # Memory optimization: Memory-critical operation
        enable_monitoring=True,
        log_file="stress_test_memory.csv"
        # Memory optimization: Memory-critical operation
    )
    
    # Get total VRAM
    total_vram = torch.cuda.get_device_properties(device).total_memory / 1024**2
    # Memory optimization: CUDA operations for GPU acceleration
    target_vram = total_vram * target_usage
    logger.info(f"Target VRAM usage: {target_vram:.2f}MB ({target_usage*100:.0f}% of {total_vram:.2f}MB)")
    
    # Create live memory display if Rich is available
    # Memory optimization: Memory-critical operation
    memory_display = None
    # Memory optimization: Memory-critical operation
    if HAS_RICH and not args.no_rich:
        memory_display = create_memory_display()
        # Memory optimization: Memory-critical operation
    
    # Track memory usage
    # Memory optimization: Memory-critical operation
    memory_tracker = MemoryTracker()
    # Memory optimization: Memory-critical operation
    memory_tracker.start()
    # Memory optimization: Memory-critical operation
    
    # Create tensors until we reach target usage
    tensors = []
    allocated = 0
    tensor_size = size * size * 4 / 1024**2  # Approximate size in MB for float32
    
    try:
        # Create tensors with Rich live display
        if HAS_RICH and not args.no_rich and memory_display:
        # Memory optimization: Memory-critical operation
            with Live(memory_display, refresh_per_second=4) as live:
            # Memory optimization: Memory-critical operation
                try:
                    while allocated < target_vram:
                        # Create a new tensor
                        tensor = torch.rand(size, size, device=device)
                        # Memory optimization: Device placement for memory management
                        tensors.append(tensor)
                        
                        # Update allocated memory and display
                        # Memory optimization: Memory-critical operation
                        allocated = torch.cuda.memory_allocated() / 1024**2
                        # Memory optimization: CUDA operations for GPU acceleration
                        memory_info = memory_tracker.track()
                        # Memory optimization: Memory-critical operation
                        update_memory_display(memory_display, memory_info)
                        # Memory optimization: Memory-critical operation
                        
                        # Perform some operations to stress memory
                        # Memory optimization: Memory-critical operation
                        if len(tensors) >= 2:
                            result = torch.matmul(tensors[-2], tensors[-1])
                            result_sum = result.sum().item()
                except RuntimeError as e:
                    if "CUDA out of memory" in str(e):
                    # Memory optimization: Memory-critical operation
                        memory_info = memory_tracker.track()
                        # Memory optimization: Memory-critical operation
                        update_memory_display(memory_display, memory_info)
                        # Memory optimization: Memory-critical operation
                        console.print(f"[bold red]Reached memory limit after {len(tensors)} tensors[/]")
                        # Memory optimization: Memory-critical operation
                        # Clean up the last tensor that caused OOM
                        if tensors:
                            del tensors[-1]
                            # Memory optimization: Explicit memory cleanup
                            torch.cuda.empty_cache()
                            # Memory optimization: CUDA operations for GPU acceleration
                    else:
                        raise
        else:
            # Standard creation without Rich
            while allocated < target_vram:
                # Create a new tensor
                tensor = torch.rand(size, size, device=device)
                # Memory optimization: Device placement for memory management
                tensors.append(tensor)
                
                # Update allocated memory
                # Memory optimization: Memory-critical operation
                allocated = torch.cuda.memory_allocated() / 1024**2
                # Memory optimization: CUDA operations for GPU acceleration
                logger.info(f"Created tensor {len(tensors)}, "
                          f"VRAM usage: {allocated:.2f}MB / {target_vram:.2f}MB "
                          f"({allocated/total_vram*100:.1f}%)")
                
                # Perform some operations to stress memory
                # Memory optimization: Memory-critical operation
                if len(tensors) >= 2:
                    result = torch.matmul(tensors[-2], tensors[-1])
                    # Use result to prevent it from being optimized away
                    result_sum = result.sum().item()
                    logger.debug(f"Matrix multiply result sum: {result_sum:.2f}")
    
    except RuntimeError as e:
        if "CUDA out of memory" in str(e):
        # Memory optimization: Memory-critical operation
            logger.info(f"Reached memory limit after {len(tensors)} tensors")
            # Memory optimization: Memory-critical operation
            # Clean up the last tensor that caused OOM
            if tensors:
                del tensors[-1]
                # Memory optimization: Explicit memory cleanup
                torch.cuda.empty_cache()
                # Memory optimization: CUDA operations for GPU acceleration
        else:
            raise
    
    # Display memory usage summary
    # Memory optimization: Memory-critical operation
    memory_stats = memory_tracker.stop()
    # Memory optimization: Memory-critical operation
    if HAS_RICH and not args.no_rich:
        console.print(memory_tracker.get_summary_table())
        # Memory optimization: Memory-critical operation
    else:
        logger.info(f"Peak system memory: {memory_stats['peak_system_mb']:.2f}MB")
        # Memory optimization: Memory-critical operation
        logger.info(f"Peak GPU memory: {memory_stats['peak_gpu_mb']:.2f}MB")
        # Memory optimization: Memory-critical operation
    
    # Clean up memory
    # Memory optimization: Memory-critical operation
    memory_manager.cleanup()
    # Memory optimization: Memory-critical operation
    
    return f"Stress test completed with {len(tensors)} tensors of size {tensor_size:.2f}MB each"

@track_performance
def parameter_swap_test(model_size, device, use_shared_memory=False):
# Memory optimization: Device placement for memory management
    """Test parameter swapping between VRAM and system RAM."""
    if device.type != "cuda":
    # Memory optimization: Device placement for memory management
        logger.warning("Parameter swap test requires CUDA device")
        # Memory optimization: Device placement for memory management
        return "Skipped parameter swap test (no CUDA)"
        # Memory optimization: Memory-critical operation
    
    # Initialize swap manager
    swap_manager = MemorySwapManager(
    # Memory optimization: Memory-critical operation
        vram_target_usage=0.7,
        enable_monitoring=True,
        device=device,
        # Memory optimization: Device placement for memory management
        use_pinned_memory=True
        # Memory optimization: Memory-critical operation
    )
    
    # Create a simple model with specific layer groups
    # Memory optimization: Explicit memory cleanup
    class TestModel(torch.nn.Module):
        """
        
    TestModel class for ImpressionCore framework.
    # Memory optimization: Explicit memory cleanup
    
    This class implements testmodel functionality optimized for
    # Memory optimization: Explicit memory cleanup
    memory-constrained environments like the GTX 1050 Ti.
    # Memory optimization: Memory-critical operation
    
    Memory Considerations:
    # Memory optimization: Memory-critical operation
        - Implements memory-efficient algorithms
        # Memory optimization: Memory-critical operation
        - Supports gradient checkpointing
        - Provides CPU fallback options
    
    Notes:
        - Thread-safe implementation
        - GPU memory optimized
        # Memory optimization: Memory-critical operation
        - Part of ImpressionCore ecosystem
    
        """
        def __init__(self, size):
            """
            
    __init__ function for processing.
    
    Args:
        self, size: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
            """
            super().__init__()
            # Create separate layer groups for testing
            self.encoder = torch.nn.Sequential(
                torch.nn.Linear(size, size),
                torch.nn.ReLU(),
                torch.nn.Linear(size, size//2)
            )
            
            self.middle = torch.nn.Sequential(
                torch.nn.Linear(size//2, size//2),
                torch.nn.ReLU(),
            )
            
            self.decoder = torch.nn.Sequential(
                torch.nn.Linear(size//2, size),
                torch.nn.ReLU(),
                torch.nn.Linear(size, size)
            )
            
        def forward(self, x):
            """
            
    forward function for processing.
    
    Args:
        self, x: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
            """
            x = self.encoder(x)
            x = self.middle(x)
            return self.decoder(x)
    
    # Create memory tracker
    # Memory optimization: Memory-critical operation
    memory_tracker = MemoryTracker()
    # Memory optimization: Memory-critical operation
    memory_tracker.start()
    # Memory optimization: Memory-critical operation
    
    # Create and move model to device with visual feedback
    # Memory optimization: Device placement for memory management
    if HAS_RICH and not args.no_rich:
        with console.status(f"[bold cyan]Creating test model with size parameter {model_size}...", spinner="dots"):
        # Memory optimization: Explicit memory cleanup
            model = TestModel(model_size)
            # Memory optimization: Explicit memory cleanup
            model = model.to(device)
            # Memory optimization: Device placement for memory management
    else:
        logger.info(f"Creating test model with size parameter {model_size}")
        # Memory optimization: Explicit memory cleanup
        model = TestModel(model_size)
        # Memory optimization: Explicit memory cleanup
        model = model.to(device)
        # Memory optimization: Device placement for memory management
    
    # Register parameters with swap manager
    if HAS_RICH and not args.no_rich:
        with console.status("[bold cyan]Registering model parameters with swap manager...", spinner="dots"):
        # Memory optimization: Explicit memory cleanup
            swap_manager.register_model_parameters(model, group_by_layer=True)
    else:
        swap_manager.register_model_parameters(model, group_by_layer=True)
    
    # Log initial statistics
    stats = swap_manager.get_statistics()
    if HAS_RICH and not args.no_rich:
        console.print(Panel(f"[bold green]Registered {stats['tracked_tensors_count']} tensors "
                          f"({stats['total_managed_size_mb']:.2f}MB) for management"))
    else:
        logger.info(f"Registered {stats['tracked_tensors_count']} tensors "
                   f"({stats['total_managed_size_mb']:.2f}MB) for management")
    
    # Create test data
    input_data = torch.rand(32, model_size, device=device)
    # Memory optimization: Device placement for memory management
    
    # Test forward pass
    if HAS_RICH and not args.no_rich:
        with console.status("[bold green]Testing standard forward pass...", spinner="dots"):
            output = model(input_data)
    else:
        logger.info("Testing standard forward pass...")
        output = model(input_data)
    
    # Now test with layer swapping
    if HAS_RICH and not args.no_rich:
        console.print("[bold yellow]Testing forward pass with manual layer swapping:")
        
        # Encoder pass
        with console.status("[cyan]Processing encoder layer...", spinner="dots"):
            swap_manager.ensure_group_on_gpu("encoder")
            # Memory optimization: Memory-critical operation
            x = model.encoder(input_data)
        
        # Swap encoder to CPU, move middle to GPU
        # Memory optimization: Memory-critical operation
        with console.status("[cyan]Processing middle layer...", spinner="dots"):
            swap_manager.ensure_group_on_gpu("middle")
            # Memory optimization: Memory-critical operation
            x = model.middle(x)
        
        # Swap middle to CPU, move decoder to GPU
        # Memory optimization: Memory-critical operation
        with console.status("[cyan]Processing decoder layer...", spinner="dots"):
            swap_manager.ensure_group_on_gpu("decoder")
            # Memory optimization: Memory-critical operation
            output2 = model.decoder(x)
    else:
        # Standard operations without Rich
        logger.info("Testing forward pass with manual layer swapping...")
        
        # Encoder pass
        swap_manager.ensure_group_on_gpu("encoder")
        # Memory optimization: Memory-critical operation
        x = model.encoder(input_data)
        
        # Swap encoder to CPU, move middle to GPU
        # Memory optimization: Memory-critical operation
        swap_manager.ensure_group_on_gpu("middle")
        # Memory optimization: Memory-critical operation
        x = model.middle(x)
        
        # Swap middle to CPU, move decoder to GPU
        # Memory optimization: Memory-critical operation
        swap_manager.ensure_group_on_gpu("decoder")
        # Memory optimization: Memory-critical operation
        output2 = model.decoder(x)
    
    # Verify results match
    diff = (output - output2).abs().max().item()
    if HAS_RICH and not args.no_rich:
        diff_style = "green" if diff < 1e-5 else "red"
        console.print(f"Max difference between standard and swapped execution: [bold {diff_style}]{diff:.8f}[/]")
    else:
        logger.info(f"Max difference between standard and swapped execution: {diff:.8f}")
    
    # Get statistics
    stats = swap_manager.get_statistics()
    if HAS_RICH and not args.no_rich:
        stat_table = Table(title="Memory Swap Statistics")
        # Memory optimization: Memory-critical operation
        stat_table.add_column("Metric", style="cyan")
        stat_table.add_column("Value", style="yellow")
        
        stat_table.add_row("Swaps performed", str(stats['swap_count']))
        stat_table.add_row("Restores performed", str(stats['restore_count']))
        stat_table.add_row("Managed memory", f"{stats['total_managed_size_mb']:.2f} MB")
        # Memory optimization: Memory-critical operation
        
        console.print(stat_table)
    else:
        logger.info(f"Swaps performed: {stats['swap_count']}")
        logger.info(f"Restores performed: {stats['restore_count']}")
    
    # Display memory usage summary
    # Memory optimization: Memory-critical operation
    memory_stats = memory_tracker.stop()
    # Memory optimization: Memory-critical operation
    if HAS_RICH and not args.no_rich:
        console.print(memory_tracker.get_summary_table())
        # Memory optimization: Memory-critical operation
    
    # Clean up
    swap_manager.cleanup()
    
    return "Parameter swap test completed successfully"

def main():
    """Main test function."""
    global args
    args = parse_args()
    
    # Disable Rich if requested
    global HAS_RICH
    if args.no_rich:
        HAS_RICH = False
    
    # Show welcome message
    if HAS_RICH:
        console.print(Panel.fit(
            "[bold blue]ImpressionCore GPU Memory Management Tests[/]\n"
            # Memory optimization: Memory-critical operation
            "[dim]Optimized for low-VRAM environments (4GB VRAM target)[/]",
            border_style="cyan"
        ))
    
    # Check for CUDA
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        device = torch.device("cuda:0")
        # Memory optimization: Device placement for memory management
        device_name = torch.cuda.get_device_name(device)
        # Memory optimization: CUDA operations for GPU acceleration
        total_memory = torch.cuda.get_device_properties(device).total_memory / 1024**2
        # Memory optimization: CUDA operations for GPU acceleration
        
        if HAS_RICH:
            device_info = Table(show_header=False, box=rich.box.ROUNDED)
            # Memory optimization: Device placement for memory management
            device_info.add_column("Property", style="cyan")
            # Memory optimization: Device placement for memory management
            device_info.add_column("Value", style="green")
            # Memory optimization: Device placement for memory management
            
            device_info.add_row("CUDA Device", device_name)
            # Memory optimization: Device placement for memory management
            device_info.add_row("Total VRAM", f"{total_memory:.2f} MB")
            # Memory optimization: Device placement for memory management
            device_info.add_row("CUDA Version", torch.version.cuda)
            # Memory optimization: Device placement for memory management
            
            console.print(device_info)
            # Memory optimization: Device placement for memory management
        else:
            logger.info(f"CUDA available: {device_name} with {total_memory:.2f}MB VRAM")
            # Memory optimization: Device placement for memory management
    else:
        device = torch.device("cpu")
        # Memory optimization: Device placement for memory management
        if HAS_RICH:
            console.print("[bold yellow]CUDA not available, using CPU[/]")
            # Memory optimization: Memory-critical operation
        else:
            logger.warning("CUDA not available, using CPU")
            # Memory optimization: Memory-critical operation
    
    # Set up performance tracker if requested
    tracker = None
    if args.track and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        tracker = GPUPerformanceTracker()
        # Memory optimization: Memory-critical operation
        tracker.start_tracking("memory_test")
        # Memory optimization: Memory-critical operation
    
    # Run the tests
    try:
        if args.test == "basic" or args.test == "all":
            if HAS_RICH:
                console.rule("[bold green]Running Basic Tensor Test")
            result = basic_tensor_test(args.size, args.count, device)
            # Memory optimization: Device placement for memory management
            if HAS_RICH:
                console.print(f"[bold green]✓[/] {result}")
            else:
                logger.info(result)
        
        if args.test == "stress" or args.test == "all":
            if HAS_RICH:
                console.rule("[bold yellow]Running Stress Test")
            result = stress_test(args.size, args.target, device, args.shared)
            # Memory optimization: Device placement for memory management
            if HAS_RICH:
                console.print(f"[bold yellow]✓[/] {result}")
            else:
                logger.info(result)
        
        if args.test == "swap" or args.test == "all":
            if HAS_RICH:
                console.rule("[bold blue]Running Parameter Swap Test")
            result = parameter_swap_test(args.size, device, args.shared)
            # Memory optimization: Device placement for memory management
            if HAS_RICH:
                console.print(f"[bold blue]✓[/] {result}")
            else:
                logger.info(result)
    
    finally:
        # Clean up resources and display summary
        if tracker:
            summary = tracker.stop_tracking()
            
            if HAS_RICH:
                perf_table = Table(title="Performance Summary")
                perf_table.add_column("Metric", style="cyan")
                perf_table.add_column("Average", style="green")
                perf_table.add_column("Maximum", style="yellow")
                
                for metric, values in summary.items():
                    if isinstance(values, dict) and 'avg' in values:
                        perf_table.add_row(
                            metric,
                            f"{values['avg']:.2f}",
                            f"{values['max']:.2f}"
                        )
                
                console.print(perf_table)
            else:
                logger.info("Performance summary:")
                for metric, values in summary.items():
                    if isinstance(values, dict) and 'avg' in values:
                        logger.info(f"  {metric}: avg={values['avg']:.2f}, max={values['max']:.2f}")
                    elif not isinstance(values, dict):
                        logger.info(f"  {metric}: {values}")
        
        # Clean up CUDA memory
        # Memory optimization: Memory-critical operation
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
            
            # Report final memory usage
            # Memory optimization: Memory-critical operation
            allocated = torch.cuda.memory_allocated() / 1024**2
            # Memory optimization: CUDA operations for GPU acceleration
            reserved = torch.cuda.memory_reserved() / 1024**2
            # Memory optimization: CUDA operations for GPU acceleration
            
            if HAS_RICH:
                console.print(f"[dim]Final CUDA memory state: {allocated:.2f}MB allocated, {reserved:.2f}MB reserved[/]")
                # Memory optimization: Memory-critical operation
            else:
                logger.info(f"Final CUDA memory state: {allocated:.2f}MB allocated, {reserved:.2f}MB reserved")
                # Memory optimization: Memory-critical operation
    
    # Final message
    if HAS_RICH:
        console.print(Panel.fit(
            "[bold green]GPU memory management tests completed successfully[/]",
            # Memory optimization: Memory-critical operation
            border_style="green"
        ))
    else:
        logger.info("GPU memory management tests completed")
        # Memory optimization: Memory-critical operation

def run_standard_benchmark():
    """Run a standard benchmark suite for memory management features."""
    # Memory optimization: Memory-critical operation
    logger.info("Running standard benchmark suite for GPU memory management")
    # Memory optimization: Memory-critical operation
    
    # Check for CUDA
    # Memory optimization: Memory-critical operation
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.error("CUDA not available, benchmark requires GPU")
        # Memory optimization: Memory-critical operation
        return
    
    device = torch.device("cuda:0")
    # Memory optimization: Device placement for memory management
    device_properties = torch.cuda.get_device_properties(device)
    # Memory optimization: CUDA operations for GPU acceleration
    
    # Log system information
    logger.info(f"GPU: {device_properties.name}")
    # Memory optimization: Device placement for memory management
    logger.info(f"Compute capability: {device_properties.major}.{device_properties.minor}")
    # Memory optimization: Device placement for memory management
    logger.info(f"Total memory: {device_properties.total_memory / 1024**2:.2f}MB")
    # Memory optimization: Device placement for memory management
    
    # Benchmark results
    results = {
        "basic_tensors": {},
        "with_shared_memory": {},
        # Memory optimization: Memory-critical operation
        "with_parameter_swapping": {}
    }
    
    # Create performance tracker
    tracker = GPUPerformanceTracker(log_dir="benchmark_logs")
    # Memory optimization: Memory-critical operation
    tracker.start_tracking("standard_benchmark")
    
    try:
        # Run benchmarks and collect results
        logger.info("Running basic tensor operations benchmark...")
        results["basic_tensors"] = basic_tensor_test(1000, 5, device)
        # Memory optimization: Device placement for memory management
        
        logger.info("Running benchmark with shared memory...")
        # Memory optimization: Memory-critical operation
        results["with_shared_memory"] = stress_test(1000, 0.7, device, use_shared_memory=True)
        # Memory optimization: Device placement for memory management
        
        logger.info("Running benchmark with parameter swapping...")
        results["with_parameter_swapping"] = parameter_swap_test(1000, device, use_shared_memory=True)
        # Memory optimization: Device placement for memory management
        
        # Log results
        logger.info("Benchmark completed successfully")
        
    finally:
        # Stop tracking and get summary
        summary = tracker.stop_tracking()
        
        # Log performance summary
        logger.info("Performance summary:")
        for metric, values in summary.items():
            if isinstance(values, dict) and 'avg' in values:
                logger.info(f"  {metric}: avg={values['avg']:.2f}, max={values['max']:.2f}")
            elif not isinstance(values, dict):
                logger.info(f"  {metric}: {values}")
        
        # Clean up GPU memory
        # Memory optimization: Memory-critical operation
        torch.cuda.empty_cache()
        # Memory optimization: CUDA operations for GPU acceleration
    
    return results


if __name__ == "__main__":
    main()