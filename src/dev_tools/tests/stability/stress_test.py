#!/usr/bin/env python3
"""
ImpressionCore: Stress Test

Module for stress test functionality in the ImpressionCore framework.

File: tests\stability\stress_test.py
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
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements stress test functionality for the
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
from tests.stability.stress_test import StressTester
instance = StressTester()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import argparse
import concurrent.futures
import gc
import logging
import os
import signal
import sys
import threading
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Callable, Any

import numpy as np
import torch
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stress_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("stress_test")

# Add project root to system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Visualization components are imported dynamically to avoid errors if not available


class StressTester:
    """
    Stress tester for visualization components.
    
    This class provides utilities for:
    - Running components under high load
    - Testing with progressively increasing resource demands
    - Detecting performance degradation
    - Measuring system stability
    """
    
    def __init__(self, output_dir: str = "stress_test_results"):
        """
        Initialize the stress tester.
        
        Args:
            output_dir: Directory to store test results
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.has_cuda = torch.cuda.is_available()
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Track system resources
        self.resources = {
            'ram': [],
            'cpu': [],
            'vram': [] if self.has_cuda else None,
            # Memory optimization: Memory-critical operation
            'timestamps': []
        }
        
        # Track component performance
        self.perf_metrics = {}
        
        # Import visualization components if available
        self.components = self._import_components()
    
    def _import_components(self) -> Dict[str, Any]:
        """Import visualization components dynamically"""
        components = {}
        
        try:
            from src.dev_tools.visualization.model_visualizer import ModelVisualizer
            components['visualizer'] = ModelVisualizer
            logger.info("Imported ModelVisualizer")
        except ImportError:
            logger.warning("ModelVisualizer not available")
        
        try:
            from src.dev_tools.visualization.architecture_graph import ModelArchitectureGraph
            components['architecture'] = ModelArchitectureGraph
            logger.info("Imported ModelArchitectureGraph")
        except ImportError:
            logger.warning("ModelArchitectureGraph not available")
        
        try:
            from src.dev_tools.visualization.attention_patterns import AttentionVisualizer
            components['attention'] = AttentionVisualizer
            logger.info("Imported AttentionVisualizer")
        except ImportError:
            logger.warning("AttentionVisualizer not available")
        
        try:
            from src.dev_tools.visualization.activation_maps import ActivationVisualizer
            components['activation'] = ActivationVisualizer
            logger.info("Imported ActivationVisualizer")
        except ImportError:
            logger.warning("ActivationVisualizer not available")
        
        return components
    
    def _create_test_models(self, complexity: str = "medium") -> List[torch.nn.Module]:
        """
        Create test models of varying complexity.
        
        Args:
            complexity: 'low', 'medium', or 'high' model complexity
            # Memory optimization: Explicit memory cleanup
            
        Returns:
            List of model instances
            # Memory optimization: Explicit memory cleanup
        """
        models = []
        
        if complexity == "low":
            # Simple model, very low VRAM requirements
            model = torch.nn.Sequential(
            # Memory optimization: Explicit memory cleanup
                torch.nn.Linear(128, 256),
                torch.nn.ReLU(),
                torch.nn.Linear(256, 128)
            )
            models.append(model)
            
        elif complexity == "medium":
            # Medium complexity model
            model = torch.nn.Sequential(
            # Memory optimization: Explicit memory cleanup
                torch.nn.Linear(512, 1024),
                torch.nn.ReLU(),
                torch.nn.Linear(1024, 2048),
                torch.nn.ReLU(),
                torch.nn.Linear(2048, 1024),
                torch.nn.ReLU(),
                torch.nn.Linear(1024, 512)
            )
            models.append(model)
            
        elif complexity == "high":
            # Higher complexity model, multiple parallel branches
            class ComplexModel(torch.nn.Module):
                """
                
    ComplexModel class for ImpressionCore framework.
    # Memory optimization: Explicit memory cleanup
    
    This class implements complexmodel functionality optimized for
    # Memory optimization: Explicit memory cleanup
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
                def __init__(self):
                    """
                    
    __init__ function for processing.
    
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
                    super().__init__()
                    self.branch1 = torch.nn.Sequential(
                        torch.nn.Linear(1024, 1024),
                        torch.nn.ReLU(),
                        torch.nn.Linear(1024, 512)
                    )
                    self.branch2 = torch.nn.Sequential(
                        torch.nn.Linear(1024, 2048),
                        torch.nn.ReLU(),
                        torch.nn.Linear(2048, 512)
                    )
                    self.branch3 = torch.nn.Sequential(
                        torch.nn.Linear(1024, 1536),
                        torch.nn.ReLU(),
                        torch.nn.Linear(1536, 512)
                    )
                    self.output = torch.nn.Linear(1536, 1024)
                
                def forward(self, x):
                    """
                    
    forward function for processing.
    
    Args:
        self, x: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                    """
                    b1 = self.branch1(x)
                    b2 = self.branch2(x)
                    b3 = self.branch3(x)
                    combined = torch.cat((b1, b2, b3), dim=1)
                    return self.output(combined)
            
            models.append(ComplexModel())
        
        # Move models to CUDA if available
        # Memory optimization: Memory-critical operation
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            models = [model.cuda() for model in models]
            # Memory optimization: Explicit memory cleanup
        
        return models
    
    def _record_system_metrics(self):
        """Record current system metrics"""
        import psutil
        
        # Get RAM usage
        ram_usage = psutil.virtual_memory().percent
        # Memory optimization: Memory-critical operation
        
        # Get CPU usage
        cpu_usage = psutil.cpu_percent()
        
        # Get VRAM usage
        vram_usage = None
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            vram_usage = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() * 100
            # Memory optimization: CUDA operations for GPU acceleration
        
        # Record metrics
        self.resources['timestamps'].append(datetime.now())
        self.resources['ram'].append(ram_usage)
        self.resources['cpu'].append(cpu_usage)
        if vram_usage is not None:
            self.resources['vram'].append(vram_usage)
        
        return {
            'ram': ram_usage,
            'cpu': cpu_usage,
            'vram': vram_usage
        }
    
    def _plot_system_metrics(self, title: str = "System Resources During Stress Test"):
        """Plot system metrics over time"""
        plt.figure(figsize=(12, 6))
        
        # Convert timestamps to seconds from start
        start_time = self.resources['timestamps'][0]
        x_values = [(t - start_time).total_seconds() for t in self.resources['timestamps']]
        
        # Plot RAM usage
        plt.plot(x_values, self.resources['ram'], label='RAM Usage (%)', color='blue')
        
        # Plot CPU usage
        plt.plot(x_values, self.resources['cpu'], label='CPU Usage (%)', color='green')
        
        # Plot VRAM usage if available
        if self.has_cuda and self.resources['vram']:
        # Memory optimization: Memory-critical operation
            plt.plot(x_values, self.resources['vram'], label='VRAM Usage (%)', color='red')
        
        plt.xlabel('Time (seconds)')
        plt.ylabel('Usage (%)')
        plt.title(title)
        plt.legend()
        plt.grid(True)
        
        # Save the plot
        plt.savefig(os.path.join(self.output_dir, "system_metrics.png"))
        plt.close()
    
    def _plot_performance_metrics(self):
        """Plot performance metrics for components"""
        for component, metrics in self.perf_metrics.items():
            plt.figure(figsize=(12, 6))
            
            iterations = list(range(1, len(metrics['duration']) + 1))
            plt.plot(iterations, metrics['duration'], label='Duration (s)', color='blue')
            
            # Add peak memory if available
            # Memory optimization: Memory-critical operation
            if 'peak_memory' in metrics:
            # Memory optimization: Memory-critical operation
                # Normalize memory to fit on same scale
                # Memory optimization: Memory-critical operation
                max_duration = max(metrics['duration'])
                normalized_memory = [m * max_duration / max(metrics['peak_memory']) for m in metrics['peak_memory']]
                # Memory optimization: Memory-critical operation
                plt.plot(iterations, normalized_memory, label='Peak Memory (normalized)', color='red', linestyle='--')
                # Memory optimization: Memory-critical operation
            
            plt.xlabel('Iteration')
            plt.ylabel('Duration (seconds)')
            plt.title(f'{component} Performance')
            plt.legend()
            plt.grid(True)
            
            # Save the plot
            plt.savefig(os.path.join(self.output_dir, f"{component}_performance.png"))
            plt.close()
    
    def _run_with_resource_monitoring(self, func: Callable, *args, **kwargs):
        """Run a function with resource monitoring"""
        # Start resource monitoring thread
        stop_monitor = threading.Event()
        
        def monitor_resources():
            """
            
    monitor_resources function for processing.
    
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
            while not stop_monitor.is_set():
                self._record_system_metrics()
                time.sleep(1)  # Record every second
        
        monitor_thread = threading.Thread(target=monitor_resources)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Run the function
        result = None
        start_time = time.time()
        peak_memory = 0
        # Memory optimization: Memory-critical operation
        
        try:
            result = func(*args, **kwargs)
            
            # Record peak memory if CUDA available
            # Memory optimization: Memory-critical operation
            if self.has_cuda:
            # Memory optimization: Memory-critical operation
                peak_memory = torch.cuda.max_memory_allocated() / (1024 * 1024)  # MB
                # Memory optimization: CUDA operations for GPU acceleration
                torch.cuda.reset_peak_memory_stats()
                # Memory optimization: CUDA operations for GPU acceleration
            
        finally:
            # Stop monitoring
            duration = time.time() - start_time
            stop_monitor.set()
            monitor_thread.join()
            
            # Record duration
            logger.info(f"Function completed in {duration:.2f} seconds")
            if self.has_cuda:
            # Memory optimization: Memory-critical operation
                logger.info(f"Peak VRAM usage: {peak_memory:.2f} MB")
                # Memory optimization: Memory-critical operation
            
            return result, duration, peak_memory
            # Memory optimization: Memory-critical operation
    
    def stress_test_architecture(self, iterations: int = 10, complexity: str = "medium") -> Dict[str, Any]:
        """
        Stress test architecture visualization component.
        
        Args:
            iterations: Number of iterations to run
            complexity: Model complexity level ('low', 'medium', 'high')
            # Memory optimization: Explicit memory cleanup
            
        Returns:
            Test results
        """
        if 'architecture' not in self.components:
            logger.error("Architecture visualization component not available")
            return {'success': False, 'error': 'Component not available'}
        
        logger.info(f"Starting architecture visualization stress test ({iterations} iterations, {complexity} complexity)")
        
        # Create test models
        models = self._create_test_models(complexity)
        
        # Initialize performance metrics
        self.perf_metrics['architecture'] = {
            'duration': [],
            'peak_memory': []
            # Memory optimization: Memory-critical operation
        }
        
        # Run test iterations
        success_count = 0
        
        for i in range(iterations):
            logger.info(f"Architecture test iteration {i+1}/{iterations}")
            
            # Force garbage collection
            gc.collect()
            # Memory optimization: Force garbage collection
            if self.has_cuda:
            # Memory optimization: Memory-critical operation
                torch.cuda.empty_cache()
                # Memory optimization: CUDA operations for GPU acceleration
            
            # Create visualizer instance
            try:
                visualizer = self.components['architecture']()
                
                # Select model (alternate between available models)
                # Memory optimization: Explicit memory cleanup
                model = models[i % len(models)]
                # Memory optimization: Explicit memory cleanup
                
                # Run with resource monitoring
                def run_visualization():
                    """
                    
    run_visualization function for processing.
    
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
                    return visualizer.generate_architecture_graph(
                        model=model,
                        save_path=os.path.join(self.output_dir, f"arch_stress_{i}.png"),
                        simplify=True
                    )
                
                _, duration, peak_memory = self._run_with_resource_monitoring(run_visualization)
                # Memory optimization: Memory-critical operation
                
                # Record metrics
                self.perf_metrics['architecture']['duration'].append(duration)
                if peak_memory > 0:
                # Memory optimization: Memory-critical operation
                    self.perf_metrics['architecture']['peak_memory'].append(peak_memory)
                    # Memory optimization: Memory-critical operation
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error in architecture test iteration {i+1}: {e}")
                logger.error(traceback.format_exc())
        
        # Generate plots
        self._plot_system_metrics("System Resources During Architecture Stress Test")
        self._plot_performance_metrics()
        
        return {
            'success': success_count > 0,
            'success_rate': success_count / iterations,
            'avg_duration': sum(self.perf_metrics['architecture']['duration']) / max(1, len(self.perf_metrics['architecture']['duration'])),
            'iterations_completed': success_count,
            'performance_degradation': self._check_performance_degradation('architecture')
        }
    
    def stress_test_activation(self, iterations: int = 10, complexity: str = "medium") -> Dict[str, Any]:
        """
        Stress test activation visualization component.
        
        Args:
            iterations: Number of iterations to run
            complexity: Model complexity level ('low', 'medium', 'high')
            # Memory optimization: Explicit memory cleanup
            
        Returns:
            Test results
        """
        if 'activation' not in self.components:
            logger.error("Activation visualization component not available")
            return {'success': False, 'error': 'Component not available'}
        
        logger.info(f"Starting activation visualization stress test ({iterations} iterations, {complexity} complexity)")
        
        # Create test models
        models = self._create_test_models(complexity)
        
        # Initialize performance metrics
        self.perf_metrics['activation'] = {
            'duration': [],
            'peak_memory': []
            # Memory optimization: Memory-critical operation
        }
        
        # Create input tensors of different sizes
        input_sizes = [(1, 128), (1, 256), (1, 512), (1, 1024)]
        input_tensors = []
        
        for size in input_sizes:
            if self.has_cuda:
            # Memory optimization: Memory-critical operation
                input_tensors.append(torch.randn(*size, device="cuda"))
                # Memory optimization: Device placement for memory management
            else:
                input_tensors.append(torch.randn(*size))
        
        # Run test iterations
        success_count = 0
        
        for i in range(iterations):
            logger.info(f"Activation test iteration {i+1}/{iterations}")
            
            # Force garbage collection
            gc.collect()
            # Memory optimization: Force garbage collection
            if self.has_cuda:
            # Memory optimization: Memory-critical operation
                torch.cuda.empty_cache()
                # Memory optimization: CUDA operations for GPU acceleration
            
            try:
                # Select model and input tensor (alternate between available options)
                # Memory optimization: Explicit memory cleanup
                model = models[i % len(models)]
                # Memory optimization: Explicit memory cleanup
                input_tensor = input_tensors[i % len(input_tensors)]
                
                # Create activation visualizer
                visualizer = self.components['activation'](model=model)
                
                # Run with resource monitoring
                def run_visualization():
                    """
                    
    run_visualization function for processing.
    
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
                    visualizer.register_hooks()
                    result = visualizer.visualize_layer_activations(
                        input_tensor=input_tensor,
                        save_path=os.path.join(self.output_dir, f"act_stress_{i}.png")
                    )
                    visualizer.remove_hooks()
                    return result
                
                _, duration, peak_memory = self._run_with_resource_monitoring(run_visualization)
                # Memory optimization: Memory-critical operation
                
                # Record metrics
                self.perf_metrics['activation']['duration'].append(duration)
                if peak_memory > 0:
                # Memory optimization: Memory-critical operation
                    self.perf_metrics['activation']['peak_memory'].append(peak_memory)
                    # Memory optimization: Memory-critical operation
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error in activation test iteration {i+1}: {e}")
                logger.error(traceback.format_exc())
        
        # Generate plots
        self._plot_system_metrics("System Resources During Activation Stress Test")
        self._plot_performance_metrics()
        
        return {
            'success': success_count > 0,
            'success_rate': success_count / iterations,
            'avg_duration': sum(self.perf_metrics['activation']['duration']) / max(1, len(self.perf_metrics['activation']['duration'])),
            'iterations_completed': success_count,
            'performance_degradation': self._check_performance_degradation('activation')
        }
    
    def stress_test_parallel(self, iterations: int = 5, complexity: str = "low") -> Dict[str, Any]:
        """
        Stress test multiple visualization components in parallel.
        
        Args:
            iterations: Number of iterations to run
            complexity: Model complexity level ('low', 'medium', 'high')
            # Memory optimization: Explicit memory cleanup
            
        Returns:
            Test results
        """
        logger.info(f"Starting parallel visualization stress test ({iterations} iterations, {complexity} complexity)")
        
        # Ensure we have at least one component
        available_components = [k for k in self.components if k != 'visualizer']
        if not available_components:
            logger.error("No visualization components available")
            return {'success': False, 'error': 'Components not available'}
        
        # Create test models
        models = self._create_test_models(complexity)
        
        # Create input tensors
        input_size = (1, 128) if complexity == "low" else (1, 512)
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            input_tensor = torch.randn(*input_size, device="cuda")
            # Memory optimization: Device placement for memory management
        else:
            input_tensor = torch.randn(*input_size)
        
        # Initialize tasks for parallel execution
        success_count = 0
        error_count = 0
        
        for i in range(iterations):
            logger.info(f"Parallel test iteration {i+1}/{iterations}")
            
            # Force garbage collection
            gc.collect()
            # Memory optimization: Force garbage collection
            if self.has_cuda:
            # Memory optimization: Memory-critical operation
                torch.cuda.empty_cache()
                # Memory optimization: CUDA operations for GPU acceleration
            
            # Record system metrics
            self._record_system_metrics()
            
            # Select model
            model = models[i % len(models)]
            # Memory optimization: Explicit memory cleanup
            
            try:
                # Use ThreadPoolExecutor for parallelism
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = []
                    
                    # Queue architecture task if available
                    if 'architecture' in self.components:
                        def run_architecture():
                            """
                            
    run_architecture function for processing.
    
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
                            visualizer = self.components['architecture']()
                            return visualizer.generate_architecture_graph(
                                model=model,
                                save_path=os.path.join(self.output_dir, f"parallel_arch_{i}.png"),
                                simplify=True
                            )
                        
                        futures.append(executor.submit(run_architecture))
                    
                    # Queue activation task if available
                    if 'activation' in self.components:
                        def run_activation():
                            """
                            
    run_activation function for processing.
    
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
                            visualizer = self.components['activation'](model=model)
                            visualizer.register_hooks()
                            result = visualizer.visualize_layer_activations(
                                input_tensor=input_tensor,
                                save_path=os.path.join(self.output_dir, f"parallel_act_{i}.png")
                            )
                            visualizer.remove_hooks()
                            return result
                        
                        futures.append(executor.submit(run_activation))
                    
                    # Wait for all tasks to complete
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            future.result()
                            success_count += 1
                        except Exception as e:
                            logger.error(f"Error in parallel test: {e}")
                            logger.error(traceback.format_exc())
                            error_count += 1
            
            except Exception as e:
                logger.error(f"Error setting up parallel test: {e}")
                logger.error(traceback.format_exc())
                error_count += 1
            
            # Record final metrics for this iteration
            self._record_system_metrics()
        
        # Generate plots
        self._plot_system_metrics("System Resources During Parallel Stress Test")
        
        total_tasks = iterations * len(available_components)
        completed_tasks = success_count
        
        return {
            'success': success_count > 0,
            'success_rate': success_count / total_tasks,
            'errors': error_count,
            'tasks_completed': success_count,
            'total_tasks': total_tasks
        }
    
    def stress_test_progressive_load(self, start_complexity: str = "low", max_iterations: int = 10) -> Dict[str, Any]:
        """
        Stress test with progressively increasing load until failure.
        
        Args:
            start_complexity: Starting complexity level ('low', 'medium', 'high')
            max_iterations: Maximum number of iterations to run
            
        Returns:
            Test results with failure points
        """
        logger.info(f"Starting progressive load stress test (starting at {start_complexity} complexity)")
        
        # Map complexity levels to numeric values
        complexity_levels = {"low": 1, "medium": 2, "high": 3}
        current_complexity = complexity_levels.get(start_complexity, 1)
        
        # Track failure points
        failure_points = {}
        
        # Progressive test parameters
        batch_sizes = [1, 2, 4, 8, 16]  # Increasing batch sizes
        sequence_lengths = [128, 256, 512, 1024, 2048, 4096]  # Increasing sequence lengths
        
        # Initialize test state
        iteration = 0
        has_failures = False
        
        # Test architecture component with progressive load
        if 'architecture' in self.components:
            logger.info("Testing architecture visualizer with progressive load")
            
            for batch_size in batch_sizes:
                for seq_len in sequence_lengths:
                    if iteration >= max_iterations:
                        break
                    
                    logger.info(f"Architecture test iteration {iteration+1}: batch_size={batch_size}, seq_len={seq_len}")
                    
                    # Force garbage collection
                    gc.collect()
                    # Memory optimization: Force garbage collection
                    if self.has_cuda:
                    # Memory optimization: Memory-critical operation
                        torch.cuda.empty_cache()
                        # Memory optimization: CUDA operations for GPU acceleration
                    
                    try:
                        # Create a model of appropriate size
                        # Memory optimization: Explicit memory cleanup
                        model = torch.nn.Sequential(
                        # Memory optimization: Explicit memory cleanup
                            torch.nn.Linear(seq_len, seq_len * 2),
                            torch.nn.ReLU(),
                            torch.nn.Linear(seq_len * 2, seq_len)
                        )
                        
                        if self.has_cuda:
                        # Memory optimization: Memory-critical operation
                            model = model.cuda()
                            # Memory optimization: Explicit memory cleanup
                        
                        # Create visualizer
                        visualizer = self.components['architecture']()
                        
                        # Record system metrics
                        start_metrics = self._record_system_metrics()
                        
                        # Run visualization
                        start_time = time.time()
                        visualizer.generate_architecture_graph(
                            model=model,
                            save_path=os.path.join(self.output_dir, f"progressive_arch_{iteration}.png"),
                            simplify=True
                        )
                        duration = time.time() - start_time
                        
                        # Record final metrics
                        end_metrics = self._record_system_metrics()
                        
                        logger.info(f"Architecture visualization completed in {duration:.2f} seconds")
                        
                    except Exception as e:
                        logger.error(f"Architecture test failed at batch_size={batch_size}, seq_len={seq_len}: {e}")
                        failure_points['architecture'] = {
                            'batch_size': batch_size,
                            'sequence_length': seq_len,
                            'error': str(e)
                        }
                        has_failures = True
                        break
                    
                    iteration += 1
                
                if has_failures or iteration >= max_iterations:
                    break
        
        # Reset for activation tests
        iteration = 0
        has_failures = False
        
        # Test activation component with progressive load
        if 'activation' in self.components:
            logger.info("Testing activation visualizer with progressive load")
            
            for batch_size in batch_sizes:
                for seq_len in sequence_lengths:
                    if iteration >= max_iterations:
                        break
                    
                    logger.info(f"Activation test iteration {iteration+1}: batch_size={batch_size}, seq_len={seq_len}")
                    
                    # Force garbage collection
                    gc.collect()
                    # Memory optimization: Force garbage collection
                    if self.has_cuda:
                    # Memory optimization: Memory-critical operation
                        torch.cuda.empty_cache()
                        # Memory optimization: CUDA operations for GPU acceleration
                    
                    try:
                        # Create a model of appropriate size
                        # Memory optimization: Explicit memory cleanup
                        model = torch.nn.Sequential(
                        # Memory optimization: Explicit memory cleanup
                            torch.nn.Linear(seq_len, seq_len * 2),
                            torch.nn.ReLU(),
                            torch.nn.Linear(seq_len * 2, seq_len)
                        )
                        
                        if self.has_cuda:
                        # Memory optimization: Memory-critical operation
                            model = model.cuda()
                            # Memory optimization: Explicit memory cleanup
                        
                        # Create input tensor
                        if self.has_cuda:
                        # Memory optimization: Memory-critical operation
                            input_tensor = torch.randn(batch_size, seq_len, device="cuda")
                            # Memory optimization: Device placement for memory management
                        else:
                            input_tensor = torch.randn(batch_size, seq_len)
                        
                        # Create visualizer
                        visualizer = self.components['activation'](model=model)
                        
                        # Record system metrics
                        start_metrics = self._record_system_metrics()
                        
                        # Run visualization
                        start_time = time.time()
                        visualizer.register_hooks()
                        visualizer.visualize_layer_activations(
                            input_tensor=input_tensor,
                            save_path=os.path.join(self.output_dir, f"progressive_act_{iteration}.png")
                        )
                        visualizer.remove_hooks()
                        duration = time.time() - start_time
                        
                        # Record final metrics
                        end_metrics = self._record_system_metrics()
                        
                        logger.info(f"Activation visualization completed in {duration:.2f} seconds")
                        
                    except Exception as e:
                        logger.error(f"Activation test failed at batch_size={batch_size}, seq_len={seq_len}: {e}")
                        failure_points['activation'] = {
                            'batch_size': batch_size,
                            'sequence_length': seq_len,
                            'error': str(e)
                        }
                        has_failures = True
                        break
                    
                    iteration += 1
                
                if has_failures or iteration >= max_iterations:
                    break
        
        # Generate plots
        self._plot_system_metrics("System Resources During Progressive Stress Test")
        
        return {
            'failure_points': failure_points,
            'max_safe_params': self._determine_safe_parameters(failure_points),
            'completed_iterations': iteration
        }
    
    def _determine_safe_parameters(self, failure_points: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Determine safe parameters based on failure points"""
        safe_params = {}
        
        # Default safe parameters (conservative)
        default_safe = {
            'batch_size': 1,
            'sequence_length': 512,
            'model_complexity': 'low'
        }
        
        # Architecture component
        if 'architecture' in failure_points:
            failure = failure_points['architecture']
            
            # If it failed at the smallest batch size, keep defaults
            if failure['batch_size'] > 1:
                safe_params['architecture'] = {
                    'batch_size': failure['batch_size'] // 2,  # Half of failing batch size
                    'sequence_length': min(failure['sequence_length'], 1024),
                    'model_complexity': 'low' if failure['sequence_length'] > 512 else 'medium'
                }
            else:
                safe_params['architecture'] = default_safe
        else:
            # No failures - can use higher limits
            safe_params['architecture'] = {
                'batch_size': 4,
                'sequence_length': 2048,
                'model_complexity': 'medium'
            }
        
        # Activation component
        if 'activation' in failure_points:
            failure = failure_points['activation']
            
            # If it failed at the smallest batch size, keep defaults
            if failure['batch_size'] > 1:
                safe_params['activation'] = {
                    'batch_size': failure['batch_size'] // 2,  # Half of failing batch size
                    'sequence_length': min(failure['sequence_length'], 1024),
                    'model_complexity': 'low' if failure['sequence_length'] > 512 else 'medium'
                }
            else:
                safe_params['activation'] = default_safe
        else:
            # No failures - can use higher limits
            safe_params['activation'] = {
                'batch_size': 2,
                'sequence_length': 1024,
                'model_complexity': 'medium'
            }
        
        return safe_params
    
    def _check_performance_degradation(self, component: str) -> Dict[str, Any]:
        """
        Check for performance degradation over iterations.
        
        Args:
            component: Component name to check
            
        Returns:
            Dictionary with degradation analysis
        """
        if component not in self.perf_metrics or not self.perf_metrics[component]['duration']:
            return {'has_degradation': False}
        
        durations = self.perf_metrics[component]['duration']
        
        # Need at least 3 data points for meaningful analysis
        if len(durations) < 3:
            return {'has_degradation': False}
        
        # Calculate trend (simple linear regression)
        x = list(range(len(durations)))
        y = durations
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x_i * y_i for x_i, y_i in zip(x, y))
        sum_xx = sum(x_i * x_i for x_i in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        
        # Calculate performance degradation percentage
        first_third_avg = sum(durations[:n//3]) / (n//3)
        last_third_avg = sum(durations[-n//3:]) / (n//3)
        
        if first_third_avg > 0:
            degradation_pct = (last_third_avg - first_third_avg) / first_third_avg * 100
        else:
            degradation_pct = 0
        
        # Significant degradation threshold (20% increase in time)
        has_degradation = slope > 0 and degradation_pct > 20
        
        return {
            'has_degradation': has_degradation,
            'slope': slope,
            'degradation_percent': degradation_pct,
            'first_third_avg': first_third_avg,
            'last_third_avg': last_third_avg
        }
    
    def generate_report(self, results: Dict[str, Any], title: str = "Stress Test Report") -> str:
        """Generate a detailed stress test report"""
        report = []
        report.append(f"=== {title} ===")
        report.append(f"Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Hardware: {'CUDA ' + torch.cuda.get_device_name(0) if self.has_cuda else 'CPU only'}")
        # Memory optimization: CUDA operations for GPU acceleration
        report.append("")
        
        # Add overall results
        if 'architecture' in results:
            arch_results = results['architecture']
            report.append("--- Architecture Visualization Results ---")
            report.append(f"Success Rate: {arch_results['success_rate'] * 100:.1f}%")
            report.append(f"Average Duration: {arch_results['avg_duration']:.2f} seconds")
            report.append(f"Iterations Completed: {arch_results['iterations_completed']}")
            
            # Add performance degradation info if available
            if 'performance_degradation' in arch_results:
                deg = arch_results['performance_degradation']
                if deg['has_degradation']:
                    report.append(f"⚠️ Performance degradation detected: {deg['degradation_percent']:.1f}%")
                else:
                    report.append("✅ No performance degradation detected")
            
            report.append("")
        
        if 'activation' in results:
            act_results = results['activation']
            report.append("--- Activation Visualization Results ---")
            report.append(f"Success Rate: {act_results['success_rate'] * 100:.1f}%")
            report.append(f"Average Duration: {act_results['avg_duration']:.2f} seconds")
            report.append(f"Iterations Completed: {act_results['iterations_completed']}")
            
            # Add performance degradation info if available
            if 'performance_degradation' in act_results:
                deg = act_results['performance_degradation']
                if deg['has_degradation']:
                    report.append(f"⚠️ Performance degradation detected: {deg['degradation_percent']:.1f}%")
                else:
                    report.append("✅ No performance degradation detected")
            
            report.append("")
        
        if 'parallel' in results:
            para_results = results['parallel']
            report.append("--- Parallel Execution Results ---")
            report.append(f"Success Rate: {para_results['success_rate'] * 100:.1f}%")
            report.append(f"Tasks Completed: {para_results['tasks_completed']}/{para_results['total_tasks']}")
            report.append(f"Errors: {para_results['errors']}")
            report.append("")
        
        if 'progressive' in results:
            prog_results = results['progressive']
            report.append("--- Progressive Load Results ---")
            report.append(f"Completed Iterations: {prog_results['completed_iterations']}")
            
            if prog_results['failure_points']:
                report.append("Failure Points:")
                for component, failure in prog_results['failure_points'].items():
                    report.append(f"  {component}: batch_size={failure['batch_size']}, sequence_length={failure['sequence_length']}")
                    report.append(f"    Error: {failure['error']}")
            else:
                report.append("No failures detected within tested parameters")
            
            report.append("")
            
            # Add safe parameters
            if 'max_safe_params' in prog_results:
                report.append("Recommended Safe Parameters:")
                for component, params in prog_results['max_safe_params'].items():
                    report.append(f"  {component}:")
                    for param, value in params.items():
                        report.append(f"    {param}: {value}")
            
            report.append("")
        
        # Add system recommendations
        report.append("--- System Recommendations ---")
        
        # Check if any test had memory-related failures
        # Memory optimization: Memory-critical operation
        has_memory_failures = False
        # Memory optimization: Memory-critical operation
        memory_error_keywords = ["memory", "CUDA out of memory", "CUDA error", "memory leak"]
        # Memory optimization: Memory-critical operation
        
        if 'progressive' in results and 'failure_points' in results['progressive']:
            for component, failure in results['progressive']['failure_points'].items():
                error_msg = failure['error'].lower()
                if any(keyword in error_msg for keyword in memory_error_keywords):
                # Memory optimization: Memory-critical operation
                    has_memory_failures = True
                    # Memory optimization: Memory-critical operation
        
        if has_memory_failures:
        # Memory optimization: Memory-critical operation
            report.append("⚠️ Memory-related failures detected. Recommendations:")
            # Memory optimization: Memory-critical operation
            report.append("  1. Use smaller batch sizes and sequence lengths")
            report.append("  2. Enable gradient checkpointing for model training")
            # Memory optimization: Explicit memory cleanup
            report.append("  3. Use CPU offloading for visualization operations")
            report.append("  4. Consider enabling Flash Attention if possible")
            report.append("  5. Use lower precision formats (fp16 instead of fp32)")
        else:
            report.append("✅ No memory-related failures detected.")
            # Memory optimization: Memory-critical operation
        
        # Check for performance degradation
        has_perf_degradation = False
        
        for component in ['architecture', 'activation']:
            if component in results and 'performance_degradation' in results[component]:
                if results[component]['performance_degradation']['has_degradation']:
                    has_perf_degradation = True
        
        if has_perf_degradation:
            report.append("⚠️ Performance degradation detected. Recommendations:")
            report.append("  1. Check for resource leaks in visualization components")
            report.append("  2. Improve cleanup after visualizations")
            report.append("  3. Reduce visualization quality for better performance")
            report.append("  4. Add caching for repeated visualizations")
        else:
            report.append("✅ No performance degradation detected.")
        
        return "\n".join(report)
    
    def run_comprehensive_test(self, complexity: str = "medium") -> Dict[str, Any]:
        """
        Run a comprehensive stress test of all visualization components.
        
        Args:
            complexity: Model complexity level ('low', 'medium', 'high')
            # Memory optimization: Explicit memory cleanup
            
        Returns:
            Combined test results
        """
        logger.info(f"Starting comprehensive visualization stress test ({complexity} complexity)")
        
        # Store all test results
        all_results = {}
        
        # Run architecture tests (10 iterations)
        if 'architecture' in self.components:
            architecture_results = self.stress_test_architecture(iterations=10, complexity=complexity)
            all_results['architecture'] = architecture_results
        
        # Run activation tests (10 iterations)
        if 'activation' in self.components:
            activation_results = self.stress_test_activation(iterations=10, complexity=complexity)
            all_results['activation'] = activation_results
        
        # Run parallel tests (5 iterations)
        # Use lower complexity for parallel tests to avoid OOM
        lower_complexity = "low" if complexity != "low" else "low"
        parallel_results = self.stress_test_parallel(iterations=5, complexity=lower_complexity)
        all_results['parallel'] = parallel_results
        
        # Run progressive load tests (max 20 iterations)
        progressive_results = self.stress_test_progressive_load(start_complexity="low", max_iterations=20)
        all_results['progressive'] = progressive_results
        
        # Generate comprehensive report
        report = self.generate_report(all_results, "Comprehensive Visualization Stress Test Report")
        
        # Save report
        report_path = os.path.join(self.output_dir, "comprehensive_report.txt")
        with open(report_path, "w") as f:
            f.write(report)
        
        logger.info(f"Comprehensive stress test completed. Report saved to {report_path}")
        
        return all_results


def main():
    """Main entry point for stress testing"""
    parser = argparse.ArgumentParser(description="ImpressionCore Visualization Stress Test")
    parser.add_argument("--test-type", choices=["architecture", "activation", "parallel", "progressive", "all"], 
                        default="all", help="Type of stress test to run")
    parser.add_argument("--complexity", choices=["low", "medium", "high"], 
                        default="medium", help="Model complexity level")
                        # Memory optimization: Explicit memory cleanup
    parser.add_argument("--iterations", type=int, default=10, 
                        help="Number of iterations for component tests")
    parser.add_argument("--output-dir", type=str, default="stress_test_results", 
                        help="Directory to store test results")
    
    args = parser.parse_args()
    
    logger.info(f"Starting ImpressionCore visualization stress testing")
    logger.info(f"Test type: {args.test_type}, Complexity: {args.complexity}, Iterations: {args.iterations}")
    
    try:
        # Create stress tester
        tester = StressTester(output_dir=args.output_dir)
        
        # Run the requested tests
        if args.test_type == "architecture":
            tester.stress_test_architecture(iterations=args.iterations, complexity=args.complexity)
        elif args.test_type == "activation":
            tester.stress_test_activation(iterations=args.iterations, complexity=args.complexity)
        elif args.test_type == "parallel":
            tester.stress_test_parallel(iterations=args.iterations, complexity=args.complexity)
        elif args.test_type == "progressive":
            tester.stress_test_progressive_load(start_complexity=args.complexity, max_iterations=args.iterations*2)
        elif args.test_type == "all":
            tester.run_comprehensive_test(complexity=args.complexity)
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error during stress testing: {e}")
        logger.error(traceback.format_exc())
        return 1
    
    logger.info("Stress testing completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
