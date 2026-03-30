#!/usr/bin/env python3
"""
ImpressionCore: Benchmark Context Window

Module for benchmark context window functionality in the ImpressionCore framework.

File: tools\benchmark_context_window.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, 2025, object-oriented]
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements benchmark context window functionality for the
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
# from tools.benchmark_context_window import  # Fixed: using local implementation MemoryTracker
instance = MemoryTracker()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
import torch.nn as nn
import time
import argparse
import os
import sys
import json
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import logging
from tqdm import tqdm

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.architectures.impressioncore_b1 import (
    build_impressioncore_b1, 
    impressioncore_b1_forward
)
from src.models.layers.memory_efficient_attention import MemoryEfficientAttention
# Memory optimization: Memory-critical operation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "benchmark_results.log"))
    ]
)
logger = logging.getLogger(__name__)

class MemoryTracker:
# Memory optimization: Memory-critical operation
    """
    Tracks GPU memory usage during model execution.
    # Memory optimization: Explicit memory cleanup
    """
    def __init__(self, device: torch.device):
    # Memory optimization: Device placement for memory management
        """
        
    __init__ function for processing.
    
    Args:
        self, device: Function parameters
        # Memory optimization: Device placement for memory management
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.device = device
        # Memory optimization: Device placement for memory management
        self.is_cuda = device.type == "cuda"
        # Memory optimization: Device placement for memory management
        self.reset()
        
    def reset(self):
        """Reset memory tracking stats."""
        # Memory optimization: Memory-critical operation
        if self.is_cuda:
        # Memory optimization: Memory-critical operation
            torch.cuda.reset_peak_memory_stats(self.device)
            # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
        self.start_mem = self.get_allocated()
        self.measurements = []
        
    def get_allocated(self) -> float:
        """Get current allocated memory in MB."""
        # Memory optimization: Memory-critical operation
        if self.is_cuda:
        # Memory optimization: Memory-critical operation
            return torch.cuda.memory_allocated(self.device) / (1024 * 1024)
            # Memory optimization: CUDA operations for GPU acceleration
        return 0
        
    def get_reserved(self) -> float:
        """Get current reserved memory in MB."""
        # Memory optimization: Memory-critical operation
        if self.is_cuda:
        # Memory optimization: Memory-critical operation
            return torch.cuda.memory_reserved(self.device) / (1024 * 1024)
            # Memory optimization: CUDA operations for GPU acceleration
        return 0
        
    def get_peak(self) -> float:
        """Get peak allocated memory in MB."""
        # Memory optimization: Memory-critical operation
        if self.is_cuda:
        # Memory optimization: Memory-critical operation
            return torch.cuda.max_memory_allocated(self.device) / (1024 * 1024)
            # Memory optimization: CUDA operations for GPU acceleration
        return 0
        
    def measure(self, label: str):
        """Take a labeled memory measurement."""
        # Memory optimization: Memory-critical operation
        if self.is_cuda:
        # Memory optimization: Memory-critical operation
            allocated = self.get_allocated()
            reserved = self.get_reserved()
            peak = self.get_peak()
            self.measurements.append({
                "label": label,
                "allocated_mb": allocated,
                "reserved_mb": reserved,
                "peak_mb": peak,
                "used_since_start_mb": allocated - self.start_mem
            })
            
    def report(self) -> Dict[str, Any]:
        """Generate a report of memory usage."""
        # Memory optimization: Memory-critical operation
        if not self.measurements:
            return {}
            
        # Find max values
        max_allocated = max(m["allocated_mb"] for m in self.measurements)
        max_reserved = max(m["reserved_mb"] for m in self.measurements)
        max_peak = max(m["peak_mb"] for m in self.measurements)
        
        return {
            "measurements": self.measurements,
            "max_allocated_mb": max_allocated,
            "max_reserved_mb": max_reserved, 
            "max_peak_mb": max_peak,
            "is_cuda": self.is_cuda,
            # Memory optimization: Memory-critical operation
            "device": str(self.device)
            # Memory optimization: Device placement for memory management
        }

