"""
Authentication Base Classes for ImpressionCore Security Infrastructure
Phase 8A: Security Infrastructure Foundation

This module provides the foundational classes and interfaces for all authentication
mechanisms in ImpressionCore, including biometric, MFA, and session management.

Author: ImpressionCore Development Team
Created: 2025-05-31
Hardware Target: GTX 1050 Ti (4GB VRAM)
Memory Target: <100MB for base authentication operations
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import logging
import asyncio
import hashlib
import secrets
import json

# Initialize authentication logger
auth_logger = logging.getLogger(__name__)

class AuthenticationStatus(Enum):
    """Authentication status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    EXPIRED = "expired"
    LOCKED = "locked"
    REQUIRES_MFA = "requires_mfa"
    INVALID_CREDENTIALS = "invalid_credentials"
    BIOMETRIC_FAILED = "biometric_failed"
    SESSION_EXPIRED = "session_expired"

class AuthenticationType(Enum):
    """Authentication type enumeration"""
    BIOMETRIC = "biometric"
    VOICE = "voice"
    FINGERPRINT = "fingerprint"
    FACIAL = "facial"
    MFA = "mfa"
    SESSION = "session"
    PASSWORD = "password"
    TOKEN = "token"

@dataclass
class AuthenticationResult:
    """
    Standardized authentication result containing status, metadata, and security info
    
    Attributes:
        status: Authentication status from AuthenticationStatus enum
        user_id: Unique identifier for authenticated user
        session_id: Session identifier if authentication successful
        authentication_type: Type of authentication used
        timestamp: When authentication occurred
        confidence_score: Confidence level (0.0-1.0) for biometric auth
        metadata: Additional authentication metadata
        error_message: Error details if authentication failed
        requires_additional_auth: Whether additional authentication steps needed
        expiry_time: When this authentication result expires
    """
    status: AuthenticationStatus
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    authentication_type: Optional[AuthenticationType] = None
    timestamp: Optional[datetime] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    requires_additional_auth: bool = False
    expiry_time: Optional[datetime] = None
    
    def __post_init__(self):
        """Set default timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
            
    def is_valid(self) -> bool:
        """Check if authentication result is still valid"""
        if self.status != AuthenticationStatus.SUCCESS:
            return False
        if self.expiry_time and datetime.utcnow() > self.expiry_time:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization"""
        return {
            "status": self.status.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "authentication_type": self.authentication_type.value if self.authentication_type else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "confidence_score": self.confidence_score,
            "metadata": self.metadata or {},
            "error_message": self.error_message,
            "requires_additional_auth": self.requires_additional_auth,
            "expiry_time": self.expiry_time.isoformat() if self.expiry_time else None
        }

class AuthenticationError(Exception):
    """
    Custom exception for authentication errors
    
    Attributes:
        message: Error message
        error_code: Standardized error code
        auth_type: Authentication type that failed
        user_id: User ID if available
        retry_allowed: Whether retry is allowed
        lockout_duration: Duration of lockout if applicable
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None,
        auth_type: AuthenticationType = None,
        user_id: str = None,
        retry_allowed: bool = True,
        lockout_duration: timedelta = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.auth_type = auth_type
        self.user_id = user_id
        self.retry_allowed = retry_allowed
        self.lockout_duration = lockout_duration
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/reporting"""
        return {
            "message": self.message,
            "error_code": self.error_code,
            "auth_type": self.auth_type.value if self.auth_type else None,
            "user_id": self.user_id,
            "retry_allowed": self.retry_allowed,
            "lockout_duration": str(self.lockout_duration) if self.lockout_duration else None,
            "timestamp": datetime.utcnow().isoformat()
        }

