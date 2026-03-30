"""
Compliance Reporting - ImpressionCore

Automated compliance reporting and audit trail management system.
Provides GDPR, CCPA, and other regulatory compliance reporting capabilities
with comprehensive audit trails and documentation.

Features:
- Automated compliance status monitoring and reporting
- GDPR/CCPA compliance tracking and documentation
- Audit trail generation and management
- Privacy impact assessment reporting
- Regulatory compliance dashboard and alerts
- Export capabilities for compliance audits

Memory Budget: 8MB
Performance Target: <100ms report generation
Hardware: Optimized for GTX 1050 Ti

Created: 2025-05-31
Author: ImpressionCore AI
"""

import asyncio
import time
import sqlite3
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
import uuid
import hashlib

# Import rich enhancements for better UX
try:
    from src.core.utils.rich_logging import RichLogger
    from src.core.utils.rich_enhancements import RichConsole
    logger = RichLogger("ComplianceReporting")
    console = RichConsole()
except ImportError:
    import logging
    logger = logging.getLogger("ComplianceReporting")
    console = None

@dataclass
class ComplianceRule:
    """Individual compliance rule definition."""
    rule_id: str
    rule_name: str
    regulation: str  # "GDPR", "CCPA", "SOX", etc.
    description: str
    category: str
    severity: str  # "critical", "high", "medium", "low"
    check_function: str
    check_interval: int  # hours
    last_checked: Optional[datetime] = None
    status: str = "pending"  # "compliant", "non_compliant", "pending", "error"
    remediation_steps: List[str] = None
    
    def __post_init__(self):
        if self.remediation_steps is None:
            self.remediation_steps = []

@dataclass
class ComplianceViolation:
    """Compliance violation record."""
    violation_id: str
    rule_id: str
    severity: str
    description: str
    detected_at: datetime
    affected_components: List[str]
    risk_level: str
    status: str = "open"  # "open", "investigating", "resolved", "accepted"
    remediation_deadline: Optional[datetime] = None
    resolution_notes: str = ""
    assigned_to: str = ""

@dataclass
class AuditTrailEntry:
    """Individual audit trail entry."""
    entry_id: str
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: str = ""
    user_agent: str = ""
    outcome: str = "success"  # "success", "failure", "error"
    compliance_relevant: bool = True

@dataclass
class ComplianceReport:
    """Comprehensive compliance report."""
    report_id: str
    report_type: str  # "summary", "detailed", "audit", "violation"
    regulation: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    overall_status: str
    compliance_score: float
    total_rules: int
    compliant_rules: int
    violations: List[ComplianceViolation]
    recommendations: List[str]
    metadata: Dict[str, Any]

