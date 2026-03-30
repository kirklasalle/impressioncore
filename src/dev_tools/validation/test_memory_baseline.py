#!/usr/bin/env python3
"""
ImpressionCore Memory Baseline Test
Tests fundamental memory patterns and PyTorch operations on target hardware constraints

Created: 2025-01-07
Modified: 2025-01-07
"""

import sys
import os
import tracemalloc
import gc
import torch
import psutil
from typing import Dict, Any, List, Tuple
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress
    from rich.text import Text
    rich_available = True
except ImportError:
    rich_available = False

def print_rich_or_fallback(content, title="", style=""):
    """Print with rich formatting if available, else fallback to plain text"""
    if rich_available:
        console = Console()
        if title:
            console.print(Panel(content, title=title, style=style))
        else:
            console.print(content)
    else:
        if title:
            print(f"\n=== {title} ===")
        print(content)
        print()

class MemoryProfiler:
    """Memory profiling utility for ImpressionCore"""
    
    def __init__(self):
        self.console = Console() if rich_available else None
        self.baseline_memory = {}
        self.checkpoints = []
        
    def start_profiling(self):
        """Start memory profiling session"""
        tracemalloc.start()
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        self.baseline_memory = self.get_memory_stats()
        print_rich_or_fallback("Memory profiling started", "🔍 PROFILER", "blue")
        
    def checkpoint(self, name: str):
        """Create a memory checkpoint"""
        current_memory = self.get_memory_stats()
        
        # Calculate delta from baseline
        delta = {}
        for key, value in current_memory.items():
            if key in self.baseline_memory:
                delta[key] = value - self.baseline_memory[key]
            else:
                delta[key] = value
                
        checkpoint_data = {
            'name': name,
            'memory': current_memory,
            'delta': delta,
            'timestamp': tracemalloc.get_traced_memory()[0] if tracemalloc.is_tracing() else 0
        }
        
        self.checkpoints.append(checkpoint_data)
        
        if rich_available and self.console:
            self.console.print(f"📊 Checkpoint: {name} - RAM: {current_memory['ram']:.1f}MB, GPU: {current_memory['gpu_allocated']:.1f}MB", style="cyan")
        else:
            print(f"📊 Checkpoint: {name} - RAM: {current_memory['ram']:.1f}MB, GPU: {current_memory['gpu_allocated']:.1f}MB")
            
        return checkpoint_data
        
    def get_memory_stats(self) -> Dict[str, float]:
        """Get current memory statistics"""
        stats = {}
        
        # System RAM
        process = psutil.Process()
        stats['ram'] = process.memory_info().rss / 1024 / 1024  # MB
        
        # GPU memory if available
        if torch.cuda.is_available():
            stats['gpu_allocated'] = torch.cuda.memory_allocated() / 1024 / 1024  # MB
            stats['gpu_reserved'] = torch.cuda.memory_reserved() / 1024 / 1024  # MB
            stats['gpu_free'] = (torch.cuda.get_device_properties(0).total_memory - 
                                torch.cuda.memory_reserved()) / 1024 / 1024
        else:
            stats['gpu_allocated'] = 0
            stats['gpu_reserved'] = 0
            stats['gpu_free'] = 0
            
        # Python memory
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            stats['python_current'] = current / 1024 / 1024  # MB
            stats['python_peak'] = peak / 1024 / 1024  # MB
        else:
            stats['python_current'] = 0
            stats['python_peak'] = 0
            
        return stats
        
    def report(self):
        """Generate memory profiling report"""
        if not self.checkpoints:
            print_rich_or_fallback("No checkpoints recorded", "⚠️ WARNING", "yellow")
            return
            
        if rich_available and self.console:
            # Rich table
            table = Table(title="Memory Profiling Report")
            table.add_column("Checkpoint", style="cyan")
            table.add_column("RAM (MB)", justify="right", style="green")
            table.add_column("GPU Alloc (MB)", justify="right", style="blue")
            table.add_column("GPU Reserved (MB)", justify="right", style="magenta")
            table.add_column("GPU Free (MB)", justify="right", style="yellow")
            table.add_column("RAM Delta", justify="right", style="red")
            
            for checkpoint in self.checkpoints:
                mem = checkpoint['memory']
                delta = checkpoint['delta']
                table.add_row(
                    checkpoint['name'],
                    f"{mem['ram']:.1f}",
                    f"{mem['gpu_allocated']:.1f}",
                    f"{mem['gpu_reserved']:.1f}", 
                    f"{mem['gpu_free']:.1f}",
                    f"{delta['ram']:+.1f}"
                )
                
            self.console.print(table)
            
            # Summary
            final_checkpoint = self.checkpoints[-1]
            if final_checkpoint['memory']['gpu_allocated'] > 4000:  # 4GB limit
                self.console.print(
                    "⚠️ GPU memory usage exceeds 4GB target limit!", 
                    style="bold red"
                )
            else:
                self.console.print(
                    "✅ GPU memory usage within 4GB target limit", 
                    style="bold green"
                )
        else:
            # Plain text fallback
            print("\n=== Memory Profiling Report ===")
            print(f"{'Checkpoint':<25} {'RAM(MB)':<10} {'GPU(MB)':<10} {'Delta':<10}")
            print("-" * 65)
            
            for checkpoint in self.checkpoints:
                mem = checkpoint['memory'] 
                delta = checkpoint['delta']
                print(f"{checkpoint['name']:<25} {mem['ram']:<10.1f} {mem['gpu_allocated']:<10.1f} {delta['ram']:+.1f}")
                
            final_checkpoint = self.checkpoints[-1]
            if final_checkpoint['memory']['gpu_allocated'] > 4000:
                print("\n⚠️ GPU memory usage exceeds 4GB target limit!")
            else:
                print("\n✅ GPU memory usage within 4GB target limit")

