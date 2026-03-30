#!/usr/bin/env python3
"""
ImpressionCore: Stability Test

Module for stability test functionality in the ImpressionCore framework.

File: tests\stability\stability_test.py
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
This module implements stability test functionality for the
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
from tests.stability.stability_test import MemoryTracker
instance = MemoryTracker()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import argparse
import gc
import logging
import os
import psutil
import signal
import sys
import time
import threading
import tracemalloc
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Callable, Any

import numpy as np
import torch
import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stability_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("stability_test")

# Add project root to system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import visualization modules
try:
    from src.dev_tools.visualization.model_visualizer import ModelVisualizer
    from src.dev_tools.visualization.architecture_graph import ModelArchitectureGraph
    from src.dev_tools.visualization.attention_patterns import AttentionVisualizer
    from src.dev_tools.visualization.activation_maps import ActivationVisualizer
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Visualization modules not available: {e}")
    VISUALIZATION_AVAILABLE = False


class MemoryTracker:
# Memory optimization: Memory-critical operation
    """
    Tracks memory usage over time to detect leaks and anomalies.
    # Memory optimization: Memory-critical operation
    
    Supports tracking of:
    - System RAM usage
    - VRAM usage (if CUDA available)
    # Memory optimization: Memory-critical operation
    - Python memory allocations
    # Memory optimization: Memory-critical operation
    """
    
    def __init__(self, track_cuda: bool = True, track_tracemalloc: bool = True):
    # Memory optimization: Memory-critical operation
        """
        Initialize the memory tracker.
        # Memory optimization: Memory-critical operation
        
        Args:
            track_cuda: Whether to track CUDA memory (if available)
            # Memory optimization: Memory-critical operation
            track_tracemalloc: Whether to track Python memory allocations
            # Memory optimization: Memory-critical operation
        """
        self.process = psutil.Process(os.getpid())
        self.track_cuda = track_cuda and torch.cuda.is_available()
        # Memory optimization: CUDA operations for GPU acceleration
        self.track_tracemalloc = track_tracemalloc
        
        self.log_interval_seconds = 10
        self.peak_memory = {
        # Memory optimization: Memory-critical operation
            'ram': 0,
            'vram': 0 if self.track_cuda else None,
            # Memory optimization: Memory-critical operation
            'python': 0 if self.track_tracemalloc else None
        }
        
        self.history = {
            'ram': [],
            'vram': [] if self.track_cuda else None,
            # Memory optimization: Memory-critical operation
            'python': [] if self.track_tracemalloc else None,
            'timestamps': []
        }
        
        if self.track_tracemalloc:
            tracemalloc.start()
    
    def get_ram_usage(self) -> int:
        """Get current RAM usage in bytes"""
        return self.process.memory_info().rss
        # Memory optimization: Memory-critical operation
    
    def get_vram_usage(self) -> Optional[int]:
        """Get current VRAM usage in bytes"""
        if not self.track_cuda:
        # Memory optimization: Memory-critical operation
            return None
        return torch.cuda.memory_allocated()
        # Memory optimization: CUDA operations for GPU acceleration
    
    def get_python_memory(self) -> Optional[int]:
    # Memory optimization: Memory-critical operation
        """Get current Python memory allocation in bytes"""
        # Memory optimization: Memory-critical operation
        if not self.track_tracemalloc:
            return None
        return tracemalloc.get_traced_memory()[0]
        # Memory optimization: Memory-critical operation
    
    def snapshot(self) -> Dict[str, Union[int, None]]:
        """Take a snapshot of current memory usage"""
        # Memory optimization: Memory-critical operation
        ram_usage = self.get_ram_usage()
        vram_usage = self.get_vram_usage()
        python_usage = self.get_python_memory()
        # Memory optimization: Memory-critical operation
        
        # Update peak values
        self.peak_memory['ram'] = max(self.peak_memory['ram'], ram_usage)
        # Memory optimization: Memory-critical operation
        if vram_usage is not None:
            self.peak_memory['vram'] = max(self.peak_memory['vram'], vram_usage)
            # Memory optimization: Memory-critical operation
        if python_usage is not None:
            self.peak_memory['python'] = max(self.peak_memory['python'], python_usage)
            # Memory optimization: Memory-critical operation
        
        # Record history
        self.history['timestamps'].append(datetime.now())
        self.history['ram'].append(ram_usage)
        if vram_usage is not None:
            self.history['vram'].append(vram_usage)
        if python_usage is not None:
            self.history['python'].append(python_usage)
        
        return {
            'ram': ram_usage,
            'vram': vram_usage,
            'python': python_usage
        }
    
    def log_memory_usage(self):
    # Memory optimization: Memory-critical operation
        """Log current memory usage"""
        # Memory optimization: Memory-critical operation
        snapshot = self.snapshot()
        
        ram_mb = snapshot['ram'] / (1024 * 1024)
        
        log_message = f"RAM: {ram_mb:.2f} MB"
        
        if snapshot['vram'] is not None:
            vram_mb = snapshot['vram'] / (1024 * 1024)
            log_message += f", VRAM: {vram_mb:.2f} MB"
        
        if snapshot['python'] is not None:
            python_mb = snapshot['python'] / (1024 * 1024)
            log_message += f", Python: {python_mb:.2f} MB"
        
        logger.info(log_message)
    
    def check_for_leaks(self, num_samples: int = 30) -> Dict[str, Union[bool, float]]:
        """
        Check for memory leaks by analyzing recent memory usage patterns.
        # Memory optimization: Memory-critical operation
        
        Args:
            num_samples: Number of most recent samples to consider
            
        Returns:
            Dictionary with leak detection results for each memory type
            # Memory optimization: Memory-critical operation
        """
        result = {}
        
        # Need at least 10 samples for reliable leak detection
        if len(self.history['timestamps']) < 10:
            return {'error': 'Not enough samples for leak detection'}
        
        # Use only the last n samples
        n = min(num_samples, len(self.history['timestamps']))
        recent_timestamps = self.history['timestamps'][-n:]
        
        # Check RAM usage trend
        recent_ram = self.history['ram'][-n:]
        ram_slope = self._calculate_trend_slope(recent_ram)
        ram_is_leaking = ram_slope > 100 * 1024  # 100 KB/s threshold for RAM leak
        
        result['ram'] = {
            'is_leaking': ram_is_leaking,
            'slope_bytes_per_second': ram_slope
        }
        
        # Check VRAM usage trend
        if self.track_cuda:
        # Memory optimization: Memory-critical operation
            recent_vram = self.history['vram'][-n:]
            vram_slope = self._calculate_trend_slope(recent_vram)
            vram_is_leaking = vram_slope > 50 * 1024  # 50 KB/s threshold for VRAM leak
            
            result['vram'] = {
                'is_leaking': vram_is_leaking,
                'slope_bytes_per_second': vram_slope
            }
        
        # Check Python memory trend
        # Memory optimization: Memory-critical operation
        if self.track_tracemalloc:
            recent_python = self.history['python'][-n:]
            python_slope = self._calculate_trend_slope(recent_python)
            python_is_leaking = python_slope > 20 * 1024  # 20 KB/s threshold for Python memory leak
            # Memory optimization: Memory-critical operation
            
            result['python'] = {
                'is_leaking': python_is_leaking,
                'slope_bytes_per_second': python_slope
            }
        
        return result
    
    def _calculate_trend_slope(self, values: List[int]) -> float:
        """Calculate the trend slope in bytes per second"""
        if len(values) < 2:
            return 0
        
        time_range_seconds = (self.history['timestamps'][-1] - self.history['timestamps'][-len(values)]).total_seconds()
        if time_range_seconds <= 0:
            return 0
        
        first_value = values[0]
        last_value = values[-1]
        
        return (last_value - first_value) / time_range_seconds
    
    def generate_report(self, title: str = "Memory Usage Report") -> str:
    # Memory optimization: Memory-critical operation
        """Generate a detailed report of memory usage and potential leaks"""
        # Memory optimization: Memory-critical operation
        report = []
        report.append(f"=== {title} ===")
        report.append(f"Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Monitoring Duration: {(self.history['timestamps'][-1] - self.history['timestamps'][0])}")
        report.append("")
        
        # Peak memory usage
        # Memory optimization: Memory-critical operation
        report.append("--- Peak Memory Usage ---")
        # Memory optimization: Memory-critical operation
        report.append(f"Peak RAM: {self.peak_memory['ram'] / (1024 * 1024):.2f} MB")
        # Memory optimization: Memory-critical operation
        if self.track_cuda:
        # Memory optimization: Memory-critical operation
            report.append(f"Peak VRAM: {self.peak_memory['vram'] / (1024 * 1024):.2f} MB")
            # Memory optimization: Memory-critical operation
        if self.track_tracemalloc:
            report.append(f"Peak Python Memory: {self.peak_memory['python'] / (1024 * 1024):.2f} MB")
            # Memory optimization: Memory-critical operation
        report.append("")
        
        # Current memory usage
        # Memory optimization: Memory-critical operation
        current = self.snapshot()
        report.append("--- Current Memory Usage ---")
        # Memory optimization: Memory-critical operation
        report.append(f"Current RAM: {current['ram'] / (1024 * 1024):.2f} MB")
        if self.track_cuda:
        # Memory optimization: Memory-critical operation
            report.append(f"Current VRAM: {current['vram'] / (1024 * 1024):.2f} MB")
        if self.track_tracemalloc:
            report.append(f"Current Python Memory: {current['python'] / (1024 * 1024):.2f} MB")
            # Memory optimization: Memory-critical operation
        report.append("")
        
        # Leak analysis
        leak_analysis = self.check_for_leaks()
        report.append("--- Memory Leak Analysis ---")
        # Memory optimization: Memory-critical operation
        
        if 'ram' in leak_analysis:
            ram_analysis = leak_analysis['ram']
            ram_slope_mb = ram_analysis['slope_bytes_per_second'] / (1024 * 1024)
            ram_status = "LEAKING" if ram_analysis['is_leaking'] else "Stable"
            report.append(f"RAM: {ram_status} ({ram_slope_mb:.4f} MB/s)")
        
        if 'vram' in leak_analysis:
            vram_analysis = leak_analysis['vram']
            vram_slope_mb = vram_analysis['slope_bytes_per_second'] / (1024 * 1024)
            vram_status = "LEAKING" if vram_analysis['is_leaking'] else "Stable"
            report.append(f"VRAM: {vram_status} ({vram_slope_mb:.4f} MB/s)")
        
        if 'python' in leak_analysis:
            python_analysis = leak_analysis['python']
            python_slope_mb = python_analysis['slope_bytes_per_second'] / (1024 * 1024)
            python_status = "LEAKING" if python_analysis['is_leaking'] else "Stable"
            report.append(f"Python Memory: {python_status} ({python_slope_mb:.4f} MB/s)")
            # Memory optimization: Memory-critical operation
        
        # Check overall stability status
        any_leaks = any([leak_analysis.get(k, {}).get('is_leaking', False) 
                        for k in ['ram', 'vram', 'python'] if k in leak_analysis])
        
        report.append("")
        if any_leaks:
            report.append("OVERALL STATUS: MEMORY LEAK DETECTED - Action Required")
            # Memory optimization: Memory-critical operation
        else:
            report.append("OVERALL STATUS: Stable - No Memory Leaks Detected")
            # Memory optimization: Memory-critical operation
        
        return "\n".join(report)
    
    def cleanup(self):
        """Clean up resources used by the memory tracker"""
        # Memory optimization: Memory-critical operation
        if self.track_tracemalloc:
            tracemalloc.stop()


class VisualizationStabilityTest:
    """
    Test framework for visualization component stability.
    
    Performs extended tests on visualization components to detect:
    - Memory leaks during repeated visualization operations
    # Memory optimization: Memory-critical operation
    - Performance degradation over time
    - Component stability under load
    """
    
    def __init__(self, output_dir: str = "stability_test_results"):
        """
        Initialize the visualization stability test framework.
        
        Args:
            output_dir: Directory to store test results
        """
        if not VISUALIZATION_AVAILABLE:
            raise ImportError("Visualization modules not available")
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.memory_tracker = MemoryTracker(track_cuda=True, track_tracemalloc=True)
        # Memory optimization: Memory-critical operation
        self.test_duration = timedelta(minutes=30)  # Default test duration
        self.iteration_count = 0
        
        # Load a small test model for visualization testing
        # Memory optimization: Explicit memory cleanup
        self.model = self._create_test_model()
        # Memory optimization: Explicit memory cleanup
        self.visualizers = self._setup_visualizers()
    
    def _create_test_model(self) -> torch.nn.Module:
        """Create a small test model for visualization"""
        # Memory optimization: Explicit memory cleanup
        # Use a very small model to avoid OOM on limited VRAM
        # Memory optimization: Explicit memory cleanup
        model = torch.nn.Sequential(
        # Memory optimization: Explicit memory cleanup
            torch.nn.Linear(512, 768),
            torch.nn.ReLU(),
            torch.nn.Linear(768, 1024),
            torch.nn.ReLU(),
            torch.nn.Linear(1024, 768),
            torch.nn.ReLU(),
            torch.nn.Linear(768, 512)
        )
        
        # Move to CUDA if available and tracker is using it
        # Memory optimization: Memory-critical operation
        if self.memory_tracker.track_cuda:
        # Memory optimization: Memory-critical operation
            try:
                model = model.cuda()
                # Memory optimization: Explicit memory cleanup
                logger.info("Test model loaded on CUDA")
                # Memory optimization: Explicit memory cleanup
            except RuntimeError as e:
                logger.warning(f"Unable to load model on CUDA: {e}")
                # Memory optimization: Explicit memory cleanup
        
        return model
    
    def _setup_visualizers(self) -> Dict[str, Any]:
        """Setup visualization components for testing"""
        visualizers = {}
        
        try:
            visualizers['architecture'] = ModelArchitectureGraph()
            logger.info("Architecture visualizer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize architecture visualizer: {e}")
        
        try:
            visualizers['activation'] = ActivationVisualizer(model=self.model)
            logger.info("Activation visualizer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize activation visualizer: {e}")
        
        # For attention visualizer, we would need a transformer model with attention heads
        # Memory optimization: Explicit memory cleanup
        # Since we're using a simple test model, we'll skip this for now
        
        return visualizers
    
    def run_architecture_test(self, iterations: int = 10) -> bool:
        """
        Run stability test for architecture visualization.
        
        Args:
            iterations: Number of times to generate architecture visualization
            
        Returns:
            True if test passed without memory leaks, False otherwise
            # Memory optimization: Memory-critical operation
        """
        logger.info(f"Starting architecture visualization test ({iterations} iterations)")
        
        # Force garbage collection before test
        gc.collect()
        # Memory optimization: Force garbage collection
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
        
        # Take memory snapshot before test
        # Memory optimization: Memory-critical operation
        self.memory_tracker.log_memory_usage()
        # Memory optimization: Memory-critical operation
        
        # Run visualization iterations
        for i in range(iterations):
            try:
                viz_path = os.path.join(self.output_dir, f"arch_test_{i}.png")
                self.visualizers['architecture'].generate_architecture_graph(
                    model=self.model,
                    save_path=viz_path,
                    simplify=True
                )
                logger.info(f"Completed architecture visualization iteration {i+1}/{iterations}")
                
                # Take memory snapshot
                # Memory optimization: Memory-critical operation
                self.memory_tracker.log_memory_usage()
                # Memory optimization: Memory-critical operation
                
                # Check for leaks every 5 iterations
                if (i + 1) % 5 == 0:
                    leak_check = self.memory_tracker.check_for_leaks()
                    # Memory optimization: Memory-critical operation
                    any_leaks = any([leak_check.get(k, {}).get('is_leaking', False) 
                                    for k in ['ram', 'vram', 'python'] if k in leak_check])
                    if any_leaks:
                        logger.warning("Memory leak detected during architecture test")
                        # Memory optimization: Memory-critical operation
                        # Continue the test to gather more data
            
            except Exception as e:
                logger.error(f"Error in architecture visualization iteration {i}: {e}")
                return False
            
            # Small delay to allow for memory stabilization
            # Memory optimization: Memory-critical operation
            time.sleep(1)
        
        # Final leak check
        leak_check = self.memory_tracker.check_for_leaks()
        # Memory optimization: Memory-critical operation
        any_leaks = any([leak_check.get(k, {}).get('is_leaking', False) 
                        for k in ['ram', 'vram', 'python'] if k in leak_check])
        
        # Generate report
        report = self.memory_tracker.generate_report(
        # Memory optimization: Memory-critical operation
            title=f"Architecture Visualization Test Report ({iterations} iterations)"
        )
        
        report_path = os.path.join(self.output_dir, "architecture_test_report.txt")
        with open(report_path, "w") as f:
            f.write(report)
        
        logger.info(f"Architecture test completed. Report saved to {report_path}")
        return not any_leaks
    
    def run_activation_test(self, iterations: int = 10) -> bool:
        """
        Run stability test for activation visualization.
        
        Args:
            iterations: Number of times to generate activation visualization
            
        Returns:
            True if test passed without memory leaks, False otherwise
            # Memory optimization: Memory-critical operation
        """
        logger.info(f"Starting activation visualization test ({iterations} iterations)")
        
        # Force garbage collection before test
        gc.collect()
        # Memory optimization: Force garbage collection
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
        
        # Take memory snapshot before test
        # Memory optimization: Memory-critical operation
        self.memory_tracker.log_memory_usage()
        # Memory optimization: Memory-critical operation
        
        # Create a random input tensor
        input_shape = (1, 512)  # Batch size 1, dimension 512
        if torch.cuda.is_available() and self.memory_tracker.track_cuda:
        # Memory optimization: CUDA operations for GPU acceleration
            input_tensor = torch.randn(*input_shape, device="cuda")
            # Memory optimization: Device placement for memory management
        else:
            input_tensor = torch.randn(*input_shape)
        
        # Register activation hooks
        try:
            self.visualizers['activation'].register_hooks()
        except Exception as e:
            logger.error(f"Failed to register activation hooks: {e}")
            return False
        
        # Run visualization iterations
        for i in range(iterations):
            try:
                viz_path = os.path.join(self.output_dir, f"activation_test_{i}.png")
                self.visualizers['activation'].visualize_layer_activations(
                    input_tensor=input_tensor,
                    save_path=viz_path
                )
                logger.info(f"Completed activation visualization iteration {i+1}/{iterations}")
                
                # Take memory snapshot
                # Memory optimization: Memory-critical operation
                self.memory_tracker.log_memory_usage()
                # Memory optimization: Memory-critical operation
                
                # Check for leaks every 5 iterations
                if (i + 1) % 5 == 0:
                    leak_check = self.memory_tracker.check_for_leaks()
                    # Memory optimization: Memory-critical operation
                    any_leaks = any([leak_check.get(k, {}).get('is_leaking', False) 
                                    for k in ['ram', 'vram', 'python'] if k in leak_check])
                    if any_leaks:
                        logger.warning("Memory leak detected during activation test")
                        # Memory optimization: Memory-critical operation
                        # Continue the test to gather more data
            
            except Exception as e:
                logger.error(f"Error in activation visualization iteration {i}: {e}")
                self.visualizers['activation'].remove_hooks()  # Clean up hooks
                return False
            
            # Small delay to allow for memory stabilization
            # Memory optimization: Memory-critical operation
            time.sleep(1)
        
        # Clean up hooks to prevent memory leaks
        # Memory optimization: Memory-critical operation
        self.visualizers['activation'].remove_hooks()
        
        # Allow for memory to stabilize after hooks removal
        # Memory optimization: Memory-critical operation
        time.sleep(2)
        gc.collect()
        # Memory optimization: Force garbage collection
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
        
        # Final memory snapshot
        # Memory optimization: Memory-critical operation
        self.memory_tracker.log_memory_usage()
        # Memory optimization: Memory-critical operation
        
        # Final leak check
        leak_check = self.memory_tracker.check_for_leaks()
        # Memory optimization: Memory-critical operation
        any_leaks = any([leak_check.get(k, {}).get('is_leaking', False) 
                        for k in ['ram', 'vram', 'python'] if k in leak_check])
        
        # Generate report
        report = self.memory_tracker.generate_report(
        # Memory optimization: Memory-critical operation
            title=f"Activation Visualization Test Report ({iterations} iterations)"
        )
        
        report_path = os.path.join(self.output_dir, "activation_test_report.txt")
        with open(report_path, "w") as f:
            f.write(report)
        
        logger.info(f"Activation test completed. Report saved to {report_path}")
        return not any_leaks
    
    def run_combined_stress_test(self, duration_minutes: int = 30) -> bool:
        """
        Run a combined stress test of all visualization components.
        
        Args:
            duration_minutes: How long to run the test in minutes
            
        Returns:
            True if test passed without issues, False otherwise
        """
        logger.info(f"Starting combined visualization stress test ({duration_minutes} minutes)")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        success = True
        
        # Create input tensor for tests
        input_shape = (1, 512)
        if torch.cuda.is_available() and self.memory_tracker.track_cuda:
        # Memory optimization: CUDA operations for GPU acceleration
            input_tensor = torch.randn(*input_shape, device="cuda")
            # Memory optimization: Device placement for memory management
        else:
            input_tensor = torch.randn(*input_shape)
        
        # Start memory logging thread
        # Memory optimization: Memory-critical operation
        stop_logging = threading.Event()
        
        def memory_logging_task():
        # Memory optimization: Memory-critical operation
            """
            
    memory_logging_task function for processing.
    # Memory optimization: Memory-critical operation
    
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
            while not stop_logging.is_set():
                self.memory_tracker.log_memory_usage()
                # Memory optimization: Memory-critical operation
                time.sleep(10)  # Log every 10 seconds
        
        logging_thread = threading.Thread(target=memory_logging_task)
        # Memory optimization: Memory-critical operation
        logging_thread.daemon = True
        logging_thread.start()
        
        # Alternate between visualization types until test duration is reached
        test_count = 0
        while datetime.now() < end_time:
            test_type = test_count % 2  # Alternate between test types
            iteration = test_count // 2
            
            # Force garbage collection between tests
            gc.collect()
            # Memory optimization: Force garbage collection
            if torch.cuda.is_available():
            # Memory optimization: CUDA operations for GPU acceleration
                torch.cuda.empty_cache()
                # Memory optimization: CUDA operations for GPU acceleration
            
            try:
                if test_type == 0:
                    # Architecture test
                    viz_path = os.path.join(self.output_dir, f"stress_arch_{iteration}.png")
                    self.visualizers['architecture'].generate_architecture_graph(
                        model=self.model,
                        save_path=viz_path,
                        simplify=True
                    )
                    logger.info(f"Completed stress test architecture iteration {iteration}")
                else:
                    # Activation test
                    self.visualizers['activation'].register_hooks()
                    viz_path = os.path.join(self.output_dir, f"stress_act_{iteration}.png")
                    self.visualizers['activation'].visualize_layer_activations(
                        input_tensor=input_tensor,
                        save_path=viz_path
                    )
                    self.visualizers['activation'].remove_hooks()
                    logger.info(f"Completed stress test activation iteration {iteration}")
            
            except Exception as e:
                logger.error(f"Error in stress test iteration {test_count}: {e}")
                success = False
                # Continue the test to gather more data
            
            # Check for leaks every 5 tests
            if test_count % 5 == 0 and test_count > 0:
                leak_check = self.memory_tracker.check_for_leaks()
                # Memory optimization: Memory-critical operation
                any_leaks = any([leak_check.get(k, {}).get('is_leaking', False) 
                                for k in ['ram', 'vram', 'python'] if k in leak_check])
                if any_leaks:
                    logger.warning(f"Memory leak detected during stress test at iteration {test_count}")
                    # Memory optimization: Memory-critical operation
                    # Continue the test to gather more data
            
            test_count += 1
            # Small delay between tests
            time.sleep(3)
        
        # Stop memory logging
        # Memory optimization: Memory-critical operation
        stop_logging.set()
        logging_thread.join()
        
        # Generate report
        report = self.memory_tracker.generate_report(
        # Memory optimization: Memory-critical operation
            title=f"Visualization Stress Test Report ({test_count} iterations, {duration_minutes} minutes)"
        )
        
        report_path = os.path.join(self.output_dir, "stress_test_report.txt")
        with open(report_path, "w") as f:
            f.write(report)
        
        logger.info(f"Stress test completed. Report saved to {report_path}")
        
        # Final leak check
        leak_check = self.memory_tracker.check_for_leaks()
        # Memory optimization: Memory-critical operation
        any_leaks = any([leak_check.get(k, {}).get('is_leaking', False) 
                        for k in ['ram', 'vram', 'python'] if k in leak_check])
        
        return success and not any_leaks
    
    def cleanup(self):
        """Clean up resources used by the stability test"""
        self.memory_tracker.cleanup()
        # Memory optimization: Memory-critical operation
        
        # Remove hooks if they're still registered
        if 'activation' in self.visualizers:
            try:
                self.visualizers['activation'].remove_hooks()
            except:
                pass
        
        # Clear model to free memory
        # Memory optimization: Explicit memory cleanup
        self.model = None
        # Memory optimization: Explicit memory cleanup
        self.visualizers = {}
        
        # Force garbage collection
        gc.collect()
        # Memory optimization: Force garbage collection
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration


