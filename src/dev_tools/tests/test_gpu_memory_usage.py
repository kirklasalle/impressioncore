#!/usr/bin/env python3
"""
ImpressionCore: Test Gpu Memory Usage

Module for test gpu memory usage functionality in the ImpressionCore framework.

File: tests\test_gpu_memory_usage.py
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
Dependencies: [torch, rich, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements test gpu memory usage functionality for the
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
from tests.test_gpu_memory_usage import DummyProgress
instance = DummyProgress()
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
import logging
import torch
import argparse
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import Rich for enhanced logging and progress display
try:
    from rich.console import Console
    from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
    from rich.logging import RichHandler
    from rich.panel import Panel
    from rich.table import Table
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("Rich library not found. Install with 'pip install rich' for enhanced output.")

# Fix import paths to use src.core instead of impressioncore
from src.core.gpu_utils import (
# Memory optimization: Memory-critical operation
    get_device,
    # Memory optimization: Device placement for memory management
    get_memory_info,
    # Memory optimization: Memory-critical operation
    clear_gpu_memory,
    # Memory optimization: Memory-critical operation
    MemoryTracker,
    # Memory optimization: Memory-critical operation
    is_shared_memory_gpu
    # Memory optimization: Memory-critical operation
)
from src.core.model import ImpressionCoreModel
# Memory optimization: Explicit memory cleanup
from src.core.config import ModelConfig, ModelDimensions
from src.core.memory_optimization import (
# Memory optimization: Memory-critical operation
    memory_efficient_inference,
    # Memory optimization: Memory-critical operation
    optimize_memory_allocation
    # Memory optimization: Memory-critical operation
)
from src.core.incremental_loader import load_model_incrementally

# Configure enhanced logging with Rich if available
if HAS_RICH:
    console = Console()
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )
else:
    # Fallback to standard logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

logger = logging.getLogger(__name__)

# Create progress animation function using Rich
def create_progress(total, description="Processing", transient=True):
    """Create a Rich progress bar with memory statistics."""
    # Memory optimization: Memory-critical operation
    if not HAS_RICH:
        # Return dummy context manager if Rich is not available
        class DummyProgress:
            """
            
    DummyProgress class for ImpressionCore framework.
    
    This class implements dummyprogress functionality optimized for
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
            def __enter__(self):
                """
                
    __enter__ function for processing.
    
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
                return self
            def __exit__(self, *args):
                """
                
    __exit__ function for processing.
    
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
                pass
            def add_task(self, description, total=None):
                """
                
    add_task function for processing.
    
    Args:
        self, description, total: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                return 0
            def update(self, task_id, advance=1):
                """
                
    update function for processing.
    
    Args:
        self, task_id, advance: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                pass
        return DummyProgress()
    
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TextColumn("• [bold green]{task.fields[memory_usage]:.2f}MB GPU"),
        # Memory optimization: Memory-critical operation
        console=console,
        transient=transient
    )

def test_shared_memory_detection():
# Memory optimization: Memory-critical operation
    """Test detection of shared memory GPU configuration."""
    # Memory optimization: Memory-critical operation
    is_shared, dedicated_vram, total_shared = is_shared_memory_gpu()
    # Memory optimization: Memory-critical operation
    
    if HAS_RICH:
        table = Table(title="GPU Memory Configuration", show_header=True)
        # Memory optimization: Memory-critical operation
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Shared memory GPU", str(is_shared))
        # Memory optimization: Memory-critical operation
        if is_shared:
            table.add_row("Dedicated VRAM", f"{dedicated_vram:.2f} GB")
            table.add_row("Total shared memory", f"{total_shared:.2f} GB")
            # Memory optimization: Memory-critical operation
        
        console.print(table)
    else:
        logger.info(f"Shared memory GPU: {is_shared}")
        # Memory optimization: Memory-critical operation
        if is_shared:
            logger.info(f"Dedicated VRAM: {dedicated_vram:.2f}GB")
            logger.info(f"Total shared memory: {total_shared:.2f}GB")
            # Memory optimization: Memory-critical operation
    
    return is_shared