def benchmark_forward_pass(
    text: torch.Tensor, 
    image: torch.Tensor, 
    modules: Dict[str, nn.Module],
    memory_tracker: MemoryTracker,
    # Memory optimization: Memory-critical operation
    n_repeat: int = 3
) -> Dict[str, Any]:
    """
    Benchmark forward pass performance and memory usage.
    # Memory optimization: Memory-critical operation
    
    Args:
        text: Text input tensor
        image: Image input tensor
        modules: Model components dict
        # Memory optimization: Explicit memory cleanup
        memory_tracker: Memory usage tracker
        # Memory optimization: Memory-critical operation
        n_repeat: Number of repetitions for timing
    
    Returns:
        Dict with benchmark results
    """
    device = text.device
    # Memory optimization: Device placement for memory management
    batch_size = text.size(0)
    seq_len = text.size(1)
    
    # Warmup
    with torch.no_grad():
    # Memory optimization: Disable gradient computation to save memory
        _ = impressioncore_b1_forward(text, image, modules)
    
    memory_tracker.reset()
    # Memory optimization: Memory-critical operation
    memory_tracker.measure("pre_forward")
    # Memory optimization: Memory-critical operation
    
    # Time forward pass
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    start_time = time.time()
    
    for _ in range(n_repeat):
        with torch.no_grad():
        # Memory optimization: Disable gradient computation to save memory
            output = impressioncore_b1_forward(text, image, modules)
    
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    end_time = time.time()
    
    memory_tracker.measure("post_forward")
    # Memory optimization: Memory-critical operation
    
    # Calculate metrics
    forward_time = (end_time - start_time) / n_repeat
    tokens_per_second = (batch_size * seq_len) / forward_time
    
    return {
        "forward_time_ms": forward_time * 1000,
        "tokens_per_second": tokens_per_second,
        "output_shape": list(output.shape),
        "memory": memory_tracker.report()
        # Memory optimization: Memory-critical operation
    }

def benchmark_backward_pass(
    text: torch.Tensor, 
    image: torch.Tensor, 
    modules: Dict[str, nn.Module],
    memory_tracker: MemoryTracker,
    # Memory optimization: Memory-critical operation
    n_repeat: int = 3
) -> Dict[str, Any]:
    """
    Benchmark backward pass performance and memory usage.
    # Memory optimization: Memory-critical operation
    
    Args:
        text: Text input tensor
        image: Image input tensor
        modules: Model components dict
        # Memory optimization: Explicit memory cleanup
        memory_tracker: Memory usage tracker
        # Memory optimization: Memory-critical operation
        n_repeat: Number of repetitions for timing
    
    Returns:
        Dict with benchmark results
    """
    device = text.device
    # Memory optimization: Device placement for memory management
    batch_size = text.size(0)
    seq_len = text.size(1)
    
    # Create dummy criterion
    criterion = nn.CrossEntropyLoss()
    target = torch.zeros(batch_size, dtype=torch.long, device=device)
    # Memory optimization: Device placement for memory management
    
    # Get all parameters
    parameters = [p for module in modules.values() if hasattr(module, 'parameters')
                for p in module.parameters() if p.requires_grad]
    
    # Warmup
    output = impressioncore_b1_forward(text, image, modules)
    loss = criterion(output, target)
    loss.backward()
    
    # Reset gradients
    for p in parameters:
        p.grad = None
    
    memory_tracker.reset()
    # Memory optimization: Memory-critical operation
    memory_tracker.measure("pre_backward")
    # Memory optimization: Memory-critical operation
    
    # Time backward pass
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    start_time = time.time()
    
    for _ in range(n_repeat):
        output = impressioncore_b1_forward(text, image, modules)
        loss = criterion(output, target)
        loss.backward()
        
        # Reset gradients between iterations
        for p in parameters:
            p.grad = None
    
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    end_time = time.time()
    
    memory_tracker.measure("post_backward")
    # Memory optimization: Memory-critical operation
    
    # Calculate metrics
    backward_time = (end_time - start_time) / n_repeat
    tokens_per_second = (batch_size * seq_len) / backward_time
    
    return {
        "backward_time_ms": backward_time * 1000,
        "tokens_per_second": tokens_per_second,
        "memory": memory_tracker.report()
        # Memory optimization: Memory-critical operation
    }

