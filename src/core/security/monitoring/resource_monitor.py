"""
ImpressionCore Resource Security Monitor

Comprehensive system resource monitoring for security anomaly detection,
performance optimization, and threat identification. Designed specifically
for GTX 1050 Ti hardware constraints with efficient resource utilization.

Author: ImpressionCore Development Team
Created: 2025-01-11
Memory Target: 20MB maximum (GTX 1050 Ti optimization)
"""

import asyncio
import json
import psutil
import sqlite3
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from src.core.utils.rich_logging import RichLogger

# Resource types for monitoring
class ResourceType(Enum):
    CPU = auto()
    MEMORY = auto()
    GPU = auto()
    DISK = auto()
    NETWORK = auto()
    PROCESS = auto()
    THREAD = auto()
    FILE_HANDLE = auto()
    SOCKET = auto()

# Anomaly types for resource monitoring
class ResourceAnomalyType(Enum):
    EXCESSIVE_USAGE = auto()
    RAPID_CONSUMPTION = auto()
    SUSPICIOUS_PATTERN = auto()
    RESOURCE_EXHAUSTION = auto()
    UNAUTHORIZED_ACCESS = auto()
    PERFORMANCE_DEGRADATION = auto()
    RESOURCE_LEAK = auto()

@dataclass
class ResourceUsage:
    """Resource usage measurement"""
    resource_type: ResourceType
    timestamp: datetime
    value: float
    percentage: float
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourceAnomaly:
    """Resource usage anomaly"""
    id: str
    timestamp: datetime
    resource_type: ResourceType
    anomaly_type: ResourceAnomalyType
    severity: int  # 1-5 scale
    confidence: float  # 0.0-1.0
    description: str
    current_value: float
    baseline_value: float
    deviation_score: float
    affected_processes: List[int] = field(default_factory=list)
    indicators: Dict[str, Any] = field(default_factory=dict)
    mitigation_suggestions: List[str] = field(default_factory=list)

@dataclass
class ProcessResourceProfile:
    """Process resource usage profile"""
    pid: int
    name: str
    cpu_usage: float
    memory_usage: int
    memory_percentage: float
    disk_io_read: int
    disk_io_write: int
    network_io_sent: int
    network_io_recv: int
    file_handles: int
    threads_count: int
    creation_time: datetime
    last_updated: datetime

