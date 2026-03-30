# ImpressionCore Digital Identity Management Module
# Phase 8A: Security Infrastructure Foundation - Week 2
# Digital Identity Management Core Implementation

"""
ImpressionCore Digital Identity Management System

This module provides comprehensive digital identity management with quantum-resistant
cryptography, secure personal data storage, and privacy-first data handling.
Optimized for GTX 1050 Ti hardware constraints.

Components:
- IdentityManager: Core identity management orchestrator
- CryptographicCore: Quantum-resistant cryptography implementation
- PersonalDataVault: Secure encrypted personal data storage
- VerificationSystem: Identity verification and proof generation

Hardware Optimization:
- Memory usage target: <150MB total for all identity components
- Lazy loading of cryptographic modules for memory efficiency
- Hardware-accelerated encryption when available on GTX 1050 Ti
"""

from .identity_manager import IdentityManager, IdentityProfile, IdentityError
from .cryptographic_core import CryptographicCore, KeyPair, QuantumResistantError
from .personal_data_vault import PersonalDataVault, VaultEntry, VaultError
from .verification_system import VerificationSystem, VerificationProof, VerificationError

__all__ = [
    # Core identity management
    'IdentityManager',
    'IdentityProfile', 
    'IdentityError',
    
    # Cryptographic components
    'CryptographicCore',
    'KeyPair',
    'QuantumResistantError',
    
    # Data vault
    'PersonalDataVault',
    'VaultEntry',
    'VaultError',
    
    # Verification system
    'VerificationSystem',
    'VerificationProof',
    'VerificationError'
]

# Identity module configuration optimized for GTX 1050 Ti
IDENTITY_CONFIG = {
    'memory_limits': {
        'total_identity_memory': 150 * 1024 * 1024,  # 150MB total limit
        'cryptographic_core': 50 * 1024 * 1024,     # 50MB for crypto operations
        'data_vault': 60 * 1024 * 1024,             # 60MB for encrypted storage
        'verification_system': 40 * 1024 * 1024     # 40MB for verification
    },
    'performance': {
        'enable_gpu_acceleration': True,             # Use GTX 1050 Ti when available
        'lazy_loading': True,                        # Load components on demand
        'cache_expiry': 300,                         # 5 minute cache expiry
        'batch_size': 32                             # Optimal batch size for GTX 1050 Ti
    },
    'security': {
        'quantum_resistant': True,                   # Enable post-quantum cryptography
        'key_rotation_interval': 86400,              # 24 hours key rotation
        'audit_logging': True,                       # Enable comprehensive audit logs
        'zero_knowledge_proofs': True                # Enable ZK proof generation
    }
}
