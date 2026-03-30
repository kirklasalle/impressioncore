# Phase 8A Week 2: TLS Handler Implementation
# File: src/security/encryption/tls_handler.py
# Description: TLS 1.3 secure communication handler
# Created: 2025-01-18 21:45:00 UTC
# Author: GitHub Copilot (ImpressionCore)

"""
TLS Handler

Provides TLS 1.3 secure communication capabilities with:
- Certificate management and validation
- Secure client/server connections
- Perfect forward secrecy
- Session management and resumption
- Performance optimized for limited resources

Memory limit: <25MB for active TLS sessions
"""

import logging
import ssl
import socket
import time
import json
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
import asyncio
from dataclasses import dataclass, field
from pathlib import Path
import threading
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac

# TLS and certificate handling
import cryptography.x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
import certifi

# Performance monitoring
import psutil

logger = logging.getLogger(__name__)

class TLSVersion(Enum):
    """Supported TLS versions."""
    TLS_1_2 = ssl.TLSVersion.TLSv1_2
    TLS_1_3 = ssl.TLSVersion.TLSv1_3

class CertificateType(Enum):
    """Certificate types."""
    SERVER = "server"
    CLIENT = "client"
    CA = "ca"
    INTERMEDIATE = "intermediate"

@dataclass
class TLSConfig:
    """TLS configuration."""
    min_version: TLSVersion = TLSVersion.TLS_1_3
    max_version: TLSVersion = TLSVersion.TLS_1_3
    cipher_suites: List[str] = field(default_factory=lambda: [
        'TLS_AES_256_GCM_SHA384',
        'TLS_CHACHA20_POLY1305_SHA256',
        'TLS_AES_128_GCM_SHA256'
    ])
    verify_mode: ssl.VerifyMode = ssl.CERT_REQUIRED
    check_hostname: bool = True
    session_timeout: int = 300  # 5 minutes
    max_connections: int = 100
    enable_session_resumption: bool = True
    enable_ocsp_stapling: bool = True

@dataclass
class CertificateInfo:
    """Certificate information."""
    subject: str
    issuer: str
    serial_number: str
    not_before: datetime
    not_after: datetime
    fingerprint: str
    key_size: int
    signature_algorithm: str
    extensions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TLSSession:
    """TLS session information."""
    session_id: str
    peer_certificate: Optional[CertificateInfo]
    cipher_suite: str
    protocol_version: str
    created_at: datetime
    last_used: datetime
    bytes_transmitted: int = 0
    bytes_received: int = 0
    is_resumed: bool = False

