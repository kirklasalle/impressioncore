"""
ImpressionCore Security Monitoring Module

This module provides comprehensive security monitoring, intrusion detection,
behavioral analysis, and audit logging capabilities. Optimized for GTX 1050 Ti
hardware constraints with memory usage limits and performance monitoring.

Author: ImpressionCore Security Team
Created: 2025-01-27
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Budget: 120MB total for security monitoring
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable
from pathlib import Path
import psutil
import threading
from datetime import datetime, timedelta
import json
import sqlite3
from dataclasses import dataclass, field
from enum import Enum
import gc
import weakref

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.utils.rich_enhancements import RichStatusManager
from src.core.utils.rich_logging import RichLogger


class SecurityMonitoringConfig:
    """Configuration for security monitoring components."""
    
    # Memory management
    MAX_TOTAL_MEMORY_MB = 120  # Total memory budget for monitoring
    MAX_IDS_MEMORY_MB = 40     # Intrusion detection system
    MAX_BEHAVIORAL_MEMORY_MB = 30  # Behavioral analysis
    MAX_LOGGING_MEMORY_MB = 25     # Security logging
    MAX_ALERTS_MEMORY_MB = 15      # Alert system
    MAX_CACHE_MEMORY_MB = 10       # Caching layer
    
    # Performance thresholds
    MAX_DETECTION_LATENCY_MS = 100  # Maximum detection latency
    MAX_LOG_PROCESSING_TIME_MS = 50  # Maximum log processing time
    MAX_ALERT_GENERATION_TIME_MS = 25  # Maximum alert generation time
    
    # Database configuration
    MONITORING_DB_PATH = "data/security/monitoring.db"
    LOG_RETENTION_DAYS = 90
    ALERT_RETENTION_DAYS = 365
    
    # Monitoring intervals
    HEALTH_CHECK_INTERVAL = 30     # seconds
    MEMORY_CHECK_INTERVAL = 5      # seconds
    PERFORMANCE_LOG_INTERVAL = 60  # seconds
    
    # Alert thresholds
    FAILED_LOGIN_THRESHOLD = 5
    SUSPICIOUS_ACTIVITY_THRESHOLD = 10
    MEMORY_USAGE_THRESHOLD = 0.9
    PERFORMANCE_DEGRADATION_THRESHOLD = 0.8


class MonitoringComponentType(Enum):
    """Types of monitoring components."""
    INTRUSION_DETECTION = "intrusion_detection"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    SECURITY_LOGGER = "security_logger"
    ALERT_SYSTEM = "alert_system"
    RESOURCE_MONITOR = "resource_monitor"


@dataclass
class ComponentStatus:
    """Status information for monitoring components."""
    name: str
    component_type: MonitoringComponentType
    is_active: bool = False
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    last_heartbeat: Optional[datetime] = None
    error_count: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)


class SecurityMonitoringOrchestrator:
    """
    Main orchestrator for security monitoring components.
    
    Manages lifecycle, resource allocation, and coordination between
    intrusion detection, behavioral analysis, logging, and alerting systems.
    """
    
    def __init__(self):
        self.config = SecurityMonitoringConfig()
        self.logger = self._setup_logging()
        self.status_manager = RichStatusManager("Security Monitoring")
        
        # Component management
        self.components: Dict[str, Any] = {}
        self.component_status: Dict[str, ComponentStatus] = {}
        self.component_locks: Dict[str, threading.Lock] = {}
        
        # Resource monitoring
        self.total_memory_usage = 0.0
        self.performance_history: List[Dict[str, float]] = []
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None
        
        # Database connection
        self._db_connection: Optional[sqlite3.Connection] = None
        self._initialize_database()
        
        # Lazy loading flags
        self._ids_loaded = False
        self._behavioral_loaded = False
        self._logger_loaded = False
        self._alerts_loaded = False
        
    def _setup_logging(self) -> RichLogger:
        """Setup rich logging for the monitoring orchestrator."""
        logger = RichLogger(
            name="security_monitoring",
            level=logging.INFO,
            log_file="logs/security_monitoring.log"
        )
        return logger
    
    def _initialize_database(self):
        """Initialize the monitoring database."""
        try:
            os.makedirs(os.path.dirname(self.config.MONITORING_DB_PATH), exist_ok=True)
            self._db_connection = sqlite3.connect(
                self.config.MONITORING_DB_PATH,
                check_same_thread=False
            )
            
            # Create tables
            self._create_monitoring_tables()
            
            self.logger.info("Security monitoring database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize monitoring database: {e}")
            raise
    
    def _create_monitoring_tables(self):
        """Create necessary database tables."""
        cursor = self._db_connection.cursor()
        
        # Component status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS component_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_name TEXT NOT NULL,
                component_type TEXT NOT NULL,
                is_active BOOLEAN NOT NULL,
                memory_usage_mb REAL NOT NULL,
                cpu_usage_percent REAL NOT NULL,
                error_count INTEGER NOT NULL,
                last_heartbeat TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_name TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Security events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source_component TEXT NOT NULL,
                event_data TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self._db_connection.commit()
    
    @property
    def intrusion_detection(self):
        """Lazy loading for intrusion detection system."""
        if not self._ids_loaded:
            from .intrusion_detection import IntrusionDetectionSystem
            self.components['ids'] = IntrusionDetectionSystem()
            self._ids_loaded = True
            self.logger.info("Intrusion Detection System loaded")
        return self.components['ids']
    
    @property
    def behavioral_analysis(self):
        """Lazy loading for behavioral analysis system."""
        if not self._behavioral_loaded:
            from .behavioral_analysis import BehavioralAnalysisEngine
            self.components['behavioral'] = BehavioralAnalysisEngine()
            self._behavioral_loaded = True
            self.logger.info("Behavioral Analysis Engine loaded")
        return self.components['behavioral']
    
    @property
    def security_logger(self):
        """Lazy loading for security logger."""
        if not self._logger_loaded:
            from .security_logger import SecurityLogger
            self.components['logger'] = SecurityLogger()
            self._logger_loaded = True
            self.logger.info("Security Logger loaded")
        return self.components['logger']
    
    @property
    def alert_system(self):
        """Lazy loading for alert system."""
        if not self._alerts_loaded:
            from .alert_system import SecurityAlertSystem
            self.components['alerts'] = SecurityAlertSystem()
            self._alerts_loaded = True
            self.logger.info("Security Alert System loaded")
        return self.components['alerts']
    
    def start_monitoring(self) -> bool:
        """Start the security monitoring system."""
        try:
            self.status_manager.start("Starting security monitoring system...")
            
            # Start resource monitoring
            self._monitoring_active = True
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self._monitoring_thread.start()
            
            # Initialize core components
            self._initialize_components()
            
            self.status_manager.stop("Security monitoring system started successfully")
            self.logger.info("Security monitoring system started")
            return True
            
        except Exception as e:
            self.status_manager.stop(f"Failed to start monitoring: {e}")
            self.logger.error(f"Failed to start security monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop the security monitoring system."""
        try:
            self.status_manager.start("Stopping security monitoring system...")
            
            # Stop monitoring loop
            self._monitoring_active = False
            if self._monitoring_thread:
                self._monitoring_thread.join(timeout=5.0)
            
            # Cleanup components
            self._cleanup_components()
            
            # Close database connection
            if self._db_connection:
                self._db_connection.close()
                self._db_connection = None
            
            self.status_manager.stop("Security monitoring system stopped")
            self.logger.info("Security monitoring system stopped")
            return True
            
        except Exception as e:
            self.status_manager.stop(f"Error stopping monitoring: {e}")
            self.logger.error(f"Error stopping security monitoring: {e}")
            return False
    
    def _initialize_components(self):
        """Initialize monitoring components."""
        # Initialize with lazy loading - components will be loaded when accessed
        self.logger.info("Monitoring components ready for lazy loading")
    
    def _cleanup_components(self):
        """Cleanup all monitoring components."""
        for component_name, component in self.components.items():
            try:
                if hasattr(component, 'stop'):
                    component.stop()
                if hasattr(component, 'cleanup'):
                    component.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up {component_name}: {e}")
        
        self.components.clear()
        self.component_status.clear()
        
        # Force garbage collection
        gc.collect()
    
    def _monitoring_loop(self):
        """Main monitoring loop for resource and performance tracking."""
        while self._monitoring_active:
            try:
                # Update component status
                self._update_component_status()
                
                # Check memory usage
                self._check_memory_usage()
                
                # Log performance metrics
                self._log_performance_metrics()
                
                # Clean up old data
                self._cleanup_old_data()
                
                # Sleep for the configured interval
                threading.Event().wait(self.config.HEALTH_CHECK_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                threading.Event().wait(1.0)  # Brief pause before retry
    
    def _update_component_status(self):
        """Update status for all active components."""
        for component_name, component in self.components.items():
            try:
                # Get component memory usage
                memory_usage = self._get_component_memory_usage(component)
                
                # Update status
                status = ComponentStatus(
                    name=component_name,
                    component_type=self._get_component_type(component_name),
                    is_active=hasattr(component, 'is_active') and component.is_active,
                    memory_usage_mb=memory_usage,
                    cpu_usage_percent=0.0,  # TODO: Implement CPU monitoring
                    last_heartbeat=datetime.now()
                )
                
                self.component_status[component_name] = status
                
                # Store in database
                self._store_component_status(status)
                
            except Exception as e:
                self.logger.error(f"Error updating status for {component_name}: {e}")
    
    def _get_component_memory_usage(self, component) -> float:
        """Get memory usage for a component."""
        try:
            if hasattr(component, 'get_memory_usage'):
                return component.get_memory_usage()
            return 0.0
        except Exception:
            return 0.0
    
    def _get_component_type(self, component_name: str) -> MonitoringComponentType:
        """Get the type of a component."""
        type_mapping = {
            'ids': MonitoringComponentType.INTRUSION_DETECTION,
            'behavioral': MonitoringComponentType.BEHAVIORAL_ANALYSIS,
            'logger': MonitoringComponentType.SECURITY_LOGGER,
            'alerts': MonitoringComponentType.ALERT_SYSTEM
        }
        return type_mapping.get(component_name, MonitoringComponentType.RESOURCE_MONITOR)
    
    def _check_memory_usage(self):
        """Check total memory usage and enforce limits."""
        try:
            total_usage = sum(
                status.memory_usage_mb 
                for status in self.component_status.values()
            )
            
            self.total_memory_usage = total_usage
            
            if total_usage > self.config.MAX_TOTAL_MEMORY_MB:
                self.logger.warning(
                    f"Total memory usage ({total_usage:.1f}MB) exceeds limit "
                    f"({self.config.MAX_TOTAL_MEMORY_MB}MB)"
                )
                
                # Trigger cleanup
                self._trigger_memory_cleanup()
                
        except Exception as e:
            self.logger.error(f"Error checking memory usage: {e}")
    
    def _trigger_memory_cleanup(self):
        """Trigger memory cleanup in components."""
        for component in self.components.values():
            try:
                if hasattr(component, 'cleanup_memory'):
                    component.cleanup_memory()
            except Exception as e:
                self.logger.error(f"Error during memory cleanup: {e}")
        
        # Force garbage collection
        gc.collect()
    
    def _log_performance_metrics(self):
        """Log performance metrics to database."""
        try:
            current_metrics = {
                'total_memory_mb': self.total_memory_usage,
                'active_components': len([
                    s for s in self.component_status.values() if s.is_active
                ]),
                'timestamp': datetime.now().isoformat()
            }
            
            self.performance_history.append(current_metrics)
            
            # Keep only recent history
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-500:]
            
        except Exception as e:
            self.logger.error(f"Error logging performance metrics: {e}")
    
    def _store_component_status(self, status: ComponentStatus):
        """Store component status in database."""
        try:
            cursor = self._db_connection.cursor()
            cursor.execute("""
                INSERT INTO component_status 
                (component_name, component_type, is_active, memory_usage_mb, 
                 cpu_usage_percent, error_count, last_heartbeat)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                status.name,
                status.component_type.value,
                status.is_active,
                status.memory_usage_mb,
                status.cpu_usage_percent,
                status.error_count,
                status.last_heartbeat.isoformat() if status.last_heartbeat else None
            ))
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing component status: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data from database."""
        try:
            cursor = self._db_connection.cursor()
            
            # Clean old component status records
            cutoff_date = datetime.now() - timedelta(days=7)
            cursor.execute(
                "DELETE FROM component_status WHERE created_at < ?",
                (cutoff_date.isoformat(),)
            )
            
            # Clean old performance metrics
            cursor.execute(
                "DELETE FROM performance_metrics WHERE timestamp < ?",
                (cutoff_date.isoformat(),)
            )
            
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'monitoring_active': self._monitoring_active,
            'total_memory_usage_mb': self.total_memory_usage,
            'component_count': len(self.components),
            'active_components': len([
                s for s in self.component_status.values() if s.is_active
            ]),
            'components': {
                name: {
                    'type': status.component_type.value,
                    'active': status.is_active,
                    'memory_mb': status.memory_usage_mb,
                    'last_heartbeat': status.last_heartbeat.isoformat() 
                    if status.last_heartbeat else None
                }
                for name, status in self.component_status.items()
            },
            'performance_history': self.performance_history[-10:]  # Last 10 entries
        }


