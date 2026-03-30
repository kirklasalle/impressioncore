"""
ImpressionCore Intrusion Detection System

Advanced intrusion detection system with real-time threat monitoring,
pattern recognition, and automated response capabilities. Optimized for
GTX 1050 Ti hardware constraints with efficient memory usage and
high-performance threat detection algorithms.

Author: ImpressionCore Security Team
Created: 2025-01-27
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Budget: 40MB for intrusion detection
"""

import os
import sys
import asyncio
import logging
import threading
import time
import hashlib
import json
import sqlite3
from typing import Dict, List, Optional, Union, Any, Callable, Tuple, Set
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import re
import collections
import gc
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.utils.rich_enhancements import RichStatusManager
from src.core.utils.rich_logging import RichLogger


class ThreatLevel(Enum):
    """Threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackType(Enum):
    """Types of security attacks."""
    BRUTE_FORCE = "brute_force"
    DDoS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    MALWARE = "malware"
    PHISHING = "phishing"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    UNKNOWN = "unknown"


class DetectionMethod(Enum):
    """Detection methods used."""
    SIGNATURE_BASED = "signature_based"
    ANOMALY_BASED = "anomaly_based"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    MACHINE_LEARNING = "machine_learning"
    HEURISTIC = "heuristic"
    HYBRID = "hybrid"


@dataclass
class SecurityEvent:
    """Security event detected by the IDS."""
    event_id: str
    timestamp: datetime
    source_ip: Optional[str]
    target_ip: Optional[str]
    attack_type: AttackType
    threat_level: ThreatLevel
    detection_method: DetectionMethod
    confidence_score: float  # 0.0 - 1.0
    description: str
    raw_data: Dict[str, Any]
    affected_resources: List[str] = field(default_factory=list)
    mitigation_actions: List[str] = field(default_factory=list)
    false_positive_probability: float = 0.0


@dataclass
class AttackPattern:
    """Attack pattern for signature-based detection."""
    pattern_id: str
    name: str
    attack_type: AttackType
    signature: Union[str, re.Pattern]
    confidence_weight: float
    description: str
    created_at: datetime
    last_updated: datetime


@dataclass
class NetworkSession:
    """Network session tracking."""
    session_id: str
    source_ip: str
    target_ip: str
    start_time: datetime
    last_activity: datetime
    packet_count: int = 0
    byte_count: int = 0
    flags: Set[str] = field(default_factory=set)
    suspicious_indicators: List[str] = field(default_factory=list)


class IntrusionDetectionConfig:
    """Configuration for intrusion detection system."""
    
    # Memory management
    MAX_MEMORY_MB = 40
    MAX_EVENTS_IN_MEMORY = 1000
    MAX_SESSIONS_IN_MEMORY = 500
    MAX_PATTERNS_IN_MEMORY = 200
    
    # Detection thresholds
    BRUTE_FORCE_THRESHOLD = 5  # Failed attempts
    BRUTE_FORCE_WINDOW_MINUTES = 5
    DDoS_THRESHOLD = 100  # Requests per minute
    ANOMALY_THRESHOLD = 0.8  # Confidence threshold
    
    # Performance settings
    MAX_DETECTION_THREADS = 4
    DETECTION_BATCH_SIZE = 50
    SESSION_TIMEOUT_MINUTES = 30
    EVENT_PROCESSING_TIMEOUT_MS = 100
    
    # Database settings
    IDS_DB_PATH = "data/security/ids.db"
    EVENT_RETENTION_DAYS = 90
    PATTERN_UPDATE_INTERVAL_HOURS = 24


class IntrusionDetectionSystem:
    """
    Advanced intrusion detection system with multiple detection methods.
    
    Features:
    - Signature-based detection with pattern matching
    - Anomaly-based detection using statistical analysis
    - Behavioral analysis for user activity monitoring
    - Real-time threat assessment and response
    - Memory-optimized for GTX 1050 Ti constraints
    """
    
    def __init__(self):
        self.config = IntrusionDetectionConfig()
        self.logger = self._setup_logging()
        self.status_manager = RichStatusManager("Intrusion Detection")
        
        # System state
        self.is_active = False
        self.memory_usage_mb = 0.0
        self._shutdown_event = threading.Event()
        
        # Detection components
        self._attack_patterns: Dict[str, AttackPattern] = {}
        self._active_sessions: Dict[str, NetworkSession] = {}
        self._recent_events: collections.deque = collections.deque(
            maxlen=self.config.MAX_EVENTS_IN_MEMORY
        )
        
        # Thread management
        self._detection_executor = ThreadPoolExecutor(
            max_workers=self.config.MAX_DETECTION_THREADS,
            thread_name_prefix="ids_detection"
        )
        self._monitoring_thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self._events_processed = 0
        self._false_positives = 0
        self._true_positives = 0
        self._detection_times: collections.deque = collections.deque(maxlen=100)
        
        # Database
        self._db_connection: Optional[sqlite3.Connection] = None
        self._initialize_database()
        
        # Load attack patterns
        self._load_attack_patterns()
        
        # Statistical baselines for anomaly detection
        self._baseline_metrics: Dict[str, Dict[str, float]] = {}
        self._initialize_baselines()
    
    def _setup_logging(self) -> RichLogger:
        """Setup rich logging for the IDS."""
        logger = RichLogger(
            name="intrusion_detection",
            level=logging.INFO,
            log_file="logs/intrusion_detection.log"
        )
        return logger
    
    def _initialize_database(self):
        """Initialize the IDS database."""
        try:
            os.makedirs(os.path.dirname(self.config.IDS_DB_PATH), exist_ok=True)
            self._db_connection = sqlite3.connect(
                self.config.IDS_DB_PATH,
                check_same_thread=False
            )
            
            self._create_ids_tables()
            self.logger.info("IDS database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize IDS database: {e}")
            raise
    
    def _create_ids_tables(self):
        """Create IDS database tables."""
        cursor = self._db_connection.cursor()
        
        # Security events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                source_ip TEXT,
                target_ip TEXT,
                attack_type TEXT NOT NULL,
                threat_level TEXT NOT NULL,
                detection_method TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                description TEXT NOT NULL,
                raw_data TEXT NOT NULL,
                false_positive BOOLEAN DEFAULT FALSE,
                resolved BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Attack patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attack_patterns (
                pattern_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                attack_type TEXT NOT NULL,
                signature TEXT NOT NULL,
                confidence_weight REAL NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                enabled BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Network sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_sessions (
                session_id TEXT PRIMARY KEY,
                source_ip TEXT NOT NULL,
                target_ip TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                packet_count INTEGER DEFAULT 0,
                byte_count INTEGER DEFAULT 0,
                suspicious_score REAL DEFAULT 0.0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ids_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self._db_connection.commit()
    
    def start(self) -> bool:
        """Start the intrusion detection system."""
        try:
            self.status_manager.start("Starting intrusion detection system...")
            
            # Start monitoring thread
            self.is_active = True
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self._monitoring_thread.start()
            
            # Update memory usage
            self._update_memory_usage()
            
            self.status_manager.stop("Intrusion detection system started")
            self.logger.info("Intrusion detection system started")
            return True
            
        except Exception as e:
            self.status_manager.stop(f"Failed to start IDS: {e}")
            self.logger.error(f"Failed to start intrusion detection: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the intrusion detection system."""
        try:
            self.status_manager.start("Stopping intrusion detection system...")
            
            # Signal shutdown
            self.is_active = False
            self._shutdown_event.set()
            
            # Wait for monitoring thread
            if self._monitoring_thread:
                self._monitoring_thread.join(timeout=5.0)
            
            # Shutdown thread pool
            self._detection_executor.shutdown(wait=True, timeout=5.0)
            
            # Close database
            if self._db_connection:
                self._db_connection.close()
                self._db_connection = None
            
            self.status_manager.stop("Intrusion detection system stopped")
            self.logger.info("Intrusion detection system stopped")
            return True
            
        except Exception as e:
            self.status_manager.stop(f"Error stopping IDS: {e}")
            self.logger.error(f"Error stopping intrusion detection: {e}")
            return False
    
    def detect_intrusion(self, event_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """
        Detect potential intrusions from event data.
        
        Args:
            event_data: Raw event data to analyze
            
        Returns:
            SecurityEvent if intrusion detected, None otherwise
        """
        start_time = time.time()
        
        try:
            # Run parallel detection methods
            detection_futures = []
            
            # Signature-based detection
            detection_futures.append(
                self._detection_executor.submit(
                    self._signature_based_detection, event_data
                )
            )
            
            # Anomaly-based detection
            detection_futures.append(
                self._detection_executor.submit(
                    self._anomaly_based_detection, event_data
                )
            )
            
            # Behavioral analysis
            detection_futures.append(
                self._detection_executor.submit(
                    self._behavioral_analysis, event_data
                )
            )
            
            # Collect results
            detected_events = []
            for future in as_completed(detection_futures, timeout=0.1):
                try:
                    result = future.result()
                    if result:
                        detected_events.append(result)
                except Exception as e:
                    self.logger.error(f"Detection method failed: {e}")
            
            # Select highest confidence event
            if detected_events:
                best_event = max(detected_events, key=lambda e: e.confidence_score)
                
                # Store event
                self._store_security_event(best_event)
                self._recent_events.append(best_event)
                
                # Update statistics
                self._events_processed += 1
                
                # Record detection time
                detection_time = (time.time() - start_time) * 1000
                self._detection_times.append(detection_time)
                
                self.logger.warning(
                    f"Intrusion detected: {best_event.attack_type.value} "
                    f"(confidence: {best_event.confidence_score:.2f})"
                )
                
                return best_event
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in intrusion detection: {e}")
            return None
    
    def _signature_based_detection(self, event_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Signature-based intrusion detection."""
        try:
            # Extract relevant fields
            content = str(event_data.get('content', ''))
            source_ip = event_data.get('source_ip')
            target_ip = event_data.get('target_ip')
            
            # Check against attack patterns
            for pattern in self._attack_patterns.values():
                if isinstance(pattern.signature, re.Pattern):
                    match = pattern.signature.search(content)
                else:
                    match = pattern.signature in content
                
                if match:
                    # Create security event
                    event = SecurityEvent(
                        event_id=self._generate_event_id(),
                        timestamp=datetime.now(),
                        source_ip=source_ip,
                        target_ip=target_ip,
                        attack_type=pattern.attack_type,
                        threat_level=self._assess_threat_level(pattern.attack_type),
                        detection_method=DetectionMethod.SIGNATURE_BASED,
                        confidence_score=pattern.confidence_weight,
                        description=f"Signature match: {pattern.name}",
                        raw_data=event_data
                    )
                    
                    return event
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in signature-based detection: {e}")
            return None
    
    def _anomaly_based_detection(self, event_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Anomaly-based intrusion detection using statistical analysis."""
        try:
            # Extract metrics for analysis
            metrics = self._extract_event_metrics(event_data)
            
            # Calculate anomaly score
            anomaly_score = self._calculate_anomaly_score(metrics)
            
            if anomaly_score > self.config.ANOMALY_THRESHOLD:
                # Create security event
                event = SecurityEvent(
                    event_id=self._generate_event_id(),
                    timestamp=datetime.now(),
                    source_ip=event_data.get('source_ip'),
                    target_ip=event_data.get('target_ip'),
                    attack_type=AttackType.ANOMALOUS_BEHAVIOR,
                    threat_level=self._assess_threat_level_from_score(anomaly_score),
                    detection_method=DetectionMethod.ANOMALY_BASED,
                    confidence_score=anomaly_score,
                    description=f"Anomalous behavior detected (score: {anomaly_score:.2f})",
                    raw_data=event_data
                )
                
                return event
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in anomaly-based detection: {e}")
            return None
    
    def _behavioral_analysis(self, event_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Behavioral analysis for user activity patterns."""
        try:
            user_id = event_data.get('user_id')
            if not user_id:
                return None
            
            # Analyze user behavior patterns
            current_activity = self._extract_user_activity(event_data)
            historical_pattern = self._get_user_baseline(user_id)
            
            # Calculate behavioral deviation
            deviation_score = self._calculate_behavioral_deviation(
                current_activity, historical_pattern
            )
            
            if deviation_score > 0.7:  # High deviation threshold
                event = SecurityEvent(
                    event_id=self._generate_event_id(),
                    timestamp=datetime.now(),
                    source_ip=event_data.get('source_ip'),
                    target_ip=event_data.get('target_ip'),
                    attack_type=AttackType.ANOMALOUS_BEHAVIOR,
                    threat_level=self._assess_threat_level_from_score(deviation_score),
                    detection_method=DetectionMethod.BEHAVIORAL_ANALYSIS,
                    confidence_score=deviation_score,
                    description=f"Behavioral anomaly for user {user_id}",
                    raw_data=event_data
                )
                
                return event
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in behavioral analysis: {e}")
            return None
    
    def _assess_threat_level(self, attack_type: AttackType) -> ThreatLevel:
        """Assess threat level based on attack type."""
        threat_mapping = {
            AttackType.BRUTE_FORCE: ThreatLevel.MEDIUM,
            AttackType.DDoS: ThreatLevel.HIGH,
            AttackType.SQL_INJECTION: ThreatLevel.HIGH,
            AttackType.XSS: ThreatLevel.MEDIUM,
            AttackType.PRIVILEGE_ESCALATION: ThreatLevel.CRITICAL,
            AttackType.DATA_EXFILTRATION: ThreatLevel.CRITICAL,
            AttackType.MALWARE: ThreatLevel.CRITICAL,
            AttackType.UNAUTHORIZED_ACCESS: ThreatLevel.HIGH,
            AttackType.ANOMALOUS_BEHAVIOR: ThreatLevel.MEDIUM
        }
        return threat_mapping.get(attack_type, ThreatLevel.LOW)
    
    def _assess_threat_level_from_score(self, score: float) -> ThreatLevel:
        """Assess threat level from confidence score."""
        if score >= 0.9:
            return ThreatLevel.CRITICAL
        elif score >= 0.7:
            return ThreatLevel.HIGH
        elif score >= 0.5:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _load_attack_patterns(self):
        """Load attack patterns from database and defaults."""
        try:
            # Load from database
            cursor = self._db_connection.cursor()
            cursor.execute("SELECT * FROM attack_patterns WHERE enabled = TRUE")
            
            for row in cursor.fetchall():
                pattern = AttackPattern(
                    pattern_id=row[0],
                    name=row[1],
                    attack_type=AttackType(row[2]),
                    signature=re.compile(row[3]) if row[3].startswith('^') else row[3],
                    confidence_weight=row[4],
                    description=row[5],
                    created_at=datetime.fromisoformat(row[6]),
                    last_updated=datetime.fromisoformat(row[7])
                )
                self._attack_patterns[pattern.pattern_id] = pattern
            
            # Load default patterns if none exist
            if not self._attack_patterns:
                self._load_default_patterns()
            
            self.logger.info(f"Loaded {len(self._attack_patterns)} attack patterns")
            
        except Exception as e:
            self.logger.error(f"Error loading attack patterns: {e}")
            self._load_default_patterns()
    
    def _load_default_patterns(self):
        """Load default attack patterns."""
        default_patterns = [
            {
                'pattern_id': 'sql_injection_1',
                'name': 'SQL Injection - Union Select',
                'attack_type': AttackType.SQL_INJECTION,
                'signature': re.compile(r'union\s+select', re.IGNORECASE),
                'confidence_weight': 0.9,
                'description': 'Detects UNION SELECT SQL injection attempts'
            },
            {
                'pattern_id': 'xss_1',
                'name': 'XSS - Script Tag',
                'attack_type': AttackType.XSS,
                'signature': re.compile(r'<script[^>]*>', re.IGNORECASE),
                'confidence_weight': 0.85,
                'description': 'Detects script tag XSS attempts'
            },
            {
                'pattern_id': 'brute_force_1',
                'name': 'Brute Force - Failed Login',
                'attack_type': AttackType.BRUTE_FORCE,
                'signature': 'authentication_failed',
                'confidence_weight': 0.7,
                'description': 'Detects authentication failure patterns'
            }
        ]
        
        for pattern_data in default_patterns:
            pattern = AttackPattern(
                pattern_id=pattern_data['pattern_id'],
                name=pattern_data['name'],
                attack_type=pattern_data['attack_type'],
                signature=pattern_data['signature'],
                confidence_weight=pattern_data['confidence_weight'],
                description=pattern_data['description'],
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            self._attack_patterns[pattern.pattern_id] = pattern
            self._store_attack_pattern(pattern)
    
    def _initialize_baselines(self):
        """Initialize statistical baselines for anomaly detection."""
        self._baseline_metrics = {
            'request_rate': {'mean': 10.0, 'std': 5.0},
            'payload_size': {'mean': 1024.0, 'std': 512.0},
            'session_duration': {'mean': 300.0, 'std': 150.0},
            'error_rate': {'mean': 0.05, 'std': 0.02}
        }
    
    def _extract_event_metrics(self, event_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical metrics from event data."""
        metrics = {}
        
        # Request rate (requests per minute)
        if 'timestamp' in event_data:
            metrics['request_rate'] = self._calculate_request_rate(event_data)
        
        # Payload size
        if 'content' in event_data:
            metrics['payload_size'] = len(str(event_data['content']))
        
        # Error indicators
        metrics['error_rate'] = 1.0 if event_data.get('is_error', False) else 0.0
        
        return metrics
    
    def _calculate_anomaly_score(self, metrics: Dict[str, float]) -> float:
        """Calculate anomaly score using statistical analysis."""
        try:
            anomaly_scores = []
            
            for metric_name, value in metrics.items():
                if metric_name in self._baseline_metrics:
                    baseline = self._baseline_metrics[metric_name]
                    
                    # Calculate z-score
                    z_score = abs(value - baseline['mean']) / baseline['std']
                    
                    # Convert to probability (0-1)
                    anomaly_score = min(z_score / 3.0, 1.0)  # 3-sigma rule
                    anomaly_scores.append(anomaly_score)
            
            # Return maximum anomaly score
            return max(anomaly_scores) if anomaly_scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating anomaly score: {e}")
            return 0.0
    
    def _calculate_request_rate(self, event_data: Dict[str, Any]) -> float:
        """Calculate request rate for the current source."""
        try:
            source_ip = event_data.get('source_ip')
            if not source_ip:
                return 0.0
            
            # Count recent requests from this IP
            current_time = datetime.now()
            window_start = current_time - timedelta(minutes=1)
            
            count = sum(
                1 for event in self._recent_events
                if (event.source_ip == source_ip and 
                    event.timestamp >= window_start)
            )
            
            return float(count)
            
        except Exception as e:
            self.logger.error(f"Error calculating request rate: {e}")
            return 0.0
    
    def _extract_user_activity(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user activity patterns from event data."""
        return {
            'action_type': event_data.get('action', 'unknown'),
            'resource_accessed': event_data.get('resource', ''),
            'timestamp': event_data.get('timestamp', datetime.now()),
            'source_ip': event_data.get('source_ip', ''),
            'user_agent': event_data.get('user_agent', '')
        }
    
    def _get_user_baseline(self, user_id: str) -> Dict[str, Any]:
        """Get historical baseline for user behavior."""
        # Simplified baseline - in practice, this would query historical data
        return {
            'typical_actions': ['read', 'write'],
            'typical_resources': ['/api/data', '/dashboard'],
            'typical_hours': list(range(9, 17)),  # 9 AM to 5 PM
            'typical_ips': ['192.168.1.0/24']
        }
    
    def _calculate_behavioral_deviation(
        self, 
        current_activity: Dict[str, Any],
        baseline: Dict[str, Any]
    ) -> float:
        """Calculate deviation from normal behavior patterns."""
        try:
            deviation_factors = []
            
            # Check action type
            action = current_activity.get('action_type', '')
            if action not in baseline.get('typical_actions', []):
                deviation_factors.append(0.5)
            
            # Check resource access
            resource = current_activity.get('resource_accessed', '')
            typical_resources = baseline.get('typical_resources', [])
            if not any(resource.startswith(tr) for tr in typical_resources):
                deviation_factors.append(0.3)
            
            # Check time of access
            timestamp = current_activity.get('timestamp', datetime.now())
            if timestamp.hour not in baseline.get('typical_hours', []):
                deviation_factors.append(0.2)
            
            # Return maximum deviation
            return max(deviation_factors) if deviation_factors else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating behavioral deviation: {e}")
            return 0.0
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{timestamp}_{self._events_processed}_{id(self)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _store_security_event(self, event: SecurityEvent):
        """Store security event in database."""
        try:
            cursor = self._db_connection.cursor()
            cursor.execute("""
                INSERT INTO security_events 
                (event_id, timestamp, source_ip, target_ip, attack_type, 
                 threat_level, detection_method, confidence_score, description, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.timestamp.isoformat(),
                event.source_ip,
                event.target_ip,
                event.attack_type.value,
                event.threat_level.value,
                event.detection_method.value,
                event.confidence_score,
                event.description,
                json.dumps(event.raw_data)
            ))
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing security event: {e}")
    
    def _store_attack_pattern(self, pattern: AttackPattern):
        """Store attack pattern in database."""
        try:
            cursor = self._db_connection.cursor()
            signature_str = pattern.signature.pattern if isinstance(pattern.signature, re.Pattern) else str(pattern.signature)
            
            cursor.execute("""
                INSERT OR REPLACE INTO attack_patterns 
                (pattern_id, name, attack_type, signature, confidence_weight, 
                 description, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.pattern_id,
                pattern.name,
                pattern.attack_type.value,
                signature_str,
                pattern.confidence_weight,
                pattern.description,
                pattern.created_at.isoformat(),
                pattern.last_updated.isoformat()
            ))
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing attack pattern: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop for IDS maintenance."""
        while self.is_active and not self._shutdown_event.is_set():
            try:
                # Update memory usage
                self._update_memory_usage()
                
                # Clean up old data
                self._cleanup_old_data()
                
                # Update performance metrics
                self._update_performance_metrics()
                
                # Check for memory pressure
                if self.memory_usage_mb > self.config.MAX_MEMORY_MB * 0.9:
                    self._trigger_memory_cleanup()
                
                # Sleep for monitoring interval
                self._shutdown_event.wait(30)  # 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in IDS monitoring loop: {e}")
                self._shutdown_event.wait(1)
    
    def _update_memory_usage(self):
        """Update current memory usage estimate."""
        try:
            # Estimate memory usage
            events_memory = len(self._recent_events) * 0.01  # ~10KB per event
            patterns_memory = len(self._attack_patterns) * 0.005  # ~5KB per pattern
            sessions_memory = len(self._active_sessions) * 0.002  # ~2KB per session
            base_memory = 5.0  # Base memory overhead
            
            self.memory_usage_mb = (
                events_memory + patterns_memory + 
                sessions_memory + base_memory
            )
            
        except Exception as e:
            self.logger.error(f"Error updating memory usage: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data to free memory."""
        try:
            # Clean old events from database
            cutoff_date = datetime.now() - timedelta(days=self.config.EVENT_RETENTION_DAYS)
            cursor = self._db_connection.cursor()
            cursor.execute(
                "DELETE FROM security_events WHERE timestamp < ?",
                (cutoff_date.isoformat(),)
            )
            
            # Clean old sessions
            session_cutoff = datetime.now() - timedelta(
                minutes=self.config.SESSION_TIMEOUT_MINUTES
            )
            expired_sessions = [
                sid for sid, session in self._active_sessions.items()
                if session.last_activity < session_cutoff
            ]
            
            for session_id in expired_sessions:
                del self._active_sessions[session_id]
            
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def _update_performance_metrics(self):
        """Update performance metrics in database."""
        try:
            cursor = self._db_connection.cursor()
            
            # Average detection time
            if self._detection_times:
                avg_detection_time = sum(self._detection_times) / len(self._detection_times)
                cursor.execute(
                    "INSERT INTO ids_metrics (metric_name, metric_value) VALUES (?, ?)",
                    ("avg_detection_time_ms", avg_detection_time)
                )
            
            # Events processed rate
            cursor.execute(
                "INSERT INTO ids_metrics (metric_name, metric_value) VALUES (?, ?)",
                ("events_processed_total", self._events_processed)
            )
            
            # Memory usage
            cursor.execute(
                "INSERT INTO ids_metrics (metric_name, metric_value) VALUES (?, ?)",
                ("memory_usage_mb", self.memory_usage_mb)
            )
            
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    def _trigger_memory_cleanup(self):
        """Trigger aggressive memory cleanup."""
        try:
            # Limit recent events
            if len(self._recent_events) > self.config.MAX_EVENTS_IN_MEMORY // 2:
                # Keep only the most recent half
                events_to_keep = self.config.MAX_EVENTS_IN_MEMORY // 2
                self._recent_events = collections.deque(
                    list(self._recent_events)[-events_to_keep:],
                    maxlen=self.config.MAX_EVENTS_IN_MEMORY
                )
            
            # Clear old detection times
            if len(self._detection_times) > 50:
                self._detection_times = collections.deque(
                    list(self._detection_times)[-50:],
                    maxlen=100
                )
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info("IDS memory cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during memory cleanup: {e}")
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.memory_usage_mb
    
    def cleanup_memory(self):
        """External interface for memory cleanup."""
        self._trigger_memory_cleanup()
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection statistics."""
        return {
            'events_processed': self._events_processed,
            'true_positives': self._true_positives,
            'false_positives': self._false_positives,
            'active_patterns': len(self._attack_patterns),
            'recent_events': len(self._recent_events),
            'active_sessions': len(self._active_sessions),
            'memory_usage_mb': self.memory_usage_mb,
            'avg_detection_time_ms': (
                sum(self._detection_times) / len(self._detection_times)
                if self._detection_times else 0.0
            )
        }
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent security events."""
        events = list(self._recent_events)[-limit:]
        return [
            {
                'event_id': event.event_id,
                'timestamp': event.timestamp.isoformat(),
                'attack_type': event.attack_type.value,
                'threat_level': event.threat_level.value,
                'confidence_score': event.confidence_score,
                'description': event.description,
                'source_ip': event.source_ip
            }
            for event in events
        ]


# Export main classes and functions
__all__ = [
    'IntrusionDetectionSystem',
    'SecurityEvent',
    'AttackPattern',
    'ThreatLevel',
    'AttackType',
    'DetectionMethod'
]