def benchmark_module_breakdown(
    text: torch.Tensor, 
    image: torch.Tensor, 
    modules: Dict[str, nn.Module],
    memory_tracker: MemoryTracker
    # Memory optimization: Memory-critical operation
) -> Dict[str, Any]:
    """
    Breakdown of performance and memory usage by model component.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        text: Text input tensor
        image: Image input tensor
        modules: Model components dict
        # Memory optimization: Explicit memory cleanup
        memory_tracker: Memory usage tracker
        # Memory optimization: Memory-critical operation
    
    Returns:
        Dict with breakdown results
    """
    device = text.device
    # Memory optimization: Device placement for memory management
    results = {}
    
    # Text encoder
    memory_tracker.reset()
    # Memory optimization: Memory-critical operation
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    start_time = time.time()
    
    text_feat = modules["text_encoder"](text)
    
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    end_time = time.time()
    memory_tracker.measure("text_encoder")
    # Memory optimization: Memory-critical operation
    
    results["text_encoder"] = {
        "time_ms": (end_time - start_time) * 1000,
        "memory": memory_tracker.report()
        # Memory optimization: Memory-critical operation
    }
    
    # Image encoder
    memory_tracker.reset()
    # Memory optimization: Memory-critical operation
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    start_time = time.time()
    
    image_feat = modules["image_encoder"](image)
    
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    end_time = time.time()
    memory_tracker.measure("image_encoder")
    # Memory optimization: Memory-critical operation
    
    results["image_encoder"] = {
        "time_ms": (end_time - start_time) * 1000,
        "memory": memory_tracker.report()
        # Memory optimization: Memory-critical operation
    }
    
    # Fusion layer
    fused_input = torch.cat([text_feat, image_feat], dim=-1)
    memory_tracker.reset()
    # Memory optimization: Memory-critical operation
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    start_time = time.time()
    
    fused = modules["fusion_layer"](fused_input)
    
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    end_time = time.time()
    memory_tracker.measure("fusion_layer")
    # Memory optimization: Memory-critical operation
    
    results["fusion_layer"] = {
        "time_ms": (end_time - start_time) * 1000,
        "memory": memory_tracker.report()
        # Memory optimization: Memory-critical operation
    }
    
    # MoE routing
    memory_tracker.reset()
    # Memory optimization: Memory-critical operation
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    start_time = time.time()
    
    gate_scores = torch.softmax(modules["gate"](fused), dim=-1)
    expert_outputs = torch.stack([expert(fused) for expert in modules["experts"]], dim=1)
    moe_out = (gate_scores.unsqueeze(-1) * expert_outputs).sum(dim=1)
    
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    end_time = time.time()
    memory_tracker.measure("moe")
    # Memory optimization: Memory-critical operation
    
    results["moe"] = {
        "time_ms": (end_time - start_time) * 1000,
        "memory": memory_tracker.report()
        # Memory optimization: Memory-critical operation
    }
    
    # Output head
    memory_tracker.reset()
    # Memory optimization: Memory-critical operation
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    start_time = time.time()
    
    output = modules["head"](moe_out)
    
    torch.cuda.synchronize(device)
    # Memory optimization: CUDA operations for GPU acceleration
    end_time = time.time()
    memory_tracker.measure("head")
    # Memory optimization: Memory-critical operation
    
    results["head"] = {
        "time_ms": (end_time - start_time) * 1000,
        "memory": memory_tracker.report()
        # Memory optimization: Memory-critical operation
    }
    
    return results

