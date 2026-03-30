"""
Dashboard Metrics - ImpressionCore

Advanced metrics collection and analysis system for the security dashboard.
Provides statistical analysis, trend detection, and performance monitoring
for all security components.

Features:
- Real-time metrics aggregation and statistical analysis
- Trend detection and anomaly identification in metrics
- Performance benchmarking and threshold monitoring
- Automated alerts based on metric patterns
- Memory-efficient time-series data management

Memory Budget: 15MB
Performance Target: <20ms metric processing
Hardware: Optimized for GTX 1050 Ti

Created: 2025-05-31
Author: ImpressionCore AI
"""

import asyncio
import time
import sqlite3
import json
import statistics
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
import math

# Import rich enhancements for better UX
try:
    from src.core.utils.rich_logging import RichLogger
    from src.core.utils.rich_enhancements import RichConsole
    logger = RichLogger("DashboardMetrics")
    console = RichConsole()
except ImportError:
    import logging
    logger = logging.getLogger("DashboardMetrics")
    console = None

@dataclass
class MetricSample:
    """Individual metric sample with timestamp and metadata."""
    value: Union[int, float]
    timestamp: datetime
    source: str
    category: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MetricStatistics:
    """Statistical analysis of metric values."""
    count: int
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    percentile_25: float
    percentile_75: float
    percentile_95: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    anomaly_score: float
    last_updated: datetime

@dataclass
class PerformanceBenchmark:
    """Performance benchmark for metric tracking."""
    metric_name: str
    target_value: float
    threshold_warning: float
    threshold_critical: float
    measurement_unit: str
    current_value: float
    status: str  # "optimal", "warning", "critical"
    last_measured: datetime

