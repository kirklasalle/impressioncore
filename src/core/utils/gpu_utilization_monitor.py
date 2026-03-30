#!/usr/bin/env python3
"""
ImpressionCore: Gpu Utilization Monitor

Module for gpu utilization monitor functionality in the ImpressionCore framework.

File: core\utils\gpu_utilization_monitor.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, memory-critical, framework, core, production, utils, 2025, object-oriented]
Dependencies: [typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements gpu utilization monitor functionality for the
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
from core.utils.gpu_utilization_monitor import GPUUtilizationMonitor
instance = GPUUtilizationMonitor()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import os
import sys
import time
import threading
import subprocess
from pathlib import Path
import json
from typing import Dict, List, Optional, Any
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.gpu_enforcer import initialize_memlog
# Memory optimization: Memory-critical operation

# Configure logger
logger = logging.getLogger(__name__)

class GPUUtilizationMonitor:
# Memory optimization: Memory-critical operation
    """
    Monitor GPU utilization metrics in real-time.
    # Memory optimization: Memory-critical operation
    
    This class provides utilities to track GPU utilization, including
    # Memory optimization: Memory-critical operation
    compute usage, memory usage, and power consumption.
    # Memory optimization: Memory-critical operation
    """
    
    def __init__(
        self,
        sampling_interval: float = 1.0,
        log_dir: Optional[str] = None,
        alert_threshold: int = 20,
        persistent: bool = True
    ):
        """
        Initialize GPU utilization monitor.
        # Memory optimization: Memory-critical operation
        
        Args:
            sampling_interval: Time between samples in seconds
            log_dir: Directory to write logs (None for default)
            alert_threshold: Utilization % threshold for low utilization alerts
            persistent: Whether to keep persistent logs
        """
        # Initialize memlog
        self.memlog_initialized = initialize_memlog()
        
        # Configuration
        self.sampling_interval = sampling_interval
        self.alert_threshold = alert_threshold
        self.persistent = persistent
        
        # Set up log directory
        if log_dir is None:
            self.log_dir = project_root / "src" / "memlog" / "utilization"
        else:
            self.log_dir = Path(log_dir)
        
        if self.persistent:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # State
        self.is_monitoring = False
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.current_session = None
        self.snapshots = []
        self.start_time = None
        
        # Check for NVIDIA SMI
        self._check_nvidia_smi()
    
    def _check_nvidia_smi(self) -> bool:
        """
        Check if NVIDIA SMI is available.
        
        Returns:
            bool: True if nvidia-smi is available
        """
        try:
            subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            # Memory optimization: Memory-critical operation
                         capture_output=True, text=True, check=True)
            self.nvidia_smi_available = True
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            self.nvidia_smi_available = False
            logger.warning("nvidia-smi not available, GPU monitoring will be limited")
            # Memory optimization: Memory-critical operation
            return False
    
    def start_monitoring(self, session_name: Optional[str] = None) -> bool:
        """
        Start monitoring GPU utilization.
        # Memory optimization: Memory-critical operation
        
        Args:
            session_name: Optional name for the monitoring session
            
        Returns:
            bool: True if monitoring started successfully
        """
        if self.is_monitoring:
            logger.warning("Monitoring already in progress")
            return False
        
        if not self.nvidia_smi_available:
            logger.warning("Cannot start monitoring: nvidia-smi not available")
            return False
        
        # Generate session name if not provided
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.current_session = session_name or f"gpu_util_{timestamp}"
        # Memory optimization: Memory-critical operation
        
        # Set up log file if persistent
        if self.persistent:
            self.log_file = self.log_dir / f"{self.current_session}.csv"
            
            # Write header to log file
            with open(self.log_file, 'w') as f:
                f.write("timestamp,elapsed_seconds,utilization_gpu,utilization_memory,temperature_gpu,power_draw,memory_used,memory_free\n#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src\core\utils\gpu_utilization_monitor.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [core, utils, utility]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.
"""
\n\n")
                # Memory optimization: Memory-critical operation
        
        # Reset monitoring state
        self.snapshots = []
        self.start_time = time.time()
        
        # Start monitoring thread
        self.is_monitoring = True
        self.stop_event.clear()
        # Memory optimization: Memory-critical operation
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"Started GPU utilization monitoring: {self.current_session}")
        # Memory optimization: Memory-critical operation
        return True
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """
        Stop monitoring and return summary statistics.
        
        Returns:
            Dict: Summary statistics
        """
        if not self.is_monitoring:
            logger.warning("No monitoring in progress")
            return {}
        
        # Signal monitoring thread to stop
        self.stop_event.set()
        if self.monitor_thread is not None:
            self.monitor_thread.join(timeout=2.0)
        
        self.is_monitoring = False
        
        # Generate summary
        summary = self._generate_summary()
        
        # Log summary to memlog
        if self.memlog_initialized:
            summary_path = project_root / "src" / "memlog" / "state" / "gpu_utilization_summary.log"
            # Memory optimization: Memory-critical operation
            with open(summary_path, 'w') as f:
                f.write(f"GPU_UTILIZATION_SUMMARY - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                # Memory optimization: Memory-critical operation
                for k, v in summary.items():
                    if isinstance(v, dict):
                        for sk, sv in v.items():
                            f.write(f"{k}_{sk}: {sv}\n")
                    else:
                        f.write(f"{k}: {v}\n")
        
        logger.info(f"Stopped GPU utilization monitoring: {self.current_session}")
        # Memory optimization: Memory-critical operation
        
        return summary
    
    def _monitoring_loop(self):
        """Background thread for utilization monitoring."""
        while not self.stop_event.is_set():
            try:
                # Get GPU metrics
                # Memory optimization: Memory-critical operation
                snapshot = self._get_gpu_metrics()
                # Memory optimization: Memory-critical operation
                elapsed = time.time() - self.start_time
                snapshot['elapsed_seconds'] = elapsed
                
                # Add to snapshots list
                self.snapshots.append(snapshot)
                
                # Log to file if persistent
                if self.persistent and hasattr(self, 'log_file'):
                    with open(self.log_file, 'a') as f:
                        f.write(f"{snapshot['timestamp']},{elapsed:.2f},{snapshot['utilization_gpu']},"
                        # Memory optimization: Memory-critical operation
                              f"{snapshot['utilization_memory']},{snapshot['temperature_gpu']},"
                              # Memory optimization: Memory-critical operation
                              f"{snapshot['power_draw']},{snapshot['memory_used']},{snapshot['memory_free']}\n")
                              # Memory optimization: Memory-critical operation
                
                # Check for low utilization
                if snapshot['utilization_gpu'] < self.alert_threshold:
                # Memory optimization: Memory-critical operation
                    logger.warning(f"Low GPU utilization detected: {snapshot['utilization_gpu']}%")
                    # Memory optimization: Memory-critical operation
                
            except Exception as e:
                logger.error(f"Error in utilization monitoring: {e}")
            
            # Wait for next interval
            self.stop_event.wait(self.sampling_interval)
    
    def _get_gpu_metrics(self) -> Dict[str, Any]:
    # Memory optimization: Memory-critical operation
        """
        Get current GPU metrics from nvidia-smi.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dict: GPU metrics
            # Memory optimization: Memory-critical operation
        """
        metrics = {
            'timestamp': time.time(),
            'utilization_gpu': 0,
            # Memory optimization: Memory-critical operation
            'utilization_memory': 0,
            # Memory optimization: Memory-critical operation
            'temperature_gpu': 0,
            # Memory optimization: Memory-critical operation
            'power_draw': 0,
            'memory_used': 0,
            # Memory optimization: Memory-critical operation
            'memory_free': 0
            # Memory optimization: Memory-critical operation
        }
        
        if not self.nvidia_smi_available:
            return metrics
        
        try:
            # Get utilization
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,utilization.memory,temperature.gpu,power.draw,memory.used,memory.free", "--format=csv,noheader,nounits"],
                # Memory optimization: Memory-critical operation
                capture_output=True, text=True, check=True
            )
            
            if result.stdout:
                values = result.stdout.strip().split(',')
                if len(values) >= 6:
                    metrics['utilization_gpu'] = int(values[0].strip())
                    # Memory optimization: Memory-critical operation
                    metrics['utilization_memory'] = int(values[1].strip())
                    # Memory optimization: Memory-critical operation
                    metrics['temperature_gpu'] = int(values[2].strip())
                    # Memory optimization: Memory-critical operation
                    
                    # Handle power draw which might have a unit (W)
                    power = values[3].strip()
                    if 'W' in power:
                        power = power.replace('W', '')
                    metrics['power_draw'] = float(power) if power else 0
                    
                    # Handle memory values which might have units (MiB)
                    # Memory optimization: Memory-critical operation
                    mem_used = values[4].strip()
                    mem_free = values[5].strip()
                    if 'MiB' in mem_used:
                        mem_used = mem_used.replace('MiB', '')
                    if 'MiB' in mem_free:
                        mem_free = mem_free.replace('MiB', '')
                        
                    metrics['memory_used'] = int(mem_used) if mem_used else 0
                    # Memory optimization: Memory-critical operation
                    metrics['memory_free'] = int(mem_free) if mem_free else 0
                    # Memory optimization: Memory-critical operation
        
        except Exception as e:
            logger.warning(f"Could not get GPU metrics via nvidia-smi: {e}")
            # Memory optimization: Memory-critical operation
        
        return metrics
    
    def _generate_summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics from monitoring data.
        
        Returns:
            Dict: Summary statistics
        """
        summary = {
            'session': self.current_session,
            'duration_seconds': time.time() - self.start_time,
            'samples': len(self.snapshots)
        }
        
        if not self.snapshots:
            return summary
        
        # Calculate statistics for each metric
        metrics = ['utilization_gpu', 'utilization_memory', 'temperature_gpu', 
        # Memory optimization: Memory-critical operation
                  'power_draw', 'memory_used', 'memory_free']
                  # Memory optimization: Memory-critical operation
        
        for metric in metrics:
            values = [s[metric] for s in self.snapshots]
            summary[metric] = {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values)
            }
            
            # For percentages, also calculate time above 50%
            if metric in ['utilization_gpu', 'utilization_memory']:
            # Memory optimization: Memory-critical operation
                above_50 = [s['elapsed_seconds'] for s in self.snapshots if s[metric] > 50]
                if above_50:
                    total_time = self.snapshots[-1]['elapsed_seconds'] - self.snapshots[0]['elapsed_seconds']
                    time_above_50 = len(above_50) / len(self.snapshots) * total_time
                    summary[f"{metric}_time_above_50pct"] = time_above_50
                    summary[f"{metric}_pct_time_above_50"] = len(above_50) / len(self.snapshots) * 100
        
        return summary
    
    def get_current_utilization(self) -> Dict[str, Any]:
        """
        Get current GPU utilization.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dict: Current GPU metrics
            # Memory optimization: Memory-critical operation
        """
        return self._get_gpu_metrics()
        # Memory optimization: Memory-critical operation
    
    def is_gpu_underutilized(self) -> bool:
    # Memory optimization: Memory-critical operation
        """
        Check if GPU is currently underutilized.
        # Memory optimization: Memory-critical operation
        
        Returns:
            bool: True if GPU utilization is below threshold
            # Memory optimization: Memory-critical operation
        """
        metrics = self._get_gpu_metrics()
        # Memory optimization: Memory-critical operation
        return metrics['utilization_gpu'] < self.alert_threshold
        # Memory optimization: Memory-critical operation

def main():
    """Command line interface for GPU utilization monitor."""
    # Memory optimization: Memory-critical operation
    parser = argparse.ArgumentParser(description="Monitor GPU utilization")
    # Memory optimization: Memory-critical operation
    parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    parser.add_argument("--duration", type=float, default=0, help="Monitoring duration in seconds (0 for continuous)")
    parser.add_argument("--threshold", type=int, default=20, help="Low utilization alert threshold (%)")
    parser.add_argument("--output", type=str, help="Output directory for logs")
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Create monitor
    monitor = GPUUtilizationMonitor(
    # Memory optimization: Memory-critical operation
        sampling_interval=args.interval,
        log_dir=args.output,
        alert_threshold=args.threshold
    )
    
    # Start monitoring
    if not monitor.start_monitoring():
        logger.error("Failed to start monitoring")
        return
    
    try:
        if args.duration > 0:
            # Monitor for specified duration
            logger.info(f"Monitoring GPU utilization for {args.duration} seconds")
            # Memory optimization: Memory-critical operation
            time.sleep(args.duration)
        else:
            # Monitor continuously until interrupted
            logger.info("Monitoring GPU utilization (Ctrl+C to stop)")
            # Memory optimization: Memory-critical operation
            while True:
                # Display current utilization every 10 seconds
                time.sleep(10)
                metrics = monitor.get_current_utilization()
                logger.info(f"GPU: {metrics['utilization_gpu']}% util, "
                # Memory optimization: Memory-critical operation
                          f"{metrics['temperature_gpu']}°C, "
                          # Memory optimization: Memory-critical operation
                          f"{metrics['power_draw']:.1f}W, "
                          f"{metrics['memory_used']}MiB used")
                          # Memory optimization: Memory-critical operation
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
    finally:
        # Stop monitoring and show summary
        summary = monitor.stop_monitoring()
        
        if summary and 'utilization_gpu' in summary:
        # Memory optimization: Memory-critical operation
            gpu_util = summary['utilization_gpu']
            # Memory optimization: Memory-critical operation
            print("\nGPU Utilization Summary:")
            # Memory optimization: Memory-critical operation
            print(f"  Min: {gpu_util['min']}%")
            # Memory optimization: Memory-critical operation
            print(f"  Max: {gpu_util['max']}%")
            # Memory optimization: Memory-critical operation
            print(f"  Avg: {gpu_util['avg']:.1f}%")
            # Memory optimization: Memory-critical operation
            
            if 'utilization_gpu_pct_time_above_50' in summary:
            # Memory optimization: Memory-critical operation
                print(f"  Time above 50%: {summary['utilization_gpu_pct_time_above_50']:.1f}% of total")
                # Memory optimization: Memory-critical operation
            
            print(f"  Temperature: {summary['temperature_gpu']['avg']:.1f}°C avg, {summary['temperature_gpu']['max']}°C max")
            # Memory optimization: Memory-critical operation
            print(f"  Power: {summary['power_draw']['avg']:.1f}W avg, {summary['power_draw']['max']:.1f}W max")

if __name__ == "__main__":
    main()