class AuthenticationBase(ABC):
    """
    Abstract base class for all authentication mechanisms in ImpressionCore
    
    This class defines the standard interface that all authentication providers
    must implement, ensuring consistency across biometric, MFA, and other auth types.
    
    Hardware Optimization: Designed for GTX 1050 Ti constraints
    Memory Target: <50MB per authentication instance
    """
    
    def __init__(
        self, 
        config: Dict[str, Any] = None,
        memory_limit_mb: int = 50,
        enable_logging: bool = True
    ):
        """
        Initialize authentication base
        
        Args:
            config: Authentication configuration dictionary
            memory_limit_mb: Memory limit in MB for this authenticator
            enable_logging: Whether to enable detailed logging
        """
        self.config = config or {}
        self.memory_limit_mb = memory_limit_mb
        self.enable_logging = enable_logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Authentication state tracking
        self._authentication_attempts: Dict[str, int] = {}
        self._lockout_times: Dict[str, datetime] = {}
        self._active_sessions: Dict[str, datetime] = {}
        
        # Performance metrics
        self._auth_count = 0
        self._success_count = 0
        self._failure_count = 0
        self._total_auth_time = 0.0
        
        if self.enable_logging:
            self.logger.info(f"Initialized {self.__class__.__name__} with {memory_limit_mb}MB memory limit")
    
    @property
    def authentication_type(self) -> AuthenticationType:
        """Return the authentication type for this provider"""
        return AuthenticationType.TOKEN  # Default, should be overridden
    
    @property
    def is_hardware_optimized(self) -> bool:
        """Check if authenticator is optimized for GTX 1050 Ti"""
        return self.memory_limit_mb <= 100
    
    @property
    def success_rate(self) -> float:
        """Calculate authentication success rate"""
        if self._auth_count == 0:
            return 0.0
        return self._success_count / self._auth_count
    
    @property
    def average_auth_time(self) -> float:
        """Calculate average authentication time in seconds"""
        if self._auth_count == 0:
            return 0.0
        return self._total_auth_time / self._auth_count
    
    def is_user_locked_out(self, user_id: str) -> bool:
        """
        Check if user is currently locked out
        
        Args:
            user_id: User identifier to check
            
        Returns:
            True if user is locked out, False otherwise
        """
        if user_id not in self._lockout_times:
            return False
            
        lockout_time = self._lockout_times[user_id]
        lockout_duration = timedelta(minutes=self.config.get('lockout_duration_minutes', 15))
        
        if datetime.utcnow() > lockout_time + lockout_duration:
            # Lockout expired, remove from tracking
            del self._lockout_times[user_id]
            if user_id in self._authentication_attempts:
                del self._authentication_attempts[user_id]
            return False
            
        return True
    
    def increment_auth_attempts(self, user_id: str) -> int:
        """
        Increment authentication attempts for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Current number of attempts
        """
        current_attempts = self._authentication_attempts.get(user_id, 0) + 1
        self._authentication_attempts[user_id] = current_attempts
        
        max_attempts = self.config.get('max_authentication_attempts', 3)
        if current_attempts >= max_attempts:
            self._lockout_times[user_id] = datetime.utcnow()
            if self.enable_logging:
                self.logger.warning(f"User {user_id} locked out after {current_attempts} failed attempts")
        
        return current_attempts
    
    def reset_auth_attempts(self, user_id: str):
        """Reset authentication attempts for successful auth"""
        if user_id in self._authentication_attempts:
            del self._authentication_attempts[user_id]
        if user_id in self._lockout_times:
            del self._lockout_times[user_id]
    
    def generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
    
    def hash_credential(self, credential: str, salt: str = None) -> tuple[str, str]:
        """
        Securely hash credentials using SHA-256 with salt
        
        Args:
            credential: Credential to hash
            salt: Optional salt, generates if not provided
            
        Returns:
            Tuple of (hashed_credential, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        combined = f"{credential}{salt}".encode('utf-8')
        hashed = hashlib.sha256(combined).hexdigest()
        
        return hashed, salt
    
    def verify_credential_hash(self, credential: str, hashed_credential: str, salt: str) -> bool:
        """
        Verify credential against stored hash
        
        Args:
            credential: Plain credential to verify
            hashed_credential: Stored hash
            salt: Salt used for hashing
            
        Returns:
            True if credential matches hash, False otherwise
        """
        test_hash, _ = self.hash_credential(credential, salt)
        return test_hash == hashed_credential
    
    @abstractmethod
    async def authenticate(
        self, 
        user_id: str, 
        credentials: Dict[str, Any],
        **kwargs
    ) -> AuthenticationResult:
        """
        Perform authentication for given user and credentials
        
        Args:
            user_id: Unique user identifier
            credentials: Authentication credentials (format varies by auth type)
            **kwargs: Additional authentication parameters
            
        Returns:
            AuthenticationResult with status and metadata
            
        Raises:
            AuthenticationError: If authentication fails with specific error
        """
        pass
    
    @abstractmethod
    async def validate_session(self, session_id: str) -> AuthenticationResult:
        """
        Validate existing authentication session
        
        Args:
            session_id: Session identifier to validate
            
        Returns:
            AuthenticationResult indicating session validity
        """
        pass
    
    @abstractmethod
    async def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate authentication session
        
        Args:
            session_id: Session identifier to invalidate
            
        Returns:
            True if session was invalidated, False if session not found
        """
        pass
    
    async def cleanup_expired_sessions(self):
        """Clean up expired authentication sessions"""
        current_time = datetime.utcnow()
        session_timeout = timedelta(minutes=self.config.get('session_timeout_minutes', 60))
        
        expired_sessions = []
        for session_id, created_time in self._active_sessions.items():
            if current_time > created_time + session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.invalidate_session(session_id)
            
        if expired_sessions and self.enable_logging:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get authentication performance metrics
        
        Returns:
            Dictionary containing performance statistics
        """
        return {
            "total_authentications": self._auth_count,
            "successful_authentications": self._success_count,
            "failed_authentications": self._failure_count,
            "success_rate": self.success_rate,
            "average_auth_time_seconds": self.average_auth_time,
            "active_sessions": len(self._active_sessions),
            "locked_out_users": len(self._lockout_times),
            "memory_limit_mb": self.memory_limit_mb,
            "hardware_optimized": self.is_hardware_optimized
        }
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get current security status and alerts
        
        Returns:
            Dictionary containing security status information
        """
        current_time = datetime.utcnow()
        
        # Check for security concerns
        high_failure_rate = self.success_rate < 0.5 if self._auth_count > 10 else False
        many_lockouts = len(self._lockout_times) > 5
        
        return {
            "authentication_type": self.authentication_type.value,
            "status": "healthy" if not (high_failure_rate or many_lockouts) else "warning",
            "high_failure_rate": high_failure_rate,
            "excessive_lockouts": many_lockouts,
            "active_lockouts": len(self._lockout_times),
            "success_rate": self.success_rate,
            "last_auth_time": current_time.isoformat(),
            "hardware_optimization": self.is_hardware_optimized
        }

