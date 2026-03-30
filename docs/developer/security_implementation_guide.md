# Security Implementation Guide

**Created:** June 03, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\developer\security_implementation_guide.md #api #command_line #deployment #documentation #inference #security #testing #training #web_interface [security, implementation, guide, authentication, encryption, best-practices, 2025]  
**Category:** Developer Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

title: "ImpressionCore Security Implementation Guide"
tags: [security, implementation, guide, authentication, encryption, best-practices, 2025]
created: 2025-06-03
modified: 2025-06-03
responsible: "GitHub Copilot"
status: "complete"
category: "developer"
version: "2.0.0"
---

# Security Implementation Guide

**Last Updated:** 2025-06-03 16:00:00  
**Version:** 2.0.0  
**Document Type:** Security Implementation Guide  
**Target Audience:** Developers, Security Engineers, System Administrators  

## Overview

This guide provides comprehensive security implementation details for ImpressionCore, covering authentication, authorization, encryption, secure communication, and best practices for maintaining a secure AI framework.

## Table of Contents

1. [Authentication and Authorization](#authentication-and-authorization)
2. [Data Encryption](#data-encryption)
3. [Secure Communication](#secure-communication)
4. [Input Validation and Sanitization](#input-validation-and-sanitization)
5. [Security Monitoring and Logging](#security-monitoring-and-logging)
6. [API Security](#api-security)
7. [Model Security](#model-security)
8. [Deployment Security](#deployment-security)
9. [Security Best Practices](#security-best-practices)
10. [Compliance and Standards](#compliance-and-standards)

---

## Authentication and Authorization

### Multi-Factor Authentication (MFA)

```python
"""
Authentication implementation with MFA support
File: src/security/authentication.py
"""

from typing import Dict, Optional, Tuple
import hashlib
import secrets
import pyotp
from datetime import datetime, timedelta
import jwt

class AuthenticationManager:
    """Manages user authentication with MFA support"""
    
    def __init__(self):
        self.secret_key = secrets.token_urlsafe(32)
        self.failed_attempts: Dict[str, int] = {}
        self.lockout_time: Dict[str, datetime] = {}
        
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Securely hash password using PBKDF2"""
        if not salt:
            salt = secrets.token_hex(16)
        
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        return key.hex(), salt
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash"""
        key, _ = self.hash_password(password, salt)
        return secrets.compare_digest(key, hashed)
    
    def generate_mfa_secret(self) -> str:
        """Generate MFA secret for TOTP"""
        return pyotp.random_base32()
    
    def verify_mfa_token(self, secret: str, token: str) -> bool:
        """Verify MFA token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    def generate_jwt_token(self, user_id: str, permissions: list) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def check_rate_limit(self, user_id: str) -> bool:
        """Check if user is rate limited due to failed attempts"""
        if user_id in self.lockout_time:
            if datetime.now() < self.lockout_time[user_id]:
                return False
            else:
                # Lockout expired, reset
                del self.lockout_time[user_id]
                self.failed_attempts[user_id] = 0
        
        return True
    
    def record_failed_attempt(self, user_id: str):
        """Record failed authentication attempt"""
        self.failed_attempts[user_id] = self.failed_attempts.get(user_id, 0) + 1
        
        if self.failed_attempts[user_id] >= 5:
            # Lock out for 15 minutes
            self.lockout_time[user_id] = datetime.now() + timedelta(minutes=15)
```

### Role-Based Access Control (RBAC)

```python
"""
Role-based access control implementation
File: src/security/authorization.py
"""

from enum import Enum
from typing import Set, Dict, List
from dataclasses import dataclass

class Permission(Enum):
    """System permissions"""
    READ_MODEL = "read_model"
    WRITE_MODEL = "write_model"
    DELETE_MODEL = "delete_model"
    TRAIN_MODEL = "train_model"
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    DELETE_DATA = "delete_data"
    ADMIN_USER = "admin_user"
    SYSTEM_CONFIG = "system_config"
    API_ACCESS = "api_access"

class Role(Enum):
    """User roles"""
    GUEST = "guest"
    USER = "user"
    DEVELOPER = "developer"
    ADMIN = "admin"
    SYSTEM = "system"

@dataclass
class User:
    """User entity with roles and permissions"""
    user_id: str
    username: str
    email: str
    roles: Set[Role]
    custom_permissions: Set[Permission]
    is_active: bool = True
    mfa_enabled: bool = False
    mfa_secret: str = ""

class AuthorizationManager:
    """Manages user authorization and permissions"""
    
    def __init__(self):
        self.role_permissions = {
            Role.GUEST: {Permission.READ_MODEL, Permission.READ_DATA},
            Role.USER: {
                Permission.READ_MODEL, Permission.READ_DATA,
                Permission.API_ACCESS
            },
            Role.DEVELOPER: {
                Permission.READ_MODEL, Permission.WRITE_MODEL,
                Permission.READ_DATA, Permission.WRITE_DATA,
                Permission.TRAIN_MODEL, Permission.API_ACCESS
            },
            Role.ADMIN: {
                Permission.READ_MODEL, Permission.WRITE_MODEL, Permission.DELETE_MODEL,
                Permission.READ_DATA, Permission.WRITE_DATA, Permission.DELETE_DATA,
                Permission.TRAIN_MODEL, Permission.ADMIN_USER,
                Permission.SYSTEM_CONFIG, Permission.API_ACCESS
            },
            Role.SYSTEM: set(Permission)  # All permissions
        }
    
    def get_user_permissions(self, user: User) -> Set[Permission]:
        """Get all permissions for a user"""
        permissions = set()
        
        # Add role-based permissions
        for role in user.roles:
            permissions.update(self.role_permissions.get(role, set()))
        
        # Add custom permissions
        permissions.update(user.custom_permissions)
        
        return permissions
    
    def check_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has specific permission"""
        if not user.is_active:
            return False
        
        user_permissions = self.get_user_permissions(user)
        return permission in user_permissions
    
    def require_permission(self, permission: Permission):
        """Decorator to require specific permission"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Get user from context (implementation depends on framework)
                user = get_current_user()
                if not self.check_permission(user, permission):
                    raise PermissionError(f"Permission {permission.value} required")
                return func(*args, **kwargs)
            return wrapper
        return decorator
```

---

## Data Encryption

### Encryption at Rest

```python
"""
Data encryption implementation
File: src/security/encryption.py
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
import os

class EncryptionManager:
    """Manages data encryption and decryption"""
    
    def __init__(self, password: str = None):
        self.password = password or os.environ.get('ENCRYPTION_PASSWORD')
        if self.password:
            self.fernet = self._create_fernet_from_password(self.password)
    
    def _create_fernet_from_password(self, password: str) -> Fernet:
        """Create Fernet cipher from password"""
        password_bytes = password.encode()
        salt = b'salt_'  # In production, use a proper random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return Fernet(key)
    
    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using symmetric encryption"""
        if not hasattr(self, 'fernet'):
            raise ValueError("Encryption not initialized")
        return self.fernet.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using symmetric encryption"""
        if not hasattr(self, 'fernet'):
            raise ValueError("Encryption not initialized")
        return self.fernet.decrypt(encrypted_data)
    
    def encrypt_file(self, file_path: str, output_path: str = None):
        """Encrypt file and save to disk"""
        output_path = output_path or f"{file_path}.encrypted"
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.encrypt_data(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
    
    def decrypt_file(self, encrypted_path: str, output_path: str = None):
        """Decrypt file and save to disk"""
        output_path = output_path or encrypted_path.replace('.encrypted', '')
        
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.decrypt_data(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

class ModelEncryption:
    """Specialized encryption for ML models"""
    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
    
    def encrypt_model(self, model_path: str, encrypted_path: str = None):
        """Encrypt trained model file"""
        encrypted_path = encrypted_path or f"{model_path}.encrypted"
        self.encryption_manager.encrypt_file(model_path, encrypted_path)
    
    def decrypt_model(self, encrypted_path: str, model_path: str = None):
        """Decrypt model file for loading"""
        model_path = model_path or encrypted_path.replace('.encrypted', '')
        self.encryption_manager.decrypt_file(encrypted_path, model_path)
        return model_path
```

### Key Management

```python
"""
Secure key management implementation
File: src/security/key_management.py
"""

import os
import json
from typing import Dict, Optional
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import keyring

class KeyManager:
    """Manages encryption keys securely"""
    
    def __init__(self):
        self.key_store = {}
        self.key_directory = os.path.expanduser("~/.impressioncore/keys")
        os.makedirs(self.key_directory, mode=0o700, exist_ok=True)
    
    def generate_key_pair(self, key_name: str) -> tuple:
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        # Store keys securely
        self.store_private_key(key_name, private_key)
        self.store_public_key(key_name, public_key)
        
        return private_key, public_key
    
    def store_private_key(self, key_name: str, private_key):
        """Store private key securely using keyring"""
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        keyring.set_password("impressioncore", f"{key_name}_private", pem.decode())
    
    def store_public_key(self, key_name: str, public_key):
        """Store public key to file"""
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        key_file = os.path.join(self.key_directory, f"{key_name}_public.pem")
        with open(key_file, 'wb') as f:
            f.write(pem)
        
        # Set restrictive permissions
        os.chmod(key_file, 0o600)
    
    def load_private_key(self, key_name: str):
        """Load private key from secure storage"""
        pem_str = keyring.get_password("impressioncore", f"{key_name}_private")
        if not pem_str:
            return None
        
        return serialization.load_pem_private_key(
            pem_str.encode(),
            password=None
        )
    
    def load_public_key(self, key_name: str):
        """Load public key from file"""
        key_file = os.path.join(self.key_directory, f"{key_name}_public.pem")
        if not os.path.exists(key_file):
            return None
        
        with open(key_file, 'rb') as f:
            pem = f.read()
        
        return serialization.load_pem_public_key(pem)
    
    def rotate_keys(self, key_name: str):
        """Rotate encryption keys"""
        # Generate new key pair
        new_private, new_public = self.generate_key_pair(f"{key_name}_new")
        
        # Archive old keys
        old_private = self.load_private_key(key_name)
        old_public = self.load_public_key(key_name)
        
        if old_private and old_public:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.store_private_key(f"{key_name}_archived_{timestamp}", old_private)
            self.store_public_key(f"{key_name}_archived_{timestamp}", old_public)
        
        # Replace current keys
        self.store_private_key(key_name, new_private)
        self.store_public_key(key_name, new_public)
        
        return new_private, new_public
```

---

## Secure Communication

### TLS/SSL Configuration

```python
"""
Secure communication setup
File: src/security/communication.py
"""

import ssl
import socket
from pathlib import Path

class SecureCommunication:
    """Manages secure communication protocols"""
    
    def __init__(self):
        self.cert_directory = Path("~/.impressioncore/certs").expanduser()
        self.cert_directory.mkdir(mode=0o700, exist_ok=True)
    
    def create_ssl_context(self, 
                          cert_file: str = None, 
                          key_file: str = None, 
                          ca_file: str = None) -> ssl.SSLContext:
        """Create SSL context for secure connections"""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        
        # Configure security settings
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        if cert_file and key_file:
            context.load_cert_chain(cert_file, key_file)
        
        if ca_file:
            context.load_verify_locations(ca_file)
        
        return context
    
    def setup_server_ssl(self, app, cert_file: str, key_file: str):
        """Setup SSL for Flask server"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        
        # Security configurations
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        return context
    
    def generate_self_signed_cert(self, hostname: str = "localhost"):
        """Generate self-signed certificate for development"""
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ImpressionCore"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(hostname),
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Save certificate and key
        cert_file = self.cert_directory / "server.crt"
        key_file = self.cert_directory / "server.key"
        
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Set restrictive permissions
        os.chmod(cert_file, 0o644)
        os.chmod(key_file, 0o600)
        
        return str(cert_file), str(key_file)
```

---

## Input Validation and Sanitization

```python
"""
Input validation and sanitization
File: src/security/validation.py
"""

import re
import html
from typing import Any, Dict, List, Union
import bleach
from marshmallow import Schema, ValidationError

class InputValidator:
    """Validates and sanitizes user input"""
    
    def __init__(self):
        self.allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
        self.allowed_attributes = {}
    
    def sanitize_html(self, text: str) -> str:
        """Sanitize HTML input to prevent XSS"""
        return bleach.clean(
            text,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True
        )
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_username(self, username: str) -> bool:
        """Validate username format"""
        if not username or len(username) < 3 or len(username) > 50:
            return False
        
        # Only alphanumeric and specific special characters
        pattern = r'^[a-zA-Z0-9_.-]+$'
        return bool(re.match(pattern, username))
    
    def validate_password_strength(self, password: str) -> tuple[bool, List[str]]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove any path components
        filename = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    def validate_file_type(self, filename: str, allowed_types: List[str]) -> bool:
        """Validate file type by extension"""
        if not filename:
            return False
        
        ext = os.path.splitext(filename)[1].lower()
        return ext in allowed_types
    
    def validate_json_input(self, data: str, schema: Schema) -> tuple[bool, Union[Dict, str]]:
        """Validate JSON input against schema"""
        try:
            json_data = json.loads(data)
            result = schema.load(json_data)
            return True, result
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except ValidationError as e:
            return False, f"Validation error: {str(e)}"

class APIInputValidator:
    """Validates API input parameters"""
    
    def __init__(self):
        self.validator = InputValidator()
    
    def validate_model_name(self, model_name: str) -> bool:
        """Validate model name parameter"""
        if not model_name:
            return False
        
        # Only allow alphanumeric, hyphens, and underscores
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, model_name)) and len(model_name) <= 100
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key format"""
        if not api_key:
            return False
        
        # Check for proper format (adjust based on your API key format)
        pattern = r'^[a-zA-Z0-9]{32,128}$'
        return bool(re.match(pattern, api_key))
    
    def validate_request_size(self, content_length: int, max_size: int = 10485760) -> bool:
        """Validate request size (default 10MB)"""
        return content_length <= max_size
    
    def sanitize_text_input(self, text: str, max_length: int = 10000) -> str:
        """Sanitize text input for processing"""
        if not text:
            return ""
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove potentially dangerous characters
        text = html.escape(text)
        
        return text
```

---

## Security Monitoring and Logging

```python
"""
Security monitoring and logging
File: src/security/monitoring.py
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional
import json

class SecurityLogger:
    """Enhanced logging for security events"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s - %(extra)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_authentication_attempt(self, username: str, success: bool, ip_address: str):
        """Log authentication attempts"""
        extra = {
            'event_type': 'authentication',
            'username': username,
            'success': success,
            'ip_address': ip_address,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if success:
            self.logger.info(f"Successful login for {username}", extra=extra)
        else:
            self.logger.warning(f"Failed login attempt for {username}", extra=extra)
    
    def log_permission_check(self, username: str, permission: str, granted: bool):
        """Log permission checks"""
        extra = {
            'event_type': 'permission_check',
            'username': username,
            'permission': permission,
            'granted': granted,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Permission check: {permission} for {username}", extra=extra)
    
    def log_security_violation(self, event_type: str, details: Dict):
        """Log security violations"""
        extra = {
            'event_type': 'security_violation',
            'violation_type': event_type,
            'details': json.dumps(details),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.error(f"Security violation: {event_type}", extra=extra)

class ThreatDetector:
    """Detects potential security threats"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(deque)
        self.request_counts = defaultdict(deque)
        self.blocked_ips = set()
        self.security_logger = SecurityLogger()
    
    def check_brute_force(self, ip_address: str, username: str) -> bool:
        """Check for brute force attacks"""
        key = f"{ip_address}:{username}"
        now = time.time()
        
        # Clean old attempts (older than 15 minutes)
        while (self.failed_attempts[key] and 
               now - self.failed_attempts[key][0] > 900):
            self.failed_attempts[key].popleft()
        
        # Check if too many attempts
        if len(self.failed_attempts[key]) >= 5:
            self.blocked_ips.add(ip_address)
            self.security_logger.log_security_violation(
                'brute_force',
                {'ip_address': ip_address, 'username': username}
            )
            return True
        
        return False
    
    def record_failed_attempt(self, ip_address: str, username: str):
        """Record failed authentication attempt"""
        key = f"{ip_address}:{username}"
        self.failed_attempts[key].append(time.time())
    
    def check_rate_limit(self, ip_address: str, limit: int = 100, window: int = 60) -> bool:
        """Check for rate limiting violations"""
        now = time.time()
        
        # Clean old requests
        while (self.request_counts[ip_address] and 
               now - self.request_counts[ip_address][0] > window):
            self.request_counts[ip_address].popleft()
        
        # Check rate limit
        if len(self.request_counts[ip_address]) >= limit:
            self.security_logger.log_security_violation(
                'rate_limit_exceeded',
                {'ip_address': ip_address, 'requests': len(self.request_counts[ip_address])}
            )
            return True
        
        self.request_counts[ip_address].append(now)
        return False
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips
    
    def unblock_ip(self, ip_address: str):
        """Unblock IP address"""
        self.blocked_ips.discard(ip_address)
    
    def scan_for_suspicious_patterns(self, log_entries: List[Dict]):
        """Scan logs for suspicious patterns"""
        # Implement pattern detection logic
        pass

class SecurityMetrics:
    """Collect and analyze security metrics"""
    
    def __init__(self):
        self.metrics = {
            'authentication_attempts': 0,
            'failed_authentications': 0,
            'blocked_ips': 0,
            'api_requests': 0,
            'security_violations': 0
        }
        self.start_time = datetime.utcnow()
    
    def increment_metric(self, metric_name: str, value: int = 1):
        """Increment security metric"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    def get_metrics(self) -> Dict:
        """Get current security metrics"""
        runtime = datetime.utcnow() - self.start_time
        return {
            **self.metrics,
            'uptime_seconds': runtime.total_seconds(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        for key in self.metrics:
            self.metrics[key] = 0
        self.start_time = datetime.utcnow()
```

---

## API Security

```python
"""
API security implementation
File: src/security/api_security.py
"""

from functools import wraps
from flask import request, jsonify, g
import time
import hashlib
import hmac

class APISecurityManager:
    """Manages API security features"""
    
    def __init__(self):
        self.threat_detector = ThreatDetector()
        self.rate_limits = {
            'default': (100, 3600),  # 100 requests per hour
            'inference': (1000, 3600),  # 1000 inferences per hour
            'training': (10, 86400),  # 10 training sessions per day
        }
    
    def require_api_key(self, f):
        """Decorator to require valid API key"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            # Validate API key
            if not self.validate_api_key(api_key):
                return jsonify({'error': 'Invalid API key'}), 401
            
            # Store user info in context
            g.user = self.get_user_from_api_key(api_key)
            
            return f(*args, **kwargs)
        return decorated_function
    
    def rate_limit(self, endpoint_type: str = 'default'):
        """Decorator for rate limiting"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = request.remote_addr
                user_id = getattr(g, 'user', {}).get('id', client_ip)
                
                # Check rate limit
                limit, window = self.rate_limits.get(endpoint_type, (100, 3600))
                if self.threat_detector.check_rate_limit(f"{user_id}:{endpoint_type}", limit, window):
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def validate_signature(self, f):
        """Decorator to validate request signature"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            signature = request.headers.get('X-Signature')
            if not signature:
                return jsonify({'error': 'Signature required'}), 401
            
            # Calculate expected signature
            secret = self.get_webhook_secret()
            payload = request.get_data()
            expected = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, f"sha256={expected}"):
                return jsonify({'error': 'Invalid signature'}), 401
            
            return f(*args, **kwargs)
        return decorated_function
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        # Implement API key validation logic
        # This could involve database lookup, token verification, etc.
        return True  # Placeholder
    
    def get_user_from_api_key(self, api_key: str) -> Dict:
        """Get user information from API key"""
        # Implement user lookup logic
        return {'id': 'user123', 'username': 'testuser'}  # Placeholder
    
    def get_webhook_secret(self) -> str:
        """Get webhook secret for signature validation"""
        return os.environ.get('WEBHOOK_SECRET', 'default_secret')

# Usage examples in Flask routes
"""
@app.route('/api/v1/inference', methods=['POST'])
@api_security.require_api_key
@api_security.rate_limit('inference')
def inference():
    # Process inference request
    pass

@app.route('/webhook/github', methods=['POST'])
@api_security.validate_signature
def github_webhook():
    # Process GitHub webhook
    pass
"""
```

---

## Security Best Practices

### Secure Development Guidelines

1. **Input Validation**
   - Always validate and sanitize user input
   - Use parameterized queries to prevent SQL injection
   - Implement proper input length limits
   - Validate file types and sizes for uploads

2. **Authentication & Authorization**
   - Implement strong password policies
   - Use multi-factor authentication where possible
   - Apply principle of least privilege
   - Regularly rotate credentials and keys

3. **Data Protection**
   - Encrypt sensitive data at rest and in transit
   - Use secure key management practices
   - Implement proper data backup and recovery
   - Apply data retention policies

4. **Monitoring & Logging**
   - Log all security-relevant events
   - Monitor for suspicious activities
   - Implement alerting for security violations
   - Regularly review security logs

5. **System Security**
   - Keep all dependencies up to date
   - Apply security patches promptly
   - Use secure communication protocols
   - Implement proper error handling

### Security Configuration

```python
"""
Security configuration
File: src/security/config.py
"""

class SecurityConfig:
    """Security configuration settings"""
    
    # Authentication settings
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Session settings
    SESSION_TIMEOUT = 3600  # 1 hour
    SESSION_SECURE = True
    SESSION_HTTPONLY = True
    SESSION_SAMESITE = 'Strict'
    
    # Rate limiting
    RATE_LIMIT_DEFAULT = (100, 3600)  # 100 requests per hour
    RATE_LIMIT_LOGIN = (5, 900)  # 5 login attempts per 15 minutes
    
    # Encryption
    ENCRYPTION_ALGORITHM = 'AES-256-GCM'
    KEY_DERIVATION_ITERATIONS = 100000
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'"
    }
    
    # File upload restrictions
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.wav', '.mp3'}
    UPLOAD_FOLDER_PERMISSIONS = 0o755
    
    # API security
    API_KEY_LENGTH = 32
    API_RATE_LIMIT = (1000, 3600)  # 1000 requests per hour
    WEBHOOK_TIMEOUT = 30  # seconds
    
    @classmethod
    def validate_config(cls):
        """Validate security configuration"""
        assert cls.PASSWORD_MIN_LENGTH >= 8, "Password minimum length too short"
        assert cls.SESSION_TIMEOUT > 0, "Session timeout must be positive"
        assert cls.MAX_FILE_SIZE > 0, "Max file size must be positive"
```

---

## Compliance and Standards

### GDPR Compliance

```python
"""
GDPR compliance implementation
File: src/security/gdpr.py
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

class GDPRManager:
    """Manages GDPR compliance features"""
    
    def __init__(self):
        self.data_retention_periods = {
            'user_data': timedelta(days=2555),  # 7 years
            'log_data': timedelta(days=90),
            'model_data': timedelta(days=1825),  # 5 years
            'training_data': timedelta(days=3650),  # 10 years
        }
    
    def record_consent(self, user_id: str, consent_type: str, granted: bool):
        """Record user consent"""
        consent_record = {
            'user_id': user_id,
            'consent_type': consent_type,
            'granted': granted,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr if 'request' in globals() else None
        }
        
        # Store consent record
        self.store_consent_record(consent_record)
    
    def get_user_data(self, user_id: str) -> Dict:
        """Get all data for a user (data portability)"""
        user_data = {
            'personal_info': self.get_personal_info(user_id),
            'usage_data': self.get_usage_data(user_id),
            'model_data': self.get_model_data(user_id),
            'consent_records': self.get_consent_records(user_id),
            'export_date': datetime.utcnow().isoformat()
        }
        
        return user_data
    
    def delete_user_data(self, user_id: str, data_types: List[str] = None):
        """Delete user data (right to erasure)"""
        if not data_types:
            data_types = ['personal_info', 'usage_data', 'model_data']
        
        deletion_log = {
            'user_id': user_id,
            'data_types': data_types,
            'deletion_date': datetime.utcnow().isoformat(),
            'requested_by': self.get_current_user()
        }
        
        for data_type in data_types:
            self.delete_data_by_type(user_id, data_type)
        
        # Log deletion for compliance
        self.log_data_deletion(deletion_log)
    
    def anonymize_user_data(self, user_id: str):
        """Anonymize user data while preserving utility"""
        # Replace personal identifiers with anonymous IDs
        anonymous_id = self.generate_anonymous_id()
        
        # Update records to use anonymous ID
        self.replace_user_id(user_id, anonymous_id)
        
        # Remove direct personal identifiers
        self.remove_personal_identifiers(anonymous_id)
    
    def check_data_retention(self):
        """Check and enforce data retention policies"""
        current_time = datetime.utcnow()
        
        for data_type, retention_period in self.data_retention_periods.items():
            cutoff_date = current_time - retention_period
            expired_data = self.find_expired_data(data_type, cutoff_date)
            
            for data_record in expired_data:
                self.delete_expired_data(data_record)
                
    def generate_privacy_report(self) -> Dict:
        """Generate privacy compliance report"""
        return {
            'total_users': self.count_total_users(),
            'active_consents': self.count_active_consents(),
            'data_retention_status': self.check_retention_compliance(),
            'deletion_requests': self.count_deletion_requests(),
            'data_breaches': self.count_data_breaches(),
            'report_date': datetime.utcnow().isoformat()
        }
```

### SOC 2 Compliance

```python
"""
SOC 2 compliance implementation
File: src/security/soc2.py
"""

class SOC2Manager:
    """Manages SOC 2 compliance controls"""
    
    def __init__(self):
        self.control_activities = {
            'CC6.1': 'Logical and physical access controls',
            'CC6.2': 'Authentication and authorization',
            'CC6.3': 'System access controls',
            'CC7.1': 'Change management procedures',
            'CC8.1': 'System monitoring and detection'
        }
    
    def implement_access_controls(self):
        """Implement CC6.1 - Access Controls"""
        # Network segmentation
        # Firewall configurations
        # VPN access requirements
        # Physical security measures
        pass
    
    def implement_authentication_controls(self):
        """Implement CC6.2 - Authentication"""
        # Multi-factor authentication
        # Password complexity requirements
        # Account lockout policies
        # Session management
        pass
    
    def implement_monitoring_controls(self):
        """Implement CC8.1 - System Monitoring"""
        # Log aggregation and analysis
        # Intrusion detection systems
        # Vulnerability assessments
        # Incident response procedures
        pass
    
    def generate_compliance_report(self) -> Dict:
        """Generate SOC 2 compliance report"""
        return {
            'control_implementation': self.assess_control_implementation(),
            'audit_findings': self.get_audit_findings(),
            'remediation_status': self.get_remediation_status(),
            'compliance_score': self.calculate_compliance_score(),
            'report_date': datetime.utcnow().isoformat()
        }
```

---

## Document Metadata

**Version Control:**

- **Version**: 2.0.0
- **Last Updated**: 2025-06-03 16:00:00
- **Next Review**: 2025-09-03
- **Authors**: GitHub Copilot
- **Status**: Active

**Related Documentation:**

- [API Reference](../api/complete_api_reference_v2.md)
- [Deployment Guide](../user/deployment_guide.md)
- [System Administration Guide](../reference/system_administration.md)
- [Compliance Documentation](../reference/compliance_guide.md)

**Implementation Status:**

- ✅ Authentication and Authorization
- ✅ Data Encryption
- ✅ Secure Communication
- ✅ Input Validation
- ✅ Security Monitoring
- ✅ API Security
- ✅ Compliance Framework

---

*This security implementation guide provides comprehensive security measures for ImpressionCore. Regular security audits and updates are recommended to maintain effectiveness against evolving threats.*
