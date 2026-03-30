# Phase 8A Week 2: Privacy Controls System
# File: src/security/privacy/__init__.py
# Description: Privacy controls module initialization and configuration
# Created: 2025-01-18 21:55:00 UTC
# Author: GitHub Copilot (ImpressionCore)

"""
Privacy Controls System Module

This module provides comprehensive privacy management capabilities for ImpressionCore,
implementing access control, consent management, data anonymization, and compliance
frameworks. Optimized for GTX 1050 Ti hardware constraints.

Components:
- AccessControl: Fine-grained data access management
- ConsentManager: User consent tracking and enforcement
- DataAnonymizer: Data anonymization and pseudonymization
- ComplianceFramework: GDPR/CCPA compliance infrastructure

Memory Limits:
- Total privacy subsystem: <80MB memory usage
- Access control cache: <15MB active permissions
- Consent database: <20MB active consents
- Anonymization buffer: <25MB temporary operations
"""

import logging
from typing import Dict, Any, Optional
import asyncio
from pathlib import Path

# Configure module logging
logger = logging.getLogger(__name__)

# Privacy module configuration
PRIVACY_CONFIG = {
    'memory_limits': {
        'total_limit_mb': 80,
        'access_control_mb': 15,
        'consent_db_mb': 20,
        'anonymization_mb': 25,
        'compliance_mb': 20
    },
    'performance': {
        'max_concurrent_operations': 8,
        'cache_ttl_seconds': 1800,  # 30 minutes
        'cleanup_interval_seconds': 300,
        'consent_check_timeout_ms': 100
    },
    'compliance': {
        'gdpr_enabled': True,
        'ccpa_enabled': True,
        'retention_days_default': 365,
        'anonymization_delay_days': 30,
        'audit_retention_years': 7
    },
    'security': {
        'encrypt_consent_data': True,
        'hash_personal_identifiers': True,
        'secure_deletion': True,
        'access_log_retention_days': 90
    },
    'anonymization': {
        'default_k_anonymity': 5,
        'differential_privacy_epsilon': 1.0,
        'suppression_threshold': 0.1,
        'generalization_levels': 3
    }
}

# Lazy imports for memory optimization
_access_control = None
_consent_manager = None
_data_anonymizer = None
_compliance_framework = None

def get_access_control():
    """Get access control instance with lazy loading."""
    global _access_control
    if _access_control is None:
        from .access_control import AccessControl
        _access_control = AccessControl()
        logger.info("Access control system initialized")
    return _access_control

def get_consent_manager():
    """Get consent manager instance with lazy loading."""
    global _consent_manager
    if _consent_manager is None:
        from .consent_manager import ConsentManager
        _consent_manager = ConsentManager()
        logger.info("Consent manager initialized")
    return _consent_manager

def get_data_anonymizer():
    """Get data anonymizer instance with lazy loading."""
    global _data_anonymizer
    if _data_anonymizer is None:
        from .data_anonymizer import DataAnonymizer
        _data_anonymizer = DataAnonymizer()
        logger.info("Data anonymizer initialized")
    return _data_anonymizer

def get_compliance_framework():
    """Get compliance framework instance with lazy loading."""
    global _compliance_framework
    if _compliance_framework is None:
        from .compliance_framework import ComplianceFramework
        _compliance_framework = ComplianceFramework()
        logger.info("Compliance framework initialized")
    return _compliance_framework

def cleanup_privacy_cache():
    """Clean up privacy module cache to free memory."""
    global _access_control, _consent_manager, _data_anonymizer, _compliance_framework
    
    cleanup_count = 0
    if _access_control:
        _access_control.cleanup()
        cleanup_count += 1
    if _consent_manager:
        _consent_manager.cleanup()
        cleanup_count += 1
    if _data_anonymizer:
        _data_anonymizer.cleanup()
        cleanup_count += 1
    if _compliance_framework:
        _compliance_framework.cleanup()
        cleanup_count += 1
    
    logger.info(f"Cleaned up {cleanup_count} privacy components")

# Export main classes and functions
__all__ = [
    'get_access_control',
    'get_consent_manager',
    'get_data_anonymizer',
    'get_compliance_framework',
    'cleanup_privacy_cache',
    'PRIVACY_CONFIG'
]

# Module metadata
__version__ = "8A.2.2"
__author__ = "ImpressionCore Privacy Team"
__status__ = "Development"