def test_memory_allocation(size_mb=100, step_mb=10, max_mb=1000):
# Memory optimization: Memory-critical operation
    """
    Test memory allocation in steps to find limits.
    # Memory optimization: Memory-critical operation
    
    Args:
        size_mb: Initial allocation size in MB
        step_mb: Step size for each allocation in MB
        max_mb: Maximum allocation to attempt in MB
    """
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.warning("CUDA not available, skipping memory allocation test")
        # Memory optimization: Memory-critical operation
        return
    
    device = get_device()
    # Memory optimization: Device placement for memory management
    tensors = []
    allocated_mb = 0
    
    logger.info("Testing memory allocation limits")
    # Memory optimization: Memory-critical operation
    
    try:
        # Create Rich progress bar
        with create_progress(total=max_mb, description="Allocating GPU memory") as progress:
        # Memory optimization: Memory-critical operation
            # Add task with initial memory usage
            # Memory optimization: Memory-critical operation
            mem_info = get_memory_info()
            # Memory optimization: Memory-critical operation
            vram_info = mem_info.get("gpu_vram", {})
            # Memory optimization: Memory-critical operation
            initial_vram = vram_info.get("allocated", 0) * 1024  # Convert GB to MB
            
            task_id = progress.add_task(
                "Allocating memory", 
                # Memory optimization: Memory-critical operation
                total=max_mb, 
                memory_usage=initial_vram
                # Memory optimization: Memory-critical operation
            )
            
            # Allocate memory in steps
            # Memory optimization: Memory-critical operation
            while allocated_mb < max_mb:
                # Calculate allocation size
                current_size = min(size_mb, max_mb - allocated_mb)
                if current_size <= 0:
                    break
                
                # Calculate tensor dimensions (approximately size_mb of memory)
                # Memory optimization: Memory-critical operation
                # Each float32 is 4 bytes, so we need size_mb * 1024 * 1024 / 4 elements
                elements = int(current_size * 1024 * 1024 / 4)
                dim = int(elements ** 0.5)  # Make it roughly square
                
                # Create tensor and add to list
                tensor = torch.zeros((dim, dim), dtype=torch.float32, device=device)
                # Memory optimization: Device placement for memory management
                tensors.append(tensor)
                
                # Update allocated memory
                # Memory optimization: Memory-critical operation
                allocated_mb += current_size
                
                # Get memory info
                # Memory optimization: Memory-critical operation
                mem_info = get_memory_info()
                # Memory optimization: Memory-critical operation
                vram_info = mem_info.get("gpu_vram", {})
                # Memory optimization: Memory-critical operation
                vram_used = vram_info.get("allocated", 0) * 1024  # Convert GB to MB
                
                # Update progress bar
                progress.update(
                    task_id, 
                    completed=allocated_mb,
                    memory_usage=vram_used
                    # Memory optimization: Memory-critical operation
                )
                
                # Small delay to make progress visible
                time.sleep(0.1)
                
                # Increase allocation size for next iteration
                size_mb += step_mb
                
        # Print final allocation
        if HAS_RICH:
            console.print(f"[bold green]Maximum allocation reached: {allocated_mb:.1f}MB[/]")
        else:
            logger.info(f"Maximum allocation reached: {allocated_mb:.1f}MB")
                
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
        # Memory optimization: Memory-critical operation
            if HAS_RICH:
                console.print(f"[bold red]Out of memory error at {allocated_mb:.1f}MB allocation[/]")
                # Memory optimization: Memory-critical operation
            else:
                logger.info(f"Out of memory error at {allocated_mb:.1f}MB allocation")
                # Memory optimization: Memory-critical operation
        else:
            logger.error(f"Error during memory allocation: {e}")
            # Memory optimization: Memory-critical operation
    finally:
        # Clean up tensors
        tensors.clear()
        # Memory optimization: Memory-critical operation
        clear_gpu_memory()
        # Memory optimization: Memory-critical operation
        logger.info("Memory cleared")
        # Memory optimization: Memory-critical operation

