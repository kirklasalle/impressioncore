"""
ImpressionCore Security Alert System

A comprehensive alert and notification system for security monitoring,
providing real-time threat notifications, escalation management, and 
response coordination. Optimized for GTX 1050 Ti hardware constraints.

Author: ImpressionCore Development Team
Created: 2025-01-11
Memory Target: 30MB maximum (GTX 1050 Ti optimization)
"""

import asyncio
import json
import sqlite3
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import logging
from src.core.utils.rich_logging import RichLogger

# Alert severity levels
class AlertSeverity(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5

# Alert categories for classification
class AlertCategory(Enum):
    INTRUSION = auto()
    AUTHENTICATION = auto()
    BEHAVIORAL = auto()
    SYSTEM = auto()
    PRIVACY = auto()
    ENCRYPTION = auto()
    COMPLIANCE = auto()

# Alert status for tracking
class AlertStatus(Enum):
    PENDING = auto()
    ACKNOWLEDGED = auto()
    INVESTIGATING = auto()
    RESOLVED = auto()
    DISMISSED = auto()
    ESCALATED = auto()

@dataclass
class SecurityAlert:
    """Security alert data structure"""
    id: str
    timestamp: datetime
    severity: AlertSeverity
    category: AlertCategory
    title: str
    description: str
    source: str
    affected_resources: List[str] = field(default_factory=list)
    threat_indicators: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    risk_score: float = 0.0
    status: AlertStatus = AlertStatus.PENDING
    assigned_to: Optional[str] = None
    escalation_level: int = 0
    related_alerts: List[str] = field(default_factory=list)
    response_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationChannel:
    """Notification channel configuration"""
    name: str
    channel_type: str  # email, sms, webhook, dashboard
    endpoint: str
    severity_filter: Set[AlertSeverity]
    category_filter: Set[AlertCategory]
    enabled: bool = True
    rate_limit: int = 10  # alerts per minute
    retry_count: int = 3

@dataclass
class EscalationRule:
    """Alert escalation rule configuration"""
    name: str
    conditions: Dict[str, Any]
    escalation_delay: timedelta
    target_channel: str
    auto_escalate: bool = True
    max_escalations: int = 3

class AlertManager:
    """
    Core alert management system for security events
    
    Features:
    - Real-time alert processing and routing
    - Severity-based escalation management
    - Multi-channel notification system
    - Alert correlation and deduplication
    - Performance monitoring and optimization
    """
    
    def __init__(self, config_dir: str = "src/security/monitoring/config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging
        self.logger = RichLogger("SecurityAlertManager")
        
        # Alert storage and processing
        self.active_alerts: Dict[str, SecurityAlert] = {}
        self.alert_history: deque = deque(maxlen=10000)  # Last 10k alerts
        self.alert_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        
        # Notification and escalation
        self.notification_channels: Dict[str, NotificationChannel] = {}
        self.escalation_rules: List[EscalationRule] = []
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Correlation and deduplication
        self.correlation_rules: List[Dict[str, Any]] = []
        self.alert_signatures: Dict[str, datetime] = {}
        self.duplicate_threshold = timedelta(minutes=5)
        
        # Performance tracking
        self.processing_stats = {
            "alerts_processed": 0,
            "notifications_sent": 0,
            "escalations_triggered": 0,
            "processing_errors": 0,
            "average_processing_time": 0.0
        }
        
        # Threading and async management
        self.running = False
        self.processing_lock = threading.RLock()
        self.alert_processor_task: Optional[asyncio.Task] = None
        
        # Database setup
        self.db_path = self.config_dir / "alerts.db"
        self._init_database()
        self._load_configuration()
        
    def _init_database(self):
        """Initialize SQLite database for alert storage"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Alerts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        severity INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        source TEXT NOT NULL,
                        affected_resources TEXT,
                        threat_indicators TEXT,
                        confidence_score REAL,
                        risk_score REAL,
                        status TEXT,
                        assigned_to TEXT,
                        escalation_level INTEGER DEFAULT 0,
                        related_alerts TEXT,
                        response_actions TEXT,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Notification history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notification_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT NOT NULL,
                        channel_name TEXT NOT NULL,
                        status TEXT NOT NULL,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        retry_count INTEGER DEFAULT 0,
                        error_message TEXT,
                        FOREIGN KEY (alert_id) REFERENCES alerts (id)
                    )
                ''')
                
                # Performance metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_category ON alerts(category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)')
                
                conn.commit()
                self.logger.info("Alert database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize alert database: {e}")
            raise
    
    def _load_configuration(self):
        """Load alert system configuration"""
        try:
            # Load notification channels
            channels_file = self.config_dir / "notification_channels.json"
            if channels_file.exists():
                with open(channels_file, 'r') as f:
                    channels_data = json.load(f)
                    for channel_data in channels_data:
                        channel = NotificationChannel(
                            name=channel_data['name'],
                            channel_type=channel_data['type'],
                            endpoint=channel_data['endpoint'],
                            severity_filter=set(AlertSeverity(s) for s in channel_data['severity_filter']),
                            category_filter=set(AlertCategory[c] for c in channel_data['category_filter']),
                            enabled=channel_data.get('enabled', True),
                            rate_limit=channel_data.get('rate_limit', 10),
                            retry_count=channel_data.get('retry_count', 3)
                        )
                        self.notification_channels[channel.name] = channel
            
            # Load escalation rules
            escalation_file = self.config_dir / "escalation_rules.json"
            if escalation_file.exists():
                with open(escalation_file, 'r') as f:
                    escalation_data = json.load(f)
                    for rule_data in escalation_data:
                        rule = EscalationRule(
                            name=rule_data['name'],
                            conditions=rule_data['conditions'],
                            escalation_delay=timedelta(seconds=rule_data['escalation_delay_seconds']),
                            target_channel=rule_data['target_channel'],
                            auto_escalate=rule_data.get('auto_escalate', True),
                            max_escalations=rule_data.get('max_escalations', 3)
                        )
                        self.escalation_rules.append(rule)
            
            # Load correlation rules
            correlation_file = self.config_dir / "correlation_rules.json"
            if correlation_file.exists():
                with open(correlation_file, 'r') as f:
                    self.correlation_rules = json.load(f)
            
            self.logger.info("Alert system configuration loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load configuration: {e}, using defaults")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default alert system configuration"""
        try:
            # Default notification channels
            default_channels = [
                {
                    "name": "security_dashboard",
                    "type": "dashboard",
                    "endpoint": "internal://dashboard",
                    "severity_filter": [1, 2, 3, 4, 5],  # All severities
                    "category_filter": ["INTRUSION", "AUTHENTICATION", "BEHAVIORAL", "SYSTEM", "PRIVACY", "ENCRYPTION", "COMPLIANCE"],
                    "enabled": True,
                    "rate_limit": 50,
                    "retry_count": 1
                },
                {
                    "name": "critical_alerts",
                    "type": "webhook",
                    "endpoint": "http://localhost:8080/api/alerts/critical",
                    "severity_filter": [1, 2],  # Critical and High only
                    "category_filter": ["INTRUSION", "AUTHENTICATION", "SYSTEM"],
                    "enabled": True,
                    "rate_limit": 10,
                    "retry_count": 3
                }
            ]
            
            channels_file = self.config_dir / "notification_channels.json"
            with open(channels_file, 'w') as f:
                json.dump(default_channels, f, indent=2)
            
            # Default escalation rules
            default_escalation = [
                {
                    "name": "critical_auto_escalate",
                    "conditions": {
                        "severity": 1,
                        "unacknowledged_duration": 300  # 5 minutes
                    },
                    "escalation_delay_seconds": 300,
                    "target_channel": "critical_alerts",
                    "auto_escalate": True,
                    "max_escalations": 3
                },
                {
                    "name": "high_severity_escalate",
                    "conditions": {
                        "severity": 2,
                        "unacknowledged_duration": 600  # 10 minutes
                    },
                    "escalation_delay_seconds": 600,
                    "target_channel": "critical_alerts",
                    "auto_escalate": True,
                    "max_escalations": 2
                }
            ]
            
            escalation_file = self.config_dir / "escalation_rules.json"
            with open(escalation_file, 'w') as f:
                json.dump(default_escalation, f, indent=2)
            
            # Default correlation rules
            default_correlation = [
                {
                    "name": "brute_force_correlation",
                    "pattern": {
                        "category": "AUTHENTICATION",
                        "title_contains": "failed login",
                        "time_window": 300,
                        "count_threshold": 5
                    },
                    "action": "create_correlated_alert",
                    "new_severity": 2
                },
                {
                    "name": "intrusion_sequence_correlation",
                    "pattern": {
                        "category": "INTRUSION",
                        "sequence": ["reconnaissance", "exploitation", "privilege_escalation"],
                        "time_window": 3600
                    },
                    "action": "elevate_severity",
                    "severity_increase": 1
                }
            ]
            
            correlation_file = self.config_dir / "correlation_rules.json"
            with open(correlation_file, 'w') as f:
                json.dump(default_correlation, f, indent=2)
            
            self.logger.info("Default alert configuration created")
            
        except Exception as e:
            self.logger.error(f"Failed to create default configuration: {e}")
    
    async def start_processing(self):
        """Start the alert processing system"""
        if self.running:
            self.logger.warning("Alert processing already running")
            return
        
        self.running = True
        self.alert_processor_task = asyncio.create_task(self._process_alerts())
        self.logger.info("Alert processing system started")
    
    async def stop_processing(self):
        """Stop the alert processing system"""
        self.running = False
        if self.alert_processor_task:
            self.alert_processor_task.cancel()
            try:
                await self.alert_processor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Alert processing system stopped")
    
    async def _process_alerts(self):
        """Main alert processing loop"""
        while self.running:
            try:
                # Process alerts with timeout
                alert = await asyncio.wait_for(self.alert_queue.get(), timeout=1.0)
                
                start_time = time.time()
                await self._handle_alert(alert)
                processing_time = time.time() - start_time
                
                # Update processing statistics
                self.processing_stats["alerts_processed"] += 1
                self.processing_stats["average_processing_time"] = (
                    (self.processing_stats["average_processing_time"] * 
                     (self.processing_stats["alerts_processed"] - 1) + processing_time) /
                    self.processing_stats["alerts_processed"]
                )
                
                self.alert_queue.task_done()
                
            except asyncio.TimeoutError:
                # Check for escalations and maintenance
                await self._check_escalations()
                await self._cleanup_old_data()
                continue
                
            except Exception as e:
                self.logger.error(f"Error processing alert: {e}")
                self.processing_stats["processing_errors"] += 1
                continue
    
    async def create_alert(self, 
                          severity: AlertSeverity,
                          category: AlertCategory,
                          title: str,
                          description: str,
                          source: str,
                          **kwargs) -> str:
        """
        Create and queue a new security alert
        
        Args:
            severity: Alert severity level
            category: Alert category
            title: Alert title
            description: Alert description
            source: Alert source component
            **kwargs: Additional alert parameters
            
        Returns:
            Alert ID
        """
        try:
            # Generate unique alert ID
            alert_id = f"{category.name}_{int(time.time() * 1000)}_{hash(title) % 10000}"
            
            # Check for duplicates
            alert_signature = f"{category.name}_{title}_{source}"
            if self._is_duplicate_alert(alert_signature):
                self.logger.debug(f"Duplicate alert suppressed: {alert_signature}")
                return alert_id
            
            # Create alert object
            alert = SecurityAlert(
                id=alert_id,
                timestamp=datetime.now(),
                severity=severity,
                category=category,
                title=title,
                description=description,
                source=source,
                affected_resources=kwargs.get('affected_resources', []),
                threat_indicators=kwargs.get('threat_indicators', {}),
                confidence_score=kwargs.get('confidence_score', 0.0),
                risk_score=kwargs.get('risk_score', 0.0),
                metadata=kwargs.get('metadata', {})
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Queue for processing
            await self.alert_queue.put(alert)
            
            # Store in database
            await self._store_alert_in_db(alert)
            
            self.logger.info(f"Alert created: {alert_id} - {title}")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
            raise
    
    def _is_duplicate_alert(self, signature: str) -> bool:
        """Check if alert is a duplicate within the threshold window"""
        now = datetime.now()
        last_seen = self.alert_signatures.get(signature)
        
        if last_seen and (now - last_seen) < self.duplicate_threshold:
            return True
        
        self.alert_signatures[signature] = now
        return False
    
    async def _handle_alert(self, alert: SecurityAlert):
        """Process a single alert through the pipeline"""
        try:
            # Apply correlation rules
            await self._apply_correlation_rules(alert)
            
            # Send notifications
            await self._send_notifications(alert)
            
            # Schedule escalation check
            await self._schedule_escalation_check(alert)
            
            self.logger.debug(f"Alert processed: {alert.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle alert {alert.id}: {e}")
            raise
    
    async def _apply_correlation_rules(self, alert: SecurityAlert):
        """Apply correlation rules to detect patterns"""
        try:
            for rule in self.correlation_rules:
                if await self._matches_correlation_pattern(alert, rule):
                    await self._execute_correlation_action(alert, rule)
                    
        except Exception as e:
            self.logger.error(f"Error applying correlation rules: {e}")
    
    async def _matches_correlation_pattern(self, alert: SecurityAlert, rule: Dict[str, Any]) -> bool:
        """Check if alert matches correlation pattern"""
        pattern = rule.get('pattern', {})
        
        # Category match
        if 'category' in pattern and alert.category.name != pattern['category']:
            return False
        
        # Title contains match
        if 'title_contains' in pattern and pattern['title_contains'] not in alert.title.lower():
            return False
        
        # Additional pattern matching logic can be added here
        return True
    
    async def _execute_correlation_action(self, alert: SecurityAlert, rule: Dict[str, Any]):
        """Execute correlation rule action"""
        action = rule.get('action')
        
        if action == 'create_correlated_alert':
            # Create a new correlated alert
            new_severity = AlertSeverity(rule.get('new_severity', alert.severity.value))
            await self.create_alert(
                severity=new_severity,
                category=alert.category,
                title=f"Correlated Alert: {rule['name']}",
                description=f"Multiple related incidents detected: {alert.title}",
                source="correlation_engine",
                related_alerts=[alert.id]
            )
        
        elif action == 'elevate_severity':
            # Elevate alert severity
            severity_increase = rule.get('severity_increase', 1)
            new_severity_value = max(1, alert.severity.value - severity_increase)
            alert.severity = AlertSeverity(new_severity_value)
            await self._update_alert_in_db(alert)
    
    async def _send_notifications(self, alert: SecurityAlert):
        """Send alert notifications through configured channels"""
        for channel_name, channel in self.notification_channels.items():
            if not channel.enabled:
                continue
            
            # Check filters
            if alert.severity not in channel.severity_filter:
                continue
            if alert.category not in channel.category_filter:
                continue
            
            # Check rate limits
            if self._is_rate_limited(channel_name, channel.rate_limit):
                continue
            
            # Send notification
            await self._send_notification(alert, channel)
    
    def _is_rate_limited(self, channel_name: str, rate_limit: int) -> bool:
        """Check if channel is rate limited"""
        now = time.time()
        channel_history = self.rate_limits[channel_name]
        
        # Remove old entries
        while channel_history and channel_history[0] < now - 60:  # 1 minute window
            channel_history.popleft()
        
        return len(channel_history) >= rate_limit
    
    async def _send_notification(self, alert: SecurityAlert, channel: NotificationChannel):
        """Send notification to specific channel"""
        try:
            # Record rate limit
            self.rate_limits[channel.name].append(time.time())
            
            # Prepare notification payload
            notification_data = {
                'alert_id': alert.id,
                'timestamp': alert.timestamp.isoformat(),
                'severity': alert.severity.name,
                'category': alert.category.name,
                'title': alert.title,
                'description': alert.description,
                'source': alert.source,
                'confidence_score': alert.confidence_score,
                'risk_score': alert.risk_score
            }
            
            # Send based on channel type
            success = False
            error_message = None
            
            if channel.channel_type == "dashboard":
                success = await self._send_dashboard_notification(notification_data)
            elif channel.channel_type == "webhook":
                success = await self._send_webhook_notification(channel.endpoint, notification_data)
            elif channel.channel_type == "email":
                success = await self._send_email_notification(channel.endpoint, notification_data)
            
            # Record notification attempt
            await self._record_notification_attempt(alert.id, channel.name, success, error_message)
            
            if success:
                self.processing_stats["notifications_sent"] += 1
                self.logger.debug(f"Notification sent: {channel.name}")
            else:
                self.logger.warning(f"Failed to send notification: {channel.name}")
                
        except Exception as e:
            error_message = str(e)
            await self._record_notification_attempt(alert.id, channel.name, False, error_message)
            self.logger.error(f"Error sending notification to {channel.name}: {e}")
    
    async def _send_dashboard_notification(self, data: Dict[str, Any]) -> bool:
        """Send notification to security dashboard"""
        try:
            # This would integrate with the security dashboard component
            # For now, we'll just log the notification
            self.logger.info(f"Dashboard notification: {data['title']}")
            return True
        except Exception as e:
            self.logger.error(f"Dashboard notification failed: {e}")
            return False
    
    async def _send_webhook_notification(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Send webhook notification"""
        try:
            # This would make an HTTP POST to the webhook endpoint
            # For now, we'll simulate success
            self.logger.info(f"Webhook notification to {endpoint}: {data['title']}")
            return True
        except Exception as e:
            self.logger.error(f"Webhook notification failed: {e}")
            return False
    
    async def _send_email_notification(self, email: str, data: Dict[str, Any]) -> bool:
        """Send email notification"""
        try:
            # This would send an email notification
            # For now, we'll simulate success
            self.logger.info(f"Email notification to {email}: {data['title']}")
            return True
        except Exception as e:
            self.logger.error(f"Email notification failed: {e}")
            return False
    
    async def _schedule_escalation_check(self, alert: SecurityAlert):
        """Schedule escalation check for alert"""
        for rule in self.escalation_rules:
            if self._alert_matches_escalation_rule(alert, rule):
                # Schedule escalation check after delay
                escalation_time = datetime.now() + rule.escalation_delay
                # This would typically use a scheduler like asyncio.create_task
                # For now, we'll add to a simple check list
                self.logger.debug(f"Escalation scheduled for alert {alert.id} at {escalation_time}")
    
    def _alert_matches_escalation_rule(self, alert: SecurityAlert, rule: EscalationRule) -> bool:
        """Check if alert matches escalation rule conditions"""
        conditions = rule.conditions
        
        if 'severity' in conditions and alert.severity.value != conditions['severity']:
            return False
        
        return True
    
    async def _check_escalations(self):
        """Check for alerts that need escalation"""
        try:
            current_time = datetime.now()
            
            for alert in self.active_alerts.values():
                if alert.status != AlertStatus.PENDING:
                    continue
                
                for rule in self.escalation_rules:
                    if not self._alert_matches_escalation_rule(alert, rule):
                        continue
                    
                    # Check if escalation time has passed
                    unacknowledged_duration = rule.conditions.get('unacknowledged_duration', 0)
                    if (current_time - alert.timestamp).total_seconds() >= unacknowledged_duration:
                        await self._escalate_alert(alert, rule)
                        
        except Exception as e:
            self.logger.error(f"Error checking escalations: {e}")
    
    async def _escalate_alert(self, alert: SecurityAlert, rule: EscalationRule):
        """Escalate an alert according to rule"""
        try:
            if alert.escalation_level >= rule.max_escalations:
                return
            
            alert.escalation_level += 1
            alert.status = AlertStatus.ESCALATED
            
            # Find target channel
            target_channel = self.notification_channels.get(rule.target_channel)
            if target_channel:
                await self._send_notification(alert, target_channel)
            
            # Update database
            await self._update_alert_in_db(alert)
            
            self.processing_stats["escalations_triggered"] += 1
            self.logger.warning(f"Alert escalated: {alert.id} (level {alert.escalation_level})")
            
        except Exception as e:
            self.logger.error(f"Failed to escalate alert {alert.id}: {e}")
    
    async def acknowledge_alert(self, alert_id: str, user: str = None) -> bool:
        """Acknowledge an alert"""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                return False
            
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.assigned_to = user
            await self._update_alert_in_db(alert)
            
            self.logger.info(f"Alert acknowledged: {alert_id} by {user}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, user: str = None, resolution_notes: str = None) -> bool:
        """Resolve an alert"""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                return False
            
            alert.status = AlertStatus.RESOLVED
            if resolution_notes:
                alert.metadata['resolution_notes'] = resolution_notes
                alert.metadata['resolved_by'] = user
                alert.metadata['resolved_at'] = datetime.now().isoformat()
            
            await self._update_alert_in_db(alert)
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            self.logger.info(f"Alert resolved: {alert_id} by {user}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False
    
    async def _store_alert_in_db(self, alert: SecurityAlert):
        """Store alert in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO alerts (
                        id, timestamp, severity, category, title, description, source,
                        affected_resources, threat_indicators, confidence_score, risk_score,
                        status, assigned_to, escalation_level, related_alerts,
                        response_actions, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.id,
                    alert.timestamp.isoformat(),
                    alert.severity.value,
                    alert.category.name,
                    alert.title,
                    alert.description,
                    alert.source,
                    json.dumps(alert.affected_resources),
                    json.dumps(alert.threat_indicators),
                    alert.confidence_score,
                    alert.risk_score,
                    alert.status.name,
                    alert.assigned_to,
                    alert.escalation_level,
                    json.dumps(alert.related_alerts),
                    json.dumps(alert.response_actions),
                    json.dumps(alert.metadata)
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store alert in database: {e}")
    
    async def _update_alert_in_db(self, alert: SecurityAlert):
        """Update alert in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE alerts SET
                        status = ?, assigned_to = ?, escalation_level = ?,
                        metadata = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    alert.status.name,
                    alert.assigned_to,
                    alert.escalation_level,
                    json.dumps(alert.metadata),
                    alert.id
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to update alert in database: {e}")
    
    async def _record_notification_attempt(self, alert_id: str, channel_name: str, 
                                         success: bool, error_message: str = None):
        """Record notification attempt in database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO notification_history (
                        alert_id, channel_name, status, error_message
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    alert_id,
                    channel_name,
                    "success" if success else "failed",
                    error_message
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to record notification attempt: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old alerts and performance data"""
        try:
            cutoff_time = datetime.now() - timedelta(days=30)  # Keep 30 days
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Clean up old resolved alerts
                cursor.execute('''
                    DELETE FROM alerts 
                    WHERE status IN ('RESOLVED', 'DISMISSED') 
                    AND timestamp < ?
                ''', (cutoff_time.isoformat(),))
                
                # Clean up old notification history
                cursor.execute('''
                    DELETE FROM notification_history 
                    WHERE timestamp < ?
                ''', (cutoff_time.isoformat(),))
                
                # Clean up old performance metrics
                cursor.execute('''
                    DELETE FROM performance_metrics 
                    WHERE timestamp < ?
                ''', (cutoff_time.isoformat(),))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics"""
        try:
            stats = {
                "active_alerts": len(self.active_alerts),
                "processing_stats": self.processing_stats.copy(),
                "alert_queue_size": self.alert_queue.qsize(),
                "notification_channels": len(self.notification_channels),
                "escalation_rules": len(self.escalation_rules)
            }
            
            # Add severity breakdown
            severity_counts = defaultdict(int)
            for alert in self.active_alerts.values():
                severity_counts[alert.severity.name] += 1
            stats["severity_breakdown"] = dict(severity_counts)
            
            # Add category breakdown
            category_counts = defaultdict(int)
            for alert in self.active_alerts.values():
                category_counts[alert.category.name] += 1
            stats["category_breakdown"] = dict(category_counts)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def get_active_alerts(self, 
                         severity_filter: Optional[List[AlertSeverity]] = None,
                         category_filter: Optional[List[AlertCategory]] = None,
                         limit: int = 100) -> List[SecurityAlert]:
        """Get active alerts with optional filtering"""
        try:
            alerts = list(self.active_alerts.values())
            
            # Apply filters
            if severity_filter:
                alerts = [a for a in alerts if a.severity in severity_filter]
            
            if category_filter:
                alerts = [a for a in alerts if a.category in category_filter]
            
            # Sort by severity and timestamp
            alerts.sort(key=lambda x: (x.severity.value, x.timestamp), reverse=True)
            
            return alerts[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get active alerts: {e}")
            return []

class SecurityAlertSystem:
    """
    High-level security alert system interface
    
    Provides a simplified interface for security components to create
    and manage alerts within the ImpressionCore security framework.
    """
    
    def __init__(self):
        self.alert_manager = AlertManager()
        self.logger = RichLogger("SecurityAlertSystem")
        
    async def start(self):
        """Start the alert system"""
        await self.alert_manager.start_processing()
        self.logger.info("Security alert system started")
    
    async def stop(self):
        """Stop the alert system"""
        await self.alert_manager.stop_processing()
        self.logger.info("Security alert system stopped")
    
    async def create_critical_alert(self, title: str, description: str, 
                                  source: str, **kwargs) -> str:
        """Create a critical security alert"""
        return await self.alert_manager.create_alert(
            AlertSeverity.CRITICAL, AlertCategory.INTRUSION,
            title, description, source, **kwargs
        )
    
    async def create_authentication_alert(self, title: str, description: str,
                                        source: str, **kwargs) -> str:
        """Create an authentication-related alert"""
        return await self.alert_manager.create_alert(
            AlertSeverity.HIGH, AlertCategory.AUTHENTICATION,
            title, description, source, **kwargs
        )
    
    async def create_behavioral_alert(self, title: str, description: str,
                                    source: str, **kwargs) -> str:
        """Create a behavioral anomaly alert"""
        return await self.alert_manager.create_alert(
            AlertSeverity.MEDIUM, AlertCategory.BEHAVIORAL,
            title, description, source, **kwargs
        )
    
    async def acknowledge_alert(self, alert_id: str, user: str = None) -> bool:
        """Acknowledge an alert"""
        return await self.alert_manager.acknowledge_alert(alert_id, user)
    
    async def resolve_alert(self, alert_id: str, user: str = None, 
                          resolution_notes: str = None) -> bool:
        """Resolve an alert"""
        return await self.alert_manager.resolve_alert(alert_id, user, resolution_notes)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics"""
        return self.alert_manager.get_alert_statistics()
    
    def get_active_alerts(self, **kwargs) -> List[SecurityAlert]:
        """Get active alerts"""
        return self.alert_manager.get_active_alerts(**kwargs)

# Export main classes
__all__ = [
    'SecurityAlertSystem',
    'AlertManager', 
    'SecurityAlert',
    'AlertSeverity',
    'AlertCategory',
    'AlertStatus',
    'NotificationChannel',
    'EscalationRule'
]
