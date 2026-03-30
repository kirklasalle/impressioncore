"""
ImpressionCore Security Module
Security Infrastructure Foundation for Phase 8A

This module provides comprehensive security infrastructure including:
- Biometric authentication (voice, fingerprint)
- Multi-factor authentication 
- Digital identity management
- Data encryption and privacy controls
- Security monitoring and anomaly detection

Author: ImpressionCore Development Team
Created: 2025-05-31
Hardware Target: GTX 1050 Ti (4GB VRAM)
Phase: Phase 8A - Security Infrastructure Foundation
"""

from .authentication import *
from .encryption import *
from .identity import *
from .privacy import *
from .monitoring import *

__version__ = "8.0.0-alpha"
__author__ = "ImpressionCore Development Team"
__phase__ = "Phase 8A - Security Infrastructure Foundation"

# Security module configuration
SECURITY_CONFIG = {
    "memory_limit_mb": 1024,  # 1GB memory limit for security operations on GTX 1050 Ti
    "encryption_level": "AES-256",
    "authentication_timeout": 300,  # 5 minutes
    "session_duration": 3600,  # 1 hour
    "audit_logging": True,
    "real_time_monitoring": True
}

# Initialize security logging
import logging
security_logger = logging.getLogger(__name__)
security_logger.info(f"ImpressionCore Security Module {__version__} initialized")
security_logger.info(f"Current Phase: {__phase__}")