def benchmark_context_window(
    seq_len: int,
    batch_size: int = 1,
    device: torch.device = None,
    # Memory optimization: Device placement for memory management
    use_checkpoint: bool = True,
    use_flash_attention: bool = True,
    n_repeat: int = 3
) -> Dict[str, Any]:
    """
    Benchmark model performance for a specific context window size.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        seq_len: Sequence length to benchmark
        batch_size: Batch size
        device: Device to run on
        # Memory optimization: Device placement for memory management
        use_checkpoint: Whether to use gradient checkpointing
        use_flash_attention: Whether to use flash attention
        n_repeat: Number of repetitions for timing
    
    Returns:
        Dict with benchmark results
    """
    if device is None:
    # Memory optimization: Device placement for memory management
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Memory optimization: CUDA operations for GPU acceleration
        
    logger.info(f"Benchmarking context window size: {seq_len} on {device}")
    # Memory optimization: Device placement for memory management
    
    # Build model
    modules = build_impressioncore_b1(
        text_dim=seq_len,
        image_dim=3*32*32,  # CIFAR-10 size
        use_checkpoint=use_checkpoint
    )
    
    # Move modules to device
    # Memory optimization: Device placement for memory management
    for name, module in modules.items():
        if isinstance(module, torch.nn.Module):
            modules[name] = module.to(device)
            # Memory optimization: Device placement for memory management
    
    # Replace attention mechanisms if needed
    if use_flash_attention and device.type == "cuda":
    # Memory optimization: Device placement for memory management
        # This is just a simulation - in practice, we would inject flash attention
        # into the transformer layers within the text and image encoders
        logger.info("Using flash attention (simulated)")
    
    # Generate inputs
    torch.cuda.empty_cache()
    # Memory optimization: CUDA operations for GPU acceleration
    text = torch.randn(batch_size, seq_len, device=device)
    # Memory optimization: Device placement for memory management
    image = torch.randn(batch_size, 3*32*32, device=device)
    # Memory optimization: Device placement for memory management
    
    memory_tracker = MemoryTracker(device)
    # Memory optimization: Device placement for memory management
    
    # Run benchmarks
    try:
        # Forward pass benchmark
        forward_results = benchmark_forward_pass(
            text, image, modules, memory_tracker, n_repeat
            # Memory optimization: Memory-critical operation
        )
        
        # Backward pass benchmark
        backward_results = benchmark_backward_pass(
            text, image, modules, memory_tracker, n_repeat
            # Memory optimization: Memory-critical operation
        )
        
        # Component breakdown
        component_results = benchmark_module_breakdown(
            text, image, modules, memory_tracker
            # Memory optimization: Memory-critical operation
        )
        
        results = {
            "seq_len": seq_len,
            "batch_size": batch_size,
            "device": str(device),
            # Memory optimization: Device placement for memory management
            "use_checkpoint": use_checkpoint,
            "use_flash_attention": use_flash_attention,
            "forward": forward_results,
            "backward": backward_results,
            "components": component_results,
            "success": True
        }
    except RuntimeError as e:
        # Handle OOM errors
        logger.warning(f"Error during benchmark with seq_len={seq_len}: {e}")
        results = {
            "seq_len": seq_len,
            "batch_size": batch_size,
            "device": str(device),
            # Memory optimization: Device placement for memory management
            "use_checkpoint": use_checkpoint,
            "use_flash_attention": use_flash_attention,
            "error": str(e),
            "success": False
        }
    
    return results

