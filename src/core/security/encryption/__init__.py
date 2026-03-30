# Phase 8A Week 2: Data Security & Encryption Framework
# File: src/security/encryption/__init__.py
# Description: Encryption module initialization and configuration
# Created: 2025-01-18 21:30:00 UTC
# Author: GitHub Copilot (ImpressionCore)

"""
Encryption Framework Module

This module provides comprehensive encryption capabilities for ImpressionCore,
implementing AES-256 encryption, secure key management, and TLS 1.3 integration.
Optimized for GTX 1050 Ti hardware constraints.

Components:
- AESEncryption: High-performance AES-256 encryption engine
- KeyManager: Secure cryptographic key management system
- TLSHandler: TLS 1.3 secure communication handler
- EncryptionEngine: Main encryption orchestrator

Memory Limits:
- Total encryption subsystem: <100MB memory usage
- Key cache: <20MB active keys
- Encryption buffer: <30MB temporary operations
"""

import logging
from typing import Dict, Any, Optional
import asyncio
from pathlib import Path

# Configure module logging
logger = logging.getLogger(__name__)

# Encryption module configuration
ENCRYPTION_CONFIG = {
    'memory_limits': {
        'total_limit_mb': 100,
        'key_cache_mb': 20,
        'buffer_limit_mb': 30,
        'session_limit_mb': 25
    },
    'performance': {
        'max_concurrent_operations': 10,
        'key_derivation_iterations': 100000,
        'cache_ttl_seconds': 3600,
        'cleanup_interval_seconds': 300
    },
    'security': {
        'aes_key_size': 256,
        'gcm_tag_size': 16,
        'salt_size': 32,
        'iv_size': 16,
        'enforce_tls_13': True
    },
    'hardware_optimization': {
        'enable_aes_ni': True,
        'use_hardware_rng': True,
        'parallel_operations': 4,
        'memory_pool_size_mb': 50
    }
}

# Lazy imports for memory optimization
_aes_encryption = None
_key_manager = None
_tls_handler = None
_encryption_engine = None

def get_aes_encryption():
    """Get AES encryption instance with lazy loading."""
    global _aes_encryption
    if _aes_encryption is None:
        from .aes_encryption import AESEncryption
        _aes_encryption = AESEncryption()
        logger.info("AES encryption engine initialized")
    return _aes_encryption

def get_key_manager():
    """Get key manager instance with lazy loading."""
    global _key_manager
    if _key_manager is None:
        from .key_management import KeyManager
        _key_manager = KeyManager()
        logger.info("Key manager initialized")
    return _key_manager

def get_tls_handler():
    """Get TLS handler instance with lazy loading."""
    global _tls_handler
    if _tls_handler is None:
        from .tls_handler import TLSHandler
        _tls_handler = TLSHandler()
        logger.info("TLS handler initialized")
    return _tls_handler

def get_encryption_engine():
    """Get main encryption engine with lazy loading."""
    global _encryption_engine
    if _encryption_engine is None:
        from .encryption_engine import EncryptionEngine
        _encryption_engine = EncryptionEngine()
        logger.info("Encryption engine initialized")
    return _encryption_engine

def cleanup_encryption_cache():
    """Clean up encryption module cache to free memory."""
    global _aes_encryption, _key_manager, _tls_handler, _encryption_engine
    
    cleanup_count = 0
    if _aes_encryption:
        _aes_encryption.cleanup()
        cleanup_count += 1
    if _key_manager:
        _key_manager.cleanup()
        cleanup_count += 1
    if _tls_handler:
        _tls_handler.cleanup()
        cleanup_count += 1
    if _encryption_engine:
        _encryption_engine.cleanup()
        cleanup_count += 1
    
    logger.info(f"Cleaned up {cleanup_count} encryption components")

# Export main classes and functions
__all__ = [
    'get_aes_encryption',
    'get_key_manager', 
    'get_tls_handler',
    'get_encryption_engine',
    'cleanup_encryption_cache',
    'ENCRYPTION_CONFIG'
]

# Module metadata
__version__ = "8A.2.1"
__author__ = "ImpressionCore Security Team"
__status__ = "Development"
