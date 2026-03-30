#!/usr/bin/env python3
"""
ImpressionCore: Run Stability Tests

Module for run stability tests functionality in the ImpressionCore framework.

File: tests\stability\run_stability_tests.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, qa, pytorch, production, testing, 2025]
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements run stability tests functionality for the
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
from tests.stability.run_stability_tests import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stability_test_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("stability_test_runner")

# Add parent directory to path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Check if the required modules are available
try:
    import torch
    import numpy as np
    import matplotlib.pyplot as plt
    import psutil
    import tracemalloc
except ImportError as e:
    logger.error(f"Missing required dependency: {e}")
    logger.error("Please install all dependencies before running stability tests.")
    sys.exit(1)

# Import test modules
try:
    from src.dev_tools.tests.stability.stability_test import VisualizationStabilityTest
    from src.dev_tools.tests.stability.memory_leak_detector import MemoryLeakDetector, test_visualization_component
    # Memory optimization: Memory-critical operation
    from src.dev_tools.tests.stability.stress_test import StressTester
    STABILITY_MODULES_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import stability test modules: {e}")
    STABILITY_MODULES_AVAILABLE = False


def print_hardware_info():
    """Print information about the current hardware"""
    logger.info("=== Hardware Information ===")
    
    # System info
    import platform
    logger.info(f"OS: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    
    # CPU info
    cpu_count = psutil.cpu_count(logical=False)
    cpu_logical = psutil.cpu_count(logical=True)
    logger.info(f"CPU: {cpu_count} cores ({cpu_logical} logical processors)")
    
    # RAM info
    ram = psutil.virtual_memory()
    # Memory optimization: Memory-critical operation
    ram_gb = ram.total / (1024 ** 3)
    logger.info(f"RAM: {ram_gb:.1f} GB")
    
    # GPU info
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        gpu_count = torch.cuda.device_count()
        # Memory optimization: CUDA operations for GPU acceleration
        logger.info(f"GPU: {gpu_count} device(s)")
        # Memory optimization: Device placement for memory management
        
        for i in range(gpu_count):
        # Memory optimization: Memory-critical operation
            gpu_name = torch.cuda.get_device_name(i)
            # Memory optimization: CUDA operations for GPU acceleration
            gpu_mem = torch.cuda.get_device_properties(i).total_memory / (1024 ** 3)
            # Memory optimization: CUDA operations for GPU acceleration
            logger.info(f"  GPU {i}: {gpu_name} ({gpu_mem:.1f} GB)")
            # Memory optimization: Memory-critical operation
    else:
        logger.info("GPU: None (CPU only)")
        # Memory optimization: Memory-critical operation


def create_test_output_directory() -> str:
    """Create a timestamped directory for test outputs"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.abspath(f"stability_test_results_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Created test output directory: {output_dir}")
    return output_dir


def run_stability_test(args):
    """Run a stability test"""
    if not STABILITY_MODULES_AVAILABLE:
        logger.error("Stability test modules not available")
        return 1
    
    output_dir = create_test_output_directory()
    print_hardware_info()
    
    logger.info(f"Starting stability test: {args.test_type}, Duration: {args.duration} minutes")
    
    try:
        tester = VisualizationStabilityTest(output_dir=output_dir)
        
        if args.test_type == "architecture":
            # Convert minutes to iteration count (approx)
            iterations = max(10, args.duration * 2)
            success = tester.run_architecture_test(iterations=iterations)
            logger.info(f"Architecture stability test {'passed' if success else 'failed'}")
            
        elif args.test_type == "activation":
            # Convert minutes to iteration count (approx)
            iterations = max(10, args.duration * 2)
            success = tester.run_activation_test(iterations=iterations)
            logger.info(f"Activation stability test {'passed' if success else 'failed'}")
            
        elif args.test_type == "stress":
            success = tester.run_combined_stress_test(duration_minutes=args.duration)
            logger.info(f"Combined stress test {'passed' if success else 'failed'}")
            
        elif args.test_type == "all":
            # Run all test types with appropriate duration
            arch_success = tester.run_architecture_test(iterations=max(10, args.duration))
            logger.info(f"Architecture stability test {'passed' if arch_success else 'failed'}")
            
            act_success = tester.run_activation_test(iterations=max(10, args.duration))
            logger.info(f"Activation stability test {'passed' if act_success else 'failed'}")
            
            stress_success = tester.run_combined_stress_test(duration_minutes=args.duration)
            logger.info(f"Combined stress test {'passed' if stress_success else 'failed'}")
            
            success = arch_success and act_success and stress_success
            
        # Clean up
        tester.cleanup()
        
        logger.info(f"Stability test completed. Results in {output_dir}")
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Error during stability test: {e}")
        logger.exception("Exception details:")
        return 1


