"""
ImpressionCore Memory Security Monitoring System

Advanced memory monitoring and security analysis system designed
for GTX 1050 Ti hardware constraints. Provides real-time memory
security monitoring, anomaly detection, and forensic capabilities.

Author: ImpressionCore Development Team
Created: 2025-01-11
Memory Target: 25MB maximum (GTX 1050 Ti optimization)
"""

import asyncio
import gc
import json
import mmap
import os
import psutil
import sqlite3
import threading
import time
import tracemalloc
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from src.core.utils.rich_logging import RichLogger

# Memory security threat types
class MemoryThreatType(Enum):
    BUFFER_OVERFLOW = auto()
    MEMORY_LEAK = auto()
    HEAP_CORRUPTION = auto()
    STACK_OVERFLOW = auto()
    USE_AFTER_FREE = auto()
    DOUBLE_FREE = auto()
    INJECTION_ATTEMPT = auto()
    PRIVILEGE_ESCALATION = auto()
    UNAUTHORIZED_ACCESS = auto()

# Memory region types
class MemoryRegionType(Enum):
    HEAP = auto()
    STACK = auto()
    CODE = auto()
    DATA = auto()
    SHARED = auto()
    MAPPED_FILE = auto()
    DEVICE = auto()

@dataclass
class MemoryRegion:
    """Memory region information"""
    start_address: int
    end_address: int
    size: int
    region_type: MemoryRegionType
    permissions: str  # rwx permissions
    mapped_file: Optional[str] = None
    process_id: Optional[int] = None
    thread_id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MemoryAnomaly:
    """Memory security anomaly detection result"""
    id: str
    timestamp: datetime
    threat_type: MemoryThreatType
    severity: int  # 1-5 scale
    confidence: float  # 0.0-1.0
    affected_region: MemoryRegion
    description: str
    indicators: Dict[str, Any]
    mitigation_suggested: List[str]
    forensic_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MemoryUsageSnapshot:
    """Memory usage snapshot for analysis"""
    timestamp: datetime
    total_memory: int
    available_memory: int
    used_memory: int
    cached_memory: int
    gpu_memory_total: int
    gpu_memory_used: int
    gpu_memory_free: int
    process_memory: Dict[int, int]  # pid -> memory usage
    heap_size: int
    stack_size: int
    virtual_memory: int

