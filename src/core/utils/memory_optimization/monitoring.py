#!/usr/bin/env python3
"""
ImpressionCore: Monitoring

Module for monitoring functionality in the ImpressionCore framework.

File: core/utils/memory_optimization/monitoring.py
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
Dependencies: [torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements monitoring functionality for the
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





# Examples:
# Basic usage example:
# from core.utils.memory_optimization.monitoring import MemoryMonitor
# instance = MemoryMonitor()
# result = instance.process()

# Notes:
# - Optimized for GTX 1050 Ti (4GB VRAM)
# - Implements memory-efficient algorithms
# - Provides CPU fallback capabilities
# - Thread-safe implementation
"""

import logging
import torch
import gc
import psutil
import os
import threading
import time
from typing import Dict, List, Tuple, Union, Optional, Callable

# Configure logging
logger = logging.getLogger(__name__)

def monitor_memory_usage(device: str = "cuda", log_level: str = "info") -> Dict[str, Union[int, float]]:
# Memory optimization: Device placement for memory management
    """
    Monitor current memory usage on the specified device.
    # Memory optimization: Device placement for memory management
    
    Args:
        device: Device to monitor ('cuda' for GPU, 'cpu' for CPU)
        # Memory optimization: Device placement for memory management
        log_level: Logging level ('debug', 'info', 'warning')
    
    Returns:
        Dict containing memory usage statistics
        # Memory optimization: Memory-critical operation
    """
    memory_stats = {}
    # Memory optimization: Memory-critical operation
    
    # Force garbage collection first
    gc.collect()
    # Memory optimization: Force garbage collection
    
    if device.startswith('cuda') and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        # For CUDA devices
        # Memory optimization: Device placement for memory management
        torch.cuda.synchronize()
        # Memory optimization: CUDA operations for GPU acceleration
        
        memory_allocated = torch.cuda.memory_allocated(device=device)
        # Memory optimization: CUDA operations for GPU acceleration
        memory_reserved = torch.cuda.memory_reserved(device=device)
        # Memory optimization: CUDA operations for GPU acceleration
        max_memory_allocated = torch.cuda.max_memory_allocated(device=device)
        # Memory optimization: CUDA operations for GPU acceleration
        
        memory_stats = {
        # Memory optimization: Memory-critical operation
            'allocated_mb': memory_allocated / (1024 * 1024),
            # Memory optimization: Memory-critical operation
            'reserved_mb': memory_reserved / (1024 * 1024),
            # Memory optimization: Memory-critical operation
            'max_allocated_mb': max_memory_allocated / (1024 * 1024),
            # Memory optimization: Memory-critical operation
        }
        
        if hasattr(torch.cuda, 'memory_summary'):
        # Memory optimization: CUDA operations for GPU acceleration
            # This provides more detailed info if available
            memory_stats['memory_summary'] = torch.cuda.memory_summary(device=device)
            # Memory optimization: CUDA operations for GPU acceleration
    
    # Always include CPU memory stats
    # Memory optimization: Memory-critical operation
    process = psutil.Process(os.getpid())
    cpu_memory = process.memory_info().rss
    # Memory optimization: Memory-critical operation
    
    memory_stats['cpu_memory_mb'] = cpu_memory / (1024 * 1024)
    # Memory optimization: Memory-critical operation
    memory_stats['cpu_percent'] = process.cpu_percent()
    # Memory optimization: Memory-critical operation
    memory_stats['system_memory_percent'] = psutil.virtual_memory().percent
    # Memory optimization: Memory-critical operation
    
    # Log based on requested level
    log_func = getattr(logger, log_level.lower(), logger.info)
    log_func(f"Memory usage: {memory_stats}")
    # Memory optimization: Memory-critical operation
    
    return memory_stats
    # Memory optimization: Memory-critical operation