class MetricsAnalyzer:
    """Advanced statistical analysis for dashboard metrics."""
    
    def __init__(self, window_size: int = 100):
        """Initialize metrics analyzer."""
        self.window_size = window_size
        self.anomaly_threshold = 2.5  # Standard deviations
        
    def analyze_metric_series(self, samples: List[MetricSample]) -> MetricStatistics:
        """Perform comprehensive statistical analysis on metric series."""
        if not samples:
            return self._empty_statistics()
        
        try:
            values = [s.value for s in samples]
            timestamps = [s.timestamp for s in samples]
            
            # Basic statistics
            count = len(values)
            mean = statistics.mean(values)
            median = statistics.median(values)
            std_dev = statistics.stdev(values) if count > 1 else 0.0
            min_value = min(values)
            max_value = max(values)
            
            # Percentiles
            sorted_values = sorted(values)
            percentile_25 = self._percentile(sorted_values, 25)
            percentile_75 = self._percentile(sorted_values, 75)
            percentile_95 = self._percentile(sorted_values, 95)
            
            # Trend analysis
            trend_direction = self._analyze_trend(values, timestamps)
            
            # Anomaly detection
            anomaly_score = self._calculate_anomaly_score(values[-1], mean, std_dev) if values else 0.0
            
            return MetricStatistics(
                count=count,
                mean=mean,
                median=median,
                std_dev=std_dev,
                min_value=min_value,
                max_value=max_value,
                percentile_25=percentile_25,
                percentile_75=percentile_75,
                percentile_95=percentile_95,
                trend_direction=trend_direction,
                anomaly_score=anomaly_score,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error in metric analysis: {e}")
            return self._empty_statistics()
    
    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile from sorted values."""
        if not sorted_values:
            return 0.0
        
        k = (len(sorted_values) - 1) * (percentile / 100)
        f = math.floor(k)
        c = math.ceil(k)
        
        if f == c:
            return sorted_values[int(k)]
        
        return sorted_values[int(f)] * (c - k) + sorted_values[int(c)] * (k - f)
    
    def _analyze_trend(self, values: List[float], timestamps: List[datetime]) -> str:
        """Analyze trend direction using linear regression."""
        if len(values) < 2:
            return "stable"
        
        try:
            # Convert timestamps to numeric values (seconds since first timestamp)
            base_time = timestamps[0]
            x_values = [(t - base_time).total_seconds() for t in timestamps]
            
            # Simple linear regression
            n = len(values)
            sum_x = sum(x_values)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(x_values, values))
            sum_x2 = sum(x * x for x in x_values)
            
            # Calculate slope
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Determine trend based on slope
            if abs(slope) < 0.01:  # Very small slope threshold
                return "stable"
            elif slope > 0:
                return "increasing"
            else:
                return "decreasing"
                
        except (ZeroDivisionError, ValueError):
            return "stable"
    
    def _calculate_anomaly_score(self, value: float, mean: float, std_dev: float) -> float:
        """Calculate anomaly score based on standard deviations from mean."""
        if std_dev == 0:
            return 0.0
        
        return abs(value - mean) / std_dev
    
    def _empty_statistics(self) -> MetricStatistics:
        """Return empty statistics object."""
        return MetricStatistics(
            count=0, mean=0.0, median=0.0, std_dev=0.0,
            min_value=0.0, max_value=0.0,
            percentile_25=0.0, percentile_75=0.0, percentile_95=0.0,
            trend_direction="stable", anomaly_score=0.0,
            last_updated=datetime.now()
        )

class DashboardMetrics:
    """
    Advanced metrics collection and analysis system for security dashboard.
    Handles real-time metric processing, statistical analysis, and alerting.
    """
    
    def __init__(self, db_path: str = "dashboard_metrics.db"):
        """Initialize dashboard metrics system."""
        self.db_path = db_path
        self.is_running = False
        self.metrics_lock = threading.Lock()
        
        # Memory-optimized metric storage
        self.metric_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.current_statistics: Dict[str, MetricStatistics] = {}
        self.performance_benchmarks: Dict[str, PerformanceBenchmark] = {}
        
        # Analysis components
        self.analyzer = MetricsAnalyzer()
        
        # Processing configuration
        self.config = {
            'analysis_interval': 30,  # seconds
            'retention_hours': 48,
            'anomaly_threshold': 2.5,
            'trend_window_size': 50,
            'benchmark_check_interval': 60
        }
        
        # Performance tracking
        self.processing_metrics = {
            'analysis_times': deque(maxlen=100),
            'memory_usage': deque(maxlen=100),
            'metric_counts': deque(maxlen=100)
        }
        
        # Initialize database
        self._init_database()
        self._init_default_benchmarks()
        
        logger.info("DashboardMetrics initialized")
    
    def _init_database(self) -> None:
        """Initialize SQLite database for metrics storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Metric samples table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metric_samples (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        value REAL NOT NULL,
                        source TEXT NOT NULL,
                        category TEXT NOT NULL,
                        metadata TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        INDEX(metric_name, timestamp)
                    )
                """)
                
                # Metric statistics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metric_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        count INTEGER NOT NULL,
                        mean REAL NOT NULL,
                        median REAL NOT NULL,
                        std_dev REAL NOT NULL,
                        min_value REAL NOT NULL,
                        max_value REAL NOT NULL,
                        percentile_25 REAL NOT NULL,
                        percentile_75 REAL NOT NULL,
                        percentile_95 REAL NOT NULL,
                        trend_direction TEXT NOT NULL,
                        anomaly_score REAL NOT NULL,
                        analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Performance benchmarks table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performance_benchmarks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT UNIQUE NOT NULL,
                        target_value REAL NOT NULL,
                        threshold_warning REAL NOT NULL,
                        threshold_critical REAL NOT NULL,
                        measurement_unit TEXT NOT NULL,
                        current_value REAL,
                        status TEXT,
                        last_measured DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Metric alerts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metric_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        message TEXT NOT NULL,
                        triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        resolved_at DATETIME,
                        metadata TEXT
                    )
                """)
                
                conn.commit()
                logger.info("Metrics database initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize metrics database: {e}")
            raise
    
    def _init_default_benchmarks(self) -> None:
        """Initialize default performance benchmarks."""
        default_benchmarks = [
            PerformanceBenchmark(
                metric_name="dashboard_refresh_time",
                target_value=0.05,  # 50ms
                threshold_warning=0.1,  # 100ms
                threshold_critical=0.2,  # 200ms
                measurement_unit="seconds",
                current_value=0.0,
                status="optimal",
                last_measured=datetime.now()
            ),
            PerformanceBenchmark(
                metric_name="memory_usage_mb",
                target_value=25.0,  # 25MB
                threshold_warning=35.0,  # 35MB
                threshold_critical=45.0,  # 45MB
                measurement_unit="megabytes",
                current_value=0.0,
                status="optimal",
                last_measured=datetime.now()
            ),
            PerformanceBenchmark(
                metric_name="cpu_usage_percent",
                target_value=5.0,  # 5%
                threshold_warning=15.0,  # 15%
                threshold_critical=30.0,  # 30%
                measurement_unit="percentage",
                current_value=0.0,
                status="optimal",
                last_measured=datetime.now()
            ),
            PerformanceBenchmark(
                metric_name="active_threats",
                target_value=0.0,  # No threats
                threshold_warning=1.0,  # 1 threat
                threshold_critical=5.0,  # 5 threats
                measurement_unit="count",
                current_value=0.0,
                status="optimal",
                last_measured=datetime.now()
            )
        ]
        
        for benchmark in default_benchmarks:
            self.performance_benchmarks[benchmark.metric_name] = benchmark
    
    async def start_metrics_processing(self) -> Dict[str, Any]:
        """Start the metrics processing system."""
        if self.is_running:
            return {'status': 'already_running'}
        
        try:
            self.is_running = True
            logger.info("Starting metrics processing...")
            
            # Start background processing task
            self.processing_task = asyncio.create_task(self._processing_loop())
            
            return {
                'status': 'started',
                'benchmarks': len(self.performance_benchmarks),
                'processing_active': True
            }
            
        except Exception as e:
            self.is_running = False
            logger.error(f"Failed to start metrics processing: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def stop_metrics_processing(self) -> Dict[str, Any]:
        """Stop the metrics processing system."""
        if not self.is_running:
            return {'status': 'not_running'}
        
        try:
            self.is_running = False
            
            # Cancel processing task
            if hasattr(self, 'processing_task'):
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Metrics processing stopped")
            return {'status': 'stopped'}
            
        except Exception as e:
            logger.error(f"Error stopping metrics processing: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _processing_loop(self) -> None:
        """Main processing loop for metrics analysis."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Analyze all metric series
                await self._analyze_all_metrics()
                
                # Check performance benchmarks
                await self._check_benchmarks()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                # Track processing performance
                processing_time = time.time() - start_time
                self.processing_metrics['analysis_times'].append(processing_time)
                
                # Sleep until next analysis
                await asyncio.sleep(self.config['analysis_interval'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics processing loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _analyze_all_metrics(self) -> None:
        """Analyze all metric series and update statistics."""
        with self.metrics_lock:
            try:
                for metric_name, samples_deque in self.metric_series.items():
                    if samples_deque:
                        # Convert deque to list for analysis
                        samples = list(samples_deque)
                        
                        # Perform statistical analysis
                        statistics = self.analyzer.analyze_metric_series(samples)
                        self.current_statistics[metric_name] = statistics
                        
                        # Store statistics in database
                        await self._store_statistics(metric_name, statistics)
                        
                        # Check for anomalies and generate alerts
                        if statistics.anomaly_score > self.config['anomaly_threshold']:
                            await self._generate_anomaly_alert(metric_name, statistics)
                
            except Exception as e:
                logger.error(f"Error analyzing metrics: {e}")
    
    async def _check_benchmarks(self) -> None:
        """Check current metrics against performance benchmarks."""
        try:
            for benchmark_name, benchmark in self.performance_benchmarks.items():
                # Get current metric value
                if benchmark_name in self.metric_series:
                    samples = list(self.metric_series[benchmark_name])
                    if samples:
                        current_value = samples[-1].value
                        benchmark.current_value = current_value
                        benchmark.last_measured = datetime.now()
                        
                        # Determine status
                        if current_value <= benchmark.target_value:
                            benchmark.status = "optimal"
                        elif current_value <= benchmark.threshold_warning:
                            benchmark.status = "good"
                        elif current_value <= benchmark.threshold_critical:
                            benchmark.status = "warning"
                        else:
                            benchmark.status = "critical"
                        
                        # Generate benchmark alert if needed
                        if benchmark.status in ["warning", "critical"]:
                            await self._generate_benchmark_alert(benchmark)
                
        except Exception as e:
            logger.error(f"Error checking benchmarks: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old metric data to maintain memory efficiency."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.config['retention_hours'])
            
            # Clean up in-memory data
            with self.metrics_lock:
                for metric_name, samples_deque in self.metric_series.items():
                    # Remove old samples from deque
                    while (samples_deque and 
                           samples_deque[0].timestamp < cutoff_time):
                        samples_deque.popleft()
            
            # Clean up database data
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM metric_samples 
                    WHERE timestamp < ?
                """, (cutoff_time,))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def _store_statistics(self, metric_name: str, statistics: MetricStatistics) -> None:
        """Store metric statistics in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO metric_statistics (
                        metric_name, count, mean, median, std_dev,
                        min_value, max_value, percentile_25, percentile_75,
                        percentile_95, trend_direction, anomaly_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric_name, statistics.count, statistics.mean,
                    statistics.median, statistics.std_dev, statistics.min_value,
                    statistics.max_value, statistics.percentile_25,
                    statistics.percentile_75, statistics.percentile_95,
                    statistics.trend_direction, statistics.anomaly_score
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing statistics: {e}")
    
    async def _generate_anomaly_alert(self, metric_name: str, statistics: MetricStatistics) -> None:
        """Generate alert for metric anomaly."""
        try:
            alert_data = {
                'metric_name': metric_name,
                'alert_type': 'anomaly',
                'severity': 'high' if statistics.anomaly_score > 3.0 else 'medium',
                'message': f"Anomaly detected in {metric_name}: {statistics.anomaly_score:.2f} standard deviations from mean",
                'metadata': {
                    'anomaly_score': statistics.anomaly_score,
                    'mean': statistics.mean,
                    'std_dev': statistics.std_dev,
                    'trend': statistics.trend_direction
                }
            }
            
            # Store alert in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO metric_alerts (
                        metric_name, alert_type, severity, message, metadata
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    alert_data['metric_name'],
                    alert_data['alert_type'],
                    alert_data['severity'],
                    alert_data['message'],
                    json.dumps(alert_data['metadata'])
                ))
                conn.commit()
            
            logger.warning(f"Anomaly alert: {alert_data['message']}")
            
        except Exception as e:
            logger.error(f"Error generating anomaly alert: {e}")
    
    async def _generate_benchmark_alert(self, benchmark: PerformanceBenchmark) -> None:
        """Generate alert for benchmark threshold violation."""
        try:
            alert_data = {
                'metric_name': benchmark.metric_name,
                'alert_type': 'benchmark',
                'severity': benchmark.status,
                'message': f"{benchmark.metric_name} exceeded {benchmark.status} threshold: {benchmark.current_value} {benchmark.measurement_unit}",
                'metadata': {
                    'current_value': benchmark.current_value,
                    'target_value': benchmark.target_value,
                    'threshold_warning': benchmark.threshold_warning,
                    'threshold_critical': benchmark.threshold_critical,
                    'status': benchmark.status
                }
            }
            
            # Store alert in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO metric_alerts (
                        metric_name, alert_type, severity, message, metadata
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    alert_data['metric_name'],
                    alert_data['alert_type'],
                    alert_data['severity'],
                    alert_data['message'],
                    json.dumps(alert_data['metadata'])
                ))
                conn.commit()
            
            logger.warning(f"Benchmark alert: {alert_data['message']}")
            
        except Exception as e:
            logger.error(f"Error generating benchmark alert: {e}")
    
    def add_metric_sample(self, metric_name: str, value: Union[int, float], 
                         source: str, category: str, 
                         metadata: Dict[str, Any] = None) -> None:
        """Add a new metric sample."""
        try:
            sample = MetricSample(
                value=float(value),
                timestamp=datetime.now(),
                source=source,
                category=category,
                metadata=metadata or {}
            )
            
            with self.metrics_lock:
                self.metric_series[metric_name].append(sample)
            
            # Store in database
            asyncio.create_task(self._store_metric_sample(sample, metric_name))
            
        except Exception as e:
            logger.error(f"Error adding metric sample: {e}")
    
    async def _store_metric_sample(self, sample: MetricSample, metric_name: str) -> None:
        """Store metric sample in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO metric_samples (
                        metric_name, value, source, category, metadata, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    metric_name, sample.value, sample.source,
                    sample.category, json.dumps(sample.metadata),
                    sample.timestamp
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing metric sample: {e}")
    
    def get_metric_statistics(self, metric_name: str) -> Optional[MetricStatistics]:
        """Get current statistics for a metric."""
        return self.current_statistics.get(metric_name)
    
    def get_all_statistics(self) -> Dict[str, MetricStatistics]:
        """Get statistics for all metrics."""
        return dict(self.current_statistics)
    
    def get_performance_benchmarks(self) -> Dict[str, PerformanceBenchmark]:
        """Get all performance benchmarks."""
        return dict(self.performance_benchmarks)
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent metric alerts."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT metric_name, alert_type, severity, message, 
                           triggered_at, metadata
                    FROM metric_alerts
                    WHERE resolved_at IS NULL
                    ORDER BY triggered_at DESC
                    LIMIT ?
                """, (limit,))
                
                alerts = []
                for row in cursor.fetchall():
                    alerts.append({
                        'metric_name': row[0],
                        'alert_type': row[1],
                        'severity': row[2],
                        'message': row[3],
                        'triggered_at': row[4],
                        'metadata': json.loads(row[5]) if row[5] else {}
                    })
                
                return alerts
                
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []
    
    def get_processing_performance(self) -> Dict[str, Any]:
        """Get metrics processing performance statistics."""
        try:
            analysis_times = list(self.processing_metrics['analysis_times'])
            if not analysis_times:
                return {'status': 'no_data'}
            
            return {
                'avg_analysis_time': statistics.mean(analysis_times),
                'max_analysis_time': max(analysis_times),
                'min_analysis_time': min(analysis_times),
                'recent_analysis_time': analysis_times[-1],
                'total_analyses': len(analysis_times),
                'metrics_tracked': len(self.metric_series),
                'total_samples': sum(len(samples) for samples in self.metric_series.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting processing performance: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def cleanup(self) -> None:
        """Clean up metrics system resources."""
        try:
            self.is_running = False
            
            # Clear metric data
            with self.metrics_lock:
                self.metric_series.clear()
                self.current_statistics.clear()
                self.performance_benchmarks.clear()
            
            # Clear processing metrics
            for metric_deque in self.processing_metrics.values():
                metric_deque.clear()
            
            logger.info("DashboardMetrics cleaned up")
            
        except Exception as e:
            logger.error(f"Error during metrics cleanup: {e}")
