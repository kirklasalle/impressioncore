"""
ImpressionCore Production Optimizer
Phase 7D: Production Integration and Optimization

Multi-tenant resource management and scalable session handling for production deployment.

Author: GitHub Copilot & Kirk LaSalle
Date: June 1, 2025
"""

import asyncio
import threading
import time
import psutil
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import queue
import weakref

# Rich console enhancements
try:
    from src.core.utils.rich_enhancements import FallbackConsole
    from src.core.utils.rich_logging import setup_rich_logger
    from src.core.utils.gpu_memory_manager import GPUMemoryManager, get_gpu_memory_info
    from src.tools.performance_optimizer import PerformanceOptimizer as AdvancedPerformanceOptimizer
    from src.tools.memory_manager import MemoryManager as AdvancedMemoryManager
    RICH_AVAILABLE = True
    console = FallbackConsole()
    logger = setup_rich_logger(__name__)
except ImportError:
    RICH_AVAILABLE = False
    import logging
    logging.basicConfig(level=logging.INFO)

# Memory management
try:
    from ...core.memory_manager import MemoryManager
    MEMORY_MANAGER_AVAILABLE = True
except ImportError:
    MEMORY_MANAGER_AVAILABLE = False

# Setup logging
if RICH_AVAILABLE:
    logger = setup_rich_logger(__name__)
else:
    logger = logging.getLogger("production_optimizer")

@dataclass
class ResourceMetrics:
    """Resource usage metrics for monitoring."""
    cpu_percent: float
    memory_percent: float
    gpu_memory_used: float
    gpu_memory_total: float
    disk_usage: float
    network_io: Tuple[int, int]  # bytes_sent, bytes_recv
    timestamp: datetime

