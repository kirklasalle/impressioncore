#!/usr/bin/env python3
"""
ImpressionCore: Gpu Memory Profiler

Module for gpu memory profiler functionality in the ImpressionCore framework.

File: core\utils\gpu_memory_profiler.py
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
This module implements gpu memory profiler functionality for the
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
from core.utils.gpu_memory_profiler import GPUMemoryProfiler
instance = GPUMemoryProfiler()
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
import torch
import time
import threading
from pathlib import Path
import json
import csv
import argparse
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Any, Union, Callable

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.gpu_enforcer import initialize_memlog
# Memory optimization: Memory-critical operation
from utils.cuda_utils import get_cuda_info, get_nvidia_smi_info
# Memory optimization: Memory-critical operation

# Configure logger
logger = logging.getLogger(__name__)

class GPUMemoryProfiler:
# Memory optimization: Memory-critical operation
    """
    Profile GPU memory usage during model training or inference.
    # Memory optimization: Explicit memory cleanup
    
    This class provides utilities to track memory usage over time and
    # Memory optimization: Memory-critical operation
    detect potential issues like memory leaks or inefficient memory usage.
    # Memory optimization: Memory-critical operation
    """
    
    def __init__(
        self, 
        log_dir: Optional[str] = None,
        sampling_interval: float = 0.5,
        record_stack_trace: bool = False,
        track_system_ram: bool = True,
        track_tensors: bool = True,
        plot_results: bool = True,
        enforce_gpu: bool = True
        # Memory optimization: Memory-critical operation
    ):
        """
        Initialize GPU memory profiler.
        # Memory optimization: Memory-critical operation
        
        Args:
            log_dir: Directory to store profiling logs (None for auto-generation)
            sampling_interval: Time in seconds between memory samples
            # Memory optimization: Memory-critical operation
            record_stack_trace: Whether to record stack traces for allocations
            track_system_ram: Whether to track system RAM usage
            track_tensors: Whether to track individual tensors
            plot_results: Whether to generate plots automatically
            enforce_gpu: Whether to enforce GPU usage
            # Memory optimization: Memory-critical operation
        """
        # Initialize memlog
        initialize_memlog()
        
        # Set up log directory
        if log_dir is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.log_dir = project_root / "src" / "memlog" / "profiling" / f"gpu_profile_{timestamp}"
            # Memory optimization: Memory-critical operation
        else:
            self.log_dir = Path(log_dir)
            
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.sampling_interval = sampling_interval
        self.record_stack_trace = record_stack_trace
        self.track_system_ram = track_system_ram
        self.track_tensors = track_tensors
        self.plot_results = plot_results
        
        # State
        self.is_profiling = False
        self.profile_thread = None
        self.stop_event = threading.Event()
        self.snapshots = []
        self.tensor_snapshots = []
        self.profiling_start_time = None
        
        # Enforce GPU if requested
        # Memory optimization: Memory-critical operation
        if enforce_gpu:
        # Memory optimization: Memory-critical operation
            try:
                from utils.gpu_enforcer import enforce_gpu_usage
                # Memory optimization: Memory-critical operation
                enforce_gpu_usage()
                # Memory optimization: Memory-critical operation
            except Exception as e:
                logger.warning(f"Failed to enforce GPU usage: {e}")
                # Memory optimization: Memory-critical operation
        
        # Check CUDA availability
        # Memory optimization: Memory-critical operation
        self.cuda_available = torch.cuda.is_available()
        # Memory optimization: CUDA operations for GPU acceleration
        if not self.cuda_available:
        # Memory optimization: Memory-critical operation
            logger.warning("CUDA not available. Memory profiling will be limited.")
            # Memory optimization: Memory-critical operation
            return
            
        # Get initial device info
        # Memory optimization: Device placement for memory management
        self.device_name = torch.cuda.get_device_name(0)
        # Memory optimization: CUDA operations for GPU acceleration
        self.device_info = torch.cuda.get_device_properties(0)
        # Memory optimization: CUDA operations for GPU acceleration
        
        logger.info(f"GPU Memory Profiler initialized for {self.device_name}")
        # Memory optimization: Device placement for memory management
        logger.info(f"Profiling data will be saved to {self.log_dir}")

    def start_profiling(self, session_name: Optional[str] = None) -> str:
        """
        Start profiling GPU memory usage.
        # Memory optimization: Memory-critical operation
        
        Args:
            session_name: Optional name for the profiling session
            
        Returns:
            Session ID
        """
        if self.is_profiling:
            logger.warning("Profiling already in progress")
            return ""
            
        # Generate session name if not provided
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.session_id = session_name or f"profile_{timestamp}"
        
        # Create log files
        self.memory_log_file = self.log_dir / f"{self.session_id}_memory.csv"
        # Memory optimization: Memory-critical operation
        self.tensor_log_file = self.log_dir / f"{self.session_id}_tensors.csv"
        self.metadata_file = self.log_dir / f"{self.session_id}_metadata.json"
        
        # Write headers to CSV files
        with open(self.memory_log_file, 'w', newline='') as f:
        # Memory optimization: Memory-critical operation
            writer = csv.writer(f)
            header = [
                'timestamp', 'elapsed_seconds', 'allocated_mb', 'reserved_mb',
                'free_mb', 'utilization_pct', 'active_tensors'
            ]
            if self.track_system_ram:
                header.extend(['sys_ram_used_mb', 'sys_ram_free_mb'])
            writer.writerow(header)
        
        if self.track_tensors:
            with open(self.tensor_log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'elapsed_seconds', 'tensor_id', 'size_mb', 'shape', 'dtype'])
        
        # Write metadata
        metadata = {
            'session_id': self.session_id,
            'start_time': timestamp,
            'device_name': self.device_name if self.cuda_available else "CPU",
            # Memory optimization: Device placement for memory management
            'cuda_available': self.cuda_available,
            # Memory optimization: Memory-critical operation
            'sampling_interval': self.sampling_interval,
            'track_system_ram': self.track_system_ram,
            'track_tensors': self.track_tensors,
            'record_stack_trace': self.record_stack_trace,
            'pytorch_version': torch.__version__
        }
        
        if self.cuda_available:
        # Memory optimization: Memory-critical operation
            metadata.update({
                'total_memory_mb': self.device_info.total_memory / (1024**2),
                # Memory optimization: Device placement for memory management
                'compute_capability': f"{self.device_info.major}.{self.device_info.minor}"
                # Memory optimization: Device placement for memory management
            })
            
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Reset state
        self.snapshots = []
        self.tensor_snapshots = []
        self.profiling_start_time = time.time()
        
        # Start profiling thread
        self.is_profiling = True
        self.stop_event.clear()
        # Memory optimization: Memory-critical operation
        self.profile_thread = threading.Thread(
            target=self._profiling_loop,
            daemon=True
        )
        self.profile_thread.start()
        
        logger.info(f"Started GPU memory profiling: {self.session_id}")
        # Memory optimization: Memory-critical operation
        return self.session_id
    
    def stop_profiling(self) -> Dict[str, Any]:
        """
        Stop profiling and return summary statistics.
        
        Returns:
            Dictionary containing profiling summary
        """
        if not self.is_profiling:
            logger.warning("No profiling in progress")
            return {}
            
        # Signal profiling thread to stop
        self.stop_event.set()
        if self.profile_thread is not None:
            self.profile_thread.join(timeout=2.0)
            
        self.is_profiling = False
        profiling_duration = time.time() - self.profiling_start_time
        
        logger.info(f"Stopped GPU memory profiling: {self.session_id}")
        # Memory optimization: Memory-critical operation
        logger.info(f"Profiling duration: {profiling_duration:.2f} seconds")
        logger.info(f"Collected {len(self.snapshots)} memory snapshots")
        # Memory optimization: Memory-critical operation
        
        # Generate summary
        if not self.snapshots:
            return {"error": "No snapshots collected"}
            
        summary = self._generate_summary()
        
        # Write summary to file
        summary_file = self.log_dir / f"{self.session_id}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        # Generate plots if requested
        if self.plot_results:
            self._generate_plots()
            
        return summary
    
    def _profiling_loop(self):
        """Background thread for memory profiling."""
        # Memory optimization: Memory-critical operation
        while not self.stop_event.is_set():
            try:
                # Take memory snapshot
                # Memory optimization: Memory-critical operation
                snapshot = self._take_memory_snapshot()
                # Memory optimization: Memory-critical operation
                self.snapshots.append(snapshot)
                
                # Write snapshot to log file
                with open(self.memory_log_file, 'a', newline='') as f:
                # Memory optimization: Memory-critical operation
                    writer = csv.writer(f)
                    writer.writerow([
                        snapshot['timestamp'],
                        snapshot['elapsed_seconds'],
                        snapshot['allocated_mb'],
                        snapshot['reserved_mb'],
                        snapshot['free_mb'],
                        snapshot['utilization_pct'],
                        snapshot['active_tensors']
                    ] + ([
                        snapshot['sys_ram_used_mb'],
                        snapshot['sys_ram_free_mb']
                    ] if self.track_system_ram and 'sys_ram_used_mb' in snapshot else []))
                
                # Take tensor snapshot if requested
                if self.track_tensors and self.cuda_available:
                # Memory optimization: Memory-critical operation
                    tensor_snapshot = self._take_tensor_snapshot()
                    self.tensor_snapshots.append(tensor_snapshot)
                    
                    # Write tensor snapshot to log file
                    with open(self.tensor_log_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        for tensor_info in tensor_snapshot['tensors']:
                            writer.writerow([
                                tensor_snapshot['timestamp'],
                                tensor_snapshot['elapsed_seconds'],
                                tensor_info['id'],
                                tensor_info['size_mb'],
                                str(tensor_info['shape']),
                                str(tensor_info['dtype'])
                            ])
                
            except Exception as e:
                logger.error(f"Error in profiling loop: {e}")
                
            # Wait for next sample
            self.stop_event.wait(self.sampling_interval)
    
    def _take_memory_snapshot(self) -> Dict[str, Any]:
    # Memory optimization: Memory-critical operation
        """Take a snapshot of current memory usage."""
        # Memory optimization: Memory-critical operation
        snapshot = {
            'timestamp': time.time(),
            'elapsed_seconds': time.time() - self.profiling_start_time,
            'allocated_mb': 0,
            'reserved_mb': 0,
            'free_mb': 0,
            'utilization_pct': 0,
            'active_tensors': 0
        }
        
        # Get CUDA memory info
        # Memory optimization: Memory-critical operation
        if self.cuda_available:
        # Memory optimization: Memory-critical operation
            snapshot['allocated_mb'] = torch.cuda.memory_allocated() / (1024**2)
            # Memory optimization: CUDA operations for GPU acceleration
            snapshot['reserved_mb'] = torch.cuda.memory_reserved() / (1024**2)
            # Memory optimization: CUDA operations for GPU acceleration
            snapshot['free_mb'] = (self.device_info.total_memory / (1024**2)) - snapshot['reserved_mb']
            # Memory optimization: Device placement for memory management
            snapshot['utilization_pct'] = (snapshot['reserved_mb'] / (self.device_info.total_memory / (1024**2))) * 100
            # Memory optimization: Device placement for memory management
            
            # Count active tensors on GPU
            # Memory optimization: Memory-critical operation
            if self.track_tensors:
                active_tensors = 0
                for obj in gc.get_objects():
                    try:
                        if isinstance(obj, torch.Tensor) and obj.is_cuda:
                        # Memory optimization: Memory-critical operation
                            active_tensors += 1
                    except:
                        pass
                snapshot['active_tensors'] = active_tensors
        
        # Get system RAM info if requested
        if self.track_system_ram:
            try:
                import psutil
                memory = psutil.virtual_memory()
                # Memory optimization: Memory-critical operation
                snapshot['sys_ram_used_mb'] = memory.used / (1024**2)
                # Memory optimization: Memory-critical operation
                snapshot['sys_ram_free_mb'] = memory.available / (1024**2)
                # Memory optimization: Memory-critical operation
            except ImportError:
                pass
                
        return snapshot
    
    def _take_tensor_snapshot(self) -> Dict[str, Any]:
        """Take a snapshot of CUDA tensors."""
        # Memory optimization: Memory-critical operation
        import gc
        
        snapshot = {
            'timestamp': time.time(),
            'elapsed_seconds': time.time() - self.profiling_start_time,
            'tensors': []
        }
        
        if not self.cuda_available:
        # Memory optimization: Memory-critical operation
            return snapshot
            
        # Find all CUDA tensors
        # Memory optimization: Memory-critical operation
        for obj in gc.get_objects():
            try:
                if isinstance(obj, torch.Tensor) and obj.is_cuda:
                # Memory optimization: Memory-critical operation
                    tensor_info = {
                        'id': id(obj),
                        'size_mb': obj.element_size() * obj.numel() / (1024**2),
                        'shape': list(obj.shape),
                        'dtype': str(obj.dtype)
                    }
                    
                    # Record stack trace if requested
                    if self.record_stack_trace:
                        try:
                            tensor_info['stack_trace'] = "".join(traceback.format_stack())
                        except:
                            tensor_info['stack_trace'] = "Unavailable"
                            
                    snapshot['tensors'].append(tensor_info)
            except:
                # Skip tensors that can't be safely inspected
                pass
                
        return snapshot
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from profiling data."""
        summary = {
            'session_id': self.session_id,
            'duration_seconds': time.time() - self.profiling_start_time,
            'num_snapshots': len(self.snapshots)
        }
        
        if not self.snapshots:
            return summary
            
        # Calculate memory statistics
        # Memory optimization: Memory-critical operation
        allocated_mb = [s['allocated_mb'] for s in self.snapshots]
        reserved_mb = [s['reserved_mb'] for s in self.snapshots]
        free_mb = [s['free_mb'] for s in self.snapshots]
        utilization_pct = [s['utilization_pct'] for s in self.snapshots]
        
        summary['memory'] = {
        # Memory optimization: Memory-critical operation
            'allocated_mb': {
                'min': min(allocated_mb),
                'max': max(allocated_mb),
                'avg': sum(allocated_mb) / len(allocated_mb)
            },
            'reserved_mb': {
                'min': min(reserved_mb),
                'max': max(reserved_mb),
                'avg': sum(reserved_mb) / len(reserved_mb)
            },
            'free_mb': {
                'min': min(free_mb),
                'max': max(free_mb),
                'avg': sum(free_mb) / len(free_mb)
            },
            'utilization_pct': {
                'min': min(utilization_pct),
                'max': max(utilization_pct),
                'avg': sum(utilization_pct) / len(utilization_pct)
            }
        }
        
        # Calculate tensor statistics
        if self.track_tensors and 'active_tensors' in self.snapshots[0]:
            active_tensors = [s['active_tensors'] for s in self.snapshots]
            summary['tensors'] = {
                'count': {
                    'min': min(active_tensors),
                    'max': max(active_tensors),
                    'avg': sum(active_tensors) / len(active_tensors)
                }
            }
            
        # Calculate system RAM statistics
        if self.track_system_ram and 'sys_ram_used_mb' in self.snapshots[0]:
            ram_used = [s['sys_ram_used_mb'] for s in self.snapshots]
            ram_free = [s['sys_ram_free_mb'] for s in self.snapshots]
            summary['system_ram'] = {
                'used_mb': {
                    'min': min(ram_used),
                    'max': max(ram_used),
                    'avg': sum(ram_used) / len(ram_used)
                },
                'free_mb': {
                    'min': min(ram_free),
                    'max': max(ram_free),
                    'avg': sum(ram_free) / len(ram_free)
                }
            }
            
        return summary
    
    def _generate_plots(self):
        """Generate plots from profiling data."""
        if not self.snapshots or not self.plot_results:
            return
            
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            logger.warning("Matplotlib not available. Skipping plot generation.")
            return
            
        # Extract time data
        elapsed = [s['elapsed_seconds'] for s in self.snapshots]
        
        # Plot memory usage
        # Memory optimization: Memory-critical operation
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Memory (MB)')
        # Memory optimization: Memory-critical operation
        
        ax1.plot(elapsed, [s['allocated_mb'] for s in self.snapshots], 'b-', label='Allocated')
        ax1.plot(elapsed, [s['reserved_mb'] for s in self.snapshots], 'g-', label='Reserved')
        
        if self.cuda_available:
        # Memory optimization: Memory-critical operation
            # Add line for total memory
            # Memory optimization: Memory-critical operation
            total_mb = self.device_info.total_memory / (1024**2)
            # Memory optimization: Device placement for memory management
            ax1.axhline(y=total_mb, color='r', linestyle='--', label=f'Total ({total_mb:.0f} MB)')
        
        ax1.set_title(f'GPU Memory Usage - {self.device_name}')
        # Memory optimization: Device placement for memory management
        ax1.grid(True)
        ax1.legend(loc='upper left')
        
        # Add utilization on secondary axis
        if 'utilization_pct' in self.snapshots[0]:
            ax2 = ax1.twinx()
            ax2.set_ylabel('Utilization (%)')
            ax2.plot(elapsed, [s['utilization_pct'] for s in self.snapshots], 'r.', alpha=0.5, label='Utilization')
            ax2.set_ylim(0, 105)
            ax2.legend(loc='upper right')
            
        # Save the figure
        memory_plot_file = self.log_dir / f"{self.session_id}_memory_plot.png"
        # Memory optimization: Memory-critical operation
        plt.tight_layout()
        plt.savefig(memory_plot_file)
        # Memory optimization: Memory-critical operation
        plt.close(fig)
        
        # Plot tensor count if available
        if self.track_tensors and 'active_tensors' in self.snapshots[0]:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(elapsed, [s['active_tensors'] for s in self.snapshots], 'b.-')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Active CUDA Tensors')
            # Memory optimization: Memory-critical operation
            ax.set_title('Active CUDA Tensor Count')
            # Memory optimization: Memory-critical operation
            ax.grid(True)
            
            # Save the figure
            tensors_plot_file = self.log_dir / f"{self.session_id}_tensors_plot.png"
            plt.tight_layout()
            plt.savefig(tensors_plot_file)
            plt.close(fig)
            
        # Plot system RAM if tracked
        if self.track_system_ram and 'sys_ram_used_mb' in self.snapshots[0]:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(elapsed, [s['sys_ram_used_mb'] for s in self.snapshots], 'g-', label='Used')
            ax.plot(elapsed, [s['sys_ram_free_mb'] for s in self.snapshots], 'b-', label='Free')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('System RAM (MB)')
            ax.set_title('System RAM Usage')
            ax.grid(True)
            ax.legend()
            
            # Save the figure
            ram_plot_file = self.log_dir / f"{self.session_id}_ram_plot.png"
            plt.tight_layout()
            plt.savefig(ram_plot_file)
            plt.close(fig)
        
        logger.info(f"Generated profiling plots in {self.log_dir}")

