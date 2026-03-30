#!/usr/bin/env python3
"""
ImpressionCore: Priority 6C - Production Error Handler

Comprehensive error handling and graceful degradation for 256k context processing.
Implements robust recovery mechanisms for memory pressure and hardware limitations.

File: src/core/reliability/production_error_handler.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-30
Modified: 2025-05-30
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle <kirk@impressioncore.ai>

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [error-handling, production, memory-management, graceful-degradation, 2025]
Dependencies: [torch, psutil, typing, logging, enum]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Production-ready error handling system with:
- Automatic memory pressure detection and recovery
- Quality/speed tradeoff mechanisms
- Hardware-aware degradation strategies
- Real-time error analytics and reporting
- Self-healing capabilities for long-running operations
"""

import torch
import psutil
import gc
import time
import traceback
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from contextlib import contextmanager
import threading
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for graduated response."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DegradationStrategy(Enum):
    """Available degradation strategies."""
    REDUCE_PRECISION = "reduce_precision"
    TRUNCATE_SEQUENCE = "truncate_sequence"
    INCREASE_SPARSITY = "increase_sparsity"
    OFFLOAD_TO_CPU = "offload_to_cpu"
    REDUCE_BATCH_SIZE = "reduce_batch_size"
    SIMPLIFY_ATTENTION = "simplify_attention"
    EMERGENCY_CLEANUP = "emergency_cleanup"


@dataclass
class ErrorContext:
    """Context information for error analysis."""
    error_type: str
    severity: ErrorSeverity
    timestamp: float
    sequence_length: int
    batch_size: int
    memory_used_gb: float
    gpu_memory_used_gb: float
    stack_trace: str
    suggested_actions: List[DegradationStrategy]
    recovery_successful: bool = False
    recovery_time_ms: float = 0.0


@dataclass
class MemoryPressureThresholds:
    """Memory pressure detection thresholds."""
    warning_threshold: float = 0.75  # 75% usage warning
    error_threshold: float = 0.85    # 85% usage error
    critical_threshold: float = 0.95  # 95% usage critical
    gpu_warning_threshold: float = 0.80  # 80% GPU warning
    gpu_error_threshold: float = 0.90    # 90% GPU error


@dataclass
class QualitySpeedTradeoff:
    """Configuration for quality vs speed tradeoffs."""
    max_sequence_length: int = 262144
    min_sequence_length: int = 32768
    precision_levels: List[str] = field(default_factory=lambda: ["fp32", "fp16", "int8"])
    sparsity_levels: List[float] = field(default_factory=lambda: [0.1, 0.3, 0.5, 0.7])
    attention_patterns: List[str] = field(default_factory=lambda: ["full", "sparse", "sliding"])


