#!/usr/bin/env python3
"""
ImpressionCore: Attention Benchmark

Module for attention benchmark functionality in the ImpressionCore framework.

File: modules\attention\attention_benchmark.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, memory-critical, 2025]
Dependencies: [torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements attention benchmark functionality for the
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
from modules.attention.attention_benchmark import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
import time
import math
import argparse
from typing import Optional, Dict, List, Tuple
import warnings

# Try to import matplotlib for plotting, but make it optional
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn(
        "matplotlib is not installed. Visualizations will be disabled. "
        "Install with: pip install matplotlib"
    )

from sparse_attention import (
    LocalAttention,
    MemoryEfficientAttention,
    # Memory optimization: Memory-critical operation
    AxialAttention,
    AttentionRouter
)


def memory_usage_report() -> Dict[str, float]:
# Memory optimization: Memory-critical operation
    """
    Reports current memory usage statistics for PyTorch tensors.
    # Memory optimization: Memory-critical operation
    
    Returns:
        Dict containing memory usage statistics in MB
        # Memory optimization: Memory-critical operation
    """
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        # Get statistics from CUDA
        # Memory optimization: Memory-critical operation
        allocated = torch.cuda.memory_allocated() / 1024**2
        # Memory optimization: CUDA operations for GPU acceleration
        reserved = torch.cuda.memory_reserved() / 1024**2
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Some older PyTorch versions might not have max_memory_allocated
        # Memory optimization: Memory-critical operation
        try:
            max_allocated = torch.cuda.max_memory_allocated() / 1024**2
            # Memory optimization: CUDA operations for GPU acceleration
        except AttributeError:
            max_allocated = allocated  # Fallback to current allocation
        
        return {
            "allocated_mb": allocated,
            "reserved_mb": reserved,
            "max_allocated_mb": max_allocated
        }
    else:
        # CPU mode - can't measure GPU memory as easily, just provide placeholder
        # Memory optimization: Memory-critical operation
        return {"allocated_mb": 0, "reserved_mb": 0, "max_allocated_mb": 0}


def benchmark_attention(
    attention_module: torch.nn.Module,
    batch_size: int,
    seq_length: int,
    hidden_size: int,
    n_runs: int = 5,
    use_cuda: bool = torch.cuda.is_available()
    # Memory optimization: CUDA operations for GPU acceleration
) -> Dict[str, float]:
    """
    Benchmark attention module for performance and memory usage.
    # Memory optimization: Memory-critical operation
    
    Args:
        attention_module: The attention module to benchmark
        batch_size: Batch size for input tensors
        seq_length: Sequence length for input tensors
        hidden_size: Hidden dimension size
        n_runs: Number of runs for averaging performance
        use_cuda: Whether to use CUDA (if available)
        # Memory optimization: Memory-critical operation
        
    Returns:
        Dict containing benchmark results
    """
    device = torch.device("cuda" if use_cuda and torch.cuda.is_available() else "cpu")
    # Memory optimization: CUDA operations for GPU acceleration
    
    # Move module to device
    # Memory optimization: Device placement for memory management
    attention_module = attention_module.to(device)
    # Memory optimization: Device placement for memory management
    
    # Create random input tensors
    hidden_states = torch.randn(batch_size, seq_length, hidden_size, device=device)
    # Memory optimization: Device placement for memory management
    
    # Optional attention mask (all 1s - no masking)
    attention_mask = torch.ones(batch_size, seq_length, device=device)
    # Memory optimization: Device placement for memory management
    
    # Record initial memory
    # Memory optimization: Memory-critical operation
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        try:
            torch.cuda.reset_peak_memory_stats()
            # Memory optimization: CUDA operations for GPU acceleration
        except AttributeError:
            # Older PyTorch versions might not have this method
            pass
    initial_mem = memory_usage_report()
    # Memory optimization: Memory-critical operation
    
    # Warmup - handle different module types
    with torch.no_grad():
    # Memory optimization: Disable gradient computation to save memory
        if isinstance(attention_module, torch.nn.MultiheadAttention):
            # PyTorch MultiheadAttention expects separate key, query, value tensors
            _ = attention_module(hidden_states, hidden_states, hidden_states)
        else:
            # Our custom attention implementations take hidden_states and attention_mask
            _ = attention_module(hidden_states, attention_mask)
    
    # Benchmark runs
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        torch.cuda.synchronize()
        # Memory optimization: CUDA operations for GPU acceleration
    start_time = time.time()
    
    with torch.no_grad():
    # Memory optimization: Disable gradient computation to save memory
        for _ in range(n_runs):
            if isinstance(attention_module, torch.nn.MultiheadAttention):
                _ = attention_module(hidden_states, hidden_states, hidden_states)
            else:
                _ = attention_module(hidden_states, attention_mask)
            
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        torch.cuda.synchronize()
        # Memory optimization: CUDA operations for GPU acceleration
    end_time = time.time()
    
    # Record final memory
    # Memory optimization: Memory-critical operation
    final_mem = memory_usage_report()
    # Memory optimization: Memory-critical operation
    
    # Calculate results
    avg_time = (end_time - start_time) / n_runs
    
    # For CPU mode, we can't accurately measure GPU memory increase
    # Memory optimization: Memory-critical operation
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        mem_increase = final_mem["max_allocated_mb"] - initial_mem["allocated_mb"]
    else:
        mem_increase = 0  # Placeholder for CPU mode
    
    return {
        "avg_time_ms": avg_time * 1000,
        "memory_used_mb": mem_increase,
        # Memory optimization: Memory-critical operation
        "seq_length": seq_length,
        "hidden_size": hidden_size,
        "batch_size": batch_size,
        "device": str(device),
        # Memory optimization: Device placement for memory management
    }


def compare_attention_methods(
    hidden_size: int = 768,
    batch_size: int = 1,
    sequence_lengths: List[int] = [128, 512, 1024, 2048, 4096]
) -> Dict[str, List[Dict[str, float]]]:
    """
    Compare different attention methods across various sequence lengths.
    
    Args:
        hidden_size: Hidden dimension size
        batch_size: Batch size for input tensors
        sequence_lengths: List of sequence lengths to test
        
    Returns:
        Dict mapping attention method names to lists of benchmark results
    """
    results = {}
    
    device_name = "CUDA" if torch.cuda.is_available() else "CPU"
    # Memory optimization: CUDA operations for GPU acceleration
    print(f"Running benchmarks on {device_name}...")
    # Memory optimization: Device placement for memory management
    
    # For 2D data benchmarking
    is_2d_square = lambda x: int(math.sqrt(x)) ** 2 == x
    
    for seq_length in sequence_lengths:
        print(f"Testing sequence length: {seq_length}")
        
        # Standard attention (only for shorter sequences to avoid OOM)
        if seq_length <= 512:
            try:
                print("  Testing Standard Attention...")
                std_attention = torch.nn.MultiheadAttention(hidden_size, num_heads=8, batch_first=True)
                std_result = benchmark_attention(std_attention, batch_size, seq_length, hidden_size)
                results.setdefault("Standard Attention", []).append(std_result)
                print(f"    Time: {std_result['avg_time_ms']:.2f}ms, Memory: {std_result['memory_used_mb']:.2f}MB")
                # Memory optimization: Memory-critical operation
            except RuntimeError as e:
                print(f"    Error with Standard Attention: {e}")
        
        # Local attention
        try:
            print("  Testing Local Attention...")
            window_size = min(128, seq_length // 4)
            local_attention = LocalAttention(hidden_size, window_size=window_size)
            local_result = benchmark_attention(local_attention, batch_size, seq_length, hidden_size)
            results.setdefault("Local Attention", []).append(local_result)
            print(f"    Time: {local_result['avg_time_ms']:.2f}ms, Memory: {local_result['memory_used_mb']:.2f}MB")
            # Memory optimization: Memory-critical operation
        except RuntimeError as e:
            print(f"    Error with Local Attention: {e}")
        
        # Memory-efficient attention
        # Memory optimization: Memory-critical operation
        try:
            print("  Testing Memory-Efficient Attention...")
            # Memory optimization: Memory-critical operation
            chunk_size = min(512, seq_length // 2)
            memory_attention = MemoryEfficientAttention(hidden_size, chunk_size=chunk_size)
            # Memory optimization: Memory-critical operation
            memory_result = benchmark_attention(memory_attention, batch_size, seq_length, hidden_size)
            # Memory optimization: Memory-critical operation
            results.setdefault("Memory-Efficient Attention", []).append(memory_result)
            # Memory optimization: Memory-critical operation
            print(f"    Time: {memory_result['avg_time_ms']:.2f}ms, Memory: {memory_result['memory_used_mb']:.2f}MB")
            # Memory optimization: Memory-critical operation
        except RuntimeError as e:
            print(f"    Error with Memory-Efficient Attention: {e}")
            # Memory optimization: Memory-critical operation
        
        # Axial attention (only if sequence length is a perfect square for simplicity)
        if is_2d_square(seq_length):
            try:
                print("  Testing Axial Attention...")
                height = width = int(math.sqrt(seq_length))
                axial_attention = AxialAttention(hidden_size, height, width)
                axial_result = benchmark_attention(axial_attention, batch_size, seq_length, hidden_size)
                results.setdefault("Axial Attention", []).append(axial_result)
                print(f"    Time: {axial_result['avg_time_ms']:.2f}ms, Memory: {axial_result['memory_used_mb']:.2f}MB")
                # Memory optimization: Memory-critical operation
            except RuntimeError as e:
                print(f"    Error with Axial Attention: {e}")
                
        # Clear cache between runs
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
    
    return results


def plot_results(results: Dict[str, List[Dict[str, float]]]):
    """
    Plot benchmark results for different attention mechanisms.
    
    Args:
        results: Dictionary mapping attention method names to lists of benchmark results
    """
    if not MATPLOTLIB_AVAILABLE:
        print("\nCannot generate plots: matplotlib is not installed.")
        print("To enable visualization, install matplotlib: pip install matplotlib")
        return
        
    plt.figure(figsize=(14, 10))
    
    # Plot 1: Execution Time vs Sequence Length
    plt.subplot(2, 1, 1)
    for method, method_results in results.items():
        seq_lengths = [r["seq_length"] for r in method_results]
        times = [r["avg_time_ms"] for r in method_results]
        plt.plot(seq_lengths, times, marker='o', label=method)
    
    plt.xlabel('Sequence Length')
    plt.ylabel('Average Execution Time (ms)')
    plt.title('Attention Mechanisms: Execution Time vs Sequence Length')
    plt.grid(True)
    plt.legend()
    plt.xscale('log')
    plt.yscale('log')
    
    # Plot 2: Memory Usage vs Sequence Length
    # Memory optimization: Memory-critical operation
    plt.subplot(2, 1, 2)
    for method, method_results in results.items():
        seq_lengths = [r["seq_length"] for r in method_results]
        memory = [r["memory_used_mb"] for r in method_results]
        # Memory optimization: Memory-critical operation
        plt.plot(seq_lengths, memory, marker='o', label=method)
        # Memory optimization: Memory-critical operation
    
    plt.xlabel('Sequence Length')
    plt.ylabel('Memory Usage (MB)')
    # Memory optimization: Memory-critical operation
    plt.title('Attention Mechanisms: Memory Usage vs Sequence Length')
    # Memory optimization: Memory-critical operation
    plt.grid(True)
    plt.legend()
    plt.xscale('log')
    plt.yscale('log')
    
    plt.tight_layout()
    plt.savefig("attention_benchmark_results.png")
    print("\nBenchmark visualization saved to: attention_benchmark_results.png")
    plt.show()


def demonstrate_attention_router():
    """
    Demonstrate the automatic attention mechanism selection based on sequence length and memory.
    # Memory optimization: Memory-critical operation
    """
    print("\nDemonstrating AttentionRouter with different inputs:")
    
    test_cases = [
        {"seq_length": 128, "hidden_size": 768, "desc": "Short sequence"},
        {"seq_length": 1024, "hidden_size": 768, "desc": "Medium sequence"},
        {"seq_length": 4096, "hidden_size": 768, "desc": "Long sequence"},
        {"seq_length": 1024, "hidden_size": 768, "is_2d_data": True, "height": 32, "width": 32, "desc": "2D data"}
    ]
    
    for case in test_cases:
        desc = case.pop("desc")
        print(f"\n{desc}:")
        try:
            attention_module = AttentionRouter.select_attention_mechanism(**case)
            print(f"  Selected: {attention_module.__class__.__name__}")
            
            # Additional info for specialized modules
            if hasattr(attention_module, 'window_size'):
                print(f"  Window size: {attention_module.window_size}")
            if hasattr(attention_module, 'chunk_size'):
                print(f"  Chunk size: {attention_module.chunk_size}")
                
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark different attention mechanisms")
    parser.add_argument("--hidden-size", type=int, default=768, help="Hidden dimension size")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size")
    parser.add_argument("--cpu-only", action="store_true", help="Force CPU usage even if CUDA is available")
    # Memory optimization: Memory-critical operation
    parser.add_argument("--no-plot", action="store_true", help="Skip plotting results")
    args = parser.parse_args()
    
    # Set the device based on args
    # Memory optimization: Device placement for memory management
    device = torch.device("cpu" if args.cpu_only else "cuda" if torch.cuda.is_available() else "cpu")
    # Memory optimization: CUDA operations for GPU acceleration
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        # Memory optimization: CUDA operations for GPU acceleration
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        # Memory optimization: CUDA operations for GPU acceleration
    else:
        print("Using CPU")
    
    # For NVIDIA GTX 1050 Ti (4GB VRAM), adjust sequence lengths to avoid OOM
    sequence_lengths = [128, 256, 512, 1024, 2048, 4096]
    
    # Show attention router in action
    demonstrate_attention_router()
    
    # Run benchmarks
    print("\nRunning benchmarks...")
    results = compare_attention_methods(
        hidden_size=args.hidden_size,
        batch_size=args.batch_size,
        sequence_lengths=sequence_lengths
    )
    
    # Plot results if matplotlib is available and plotting isn't disabled
    if not args.no_plot:
        try:
            plot_results(results)
        except Exception as e:
            print(f"Could not generate plots: {e}")
    
    # Always show text summary of results
    print("\nBenchmark complete! Results summary:")
    
    # Create a more detailed text-based visualization for CLI
    print("\n{:<25} {:<15} {:<15} {:<15}".format(
        "Attention Method", "Seq Length", "Time (ms)", "Memory (MB)"))
        # Memory optimization: Memory-critical operation
    print("-" * 75)
    
    for method, method_results in results.items():
        for result in method_results:
            print("{:<25} {:<15} {:<15.2f} {:<15.2f}".format(
                method,
                result['seq_length'],
                result['avg_time_ms'],
                result['memory_used_mb']
                # Memory optimization: Memory-critical operation
            ))
        print("-" * 75)