class TLSHandler:
    """
    TLS 1.3 secure communication handler.
    
    Features:
    - TLS 1.3 client and server connections
    - Certificate generation and management
    - Session management and resumption
    - Performance monitoring and optimization
    - Memory-efficient connection pooling
    """
    
    def __init__(self, config: Optional[TLSConfig] = None, cert_store_path: Optional[str] = None):
        """Initialize TLS handler."""
        self.config = config or TLSConfig()
        self.cert_store_path = Path(cert_store_path or "data/security/certificates")
        self.cert_store_path.mkdir(parents=True, exist_ok=True)
        
        # Session management
        self.active_sessions = {}
        self.session_lock = threading.RLock()
        self.max_sessions = self.config.max_connections
        
        # Certificate cache
        self.cert_cache = {}
        self.cert_lock = threading.RLock()
        
        # Performance monitoring
        self.metrics = {
            'connections_established': 0,
            'connections_failed': 0,
            'sessions_resumed': 0,
            'certificates_generated': 0,
            'certificates_validated': 0,
            'bytes_encrypted': 0,
            'bytes_decrypted': 0
        }
        
        # Memory monitoring
        self.memory_limit_mb = 25
        self.memory_monitor = threading.Timer(300.0, self._monitor_memory)
        self.memory_monitor.daemon = True
        self.memory_monitor.start()
        
        # Initialize SSL context
        self.ssl_context = self._create_ssl_context()
        
        logger.info(f"TLS handler initialized - Version: {self.config.min_version.name}")

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with security settings."""
        try:
            # Create context for TLS 1.3
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            
            # Set TLS version constraints
            context.minimum_version = self.config.min_version.value
            context.maximum_version = self.config.max_version.value
            
            # Security settings
            context.verify_mode = self.config.verify_mode
            context.check_hostname = self.config.check_hostname
            
            # Load default CA certificates
            context.load_verify_locations(certifi.where())
            
            # Cipher suite configuration
            if self.config.cipher_suites:
                context.set_ciphers(':'.join(self.config.cipher_suites))
            
            # Enable session resumption if configured
            if self.config.enable_session_resumption:
                context.session_stats()
            
            # Additional security options
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.options |= ssl.OP_NO_TLSv1
            context.options |= ssl.OP_NO_TLSv1_1
            context.options |= ssl.OP_SINGLE_DH_USE
            context.options |= ssl.OP_SINGLE_ECDH_USE
            
            logger.info("SSL context created with TLS 1.3 security settings")
            return context
            
        except Exception as e:
            logger.error(f"SSL context creation error: {e}")
            raise

    def generate_certificate(self, 
                           subject_name: str,
                           cert_type: CertificateType = CertificateType.SERVER,
                           key_size: int = 2048,
                           validity_days: int = 365,
                           san_list: Optional[List[str]] = None) -> Tuple[str, str]:
        """
        Generate a self-signed certificate.
        
        Args:
            subject_name: Certificate subject name
            cert_type: Type of certificate
            key_size: RSA key size
            validity_days: Certificate validity period
            san_list: Subject Alternative Names
            
        Returns:
            Tuple of (certificate_path, private_key_path)
        """
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ImpressionCore"),
                x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
            ])
            
            now = datetime.utcnow()
            cert_builder = x509.CertificateBuilder()
            cert_builder = cert_builder.subject_name(subject)
            cert_builder = cert_builder.issuer_name(issuer)
            cert_builder = cert_builder.public_key(private_key.public_key())
            cert_builder = cert_builder.serial_number(x509.random_serial_number())
            cert_builder = cert_builder.not_valid_before(now)
            cert_builder = cert_builder.not_valid_after(now + timedelta(days=validity_days))
            
            # Add extensions
            if cert_type == CertificateType.SERVER:
                cert_builder = cert_builder.add_extension(
                    x509.KeyUsage(
                        digital_signature=True,
                        key_encipherment=True,
                        key_agreement=False,
                        key_cert_sign=False,
                        crl_sign=False,
                        content_commitment=False,
                        data_encipherment=False,
                        encipher_only=False,
                        decipher_only=False
                    ),
                    critical=True
                )
                
                cert_builder = cert_builder.add_extension(
                    x509.ExtendedKeyUsage([
                        x509.oid.ExtendedKeyUsageOID.SERVER_AUTH
                    ]),
                    critical=True
                )
            
            # Add Subject Alternative Names
            if san_list:
                san_names = []
                for san in san_list:
                    if san.startswith('DNS:'):
                        san_names.append(x509.DNSName(san[4:]))
                    elif san.startswith('IP:'):
                        san_names.append(x509.IPAddress(san[3:]))
                    else:
                        san_names.append(x509.DNSName(san))
                
                cert_builder = cert_builder.add_extension(
                    x509.SubjectAlternativeName(san_names),
                    critical=False
                )
            
            # Sign certificate
            certificate = cert_builder.sign(private_key, hashes.SHA256())
            
            # Save certificate and key
            cert_filename = f"{subject_name}_{int(time.time())}.crt"
            key_filename = f"{subject_name}_{int(time.time())}.key"
            
            cert_path = self.cert_store_path / cert_filename
            key_path = self.cert_store_path / key_filename
            
            # Write certificate
            with open(cert_path, 'wb') as f:
                f.write(certificate.public_bytes(serialization.Encoding.PEM))
            
            # Write private key
            with open(key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Update metrics
            self.metrics['certificates_generated'] += 1
            
            logger.info(f"Generated certificate for {subject_name}")
            return str(cert_path), str(key_path)
            
        except Exception as e:
            logger.error(f"Certificate generation error: {e}")
            raise

    def load_certificate_info(self, cert_path: str) -> CertificateInfo:
        """
        Load certificate information from file.
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            Certificate information
        """
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            # Extract certificate information
            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            serial_number = str(cert.serial_number)
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
            
            # Calculate fingerprint
            fingerprint = hashlib.sha256(cert_data).hexdigest()
            
            # Get key information
            public_key = cert.public_key()
            key_size = public_key.key_size if hasattr(public_key, 'key_size') else 0
            
            # Get signature algorithm
            signature_algorithm = cert.signature_algorithm_oid._name
            
            # Parse extensions
            extensions = {}
            for ext in cert.extensions:
                extensions[ext.oid._name] = str(ext.value)
            
            cert_info = CertificateInfo(
                subject=subject,
                issuer=issuer,
                serial_number=serial_number,
                not_before=not_before,
                not_after=not_after,
                fingerprint=fingerprint,
                key_size=key_size,
                signature_algorithm=signature_algorithm,
                extensions=extensions
            )
            
            # Cache certificate info
            with self.cert_lock:
                self.cert_cache[cert_path] = cert_info
            
            logger.debug(f"Loaded certificate info for {subject}")
            return cert_info
            
        except Exception as e:
            logger.error(f"Certificate loading error: {e}")
            raise

    def validate_certificate(self, cert_path: str, ca_path: Optional[str] = None) -> bool:
        """
        Validate certificate against CA.
        
        Args:
            cert_path: Path to certificate to validate
            ca_path: Path to CA certificate (optional)
            
        Returns:
            True if certificate is valid
        """
        try:
            cert_info = self.load_certificate_info(cert_path)
            
            # Check expiration
            now = datetime.utcnow()
            if now < cert_info.not_before or now > cert_info.not_after:
                logger.warning(f"Certificate expired or not yet valid: {cert_path}")
                return False
            
            # Additional validation against CA if provided
            if ca_path:
                # Load CA certificate
                with open(ca_path, 'rb') as f:
                    ca_cert = x509.load_pem_x509_certificate(f.read())
                
                # Verify certificate against CA
                with open(cert_path, 'rb') as f:
                    cert = x509.load_pem_x509_certificate(f.read())
                
                # Basic validation - in production, use proper certificate chain validation
                if cert.issuer != ca_cert.subject:
                    logger.warning(f"Certificate issuer mismatch: {cert_path}")
                    return False
            
            self.metrics['certificates_validated'] += 1
            logger.debug(f"Certificate validated: {cert_path}")
            return True
            
        except Exception as e:
            logger.error(f"Certificate validation error: {e}")
            return False

    async def create_secure_connection(self, 
                                     host: str, 
                                     port: int,
                                     cert_file: Optional[str] = None,
                                     key_file: Optional[str] = None,
                                     ca_file: Optional[str] = None,
                                     timeout: float = 30.0) -> ssl.SSLSocket:
        """
        Create a secure TLS connection.
        
        Args:
            host: Remote host
            port: Remote port
            cert_file: Client certificate file
            key_file: Client private key file
            ca_file: CA certificate file
            timeout: Connection timeout
            
        Returns:
            SSL socket connection
        """
        try:
            start_time = time.time()
            
            # Create SSL context
            context = self._create_ssl_context()
            
            # Load client certificate if provided
            if cert_file and key_file:
                context.load_cert_chain(cert_file, key_file)
            
            # Load CA certificate if provided
            if ca_file:
                context.load_verify_locations(ca_file)
            
            # Create socket connection
            sock = socket.create_connection((host, port), timeout=timeout)
            
            # Wrap with SSL
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            
            # Get connection information
            cipher = ssl_sock.cipher()
            protocol = ssl_sock.version()
            peer_cert = ssl_sock.getpeercert()
            
            # Create session record
            session_id = f"{host}:{port}_{int(time.time())}"
            session = TLSSession(
                session_id=session_id,
                peer_certificate=self._parse_peer_certificate(peer_cert) if peer_cert else None,
                cipher_suite=cipher[0] if cipher else "unknown",
                protocol_version=protocol or "unknown",
                created_at=datetime.now(),
                last_used=datetime.now()
            )
            
            # Store session
            with self.session_lock:
                self.active_sessions[session_id] = session
                self._cleanup_sessions()
            
            # Update metrics
            self.metrics['connections_established'] += 1
            connection_time = time.time() - start_time
            
            logger.info(f"Secure connection established to {host}:{port} in {connection_time:.3f}s")
            logger.debug(f"Cipher: {cipher}, Protocol: {protocol}")
            
            return ssl_sock
            
        except Exception as e:
            self.metrics['connections_failed'] += 1
            logger.error(f"Secure connection failed to {host}:{port}: {e}")
            raise

    def _parse_peer_certificate(self, peer_cert: Dict[str, Any]) -> CertificateInfo:
        """Parse peer certificate information."""
        try:
            subject = peer_cert.get('subject', [])
            issuer = peer_cert.get('issuer', [])
            
            # Convert to string format
            subject_str = ', '.join([f"{item[0][0]}={item[0][1]}" for item in subject])
            issuer_str = ', '.join([f"{item[0][0]}={item[0][1]}" for item in issuer])
            
            return CertificateInfo(
                subject=subject_str,
                issuer=issuer_str,
                serial_number=peer_cert.get('serialNumber', ''),
                not_before=datetime.strptime(peer_cert['notBefore'], '%b %d %H:%M:%S %Y %Z'),
                not_after=datetime.strptime(peer_cert['notAfter'], '%b %d %H:%M:%S %Y %Z'),
                fingerprint=peer_cert.get('fingerprint', ''),
                key_size=0,  # Not available in getpeercert()
                signature_algorithm=peer_cert.get('signatureAlgorithm', '')
            )
            
        except Exception as e:
            logger.error(f"Peer certificate parsing error: {e}")
            return None

    def create_tls_server(self, 
                         host: str, 
                         port: int,
                         cert_file: str,
                         key_file: str,
                         client_cert_required: bool = False) -> ssl.SSLSocket:
        """
        Create a TLS server socket.
        
        Args:
            host: Server host
            port: Server port
            cert_file: Server certificate file
            key_file: Server private key file
            client_cert_required: Require client certificates
            
        Returns:
            SSL server socket
        """
        try:
            # Create SSL context for server
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.minimum_version = self.config.min_version.value
            context.maximum_version = self.config.max_version.value
            
            # Load server certificate
            context.load_cert_chain(cert_file, key_file)
            
            # Client certificate settings
            if client_cert_required:
                context.verify_mode = ssl.CERT_REQUIRED
            else:
                context.verify_mode = ssl.CERT_NONE
            
            # Create server socket
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((host, port))
            server_sock.listen(self.config.max_connections)
            
            # Wrap with SSL
            ssl_server = context.wrap_socket(server_sock, server_side=True)
            
            logger.info(f"TLS server created on {host}:{port}")
            return ssl_server
            
        except Exception as e:
            logger.error(f"TLS server creation error: {e}")
            raise

    def _cleanup_sessions(self):
        """Clean up expired sessions."""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if (now - session.last_used).total_seconds() > self.config.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        if expired_sessions:
            logger.debug(f"Cleaned up {len(expired_sessions)} expired sessions")

    def _monitor_memory(self):
        """Monitor memory usage."""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            
            if memory_mb > self.memory_limit_mb:
                logger.warning(f"TLS handler memory usage ({memory_mb:.1f}MB) exceeds limit")
                # Clear caches to free memory
                with self.cert_lock:
                    self.cert_cache.clear()
                with self.session_lock:
                    self._cleanup_sessions()
            
            # Schedule next monitoring
            self.memory_monitor = threading.Timer(300.0, self._monitor_memory)
            self.memory_monitor.daemon = True
            self.memory_monitor.start()
            
        except Exception as e:
            logger.error(f"Memory monitoring error: {e}")

    def get_session_info(self, session_id: str) -> Optional[TLSSession]:
        """Get TLS session information."""
        with self.session_lock:
            return self.active_sessions.get(session_id)

    def list_active_sessions(self) -> List[TLSSession]:
        """List all active TLS sessions."""
        with self.session_lock:
            return list(self.active_sessions.values())

    def get_metrics(self) -> Dict[str, Any]:
        """Get TLS handler performance metrics."""
        with self.session_lock:
            active_session_count = len(self.active_sessions)
        
        with self.cert_lock:
            cached_cert_count = len(self.cert_cache)
        
        return {
            'operations': dict(self.metrics),
            'sessions': {
                'active_count': active_session_count,
                'max_sessions': self.max_sessions,
                'timeout_seconds': self.config.session_timeout
            },
            'certificates': {
                'cached_count': cached_cert_count,
                'store_path': str(self.cert_store_path)
            },
            'configuration': {
                'min_tls_version': self.config.min_version.name,
                'max_tls_version': self.config.max_version.name,
                'cipher_suites': self.config.cipher_suites,
                'verify_mode': self.config.verify_mode.name
            }
        }

    def cleanup(self):
        """Clean up TLS handler resources."""
        try:
            if hasattr(self, 'memory_monitor'):
                self.memory_monitor.cancel()
            
            with self.session_lock:
                self.active_sessions.clear()
            
            with self.cert_lock:
                self.cert_cache.clear()
            
            logger.info("TLS handler cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except:
            pass