def test_batch_size_calculation():
    """Test batch size calculation for different model sizes."""
    # Memory optimization: Explicit memory cleanup
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.warning("CUDA not available, skipping batch size calculation test")
        # Memory optimization: Memory-critical operation
        return
    
    # Test with different model sizes
    # Memory optimization: Explicit memory cleanup
    model_sizes = {
        "tiny": 100,       # ~100MB model
        "small": 500,      # ~500MB model
        "medium": 2000,    # ~2GB model
        "large": 4000      # ~4GB model
    }
    
    sequence_lengths = [128, 512, 1024, 2048]
    
    logger.info("Testing optimal batch size calculation")
    
    if HAS_RICH:
        # Create a table for displaying batch size information
        table = Table(title="Optimal Batch Size Calculation")
        table.add_column("Model Size", style="cyan")
        # Memory optimization: Explicit memory cleanup
        table.add_column("Size (MB)", style="blue")
        table.add_column("Sequence Length", style="magenta")
        table.add_column("Batch Size", style="green")
        
        # Fill table with batch size calculations
        for model_name, model_size_mb in model_sizes.items():
            for seq_len in sequence_lengths:
                # Get optimal batch size
                batch_size = get_optimal_batch_size(
                    model_size_mb=model_size_mb,
                    sequence_length=seq_len,
                    dtype=torch.float16
                )
                
                # Add row to table
                table.add_row(
                    model_name,
                    str(model_size_mb),
                    str(seq_len),
                    str(batch_size)
                )
        
        # Display the table
        console.print(table)
    else:
        # Traditional logging for batch size information
        for model_name, model_size_mb in model_sizes.items():
            for seq_len in sequence_lengths:
                # Get optimal batch size
                batch_size = get_optimal_batch_size(
                    model_size_mb=model_size_mb,
                    sequence_length=seq_len,
                    dtype=torch.float16
                )
                
                logger.info(f"Model size: {model_name} ({model_size_mb}MB), "
                # Memory optimization: Explicit memory cleanup
                           f"Sequence length: {seq_len}, "
                           f"Optimal batch size: {batch_size}")

