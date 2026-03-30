"""
Session Manager for ImpressionCore Security Infrastructure

This module implements secure session management with adaptive security policies,
device tracking, and memory-optimized operations for GTX 1050 Ti hardware constraints.

Created: 2025-01-01
Author: ImpressionCore Security Team
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Limit: <50MB for session management
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Tuple
import secrets
import threading
from concurrent.futures import ThreadPoolExecutor

# Import security components
from .auth_base import AuthenticationResult, AuthenticationError

# Configure logging for session management
logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Session status states"""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    LOCKED = "locked"


class SessionType(Enum):
    """Session type classifications"""
    AUTHENTICATION = "authentication"
    APPLICATION = "application"
    API = "api"
    ADMIN = "admin"
    TEMPORARY = "temporary"


@dataclass
class SessionSecurityPolicy:
    """Security policy configuration for sessions"""
    max_idle_time: int = 1800  # 30 minutes
    max_session_duration: int = 28800  # 8 hours
    require_periodic_auth: bool = True
    periodic_auth_interval: int = 3600  # 1 hour
    max_concurrent_sessions: int = 5
    device_binding: bool = True
    ip_validation: bool = True
    session_rotation: bool = True
    rotation_interval: int = 7200  # 2 hours
    inactivity_warning: int = 300  # 5 minutes before expiry
    
    # Memory optimization
    cleanup_interval: int = 300  # 5 minutes
    max_sessions_per_user: int = 10
    session_cache_size: int = 1000


@dataclass
class DeviceInfo:
    """Device information for session binding"""
    fingerprint: str
    user_agent: str
    ip_address: str
    platform: str
    browser: str
    screen_resolution: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class SessionMetrics:
    """Session performance and security metrics"""
    created_at: datetime
    last_activity: datetime
    auth_attempts: int = 0
    failed_auth_attempts: int = 0
    data_transferred: int = 0  # bytes
    requests_count: int = 0
    security_events: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class Session:
    """Secure session with comprehensive tracking and validation"""
    session_id: str
    user_id: str
    session_type: SessionType
    status: SessionStatus
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    device_info: DeviceInfo
    metrics: SessionMetrics
    
    # Security attributes
    authentication_level: int = 1  # MFA level completed
    permissions: Set[str] = field(default_factory=set)
    security_context: Dict[str, Any] = field(default_factory=dict)
    
    # Session data (encrypted in production)
    session_data: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking
    parent_session_id: Optional[str] = None
    child_sessions: Set[str] = field(default_factory=set)
    
    def is_valid(self) -> bool:
        """Check if session is valid and active"""
        now = datetime.now()
        return (
            self.status == SessionStatus.ACTIVE and
            now < self.expires_at and
            (now - self.last_activity).total_seconds() < 1800  # 30 min idle
        )
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        self.metrics.requests_count += 1
    
    def add_security_event(self, event: str):
        """Add security event to session tracking"""
        self.metrics.security_events.append(f"{datetime.now().isoformat()}: {event}")
        
        # Limit security events for memory optimization
        if len(self.metrics.security_events) > 50:
            self.metrics.security_events = self.metrics.security_events[-25:]


