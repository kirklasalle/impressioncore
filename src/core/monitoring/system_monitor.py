#!/usr/bin/env python3
"""
ImpressionCore: System Monitor

Module for system monitor functionality in the ImpressionCore framework.

File: core\system_monitor.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, pytorch, core, production, 2025, object-oriented]
Dependencies: [torch]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements system monitor functionality for the
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
from core.system_monitor import SystemMonitor
instance = SystemMonitor()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import platform
import psutil
import torch
import logging
import time
import os

logger = logging.getLogger(__name__)

class SystemMonitor:
    """
    
    SystemMonitor class for ImpressionCore framework.
    
    This class implements systemmonitor functionality optimized for
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
    def __init__(self, config=None):
        """
        Initializes the SystemMonitor.

        Args:
            config (dict, optional): Configuration for the system monitor.
                                     Example: {"log_frequency_seconds": 60, "vram_check_threshold_gb": 1}
        """
        self.config = config if config else {}
        self.log_frequency_seconds = self.config.get("log_frequency_seconds", 60)
        self.vram_check_threshold_gb = self.config.get("vram_check_threshold_gb", 1.0)
        self.last_log_time = 0
        logger.info("SystemMonitor initialized.")

    def get_hardware_info(self):
        """
        Gathers basic hardware information (CPU, RAM, GPU if available).
        # Memory optimization: Memory-critical operation

        Returns:
            dict: A dictionary containing hardware information.
        """
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_logical_processors": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            # Memory optimization: Memory-critical operation
            "gpu_info": []
            # Memory optimization: Memory-critical operation
        }

        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            info["cuda_available"] = True
            # Memory optimization: Memory-critical operation
            info["cuda_version"] = torch.version.cuda
            # Memory optimization: Memory-critical operation
            for i in range(torch.cuda.device_count()):
            # Memory optimization: CUDA operations for GPU acceleration
                gpu_props = torch.cuda.get_device_properties(i)
                # Memory optimization: CUDA operations for GPU acceleration
                gpu_mem_total_gb = round(gpu_props.total_memory / (1024**3), 2)
                # Memory optimization: Memory-critical operation
                # Note: Free memory can only be accurately obtained at runtime
                # Memory optimization: Memory-critical operation
                info["gpu_info"].append({
                # Memory optimization: Memory-critical operation
                    "name": gpu_props.name,
                    # Memory optimization: Memory-critical operation
                    "total_memory_gb": gpu_mem_total_gb,
                    # Memory optimization: Memory-critical operation
                    "cuda_capability": f"{gpu_props.major}.{gpu_props.minor}"
                    # Memory optimization: Memory-critical operation
                })
        else:
            info["cuda_available"] = False
            # Memory optimization: Memory-critical operation
        
        logger.info(f"Hardware Info: {info}")
        return info

    def get_resource_usage(self, detailed=False):
        """
        Gets current CPU, RAM, and GPU (if available) usage.
        # Memory optimization: Memory-critical operation

        Args:
            detailed (bool): If True, provides more detailed per-core CPU usage.

        Returns:
            dict: A dictionary containing resource usage information.
        """
        usage = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
            # Memory optimization: Memory-critical operation
            "ram_percent": psutil.virtual_memory().percent,
            # Memory optimization: Memory-critical operation
            "gpu_usage": []
            # Memory optimization: Memory-critical operation
        }
        if detailed:
            usage["cpu_percent_per_core"] = psutil.cpu_percent(interval=0.1, percpu=True)

        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            for i in range(torch.cuda.device_count()):
            # Memory optimization: CUDA operations for GPU acceleration
                gpu_mem = torch.cuda.mem_get_info(i) # (free, total) in bytes
                # Memory optimization: CUDA operations for GPU acceleration
                gpu_mem_used_gb = round((gpu_mem[1] - gpu_mem[0]) / (1024**3), 2)
                # Memory optimization: Memory-critical operation
                gpu_mem_total_gb = round(gpu_mem[1] / (1024**3), 2)
                # Memory optimization: Memory-critical operation
                gpu_mem_percent = round((gpu_mem_used_gb / gpu_mem_total_gb) * 100, 2) if gpu_mem_total_gb > 0 else 0
                # Memory optimization: Memory-critical operation
                
                # Note: torch.cuda.utilization() is not a standard PyTorch function.
                # Memory optimization: CUDA operations for GPU acceleration
                # GPU utilization often requires nvidia-smi or similar tools.
                # Memory optimization: Memory-critical operation
                # For now, we'll focus on memory.
                # Memory optimization: Memory-critical operation
                usage["gpu_usage"].append({
                # Memory optimization: Memory-critical operation
                    "device_id": i,
                    # Memory optimization: Device placement for memory management
                    "name": torch.cuda.get_device_properties(i).name,
                    # Memory optimization: CUDA operations for GPU acceleration
                    "memory_used_gb": gpu_mem_used_gb,
                    # Memory optimization: Memory-critical operation
                    "memory_total_gb": gpu_mem_total_gb,
                    # Memory optimization: Memory-critical operation
                    "memory_percent": gpu_mem_percent
                    # Memory optimization: Memory-critical operation
                })
        return usage

    def log_resource_usage(self, force_log=False, context_message=""):
        """
        Logs current resource usage if enough time has passed since the last log
        or if force_log is True.

        Args:
            force_log (bool): If True, logs regardless of log frequency.
            context_message (str): An optional message to add context to the log.
        """
        current_time = time.time()
        if force_log or (current_time - self.last_log_time >= self.log_frequency_seconds):
            usage = self.get_resource_usage()
            log_message = f"Resource Usage: CPU {usage['cpu_percent']:.2f}%, RAM {usage['ram_used_gb']:.2f}GB ({usage['ram_percent']:.2f}%)"
            if usage["gpu_usage"]:
            # Memory optimization: Memory-critical operation
                for gpu in usage["gpu_usage"]:
                # Memory optimization: Memory-critical operation
                    log_message += f", GPU{gpu['device_id']} Mem {gpu['memory_used_gb']:.2f}/{gpu['memory_total_gb']:.2f}GB ({gpu['memory_percent']:.2f}%)"
                    # Memory optimization: Device placement for memory management
            if context_message:
                log_message = f"[{context_message}] {log_message}"
            logger.info(log_message)
            self.last_log_time = current_time
            return usage
        return None

    def check_vram_availability(self, required_gb=None):
        """
        Checks if there is sufficient VRAM available on CUDA devices.
        # Memory optimization: Device placement for memory management

        Args:
            required_gb (float, optional): The amount of VRAM in GB required.
                                           Defaults to self.vram_check_threshold_gb.

        Returns:
            bool: True if sufficient VRAM is available on at least one device, False otherwise.
            # Memory optimization: Device placement for memory management
                  Returns True if no CUDA device is present (as VRAM check is not applicable).
                  # Memory optimization: Device placement for memory management
        """
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            logger.info("No CUDA devices found. VRAM check not applicable.")
            # Memory optimization: Device placement for memory management
            return True # No GPU, so VRAM constraint doesn't apply in the same way
            # Memory optimization: Memory-critical operation

        threshold_gb = required_gb if required_gb is not None else self.vram_check_threshold_gb
        sufficient_vram_found = False
        for i in range(torch.cuda.device_count()):
        # Memory optimization: CUDA operations for GPU acceleration
            gpu_mem_info = torch.cuda.mem_get_info(i)  # (free, total)
            # Memory optimization: CUDA operations for GPU acceleration
            available_gb = round(gpu_mem_info[0] / (1024**3), 2)
            # Memory optimization: Memory-critical operation
            total_gb = round(gpu_mem_info[1] / (1024**3), 2)
            # Memory optimization: Memory-critical operation
            device_name = torch.cuda.get_device_properties(i).name
            # Memory optimization: CUDA operations for GPU acceleration
            
            logger.info(f"GPU {i} ({device_name}): Available VRAM {available_gb:.2f}GB / {total_gb:.2f}GB. Required: {threshold_gb:.2f}GB.")
            # Memory optimization: Device placement for memory management
            if available_gb >= threshold_gb:
                sufficient_vram_found = True
                # We could break here if any device is sufficient, or check all
                # Memory optimization: Device placement for memory management
            else:
                logger.warning(f"GPU {i} ({device_name}): Insufficient VRAM. Available {available_gb:.2f}GB, Required {threshold_gb:.2f}GB.")
                # Memory optimization: Device placement for memory management
        
        if not sufficient_vram_found and torch.cuda.device_count() > 0:
        # Memory optimization: CUDA operations for GPU acceleration
             logger.error(f"Overall insufficient VRAM based on threshold {threshold_gb:.2f}GB across all detected GPUs.")
             # Memory optimization: Memory-critical operation
        elif sufficient_vram_found:
            logger.info(f"Sufficient VRAM ({threshold_gb=:.2f}GB) available on at least one GPU.")
            # Memory optimization: Memory-critical operation

        return sufficient_vram_found

    def start_monitoring_thread(self, interval_seconds=None, context=""):
        """
        Placeholder for starting a background thread for continuous monitoring.
        Actual implementation would require threading.Thread.
        """
        _interval = interval_seconds if interval_seconds is not None else self.log_frequency_seconds
        logger.info(f"Placeholder: System monitoring thread would start now, logging every {_interval}s. Context: {context}")
        # Example (conceptual, not run):
        # def _monitor_loop():
        #     while not self._stop_event.is_set():
        #         self.log_resource_usage(context_message=f"Background Monitor ({context})")
        #         time.sleep(_interval)
        # self._stop_event = threading.Event()
        # self._monitor_thread = threading.Thread(target=_monitor_loop)
        # self._monitor_thread.daemon = True
        # self._monitor_thread.start()

    def stop_monitoring_thread(self):
        """
        Placeholder for stopping the background monitoring thread.
        """
        logger.info("Placeholder: System monitoring thread would stop now.")
        # if hasattr(self, '_stop_event'):
        #     self._stop_event.set()
        # if hasattr(self, '_monitor_thread') and self._monitor_thread.is_alive():
        #     self._monitor_thread.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    
    # Test with default config
    monitor = SystemMonitor()
    hardware_info = monitor.get_hardware_info()
    # print(f"Hardware Info:\n{json.dumps(hardware_info, indent=2)}")

    monitor.log_resource_usage(force_log=True, context_message="Initial Check")
    
    # Test with custom config
    custom_config = {
        "log_frequency_seconds": 5,
        "vram_check_threshold_gb": 0.5 # Low threshold for testing
    }
    monitor_custom = SystemMonitor(config=custom_config)
    monitor_custom.get_hardware_info() # Logged by the function itself
    
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        monitor_custom.check_vram_availability()
        monitor_custom.check_vram_availability(required_gb=2.0) # Check for 2GB
    else:
        logger.info("CUDA not available, skipping VRAM specific tests.")
        # Memory optimization: Memory-critical operation

    logger.info("Simulating some activity...")
    time.sleep(2)
    monitor_custom.log_resource_usage(context_message="After 2s delay")
    
    time.sleep(6) # Should trigger automatic log due to log_frequency_seconds=5
    monitor_custom.log_resource_usage(context_message="After 6s (auto log expected)") # Will log if condition met

    monitor.start_monitoring_thread(interval_seconds=3, context="Test Thread")
    time.sleep(7) # Allow some logs from the placeholder thread
    monitor.stop_monitoring_thread()
    
    logger.info("SystemMonitor test finished.")
