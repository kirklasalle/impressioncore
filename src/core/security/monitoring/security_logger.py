"""
ImpressionCore Security Logger

Comprehensive security logging system with audit trails, event correlation,
and forensics support. Optimized for GTX 1050 Ti hardware constraints with
efficient storage and real-time log processing capabilities.

Author: ImpressionCore Security Team
Created: 2025-01-27
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Budget: 25MB for security logging
"""

import os
import sys
import asyncio
import logging
import threading
import time
import json
import sqlite3
import gzip
import hashlib
from typing import Dict, List, Optional, Union, Any, Callable, TextIO
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import collections
import gc
import weakref
from contextlib import contextmanager
import csv
import uuid

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.utils.rich_enhancements import RichStatusManager
from src.core.utils.rich_logging import RichLogger


class LogLevel(Enum):
    """Security log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    AUDIT = "audit"
    SECURITY = "security"


class EventCategory(Enum):
    """Categories of security events."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_ACCESS = "system_access"
    NETWORK_ACTIVITY = "network_activity"
    FILE_OPERATION = "file_operation"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_VIOLATION = "security_violation"
    AUDIT_TRAIL = "audit_trail"
    COMPLIANCE = "compliance"
    ERROR_EVENT = "error_event"
    PERFORMANCE = "performance"


class LogFormat(Enum):
    """Log output formats."""
    JSON = "json"
    CSV = "csv"
    SYSLOG = "syslog"
    CEF = "cef"  # Common Event Format
    STRUCTURED = "structured"


@dataclass
class SecurityLogEntry:
    """Security log entry structure."""
    log_id: str
    timestamp: datetime
    level: LogLevel
    category: EventCategory
    event_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    source_ip: Optional[str]
    target_resource: Optional[str]
    action: str
    outcome: str  # success, failure, unknown
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoggerMetrics:
    """Security logger performance metrics."""
    logs_processed: int = 0
    logs_written: int = 0
    logs_compressed: int = 0
    bytes_written: int = 0
    processing_time_ms: float = 0.0
    compression_ratio: float = 0.0
    error_count: int = 0
    queue_size: int = 0


class SecurityLoggerConfig:
    """Configuration for security logger."""
    
    # Memory management
    MAX_MEMORY_MB = 25
    MAX_QUEUE_SIZE = 10000
    MAX_BATCH_SIZE = 500
    MAX_CACHE_ENTRIES = 1000
    
    # File management
    LOG_BASE_PATH = "logs/security"
    MAX_LOG_FILE_SIZE_MB = 100
    LOG_ROTATION_COUNT = 10
    COMPRESSION_ENABLED = True
    
    # Performance settings
    FLUSH_INTERVAL_SECONDS = 30
    BATCH_PROCESSING_INTERVAL = 5
    CORRELATION_WINDOW_MINUTES = 10
    
    # Database settings
    SECURITY_LOG_DB_PATH = "data/security/security_logs.db"
    LOG_RETENTION_DAYS = 90
    COMPRESSED_LOG_RETENTION_DAYS = 365
    
    # Compliance settings
    AUDIT_TRAIL_REQUIRED = True
    TAMPER_PROTECTION = True
    DIGITAL_SIGNATURES = False  # Disabled for performance
    
    # Alert thresholds
    ERROR_RATE_THRESHOLD = 0.1  # 10% error rate
    QUEUE_SIZE_WARNING_THRESHOLD = 5000
    PROCESSING_DELAY_WARNING_MS = 1000