def profile_function(log_dir: Optional[str] = None, sampling_interval: float = 0.1):
    """
    Decorator to profile GPU memory usage during function execution.
    # Memory optimization: Memory-critical operation
    
    Args:
        log_dir: Directory to store profiling logs
        sampling_interval: Time in seconds between memory samples
        # Memory optimization: Memory-critical operation
        
    Returns:
        Decorated function
    """
    def decorator(func):
        """
        
    decorator function for processing.
    
    Args:
        func: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
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
            # Initialize profiler
            profiler = GPUMemoryProfiler(
            # Memory optimization: Memory-critical operation
                log_dir=log_dir,
                sampling_interval=sampling_interval
            )
            
            # Start profiling
            profiler.start_profiling(func.__name__)
            
            try:
                # Call original function
                result = func(*args, **kwargs)
                return result
            finally:
                # Stop profiling
                summary = profiler.stop_profiling()
                
                # Log summary
                logger.info(f"Memory usage for {func.__name__}:")
                # Memory optimization: Memory-critical operation
                if 'memory' in summary:
                # Memory optimization: Memory-critical operation
                    mem = summary['memory']
                    # Memory optimization: Memory-critical operation
                    logger.info(f"  Allocated: {mem['allocated_mb']['max']:.2f}MB max, {mem['allocated_mb']['avg']:.2f}MB avg")
                    logger.info(f"  Utilization: {mem['utilization_pct']['max']:.1f}% max, {mem['utilization_pct']['avg']:.1f}% avg")
        return wrapper
    return decorator

def main():
    """Command line tool for GPU memory profiling."""
    # Memory optimization: Memory-critical operation
    parser = argparse.ArgumentParser(description="Profile GPU memory usage")
    # Memory optimization: Memory-critical operation
    parser.add_argument("--interval", type=float, default=0.5, 
                     help="Sampling interval in seconds")
    parser.add_argument("--duration", type=float, default=60.0, 
                     help="Profiling duration in seconds")
    parser.add_argument("--no-plot", action="store_true",
                     help="Disable plot generation")
    parser.add_argument("--test", action="store_true",
                     help="Run memory test during profiling")
                     # Memory optimization: Memory-critical operation
    parser.add_argument("--log-dir", type=str, default=None,
                     help="Directory to store profiling logs")
    parser.add_argument("--command", type=str, default=None, 
                     help="Shell command to profile")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Create profiler
    profiler = GPUMemoryProfiler(
    # Memory optimization: Memory-critical operation
        log_dir=args.log_dir,
        sampling_interval=args.interval,
        plot_results=not args.no_plot
    )
    
    # Start profiling
    session_id = profiler.start_profiling()
    
    try:
        if args.command:
            # Profile external command
            logger.info(f"Profiling command: {args.command}")
            import subprocess
            process = subprocess.Popen(args.command, shell=True)
            process.wait()
        elif args.test:
            # Run memory test
            # Memory optimization: Memory-critical operation
            logger.info("Running memory test...")
            # Memory optimization: Memory-critical operation
            run_memory_test(duration=args.duration)
            # Memory optimization: Memory-critical operation
        else:
            # Just profile for specified duration
            logger.info(f"Profiling for {args.duration} seconds...")
            time.sleep(args.duration)
    
    except KeyboardInterrupt:
        logger.info("Profiling interrupted by user")
    finally:
        # Stop profiling
        summary = profiler.stop_profiling()
        
        # Print summary
        if 'memory' in summary:
        # Memory optimization: Memory-critical operation
            mem = summary['memory']
            # Memory optimization: Memory-critical operation
            print("\n#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src\core\utils\gpu_memory_profiler.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [core, utils]
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
\n\nGPU Memory Usage Summary:")
            # Memory optimization: Memory-critical operation
            print(f"  Allocated: {mem['allocated_mb']['max']:.2f}MB max, {mem['allocated_mb']['avg']:.2f}MB avg")
            print(f"  Reserved:  {mem['reserved_mb']['max']:.2f}MB max, {mem['reserved_mb']['avg']:.2f}MB avg")
            print(f"  Free:      {mem['free_mb']['min']:.2f}MB min, {mem['free_mb']['avg']:.2f}MB avg")
            print(f"  Utilization: {mem['utilization_pct']['max']:.1f}% max, {mem['utilization_pct']['avg']:.1f}% avg")
        
        if 'tensors' in summary:
            tensors = summary['tensors']['count']
            print(f"  Tensor count: {tensors['max']} max, {tensors['avg']:.1f} avg")
        
        print(f"\nDetailed logs saved to {profiler.log_dir}")

def run_memory_test(duration: float = 10.0, device: Optional[torch.device] = None):
# Memory optimization: Device placement for memory management
    """
    Run a memory test to demonstrate GPU memory allocation patterns.
    # Memory optimization: Memory-critical operation
    
    Args:
        duration: Duration of test in seconds
        device: PyTorch device to use (defaults to CUDA if available)
        # Memory optimization: Device placement for memory management
    """
    import gc
    
    # Determine device
    # Memory optimization: Device placement for memory management
    if device is None:
    # Memory optimization: Device placement for memory management
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        # Memory optimization: CUDA operations for GPU acceleration
    
    if device.type != "cuda":
    # Memory optimization: Device placement for memory management
        logger.warning("Memory test requires CUDA device. Using CPU instead.")
        # Memory optimization: Device placement for memory management
    
    logger.info(f"Running memory test on {device} for {duration:.1f} seconds")
    # Memory optimization: Device placement for memory management
    
    # Start time
    start_time = time.time()
    end_time = start_time + duration
    
    # Keep track of tensors to prevent garbage collection
    tensors = []
    
    # Different sizes to allocate
    sizes = [
        (1000, 100),    # Small: ~0.4MB
        (2000, 500),    # Medium: ~4MB
        (3000, 1000),   # Large: ~12MB
        (5000, 2000),   # XLarge: ~40MB
    ]
    
    # Run until duration is reached
    step = 0
    while time.time() < end_time:
        step += 1
        
        # Alternate between allocation and deallocation
        if step % 5 == 0:
            # Free some tensors
            if tensors:
                num_to_free = max(1, len(tensors) // 3)
                logger.info(f"Step {step}: Freeing {num_to_free} tensors")
                for _ in range(num_to_free):
                    if tensors:
                        tensors.pop(0)  # Remove oldest tensor
                
                # Force garbage collection
                gc.collect()
                # Memory optimization: Force garbage collection
                if device.type == "cuda":
                # Memory optimization: Device placement for memory management
                    torch.cuda.empty_cache()
                    # Memory optimization: CUDA operations for GPU acceleration
        else:
            # Create a new tensor
            size_idx = step % len(sizes)
            rows, cols = sizes[size_idx]
            
            # Create tensor on device
            # Memory optimization: Device placement for memory management
            tensor = torch.randn(rows, cols, device=device)
            # Memory optimization: Device placement for memory management
            size_mb = tensor.element_size() * tensor.numel() / 1024**2
            
            # Keep reference to prevent garbage collection
            tensors.append(tensor)
            
            logger.info(f"Step {step}: Allocated tensor of shape {rows}x{cols} ({size_mb:.2f}MB)")
            
        # Log memory stats
        # Memory optimization: Memory-critical operation
        if device.type == "cuda":
        # Memory optimization: Device placement for memory management
            allocated = torch.cuda.memory_allocated() / 1024**2
            # Memory optimization: CUDA operations for GPU acceleration
            reserved = torch.cuda.memory_reserved() / 1024**2
            # Memory optimization: CUDA operations for GPU acceleration
            logger.info(f"CUDA memory: {allocated:.1f}MB allocated, {reserved:.1f}MB reserved")
            # Memory optimization: Memory-critical operation
        
        # Sleep briefly
        time.sleep(0.5)
    
    # Clean up
    tensors.clear()
    # Memory optimization: Memory-critical operation
    gc.collect()
    # Memory optimization: Force garbage collection
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        torch.cuda.empty_cache()
        # Memory optimization: CUDA operations for GPU acceleration
    
    logger.info("Memory test completed")
    # Memory optimization: Memory-critical operation

if __name__ == "__main__":
    # Import gc here as it's used within the script
    import gc
    main()