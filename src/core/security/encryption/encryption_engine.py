# Phase 8A Week 2: Encryption Engine Implementation
# File: src/security/encryption/encryption_engine.py
# Description: Main encryption orchestrator and coordinator
# Created: 2025-01-18 21:50:00 UTC
# Author: GitHub Copilot (ImpressionCore)

"""
Encryption Engine

Main orchestrator for all encryption operations in ImpressionCore.
Coordinates AES encryption, key management, and TLS handling with
memory optimization for GTX 1050 Ti hardware constraints.

Features:
- Unified encryption API
- Automatic key management
- Secure communication setup
- Performance monitoring and optimization
- Memory-efficient operations

Memory limit: <100MB total encryption subsystem
"""

import logging
import time
import asyncio
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import threading
from datetime import datetime, timedelta
from enum import Enum
import json

# Performance monitoring
import psutil

logger = logging.getLogger(__name__)

class EncryptionMode(Enum):
    """Encryption operation modes."""
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"

class SecurityLevel(Enum):
    """Security levels for encryption operations."""
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"

@dataclass
class EncryptionRequest:
    """Request for encryption operation."""
    operation: EncryptionMode
    data: Union[str, bytes]
    security_level: SecurityLevel = SecurityLevel.STANDARD
    key_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class EncryptionResponse:
    """Response from encryption operation."""
    success: bool
    result: Optional[Union[str, bytes]]
    key_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)