class SecurityLogger:
    """
    Advanced security logging system with comprehensive audit capabilities.
    
    Features:
    - Real-time log processing and correlation
    - Multiple output formats (JSON, CSV, CEF, Syslog)
    - Log rotation and compression
    - Event correlation and chain tracking
    - Performance monitoring and metrics
    - Memory-optimized for GTX 1050 Ti constraints
    """
    
    def __init__(self):
        self.config = SecurityLoggerConfig()
        self.logger = self._setup_logging()
        self.status_manager = RichStatusManager("Security Logger")
        
        # System state
        self.is_active = False
        self.memory_usage_mb = 0.0
        self._shutdown_event = threading.Event()
        
        # Log processing
        self._log_queue: collections.deque = collections.deque(
            maxlen=self.config.MAX_QUEUE_SIZE
        )
        self._log_cache: collections.OrderedDict = collections.OrderedDict()
        self._processing_thread: Optional[threading.Thread] = None
        self._queue_lock = threading.Lock()
        
        # File management
        self._log_files: Dict[str, TextIO] = {}
        self._current_file_sizes: Dict[str, int] = {}
        self._file_rotation_lock = threading.Lock()
        
        # Event correlation
        self._correlation_cache: Dict[str, List[str]] = {}
        self._event_chains: Dict[str, List[SecurityLogEntry]] = {}
        
        # Performance tracking
        self.metrics = LoggerMetrics()
        self._processing_times: collections.deque = collections.deque(maxlen=100)
        
        # Database
        self._db_connection: Optional[sqlite3.Connection] = None
        self._initialize_database()
        
        # Initialize log directories
        self._initialize_log_directories()
    
    def _setup_logging(self) -> RichLogger:
        """Setup rich logging for the security logger."""
        logger = RichLogger(
            name="security_logger",
            level=logging.INFO,
            log_file="logs/security_logger.log"
        )
        return logger
    
    def _initialize_database(self):
        """Initialize the security logging database."""
        try:
            os.makedirs(os.path.dirname(self.config.SECURITY_LOG_DB_PATH), exist_ok=True)
            self._db_connection = sqlite3.connect(
                self.config.SECURITY_LOG_DB_PATH,
                check_same_thread=False
            )
            
            self._create_log_tables()
            self.logger.info("Security logging database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize security logging database: {e}")
            raise
    
    def _create_log_tables(self):
        """Create security logging database tables."""
        cursor = self._db_connection.cursor()
        
        # Security logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_logs (
                log_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                category TEXT NOT NULL,
                event_type TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                source_ip TEXT,
                target_resource TEXT,
                action TEXT NOT NULL,
                outcome TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                risk_score REAL DEFAULT 0.0,
                correlation_id TEXT,
                parent_event_id TEXT,
                tags TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Event correlations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_correlations (
                correlation_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                PRIMARY KEY (correlation_id, event_id)
            )
        """)
        
        # Logger metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logger_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Audit trail table for tamper detection
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id TEXT NOT NULL,
                old_hash TEXT,
                new_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON security_logs(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_user_id ON security_logs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_category ON security_logs(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_correlation ON security_logs(correlation_id)")
        
        self._db_connection.commit()
    
    def _initialize_log_directories(self):
        """Initialize log directory structure."""
        try:
            # Create main log directories
            log_dirs = [
                self.config.LOG_BASE_PATH,
                f"{self.config.LOG_BASE_PATH}/audit",
                f"{self.config.LOG_BASE_PATH}/security",
                f"{self.config.LOG_BASE_PATH}/access",
                f"{self.config.LOG_BASE_PATH}/system",
                f"{self.config.LOG_BASE_PATH}/compressed"
            ]
            
            for log_dir in log_dirs:
                os.makedirs(log_dir, exist_ok=True)
            
            self.logger.info("Log directories initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize log directories: {e}")
            raise
    
    def start(self) -> bool:
        """Start the security logging system."""
        try:
            self.status_manager.start("Starting security logging system...")
            
            # Start processing thread
            self.is_active = True
            self._processing_thread = threading.Thread(
                target=self._processing_loop,
                daemon=True
            )
            self._processing_thread.start()
            
            # Update memory usage
            self._update_memory_usage()
            
            self.status_manager.stop("Security logging system started")
            self.logger.info("Security logging system started")
            return True
            
        except Exception as e:
            self.status_manager.stop(f"Failed to start security logger: {e}")
            self.logger.error(f"Failed to start security logger: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the security logging system."""
        try:
            self.status_manager.start("Stopping security logging system...")
            
            # Signal shutdown
            self.is_active = False
            self._shutdown_event.set()
            
            # Wait for processing thread
            if self._processing_thread:
                self._processing_thread.join(timeout=10.0)
            
            # Flush remaining logs
            self._flush_all_logs()
            
            # Close log files
            self._close_log_files()
            
            # Close database
            if self._db_connection:
                self._db_connection.close()
                self._db_connection = None
            
            self.status_manager.stop("Security logging system stopped")
            self.logger.info("Security logging system stopped")
            return True
            
        except Exception as e:
            self.status_manager.stop(f"Error stopping security logger: {e}")
            self.logger.error(f"Error stopping security logger: {e}")
            return False
    
    def log_security_event(
        self,
        level: LogLevel,
        category: EventCategory,
        event_type: str,
        action: str,
        outcome: str,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        target_resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        risk_score: float = 0.0,
        correlation_id: Optional[str] = None,
        parent_event_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Log a security event.
        
        Args:
            level: Log level
            category: Event category
            event_type: Specific event type
            action: Action performed
            outcome: Result of the action
            message: Human-readable message
            user_id: User identifier
            session_id: Session identifier
            source_ip: Source IP address
            target_resource: Target resource
            details: Additional event details
            risk_score: Risk score (0.0-1.0)
            correlation_id: Correlation identifier
            parent_event_id: Parent event identifier
            tags: Event tags
            
        Returns:
            Log entry ID
        """
        try:
            # Create log entry
            log_entry = SecurityLogEntry(
                log_id=self._generate_log_id(),
                timestamp=datetime.now(),
                level=level,
                category=category,
                event_type=event_type,
                user_id=user_id,
                session_id=session_id,
                source_ip=source_ip,
                target_resource=target_resource,
                action=action,
                outcome=outcome,
                message=message,
                details=details or {},
                risk_score=risk_score,
                correlation_id=correlation_id,
                parent_event_id=parent_event_id,
                tags=tags or [],
                metadata={
                    'logger_version': '1.0',
                    'system_id': 'impressioncore'
                }
            )
            
            # Add to processing queue
            with self._queue_lock:
                self._log_queue.append(log_entry)
                self.metrics.queue_size = len(self._log_queue)
            
            # Check queue size warning
            if self.metrics.queue_size > self.config.QUEUE_SIZE_WARNING_THRESHOLD:
                self.logger.warning(
                    f"Log queue size ({self.metrics.queue_size}) exceeds threshold"
                )
            
            return log_entry.log_id
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {e}")
            return ""
    
    def log_authentication_event(
        self,
        user_id: str,
        action: str,
        outcome: str,
        source_ip: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log authentication event."""
        return self.log_security_event(
            level=LogLevel.AUDIT,
            category=EventCategory.AUTHENTICATION,
            event_type="user_authentication",
            action=action,
            outcome=outcome,
            message=f"User {user_id} authentication {action}: {outcome}",
            user_id=user_id,
            source_ip=source_ip,
            details=details,
            risk_score=0.5 if outcome == "failure" else 0.1,
            tags=["authentication", "audit"]
        )
    
    def log_authorization_event(
        self,
        user_id: str,
        resource: str,
        action: str,
        outcome: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log authorization event."""
        return self.log_security_event(
            level=LogLevel.AUDIT,
            category=EventCategory.AUTHORIZATION,
            event_type="resource_authorization",
            action=action,
            outcome=outcome,
            message=f"User {user_id} {action} access to {resource}: {outcome}",
            user_id=user_id,
            target_resource=resource,
            details=details,
            risk_score=0.6 if outcome == "denied" else 0.1,
            tags=["authorization", "audit"]
        )
    
    def log_data_access_event(
        self,
        user_id: str,
        resource: str,
        action: str,
        outcome: str,
        data_volume: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log data access event."""
        event_details = details or {}
        if data_volume is not None:
            event_details['data_volume'] = data_volume
        
        # Higher risk score for large data volumes
        risk_score = 0.1
        if data_volume and data_volume > 1000000:  # > 1MB
            risk_score = 0.4
        
        return self.log_security_event(
            level=LogLevel.INFO,
            category=EventCategory.DATA_ACCESS,
            event_type="data_operation",
            action=action,
            outcome=outcome,
            message=f"User {user_id} {action} data from {resource}: {outcome}",
            user_id=user_id,
            target_resource=resource,
            details=event_details,
            risk_score=risk_score,
            tags=["data_access", "audit"]
        )
    
    def log_security_violation(
        self,
        violation_type: str,
        description: str,
        user_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        risk_score: float = 0.8
    ) -> str:
        """Log security violation."""
        return self.log_security_event(
            level=LogLevel.CRITICAL,
            category=EventCategory.SECURITY_VIOLATION,
            event_type=violation_type,
            action="security_violation",
            outcome="detected",
            message=f"Security violation detected: {description}",
            user_id=user_id,
            source_ip=source_ip,
            details=details,
            risk_score=risk_score,
            tags=["security", "violation", "alert"]
        )
    
    def start_correlation_chain(
        self,
        chain_type: str,
        description: str,
        user_id: Optional[str] = None
    ) -> str:
        """Start a new event correlation chain."""
        correlation_id = self._generate_correlation_id()
        
        # Log chain start event
        self.log_security_event(
            level=LogLevel.INFO,
            category=EventCategory.AUDIT_TRAIL,
            event_type="correlation_chain_start",
            action="start_chain",
            outcome="success",
            message=f"Started correlation chain: {description}",
            user_id=user_id,
            correlation_id=correlation_id,
            details={"chain_type": chain_type},
            tags=["correlation", "chain_start"]
        )
        
        # Initialize chain tracking
        self._event_chains[correlation_id] = []
        
        return correlation_id
    
    def add_to_correlation_chain(
        self,
        correlation_id: str,
        log_entry_id: str
    ):
        """Add an event to a correlation chain."""
        try:
            if correlation_id in self._event_chains:
                # Find the log entry
                log_entry = self._find_log_entry(log_entry_id)
                if log_entry:
                    self._event_chains[correlation_id].append(log_entry)
                    
                    # Store correlation in database
                    self._store_correlation(correlation_id, log_entry_id)
        
        except Exception as e:
            self.logger.error(f"Error adding to correlation chain: {e}")
    
    def _processing_loop(self):
        """Main log processing loop."""
        while self.is_active and not self._shutdown_event.is_set():
            try:
                # Process queued logs
                self._process_log_batch()
                
                # Update memory usage
                self._update_memory_usage()
                
                # Rotate log files if needed
                self._check_log_rotation()
                
                # Compress old logs
                self._compress_old_logs()
                
                # Clean up old data
                self._cleanup_old_data()
                
                # Update metrics
                self._update_metrics()
                
                # Sleep for processing interval
                self._shutdown_event.wait(self.config.BATCH_PROCESSING_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Error in log processing loop: {e}")
                self._shutdown_event.wait(1)
    
    def _process_log_batch(self):
        """Process a batch of queued logs."""
        try:
            start_time = time.time()
            batch = []
            
            # Collect batch
            with self._queue_lock:
                batch_size = min(len(self._log_queue), self.config.MAX_BATCH_SIZE)
                for _ in range(batch_size):
                    if self._log_queue:
                        batch.append(self._log_queue.popleft())
                
                self.metrics.queue_size = len(self._log_queue)
            
            if not batch:
                return
            
            # Process each log entry
            for log_entry in batch:
                self._process_single_log(log_entry)
            
            # Update processing metrics
            processing_time = (time.time() - start_time) * 1000
            self._processing_times.append(processing_time)
            self.metrics.logs_processed += len(batch)
            
            # Check processing delay warning
            if processing_time > self.config.PROCESSING_DELAY_WARNING_MS:
                self.logger.warning(
                    f"Log processing delay: {processing_time:.1f}ms for {len(batch)} logs"
                )
            
        except Exception as e:
            self.logger.error(f"Error processing log batch: {e}")
    
    def _process_single_log(self, log_entry: SecurityLogEntry):
        """Process a single log entry."""
        try:
            # Store in database
            self._store_log_entry(log_entry)
            
            # Write to log files
            self._write_to_log_files(log_entry)
            
            # Update cache
            self._update_cache(log_entry)
            
            # Handle correlations
            if log_entry.correlation_id:
                self._handle_correlation(log_entry)
            
            self.metrics.logs_written += 1
            
        except Exception as e:
            self.logger.error(f"Error processing log entry {log_entry.log_id}: {e}")
            self.metrics.error_count += 1
    
    def _store_log_entry(self, log_entry: SecurityLogEntry):
        """Store log entry in database."""
        try:
            cursor = self._db_connection.cursor()
            cursor.execute("""
                INSERT INTO security_logs 
                (log_id, timestamp, level, category, event_type, user_id, session_id,
                 source_ip, target_resource, action, outcome, message, details,
                 risk_score, correlation_id, parent_event_id, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_entry.log_id,
                log_entry.timestamp.isoformat(),
                log_entry.level.value,
                log_entry.category.value,
                log_entry.event_type,
                log_entry.user_id,
                log_entry.session_id,
                log_entry.source_ip,
                log_entry.target_resource,
                log_entry.action,
                log_entry.outcome,
                log_entry.message,
                json.dumps(log_entry.details),
                log_entry.risk_score,
                log_entry.correlation_id,
                log_entry.parent_event_id,
                json.dumps(log_entry.tags),
                json.dumps(log_entry.metadata)
            ))
            
            # Create audit trail entry if tamper protection enabled
            if self.config.TAMPER_PROTECTION:
                self._create_audit_trail_entry(log_entry)
            
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing log entry: {e}")
            raise
    
    def _write_to_log_files(self, log_entry: SecurityLogEntry):
        """Write log entry to appropriate log files."""
        try:
            # Determine log file based on category
            file_mapping = {
                EventCategory.AUTHENTICATION: "audit/authentication.log",
                EventCategory.AUTHORIZATION: "audit/authorization.log",
                EventCategory.DATA_ACCESS: "access/data_access.log",
                EventCategory.SECURITY_VIOLATION: "security/violations.log",
                EventCategory.AUDIT_TRAIL: "audit/audit_trail.log",
                EventCategory.SYSTEM_ACCESS: "system/system_access.log"
            }
            
            log_file_path = file_mapping.get(
                log_entry.category, 
                "security/general.log"
            )
            
            # Write in JSON format
            self._write_json_log(log_file_path, log_entry)
            
            # Write high-risk events to separate file
            if log_entry.risk_score > 0.7:
                self._write_json_log("security/high_risk.log", log_entry)
            
        except Exception as e:
            self.logger.error(f"Error writing to log files: {e}")
    
    def _write_json_log(self, file_path: str, log_entry: SecurityLogEntry):
        """Write log entry in JSON format."""
        try:
            full_path = os.path.join(self.config.LOG_BASE_PATH, file_path)
            
            # Get or create file handle
            if file_path not in self._log_files:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                self._log_files[file_path] = open(full_path, 'a', encoding='utf-8')
                self._current_file_sizes[file_path] = os.path.getsize(full_path) if os.path.exists(full_path) else 0
            
            # Prepare log data
            log_data = {
                'log_id': log_entry.log_id,
                'timestamp': log_entry.timestamp.isoformat(),
                'level': log_entry.level.value,
                'category': log_entry.category.value,
                'event_type': log_entry.event_type,
                'user_id': log_entry.user_id,
                'session_id': log_entry.session_id,
                'source_ip': log_entry.source_ip,
                'target_resource': log_entry.target_resource,
                'action': log_entry.action,
                'outcome': log_entry.outcome,
                'message': log_entry.message,
                'details': log_entry.details,
                'risk_score': log_entry.risk_score,
                'correlation_id': log_entry.correlation_id,
                'parent_event_id': log_entry.parent_event_id,
                'tags': log_entry.tags,
                'metadata': log_entry.metadata
            }
            
            # Write JSON line
            json_line = json.dumps(log_data, separators=(',', ':'))
            self._log_files[file_path].write(json_line + '\n')
            
            # Update file size tracking
            self._current_file_sizes[file_path] += len(json_line.encode('utf-8')) + 1
            self.metrics.bytes_written += len(json_line.encode('utf-8')) + 1
            
        except Exception as e:
            self.logger.error(f"Error writing JSON log: {e}")
    
    def _update_cache(self, log_entry: SecurityLogEntry):
        """Update log cache with recent entries."""
        try:
            # Add to cache
            self._log_cache[log_entry.log_id] = log_entry
            
            # Limit cache size
            while len(self._log_cache) > self.config.MAX_CACHE_ENTRIES:
                self._log_cache.popitem(last=False)  # Remove oldest
            
        except Exception as e:
            self.logger.error(f"Error updating cache: {e}")
    
    def _handle_correlation(self, log_entry: SecurityLogEntry):
        """Handle event correlation."""
        try:
            correlation_id = log_entry.correlation_id
            
            if correlation_id not in self._correlation_cache:
                self._correlation_cache[correlation_id] = []
            
            self._correlation_cache[correlation_id].append(log_entry.log_id)
            
            # Store correlation in database
            self._store_correlation(correlation_id, log_entry.log_id)
            
        except Exception as e:
            self.logger.error(f"Error handling correlation: {e}")
    
    def _store_correlation(self, correlation_id: str, event_id: str):
        """Store event correlation in database."""
        try:
            cursor = self._db_connection.cursor()
            
            # Get sequence number
            cursor.execute(
                "SELECT COUNT(*) FROM event_correlations WHERE correlation_id = ?",
                (correlation_id,)
            )
            sequence_number = cursor.fetchone()[0]
            
            # Insert correlation
            cursor.execute("""
                INSERT INTO event_correlations 
                (correlation_id, event_id, sequence_number, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                correlation_id,
                event_id,
                sequence_number,
                datetime.now().isoformat()
            ))
            
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing correlation: {e}")
    
    def _create_audit_trail_entry(self, log_entry: SecurityLogEntry):
        """Create audit trail entry for tamper detection."""
        try:
            # Calculate hash of log entry
            log_data = json.dumps(asdict(log_entry), sort_keys=True)
            log_hash = hashlib.sha256(log_data.encode()).hexdigest()
            
            cursor = self._db_connection.cursor()
            cursor.execute("""
                INSERT INTO audit_trail 
                (operation, table_name, record_id, new_hash)
                VALUES (?, ?, ?, ?)
            """, (
                "INSERT",
                "security_logs",
                log_entry.log_id,
                log_hash
            ))
            
        except Exception as e:
            self.logger.error(f"Error creating audit trail entry: {e}")
    
    def _check_log_rotation(self):
        """Check if log files need rotation."""
        try:
            with self._file_rotation_lock:
                for file_path, current_size in self._current_file_sizes.items():
                    if current_size > self.config.MAX_LOG_FILE_SIZE_MB * 1024 * 1024:
                        self._rotate_log_file(file_path)
        
        except Exception as e:
            self.logger.error(f"Error checking log rotation: {e}")
    
    def _rotate_log_file(self, file_path: str):
        """Rotate a log file."""
        try:
            # Close current file
            if file_path in self._log_files:
                self._log_files[file_path].close()
                del self._log_files[file_path]
            
            full_path = os.path.join(self.config.LOG_BASE_PATH, file_path)
            
            # Rotate existing files
            for i in range(self.config.LOG_ROTATION_COUNT - 1, 0, -1):
                old_file = f"{full_path}.{i}"
                new_file = f"{full_path}.{i + 1}"
                
                if os.path.exists(old_file):
                    if os.path.exists(new_file):
                        os.remove(new_file)
                    os.rename(old_file, new_file)
            
            # Move current file to .1
            if os.path.exists(full_path):
                os.rename(full_path, f"{full_path}.1")
                
                # Compress the rotated file
                if self.config.COMPRESSION_ENABLED:
                    self._compress_log_file(f"{full_path}.1")
            
            # Reset file size tracking
            self._current_file_sizes[file_path] = 0
            
            self.logger.info(f"Rotated log file: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error rotating log file {file_path}: {e}")
    
    def _compress_log_file(self, file_path: str):
        """Compress a log file."""
        try:
            compressed_path = f"{file_path}.gz"
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Remove original file
            os.remove(file_path)
            
            # Update metrics
            original_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            compressed_size = os.path.getsize(compressed_path)
            
            if original_size > 0:
                compression_ratio = compressed_size / original_size
                self.metrics.compression_ratio = (
                    self.metrics.compression_ratio * 0.9 + compression_ratio * 0.1
                )
            
            self.metrics.logs_compressed += 1
            
            self.logger.info(f"Compressed log file: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error compressing log file {file_path}: {e}")
    
    def _compress_old_logs(self):
        """Compress old uncompressed log files."""
        try:
            cutoff_time = datetime.now() - timedelta(days=1)
            
            for root, dirs, files in os.walk(self.config.LOG_BASE_PATH):
                for file in files:
                    if file.endswith('.log') and not file.endswith('.gz'):
                        file_path = os.path.join(root, file)
                        
                        # Check file age
                        if os.path.getmtime(file_path) < cutoff_time.timestamp():
                            self._compress_log_file(file_path)
        
        except Exception as e:
            self.logger.error(f"Error compressing old logs: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data to free memory and storage."""
        try:
            # Clean old database records
            cutoff_date = datetime.now() - timedelta(days=self.config.LOG_RETENTION_DAYS)
            cursor = self._db_connection.cursor()
            
            cursor.execute(
                "DELETE FROM security_logs WHERE timestamp < ?",
                (cutoff_date.isoformat(),)
            )
            
            cursor.execute(
                "DELETE FROM event_correlations WHERE timestamp < ?",
                (cutoff_date.isoformat(),)
            )
            
            # Clean old compressed logs
            compressed_cutoff = datetime.now() - timedelta(
                days=self.config.COMPRESSED_LOG_RETENTION_DAYS
            )
            
            compressed_dir = os.path.join(self.config.LOG_BASE_PATH, "compressed")
            if os.path.exists(compressed_dir):
                for file in os.listdir(compressed_dir):
                    file_path = os.path.join(compressed_dir, file)
                    if os.path.getmtime(file_path) < compressed_cutoff.timestamp():
                        os.remove(file_path)
            
            # Clean correlation cache
            cutoff_time = datetime.now() - timedelta(
                minutes=self.config.CORRELATION_WINDOW_MINUTES
            )
            
            expired_correlations = []
            for correlation_id, events in self._correlation_cache.items():
                # Check if correlation is old (simplified check)
                if len(events) == 0:
                    expired_correlations.append(correlation_id)
            
            for correlation_id in expired_correlations:
                del self._correlation_cache[correlation_id]
                if correlation_id in self._event_chains:
                    del self._event_chains[correlation_id]
            
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def _flush_all_logs(self):
        """Flush all log files."""
        try:
            for file_handle in self._log_files.values():
                file_handle.flush()
                os.fsync(file_handle.fileno())
        
        except Exception as e:
            self.logger.error(f"Error flushing logs: {e}")
    
    def _close_log_files(self):
        """Close all log files."""
        try:
            for file_handle in self._log_files.values():
                file_handle.close()
            
            self._log_files.clear()
            self._current_file_sizes.clear()
        
        except Exception as e:
            self.logger.error(f"Error closing log files: {e}")
    
    def _update_metrics(self):
        """Update logger performance metrics."""
        try:
            # Calculate average processing time
            if self._processing_times:
                self.metrics.processing_time_ms = sum(self._processing_times) / len(self._processing_times)
            
            # Store metrics in database
            cursor = self._db_connection.cursor()
            
            metrics_to_store = [
                ("logs_processed", self.metrics.logs_processed),
                ("logs_written", self.metrics.logs_written),
                ("queue_size", self.metrics.queue_size),
                ("processing_time_ms", self.metrics.processing_time_ms),
                ("memory_usage_mb", self.memory_usage_mb),
                ("error_count", self.metrics.error_count)
            ]
            
            for metric_name, metric_value in metrics_to_store:
                cursor.execute(
                    "INSERT INTO logger_metrics (metric_name, metric_value) VALUES (?, ?)",
                    (metric_name, metric_value)
                )
            
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
    
    def _update_memory_usage(self):
        """Update current memory usage estimate."""
        try:
            # Estimate memory usage
            queue_memory = len(self._log_queue) * 0.002  # ~2KB per log entry
            cache_memory = len(self._log_cache) * 0.002  # ~2KB per cache entry
            correlation_memory = len(self._correlation_cache) * 0.001  # ~1KB per correlation
            file_handles_memory = len(self._log_files) * 0.01  # ~10KB per file handle
            base_memory = 5.0  # Base overhead
            
            self.memory_usage_mb = (
                queue_memory + cache_memory + correlation_memory + 
                file_handles_memory + base_memory
            )
            
        except Exception as e:
            self.logger.error(f"Error updating memory usage: {e}")
    
    def _generate_log_id(self) -> str:
        """Generate unique log ID."""
        return str(uuid.uuid4())
    
    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.sha256(f"{timestamp}_{uuid.uuid4()}".encode()).hexdigest()[:16]
    
    def _find_log_entry(self, log_id: str) -> Optional[SecurityLogEntry]:
        """Find log entry by ID."""
        return self._log_cache.get(log_id)
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.memory_usage_mb
    
    def cleanup_memory(self):
        """External interface for memory cleanup."""
        self._cleanup_old_data()
        gc.collect()
    
    def get_logger_stats(self) -> Dict[str, Any]:
        """Get security logger statistics."""
        return {
            'logs_processed': self.metrics.logs_processed,
            'logs_written': self.metrics.logs_written,
            'logs_compressed': self.metrics.logs_compressed,
            'bytes_written': self.metrics.bytes_written,
            'queue_size': self.metrics.queue_size,
            'cache_size': len(self._log_cache),
            'active_correlations': len(self._correlation_cache),
            'open_files': len(self._log_files),
            'memory_usage_mb': self.memory_usage_mb,
            'avg_processing_time_ms': self.metrics.processing_time_ms,
            'compression_ratio': self.metrics.compression_ratio,
            'error_count': self.metrics.error_count
        }
    
    def search_logs(
        self,
        query: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[LogLevel] = None,
        category: Optional[EventCategory] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search security logs with filters."""
        try:
            cursor = self._db_connection.cursor()
            
            # Build query
            sql = "SELECT * FROM security_logs WHERE message LIKE ?"
            params = [f"%{query}%"]
            
            if start_time:
                sql += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                sql += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            if level:
                sql += " AND level = ?"
                params.append(level.value)
            
            if category:
                sql += " AND category = ?"
                params.append(category.value)
            
            if user_id:
                sql += " AND user_id = ?"
                params.append(user_id)
            
            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert to dictionaries
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in rows:
                log_dict = dict(zip(columns, row))
                # Parse JSON fields
                if log_dict.get('details'):
                    log_dict['details'] = json.loads(log_dict['details'])
                if log_dict.get('tags'):
                    log_dict['tags'] = json.loads(log_dict['tags'])
                if log_dict.get('metadata'):
                    log_dict['metadata'] = json.loads(log_dict['metadata'])
                
                results.append(log_dict)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching logs: {e}")
            return []
    
    def get_correlation_chain(self, correlation_id: str) -> List[Dict[str, Any]]:
        """Get events in a correlation chain."""
        try:
            cursor = self._db_connection.cursor()
            cursor.execute("""
                SELECT sl.* FROM security_logs sl
                JOIN event_correlations ec ON sl.log_id = ec.event_id
                WHERE ec.correlation_id = ?
                ORDER BY ec.sequence_number
            """, (correlation_id,))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            results = []
            for row in rows:
                log_dict = dict(zip(columns, row))
                # Parse JSON fields
                if log_dict.get('details'):
                    log_dict['details'] = json.loads(log_dict['details'])
                if log_dict.get('tags'):
                    log_dict['tags'] = json.loads(log_dict['tags'])
                if log_dict.get('metadata'):
                    log_dict['metadata'] = json.loads(log_dict['metadata'])
                
                results.append(log_dict)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting correlation chain: {e}")
            return []


# Export main classes and functions
__all__ = [
    'SecurityLogger',
    'SecurityLogEntry',
    'LogLevel',
    'EventCategory',
    'LogFormat',
    'LoggerMetrics'
]
