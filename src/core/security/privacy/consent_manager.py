# Phase 8A Week 2: Consent Manager
# File: src/security/privacy/consent_manager.py
# Description: User consent tracking and enforcement system
# Created: 2025-01-18 22:10:00 UTC
# Author: GitHub Copilot (ImpressionCore)

"""
Consent Manager System

Implements comprehensive user consent management for GDPR and CCPA compliance,
including consent collection, storage, validation, and enforcement. Supports
granular consent types and automated consent lifecycle management.

Features:
- Multi-level consent granularity (purpose-specific)
- Consent versioning and history tracking
- Automated consent expiration and renewal
- Legal basis tracking for data processing
- Consent withdrawal and right to be forgotten
- Audit trail for compliance reporting

Memory Target: <20MB for active consents and processing
"""

import logging
import asyncio
import sqlite3
import hashlib
import json
import time
from typing import Dict, List, Set, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta
import threading
import uuid

logger = logging.getLogger(__name__)

class ConsentType(Enum):
    """Types of consent that can be requested."""
    ESSENTIAL = "essential"  # Required for service operation
    FUNCTIONAL = "functional"  # Enhance user experience
    ANALYTICS = "analytics"  # Usage analytics and improvements
    MARKETING = "marketing"  # Marketing communications
    PERSONALIZATION = "personalization"  # Personalized content
    THIRD_PARTY = "third_party"  # Third-party integrations
    BIOMETRIC = "biometric"  # Biometric data processing
    AI_TRAINING = "ai_training"  # AI model training data

class ConsentStatus(Enum):
    """Status of consent."""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"

class LegalBasis(Enum):
    """Legal basis for data processing under GDPR."""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"

@dataclass
class ConsentRecord:
    """Represents a consent record."""
    consent_id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    legal_basis: LegalBasis
    purpose: str
    data_categories: List[str]
    retention_period_days: int
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    version: str = "1.0"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.consent_id is None:
            self.consent_id = str(uuid.uuid4())
    
    def is_valid(self) -> bool:
        """Check if consent is currently valid."""
        if self.status != ConsentStatus.GRANTED:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def is_expired(self) -> bool:
        """Check if consent has expired."""
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['consent_type'] = self.consent_type.value
        data['status'] = self.status.value
        data['legal_basis'] = self.legal_basis.value
        if self.granted_at:
            data['granted_at'] = self.granted_at.isoformat()
        if self.withdrawn_at:
            data['withdrawn_at'] = self.withdrawn_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data

@dataclass
class ConsentRequest:
    """Represents a consent request."""
    user_id: str
    consent_types: List[ConsentType]
    purposes: Dict[ConsentType, str]
    retention_periods: Dict[ConsentType, int]
    legal_bases: Dict[ConsentType, LegalBasis]
    data_categories: Dict[ConsentType, List[str]]
    request_context: Dict[str, Any]
    expires_in_days: int = 365
    
    def __post_init__(self):
        if self.request_context is None:
            self.request_context = {}

@dataclass
class ConsentWithdrawalRequest:
    """Represents a consent withdrawal request."""
    user_id: str
    consent_types: List[ConsentType]
    withdrawal_reason: str
    delete_data: bool = False
    effective_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.effective_date is None:
            self.effective_date = datetime.utcnow()

