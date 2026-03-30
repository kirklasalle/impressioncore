#!/usr/bin/env python3
"""
ImpressionCore: Priority 6B - Pipeline Parallelism System

Advanced pipeline parallelism for 256k context window processing
with GPU-CPU coordination and async operation management.

File: src/core/pipeline/parallel_processor.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-30
Modified: 2025-05-30
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle <kirk@impressioncore.ai>

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pipeline-parallelism, async, gpu-cpu, performance-critical, 2025]
Dependencies: [torch, asyncio, threading, queue, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM) with CPU fallback

Description:
Advanced pipeline parallelism system for ultra-efficient 256k context processing:
- Async GPU-CPU coordination
- Overlapped computation and data transfer
- Dynamic workload balancing
- Memory-aware task scheduling
- Real-time performance monitoring
"""

import torch
import torch.nn as nn
import asyncio
import threading
import queue
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future
import multiprocessing as mp
from collections import deque
import psutil
import weakref

# Import rich logging if available
try:
    from src.core.utils.rich_logging import get_rich_logger
    logger = get_rich_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

# Import memory manager
try:
    from src.core.memory_manager.ultra_efficient_manager import (
        UltraEfficientMemoryManager,
        MemoryPoolType
    )
except ImportError:
    logger.warning("Ultra-efficient memory manager not found")
    UltraEfficientMemoryManager = None


class ProcessingUnit(Enum):
    """Available processing units for pipeline operations."""
    GPU = "gpu"
    CPU = "cpu"
    HYBRID = "hybrid"


