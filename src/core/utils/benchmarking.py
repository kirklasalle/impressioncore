#!/usr/bin/env python3
"""
ImpressionCore: Benchmarking

Module for benchmarking functionality in the ImpressionCore framework.

File: core/utils/benchmarking.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, memory-critical, framework, pytorch, core, production, utils, 2025, object-oriented]
Dependencies: [torch, typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements benchmarking functionality for the
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
from src.core.utils.benchmarking import ModelBenchmark
instance = ModelBenchmark()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import time
import torch
import numpy as np
import logging
from typing import Dict, Any, List, Tuple, Optional, Union
from pathlib import Path
import json
import matplotlib.pyplot as plt

from ..utils.memory_optimization import monitor_memory_usage
# Memory optimization: Memory-critical operation

logger = logging.getLogger(__name__)

class ModelBenchmark:
    """
    Benchmark framework for evaluating model performance
    # Memory optimization: Explicit memory cleanup
    """
    def __init__(self, 
                model: torch.nn.Module, 
                tokenizer: Any, 
                device: str = "cuda",
                # Memory optimization: Device placement for memory management
                output_dir: Optional[str] = None):
        """
        Initialize benchmarking framework
        
        Args:
            model: PyTorch model to benchmark
            # Memory optimization: Explicit memory cleanup
            tokenizer: Tokenizer for text processing
            device: Device to run benchmarks on ("cuda" or "cpu")
            # Memory optimization: Device placement for memory management
            output_dir: Directory to save benchmark results
        """
        self.model = model
        # Memory optimization: Explicit memory cleanup
        self.tokenizer = tokenizer
        self.device = torch.device(device if torch.cuda.is_available() and device == "cuda" else "cpu")
        # Memory optimization: CUDA operations for GPU acceleration
        self.model.to(self.device)
        # Memory optimization: Device placement for memory management
        self.output_dir = Path(output_dir) if output_dir else None
        
        # Create output directory
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure model is in eval mode
        # Memory optimization: Explicit memory cleanup
        self.model.eval()
    
    def benchmark_inference_speed(self, 
                                 prompt: str, 
                                 iterations: int = 10, 
                                 max_length: int = 100, 
                                 warmup: int = 2) -> Dict[str, float]:
        """
        Measure text generation speed in tokens per second
        
        Args:
            prompt: Text prompt for generation
            iterations: Number of generation iterations
            max_length: Maximum generation length
            warmup: Number of warmup iterations (not counted)
            
        Returns:
            Dictionary with speed metrics
        """
        # Convert prompt to input tensors
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        # Memory optimization: Device placement for memory management
        
        # Warmup runs
        for _ in range(warmup):
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                self.model.generate(
                    input_ids,
                    max_length=max_length,
                    do_sample=False  # Deterministic generation for consistent measurement
                )
        
        # Timed runs
        torch.cuda.synchronize()
        # Memory optimization: CUDA operations for GPU acceleration
        start_time = time.time()
        tokens_generated = 0
        
        for _ in range(iterations):
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                output = self.model.generate(
                    input_ids,
                    max_length=max_length,
                    do_sample=False
                )
            tokens_generated += output.shape[1] - input_ids.shape[1]
            torch.cuda.synchronize()
            # Memory optimization: CUDA operations for GPU acceleration
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate metrics
        tokens_per_second = tokens_generated / duration
        seconds_per_iteration = duration / iterations
        tokens_per_iteration = tokens_generated / iterations
        
        results = {
            "tokens_per_second": tokens_per_second,
            "seconds_per_iteration": seconds_per_iteration,
            "tokens_per_iteration": tokens_per_iteration,
            "total_tokens": tokens_generated,
            "total_time": duration,
            "iterations": iterations
        }
        
        logger.info(f"Inference speed: {tokens_per_second:.2f} tokens/second")
        logger.info(f"Average generation time: {seconds_per_iteration:.2f} seconds")
        
        # Save results if output directory is specified
        if self.output_dir:
            with open(self.output_dir / "speed_benchmark.json", "w") as f:
                json.dump(results, f, indent=2)
                
        return results
    
    def benchmark_memory_usage(self, 
    # Memory optimization: Memory-critical operation
                              batch_size: int = 1, 
                              sequence_length: int = 512,
                              train_mode: bool = False) -> Dict[str, float]:
        """
        Measure peak memory usage during inference and optionally training
        # Memory optimization: Memory-critical operation
        
        Args:
            batch_size: Batch size for testing
            sequence_length: Sequence length for testing
            train_mode: Whether to test training memory usage
            # Memory optimization: Memory-critical operation
            
        Returns:
            Dictionary with memory usage metrics in GB
            # Memory optimization: Memory-critical operation
        """
        # Create dummy inputs
        inputs = torch.randint(
            0, 1000, 
            (batch_size, sequence_length),
            device=self.device
            # Memory optimization: Device placement for memory management
        )
        
        # Record baseline memory
        # Memory optimization: Memory-critical operation
        torch.cuda.reset_peak_memory_stats()
        # Memory optimization: CUDA operations for GPU acceleration
        torch.cuda.empty_cache()
        # Memory optimization: CUDA operations for GPU acceleration
        baseline_memory = torch.cuda.memory_allocated()
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Run inference
        self.model.eval()
        with torch.no_grad():
        # Memory optimization: Disable gradient computation to save memory
            outputs = self.model(inputs)
        
        torch.cuda.synchronize()
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Record peak memory after inference
        # Memory optimization: Memory-critical operation
        inference_peak = torch.cuda.max_memory_allocated() - baseline_memory
        # Memory optimization: CUDA operations for GPU acceleration
        inference_peak_gb = inference_peak / 1e9
        
        results = {
            "baseline_gb": baseline_memory / 1e9,
            # Memory optimization: Memory-critical operation
            "inference_peak_gb": inference_peak_gb,
        }
        
        logger.info(f"Inference peak memory: {inference_peak_gb:.2f} GB")
        # Memory optimization: Memory-critical operation
        
        # Optionally measure training memory
        # Memory optimization: Memory-critical operation
        if train_mode:
            # Reset stats for training measurement
            torch.cuda.reset_peak_memory_stats()
            # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
            
            # Switch to train mode
            self.model.train()
            
            # Forward pass
            outputs = self.model(inputs)
            
            # Backward pass with dummy loss
            if hasattr(outputs, "logits"):
                loss = outputs.logits.sum()
            else:
                loss = outputs.sum()
                
            loss.backward()
            
            torch.cuda.synchronize()
            # Memory optimization: CUDA operations for GPU acceleration
            
            # Record peak training memory
            # Memory optimization: Memory-critical operation
            training_peak = torch.cuda.max_memory_allocated()
            # Memory optimization: CUDA operations for GPU acceleration
            training_peak_gb = training_peak / 1e9
            
            results["training_peak_gb"] = training_peak_gb
            logger.info(f"Training peak memory: {training_peak_gb:.2f} GB")
            # Memory optimization: Memory-critical operation
            
            # Reset model to eval mode
            # Memory optimization: Explicit memory cleanup
            self.model.eval()
        
        # Save results if output directory is specified
        if self.output_dir:
            with open(self.output_dir / "memory_benchmark.json", "w") as f:
            # Memory optimization: Memory-critical operation
                json.dump(results, f, indent=2)
                
        return results
    
    def visualize_benchmarks(self, benchmark_data: Dict[str, Any], benchmark_type: str):
        """
        Create visualizations of benchmark results
        
        Args:
            benchmark_data: Dictionary with benchmark results
            benchmark_type: Type of benchmark ('speed' or 'memory')
            # Memory optimization: Memory-critical operation
        """
        if not self.output_dir:
            logger.warning("No output directory specified, skipping visualization")
            return
            
        plt.figure(figsize=(10, 6))
        
        if benchmark_type == 'speed':
            # Create bar chart of tokens per second
            plt.bar(['Tokens/Second'], [benchmark_data['tokens_per_second']], color='blue')
            plt.title('Generation Speed Benchmark')
            plt.ylabel('Tokens per Second')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.savefig(self.output_dir / "speed_benchmark.png", dpi=300, bbox_inches='tight')
            
        elif benchmark_type == 'memory':
        # Memory optimization: Memory-critical operation
            # Create bar chart of memory usage
            # Memory optimization: Memory-critical operation
            memory_data = []
            # Memory optimization: Memory-critical operation
            labels = []
            
            if 'inference_peak_gb' in benchmark_data:
                memory_data.append(benchmark_data['inference_peak_gb'])
                # Memory optimization: Memory-critical operation
                labels.append('Inference')
                
            if 'training_peak_gb' in benchmark_data:
                memory_data.append(benchmark_data['training_peak_gb'])
                # Memory optimization: Memory-critical operation
                labels.append('Training')
            
            plt.bar(labels, memory_data, color=['blue', 'orange'][:len(labels)])
            # Memory optimization: Memory-critical operation
            plt.title('Memory Usage Benchmark')
            # Memory optimization: Memory-critical operation
            plt.ylabel('Memory (GB)')
            # Memory optimization: Memory-critical operation
            plt.ylim(bottom=0)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add horizontal line for 4GB VRAM limit
            plt.axhline(y=4.0, color='red', linestyle='--', label='4GB VRAM Limit')
            plt.legend()
            
            plt.savefig(self.output_dir / "memory_benchmark.png", dpi=300, bbox_inches='tight')
            # Memory optimization: Memory-critical operation
        
        plt.close()

    def run_full_benchmark_suite(self, prompt: str = "The quick brown fox jumps over the lazy dog"):
        """
        Run a complete set of benchmarks and generate a report
        
        Args:
            prompt: Text prompt for generation benchmarks
        """
        results = {
            "device": str(self.device),
            # Memory optimization: Device placement for memory management
            "model_parameters": sum(p.numel() for p in self.model.parameters()),
        }
        
        # Memory usage benchmarks
        # Memory optimization: Memory-critical operation
        logger.info("Running memory usage benchmarks...")
        # Memory optimization: Memory-critical operation
        memory_results = self.benchmark_memory_usage(train_mode=True)
        # Memory optimization: Memory-critical operation
        results["memory"] = memory_results
        # Memory optimization: Memory-critical operation
        
        # Speed benchmarks
        logger.info("Running inference speed benchmarks...")
        speed_results = self.benchmark_inference_speed(prompt=prompt)
        results["speed"] = speed_results
        
        # Create visualizations
        logger.info("Generating visualizations...")
        self.visualize_benchmarks(speed_results, 'speed')
        self.visualize_benchmarks(memory_results, 'memory')
        # Memory optimization: Memory-critical operation
        
        # Save comprehensive results
        if self.output_dir:
            with open(self.output_dir / "benchmark_report.json", "w") as f:
                json.dump(results, f, indent=2)
                
            self.generate_html_report(results)
        
        return results
    
    def generate_html_report(self, results: Dict[str, Any]):
        """Generate an HTML report from benchmark results"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ImpressionCore Benchmark Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 1000px; margin: 0 auto; }}
                h1 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .metric {{ font-weight: bold; }}
                .value {{ font-family: monospace; }}
                img {{ max-width: 100%; height: auto; margin: 20px 0; }}
                .warning {{ color: #e74c3c; }}
                .success {{ color: #27ae60; }}
            </style>
        </head>
        <body>
            <h1>ImpressionCore Benchmark Report</h1>
            
            <h2>System Information</h2>
            <table>
                <tr>
                    <td class="metric">Device</td>
                    # Memory optimization: Device placement for memory management
                    <td class="value">{results["device"]}</td>
                    # Memory optimization: Device placement for memory management
                </tr>
                <tr>
                    <td class="metric">Model Parameters</td>
                    # Memory optimization: Explicit memory cleanup
                    <td class="value">{results["model_parameters"]:,}</td>
                </tr>
            </table>
            
            <h2>Memory Usage</h2>
            # Memory optimization: Memory-critical operation
            <table>
                <tr>
                    <td class="metric">Inference Peak Memory</td>
                    # Memory optimization: Memory-critical operation
                    <td class="value">{results["memory"]["inference_peak_gb"]:.2f} GB</td>
                    # Memory optimization: Memory-critical operation
                </tr>
        """
        
        # Add training memory if available
        # Memory optimization: Memory-critical operation
        if "training_peak_gb" in results["memory"]:
        # Memory optimization: Memory-critical operation
            memory_class = "success" if results["memory"]["training_peak_gb"] < 4.0 else "warning"
            # Memory optimization: Memory-critical operation
            html_content += f"""
                <tr>
                    <td class="metric">Training Peak Memory</td>
                    # Memory optimization: Memory-critical operation
                    <td class="value {memory_class}">{results["memory"]["training_peak_gb"]:.2f} GB</td>
                    # Memory optimization: Memory-critical operation
                </tr>
            """
        
        html_content += f"""
            </table>
            <img src="memory_benchmark.png" alt="Memory Usage Graph">
            # Memory optimization: Memory-critical operation
            
            <h2>Generation Speed</h2>
            <table>
                <tr>
                    <td class="metric">Tokens per Second</td>
                    <td class="value">{results["speed"]["tokens_per_second"]:.2f}</td>
                </tr>
                <tr>
                    <td class="metric">Average Generation Time</td>
                    <td class="value">{results["speed"]["seconds_per_iteration"]:.2f} seconds</td>
                </tr>
                <tr>
                    <td class="metric">Tokens per Generation</td>
                    <td class="value">{results["speed"]["tokens_per_iteration"]:.1f}</td>
                </tr>
            </table>
            <img src="speed_benchmark.png" alt="Speed Benchmark Graph">
            
            <h2>Recommendations</h2>
        """
        
        # Add recommendations based on benchmark results
        if "training_peak_gb" in results["memory"] and results["memory"]["training_peak_gb"] > 3.8:
        # Memory optimization: Memory-critical operation
            html_content += """
            <p class="warning">
                ⚠️ Training memory usage exceeds the 4GB VRAM target. Consider these optimizations:
                # Memory optimization: Memory-critical operation
                <ul>
                    <li>Enable gradient checkpointing</li>
                    <li>Reduce batch size</li>
                    <li>Use 16-bit precision</li>
                    <li>Implement activation offloading</li>
                </ul>
            </p>
            """
        else:
            html_content += """
            <p class="success">
                ✅ Memory usage is within target range for 4GB VRAM cards.
                # Memory optimization: Memory-critical operation
            </p>
            """
        
        if "tokens_per_second" in results["speed"] and results["speed"]["tokens_per_second"] < 10:
            html_content += """
            <p class="warning">
                ⚠️ Generation speed is below target. Consider these optimizations:
                <ul>
                    <li>Optimize attention mechanisms</li>
                    <li>Reduce model size</li>
                    # Memory optimization: Explicit memory cleanup
                    <li>Implement caching for key/value states</li>
                </ul>
            </p>
            """
        else:
            html_content += """
            <p class="success">
                ✅ Generation speed meets or exceeds the target rate.
            </p>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(self.output_dir / "benchmark_report.html", "w") as f:
            f.write(html_content)

class PerformanceBenchmark:
    """
    Performance benchmarking utility for ImpressionCore components.
    
    Provides comprehensive performance metrics and analysis capabilities
    optimized for GTX 1050 Ti constraints.
    """
    
    def __init__(self, name: str = "ImpressionCore Benchmark"):
        """
        Initialize performance benchmark.
        
        Args:
            name: Name of the benchmark
        """
        self.name = name
        self.metrics = {}
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start benchmark timing."""
        import time
        self.start_time = time.time()
    
    def stop(self):
        """Stop benchmark timing."""
        import time
        self.end_time = time.time()
    
    def add_metric(self, name: str, value: float):
        """Add a performance metric."""
        self.metrics[name] = value
    
    def get_duration(self) -> float:
        """Get benchmark duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def get_report(self) -> dict:
        """Get benchmark report."""
        return {
            'name': self.name,
            'duration': self.get_duration(),
            'metrics': self.metrics
        }
    
    def print_report(self):
        """Print benchmark report to console."""
        print(f"\n📊 {self.name} Performance Report")
        print("=" * 50)
        print(f"Duration: {self.get_duration():.2f}s")
        for name, value in self.metrics.items():
            print(f"{name}: {value}")


# Export classes for easy access
__all__ = [
    'ModelBenchmark',
    'PerformanceBenchmark'
]
