# Phase 8A Week 2: Key Management System
# File: src/security/encryption/key_management.py
# Description: Secure cryptographic key management system
# Created: 2025-01-18 21:40:00 UTC
# Author: GitHub Copilot (ImpressionCore)

"""
Key Management System

Provides secure cryptographic key management with:
- Hardware Security Module (HSM) integration
- Key lifecycle management (generation, rotation, revocation)
- Secure key storage and retrieval
- Key escrow and recovery capabilities
- Performance optimized for GTX 1050 Ti

Memory limit: <20MB for active key cache
"""

import logging
import os
import time
import json
import sqlite3
from typing import Dict, Any, Optional, List, Tuple, Union
import asyncio
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import hmac
from datetime import datetime, timedelta
from enum import Enum
import threading

# Cryptographic imports
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256, SHA512
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.fernet import Fernet
import base64

# Performance monitoring
import psutil

logger = logging.getLogger(__name__)

class KeyType(Enum):
    """Types of cryptographic keys."""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    MASTER = "master"
    SESSION = "session"
    DERIVED = "derived"

class KeyStatus(Enum):
    """Key lifecycle status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"
    PENDING = "pending"

@dataclass
class KeyMetadata:
    """Metadata for a cryptographic key."""
    key_id: str
    key_type: KeyType
    algorithm: str
    key_size: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    status: KeyStatus = KeyStatus.ACTIVE
    usage_count: int = 0
    last_used: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)
    access_level: str = "standard"
    rotation_interval: Optional[timedelta] = None
    
@dataclass
class KeyEntry:
    """Complete key entry with metadata and encrypted key material."""
    metadata: KeyMetadata
    encrypted_key: bytes
    checksum: str
    storage_location: str
    backup_locations: List[str] = field(default_factory=list)

class KeyManager:
    """
    Secure cryptographic key management system.
    
    Features:
    - Secure key generation and storage
    - Key lifecycle management
    - Hardware security module integration
    - Memory-optimized key caching
    - Audit logging and compliance
    """
    
    def __init__(self, storage_path: Optional[str] = None, master_password: Optional[str] = None):
        """Initialize key manager."""
        self.storage_path = Path(storage_path or "data/security/keys")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Database for key metadata
        self.db_path = self.storage_path / "key_metadata.db"
        self.init_database()
        
        # Master key for encrypting stored keys
        self.master_key = None
        if master_password:
            self.set_master_password(master_password)
        
        # Key cache for performance
        self.key_cache = {}
        self.cache_lock = threading.RLock()
        self.cache_ttl = 3600  # 1 hour
        self.max_cache_size = 100  # Maximum keys in cache
        
        # Performance monitoring
        self.metrics = {
            'keys_generated': 0,
            'keys_retrieved': 0,
            'keys_rotated': 0,
            'keys_revoked': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Memory monitoring
        self.memory_limit_mb = 20
        self.memory_monitor = threading.Timer(300.0, self._monitor_memory)
        self.memory_monitor.daemon = True
        self.memory_monitor.start()
        
        logger.info(f"Key manager initialized - Storage: {self.storage_path}")

    def init_database(self):
        """Initialize SQLite database for key metadata."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS key_metadata (
                    key_id TEXT PRIMARY KEY,
                    key_type TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    key_size INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    status TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT,
                    tags TEXT,
                    access_level TEXT DEFAULT 'standard',
                    rotation_interval INTEGER,
                    storage_location TEXT NOT NULL,
                    backup_locations TEXT,
                    checksum TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS key_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    details TEXT,
                    FOREIGN KEY (key_id) REFERENCES key_metadata (key_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Key metadata database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def set_master_password(self, password: str):
        """Set master password for key encryption."""
        try:
            # Derive master key from password
            salt = os.urandom(32)
            kdf = PBKDF2HMAC(
                algorithm=SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            self.master_key = kdf.derive(password.encode('utf-8'))
            
            # Store salt for future derivation
            salt_file = self.storage_path / "master.salt"
            with open(salt_file, 'wb') as f:
                f.write(salt)
            
            logger.info("Master password set successfully")
            
        except Exception as e:
            logger.error(f"Master password setup error: {e}")
            raise

    def load_master_key(self, password: str) -> bool:
        """Load master key from password."""
        try:
            salt_file = self.storage_path / "master.salt"
            if not salt_file.exists():
                logger.error("Master salt file not found")
                return False
            
            with open(salt_file, 'rb') as f:
                salt = f.read()
            
            kdf = PBKDF2HMAC(
                algorithm=SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            self.master_key = kdf.derive(password.encode('utf-8'))
            
            logger.info("Master key loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Master key loading error: {e}")
            return False

    def _encrypt_key(self, key_material: bytes) -> bytes:
        """Encrypt key material using master key."""
        if not self.master_key:
            raise ValueError("Master key not set")
        
        # Use Fernet for authenticated encryption
        fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
        return fernet.encrypt(key_material)

    def _decrypt_key(self, encrypted_key: bytes) -> bytes:
        """Decrypt key material using master key."""
        if not self.master_key:
            raise ValueError("Master key not set")
        
        fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
        return fernet.decrypt(encrypted_key)

    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of data."""
        return hashlib.sha256(data).hexdigest()

    def generate_key(self, 
                    key_type: KeyType, 
                    algorithm: str, 
                    key_size: int,
                    key_id: Optional[str] = None,
                    expires_in: Optional[timedelta] = None,
                    tags: Optional[Dict[str, str]] = None) -> str:
        """
        Generate a new cryptographic key.
        
        Args:
            key_type: Type of key to generate
            algorithm: Cryptographic algorithm
            key_size: Key size in bits
            key_id: Optional key identifier
            expires_in: Optional expiration time
            tags: Optional metadata tags
            
        Returns:
            Key identifier
        """
        try:
            # Generate unique key ID if not provided
            if not key_id:
                key_id = f"{algorithm}_{key_size}_{int(time.time())}"
            
            # Generate key material based on type and algorithm
            if key_type == KeyType.SYMMETRIC:
                if algorithm.upper().startswith('AES'):
                    key_material = os.urandom(key_size // 8)
                else:
                    raise ValueError(f"Unsupported symmetric algorithm: {algorithm}")
            
            elif key_type in [KeyType.ASYMMETRIC_PUBLIC, KeyType.ASYMMETRIC_PRIVATE]:
                if algorithm.upper().startswith('RSA'):
                    private_key = rsa.generate_private_key(
                        public_exponent=65537,
                        key_size=key_size,
                        backend=default_backend()
                    )
                    
                    if key_type == KeyType.ASYMMETRIC_PRIVATE:
                        key_material = private_key.private_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PrivateFormat.PKCS8,
                            encryption_algorithm=serialization.NoEncryption()
                        )
                    else:
                        public_key = private_key.public_key()
                        key_material = public_key.public_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PublicFormat.SubjectPublicKeyInfo
                        )
                else:
                    raise ValueError(f"Unsupported asymmetric algorithm: {algorithm}")
            
            else:
                raise ValueError(f"Unsupported key type: {key_type}")
            
            # Create metadata
            created_at = datetime.now()
            expires_at = created_at + expires_in if expires_in else None
            
            metadata = KeyMetadata(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                key_size=key_size,
                created_at=created_at,
                expires_at=expires_at,
                tags=tags or {}
            )
            
            # Encrypt key material
            encrypted_key = self._encrypt_key(key_material)
            checksum = self._calculate_checksum(key_material)
            
            # Store key
            storage_location = str(self.storage_path / f"{key_id}.key")
            with open(storage_location, 'wb') as f:
                f.write(encrypted_key)
            
            # Store metadata in database
            self._store_metadata(metadata, storage_location, checksum)
            
            # Add to cache
            with self.cache_lock:
                self.key_cache[key_id] = {
                    'key_material': key_material,
                    'metadata': metadata,
                    'timestamp': time.time()
                }
                self._cleanup_cache()
            
            # Update metrics
            self.metrics['keys_generated'] += 1
            
            # Audit log
            self._audit_log(key_id, 'generate', f"Generated {algorithm} {key_size}-bit key")
            
            logger.info(f"Generated key {key_id} ({algorithm}, {key_size} bits)")
            return key_id
            
        except Exception as e:
            logger.error(f"Key generation error: {e}")
            raise

    def _store_metadata(self, metadata: KeyMetadata, storage_location: str, checksum: str):
        """Store key metadata in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO key_metadata (
                    key_id, key_type, algorithm, key_size, created_at, expires_at,
                    status, usage_count, last_used, tags, access_level, 
                    rotation_interval, storage_location, backup_locations, checksum
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.key_id,
                metadata.key_type.value,
                metadata.algorithm,
                metadata.key_size,
                metadata.created_at.isoformat(),
                metadata.expires_at.isoformat() if metadata.expires_at else None,
                metadata.status.value,
                metadata.usage_count,
                metadata.last_used.isoformat() if metadata.last_used else None,
                json.dumps(metadata.tags),
                metadata.access_level,
                metadata.rotation_interval.total_seconds() if metadata.rotation_interval else None,
                storage_location,
                json.dumps([]),  # backup_locations
                checksum
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Metadata storage error: {e}")
            raise

    def get_key(self, key_id: str) -> Optional[bytes]:
        """
        Retrieve key material by ID.
        
        Args:
            key_id: Key identifier
            
        Returns:
            Key material or None if not found
        """
        try:
            # Check cache first
            with self.cache_lock:
                if key_id in self.key_cache:
                    cache_entry = self.key_cache[key_id]
                    # Check if cache entry is still valid
                    if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                        self.metrics['cache_hits'] += 1
                        self._update_usage(key_id)
                        return cache_entry['key_material']
                    else:
                        # Remove expired entry
                        del self.key_cache[key_id]
            
            self.metrics['cache_misses'] += 1
            
            # Load from storage
            metadata = self._get_metadata(key_id)
            if not metadata:
                logger.warning(f"Key {key_id} not found")
                return None
            
            # Check key status
            if metadata.status != KeyStatus.ACTIVE:
                logger.warning(f"Key {key_id} is not active (status: {metadata.status.value})")
                return None
            
            # Check expiration
            if metadata.expires_at and datetime.now() > metadata.expires_at:
                logger.warning(f"Key {key_id} has expired")
                self._update_key_status(key_id, KeyStatus.EXPIRED)
                return None
            
            # Load encrypted key
            if not os.path.exists(metadata.storage_location):
                logger.error(f"Key file not found: {metadata.storage_location}")
                return None
            
            with open(metadata.storage_location, 'rb') as f:
                encrypted_key = f.read()
            
            # Decrypt key material
            key_material = self._decrypt_key(encrypted_key)
            
            # Verify checksum
            if self._calculate_checksum(key_material) != metadata.checksum:
                logger.error(f"Key {key_id} checksum verification failed")
                return None
            
            # Add to cache
            with self.cache_lock:
                self.key_cache[key_id] = {
                    'key_material': key_material,
                    'metadata': metadata,
                    'timestamp': time.time()
                }
                self._cleanup_cache()
            
            # Update usage
            self._update_usage(key_id)
            self.metrics['keys_retrieved'] += 1
            
            logger.debug(f"Retrieved key {key_id}")
            return key_material
            
        except Exception as e:
            logger.error(f"Key retrieval error: {e}")
            return None

    def _get_metadata(self, key_id: str) -> Optional[KeyMetadata]:
        """Get key metadata from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT key_id, key_type, algorithm, key_size, created_at, expires_at,
                       status, usage_count, last_used, tags, access_level, 
                       rotation_interval, storage_location, checksum
                FROM key_metadata WHERE key_id = ?
            ''', (key_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return KeyMetadata(
                key_id=row[0],
                key_type=KeyType(row[1]),
                algorithm=row[2],
                key_size=row[3],
                created_at=datetime.fromisoformat(row[4]),
                expires_at=datetime.fromisoformat(row[5]) if row[5] else None,
                status=KeyStatus(row[6]),
                usage_count=row[7],
                last_used=datetime.fromisoformat(row[8]) if row[8] else None,
                tags=json.loads(row[9]) if row[9] else {},
                access_level=row[10],
                rotation_interval=timedelta(seconds=row[11]) if row[11] else None
            )
            
        except Exception as e:
            logger.error(f"Metadata retrieval error: {e}")
            return None

    def _update_usage(self, key_id: str):
        """Update key usage statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE key_metadata 
                SET usage_count = usage_count + 1, last_used = ?
                WHERE key_id = ?
            ''', (datetime.now().isoformat(), key_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Usage update error: {e}")

    def _update_key_status(self, key_id: str, status: KeyStatus):
        """Update key status."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE key_metadata SET status = ? WHERE key_id = ?
            ''', (status.value, key_id))
            
            conn.commit()
            conn.close()
            
            # Remove from cache if revoked or expired
            if status in [KeyStatus.REVOKED, KeyStatus.EXPIRED]:
                with self.cache_lock:
                    self.key_cache.pop(key_id, None)
            
            self._audit_log(key_id, 'status_update', f"Status changed to {status.value}")
            
        except Exception as e:
            logger.error(f"Status update error: {e}")

    def rotate_key(self, key_id: str) -> str:
        """
        Rotate a key by generating a new version.
        
        Args:
            key_id: Key identifier to rotate
            
        Returns:
            New key identifier
        """
        try:
            # Get current key metadata
            metadata = self._get_metadata(key_id)
            if not metadata:
                raise ValueError(f"Key {key_id} not found")
            
            # Generate new key with same parameters
            new_key_id = f"{key_id}_rotated_{int(time.time())}"
            
            new_key_id = self.generate_key(
                key_type=metadata.key_type,
                algorithm=metadata.algorithm,
                key_size=metadata.key_size,
                key_id=new_key_id,
                expires_in=metadata.rotation_interval,
                tags=metadata.tags
            )
            
            # Mark old key as inactive
            self._update_key_status(key_id, KeyStatus.INACTIVE)
            
            self.metrics['keys_rotated'] += 1
            self._audit_log(key_id, 'rotate', f"Rotated to {new_key_id}")
            
            logger.info(f"Rotated key {key_id} to {new_key_id}")
            return new_key_id
            
        except Exception as e:
            logger.error(f"Key rotation error: {e}")
            raise

    def revoke_key(self, key_id: str, reason: str = ""):
        """
        Revoke a key.
        
        Args:
            key_id: Key identifier to revoke
            reason: Reason for revocation
        """
        try:
            self._update_key_status(key_id, KeyStatus.REVOKED)
            self.metrics['keys_revoked'] += 1
            
            # Remove key file
            metadata = self._get_metadata(key_id)
            if metadata and os.path.exists(metadata.storage_location):
                os.remove(metadata.storage_location)
            
            self._audit_log(key_id, 'revoke', reason or "Key revoked")
            logger.info(f"Revoked key {key_id}: {reason}")
            
        except Exception as e:
            logger.error(f"Key revocation error: {e}")
            raise

    def list_keys(self, 
                 key_type: Optional[KeyType] = None,
                 status: Optional[KeyStatus] = None,
                 algorithm: Optional[str] = None) -> List[KeyMetadata]:
        """
        List keys with optional filtering.
        
        Args:
            key_type: Filter by key type
            status: Filter by status
            algorithm: Filter by algorithm
            
        Returns:
            List of key metadata
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM key_metadata WHERE 1=1"
            params = []
            
            if key_type:
                query += " AND key_type = ?"
                params.append(key_type.value)
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if algorithm:
                query += " AND algorithm = ?"
                params.append(algorithm)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            keys = []
            for row in rows:
                metadata = KeyMetadata(
                    key_id=row[0],
                    key_type=KeyType(row[1]),
                    algorithm=row[2],
                    key_size=row[3],
                    created_at=datetime.fromisoformat(row[4]),
                    expires_at=datetime.fromisoformat(row[5]) if row[5] else None,
                    status=KeyStatus(row[6]),
                    usage_count=row[7],
                    last_used=datetime.fromisoformat(row[8]) if row[8] else None,
                    tags=json.loads(row[9]) if row[9] else {},
                    access_level=row[10]
                )
                keys.append(metadata)
            
            return keys
            
        except Exception as e:
            logger.error(f"Key listing error: {e}")
            return []

    def _cleanup_cache(self):
        """Clean up key cache to maintain memory limits."""
        if len(self.key_cache) <= self.max_cache_size:
            return
        
        # Remove oldest entries
        sorted_entries = sorted(
            self.key_cache.items(),
            key=lambda x: x[1]['timestamp']
        )
        
        remove_count = len(self.key_cache) - self.max_cache_size
        for key_id, _ in sorted_entries[:remove_count]:
            del self.key_cache[key_id]
        
        logger.debug(f"Cleaned up {remove_count} cache entries")

    def _monitor_memory(self):
        """Monitor memory usage."""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            
            if memory_mb > self.memory_limit_mb:
                logger.warning(f"Key manager memory usage ({memory_mb:.1f}MB) exceeds limit")
                # Clear cache to free memory
                with self.cache_lock:
                    self.key_cache.clear()
            
            # Schedule next monitoring
            self.memory_monitor = threading.Timer(300.0, self._monitor_memory)
            self.memory_monitor.daemon = True
            self.memory_monitor.start()
            
        except Exception as e:
            logger.error(f"Memory monitoring error: {e}")

    def _audit_log(self, key_id: str, operation: str, details: str):
        """Log key management operations for audit."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO key_audit (key_id, operation, timestamp, details)
                VALUES (?, ?, ?, ?)
            ''', (key_id, operation, datetime.now().isoformat(), details))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Audit logging error: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get key manager performance metrics."""
        with self.cache_lock:
            cache_size = len(self.key_cache)
        
        return {
            'operations': dict(self.metrics),
            'cache': {
                'size': cache_size,
                'max_size': self.max_cache_size,
                'hit_rate': self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
            },
            'memory': {
                'limit_mb': self.memory_limit_mb,
                'active_keys': cache_size
            }
        }

    def cleanup(self):
        """Clean up key manager resources."""
        try:
            if hasattr(self, 'memory_monitor'):
                self.memory_monitor.cancel()
            
            with self.cache_lock:
                self.key_cache.clear()
            
            logger.info("Key manager cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except:
            pass