def test_pytorch_baseline():
    """Test basic PyTorch operations and memory patterns"""
    profiler = MemoryProfiler()
    profiler.start_profiling()
    
    try:
        profiler.checkpoint("Baseline")
        
        print_rich_or_fallback("Testing basic PyTorch operations...", "🔧 PYTORCH BASELINE", "blue")
        
        # Test tensor creation and operations
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print_rich_or_fallback(f"Using device: {device}", "📱 DEVICE", "cyan")
        
        # Create test tensors
        batch_size = 8
        seq_length = 512
        hidden_size = 768
        
        # Text-like data
        input_ids = torch.randint(0, 30000, (batch_size, seq_length), device=device)
        attention_mask = torch.ones(batch_size, seq_length, device=device)
        
        profiler.checkpoint("Tensors Created")
        
        # Simulate transformer operations
        print_rich_or_fallback("Testing transformer-like operations...", "🧠 TRANSFORMER OPS", "green")
        
        # Embedding layer
        embedding = torch.nn.Embedding(30000, hidden_size).to(device)
        embedded = embedding(input_ids)
        
        profiler.checkpoint("Embeddings")
        
        # Attention computation
        num_heads = 12
        head_dim = hidden_size // num_heads
        
        query = torch.nn.Linear(hidden_size, hidden_size).to(device)
        key = torch.nn.Linear(hidden_size, hidden_size).to(device)
        value = torch.nn.Linear(hidden_size, hidden_size).to(device)
        
        q = query(embedded).view(batch_size, seq_length, num_heads, head_dim).transpose(1, 2)
        k = key(embedded).view(batch_size, seq_length, num_heads, head_dim).transpose(1, 2)
        v = value(embedded).view(batch_size, seq_length, num_heads, head_dim).transpose(1, 2)
        
        # Attention scores
        scores = torch.matmul(q, k.transpose(-2, -1)) / (head_dim ** 0.5)
        attention_probs = torch.softmax(scores, dim=-1)
        context = torch.matmul(attention_probs, v)
        
        profiler.checkpoint("Attention Computation")
        
        # FFN
        print_rich_or_fallback("Testing feed-forward operations...", "⚡ FFN OPS", "yellow")
        
        ffn_hidden = hidden_size * 4
        ffn1 = torch.nn.Linear(hidden_size, ffn_hidden).to(device)
        ffn2 = torch.nn.Linear(ffn_hidden, hidden_size).to(device)
        
        context_reshaped = context.transpose(1, 2).contiguous().view(batch_size, seq_length, hidden_size)
        ffn_out = ffn2(torch.nn.functional.gelu(ffn1(context_reshaped)))
        
        profiler.checkpoint("FFN Computation")
        
        # Test larger batch for memory scaling
        print_rich_or_fallback("Testing memory scaling...", "📈 SCALING", "magenta")
        
        large_batch = 16
        large_input = torch.randint(0, 30000, (large_batch, seq_length), device=device)
        large_embedded = embedding(large_input)
        
        profiler.checkpoint("Large Batch")
        
        # Cleanup
        print_rich_or_fallback("Testing memory cleanup...", "🧹 CLEANUP", "red")
        del input_ids, attention_mask, embedded, q, k, v, scores, attention_probs, context
        del context_reshaped, ffn_out, large_input, large_embedded
        del embedding, query, key, value, ffn1, ffn2
        
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        profiler.checkpoint("Cleanup Complete")
        
    except Exception as e:
        print_rich_or_fallback(f"Error during testing: {str(e)}", "❌ ERROR", "red")
        profiler.checkpoint("Error Occurred")
        
    finally:
        profiler.report()