@dataclass
class SessionResource:
    """Resource allocation for a user session."""
    session_id: str
    user_id: str
    priority: int  # 1-10, higher is more important
    cpu_allocation: float  # percentage
    memory_allocation: float  # bytes
    gpu_memory_allocation: float  # bytes
    max_processing_time: float  # seconds
    created_at: datetime
    last_access: datetime
    resource_usage: Dict[str, float] = field(default_factory=dict)
    status: str = "active"

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation for system performance."""
    recommendation_id: str
    type: str  # "resource_reallocation", "session_migration", "quality_adjustment", etc.
    priority: int  # 1-10
    description: str
    impact_estimate: Dict[str, float]  # estimated improvements
    implementation_cost: float  # effort required (0-1)
    created_at: datetime
    expires_at: Optional[datetime] = None

class ResourceScheduler:
    """
    Advanced resource scheduler for multi-tenant environments.
    Manages CPU, memory, and GPU resources across multiple user sessions.
    """
    
    def __init__(self, max_concurrent_sessions: int = 10):
        """Initialize the resource scheduler."""
        self.max_concurrent_sessions = max_concurrent_sessions
        self.session_resources: Dict[str, SessionResource] = {}
        self.resource_queue = queue.PriorityQueue()
        self.active_sessions: Set[str] = set()
        self.waiting_sessions: Set[str] = set()
        
        # Resource limits (configurable)
        self.max_cpu_percent = 80.0  # Maximum CPU usage
        self.max_memory_percent = 75.0  # Maximum memory usage
        self.max_gpu_memory_percent = 90.0  # Maximum GPU memory usage
        
        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None
        
        logger.info(f"ResourceScheduler initialized with max {max_concurrent_sessions} sessions")
    
    def start_monitoring(self):
        """Start resource monitoring thread."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring thread."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Resource monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop running in background thread."""
        while self.monitoring_active:
            try:
                # Monitor system resources
                metrics = self._get_resource_metrics()
                
                # Check for resource pressure
                if self._is_resource_pressure(metrics):
                    self._handle_resource_pressure(metrics)
                
                # Update session resource usage
                self._update_session_usage()
                
                # Process resource queue
                self._process_resource_queue()
                
                time.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5.0)  # Back off on error
    
    def _get_resource_metrics(self) -> ResourceMetrics:
        """Get current system resource metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # GPU metrics (if available)
            gpu_memory_used = 0.0
            gpu_memory_total = 1.0
            
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory_used = torch.cuda.memory_allocated(0)
                    gpu_memory_total = torch.cuda.get_device_properties(0).total_memory
            except ImportError:
                pass
            
            return ResourceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                gpu_memory_used=gpu_memory_used,
                gpu_memory_total=gpu_memory_total,
                disk_usage=disk.percent,
                network_io=(network.bytes_sent, network.bytes_recv),
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get resource metrics: {e}")
            return ResourceMetrics(0, 0, 0, 1, 0, (0, 0), datetime.now())
    
    def _is_resource_pressure(self, metrics: ResourceMetrics) -> bool:
        """Check if system is under resource pressure."""
        return (
            metrics.cpu_percent > self.max_cpu_percent or
            metrics.memory_percent > self.max_memory_percent or
            (metrics.gpu_memory_used / metrics.gpu_memory_total * 100) > self.max_gpu_memory_percent
        )
    
    def _handle_resource_pressure(self, metrics: ResourceMetrics):
        """Handle system resource pressure by optimizing allocations."""
        logger.warning(f"Resource pressure detected: CPU={metrics.cpu_percent:.1f}%, "
                      f"Memory={metrics.memory_percent:.1f}%, "
                      f"GPU={metrics.gpu_memory_used/metrics.gpu_memory_total*100:.1f}%")
        
        # Find sessions to throttle or suspend
        sessions_by_priority = sorted(
            self.session_resources.values(),
            key=lambda s: (s.priority, s.last_access),
            reverse=True
        )
        
        # Throttle lowest priority sessions first
        for session in sessions_by_priority[-3:]:  # Bottom 3 sessions
            if session.status == "active":
                self._throttle_session(session.session_id)
    
    def _throttle_session(self, session_id: str):
        """Throttle a session to reduce resource usage."""
        session = self.session_resources.get(session_id)
        if session:
            # Reduce resource allocations
            session.cpu_allocation *= 0.7
            session.memory_allocation *= 0.8
            session.gpu_memory_allocation *= 0.8
            
            logger.info(f"Throttled session {session_id} due to resource pressure")
    
    def _update_session_usage(self):
        """Update resource usage for all active sessions."""
        for session_id in self.active_sessions:
            session = self.session_resources.get(session_id)
            if session:
                # Update last access time if recently active
                session.last_access = datetime.now()
    
    def _process_resource_queue(self):
        """Process waiting sessions in the resource queue."""
        while not self.resource_queue.empty() and len(self.active_sessions) < self.max_concurrent_sessions:
            try:
                priority, session_id = self.resource_queue.get_nowait()
                if session_id in self.waiting_sessions:
                    self._activate_session(session_id)
            except queue.Empty:
                break
    
    def allocate_session_resources(self, session_id: str, user_id: str, 
                                  priority: int = 5, requirements: Optional[Dict[str, Any]] = None) -> SessionResource:
        """Allocate resources for a new session."""
        requirements = requirements or {}
        
        # Calculate resource allocations based on requirements and availability
        cpu_allocation = min(requirements.get('cpu_percent', 25.0), 50.0)
        memory_allocation = requirements.get('memory_gb', 2.0) * 1024**3  # Convert GB to bytes
        gpu_memory_allocation = requirements.get('gpu_memory_gb', 1.0) * 1024**3
        max_processing_time = requirements.get('max_time_seconds', 300.0)
        
        session_resource = SessionResource(
            session_id=session_id,
            user_id=user_id,
            priority=priority,
            cpu_allocation=cpu_allocation,
            memory_allocation=memory_allocation,
            gpu_memory_allocation=gpu_memory_allocation,
            max_processing_time=max_processing_time,
            created_at=datetime.now(),
            last_access=datetime.now()
        )
        
        self.session_resources[session_id] = session_resource
        
        # Try to activate session immediately or queue it
        if len(self.active_sessions) < self.max_concurrent_sessions:
            self._activate_session(session_id)
        else:
            self._queue_session(session_id, priority)
        
        logger.info(f"Allocated resources for session {session_id} (priority {priority})")
        return session_resource
    
    def _activate_session(self, session_id: str):
        """Activate a session for processing."""
        if session_id in self.waiting_sessions:
            self.waiting_sessions.remove(session_id)
        
        self.active_sessions.add(session_id)
        session = self.session_resources[session_id]
        session.status = "active"
        
        logger.info(f"Activated session {session_id}")
    
    def _queue_session(self, session_id: str, priority: int):
        """Queue a session for later activation."""
        self.waiting_sessions.add(session_id)
        self.resource_queue.put((-priority, session_id))  # Negative for max-heap behavior
        
        session = self.session_resources[session_id]
        session.status = "queued"
        
        logger.info(f"Queued session {session_id} (priority {priority})")
    
    def deallocate_session_resources(self, session_id: str):
        """Deallocate resources for a finished session."""
        if session_id in self.active_sessions:
            self.active_sessions.remove(session_id)
        
        if session_id in self.waiting_sessions:
            self.waiting_sessions.remove(session_id)
        
        if session_id in self.session_resources:
            del self.session_resources[session_id]
        
        logger.info(f"Deallocated resources for session {session_id}")
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource allocation status."""
        metrics = self._get_resource_metrics()
        
        return {
            "system_metrics": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "gpu_memory_percent": metrics.gpu_memory_used / metrics.gpu_memory_total * 100,
                "timestamp": metrics.timestamp.isoformat()
            },
            "session_metrics": {
                "active_sessions": len(self.active_sessions),
                "waiting_sessions": len(self.waiting_sessions),
                "max_concurrent": self.max_concurrent_sessions,
                "total_sessions": len(self.session_resources)
            },
            "resource_allocations": {
                session_id: {
                    "cpu_allocation": session.cpu_allocation,
                    "memory_allocation": session.memory_allocation / 1024**3,  # Convert to GB
                    "gpu_memory_allocation": session.gpu_memory_allocation / 1024**3,
                    "priority": session.priority,
                    "status": session.status
                }
                for session_id, session in self.session_resources.items()
            }
        }

class PerformanceMonitor:
    """
    Production performance monitoring and alerting system.
    Tracks system health and generates optimization recommendations.
    """
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics_history: deque = deque(maxlen=1000)  # Keep last 1000 metrics
        self.alerts: List[Dict[str, Any]] = []
        self.recommendations: List[OptimizationRecommendation] = []
        
        # Performance thresholds
        self.thresholds = {
            "cpu_critical": 85.0,
            "cpu_warning": 70.0,
            "memory_critical": 90.0,
            "memory_warning": 75.0,
            "gpu_memory_critical": 95.0,
            "gpu_memory_warning": 80.0,
            "response_time_critical": 5.0,  # seconds
            "response_time_warning": 2.0
        }
        
        logger.info("PerformanceMonitor initialized")
    
    def record_metrics(self, metrics: ResourceMetrics, additional_data: Optional[Dict[str, Any]] = None):
        """Record performance metrics for analysis."""
        metric_data = {
            "timestamp": metrics.timestamp,
            "cpu_percent": metrics.cpu_percent,
            "memory_percent": metrics.memory_percent,
            "gpu_memory_percent": metrics.gpu_memory_used / metrics.gpu_memory_total * 100,
            "disk_usage": metrics.disk_usage,
            "network_io": metrics.network_io
        }
        
        if additional_data:
            metric_data.update(additional_data)
        
        self.metrics_history.append(metric_data)
        
        # Check for alert conditions
        self._check_alerts(metric_data)
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and generate alerts."""
        alerts_generated = []
        
        # CPU alerts
        if metrics["cpu_percent"] > self.thresholds["cpu_critical"]:
            alerts_generated.append({
                "type": "cpu_critical",
                "message": f"CPU usage critical: {metrics['cpu_percent']:.1f}%",
                "severity": "critical",
                "timestamp": metrics["timestamp"]
            })
        elif metrics["cpu_percent"] > self.thresholds["cpu_warning"]:
            alerts_generated.append({
                "type": "cpu_warning",
                "message": f"CPU usage high: {metrics['cpu_percent']:.1f}%",
                "severity": "warning",
                "timestamp": metrics["timestamp"]
            })
        
        # Memory alerts
        if metrics["memory_percent"] > self.thresholds["memory_critical"]:
            alerts_generated.append({
                "type": "memory_critical",
                "message": f"Memory usage critical: {metrics['memory_percent']:.1f}%",
                "severity": "critical",
                "timestamp": metrics["timestamp"]
            })
        elif metrics["memory_percent"] > self.thresholds["memory_warning"]:
            alerts_generated.append({
                "type": "memory_warning",
                "message": f"Memory usage high: {metrics['memory_percent']:.1f}%",
                "severity": "warning",
                "timestamp": metrics["timestamp"]
            })
        
        # GPU memory alerts
        if metrics["gpu_memory_percent"] > self.thresholds["gpu_memory_critical"]:
            alerts_generated.append({
                "type": "gpu_memory_critical",
                "message": f"GPU memory usage critical: {metrics['gpu_memory_percent']:.1f}%",
                "severity": "critical",
                "timestamp": metrics["timestamp"]
            })
        elif metrics["gpu_memory_percent"] > self.thresholds["gpu_memory_warning"]:
            alerts_generated.append({
                "type": "gpu_memory_warning",
                "message": f"GPU memory usage high: {metrics['gpu_memory_percent']:.1f}%",
                "severity": "warning",
                "timestamp": metrics["timestamp"]
            })
        
        # Add new alerts
        self.alerts.extend(alerts_generated)
        
        # Keep only recent alerts (last 100)
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Log critical alerts
        for alert in alerts_generated:
            if alert["severity"] == "critical":
                logger.error(alert["message"])
            else:
                logger.warning(alert["message"])
    
    def generate_recommendations(self) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on performance history."""
        recommendations = []
        
        if len(self.metrics_history) < 10:
            return recommendations
        
        # Analyze recent metrics
        recent_metrics = list(self.metrics_history)[-10:]
        avg_cpu = sum(m["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m["memory_percent"] for m in recent_metrics) / len(recent_metrics)
        avg_gpu = sum(m["gpu_memory_percent"] for m in recent_metrics) / len(recent_metrics)
        
        # CPU optimization recommendations
        if avg_cpu > 75.0:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"cpu_opt_{int(time.time())}",
                type="cpu_optimization",
                priority=8,
                description="Consider reducing batch sizes or implementing CPU offloading",
                impact_estimate={"cpu_reduction": 15.0, "performance_impact": -5.0},
                implementation_cost=0.3,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1)
            ))
        
        # Memory optimization recommendations
        if avg_memory > 80.0:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"memory_opt_{int(time.time())}",
                type="memory_optimization",
                priority=9,
                description="Implement memory cleanup and reduce context window sizes",
                impact_estimate={"memory_reduction": 20.0, "quality_impact": -3.0},
                implementation_cost=0.4,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=2)
            ))
        
        # GPU optimization recommendations
        if avg_gpu > 85.0:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"gpu_opt_{int(time.time())}",
                type="gpu_optimization",
                priority=10,
                description="Enable gradient checkpointing and reduce precision to FP16",
                impact_estimate={"gpu_memory_reduction": 25.0, "speed_impact": -10.0},
                implementation_cost=0.2,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=3)
            ))
        
        # Add to internal recommendations list
        self.recommendations.extend(recommendations)
        
        # Clean up old recommendations
        current_time = datetime.now()
        self.recommendations = [
            r for r in self.recommendations 
            if r.expires_at is None or r.expires_at > current_time
        ]
        
        return recommendations
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary and statistics."""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        recent_metrics = list(self.metrics_history)[-30:]  # Last 30 measurements
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "metrics_count": len(self.metrics_history),
            "recent_averages": {
                "cpu_percent": sum(m["cpu_percent"] for m in recent_metrics) / len(recent_metrics),
                "memory_percent": sum(m["memory_percent"] for m in recent_metrics) / len(recent_metrics),
                "gpu_memory_percent": sum(m["gpu_memory_percent"] for m in recent_metrics) / len(recent_metrics)
            },
            "alerts": {
                "total": len(self.alerts),
                "critical": len([a for a in self.alerts if a["severity"] == "critical"]),
                "warnings": len([a for a in self.alerts if a["severity"] == "warning"])
            },
            "recommendations": {
                "total": len(self.recommendations),
                "high_priority": len([r for r in self.recommendations if r.priority >= 8])
            }
        }
        
        return summary

