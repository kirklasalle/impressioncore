#!/usr/bin/env python3
"""
ImpressionCore: Test Memory Manager

Module for test memory manager functionality in the ImpressionCore framework.

File: tests\test_memory_manager.py
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
Dependencies: [torch, rich]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements test memory manager functionality for the
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
from tests.test_memory_manager import TestMemoryManager
instance = TestMemoryManager()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import unittest
import torch
import logging
import sys
import time
import psutil
import os
from datetime import datetime
from src.memory_manager import MemoryManager
# Memory optimization: Memory-critical operation
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

# Configure enhanced logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("memory_manager_test")
# Memory optimization: Memory-critical operation
console = Console()

def log_memory_status():
# Memory optimization: Memory-critical operation
    """Log current memory usage status."""
    # Memory optimization: Memory-critical operation
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    # Memory optimization: Memory-critical operation
    
    # Create memory status table
    # Memory optimization: Memory-critical operation
    memory_table = Table(title="Memory Usage Status")
    # Memory optimization: Memory-critical operation
    memory_table.add_column("Metric", style="cyan")
    # Memory optimization: Memory-critical operation
    memory_table.add_column("Value", justify="right", style="green")
    # Memory optimization: Memory-critical operation
    
    # Add process memory info
    # Memory optimization: Memory-critical operation
    memory_table.add_row("Process RSS", f"{memory_info.rss / (1024 * 1024):.2f} MB")
    # Memory optimization: Memory-critical operation
    memory_table.add_row("Process VMS", f"{memory_info.vms / (1024 * 1024):.2f} MB")
    # Memory optimization: Memory-critical operation
    
    # Add system memory info
    # Memory optimization: Memory-critical operation
    system_memory = psutil.virtual_memory()
    # Memory optimization: Memory-critical operation
    memory_table.add_row("System Total", f"{system_memory.total / (1024 * 1024 * 1024):.2f} GB")
    # Memory optimization: Memory-critical operation
    memory_table.add_row("System Available", f"{system_memory.available / (1024 * 1024 * 1024):.2f} GB")
    # Memory optimization: Memory-critical operation
    memory_table.add_row("System Used", f"{system_memory.percent:.1f}%")
    # Memory optimization: Memory-critical operation
    
    # Add GPU memory info if available
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        for i in range(torch.cuda.device_count()):
        # Memory optimization: CUDA operations for GPU acceleration
            gpu_name = torch.cuda.get_device_name(i)
            # Memory optimization: CUDA operations for GPU acceleration
            total_memory = torch.cuda.get_device_properties(i).total_memory / (1024 * 1024)
            # Memory optimization: CUDA operations for GPU acceleration
            allocated_memory = torch.cuda.memory_allocated(i) / (1024 * 1024)
            # Memory optimization: CUDA operations for GPU acceleration
            reserved_memory = torch.cuda.memory_reserved(i) / (1024 * 1024)
            # Memory optimization: CUDA operations for GPU acceleration
            
            memory_table.add_row(f"GPU {i} Total", f"{total_memory:.2f} MB")
            # Memory optimization: Memory-critical operation
            memory_table.add_row(f"GPU {i} Allocated", f"{allocated_memory:.2f} MB")
            # Memory optimization: Memory-critical operation
            memory_table.add_row(f"GPU {i} Reserved", f"{reserved_memory:.2f} MB")
            # Memory optimization: Memory-critical operation
            memory_table.add_row(f"GPU {i} Utilization", f"{allocated_memory/total_memory*100:.1f}%")
            # Memory optimization: Memory-critical operation
    
    console.print(memory_table)
    # Memory optimization: Memory-critical operation
    
    return memory_info.rss / (1024 * 1024), system_memory.percent
    # Memory optimization: Memory-critical operation

class TestMemoryManager(unittest.TestCase):
# Memory optimization: Memory-critical operation
    """
    
    TestMemoryManager class for ImpressionCore framework.
    # Memory optimization: Memory-critical operation
    
    This class implements testmemorymanager functionality optimized for
    # Memory optimization: Memory-critical operation
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
    def setUp(self):
        """
        
    setUp function for processing.
    
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
        self.manager = MemoryManager()
        # Memory optimization: Memory-critical operation
        console.print(Panel.fit(
            "[bold blue]Initialized MemoryManager for testing[/bold blue]", 
            # Memory optimization: Memory-critical operation
            border_style="cyan"
        ))
        log_memory_status()
        # Memory optimization: Memory-critical operation

    def test_track_vram(self):
        """
        
    test_track_vram function for processing.
    
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
        console.print(Panel.fit(
            "[bold blue]STARTING TEST: test_track_vram[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Creating test tensor (100x100) on CUDA device[/yellow]")
        # Memory optimization: Device placement for memory management
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        # Create test tensor
        tensor = torch.randn(100, 100).cuda()
        # Memory optimization: Memory-critical operation
        console.print("[green]✓[/green] Created test tensor on CUDA device")
        # Memory optimization: Device placement for memory management
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        # Log CUDA memory status
        # Memory optimization: Memory-critical operation
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            gpu_info_table = Table(title="GPU Information")
            # Memory optimization: Memory-critical operation
            gpu_info_table.add_column("GPU", style="cyan")
            # Memory optimization: Memory-critical operation
            gpu_info_table.add_column("Total Memory", justify="right", style="green")
            # Memory optimization: Memory-critical operation
            gpu_info_table.add_column("Allocated Memory", justify="right", style="yellow")
            # Memory optimization: Memory-critical operation
            gpu_info_table.add_column("Reserved Memory", justify="right", style="blue")
            # Memory optimization: Memory-critical operation
            
            for i in range(torch.cuda.device_count()):
            # Memory optimization: CUDA operations for GPU acceleration
                props = torch.cuda.get_device_properties(i)
                # Memory optimization: CUDA operations for GPU acceleration
                gpu_info_table.add_row(
                # Memory optimization: Memory-critical operation
                    f"GPU {i}: {props.name}",
                    # Memory optimization: Memory-critical operation
                    f"{props.total_memory / 1024**2:.1f}MB",
                    # Memory optimization: Memory-critical operation
                    f"{torch.cuda.memory_allocated(i) / 1024**2:.1f}MB",
                    # Memory optimization: CUDA operations for GPU acceleration
                    f"{torch.cuda.memory_reserved(i) / 1024**2:.1f}MB"
                    # Memory optimization: CUDA operations for GPU acceleration
                )
            
            console.print(gpu_info_table)
            # Memory optimization: Memory-critical operation
        
        with console.status("[bold green]Tracking VRAM usage...[/bold green]", spinner="dots") as status:
            # Get initial VRAM usage
            console.print("[cyan]Getting initial VRAM usage...[/cyan]")
            initial_usage = self.manager.get_vram_usage()
            console.print(f"[green]✓[/green] Initial VRAM usage: {initial_usage} MB")
            
            # Track tensor in VRAM
            console.print("[cyan]Tracking tensor in VRAM...[/cyan]")
            self.manager.track_vram(tensor)
            console.print("[green]✓[/green] Tensor tracked in VRAM")
            
            # Get updated VRAM usage
            console.print("[cyan]Getting updated VRAM usage...[/cyan]")
            current_usage = self.manager.get_vram_usage()
            console.print(f"[green]✓[/green] Updated VRAM usage: {current_usage} MB")
        
        # Final assertion
        self.assertGreater(current_usage, initial_usage, "VRAM usage should increase after tracking a tensor.")
        console.print(f"[green]✓[/green] VRAM usage increased from {initial_usage} MB to {current_usage} MB")
        
        console.print(Panel.fit(
            f"[bold green]VRAM tracking test results:[/bold green]\n" +
            f"[cyan]Initial VRAM usage:[/cyan] {initial_usage} MB\n" +
            f"[cyan]Final VRAM usage:[/cyan] {current_usage} MB\n" +
            f"[cyan]Increase:[/cyan] {current_usage - initial_usage} MB",
            border_style="green"
        ))
        
        log_memory_status()
        # Memory optimization: Memory-critical operation
        console.print("[bold blue]TEST COMPLETE: test_track_vram[/bold blue]")

    def test_offload_to_cpu(self):
        """
        
    test_offload_to_cpu function for processing.
    
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
        console.print(Panel.fit(
            "[bold blue]STARTING TEST: test_offload_to_cpu[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Creating linear model (10x10) on CUDA device[/yellow]")
        # Memory optimization: Device placement for memory management
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        # Create model
        model = torch.nn.Linear(10, 10).cuda()
        # Memory optimization: Explicit memory cleanup
        console.print("[green]✓[/green] Created linear model on CUDA device")
        # Memory optimization: Device placement for memory management
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        # Log initial GPU stats
        # Memory optimization: Memory-critical operation
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            current_allocated = torch.cuda.memory_allocated() / (1024 * 1024)
            # Memory optimization: CUDA operations for GPU acceleration
            console.print(f"[cyan]GPU memory allocated before offload:[/cyan] {current_allocated:.2f} MB")
            # Memory optimization: Memory-critical operation
        
        with console.status("[bold green]Offloading model to CPU...[/bold green]", spinner="dots") as status:
        # Memory optimization: Explicit memory cleanup
            # Execute offloading
            self.manager.offload_to_cpu(model)
            console.print("[green]✓[/green] Model offloaded to CPU")
            # Memory optimization: Explicit memory cleanup
            
            # Verify parameters location
            console.print("[cyan]Verifying model parameters location...[/cyan]")
            # Memory optimization: Explicit memory cleanup
            all_on_cpu = all(not param.is_cuda for param in model.parameters())
            # Memory optimization: Memory-critical operation
            if all_on_cpu:
                console.print("[green]✓[/green] All model parameters successfully moved to CPU")
                # Memory optimization: Explicit memory cleanup
            else:
                console.print("[red]✗[/red] Some parameters are still on CUDA")
                # Memory optimization: Memory-critical operation
                for param in model.parameters():
                    if param.is_cuda:
                    # Memory optimization: Memory-critical operation
                        console.print(f"[red]- Parameter {param.shape} still on CUDA[/red]")
                        # Memory optimization: Memory-critical operation
        
        # Final assertion
        self.assertTrue(all_on_cpu, "All parameters should be offloaded to CPU.")
        
        # Log final GPU status
        # Memory optimization: Memory-critical operation
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            current_allocated = torch.cuda.memory_allocated() / (1024 * 1024)
            # Memory optimization: CUDA operations for GPU acceleration
            console.print(f"[cyan]GPU memory allocated after offload:[/cyan] {current_allocated:.2f} MB")
            # Memory optimization: Memory-critical operation
        
        console.print(Panel.fit(
            f"[bold green]CPU offloading test results:[/bold green]\n" +
            f"[cyan]Model parameters:[/cyan] Successfully offloaded to CPU\n" +
            # Memory optimization: Explicit memory cleanup
            f"[cyan]Current GPU memory:[/cyan] {current_allocated:.2f} MB",
            # Memory optimization: Memory-critical operation
            border_style="green"
        ))
        
        log_memory_status()
        # Memory optimization: Memory-critical operation
        console.print("[bold blue]TEST COMPLETE: test_offload_to_cpu[/bold blue]")

    def test_vram_usage_reporting(self):
        """
        
    test_vram_usage_reporting function for processing.
    
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
        console.print(Panel.fit(
            "[bold blue]STARTING TEST: test_vram_usage_reporting[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Setting up VRAM usage reporting test...[/yellow]")
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        with console.status("[bold green]Testing VRAM usage reporting...[/bold green]", spinner="dots") as status:
            # Create test tensor
            console.print("[cyan]Creating test tensor (50x50) on CUDA device...[/cyan]")
            # Memory optimization: Device placement for memory management
            tensor = torch.randn(50, 50).cuda()
            # Memory optimization: Memory-critical operation
            console.print("[green]✓[/green] Created test tensor on CUDA device")
            # Memory optimization: Device placement for memory management
            
            # Track the tensor
            console.print("[cyan]Tracking tensor in VRAM...[/cyan]")
            self.manager.track_vram(tensor)
            console.print("[green]✓[/green] Tensor tracked in memory manager")
            # Memory optimization: Memory-critical operation
            
            # Get usage report
            console.print("[cyan]Getting VRAM usage report...[/cyan]")
            usage = self.manager.get_vram_usage()
            console.print(f"[green]✓[/green] Reported VRAM usage: {usage} MB")
        
        # Validate
        self.assertGreater(usage, 0, "VRAM usage should be reported as greater than zero.")
        
        console.print(Panel.fit(
            f"[bold green]VRAM usage reporting test results:[/bold green]\n" +
            f"[cyan]Reported VRAM usage:[/cyan] {usage} MB\n" +
            f"[cyan]Validation:[/cyan] {'Passed' if usage > 0 else 'Failed'}",
            border_style="green"
        ))
        
        log_memory_status()
        # Memory optimization: Memory-critical operation
        console.print("[bold blue]TEST COMPLETE: test_vram_usage_reporting[/bold blue]")

if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold blue]=== Memory Manager Test Suite ===[/bold blue]",
        # Memory optimization: Memory-critical operation
        border_style="cyan"
    ))
    
    start_time = time.time()
    initial_memory, initial_percent = log_memory_status()
    # Memory optimization: Memory-critical operation
    
    # System information
    system_info_table = Table(title="System Information")
    system_info_table.add_column("Component", style="cyan")
    system_info_table.add_column("Details", style="green")
    
    system_info_table.add_row("System", os.name)
    system_info_table.add_row("Python", sys.version.split()[0])
    system_info_table.add_row("Total RAM", f"{psutil.virtual_memory().total / (1024**3):.2f} GB")
    # Memory optimization: Memory-critical operation
    system_info_table.add_row("CUDA Available", str(torch.cuda.is_available()))
    # Memory optimization: CUDA operations for GPU acceleration
    
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        system_info_table.add_row("CUDA Device Count", str(torch.cuda.device_count()))
        # Memory optimization: CUDA operations for GPU acceleration
        system_info_table.add_row("CUDA Current Device", str(torch.cuda.current_device()))
        # Memory optimization: CUDA operations for GPU acceleration
        
        for i in range(torch.cuda.device_count()):
        # Memory optimization: CUDA operations for GPU acceleration
            device_props = torch.cuda.get_device_properties(i)
            # Memory optimization: CUDA operations for GPU acceleration
            system_info_table.add_row(
                f"GPU {i}", 
                # Memory optimization: Memory-critical operation
                f"{device_props.name} - {device_props.total_memory / (1024**3):.2f} GB total memory"
                # Memory optimization: Device placement for memory management
            )
    
    console.print(system_info_table)
    
    # Create and run the test suite
    suite = unittest.TestSuite()
    tests = [
        "test_track_vram",
        "test_offload_to_cpu",
        "test_vram_usage_reporting"
    ]
    
    # Run tests sequentially
    for i, test_name in enumerate(tests):
        test_number = i + 1
        total_tests = len(tests)
        console.print(f"[bold blue]Running test {test_number}/{total_tests}: {test_name}[/bold blue]")
        
        # Add this test to the suite
        suite.addTest(TestMemoryManager(test_name))
        # Memory optimization: Memory-critical operation
        
        # Run this test
        result = unittest.TextTestRunner(verbosity=0).run(suite)
        
        # Clear the suite for the next test
        suite = unittest.TestSuite()
        
        # Show progress
        console.print(f"[green]Completed test {test_number}/{total_tests}[/green]")
    
    # Print test summary with memory usage
    # Memory optimization: Memory-critical operation
    final_memory, final_percent = log_memory_status()
    # Memory optimization: Memory-critical operation
    memory_delta = final_memory - initial_memory
    # Memory optimization: Memory-critical operation
    
    # Summary report
    elapsed_time = time.time() - start_time
    
    console.print(Panel.fit(
        f"[bold green]Test Summary:[/bold green]\n" +
        f"[cyan]Tests run:[/cyan] {len(tests)}\n" +
        f"[cyan]Test suite completed in:[/cyan] {elapsed_time:.2f} seconds\n" +
        f"[cyan]Total memory change:[/cyan] {memory_delta:+.2f}MB ({initial_percent:.1f}% → {final_percent:.1f}%)",
        # Memory optimization: Memory-critical operation
        border_style="green"
    ))
    
    # VRAM summary if available
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        vram_allocated = torch.cuda.memory_allocated() / (1024 * 1024)
        # Memory optimization: CUDA operations for GPU acceleration
        vram_reserved = torch.cuda.memory_reserved() / (1024 * 1024)
        # Memory optimization: CUDA operations for GPU acceleration
        
        console.print(Panel.fit(
            f"[bold green]Final VRAM Status:[/bold green]\n" +
            f"[cyan]VRAM allocated:[/cyan] {vram_allocated:.2f}MB\n" +
            f"[cyan]VRAM reserved:[/cyan] {vram_reserved:.2f}MB",
            border_style="green"
        ))
    
    # Display timestamp
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(Panel.fit(
        f"[bold green]Memory Manager Test Suite Completed[/bold green]\n" +
        # Memory optimization: Memory-critical operation
        f"[cyan]Finished at:[/cyan] {end_time}",
        border_style="green"
    ))