def test_diffusion_simulation():
    """Test diffusion-like operations for memory validation"""
    profiler = MemoryProfiler()
    profiler.start_profiling()
    
    try:
        print_rich_or_fallback("Testing diffusion-like operations...", "🌊 DIFFUSION SIM", "blue")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Simulate latent diffusion
        batch_size = 4
        latent_channels = 8
        latent_height = 64
        latent_width = 64
        timesteps = 1000
        
        # Initial noise
        noise = torch.randn(batch_size, latent_channels, latent_height, latent_width, device=device)
        
        profiler.checkpoint("Noise Generated")
        
        # Simple U-Net-like architecture simulation
        print_rich_or_fallback("Simulating U-Net operations...", "🏗️ UNET", "cyan")
        
        # Encoder
        conv1 = torch.nn.Conv2d(latent_channels, 64, 3, padding=1).to(device)
        conv2 = torch.nn.Conv2d(64, 128, 3, padding=1).to(device)
        conv3 = torch.nn.Conv2d(128, 256, 3, padding=1).to(device)
        
        # Process noise through encoder
        x = torch.nn.functional.relu(conv1(noise))
        x = torch.nn.functional.relu(conv2(x))
        x = torch.nn.functional.relu(conv3(x))
        
        profiler.checkpoint("Encoder Forward")
        
        # Decoder
        deconv1 = torch.nn.ConvTranspose2d(256, 128, 3, padding=1).to(device)
        deconv2 = torch.nn.ConvTranspose2d(128, 64, 3, padding=1).to(device)
        deconv3 = torch.nn.ConvTranspose2d(64, latent_channels, 3, padding=1).to(device)
        
        x = torch.nn.functional.relu(deconv1(x))
        x = torch.nn.functional.relu(deconv2(x))
        predicted_noise = deconv3(x)
        
        profiler.checkpoint("Decoder Forward")
        
        # Loss computation
        loss = torch.nn.functional.mse_loss(predicted_noise, noise)
        
        profiler.checkpoint("Loss Computed")
        
        # Cleanup
        del noise, x, predicted_noise, loss
        del conv1, conv2, conv3, deconv1, deconv2, deconv3
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        profiler.checkpoint("Diffusion Cleanup")
        
    except Exception as e:
        print_rich_or_fallback(f"Error during diffusion test: {str(e)}", "❌ ERROR", "red")
        
    finally:
        profiler.report()

def main():
    """Main memory profiling test"""
    print_rich_or_fallback(
        "ImpressionCore Memory Baseline Test\n"
        "Target Hardware: NVIDIA GTX 1050 Ti (4GB VRAM)\n"
        "Testing fundamental memory patterns and PyTorch operations", 
        "🧠 MEMORY BASELINE PROFILER", 
        "bold blue"
    )
    
    # System info
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024  # MB
        print_rich_or_fallback(f"GPU: {gpu_name} ({gpu_memory:.0f}MB)", "🎯 HARDWARE", "green")
    else:
        print_rich_or_fallback("No GPU available - testing CPU mode", "⚠️ CPU MODE", "yellow")
        
    # Run tests
    print("\n" + "="*60)
    print("1. PyTorch Baseline Operations Test")
    print("="*60)
    test_pytorch_baseline()
    
    print("\n" + "="*60)
    print("2. Diffusion Simulation Test") 
    print("="*60)
    test_diffusion_simulation()
    
    print_rich_or_fallback("Memory baseline testing complete!", "✅ COMPLETE", "bold green")

if __name__ == "__main__":
    main()