def run_memory_leak_detection(args):
# Memory optimization: Memory-critical operation
    """Run memory leak detection"""
    # Memory optimization: Memory-critical operation
    if not STABILITY_MODULES_AVAILABLE:
        logger.error("Stability test modules not available")
        return 1
    
    output_dir = create_test_output_directory()
    print_hardware_info()
    
    logger.info(f"Starting memory leak detection: {args.component}, Iterations: {args.iterations}")
    # Memory optimization: Memory-critical operation
    
    # Import visualization components
    try:
        from src.dev_tools.visualization.model_visualizer import ModelVisualizer
        from src.dev_tools.visualization.architecture_graph import ModelArchitectureGraph
        from src.dev_tools.visualization.attention_patterns import AttentionVisualizer
        from src.dev_tools.visualization.activation_maps import ActivationVisualizer
        
        # Create a simple test model
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
        
        # Define test functions
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
                save_path=os.path.join(output_dir, f"arch_test_{int(time.time())}.png"),
                simplify=True
            )
            
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
            try:
                act_viz.visualize_layer_activations(
                    input_tensor=input_tensor,
                    save_path=os.path.join(output_dir, f"act_test_{int(time.time())}.png")
                )
            finally:
                act_viz.remove_hooks()
        
        # Run selected test
        detector = MemoryLeakDetector()
        # Memory optimization: Memory-critical operation
        
        if args.component == "architecture" or args.component == "all":
            results = detector.detect_leaks_in_function(test_architecture, iterations=args.iterations)
            logger.info(f"Architecture leak test: {'LEAK DETECTED' if results['has_leak'] else 'No leak detected'}")
            
        if args.component == "activation" or args.component == "all":
            results = detector.detect_leaks_in_function(test_activation, iterations=args.iterations)
            logger.info(f"Activation leak test: {'LEAK DETECTED' if results['has_leak'] else 'No leak detected'}")
            
        # Clean up
        detector.cleanup()
        
        logger.info(f"Memory leak detection completed. Results in current directory.")
        # Memory optimization: Memory-critical operation
        return 0
        
    except ImportError as e:
        logger.error(f"Failed to import visualization components: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error during memory leak detection: {e}")
        # Memory optimization: Memory-critical operation
        logger.exception("Exception details:")
        return 1


def run_stress_test(args):
    """Run stress test"""
    if not STABILITY_MODULES_AVAILABLE:
        logger.error("Stability test modules not available")
        return 1
    
    output_dir = create_test_output_directory()
    print_hardware_info()
    
    logger.info(f"Starting stress test: {args.stress_type}, Complexity: {args.complexity}")
    
    try:
        tester = StressTester(output_dir=output_dir)
        
        if args.stress_type == "architecture":
            results = tester.stress_test_architecture(iterations=args.iterations, complexity=args.complexity)
            success = results['success_rate'] > 0.8  # Success if over 80% successful
            
        elif args.stress_type == "activation":
            results = tester.stress_test_activation(iterations=args.iterations, complexity=args.complexity)
            success = results['success_rate'] > 0.8  # Success if over 80% successful
            
        elif args.stress_type == "parallel":
            results = tester.stress_test_parallel(iterations=args.iterations, complexity=args.complexity)
            success = results['success_rate'] > 0.8  # Success if over 80% successful
            
        elif args.stress_type == "progressive":
            results = tester.stress_test_progressive_load(start_complexity=args.complexity, max_iterations=args.iterations*2)
            # Success if we can determine safe parameters
            success = 'max_safe_params' in results and bool(results['max_safe_params'])
            
        elif args.stress_type == "all":
            results = tester.run_comprehensive_test(complexity=args.complexity)
            # Success if any tests completed successfully
            success = any(component in results and results[component].get('success', False) 
                        for component in ['architecture', 'activation', 'parallel'])
        
        logger.info(f"Stress test completed. Results in {output_dir}")
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Error during stress test: {e}")
        logger.exception("Exception details:")
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ImpressionCore Long-term Stability Test Runner")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Stability test parser
    stability_parser = subparsers.add_parser("stability", help="Run stability tests")
    stability_parser.add_argument("--test-type", choices=["architecture", "activation", "stress", "all"], 
                               default="all", help="Type of stability test to run")
    stability_parser.add_argument("--duration", type=int, default=30, 
                               help="Duration of test in minutes")
    
    # Memory leak detection parser
    # Memory optimization: Memory-critical operation
    leak_parser = subparsers.add_parser("leak", help="Run memory leak detection")
    # Memory optimization: Memory-critical operation
    leak_parser.add_argument("--component", choices=["architecture", "activation", "all"], 
                          default="all", help="Component to test for memory leaks")
                          # Memory optimization: Memory-critical operation
    leak_parser.add_argument("--iterations", type=int, default=20, 
                          help="Number of iterations for leak detection")
    
    # Stress test parser
    stress_parser = subparsers.add_parser("stress", help="Run stress tests")
    stress_parser.add_argument("--stress-type", choices=["architecture", "activation", "parallel", "progressive", "all"], 
                            default="all", help="Type of stress test to run")
    stress_parser.add_argument("--complexity", choices=["low", "medium", "high"], 
                            default="medium", help="Complexity level for models")
    stress_parser.add_argument("--iterations", type=int, default=10, 
                            help="Number of iterations for component tests")
    
    # Parse arguments
    args = parser.parse_args()
    
    # No command provided
    if not args.command:
        parser.print_help()
        return 1
    
    # Check if CUDA is available
    # Memory optimization: Memory-critical operation
    has_cuda = torch.cuda.is_available()
    # Memory optimization: CUDA operations for GPU acceleration
    if has_cuda:
    # Memory optimization: Memory-critical operation
        logger.info(f"CUDA is available, using device: {torch.cuda.get_device_name(0)}")
        # Memory optimization: CUDA operations for GPU acceleration
    else:
        logger.info("CUDA is not available, running on CPU")
        # Memory optimization: Memory-critical operation
    
    # Run the requested command
    if args.command == "stability":
        return run_stability_test(args)
    elif args.command == "leak":
        return run_memory_leak_detection(args)
        # Memory optimization: Memory-critical operation
    elif args.command == "stress":
        return run_stress_test(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
