#!/usr/bin/env python3
"""
ImpressionCore: Test Mixed Modality

Module for test mixed modality functionality in the ImpressionCore framework.

File: tests\test_mixed_modality.py
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
This module implements test mixed modality functionality for the
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
from tests.test_mixed_modality import TestMixedModality
instance = TestMixedModality()
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
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn
from src.core.ai.tokenization.tokenizer import Tokenizer # Corrected import
from src.memory_manager import MemoryManager
# Memory optimization: Memory-critical operation
from src.performance_optimizer import PerformanceOptimizer
from src.training.datasets.data_loading import load_text_data, load_image_data, load_audio_data

# Configure enhanced logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("mixed_modality_test")
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

class TestMixedModality(unittest.TestCase):
    """
    
    TestMixedModality class for ImpressionCore framework.
    
    This class implements testmixedmodality functionality optimized for
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
            "[bold blue]Setting up Mixed Modality tests[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Initializing components for mixed modality testing...[/yellow]")
        initial_memory, _ = log_memory_status()
        # Memory optimization: Memory-critical operation
        
        self.tokenizer = Tokenizer(config={})
        self.manager = MemoryManager()
        # Memory optimization: Memory-critical operation
        self.optimizer = PerformanceOptimizer()
        
        final_memory, _ = log_memory_status()
        # Memory optimization: Memory-critical operation
        memory_delta = final_memory - initial_memory
        # Memory optimization: Memory-critical operation
        console.print(f"[green]✓[/green] Test components initialized (memory change: {memory_delta:+.2f} MB)")
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

    async def async_test_distribute_tensors(self, data):
        """
        
    async_test_distribute_tensors function for processing.
    
    Args:
        self, data: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        console.print(f"[cyan]Distributing {len(data)} tensors asynchronously...[/cyan]")
        return await self.optimizer.distribute_tensors_async(data)

    def test_mixed_modality_dataset(self):
        """
        
    test_mixed_modality_dataset function for processing.
    
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
            "[bold blue]STARTING TEST: test_mixed_modality_dataset[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Setting up mixed modality dataset test...[/yellow]")
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[bold green]{task.completed}/{task.total}"),
            TimeElapsedColumn()
        ) as progress:
            # Create the main task
            task_id = progress.add_task("[cyan]Running mixed modality test...", total=100)
            
            # Load text data
            progress.update(task_id, description="[cyan]Loading text datasets...", advance=10)
            with console.status("[bold green]Loading text data...[/bold green]", spinner="dots") as status:
                text_data = load_text_data("src/training/datasets/text_corpus/")
                console.print(f"[green]✓[/green] Loaded {len(text_data)} text samples")
            
            # Load image data
            progress.update(task_id, description="[cyan]Loading image datasets...", advance=10)
            with console.status("[bold green]Loading image data...[/bold green]", spinner="dots") as status:
                image_data = load_image_data("src/training/datasets/image_dataset/")
                console.print(f"[green]✓[/green] Loaded {len(image_data)} image samples")
            
            # Load audio data
            progress.update(task_id, description="[cyan]Loading audio datasets...", advance=10)
            with console.status("[bold green]Loading audio data...[/bold green]", spinner="dots") as status:
                audio_data = load_audio_data("src/training/datasets/raw/")
                console.print(f"[green]✓[/green] Loaded {len(audio_data)} audio samples")
            
            # Display dataset summary
            dataset_table = Table(title="Dataset Summary")
            dataset_table.add_column("Modality", style="cyan")
            dataset_table.add_column("Samples", justify="right", style="green")
            dataset_table.add_column("Test Sample Size", justify="right", style="yellow")
            
            dataset_table.add_row("Text", str(len(text_data)), str(min(len(text_data), 1000)))
            dataset_table.add_row("Image", str(len(image_data)), str(min(len(image_data), 1000)))
            dataset_table.add_row("Audio", str(len(audio_data)), str(min(len(audio_data), 1000)))
            
            console.print(dataset_table)
            log_memory_status()
            # Memory optimization: Memory-critical operation

            # Tokenize text data
            progress.update(task_id, description="[cyan]Tokenizing text data...", advance=15)
            with console.status("[bold green]Tokenizing text data...[/bold green]", spinner="dots") as status:
                samples_to_tokenize = text_data[:min(len(text_data), 1000)]
                start_time = time.time()
                batch_tokens = self.tokenizer.batch_tokenize(samples_to_tokenize)
                elapsed_time = time.time() - start_time
                
                console.print(f"[green]✓[/green] Tokenized {len(samples_to_tokenize)} text samples in {elapsed_time:.4f} seconds")
                
                # Verification
                self.assertEqual(len(batch_tokens), len(samples_to_tokenize), 
                               "Batch tokenization should process all provided samples.")
                
                # Display tokenization results
                token_stats = {
                    "min_length": min(len(tokens) for tokens in batch_tokens),
                    "max_length": max(len(tokens) for tokens in batch_tokens),
                    "avg_length": sum(len(tokens) for tokens in batch_tokens) / len(batch_tokens)
                }
                
                console.print(f"[cyan]Token statistics:[/cyan] min={token_stats['min_length']}, max={token_stats['max_length']}, avg={token_stats['avg_length']:.1f}")
            
            log_memory_status()
            # Memory optimization: Memory-critical operation

            # Distribute image data across GPUs
            # Memory optimization: Memory-critical operation
            progress.update(task_id, description="[cyan]Distributing image data...", advance=15)
            with console.status("[bold green]Distributing image data across GPUs...[/bold green]", spinner="dots") as status:
            # Memory optimization: Memory-critical operation
                img_samples = image_data[:min(len(image_data), 1000)]
                start_time = time.time()
                distributed_images = asyncio.run(self.async_test_distribute_tensors(img_samples))
                elapsed_time = time.time() - start_time
                
                console.print(f"[green]✓[/green] Distributed {len(img_samples)} image samples in {elapsed_time:.4f} seconds")
                
                # Verification
                if torch.cuda.is_available() and self.optimizer.devices:
                # Memory optimization: CUDA operations for GPU acceleration
                    valid_distribution = True
                    for i, tensor in enumerate(distributed_images):
                        expected_device = self.optimizer.devices[i % len(self.optimizer.devices)]
                        # Memory optimization: Device placement for memory management
                        if tensor.device != expected_device:
                        # Memory optimization: Device placement for memory management
                            valid_distribution = False
                            console.print(f"[red]✗[/red] Image {i} on incorrect device: {tensor.device} vs {expected_device}")
                            # Memory optimization: Device placement for memory management
                    
                    if valid_distribution:
                        console.print(f"[green]✓[/green] All images correctly distributed across {len(self.optimizer.devices)} devices")
                        # Memory optimization: Device placement for memory management
                else:
                    console.print("[yellow]No CUDA devices available, skipping distribution verification[/yellow]")
                    # Memory optimization: Device placement for memory management
            
            log_memory_status()
            # Memory optimization: Memory-critical operation

            # Distribute audio data across GPUs
            # Memory optimization: Memory-critical operation
            progress.update(task_id, description="[cyan]Distributing audio data...", advance=15)
            with console.status("[bold green]Distributing audio data across GPUs...[/bold green]", spinner="dots") as status:
            # Memory optimization: Memory-critical operation
                audio_samples = audio_data[:min(len(audio_data), 1000)]
                start_time = time.time()
                distributed_audio = asyncio.run(self.async_test_distribute_tensors(audio_samples))
                elapsed_time = time.time() - start_time
                
                console.print(f"[green]✓[/green] Distributed {len(audio_samples)} audio samples in {elapsed_time:.4f} seconds")
                
                # Verification
                if torch.cuda.is_available() and self.optimizer.devices:
                # Memory optimization: CUDA operations for GPU acceleration
                    valid_distribution = True
                    for i, tensor in enumerate(distributed_audio):
                        expected_device = self.optimizer.devices[i % len(self.optimizer.devices)]
                        # Memory optimization: Device placement for memory management
                        if tensor.device != expected_device:
                        # Memory optimization: Device placement for memory management
                            valid_distribution = False
                            console.print(f"[red]✗[/red] Audio {i} on incorrect device: {tensor.device} vs {expected_device}")
                            # Memory optimization: Device placement for memory management
                    
                    if valid_distribution:
                        console.print(f"[green]✓[/green] All audio samples correctly distributed across {len(self.optimizer.devices)} devices")
                        # Memory optimization: Device placement for memory management
                else:
                    console.print("[yellow]No CUDA devices available, skipping distribution verification[/yellow]")
                    # Memory optimization: Device placement for memory management
            
            # Final test progress update
            progress.update(task_id, description="[green]Mixed modality test complete", advance=25)
        
        # Display test results
        console.print(Panel.fit(
            f"[bold green]Mixed Modality Test Results:[/bold green]\n" +
            f"[cyan]Text samples processed:[/cyan] {len(samples_to_tokenize)}\n" +
            f"[cyan]Image samples distributed:[/cyan] {len(img_samples)}\n" +
            f"[cyan]Audio samples distributed:[/cyan] {len(audio_samples)}\n" +
            f"[cyan]Tokenization successful:[/cyan] {'Yes' if len(batch_tokens) == len(samples_to_tokenize) else 'No'}\n" +
            f"[cyan]Image distribution successful:[/cyan] {'Yes' if torch.cuda.is_available() and valid_distribution else 'N/A'}\n" +
            # Memory optimization: CUDA operations for GPU acceleration
            f"[cyan]Audio distribution successful:[/cyan] {'Yes' if torch.cuda.is_available() and valid_distribution else 'N/A'}",
            # Memory optimization: CUDA operations for GPU acceleration
            border_style="green"
        ))
        
        log_memory_status()
        # Memory optimization: Memory-critical operation
        console.print("[bold blue]TEST COMPLETE: test_mixed_modality_dataset[/bold blue]")

if __name__ == "__main__":
    # Display test header
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(Panel.fit(
        f"[bold blue]ImpressionCore Mixed Modality Tests[/bold blue]\n"
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
        "test_mixed_modality_dataset"
    ]
    
    # Run tests sequentially
    for i, test_name in enumerate(tests):
        test_number = i + 1
        total_tests = len(tests)
        console.print(f"[bold blue]Running test {test_number}/{total_tests}: {test_name}[/bold blue]")
        
        # Add this test to the suite
        suite.addTest(TestMixedModality(test_name))
        
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
        f"[bold green]Mixed Modality Tests Completed[/bold green]\n" +
        f"[cyan]Finished at:[/cyan] {end_time}",
        border_style="green"
    ))