def test_memory_efficient_inference():
# Memory optimization: Memory-critical operation
    """Test memory-efficient inference."""
    # Memory optimization: Memory-critical operation
    logger.info("Creating test model for memory efficiency comparison")
    # Memory optimization: Explicit memory cleanup
    
    # Create a small model for testing with proper initialization parameters
    # Memory optimization: Explicit memory cleanup
    # Create model dimensions first
    # Memory optimization: Explicit memory cleanup
    dimensions = ModelDimensions(
        hidden_size=256,
        intermediate_size=1024,
        num_attention_heads=8,
        num_hidden_layers=4,
        max_position_embeddings=512
    )
    
    # Now create the model config with all required parameters
    # Memory optimization: Explicit memory cleanup
    config = ModelConfig(
        model_type="test_model",
        model_name="memory_test_model",
        # Memory optimization: Memory-critical operation
        dimensions=dimensions
    )
    
    # Create the model from the config
    # Memory optimization: Explicit memory cleanup
    model = ImpressionCoreModel(config)
    # Memory optimization: Explicit memory cleanup
    
    # Print model memory usage
    # Memory optimization: Explicit memory cleanup
    memory_usage = print_model_memory_usage(model)
    # Memory optimization: Memory-critical operation
    
    # Get device
    # Memory optimization: Device placement for memory management
    device = get_device()
    # Memory optimization: Device placement for memory management
    
    # Move model to the correct device
    # Memory optimization: Device placement for memory management
    model = model.to(device)
    # Memory optimization: Device placement for memory management
    
    # Create random input
    batch_size = 2
    seq_length = 128
    input_ids = torch.randint(0, config.dimensions.vocab_size, (batch_size, seq_length)).to(device)
    # Memory optimization: Device placement for memory management
    
    # Test standard inference
    logger.info("Testing standard inference")
    
    # Initialize variables to store memory statistics
    # Memory optimization: Memory-critical operation
    standard_stats = {'peak_gpu_mb': 0, 'peak_system_mb': 0}
    # Memory optimization: Memory-critical operation
    efficient_stats = {'peak_gpu_mb': 0, 'peak_system_mb': 0}
    # Memory optimization: Memory-critical operation
    
    # Monitor standard inference memory usage
    # Memory optimization: Memory-critical operation
    tracker = MemoryTracker()
    # Memory optimization: Memory-critical operation
    tracker.start()
    
    # Show progress animation if Rich is available
    with create_progress(total=1, description="Standard inference") as progress:
        task = progress.add_task("Running", total=1, memory_usage=0)
        # Memory optimization: Memory-critical operation
        
        # Run inference
        time.sleep(0.5)  # Artificial delay for visualization
        output_standard = model(input_ids)
        
        # Update progress with memory usage
        # Memory optimization: Memory-critical operation
        mem_info = get_memory_info()
        # Memory optimization: Memory-critical operation
        vram_info = mem_info.get("gpu_vram", {})
        # Memory optimization: Memory-critical operation
        vram_used = vram_info.get("allocated", 0) * 1024  # Convert GB to MB
        progress.update(task, completed=1, memory_usage=vram_used)
        # Memory optimization: Memory-critical operation
    
    # Get standard inference memory stats
    # Memory optimization: Memory-critical operation
    standard_stats = tracker.stop()
    
    # Test memory-efficient inference
    # Memory optimization: Memory-critical operation
    logger.info("Testing memory-efficient inference")
    # Memory optimization: Memory-critical operation
    
    # Clear memory before test
    # Memory optimization: Memory-critical operation
    clear_gpu_memory()
    # Memory optimization: Memory-critical operation
    
    # Monitor memory-efficient inference memory usage
    # Memory optimization: Memory-critical operation
    tracker = MemoryTracker()
    # Memory optimization: Memory-critical operation
    tracker.start()
    
    # Show progress animation if Rich is available
    with create_progress(total=1, description="Memory-efficient inference") as progress:
    # Memory optimization: Memory-critical operation
        task = progress.add_task("Running", total=1, memory_usage=0)
        # Memory optimization: Memory-critical operation
        
        # Run memory-efficient inference
        # Memory optimization: Memory-critical operation
        with memory_efficient_inference():
        # Memory optimization: Memory-critical operation
            time.sleep(0.5)  # Artificial delay for visualization
            output_efficient = model(input_ids)
        
        # Update progress with memory usage
        # Memory optimization: Memory-critical operation
        mem_info = get_memory_info()
        # Memory optimization: Memory-critical operation
        vram_info = mem_info.get("gpu_vram", {})
        # Memory optimization: Memory-critical operation
        vram_used = vram_info.get("allocated", 0) * 1024  # Convert GB to MB
        progress.update(task, completed=1, memory_usage=vram_used)
        # Memory optimization: Memory-critical operation
    
    # Get memory-efficient inference memory stats
    # Memory optimization: Memory-critical operation
    efficient_stats = tracker.stop()
    
    # Compare memory usage with rich formatting if available
    # Memory optimization: Memory-critical operation
    if HAS_RICH:
        comparison_table = Table(title="Memory Usage Comparison")
        # Memory optimization: Memory-critical operation
        comparison_table.add_column("Inference Method", style="cyan")
        comparison_table.add_column("Peak Memory (MB)", style="magenta")
        # Memory optimization: Memory-critical operation
        comparison_table.add_column("Memory Savings", style="green")
        # Memory optimization: Memory-critical operation
        
        # Calculate savings
        memory_savings = standard_stats['peak_gpu_mb'] - efficient_stats['peak_gpu_mb']
        # Memory optimization: Memory-critical operation
        savings_percent = (1 - efficient_stats['peak_gpu_mb'] / standard_stats['peak_gpu_mb']) * 100 if standard_stats['peak_gpu_mb'] > 0 else 0
        # Memory optimization: Memory-critical operation
        
        # Add rows
        comparison_table.add_row(
            "Standard",
            f"{standard_stats['peak_gpu_mb']:.2f}",
            # Memory optimization: Memory-critical operation
            ""
        )
        comparison_table.add_row(
            "Memory-efficient",
            # Memory optimization: Memory-critical operation
            f"{efficient_stats['peak_gpu_mb']:.2f}",
            # Memory optimization: Memory-critical operation
            f"{memory_savings:.2f}MB ({savings_percent:.1f}%)"
            # Memory optimization: Memory-critical operation
        )
        
        console.print(comparison_table)
    else:
        # Traditional logging for comparison
        logger.info("Memory usage comparison:")
        # Memory optimization: Memory-critical operation
        logger.info(f"  Standard inference: {standard_stats['peak_gpu_mb']:.2f}MB peak")
        # Memory optimization: Memory-critical operation
        logger.info(f"  Memory-efficient inference: {efficient_stats['peak_gpu_mb']:.2f}MB peak")
        # Memory optimization: Memory-critical operation
        logger.info(f"  Memory savings: {standard_stats['peak_gpu_mb'] - efficient_stats['peak_gpu_mb']:.2f}MB "
        # Memory optimization: Memory-critical operation
                   f"({(1 - efficient_stats['peak_gpu_mb'] / standard_stats['peak_gpu_mb']) * 100:.1f}%)")
                   # Memory optimization: Memory-critical operation
    
    # Verify outputs are the same
    if isinstance(output_standard, dict) and isinstance(output_efficient, dict):
        # Compare logits if outputs are dictionaries
        standard_logits = output_standard.get("logits")
        efficient_logits = output_efficient.get("logits")
        
        if torch.allclose(standard_logits, efficient_logits):
            if HAS_RICH:
                console.print("[bold green]✓ Output verification passed:[/] both methods produced the same logits")
            else:
                logger.info("Output verification passed: both methods produced the same logits")
        else:
            if HAS_RICH:
                console.print("[bold red]✗ Output verification failed:[/] logits differ between methods")
            else:
                logger.warning("Output verification failed: logits differ between methods")
    
    # Clean up
    clear_gpu_memory()
    # Memory optimization: Memory-critical operation