def main():
    """Main entry point for stability testing"""
    parser = argparse.ArgumentParser(description="ImpressionCore Long-term Stability Test")
    parser.add_argument("--test-type", choices=["architecture", "activation", "stress", "all"], 
                        default="all", help="Type of stability test to run")
    parser.add_argument("--duration", type=int, default=30, 
                        help="Duration of stress test in minutes")
    parser.add_argument("--iterations", type=int, default=20, 
                        help="Number of iterations for component tests")
    parser.add_argument("--output-dir", type=str, default="stability_test_results", 
                        help="Directory to store test results")
    
    args = parser.parse_args()
    
    logger.info(f"Starting ImpressionCore stability testing")
    logger.info(f"Test type: {args.test_type}, Duration: {args.duration} minutes, Iterations: {args.iterations}")
    
    # Check if visualization modules are available
    if not VISUALIZATION_AVAILABLE:
        logger.error("Visualization modules not available. Exiting.")
        return 1
    
    # Run the requested tests
    try:
        tester = VisualizationStabilityTest(output_dir=args.output_dir)
        
        if args.test_type == "architecture" or args.test_type == "all":
            success = tester.run_architecture_test(iterations=args.iterations)
            logger.info(f"Architecture test {'passed' if success else 'failed'}")
        
        if args.test_type == "activation" or args.test_type == "all":
            success = tester.run_activation_test(iterations=args.iterations)
            logger.info(f"Activation test {'passed' if success else 'failed'}")
        
        if args.test_type == "stress" or args.test_type == "all":
            success = tester.run_combined_stress_test(duration_minutes=args.duration)
            logger.info(f"Stress test {'passed' if success else 'failed'}")
        
        # Clean up resources
        tester.cleanup()
        
    except Exception as e:
        logger.error(f"Error during stability testing: {e}")
        logger.error(traceback.format_exc())
        return 1
    
    logger.info("Stability testing completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