class TaskPriority(Enum):
    """Task priority levels for scheduling."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineTask:
    """Individual task in the processing pipeline."""
    task_id: str
    operation: Callable
    inputs: Tuple[Any, ...]
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    preferred_unit: ProcessingUnit = ProcessingUnit.GPU
    memory_requirement: int = 0  # in bytes
    estimated_time: float = 0.0  # in seconds
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def execution_time(self) -> Optional[float]:
        """Get task execution time."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class PipelineStats:
    """Statistics tracking for pipeline performance."""
    
    def __init__(self):
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_execution_time = 0.0
        self.gpu_utilization_history = deque(maxlen=100)
        self.cpu_utilization_history = deque(maxlen=100)
        self.memory_usage_history = deque(maxlen=100)
        self.throughput_history = deque(maxlen=100)
        self._lock = threading.Lock()
    
    def update_task_completion(self, task: PipelineTask):
        """Update stats when a task completes."""
        with self._lock:
            if task.status == TaskStatus.COMPLETED:
                self.tasks_completed += 1
                if task.execution_time:
                    self.total_execution_time += task.execution_time
            elif task.status == TaskStatus.FAILED:
                self.tasks_failed += 1
    
    def record_system_metrics(self):
        """Record current system utilization metrics."""
        with self._lock:
            # CPU utilization
            cpu_percent = psutil.cpu_percent()
            self.cpu_utilization_history.append(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage_history.append(memory.percent)
            
            # GPU utilization (if available)
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
                self.gpu_utilization_history.append(gpu_memory * 100)
            
            # Calculate throughput (tasks per second)
            current_time = time.time()
            if hasattr(self, '_last_throughput_time'):
                time_delta = current_time - self._last_throughput_time
                if time_delta > 0:
                    throughput = self.tasks_completed / time_delta
                    self.throughput_history.append(throughput)
            
            self._last_throughput_time = current_time
    
    def get_average_metrics(self) -> Dict[str, float]:
        """Get average performance metrics."""
        with self._lock:
            return {
                "avg_cpu_utilization": sum(self.cpu_utilization_history) / max(len(self.cpu_utilization_history), 1),
                "avg_gpu_utilization": sum(self.gpu_utilization_history) / max(len(self.gpu_utilization_history), 1),
                "avg_memory_usage": sum(self.memory_usage_history) / max(len(self.memory_usage_history), 1),
                "avg_throughput": sum(self.throughput_history) / max(len(self.throughput_history), 1),
                "success_rate": self.tasks_completed / max(self.tasks_completed + self.tasks_failed, 1),
                "total_tasks": self.tasks_completed + self.tasks_failed
            }


class AdaptiveScheduler:
    """
    Adaptive task scheduler for optimal resource utilization.
    
    Dynamically balances workload between GPU and CPU based on:
    - Current system utilization
    - Task requirements and priorities
    - Historical performance data
    """
    
    def __init__(self, max_gpu_memory: float = 3.8):
        """Initialize adaptive scheduler."""
        self.max_gpu_memory_gb = max_gpu_memory
        self.gpu_queue = queue.PriorityQueue()
        self.cpu_queue = queue.PriorityQueue()
        self.pending_tasks: Dict[str, PipelineTask] = {}
        self.running_tasks: Dict[str, PipelineTask] = {}
        self.completed_tasks: Dict[str, PipelineTask] = {}
        self.stats = PipelineStats()
        self._lock = threading.Lock()
        
        # Resource monitoring
        self.current_gpu_memory = 0.0
        self.current_cpu_load = 0.0
        
        logger.info(f"Initialized adaptive scheduler (max GPU memory: {max_gpu_memory}GB)")
    
    def submit_task(self, task: PipelineTask) -> str:
        """
        Submit a task for execution.
        
        Args:
            task: Pipeline task to execute
            
        Returns:
            Task ID for tracking
        """
        with self._lock:
            # Check dependencies
            if not self._dependencies_satisfied(task):
                self.pending_tasks[task.task_id] = task
                logger.debug(f"Task {task.task_id} pending dependencies")
                return task.task_id
            
            # Determine optimal processing unit
            optimal_unit = self._select_processing_unit(task)
            
            # Add to appropriate queue
            priority_value = -task.priority.value  # Negative for priority queue ordering
            
            if optimal_unit == ProcessingUnit.GPU:
                self.gpu_queue.put((priority_value, time.time(), task))
                logger.debug(f"Queued task {task.task_id} for GPU processing")
            else:
                self.cpu_queue.put((priority_value, time.time(), task))
                logger.debug(f"Queued task {task.task_id} for CPU processing")
            
            return task.task_id
    
    def get_next_gpu_task(self) -> Optional[PipelineTask]:
        """Get next task for GPU processing."""
        try:
            _, _, task = self.gpu_queue.get_nowait()
            with self._lock:
                self.running_tasks[task.task_id] = task
                task.status = TaskStatus.RUNNING
                task.start_time = time.time()
            return task
        except queue.Empty:
            return None
    
    def get_next_cpu_task(self) -> Optional[PipelineTask]:
        """Get next task for CPU processing."""
        try:
            _, _, task = self.cpu_queue.get_nowait()
            with self._lock:
                self.running_tasks[task.task_id] = task
                task.status = TaskStatus.RUNNING
                task.start_time = time.time()
            return task
        except queue.Empty:
            return None
    
    def complete_task(self, task_id: str, result: Any = None, error: Optional[Exception] = None):
        """Mark a task as completed."""
        with self._lock:
            if task_id in self.running_tasks:
                task = self.running_tasks.pop(task_id)
                task.end_time = time.time()
                
                if error:
                    task.status = TaskStatus.FAILED
                    task.error = error
                    logger.error(f"Task {task_id} failed: {error}")
                else:
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    logger.debug(f"Task {task_id} completed in {task.execution_time:.3f}s")
                
                self.completed_tasks[task_id] = task
                self.stats.update_task_completion(task)
                
                # Check for dependent tasks
                self._check_dependent_tasks(task_id)
    
    def _dependencies_satisfied(self, task: PipelineTask) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
            if self.completed_tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _select_processing_unit(self, task: PipelineTask) -> ProcessingUnit:
        """Select optimal processing unit for a task."""
        # Check memory requirements
        gpu_memory_available = self.max_gpu_memory_gb - self.current_gpu_memory
        task_memory_gb = task.memory_requirement / (1024**3)
        
        # If task requires more memory than available, use CPU
        if task_memory_gb > gpu_memory_available:
            return ProcessingUnit.CPU
        
        # Check current utilization
        if self.current_cpu_load < 50 and task.preferred_unit == ProcessingUnit.CPU:
            return ProcessingUnit.CPU
        
        # Default to GPU for compute-intensive tasks
        if torch.cuda.is_available():
            return ProcessingUnit.GPU
        else:
            return ProcessingUnit.CPU
    
    def _check_dependent_tasks(self, completed_task_id: str):
        """Check and submit dependent tasks that are now ready."""
        ready_tasks = []
        
        for task_id, task in list(self.pending_tasks.items()):
            if completed_task_id in task.dependencies:
                if self._dependencies_satisfied(task):
                    ready_tasks.append(task)
                    del self.pending_tasks[task_id]
        
        # Submit ready tasks
        for task in ready_tasks:
            self.submit_task(task)
    
    def get_queue_sizes(self) -> Dict[str, int]:
        """Get current queue sizes."""
        return {
            "gpu_queue": self.gpu_queue.qsize(),
            "cpu_queue": self.cpu_queue.qsize(),
            "pending_tasks": len(self.pending_tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks)
        }


class GPUWorker:
    """GPU worker for processing GPU-bound tasks."""
    
    def __init__(self, device: torch.device, scheduler: AdaptiveScheduler):
        """Initialize GPU worker."""
        self.device = device
        self.scheduler = scheduler
        self.running = True
        self.worker_thread = None
        
        # Memory management integration
        if UltraEfficientMemoryManager is not None:
            self.memory_manager = UltraEfficientMemoryManager(device=device)
        else:
            self.memory_manager = None
    
    def start(self):
        """Start the GPU worker thread."""
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info(f"Started GPU worker on {self.device}")
    
    def stop(self):
        """Stop the GPU worker thread."""
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
        logger.info("Stopped GPU worker")
    
    def _worker_loop(self):
        """Main worker loop for GPU processing."""
        while self.running:
            try:
                # Get next task
                task = self.scheduler.get_next_gpu_task()
                
                if task is None:
                    time.sleep(0.01)  # Brief sleep if no tasks
                    continue
                
                # Execute task
                try:
                    # Move inputs to GPU if needed
                    gpu_inputs = self._move_to_gpu(task.inputs)
                    gpu_kwargs = self._move_to_gpu(task.kwargs)
                    
                    # Execute operation
                    with torch.cuda.device(self.device):
                        result = task.operation(*gpu_inputs, **gpu_kwargs)
                    
                    # Move result back to CPU if needed
                    cpu_result = self._move_to_cpu(result)
                    
                    self.scheduler.complete_task(task.task_id, cpu_result)
                    
                except Exception as e:
                    logger.error(f"GPU task {task.task_id} failed: {e}")
                    self.scheduler.complete_task(task.task_id, error=e)
                
            except Exception as e:
                logger.error(f"GPU worker error: {e}")
                time.sleep(0.1)
    
    def _move_to_gpu(self, obj):
        """Move tensors to GPU recursively."""
        if isinstance(obj, torch.Tensor):
            return obj.to(self.device, non_blocking=True)
        elif isinstance(obj, (list, tuple)):
            return type(obj)(self._move_to_gpu(item) for item in obj)
        elif isinstance(obj, dict):
            return {key: self._move_to_gpu(value) for key, value in obj.items()}
        else:
            return obj
    
    def _move_to_cpu(self, obj):
        """Move tensors to CPU recursively."""
        if isinstance(obj, torch.Tensor):
            return obj.cpu()
        elif isinstance(obj, (list, tuple)):
            return type(obj)(self._move_to_cpu(item) for item in obj)
        elif isinstance(obj, dict):
            return {key: self._move_to_cpu(value) for key, value in obj.items()}
        else:
            return obj


class CPUWorker:
    """CPU worker for processing CPU-bound tasks."""
    
    def __init__(self, scheduler: AdaptiveScheduler, num_workers: int = None):
        """Initialize CPU worker pool."""
        self.scheduler = scheduler
        self.num_workers = num_workers or min(4, mp.cpu_count())
        self.executor = ThreadPoolExecutor(max_workers=self.num_workers)
        self.running = True
        self.worker_thread = None
    
    def start(self):
        """Start the CPU worker."""
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info(f"Started CPU worker pool with {self.num_workers} workers")
    
    def stop(self):
        """Stop the CPU worker."""
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
        self.executor.shutdown(wait=True)
        logger.info("Stopped CPU worker pool")
    
    def _worker_loop(self):
        """Main worker loop for CPU processing."""
        pending_futures: Dict[Future, str] = {}
        
        while self.running:
            try:
                # Submit new tasks
                task = self.scheduler.get_next_cpu_task()
                if task:
                    future = self.executor.submit(self._execute_task, task)
                    pending_futures[future] = task.task_id
                
                # Check completed futures
                completed_futures = [f for f in pending_futures.keys() if f.done()]
                
                for future in completed_futures:
                    task_id = pending_futures.pop(future)
                    
                    try:
                        result = future.result()
                        self.scheduler.complete_task(task_id, result)
                    except Exception as e:
                        self.scheduler.complete_task(task_id, error=e)
                
                time.sleep(0.01)  # Brief sleep
                
            except Exception as e:
                logger.error(f"CPU worker error: {e}")
                time.sleep(0.1)
    
    def _execute_task(self, task: PipelineTask):
        """Execute a CPU task."""
        return task.operation(*task.inputs, **task.kwargs)


class PipelineParallelProcessor:
    """
    Main pipeline parallel processor.
    
    Coordinates GPU and CPU workers for optimal 256k context processing
    with automatic load balancing and error recovery.
    """
    
    def __init__(self, device: Optional[torch.device] = None, max_gpu_memory: float = 3.8):
        """Initialize pipeline parallel processor."""
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scheduler = AdaptiveScheduler(max_gpu_memory=max_gpu_memory)
        
        # Initialize workers
        if self.device.type == "cuda":
            self.gpu_worker = GPUWorker(self.device, self.scheduler)
        else:
            self.gpu_worker = None
        
        self.cpu_worker = CPUWorker(self.scheduler)
        
        # Performance monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        
        logger.info(f"Initialized pipeline parallel processor on {self.device}")
    
    def start(self):
        """Start the pipeline processor."""
        if self.gpu_worker:
            self.gpu_worker.start()
        
        self.cpu_worker.start()
        
        # Start monitoring
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Pipeline parallel processor started")
    
    def stop(self):
        """Stop the pipeline processor."""
        if self.gpu_worker:
            self.gpu_worker.stop()
        
        self.cpu_worker.stop()
        
        # Stop monitoring
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("Pipeline parallel processor stopped")
    
    def submit_task(
        self,
        operation: Callable,
        *args,
        task_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        preferred_unit: ProcessingUnit = ProcessingUnit.GPU,
        memory_requirement: int = 0,
        dependencies: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Submit a task for parallel processing.
        
        Args:
            operation: Function to execute
            *args: Positional arguments for operation
            task_id: Optional task identifier
            priority: Task priority level
            preferred_unit: Preferred processing unit
            memory_requirement: Memory requirement in bytes
            dependencies: List of dependent task IDs
            **kwargs: Keyword arguments for operation
            
        Returns:
            Task ID for tracking
        """
        if task_id is None:
            task_id = f"task_{int(time.time() * 1000000)}"
        
        task = PipelineTask(
            task_id=task_id,
            operation=operation,
            inputs=args,
            kwargs=kwargs,
            priority=priority,
            preferred_unit=preferred_unit,
            memory_requirement=memory_requirement,
            dependencies=dependencies or []
        )
        
        return self.scheduler.submit_task(task)
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        Get the result of a completed task.
        
        Args:
            task_id: Task identifier
            timeout: Maximum time to wait for completion
            
        Returns:
            Task result
            
        Raises:
            TimeoutError: If task doesn't complete within timeout
            Exception: If task failed
        """
        start_time = time.time()
        
        while True:
            with self.scheduler._lock:
                if task_id in self.scheduler.completed_tasks:
                    task = self.scheduler.completed_tasks[task_id]
                    
                    if task.status == TaskStatus.FAILED:
                        raise task.error
                    
                    return task.result
            
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")
            
            time.sleep(0.01)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics."""
        queue_sizes = self.scheduler.get_queue_sizes()
        performance_metrics = self.scheduler.stats.get_average_metrics()
        
        return {
            "queue_sizes": queue_sizes,
            "performance_metrics": performance_metrics,
            "device": str(self.device),
            "workers_active": {
                "gpu": self.gpu_worker is not None,
                "cpu": True
            }
        }
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                self.scheduler.stats.record_system_metrics()
                time.sleep(1.0)  # Record metrics every second
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(5.0)
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# Example usage functions
def example_gpu_operation(tensor: torch.Tensor, weight: torch.Tensor) -> torch.Tensor:
    """Example GPU-bound operation."""
    return torch.matmul(tensor, weight)

def example_cpu_operation(data: List[int]) -> List[int]:
    """Example CPU-bound operation."""
    return [x * 2 for x in data]


# Example usage and testing
if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print(f"Testing pipeline parallel processor on {device}")
    
    with PipelineParallelProcessor(device=device) as processor:
        # Submit test tasks
        gpu_task_id = processor.submit_task(
            example_gpu_operation,
            torch.randn(1000, 1000),
            torch.randn(1000, 1000),
            task_id="gpu_test",
            preferred_unit=ProcessingUnit.GPU
        )
        
        cpu_task_id = processor.submit_task(
            example_cpu_operation,
            list(range(10000)),
            task_id="cpu_test",
            preferred_unit=ProcessingUnit.CPU
        )
        
        # Get results
        try:
            gpu_result = processor.get_result(gpu_task_id, timeout=10.0)
            cpu_result = processor.get_result(cpu_task_id, timeout=10.0)
            
            print(f"GPU result shape: {gpu_result.shape}")
            print(f"CPU result length: {len(cpu_result)}")
            
        except Exception as e:
            print(f"Error getting results: {e}")
        
        # Show stats
        stats = processor.get_stats()
        print(f"Pipeline stats: {stats}")
        
        time.sleep(2)  # Let monitoring collect some data
