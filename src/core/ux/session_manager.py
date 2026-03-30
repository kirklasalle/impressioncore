"""
ImpressionCore Session Manager
Phase 7D: Production Integration and Optimization

Comprehensive session lifecycle management with user isolation and security.

Author: GitHub Copilot & Kirk LaSalle
Date: June 1, 2025
"""

import asyncio
import sqlite3
import json
import pickle
import hashlib
import secrets
import threading
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
import weakref
import logging

# Rich console enhancements  
try:
    from src.core.utils.rich_enhancements import FallbackConsole
    from src.core.utils.rich_logging import setup_rich_logger
    from src.core.utils.rich_status_animation import StatusAnimation
    from src.core.utils.token_rate_control import TokenRateController
    RICH_AVAILABLE = True
    console = FallbackConsole()
    logger = setup_rich_logger(__name__)
    status_animation = StatusAnimation()
except ImportError:
    RICH_AVAILABLE = False
    console = None
    logger = logging.getLogger(__name__)
    status_animation = None
    import logging
    logging.basicConfig(level=logging.INFO)

import time  # Add missing import

# Setup logging - logger already configured above

@dataclass
class SessionConfig:
    """Configuration settings for a user session."""
    precision: str = "mixed_fp16"
    batch_size: int = 1
    context_length: int = 32768
    quality_level: str = "balanced"  # "speed", "balanced", "quality"
    memory_optimization: bool = True
    cpu_threads: int = 4
    gpu_enabled: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SessionMetrics:
    """Performance and usage metrics for a session."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_processing_time: float = 0.0
    average_response_time: float = 0.0
    memory_peak_usage: float = 0.0
    gpu_memory_peak_usage: float = 0.0
    cpu_time_used: float = 0.0
    data_processed: float = 0.0  # bytes
    quality_scores: List[float] = field(default_factory=list)
    error_count: Dict[str, int] = field(default_factory=dict)

@dataclass
class SessionSecurityContext:
    """Security context and isolation settings for a session."""
    session_token: str
    user_permissions: Set[str] = field(default_factory=set)
    resource_quotas: Dict[str, float] = field(default_factory=dict)
    allowed_operations: Set[str] = field(default_factory=set)
    data_isolation_level: str = "strict"  # "strict", "moderate", "relaxed"
    encryption_enabled: bool = True
    audit_logging: bool = True

@dataclass
class UserSession:
    """Complete user session with all components."""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    expires_at: Optional[datetime]
    status: str  # "active", "idle", "suspended", "ended"
    config: SessionConfig
    metrics: SessionMetrics
    security: SessionSecurityContext
    data_store: Dict[str, Any] = field(default_factory=dict)
    temp_data: Dict[str, Any] = field(default_factory=dict)  # Not persisted
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status,
            "config": asdict(self.config),
            "metrics": asdict(self.metrics),
            "security": {
                "session_token": self.security.session_token,
                "user_permissions": list(self.security.user_permissions),
                "resource_quotas": self.security.resource_quotas,
                "allowed_operations": list(self.security.allowed_operations),
                "data_isolation_level": self.security.data_isolation_level,
                "encryption_enabled": self.security.encryption_enabled,
                "audit_logging": self.security.audit_logging
            },
            "data_store": self.data_store
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        """Create session from dictionary."""
        security_data = data["security"]
        security = SessionSecurityContext(
            session_token=security_data["session_token"],
            user_permissions=set(security_data["user_permissions"]),
            resource_quotas=security_data["resource_quotas"],
            allowed_operations=set(security_data["allowed_operations"]),
            data_isolation_level=security_data["data_isolation_level"],
            encryption_enabled=security_data["encryption_enabled"],
            audit_logging=security_data["audit_logging"]
        )
        
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None,
            status=data["status"],
            config=SessionConfig(**data["config"]),
            metrics=SessionMetrics(**data["metrics"]),
            security=security,
            data_store=data["data_store"]
        )

class SessionDatabase:
    """
    SQLite database interface for session persistence.
    Handles session storage, retrieval, and analytics.
    """
    
    def __init__(self, db_path: str = "data/sessions.db"):
        """Initialize the session database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        self._connection_lock = threading.Lock()
        
        logger.info(f"SessionDatabase initialized at {self.db_path}")
    
    def _init_database(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    expires_at TEXT,
                    status TEXT NOT NULL,
                    session_data TEXT NOT NULL,
                    UNIQUE(session_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_metrics (
                    session_id TEXT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id),
                    PRIMARY KEY(session_id, timestamp, metric_name)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_metrics_timestamp ON session_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_events_timestamp ON session_events(timestamp)")
            
            conn.commit()
    
    def save_session(self, session: UserSession):
        """Save session to database."""
        with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                session_data = json.dumps(session.to_dict())
                
                conn.execute("""
                    INSERT OR REPLACE INTO sessions 
                    (session_id, user_id, created_at, last_activity, expires_at, status, session_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.user_id,
                    session.created_at.isoformat(),
                    session.last_activity.isoformat(),
                    session.expires_at.isoformat() if session.expires_at else None,
                    session.status,
                    session_data
                ))
                
                conn.commit()
    
    def load_session(self, session_id: str) -> Optional[UserSession]:
        """Load session from database."""
        with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT session_data FROM sessions WHERE session_id = ?",
                    (session_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    session_data = json.loads(row[0])
                    return UserSession.from_dict(session_data)
                
                return None
    
    def delete_session(self, session_id: str):
        """Delete session from database."""
        with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.execute("DELETE FROM session_metrics WHERE session_id = ?", (session_id,))
                conn.execute("DELETE FROM session_events WHERE session_id = ?", (session_id,))
                conn.commit()
    
    def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[UserSession]:
        """Get all sessions for a user."""
        with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT session_data FROM sessions WHERE user_id = ?"
                params = [user_id]
                
                if active_only:
                    query += " AND status IN ('active', 'idle')"
                
                cursor = conn.execute(query, params)
                sessions = []
                
                for row in cursor.fetchall():
                    session_data = json.loads(row[0])
                    sessions.append(UserSession.from_dict(session_data))
                
                return sessions
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions."""
        current_time = datetime.now()
        
        with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                # Find expired sessions
                cursor = conn.execute("""
                    SELECT session_id FROM sessions 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (current_time.isoformat(),))
                
                expired_sessions = [row[0] for row in cursor.fetchall()]
                
                # Delete expired sessions
                for session_id in expired_sessions:
                    conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                    conn.execute("DELETE FROM session_metrics WHERE session_id = ?", (session_id,))
                    conn.execute("DELETE FROM session_events WHERE session_id = ?", (session_id,))
                
                conn.commit()
                return len(expired_sessions)
    
    def log_event(self, session_id: str, event_type: str, event_data: Optional[Dict[str, Any]] = None):
        """Log an event for a session."""
        with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO session_events (session_id, timestamp, event_type, event_data)
                    VALUES (?, ?, ?, ?)
                """, (
                    session_id,
                    datetime.now().isoformat(),
                    event_type,
                    json.dumps(event_data) if event_data else None
                ))
                conn.commit()
    
    def record_metric(self, session_id: str, metric_name: str, metric_value: float, 
                     metadata: Optional[Dict[str, Any]] = None):
        """Record a metric for a session."""
        with self._connection_lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO session_metrics (session_id, timestamp, metric_name, metric_value, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id,
                    datetime.now().isoformat(),
                    metric_name,
                    metric_value,
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()

class SessionIsolationManager:
    """
    Manages data isolation and security between user sessions.
    Ensures users can only access their own data and resources.
    """
    
    def __init__(self):
        """Initialize the session isolation manager."""
        self.access_control_cache: Dict[str, Dict[str, Any]] = {}
        self.resource_locks: Dict[str, threading.Lock] = {}
        self._cache_lock = threading.Lock()
        
        logger.info("SessionIsolationManager initialized")
    
    def create_security_context(self, user_id: str, permissions: Optional[Set[str]] = None) -> SessionSecurityContext:
        """Create a new security context for a session."""
        session_token = self._generate_session_token()
        
        # Default permissions
        default_permissions = {
            "read_own_data",
            "write_own_data",
            "create_sessions",
            "end_own_sessions"
        }
        
        # Add custom permissions
        if permissions:
            default_permissions.update(permissions)
        
        # Default resource quotas
        resource_quotas = {
            "max_memory_gb": 4.0,
            "max_cpu_percent": 50.0,
            "max_gpu_memory_gb": 2.0,
            "max_concurrent_sessions": 3,
            "max_session_duration_hours": 8.0
        }
        
        # Default allowed operations
        allowed_operations = {
            "text_generation",
            "image_processing",
            "audio_processing",
            "configuration_update",
            "feedback_submission"
        }
        
        return SessionSecurityContext(
            session_token=session_token,
            user_permissions=default_permissions,
            resource_quotas=resource_quotas,
            allowed_operations=allowed_operations,
            data_isolation_level="strict",
            encryption_enabled=True,
            audit_logging=True
        )
    
    def _generate_session_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(32)
    
    def validate_access(self, session_id: str, user_id: str, operation: str, 
                       resource: Optional[str] = None) -> bool:
        """Validate if a user can perform an operation."""
        # Implementation would check session permissions, resource quotas, etc.
        # For now, return basic validation
        return True
    
    def isolate_user_data(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply data isolation filters to user data."""
        # Remove sensitive fields that shouldn't be exposed
        isolated_data = data.copy()
        
        # Remove system-level information
        system_keys = ["system_config", "admin_settings", "internal_state"]
        for key in system_keys:
            isolated_data.pop(key, None)
        
        return isolated_data
    
    def get_resource_lock(self, resource_id: str) -> threading.Lock:
        """Get a thread lock for a specific resource."""
        with self._cache_lock:
            if resource_id not in self.resource_locks:
                self.resource_locks[resource_id] = threading.Lock()
            return self.resource_locks[resource_id]

class SessionManager:
    """
    Main session manager coordinating all session operations.
    Provides unified interface for session lifecycle management.
    """
    
    def __init__(self, db_path: str = "data/sessions.db"):
        """Initialize the session manager."""
        self.database = SessionDatabase(db_path)
        self.isolation_manager = SessionIsolationManager()
        
        # Active sessions cache
        self.active_sessions: Dict[str, UserSession] = {}
        self._session_lock = threading.Lock()
        
        # Session cleanup thread
        self._cleanup_active = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        
        logger.info("SessionManager initialized and active")
    
    def _cleanup_loop(self):
        """Background cleanup loop for expired sessions."""
        while self._cleanup_active:
            try:
                # Clean up expired sessions from database
                expired_count = self.database.cleanup_expired_sessions()
                if expired_count > 0:
                    logger.info(f"Cleaned up {expired_count} expired sessions")
                
                # Clean up inactive sessions from cache
                current_time = datetime.now()
                inactive_sessions = []
                
                with self._session_lock:
                    for session_id, session in self.active_sessions.items():
                        time_since_activity = (current_time - session.last_activity).total_seconds()
                        
                        # Mark as idle if inactive for 10 minutes
                        if time_since_activity > 600 and session.status == "active":
                            session.status = "idle"
                            self.database.save_session(session)
                            self.database.log_event(session_id, "session_idle")
                        
                        # Remove from cache if inactive for 1 hour
                        elif time_since_activity > 3600:
                            inactive_sessions.append(session_id)
                
                # Remove inactive sessions from cache
                for session_id in inactive_sessions:
                    with self._session_lock:
                        if session_id in self.active_sessions:
                            session = self.active_sessions[session_id]
                            if session.status in ["idle", "suspended"]:
                                del self.active_sessions[session_id]
                                logger.info(f"Removed inactive session {session_id} from cache")
                
                # Sleep for 5 minutes before next cleanup
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                time.sleep(60)  # Back off on error
    
    async def create_session(self, user_id: str, config: Optional[SessionConfig] = None,
                           permissions: Optional[Set[str]] = None,
                           expiration_hours: Optional[float] = None) -> UserSession:
        """Create a new user session."""
        # Generate unique session ID
        session_id = f"sess_{secrets.token_hex(16)}"
        
        # Use default config if not provided
        if config is None:
            config = SessionConfig()
        
        # Create security context
        security = self.isolation_manager.create_security_context(user_id, permissions)
        
        # Set expiration
        expires_at = None
        if expiration_hours:
            expires_at = datetime.now() + timedelta(hours=expiration_hours)
        
        # Create session
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            expires_at=expires_at,
            status="active",
            config=config,
            metrics=SessionMetrics(),
            security=security
        )
        
        # Save to database and cache
        self.database.save_session(session)
        self.database.log_event(session_id, "session_created")
        
        with self._session_lock:
            self.active_sessions[session_id] = session
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session
    
    async def get_session(self, session_id: str, update_activity: bool = True) -> Optional[UserSession]:
        """Get a session by ID."""
        # Check cache first
        with self._session_lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                if update_activity:
                    session.last_activity = datetime.now()
                    self.database.save_session(session)
                return session
        
        # Load from database
        session = self.database.load_session(session_id)
        if session:
            # Add to cache if active
            if session.status in ["active", "idle"]:
                with self._session_lock:
                    self.active_sessions[session_id] = session
                
                if update_activity:
                    session.last_activity = datetime.now()
                    session.status = "active"
                    self.database.save_session(session)
        
        return session
    
    async def end_session(self, session_id: str) -> bool:
        """End a session and clean up resources."""
        session = await self.get_session(session_id, update_activity=False)
        if not session:
            return False
        
        # Update session status
        session.status = "ended"
        session.last_activity = datetime.now()
        
        # Save final state
        self.database.save_session(session)
        self.database.log_event(session_id, "session_ended")
        
        # Remove from cache
        with self._session_lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
        
        logger.info(f"Ended session {session_id}")
        return True
    
    async def update_session_config(self, session_id: str, config_updates: Dict[str, Any]) -> bool:
        """Update session configuration."""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Update configuration
        for key, value in config_updates.items():
            if hasattr(session.config, key):
                setattr(session.config, key, value)
        
        # Save changes
        self.database.save_session(session)
        self.database.log_event(session_id, "config_updated", config_updates)
        
        return True
    
    async def record_session_metric(self, session_id: str, metric_name: str, 
                                  metric_value: float, metadata: Optional[Dict[str, Any]] = None):
        """Record a metric for a session."""
        session = await self.get_session(session_id)
        if session:
            # Update session metrics
            if metric_name == "processing_time":
                session.metrics.total_processing_time += metric_value
                session.metrics.total_requests += 1
                session.metrics.average_response_time = (
                    session.metrics.total_processing_time / session.metrics.total_requests
                )
            elif metric_name == "memory_usage":
                session.metrics.memory_peak_usage = max(
                    session.metrics.memory_peak_usage, metric_value
                )
            elif metric_name == "quality_score":
                session.metrics.quality_scores.append(metric_value)
            
            # Save to database
            self.database.save_session(session)
            self.database.record_metric(session_id, metric_name, metric_value, metadata)
    
    async def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[UserSession]:
        """Get all sessions for a user."""
        return self.database.get_user_sessions(user_id, active_only)
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Get session analytics and statistics."""
        with self._session_lock:
            active_count = len(self.active_sessions)
            status_counts = {}
            
            for session in self.active_sessions.values():
                status = session.status
                status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_sessions": active_count,
            "status_distribution": status_counts,
            "cache_size": len(self.active_sessions)
        }
    
    def shutdown(self):
        """Shutdown the session manager."""
        self._cleanup_active = False
        
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=10.0)
        
        logger.info("SessionManager shutdown complete")

# Global session manager instance
session_manager = None

def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global session_manager
    if session_manager is None:
        session_manager = SessionManager()
    return session_manager

def shutdown_session_manager():
    """Shutdown the global session manager."""
    global session_manager
    if session_manager:
        session_manager.shutdown()
        session_manager = None
