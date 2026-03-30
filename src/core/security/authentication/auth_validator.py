"""
Authentication Validator for ImpressionCore Security Infrastructure

This module implements comprehensive authentication validation with risk assessment,
policy enforcement, and adaptive security measures optimized for GTX 1050 Ti hardware.

Created: 2025-01-01
Author: ImpressionCore Security Team
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Limit: <30MB for validation operations
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Tuple, Union
import re
import secrets

# Import security components
from .auth_base import AuthenticationResult, AuthenticationError
from .mfa_manager import MFAManager, AuthenticationFactor, MFAPolicy
from .session_manager import SessionManager, Session, SessionType

# Configure logging for authentication validation
logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Authentication validation results"""
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"
    REQUIRES_MFA = "requires_mfa"
    REQUIRES_VERIFICATION = "requires_verification"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyViolationType(Enum):
    """Types of policy violations"""
    RATE_LIMIT = "rate_limit"
    GEO_RESTRICTION = "geo_restriction"
    TIME_RESTRICTION = "time_restriction"
    DEVICE_RESTRICTION = "device_restriction"
    CONCURRENT_SESSIONS = "concurrent_sessions"
    AUTHENTICATION_FAILURE = "authentication_failure"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"


@dataclass
class ValidationContext:
    """Context for authentication validation"""
    user_id: str
    ip_address: str
    user_agent: str
    device_fingerprint: str
    timestamp: datetime = field(default_factory=datetime.now)
    location: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    authentication_factors: List[AuthenticationFactor] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskAssessment:
    """Risk assessment for authentication attempt"""
    risk_level: RiskLevel
    risk_score: float  # 0.0 to 1.0
    risk_factors: List[str]
    recommended_actions: List[str]
    confidence: float
    assessment_time: datetime = field(default_factory=datetime.now)


@dataclass
class PolicyViolation:
    """Policy violation record"""
    violation_type: PolicyViolationType
    severity: RiskLevel
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationPolicy:
    """Authentication validation policy configuration"""
    # Rate limiting
    max_attempts_per_minute: int = 5
    max_attempts_per_hour: int = 20
    lockout_duration: int = 900  # 15 minutes
    progressive_delays: bool = True
    
    # Geographic restrictions
    allowed_countries: Optional[Set[str]] = None
    blocked_countries: Optional[Set[str]] = None
    geo_change_threshold: float = 1000.0  # km
    
    # Time restrictions
    allowed_hours: Optional[Tuple[int, int]] = None  # (start_hour, end_hour)
    allowed_days: Optional[Set[int]] = None  # weekdays (0-6)
    timezone_change_threshold: int = 3  # hours
    
    # Device and behavioral analysis
    require_known_device: bool = False
    device_change_requires_mfa: bool = True
    behavioral_analysis: bool = True
    anomaly_threshold: float = 0.8
    
    # MFA requirements
    mfa_policy: MFAPolicy = MFAPolicy.ADAPTIVE
    force_mfa_risk_threshold: float = 0.6
    admin_always_mfa: bool = True
    
    # Session management
    max_concurrent_sessions: int = 5
    session_timeout: int = 3600  # 1 hour
    require_reauthentication: bool = True
    
    # Memory optimization
    cache_size: int = 1000
    cache_timeout: int = 300  # 5 minutes


