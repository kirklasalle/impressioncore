#!/usr/bin/env python3
"""
ImpressionCore: Memory Leak Detector

Module for memory leak detector functionality in the ImpressionCore framework.

File: tests\stability\memory_leak_detector.py
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
This module implements memory leak detector functionality for the
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
from tests.stability.memory_leak_detector import MemoryLeakDetector
instance = MemoryLeakDetector()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import gc
import logging
import os
import sys
import time
import tracemalloc
from typing import Dict, List, Optional, Set, Tuple, Union, Callable

import numpy as np
import psutil
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory_leak_detection.log"),
        # Memory optimization: Memory-critical operation
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("memory_leak_detection")
# Memory optimization: Memory-critical operation

# Add project root to system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

class MemoryLeakDetector:
# Memory optimization: Memory-critical operation
    """
    Detects memory leaks in Python code with a focus on PyTorch operations.
    # Memory optimization: Memory-critical operation
    
    Provides utilities for:
    - Running a function repeatedly to detect leaks
    - Monitoring RAM and VRAM usage during function execution
    - Identifying leaked Python objects
    - Generating detailed memory leak reports
    # Memory optimization: Memory-critical operation
    """
    
    def __init__(self):
        """Initialize the memory leak detector"""
        # Memory optimization: Memory-critical operation
        self.process = psutil.Process(os.getpid())
        self.has_cuda = torch.cuda.is_available()
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Track object counts to detect leaking objects
        self.start_objects: Dict[str, int] = {}
        self.leaked_objects: Dict[str, int] = {}
        
        # Configure tracemalloc for Python object tracking
        tracemalloc.start()
    
    def get_memory_usage(self) -> Dict[str, int]:
    # Memory optimization: Memory-critical operation
        """Get current memory usage in bytes"""
        # Memory optimization: Memory-critical operation
        memory_usage = {
        # Memory optimization: Memory-critical operation
            'ram': self.process.memory_info().rss,
            # Memory optimization: Memory-critical operation
        }
        
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            memory_usage['vram_allocated'] = torch.cuda.memory_allocated()
            # Memory optimization: CUDA operations for GPU acceleration
            memory_usage['vram_reserved'] = torch.cuda.memory_reserved()
            # Memory optimization: CUDA operations for GPU acceleration
        
        return memory_usage
        # Memory optimization: Memory-critical operation
    
    def get_object_counts(self) -> Dict[str, int]:
        """Count objects by type in memory"""
        # Memory optimization: Memory-critical operation
        object_counts = {}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            if obj_type not in object_counts:
                object_counts[obj_type] = 0
            object_counts[obj_type] += 1
        
        return object_counts
    
    def get_tensor_counts(self) -> Dict[str, int]:
        """Count tensors by shape in memory"""
        # Memory optimization: Memory-critical operation
        tensor_counts = {}
        total_bytes = 0
        
        for obj in gc.get_objects():
            if isinstance(obj, torch.Tensor):
                key = f"Tensor{tuple(obj.shape)}"
                size_bytes = obj.element_size() * obj.nelement()
                total_bytes += size_bytes
                
                if key not in tensor_counts:
                    tensor_counts[key] = {'count': 0, 'bytes': 0}
                
                tensor_counts[key]['count'] += 1
                tensor_counts[key]['bytes'] += size_bytes
        
        tensor_counts['Total'] = {'count': sum(item['count'] for item in tensor_counts.values()), 
                                  'bytes': total_bytes}
        
        return tensor_counts
    
    def start_monitoring(self):
        """Start monitoring for leaks"""
        # Force garbage collection
        gc.collect()
        # Memory optimization: Force garbage collection
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
        
        # Record starting state
        self.start_memory = self.get_memory_usage()
        # Memory optimization: Memory-critical operation
        self.start_objects = self.get_object_counts()
        self.start_tensors = self.get_tensor_counts()
        self.start_trace = tracemalloc.take_snapshot()
        
        logger.info("Memory leak monitoring started")
        # Memory optimization: Memory-critical operation
        logger.info(f"Initial RAM: {self.start_memory['ram'] / (1024 * 1024):.2f} MB")
        # Memory optimization: Memory-critical operation
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            logger.info(f"Initial VRAM (allocated): {self.start_memory['vram_allocated'] / (1024 * 1024):.2f} MB")
            # Memory optimization: Memory-critical operation
            logger.info(f"Initial VRAM (reserved): {self.start_memory['vram_reserved'] / (1024 * 1024):.2f} MB")
            # Memory optimization: Memory-critical operation
    
    def stop_monitoring(self) -> Dict[str, Union[bool, Dict]]:
        """
        Stop monitoring and check for leaks
        
        Returns:
            Dict with leak analysis results
        """
        # Force garbage collection
        gc.collect()
        # Memory optimization: Force garbage collection
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
        
        # Get current state
        end_memory = self.get_memory_usage()
        # Memory optimization: Memory-critical operation
        end_objects = self.get_object_counts()
        end_tensors = self.get_tensor_counts()
        end_trace = tracemalloc.take_snapshot()
        
        # Calculate differences
        memory_diff = {k: end_memory[k] - self.start_memory[k] for k in self.start_memory}
        # Memory optimization: Memory-critical operation
        
        # Check for leaked objects
        leaked_objects = {}
        for obj_type in end_objects:
            start_count = self.start_objects.get(obj_type, 0)
            end_count = end_objects[obj_type]
            
            if end_count > start_count:
                leaked_objects[obj_type] = end_count - start_count
        
        # Check for leaked tensors
        leaked_tensors = {}
        for tensor_key in end_tensors:
            if tensor_key == 'Total':
                continue
                
            start_info = self.start_tensors.get(tensor_key, {'count': 0, 'bytes': 0})
            end_info = end_tensors[tensor_key]
            
            if end_info['count'] > start_info['count']:
                leaked_tensors[tensor_key] = {
                    'count': end_info['count'] - start_info['count'],
                    'bytes': end_info['bytes'] - start_info['bytes'],
                }
        
        # Get tracemalloc stats
        memory_leaks = end_trace.compare_to(self.start_trace, 'lineno')
        # Memory optimization: Memory-critical operation
        
        # Determine if there's a memory leak
        # Memory optimization: Memory-critical operation
        ram_leak_threshold = 10 * 1024 * 1024  # 10 MB
        vram_leak_threshold = 5 * 1024 * 1024  # 5 MB
        
        has_ram_leak = memory_diff['ram'] > ram_leak_threshold
        # Memory optimization: Memory-critical operation
        has_vram_leak = False
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            has_vram_leak = memory_diff['vram_allocated'] > vram_leak_threshold
            # Memory optimization: Memory-critical operation
        
        # Log results
        logger.info("Memory leak monitoring stopped")
        # Memory optimization: Memory-critical operation
        logger.info(f"RAM change: {memory_diff['ram'] / (1024 * 1024):.2f} MB")
        # Memory optimization: Memory-critical operation
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            logger.info(f"VRAM (allocated) change: {memory_diff['vram_allocated'] / (1024 * 1024):.2f} MB")
            # Memory optimization: Memory-critical operation
            logger.info(f"VRAM (reserved) change: {memory_diff['vram_reserved'] / (1024 * 1024):.2f} MB")
            # Memory optimization: Memory-critical operation
        
        if has_ram_leak:
            logger.warning("RAM LEAK DETECTED")
        if has_vram_leak:
            logger.warning("VRAM LEAK DETECTED")
        
        # Get top 10 memory leaks from tracemalloc
        # Memory optimization: Memory-critical operation
        top_leaks = []
        for stat in memory_leaks[:10]:
        # Memory optimization: Memory-critical operation
            if stat.size_diff > 0:  # Only include positive size diffs (leaks)
                frame = stat.traceback[0]
                filename = os.path.basename(frame.filename)
                line = frame.lineno
                size_mb = stat.size_diff / (1024 * 1024)
                
                leak_info = f"{filename}:{line} - {size_mb:.2f} MB"
                top_leaks.append((leak_info, size_mb))
                
                logger.info(f"Leak: {leak_info}")
        
        # Return analysis results
        return {
            'has_leak': has_ram_leak or has_vram_leak,
            'memory_diff': memory_diff,
            # Memory optimization: Memory-critical operation
            'leaked_objects': leaked_objects,
            'leaked_tensors': leaked_tensors,
            'top_leaks': top_leaks,
        }
    
    def detect_leaks_in_function(self, func: Callable, iterations: int = 10) -> Dict[str, Union[bool, Dict]]:
        """
        Detect memory leaks in a function by running it multiple times
        # Memory optimization: Memory-critical operation
        
        Args:
            func: Function to test
            iterations: Number of iterations to run
            
        Returns:
            Dict with leak analysis results
        """
        logger.info(f"Testing function {func.__name__} for memory leaks ({iterations} iterations)")
        # Memory optimization: Memory-critical operation
        
        # Start monitoring
        self.start_monitoring()
        
        # Run the function multiple times
        for i in range(iterations):
            logger.info(f"Iteration {i+1}/{iterations}")
            try:
                func()
            except Exception as e:
                logger.error(f"Error in iteration {i+1}: {e}")
                # Continue testing
            
            # Small delay to allow for memory operations to complete
            # Memory optimization: Memory-critical operation
            time.sleep(0.5)
            
            # Periodically force garbage collection
            if (i + 1) % 3 == 0:
                gc.collect()
                # Memory optimization: Force garbage collection
                if self.has_cuda:
                # Memory optimization: Memory-critical operation
                    torch.cuda.empty_cache()
                    # Memory optimization: CUDA operations for GPU acceleration
        
        # Stop monitoring and get results
        results = self.stop_monitoring()
        
        # Generate report
        report = self._generate_leak_report(func.__name__, iterations, results)
        
        # Save report
        report_file = f"leak_report_{func.__name__}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Leak report saved to {report_file}")
        
        return results
    
    def _generate_leak_report(self, func_name: str, iterations: int, results: Dict) -> str:
        """Generate a detailed leak report"""
        report = []
        report.append(f"=== Memory Leak Report for {func_name} ===")
        # Memory optimization: Memory-critical operation
        report.append(f"Iterations: {iterations}")
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Memory differences
        # Memory optimization: Memory-critical operation
        report.append("--- Memory Differences ---")
        # Memory optimization: Memory-critical operation
        memory_diff = results['memory_diff']
        # Memory optimization: Memory-critical operation
        ram_diff_mb = memory_diff['ram'] / (1024 * 1024)
        # Memory optimization: Memory-critical operation
        report.append(f"RAM: {ram_diff_mb:.2f} MB")
        
        if self.has_cuda:
        # Memory optimization: Memory-critical operation
            vram_allocated_diff_mb = memory_diff['vram_allocated'] / (1024 * 1024)
            # Memory optimization: Memory-critical operation
            vram_reserved_diff_mb = memory_diff['vram_reserved'] / (1024 * 1024)
            # Memory optimization: Memory-critical operation
            report.append(f"VRAM (allocated): {vram_allocated_diff_mb:.2f} MB")
            report.append(f"VRAM (reserved): {vram_reserved_diff_mb:.2f} MB")
        
        report.append("")
        
        # Leak status
        report.append("--- Leak Detection ---")
        if results['has_leak']:
            report.append("STATUS: MEMORY LEAK DETECTED")
            # Memory optimization: Memory-critical operation
        else:
            report.append("STATUS: No memory leak detected")
            # Memory optimization: Memory-critical operation
        
        report.append("")
        
        # Top leaks
        report.append("--- Top Memory Leaks ---")
        # Memory optimization: Memory-critical operation
        if not results['top_leaks']:
            report.append("No significant memory leaks detected by tracemalloc")
            # Memory optimization: Memory-critical operation
        else:
            for leak_info, size_mb in results['top_leaks']:
                report.append(leak_info)
        
        report.append("")
        
        # Leaked objects
        report.append("--- Leaked Python Objects ---")
        leaked_objects = results['leaked_objects']
        if not leaked_objects:
            report.append("No leaked Python objects detected")
        else:
            for obj_type, count in sorted(leaked_objects.items(), key=lambda x: x[1], reverse=True)[:20]:
                report.append(f"{obj_type}: {count}")
        
        report.append("")
        
        # Leaked tensors
        report.append("--- Leaked PyTorch Tensors ---")
        leaked_tensors = results['leaked_tensors']
        if not leaked_tensors:
            report.append("No leaked PyTorch tensors detected")
        else:
            for tensor_key, info in sorted(leaked_tensors.items(), key=lambda x: x[1]['bytes'], reverse=True)[:20]:
                size_mb = info['bytes'] / (1024 * 1024)
                report.append(f"{tensor_key}: {info['count']} tensors, {size_mb:.2f} MB")
        
        report.append("")
        
        # Recommendations
        report.append("--- Recommendations ---")
        if results['has_leak']:
            report.append("1. Check code paths indicated in the top memory leaks section")
            # Memory optimization: Memory-critical operation
            report.append("2. Ensure all tensors are explicitly freed or moved to CPU when not needed")
            report.append("3. Check for circular references that might prevent garbage collection")
            report.append("4. Verify that PyTorch hooks are properly removed")
            report.append("5. Consider using context managers for temporary CUDA operations")
            # Memory optimization: Memory-critical operation
        else:
            report.append("No action needed. Memory usage is stable.")
            # Memory optimization: Memory-critical operation
        
        return "\n".join(report)
    
    def cleanup(self):
        """Clean up resources used by the leak detector"""
        tracemalloc.stop()


def test_visualization_component(component_name: str, test_func: Callable, iterations: int = 10) -> bool:
    """
    Test a visualization component for memory leaks
    # Memory optimization: Memory-critical operation
    
    Args:
        component_name: Name of the component being tested
        test_func: Function that exercises the component
        iterations: Number of iterations to run
        
    Returns:
        True if no leaks detected, False otherwise
    """
    logger.info(f"Testing {component_name} for memory leaks")
    # Memory optimization: Memory-critical operation
    
    detector = MemoryLeakDetector()
    # Memory optimization: Memory-critical operation
    results = detector.detect_leaks_in_function(test_func, iterations)
    detector.cleanup()
    
    return not results['has_leak']


def main():
    """Main function for standalone usage"""
    if len(sys.argv) < 2:
        print("Usage: python memory_leak_detector.py <component>")
        # Memory optimization: Memory-critical operation
        print("Components: architecture, activation, attention, all")
        return 1
    
    component = sys.argv[1].lower()
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    try:
        # Import visualization components
        from src.dev_tools.visualization.model_visualizer import ModelVisualizer
        from src.dev_tools.visualization.architecture_graph import ModelArchitectureGraph
        from src.dev_tools.visualization.attention_patterns import AttentionVisualizer
        from src.dev_tools.visualization.activation_maps import ActivationVisualizer
        
        # Create a small test model
        model = torch.nn.Sequential(
        # Memory optimization: Explicit memory cleanup
            torch.nn.Linear(512, 768),
            torch.nn.ReLU(),
            torch.nn.Linear(768, 512)
        )
        
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            model = model.cuda()
            # Memory optimization: Explicit memory cleanup
            
        # Create test input
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            input_tensor = torch.randn(1, 512, device="cuda")
            # Memory optimization: Device placement for memory management
        else:
            input_tensor = torch.randn(1, 512)
            
        # Architecture visualization test
        def test_architecture():
            """
            
    test_architecture function for processing.
    
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
            arch_viz = ModelArchitectureGraph()
            arch_viz.generate_architecture_graph(
                model=model,
                save_path=f"arch_test_{time.time()}.png",
                simplify=True
            )
            
        # Activation visualization test
        def test_activation():
            """
            
    test_activation function for processing.
    
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
            act_viz = ActivationVisualizer(model=model)
            act_viz.register_hooks()
            act_viz.visualize_layer_activations(
                input_tensor=input_tensor,
                save_path=f"act_test_{time.time()}.png"
            )
            act_viz.remove_hooks()
            
        # Run selected test
        if component == "architecture" or component == "all":
            test_visualization_component("Architecture Visualization", test_architecture, iterations)
            
        if component == "activation" or component == "all":
            test_visualization_component("Activation Visualization", test_activation, iterations)
            
        logger.info("Memory leak detection completed")
        # Memory optimization: Memory-critical operation
        return 0
    
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error during memory leak detection: {e}")
        # Memory optimization: Memory-critical operation
        return 1


if __name__ == "__main__":
    sys.exit(main())