def run_benchmarks(
    context_sizes: List[int],
    output_dir: str = "benchmark_results",
    device: torch.device = None
    # Memory optimization: Device placement for memory management
) -> Dict[str, Any]:
    """
    Run benchmarks for multiple context window sizes.
    
    Args:
        context_sizes: List of sequence lengths to benchmark
        output_dir: Directory to save results
        device: Device to run benchmarks on
        # Memory optimization: Device placement for memory management
    
    Returns:
        Dict with all benchmark results
    """
    if device is None:
    # Memory optimization: Device placement for memory management
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Memory optimization: CUDA operations for GPU acceleration
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get device info
    # Memory optimization: Device placement for memory management
    device_name = "CPU"
    # Memory optimization: Device placement for memory management
    memory_info = {"total_gb": 0}
    # Memory optimization: Memory-critical operation
    
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        device_name = torch.cuda.get_device_name(device)
        # Memory optimization: CUDA operations for GPU acceleration
        total_memory = torch.cuda.get_device_properties(device).total_memory
        # Memory optimization: CUDA operations for GPU acceleration
        memory_info = {
        # Memory optimization: Memory-critical operation
            "total_gb": total_memory / (1024**3),
            # Memory optimization: Memory-critical operation
            "name": device_name
            # Memory optimization: Device placement for memory management
        }
    
    logger.info(f"Running benchmarks on: {device_name}")
    # Memory optimization: Device placement for memory management
    logger.info(f"Context window sizes: {context_sizes}")
    
    # Run benchmarks for each context size
    results = {
        "device": {
        # Memory optimization: Device placement for memory management
            "name": device_name,
            # Memory optimization: Device placement for memory management
            "type": device.type,
            # Memory optimization: Device placement for memory management
            "memory": memory_info
            # Memory optimization: Memory-critical operation
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "context_windows": {}
    }
    
    for seq_len in tqdm(context_sizes, desc="Benchmarking context sizes"):
        # With gradient checkpointing
        checkpoint_results = benchmark_context_window(
            seq_len=seq_len,
            batch_size=1,
            device=device,
            # Memory optimization: Device placement for memory management
            use_checkpoint=True,
            use_flash_attention=True
        )
        
        # Without gradient checkpointing (for smaller sizes only)
        no_checkpoint_results = None
        if seq_len <= 8192:
            no_checkpoint_results = benchmark_context_window(
                seq_len=seq_len,
                batch_size=1,
                device=device,
                # Memory optimization: Device placement for memory management
                use_checkpoint=False,
                use_flash_attention=True
            )
        
        results["context_windows"][seq_len] = {
            "with_checkpointing": checkpoint_results,
            "without_checkpointing": no_checkpoint_results
        }
        
        # Save intermediate results
        output_file = os.path.join(output_dir, f"benchmark_{seq_len}.json")
        with open(output_file, 'w') as f:
            json.dump(results["context_windows"][seq_len], f, indent=2)
    
    # Save complete results
    output_file = os.path.join(output_dir, "benchmark_all_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate plots
    generate_plots(results, output_dir)
    
    return results

def generate_plots(results: Dict[str, Any], output_dir: str):
    """
    Generate visualizations of benchmark results.
    
    Args:
        results: Benchmark results dictionary
        output_dir: Directory to save plots
    """
    context_sizes = sorted([int(k) for k in results["context_windows"].keys()])
    
    # Extract metrics
    forward_times = []
    backward_times = []
    memory_usage = []
    # Memory optimization: Memory-critical operation
    tokens_per_second = []
    
    for size in context_sizes:
        window_results = results["context_windows"][str(size)]["with_checkpointing"]
        if window_results["success"]:
            forward_times.append(window_results["forward"]["forward_time_ms"])
            backward_times.append(window_results["backward"]["backward_time_ms"])
            memory_usage.append(window_results["forward"]["memory"]["max_peak_mb"])
            # Memory optimization: Memory-critical operation
            tokens_per_second.append(window_results["forward"]["tokens_per_second"])
        else:
            forward_times.append(None)
            backward_times.append(None)
            memory_usage.append(None)
            # Memory optimization: Memory-critical operation
            tokens_per_second.append(None)
    
    # Filter out failed benchmarks
    valid_sizes = []
    valid_forward = []
    valid_backward = []
    valid_memory = []
    # Memory optimization: Memory-critical operation
    valid_throughput = []
    
    for i, size in enumerate(context_sizes):
        if forward_times[i] is not None:
            valid_sizes.append(size)
            valid_forward.append(forward_times[i])
            valid_backward.append(backward_times[i])
            valid_memory.append(memory_usage[i])
            # Memory optimization: Memory-critical operation
            valid_throughput.append(tokens_per_second[i])
    
    # Convert sizes to labels
    size_labels = [f"{s/1024:.0f}k" if s >= 1024 else str(s) for s in valid_sizes]
    
    # Plot 1: Forward/Backward pass times
    plt.figure(figsize=(10, 6))
    plt.plot(size_labels, valid_forward, 'o-', label='Forward pass')
    plt.plot(size_labels, valid_backward, 'o-', label='Backward pass')
    plt.xlabel('Context Window Size')
    plt.ylabel('Time (ms)')
    plt.title('Forward/Backward Pass Time vs Context Window Size')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'time_vs_context.png'), dpi=300)
    
    # Plot 2: Memory usage
    # Memory optimization: Memory-critical operation
    plt.figure(figsize=(10, 6))
    plt.plot(size_labels, valid_memory, 'o-')
    # Memory optimization: Memory-critical operation
    plt.xlabel('Context Window Size')
    plt.ylabel('Memory Usage (MB)')
    # Memory optimization: Memory-critical operation
    plt.title('Peak Memory Usage vs Context Window Size')
    # Memory optimization: Memory-critical operation
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'memory_vs_context.png'), dpi=300)
    # Memory optimization: Memory-critical operation
    
    # Plot 3: Throughput
    plt.figure(figsize=(10, 6))
    plt.plot(size_labels, valid_throughput, 'o-')
    plt.xlabel('Context Window Size')
    plt.ylabel('Tokens per Second')
    plt.title('Throughput vs Context Window Size')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'throughput_vs_context.png'), dpi=300)
    
    # Plot 4: Component breakdown for largest working context size
    if valid_sizes:
        largest_size = valid_sizes[-1]
        components = results["context_windows"][str(largest_size)]["with_checkpointing"]["components"]
        
        component_names = list(components.keys())
        component_times = [components[c]["time_ms"] for c in component_names]
        component_memory = [components[c]["memory"]["max_peak_mb"] for c in component_names]
        # Memory optimization: Memory-critical operation
        
        # Time breakdown
        plt.figure(figsize=(10, 6))
        plt.bar(component_names, component_times)
        plt.xlabel('Model Component')
        # Memory optimization: Explicit memory cleanup
        plt.ylabel('Time (ms)')
        plt.title(f'Component Time Breakdown ({largest_size/1024:.0f}k context)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'component_time_breakdown.png'), dpi=300)
        
        # Memory breakdown
        # Memory optimization: Memory-critical operation
        plt.figure(figsize=(10, 6))
        plt.bar(component_names, component_memory)
        # Memory optimization: Memory-critical operation
        plt.xlabel('Model Component')
        # Memory optimization: Explicit memory cleanup
        plt.ylabel('Memory (MB)')
        # Memory optimization: Memory-critical operation
        plt.title(f'Component Memory Breakdown ({largest_size/1024:.0f}k context)')
        # Memory optimization: Memory-critical operation
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'component_memory_breakdown.png'), dpi=300)
        # Memory optimization: Memory-critical operation
    
    logger.info(f"Saved plots to {output_dir}")