class SessionManager:
    """
    Secure Session Manager
    
    Manages user sessions with adaptive security policies, device tracking,
    and memory-optimized operations for GTX 1050 Ti hardware constraints.
    """
    
    def __init__(self, policy: Optional[SessionSecurityPolicy] = None):
        """Initialize session manager with security policies"""
        self.policy = policy or SessionSecurityPolicy()
        self.sessions: Dict[str, Session] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self.device_sessions: Dict[str, Set[str]] = {}  # device_fingerprint -> session_ids
        
        # Session cleanup and monitoring
        self._cleanup_lock = threading.Lock()
        self._cleanup_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="session_cleanup")
        self._last_cleanup = datetime.now()
        
        # Performance tracking
        self.session_stats = {
            'total_sessions_created': 0,
            'active_sessions': 0,
            'expired_sessions': 0,
            'terminated_sessions': 0,
            'security_violations': 0,
            'average_session_duration': 0.0,
            'memory_usage_mb': 0
        }
        
        # Security monitoring
        self.security_events: List[Dict[str, Any]] = []
        self.suspicious_activities: Dict[str, List[Dict[str, Any]]] = {}
        
        logger.info("Session Manager initialized with adaptive security policies")
    
    async def create_session(
        self,
        user_id: str,
        device_info: DeviceInfo,
        session_type: SessionType = SessionType.APPLICATION,
        authentication_level: int = 1,
        permissions: Optional[Set[str]] = None,
        parent_session_id: Optional[str] = None
    ) -> Session:
        """Create new secure session with device binding and validation"""
        try:
            # Validate concurrent session limits
            await self._validate_session_limits(user_id, device_info)
            
            # Generate cryptographically secure session ID
            session_id = secrets.token_urlsafe(32)
            
            # Calculate session expiry
            now = datetime.now()
            max_duration = timedelta(seconds=self.policy.max_session_duration)
            expires_at = now + max_duration
            
            # Create session metrics
            metrics = SessionMetrics(
                created_at=now,
                last_activity=now
            )
            
            # Create session
            session = Session(
                session_id=session_id,
                user_id=user_id,
                session_type=session_type,
                status=SessionStatus.ACTIVE,
                created_at=now,
                expires_at=expires_at,
                last_activity=now,
                device_info=device_info,
                metrics=metrics,
                authentication_level=authentication_level,
                permissions=permissions or set(),
                parent_session_id=parent_session_id
            )
            
            # Store session
            self.sessions[session_id] = session
            
            # Update user session tracking
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)
            
            # Update device session tracking
            device_fingerprint = device_info.fingerprint
            if device_fingerprint not in self.device_sessions:
                self.device_sessions[device_fingerprint] = set()
            self.device_sessions[device_fingerprint].add(session_id)
            
            # Link to parent session if specified
            if parent_session_id and parent_session_id in self.sessions:
                self.sessions[parent_session_id].child_sessions.add(session_id)
            
            # Update statistics
            self.session_stats['total_sessions_created'] += 1
            self.session_stats['active_sessions'] = len([
                s for s in self.sessions.values() if s.status == SessionStatus.ACTIVE
            ])
            
            # Schedule cleanup if needed
            await self._schedule_cleanup()
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise AuthenticationError(f"Failed to create session: {e}")
    
    async def validate_session(self, session_id: str) -> Optional[Session]:
        """Validate and refresh session if valid"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return None
            
            now = datetime.now()
            
            # Check basic validity
            if not session.is_valid():
                await self._expire_session(session_id, "Session validation failed")
                return None
            
            # Check for required periodic authentication
            if self.policy.require_periodic_auth:
                time_since_auth = (now - session.created_at).total_seconds()
                if time_since_auth > self.policy.periodic_auth_interval:
                    session.add_security_event("Periodic authentication required")
                    session.status = SessionStatus.SUSPENDED
                    return session
            
            # Check for session rotation requirement
            if self.policy.session_rotation:
                time_since_creation = (now - session.created_at).total_seconds()
                if time_since_creation > self.policy.rotation_interval:
                    return await self._rotate_session(session)
            
            # Update activity
            session.update_activity()
            
            return session
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return None
    
    async def terminate_session(self, session_id: str, reason: str = "User logout") -> bool:
        """Terminate session and cleanup resources"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            # Terminate child sessions first
            for child_session_id in session.child_sessions.copy():
                await self.terminate_session(child_session_id, "Parent session terminated")
            
            # Update session status
            session.status = SessionStatus.TERMINATED
            session.add_security_event(f"Session terminated: {reason}")
            
            # Remove from tracking structures
            self._remove_session_tracking(session_id, session)
            
            # Update statistics
            self.session_stats['terminated_sessions'] += 1
            self.session_stats['active_sessions'] = len([
                s for s in self.sessions.values() if s.status == SessionStatus.ACTIVE
            ])
            
            # Remove from memory after short delay (for audit purposes)
            await asyncio.sleep(1)
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            logger.info(f"Terminated session {session_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate session: {e}")
            return False
    
    async def terminate_user_sessions(
        self,
        user_id: str,
        exclude_session_id: Optional[str] = None,
        reason: str = "Bulk termination"
    ) -> int:
        """Terminate all sessions for a user"""
        try:
            user_session_ids = self.user_sessions.get(user_id, set()).copy()
            
            if exclude_session_id:
                user_session_ids.discard(exclude_session_id)
            
            terminated_count = 0
            for session_id in user_session_ids:
                if await self.terminate_session(session_id, reason):
                    terminated_count += 1
            
            logger.info(f"Terminated {terminated_count} sessions for user {user_id}")
            return terminated_count
            
        except Exception as e:
            logger.error(f"Failed to terminate user sessions: {e}")
            return 0
    
    async def update_session_permissions(
        self,
        session_id: str,
        permissions: Set[str],
        require_auth: bool = True
    ) -> bool:
        """Update session permissions with optional re-authentication"""
        try:
            session = self.sessions.get(session_id)
            if not session or not session.is_valid():
                return False
            
            if require_auth and session.status == SessionStatus.SUSPENDED:
                session.add_security_event("Permission update blocked: suspended session")
                return False
            
            # Log permission changes for security audit
            old_permissions = session.permissions.copy()
            session.permissions = permissions
            
            session.add_security_event(
                f"Permissions updated: {old_permissions} -> {permissions}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session permissions: {e}")
            return False
    
    async def get_session_data(self, session_id: str, key: str) -> Any:
        """Get session data with validation"""
        try:
            session = self.sessions.get(session_id)
            if not session or not session.is_valid():
                return None
            
            session.update_activity()
            return session.session_data.get(key)
            
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            return None
    
    async def set_session_data(self, session_id: str, key: str, value: Any) -> bool:
        """Set session data with validation"""
        try:
            session = self.sessions.get(session_id)
            if not session or not session.is_valid():
                return False
            
            session.session_data[key] = value
            session.update_activity()
            
            # Track data size for memory optimization
            session.metrics.data_transferred += len(str(value))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set session data: {e}")
            return False
    
    async def check_device_session_limit(self, device_fingerprint: str) -> bool:
        """Check if device has reached session limit"""
        try:
            device_sessions = self.device_sessions.get(device_fingerprint, set())
            active_sessions = 0
            
            for session_id in device_sessions:
                session = self.sessions.get(session_id)
                if session and session.is_valid():
                    active_sessions += 1
            
            return active_sessions < self.policy.max_concurrent_sessions
            
        except Exception as e:
            logger.error(f"Failed to check device session limit: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[Session]:
        """Get all active sessions for user"""
        try:
            user_session_ids = self.user_sessions.get(user_id, set())
            active_sessions = []
            
            for session_id in user_session_ids:
                session = self.sessions.get(session_id)
                if session and session.status == SessionStatus.ACTIVE:
                    active_sessions.append(session)
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    async def detect_session_anomalies(self, session_id: str) -> List[str]:
        """Detect potential security anomalies in session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return []
            
            anomalies = []
            
            # Check for rapid session creation
            user_sessions = await self.get_user_sessions(session.user_id)
            recent_sessions = [
                s for s in user_sessions
                if (datetime.now() - s.created_at).total_seconds() < 300  # 5 minutes
            ]
            
            if len(recent_sessions) > 3:
                anomalies.append("Rapid session creation detected")
            
            # Check for unusual activity patterns
            if session.metrics.requests_count > 1000:  # High request volume
                anomalies.append("High request volume detected")
            
            # Check for failed authentication attempts
            if session.metrics.failed_auth_attempts > 5:
                anomalies.append("Multiple authentication failures")
            
            # Check for device fingerprint changes
            device_sessions = self.device_sessions.get(session.device_info.fingerprint, set())
            if len(device_sessions) > self.policy.max_concurrent_sessions:
                anomalies.append("Device session limit exceeded")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect session anomalies: {e}")
            return []
    
    async def _validate_session_limits(self, user_id: str, device_info: DeviceInfo):
        """Validate session creation against security limits"""
        # Check user session limit
        user_session_count = len(self.user_sessions.get(user_id, set()))
        if user_session_count >= self.policy.max_sessions_per_user:
            # Terminate oldest session
            oldest_session = await self._get_oldest_user_session(user_id)
            if oldest_session:
                await self.terminate_session(oldest_session.session_id, "Session limit exceeded")
        
        # Check device session limit
        if not await self.check_device_session_limit(device_info.fingerprint):
            raise AuthenticationError("Device session limit exceeded")
    
    async def _get_oldest_user_session(self, user_id: str) -> Optional[Session]:
        """Get oldest session for user"""
        user_sessions = await self.get_user_sessions(user_id)
        if not user_sessions:
            return None
        
        return min(user_sessions, key=lambda s: s.created_at)
    
    async def _rotate_session(self, session: Session) -> Session:
        """Rotate session with new ID while preserving context"""
        try:
            # Create new session with same context
            new_session = await self.create_session(
                user_id=session.user_id,
                device_info=session.device_info,
                session_type=session.session_type,
                authentication_level=session.authentication_level,
                permissions=session.permissions.copy()
            )
            
            # Transfer session data
            new_session.session_data = session.session_data.copy()
            new_session.security_context = session.security_context.copy()
            
            # Terminate old session
            await self.terminate_session(session.session_id, "Session rotated")
            
            new_session.add_security_event("Session rotated for security")
            
            return new_session
            
        except Exception as e:
            logger.error(f"Failed to rotate session: {e}")
            return session
    
    async def _expire_session(self, session_id: str, reason: str):
        """Expire session with cleanup"""
        session = self.sessions.get(session_id)
        if session:
            session.status = SessionStatus.EXPIRED
            session.add_security_event(f"Session expired: {reason}")
            
            self.session_stats['expired_sessions'] += 1
            
            # Remove from tracking after delay
            await asyncio.sleep(60)  # Keep for 1 minute for audit
            self._remove_session_tracking(session_id, session)
    
    def _remove_session_tracking(self, session_id: str, session: Session):
        """Remove session from tracking structures"""
        # Remove from user sessions
        if session.user_id in self.user_sessions:
            self.user_sessions[session.user_id].discard(session_id)
            if not self.user_sessions[session.user_id]:
                del self.user_sessions[session.user_id]
        
        # Remove from device sessions
        device_fingerprint = session.device_info.fingerprint
        if device_fingerprint in self.device_sessions:
            self.device_sessions[device_fingerprint].discard(session_id)
            if not self.device_sessions[device_fingerprint]:
                del self.device_sessions[device_fingerprint]
    
    async def _schedule_cleanup(self):
        """Schedule session cleanup if needed"""
        now = datetime.now()
        time_since_cleanup = (now - self._last_cleanup).total_seconds()
        
        if time_since_cleanup > self.policy.cleanup_interval:
            self._cleanup_executor.submit(self._cleanup_sessions)
            self._last_cleanup = now
    
    def _cleanup_sessions(self):
        """Clean up expired and invalid sessions"""
        try:
            with self._cleanup_lock:
                now = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.sessions.items():
                    if (session.status != SessionStatus.ACTIVE or
                        now > session.expires_at or
                        (now - session.last_activity).total_seconds() > self.policy.max_idle_time):
                        expired_sessions.append(session_id)
                
                # Clean up expired sessions
                for session_id in expired_sessions:
                    asyncio.create_task(self._expire_session(session_id, "Cleanup"))
                
                # Update memory usage statistics
                import sys
                total_size = sum(sys.getsizeof(session) for session in self.sessions.values())
                self.session_stats['memory_usage_mb'] = total_size / (1024 * 1024)
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                    
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        return {
            **self.session_stats,
            'active_users': len(self.user_sessions),
            'active_devices': len(self.device_sessions),
            'total_sessions': len(self.sessions),
            'security_events_count': len(self.security_events),
            'suspicious_activities': len(self.suspicious_activities)
        }