class EncryptionEngine:
    """
    Main encryption engine coordinating all encryption operations.
    
    Provides a unified interface for:
    - Data encryption/decryption
    - Key management
    - Secure communications
    - Performance optimization
    """
    
    def __init__(self, 
                 storage_path: Optional[str] = None,
                 master_password: Optional[str] = None,
                 enable_hardware_acceleration: bool = True):
        """Initialize encryption engine."""
        self.storage_path = Path(storage_path or "data/security")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Component initialization flags
        self._aes_encryption = None
        self._key_manager = None
        self._tls_handler = None
        self._components_lock = threading.RLock()
        
        # Configuration
        self.master_password = master_password
        self.enable_hardware_acceleration = enable_hardware_acceleration
        
        # Performance monitoring
        self.metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'bytes_processed': 0,
            'average_operation_time': 0.0,
            'memory_usage_mb': 0.0
        }
        
        self.operation_history = []
        self.max_history_size = 1000
        
        # Memory management
        self.memory_limit_mb = 100
        self.component_memory_limits = {
            'aes_encryption': 30,
            'key_manager': 20,
            'tls_handler': 25,
            'engine_overhead': 25
        }
        
        # Monitoring and cleanup
        self.cleanup_interval = 300  # 5 minutes
        self.memory_monitor = threading.Timer(60.0, self._monitor_memory)
        self.memory_monitor.daemon = True
        self.memory_monitor.start()
        
        self.cleanup_timer = threading.Timer(self.cleanup_interval, self._periodic_cleanup)
        self.cleanup_timer.daemon = True
        self.cleanup_timer.start()
        
        logger.info(f"Encryption engine initialized - Storage: {self.storage_path}")

    @property
    def aes_encryption(self):
        """Get AES encryption instance with lazy loading."""
        if self._aes_encryption is None:
            with self._components_lock:
                if self._aes_encryption is None:
                    from .aes_encryption import AESEncryption, EncryptionConfig
                    config = EncryptionConfig(memory_limit_mb=self.component_memory_limits['aes_encryption'])
                    self._aes_encryption = AESEncryption(config)
                    logger.debug("AES encryption component loaded")
        return self._aes_encryption

    @property
    def key_manager(self):
        """Get key manager instance with lazy loading."""
        if self._key_manager is None:
            with self._components_lock:
                if self._key_manager is None:
                    from .key_management import KeyManager
                    storage_path = str(self.storage_path / "keys")
                    self._key_manager = KeyManager(storage_path, self.master_password)
                    logger.debug("Key manager component loaded")
        return self._key_manager

    @property
    def tls_handler(self):
        """Get TLS handler instance with lazy loading."""
        if self._tls_handler is None:
            with self._components_lock:
                if self._tls_handler is None:
                    from .tls_handler import TLSHandler, TLSConfig
                    config = TLSConfig(max_connections=50)  # Reduced for memory constraints
                    cert_store = str(self.storage_path / "certificates")
                    self._tls_handler = TLSHandler(config, cert_store)
                    logger.debug("TLS handler component loaded")
        return self._tls_handler

    async def encrypt_data(self, 
                          data: Union[str, bytes], 
                          security_level: SecurityLevel = SecurityLevel.STANDARD,
                          key_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> EncryptionResponse:
        """
        Encrypt data with specified security level.
        
        Args:
            data: Data to encrypt
            security_level: Security level for encryption
            key_id: Optional existing key ID
            metadata: Optional metadata
            
        Returns:
            Encryption response with result and metrics
        """
        start_time = time.time()
        
        try:
            # Determine encryption parameters based on security level
            algorithm, key_size = self._get_encryption_params(security_level)
            
            # Get or generate encryption key
            if key_id:
                key = self.key_manager.get_key(key_id)
                if not key:
                    return EncryptionResponse(
                        success=False,
                        result=None,
                        key_id=key_id,
                        error=f"Key {key_id} not found"
                    )
            else:
                # Generate new key
                from .key_management import KeyType
                key_id = self.key_manager.generate_key(
                    key_type=KeyType.SYMMETRIC,
                    algorithm=algorithm,
                    key_size=key_size,
                    tags=metadata or {}
                )
                key = self.key_manager.get_key(key_id)
            
            # Perform encryption
            encryption_result = self.aes_encryption.encrypt(data, key)
            
            # Calculate metrics
            operation_time = time.time() - start_time
            data_size = len(data) if isinstance(data, (str, bytes)) else 0
            
            # Update metrics
            self._update_metrics(True, operation_time, data_size)
            
            # Create response
            response = EncryptionResponse(
                success=True,
                result=encryption_result.ciphertext,
                key_id=key_id,
                metadata={
                    'iv': encryption_result.iv.hex(),
                    'tag': encryption_result.tag.hex(),
                    'algorithm': algorithm,
                    'key_size': key_size,
                    'security_level': security_level.value,
                    **(metadata or {})
                },
                performance_metrics={
                    'operation_time_ms': operation_time * 1000,
                    'throughput_mbps': (data_size / (1024 * 1024)) / operation_time if operation_time > 0 else 0,
                    'data_size_bytes': data_size
                }
            )
            
            logger.debug(f"Encrypted {data_size} bytes in {operation_time:.3f}s")
            return response
            
        except Exception as e:
            operation_time = time.time() - start_time
            self._update_metrics(False, operation_time, 0)
            
            logger.error(f"Encryption error: {e}")
            return EncryptionResponse(
                success=False,
                result=None,
                key_id=key_id,
                error=str(e),
                performance_metrics={
                    'operation_time_ms': operation_time * 1000,
                    'error': True
                }
            )

    async def decrypt_data(self, 
                          ciphertext: bytes,
                          key_id: str,
                          iv: Union[str, bytes],
                          tag: Union[str, bytes],
                          metadata: Optional[Dict[str, Any]] = None) -> EncryptionResponse:
        """
        Decrypt data using specified key.
        
        Args:
            ciphertext: Encrypted data
            key_id: Key identifier for decryption
            iv: Initialization vector
            tag: Authentication tag
            metadata: Optional metadata
            
        Returns:
            Decryption response with result and metrics
        """
        start_time = time.time()
        
        try:
            # Get decryption key
            key = self.key_manager.get_key(key_id)
            if not key:
                return EncryptionResponse(
                    success=False,
                    result=None,
                    key_id=key_id,
                    error=f"Key {key_id} not found"
                )
            
            # Convert hex strings to bytes if needed
            if isinstance(iv, str):
                iv = bytes.fromhex(iv)
            if isinstance(tag, str):
                tag = bytes.fromhex(tag)
            
            # Perform decryption
            decryption_result = self.aes_encryption.decrypt(ciphertext, key, iv, tag)
            
            if not decryption_result.verified:
                return EncryptionResponse(
                    success=False,
                    result=None,
                    key_id=key_id,
                    error="Decryption failed: authentication verification failed"
                )
            
            # Calculate metrics
            operation_time = time.time() - start_time
            data_size = len(decryption_result.plaintext)
            
            # Update metrics
            self._update_metrics(True, operation_time, data_size)
            
            # Create response
            response = EncryptionResponse(
                success=True,
                result=decryption_result.plaintext,
                key_id=key_id,
                metadata={
                    'verified': decryption_result.verified,
                    'original_size': data_size,
                    **(metadata or {})
                },
                performance_metrics={
                    'operation_time_ms': operation_time * 1000,
                    'throughput_mbps': (data_size / (1024 * 1024)) / operation_time if operation_time > 0 else 0,
                    'data_size_bytes': data_size
                }
            )
            
            logger.debug(f"Decrypted {data_size} bytes in {operation_time:.3f}s")
            return response
            
        except Exception as e:
            operation_time = time.time() - start_time
            self._update_metrics(False, operation_time, 0)
            
            logger.error(f"Decryption error: {e}")
            return EncryptionResponse(
                success=False,
                result=None,
                key_id=key_id,
                error=str(e),
                performance_metrics={
                    'operation_time_ms': operation_time * 1000,
                    'error': True
                }
            )

    async def encrypt_file(self, 
                          file_path: str,
                          output_path: str,
                          security_level: SecurityLevel = SecurityLevel.STANDARD,
                          password: Optional[str] = None) -> EncryptionResponse:
        """
        Encrypt a file with streaming for memory efficiency.
        
        Args:
            file_path: Path to input file
            output_path: Path to encrypted output file
            security_level: Security level for encryption
            password: Optional password (generates key if not provided)
            
        Returns:
            Encryption response with result and metrics
        """
        start_time = time.time()
        
        try:
            if not password:
                # Generate a secure password
                import secrets
                import string
                alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
                password = ''.join(secrets.choice(alphabet) for _ in range(32))
            
            # Perform file encryption
            metadata = self.aes_encryption.encrypt_file(file_path, output_path, password)
            
            operation_time = time.time() - start_time
            
            # Update metrics
            self._update_metrics(True, operation_time, metadata['bytes_processed'])
            
            response = EncryptionResponse(
                success=True,
                result=output_path,
                key_id=None,  # File encryption uses password
                metadata={
                    'password': password,
                    'file_encryption': True,
                    **metadata
                },
                performance_metrics={
                    'operation_time_ms': operation_time * 1000,
                    'throughput_mbps': (metadata['bytes_processed'] / (1024 * 1024)) / operation_time if operation_time > 0 else 0,
                    'file_size_bytes': metadata['file_size']
                }
            )
            
            logger.info(f"Encrypted file {file_path} in {operation_time:.3f}s")
            return response
            
        except Exception as e:
            operation_time = time.time() - start_time
            self._update_metrics(False, operation_time, 0)
            
            logger.error(f"File encryption error: {e}")
            return EncryptionResponse(
                success=False,
                result=None,
                key_id=None,
                error=str(e),
                performance_metrics={
                    'operation_time_ms': operation_time * 1000,
                    'error': True
                }
            )

    async def decrypt_file(self, 
                          file_path: str,
                          output_path: str,
                          password: str) -> EncryptionResponse:
        """
        Decrypt a file using password.
        
        Args:
            file_path: Path to encrypted file
            output_path: Path to decrypted output file
            password: Password for decryption
            
        Returns:
            Decryption response with result and metrics
        """
        start_time = time.time()
        
        try:
            # Perform file decryption
            metadata = self.aes_encryption.decrypt_file(file_path, output_path, password)
            
            operation_time = time.time() - start_time
            
            # Update metrics
            self._update_metrics(True, operation_time, metadata['bytes_processed'])
            
            response = EncryptionResponse(
                success=True,
                result=output_path,
                key_id=None,
                metadata={
                    'file_decryption': True,
                    **metadata
                },
                performance_metrics={
                    'operation_time_ms': operation_time * 1000,
                    'throughput_mbps': (metadata['bytes_processed'] / (1024 * 1024)) / operation_time if operation_time > 0 else 0,
                    'bytes_processed': metadata['bytes_processed']
                }
            )
            
            logger.info(f"Decrypted file {file_path} in {operation_time:.3f}s")
            return response
            
        except Exception as e:
            operation_time = time.time() - start_time
            self._update_metrics(False, operation_time, 0)
            
            logger.error(f"File decryption error: {e}")
            return EncryptionResponse(
                success=False,
                result=None,
                key_id=None,
                error=str(e),
                performance_metrics={
                    'operation_time_ms': operation_time * 1000,
                    'error': True
                }
            )

    async def create_secure_connection(self, 
                                     host: str, 
                                     port: int,
                                     cert_file: Optional[str] = None,
                                     key_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a secure TLS connection.
        
        Args:
            host: Remote host
            port: Remote port
            cert_file: Client certificate file
            key_file: Client private key file
            
        Returns:
            Connection information and socket
        """
        try:
            ssl_socket = await self.tls_handler.create_secure_connection(
                host, port, cert_file, key_file
            )
            
            return {
                'success': True,
                'socket': ssl_socket,
                'host': host,
                'port': port,
                'tls_version': ssl_socket.version(),
                'cipher': ssl_socket.cipher()
            }
            
        except Exception as e:
            logger.error(f"Secure connection error: {e}")
            return {
                'success': False,
                'error': str(e),
                'host': host,
                'port': port
            }

    def generate_certificate(self, 
                           subject_name: str,
                           key_size: int = 2048,
                           validity_days: int = 365) -> Dict[str, Any]:
        """
        Generate a TLS certificate.
        
        Args:
            subject_name: Certificate subject name
            key_size: RSA key size
            validity_days: Certificate validity period
            
        Returns:
            Certificate generation result
        """
        try:
            from .tls_handler import CertificateType
            cert_path, key_path = self.tls_handler.generate_certificate(
                subject_name, CertificateType.SERVER, key_size, validity_days
            )
            
            return {
                'success': True,
                'certificate_path': cert_path,
                'private_key_path': key_path,
                'subject_name': subject_name,
                'key_size': key_size,
                'validity_days': validity_days
            }
            
        except Exception as e:
            logger.error(f"Certificate generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'subject_name': subject_name
            }

    def _get_encryption_params(self, security_level: SecurityLevel) -> Tuple[str, int]:
        """Get encryption parameters based on security level."""
        if security_level == SecurityLevel.STANDARD:
            return "AES", 256
        elif security_level == SecurityLevel.HIGH:
            return "AES", 256  # Could add different algorithms here
        elif security_level == SecurityLevel.MAXIMUM:
            return "AES", 256  # Could add post-quantum algorithms here
        else:
            return "AES", 256

    def _update_metrics(self, success: bool, operation_time: float, bytes_processed: int):
        """Update performance metrics."""
        self.metrics['total_operations'] += 1
        if success:
            self.metrics['successful_operations'] += 1
        else:
            self.metrics['failed_operations'] += 1
        
        self.metrics['bytes_processed'] += bytes_processed
        
        # Update average operation time
        total_ops = self.metrics['total_operations']
        current_avg = self.metrics['average_operation_time']
        self.metrics['average_operation_time'] = ((current_avg * (total_ops - 1)) + operation_time) / total_ops
        
        # Store operation history
        operation_record = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'operation_time': operation_time,
            'bytes_processed': bytes_processed
        }
        
        self.operation_history.append(operation_record)
        if len(self.operation_history) > self.max_history_size:
            self.operation_history.pop(0)

    def _monitor_memory(self):
        """Monitor memory usage across all components."""
        try:
            process = psutil.Process()
            total_memory_mb = process.memory_info().rss / (1024 * 1024)
            
            self.metrics['memory_usage_mb'] = total_memory_mb
            
            if total_memory_mb > self.memory_limit_mb:
                logger.warning(f"Encryption engine memory usage ({total_memory_mb:.1f}MB) exceeds limit ({self.memory_limit_mb}MB)")
                
                # Trigger cleanup on components
                if self._aes_encryption:
                    self._aes_encryption.cleanup()
                if self._key_manager:
                    self._key_manager.cleanup()
                if self._tls_handler:
                    self._tls_handler.cleanup()
            
            # Schedule next monitoring
            self.memory_monitor = threading.Timer(60.0, self._monitor_memory)
            self.memory_monitor.daemon = True
            self.memory_monitor.start()
            
        except Exception as e:
            logger.error(f"Memory monitoring error: {e}")

    def _periodic_cleanup(self):
        """Perform periodic cleanup of resources."""
        try:
            # Clean up operation history
            if len(self.operation_history) > self.max_history_size // 2:
                self.operation_history = self.operation_history[-self.max_history_size // 2:]
            
            # Trigger component cleanup
            if self._key_manager:
                # Clean up expired keys
                from .key_management import KeyStatus
                expired_keys = self._key_manager.list_keys(status=KeyStatus.EXPIRED)
                for key_metadata in expired_keys:
                    try:
                        self._key_manager.revoke_key(key_metadata.key_id, "Expired")
                    except:
                        pass
            
            # Schedule next cleanup
            self.cleanup_timer = threading.Timer(self.cleanup_interval, self._periodic_cleanup)
            self.cleanup_timer.daemon = True
            self.cleanup_timer.start()
            
            logger.debug("Periodic cleanup completed")
            
        except Exception as e:
            logger.error(f"Periodic cleanup error: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive encryption engine metrics."""
        component_metrics = {}
        
        try:
            if self._aes_encryption:
                component_metrics['aes_encryption'] = self._aes_encryption.get_metrics()
            if self._key_manager:
                component_metrics['key_manager'] = self._key_manager.get_metrics()
            if self._tls_handler:
                component_metrics['tls_handler'] = self._tls_handler.get_metrics()
        except Exception as e:
            logger.error(f"Error getting component metrics: {e}")
        
        return {
            'engine_metrics': dict(self.metrics),
            'component_metrics': component_metrics,
            'configuration': {
                'memory_limit_mb': self.memory_limit_mb,
                'component_memory_limits': self.component_memory_limits,
                'hardware_acceleration': self.enable_hardware_acceleration,
                'storage_path': str(self.storage_path)
            },
            'recent_operations': self.operation_history[-10:] if self.operation_history else []
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        with self._components_lock:
            components_loaded = {
                'aes_encryption': self._aes_encryption is not None,
                'key_manager': self._key_manager is not None,
                'tls_handler': self._tls_handler is not None
            }
        
        return {
            'engine_running': True,
            'components_loaded': components_loaded,
            'total_operations': self.metrics['total_operations'],
            'success_rate': (self.metrics['successful_operations'] / self.metrics['total_operations']) * 100 if self.metrics['total_operations'] > 0 else 0,
            'memory_usage_mb': self.metrics['memory_usage_mb'],
            'storage_path': str(self.storage_path)
        }

    def cleanup(self):
        """Clean up encryption engine resources."""
        try:
            # Cancel timers
            if hasattr(self, 'memory_monitor'):
                self.memory_monitor.cancel()
            if hasattr(self, 'cleanup_timer'):
                self.cleanup_timer.cancel()
            
            # Clean up components
            with self._components_lock:
                if self._aes_encryption:
                    self._aes_encryption.cleanup()
                    self._aes_encryption = None
                if self._key_manager:
                    self._key_manager.cleanup()
                    self._key_manager = None
                if self._tls_handler:
                    self._tls_handler.cleanup()
                    self._tls_handler = None
            
            # Clear metrics and history
            self.metrics.clear()
            self.operation_history.clear()
            
            logger.info("Encryption engine cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except:
            pass