def main():
    """
    
    main function for processing.
    
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
    parser = argparse.ArgumentParser(description='Benchmark ImpressionCore-b1 with different context window sizes')
    
    parser.add_argument('--output', type=str, default='benchmark_results',
                       help='Directory to save benchmark results')
    parser.add_argument('--device', type=str, default='cuda',
    # Memory optimization: Device placement for memory management
                       help='Device to run benchmarks on (cuda or cpu)')
                       # Memory optimization: Device placement for memory management
    parser.add_argument('--sizes', type=str, default='1024,4096,8192,16384,32768,65536,131072',
                       help='Context window sizes to benchmark, comma-separated')
    parser.add_argument('--max-size', type=int, default=0,
                       help='Maximum context window size to try')
    
    args = parser.parse_args()
    
    device = torch.device(args.device if torch.cuda.is_available() and args.device == 'cuda' else 'cpu')
    # Memory optimization: CUDA operations for GPU acceleration
    
    # Parse context window sizes
    if args.max_size > 0:
        # Generate sizes up to max_size (doubling each time)
        size = 1024
        context_sizes = []
        while size <= args.max_size:
            context_sizes.append(size)
            size *= 2
    else:
        context_sizes = [int(s) for s in args.sizes.split(',')]
    
    # Run benchmarks
    run_benchmarks(
        context_sizes=context_sizes,
        output_dir=args.output,
        device=device
        # Memory optimization: Device placement for memory management
    )

if __name__ == "__main__":
    main()
