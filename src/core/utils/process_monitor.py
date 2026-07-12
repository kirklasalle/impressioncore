"""
ImpressionCore Process Monitor and Safety System
==================================================

Comprehensive monitoring and safety system for long-running processes including:
- Real-time resource monitoring
- Process health checks
- Automatic safety shutdowns
- Progress tracking
- Error detection and recovery
- Training pipeline monitoring

Author: ImpressionCore Development Team
Created: 2025-01-13
"""

import os
import sys
import time
import json
import psutil
import signal
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Add ImpressionCore modules to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.utils.rich_logging import RichLogger
from src.core.utils.rich_status_animation import RichStatusAnimation


@dataclass
class ProcessMetrics:
    """Container for process metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_used_gb: float
    disk_total_gb: float
    gpu_memory_used: Optional[float] = None
    gpu_memory_total: Optional[float] = None
    process_count: int = 0
    thread_count: int = 0


@dataclass
class SafetyThresholds:
    """Safety thresholds for automatic shutdown"""
    max_cpu_percent: float = 95.0
    max_memory_percent: float = 90.0
    max_disk_percent: float = 95.0
    max_gpu_memory_percent: float = 95.0
    max_runtime_hours: float = 24.0
    check_interval_seconds: float = 30.0


class ProcessMonitor:
    """
    Comprehensive process monitoring and safety system
    """
    
    def __init__(self, 
                 process_name: str = "ImpressionCore",
                 log_dir: str = "src/memlog",
                 thresholds: Optional[SafetyThresholds] = None):
        """
        Initialize process monitor
        
        Args:
            process_name: Name of the process being monitored
            log_dir: Directory for log files
            thresholds: Safety thresholds for automatic shutdown
        """
        self.process_name = process_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.thresholds = thresholds or SafetyThresholds()
        self.start_time = datetime.now()
        self.is_monitoring = False
        self.shutdown_callbacks = []
        self.metrics_history = []
        
        # Initialize logging
        self.logger = RichLogger(
            name=f"ProcessMonitor_{process_name}",
            log_file=self.log_dir / f"process_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        # Initialize status animation
        self.status = RichStatusAnimation()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"Process Monitor initialized for {process_name}")
    
    def add_shutdown_callback(self, callback: Callable):
        """Add callback to execute on shutdown"""
        self.shutdown_callbacks.append(callback)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.warning(f"Received signal {signum}, initiating graceful shutdown")
        self.stop_monitoring()
    
    def _get_gpu_memory(self) -> tuple[Optional[float], Optional[float]]:
        """Get GPU memory usage if available"""
        try:
            import torch
            if torch.cuda.is_available():
                used = torch.cuda.memory_allocated() / (1024**3)  # GB
                total = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                return used, total
        except Exception:
            pass
        return None, None
    
    def _collect_metrics(self) -> ProcessMetrics:
        """Collect current system metrics"""
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # GPU metrics
        gpu_used, gpu_total = self._get_gpu_memory()
        
        # Process metrics
        process_count = len(psutil.pids())
        thread_count = threading.active_count()
        
        metrics = ProcessMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_used_gb=disk.used / (1024**3),
            disk_total_gb=disk.total / (1024**3),
            gpu_memory_used=gpu_used,
            gpu_memory_total=gpu_total,
            process_count=process_count,
            thread_count=thread_count
        )
        
        return metrics
    
    def _check_safety_thresholds(self, metrics: ProcessMetrics) -> List[str]:
        """Check if any safety thresholds are exceeded"""
        violations = []
        
        if metrics.cpu_percent > self.thresholds.max_cpu_percent:
            violations.append(f"CPU usage: {metrics.cpu_percent:.1f}% > {self.thresholds.max_cpu_percent}%")
        
        if metrics.memory_percent > self.thresholds.max_memory_percent:
            violations.append(f"Memory usage: {metrics.memory_percent:.1f}% > {self.thresholds.max_memory_percent}%")
        
        disk_percent = (metrics.disk_used_gb / metrics.disk_total_gb) * 100
        if disk_percent > self.thresholds.max_disk_percent:
            violations.append(f"Disk usage: {disk_percent:.1f}% > {self.thresholds.max_disk_percent}%")
        
        if metrics.gpu_memory_used and metrics.gpu_memory_total:
            gpu_percent = (metrics.gpu_memory_used / metrics.gpu_memory_total) * 100
            if gpu_percent > self.thresholds.max_gpu_memory_percent:
                violations.append(f"GPU memory: {gpu_percent:.1f}% > {self.thresholds.max_gpu_memory_percent}%")
        
        # Check runtime
        runtime = datetime.now() - self.start_time
        if runtime.total_seconds() / 3600 > self.thresholds.max_runtime_hours:
            violations.append(f"Runtime: {runtime.total_seconds()/3600:.1f}h > {self.thresholds.max_runtime_hours}h")
        
        return violations
    
    def _emergency_shutdown(self, reason: str):
        """Execute emergency shutdown"""
        self.logger.error(f"EMERGENCY SHUTDOWN: {reason}")
        
        # Execute shutdown callbacks
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Shutdown callback failed: {e}")
        
        # Save final metrics
        self.save_metrics_history()
        
        # Stop monitoring
        self.is_monitoring = False
        
        self.logger.error("Emergency shutdown completed")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect metrics
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Check safety thresholds
                violations = self._check_safety_thresholds(metrics)
                
                if violations:
                    violation_text = "; ".join(violations)
                    self.logger.warning(f"Safety threshold violations: {violation_text}")
                    
                    # Emergency shutdown if multiple violations or critical single violation
                    if len(violations) > 2 or any("CPU" in v and "95" in v for v in violations):
                        self._emergency_shutdown(f"Critical safety violations: {violation_text}")
                        break
                
                # Update status
                runtime = datetime.now() - self.start_time
                status_text = (f"Monitoring {self.process_name} | "
                             f"Runtime: {str(runtime).split('.')[0]} | "
                             f"CPU: {metrics.cpu_percent:.1f}% | "
                             f"RAM: {metrics.memory_percent:.1f}% | "
                             f"Disk: {metrics.disk_used_gb:.0f}GB")
                
                if metrics.gpu_memory_used:
                    status_text += f" | GPU: {metrics.gpu_memory_used:.1f}GB"
                
                self.status.update_status(status_text)
                
                # Log periodic summary
                if len(self.metrics_history) % 10 == 0:  # Every 10 checks
                    self.logger.info(f"Status: {status_text}")
                
                # Cleanup old metrics (keep last 1000)
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                time.sleep(self.thresholds.check_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)  # Wait before retrying
    
    def start_monitoring(self):
        """Start monitoring in background thread"""
        if self.is_monitoring:
            self.logger.warning("Monitoring already running")
            return
        
        self.is_monitoring = True
        self.start_time = datetime.now()
        
        self.logger.info(f"Starting monitoring for {self.process_name}")
        
        # Start monitoring thread
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()
        
        self.status.start_animation(f"Monitoring {self.process_name}")
        
        return monitoring_thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if not self.is_monitoring:
            return
        
        self.logger.info(f"Stopping monitoring for {self.process_name}")
        
        self.is_monitoring = False
        self.status.stop_animation()
        
        # Save metrics history
        self.save_metrics_history()
        
        # Execute shutdown callbacks
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Shutdown callback failed: {e}")
    
    def save_metrics_history(self):
        """Save metrics history to file"""
        if not self.metrics_history:
            return
        
        filename = f"metrics_history_{self.process_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.log_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump([asdict(m) for m in self.metrics_history], f, indent=2)
            
            self.logger.info(f"Metrics history saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save metrics history: {e}")
    
    def get_current_metrics(self) -> ProcessMetrics:
        """Get current system metrics"""
        return self._collect_metrics()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of metrics history"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 readings
        
        return {
            "total_readings": len(self.metrics_history),
            "runtime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
            "avg_cpu_percent": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            "avg_memory_percent": sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            "max_cpu_percent": max(m.cpu_percent for m in self.metrics_history),
            "max_memory_percent": max(m.memory_percent for m in self.metrics_history),
            "current_disk_gb": recent_metrics[-1].disk_used_gb if recent_metrics else 0
        }


class TrainingProcessMonitor(ProcessMonitor):
    """
    Specialized monitor for training processes with additional training-specific metrics
    """
    
    def __init__(self, 
                 model_name: str,
                 training_config: Dict[str, Any],
                 **kwargs):
        """
        Initialize training process monitor
        
        Args:
            model_name: Name of the model being trained
            training_config: Training configuration dictionary
            **kwargs: Additional arguments for ProcessMonitor
        """
        super().__init__(process_name=f"Training_{model_name}", **kwargs)
        
        self.model_name = model_name
        self.training_config = training_config
        self.training_metrics = {
            "epoch": 0,
            "step": 0,
            "loss": 0.0,
            "learning_rate": 0.0,
            "samples_processed": 0,
            "estimated_completion": None
        }
        
        self.logger.info(f"Training monitor initialized for {model_name}")
    
    def update_training_metrics(self, **kwargs):
        """Update training-specific metrics"""
        self.training_metrics.update(kwargs)
        
        # Log training progress
        self.logger.info(f"Training update: {self.training_metrics}")
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get comprehensive training summary"""
        system_summary = self.get_metrics_summary()
        
        return {
            "model_name": self.model_name,
            "training_config": self.training_config,
            "training_metrics": self.training_metrics,
            "system_metrics": system_summary,
            "status": "running" if self.is_monitoring else "stopped"
        }


# Convenience functions for easy use
def start_process_monitoring(process_name: str, 
                           thresholds: Optional[SafetyThresholds] = None) -> ProcessMonitor:
    """Start basic process monitoring"""
    monitor = ProcessMonitor(process_name, thresholds=thresholds)
    monitor.start_monitoring()
    return monitor


def start_training_monitoring(model_name: str,
                            training_config: Dict[str, Any],
                            thresholds: Optional[SafetyThresholds] = None) -> TrainingProcessMonitor:
    """Start training process monitoring"""
    monitor = TrainingProcessMonitor(model_name, training_config, thresholds=thresholds)
    monitor.start_monitoring()
    return monitor


if __name__ == "__main__":
    # Example usage
    print("ImpressionCore Process Monitor - Example Usage")
    
    # Basic monitoring
    monitor = start_process_monitoring("TestProcess")
    
    try:
        # Simulate some work
        for i in range(10):
            time.sleep(2)
            print(f"Working... {i+1}/10")
            
            # Show current metrics
            metrics = monitor.get_current_metrics()
            print(f"CPU: {metrics.cpu_percent:.1f}%, Memory: {metrics.memory_percent:.1f}%")
    
    finally:
        monitor.stop_monitoring()
        print("Monitoring stopped")
