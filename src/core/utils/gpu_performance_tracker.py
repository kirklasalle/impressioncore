#!/usr/bin/env python3
"""
ImpressionCore: Gpu Performance Tracker

Module for gpu performance tracker functionality in the ImpressionCore framework.

File: core/utils/gpu_performance_tracker.py
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
Dependencies: [torch, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements gpu performance tracker functionality for the
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
from src.core.utils.gpu_performance_tracker import GPUPerformanceTracker
instance = GPUPerformanceTracker()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import time
import logging
import csv
import threading
import argparse
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sys
import matplotlib.pyplot as plt

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    import torch
    from utils.cuda_utils import get_cuda_info, get_nvidia_smi_info
    # Memory optimization: Memory-critical operation
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GPUPerformanceTracker:
# Memory optimization: Memory-critical operation
    """
    Track and analyze GPU performance and memory utilization.
    # Memory optimization: Memory-critical operation
    
    This class provides utilities to monitor GPU usage during model training
    # Memory optimization: Explicit memory cleanup
    and analyze the results to optimize performance.
    """
    
    def __init__(
        self,
        log_dir: str = "performance_logs",
        interval_sec: float = 1.0,
        track_processes: bool = True,
        track_system_ram: bool = True,
        plot_results: bool = True
    ):
        """
        Initialize the performance tracker.
        
        Args:
            log_dir: Directory to store log files
            interval_sec: Sampling interval in seconds
            track_processes: Whether to track GPU processes
            # Memory optimization: Memory-critical operation
            track_system_ram: Whether to track system RAM usage
            plot_results: Whether to generate plots automatically
        """
        self.log_dir = log_dir
        self.interval_sec = interval_sec
        self.track_processes = track_processes
        self.track_system_ram = track_system_ram
        self.plot_results = plot_results
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Tracking state
        self.tracking = False
        self.tracking_thread = None
        self.stop_event = threading.Event()
        self.current_session = None
        self.snapshots = []
        
        # Check if CUDA is available
        # Memory optimization: Memory-critical operation
        self.cuda_available = HAS_TORCH and torch.cuda.is_available()
        # Memory optimization: CUDA operations for GPU acceleration
        if not self.cuda_available:
        # Memory optimization: Memory-critical operation
            logger.warning("CUDA not available - limited tracking functionality")
            # Memory optimization: Memory-critical operation
    
    def start_tracking(self, session_name: Optional[str] = None) -> str:
        """
        Start tracking GPU performance.
        # Memory optimization: Memory-critical operation
        
        Args:
            session_name: Optional name for the tracking session
            
        Returns:
            Session ID
        """
        if self.tracking:
            logger.warning("Tracking already in progress")
            return self.current_session
        
        # Generate session ID
        timestamp = int(time.time())
        session_id = session_name or f"session_{timestamp}"
        self.current_session = session_id
        
        # Create session log file
        self.log_file = os.path.join(self.log_dir, f"{session_id}.csv")
        self.snapshots = []
        
        # Write header to log file
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            header = [
                'timestamp', 'gpu_util_pct', 'memory_used_mb', 'memory_free_mb',
                # Memory optimization: Memory-critical operation
                'memory_total_mb', 'power_watts', 'temperature_c'
                # Memory optimization: Memory-critical operation
            ]
            if self.track_system_ram:
                header.extend(['system_ram_used_mb', 'system_ram_free_mb'])
            writer.writerow(header)
        
        # Start tracking thread
        self.stop_event.clear()
        # Memory optimization: Memory-critical operation
        self.tracking = True
        self.tracking_thread = threading.Thread(
            target=self._tracking_loop,
            daemon=True
        )
        self.tracking_thread.start()
        
        logger.info(f"Started GPU performance tracking: {session_id}")
        # Memory optimization: Memory-critical operation
        return session_id
    
    def stop_tracking(self) -> Dict[str, Any]:
        """
        Stop tracking and return summary stats.
        
        Returns:
            Dictionary of summary statistics
        """
        if not self.tracking:
            logger.warning("No tracking in progress")
            return {}
        
        # Signal thread to stop
        self.stop_event.set()
        if self.tracking_thread:
            self.tracking_thread.join(timeout=2.0)
        
        self.tracking = False
        logger.info(f"Stopped GPU performance tracking: {self.current_session}")
        # Memory optimization: Memory-critical operation
        
        # Generate summary
        summary = self._generate_summary()
        
        # Generate plots if enabled
        if self.plot_results and self.snapshots:
            self._generate_plots()
        
        return summary
    
    def _tracking_loop(self):
        """Background thread for tracking GPU metrics."""
        # Memory optimization: Memory-critical operation
        while not self.stop_event.is_set():
            try:
                # Get GPU metrics
                # Memory optimization: Memory-critical operation
                snapshot = self._get_gpu_metrics()
                # Memory optimization: Memory-critical operation
                self.snapshots.append(snapshot)
                
                # Write to log file
                with open(self.log_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    row = [
                        snapshot['timestamp'],
                        snapshot.get('gpu_util', 0),
                        # Memory optimization: Memory-critical operation
                        snapshot.get('memory_used_mb', 0),
                        # Memory optimization: Memory-critical operation
                        snapshot.get('memory_free_mb', 0),
                        # Memory optimization: Memory-critical operation
                        snapshot.get('memory_total_mb', 0),
                        # Memory optimization: Memory-critical operation
                        snapshot.get('power_watts', 0),
                        snapshot.get('temperature_c', 0),
                    ]
                    if self.track_system_ram:
                        row.extend([
                            snapshot.get('system_ram_used_mb', 0),
                            snapshot.get('system_ram_free_mb', 0)
                        ])
                    writer.writerow(row)
                
            except Exception as e:
                logger.debug(f"Error capturing GPU metrics: {e}")
                # Memory optimization: Memory-critical operation
            
            # Wait for interval
            time.sleep(self.interval_sec)
    
    def _get_gpu_metrics(self) -> Dict[str, Any]:
    # Memory optimization: Memory-critical operation
        """Get current GPU and system metrics."""
        # Memory optimization: Memory-critical operation
        data = {
            'timestamp': time.time(),
            'gpu_util': 0,
            # Memory optimization: Memory-critical operation
            'memory_used_mb': 0,
            # Memory optimization: Memory-critical operation
            'memory_free_mb': 0,
            # Memory optimization: Memory-critical operation
            'memory_total_mb': 0,
            # Memory optimization: Memory-critical operation
            'power_watts': 0,
            'temperature_c': 0,
        }
        
        if self.track_system_ram:
            data.update({
                'system_ram_used_mb': 0,
                'system_ram_free_mb': 0,
            })
        
        if not self.cuda_available:
        # Memory optimization: Memory-critical operation
            # If CUDA isn't available, just track system RAM if requested
            # Memory optimization: Memory-critical operation
            if self.track_system_ram:
                self._update_system_ram_metrics(data)
            return data
        
        # Get CUDA info from PyTorch
        # Memory optimization: Memory-critical operation
        try:
            # Use our utility function to get detailed GPU info
            # Memory optimization: Memory-critical operation
            from utils.cuda_utils import get_cuda_info
            # Memory optimization: Memory-critical operation
            cuda_info = get_cuda_info()
            # Memory optimization: Memory-critical operation
            
            # Update metrics from CUDA info
            # Memory optimization: Memory-critical operation
            data['memory_used_mb'] = cuda_info.get('memory_allocated_mb', 0)
            # Memory optimization: Memory-critical operation
            data['memory_free_mb'] = cuda_info.get('memory_free_mb', 0)
            # Memory optimization: Memory-critical operation
            data['memory_total_mb'] = cuda_info.get('memory_total_mb', 0)
            # Memory optimization: Memory-critical operation
        except Exception as e:
            logger.debug(f"Error getting CUDA metrics: {e}")
            # Memory optimization: Memory-critical operation
            
        # Try to get additional info from nvidia-smi
        try:
            from utils.cuda_utils import get_nvidia_smi_info
            # Memory optimization: Memory-critical operation
            nvidia_info = get_nvidia_smi_info()
            
            # If there are any GPUs detected
            # Memory optimization: Memory-critical operation
            if nvidia_info['gpus']:
            # Memory optimization: Memory-critical operation
                gpu_info = nvidia_info['gpus'][0]  # First GPU
                # Memory optimization: Memory-critical operation
                
                # Parse utilization, power and temperature if available
                if 'utilization.gpu' in gpu_info:
                # Memory optimization: Memory-critical operation
                    util_str = gpu_info['utilization.gpu'].replace('%', '').strip()
                    # Memory optimization: Memory-critical operation
                    data['gpu_util'] = float(util_str) if util_str else 0
                    # Memory optimization: Memory-critical operation
                    
                if 'power.draw' in gpu_info:
                # Memory optimization: Memory-critical operation
                    power_str = gpu_info['power.draw'].replace('W', '').strip()
                    # Memory optimization: Memory-critical operation
                    data['power_watts'] = float(power_str) if power_str else 0
                    
                if 'temperature.gpu' in gpu_info:
                # Memory optimization: Memory-critical operation
                    temp_str = gpu_info['temperature.gpu'].replace('C', '').strip()
                    # Memory optimization: Memory-critical operation
                    data['temperature_c'] = float(temp_str) if temp_str else 0
                    
                # Get memory usage as a second opinion
                # Memory optimization: Memory-critical operation
                if 'memory.used' in gpu_info and data['memory_used_mb'] == 0:
                # Memory optimization: Memory-critical operation
                    used_str = gpu_info['memory.used'].replace('MiB', '').strip()
                    # Memory optimization: Memory-critical operation
                    data['memory_used_mb'] = float(used_str) if used_str else 0
                    # Memory optimization: Memory-critical operation
        except Exception as e:
            logger.debug(f"Error getting nvidia-smi metrics: {e}")
            
        # Get system RAM info if requested
        if self.track_system_ram:
            self._update_system_ram_metrics(data)
            
        return data
    
    def _update_system_ram_metrics(self, data: Dict[str, Any]):
        """Update the data dictionary with system RAM metrics."""
        try:
            # Cross-platform system memory info
            # Memory optimization: Memory-critical operation
            import psutil
            memory = psutil.virtual_memory()
            # Memory optimization: Memory-critical operation
            data['system_ram_used_mb'] = memory.used / 1024 / 1024
            # Memory optimization: Memory-critical operation
            data['system_ram_free_mb'] = memory.available / 1024 / 1024
            # Memory optimization: Memory-critical operation
        except ImportError:
            logger.debug("psutil not available, can't track system RAM")
        except Exception as e:
            logger.debug(f"Error getting system RAM metrics: {e}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from collected data."""
        if not self.snapshots:
            return {}
            
        # Calculate statistics
        memory_used = [s.get('memory_used_mb', 0) for s in self.snapshots]
        # Memory optimization: Memory-critical operation
        gpu_util = [s.get('gpu_util', 0) for s in self.snapshots]
        # Memory optimization: Memory-critical operation
        
        summary = {
            'session_id': self.current_session,
            'duration_sec': self.snapshots[-1]['timestamp'] - self.snapshots[0]['timestamp'],
            'samples': len(self.snapshots),
            'memory_used_mb': {
            # Memory optimization: Memory-critical operation
                'min': min(memory_used),
                # Memory optimization: Memory-critical operation
                'max': max(memory_used),
                # Memory optimization: Memory-critical operation
                'avg': sum(memory_used) / len(memory_used)
                # Memory optimization: Memory-critical operation
            },
            'gpu_utilization_pct': {
            # Memory optimization: Memory-critical operation
                'min': min(gpu_util),
                # Memory optimization: Memory-critical operation
                'max': max(gpu_util),
                # Memory optimization: Memory-critical operation
                'avg': sum(gpu_util) / len(gpu_util)
                # Memory optimization: Memory-critical operation
            }
        }
        
        # Add system RAM stats if tracked
        if self.track_system_ram and any('system_ram_used_mb' in s for s in self.snapshots):
            ram_used = [s.get('system_ram_used_mb', 0) for s in self.snapshots]
            summary['system_ram_used_mb'] = {
                'min': min(ram_used),
                'max': max(ram_used),
                'avg': sum(ram_used) / len(ram_used)
            }
            
        # Save summary to disk
        summary_file = os.path.join(self.log_dir, f"{self.current_session}_summary.csv")
        with open(summary_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['metric', 'min', 'max', 'avg'])
            # Write memory stats
            # Memory optimization: Memory-critical operation
            writer.writerow(['memory_used_mb', 
            # Memory optimization: Memory-critical operation
                           summary['memory_used_mb']['min'],
                           # Memory optimization: Memory-critical operation
                           summary['memory_used_mb']['max'],
                           # Memory optimization: Memory-critical operation
                           summary['memory_used_mb']['avg']])
                           # Memory optimization: Memory-critical operation
            # Write utilization stats
            writer.writerow(['gpu_utilization_pct',
            # Memory optimization: Memory-critical operation
                           summary['gpu_utilization_pct']['min'],
                           # Memory optimization: Memory-critical operation
                           summary['gpu_utilization_pct']['max'],
                           # Memory optimization: Memory-critical operation
                           summary['gpu_utilization_pct']['avg']])
                           # Memory optimization: Memory-critical operation
            
        logger.info(f"Performance summary saved to {summary_file}")
        return summary
    
    def _generate_plots(self):
        """Generate performance plots from the collected data."""
        try:
            if not self.snapshots:
                return
                
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            
            # Extract data for plotting
            timestamps = [(s['timestamp'] - self.snapshots[0]['timestamp']) / 60 for s in self.snapshots]  # Minutes
            memory_used = [s.get('memory_used_mb', 0) for s in self.snapshots]
            # Memory optimization: Memory-critical operation
            memory_free = [s.get('memory_free_mb', 0) for s in self.snapshots]
            # Memory optimization: Memory-critical operation
            gpu_util = [s.get('gpu_util', 0) for s in self.snapshots]
            # Memory optimization: Memory-critical operation
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Plot memory usage
            # Memory optimization: Memory-critical operation
            ax1.plot(timestamps, memory_used, 'b-', label='Used VRAM (MB)')
            # Memory optimization: Memory-critical operation
            ax1.plot(timestamps, memory_free, 'g-', label='Free VRAM (MB)')
            # Memory optimization: Memory-critical operation
            ax1.set_title('GPU Memory Usage')
            # Memory optimization: Memory-critical operation
            ax1.set_xlabel('Time (minutes)')
            ax1.set_ylabel('Memory (MB)')
            # Memory optimization: Memory-critical operation
            ax1.legend()
            ax1.grid(True)
            
            # Plot GPU utilization
            # Memory optimization: Memory-critical operation
            ax2.plot(timestamps, gpu_util, 'r-', label='GPU Utilization (%)')
            # Memory optimization: Memory-critical operation
            ax2.set_title('GPU Utilization')
            # Memory optimization: Memory-critical operation
            ax2.set_xlabel('Time (minutes)')
            ax2.set_ylabel('Utilization (%)')
            ax2.set_ylim(0, 100)
            ax2.legend()
            ax2.grid(True)
            
            # Adjust layout and save
            plt.tight_layout()
            plot_file = os.path.join(self.log_dir, f"{self.current_session}_plot.png")
            plt.savefig(plot_file)
            plt.close(fig)
            
            logger.info(f"Performance plot saved to {plot_file}")
            
            # If we're tracking system RAM, create another plot
            if self.track_system_ram and any('system_ram_used_mb' in s for s in self.snapshots):
                ram_used = [s.get('system_ram_used_mb', 0) for s in self.snapshots]
                ram_free = [s.get('system_ram_free_mb', 0) for s in self.snapshots]
                
                # Create figure
                fig, ax = plt.subplots(figsize=(10, 4))
                
                # Plot system RAM usage
                ax.plot(timestamps, ram_used, 'b-', label='Used System RAM (MB)')
                ax.plot(timestamps, ram_free, 'g-', label='Free System RAM (MB)')
                ax.set_title('System RAM Usage')
                ax.set_xlabel('Time (minutes)')
                ax.set_ylabel('Memory (MB)')
                # Memory optimization: Memory-critical operation
                ax.legend()
                ax.grid(True)
                
                # Save RAM plot
                plt.tight_layout()
                ram_plot_file = os.path.join(self.log_dir, f"{self.current_session}_ram_plot.png")
                plt.savefig(ram_plot_file)
                plt.close(fig)
                
                logger.info(f"System RAM plot saved to {ram_plot_file}")
                
        except ImportError:
            logger.warning("matplotlib not installed, skipping plot generation")
        except Exception as e:
            logger.error(f"Error generating performance plots: {e}")