class ConsentManager:
    """
    Comprehensive consent management system for privacy compliance.
    
    Manages user consent lifecycle, enforcement, and compliance reporting
    with support for GDPR and CCPA requirements.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize consent manager."""
        self.db_path = db_path or "privacy_consent.db"
        self.memory_limit_mb = 20
        self.consent_cache = {}  # Cache for active consents
        self.cache_size = 2000
        self.cleanup_interval = 3600  # 1 hour
        self.lock = threading.RLock()
        
        # Performance tracking
        self.stats = {
            'consent_requests': 0,
            'consents_granted': 0,
            'consents_denied': 0,
            'consents_withdrawn': 0,
            'consents_expired': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'last_cleanup': time.time()
        }
        
        # Initialize database
        self._init_database()
        self._load_default_purposes()
        
        logger.info("Consent manager initialized")
    
    def _init_database(self):
        """Initialize SQLite database for consent management."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Consent records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS consent_records (
                        consent_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        consent_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        legal_basis TEXT NOT NULL,
                        purpose TEXT NOT NULL,
                        data_categories TEXT NOT NULL,
                        retention_period_days INTEGER NOT NULL,
                        granted_at TEXT,
                        withdrawn_at TEXT,
                        expires_at TEXT,
                        version TEXT DEFAULT '1.0',
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Consent history table for audit trail
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS consent_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        consent_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        old_status TEXT,
                        new_status TEXT,
                        reason TEXT,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                ''')
                
                # Consent purposes template table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS consent_purposes (
                        purpose_id TEXT PRIMARY KEY,
                        consent_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        legal_basis TEXT NOT NULL,
                        data_categories TEXT NOT NULL,
                        retention_days INTEGER NOT NULL,
                        is_required BOOLEAN DEFAULT 0,
                        version TEXT DEFAULT '1.0',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Data processing activities log
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processing_activities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        consent_id TEXT NOT NULL,
                        activity_type TEXT NOT NULL,
                        data_processed TEXT,
                        purpose TEXT NOT NULL,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_consent_user ON consent_records(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_consent_type ON consent_records(consent_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_consent_status ON consent_records(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_consent_expires ON consent_records(expires_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_user ON consent_history(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_consent ON consent_history(consent_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_user ON processing_activities(user_id)')
                
                conn.commit()
                logger.info("Consent manager database initialized")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _load_default_purposes(self):
        """Load default consent purposes and templates."""
        default_purposes = [
            {
                'purpose_id': 'essential_service',
                'consent_type': ConsentType.ESSENTIAL.value,
                'title': 'Essential Service Operations',
                'description': 'Required for basic service functionality and user authentication',
                'legal_basis': LegalBasis.CONTRACT.value,
                'data_categories': ['account_data', 'authentication_data'],
                'retention_days': 2555,  # 7 years
                'is_required': True
            },
            {
                'purpose_id': 'user_experience',
                'consent_type': ConsentType.FUNCTIONAL.value,
                'title': 'Enhanced User Experience',
                'description': 'Improve service functionality and user interface preferences',
                'legal_basis': LegalBasis.CONSENT.value,
                'data_categories': ['preference_data', 'interaction_data'],
                'retention_days': 730,  # 2 years
                'is_required': False
            },
            {
                'purpose_id': 'service_analytics',
                'consent_type': ConsentType.ANALYTICS.value,
                'title': 'Service Analytics',
                'description': 'Analyze usage patterns to improve our services',
                'legal_basis': LegalBasis.LEGITIMATE_INTERESTS.value,
                'data_categories': ['usage_data', 'performance_data'],
                'retention_days': 1095,  # 3 years
                'is_required': False
            },
            {
                'purpose_id': 'ai_improvement',
                'consent_type': ConsentType.AI_TRAINING.value,
                'title': 'AI Model Training',
                'description': 'Use anonymized data to improve AI model performance',
                'legal_basis': LegalBasis.CONSENT.value,
                'data_categories': ['interaction_data', 'anonymized_usage'],
                'retention_days': 1825,  # 5 years
                'is_required': False
            },
            {
                'purpose_id': 'biometric_auth',
                'consent_type': ConsentType.BIOMETRIC.value,
                'title': 'Biometric Authentication',
                'description': 'Store and process biometric data for secure authentication',
                'legal_basis': LegalBasis.CONSENT.value,
                'data_categories': ['biometric_templates', 'facial_features'],
                'retention_days': 365,  # 1 year
                'is_required': False
            }
        ]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for purpose in default_purposes:
                    cursor.execute('''
                        INSERT OR IGNORE INTO consent_purposes 
                        (purpose_id, consent_type, title, description, legal_basis, 
                         data_categories, retention_days, is_required)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        purpose['purpose_id'],
                        purpose['consent_type'],
                        purpose['title'],
                        purpose['description'],
                        purpose['legal_basis'],
                        json.dumps(purpose['data_categories']),
                        purpose['retention_days'],
                        purpose['is_required']
                    ))
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Failed to load default purposes: {e}")
    
    def request_consent(self, request: ConsentRequest) -> Dict[str, str]:
        """Request consent from user for specified purposes."""
        consent_ids = {}
        
        try:
            self.stats['consent_requests'] += 1
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for consent_type in request.consent_types:
                    consent_id = str(uuid.uuid4())
                    
                    # Calculate expiration date
                    expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
                    
                    # Create consent record
                    consent_record = ConsentRecord(
                        consent_id=consent_id,
                        user_id=request.user_id,
                        consent_type=consent_type,
                        status=ConsentStatus.PENDING,
                        legal_basis=request.legal_bases.get(consent_type, LegalBasis.CONSENT),
                        purpose=request.purposes.get(consent_type, ""),
                        data_categories=request.data_categories.get(consent_type, []),
                        retention_period_days=request.retention_periods.get(consent_type, 365),
                        expires_at=expires_at,
                        metadata=request.request_context
                    )
                    
                    # Store in database
                    cursor.execute('''
                        INSERT INTO consent_records 
                        (consent_id, user_id, consent_type, status, legal_basis, purpose,
                         data_categories, retention_period_days, expires_at, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        consent_record.consent_id,
                        consent_record.user_id,
                        consent_record.consent_type.value,
                        consent_record.status.value,
                        consent_record.legal_basis.value,
                        consent_record.purpose,
                        json.dumps(consent_record.data_categories),
                        consent_record.retention_period_days,
                        consent_record.expires_at.isoformat(),
                        json.dumps(consent_record.metadata) if consent_record.metadata else None
                    ))
                    
                    # Log history
                    self._log_consent_history(
                        consent_id,
                        request.user_id,
                        "REQUEST",
                        None,
                        ConsentStatus.PENDING.value,
                        "Consent requested",
                        conn
                    )
                    
                    consent_ids[consent_type.value] = consent_id
                
                conn.commit()
                logger.info(f"Consent requested for user {request.user_id}: {list(consent_ids.keys())}")
                
            return consent_ids
            
        except Exception as e:
            logger.error(f"Failed to request consent: {e}")
            return {}
    
    def grant_consent(self, user_id: str, consent_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Grant consent for a specific consent request."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update consent record
                granted_at = datetime.utcnow()
                cursor.execute('''
                    UPDATE consent_records 
                    SET status = ?, granted_at = ?, updated_at = ?, metadata = ?
                    WHERE consent_id = ? AND user_id = ? AND status = ?
                ''', (
                    ConsentStatus.GRANTED.value,
                    granted_at.isoformat(),
                    granted_at.isoformat(),
                    json.dumps(metadata) if metadata else None,
                    consent_id,
                    user_id,
                    ConsentStatus.PENDING.value
                ))
                
                if cursor.rowcount == 0:
                    logger.warning(f"No pending consent found for ID: {consent_id}")
                    return False
                
                # Log history
                self._log_consent_history(
                    consent_id,
                    user_id,
                    "GRANT",
                    ConsentStatus.PENDING.value,
                    ConsentStatus.GRANTED.value,
                    "Consent granted by user",
                    conn
                )
                
                conn.commit()
                
                # Update cache
                with self.lock:
                    cache_key = f"{user_id}:{consent_id}"
                    if cache_key in self.consent_cache:
                        self.consent_cache[cache_key]['status'] = ConsentStatus.GRANTED
                        self.consent_cache[cache_key]['granted_at'] = granted_at
                
                self.stats['consents_granted'] += 1
                logger.info(f"Consent granted: {consent_id} for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to grant consent: {e}")
            return False
    
    def deny_consent(self, user_id: str, consent_id: str, reason: str = "") -> bool:
        """Deny consent for a specific consent request."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update consent record
                updated_at = datetime.utcnow()
                cursor.execute('''
                    UPDATE consent_records 
                    SET status = ?, updated_at = ?
                    WHERE consent_id = ? AND user_id = ? AND status = ?
                ''', (
                    ConsentStatus.DENIED.value,
                    updated_at.isoformat(),
                    consent_id,
                    user_id,
                    ConsentStatus.PENDING.value
                ))
                
                if cursor.rowcount == 0:
                    logger.warning(f"No pending consent found for ID: {consent_id}")
                    return False
                
                # Log history
                self._log_consent_history(
                    consent_id,
                    user_id,
                    "DENY",
                    ConsentStatus.PENDING.value,
                    ConsentStatus.DENIED.value,
                    reason or "Consent denied by user",
                    conn
                )
                
                conn.commit()
                
                # Update cache
                with self.lock:
                    cache_key = f"{user_id}:{consent_id}"
                    if cache_key in self.consent_cache:
                        self.consent_cache[cache_key]['status'] = ConsentStatus.DENIED
                
                self.stats['consents_denied'] += 1
                logger.info(f"Consent denied: {consent_id} for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to deny consent: {e}")
            return False
    
    def withdraw_consent(self, withdrawal_request: ConsentWithdrawalRequest) -> bool:
        """Withdraw consent and optionally delete associated data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                withdrawn_at = withdrawal_request.effective_date
                success_count = 0
                
                for consent_type in withdrawal_request.consent_types:
                    # Update consent records
                    cursor.execute('''
                        UPDATE consent_records 
                        SET status = ?, withdrawn_at = ?, updated_at = ?
                        WHERE user_id = ? AND consent_type = ? AND status = ?
                    ''', (
                        ConsentStatus.WITHDRAWN.value,
                        withdrawn_at.isoformat(),
                        withdrawn_at.isoformat(),
                        withdrawal_request.user_id,
                        consent_type.value,
                        ConsentStatus.GRANTED.value
                    ))
                    
                    if cursor.rowcount > 0:
                        success_count += cursor.rowcount
                        
                        # Log history
                        cursor.execute('''
                            SELECT consent_id FROM consent_records 
                            WHERE user_id = ? AND consent_type = ? AND status = ?
                        ''', (
                            withdrawal_request.user_id,
                            consent_type.value,
                            ConsentStatus.WITHDRAWN.value
                        ))
                        
                        for (consent_id,) in cursor.fetchall():
                            self._log_consent_history(
                                consent_id,
                                withdrawal_request.user_id,
                                "WITHDRAW",
                                ConsentStatus.GRANTED.value,
                                ConsentStatus.WITHDRAWN.value,
                                withdrawal_request.withdrawal_reason,
                                conn
                            )
                
                conn.commit()
                
                if success_count > 0:
                    # Clear cache for user
                    with self.lock:
                        keys_to_remove = [
                            k for k in self.consent_cache.keys() 
                            if k.startswith(f"{withdrawal_request.user_id}:")
                        ]
                        for key in keys_to_remove:
                            del self.consent_cache[key]
                    
                    self.stats['consents_withdrawn'] += success_count
                    
                    # Handle data deletion if requested
                    if withdrawal_request.delete_data:
                        self._schedule_data_deletion(
                            withdrawal_request.user_id,
                            withdrawal_request.consent_types
                        )
                    
                    logger.info(f"Consent withdrawn for user {withdrawal_request.user_id}: {success_count} consents")
                    return True
                else:
                    logger.warning(f"No active consents found to withdraw for user {withdrawal_request.user_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to withdraw consent: {e}")
            return False
    
    def check_consent(self, user_id: str, consent_type: ConsentType, 
                     purpose: Optional[str] = None) -> bool:
        """Check if user has valid consent for a specific purpose."""
        try:
            # Check cache first
            cache_key = f"{user_id}:{consent_type.value}"
            
            with self.lock:
                if cache_key in self.consent_cache:
                    cached_consent = self.consent_cache[cache_key]
                    if cached_consent['expires'] > time.time():
                        self.stats['cache_hits'] += 1
                        return cached_consent['status'] == ConsentStatus.GRANTED
                    else:
                        del self.consent_cache[cache_key]
                
                self.stats['cache_misses'] += 1
            
            # Query database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT status, expires_at FROM consent_records 
                    WHERE user_id = ? AND consent_type = ?
                '''
                params = [user_id, consent_type.value]
                
                if purpose:
                    query += ' AND purpose = ?'
                    params.append(purpose)
                
                query += ' ORDER BY updated_at DESC LIMIT 1'
                
                cursor.execute(query, params)
                row = cursor.fetchone()
                
                if not row:
                    return False
                
                status, expires_at = row
                
                # Check if consent is granted and not expired
                is_valid = (status == ConsentStatus.GRANTED.value and 
                           (not expires_at or datetime.fromisoformat(expires_at) > datetime.utcnow()))
                
                # Cache result
                if len(self.consent_cache) < self.cache_size:
                    with self.lock:
                        self.consent_cache[cache_key] = {
                            'status': ConsentStatus(status),
                            'expires': time.time() + 300  # Cache for 5 minutes
                        }
                
                return is_valid
                
        except Exception as e:
            logger.error(f"Failed to check consent: {e}")
            return False
    
    def get_user_consents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all consent records for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT consent_id, consent_type, status, legal_basis, purpose,
                           data_categories, retention_period_days, granted_at, 
                           withdrawn_at, expires_at, version, metadata
                    FROM consent_records 
                    WHERE user_id = ? 
                    ORDER BY updated_at DESC
                ''', (user_id,))
                
                consents = []
                for row in cursor.fetchall():
                    (consent_id, consent_type, status, legal_basis, purpose,
                     data_categories, retention_period_days, granted_at,
                     withdrawn_at, expires_at, version, metadata) = row
                    
                    consent_data = {
                        'consent_id': consent_id,
                        'consent_type': consent_type,
                        'status': status,
                        'legal_basis': legal_basis,
                        'purpose': purpose,
                        'data_categories': json.loads(data_categories) if data_categories else [],
                        'retention_period_days': retention_period_days,
                        'granted_at': granted_at,
                        'withdrawn_at': withdrawn_at,
                        'expires_at': expires_at,
                        'version': version,
                        'metadata': json.loads(metadata) if metadata else {}
                    }
                    consents.append(consent_data)
                
                return consents
                
        except Exception as e:
            logger.error(f"Failed to get user consents: {e}")
            return []
    
    def log_processing_activity(self, user_id: str, consent_id: str, 
                               activity_type: str, data_processed: List[str],
                               purpose: str, metadata: Optional[Dict[str, Any]] = None):
        """Log data processing activity for audit trail."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO processing_activities 
                    (user_id, consent_id, activity_type, data_processed, purpose, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    consent_id,
                    activity_type,
                    json.dumps(data_processed),
                    purpose,
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log processing activity: {e}")
    
    def _log_consent_history(self, consent_id: str, user_id: str, action: str,
                           old_status: Optional[str], new_status: str,
                           reason: str, conn: sqlite3.Connection):
        """Log consent history entry."""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO consent_history 
                (consent_id, user_id, action, old_status, new_status, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (consent_id, user_id, action, old_status, new_status, reason))
        except sqlite3.Error as e:
            logger.error(f"Failed to log consent history: {e}")
    
    def _schedule_data_deletion(self, user_id: str, consent_types: List[ConsentType]):
        """Schedule data deletion for withdrawn consents."""
        # This would integrate with a data deletion service
        # For now, we'll just log the deletion request
        logger.info(f"Data deletion scheduled for user {user_id}, consent types: {[ct.value for ct in consent_types]}")
        
        # In a real implementation, this would:
        # 1. Identify all data associated with the consent types
        # 2. Schedule deletion jobs for data retention periods
        # 3. Handle cascading deletions and dependencies
        # 4. Provide deletion confirmation and audit trail
    
    def expire_consents(self) -> int:
        """Expire consents that have passed their expiration date."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find expired consents
                cursor.execute('''
                    SELECT consent_id, user_id FROM consent_records 
                    WHERE status = ? AND expires_at < CURRENT_TIMESTAMP
                ''', (ConsentStatus.GRANTED.value,))
                
                expired_consents = cursor.fetchall()
                
                if expired_consents:
                    # Update status to expired
                    consent_ids = [consent[0] for consent in expired_consents]
                    placeholders = ','.join(['?' for _ in consent_ids])
                    
                    cursor.execute(f'''
                        UPDATE consent_records 
                        SET status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE consent_id IN ({placeholders})
                    ''', [ConsentStatus.EXPIRED.value] + consent_ids)
                    
                    # Log history for each expired consent
                    for consent_id, user_id in expired_consents:
                        self._log_consent_history(
                            consent_id,
                            user_id,
                            "EXPIRE",
                            ConsentStatus.GRANTED.value,
                            ConsentStatus.EXPIRED.value,
                            "Consent expired automatically",
                            conn
                        )
                    
                    conn.commit()
                    
                    # Clear cache for expired consents
                    with self.lock:
                        for consent_id, user_id in expired_consents:
                            cache_key = f"{user_id}:{consent_id}"
                            self.consent_cache.pop(cache_key, None)
                    
                    self.stats['consents_expired'] += len(expired_consents)
                    logger.info(f"Expired {len(expired_consents)} consents")
                
                return len(expired_consents)
                
        except Exception as e:
            logger.error(f"Failed to expire consents: {e}")
            return 0
    
    def cleanup(self):
        """Clean up expired cache entries and perform maintenance."""
        try:
            current_time = time.time()
            
            # Clean expired cache entries
            with self.lock:
                expired_keys = [
                    key for key, value in self.consent_cache.items()
                    if value.get('expires', 0) <= current_time
                ]
                for key in expired_keys:
                    del self.consent_cache[key]
            
            # Expire old consents
            self.expire_consents()
            
            # Clean old history records (keep last 7 years for compliance)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_date = (datetime.utcnow() - timedelta(days=2555)).isoformat()  # 7 years
                cursor.execute('''
                    DELETE FROM consent_history 
                    WHERE timestamp < ?
                ''', (cutoff_date,))
                
                # Clean old processing activity logs (keep last 3 years)
                cutoff_date = (datetime.utcnow() - timedelta(days=1095)).isoformat()  # 3 years
                cursor.execute('''
                    DELETE FROM processing_activities 
                    WHERE timestamp < ?
                ''', (cutoff_date,))
                
                conn.commit()
            
            self.stats['last_cleanup'] = current_time
            logger.info("Consent manager cleanup completed")
            
        except Exception as e:
            logger.error(f"Consent cleanup failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get consent manager statistics."""
        return {
            **self.stats,
            'cache_size': len(self.consent_cache),
            'cache_hit_rate': (
                self.stats['cache_hits'] / 
                max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
            ) * 100
        }
    
    def generate_compliance_report(self, user_id: Optional[str] = None, 
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate compliance report for audit purposes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Base query conditions
                conditions = []
                params = []
                
                if user_id:
                    conditions.append("user_id = ?")
                    params.append(user_id)
                
                if start_date:
                    conditions.append("created_at >= ?")
                    params.append(start_date.isoformat())
                
                if end_date:
                    conditions.append("created_at <= ?")
                    params.append(end_date.isoformat())
                
                where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
                
                # Consent summary
                cursor.execute(f'''
                    SELECT status, COUNT(*) FROM consent_records{where_clause}
                    GROUP BY status
                ''', params)
                consent_summary = dict(cursor.fetchall())
                
                # Consent by type
                cursor.execute(f'''
                    SELECT consent_type, COUNT(*) FROM consent_records{where_clause}
                    GROUP BY consent_type
                ''', params)
                consent_by_type = dict(cursor.fetchall())
                
                # Recent activities
                cursor.execute(f'''
                    SELECT action, COUNT(*) FROM consent_history{where_clause}
                    GROUP BY action
                ''', params)
                recent_activities = dict(cursor.fetchall())
                
                report = {
                    'generated_at': datetime.utcnow().isoformat(),
                    'period': {
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None
                    },
                    'user_id': user_id,
                    'consent_summary': consent_summary,
                    'consent_by_type': consent_by_type,
                    'recent_activities': recent_activities,
                    'total_consents': sum(consent_summary.values()),
                    'active_consents': consent_summary.get(ConsentStatus.GRANTED.value, 0)
                }
                
                return report
                
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            return {}
