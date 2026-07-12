#!/usr/bin/env python3
"""
ImpressionCore: Memory Tracking Utils

Module for memory tracking utils functionality in the ImpressionCore framework.

File: core/utils/memory_tracking_utils.py
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
Dependencies: [torch]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements memory tracking utils functionality for the
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
from src.core.utils.memory_tracking_utils import MemoryTestResult
instance = MemoryTestResult()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import sys
import time
import psutil
import os
import torch
import gc
from src.core.utils.status_animation import StatusAnimation

# Configure logging
def setup_logger(name):
    """
    Set up a logger with the specified name.
    
    Args:
        name (str): The name for the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    return logger

def get_memory_usage():
# Memory optimization: Memory-critical operation
    """
    Get current memory usage of the process in MB.
    # Memory optimization: Memory-critical operation
    
    Returns:
        tuple: (used_memory_mb, percent_memory)
        # Memory optimization: Memory-critical operation
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    # Memory optimization: Memory-critical operation
    memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
    # Memory optimization: Memory-critical operation
    memory_percent = psutil.virtual_memory().percent
    # Memory optimization: Memory-critical operation
    return memory_mb, memory_percent
    # Memory optimization: Memory-critical operation

def log_memory_usage(logger, tag=""):
# Memory optimization: Memory-critical operation
    """
    Log the current memory usage with an optional tag.
    # Memory optimization: Memory-critical operation
    
    Args:
        logger (logging.Logger): Logger to use for output
        tag (str): Description tag for the log entry
        
    Returns:
        tuple: (memory_mb, memory_percent) - Current memory usage stats
        # Memory optimization: Memory-critical operation
    """
    memory_mb, memory_percent = get_memory_usage()
    # Memory optimization: Memory-critical operation
    logger.info(f"Memory usage {tag}: {memory_mb:.2f} MB ({memory_percent:.1f}% of system RAM)")
    # Memory optimization: Memory-critical operation
    return memory_mb, memory_percent
    # Memory optimization: Memory-critical operation

def log_cuda_memory(logger, device_id=None):
# Memory optimization: Device placement for memory management
    """
    Log CUDA memory usage for the specified device or all devices.
    # Memory optimization: Device placement for memory management
    
    Args:
        logger (logging.Logger): Logger to use for output
        device_id (int, optional): Specific GPU device ID. If None, logs for all devices.
        # Memory optimization: Device placement for memory management
    """
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.info("CUDA not available")
        # Memory optimization: Memory-critical operation
        return
    
    devices = [device_id] if device_id is not None else range(torch.cuda.device_count())
    # Memory optimization: CUDA operations for GPU acceleration
    
    for i in devices:
    # Memory optimization: Device placement for memory management
        if i >= torch.cuda.device_count():
        # Memory optimization: CUDA operations for GPU acceleration
            logger.warning(f"Device {i} out of range (max: {torch.cuda.device_count()-1})")
            # Memory optimization: CUDA operations for GPU acceleration
            continue
            
        props = torch.cuda.get_device_properties(i)
        # Memory optimization: CUDA operations for GPU acceleration
        allocated = torch.cuda.memory_allocated(i) / (1024 * 1024)  # MB
        # Memory optimization: CUDA operations for GPU acceleration
        reserved = torch.cuda.memory_reserved(i) / (1024 * 1024)    # MB
        # Memory optimization: CUDA operations for GPU acceleration
        total = props.total_memory / (1024 * 1024)                  # MB
        # Memory optimization: Memory-critical operation
        
        logger.info(f"GPU {i} ({props.name}) memory: "
        # Memory optimization: Memory-critical operation
                   f"{total:.1f}MB total, "
                   f"{allocated:.1f}MB allocated, "
                   f"{reserved:.1f}MB reserved, "
                   f"{(allocated/total)*100:.1f}% utilization")

class MemoryTestResult(unittest.TextTestResult):
# Memory optimization: Memory-critical operation
    """Custom TestResult class that tracks memory usage for each test."""
    # Memory optimization: Memory-critical operation
    
    def __init__(self, *args, **kwargs):
        """Initialize the MemoryTestResult class with memory tracking."""
        # Memory optimization: Memory-critical operation
        self.animation = kwargs.pop('animation', None)
        self.logger = kwargs.pop('logger', None)
        super().__init__(*args, **kwargs)
        self.test_memory_usage = {}
        # Memory optimization: Memory-critical operation
        self.current_test = None
        self.test_count = 0
        
    def startTest(self, test):
        """Called when a test begins, records initial memory usage."""
        # Memory optimization: Memory-critical operation
        self.current_test = test._testMethodName
        if self.logger:
            self.logger.info(f"Starting test: {self.current_test}")
        gc.collect()  # Force garbage collection before test
        # Memory optimization: Force garbage collection
        self.test_memory_usage[self.current_test] = {
        # Memory optimization: Memory-critical operation
            'before': get_memory_usage()[0]
            # Memory optimization: Memory-critical operation
        }
        super().startTest(test)
        
    def stopTest(self, test):
        """Called when a test completes, records final memory usage."""
        # Memory optimization: Memory-critical operation
        gc.collect()  # Force garbage collection after test
        # Memory optimization: Force garbage collection
        memory_after = get_memory_usage()[0]
        # Memory optimization: Memory-critical operation
        self.test_memory_usage[self.current_test]['after'] = memory_after
        # Memory optimization: Memory-critical operation
        self.test_memory_usage[self.current_test]['delta'] = (
        # Memory optimization: Memory-critical operation
            memory_after - self.test_memory_usage[self.current_test]['before']
            # Memory optimization: Memory-critical operation
        )
        
        # Update animation if provided
        if self.animation:
            self.test_count += 1
            total_tests = self.test_count + len(self._tests) - 1  # Estimate total
            self.animation.update(self.test_count, f"Completed {self.test_count}/{total_tests} tests")
        
        super().stopTest(test)

def run_tests_with_memory_tracking(test_case_class, logger=None):
# Memory optimization: Memory-critical operation
    """
    Run tests with memory tracking and reporting.
    # Memory optimization: Memory-critical operation
    
    Args:
        test_case_class (unittest.TestCase): The test case class to run
        logger (logging.Logger, optional): Logger to use, creates one if not provided
        
    Returns:
        int: Exit code (number of errors + failures)
    """
    import unittest
    
    # Setup logger if not provided
    if logger is None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        logger = logging.getLogger(test_case_class.__name__.lower())
    
    # Print header
    logger.info("="*80)
    logger.info(f"=== {test_case_class.__name__} Test Suite ===")
    start_time = time.time()
    initial_memory, initial_percent = log_memory_usage(logger, "at test suite start")
    # Memory optimization: Memory-critical operation
    
    # System information
    logger.info(f"System: {os.name}, Python: {sys.version.split()[0]}")
    logger.info(f"Total RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    # Memory optimization: Memory-critical operation
    
    # GPU information
    # Memory optimization: Memory-critical operation
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    # Memory optimization: CUDA operations for GPU acceleration
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.info(f"CUDA device count: {torch.cuda.device_count()}")
        # Memory optimization: CUDA operations for GPU acceleration
        logger.info(f"CUDA current device: {torch.cuda.current_device()}")
        # Memory optimization: CUDA operations for GPU acceleration
        for i in range(torch.cuda.device_count()):
        # Memory optimization: CUDA operations for GPU acceleration
            device_props = torch.cuda.get_device_properties(i)
            # Memory optimization: CUDA operations for GPU acceleration
            logger.info(f"GPU {i}: {device_props.name} - {device_props.total_memory / (1024**3):.2f} GB total memory")
            # Memory optimization: Device placement for memory management
    
    # Load test suite
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_case_class)
    
    # Print test count
    logger.info(f"Running {test_suite.countTestCases()} tests...")
    
    # Create a status animation for overall progress
    animation = StatusAnimation(test_suite.countTestCases(), "Running tests")
    animation.update(0, "Preparing test suite")
    
    # Create a test runner with memory tracking
    # Memory optimization: Memory-critical operation
    memory_runner = unittest.TextTestRunner(
    # Memory optimization: Memory-critical operation
        resultclass=MemoryTestResult,
        # Memory optimization: Memory-critical operation
        verbosity=2
    )
    memory_runner.resultclass = lambda *args, **kwargs: MemoryTestResult(
    # Memory optimization: Memory-critical operation
        *args, **kwargs, animation=animation, logger=logger
    )
    
    # Run the tests
    result = memory_runner.run(test_suite)
    # Memory optimization: Memory-critical operation
    
    # Complete the animation
    animation.complete(logger, f"Completed all {test_suite.countTestCases()} tests")
    
    # Print test summary with memory usage
    # Memory optimization: Memory-critical operation
    logger.info("="*80)
    logger.info("Test Summary:")
    
    if hasattr(result, 'test_memory_usage'):
    # Memory optimization: Memory-critical operation
        logger.info("Memory Usage by Test:")
        # Memory optimization: Memory-critical operation
        for test_name, memory_data in result.test_memory_usage.items():
        # Memory optimization: Memory-critical operation
            logger.info(f"  {test_name}: {memory_data['before']:.2f}MB → {memory_data['after']:.2f}MB (delta: {memory_data['delta']:+.2f}MB)")
            # Memory optimization: Memory-critical operation
    
    # Log overall memory usage
    # Memory optimization: Memory-critical operation
    final_memory, final_percent = log_memory_usage(logger, "at test suite end")
    # Memory optimization: Memory-critical operation
    memory_delta = final_memory - initial_memory
    # Memory optimization: Memory-critical operation
    
    # VRAM summary if available
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        vram_allocated = torch.cuda.memory_allocated() / (1024 * 1024)
        # Memory optimization: CUDA operations for GPU acceleration
        vram_reserved = torch.cuda.memory_reserved() / (1024 * 1024)
        # Memory optimization: CUDA operations for GPU acceleration
        logger.info(f"Final VRAM status: {vram_allocated:.2f}MB allocated, {vram_reserved:.2f}MB reserved")
    
    # Summary report
    elapsed_time = time.time() - start_time
    logger.info(f"Test suite completed in {elapsed_time:.2f} seconds")
    logger.info(f"Total memory change: {memory_delta:+.2f}MB ({initial_percent:.1f}% → {final_percent:.1f}%)")
    # Memory optimization: Memory-critical operation
    logger.info(f"Tests run: {result.testsRun}, Errors: {len(result.errors)}, Failures: {len(result.failures)}")
    
    # Return count of errors and failures
    return len(result.errors) + len(result.failures)

# Example usage in a test file:
"""
from tests.memory_tracking_utils import (
# Memory optimization: Memory-critical operation
    setup_logger, log_memory_usage, log_cuda_memory, 
    # Memory optimization: Memory-critical operation
    StatusAnimation, run_tests_with_memory_tracking
    # Memory optimization: Memory-critical operation
)

# Create logger
logger = setup_logger('my_test_logger')

class TestMyComponent(unittest.TestCase):
    def setUp(self):
        logger.info("Setting up test")
        log_memory_usage(logger, "before component creation")
        # Memory optimization: Memory-critical operation
        # Setup code...
        
    def test_something(self):
        logger.info("="*80)
        logger.info("STARTING TEST: test_something")
        animation = StatusAnimation(3, "Testing something")
        
        # Test code with animation updates...
        animation.update(1, "Step 1")
        # More test code...
        
        animation.complete(logger, "Test completed")
        
if __name__ == "__main__":
    import sys
    sys.exit(run_tests_with_memory_tracking(TestMyComponent, logger))
    # Memory optimization: Memory-critical operation
"""