class AuthenticationValidator:
    """
    Authentication Validator
    
    Implements comprehensive authentication validation with risk assessment,
    policy enforcement, and adaptive security measures for ImpressionCore.
    """
    
    def __init__(
        self,
        policy: Optional[ValidationPolicy] = None,
        mfa_manager: Optional[MFAManager] = None,
        session_manager: Optional[SessionManager] = None
    ):
        """Initialize authentication validator"""
        self.policy = policy or ValidationPolicy()
        self.mfa_manager = mfa_manager or MFAManager()
        self.session_manager = session_manager or SessionManager()
        
        # Tracking and monitoring
        self.attempt_history: Dict[str, List[datetime]] = {}  # user_id -> attempts
        self.ip_attempts: Dict[str, List[datetime]] = {}  # ip -> attempts
        self.device_history: Dict[str, Dict[str, Any]] = {}  # device_fingerprint -> info
        self.user_baselines: Dict[str, Dict[str, Any]] = {}  # user_id -> behavior baseline
        
        # Cache for performance optimization
        self.validation_cache: Dict[str, Tuple[ValidationResult, datetime]] = {}
        self.risk_cache: Dict[str, Tuple[RiskAssessment, datetime]] = {}
        
        # Security monitoring
        self.policy_violations: List[PolicyViolation] = []
        self.security_events: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.validation_stats = {
            'total_validations': 0,
            'valid_attempts': 0,
            'invalid_attempts': 0,
            'blocked_attempts': 0,
            'mfa_required': 0,
            'average_validation_time_ms': 0.0,
            'memory_usage_mb': 0
        }
        
        logger.info("Authentication Validator initialized with adaptive security policies")
    
    async def validate_authentication(
        self,
        context: ValidationContext
    ) -> Tuple[ValidationResult, Optional[RiskAssessment], List[PolicyViolation]]:
        """
        Comprehensive authentication validation with risk assessment
        
        Returns:
            Tuple of (validation_result, risk_assessment, policy_violations)
        """
        start_time = time.time()
        
        try:
            # Check cache first for performance
            cache_key = self._generate_cache_key(context)
            cached_result = self._get_cached_validation(cache_key)
            if cached_result:
                return cached_result
            
            violations = []
            
            # Step 1: Basic policy validation
            policy_result = await self._validate_policies(context)
            if policy_result != ValidationResult.VALID:
                violations.extend(self._get_policy_violations(context, policy_result))
                return policy_result, None, violations
            
            # Step 2: Rate limiting validation
            rate_limit_result = await self._validate_rate_limits(context)
            if rate_limit_result != ValidationResult.VALID:
                violations.append(PolicyViolation(
                    violation_type=PolicyViolationType.RATE_LIMIT,
                    severity=RiskLevel.HIGH,
                    description="Rate limit exceeded"
                ))
                return rate_limit_result, None, violations
            
            # Step 3: Risk assessment
            risk_assessment = await self._assess_risk(context)
            
            # Step 4: Determine validation result based on risk
            validation_result = await self._determine_validation_result(
                context, risk_assessment
            )
            
            # Step 5: Update tracking and cache
            await self._update_tracking(context, validation_result)
            self._cache_validation_result(cache_key, validation_result, risk_assessment, violations)
            
            # Update statistics
            self._update_validation_stats(validation_result, start_time)
            
            return validation_result, risk_assessment, violations
            
        except Exception as e:
            logger.error(f"Authentication validation failed: {e}")
            return ValidationResult.INVALID, None, [
                PolicyViolation(
                    violation_type=PolicyViolationType.ANOMALOUS_BEHAVIOR,
                    severity=RiskLevel.CRITICAL,
                    description=f"Validation error: {e}"
                )
            ]
    
    async def _validate_policies(self, context: ValidationContext) -> ValidationResult:
        """Validate against security policies"""
        try:
            # Geographic restrictions
            if not await self._validate_geographic_policy(context):
                return ValidationResult.BLOCKED
            
            # Time restrictions
            if not await self._validate_time_policy(context):
                return ValidationResult.BLOCKED
            
            # Device restrictions
            if not await self._validate_device_policy(context):
                return ValidationResult.SUSPICIOUS
            
            # Session limits
            if not await self._validate_session_policy(context):
                return ValidationResult.BLOCKED
            
            return ValidationResult.VALID
            
        except Exception as e:
            logger.error(f"Policy validation failed: {e}")
            return ValidationResult.INVALID
    
    async def _validate_geographic_policy(self, context: ValidationContext) -> bool:
        """Validate geographic access policies"""
        try:
            if not context.location:
                return True  # Allow if location unknown
            
            country = context.location.get('country_code')
            if not country:
                return True
            
            # Check allowed countries
            if self.policy.allowed_countries and country not in self.policy.allowed_countries:
                return False
            
            # Check blocked countries
            if self.policy.blocked_countries and country in self.policy.blocked_countries:
                return False
            
            # Check for unusual geographic changes
            user_baseline = self.user_baselines.get(context.user_id, {})
            if 'typical_locations' in user_baseline:
                # Calculate distance from typical locations
                for typical_location in user_baseline['typical_locations']:
                    distance = self._calculate_distance(
                        context.location, typical_location
                    )
                    if distance < self.policy.geo_change_threshold:
                        return True
                
                # All locations are far from typical - flag as suspicious
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Geographic validation failed: {e}")
            return True  # Fail open for availability
    
    async def _validate_time_policy(self, context: ValidationContext) -> bool:
        """Validate time-based access policies"""
        try:
            current_time = context.timestamp
            
            # Check allowed hours
            if self.policy.allowed_hours:
                start_hour, end_hour = self.policy.allowed_hours
                current_hour = current_time.hour
                
                if start_hour <= end_hour:
                    # Same day range
                    if not (start_hour <= current_hour <= end_hour):
                        return False
                else:
                    # Overnight range
                    if not (current_hour >= start_hour or current_hour <= end_hour):
                        return False
            
            # Check allowed days
            if self.policy.allowed_days:
                current_day = current_time.weekday()
                if current_day not in self.policy.allowed_days:
                    return False
            
            # Check for unusual time patterns
            user_baseline = self.user_baselines.get(context.user_id, {})
            if 'typical_hours' in user_baseline:
                typical_hours = user_baseline['typical_hours']
                current_hour = current_time.hour
                
                # If user typically accesses during different hours
                if current_hour not in typical_hours:
                    # Allow but flag as suspicious
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"Time validation failed: {e}")
            return True  # Fail open for availability
    
    async def _validate_device_policy(self, context: ValidationContext) -> bool:
        """Validate device-based access policies"""
        try:
            device_fingerprint = context.device_fingerprint
            
            # Check if device is known
            if self.policy.require_known_device:
                if device_fingerprint not in self.device_history:
                    return False
            
            # Check device history for anomalies
            if device_fingerprint in self.device_history:
                device_info = self.device_history[device_fingerprint]
                
                # Check for inconsistent user agents
                if (device_info.get('user_agent') and 
                    device_info['user_agent'] != context.user_agent):
                    # Flag as suspicious but don't block
                    return False
                
                # Update device last seen
                device_info['last_seen'] = context.timestamp
            else:
                # New device - record information
                self.device_history[device_fingerprint] = {
                    'first_seen': context.timestamp,
                    'last_seen': context.timestamp,
                    'user_agent': context.user_agent,
                    'users': {context.user_id}
                }
            
            return True
            
        except Exception as e:
            logger.error(f"Device validation failed: {e}")
            return True  # Fail open for availability
    
    async def _validate_session_policy(self, context: ValidationContext) -> bool:
        """Validate session-related policies"""
        try:
            # Check concurrent session limits
            user_sessions = await self.session_manager.get_user_sessions(context.user_id)
            active_sessions = len([s for s in user_sessions if s.is_valid()])
            
            if active_sessions >= self.policy.max_concurrent_sessions:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return True  # Fail open for availability
    
    async def _validate_rate_limits(self, context: ValidationContext) -> ValidationResult:
        """Validate rate limiting policies"""
        try:
            now = datetime.now()
            user_id = context.user_id
            ip_address = context.ip_address
            
            # Clean old attempts
            self._clean_old_attempts(now)
            
            # Check user-based rate limits
            user_attempts = self.attempt_history.get(user_id, [])
            recent_user_attempts = [
                attempt for attempt in user_attempts
                if (now - attempt).total_seconds() < 60
            ]
            
            if len(recent_user_attempts) > self.policy.max_attempts_per_minute:
                return ValidationResult.BLOCKED
            
            # Check hourly limits
            hourly_user_attempts = [
                attempt for attempt in user_attempts
                if (now - attempt).total_seconds() < 3600
            ]
            
            if len(hourly_user_attempts) > self.policy.max_attempts_per_hour:
                return ValidationResult.BLOCKED
            
            # Check IP-based rate limits
            ip_attempts = self.ip_attempts.get(ip_address, [])
            recent_ip_attempts = [
                attempt for attempt in ip_attempts
                if (now - attempt).total_seconds() < 60
            ]
            
            if len(recent_ip_attempts) > self.policy.max_attempts_per_minute * 3:
                return ValidationResult.BLOCKED
            
            # Record current attempt
            if user_id not in self.attempt_history:
                self.attempt_history[user_id] = []
            self.attempt_history[user_id].append(now)
            
            if ip_address not in self.ip_attempts:
                self.ip_attempts[ip_address] = []
            self.ip_attempts[ip_address].append(now)
            
            return ValidationResult.VALID
            
        except Exception as e:
            logger.error(f"Rate limit validation failed: {e}")
            return ValidationResult.INVALID
    
    async def _assess_risk(self, context: ValidationContext) -> RiskAssessment:
        """Comprehensive risk assessment for authentication attempt"""
        try:
            # Check cache first
            cache_key = f"risk_{context.user_id}_{context.device_fingerprint}_{context.ip_address}"
            cached_risk = self._get_cached_risk(cache_key)
            if cached_risk:
                return cached_risk
            
            risk_factors = []
            risk_score = 0.0
            
            # Device risk assessment
            device_risk = await self._assess_device_risk(context)
            risk_score += device_risk * 0.3
            if device_risk > 0.5:
                risk_factors.append("Unknown or suspicious device")
            
            # Location risk assessment
            location_risk = await self._assess_location_risk(context)
            risk_score += location_risk * 0.2
            if location_risk > 0.5:
                risk_factors.append("Unusual geographic location")
            
            # Behavioral risk assessment
            behavioral_risk = await self._assess_behavioral_risk(context)
            risk_score += behavioral_risk * 0.3
            if behavioral_risk > 0.5:
                risk_factors.append("Anomalous behavior pattern")
            
            # Temporal risk assessment
            temporal_risk = await self._assess_temporal_risk(context)
            risk_score += temporal_risk * 0.2
            if temporal_risk > 0.5:
                risk_factors.append("Unusual access time")
            
            # Determine risk level
            if risk_score >= 0.8:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.3:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(risk_level, risk_factors)
            
            risk_assessment = RiskAssessment(
                risk_level=risk_level,
                risk_score=min(risk_score, 1.0),
                risk_factors=risk_factors,
                recommended_actions=recommendations,
                confidence=0.8  # Base confidence
            )
            
            # Cache result
            self._cache_risk_assessment(cache_key, risk_assessment)
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return RiskAssessment(
                risk_level=RiskLevel.MEDIUM,
                risk_score=0.5,
                risk_factors=["Assessment error"],
                recommended_actions=["Require MFA"],
                confidence=0.1
            )
    
    async def _assess_device_risk(self, context: ValidationContext) -> float:
        """Assess device-related risk factors"""
        try:
            device_fingerprint = context.device_fingerprint
            risk_score = 0.0
            
            # Check if device is known
            if device_fingerprint not in self.device_history:
                risk_score += 0.4  # New device
            else:
                device_info = self.device_history[device_fingerprint]
                
                # Check device consistency
                if device_info.get('user_agent') != context.user_agent:
                    risk_score += 0.3  # User agent changed
                
                # Check if device is shared among users
                user_count = len(device_info.get('users', set()))
                if user_count > 1:
                    risk_score += 0.2  # Shared device
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Device risk assessment failed: {e}")
            return 0.3  # Default moderate risk
    
    async def _assess_location_risk(self, context: ValidationContext) -> float:
        """Assess location-related risk factors"""
        try:
            if not context.location:
                return 0.1  # Low risk if location unknown
            
            risk_score = 0.0
            user_baseline = self.user_baselines.get(context.user_id, {})
            
            # Check against typical locations
            if 'typical_locations' in user_baseline:
                min_distance = float('inf')
                for typical_location in user_baseline['typical_locations']:
                    distance = self._calculate_distance(
                        context.location, typical_location
                    )
                    min_distance = min(min_distance, distance)
                
                # Risk increases with distance from typical locations
                if min_distance > 1000:  # > 1000 km
                    risk_score += 0.6
                elif min_distance > 500:  # > 500 km
                    risk_score += 0.4
                elif min_distance > 100:  # > 100 km
                    risk_score += 0.2
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Location risk assessment failed: {e}")
            return 0.1  # Default low risk
    
    async def _assess_behavioral_risk(self, context: ValidationContext) -> float:
        """Assess behavioral risk factors"""
        try:
            risk_score = 0.0
            user_baseline = self.user_baselines.get(context.user_id, {})
            
            # Check authentication factor patterns
            if 'typical_factors' in user_baseline:
                typical_factors = set(user_baseline['typical_factors'])
                current_factors = set(context.authentication_factors)
                
                # Risk if using unusual authentication factors
                if not current_factors.intersection(typical_factors):
                    risk_score += 0.3
            
            # Check session patterns
            user_sessions = await self.session_manager.get_user_sessions(context.user_id)
            if len(user_sessions) > user_baseline.get('typical_concurrent_sessions', 2):
                risk_score += 0.2
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Behavioral risk assessment failed: {e}")
            return 0.2  # Default low-moderate risk
    
    async def _assess_temporal_risk(self, context: ValidationContext) -> float:
        """Assess time-related risk factors"""
        try:
            risk_score = 0.0
            user_baseline = self.user_baselines.get(context.user_id, {})
            
            current_hour = context.timestamp.hour
            current_day = context.timestamp.weekday()
            
            # Check against typical access hours
            if 'typical_hours' in user_baseline:
                typical_hours = user_baseline['typical_hours']
                if current_hour not in typical_hours:
                    risk_score += 0.3
            
            # Check against typical days
            if 'typical_days' in user_baseline:
                typical_days = user_baseline['typical_days']
                if current_day not in typical_days:
                    risk_score += 0.2
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Temporal risk assessment failed: {e}")
            return 0.1  # Default low risk
    
    async def _determine_validation_result(
        self,
        context: ValidationContext,
        risk_assessment: RiskAssessment
    ) -> ValidationResult:
        """Determine final validation result based on risk assessment"""
        try:
            # Critical risk - block
            if risk_assessment.risk_level == RiskLevel.CRITICAL:
                return ValidationResult.BLOCKED
            
            # High risk - require MFA
            if (risk_assessment.risk_level == RiskLevel.HIGH or 
                risk_assessment.risk_score > self.policy.force_mfa_risk_threshold):
                return ValidationResult.REQUIRES_MFA
            
            # Medium risk - suspicious but allow with monitoring
            if risk_assessment.risk_level == RiskLevel.MEDIUM:
                return ValidationResult.SUSPICIOUS
            
            # Low risk - valid
            return ValidationResult.VALID
            
        except Exception as e:
            logger.error(f"Failed to determine validation result: {e}")
            return ValidationResult.INVALID
    
    def _generate_risk_recommendations(
        self,
        risk_level: RiskLevel,
        risk_factors: List[str]
    ) -> List[str]:
        """Generate security recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Block authentication attempt",
                "Require administrator review",
                "Investigate potential security breach"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Require multi-factor authentication",
                "Notify user of suspicious activity",
                "Monitor subsequent activity"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Allow with enhanced monitoring",
                "Consider additional verification",
                "Update user behavior baseline"
            ])
        else:
            recommendations.append("Allow with standard monitoring")
        
        # Factor-specific recommendations
        if "Unknown or suspicious device" in risk_factors:
            recommendations.append("Require device verification")
        
        if "Unusual geographic location" in risk_factors:
            recommendations.append("Verify location with user")
        
        return recommendations
    
    def _calculate_distance(self, loc1: Dict[str, Any], loc2: Dict[str, Any]) -> float:
        """Calculate distance between two locations (simplified)"""
        try:
            # Simplified distance calculation - in production use proper geodetic formulas
            lat1, lon1 = loc1.get('latitude', 0), loc1.get('longitude', 0)
            lat2, lon2 = loc2.get('latitude', 0), loc2.get('longitude', 0)
            
            # Simple Euclidean distance approximation
            distance = ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111  # km per degree
            return distance
            
        except Exception:
            return 0.0  # Unknown distance
    
    def _generate_cache_key(self, context: ValidationContext) -> str:
        """Generate cache key for validation result"""
        return hashlib.md5(
            f"{context.user_id}_{context.device_fingerprint}_{context.ip_address}_{context.timestamp.hour}".encode()
        ).hexdigest()
    
    def _get_cached_validation(self, cache_key: str) -> Optional[Tuple[ValidationResult, Optional[RiskAssessment], List[PolicyViolation]]]:
        """Get cached validation result if valid"""
        if cache_key in self.validation_cache:
            cached_result, cached_time = self.validation_cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.policy.cache_timeout:
                return cached_result, None, []  # Simplified cache return
        return None
    
    def _get_cached_risk(self, cache_key: str) -> Optional[RiskAssessment]:
        """Get cached risk assessment if valid"""
        if cache_key in self.risk_cache:
            cached_risk, cached_time = self.risk_cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.policy.cache_timeout:
                return cached_risk
        return None
    
    def _cache_validation_result(
        self,
        cache_key: str,
        result: ValidationResult,
        risk_assessment: Optional[RiskAssessment],
        violations: List[PolicyViolation]
    ):
        """Cache validation result for performance"""
        self.validation_cache[cache_key] = ((result, risk_assessment, violations), datetime.now())
        
        # Limit cache size for memory optimization
        if len(self.validation_cache) > self.policy.cache_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self.validation_cache.keys(),
                key=lambda k: self.validation_cache[k][1]
            )[:len(self.validation_cache) - self.policy.cache_size + 100]
            
            for key in oldest_keys:
                del self.validation_cache[key]
    
    def _cache_risk_assessment(self, cache_key: str, risk_assessment: RiskAssessment):
        """Cache risk assessment for performance"""
        self.risk_cache[cache_key] = (risk_assessment, datetime.now())
        
        # Limit cache size
        if len(self.risk_cache) > self.policy.cache_size:
            oldest_keys = sorted(
                self.risk_cache.keys(),
                key=lambda k: self.risk_cache[k][1]
            )[:len(self.risk_cache) - self.policy.cache_size + 100]
            
            for key in oldest_keys:
                del self.risk_cache[key]
    
    async def _update_tracking(self, context: ValidationContext, result: ValidationResult):
        """Update user behavior tracking and baselines"""
        try:
            user_id = context.user_id
            
            # Initialize user baseline if needed
            if user_id not in self.user_baselines:
                self.user_baselines[user_id] = {
                    'typical_hours': set(),
                    'typical_days': set(),
                    'typical_locations': [],
                    'typical_factors': set(),
                    'typical_concurrent_sessions': 1
                }
            
            baseline = self.user_baselines[user_id]
            
            # Update temporal patterns
            baseline['typical_hours'].add(context.timestamp.hour)
            baseline['typical_days'].add(context.timestamp.weekday())
            
            # Update location patterns
            if context.location and len(baseline['typical_locations']) < 5:
                baseline['typical_locations'].append(context.location)
            
            # Update authentication factor patterns
            baseline['typical_factors'].update(context.authentication_factors)
            
            # Limit baseline data for memory optimization
            if len(baseline['typical_hours']) > 24:
                baseline['typical_hours'] = set(list(baseline['typical_hours'])[-12:])
            
            if len(baseline['typical_days']) > 7:
                baseline['typical_days'] = set(list(baseline['typical_days'])[-7:])
                
        except Exception as e:
            logger.error(f"Failed to update tracking: {e}")
    
    def _clean_old_attempts(self, now: datetime):
        """Clean old attempt records for memory optimization"""
        try:
            # Clean user attempts older than 1 hour
            for user_id in list(self.attempt_history.keys()):
                self.attempt_history[user_id] = [
                    attempt for attempt in self.attempt_history[user_id]
                    if (now - attempt).total_seconds() < 3600
                ]
                
                if not self.attempt_history[user_id]:
                    del self.attempt_history[user_id]
            
            # Clean IP attempts older than 1 hour
            for ip in list(self.ip_attempts.keys()):
                self.ip_attempts[ip] = [
                    attempt for attempt in self.ip_attempts[ip]
                    if (now - attempt).total_seconds() < 3600
                ]
                
                if not self.ip_attempts[ip]:
                    del self.ip_attempts[ip]
                    
        except Exception as e:
            logger.error(f"Failed to clean old attempts: {e}")
    
    def _get_policy_violations(
        self,
        context: ValidationContext,
        result: ValidationResult
    ) -> List[PolicyViolation]:
        """Generate policy violations based on validation result"""
        violations = []
        
        if result == ValidationResult.BLOCKED:
            violations.append(PolicyViolation(
                violation_type=PolicyViolationType.ANOMALOUS_BEHAVIOR,
                severity=RiskLevel.HIGH,
                description="Authentication blocked due to policy violation"
            ))
        elif result == ValidationResult.SUSPICIOUS:
            violations.append(PolicyViolation(
                violation_type=PolicyViolationType.ANOMALOUS_BEHAVIOR,
                severity=RiskLevel.MEDIUM,
                description="Suspicious authentication pattern detected"
            ))
        
        return violations
    
    def _update_validation_stats(self, result: ValidationResult, start_time: float):
        """Update validation performance statistics"""
        try:
            self.validation_stats['total_validations'] += 1
            
            if result == ValidationResult.VALID:
                self.validation_stats['valid_attempts'] += 1
            elif result == ValidationResult.INVALID:
                self.validation_stats['invalid_attempts'] += 1
            elif result == ValidationResult.BLOCKED:
                self.validation_stats['blocked_attempts'] += 1
            elif result == ValidationResult.REQUIRES_MFA:
                self.validation_stats['mfa_required'] += 1
            
            # Update average validation time
            duration_ms = (time.time() - start_time) * 1000
            total_validations = self.validation_stats['total_validations']
            current_avg = self.validation_stats['average_validation_time_ms']
            
            new_avg = ((current_avg * (total_validations - 1)) + duration_ms) / total_validations
            self.validation_stats['average_validation_time_ms'] = new_avg
            
        except Exception as e:
            logger.error(f"Failed to update validation stats: {e}")
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive validation statistics"""
        return {
            **self.validation_stats,
            'cached_validations': len(self.validation_cache),
            'cached_risks': len(self.risk_cache),
            'tracked_users': len(self.user_baselines),
            'tracked_devices': len(self.device_history),
            'policy_violations': len(self.policy_violations),
            'security_events': len(self.security_events)
        }