def estimate_memory_requirements(
# Memory optimization: Memory-critical operation
    model_size: int, 
    batch_size: int, 
    sequence_length: int, 
    dtype: torch.dtype = torch.float32,
    include_optimizer: bool = True,
    optimizer_type: str = "adam"
) -> Dict[str, Union[int, float]]:
    """
    Estimate memory requirements for a model configuration.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        model_size: Number of parameters in the model
        batch_size: Batch size for training/inference
        sequence_length: Length of sequences
        dtype: Model data type (affects bytes per parameter)
        # Memory optimization: Explicit memory cleanup
        include_optimizer: Whether to include optimizer memory
        # Memory optimization: Memory-critical operation
        optimizer_type: Type of optimizer ('adam', 'sgd', etc.)
    
    Returns:
        Dict containing estimated memory requirements in MB
        # Memory optimization: Memory-critical operation
    """
    # Bytes per parameter based on dtype
    dtype_sizes = {
        torch.float16: 2,
        torch.float32: 4,
        torch.float64: 8,
        torch.int8: 1,
        torch.uint8: 1,
        torch.int16: 2,
        torch.int32: 4,
        torch.int64: 8,
        torch.bool: 1,
    }
    
    bytes_per_param = dtype_sizes.get(dtype, 4)  # Default to float32 (4 bytes)
    
    # Model memory
    # Memory optimization: Explicit memory cleanup
    model_memory_bytes = model_size * bytes_per_param
    # Memory optimization: Memory-critical operation
    
    # Optimizer memory
    # Memory optimization: Memory-critical operation
    optimizer_memory_bytes = 0
    # Memory optimization: Memory-critical operation
    if include_optimizer:
        if optimizer_type.lower() == "adam":
            # Adam stores 2 states per parameter
            optimizer_memory_bytes = model_size * bytes_per_param * 2
            # Memory optimization: Memory-critical operation
        else:
            # SGD and others typically store 1 state
            optimizer_memory_bytes = model_size * bytes_per_param
            # Memory optimization: Memory-critical operation
    
    # Activation memory (rough estimate)
    # Memory optimization: Memory-critical operation
    # This depends heavily on model architecture, but as a rule of thumb:
    # Memory optimization: Explicit memory cleanup
    activations_per_sample = model_size / 10  # Rough approximation
    activation_memory_bytes = activations_per_sample * batch_size * sequence_length * bytes_per_param
    # Memory optimization: Memory-critical operation
    
    # Gradient memory
    # Memory optimization: Memory-critical operation
    gradient_memory_bytes = model_size * bytes_per_param
    # Memory optimization: Memory-critical operation
    
    # Total memory
    # Memory optimization: Memory-critical operation
    total_memory_bytes = (
    # Memory optimization: Memory-critical operation
        model_memory_bytes + 
        # Memory optimization: Memory-critical operation
        optimizer_memory_bytes + 
        # Memory optimization: Memory-critical operation
        activation_memory_bytes + 
        # Memory optimization: Memory-critical operation
        gradient_memory_bytes
        # Memory optimization: Memory-critical operation
    )
    
    # Convert to MB
    memory_mb = total_memory_bytes / (1024 * 1024)
    # Memory optimization: Memory-critical operation
    
    # Prepare result
    result = {
        'model_memory_mb': model_memory_bytes / (1024 * 1024),
        # Memory optimization: Memory-critical operation
        'optimizer_memory_mb': optimizer_memory_bytes / (1024 * 1024),
        # Memory optimization: Memory-critical operation
        'activation_memory_mb': activation_memory_bytes / (1024 * 1024),
        # Memory optimization: Memory-critical operation
        'gradient_memory_mb': gradient_memory_bytes / (1024 * 1024),
        # Memory optimization: Memory-critical operation
        'total_estimated_memory_mb': memory_mb,
        # Memory optimization: Memory-critical operation
    }
    
    return result