# Global monitoring orchestrator instance
_monitoring_orchestrator: Optional[SecurityMonitoringOrchestrator] = None


def get_monitoring_orchestrator() -> SecurityMonitoringOrchestrator:
    """Get the global monitoring orchestrator instance."""
    global _monitoring_orchestrator
    if _monitoring_orchestrator is None:
        _monitoring_orchestrator = SecurityMonitoringOrchestrator()
    return _monitoring_orchestrator


def start_security_monitoring() -> bool:
    """Start the security monitoring system."""
    orchestrator = get_monitoring_orchestrator()
    return orchestrator.start_monitoring()


def stop_security_monitoring() -> bool:
    """Stop the security monitoring system."""
    orchestrator = get_monitoring_orchestrator()
    return orchestrator.stop_monitoring()


def get_security_status() -> Dict[str, Any]:
    """Get current security monitoring status."""
    orchestrator = get_monitoring_orchestrator()
    return orchestrator.get_system_status()


# Export main components for external use
__all__ = [
    'SecurityMonitoringConfig',
    'MonitoringComponentType',
    'ComponentStatus',
    'SecurityMonitoringOrchestrator',
    'get_monitoring_orchestrator',
    'start_security_monitoring',
    'stop_security_monitoring',
    'get_security_status'
]