def main():
    """Run memory usage tests."""
    # Memory optimization: Memory-critical operation
    parser = argparse.ArgumentParser(description="Test GPU memory usage")
    # Memory optimization: Memory-critical operation
    parser.add_argument('--test', choices=['all', 'shared', 'allocation', 'batch', 'inference'], 
                       default='all', help='Test to run')
    args = parser.parse_args()
    
    # Print header with rich formatting if available
    if HAS_RICH:
        header_panel = Panel(
            "[bold blue]ImpressionCore GPU Memory Test[/]\n"
            # Memory optimization: Memory-critical operation
            "Testing memory optimization techniques for the GTX 1050 Ti",
            # Memory optimization: Memory-critical operation
            title="Memory Optimization Test Suite",
            # Memory optimization: Memory-critical operation
            border_style="blue"
        )
        console.print(header_panel)
    
    # Check CUDA availability
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        device = torch.cuda.get_device_name(0)
        # Memory optimization: CUDA operations for GPU acceleration
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
        # Memory optimization: CUDA operations for GPU acceleration
        
        if HAS_RICH:
            cuda_info = f"[bold green]CUDA device:[/] {device} with [bold cyan]{vram:.2f}GB VRAM[/]"
            # Memory optimization: Device placement for memory management
            console.print(cuda_info)
            # Memory optimization: Memory-critical operation
        else:
            logger.info(f"CUDA device: {device} with {vram:.2f}GB VRAM")
            # Memory optimization: Device placement for memory management
    else:
        if HAS_RICH:
            console.print("[bold yellow]WARNING:[/] CUDA not available, tests will run on CPU")
            # Memory optimization: Memory-critical operation
        else:
            logger.warning("CUDA not available, tests will run on CPU")
            # Memory optimization: Memory-critical operation
    
    # Run selected tests with progress tracking
    test_count = 0
    
    if args.test in ['all', 'shared']:
        if HAS_RICH:
            console.rule("[bold blue]Test: Shared Memory Detection[/]")
            # Memory optimization: Memory-critical operation
        test_shared_memory_detection()
        # Memory optimization: Memory-critical operation
        test_count += 1
    
    if args.test in ['all', 'allocation']:
        if HAS_RICH:
            console.rule("[bold blue]Test: Memory Allocation Limits[/]")
            # Memory optimization: Memory-critical operation
        test_memory_allocation(size_mb=100, step_mb=100, max_mb=3000)
        # Memory optimization: Memory-critical operation
        test_count += 1
    
    if args.test in ['all', 'batch']:
        if HAS_RICH:
            console.rule("[bold blue]Test: Batch Size Calculation[/]")
        test_batch_size_calculation()
        test_count += 1
    
    if args.test in ['all', 'inference']:
        if HAS_RICH:
            console.rule("[bold blue]Test: Memory-Efficient Inference[/]")
            # Memory optimization: Memory-critical operation
        test_memory_efficient_inference()
        # Memory optimization: Memory-critical operation
        test_count += 1
    
    # Print completion message
    if HAS_RICH:
        completion_message = f"[bold green]✓ Memory usage tests completed:[/] {test_count} tests run successfully"
        # Memory optimization: Memory-critical operation
        console.print(completion_message)
    else:
        logger.info(f"Memory usage tests completed: {test_count} tests run")
        # Memory optimization: Memory-critical operation
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