class MemoryMonitor:
# Memory optimization: Memory-critical operation
    """
    Base class for memory monitoring.
    # Memory optimization: Memory-critical operation
    
    Provides continuous monitoring of memory usage with periodic logging
    # Memory optimization: Memory-critical operation
    and alert thresholds.
    """
    
    def __init__(self, 
                 monitoring_interval: float = 1.0,
                 alert_threshold: Optional[float] = None,
                 alert_callback: Optional[Callable] = None,
                 log_level: str = "info",
                 log_to_file: bool = False,
                 log_file_path: Optional[str] = None):
        """
        Initialize the memory monitor.
        # Memory optimization: Memory-critical operation
        
        Args:
            monitoring_interval: How often to check memory usage (seconds)
            # Memory optimization: Memory-critical operation
            alert_threshold: Threshold to trigger alerts (percentage)
            alert_callback: Function to call when threshold is exceeded
            log_level: Level for logging ('debug', 'info', 'warning', 'error')
            log_to_file: Whether to log memory stats to a file
            # Memory optimization: Memory-critical operation
            log_file_path: Path to log file (if log_to_file is True)
        """
        self.monitoring_interval = monitoring_interval
        self.alert_threshold = alert_threshold
        self.alert_callback = alert_callback
        self.log_level = log_level.lower()
        self.log_to_file = log_to_file
        self.log_file_path = log_file_path
        
        # Setup file logging if requested
        if self.log_to_file:
            if self.log_file_path is None:
                self.log_file_path = f"memory_monitor_{int(time.time())}.log"
                # Memory optimization: Memory-critical operation
            
            self.file_logger = logging.getLogger(f"{__name__}.file")
            file_handler = logging.FileHandler(self.log_file_path)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.file_logger.addHandler(file_handler)
            self.file_logger.setLevel(logging.INFO)
        
        # Thread management
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        self._is_monitoring = False
        
        # Memory stats history
        # Memory optimization: Memory-critical operation
        self.history = []
        self.max_history_length = 1000  # Avoid unbounded memory growth
        # Memory optimization: Memory-critical operation
    
    def _log_memory_stats(self, stats: Dict[str, Union[int, float]]) -> None:
    # Memory optimization: Memory-critical operation
        """Log memory statistics."""
        # Memory optimization: Memory-critical operation
        log_func = getattr(logger, self.log_level, logger.info)
        log_func(f"Memory stats: {stats}")
        # Memory optimization: Memory-critical operation
        
        if self.log_to_file:
            self.file_logger.info(f"Memory stats: {stats}")
            # Memory optimization: Memory-critical operation
    
    def _check_alert_threshold(self, stats: Dict[str, Union[int, float]]) -> bool:
        """
        Check if memory usage exceeds the alert threshold.
        # Memory optimization: Memory-critical operation
        
        Returns:
            bool: True if threshold is exceeded, False otherwise
        """
        if self.alert_threshold is None:
            return False
            
        # Default implementation (subclasses should override)
        memory_percent = stats.get('percent', 0)
        # Memory optimization: Memory-critical operation
        
        if memory_percent > self.alert_threshold:
        # Memory optimization: Memory-critical operation
            logger.warning(f"Memory alert: {memory_percent}% exceeds threshold of {self.alert_threshold}%")
            # Memory optimization: Memory-critical operation
            if self.alert_callback:
                self.alert_callback(stats)
            return True
            
        return False
    
    def _monitor_memory(self) -> Dict[str, Union[int, float]]:
    # Memory optimization: Memory-critical operation
        """
        Perform a single memory check.
        # Memory optimization: Memory-critical operation
        
        This method should be overridden by subclasses.
        
        Returns:
            Dict containing memory statistics
            # Memory optimization: Memory-critical operation
        """
        raise NotImplementedError("Subclasses must implement _monitor_memory()")
        # Memory optimization: Memory-critical operation
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop that runs in a separate thread."""
        while not self._stop_monitoring.is_set():
            try:
                # Get memory stats
                # Memory optimization: Memory-critical operation
                stats = self._monitor_memory()
                # Memory optimization: Memory-critical operation
                
                # Log and check for alerts
                self._log_memory_stats(stats)
                # Memory optimization: Memory-critical operation
                self._check_alert_threshold(stats)
                
                # Store in history
                self.history.append((time.time(), stats))
                
                # Trim history if needed
                if len(self.history) > self.max_history_length:
                    self.history = self.history[-self.max_history_length:]
                
            except Exception as e:
                logger.error(f"Error in memory monitoring: {e}")
                # Memory optimization: Memory-critical operation
            
            # Wait for next interval
            time.sleep(self.monitoring_interval)
    
    def start_monitoring(self) -> None:
        """Start continuous memory monitoring in a background thread."""
        # Memory optimization: Memory-critical operation
        if self._is_monitoring:
            logger.warning("Memory monitoring is already running")
            # Memory optimization: Memory-critical operation
            return
            
        self._stop_monitoring.clear()
        # Memory optimization: Memory-critical operation
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True  # Allow program to exit even if thread is running
        )
        self._monitoring_thread.start()
        self._is_monitoring = True
        logger.info("Memory monitoring started")
        # Memory optimization: Memory-critical operation
    
    def stop_monitoring(self) -> None:
        """Stop continuous memory monitoring."""
        # Memory optimization: Memory-critical operation
        if not self._is_monitoring:
            return
            
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=2*self.monitoring_interval)
            
        self._is_monitoring = False
        logger.info("Memory monitoring stopped")
        # Memory optimization: Memory-critical operation
    
    def get_memory_stats(self) -> Dict[str, Union[int, float]]:
    # Memory optimization: Memory-critical operation
        """
        Get current memory statistics.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dict containing memory statistics
            # Memory optimization: Memory-critical operation
        """
        return self._monitor_memory()
        # Memory optimization: Memory-critical operation
    
    def get_memory_history(self) -> List[Tuple[float, Dict[str, Union[int, float]]]]:
    # Memory optimization: Memory-critical operation
        """
        Get history of memory statistics.
        # Memory optimization: Memory-critical operation
        
        Returns:
            List of (timestamp, stats_dict) tuples
        """
        return self.history.copy()
    
    def __enter__(self) -> 'MemoryMonitor':
    # Memory optimization: Memory-critical operation
        """Context manager entry."""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop_monitoring()


class GPUMemoryMonitor(MemoryMonitor):
# Memory optimization: Memory-critical operation
    """
    GPU memory monitoring class.
    # Memory optimization: Memory-critical operation
    
    Monitors VRAM usage with support for multiple GPUs.
    # Memory optimization: Memory-critical operation
    """
    
    def __init__(self, 
                 device_id: Optional[int] = None,
                 # Memory optimization: Device placement for memory management
                 **kwargs):
        """
        Initialize GPU memory monitor.
        # Memory optimization: Memory-critical operation
        
        Args:
            device_id: GPU device ID to monitor (None = all devices)
            # Memory optimization: Device placement for memory management
            **kwargs: Additional arguments passed to MemoryMonitor
            # Memory optimization: Memory-critical operation
        """
        super().__init__(**kwargs)
        
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            logger.warning("CUDA is not available. GPU monitoring will be limited.")
            # Memory optimization: Memory-critical operation
            
        self.device_id = device_id
        # Memory optimization: Device placement for memory management
        
        # Set default threshold if not specified
        if self.alert_threshold is None:
            self.alert_threshold = 90.0  # 90% VRAM usage
    
    def _monitor_memory(self) -> Dict[str, Union[int, float]]:
    # Memory optimization: Memory-critical operation
        """
        Monitor GPU memory usage.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dict with GPU memory statistics
            # Memory optimization: Memory-critical operation
        """
        stats = {}
        
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            return {
                'cuda_available': False,
                # Memory optimization: Memory-critical operation
                'error': 'CUDA not available'
                # Memory optimization: Memory-critical operation
            }
        
        # Force garbage collection to get accurate readings
        gc.collect()
        # Memory optimization: Force garbage collection
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.synchronize()
            # Memory optimization: CUDA operations for GPU acceleration
        
        # Get memory info for specified device(s)
        # Memory optimization: Device placement for memory management
        devices_to_check = [self.device_id] if self.device_id is not None else range(torch.cuda.device_count())
        # Memory optimization: CUDA operations for GPU acceleration
        
        for device in devices_to_check:
        # Memory optimization: Device placement for memory management
            try:
                # Get statistics for this device
                # Memory optimization: Device placement for memory management
                allocated = torch.cuda.memory_allocated(device)
                # Memory optimization: CUDA operations for GPU acceleration
                reserved = torch.cuda.memory_reserved(device)
                # Memory optimization: CUDA operations for GPU acceleration
                total = torch.cuda.get_device_properties(device).total_memory
                # Memory optimization: CUDA operations for GPU acceleration
                
                device_stats = {
                # Memory optimization: Device placement for memory management
                    'allocated': allocated,
                    'allocated_mb': allocated / (1024 * 1024),
                    'reserved': reserved,
                    'reserved_mb': reserved / (1024 * 1024),
                    'total': total,
                    'total_mb': total / (1024 * 1024),
                    'percent': (allocated / total) * 100.0,
                    'device_name': torch.cuda.get_device_name(device)
                    # Memory optimization: CUDA operations for GPU acceleration
                }
                
                # Add to overall stats
                if self.device_id is not None:
                # Memory optimization: Device placement for memory management
                    stats = device_stats
                    # Memory optimization: Device placement for memory management
                else:
                    stats[f'device_{device}'] = device_stats
                    # Memory optimization: Device placement for memory management
                    
                # Add current CUDA allocation stats
                # Memory optimization: Memory-critical operation
                if hasattr(torch.cuda, 'memory_stats'):
                # Memory optimization: CUDA operations for GPU acceleration
                    device_stats['memory_stats'] = torch.cuda.memory_stats(device)
                    # Memory optimization: CUDA operations for GPU acceleration
                
            except Exception as e:
                logger.error(f"Error monitoring GPU {device}: {e}")
                # Memory optimization: Device placement for memory management
                if self.device_id is not None:
                # Memory optimization: Device placement for memory management
                    stats['error'] = str(e)
                else:
                    stats[f'device_{device}_error'] = str(e)
                    # Memory optimization: Device placement for memory management
        
        # Add overall stats if monitoring multiple devices
        # Memory optimization: Device placement for memory management
        if self.device_id is None and len(devices_to_check) > 1:
        # Memory optimization: Device placement for memory management
            total_allocated = sum(torch.cuda.memory_allocated(d) for d in devices_to_check)
            # Memory optimization: CUDA operations for GPU acceleration
            total_reserved = sum(torch.cuda.memory_reserved(d) for d in devices_to_check)
            # Memory optimization: CUDA operations for GPU acceleration
            total_memory = sum(torch.cuda.get_device_properties(d).total_memory for d in devices_to_check)
            # Memory optimization: CUDA operations for GPU acceleration
            
            stats['total_allocated_mb'] = total_allocated / (1024 * 1024)
            stats['total_reserved_mb'] = total_reserved / (1024 * 1024)
            stats['total_available_mb'] = total_memory / (1024 * 1024)
            # Memory optimization: Memory-critical operation
            stats['overall_percent'] = (total_allocated / total_memory) * 100.0
            # Memory optimization: Memory-critical operation
        
        return stats
    
    def _check_alert_threshold(self, stats: Dict[str, Union[int, float]]) -> bool:
        """Check if GPU memory usage exceeds alert threshold."""
        # Memory optimization: Memory-critical operation
        if self.alert_threshold is None:
            return False
        
        if self.device_id is not None:
        # Memory optimization: Device placement for memory management
            # Single device mode
            # Memory optimization: Device placement for memory management
            if 'percent' in stats and stats['percent'] > self.alert_threshold:
                logger.warning(f"GPU {self.device_id} memory alert: "
                # Memory optimization: Device placement for memory management
                            f"{stats['percent']:.1f}% exceeds threshold of {self.alert_threshold}%")
                if self.alert_callback:
                    self.alert_callback(stats)
                return True
        else:
            # Multi-device mode
            # Memory optimization: Device placement for memory management
            triggered = False
            for key, device_stats in stats.items():
            # Memory optimization: Device placement for memory management
                if isinstance(device_stats, dict) and 'percent' in device_stats:
                # Memory optimization: Device placement for memory management
                    if device_stats['percent'] > self.alert_threshold:
                    # Memory optimization: Device placement for memory management
                        logger.warning(f"{key} memory alert: "
                        # Memory optimization: Memory-critical operation
                                    f"{device_stats['percent']:.1f}% exceeds threshold of {self.alert_threshold}%")
                                    # Memory optimization: Device placement for memory management
                        triggered = True
            
            if triggered and self.alert_callback:
                self.alert_callback(stats)
            
            return triggered
        
        return False


class CPUMemoryMonitor(MemoryMonitor):
# Memory optimization: Memory-critical operation
    """
    CPU memory monitoring class.
    # Memory optimization: Memory-critical operation
    
    Monitors RAM usage of the current process and overall system.
    """
    
    def __init__(self, 
                 include_system_memory: bool = True,
                 # Memory optimization: Memory-critical operation
                 **kwargs):
        """
        Initialize CPU memory monitor.
        # Memory optimization: Memory-critical operation
        
        Args:
            include_system_memory: Whether to include system-wide memory stats
            # Memory optimization: Memory-critical operation
            **kwargs: Additional arguments passed to MemoryMonitor
            # Memory optimization: Memory-critical operation
        """
        super().__init__(**kwargs)
        
        self.include_system_memory = include_system_memory
        # Memory optimization: Memory-critical operation
        self.process = psutil.Process(os.getpid())
        
        # Set default threshold if not specified
        if self.alert_threshold is None:
            self.alert_threshold = 90.0  # 90% RAM usage
    
    def _monitor_memory(self) -> Dict[str, Union[int, float]]:
    # Memory optimization: Memory-critical operation
        """
        Monitor CPU memory usage.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dict with CPU memory statistics
            # Memory optimization: Memory-critical operation
        """
        stats = {}
        
        # Force garbage collection to get accurate readings
        gc.collect()
        # Memory optimization: Force garbage collection
        
        # Get process memory info
        # Memory optimization: Memory-critical operation
        try:
            mem_info = self.process.memory_info()
            # Memory optimization: Memory-critical operation
            stats['process'] = {
                'rss': mem_info.rss,  # Resident Set Size
                'rss_mb': mem_info.rss / (1024 * 1024),
                'vms': mem_info.vms,  # Virtual Memory Size
                # Memory optimization: Memory-critical operation
                'vms_mb': mem_info.vms / (1024 * 1024),
                'percent': self.process.memory_percent(),
                # Memory optimization: Memory-critical operation
                'cpu_percent': self.process.cpu_percent(),
            }
        except Exception as e:
            logger.error(f"Error monitoring process memory: {e}")
            # Memory optimization: Memory-critical operation
            stats['process_error'] = str(e)
        
        # Get system memory info if requested
        # Memory optimization: Memory-critical operation
        if self.include_system_memory:
        # Memory optimization: Memory-critical operation
            try:
                system_mem = psutil.virtual_memory()
                # Memory optimization: Memory-critical operation
                stats['system'] = {
                    'total': system_mem.total,
                    'total_gb': system_mem.total / (1024**3),
                    'available': system_mem.available,
                    'available_gb': system_mem.available / (1024**3),
                    'used': system_mem.used,
                    'used_gb': system_mem.used / (1024**3),
                    'percent': system_mem.percent,
                }
                
                # Add swap info
                swap = psutil.swap_memory()
                # Memory optimization: Memory-critical operation
                stats['swap'] = {
                    'total': swap.total,
                    'total_gb': swap.total / (1024**3),
                    'used': swap.used,
                    'used_gb': swap.used / (1024**3),
                    'free': swap.free,
                    'free_gb': swap.free / (1024**3),
                    'percent': swap.percent,
                }
            except Exception as e:
                logger.error(f"Error monitoring system memory: {e}")
                # Memory optimization: Memory-critical operation
                stats['system_error'] = str(e)
        
        return stats
    
    def _check_alert_threshold(self, stats: Dict[str, Union[int, float]]) -> bool:
        """
        Check if CPU memory usage exceeds alert threshold.
        # Memory optimization: Memory-critical operation
        
        This checks both process and system memory if system monitoring is enabled.
        # Memory optimization: Memory-critical operation
        """
        if self.alert_threshold is None:
            return False
        
        triggered = False
        
        # Check process memory
        # Memory optimization: Memory-critical operation
        if 'process' in stats and 'percent' in stats['process']:
            process_percent = stats['process']['percent']
            if process_percent > self.alert_threshold:
                logger.warning(f"Process memory alert: "
                # Memory optimization: Memory-critical operation
                            f"{process_percent:.1f}% exceeds threshold of {self.alert_threshold}%")
                triggered = True
        
        # Check system memory
        # Memory optimization: Memory-critical operation
        if self.include_system_memory and 'system' in stats and 'percent' in stats['system']:
        # Memory optimization: Memory-critical operation
            system_percent = stats['system']['percent']
            if system_percent > self.alert_threshold:
                logger.warning(f"System memory alert: "
                # Memory optimization: Memory-critical operation
                            f"{system_percent:.1f}% exceeds threshold of {self.alert_threshold}%")
                triggered = True
        
        if triggered and self.alert_callback:
            self.alert_callback(stats)
            
        return triggered