class ProductionOptimizer:
    """
    Enhanced Production Optimizer with Advanced Utilities Integration
    
    Leverages ImpressionCore's advanced tools for optimal performance:
    - GPU Memory Management
    - Rich UI Enhancements  
    - Performance Optimization
    - Memory Management
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with advanced utilities integration."""
        self.config = config or {}
        self.session_manager = None
        self.resource_scheduler = ResourceScheduler()
        
        # Initialize advanced utilities
        self._init_advanced_utilities()
        
        # Performance tracking
        self.metrics_history = deque(maxlen=1000)
        self.optimization_history = deque(maxlen=100)
        
        # Status tracking
        self.is_running = False
        self.last_optimization = None
        
        if console:
            console.print("[bold green]ProductionOptimizer initialized with advanced utilities[/bold green]")
        logger.info("ProductionOptimizer initialized with enhanced capabilities")
    
    def _init_advanced_utilities(self):
        """Initialize advanced ImpressionCore utilities."""
        try:
            # GPU Memory Manager
            if RICH_AVAILABLE:
                self.gpu_manager = GPUMemoryManager()
                logger.info("GPU Memory Manager initialized")
            else:
                self.gpu_manager = None
                
            # Advanced Performance Optimizer
            if RICH_AVAILABLE:
                self.perf_optimizer = AdvancedPerformanceOptimizer()
                logger.info("Advanced Performance Optimizer initialized")
            else:
                self.perf_optimizer = None
                
            # Advanced Memory Manager
            if RICH_AVAILABLE:
                self.memory_manager = AdvancedMemoryManager()
                logger.info("Advanced Memory Manager initialized")
            else:
                self.memory_manager = None
                
        except Exception as e:
            logger.warning(f"Some advanced utilities unavailable: {e}")
            self.gpu_manager = None
            self.perf_optimizer = None
            self.memory_manager = None
    
    async def get_gpu_memory_status(self) -> Dict[str, Any]:
        """Get enhanced GPU memory status using advanced utilities."""
        try:
            if self.gpu_manager:
                # Use advanced GPU memory manager
                memory_info = get_gpu_memory_info()
                return {
                    "memory_mb": memory_info,
                    "status": "optimal" if memory_info.get("free", 0) > 1000 else "constrained",
                    "recommendations": self._get_gpu_recommendations(memory_info),
                    "source": "advanced_gpu_manager"
                }
            else:
                # Fallback to basic monitoring
                return await self._basic_gpu_monitoring()
        except Exception as e:
            logger.error(f"GPU memory status error: {e}")
            return {"error": str(e), "source": "fallback"}
    
    def _get_gpu_recommendations(self, memory_info: Dict[str, float]) -> List[str]:
        """Generate GPU optimization recommendations."""
        recommendations = []
        
        free_memory = memory_info.get("free", 0)
        total_memory = memory_info.get("total", 4096)  # Default GTX 1050 Ti
        
        if free_memory < 500:  # Less than 500MB free
            recommendations.append("Consider reducing batch size")
            recommendations.append("Enable gradient checkpointing")
            
        if free_memory < 200:  # Critical low memory
            recommendations.append("CRITICAL: Move some operations to CPU")
            recommendations.append("Clear unused tensors immediately")
            
        usage_percent = ((total_memory - free_memory) / total_memory) * 100
        if usage_percent > 85:
            recommendations.append("High GPU utilization - monitor for OOM errors")
            
        return recommendations
    
    async def _basic_gpu_monitoring(self) -> Dict[str, Any]:
        """Fallback GPU monitoring when advanced utilities unavailable."""
        try:
            import torch
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / 1024**2  # MB
                cached = torch.cuda.memory_reserved() / 1024**2    # MB
                return {
                    "memory_mb": {
                        "allocated": allocated,
                        "cached": cached,
                        "free": 4096 - cached  # Assume GTX 1050 Ti
                    },
                    "status": "basic_monitoring",
                    "source": "pytorch_basic"
                }
            else:
                return {"status": "cuda_unavailable", "source": "cpu_only"}
        except Exception as e:
            return {"error": str(e), "source": "fallback_error"}

    # ...existing code...
