#!/usr/bin/env python3
"""
ImpressionCore B1 Model Memory Profiling Test
Tests memory usage patterns on target hardware constraints (4GB VRAM)

Created: 2025-01-06
Modified: 2025-01-06
"""

import sys
import os
import tracemalloc
import gc
import torch
import psutil
from typing import Dict, Any, List, Tuple
from pathlib import Path

# Add project root to path for testing (to allow src.* imports)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Also add src directly to path for relative imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

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
    """Memory profiling utility for ImpressionCore B1 model"""
    
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
            'timestamp': tracemalloc.get_traced_memory()[0]
        }
        
        self.checkpoints.append(checkpoint_data)
        
        if rich_available and self.console:
            self.console.print(f"📊 Checkpoint: {name} - RAM: {current_memory['ram']:.1f}MB", style="cyan")
        else:
            print(f"📊 Checkpoint: {name} - RAM: {current_memory['ram']:.1f}MB")
            
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
            print(f"{'Checkpoint':<20} {'RAM(MB)':<10} {'GPU(MB)':<10} {'Delta':<10}")
            print("-" * 60)
            
            for checkpoint in self.checkpoints:
                mem = checkpoint['memory'] 
                delta = checkpoint['delta']
                print(f"{checkpoint['name']:<20} {mem['ram']:<10.1f} {mem['gpu_allocated']:<10.1f} {delta['ram']:+.1f}")
                
            final_checkpoint = self.checkpoints[-1]
            if final_checkpoint['memory']['gpu_allocated'] > 4000:
                print("\n⚠️ GPU memory usage exceeds 4GB target limit!")
            else:
                print("\n✅ GPU memory usage within 4GB target limit")

def test_b1_model_memory():
    """Test B1 model memory usage patterns"""
    profiler = MemoryProfiler()
    profiler.start_profiling()
    
    try:
        profiler.checkpoint("Baseline")
        
        # Import B1 components
        print_rich_or_fallback("Loading B1 model components...", "🧠 B1 MODEL", "blue")
        
        # Test individual component loading
        sys.path.insert(0, str(project_root / "src"))
          # Use direct import path approach for hyphenated directory
        import importlib.util
        b1_model_path = project_root / "src" / "training" / "models" / "impressioncore-base" / "b1_unified_model.py"
        
        spec = importlib.util.spec_from_file_location("b1_unified_model", b1_model_path)
        b1_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(b1_module)
        
        ImpressionCoreB1UnifiedModel = b1_module.ImpressionCoreB1UnifiedModel
        profiler.checkpoint("Imports Complete")
        
        # Test model instantiation with minimal config
        print_rich_or_fallback("Creating B1 model instance...", "🔧 INSTANTIATION", "yellow")
        
        config = {
            'vocab_size': 1000,  # Reduced for memory testing
            'hidden_size': 512,  # Reduced from production size
            'num_attention_heads': 8,
            'num_hidden_layers': 6,  # Reduced from production
            'max_position_embeddings': 512,
            'vae_latent_dim': 256,  # Reduced
            'num_experts': 4,  # Reduced
            'memory_chunk_size': 64,  # Optimized for 4GB
            'use_gradient_checkpointing': True,
            'device': 'cuda' if torch.cuda.is_available() else 'cpu'
        }
        
        model = ImpressionCoreB1UnifiedModel(config)
        profiler.checkpoint("Model Created")
        
        # Move to GPU if available
        if torch.cuda.is_available():
            print_rich_or_fallback("Moving model to GPU...", "🎯 GPU TRANSFER", "green")
            model = model.cuda()
            profiler.checkpoint("Model on GPU")
        
        # Test forward pass with small batch
        print_rich_or_fallback("Testing forward pass...", "⚡ INFERENCE", "magenta")
        
        batch_size = 2  # Small batch for memory testing
        seq_length = 128  # Reduced sequence length
        
        # Create sample inputs
        text_input = torch.randint(0, config['vocab_size'], (batch_size, seq_length))
        attention_mask = torch.ones_like(text_input)
        
        if torch.cuda.is_available():
            text_input = text_input.cuda()
            attention_mask = attention_mask.cuda()
            
        # Forward pass
        with torch.no_grad():
            outputs = model.generate_text(
                input_ids=text_input,
                attention_mask=attention_mask,
                max_length=seq_length + 10,
                num_return_sequences=1
            )
            
        profiler.checkpoint("Forward Pass Complete")
        
        # Test memory cleanup
        print_rich_or_fallback("Testing memory cleanup...", "🧹 CLEANUP", "red")
        del outputs, text_input, attention_mask, model
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        profiler.checkpoint("Cleanup Complete")
        
    except Exception as e:
        print_rich_or_fallback(f"Error during testing: {str(e)}", "❌ ERROR", "red")
        profiler.checkpoint("Error Occurred")
        
    finally:
        profiler.report()
        
def test_component_memory_isolation():
    """Test individual component memory usage"""
    profiler = MemoryProfiler()
    profiler.start_profiling()
    
    # Simplified component tests using adapters
    components_to_test = [
        ("LatentDiffusionTransformer", "models.latent_diffusion_transformer"),
        ("MemoryOptimizer", "training.models.memory_optimization"),
    ]
    
    print_rich_or_fallback("Testing individual component memory usage", "🔬 COMPONENT ANALYSIS", "blue")
    
    # Add src to path for imports
    sys.path.insert(0, str(project_root / "src"))
    
    for component_name, module_path in components_to_test:
        try:
            print_rich_or_fallback(f"Loading {component_name}...", f"📦 {component_name.upper()}", "cyan")
            
            # Try importing via the adapter pattern
            if component_name == "LatentDiffusionTransformer":
                from models.latent_diffusion_transformer import LatentDiffusionTransformer
                # Create minimal instance
                instance = LatentDiffusionTransformer()
                profiler.checkpoint(f"{component_name} Loaded")
                del instance
                gc.collect()
                
            elif component_name == "MemoryOptimizer":
                from training.models.memory_optimization import MemoryOptimizer
                instance = MemoryOptimizer()
                profiler.checkpoint(f"{component_name} Loaded")
                del instance
                gc.collect()
                
        except Exception as e:
            print_rich_or_fallback(f"Error testing {component_name}: {str(e)}", "❌ ERROR", "red")
            
    profiler.checkpoint("All Components Tested")
    profiler.report()

def main():
    """Main memory profiling test"""
    print_rich_or_fallback(
        "ImpressionCore B1 Model Memory Profiling Test\n"
        "Target Hardware: NVIDIA GTX 1050 Ti (4GB VRAM)\n"
        "Testing memory efficiency and optimization", 
        "🧠 IMPRESSIONCORE B1 MEMORY PROFILER", 
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
    print("1. Component Memory Isolation Test")
    print("="*60)
    test_component_memory_isolation()
    
    print("\n" + "="*60)
    print("2. Full B1 Model Memory Test") 
    print("="*60)
    test_b1_model_memory()
    
    print_rich_or_fallback("Memory profiling complete!", "✅ COMPLETE", "bold green")

if __name__ == "__main__":
    main()
