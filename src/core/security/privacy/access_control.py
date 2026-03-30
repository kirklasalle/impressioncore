# Phase 8A Week 2: Access Control System
# File: src/security/privacy/access_control.py
# Description: Fine-grained data access management framework
# Created: 2025-01-18 22:00:00 UTC
# Author: GitHub Copilot (ImpressionCore)

"""
Access Control System

Implements fine-grained access control for data privacy, supporting role-based
access control (RBAC), attribute-based access control (ABAC), and time-based
access restrictions. Optimized for GTX 1050 Ti hardware constraints.

Features:
- Multi-level access permissions (read, write, delete, admin)
- Dynamic role assignment and inheritance
- Context-aware access decisions
- Audit logging for compliance
- Memory-efficient permission caching

Memory Target: <15MB for active permissions and cache
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
from collections import defaultdict, LRU

logger = logging.getLogger(__name__)

class AccessLevel(Enum):
    """Access permission levels."""
    NONE = 0
    READ = 1
    WRITE = 2
    DELETE = 3
    ADMIN = 4

class ResourceType(Enum):
    """Types of resources that can be access controlled."""
    USER_DATA = "user_data"
    SYSTEM_CONFIG = "system_config"
    MODEL_WEIGHTS = "model_weights"
    TRAINING_DATA = "training_data"
    LOGS = "logs"
    AUDIT_TRAILS = "audit_trails"

@dataclass
class AccessPermission:
    """Represents an access permission grant."""
    user_id: str
    resource_id: str
    resource_type: ResourceType
    access_level: AccessLevel
    granted_by: str
    granted_at: datetime
    expires_at: Optional[datetime] = None
    conditions: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}
    
    def is_valid(self) -> bool:
        """Check if permission is still valid."""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['resource_type'] = self.resource_type.value
        data['access_level'] = self.access_level.value
        data['granted_at'] = self.granted_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data

@dataclass
class Role:
    """Represents a user role with permissions."""
    role_id: str
    role_name: str
    permissions: Set[str]
    parent_roles: Set[str]
    created_at: datetime
    description: str = ""
    
    def get_all_permissions(self, role_hierarchy: Dict[str, 'Role']) -> Set[str]:
        """Get all permissions including inherited ones."""
        all_perms = set(self.permissions)
        for parent_id in self.parent_roles:
            if parent_id in role_hierarchy:
                parent_perms = role_hierarchy[parent_id].get_all_permissions(role_hierarchy)
                all_perms.update(parent_perms)
        return all_perms

@dataclass
class AccessRequest:
    """Represents an access request for evaluation."""
    user_id: str
    resource_id: str
    resource_type: ResourceType
    requested_level: AccessLevel
    context: Dict[str, Any]
    timestamp: datetime
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

class AccessControl:
    """
    Fine-grained access control system with RBAC and ABAC support.
    
    Provides comprehensive access management with role-based and attribute-based
    access control, temporal permissions, and audit logging.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize access control system."""
        self.db_path = db_path or "privacy_access_control.db"
        self.memory_limit_mb = 15
        self.permission_cache = {}  # LRU cache for permissions
        self.role_cache = {}
        self.cache_size = 1000
        self.cleanup_interval = 300  # 5 minutes
        self.lock = threading.RLock()
        
        # Performance tracking
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'permission_checks': 0,
            'grants': 0,
            'revocations': 0,
            'last_cleanup': time.time()
        }
        
        # Initialize database
        self._init_database()
        self._load_default_roles()
        
        # Start cleanup task
        self.cleanup_task = None
        
        logger.info("Access control system initialized")
    
    def _init_database(self):
        """Initialize SQLite database for access control."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Permissions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS permissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        resource_id TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        access_level INTEGER NOT NULL,
                        granted_by TEXT NOT NULL,
                        granted_at TEXT NOT NULL,
                        expires_at TEXT,
                        conditions TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Roles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS roles (
                        role_id TEXT PRIMARY KEY,
                        role_name TEXT NOT NULL,
                        permissions TEXT NOT NULL,
                        parent_roles TEXT,
                        description TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # User roles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_roles (
                        user_id TEXT NOT NULL,
                        role_id TEXT NOT NULL,
                        assigned_by TEXT NOT NULL,
                        assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        expires_at TEXT,
                        PRIMARY KEY (user_id, role_id)
                    )
                ''')
                
                # Access audit log
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS access_audit (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        resource_id TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        action TEXT NOT NULL,
                        result TEXT NOT NULL,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        context TEXT
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_permissions_user ON permissions(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON access_audit(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON access_audit(timestamp)')
                
                conn.commit()
                logger.info("Access control database initialized")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _load_default_roles(self):
        """Load default system roles."""
        default_roles = [
            Role(
                role_id="system_admin",
                role_name="System Administrator",
                permissions={"*"},
                parent_roles=set(),
                created_at=datetime.utcnow(),
                description="Full system access"
            ),
            Role(
                role_id="user_admin",
                role_name="User Administrator",
                permissions={"user_data.read", "user_data.write", "logs.read"},
                parent_roles=set(),
                created_at=datetime.utcnow(),
                description="User data management"
            ),
            Role(
                role_id="data_scientist",
                role_name="Data Scientist",
                permissions={"training_data.read", "model_weights.read", "logs.read"},
                parent_roles=set(),
                created_at=datetime.utcnow(),
                description="Model development access"
            ),
            Role(
                role_id="regular_user",
                role_name="Regular User",
                permissions={"user_data.read"},
                parent_roles=set(),
                created_at=datetime.utcnow(),
                description="Basic user access"
            )
        ]
        
        for role in default_roles:
            self._store_role(role)
    
    def _store_role(self, role: Role):
        """Store role in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO roles 
                    (role_id, role_name, permissions, parent_roles, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    role.role_id,
                    role.role_name,
                    json.dumps(list(role.permissions)),
                    json.dumps(list(role.parent_roles)),
                    role.description,
                    role.created_at.isoformat()
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to store role {role.role_id}: {e}")
    
    def grant_permission(self, permission: AccessPermission) -> bool:
        """Grant access permission to a user."""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Store permission
                    cursor.execute('''
                        INSERT INTO permissions 
                        (user_id, resource_id, resource_type, access_level, granted_by, 
                         granted_at, expires_at, conditions)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        permission.user_id,
                        permission.resource_id,
                        permission.resource_type.value,
                        permission.access_level.value,
                        permission.granted_by,
                        permission.granted_at.isoformat(),
                        permission.expires_at.isoformat() if permission.expires_at else None,
                        json.dumps(permission.conditions) if permission.conditions else None
                    ))
                    
                    conn.commit()
                    
                    # Invalidate cache
                    cache_key = f"{permission.user_id}:{permission.resource_id}"
                    self.permission_cache.pop(cache_key, None)
                    
                    # Log audit
                    self._log_access_audit(
                        permission.user_id,
                        permission.resource_id,
                        permission.resource_type.value,
                        "GRANT",
                        "SUCCESS",
                        {"granted_by": permission.granted_by}
                    )
                    
                    self.stats['grants'] += 1
                    logger.info(f"Permission granted: {permission.user_id} -> {permission.resource_id}")
                    return True
                    
        except sqlite3.Error as e:
            logger.error(f"Failed to grant permission: {e}")
            self._log_access_audit(
                permission.user_id,
                permission.resource_id,
                permission.resource_type.value,
                "GRANT",
                "FAILED",
                {"error": str(e)}
            )
            return False
    
    def revoke_permission(self, user_id: str, resource_id: str, revoked_by: str) -> bool:
        """Revoke access permission from a user."""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Mark permission as inactive
                    cursor.execute('''
                        UPDATE permissions 
                        SET is_active = 0 
                        WHERE user_id = ? AND resource_id = ? AND is_active = 1
                    ''', (user_id, resource_id))
                    
                    conn.commit()
                    
                    # Invalidate cache
                    cache_key = f"{user_id}:{resource_id}"
                    self.permission_cache.pop(cache_key, None)
                    
                    # Log audit
                    self._log_access_audit(
                        user_id,
                        resource_id,
                        "unknown",  # Resource type unknown in revocation
                        "REVOKE",
                        "SUCCESS",
                        {"revoked_by": revoked_by}
                    )
                    
                    self.stats['revocations'] += 1
                    logger.info(f"Permission revoked: {user_id} -> {resource_id}")
                    return True
                    
        except sqlite3.Error as e:
            logger.error(f"Failed to revoke permission: {e}")
            return False
    
    def check_permission(self, request: AccessRequest) -> bool:
        """Check if user has permission for the requested access."""
        self.stats['permission_checks'] += 1
        
        try:
            # Check cache first
            cache_key = f"{request.user_id}:{request.resource_id}:{request.requested_level.value}"
            
            with self.lock:
                if cache_key in self.permission_cache:
                    self.stats['cache_hits'] += 1
                    result = self.permission_cache[cache_key]
                    if result['expires'] > time.time():
                        self._log_access_audit(
                            request.user_id,
                            request.resource_id,
                            request.resource_type.value,
                            f"CHECK_{request.requested_level.name}",
                            "GRANTED" if result['allowed'] else "DENIED",
                            {"source": "cache"}
                        )
                        return result['allowed']
                    else:
                        # Cache expired
                        del self.permission_cache[cache_key]
                
                self.stats['cache_misses'] += 1
                
                # Check direct permissions
                allowed = self._check_direct_permission(request)
                
                # If not allowed by direct permission, check role-based permissions
                if not allowed:
                    allowed = self._check_role_permission(request)
                
                # Cache result (valid for 5 minutes)
                if len(self.permission_cache) < self.cache_size:
                    self.permission_cache[cache_key] = {
                        'allowed': allowed,
                        'expires': time.time() + 300  # 5 minutes
                    }
                
                # Log audit
                self._log_access_audit(
                    request.user_id,
                    request.resource_id,
                    request.resource_type.value,
                    f"CHECK_{request.requested_level.name}",
                    "GRANTED" if allowed else "DENIED",
                    request.context
                )
                
                return allowed
                
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            self._log_access_audit(
                request.user_id,
                request.resource_id,
                request.resource_type.value,
                f"CHECK_{request.requested_level.name}",
                "ERROR",
                {"error": str(e)}
            )
            return False
    
    def _check_direct_permission(self, request: AccessRequest) -> bool:
        """Check direct permissions in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT access_level, expires_at, conditions 
                    FROM permissions 
                    WHERE user_id = ? AND resource_id = ? AND resource_type = ? 
                    AND is_active = 1
                ''', (
                    request.user_id,
                    request.resource_id,
                    request.resource_type.value
                ))
                
                row = cursor.fetchone()
                if not row:
                    return False
                
                access_level, expires_at, conditions = row
                
                # Check expiration
                if expires_at:
                    expiry = datetime.fromisoformat(expires_at)
                    if datetime.utcnow() > expiry:
                        return False
                
                # Check access level
                if access_level < request.requested_level.value:
                    return False
                
                # Check conditions if any
                if conditions:
                    condition_dict = json.loads(conditions)
                    if not self._evaluate_conditions(condition_dict, request.context):
                        return False
                
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Direct permission check failed: {e}")
            return False
    
    def _check_role_permission(self, request: AccessRequest) -> bool:
        """Check role-based permissions."""
        try:
            # Get user roles
            user_roles = self._get_user_roles(request.user_id)
            if not user_roles:
                return False
            
            # Load role hierarchy
            role_hierarchy = self._load_role_hierarchy()
            
            # Check permissions for each role
            for role_id in user_roles:
                if role_id in role_hierarchy:
                    role = role_hierarchy[role_id]
                    all_permissions = role.get_all_permissions(role_hierarchy)
                    
                    # Check wildcard permission
                    if "*" in all_permissions:
                        return True
                    
                    # Check specific permission
                    required_perm = f"{request.resource_type.value}.{request.requested_level.name.lower()}"
                    if required_perm in all_permissions:
                        return True
                    
                    # Check resource-specific wildcard
                    resource_wildcard = f"{request.resource_type.value}.*"
                    if resource_wildcard in all_permissions:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Role permission check failed: {e}")
            return False
    
    def _get_user_roles(self, user_id: str) -> List[str]:
        """Get active roles for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT role_id FROM user_roles 
                    WHERE user_id = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                ''', (user_id,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get user roles: {e}")
            return []
    
    def _load_role_hierarchy(self) -> Dict[str, Role]:
        """Load complete role hierarchy from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM roles')
                
                roles = {}
                for row in cursor.fetchall():
                    role_id, role_name, permissions_json, parent_roles_json, description, created_at = row
                    
                    permissions = set(json.loads(permissions_json))
                    parent_roles = set(json.loads(parent_roles_json)) if parent_roles_json else set()
                    
                    roles[role_id] = Role(
                        role_id=role_id,
                        role_name=role_name,
                        permissions=permissions,
                        parent_roles=parent_roles,
                        created_at=datetime.fromisoformat(created_at),
                        description=description
                    )
                
                return roles
                
        except sqlite3.Error as e:
            logger.error(f"Failed to load role hierarchy: {e}")
            return {}
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate access conditions against request context."""
        try:
            for condition_key, condition_value in conditions.items():
                if condition_key == "time_range":
                    # Check if current time is within allowed range
                    current_hour = datetime.utcnow().hour
                    start_hour, end_hour = condition_value
                    if not (start_hour <= current_hour <= end_hour):
                        return False
                
                elif condition_key == "ip_whitelist":
                    # Check if request comes from allowed IP
                    client_ip = context.get("client_ip")
                    if client_ip not in condition_value:
                        return False
                
                elif condition_key == "max_usage_count":
                    # Check usage count (would need to track this)
                    usage_count = context.get("usage_count", 0)
                    if usage_count >= condition_value:
                        return False
                
                elif condition_key in context:
                    # Direct context matching
                    if context[condition_key] != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def _log_access_audit(self, user_id: str, resource_id: str, resource_type: str, 
                         action: str, result: str, context: Dict[str, Any]):
        """Log access attempt for audit trail."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO access_audit 
                    (user_id, resource_id, resource_type, action, result, context)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    resource_id,
                    resource_type,
                    action,
                    result,
                    json.dumps(context) if context else None
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to log audit entry: {e}")
    
    def assign_role(self, user_id: str, role_id: str, assigned_by: str, 
                   expires_at: Optional[datetime] = None) -> bool:
        """Assign a role to a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_roles 
                    (user_id, role_id, assigned_by, expires_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    user_id,
                    role_id,
                    assigned_by,
                    expires_at.isoformat() if expires_at else None
                ))
                conn.commit()
                
                # Invalidate user's permission cache
                with self.lock:
                    keys_to_remove = [k for k in self.permission_cache.keys() if k.startswith(f"{user_id}:")]
                    for key in keys_to_remove:
                        del self.permission_cache[key]
                
                logger.info(f"Role {role_id} assigned to user {user_id}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Failed to assign role: {e}")
            return False
    
    def get_user_permissions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all effective permissions for a user."""
        permissions = []
        
        try:
            # Get direct permissions
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT resource_id, resource_type, access_level, granted_by, 
                           granted_at, expires_at, conditions
                    FROM permissions 
                    WHERE user_id = ? AND is_active = 1
                ''', (user_id,))
                
                for row in cursor.fetchall():
                    resource_id, resource_type, access_level, granted_by, granted_at, expires_at, conditions = row
                    permissions.append({
                        'type': 'direct',
                        'resource_id': resource_id,
                        'resource_type': resource_type,
                        'access_level': AccessLevel(access_level).name,
                        'granted_by': granted_by,
                        'granted_at': granted_at,
                        'expires_at': expires_at,
                        'conditions': json.loads(conditions) if conditions else {}
                    })
            
            # Get role-based permissions
            user_roles = self._get_user_roles(user_id)
            role_hierarchy = self._load_role_hierarchy()
            
            for role_id in user_roles:
                if role_id in role_hierarchy:
                    role = role_hierarchy[role_id]
                    all_perms = role.get_all_permissions(role_hierarchy)
                    for perm in all_perms:
                        permissions.append({
                            'type': 'role',
                            'role_id': role_id,
                            'role_name': role.role_name,
                            'permission': perm
                        })
            
            return permissions
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return []
    
    def cleanup(self):
        """Clean up expired permissions and cache."""
        try:
            current_time = time.time()
            
            # Clean expired cache entries
            with self.lock:
                expired_keys = [
                    key for key, value in self.permission_cache.items()
                    if value['expires'] <= current_time
                ]
                for key in expired_keys:
                    del self.permission_cache[key]
            
            # Clean expired database permissions
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE permissions 
                    SET is_active = 0 
                    WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP
                ''')
                
                # Clean old audit logs (keep last 90 days)
                cutoff_date = (datetime.utcnow() - timedelta(days=90)).isoformat()
                cursor.execute('''
                    DELETE FROM access_audit 
                    WHERE timestamp < ?
                ''', (cutoff_date,))
                
                conn.commit()
            
            self.stats['last_cleanup'] = current_time
            logger.info("Access control cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get access control statistics."""
        return {
            **self.stats,
            'cache_size': len(self.permission_cache),
            'cache_hit_rate': (
                self.stats['cache_hits'] / 
                max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
            ) * 100
        }
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            if hasattr(self, 'cleanup_task') and self.cleanup_task:
                self.cleanup_task.cancel()
        except:
            pass