class ResourceBaseline:
    """
    Resource usage baseline calculator and anomaly detector
    """
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.measurements = defaultdict(lambda: deque(maxlen=history_size))
        self.baselines = {}
        self.thresholds = {}
        self.logger = RichLogger("ResourceBaseline")
    
    def add_measurement(self, resource_type: ResourceType, value: float, timestamp: datetime = None):
        """Add a resource measurement"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.measurements[resource_type].append({
            'value': value,
            'timestamp': timestamp
        })
        
        # Update baseline if we have enough data
        if len(self.measurements[resource_type]) >= 50:  # Minimum 50 samples
            self._update_baseline(resource_type)
    
    def _update_baseline(self, resource_type: ResourceType):
        """Update baseline statistics for resource type"""
        try:
            values = [m['value'] for m in self.measurements[resource_type]]
            
            # Calculate baseline statistics
            self.baselines[resource_type] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'median': np.median(values),
                'percentile_95': np.percentile(values, 95),
                'percentile_99': np.percentile(values, 99),
                'min': np.min(values),
                'max': np.max(values),
                'updated_at': datetime.now()
            }
            
            # Calculate dynamic thresholds
            mean = self.baselines[resource_type]['mean']
            std = self.baselines[resource_type]['std']
            
            self.thresholds[resource_type] = {
                'warning': mean + 2 * std,  # 2 sigma
                'critical': mean + 3 * std,  # 3 sigma
                'severe': self.baselines[resource_type]['percentile_99']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update baseline for {resource_type}: {e}")
    
    def detect_anomaly(self, resource_type: ResourceType, value: float) -> Optional[Dict[str, Any]]:
        """Detect if a value is anomalous"""
        if resource_type not in self.baselines:
            return None
        
        try:
            baseline = self.baselines[resource_type]
            thresholds = self.thresholds[resource_type]
            
            # Calculate z-score
            if baseline['std'] > 0:
                z_score = (value - baseline['mean']) / baseline['std']
            else:
                z_score = 0
            
            # Determine anomaly level
            anomaly_level = None
            if value > thresholds['severe']:
                anomaly_level = 'severe'
            elif value > thresholds['critical']:
                anomaly_level = 'critical'
            elif value > thresholds['warning']:
                anomaly_level = 'warning'
            
            if anomaly_level:
                return {
                    'anomaly_level': anomaly_level,
                    'z_score': z_score,
                    'current_value': value,
                    'baseline_mean': baseline['mean'],
                    'baseline_std': baseline['std'],
                    'threshold_exceeded': thresholds[anomaly_level],
                    'deviation_percentage': ((value - baseline['mean']) / baseline['mean']) * 100 if baseline['mean'] > 0 else 0
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to detect anomaly for {resource_type}: {e}")
            return None

class ProcessMonitor:
    """
    Process-specific resource monitoring
    """
    
    def __init__(self, max_processes: int = 500):
        self.max_processes = max_processes
        self.process_profiles = {}
        self.suspicious_processes = set()
        self.process_history = defaultdict(lambda: deque(maxlen=100))
        self.logger = RichLogger("ProcessMonitor")
    
    def scan_processes(self) -> List[ProcessResourceProfile]:
        """Scan all processes and update resource profiles"""
        try:
            current_profiles = []
            current_time = datetime.now()
            
            # Get all running processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 
                                           'io_counters', 'num_threads', 'create_time']):
                try:
                    info = proc.info
                    pid = info['pid']
                    
                    # Skip system processes if we have too many
                    if len(current_profiles) >= self.max_processes:
                        break
                    
                    # Get detailed process information
                    memory_info = info['memory_info']
                    io_counters = info.get('io_counters')
                    
                    # Get network IO (if available)
                    network_io_sent = 0
                    network_io_recv = 0
                    try:
                        net_io = proc.connections()
                        # This would need actual network monitoring implementation
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                    
                    # Get file handles count
                    file_handles = 0
                    try:
                        file_handles = proc.num_fds() if hasattr(proc, 'num_fds') else len(proc.open_files())
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                    
                    # Create process profile
                    profile = ProcessResourceProfile(
                        pid=pid,
                        name=info['name'],
                        cpu_usage=info['cpu_percent'] or 0.0,
                        memory_usage=memory_info.rss if memory_info else 0,
                        memory_percentage=proc.memory_percent(),
                        disk_io_read=io_counters.read_bytes if io_counters else 0,
                        disk_io_write=io_counters.write_bytes if io_counters else 0,
                        network_io_sent=network_io_sent,
                        network_io_recv=network_io_recv,
                        file_handles=file_handles,
                        threads_count=info['num_threads'] or 1,
                        creation_time=datetime.fromtimestamp(info['create_time']) if info['create_time'] else current_time,
                        last_updated=current_time
                    )
                    
                    current_profiles.append(profile)
                    self.process_profiles[pid] = profile
                    self.process_history[pid].append(profile)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    self.logger.warning(f"Error getting process info for PID {pid}: {e}")
                    continue
            
            # Clean up old processes
            active_pids = {p.pid for p in current_profiles}
            old_pids = set(self.process_profiles.keys()) - active_pids
            for old_pid in old_pids:
                if old_pid in self.process_profiles:
                    del self.process_profiles[old_pid]
            
            return current_profiles
            
        except Exception as e:
            self.logger.error(f"Error scanning processes: {e}")
            return []
    
    def detect_suspicious_processes(self, profiles: List[ProcessResourceProfile]) -> List[ProcessResourceProfile]:
        """Detect potentially suspicious processes"""
        suspicious = []
        
        try:
            for profile in profiles:
                suspicion_score = 0
                reasons = []
                
                # High CPU usage
                if profile.cpu_usage > 80:
                    suspicion_score += 2
                    reasons.append(f"High CPU usage: {profile.cpu_usage:.1f}%")
                
                # High memory usage
                if profile.memory_percentage > 20:  # >20% of system memory
                    suspicion_score += 2
                    reasons.append(f"High memory usage: {profile.memory_percentage:.1f}%")
                
                # Excessive file handles
                if profile.file_handles > 1000:
                    suspicion_score += 1
                    reasons.append(f"Many file handles: {profile.file_handles}")
                
                # Excessive threads
                if profile.threads_count > 100:
                    suspicion_score += 1
                    reasons.append(f"Many threads: {profile.threads_count}")
                
                # High disk I/O
                if profile.disk_io_write > 100 * 1024 * 1024:  # >100MB write
                    suspicion_score += 1
                    reasons.append(f"High disk write: {profile.disk_io_write:,} bytes")
                
                # Suspicious process names
                suspicious_names = ['cmd.exe', 'powershell.exe', 'nc.exe', 'telnet.exe', 'ftp.exe']
                if any(name.lower() in profile.name.lower() for name in suspicious_names):
                    suspicion_score += 1
                    reasons.append(f"Suspicious process name: {profile.name}")
                
                # Recently created processes with high resource usage
                age = datetime.now() - profile.creation_time
                if age.total_seconds() < 300 and (profile.cpu_usage > 50 or profile.memory_percentage > 10):
                    suspicion_score += 1
                    reasons.append("Recently created with high resource usage")
                
                # Mark as suspicious if score is high enough
                if suspicion_score >= 3:
                    self.suspicious_processes.add(profile.pid)
                    suspicious.append(profile)
                    profile.additional_metrics = {'suspicion_score': suspicion_score, 'reasons': reasons}
            
            return suspicious
            
        except Exception as e:
            self.logger.error(f"Error detecting suspicious processes: {e}")
            return []
    
    def get_process_trends(self, pid: int, metric: str = 'cpu_usage') -> Dict[str, Any]:
        """Get trend analysis for a specific process"""
        try:
            if pid not in self.process_history:
                return {}
            
            history = list(self.process_history[pid])
            if len(history) < 5:
                return {'status': 'insufficient_data'}
            
            # Extract metric values
            if metric == 'cpu_usage':
                values = [p.cpu_usage for p in history]
            elif metric == 'memory_usage':
                values = [p.memory_usage for p in history]
            elif metric == 'memory_percentage':
                values = [p.memory_percentage for p in history]
            else:
                return {'status': 'unknown_metric'}
            
            # Calculate trend statistics
            timestamps = [p.last_updated for p in history]
            time_diffs = [(timestamps[i] - timestamps[0]).total_seconds() for i in range(len(timestamps))]
            
            # Linear regression for trend
            if len(values) >= 3:
                trend_slope = np.polyfit(time_diffs, values, 1)[0]
            else:
                trend_slope = 0
            
            return {
                'metric': metric,
                'current_value': values[-1],
                'average_value': np.mean(values),
                'trend_slope': trend_slope,
                'min_value': min(values),
                'max_value': max(values),
                'data_points': len(values),
                'time_span_seconds': time_diffs[-1] if time_diffs else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting process trends for PID {pid}: {e}")
            return {'status': 'error', 'error': str(e)}

class SystemResourceMonitor:
    """
    Main system resource monitoring class
    """
    
    def __init__(self, config_dir: str = "src/security/monitoring/config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.logger = RichLogger("SystemResourceMonitor")
        self.baseline_analyzer = ResourceBaseline()
        self.process_monitor = ProcessMonitor()
        
        # Monitoring state
        self.monitoring_active = False
        self.resource_history = defaultdict(lambda: deque(maxlen=2000))
        self.anomalies = deque(maxlen=1000)
        self.alert_history = deque(maxlen=500)
        
        # Configuration
        self.config = {
            'monitoring_interval': 10,  # seconds
            'cpu_threshold': 90,        # percentage
            'memory_threshold': 85,     # percentage
            'gpu_threshold': 90,        # percentage
            'disk_threshold': 90,       # percentage
            'network_threshold': 100,   # Mbps
            'process_scan_interval': 30, # seconds
            'anomaly_sensitivity': 0.8,  # 0.0-1.0
            'enable_process_monitoring': True,
            'enable_network_monitoring': True,
            'max_memory_usage': 20 * 1024 * 1024  # 20MB limit
        }
        
        # Performance tracking
        self.performance_stats = {
            'monitoring_cycles': 0,
            'anomalies_detected': 0,
            'suspicious_processes_found': 0,
            'alerts_generated': 0,
            'average_cycle_time': 0.0
        }
        
        # Threading
        self.monitoring_thread: Optional[threading.Thread] = None
        self.process_monitoring_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Database setup
        self.db_path = self.config_dir / "resource_monitoring.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for resource monitoring"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Resource usage table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS resource_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        percentage REAL NOT NULL,
                        process_id INTEGER,
                        process_name TEXT,
                        additional_metrics TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Resource anomalies table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS resource_anomalies (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        anomaly_type TEXT NOT NULL,
                        severity INTEGER NOT NULL,
                        confidence REAL NOT NULL,
                        description TEXT,
                        current_value REAL,
                        baseline_value REAL,
                        deviation_score REAL,
                        affected_processes TEXT,
                        indicators TEXT,
                        mitigation_suggestions TEXT,
                        resolved BOOLEAN DEFAULT FALSE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Process profiles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS process_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        pid INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        cpu_usage REAL,
                        memory_usage INTEGER,
                        memory_percentage REAL,
                        disk_io_read INTEGER,
                        disk_io_write INTEGER,
                        network_io_sent INTEGER,
                        network_io_recv INTEGER,
                        file_handles INTEGER,
                        threads_count INTEGER,
                        creation_time TEXT,
                        is_suspicious BOOLEAN DEFAULT FALSE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_resource_usage_timestamp ON resource_usage(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_resource_usage_type ON resource_usage(resource_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON resource_anomalies(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_process_profiles_pid ON process_profiles(pid)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_process_profiles_timestamp ON process_profiles(timestamp)')
                
                conn.commit()
                self.logger.info("Resource monitoring database initialized")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring_active:
            self.logger.warning("Resource monitoring already active")
            return
        
        self.monitoring_active = True
        self.stop_event.clear()
        
        # Start main monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Start process monitoring thread if enabled
        if self.config['enable_process_monitoring']:
            self.process_monitoring_thread = threading.Thread(target=self._process_monitoring_loop, daemon=True)
            self.process_monitoring_thread.start()
        
        self.logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self.stop_event.set()
        
        # Wait for threads to complete
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        if self.process_monitoring_thread:
            self.process_monitoring_thread.join(timeout=10)
        
        self.logger.info("Resource monitoring stopped")
    
    def _monitoring_loop(self):
        """Main resource monitoring loop"""
        while self.monitoring_active and not self.stop_event.is_set():
            try:
                start_time = time.time()
                
                # Collect resource measurements
                measurements = self._collect_resource_measurements()
                
                # Store measurements
                for measurement in measurements:
                    self.resource_history[measurement.resource_type].append(measurement)
                    self.baseline_analyzer.add_measurement(
                        measurement.resource_type, 
                        measurement.value, 
                        measurement.timestamp
                    )
                    self._store_measurement_in_db(measurement)
                
                # Detect anomalies
                anomalies = self._detect_resource_anomalies(measurements)
                for anomaly in anomalies:
                    self.anomalies.append(anomaly)
                    self._store_anomaly_in_db(anomaly)
                    self._handle_resource_anomaly(anomaly)
                
                # Update performance stats
                cycle_time = time.time() - start_time
                self.performance_stats['monitoring_cycles'] += 1
                self.performance_stats['anomalies_detected'] += len(anomalies)
                self.performance_stats['average_cycle_time'] = (
                    (self.performance_stats['average_cycle_time'] * 
                     (self.performance_stats['monitoring_cycles'] - 1) + cycle_time) /
                    self.performance_stats['monitoring_cycles']
                )
                
                # Wait for next cycle
                self.stop_event.wait(self.config['monitoring_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                self.stop_event.wait(5)  # Wait before retrying
    
    def _process_monitoring_loop(self):
        """Process monitoring loop"""
        while self.monitoring_active and not self.stop_event.is_set():
            try:
                # Scan processes
                profiles = self.process_monitor.scan_processes()
                
                # Detect suspicious processes
                suspicious_processes = self.process_monitor.detect_suspicious_processes(profiles)
                self.performance_stats['suspicious_processes_found'] += len(suspicious_processes)
                
                # Store process profiles
                for profile in profiles:
                    self._store_process_profile_in_db(profile, profile.pid in [p.pid for p in suspicious_processes])
                
                # Handle suspicious processes
                for suspicious_process in suspicious_processes:
                    self._handle_suspicious_process(suspicious_process)
                
                # Wait for next scan
                self.stop_event.wait(self.config['process_scan_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in process monitoring loop: {e}")
                self.stop_event.wait(10)  # Wait before retrying
    
    def _collect_resource_measurements(self) -> List[ResourceUsage]:
        """Collect current resource measurements"""
        measurements = []
        current_time = datetime.now()
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            measurements.append(ResourceUsage(
                resource_type=ResourceType.CPU,
                timestamp=current_time,
                value=cpu_percent,
                percentage=cpu_percent,
                additional_metrics={'cpu_count': psutil.cpu_count()}
            ))
            
            # Memory usage
            memory = psutil.virtual_memory()
            measurements.append(ResourceUsage(
                resource_type=ResourceType.MEMORY,
                timestamp=current_time,
                value=memory.used,
                percentage=memory.percent,
                additional_metrics={
                    'total': memory.total,
                    'available': memory.available,
                    'cached': getattr(memory, 'cached', 0)
                }
            ))
            
            # GPU usage (simulated for GTX 1050 Ti)
            try:
                # This would integrate with actual GPU monitoring
                import random
                gpu_usage = random.uniform(10, 80)  # Simulate GPU usage
                measurements.append(ResourceUsage(
                    resource_type=ResourceType.GPU,
                    timestamp=current_time,
                    value=gpu_usage,
                    percentage=gpu_usage,
                    additional_metrics={'gpu_model': 'GTX 1050 Ti'}
                ))
            except Exception:
                pass
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            measurements.append(ResourceUsage(
                resource_type=ResourceType.DISK,
                timestamp=current_time,
                value=disk_usage.used,
                percentage=(disk_usage.used / disk_usage.total) * 100,
                additional_metrics={
                    'total': disk_usage.total,
                    'free': disk_usage.free
                }
            ))
            
            # Network usage (if enabled)
            if self.config['enable_network_monitoring']:
                try:
                    net_io = psutil.net_io_counters()
                    # Calculate network rate (this would need historical data)
                    measurements.append(ResourceUsage(
                        resource_type=ResourceType.NETWORK,
                        timestamp=current_time,
                        value=net_io.bytes_sent + net_io.bytes_recv,
                        percentage=0,  # Would need to calculate based on bandwidth
                        additional_metrics={
                            'bytes_sent': net_io.bytes_sent,
                            'bytes_recv': net_io.bytes_recv,
                            'packets_sent': net_io.packets_sent,
                            'packets_recv': net_io.packets_recv
                        }
                    ))
                except Exception as e:
                    self.logger.warning(f"Failed to get network usage: {e}")
            
        except Exception as e:
            self.logger.error(f"Error collecting resource measurements: {e}")
        
        return measurements
    
    def _detect_resource_anomalies(self, measurements: List[ResourceUsage]) -> List[ResourceAnomaly]:
        """Detect resource usage anomalies"""
        anomalies = []
        
        try:
            for measurement in measurements:
                # Check static thresholds
                threshold_exceeded = False
                if measurement.resource_type == ResourceType.CPU and measurement.percentage > self.config['cpu_threshold']:
                    threshold_exceeded = True
                elif measurement.resource_type == ResourceType.MEMORY and measurement.percentage > self.config['memory_threshold']:
                    threshold_exceeded = True
                elif measurement.resource_type == ResourceType.GPU and measurement.percentage > self.config['gpu_threshold']:
                    threshold_exceeded = True
                elif measurement.resource_type == ResourceType.DISK and measurement.percentage > self.config['disk_threshold']:
                    threshold_exceeded = True
                
                if threshold_exceeded:
                    anomaly = ResourceAnomaly(
                        id=f"{measurement.resource_type.name.lower()}_threshold_{int(time.time())}",
                        timestamp=measurement.timestamp,
                        resource_type=measurement.resource_type,
                        anomaly_type=ResourceAnomalyType.EXCESSIVE_USAGE,
                        severity=3,
                        confidence=0.9,
                        description=f"{measurement.resource_type.name} usage exceeded threshold: {measurement.percentage:.1f}%",
                        current_value=measurement.value,
                        baseline_value=0,  # Would be calculated from baseline
                        deviation_score=measurement.percentage,
                        indicators={'threshold_exceeded': True, 'percentage': measurement.percentage},
                        mitigation_suggestions=[f"Investigate high {measurement.resource_type.name.lower()} usage", "Check for resource-intensive processes"]
                    )
                    anomalies.append(anomaly)
                
                # Check baseline anomalies
                baseline_anomaly = self.baseline_analyzer.detect_anomaly(measurement.resource_type, measurement.value)
                if baseline_anomaly and baseline_anomaly['anomaly_level'] in ['critical', 'severe']:
                    severity = 4 if baseline_anomaly['anomaly_level'] == 'severe' else 3
                    anomaly = ResourceAnomaly(
                        id=f"{measurement.resource_type.name.lower()}_baseline_{int(time.time())}",
                        timestamp=measurement.timestamp,
                        resource_type=measurement.resource_type,
                        anomaly_type=ResourceAnomalyType.SUSPICIOUS_PATTERN,
                        severity=severity,
                        confidence=min(0.9, abs(baseline_anomaly['z_score']) / 3.0),
                        description=f"{measurement.resource_type.name} usage anomaly: {baseline_anomaly['deviation_percentage']:.1f}% deviation from baseline",
                        current_value=measurement.value,
                        baseline_value=baseline_anomaly['baseline_mean'],
                        deviation_score=abs(baseline_anomaly['z_score']),
                        indicators=baseline_anomaly,
                        mitigation_suggestions=["Investigate unusual resource usage pattern", "Check for system changes or new processes"]
                    )
                    anomalies.append(anomaly)
            
            # Check for rapid consumption patterns
            rapid_consumption_anomalies = self._detect_rapid_consumption()
            anomalies.extend(rapid_consumption_anomalies)
            
        except Exception as e:
            self.logger.error(f"Error detecting resource anomalies: {e}")
        
        return anomalies
    
    def _detect_rapid_consumption(self) -> List[ResourceAnomaly]:
        """Detect rapid resource consumption patterns"""
        anomalies = []
        
        try:
            for resource_type, history in self.resource_history.items():
                if len(history) < 5:
                    continue
                
                # Get recent measurements
                recent = list(history)[-5:]
                values = [m.value for m in recent]
                
                # Calculate rate of change
                if len(values) >= 3:
                    time_diffs = [(recent[i].timestamp - recent[0].timestamp).total_seconds() 
                                 for i in range(len(recent))]
                    if time_diffs[-1] > 0:
                        # Linear regression to get rate of change
                        rate_of_change = np.polyfit(time_diffs, values, 1)[0]
                        
                        # Detect rapid increases
                        if rate_of_change > 0:
                            # Define thresholds based on resource type
                            rapid_threshold = 0
                            if resource_type == ResourceType.CPU:
                                rapid_threshold = 10  # 10% per second
                            elif resource_type == ResourceType.MEMORY:
                                rapid_threshold = 100 * 1024 * 1024  # 100MB per second
                            elif resource_type == ResourceType.GPU:
                                rapid_threshold = 5  # 5% per second
                            
                            if rate_of_change > rapid_threshold:
                                anomaly = ResourceAnomaly(
                                    id=f"{resource_type.name.lower()}_rapid_{int(time.time())}",
                                    timestamp=recent[-1].timestamp,
                                    resource_type=resource_type,
                                    anomaly_type=ResourceAnomalyType.RAPID_CONSUMPTION,
                                    severity=3,
                                    confidence=0.8,
                                    description=f"Rapid {resource_type.name.lower()} consumption detected: {rate_of_change:.2f} per second",
                                    current_value=values[-1],
                                    baseline_value=values[0],
                                    deviation_score=rate_of_change,
                                    indicators={'rate_of_change': rate_of_change, 'time_span': time_diffs[-1]},
                                    mitigation_suggestions=["Identify process causing rapid consumption", "Monitor for resource leaks"]
                                )
                                anomalies.append(anomaly)
        
        except Exception as e:
            self.logger.error(f"Error detecting rapid consumption: {e}")
        
        return anomalies
    
    def _handle_resource_anomaly(self, anomaly: ResourceAnomaly):
        """Handle detected resource anomaly"""
        try:
            self.logger.warning(f"Resource anomaly detected: {anomaly.description}")
            
            # Integrate with alert system (if available)
            try:
                # This would integrate with the alert system
                # from .alert_system import SecurityAlertSystem
                # alert_system.create_alert(...)
                self.performance_stats['alerts_generated'] += 1
            except ImportError:
                pass
            
        except Exception as e:
            self.logger.error(f"Error handling resource anomaly: {e}")
    
    def _handle_suspicious_process(self, process: ProcessResourceProfile):
        """Handle suspicious process detection"""
        try:
            self.logger.warning(f"Suspicious process detected: {process.name} (PID: {process.pid})")
            
            # Get process trends
            cpu_trend = self.process_monitor.get_process_trends(process.pid, 'cpu_usage')
            memory_trend = self.process_monitor.get_process_trends(process.pid, 'memory_usage')
            
            # Create detailed analysis
            analysis = {
                'process_info': {
                    'pid': process.pid,
                    'name': process.name,
                    'cpu_usage': process.cpu_usage,
                    'memory_percentage': process.memory_percentage,
                    'creation_time': process.creation_time.isoformat()
                },
                'trends': {
                    'cpu': cpu_trend,
                    'memory': memory_trend
                },
                'suspicion_factors': process.additional_metrics.get('reasons', [])
            }
            
            self.logger.info(f"Process analysis: {json.dumps(analysis, indent=2, default=str)}")
            
        except Exception as e:
            self.logger.error(f"Error handling suspicious process: {e}")
    
    def _store_measurement_in_db(self, measurement: ResourceUsage):
        """Store resource measurement in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO resource_usage (
                        timestamp, resource_type, value, percentage,
                        process_id, process_name, additional_metrics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    measurement.timestamp.isoformat(),
                    measurement.resource_type.name,
                    measurement.value,
                    measurement.percentage,
                    measurement.process_id,
                    measurement.process_name,
                    json.dumps(measurement.additional_metrics)
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store measurement in database: {e}")
    
    def _store_anomaly_in_db(self, anomaly: ResourceAnomaly):
        """Store resource anomaly in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO resource_anomalies (
                        id, timestamp, resource_type, anomaly_type, severity,
                        confidence, description, current_value, baseline_value,
                        deviation_score, affected_processes, indicators,
                        mitigation_suggestions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    anomaly.id,
                    anomaly.timestamp.isoformat(),
                    anomaly.resource_type.name,
                    anomaly.anomaly_type.name,
                    anomaly.severity,
                    anomaly.confidence,
                    anomaly.description,
                    anomaly.current_value,
                    anomaly.baseline_value,
                    anomaly.deviation_score,
                    json.dumps(anomaly.affected_processes),
                    json.dumps(anomaly.indicators),
                    json.dumps(anomaly.mitigation_suggestions)
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store anomaly in database: {e}")
    
    def _store_process_profile_in_db(self, profile: ProcessResourceProfile, is_suspicious: bool):
        """Store process profile in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO process_profiles (
                        timestamp, pid, name, cpu_usage, memory_usage,
                        memory_percentage, disk_io_read, disk_io_write,
                        network_io_sent, network_io_recv, file_handles,
                        threads_count, creation_time, is_suspicious
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    profile.last_updated.isoformat(),
                    profile.pid,
                    profile.name,
                    profile.cpu_usage,
                    profile.memory_usage,
                    profile.memory_percentage,
                    profile.disk_io_read,
                    profile.disk_io_write,
                    profile.network_io_sent,
                    profile.network_io_recv,
                    profile.file_handles,
                    profile.threads_count,
                    profile.creation_time.isoformat(),
                    is_suspicious
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store process profile in database: {e}")
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource monitoring status"""
        try:
            current_measurements = {}
            for resource_type, history in self.resource_history.items():
                if history:
                    latest = history[-1]
                    current_measurements[resource_type.name] = {
                        'value': latest.value,
                        'percentage': latest.percentage,
                        'timestamp': latest.timestamp.isoformat()
                    }
            
            recent_anomalies = [a for a in self.anomalies if 
                             (datetime.now() - a.timestamp).total_seconds() < 3600]  # Last hour
            
            status = {
                'monitoring_active': self.monitoring_active,
                'current_measurements': current_measurements,
                'recent_anomalies': len(recent_anomalies),
                'anomaly_severity_breakdown': {
                    'critical': len([a for a in recent_anomalies if a.severity >= 4]),
                    'high': len([a for a in recent_anomalies if a.severity == 3]),
                    'medium': len([a for a in recent_anomalies if a.severity == 2]),
                    'low': len([a for a in recent_anomalies if a.severity == 1])
                },
                'process_monitoring': {
                    'active_processes': len(self.process_monitor.process_profiles),
                    'suspicious_processes': len(self.process_monitor.suspicious_processes)
                },
                'performance_stats': self.performance_stats.copy()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get resource status: {e}")
            return {}
    
    def get_resource_trends(self, resource_type: ResourceType, hours: int = 24) -> Dict[str, Any]:
        """Get resource usage trends"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            history = self.resource_history.get(resource_type, deque())
            
            # Filter recent data
            recent_data = [m for m in history if m.timestamp >= cutoff_time]
            
            if not recent_data:
                return {'status': 'no_data'}
            
            values = [m.value for m in recent_data]
            timestamps = [m.timestamp for m in recent_data]
            
            return {
                'resource_type': resource_type.name,
                'data_points': len(recent_data),
                'time_span_hours': hours,
                'average_value': np.mean(values),
                'min_value': min(values),
                'max_value': max(values),
                'current_value': values[-1],
                'trend_direction': 'increasing' if values[-1] > values[0] else 'decreasing',
                'volatility': np.std(values),
                'timestamps': [t.isoformat() for t in timestamps[-50:]],  # Last 50 points
                'values': values[-50:]  # Last 50 values
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get resource trends: {e}")
            return {'status': 'error', 'error': str(e)}

# Export main classes
__all__ = [
    'SystemResourceMonitor',
    'ResourceBaseline',
    'ProcessMonitor',
    'ResourceUsage',
    'ResourceAnomaly',
    'ProcessResourceProfile',
    'ResourceType',
    'ResourceAnomalyType'
]