class BiometricAuthenticationBase(AuthenticationBase):
    """
    Specialized base class for biometric authentication methods
    
    Provides common functionality for voice, fingerprint, facial recognition
    and other biometric authentication mechanisms.
    
    Hardware Optimization: Optimized for GTX 1050 Ti processing constraints
    Memory Target: <100MB for biometric processing
    """
    
    def __init__(
        self,
        config: Dict[str, Any] = None,
        memory_limit_mb: int = 100,
        confidence_threshold: float = 0.85,
        enable_logging: bool = True
    ):
        """
        Initialize biometric authentication base
        
        Args:
            config: Biometric configuration dictionary
            memory_limit_mb: Memory limit for biometric processing
            confidence_threshold: Minimum confidence for successful auth
            enable_logging: Whether to enable detailed logging
        """
        super().__init__(config, memory_limit_mb, enable_logging)
        
        self.confidence_threshold = confidence_threshold
        self._biometric_templates: Dict[str, Any] = {}
        self._processing_times: List[float] = []
        
        if self.enable_logging:
            self.logger.info(f"Initialized biometric authenticator with {confidence_threshold} confidence threshold")
    
    @property
    def authentication_type(self) -> AuthenticationType:
        """Return biometric authentication type"""
        return AuthenticationType.BIOMETRIC
    
    @property
    def average_processing_time(self) -> float:
        """Calculate average biometric processing time"""
        if not self._processing_times:
            return 0.0
        return sum(self._processing_times) / len(self._processing_times)
    
    def store_biometric_template(self, user_id: str, template: Any, template_type: str):
        """
        Store biometric template for user
        
        Args:
            user_id: User identifier
            template: Biometric template data
            template_type: Type of biometric template
        """
        template_key = f"{user_id}_{template_type}"
        self._biometric_templates[template_key] = {
            "template": template,
            "type": template_type,
            "created": datetime.utcnow(),
            "user_id": user_id
        }
        
        if self.enable_logging:
            self.logger.info(f"Stored {template_type} template for user {user_id}")
    
    def get_biometric_template(self, user_id: str, template_type: str) -> Optional[Any]:
        """
        Retrieve biometric template for user
        
        Args:
            user_id: User identifier
            template_type: Type of biometric template
            
        Returns:
            Biometric template if found, None otherwise
        """
        template_key = f"{user_id}_{template_type}"
        template_data = self._biometric_templates.get(template_key)
        
        if template_data:
            return template_data["template"]
        return None
    
    @abstractmethod
    async def process_biometric_data(
        self, 
        biometric_data: Any,
        user_id: str = None
    ) -> tuple[Any, float]:
        """
        Process raw biometric data into template and confidence score
        
        Args:
            biometric_data: Raw biometric input data
            user_id: Optional user ID for context
            
        Returns:
            Tuple of (processed_template, confidence_score)
        """
        pass
    
    @abstractmethod
    async def compare_biometric_templates(
        self, 
        template1: Any, 
        template2: Any
    ) -> float:
        """
        Compare two biometric templates and return similarity score
        
        Args:
            template1: First biometric template
            template2: Second biometric template
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        pass
    
    async def authenticate_biometric(
        self,
        user_id: str,
        biometric_data: Any,
        template_type: str
    ) -> AuthenticationResult:
        """
        Perform biometric authentication
        
        Args:
            user_id: User identifier
            biometric_data: Raw biometric data for authentication
            template_type: Type of biometric authentication
            
        Returns:
            AuthenticationResult with biometric-specific metadata
        """
        start_time = datetime.utcnow()
        
        try:
            # Check if user is locked out
            if self.is_user_locked_out(user_id):
                return AuthenticationResult(
                    status=AuthenticationStatus.LOCKED,
                    user_id=user_id,
                    authentication_type=self.authentication_type,
                    error_message="User account is temporarily locked"
                )
            
            # Get stored template
            stored_template = self.get_biometric_template(user_id, template_type)
            if stored_template is None:
                self.increment_auth_attempts(user_id)
                return AuthenticationResult(
                    status=AuthenticationStatus.FAILED,
                    user_id=user_id,
                    authentication_type=self.authentication_type,
                    error_message="No biometric template found for user"
                )
            
            # Process input biometric data
            processed_template, processing_confidence = await self.process_biometric_data(
                biometric_data, user_id
            )
            
            # Compare with stored template
            similarity_score = await self.compare_biometric_templates(
                stored_template, processed_template
            )
            
            # Calculate final confidence (combine processing and similarity)
            final_confidence = (processing_confidence + similarity_score) / 2.0
            
            # Record processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._processing_times.append(processing_time)
            
            # Keep only last 100 processing times for memory efficiency
            if len(self._processing_times) > 100:
                self._processing_times = self._processing_times[-100:]
            
            # Update authentication metrics
            self._auth_count += 1
            self._total_auth_time += processing_time
            
            # Check if authentication successful
            if final_confidence >= self.confidence_threshold:
                self._success_count += 1
                self.reset_auth_attempts(user_id)
                
                session_id = self.generate_session_id()
                self._active_sessions[session_id] = datetime.utcnow()
                
                return AuthenticationResult(
                    status=AuthenticationStatus.SUCCESS,
                    user_id=user_id,
                    session_id=session_id,
                    authentication_type=self.authentication_type,
                    confidence_score=final_confidence,
                    expiry_time=datetime.utcnow() + timedelta(
                        minutes=self.config.get('session_timeout_minutes', 60)
                    ),
                    metadata={
                        "template_type": template_type,
                        "processing_time_seconds": processing_time,
                        "similarity_score": similarity_score,
                        "processing_confidence": processing_confidence
                    }
                )
            else:
                self._failure_count += 1
                self.increment_auth_attempts(user_id)
                
                return AuthenticationResult(
                    status=AuthenticationStatus.BIOMETRIC_FAILED,
                    user_id=user_id,
                    authentication_type=self.authentication_type,
                    confidence_score=final_confidence,
                    error_message=f"Biometric confidence {final_confidence:.2f} below threshold {self.confidence_threshold}",
                    metadata={
                        "template_type": template_type,
                        "processing_time_seconds": processing_time,
                        "threshold": self.confidence_threshold
                    }
                )
                
        except Exception as e:
            self._failure_count += 1
            self.increment_auth_attempts(user_id)
            
            if self.enable_logging:
                self.logger.error(f"Biometric authentication error for user {user_id}: {str(e)}")
            
            return AuthenticationResult(
                status=AuthenticationStatus.FAILED,
                user_id=user_id,
                authentication_type=self.authentication_type,
                error_message=f"Biometric authentication error: {str(e)}"
            )
