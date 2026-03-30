#!/usr/bin/env python3
"""
ImpressionCore: Priority 6C - Performance Monitor & Telemetry

Comprehensive monitoring and telemetry system for 256k context processing.
Real-time performance tracking, adaptive configuration, and predictive analytics.

File: src/core/monitoring/performance_telemetry.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-30
Modified: 2025-05-30
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle <kirk@impressioncore.ai>

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [monitoring, telemetry, performance, analytics, real-time, 2025]
Dependencies: [torch, psutil, typing, logging, threading, time]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Production-ready monitoring and telemetry system featuring:
- Real-time performance metrics collection
- Memory usage tracking and prediction
- Hardware utilization monitoring
- Adaptive configuration based on performance patterns
- Predictive analytics for resource optimization
- Quality degradation detection and alerts
"""

import torch
import psutil
import time
import threading
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field, asdict
from collections import deque, defaultdict
from enum import Enum
import logging
import json
import os
from statistics import mean, median, stdev
import warnings

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to collect."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    GPU_UTILIZATION = "gpu_utilization"
    QUALITY_SCORE = "quality_score"
    ERROR_RATE = "error_rate"
    ATTENTION_SPARSITY = "attention_sparsity"
    CONTEXT_LENGTH = "context_length"


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Individual performance metric data point."""
    metric_type: MetricType
    value: float
    timestamp: float
    context_length: int = 0
    batch_size: int = 1
    operation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemSnapshot:
    """Comprehensive system state snapshot."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    gpu_memory_used_gb: float
    gpu_memory_total_gb: float
    gpu_utilization_percent: float
    active_context_length: int
    active_batch_size: int
    current_operation: str
    quality_degradation_level: int


@dataclass
class PerformanceAlert:
    """Performance alert with context."""
    alert_level: AlertLevel
    metric_type: MetricType
    message: str
    value: float
    threshold: float
    timestamp: float
    recommended_actions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptiveConfiguration:
    """Dynamic configuration based on performance patterns."""
    target_latency_ms: float = 200.0
    memory_usage_target: float = 0.85
    quality_threshold: float = 0.95
    auto_degradation_enabled: bool = True
    adaptive_sparsity_enabled: bool = True
    dynamic_precision_enabled: bool = True
    learning_rate: float = 0.1  # For adaptive adjustments


