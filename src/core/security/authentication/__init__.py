"""
Authentication Module for ImpressionCore Security Infrastructure
Phase 8A: Security Infrastructure Foundation

This module provides comprehensive authentication capabilities including:
- Biometric authentication (voice recognition, fingerprint scanning)
- Multi-factor authentication (MFA) with TOTP support
- Session management and validation
- Authentication state tracking and security monitoring

Hardware Optimization: Designed for GTX 1050 Ti (4GB VRAM) constraints
Memory Target: <200MB for all authentication operations
"""

from .auth_base import (
    AuthenticationBase, 
    BiometricAuthenticationBase,
    AuthenticationResult, 
    AuthenticationError
)
from .biometric_auth import BiometricAuthenticator
from .voice_auth import VoiceAuthenticator  
from .fingerprint_auth import FingerprintAuthenticator
from .mfa_manager import (
    MFAManager,
    MFAConfiguration,
    MFASession,
    AuthenticationFactor,
    MFAPolicy,
    TOTPGenerator
)
from .session_manager import (
    SessionManager,
    Session,
    SessionStatus,
    SessionType,
    SessionSecurityPolicy,
    DeviceInfo
)
from .auth_validator import (
    AuthenticationValidator,
    ValidationPolicy,
    ValidationContext,
    ValidationResult,
    RiskAssessment,
    RiskLevel,
    PolicyViolation
)

__all__ = [
    # Base classes
    'AuthenticationBase',
    'BiometricAuthenticationBase',
    'AuthenticationResult', 
    'AuthenticationError',
    
    # Authenticators
    'BiometricAuthenticator',
    'VoiceAuthenticator',
    'FingerprintAuthenticator', 
    
    # MFA System
    'MFAManager',
    'MFAConfiguration',
    'MFASession',
    'AuthenticationFactor',
    'MFAPolicy',
    'TOTPGenerator',
    
    # Session Management
    'SessionManager',
    'Session',
    'SessionStatus',
    'SessionType',
    'SessionSecurityPolicy',
    'DeviceInfo',
    
    # Validation System
    'AuthenticationValidator',
    'ValidationPolicy',
    'ValidationContext',
    'ValidationResult',
    'RiskAssessment',
    'RiskLevel',
    'PolicyViolation'
]

# Authentication module configuration
AUTH_CONFIG = {
    "max_authentication_attempts": 5,
    "lockout_duration_minutes": 15,
    "session_timeout_minutes": 60,
    "biometric_confidence_threshold": 0.85,
    "voice_sample_duration_seconds": 3,
    "fingerprint_match_threshold": 0.90,
    "mfa_backup_codes_count": 10,
    "memory_optimization": True,
    "hardware_target": "GTX_1050_Ti",
    "max_memory_usage_mb": 200,
    "adaptive_authentication": True,
    "risk_assessment_enabled": True
}

import logging
auth_logger = logging.getLogger(__name__)
auth_logger.info("ImpressionCore Authentication Module initialized for Phase 8A")
auth_logger.info(f"Hardware Target: {AUTH_CONFIG['hardware_target']}")
auth_logger.info(f"Memory Optimization: {AUTH_CONFIG['memory_optimization']}")
auth_logger.info(f"Max Memory Usage: {AUTH_CONFIG['max_memory_usage_mb']}MB")
auth_logger.info("Complete MFA and session management system available")
