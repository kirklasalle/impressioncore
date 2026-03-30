"""
Security Dashboard Module - ImpressionCore

This module provides a comprehensive security monitoring dashboard that integrates
with all security components to provide real-time visibility into system security
status, threats, and performance metrics.

Components:
- SecurityDashboard: Main dashboard interface and data aggregation
- DashboardMetrics: Security metrics collection and analysis
- AlertVisualization: Real-time alert and threat visualization
- ComplianceReporting: Compliance status and audit reporting

Memory Budget: 40MB (optimized for GTX 1050 Ti)
Security Level: High
Performance Target: <50ms dashboard refresh rate

Created: 2025-05-31
Author: ImpressionCore AI
"""

from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass

# Configure module logger
logger = logging.getLogger(__name__)

@dataclass
class DashboardConfig:
    """Configuration for security dashboard components."""
    # Dashboard settings
    refresh_interval: int = 5  # seconds
    max_metrics_history: int = 1000
    chart_update_interval: int = 2  # seconds
    
    # Memory constraints
    max_memory_usage: int = 40 * 1024 * 1024  # 40MB
    metrics_cache_size: int = 500
    alert_display_limit: int = 100
    
    # Performance settings
    async_processing: bool = True
    batch_size: int = 50
    compression_enabled: bool = True
    
    # Security settings
    sanitize_display_data: bool = True
    mask_sensitive_info: bool = True
    audit_dashboard_access: bool = True
    
    # Integration settings
    enable_external_apis: bool = False
    webhook_timeout: int = 5  # seconds
    export_formats: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.export_formats is None:
            self.export_formats = ['json', 'csv', 'pdf']

# Global dashboard configuration
_dashboard_config = DashboardConfig()

def get_dashboard_config() -> DashboardConfig:
    """Get the current dashboard configuration."""
    return _dashboard_config

def update_dashboard_config(**kwargs) -> None:
    """Update dashboard configuration parameters."""
    global _dashboard_config
    for key, value in kwargs.items():
        if hasattr(_dashboard_config, key):
            setattr(_dashboard_config, key, value)
            logger.info(f"Updated dashboard config: {key} = {value}")
        else:
            logger.warning(f"Unknown dashboard config parameter: {key}")

# Lazy imports for memory optimization
_security_dashboard = None
_dashboard_metrics = None
_alert_visualization = None
_compliance_reporting = None

def get_security_dashboard():
    """Get SecurityDashboard instance with lazy loading."""
    global _security_dashboard
    if _security_dashboard is None:
        from .security_dashboard import SecurityDashboard
        _security_dashboard = SecurityDashboard()
        logger.info("SecurityDashboard initialized")
    return _security_dashboard

def get_dashboard_metrics():
    """Get DashboardMetrics instance with lazy loading."""
    global _dashboard_metrics
    if _dashboard_metrics is None:
        from .dashboard_metrics import DashboardMetrics
        _dashboard_metrics = DashboardMetrics()
        logger.info("DashboardMetrics initialized")
    return _dashboard_metrics

def get_alert_visualization():
    """Get AlertVisualization instance with lazy loading."""
    global _alert_visualization
    if _alert_visualization is None:
        from .alert_visualization import AlertVisualization
        _alert_visualization = AlertVisualization()
        logger.info("AlertVisualization initialized")
    return _alert_visualization

def get_compliance_reporting():
    """Get ComplianceReporting instance with lazy loading."""
    global _compliance_reporting
    if _compliance_reporting is None:
        from .compliance_reporting import ComplianceReporting
        _compliance_reporting = ComplianceReporting()
        logger.info("ComplianceReporting initialized")
    return _compliance_reporting

def initialize_dashboard_module() -> Dict[str, Any]:
    """
    Initialize the security dashboard module.
    
    Returns:
        Dict containing initialization status and metrics
    """
    try:
        logger.info("Initializing security dashboard module...")
        
        # Initialize core components
        dashboard = get_security_dashboard()
        metrics = get_dashboard_metrics()
        
        # Verify memory usage
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        status = {
            'status': 'initialized',
            'components': {
                'security_dashboard': bool(dashboard),
                'dashboard_metrics': bool(metrics)
            },
            'memory_usage_mb': round(memory_mb, 2),
            'config': {
                'refresh_interval': _dashboard_config.refresh_interval,
                'max_memory_mb': _dashboard_config.max_memory_usage / 1024 / 1024,
                'async_processing': _dashboard_config.async_processing
            }
        }
        
        logger.info("Security dashboard module initialized successfully")
        return status
        
    except Exception as e:
        logger.error(f"Failed to initialize dashboard module: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'components': {}
        }

def cleanup_dashboard_module() -> None:
    """Clean up dashboard module resources."""
    global _security_dashboard, _dashboard_metrics, _alert_visualization, _compliance_reporting
    
    try:
        # Cleanup components
        if _security_dashboard:
            _security_dashboard.cleanup()
            _security_dashboard = None
            
        if _dashboard_metrics:
            _dashboard_metrics.cleanup()
            _dashboard_metrics = None
            
        if _alert_visualization:
            _alert_visualization.cleanup()
            _alert_visualization = None
            
        if _compliance_reporting:
            _compliance_reporting.cleanup()
            _compliance_reporting = None
            
        logger.info("Security dashboard module cleaned up")
        
    except Exception as e:
        logger.error(f"Error during dashboard module cleanup: {e}")

# Module metadata
__version__ = "1.0.0"
__author__ = "ImpressionCore AI"
__created__ = "2025-05-31"

# Export public interface
__all__ = [
    'DashboardConfig',
    'get_dashboard_config',
    'update_dashboard_config',
    'get_security_dashboard',
    'get_dashboard_metrics',
    'get_alert_visualization',
    'get_compliance_reporting',
    'initialize_dashboard_module',
    'cleanup_dashboard_module'
]