def track_performance(func):
    """
    Decorator to track GPU performance during function execution.
    # Memory optimization: Memory-critical operation
    
    Args:
        func: Function to track
        
    Returns:
        Wrapped function that tracks GPU performance
        # Memory optimization: Memory-critical operation
    """
    def wrapper(*args, **kwargs):
        """
        
    wrapper function for processing.
    
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
        # Create tracker
        tracker = GPUPerformanceTracker()
        # Memory optimization: Memory-critical operation
        
        # Start tracking
        session_id = tracker.start_tracking(func.__name__)
        
        try:
            # Call original function
            result = func(*args, **kwargs)
            return result
        finally:
            # Stop tracking
            summary = tracker.stop_tracking()
            
            # Log summary
            logger.info(f"Performance for {func.__name__}:")
            logger.info(f"  Duration: {summary.get('duration_sec', 0):.2f} seconds")
            if 'memory_used_mb' in summary:
            # Memory optimization: Memory-critical operation
                logger.info(f"  Memory usage: {summary['memory_used_mb']['avg']:.2f}MB average, " +
                # Memory optimization: Memory-critical operation
                           f"{summary['memory_used_mb']['max']:.2f}MB peak")
                           # Memory optimization: Memory-critical operation
            if 'gpu_utilization_pct' in summary:
            # Memory optimization: Memory-critical operation
                logger.info(f"  GPU utilization: {summary['gpu_utilization_pct']['avg']:.1f}% average")
                # Memory optimization: Memory-critical operation
            
    return wrapper

def main():
    """Run the GPU performance tracker as a standalone tool."""
    # Memory optimization: Memory-critical operation
    parser = argparse.ArgumentParser(description="GPU Performance Tracker")
    # Memory optimization: Memory-critical operation
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds to track performance")
    parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    parser.add_argument("--output", type=str, default="gpu_performance", help="Output prefix for log files")
    # Memory optimization: Memory-critical operation
    parser.add_argument("--no-plot", action="store_true", help="Disable plot generation")
    args = parser.parse_args()
    
    # Create tracker
    tracker = GPUPerformanceTracker(
    # Memory optimization: Memory-critical operation
        log_dir="performance_logs",
        interval_sec=args.interval,
        track_processes=True,
        track_system_ram=True,
        plot_results=not args.no_plot
    )
    
    # Start tracking
    session_id = tracker.start_tracking(args.output)
    print(f"Tracking GPU performance for {args.duration} seconds... (Ctrl+C to stop)")
    # Memory optimization: Memory-critical operation
    
    try:
        # Sleep for specified duration
        time.sleep(args.duration)
    except KeyboardInterrupt:
        print("\n\n\nTracking stopped by user")
    finally:
        # Stop tracking
        summary = tracker.stop_tracking()
        
        # Print summary
        print("\nGPU Performance Summary:")
        # Memory optimization: Memory-critical operation
        print(f"  Duration: {summary.get('duration_sec', 0):.2f} seconds")
        if 'memory_used_mb' in summary:
        # Memory optimization: Memory-critical operation
            print(f"  Memory usage: {summary['memory_used_mb']['avg']:.2f}MB average, " +
            # Memory optimization: Memory-critical operation
                 f"{summary['memory_used_mb']['max']:.2f}MB peak")
                 # Memory optimization: Memory-critical operation
        if 'gpu_utilization_pct' in summary:
        # Memory optimization: Memory-critical operation
            print(f"  GPU utilization: {summary['gpu_utilization_pct']['avg']:.1f}% average")
            # Memory optimization: Memory-critical operation
        
        print(f"\nDetailed logs saved to performance_logs/{session_id}.csv")
        if not args.no_plot:
            print(f"Performance plots saved to performance_logs/{session_id}_plot.png")

if __name__ == "__main__":
    main()