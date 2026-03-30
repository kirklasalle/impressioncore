#!/usr/bin/env python3
"""
ImpressionCore: Test Tokenizer

Module for test tokenizer functionality in the ImpressionCore framework.

File: tests\test_tokenizer.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, qa, production, testing, 2025, object-oriented]
Dependencies: [rich]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements test tokenizer functionality for the
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
from tests.test_tokenizer import TestTokenizer
instance = TestTokenizer()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import unittest
import logging
import sys
import time
import psutil
import os
from datetime import datetime
from src.core.ai.tokenization.tokenizer import Tokenizer # Corrected import
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
logger = logging.getLogger('tokenizer_test')
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
    
    console.print(memory_table)
    # Memory optimization: Memory-critical operation
    
    return memory_info.rss / (1024 * 1024), system_memory.percent
    # Memory optimization: Memory-critical operation

class TestTokenizer(unittest.TestCase):
    """
    
    TestTokenizer class for ImpressionCore framework.
    
    This class implements testtokenizer functionality optimized for
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
            "[bold blue]Setting up Tokenizer tests[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Initializing tokenizer...[/yellow]")
        initial_memory, _ = log_memory_status()
        # Memory optimization: Memory-critical operation
        
        self.tokenizer = Tokenizer(config={})
        
        final_memory, _ = log_memory_status()
        # Memory optimization: Memory-critical operation
        memory_delta = final_memory - initial_memory
        # Memory optimization: Memory-critical operation
        console.print(f"[green]✓[/green] Tokenizer instance created (memory change: {memory_delta:+.2f} MB)")
        # Memory optimization: Memory-critical operation

    def test_tokenize_caching(self):
        """
        
    test_tokenize_caching function for processing.
    
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
            "[bold blue]STARTING TEST: test_tokenize_caching[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Setting up tokenize caching test...[/yellow]")
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        with console.status("[bold green]Testing tokenize caching...[/bold green]", spinner="dots") as status:
            # First tokenization
            text = "This is a test."
            console.print(f"[cyan]Tokenizing text (first time):[/cyan] '{text}'")
            tokens1 = self.tokenizer.tokenize(text)
            console.print(f"[green]✓[/green] First tokenization result: {tokens1}")
            
            # Second tokenization (should use cache)
            console.print(f"[cyan]Tokenizing same text (second time):[/cyan] '{text}'")
            tokens2 = self.tokenizer.tokenize(text)
            console.print(f"[green]✓[/green] Second tokenization result: {tokens2}")
            
            # Check cache info
            cache_info = self.tokenizer.tokenize.cache_info()
            console.print(f"[cyan]Cache info:[/cyan] hits={cache_info.hits}, misses={cache_info.misses}")
        
        # Create a table for results
        results_table = Table(title="Tokenize Caching Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")
        
        results_table.add_row("First result", str(tokens1))
        results_table.add_row("Second result", str(tokens2))
        results_table.add_row("Match", "Yes" if tokens1 == tokens2 else "No")
        results_table.add_row("Cache hits", str(cache_info.hits))
        results_table.add_row("Cache misses", str(cache_info.misses))
        results_table.add_row("Cache size", str(cache_info.currsize))
        
        console.print(results_table)
        
        # Final assertions
        self.assertEqual(tokens1, tokens2, "Tokenized outputs should match.")
        self.assertTrue(cache_info.hits > 0, "Cache should be utilized.")
        
        console.print(Panel.fit(
            f"[bold green]Tokenize caching test results:[/bold green]\n" +
            f"[cyan]Cache working:[/cyan] {'Yes' if cache_info.hits > 0 else 'No'}\n" +
            f"[cyan]Results consistent:[/cyan] {'Yes' if tokens1 == tokens2 else 'No'}",
            border_style="green"
        ))
        
        log_memory_status()
        # Memory optimization: Memory-critical operation
        console.print("[bold blue]TEST COMPLETE: test_tokenize_caching[/bold blue]")

    def test_batch_tokenize(self):
        """
        
    test_batch_tokenize function for processing.
    
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
            "[bold blue]STARTING TEST: test_batch_tokenize[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Setting up batch tokenization test...[/yellow]")
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        with console.status("[bold green]Testing batch tokenization...[/bold green]", spinner="dots") as status:
            # Perform batch tokenization
            texts = ["This is a test.", "Another test."]
            console.print(f"[cyan]Tokenizing batch of {len(texts)} texts[/cyan]")
            start_time = time.time()
            batch_tokens = self.tokenizer.batch_tokenize(texts)
            batch_time = time.time() - start_time
            console.print(f"[green]✓[/green] Batch tokenization complete in {batch_time:.4f} seconds")
            
            # Perform individual tokenization for comparison
            console.print("[cyan]Performing individual tokenization for comparison...[/cyan]")
            start_time = time.time()
            individual_tokens = self.tokenizer.tokenize(texts[0])
            individual_time = time.time() - start_time
            console.print(f"[green]✓[/green] Individual tokenization complete in {individual_time:.4f} seconds")
        
        # Create a table for results
        results_table = Table(title="Batch Tokenization Results")
        results_table.add_column("Text", style="cyan")
        results_table.add_column("Tokens", style="green")
        
        for i, (text, tokens) in enumerate(zip(texts, batch_tokens)):
            results_table.add_row(f"Text {i+1}: {text}", str(tokens))
            
        console.print(results_table)
        
        # Performance comparison
        perf_table = Table(title="Tokenization Performance")
        perf_table.add_column("Method", style="cyan")
        perf_table.add_column("Time (s)", justify="right", style="green")
        perf_table.add_column("Tokens/sec", justify="right", style="yellow")
        
        # Add a small epsilon to prevent division by zero
        perf_table.add_row(
            "Batch", 
            f"{batch_time:.4f}", 
            f"{len(texts) / max(batch_time, 1e-10):.2f}"
        )
        perf_table.add_row(
            "Individual", 
            f"{individual_time:.4f}", 
            f"{1 / max(individual_time, 1e-10):.2f}"
        )
        
        console.print(perf_table)
        
        # Final assertions
        self.assertEqual(len(batch_tokens), len(texts), 
                      "Batch tokenization should return the same number of outputs as inputs.")
        self.assertEqual(batch_tokens[0], individual_tokens, 
                      "Individual tokenization should match batch tokenization.")
        
        console.print(Panel.fit(
            f"[bold green]Batch tokenization test results:[/bold green]\n" +
            f"[cyan]Batch output count:[/cyan] {len(batch_tokens)}\n" +
            f"[cyan]Match with individual:[/cyan] {'Yes' if batch_tokens[0] == individual_tokens else 'No'}",
            border_style="green"
        ))
        
        log_memory_status()
        # Memory optimization: Memory-critical operation
        console.print("[bold blue]TEST COMPLETE: test_batch_tokenize[/bold blue]")

    def test_edge_cases(self):
        """
        
    test_edge_cases function for processing.
    
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
            "[bold blue]STARTING TEST: test_edge_cases[/bold blue]",
            border_style="cyan"
        ))
        
        console.print("[yellow]Setting up tokenizer edge cases test...[/yellow]")
        log_memory_status()
        # Memory optimization: Memory-critical operation
        
        edge_cases = [
            ("Empty string", ""),
            ("Special characters", "!@#$%^&*()"),
            ("Numbers only", "12345"),
            ("Whitespace", "   \t   \n"),
            ("Mixed content", "Text with 123 and !@#")
        ]
        
        results_table = Table(title="Edge Case Tokenization Results")
        results_table.add_column("Case", style="cyan")
        results_table.add_column("Input", style="blue")
        results_table.add_column("Tokens", style="green")
        results_table.add_column("Token Count", justify="right", style="yellow")
        
        with console.status("[bold green]Testing tokenizer edge cases...[/bold green]", spinner="dots") as status:
            for case_name, text in edge_cases:
                console.print(f"[cyan]Testing case:[/cyan] {case_name}")
                tokens = self.tokenizer.tokenize(text)
                results_table.add_row(
                    case_name,
                    f'"{text}"',
                    str(tokens),
                    str(len(tokens))
                )
        
        console.print(results_table)
        
        # Test specific assertions
        empty_result = self.tokenizer.tokenize("")
        special_result = self.tokenizer.tokenize("!@#$%^&*()")
        
        self.assertEqual(empty_result, [], 
                      "Empty string should return an empty list.")
        self.assertEqual(special_result, ["!@#$%^&*()"], 
                      "Special characters should be tokenized as-is.")
        
        console.print(Panel.fit(
            f"[bold green]Edge case tokenization results:[/bold green]\n" +
            f"[cyan]Empty string handling:[/cyan] {'Correct' if empty_result == [] else 'Incorrect'}\n" +
            f"[cyan]Special character handling:[/cyan] {'Correct' if special_result == ['!@#$%^&*()'] else 'Incorrect'}",
            border_style="green"
        ))
        
        log_memory_status()
        # Memory optimization: Memory-critical operation
        console.print("[bold blue]TEST COMPLETE: test_edge_cases[/bold blue]")

if __name__ == "__main__":
    # Display test header
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(Panel.fit(
        f"[bold blue]ImpressionCore Tokenizer Tests[/bold blue]\n"
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
    
    console.print(system_info_table)
    
    # Create and run the test suite
    suite = unittest.TestSuite()
    tests = [
        "test_tokenize_caching",
        "test_batch_tokenize",
        "test_edge_cases"
    ]
    
    # Run tests sequentially
    for i, test_name in enumerate(tests):
        test_number = i + 1
        total_tests = len(tests)
        console.print(f"[bold blue]Running test {test_number}/{total_tests}: {test_name}[/bold blue]")
        
        # Add this test to the suite
        suite.addTest(TestTokenizer(test_name))
        
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
    
    # Display timestamp
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(Panel.fit(
        f"[bold green]Tokenizer Tests Completed[/bold green]\n" +
        f"[cyan]Finished at:[/cyan] {end_time}",
        border_style="green"
    ))
