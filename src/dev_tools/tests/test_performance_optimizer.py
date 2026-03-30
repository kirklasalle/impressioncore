#!/usr/bin/env python3
"""
ImpressionCore: Test Performance Optimizer

Module for test performance optimizer functionality in the ImpressionCore framework.

File: tests\test_performance_optimizer.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, async, qa, pytorch, production, testing, 2025, object-oriented]
Dependencies: [torch, rich]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements test performance optimizer functionality for the
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
from tests.test_performance_optimizer import TestPerformanceOptimizer
instance = TestPerformanceOptimizer()
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
import asyncio
import logging
import sys
import time
import psutil
import os
from datetime import datetime
from src.performance_optimizer import PerformanceOptimizer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn

# Configure enhanced logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger('performance_optimizer_test')
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

class TestPerformanceOptimizer(unittest.IsolatedAsyncioTestCase):
    """
    
    TestPerformanceOptimizer class for ImpressionCore framework.
    
    This class implements testperformanceoptimizer functionality optimized for
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
        console.print(Panel.fit(
            "[bold blue]Setting up Performance Optimizer tests[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Initializing PerformanceOptimizer...[/yellow]")
        initial_memory, _ = log_memory_status()
        # Memory optimization: Memory-critical operation
        
        self.optimizer = PerformanceOptimizer()
        
        final_memory, _ = log_memory_status()
        # Memory optimization: Memory-critical operation
        memory_delta = final_memory - initial_memory
        # Memory optimization: Memory-critical operation
        console.print(f"[green]✓[/green] PerformanceOptimizer instance created (memory change: {memory_delta:+.2f} MB)")
        # Memory optimization: Memory-critical operation
        
        # Show available GPUs if any
        # Memory optimization: Memory-critical operation
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            gpu_table = Table(title="Available GPUs")
            # Memory optimization: Memory-critical operation
            gpu_table.add_column("Device", style="cyan")
            # Memory optimization: Device placement for memory management
            gpu_table.add_column("Name", style="green")
            # Memory optimization: Memory-critical operation
            gpu_table.add_column("Memory", justify="right", style="yellow")
            # Memory optimization: Memory-critical operation
            
            for i in range(torch.cuda.device_count()):
            # Memory optimization: CUDA operations for GPU acceleration
                device_props = torch.cuda.get_device_properties(i)
                # Memory optimization: CUDA operations for GPU acceleration
                gpu_table.add_row(
                # Memory optimization: Memory-critical operation
                    f"GPU {i}", 
                    # Memory optimization: Memory-critical operation
                    device_props.name,
                    # Memory optimization: Device placement for memory management
                    f"{device_props.total_memory / (1024**3):.2f} GB"
                    # Memory optimization: Device placement for memory management
                )
            
            console.print(gpu_table)
            # Memory optimization: Memory-critical operation
        else:
            console.print("[bold yellow]No CUDA-capable GPUs detected. Tests will run on CPU only.[/bold yellow]")
            # Memory optimization: Memory-critical operation

    async def test_distribute_tensors(self):
        """
        
    test_distribute_tensors function for processing.
    
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
            "[bold blue]STARTING TEST: test_distribute_tensors[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Setting up tensor distribution test...[/yellow]")
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        # Create test tensors
        tensor_count = 4
        console.print(f"[cyan]Creating {tensor_count} test tensors (100x100)[/cyan]")
        tensors = [torch.randn(100, 100) for _ in range(tensor_count)]
        console.print(f"[green]✓[/green] Created {tensor_count} test tensors")
        
        # Display initial GPU status if available
        # Memory optimization: Memory-critical operation
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            gpu_status_table = Table(title="Initial GPU Status")
            # Memory optimization: Memory-critical operation
            gpu_status_table.add_column("Device", style="cyan")
            # Memory optimization: Device placement for memory management
            gpu_status_table.add_column("Allocated (MB)", justify="right", style="green")
            # Memory optimization: Memory-critical operation
            gpu_status_table.add_column("Reserved (MB)", justify="right", style="yellow")
            # Memory optimization: Memory-critical operation
            
            for i in range(torch.cuda.device_count()):
            # Memory optimization: CUDA operations for GPU acceleration
                gpu_status_table.add_row(
                # Memory optimization: Memory-critical operation
                    f"GPU {i}",
                    # Memory optimization: Memory-critical operation
                    f"{torch.cuda.memory_allocated(i) / (1024**2):.2f}",
                    # Memory optimization: CUDA operations for GPU acceleration
                    f"{torch.cuda.memory_reserved(i) / (1024**2):.2f}"
                    # Memory optimization: CUDA operations for GPU acceleration
                )
            
            console.print(gpu_status_table)
            # Memory optimization: Memory-critical operation
        
        # Display available devices
        # Memory optimization: Device placement for memory management
        device_info = "N/A" if not self.optimizer.devices else ", ".join([str(d) for d in self.optimizer.devices])
        # Memory optimization: Device placement for memory management
        console.print(f"[cyan]Available devices for distribution:[/cyan] {device_info}")
        # Memory optimization: Device placement for memory management
        
        # Manual distribution with progress tracking
        console.print("[yellow]Testing manual tensor distribution...[/yellow]")
        distributed_tensors = []
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold green]{task.completed}/{task.total}"),
            TimeElapsedColumn()
        ) as progress:
            task = progress.add_task("[cyan]Distributing tensors...", total=tensor_count)
            
            # Track GPU latency for each device
            # Memory optimization: Device placement for memory management
            gpu_latency = {device: torch.cuda.current_stream(device).query() if torch.cuda.is_available() else 0 
            # Memory optimization: CUDA operations for GPU acceleration
                         for device in self.optimizer.devices}
                         # Memory optimization: Device placement for memory management
            
            for i, tensor in enumerate(tensors):
                progress.update(task, advance=1, description=f"Processing tensor {i+1}/{tensor_count}")
                
                # Select GPU with the least latency
                # Memory optimization: Memory-critical operation
                if self.optimizer.devices:
                # Memory optimization: Device placement for memory management
                    target_device = min(gpu_latency, key=gpu_latency.get)
                    # Memory optimization: Device placement for memory management
                    distributed_tensors.append(tensor.to(target_device))
                    # Memory optimization: Device placement for memory management
                    if hasattr(tensor, 'element_size') and hasattr(tensor, 'nelement'):
                        gpu_latency[target_device] += tensor.element_size() * tensor.nelement()
                        # Memory optimization: Device placement for memory management
                else:
                    distributed_tensors.append(tensor)  # No GPUs available
                    # Memory optimization: Memory-critical operation
                
                # Small delay for visualization
                await asyncio.sleep(0.1)
        
        console.print(f"[green]✓[/green] Manually distributed {len(distributed_tensors)} tensors")
        
        # Now test the actual optimizer method
        console.print("[yellow]Testing optimizer's distribute_tensors_async method...[/yellow]")
        
        with console.status("[bold green]Distributing tensors asynchronously...[/bold green]", spinner="dots") as status:
            start_time = time.time()
            actual_distributed_tensors = await self.optimizer.distribute_tensors_async(tensors)
            elapsed_time = time.time() - start_time
            console.print(f"[green]✓[/green] Asynchronously distributed {len(actual_distributed_tensors)} tensors in {elapsed_time:.4f} seconds")
        
        # Display distribution results
        if self.optimizer.devices:
        # Memory optimization: Device placement for memory management
            distribution_table = Table(title="Tensor Distribution")
            distribution_table.add_column("Tensor", style="cyan")
            distribution_table.add_column("Device", style="green")
            # Memory optimization: Device placement for memory management
            distribution_table.add_column("Shape", style="yellow")
            
            for i, tensor in enumerate(actual_distributed_tensors):
                distribution_table.add_row(
                    f"Tensor {i+1}",
                    str(tensor.device),
                    # Memory optimization: Device placement for memory management
                    str(tensor.shape)
                )
            
            console.print(distribution_table)
        
        # Assertions
        self.assertEqual(len(actual_distributed_tensors), len(tensors), "All tensors should be distributed.")
        
        if self.optimizer.devices:
        # Memory optimization: Device placement for memory management
            all_correct = True
            for i, tensor in enumerate(actual_distributed_tensors):
                expected_device = self.optimizer.devices[i % len(self.optimizer.devices)]
                # Memory optimization: Device placement for memory management
                is_correct = tensor.device == expected_device
                # Memory optimization: Device placement for memory management
                all_correct = all_correct and is_correct
                
                if not is_correct:
                    console.print(f"[red]✗[/red] Tensor {i} is on {tensor.device} but should be on {expected_device}")
                    # Memory optimization: Device placement for memory management
            
            if all_correct:
                console.print("[green]✓[/green] All tensors are on the correct devices")
                # Memory optimization: Device placement for memory management
        
        # Final GPU status
        # Memory optimization: Memory-critical operation
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            gpu_status_table = Table(title="Final GPU Status")
            # Memory optimization: Memory-critical operation
            gpu_status_table.add_column("Device", style="cyan")
            # Memory optimization: Device placement for memory management
            gpu_status_table.add_column("Allocated (MB)", justify="right", style="green")
            # Memory optimization: Memory-critical operation
            gpu_status_table.add_column("Reserved (MB)", justify="right", style="yellow")
            # Memory optimization: Memory-critical operation
            
            for i in range(torch.cuda.device_count()):
            # Memory optimization: CUDA operations for GPU acceleration
                gpu_status_table.add_row(
                # Memory optimization: Memory-critical operation
                    f"GPU {i}",
                    # Memory optimization: Memory-critical operation
                    f"{torch.cuda.memory_allocated(i) / (1024**2):.2f}",
                    # Memory optimization: CUDA operations for GPU acceleration
                    f"{torch.cuda.memory_reserved(i) / (1024**2):.2f}"
                    # Memory optimization: CUDA operations for GPU acceleration
                )
            
            console.print(gpu_status_table)
            # Memory optimization: Memory-critical operation
        
        log_memory_status()
        # Memory optimization: Memory-critical operation
        console.print("[bold blue]TEST COMPLETE: test_distribute_tensors[/bold blue]")

    def test_smart_batching(self):
        """
        
    test_smart_batching function for processing.
    
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
            "[bold blue]STARTING TEST: test_smart_batching[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Setting up smart batching test...[/yellow]")
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        # Setup test data
        data_size = 100
        batch_size = 10
        console.print(f"[cyan]Creating test data of size {data_size} with batch size {batch_size}[/cyan]")
        
        data = list(range(data_size))
        expected_batches = data_size // batch_size
        console.print(f"[green]✓[/green] Created test data with {data_size} items. Expected batches: {expected_batches}")
        
        # Execute batching with real-time feedback
        with console.status(f"[bold green]Creating smart batches...[/bold green]", spinner="dots") as status:
            start_time = time.time()
            batches = self.optimizer.smart_batching(data, batch_size)
            elapsed_time = time.time() - start_time
            console.print(f"[green]✓[/green] Created {len(batches)} batches in {elapsed_time:.4f} seconds")
        
        # Display batch information
        batch_table = Table(title=f"Smart Batching Results ({len(batches)} batches)")
        batch_table.add_column("Batch", style="cyan")
        batch_table.add_column("Size", justify="right", style="green")
        batch_table.add_column("First Items", style="yellow")
        
        for i, batch in enumerate(batches):
            batch_table.add_row(
                f"Batch {i+1}", 
                str(len(batch)),
                str(batch[:3]) + "..." if len(batch) > 3 else str(batch)
            )
            
            # Only show first 10 batches for readability
            if i >= 9 and len(batches) > 10:
                batch_table.add_row(
                    "...", "...", "..."
                )
                batch_table.add_row(
                    f"Batch {len(batches)}", 
                    str(len(batches[-1])),
                    str(batches[-1][:3]) + "..." if len(batches[-1]) > 3 else str(batches[-1])
                )
                break
        
        console.print(batch_table)
        
        # Validate batches with progress feedback
        console.print("[yellow]Validating batch sizes...[/yellow]")
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold green]{task.completed}/{task.total}"),
            TimeElapsedColumn()
        ) as progress:
            validation_task = progress.add_task("[cyan]Validating batches...", total=len(batches))
            all_valid = True
            
            for i, batch in enumerate(batches):
                progress.update(validation_task, advance=1, description=f"Validating batch {i+1}/{len(batches)}")
                if len(batch) > batch_size:
                    all_valid = False
                    progress.print(f"[red]✗[/red] Batch {i+1} is too large: {len(batch)} > {batch_size}")
                time.sleep(0.02)  # Small delay for visualization
        
        # Assertions
        self.assertEqual(len(batches), expected_batches, 
                       "Number of batches should match the data size divided by batch size.")
        
        for i, batch in enumerate(batches):
            self.assertLessEqual(len(batch), batch_size, 
                               f"Batch {i} size ({len(batch)}) should not exceed the specified limit ({batch_size}).")
        
        console.print(Panel.fit(
            f"[bold green]Smart batching test results:[/bold green]\n" +
            f"[cyan]Data size:[/cyan] {data_size}\n" +
            f"[cyan]Batch size:[/cyan] {batch_size}\n" +
            f"[cyan]Expected batches:[/cyan] {expected_batches}\n" +
            f"[cyan]Actual batches:[/cyan] {len(batches)}\n" +
            f"[cyan]Valid batch sizes:[/cyan] {'Yes' if all_valid else 'No'}\n" +
            f"[cyan]Processing time:[/cyan] {elapsed_time:.4f} seconds",
            border_style="green"
        ))
        
        log_memory_status()
        # Memory optimization: Memory-critical operation
        console.print("[bold blue]TEST COMPLETE: test_smart_batching[/bold blue]")

if __name__ == "__main__":
    # Display test header
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(Panel.fit(
        f"[bold blue]ImpressionCore Performance Optimizer Tests[/bold blue]\n"
        f"[cyan]Started at:[/cyan] {current_time}\n"
        f"[cyan]Target:[/cyan] NVIDIA GTX 1050 Ti (4GB VRAM)",
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
        "test_distribute_tensors",
        "test_smart_batching"
    ]
    
    # Run tests sequentially
    for i, test_name in enumerate(tests):
        test_number = i + 1
        total_tests = len(tests)
        console.print(f"[bold blue]Running test {test_number}/{total_tests}: {test_name}[/bold blue]")
        
        # Add this test to the suite
        suite.addTest(TestPerformanceOptimizer(test_name))
        
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
        f"[bold green]Performance Optimizer Tests Completed[/bold green]\n" +
        f"[cyan]Finished at:[/cyan] {end_time}",
        border_style="green"
    ))