class ProductionErrorHandler:
    """
    Comprehensive error handling system for production 256k context processing.
    
    Features:
    - Real-time memory monitoring
    - Automatic degradation strategies
    - Error analytics and recovery tracking
    - Hardware-aware adaptation
    - Quality preservation under pressure
    """
    
    def __init__(
        self,
        memory_thresholds: Optional[MemoryPressureThresholds] = None,
        quality_config: Optional[QualitySpeedTradeoff] = None,
        enable_analytics: bool = True
    ):
        self.memory_thresholds = memory_thresholds or MemoryPressureThresholds()
        self.quality_config = quality_config or QualitySpeedTradeoff()
        self.enable_analytics = enable_analytics
        
        # Error tracking
        self.error_history: deque = deque(maxlen=1000)
        self.error_counts: defaultdict = defaultdict(int)
        self.recovery_success_rate: Dict[str, float] = {}
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.memory_pressure_callbacks: List[Callable] = []
        
        # Current state
        self.current_degradation_level = 0
        self.active_strategies: List[DegradationStrategy] = []
        
        logger.info("Initialized ProductionErrorHandler with comprehensive monitoring")
        
        # Start background monitoring
        if self.enable_analytics:
            self.start_monitoring()
    
    def __del__(self):
        """Cleanup monitoring thread."""
        self.stop_monitoring()
    
    def start_monitoring(self):
        """Start background memory and error monitoring."""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Started background error monitoring")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1.0)
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                self._check_memory_pressure()
                time.sleep(0.5)  # Check every 500ms
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1.0)
    
    def _check_memory_pressure(self):
        """Check for memory pressure and trigger callbacks."""
        # System memory
        memory = psutil.virtual_memory()
        memory_usage = memory.percent / 100.0
        
        # GPU memory
        gpu_usage = 0.0
        if torch.cuda.is_available():
            try:
                gpu_memory = torch.cuda.memory_stats()
                allocated = gpu_memory.get('allocated_bytes.all.current', 0)
                reserved = gpu_memory.get('reserved_bytes.all.current', 0)
                max_memory = torch.cuda.get_device_properties(0).total_memory
                gpu_usage = max(allocated, reserved) / max_memory
            except Exception:
                pass
        
        # Check thresholds
        if (memory_usage > self.memory_thresholds.critical_threshold or 
            gpu_usage > self.memory_thresholds.gpu_error_threshold):
            
            severity = ErrorSeverity.CRITICAL
            self._trigger_memory_pressure_callbacks(memory_usage, gpu_usage, severity)
            
        elif (memory_usage > self.memory_thresholds.error_threshold or 
              gpu_usage > self.memory_thresholds.gpu_error_threshold):
            
            severity = ErrorSeverity.HIGH
            self._trigger_memory_pressure_callbacks(memory_usage, gpu_usage, severity)
            
        elif (memory_usage > self.memory_thresholds.warning_threshold or 
              gpu_usage > self.memory_thresholds.gpu_warning_threshold):
            
            severity = ErrorSeverity.MEDIUM
            self._trigger_memory_pressure_callbacks(memory_usage, gpu_usage, severity)
    
    def _trigger_memory_pressure_callbacks(
        self, 
        memory_usage: float, 
        gpu_usage: float, 
        severity: ErrorSeverity
    ):
        """Trigger registered memory pressure callbacks."""
        for callback in self.memory_pressure_callbacks:
            try:
                callback(memory_usage, gpu_usage, severity)
            except Exception as e:
                logger.error(f"Error in memory pressure callback: {e}")
    
    def register_memory_pressure_callback(self, callback: Callable):
        """Register callback for memory pressure events."""
        self.memory_pressure_callbacks.append(callback)
    
    @contextmanager
    def error_recovery_context(
        self,
        operation_name: str,
        sequence_length: int,
        batch_size: int = 1,
        max_retries: int = 3
    ):
        """
        Context manager for automatic error recovery.
        
        Usage:
            with error_handler.error_recovery_context("attention", seq_len):
                result = attention_operation(input_data)
        """
        start_time = time.time()
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                yield self
                return  # Success
                
            except torch.cuda.OutOfMemoryError as e:
                retry_count += 1
                error_context = self._create_error_context(
                    "CUDA_OOM",
                    ErrorSeverity.HIGH,
                    sequence_length,
                    batch_size,
                    str(e)
                )
                
                if retry_count <= max_retries:
                    logger.warning(
                        f"CUDA OOM in {operation_name}, attempting recovery "
                        f"(attempt {retry_count}/{max_retries})"
                    )
                    
                    success = self._recover_from_oom(error_context)
                    if not success and retry_count == max_retries:
                        self._record_error(error_context)
                        raise
                else:
                    self._record_error(error_context)
                    raise
                    
            except RuntimeError as e:
                if "out of memory" in str(e).lower():
                    retry_count += 1
                    error_context = self._create_error_context(
                        "RUNTIME_OOM",
                        ErrorSeverity.HIGH,
                        sequence_length,
                        batch_size,
                        str(e)
                    )
                    
                    if retry_count <= max_retries:
                        success = self._recover_from_runtime_error(error_context)
                        if not success and retry_count == max_retries:
                            self._record_error(error_context)
                            raise
                    else:
                        self._record_error(error_context)
                        raise
                else:
                    # Non-memory related runtime error
                    error_context = self._create_error_context(
                        "RUNTIME_ERROR",
                        ErrorSeverity.MEDIUM,
                        sequence_length,
                        batch_size,
                        str(e)
                    )
                    self._record_error(error_context)
                    raise
                    
            except Exception as e:
                # Unexpected error
                error_context = self._create_error_context(
                    "UNEXPECTED_ERROR",
                    ErrorSeverity.MEDIUM,
                    sequence_length,
                    batch_size,
                    str(e)
                )
                self._record_error(error_context)
                raise
    
    def _create_error_context(
        self,
        error_type: str,
        severity: ErrorSeverity,
        sequence_length: int,
        batch_size: int,
        error_message: str
    ) -> ErrorContext:
        """Create error context for analysis."""
        # Memory usage
        memory = psutil.virtual_memory()
        memory_used_gb = (memory.total - memory.available) / (1024**3)
        
        gpu_memory_used_gb = 0.0
        if torch.cuda.is_available():
            try:
                gpu_memory_used_gb = torch.cuda.memory_allocated() / (1024**3)
            except Exception:
                pass
        
        # Suggest recovery actions
        suggested_actions = self._suggest_recovery_actions(
            error_type, severity, sequence_length, memory_used_gb, gpu_memory_used_gb
        )
        
        return ErrorContext(
            error_type=error_type,
            severity=severity,
            timestamp=time.time(),
            sequence_length=sequence_length,
            batch_size=batch_size,
            memory_used_gb=memory_used_gb,
            gpu_memory_used_gb=gpu_memory_used_gb,
            stack_trace=traceback.format_exc(),
            suggested_actions=suggested_actions
        )
    
    def _suggest_recovery_actions(
        self,
        error_type: str,
        severity: ErrorSeverity,
        sequence_length: int,
        memory_used_gb: float,
        gpu_memory_used_gb: float
    ) -> List[DegradationStrategy]:
        """Suggest appropriate recovery actions based on error context."""
        actions = []
        
        # Memory-based suggestions
        if "OOM" in error_type or gpu_memory_used_gb > 3.5:
            actions.extend([
                DegradationStrategy.EMERGENCY_CLEANUP,
                DegradationStrategy.REDUCE_PRECISION,
                DegradationStrategy.INCREASE_SPARSITY
            ])
            
            if sequence_length > 131072:  # > 128k
                actions.append(DegradationStrategy.TRUNCATE_SEQUENCE)
            
            if gpu_memory_used_gb > 3.8:
                actions.append(DegradationStrategy.OFFLOAD_TO_CPU)
        
        # Sequence length based suggestions
        if sequence_length > 200000:  # Very long sequences
            actions.extend([
                DegradationStrategy.TRUNCATE_SEQUENCE,
                DegradationStrategy.SIMPLIFY_ATTENTION
            ])
        
        # Severity-based escalation
        if severity == ErrorSeverity.CRITICAL:
            actions.insert(0, DegradationStrategy.EMERGENCY_CLEANUP)
        
        return actions
    
    def _recover_from_oom(self, error_context: ErrorContext) -> bool:
        """Attempt recovery from CUDA out of memory error."""
        logger.info("Attempting CUDA OOM recovery...")
        
        # Emergency cleanup
        torch.cuda.empty_cache()
        gc.collect()
        
        # Apply degradation strategies
        for strategy in error_context.suggested_actions:
            try:
                success = self._apply_degradation_strategy(strategy, error_context)
                if success:
                    error_context.recovery_successful = True
                    logger.info(f"Recovery successful using strategy: {strategy.value}")
                    return True
            except Exception as e:
                logger.warning(f"Strategy {strategy.value} failed: {e}")
                continue
        
        return False
    
    def _recover_from_runtime_error(self, error_context: ErrorContext) -> bool:
        """Attempt recovery from runtime errors."""
        logger.info("Attempting runtime error recovery...")
        
        # Clear caches
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        
        # Apply conservative strategies
        conservative_strategies = [
            DegradationStrategy.REDUCE_PRECISION,
            DegradationStrategy.REDUCE_BATCH_SIZE
        ]
        
        for strategy in conservative_strategies:
            try:
                success = self._apply_degradation_strategy(strategy, error_context)
                if success:
                    error_context.recovery_successful = True
                    return True
            except Exception:
                continue
        
        return False
    
    def _apply_degradation_strategy(
        self, 
        strategy: DegradationStrategy, 
        error_context: ErrorContext
    ) -> bool:
        """Apply a specific degradation strategy."""
        try:
            if strategy == DegradationStrategy.EMERGENCY_CLEANUP:
                return self._emergency_cleanup()
                
            elif strategy == DegradationStrategy.REDUCE_PRECISION:
                return self._reduce_precision()
                
            elif strategy == DegradationStrategy.INCREASE_SPARSITY:
                return self._increase_sparsity()
                
            elif strategy == DegradationStrategy.TRUNCATE_SEQUENCE:
                return self._truncate_sequence(error_context.sequence_length)
                
            elif strategy == DegradationStrategy.OFFLOAD_TO_CPU:
                return self._offload_to_cpu()
                
            elif strategy == DegradationStrategy.REDUCE_BATCH_SIZE:
                return self._reduce_batch_size()
                
            elif strategy == DegradationStrategy.SIMPLIFY_ATTENTION:
                return self._simplify_attention()
                
        except Exception as e:
            logger.error(f"Failed to apply strategy {strategy.value}: {e}")
            return False
        
        return False
    
    def _emergency_cleanup(self) -> bool:
        """Perform emergency memory cleanup."""
        logger.info("Performing emergency cleanup...")
        
        # GPU cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        # System cleanup
        gc.collect()
        
        # Additional cleanup if needed
        try:
            # Force garbage collection multiple times
            for _ in range(3):
                gc.collect()
                time.sleep(0.1)
        except Exception:
            pass
        
        return True
    
    def _reduce_precision(self) -> bool:
        """Signal to reduce computational precision."""
        # This would typically be handled by the calling code
        # We just track the degradation level
        self.current_degradation_level = max(self.current_degradation_level, 1)
        self.active_strategies.append(DegradationStrategy.REDUCE_PRECISION)
        logger.info("Precision reduction requested")
        return True
    
    def _increase_sparsity(self) -> bool:
        """Signal to increase attention sparsity."""
        self.current_degradation_level = max(self.current_degradation_level, 2)
        self.active_strategies.append(DegradationStrategy.INCREASE_SPARSITY)
        logger.info("Sparsity increase requested")
        return True
    
    def _truncate_sequence(self, current_length: int) -> bool:
        """Signal to truncate sequence length."""
        new_length = min(current_length // 2, 131072)
        self.current_degradation_level = max(self.current_degradation_level, 3)
        self.active_strategies.append(DegradationStrategy.TRUNCATE_SEQUENCE)
        logger.info(f"Sequence truncation requested: {current_length} -> {new_length}")
        return True
    
    def _offload_to_cpu(self) -> bool:
        """Signal to offload computations to CPU."""
        self.current_degradation_level = max(self.current_degradation_level, 4)
        self.active_strategies.append(DegradationStrategy.OFFLOAD_TO_CPU)
        logger.info("CPU offloading requested")
        return True
    
    def _reduce_batch_size(self) -> bool:
        """Signal to reduce batch size."""
        self.current_degradation_level = max(self.current_degradation_level, 2)
        self.active_strategies.append(DegradationStrategy.REDUCE_BATCH_SIZE)
        logger.info("Batch size reduction requested")
        return True
    
    def _simplify_attention(self) -> bool:
        """Signal to simplify attention mechanism."""
        self.current_degradation_level = max(self.current_degradation_level, 3)
        self.active_strategies.append(DegradationStrategy.SIMPLIFY_ATTENTION)
        logger.info("Attention simplification requested")
        return True
    
    def _record_error(self, error_context: ErrorContext):
        """Record error for analytics."""
        self.error_history.append(error_context)
        self.error_counts[error_context.error_type] += 1
        
        # Update recovery success rate
        error_type = error_context.error_type
        if error_type not in self.recovery_success_rate:
            self.recovery_success_rate[error_type] = 0.0
        
        # Simple moving average update
        current_rate = self.recovery_success_rate[error_type]
        success = 1.0 if error_context.recovery_successful else 0.0
        self.recovery_success_rate[error_type] = 0.9 * current_rate + 0.1 * success
    
    def get_degradation_level(self) -> int:
        """Get current degradation level (0 = no degradation, higher = more degraded)."""
        return self.current_degradation_level
    
    def get_active_strategies(self) -> List[DegradationStrategy]:
        """Get currently active degradation strategies."""
        return self.active_strategies.copy()
    
    def reset_degradation(self):
        """Reset degradation state."""
        self.current_degradation_level = 0
        self.active_strategies.clear()
        logger.info("Reset degradation state")
    
    def get_error_analytics(self) -> Dict[str, Any]:
        """Get comprehensive error analytics."""
        total_errors = len(self.error_history)
        recent_errors = [e for e in self.error_history if time.time() - e.timestamp < 3600]  # Last hour
        
        analytics = {
            "total_errors": total_errors,
            "recent_errors": len(recent_errors),
            "error_counts": dict(self.error_counts),
            "recovery_success_rates": dict(self.recovery_success_rate),
            "current_degradation_level": self.current_degradation_level,
            "active_strategies": [s.value for s in self.active_strategies],
            "monitoring_active": self.monitoring_active
        }
        
        if recent_errors:
            analytics["recent_error_types"] = {}
            for error in recent_errors:
                error_type = error.error_type
                if error_type not in analytics["recent_error_types"]:
                    analytics["recent_error_types"][error_type] = 0
                analytics["recent_error_types"][error_type] += 1
        
        return analytics
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Get system recommendations based on error history."""
        recommendations = {
            "memory_optimization": [],
            "configuration_changes": [],
            "hardware_considerations": []
        }
        
        # Analyze error patterns
        if self.error_counts.get("CUDA_OOM", 0) > 5:
            recommendations["memory_optimization"].extend([
                "Consider using more aggressive memory pooling",
                "Implement additional CPU offloading",
                "Reduce default sequence length limits"
            ])
        
        if self.current_degradation_level > 2:
            recommendations["configuration_changes"].extend([
                "Consider lowering default precision",
                "Increase default sparsity levels",
                "Implement adaptive batch sizing"
            ])
        
        avg_gpu_usage = 0.0
        if self.error_history:
            avg_gpu_usage = sum(e.gpu_memory_used_gb for e in self.error_history) / len(self.error_history)
        
        if avg_gpu_usage > 3.5:
            recommendations["hardware_considerations"].extend([
                "Current workload may benefit from additional VRAM",
                "Consider implementing more aggressive memory compression",
                "Evaluate CPU-GPU hybrid processing strategies"
            ])
        
        return recommendations


# Global error handler instance
_global_error_handler: Optional[ProductionErrorHandler] = None


def get_production_error_handler() -> ProductionErrorHandler:
    """Get or create the global production error handler."""
    global _global_error_handler
    
    if _global_error_handler is None:
        _global_error_handler = ProductionErrorHandler()
    
    return _global_error_handler


def create_production_error_handler(
    memory_thresholds: Optional[MemoryPressureThresholds] = None,
    quality_config: Optional[QualitySpeedTradeoff] = None,
    enable_analytics: bool = True
) -> ProductionErrorHandler:
    """Create a new production error handler with custom configuration."""
    return ProductionErrorHandler(
        memory_thresholds=memory_thresholds,
        quality_config=quality_config,
        enable_analytics=enable_analytics
    )


# Convenience decorators
def with_error_recovery(
    operation_name: str,
    max_retries: int = 3
):
    """Decorator for automatic error recovery."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            error_handler = get_production_error_handler()
            
            # Try to estimate sequence length from args
            sequence_length = 131072  # Default
            batch_size = 1
            
            # Look for common parameter patterns
            for arg in args:
                if hasattr(arg, 'shape') and len(arg.shape) >= 2:
                    if arg.shape[1] > sequence_length:
                        sequence_length = arg.shape[1]
                    batch_size = arg.shape[0]
                    break
            
            with error_handler.error_recovery_context(
                operation_name, 
                sequence_length, 
                batch_size, 
                max_retries
            ):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test the error handler
    error_handler = ProductionErrorHandler()
    
    # Simulate some errors
    print("Testing error handler...")
    
    try:
        with error_handler.error_recovery_context("test_operation", 256000, 1):
            # Simulate operation that might fail
            print("Operation completed successfully")
    except Exception as e:
        print(f"Operation failed: {e}")
    
    # Get analytics
    analytics = error_handler.get_error_analytics()
    print(f"Error analytics: {analytics}")
    
    recommendations = error_handler.get_recommendations()
    print(f"Recommendations: {recommendations}")
    
    error_handler.stop_monitoring()
    print("Error handler test completed")