class PerformanceTelemetry:
    """
    Comprehensive performance monitoring and telemetry system.
    
    Features:
    - Real-time metric collection and analysis
    - Predictive performance modeling
    - Automatic alert generation
    - Adaptive configuration optimization
    - Historical trend analysis
    - Export capabilities for external monitoring
    """
    
    def __init__(
        self,
        max_history_size: int = 10000,
        monitoring_interval: float = 0.1,  # 100ms
        enable_alerts: bool = True,
        enable_adaptive_config: bool = True,
        metrics_export_path: Optional[str] = None
    ):
        self.max_history_size = max_history_size
        self.monitoring_interval = monitoring_interval
        self.enable_alerts = enable_alerts
        self.enable_adaptive_config = enable_adaptive_config
        self.metrics_export_path = metrics_export_path
        
        # Metric storage
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.system_snapshots: deque = deque(maxlen=max_history_size // 10)
        self.alerts: deque = deque(maxlen=1000)
        
        # Real-time tracking
        self.current_metrics: Dict[MetricType, float] = {}
        self.metric_aggregates: Dict[MetricType, Dict[str, float]] = defaultdict(dict)
        
        # Monitoring control
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.collection_lock = threading.RLock()
        
        # Alert configuration
        self.alert_thresholds = {
            MetricType.LATENCY: {"warning": 300, "error": 500, "critical": 1000},
            MetricType.MEMORY_USAGE: {"warning": 0.80, "error": 0.90, "critical": 0.95},
            MetricType.GPU_UTILIZATION: {"warning": 0.85, "error": 0.95, "critical": 0.98},
            MetricType.ERROR_RATE: {"warning": 0.05, "error": 0.10, "critical": 0.20},
            MetricType.QUALITY_SCORE: {"warning": 0.90, "error": 0.85, "critical": 0.80}
        }
        
        # Adaptive configuration
        self.adaptive_config = AdaptiveConfiguration()
        self.performance_model: Dict[str, Any] = {}
        
        # Callback registration
        self.alert_callbacks: List[Callable] = []
        self.metric_callbacks: List[Callable] = []
        
        logger.info("Initialized PerformanceTelemetry system")
        
        # Start monitoring if enabled
        self.start_monitoring()
    
    def __del__(self):
        """Cleanup monitoring thread."""
        self.stop_monitoring()
    
    def start_monitoring(self):
        """Start background monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Started performance monitoring")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1.0)
        
        # Export final metrics if path specified
        if self.metrics_export_path:
            self.export_metrics()
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                self._collect_system_snapshot()
                self._update_metric_aggregates()
                self._check_alert_conditions()
                
                if self.enable_adaptive_config:
                    self._update_adaptive_configuration()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1.0)
    
    def _collect_system_snapshot(self):
        """Collect comprehensive system state snapshot."""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # GPU metrics
            gpu_memory_used_gb = 0.0
            gpu_memory_total_gb = 0.0
            gpu_utilization_percent = 0.0
            
            if torch.cuda.is_available():
                try:
                    gpu_memory_used_gb = torch.cuda.memory_allocated() / (1024**3)
                    gpu_memory_total_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    
                    # Try to get GPU utilization
                    try:
                        import pynvml
                        pynvml.nvmlInit()
                        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                        gpu_utilization_percent = util.gpu / 100.0
                    except ImportError:
                        # Estimate from memory usage
                        gpu_utilization_percent = min(gpu_memory_used_gb / gpu_memory_total_gb, 1.0)
                except Exception:
                    pass
            
            snapshot = SystemSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_gb=memory_available_gb,
                gpu_memory_used_gb=gpu_memory_used_gb,
                gpu_memory_total_gb=gpu_memory_total_gb,
                gpu_utilization_percent=gpu_utilization_percent,
                active_context_length=getattr(self, 'current_context_length', 0),
                active_batch_size=getattr(self, 'current_batch_size', 1),
                current_operation=getattr(self, 'current_operation', 'idle'),
                quality_degradation_level=getattr(self, 'quality_degradation_level', 0)
            )
            
            with self.collection_lock:
                self.system_snapshots.append(snapshot)
                
                # Update current metrics
                self.current_metrics[MetricType.MEMORY_USAGE] = memory_percent / 100.0
                self.current_metrics[MetricType.GPU_UTILIZATION] = gpu_utilization_percent
            
        except Exception as e:
            logger.error(f"Error collecting system snapshot: {e}")
    
    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        context_length: int = 0,
        batch_size: int = 1,
        operation: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a performance metric."""
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            timestamp=time.time(),
            context_length=context_length,
            batch_size=batch_size,
            operation=operation,
            metadata=metadata or {}
        )
        
        with self.collection_lock:
            self.metrics_history.append(metric)
            self.current_metrics[metric_type] = value
        
        # Trigger callbacks
        for callback in self.metric_callbacks:
            try:
                callback(metric)
            except Exception as e:
                logger.error(f"Error in metric callback: {e}")
        
        # Check for immediate alerts
        if self.enable_alerts:
            self._check_metric_alerts(metric)
    
    def _update_metric_aggregates(self):
        """Update aggregated metric statistics."""
        with self.collection_lock:
            recent_window = 300  # 5 minutes
            current_time = time.time()
            
            for metric_type in MetricType:
                recent_metrics = [
                    m.value for m in self.metrics_history
                    if (m.metric_type == metric_type and 
                        current_time - m.timestamp < recent_window)
                ]
                
                if recent_metrics:
                    self.metric_aggregates[metric_type] = {
                        "mean": mean(recent_metrics),
                        "median": median(recent_metrics),
                        "min": min(recent_metrics),
                        "max": max(recent_metrics),
                        "count": len(recent_metrics)
                    }
                    
                    if len(recent_metrics) > 1:
                        try:
                            self.metric_aggregates[metric_type]["std"] = stdev(recent_metrics)
                        except:
                            self.metric_aggregates[metric_type]["std"] = 0.0
    
    def _check_alert_conditions(self):
        """Check for alert conditions across all metrics."""
        current_time = time.time()
        
        for metric_type, current_value in self.current_metrics.items():
            if metric_type in self.alert_thresholds:
                thresholds = self.alert_thresholds[metric_type]
                
                alert_level = None
                threshold_value = None
                
                if current_value >= thresholds.get("critical", float('inf')):
                    alert_level = AlertLevel.CRITICAL
                    threshold_value = thresholds["critical"]
                elif current_value >= thresholds.get("error", float('inf')):
                    alert_level = AlertLevel.ERROR
                    threshold_value = thresholds["error"]
                elif current_value >= thresholds.get("warning", float('inf')):
                    alert_level = AlertLevel.WARNING
                    threshold_value = thresholds["warning"]
                
                if alert_level:
                    self._generate_alert(
                        alert_level, metric_type, current_value, threshold_value
                    )
    
    def _check_metric_alerts(self, metric: PerformanceMetric):
        """Check if a specific metric triggers an alert."""
        if metric.metric_type not in self.alert_thresholds:
            return
        
        thresholds = self.alert_thresholds[metric.metric_type]
        alert_level = None
        threshold_value = None
        
        # Special handling for quality score (lower is worse)
        if metric.metric_type == MetricType.QUALITY_SCORE:
            if metric.value <= thresholds.get("critical", 0):
                alert_level = AlertLevel.CRITICAL
                threshold_value = thresholds["critical"]
            elif metric.value <= thresholds.get("error", 0):
                alert_level = AlertLevel.ERROR
                threshold_value = thresholds["error"]
            elif metric.value <= thresholds.get("warning", 0):
                alert_level = AlertLevel.WARNING
                threshold_value = thresholds["warning"]
        else:
            # Higher values are worse
            if metric.value >= thresholds.get("critical", float('inf')):
                alert_level = AlertLevel.CRITICAL
                threshold_value = thresholds["critical"]
            elif metric.value >= thresholds.get("error", float('inf')):
                alert_level = AlertLevel.ERROR
                threshold_value = thresholds["error"]
            elif metric.value >= thresholds.get("warning", float('inf')):
                alert_level = AlertLevel.WARNING
                threshold_value = thresholds["warning"]
        
        if alert_level:
            self._generate_alert(alert_level, metric.metric_type, metric.value, threshold_value)
    
    def _generate_alert(
        self,
        alert_level: AlertLevel,
        metric_type: MetricType,
        value: float,
        threshold: float
    ):
        """Generate and record a performance alert."""
        # Generate recommendations
        recommendations = self._get_alert_recommendations(metric_type, alert_level, value)
        
        # Create alert message
        if metric_type == MetricType.QUALITY_SCORE:
            message = f"Quality score {value:.3f} below {threshold:.3f} threshold"
        else:
            message = f"{metric_type.value.title()} {value:.3f} exceeded {threshold:.3f} threshold"
        
        alert = PerformanceAlert(
            alert_level=alert_level,
            metric_type=metric_type,
            message=message,
            value=value,
            threshold=threshold,
            timestamp=time.time(),
            recommended_actions=recommendations,
            context={
                "current_context_length": getattr(self, 'current_context_length', 0),
                "current_operation": getattr(self, 'current_operation', 'unknown'),
                "system_load": self.current_metrics.get(MetricType.MEMORY_USAGE, 0.0)
            }
        )
        
        with self.collection_lock:
            self.alerts.append(alert)
        
        # Log alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }[alert_level]
        
        logger.log(log_level, f"Performance Alert: {message}")
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def _get_alert_recommendations(
        self, 
        metric_type: MetricType, 
        alert_level: AlertLevel, 
        value: float
    ) -> List[str]:
        """Get recommended actions for specific alert conditions."""
        recommendations = []
        
        if metric_type == MetricType.LATENCY:
            recommendations.extend([
                "Consider reducing sequence length",
                "Increase attention sparsity",
                "Enable CPU offloading for non-critical operations"
            ])
            if alert_level == AlertLevel.CRITICAL:
                recommendations.append("Switch to emergency fast mode")
        
        elif metric_type == MetricType.MEMORY_USAGE:
            recommendations.extend([
                "Clear intermediate caches",
                "Reduce batch size",
                "Enable gradient checkpointing"
            ])
            if alert_level == AlertLevel.CRITICAL:
                recommendations.append("Emergency memory cleanup required")
        
        elif metric_type == MetricType.GPU_UTILIZATION:
            recommendations.extend([
                "Optimize GPU memory allocation",
                "Reduce concurrent operations",
                "Consider CPU-GPU hybrid processing"
            ])
        
        elif metric_type == MetricType.QUALITY_SCORE:
            recommendations.extend([
                "Reduce degradation level",
                "Increase model precision",
                "Review sparse attention patterns"
            ])
        
        elif metric_type == MetricType.ERROR_RATE:
            recommendations.extend([
                "Review recent configuration changes",
                "Check hardware stability",
                "Enable conservative processing mode"
            ])
        
        return recommendations
    
    def _update_adaptive_configuration(self):
        """Update adaptive configuration based on performance patterns."""
        if not self.enable_adaptive_config:
            return
        
        try:
            # Get recent performance data
            recent_latency = self.metric_aggregates.get(MetricType.LATENCY, {}).get("mean", 0)
            recent_quality = self.metric_aggregates.get(MetricType.QUALITY_SCORE, {}).get("mean", 1.0)
            recent_memory = self.metric_aggregates.get(MetricType.MEMORY_USAGE, {}).get("mean", 0)
            
            # Adaptive latency target adjustment
            if recent_latency > self.adaptive_config.target_latency_ms * 1.2:
                # Performance is lagging, increase tolerance slightly
                self.adaptive_config.target_latency_ms *= (1 + self.adaptive_config.learning_rate)
            elif recent_latency < self.adaptive_config.target_latency_ms * 0.8:
                # Performance is good, tighten tolerance
                self.adaptive_config.target_latency_ms *= (1 - self.adaptive_config.learning_rate)
            
            # Adaptive quality threshold
            if recent_quality < self.adaptive_config.quality_threshold:
                # Quality degraded, be more conservative
                self.adaptive_config.quality_threshold = max(
                    0.80, 
                    self.adaptive_config.quality_threshold - self.adaptive_config.learning_rate
                )
            
            # Adaptive memory target
            if recent_memory > self.adaptive_config.memory_usage_target:
                # Memory pressure, reduce target
                self.adaptive_config.memory_usage_target = max(
                    0.70,
                    self.adaptive_config.memory_usage_target - self.adaptive_config.learning_rate
                )
            
        except Exception as e:
            logger.error(f"Error updating adaptive configuration: {e}")
    
    def register_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Register callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def register_metric_callback(self, callback: Callable[[PerformanceMetric], None]):
        """Register callback for new metrics."""
        self.metric_callbacks.append(callback)
    
    def set_context_info(
        self, 
        context_length: int, 
        batch_size: int = 1, 
        operation: str = ""
    ):
        """Set current context information for monitoring."""
        self.current_context_length = context_length
        self.current_batch_size = batch_size
        self.current_operation = operation
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current real-time metrics."""
        with self.collection_lock:
            return {
                metric_type.value: value 
                for metric_type, value in self.current_metrics.items()
            }
    
    def get_metric_summary(self, metric_type: MetricType) -> Dict[str, Any]:
        """Get comprehensive summary for a specific metric."""
        with self.collection_lock:
            aggregates = self.metric_aggregates.get(metric_type, {})
            recent_values = [
                m.value for m in self.metrics_history
                if m.metric_type == metric_type
            ][-100:]  # Last 100 values
            
            summary = {
                "current_value": self.current_metrics.get(metric_type, 0.0),
                "aggregates": aggregates,
                "recent_trend": self._calculate_trend(recent_values),
                "alert_thresholds": self.alert_thresholds.get(metric_type, {}),
                "recent_alerts": len([
                    a for a in self.alerts 
                    if a.metric_type == metric_type and time.time() - a.timestamp < 3600
                ])
            }
            
            return summary
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for values."""
        if len(values) < 5:
            return "insufficient_data"
        
        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        y = values
        
        # Calculate slope
        try:
            x_mean = sum(x) / n
            y_mean = sum(y) / n
            
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                return "stable"
            
            slope = numerator / denominator
            
            if slope > 0.01:
                return "increasing"
            elif slope < -0.01:
                return "decreasing"
            else:
                return "stable"
        except:
            return "unknown"
    
    def get_system_health_score(self) -> float:
        """Calculate overall system health score (0-1)."""
        scores = []
        
        # Latency score
        current_latency = self.current_metrics.get(MetricType.LATENCY, 0)
        if current_latency > 0:
            latency_score = max(0, 1 - (current_latency / 1000))  # Normalize to 1s max
            scores.append(latency_score)
        
        # Memory score
        memory_usage = self.current_metrics.get(MetricType.MEMORY_USAGE, 0)
        memory_score = max(0, 1 - memory_usage)
        scores.append(memory_score)
        
        # GPU utilization score (sweet spot around 80%)
        gpu_util = self.current_metrics.get(MetricType.GPU_UTILIZATION, 0)
        if gpu_util < 0.8:
            gpu_score = gpu_util / 0.8
        else:
            gpu_score = max(0, 2 - (gpu_util / 0.8))
        scores.append(gpu_score)
        
        # Quality score
        quality = self.current_metrics.get(MetricType.QUALITY_SCORE, 1.0)
        scores.append(quality)
        
        # Error rate score
        error_rate = self.current_metrics.get(MetricType.ERROR_RATE, 0)
        error_score = max(0, 1 - error_rate * 5)  # 20% error rate = 0 score
        scores.append(error_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        with self.collection_lock:
            current_time = time.time()
            
            # Recent metrics (last hour)
            recent_metrics = [
                m for m in self.metrics_history
                if current_time - m.timestamp < 3600
            ]
            
            # Recent alerts
            recent_alerts = [
                a for a in self.alerts
                if current_time - a.timestamp < 3600
            ]
            
            report = {
                "timestamp": current_time,
                "monitoring_duration_hours": (
                    current_time - min(m.timestamp for m in self.metrics_history)
                ) / 3600 if self.metrics_history else 0,
                "total_metrics_collected": len(self.metrics_history),
                "recent_metrics_count": len(recent_metrics),
                "total_alerts": len(self.alerts),
                "recent_alerts_count": len(recent_alerts),
                "current_metrics": self.get_current_metrics(),
                "metric_aggregates": dict(self.metric_aggregates),
                "system_health_score": self.get_system_health_score(),
                "adaptive_config": asdict(self.adaptive_config),
                "alert_summary": {
                    level.value: len([a for a in recent_alerts if a.alert_level == level])
                    for level in AlertLevel
                },
                "top_performance_issues": self._identify_top_issues()
            }
            
            return report
    
    def _identify_top_issues(self) -> List[Dict[str, Any]]:
        """Identify top performance issues based on alert patterns."""
        with self.collection_lock:
            recent_alerts = [
                a for a in self.alerts
                if time.time() - a.timestamp < 3600
            ]
            
            # Count issues by type and severity
            issue_counts = defaultdict(lambda: defaultdict(int))
            for alert in recent_alerts:
                issue_counts[alert.metric_type][alert.alert_level] += 1
            
            # Create issue summary
            issues = []
            for metric_type, level_counts in issue_counts.items():
                total_count = sum(level_counts.values())
                max_severity = max(level_counts.keys(), key=lambda x: x.value) if level_counts else AlertLevel.INFO
                
                issues.append({
                    "metric_type": metric_type.value,
                    "total_alerts": total_count,
                    "max_severity": max_severity.value,
                    "severity_distribution": {level.value: count for level, count in level_counts.items()}
                })
            
            # Sort by severity and count
            severity_order = {AlertLevel.CRITICAL: 4, AlertLevel.ERROR: 3, AlertLevel.WARNING: 2, AlertLevel.INFO: 1}
            issues.sort(
                key=lambda x: (severity_order.get(AlertLevel(x["max_severity"]), 0), x["total_alerts"]),
                reverse=True
            )
            
            return issues[:5]  # Top 5 issues
    
    def export_metrics(self, filepath: Optional[str] = None) -> str:
        """Export metrics to JSON file."""
        if filepath is None:
            filepath = self.metrics_export_path or "performance_metrics.json"
        
        try:
            # Prepare export data
            export_data = {
                "export_timestamp": time.time(),
                "performance_report": self.get_performance_report(),
                "metrics_history": [
                    {
                        "metric_type": m.metric_type.value,
                        "value": m.value,
                        "timestamp": m.timestamp,
                        "context_length": m.context_length,
                        "batch_size": m.batch_size,
                        "operation": m.operation,
                        "metadata": m.metadata
                    }
                    for m in self.metrics_history
                ],
                "alerts_history": [
                    {
                        "alert_level": a.alert_level.value,
                        "metric_type": a.metric_type.value,
                        "message": a.message,
                        "value": a.value,
                        "threshold": a.threshold,
                        "timestamp": a.timestamp,
                        "recommended_actions": a.recommended_actions,
                        "context": a.context
                    }
                    for a in self.alerts
                ]
            }
            
            # Write to file
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported metrics to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            raise


# Global telemetry instance
_global_telemetry: Optional[PerformanceTelemetry] = None


def get_performance_telemetry() -> PerformanceTelemetry:
    """Get or create the global performance telemetry instance."""
    global _global_telemetry
    
    if _global_telemetry is None:
        _global_telemetry = PerformanceTelemetry()
    
    return _global_telemetry


def create_performance_telemetry(
    max_history_size: int = 10000,
    monitoring_interval: float = 0.1,
    enable_alerts: bool = True,
    enable_adaptive_config: bool = True,
    metrics_export_path: Optional[str] = None
) -> PerformanceTelemetry:
    """Create a new performance telemetry instance with custom configuration."""
    return PerformanceTelemetry(
        max_history_size=max_history_size,
        monitoring_interval=monitoring_interval,
        enable_alerts=enable_alerts,
        enable_adaptive_config=enable_adaptive_config,
        metrics_export_path=metrics_export_path
    )


# Context manager for operation monitoring
class monitored_operation:
    """Context manager for automatic operation monitoring."""
    
    def __init__(
        self,
        operation_name: str,
        context_length: int = 0,
        batch_size: int = 1,
        telemetry: Optional[PerformanceTelemetry] = None
    ):
        self.operation_name = operation_name
        self.context_length = context_length
        self.batch_size = batch_size
        self.telemetry = telemetry or get_performance_telemetry()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.telemetry.set_context_info(
            self.context_length,
            self.batch_size,
            self.operation_name
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            latency_ms = (time.time() - self.start_time) * 1000
            
            # Record latency
            self.telemetry.record_metric(
                MetricType.LATENCY,
                latency_ms,
                self.context_length,
                self.batch_size,
                self.operation_name
            )
            
            # Record error if exception occurred
            if exc_type is not None:
                self.telemetry.record_metric(
                    MetricType.ERROR_RATE,
                    1.0,
                    self.context_length,
                    self.batch_size,
                    self.operation_name,
                    {"error_type": exc_type.__name__, "error_message": str(exc_val)}
                )
            else:
                # Record successful operation
                self.telemetry.record_metric(
                    MetricType.ERROR_RATE,
                    0.0,
                    self.context_length,
                    self.batch_size,
                    self.operation_name
                )


if __name__ == "__main__":
    # Test the telemetry system
    telemetry = PerformanceTelemetry(monitoring_interval=0.5)
    
    print("Testing performance telemetry...")
    
    # Simulate some operations
    with monitored_operation("test_attention", 131072, 2, telemetry):
        time.sleep(0.2)  # Simulate processing
        
        # Record some metrics
        telemetry.record_metric(MetricType.QUALITY_SCORE, 0.95, 131072, 2, "test_attention")
        telemetry.record_metric(MetricType.ATTENTION_SPARSITY, 0.3, 131072, 2, "test_attention")
    
    # Wait for monitoring to collect data
    time.sleep(2)
    
    # Get performance report
    report = telemetry.get_performance_report()
    print(f"Performance report: {json.dumps(report, indent=2)[:500]}...")
    
    # Get system health
    health_score = telemetry.get_system_health_score()
    print(f"System health score: {health_score:.3f}")
    
    # Export metrics
    export_path = telemetry.export_metrics("test_metrics.json")
    print(f"Metrics exported to: {export_path}")
    
    telemetry.stop_monitoring()
    print("Telemetry test completed")