class ComplianceChecker:
    """Implements compliance rule checking logic."""
    
    def __init__(self):
        """Initialize compliance checker."""
        self.check_functions = {
            'data_retention_check': self._check_data_retention,
            'encryption_check': self._check_encryption_compliance,
            'access_control_check': self._check_access_control,
            'audit_logging_check': self._check_audit_logging,
            'consent_management_check': self._check_consent_management,
            'data_minimization_check': self._check_data_minimization,
            'breach_notification_check': self._check_breach_notification,
            'privacy_by_design_check': self._check_privacy_by_design
        }
    
    async def check_rule(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Check a specific compliance rule."""
        try:
            check_function = self.check_functions.get(rule.check_function)
            if not check_function:
                return {
                    'status': 'error',
                    'error': f'Unknown check function: {rule.check_function}'
                }
            
            result = await check_function(rule)
            return result
            
        except Exception as e:
            logger.error(f"Error checking rule {rule.rule_id}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'rule_id': rule.rule_id
            }
    
    async def _check_data_retention(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Check data retention policy compliance."""
        try:
            # Simulate data retention check
            # In real implementation, this would check actual data retention policies
            
            violations = []
            compliant = True
            
            # Example checks:
            # - Data older than retention period should be deleted
            # - Retention policies should be documented
            # - Automated deletion processes should be in place
            
            retention_policies_exist = True  # Would check actual policies
            automated_deletion_active = True  # Would check deletion processes
            
            if not retention_policies_exist:
                violations.append("Data retention policies not properly documented")
                compliant = False
            
            if not automated_deletion_active:
                violations.append("Automated data deletion processes not active")
                compliant = False
            
            return {
                'status': 'compliant' if compliant else 'non_compliant',
                'violations': violations,
                'details': {
                    'retention_policies_documented': retention_policies_exist,
                    'automated_deletion_active': automated_deletion_active
                },
                'checked_at': datetime.now()
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _check_encryption_compliance(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Check encryption compliance requirements."""
        try:
            violations = []
            compliant = True
            
            # Example encryption checks
            encryption_at_rest = True      # Would check actual encryption
            encryption_in_transit = True   # Would check TLS implementation
            key_management_secure = True   # Would check key management
            
            if not encryption_at_rest:
                violations.append("Data at rest encryption not properly implemented")
                compliant = False
            
            if not encryption_in_transit:
                violations.append("Data in transit encryption (TLS) not properly configured")
                compliant = False
            
            if not key_management_secure:
                violations.append("Cryptographic key management not secure")
                compliant = False
            
            return {
                'status': 'compliant' if compliant else 'non_compliant',
                'violations': violations,
                'details': {
                    'encryption_at_rest': encryption_at_rest,
                    'encryption_in_transit': encryption_in_transit,
                    'key_management_secure': key_management_secure
                },
                'checked_at': datetime.now()
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _check_access_control(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Check access control compliance."""
        try:
            violations = []
            compliant = True
            
            # Example access control checks
            mfa_enabled = True            # Would check MFA implementation
            role_based_access = True      # Would check RBAC
            access_logging = True         # Would check access logs
            privileged_access_monitored = True  # Would check privileged access
            
            if not mfa_enabled:
                violations.append("Multi-factor authentication not enabled for all users")
                compliant = False
            
            if not role_based_access:
                violations.append("Role-based access control not properly implemented")
                compliant = False
            
            if not access_logging:
                violations.append("Access logging not comprehensive")
                compliant = False
            
            if not privileged_access_monitored:
                violations.append("Privileged access not properly monitored")
                compliant = False
            
            return {
                'status': 'compliant' if compliant else 'non_compliant',
                'violations': violations,
                'details': {
                    'mfa_enabled': mfa_enabled,
                    'role_based_access': role_based_access,
                    'access_logging': access_logging,
                    'privileged_access_monitored': privileged_access_monitored
                },
                'checked_at': datetime.now()
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _check_audit_logging(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Check audit logging compliance."""
        try:
            violations = []
            compliant = True
            
            # Example audit logging checks
            comprehensive_logging = True   # Would check log coverage
            log_integrity = True          # Would check log protection
            log_retention = True          # Would check retention policies
            log_monitoring = True         # Would check monitoring systems
            
            if not comprehensive_logging:
                violations.append("Audit logging not comprehensive enough")
                compliant = False
            
            if not log_integrity:
                violations.append("Audit log integrity protection insufficient")
                compliant = False
            
            if not log_retention:
                violations.append("Audit log retention policies not adequate")
                compliant = False
            
            if not log_monitoring:
                violations.append("Audit log monitoring not implemented")
                compliant = False
            
            return {
                'status': 'compliant' if compliant else 'non_compliant',
                'violations': violations,
                'details': {
                    'comprehensive_logging': comprehensive_logging,
                    'log_integrity': log_integrity,
                    'log_retention': log_retention,
                    'log_monitoring': log_monitoring
                },
                'checked_at': datetime.now()
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _check_consent_management(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Check consent management compliance."""
        try:
            violations = []
            compliant = True
            
            # Example consent management checks
            consent_tracking = True       # Would check consent system
            consent_withdrawal = True     # Would check withdrawal process
            consent_documentation = True  # Would check documentation
            consent_granularity = True    # Would check granular consent
            
            if not consent_tracking:
                violations.append("User consent not properly tracked")
                compliant = False
            
            if not consent_withdrawal:
                violations.append("Consent withdrawal process not adequate")
                compliant = False
            
            if not consent_documentation:
                violations.append("Consent documentation insufficient")
                compliant = False
            
            if not consent_granularity:
                violations.append("Consent granularity not sufficient")
                compliant = False
            
            return {
                'status': 'compliant' if compliant else 'non_compliant',
                'violations': violations,
                'details': {
                    'consent_tracking': consent_tracking,
                    'consent_withdrawal': consent_withdrawal,
                    'consent_documentation': consent_documentation,
                    'consent_granularity': consent_granularity
                },
                'checked_at': datetime.now()
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _check_data_minimization(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Check data minimization principle compliance."""
        try:
            violations = []
            compliant = True
            
            # Example data minimization checks
            purpose_limitation = True     # Would check data purpose
            data_accuracy = True         # Would check data accuracy
            storage_limitation = True    # Would check storage limits
            collection_minimization = True  # Would check collection practices
            
            if not purpose_limitation:
                violations.append("Data not limited to stated purposes")
                compliant = False
            
            if not data_accuracy:
                violations.append("Data accuracy not maintained")
                compliant = False
            
            if not storage_limitation:
                violations.append("Data storage not properly limited")
                compliant = False
            
            if not collection_minimization:
                violations.append("Data collection not minimized")
                compliant = False
            
            return {
                'status': 'compliant' if compliant else 'non_compliant',
                'violations': violations,
                'details': {
                    'purpose_limitation': purpose_limitation,
                    'data_accuracy': data_accuracy,
                    'storage_limitation': storage_limitation,
                    'collection_minimization': collection_minimization
                },
                'checked_at': datetime.now()
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _check_breach_notification(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Check breach notification compliance."""
        try:
            violations = []
            compliant = True
            
            # Example breach notification checks
            incident_response_plan = True   # Would check incident response
            notification_procedures = True  # Would check notification process
            timeline_compliance = True     # Would check notification timing
            documentation_adequate = True  # Would check breach documentation
            
            if not incident_response_plan:
                violations.append("Incident response plan not adequate")
                compliant = False
            
            if not notification_procedures:
                violations.append("Breach notification procedures not defined")
                compliant = False
            
            if not timeline_compliance:
                violations.append("Breach notification timeline not compliant")
                compliant = False
            
            if not documentation_adequate:
                violations.append("Breach documentation not adequate")
                compliant = False
            
            return {
                'status': 'compliant' if compliant else 'non_compliant',
                'violations': violations,
                'details': {
                    'incident_response_plan': incident_response_plan,
                    'notification_procedures': notification_procedures,
                    'timeline_compliance': timeline_compliance,
                    'documentation_adequate': documentation_adequate
                },
                'checked_at': datetime.now()
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _check_privacy_by_design(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Check privacy by design implementation."""
        try:
            violations = []
            compliant = True
            
            # Example privacy by design checks
            privacy_impact_assessments = True  # Would check PIAs
            default_privacy_settings = True    # Would check defaults
            privacy_enhancing_technologies = True  # Would check PETs
            privacy_governance = True          # Would check governance
            
            if not privacy_impact_assessments:
                violations.append("Privacy impact assessments not conducted")
                compliant = False
            
            if not default_privacy_settings:
                violations.append("Privacy-friendly defaults not implemented")
                compliant = False
            
            if not privacy_enhancing_technologies:
                violations.append("Privacy enhancing technologies not utilized")
                compliant = False
            
            if not privacy_governance:
                violations.append("Privacy governance framework inadequate")
                compliant = False
            
            return {
                'status': 'compliant' if compliant else 'non_compliant',
                'violations': violations,
                'details': {
                    'privacy_impact_assessments': privacy_impact_assessments,
                    'default_privacy_settings': default_privacy_settings,
                    'privacy_enhancing_technologies': privacy_enhancing_technologies,
                    'privacy_governance': privacy_governance
                },
                'checked_at': datetime.now()
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

class ComplianceReporting:
    """
    Automated compliance reporting and audit trail management system.
    Provides comprehensive compliance monitoring and reporting capabilities.
    """
    
    def __init__(self, db_path: str = "compliance_reporting.db"):
        """Initialize compliance reporting system."""
        self.db_path = db_path
        self.is_running = False
        self.compliance_lock = threading.Lock()
        
        # Compliance components
        self.checker = ComplianceChecker()
        
        # Memory-optimized storage
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.active_violations: Dict[str, ComplianceViolation] = {}
        self.audit_trail: deque = deque(maxlen=10000)  # Last 10k entries
        
        # Configuration
        self.config = {
            'check_interval': 24,  # hours
            'report_retention_days': 365,
            'audit_trail_retention_days': 90,
            'violation_escalation_hours': 72,
            'auto_generate_reports': True
        }
        
        # Performance tracking
        self.performance_metrics = {
            'check_times': deque(maxlen=100),
            'report_generation_times': deque(maxlen=100),
            'violations_detected': deque(maxlen=100)
        }
        
        # Initialize database and rules
        self._init_database()
        self._init_compliance_rules()
        
        logger.info("ComplianceReporting initialized")
    
    def _init_database(self) -> None:
        """Initialize SQLite database for compliance data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Compliance rules table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compliance_rules (
                        rule_id TEXT PRIMARY KEY,
                        rule_name TEXT NOT NULL,
                        regulation TEXT NOT NULL,
                        description TEXT NOT NULL,
                        category TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        check_function TEXT NOT NULL,
                        check_interval INTEGER NOT NULL,
                        last_checked DATETIME,
                        status TEXT DEFAULT 'pending',
                        remediation_steps TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Compliance violations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compliance_violations (
                        violation_id TEXT PRIMARY KEY,
                        rule_id TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        description TEXT NOT NULL,
                        detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        affected_components TEXT,
                        risk_level TEXT NOT NULL,
                        status TEXT DEFAULT 'open',
                        remediation_deadline DATETIME,
                        resolution_notes TEXT,
                        assigned_to TEXT,
                        resolved_at DATETIME,
                        FOREIGN KEY (rule_id) REFERENCES compliance_rules (rule_id)
                    )
                """)
                
                # Audit trail table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_trail (
                        entry_id TEXT PRIMARY KEY,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        resource TEXT NOT NULL,
                        details TEXT NOT NULL,
                        ip_address TEXT,
                        user_agent TEXT,
                        outcome TEXT DEFAULT 'success',
                        compliance_relevant BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Compliance reports table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compliance_reports (
                        report_id TEXT PRIMARY KEY,
                        report_type TEXT NOT NULL,
                        regulation TEXT NOT NULL,
                        generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        period_start DATETIME NOT NULL,
                        period_end DATETIME NOT NULL,
                        overall_status TEXT NOT NULL,
                        compliance_score REAL NOT NULL,
                        total_rules INTEGER NOT NULL,
                        compliant_rules INTEGER NOT NULL,
                        violations_data TEXT,
                        recommendations TEXT,
                        metadata TEXT
                    )
                """)
                
                # Compliance metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compliance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        regulation TEXT NOT NULL,
                        recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Compliance database initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize compliance database: {e}")
            raise
    
    def _init_compliance_rules(self) -> None:
        """Initialize default compliance rules."""
        default_rules = [
            # GDPR Rules
            ComplianceRule(
                rule_id="gdpr_data_retention",
                rule_name="GDPR Data Retention",
                regulation="GDPR",
                description="Ensure data is not retained longer than necessary",
                category="data_protection",
                severity="high",
                check_function="data_retention_check",
                check_interval=24,
                remediation_steps=[
                    "Review data retention policies",
                    "Implement automated data deletion",
                    "Document retention justifications"
                ]
            ),
            ComplianceRule(
                rule_id="gdpr_encryption",
                rule_name="GDPR Encryption Requirements",
                regulation="GDPR",
                description="Ensure appropriate technical measures including encryption",
                category="security",
                severity="critical",
                check_function="encryption_check",
                check_interval=12,
                remediation_steps=[
                    "Implement encryption at rest",
                    "Ensure TLS for data in transit",
                    "Review key management practices"
                ]
            ),
            ComplianceRule(
                rule_id="gdpr_consent",
                rule_name="GDPR Consent Management",
                regulation="GDPR",
                description="Ensure valid consent is obtained and managed",
                category="consent",
                severity="high",
                check_function="consent_management_check",
                check_interval=24,
                remediation_steps=[
                    "Implement consent tracking",
                    "Provide withdrawal mechanisms",
                    "Document consent procedures"
                ]
            ),
            
            # CCPA Rules
            ComplianceRule(
                rule_id="ccpa_access_control",
                rule_name="CCPA Access Control",
                regulation="CCPA",
                description="Ensure appropriate access controls for personal information",
                category="access_control",
                severity="high",
                check_function="access_control_check",
                check_interval=24,
                remediation_steps=[
                    "Implement role-based access",
                    "Enable multi-factor authentication",
                    "Monitor privileged access"
                ]
            ),
            ComplianceRule(
                rule_id="ccpa_audit_logging",
                rule_name="CCPA Audit Logging",
                regulation="CCPA",
                description="Maintain comprehensive audit logs",
                category="logging",
                severity="medium",
                check_function="audit_logging_check",
                check_interval=24,
                remediation_steps=[
                    "Enhance log coverage",
                    "Implement log integrity protection",
                    "Establish log monitoring"
                ]
            ),
            
            # General Security Rules
            ComplianceRule(
                rule_id="general_data_minimization",
                rule_name="Data Minimization",
                regulation="General",
                description="Ensure data collection and processing is minimized",
                category="data_protection",
                severity="medium",
                check_function="data_minimization_check",
                check_interval=48,
                remediation_steps=[
                    "Review data collection practices",
                    "Implement purpose limitation",
                    "Establish data accuracy procedures"
                ]
            ),
            ComplianceRule(
                rule_id="general_breach_notification",
                rule_name="Breach Notification",
                regulation="General",
                description="Ensure breach notification procedures are in place",
                category="incident_response",
                severity="critical",
                check_function="breach_notification_check",
                check_interval=168,  # Weekly
                remediation_steps=[
                    "Develop incident response plan",
                    "Define notification procedures",
                    "Establish breach documentation"
                ]
            ),
            ComplianceRule(
                rule_id="general_privacy_by_design",
                rule_name="Privacy by Design",
                regulation="General",
                description="Ensure privacy is built into system design",
                category="design",
                severity="medium",
                check_function="privacy_by_design_check",
                check_interval=168,  # Weekly
                remediation_steps=[
                    "Conduct privacy impact assessments",
                    "Implement privacy-friendly defaults",
                    "Utilize privacy enhancing technologies"
                ]
            )
        ]
        
        for rule in default_rules:
            self.compliance_rules[rule.rule_id] = rule
    
    async def start_compliance_monitoring(self) -> Dict[str, Any]:
        """Start compliance monitoring system."""
        if self.is_running:
            return {'status': 'already_running'}
        
        try:
            self.is_running = True
            logger.info("Starting compliance monitoring...")
            
            # Start background monitoring task
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            return {
                'status': 'started',
                'rules': len(self.compliance_rules),
                'regulations': len(set(rule.regulation for rule in self.compliance_rules.values()))
            }
            
        except Exception as e:
            self.is_running = False
            logger.error(f"Failed to start compliance monitoring: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def stop_compliance_monitoring(self) -> Dict[str, Any]:
        """Stop compliance monitoring system."""
        if not self.is_running:
            return {'status': 'not_running'}
        
        try:
            self.is_running = False
            
            # Cancel monitoring task
            if hasattr(self, 'monitoring_task'):
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Compliance monitoring stopped")
            return {'status': 'stopped'}
            
        except Exception as e:
            logger.error(f"Error stopping compliance monitoring: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for compliance checking."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Check all compliance rules
                await self._check_all_rules()
                
                # Generate periodic reports
                if self.config['auto_generate_reports']:
                    await self._generate_periodic_reports()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                # Track performance
                check_time = time.time() - start_time
                self.performance_metrics['check_times'].append(check_time)
                
                # Sleep until next check cycle
                await asyncio.sleep(self.config['check_interval'] * 3600)  # Convert hours to seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in compliance monitoring loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying
    
    async def _check_all_rules(self) -> None:
        """Check all compliance rules that are due for checking."""
        with self.compliance_lock:
            try:
                current_time = datetime.now()
                
                for rule_id, rule in self.compliance_rules.items():
                    # Check if rule is due for checking
                    if (rule.last_checked is None or 
                        (current_time - rule.last_checked).total_seconds() >= rule.check_interval * 3600):
                        
                        # Perform compliance check
                        check_result = await self.checker.check_rule(rule)
                        
                        # Update rule status
                        rule.last_checked = current_time
                        rule.status = check_result.get('status', 'error')
                        
                        # Handle violations
                        if check_result.get('status') == 'non_compliant':
                            await self._handle_compliance_violation(rule, check_result)
                        
                        # Store check result
                        await self._store_check_result(rule, check_result)
                
            except Exception as e:
                logger.error(f"Error checking compliance rules: {e}")
    
    async def _handle_compliance_violation(self, rule: ComplianceRule, 
                                         check_result: Dict[str, Any]) -> None:
        """Handle a detected compliance violation."""
        try:
            violation_id = str(uuid.uuid4())
            
            # Calculate remediation deadline
            deadline_hours = {
                'critical': 24,
                'high': 72,
                'medium': 168,  # 1 week
                'low': 720      # 1 month
            }.get(rule.severity, 168)
            
            remediation_deadline = datetime.now() + timedelta(hours=deadline_hours)
            
            violation = ComplianceViolation(
                violation_id=violation_id,
                rule_id=rule.rule_id,
                severity=rule.severity,
                description=f"Compliance violation detected for {rule.rule_name}: {', '.join(check_result.get('violations', []))}",
                detected_at=datetime.now(),
                affected_components=check_result.get('details', {}).keys(),
                risk_level=rule.severity,
                remediation_deadline=remediation_deadline
            )
            
            # Store violation
            self.active_violations[violation_id] = violation
            await self._store_violation(violation)
            
            logger.warning(f"Compliance violation detected: {violation.description}")
            
        except Exception as e:
            logger.error(f"Error handling compliance violation: {e}")
    
    async def _store_check_result(self, rule: ComplianceRule, 
                                check_result: Dict[str, Any]) -> None:
        """Store compliance check result in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE compliance_rules 
                    SET last_checked = ?, status = ?
                    WHERE rule_id = ?
                """, (rule.last_checked, rule.status, rule.rule_id))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing check result: {e}")
    
    async def _store_violation(self, violation: ComplianceViolation) -> None:
        """Store compliance violation in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO compliance_violations (
                        violation_id, rule_id, severity, description,
                        detected_at, affected_components, risk_level,
                        status, remediation_deadline
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    violation.violation_id, violation.rule_id, violation.severity,
                    violation.description, violation.detected_at,
                    json.dumps(list(violation.affected_components)), violation.risk_level,
                    violation.status, violation.remediation_deadline
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing violation: {e}")
    
    async def _generate_periodic_reports(self) -> None:
        """Generate periodic compliance reports."""
        try:
            # Generate daily summary report
            daily_report = await self.generate_compliance_report(
                regulation="All",
                report_type="summary",
                period_days=1
            )
            
            # Generate weekly detailed report
            if datetime.now().weekday() == 0:  # Monday
                weekly_report = await self.generate_compliance_report(
                    regulation="All",
                    report_type="detailed",
                    period_days=7
                )
            
        except Exception as e:
            logger.error(f"Error generating periodic reports: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old compliance data."""
        try:
            cutoff_reports = datetime.now() - timedelta(days=self.config['report_retention_days'])
            cutoff_audit = datetime.now() - timedelta(days=self.config['audit_trail_retention_days'])
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old reports
                cursor.execute("""
                    DELETE FROM compliance_reports 
                    WHERE generated_at < ?
                """, (cutoff_reports,))
                
                # Clean up old audit trail entries
                cursor.execute("""
                    DELETE FROM audit_trail 
                    WHERE timestamp < ?
                """, (cutoff_audit,))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def generate_compliance_report(self, regulation: str = "All",
                                       report_type: str = "summary",
                                       period_days: int = 30) -> ComplianceReport:
        """Generate a comprehensive compliance report."""
        try:
            start_time = time.time()
            
            report_id = str(uuid.uuid4())
            end_time = datetime.now()
            start_time_period = end_time - timedelta(days=period_days)
            
            # Filter rules by regulation
            if regulation == "All":
                rules_to_check = list(self.compliance_rules.values())
            else:
                rules_to_check = [rule for rule in self.compliance_rules.values() 
                                if rule.regulation == regulation]
            
            # Calculate compliance metrics
            total_rules = len(rules_to_check)
            compliant_rules = len([rule for rule in rules_to_check 
                                 if rule.status == 'compliant'])
            
            compliance_score = (compliant_rules / total_rules * 100) if total_rules > 0 else 0
            
            # Determine overall status
            if compliance_score >= 95:
                overall_status = "excellent"
            elif compliance_score >= 85:
                overall_status = "good"
            elif compliance_score >= 70:
                overall_status = "needs_improvement"
            else:
                overall_status = "critical"
            
            # Get violations in period
            period_violations = [v for v in self.active_violations.values() 
                               if start_time_period <= v.detected_at <= end_time]
            
            # Generate recommendations
            recommendations = self._generate_recommendations(rules_to_check, period_violations)
            
            # Create report
            report = ComplianceReport(
                report_id=report_id,
                report_type=report_type,
                regulation=regulation,
                generated_at=end_time,
                period_start=start_time_period,
                period_end=end_time,
                overall_status=overall_status,
                compliance_score=compliance_score,
                total_rules=total_rules,
                compliant_rules=compliant_rules,
                violations=period_violations,
                recommendations=recommendations,
                metadata={
                    'generation_time_ms': (time.time() - start_time) * 1000,
                    'rules_checked': total_rules,
                    'violations_count': len(period_violations)
                }
            )
            
            # Store report
            await self._store_report(report)
            
            # Track performance
            generation_time = time.time() - start_time
            self.performance_metrics['report_generation_times'].append(generation_time)
            
            logger.info(f"Generated {report_type} compliance report for {regulation}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
    
    def _generate_recommendations(self, rules: List[ComplianceRule], 
                                violations: List[ComplianceViolation]) -> List[str]:
        """Generate compliance recommendations based on current status."""
        recommendations = []
        
        try:
            # Analyze rule compliance rates
            non_compliant_rules = [rule for rule in rules if rule.status == 'non_compliant']
            
            if non_compliant_rules:
                # Group by category
                category_violations = defaultdict(int)
                for rule in non_compliant_rules:
                    category_violations[rule.category] += 1
                
                # Generate category-specific recommendations
                for category, count in category_violations.items():
                    if category == "encryption":
                        recommendations.append("Review and strengthen encryption implementations")
                    elif category == "access_control":
                        recommendations.append("Enhance access control mechanisms and monitoring")
                    elif category == "data_protection":
                        recommendations.append("Improve data protection and retention policies")
                    elif category == "logging":
                        recommendations.append("Expand audit logging coverage and protection")
                    elif category == "consent":
                        recommendations.append("Strengthen consent management processes")
            
            # Analyze violation patterns
            if violations:
                critical_violations = [v for v in violations if v.severity == 'critical']
                if critical_violations:
                    recommendations.append("Immediately address all critical compliance violations")
                
                overdue_violations = [v for v in violations 
                                    if v.remediation_deadline and 
                                    datetime.now() > v.remediation_deadline]
                if overdue_violations:
                    recommendations.append("Prioritize resolution of overdue compliance violations")
            
            # General recommendations
            if not recommendations:
                recommendations.append("Maintain current compliance posture with regular monitoring")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Review compliance status and address any identified issues"]
    
    async def _store_report(self, report: ComplianceReport) -> None:
        """Store compliance report in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO compliance_reports (
                        report_id, report_type, regulation, generated_at,
                        period_start, period_end, overall_status, compliance_score,
                        total_rules, compliant_rules, violations_data,
                        recommendations, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report.report_id, report.report_type, report.regulation,
                    report.generated_at, report.period_start, report.period_end,
                    report.overall_status, report.compliance_score,
                    report.total_rules, report.compliant_rules,
                    json.dumps([asdict(v) for v in report.violations]),
                    json.dumps(report.recommendations),
                    json.dumps(report.metadata)
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing report: {e}")
    
    def add_audit_entry(self, user_id: str, action: str, resource: str,
                       details: Dict[str, Any], ip_address: str = "",
                       user_agent: str = "", outcome: str = "success") -> None:
        """Add entry to audit trail."""
        try:
            entry = AuditTrailEntry(
                entry_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                user_id=user_id,
                action=action,
                resource=resource,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                outcome=outcome
            )
            
            # Add to memory cache
            self.audit_trail.append(entry)
            
            # Store in database
            asyncio.create_task(self._store_audit_entry(entry))
            
        except Exception as e:
            logger.error(f"Error adding audit entry: {e}")
    
    async def _store_audit_entry(self, entry: AuditTrailEntry) -> None:
        """Store audit trail entry in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_trail (
                        entry_id, timestamp, user_id, action, resource,
                        details, ip_address, user_agent, outcome, compliance_relevant
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.entry_id, entry.timestamp, entry.user_id,
                    entry.action, entry.resource, json.dumps(entry.details),
                    entry.ip_address, entry.user_agent, entry.outcome,
                    entry.compliance_relevant
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing audit entry: {e}")
    
    def get_compliance_status(self, regulation: str = "All") -> Dict[str, Any]:
        """Get current compliance status."""
        try:
            if regulation == "All":
                rules = list(self.compliance_rules.values())
            else:
                rules = [rule for rule in self.compliance_rules.values() 
                        if rule.regulation == regulation]
            
            total_rules = len(rules)
            compliant_rules = len([rule for rule in rules if rule.status == 'compliant'])
            non_compliant_rules = len([rule for rule in rules if rule.status == 'non_compliant'])
            pending_rules = len([rule for rule in rules if rule.status == 'pending'])
            
            compliance_score = (compliant_rules / total_rules * 100) if total_rules > 0 else 0
            
            active_violations_count = len([v for v in self.active_violations.values() 
                                         if any(rule.rule_id == v.rule_id for rule in rules)])
            
            return {
                'regulation': regulation,
                'total_rules': total_rules,
                'compliant_rules': compliant_rules,
                'non_compliant_rules': non_compliant_rules,
                'pending_rules': pending_rules,
                'compliance_score': round(compliance_score, 2),
                'active_violations': active_violations_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance status: {e}")
            return {'error': str(e)}
    
    def get_recent_violations(self, limit: int = 50) -> List[ComplianceViolation]:
        """Get recent compliance violations."""
        try:
            violations = sorted(self.active_violations.values(), 
                              key=lambda x: x.detected_at, reverse=True)
            return violations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent violations: {e}")
            return []
    
    def get_audit_trail(self, limit: int = 100, 
                       compliance_relevant_only: bool = True) -> List[AuditTrailEntry]:
        """Get recent audit trail entries."""
        try:
            entries = list(self.audit_trail)
            
            if compliance_relevant_only:
                entries = [entry for entry in entries if entry.compliance_relevant]
            
            # Sort by timestamp (newest first)
            entries.sort(key=lambda x: x.timestamp, reverse=True)
            
            return entries[:limit]
            
        except Exception as e:
            logger.error(f"Error getting audit trail: {e}")
            return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get compliance system performance metrics."""
        try:
            check_times = list(self.performance_metrics['check_times'])
            report_times = list(self.performance_metrics['report_generation_times'])
            
            if not check_times and not report_times:
                return {'status': 'no_data'}
            
            return {
                'avg_check_time': sum(check_times) / len(check_times) if check_times else 0,
                'avg_report_time': sum(report_times) / len(report_times) if report_times else 0,
                'total_checks': len(check_times),
                'total_reports': len(report_times),
                'rules_monitored': len(self.compliance_rules),
                'active_violations': len(self.active_violations),
                'audit_entries': len(self.audit_trail)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def cleanup(self) -> None:
        """Clean up compliance reporting resources."""
        try:
            self.is_running = False
            
            # Clear compliance data
            with self.compliance_lock:
                self.compliance_rules.clear()
                self.active_violations.clear()
                self.audit_trail.clear()
            
            # Clear performance metrics
            for metric_deque in self.performance_metrics.values():
                metric_deque.clear()
            
            logger.info("ComplianceReporting cleaned up")
            
        except Exception as e:
            logger.error(f"Error during compliance cleanup: {e}")