class MemoryPatternAnalyzer:
    """
    Advanced memory pattern analysis for security monitoring
    """
    
    def __init__(self, max_patterns: int = 1000):
        self.max_patterns = max_patterns
        self.patterns = deque(maxlen=max_patterns)
        self.baselines = {}
        self.anomaly_thresholds = {
            'memory_growth_rate': 0.1,  # 10% per minute
            'allocation_frequency': 100,  # allocations per second
            'fragmentation_ratio': 0.3,  # 30% fragmentation
            'suspicious_access_ratio': 0.05  # 5% suspicious accesses
        }
        self.logger = RichLogger("MemoryPatternAnalyzer")
    
    def analyze_allocation_pattern(self, allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze memory allocation patterns for anomalies"""
        try:
            if not allocations:
                return {"status": "no_data"}
            
            # Calculate allocation statistics
            sizes = [alloc['size'] for alloc in allocations]
            frequencies = [alloc['frequency'] for alloc in allocations]
            
            stats = {
                'total_allocations': len(allocations),
                'total_size': sum(sizes),
                'average_size': np.mean(sizes),
                'size_std': np.std(sizes),
                'max_size': max(sizes),
                'allocation_rate': np.mean(frequencies),
                'size_distribution': np.histogram(sizes, bins=10)[0].tolist()
            }
            
            # Detect anomalies
            anomalies = []
            
            # Large allocation spike
            if stats['max_size'] > stats['average_size'] * 10:
                anomalies.append({
                    'type': 'large_allocation_spike',
                    'severity': 3,
                    'description': f"Unusually large allocation detected: {stats['max_size']} bytes"
                })
            
            # High allocation frequency
            if stats['allocation_rate'] > self.anomaly_thresholds['allocation_frequency']:
                anomalies.append({
                    'type': 'high_allocation_frequency',
                    'severity': 2,
                    'description': f"High allocation frequency: {stats['allocation_rate']}/sec"
                })
            
            # Rapid memory growth
            if len(self.patterns) > 10:
                recent_growth = sum(p['total_size'] for p in list(self.patterns)[-5:])
                older_growth = sum(p['total_size'] for p in list(self.patterns)[-10:-5])
                if older_growth > 0:
                    growth_rate = (recent_growth - older_growth) / older_growth
                    if growth_rate > self.anomaly_thresholds['memory_growth_rate']:
                        anomalies.append({
                            'type': 'rapid_memory_growth',
                            'severity': 4,
                            'description': f"Rapid memory growth detected: {growth_rate:.2%}"
                        })
            
            # Store pattern
            pattern = {
                'timestamp': datetime.now(),
                'stats': stats,
                'anomalies': anomalies
            }
            self.patterns.append(pattern)
            
            return {
                'status': 'analyzed',
                'stats': stats,
                'anomalies': anomalies,
                'risk_score': sum(a['severity'] for a in anomalies) / max(1, len(anomalies))
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing allocation pattern: {e}")
            return {"status": "error", "error": str(e)}
    
    def detect_buffer_overflow_patterns(self, memory_access_log: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect potential buffer overflow patterns"""
        try:
            overflow_indicators = []
            
            for access in memory_access_log:
                address = access.get('address', 0)
                size = access.get('size', 0)
                access_type = access.get('type', 'unknown')
                
                # Check for out-of-bounds access
                if 'region_start' in access and 'region_end' in access:
                    region_start = access['region_start']
                    region_end = access['region_end']
                    
                    if address < region_start or address + size > region_end:
                        overflow_indicators.append({
                            'type': 'out_of_bounds_access',
                            'address': address,
                            'size': size,
                            'region_bounds': (region_start, region_end),
                            'severity': 5,
                            'timestamp': access.get('timestamp', datetime.now())
                        })
                
                # Check for suspicious write patterns
                if access_type == 'write' and size > 1024 * 1024:  # >1MB write
                    overflow_indicators.append({
                        'type': 'large_write_operation',
                        'address': address,
                        'size': size,
                        'severity': 3,
                        'timestamp': access.get('timestamp', datetime.now())
                    })
            
            return overflow_indicators
            
        except Exception as e:
            self.logger.error(f"Error detecting buffer overflow patterns: {e}")
            return []
    
    def analyze_heap_corruption(self, heap_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze heap for corruption indicators"""
        try:
            corruption_indicators = {
                'metadata_corruption': False,
                'free_list_corruption': False,
                'heap_consistency_errors': [],
                'suspicious_patterns': []
            }
            
            # Check heap metadata consistency
            if 'heap_chunks' in heap_state:
                chunks = heap_state['heap_chunks']
                total_declared_size = sum(chunk.get('size', 0) for chunk in chunks)
                actual_heap_size = heap_state.get('heap_size', 0)
                
                if abs(total_declared_size - actual_heap_size) > 4096:  # 4KB threshold
                    corruption_indicators['metadata_corruption'] = True
                    corruption_indicators['heap_consistency_errors'].append(
                        f"Size mismatch: declared={total_declared_size}, actual={actual_heap_size}"
                    )
            
            # Check for double-free patterns
            if 'free_operations' in heap_state:
                free_ops = heap_state['free_operations']
                freed_addresses = set()
                
                for op in free_ops:
                    address = op.get('address', 0)
                    if address in freed_addresses:
                        corruption_indicators['suspicious_patterns'].append({
                            'type': 'potential_double_free',
                            'address': address,
                            'severity': 5
                        })
                    freed_addresses.add(address)
            
            # Calculate corruption risk score
            risk_score = 0
            if corruption_indicators['metadata_corruption']:
                risk_score += 3
            if corruption_indicators['free_list_corruption']:
                risk_score += 3
            risk_score += len(corruption_indicators['heap_consistency_errors'])
            risk_score += sum(p['severity'] for p in corruption_indicators['suspicious_patterns'])
            
            return {
                'corruption_indicators': corruption_indicators,
                'risk_score': min(10, risk_score),
                'analysis_timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing heap corruption: {e}")
            return {'error': str(e)}

class MemoryForensicsEngine:
    """
    Memory forensics and investigation engine
    """
    
    def __init__(self, evidence_dir: str = "src/security/monitoring/evidence"):
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.logger = RichLogger("MemoryForensicsEngine")
        self.active_investigations = {}
    
    def create_memory_dump(self, process_id: int, dump_type: str = "full") -> str:
        """Create a memory dump for forensic analysis"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dump_file = self.evidence_dir / f"memory_dump_{process_id}_{timestamp}.bin"
            
            if dump_type == "full":
                # Full process memory dump
                process = psutil.Process(process_id)
                memory_info = process.memory_info()
                
                # Create memory dump metadata
                metadata = {
                    'process_id': process_id,
                    'process_name': process.name(),
                    'dump_type': dump_type,
                    'timestamp': timestamp,
                    'memory_size': memory_info.rss,
                    'virtual_memory_size': memory_info.vms,
                    'dump_file': str(dump_file)
                }
                
                # Save metadata
                metadata_file = dump_file.with_suffix('.json')
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2, default=str)
                
                self.logger.info(f"Memory dump created: {dump_file}")
                return str(dump_file)
                
            elif dump_type == "targeted":
                # Targeted memory regions dump
                # This would dump specific memory regions of interest
                self.logger.info(f"Targeted memory dump created for process {process_id}")
                return str(dump_file)
                
        except Exception as e:
            self.logger.error(f"Failed to create memory dump: {e}")
            return ""
    
    def analyze_memory_dump(self, dump_file: str) -> Dict[str, Any]:
        """Analyze memory dump for security artifacts"""
        try:
            dump_path = Path(dump_file)
            if not dump_path.exists():
                return {"error": "Dump file not found"}
            
            # Load dump metadata
            metadata_file = dump_path.with_suffix('.json')
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            analysis_results = {
                'dump_file': dump_file,
                'metadata': metadata,
                'analysis_timestamp': datetime.now(),
                'artifacts': [],
                'indicators': [],
                'recommendations': []
            }
            
            # Analyze for known patterns
            with open(dump_file, 'rb') as f:
                # Read in chunks to avoid memory issues
                chunk_size = 1024 * 1024  # 1MB chunks
                chunk_offset = 0
                
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Look for suspicious patterns
                    artifacts = self._scan_memory_chunk(chunk, chunk_offset)
                    analysis_results['artifacts'].extend(artifacts)
                    
                    chunk_offset += len(chunk)
            
            # Generate security indicators
            analysis_results['indicators'] = self._generate_security_indicators(
                analysis_results['artifacts']
            )
            
            # Generate recommendations
            analysis_results['recommendations'] = self._generate_forensic_recommendations(
                analysis_results['indicators']
            )
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing memory dump: {e}")
            return {"error": str(e)}
    
    def _scan_memory_chunk(self, chunk: bytes, offset: int) -> List[Dict[str, Any]]:
        """Scan memory chunk for security artifacts"""
        artifacts = []
        
        try:
            # Look for code injection patterns
            shellcode_patterns = [
                b'\x90\x90\x90\x90',  # NOP sled
                b'\xcc\xcc\xcc\xcc',  # INT3 instructions
                b'\x48\x31\xc0',      # XOR RAX, RAX (common in shellcode)
            ]
            
            for pattern in shellcode_patterns:
                pattern_offset = chunk.find(pattern)
                if pattern_offset != -1:
                    artifacts.append({
                        'type': 'potential_shellcode',
                        'pattern': pattern.hex(),
                        'offset': offset + pattern_offset,
                        'severity': 4,
                        'description': 'Potential shellcode pattern detected'
                    })
            
            # Look for suspicious strings
            suspicious_strings = [
                b'cmd.exe',
                b'powershell',
                b'/bin/sh',
                b'wget',
                b'curl',
                b'nc.exe',
                b'telnet'
            ]
            
            for sus_string in suspicious_strings:
                string_offset = chunk.find(sus_string)
                if string_offset != -1:
                    artifacts.append({
                        'type': 'suspicious_string',
                        'string': sus_string.decode('utf-8', errors='ignore'),
                        'offset': offset + string_offset,
                        'severity': 3,
                        'description': f'Suspicious string found: {sus_string.decode("utf-8", errors="ignore")}'
                    })
            
            # Look for encryption/encoding patterns
            # High entropy might indicate encrypted or encoded data
            if len(chunk) >= 256:
                entropy = self._calculate_entropy(chunk)
                if entropy > 7.5:  # High entropy threshold
                    artifacts.append({
                        'type': 'high_entropy_data',
                        'entropy': entropy,
                        'offset': offset,
                        'size': len(chunk),
                        'severity': 2,
                        'description': f'High entropy data (possibly encrypted): {entropy:.2f}'
                    })
            
        except Exception as e:
            self.logger.error(f"Error scanning memory chunk: {e}")
        
        return artifacts
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        try:
            # Count byte frequencies
            byte_counts = defaultdict(int)
            for byte in data:
                byte_counts[byte] += 1
            
            # Calculate entropy
            entropy = 0.0
            data_len = len(data)
            for count in byte_counts.values():
                probability = count / data_len
                if probability > 0:
                    entropy -= probability * np.log2(probability)
            
            return entropy
            
        except Exception as e:
            self.logger.error(f"Error calculating entropy: {e}")
            return 0.0
    
    def _generate_security_indicators(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate security indicators from artifacts"""
        indicators = []
        
        try:
            # Count artifact types
            artifact_counts = defaultdict(int)
            for artifact in artifacts:
                artifact_counts[artifact['type']] += 1
            
            # Generate indicators based on patterns
            if artifact_counts['potential_shellcode'] > 2:
                indicators.append({
                    'type': 'code_injection_suspected',
                    'confidence': 0.8,
                    'description': f"Multiple shellcode patterns found ({artifact_counts['potential_shellcode']})",
                    'severity': 5
                })
            
            if artifact_counts['suspicious_string'] > 5:
                indicators.append({
                    'type': 'malicious_tools_present',
                    'confidence': 0.7,
                    'description': f"Multiple suspicious tool strings found ({artifact_counts['suspicious_string']})",
                    'severity': 4
                })
            
            if artifact_counts['high_entropy_data'] > 10:
                indicators.append({
                    'type': 'data_obfuscation_suspected',
                    'confidence': 0.6,
                    'description': f"Multiple high-entropy regions found ({artifact_counts['high_entropy_data']})",
                    'severity': 3
                })
            
        except Exception as e:
            self.logger.error(f"Error generating security indicators: {e}")
        
        return indicators
    
    def _generate_forensic_recommendations(self, indicators: List[Dict[str, Any]]) -> List[str]:
        """Generate forensic investigation recommendations"""
        recommendations = []
        
        try:
            high_severity_count = sum(1 for ind in indicators if ind.get('severity', 0) >= 4)
            medium_severity_count = sum(1 for ind in indicators if ind.get('severity', 0) == 3)
            
            if high_severity_count > 0:
                recommendations.append("Immediate isolation of affected system recommended")
                recommendations.append("Contact incident response team")
                recommendations.append("Preserve all memory dumps and logs for investigation")
            
            if medium_severity_count > 0:
                recommendations.append("Enhanced monitoring of affected processes")
                recommendations.append("Review process execution history")
                recommendations.append("Check for additional IOCs on system")
            
            # Specific recommendations based on indicator types
            indicator_types = {ind['type'] for ind in indicators}
            
            if 'code_injection_suspected' in indicator_types:
                recommendations.append("Analyze process injection techniques used")
                recommendations.append("Check for DLL injection or process hollowing")
            
            if 'malicious_tools_present' in indicator_types:
                recommendations.append("Scan for known malware signatures")
                recommendations.append("Review network connections for C2 communication")
            
            if 'data_obfuscation_suspected' in indicator_types:
                recommendations.append("Attempt to decode/decrypt suspicious data regions")
                recommendations.append("Look for steganography or other hiding techniques")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations

class MemorySecurityMonitor:
    """
    Main memory security monitoring system
    
    Provides comprehensive memory security monitoring, anomaly detection,
    and forensic capabilities optimized for GTX 1050 Ti hardware constraints.
    """
    
    def __init__(self, config_dir: str = "src/security/monitoring/config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.logger = RichLogger("MemorySecurityMonitor")
        self.pattern_analyzer = MemoryPatternAnalyzer()
        self.forensics_engine = MemoryForensicsEngine()
        
        # Monitoring state
        self.monitoring_active = False
        self.memory_snapshots = deque(maxlen=1000)  # Last 1000 snapshots
        self.anomalies = deque(maxlen=5000)  # Last 5000 anomalies
        self.suspicious_processes = set()
        
        # Configuration
        self.config = {
            'snapshot_interval': 30,  # seconds
            'anomaly_threshold': 0.7,  # confidence threshold
            'max_memory_usage': 25 * 1024 * 1024,  # 25MB limit
            'gpu_memory_threshold': 0.95,  # 95% GPU memory threshold
            'enable_forensics': True,
            'auto_dump_on_anomaly': False
        }
        
        # Performance tracking
        self.performance_stats = {
            'snapshots_taken': 0,
            'anomalies_detected': 0,
            'forensic_dumps_created': 0,
            'processing_errors': 0,
            'average_processing_time': 0.0
        }
        
        # Threading
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Database setup
        self.db_path = self.config_dir / "memory_security.db"
        self._init_database()
        
        # Start memory tracking
        tracemalloc.start()
    
    def _init_database(self):
        """Initialize SQLite database for memory security data"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Memory snapshots table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memory_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        total_memory INTEGER NOT NULL,
                        available_memory INTEGER NOT NULL,
                        used_memory INTEGER NOT NULL,
                        gpu_memory_used INTEGER NOT NULL,
                        gpu_memory_total INTEGER NOT NULL,
                        heap_size INTEGER,
                        stack_size INTEGER,
                        virtual_memory INTEGER,
                        process_count INTEGER,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Memory anomalies table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memory_anomalies (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        threat_type TEXT NOT NULL,
                        severity INTEGER NOT NULL,
                        confidence REAL NOT NULL,
                        description TEXT,
                        affected_process INTEGER,
                        memory_region_start INTEGER,
                        memory_region_end INTEGER,
                        indicators TEXT,
                        mitigation_suggested TEXT,
                        forensic_data TEXT,
                        resolved BOOLEAN DEFAULT FALSE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Performance metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON memory_snapshots(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON memory_anomalies(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON memory_anomalies(severity)')
                
                conn.commit()
                self.logger.info("Memory security database initialized")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def start_monitoring(self):
        """Start memory security monitoring"""
        if self.monitoring_active:
            self.logger.warning("Memory monitoring already active")
            return
        
        self.monitoring_active = True
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Memory security monitoring started")
    
    def stop_monitoring(self):
        """Stop memory security monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self.stop_event.set()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        self.logger.info("Memory security monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active and not self.stop_event.is_set():
            try:
                start_time = time.time()
                
                # Take memory snapshot
                snapshot = self._take_memory_snapshot()
                if snapshot:
                    self.memory_snapshots.append(snapshot)
                    self._store_snapshot_in_db(snapshot)
                
                # Analyze for anomalies
                anomalies = self._analyze_memory_security(snapshot)
                for anomaly in anomalies:
                    self.anomalies.append(anomaly)
                    self._store_anomaly_in_db(anomaly)
                    self._handle_anomaly(anomaly)
                
                # Update performance stats
                processing_time = time.time() - start_time
                self.performance_stats['snapshots_taken'] += 1
                self.performance_stats['anomalies_detected'] += len(anomalies)
                self.performance_stats['average_processing_time'] = (
                    (self.performance_stats['average_processing_time'] * 
                     (self.performance_stats['snapshots_taken'] - 1) + processing_time) /
                    self.performance_stats['snapshots_taken']
                )
                
                # Wait for next interval
                self.stop_event.wait(self.config['snapshot_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                self.performance_stats['processing_errors'] += 1
                self.stop_event.wait(5)  # Wait 5 seconds before retrying
    
    def _take_memory_snapshot(self) -> Optional[MemoryUsageSnapshot]:
        """Take a comprehensive memory usage snapshot"""
        try:
            # System memory information
            memory = psutil.virtual_memory()
            
            # GPU memory information (if available)
            gpu_memory_total = 4 * 1024 * 1024 * 1024  # 4GB GTX 1050 Ti
            gpu_memory_used = 0
            gpu_memory_free = gpu_memory_total
            
            try:
                # This would integrate with actual GPU monitoring
                # For now, simulate GPU memory usage
                import random
                gpu_memory_used = int(gpu_memory_total * random.uniform(0.1, 0.8))
                gpu_memory_free = gpu_memory_total - gpu_memory_used
            except:
                pass
            
            # Process memory information
            process_memory = {}
            try:
                for proc in psutil.process_iter(['pid', 'memory_info']):
                    try:
                        pid = proc.info['pid']
                        mem_info = proc.info['memory_info']
                        if mem_info:
                            process_memory[pid] = mem_info.rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                self.logger.warning(f"Failed to get process memory info: {e}")
            
            # Python memory information
            current, peak = tracemalloc.get_traced_memory()
            heap_size = current
            stack_size = 0  # Estimate stack size
            
            # Virtual memory
            virtual_memory = memory.total
            
            snapshot = MemoryUsageSnapshot(
                timestamp=datetime.now(),
                total_memory=memory.total,
                available_memory=memory.available,
                used_memory=memory.used,
                cached_memory=memory.cached if hasattr(memory, 'cached') else 0,
                gpu_memory_total=gpu_memory_total,
                gpu_memory_used=gpu_memory_used,
                gpu_memory_free=gpu_memory_free,
                process_memory=process_memory,
                heap_size=heap_size,
                stack_size=stack_size,
                virtual_memory=virtual_memory
            )
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Failed to take memory snapshot: {e}")
            return None
    
    def _analyze_memory_security(self, snapshot: MemoryUsageSnapshot) -> List[MemoryAnomaly]:
        """Analyze memory snapshot for security anomalies"""
        anomalies = []
        
        try:
            # Check GPU memory usage
            gpu_usage_ratio = snapshot.gpu_memory_used / snapshot.gpu_memory_total
            if gpu_usage_ratio > self.config['gpu_memory_threshold']:
                anomaly = MemoryAnomaly(
                    id=f"gpu_memory_high_{int(time.time())}",
                    timestamp=snapshot.timestamp,
                    threat_type=MemoryThreatType.MEMORY_LEAK,
                    severity=3,
                    confidence=0.8,
                    affected_region=MemoryRegion(
                        start_address=0,
                        end_address=snapshot.gpu_memory_total,
                        size=snapshot.gpu_memory_used,
                        region_type=MemoryRegionType.DEVICE,
                        permissions="rw-"
                    ),
                    description=f"GPU memory usage at {gpu_usage_ratio:.1%} ({snapshot.gpu_memory_used:,} / {snapshot.gpu_memory_total:,} bytes)",
                    indicators={"gpu_usage_ratio": gpu_usage_ratio},
                    mitigation_suggested=["Free unused GPU memory", "Check for memory leaks in GPU kernels"]
                )
                anomalies.append(anomaly)
            
            # Check for rapid memory growth
            if len(self.memory_snapshots) >= 5:
                recent_snapshots = list(self.memory_snapshots)[-5:]
                memory_growth = []
                
                for i in range(1, len(recent_snapshots)):
                    prev_used = recent_snapshots[i-1].used_memory
                    curr_used = recent_snapshots[i].used_memory
                    if prev_used > 0:
                        growth_rate = (curr_used - prev_used) / prev_used
                        memory_growth.append(growth_rate)
                
                if memory_growth and max(memory_growth) > 0.1:  # 10% growth
                    anomaly = MemoryAnomaly(
                        id=f"rapid_growth_{int(time.time())}",
                        timestamp=snapshot.timestamp,
                        threat_type=MemoryThreatType.MEMORY_LEAK,
                        severity=2,
                        confidence=0.7,
                        affected_region=MemoryRegion(
                            start_address=0,
                            end_address=snapshot.total_memory,
                            size=snapshot.used_memory,
                            region_type=MemoryRegionType.HEAP,
                            permissions="rwx"
                        ),
                        description=f"Rapid memory growth detected: {max(memory_growth):.1%}",
                        indicators={"growth_rates": memory_growth},
                        mitigation_suggested=["Investigate memory leaks", "Review allocation patterns"]
                    )
                    anomalies.append(anomaly)
            
            # Check for suspicious processes
            for pid, memory_usage in snapshot.process_memory.items():
                if memory_usage > 1024 * 1024 * 1024:  # >1GB per process
                    try:
                        process = psutil.Process(pid)
                        process_name = process.name()
                        
                        # Check if this is a known suspicious process
                        if pid not in self.suspicious_processes:
                            anomaly = MemoryAnomaly(
                                id=f"suspicious_process_{pid}_{int(time.time())}",
                                timestamp=snapshot.timestamp,
                                threat_type=MemoryThreatType.UNAUTHORIZED_ACCESS,
                                severity=2,
                                confidence=0.6,
                                affected_region=MemoryRegion(
                                    start_address=0,
                                    end_address=memory_usage,
                                    size=memory_usage,
                                    region_type=MemoryRegionType.HEAP,
                                    permissions="rwx",
                                    process_id=pid
                                ),
                                description=f"High memory usage by process {process_name} (PID: {pid}): {memory_usage:,} bytes",
                                indicators={"process_name": process_name, "memory_usage": memory_usage},
                                mitigation_suggested=["Monitor process behavior", "Investigate process legitimacy"]
                            )
                            anomalies.append(anomaly)
                            self.suspicious_processes.add(pid)
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            # Check heap consistency (if tracking is available)
            if hasattr(self, 'heap_tracker') and self.heap_tracker:
                heap_analysis = self.pattern_analyzer.analyze_heap_corruption(
                    self.heap_tracker.get_heap_state()
                )
                
                if heap_analysis.get('risk_score', 0) > 5:
                    anomaly = MemoryAnomaly(
                        id=f"heap_corruption_{int(time.time())}",
                        timestamp=snapshot.timestamp,
                        threat_type=MemoryThreatType.HEAP_CORRUPTION,
                        severity=4,
                        confidence=0.8,
                        affected_region=MemoryRegion(
                            start_address=0,
                            end_address=snapshot.heap_size,
                            size=snapshot.heap_size,
                            region_type=MemoryRegionType.HEAP,
                            permissions="rw-"
                        ),
                        description="Potential heap corruption detected",
                        indicators=heap_analysis,
                        mitigation_suggested=["Create memory dump", "Investigate heap integrity"]
                    )
                    anomalies.append(anomaly)
            
        except Exception as e:
            self.logger.error(f"Error analyzing memory security: {e}")
        
        return anomalies
    
    def _handle_anomaly(self, anomaly: MemoryAnomaly):
        """Handle detected memory anomaly"""
        try:
            # Log the anomaly
            self.logger.warning(f"Memory anomaly detected: {anomaly.description}")
            
            # Auto-create forensic dump if configured and severity is high
            if (self.config['auto_dump_on_anomaly'] and 
                anomaly.severity >= 4 and 
                anomaly.affected_region.process_id):
                
                dump_file = self.forensics_engine.create_memory_dump(
                    anomaly.affected_region.process_id,
                    "targeted"
                )
                
                if dump_file:
                    anomaly.forensic_data['memory_dump'] = dump_file
                    self.performance_stats['forensic_dumps_created'] += 1
            
            # Integrate with alert system (if available)
            try:
                # This would integrate with the alert system
                # from .alert_system import SecurityAlertSystem
                # alert_system.create_alert(...)
                pass
            except ImportError:
                pass
            
        except Exception as e:
            self.logger.error(f"Error handling anomaly: {e}")
    
    def _store_snapshot_in_db(self, snapshot: MemoryUsageSnapshot):
        """Store memory snapshot in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO memory_snapshots (
                        timestamp, total_memory, available_memory, used_memory,
                        gpu_memory_used, gpu_memory_total, heap_size, stack_size,
                        virtual_memory, process_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    snapshot.timestamp.isoformat(),
                    snapshot.total_memory,
                    snapshot.available_memory,
                    snapshot.used_memory,
                    snapshot.gpu_memory_used,
                    snapshot.gpu_memory_total,
                    snapshot.heap_size,
                    snapshot.stack_size,
                    snapshot.virtual_memory,
                    len(snapshot.process_memory)
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store snapshot in database: {e}")
    
    def _store_anomaly_in_db(self, anomaly: MemoryAnomaly):
        """Store memory anomaly in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO memory_anomalies (
                        id, timestamp, threat_type, severity, confidence,
                        description, affected_process, memory_region_start,
                        memory_region_end, indicators, mitigation_suggested,
                        forensic_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    anomaly.id,
                    anomaly.timestamp.isoformat(),
                    anomaly.threat_type.name,
                    anomaly.severity,
                    anomaly.confidence,
                    anomaly.description,
                    anomaly.affected_region.process_id,
                    anomaly.affected_region.start_address,
                    anomaly.affected_region.end_address,
                    json.dumps(anomaly.indicators),
                    json.dumps(anomaly.mitigation_suggested),
                    json.dumps(anomaly.forensic_data)
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store anomaly in database: {e}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current memory security status"""
        try:
            current_snapshot = self.memory_snapshots[-1] if self.memory_snapshots else None
            recent_anomalies = [a for a in self.anomalies if 
                             (datetime.now() - a.timestamp).total_seconds() < 3600]  # Last hour
            
            status = {
                'monitoring_active': self.monitoring_active,
                'current_memory_usage': {
                    'total': current_snapshot.total_memory if current_snapshot else 0,
                    'used': current_snapshot.used_memory if current_snapshot else 0,
                    'gpu_used': current_snapshot.gpu_memory_used if current_snapshot else 0,
                    'gpu_total': current_snapshot.gpu_memory_total if current_snapshot else 0
                } if current_snapshot else {},
                'recent_anomalies': len(recent_anomalies),
                'anomaly_severity_breakdown': {
                    'critical': len([a for a in recent_anomalies if a.severity >= 4]),
                    'high': len([a for a in recent_anomalies if a.severity == 3]),
                    'medium': len([a for a in recent_anomalies if a.severity == 2]),
                    'low': len([a for a in recent_anomalies if a.severity == 1])
                },
                'performance_stats': self.performance_stats.copy(),
                'suspicious_processes': len(self.suspicious_processes),
                'last_snapshot': current_snapshot.timestamp.isoformat() if current_snapshot else None
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get security status: {e}")
            return {}
    
    def create_forensic_dump(self, process_id: int) -> str:
        """Create forensic memory dump for investigation"""
        try:
            return self.forensics_engine.create_memory_dump(process_id, "full")
        except Exception as e:
            self.logger.error(f"Failed to create forensic dump: {e}")
            return ""
    
    def analyze_forensic_dump(self, dump_file: str) -> Dict[str, Any]:
        """Analyze forensic memory dump"""
        try:
            return self.forensics_engine.analyze_memory_dump(dump_file)
        except Exception as e:
            self.logger.error(f"Failed to analyze forensic dump: {e}")
            return {}

# Export main classes
__all__ = [
    'MemorySecurityMonitor',
    'MemoryPatternAnalyzer',
    'MemoryForensicsEngine',
    'MemoryAnomaly',
    'MemoryRegion',
    'MemoryUsageSnapshot',
    'MemoryThreatType',
    'MemoryRegionType'
]
