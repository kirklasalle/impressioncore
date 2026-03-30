"""
Security Dashboard - ImpressionCore

Comprehensive security monitoring dashboard that aggregates data from all security
components and provides real-time visibility into system security status.

Features:
- Real-time threat monitoring and visualization
- Security metrics aggregation and analysis
- Interactive dashboard interface with filtering
- Integration with all security monitoring components
- Memory-optimized data processing and caching

Memory Budget: 25MB
Performance Target: <50ms refresh rate
Hardware: Optimized for GTX 1050 Ti

Created: 2025-05-31
Author: ImpressionCore AI
"""

import asyncio
import time
import sqlite3
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging

# Import rich enhancements for better UX
try:
    from src.core.utils.rich_logging import RichLogger
    from src.core.utils.rich_enhancements import RichConsole
    from src.core.utils.rich_status_animation import StatusAnimation
    logger = RichLogger("SecurityDashboard")
    console = RichConsole()
except ImportError:
    import logging
    logger = logging.getLogger("SecurityDashboard")
    console = None

@dataclass
class DashboardMetric:
    """Represents a security dashboard metric."""
    name: str
    value: Any
    timestamp: datetime
    category: str
    severity: str = "info"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SecuritySummary:
    """Summary of current security status."""
    overall_status: str  # healthy, warning, critical
    active_threats: int
    resolved_threats: int
    system_uptime: float
    last_updated: datetime
    components_status: Dict[str, str]
    risk_score: float
    compliance_status: str

class SecurityDashboard:
    """
    Main security monitoring dashboard providing real-time visibility
    into system security status and threat landscape.
    """
    
    def __init__(self, db_path: str = "security_dashboard.db"):
        """Initialize the security dashboard."""
        self.db_path = db_path
        self.is_running = False
        self.update_lock = threading.Lock()
        self.callbacks: List[Callable] = []
        
        # Memory-optimized data structures
        self.metrics_cache = deque(maxlen=1000)  # Last 1000 metrics
        self.alerts_cache = deque(maxlen=500)    # Last 500 alerts
        self.threat_cache = deque(maxlen=200)    # Last 200 threats
        
        # Performance tracking
        self.performance_metrics = {
            'refresh_times': deque(maxlen=100),
            'memory_usage': deque(maxlen=100),
            'cpu_usage': deque(maxlen=100)
        }
        
        # Component connections
        self.component_clients = {}
        self.last_component_check = {}
        
        # Dashboard state
        self.current_summary = None
        self.dashboard_config = {
            'refresh_interval': 5,
            'auto_refresh': True,
            'show_resolved': False,
            'severity_filter': ['critical', 'high', 'medium'],
            'max_display_items': 100
        }
        
        # Initialize database and components
        self._init_database()
        self._init_components()
        
        logger.info("SecurityDashboard initialized")
    
    def _init_database(self) -> None:
        """Initialize SQLite database for dashboard data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Dashboard metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dashboard_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        value TEXT NOT NULL,
                        category TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        metadata TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Dashboard sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dashboard_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        user_id TEXT,
                        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                        end_time DATETIME,
                        actions_count INTEGER DEFAULT 0,
                        last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Dashboard configuration table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dashboard_config (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        config_key TEXT UNIQUE NOT NULL,
                        config_value TEXT NOT NULL,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Performance metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Dashboard database initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize dashboard database: {e}")
            raise
    
    def _init_components(self) -> None:
        """Initialize connections to security monitoring components."""
        try:
            # Import monitoring components
            from ..monitoring import (
                get_intrusion_detection, get_behavioral_analysis, 
                get_security_logger, get_alert_system,
                get_memory_security, get_resource_monitor
            )
            
            # Initialize component connections
            self.component_clients = {
                'intrusion_detection': get_intrusion_detection(),
                'behavioral_analysis': get_behavioral_analysis(),
                'security_logger': get_security_logger(),
                'alert_system': get_alert_system(),
                'memory_security': get_memory_security(),
                'resource_monitor': get_resource_monitor()
            }
            
            # Test component connectivity
            for name, client in self.component_clients.items():
                try:
                    if hasattr(client, 'get_status'):
                        status = client.get_status()
                        self.last_component_check[name] = {
                            'status': 'connected',
                            'last_check': datetime.now(),
                            'details': status
                        }
                    else:
                        self.last_component_check[name] = {
                            'status': 'connected',
                            'last_check': datetime.now(),
                            'details': {'component': 'available'}
                        }
                except Exception as e:
                    self.last_component_check[name] = {
                        'status': 'error',
                        'last_check': datetime.now(),
                        'error': str(e)
                    }
                    logger.warning(f"Component {name} connection failed: {e}")
            
            logger.info(f"Initialized {len(self.component_clients)} security components")
            
        except Exception as e:
            logger.error(f"Failed to initialize security components: {e}")
            # Continue with limited functionality
            self.component_clients = {}
    
    async def start_dashboard(self) -> Dict[str, Any]:
        """Start the dashboard monitoring loop."""
        if self.is_running:
            return {'status': 'already_running'}
        
        try:
            self.is_running = True
            logger.info("Starting security dashboard...")
            
            # Start background monitoring task
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Generate initial summary
            await self._update_dashboard_data()
            
            return {
                'status': 'started',
                'components': len(self.component_clients),
                'monitoring_active': True
            }
            
        except Exception as e:
            self.is_running = False
            logger.error(f"Failed to start dashboard: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def stop_dashboard(self) -> Dict[str, Any]:
        """Stop the dashboard monitoring."""
        if not self.is_running:
            return {'status': 'not_running'}
        
        try:
            self.is_running = False
            
            # Cancel monitoring task
            if hasattr(self, 'monitoring_task'):
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Security dashboard stopped")
            return {'status': 'stopped'}
            
        except Exception as e:
            logger.error(f"Error stopping dashboard: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for dashboard updates."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Update dashboard data
                await self._update_dashboard_data()
                
                # Track performance
                refresh_time = time.time() - start_time
                self.performance_metrics['refresh_times'].append(refresh_time)
                
                # Sleep until next update
                await asyncio.sleep(self.dashboard_config['refresh_interval'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _update_dashboard_data(self) -> None:
        """Update dashboard data from all security components."""
        with self.update_lock:
            try:
                # Collect metrics from all components
                metrics = await self._collect_component_metrics()
                
                # Update caches
                self._update_metrics_cache(metrics)
                
                # Generate security summary
                self.current_summary = await self._generate_security_summary()
                
                # Store metrics in database
                await self._store_metrics(metrics)
                
                # Notify callbacks
                self._notify_callbacks()
                
            except Exception as e:
                logger.error(f"Error updating dashboard data: {e}")
    
    async def _collect_component_metrics(self) -> List[DashboardMetric]:
        """Collect metrics from all security monitoring components."""
        metrics = []
        
        for component_name, client in self.component_clients.items():
            try:
                if hasattr(client, 'get_metrics'):
                    component_metrics = await self._safe_call(client.get_metrics)
                    if component_metrics:
                        for metric_data in component_metrics:
                            metric = DashboardMetric(
                                name=metric_data.get('name', 'unknown'),
                                value=metric_data.get('value', 0),
                                timestamp=datetime.now(),
                                category=component_name,
                                severity=metric_data.get('severity', 'info'),
                                metadata=metric_data.get('metadata', {})
                            )
                            metrics.append(metric)
                
                # Update component status
                self.last_component_check[component_name] = {
                    'status': 'healthy',
                    'last_check': datetime.now(),
                    'metrics_count': len([m for m in metrics if m.category == component_name])
                }
                
            except Exception as e:
                logger.warning(f"Failed to collect metrics from {component_name}: {e}")
                self.last_component_check[component_name] = {
                    'status': 'error',
                    'last_check': datetime.now(),
                    'error': str(e)
                }
        
        return metrics
    
    async def _safe_call(self, func, *args, **kwargs):
        """Safely call a component function with timeout."""
        try:
            if asyncio.iscoroutinefunction(func):
                return await asyncio.wait_for(func(*args, **kwargs), timeout=2.0)
            else:
                return func(*args, **kwargs)
        except asyncio.TimeoutError:
            logger.warning(f"Timeout calling {func.__name__}")
            return None
        except Exception as e:
            logger.warning(f"Error calling {func.__name__}: {e}")
            return None
    
    def _update_metrics_cache(self, metrics: List[DashboardMetric]) -> None:
        """Update the metrics cache with new data."""
        for metric in metrics:
            self.metrics_cache.append(metric)
        
        # Cleanup old metrics to maintain memory efficiency
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=24)
        
        # Remove metrics older than 24 hours
        while (self.metrics_cache and 
               self.metrics_cache[0].timestamp < cutoff_time):
            self.metrics_cache.popleft()
    
    async def _generate_security_summary(self) -> SecuritySummary:
        """Generate current security status summary."""
        try:
            # Count threats by severity
            active_threats = len([m for m in self.metrics_cache 
                                if m.severity in ['critical', 'high'] and 
                                (datetime.now() - m.timestamp).seconds < 3600])
            
            resolved_threats = len([m for m in self.metrics_cache 
                                  if m.severity in ['resolved', 'mitigated']])
            
            # Calculate risk score (0-100)
            risk_score = min(100, active_threats * 10 + 
                           len([m for m in self.metrics_cache 
                               if m.severity == 'medium']) * 2)
            
            # Determine overall status
            if risk_score > 70:
                overall_status = "critical"
            elif risk_score > 30:
                overall_status = "warning"
            else:
                overall_status = "healthy"
            
            # Component status summary
            components_status = {}
            for name, status_info in self.last_component_check.items():
                components_status[name] = status_info.get('status', 'unknown')
            
            # Compliance status (simplified)
            compliance_status = "compliant" if risk_score < 50 else "review_required"
            
            return SecuritySummary(
                overall_status=overall_status,
                active_threats=active_threats,
                resolved_threats=resolved_threats,
                system_uptime=time.time(),  # Simplified
                last_updated=datetime.now(),
                components_status=components_status,
                risk_score=risk_score,
                compliance_status=compliance_status
            )
            
        except Exception as e:
            logger.error(f"Error generating security summary: {e}")
            return SecuritySummary(
                overall_status="error",
                active_threats=0,
                resolved_threats=0,
                system_uptime=0,
                last_updated=datetime.now(),
                components_status={},
                risk_score=0,
                compliance_status="unknown"
            )
    
    async def _store_metrics(self, metrics: List[DashboardMetric]) -> None:
        """Store metrics in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for metric in metrics:
                    cursor.execute("""
                        INSERT INTO dashboard_metrics 
                        (name, value, category, severity, metadata, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        metric.name,
                        json.dumps(metric.value),
                        metric.category,
                        metric.severity,
                        json.dumps(metric.metadata),
                        metric.timestamp
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    def _notify_callbacks(self) -> None:
        """Notify registered callbacks of dashboard updates."""
        for callback in self.callbacks:
            try:
                callback(self.current_summary)
            except Exception as e:
                logger.warning(f"Error in dashboard callback: {e}")
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for dashboard updates."""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
            logger.info("Dashboard callback registered")
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a dashboard callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            logger.info("Dashboard callback unregistered")
    
    def get_current_summary(self) -> Optional[SecuritySummary]:
        """Get the current security summary."""
        return self.current_summary
    
    def get_recent_metrics(self, category: str = None, 
                          severity: str = None, 
                          limit: int = 100) -> List[DashboardMetric]:
        """Get recent metrics with optional filtering."""
        metrics = list(self.metrics_cache)
        
        # Apply filters
        if category:
            metrics = [m for m in metrics if m.category == category]
        
        if severity:
            metrics = [m for m in metrics if m.severity == severity]
        
        # Sort by timestamp (newest first) and limit
        metrics.sort(key=lambda x: x.timestamp, reverse=True)
        return metrics[:limit]
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get status of all security components."""
        return dict(self.last_component_check)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get dashboard performance metrics."""
        if not self.performance_metrics['refresh_times']:
            return {'status': 'no_data'}
        
        refresh_times = list(self.performance_metrics['refresh_times'])
        
        return {
            'avg_refresh_time': sum(refresh_times) / len(refresh_times),
            'max_refresh_time': max(refresh_times),
            'min_refresh_time': min(refresh_times),
            'recent_refresh_time': refresh_times[-1] if refresh_times else 0,
            'total_refreshes': len(refresh_times)
        }
    
    def update_config(self, **kwargs) -> Dict[str, Any]:
        """Update dashboard configuration."""
        try:
            for key, value in kwargs.items():
                if key in self.dashboard_config:
                    self.dashboard_config[key] = value
                    logger.info(f"Updated dashboard config: {key} = {value}")
                else:
                    logger.warning(f"Unknown config key: {key}")
            
            return {'status': 'updated', 'config': self.dashboard_config}
            
        except Exception as e:
            logger.error(f"Error updating dashboard config: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def export_dashboard_data(self, format: str = 'json', 
                             hours: int = 24) -> Dict[str, Any]:
        """Export dashboard data in specified format."""
        try:
            # Get metrics from the last N hours
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in self.metrics_cache 
                            if m.timestamp > cutoff_time]
            
            export_data = {
                'summary': asdict(self.current_summary) if self.current_summary else {},
                'metrics': [asdict(m) for m in recent_metrics],
                'component_status': self.get_component_status(),
                'performance': self.get_performance_metrics(),
                'export_timestamp': datetime.now().isoformat(),
                'hours_covered': hours
            }
            
            if format.lower() == 'json':
                return {
                    'status': 'success',
                    'format': 'json',
                    'data': export_data
                }
            else:
                return {
                    'status': 'error',
                    'error': f'Unsupported format: {format}'
                }
                
        except Exception as e:
            logger.error(f"Error exporting dashboard data: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def cleanup(self) -> None:
        """Clean up dashboard resources."""
        try:
            self.is_running = False
            
            # Clear caches
            self.metrics_cache.clear()
            self.alerts_cache.clear()
            self.threat_cache.clear()
            
            # Clear component connections
            self.component_clients.clear()
            self.last_component_check.clear()
            
            # Clear callbacks
            self.callbacks.clear()
            
            logger.info("SecurityDashboard cleaned up")
            
        except Exception as e:
            logger.error(f"Error during dashboard cleanup: {e}")
