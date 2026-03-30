"""
ImpressionCore Behavioral Analysis Engine

Advanced behavioral analysis system for detecting anomalous user behavior,
insider threats, and sophisticated attack patterns. Uses machine learning
algorithms optimized for GTX 1050 Ti hardware constraints.

Author: ImpressionCore Security Team
Created: 2025-01-27
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Budget: 30MB for behavioral analysis
"""

import os
import sys
import asyncio
import logging
import threading
import time
import json
import sqlite3
import numpy as np
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import collections
import gc
import hashlib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
import joblib

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.utils.rich_enhancements import RichStatusManager
from src.core.utils.rich_logging import RichLogger


class BehaviorType(Enum):
    """Types of user behaviors to analyze."""
    LOGIN_PATTERN = "login_pattern"
    ACCESS_PATTERN = "access_pattern"
    DATA_USAGE = "data_usage"
    NAVIGATION_PATTERN = "navigation_pattern"
    TIME_PATTERN = "time_pattern"
    LOCATION_PATTERN = "location_pattern"
    DEVICE_PATTERN = "device_pattern"
    API_USAGE = "api_usage"


class AnomalyType(Enum):
    """Types of behavioral anomalies."""
    TEMPORAL_ANOMALY = "temporal_anomaly"
    SPATIAL_ANOMALY = "spatial_anomaly"
    VOLUME_ANOMALY = "volume_anomaly"
    PATTERN_DEVIATION = "pattern_deviation"
    ACCESS_ESCALATION = "access_escalation"
    DATA_HOARDING = "data_hoarding"
    UNUSUAL_LOCATION = "unusual_location"
    DEVICE_ANOMALY = "device_anomaly"


class RiskLevel(Enum):
    """Risk levels for behavioral anomalies."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class UserBehavior:
    """User behavior data point."""
    user_id: str
    timestamp: datetime
    behavior_type: BehaviorType
    features: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class BehavioralAnomaly:
    """Detected behavioral anomaly."""
    anomaly_id: str
    user_id: str
    timestamp: datetime
    anomaly_type: AnomalyType
    risk_level: RiskLevel
    confidence_score: float  # 0.0 - 1.0
    description: str
    features_analysis: Dict[str, float]
    baseline_comparison: Dict[str, Any]
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class UserProfile:
    """User behavioral profile."""
    user_id: str
    created_at: datetime
    last_updated: datetime
    behavior_models: Dict[BehaviorType, Any] = field(default_factory=dict)
    baseline_features: Dict[str, Dict[str, float]] = field(default_factory=dict)
    risk_score: float = 0.0
    total_behaviors: int = 0
    anomaly_count: int = 0


class BehavioralAnalysisConfig:
    """Configuration for behavioral analysis engine."""
    
    # Memory management
    MAX_MEMORY_MB = 30
    MAX_BEHAVIORS_IN_MEMORY = 5000
    MAX_PROFILES_IN_MEMORY = 100
    MAX_ANOMALIES_IN_MEMORY = 500
    
    # Analysis parameters
    BASELINE_WINDOW_DAYS = 30
    ANOMALY_THRESHOLD = 0.7
    MINIMUM_BEHAVIORS_FOR_PROFILE = 50
    PROFILE_UPDATE_INTERVAL_HOURS = 6
    
    # ML model parameters
    ISOLATION_FOREST_CONTAMINATION = 0.1
    DBSCAN_EPS = 0.5
    DBSCAN_MIN_SAMPLES = 5
    FEATURE_SCALING_WINDOW = 1000
    
    # Performance settings
    MAX_ANALYSIS_THREADS = 2
    BATCH_SIZE = 100
    ANALYSIS_TIMEOUT_MS = 200
    
    # Database settings
    BEHAVIORAL_DB_PATH = "data/security/behavioral.db"
    MODEL_CACHE_PATH = "data/security/models"
    BEHAVIOR_RETENTION_DAYS = 180
    ANOMALY_RETENTION_DAYS = 365


class BehavioralAnalysisEngine:
    """
    Advanced behavioral analysis engine for detecting user anomalies.
    
    Features:
    - Real-time behavioral profiling
    - Machine learning-based anomaly detection
    - Temporal and spatial pattern analysis
    - Risk assessment and scoring
    - Memory-optimized for GTX 1050 Ti constraints
    """
    
    def __init__(self):
        self.config = BehavioralAnalysisConfig()
        self.logger = self._setup_logging()
        self.status_manager = RichStatusManager("Behavioral Analysis")
        
        # System state
        self.is_active = False
        self.memory_usage_mb = 0.0
        self._shutdown_event = threading.Event()
        
        # Data storage
        self._user_profiles: Dict[str, UserProfile] = {}
        self._recent_behaviors: collections.deque = collections.deque(
            maxlen=self.config.MAX_BEHAVIORS_IN_MEMORY
        )
        self._recent_anomalies: collections.deque = collections.deque(
            maxlen=self.config.MAX_ANOMALIES_IN_MEMORY
        )
        
        # ML models
        self._isolation_forests: Dict[str, IsolationForest] = {}
        self._scalers: Dict[str, StandardScaler] = {}
        self._feature_buffers: Dict[str, collections.deque] = {}
        
        # Threading
        self._analysis_thread: Optional[threading.Thread] = None
        self._profile_update_thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self._behaviors_analyzed = 0
        self._anomalies_detected = 0
        self._analysis_times: collections.deque = collections.deque(maxlen=100)
        
        # Database
        self._db_connection: Optional[sqlite3.Connection] = None
        self._initialize_database()
        
        # Load existing profiles
        self._load_user_profiles()
        
        # Initialize models
        self._initialize_models()
    
    def _setup_logging(self) -> RichLogger:
        """Setup rich logging for behavioral analysis."""
        logger = RichLogger(
            name="behavioral_analysis",
            level=logging.INFO,
            log_file="logs/behavioral_analysis.log"
        )
        return logger
    
    def _initialize_database(self):
        """Initialize the behavioral analysis database."""
        try:
            os.makedirs(os.path.dirname(self.config.BEHAVIORAL_DB_PATH), exist_ok=True)
            self._db_connection = sqlite3.connect(
                self.config.BEHAVIORAL_DB_PATH,
                check_same_thread=False
            )
            
            self._create_behavioral_tables()
            self.logger.info("Behavioral analysis database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize behavioral database: {e}")
            raise
    
    def _create_behavioral_tables(self):
        """Create behavioral analysis database tables."""
        cursor = self._db_connection.cursor()
        
        # User behaviors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                behavior_type TEXT NOT NULL,
                features TEXT NOT NULL,
                metadata TEXT,
                session_id TEXT,
                source_ip TEXT,
                user_agent TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Behavioral anomalies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavioral_anomalies (
                anomaly_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                description TEXT NOT NULL,
                features_analysis TEXT NOT NULL,
                baseline_comparison TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                baseline_features TEXT NOT NULL,
                risk_score REAL NOT NULL DEFAULT 0.0,
                total_behaviors INTEGER NOT NULL DEFAULT 0,
                anomaly_count INTEGER NOT NULL DEFAULT 0,
                model_version TEXT
            )
        """)
        
        # Analysis metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavioral_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                user_id TEXT,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self._db_connection.commit()
    
    def start(self) -> bool:
        """Start the behavioral analysis engine."""
        try:
            self.status_manager.start("Starting behavioral analysis engine...")
            
            # Start analysis thread
            self.is_active = True
            self._analysis_thread = threading.Thread(
                target=self._analysis_loop,
                daemon=True
            )
            self._analysis_thread.start()
            
            # Start profile update thread
            self._profile_update_thread = threading.Thread(
                target=self._profile_update_loop,
                daemon=True
            )
            self._profile_update_thread.start()
            
            # Update memory usage
            self._update_memory_usage()
            
            self.status_manager.stop("Behavioral analysis engine started")
            self.logger.info("Behavioral analysis engine started")
            return True
            
        except Exception as e:
            self.status_manager.stop(f"Failed to start behavioral analysis: {e}")
            self.logger.error(f"Failed to start behavioral analysis: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the behavioral analysis engine."""
        try:
            self.status_manager.start("Stopping behavioral analysis engine...")
            
            # Signal shutdown
            self.is_active = False
            self._shutdown_event.set()
            
            # Wait for threads
            if self._analysis_thread:
                self._analysis_thread.join(timeout=5.0)
            if self._profile_update_thread:
                self._profile_update_thread.join(timeout=5.0)
            
            # Save models
            self._save_models()
            
            # Close database
            if self._db_connection:
                self._db_connection.close()
                self._db_connection = None
            
            self.status_manager.stop("Behavioral analysis engine stopped")
            self.logger.info("Behavioral analysis engine stopped")
            return True
            
        except Exception as e:
            self.status_manager.stop(f"Error stopping behavioral analysis: {e}")
            self.logger.error(f"Error stopping behavioral analysis: {e}")
            return False
    
    def analyze_behavior(self, behavior: UserBehavior) -> Optional[BehavioralAnomaly]:
        """
        Analyze user behavior for anomalies.
        
        Args:
            behavior: User behavior data to analyze
            
        Returns:
            BehavioralAnomaly if anomaly detected, None otherwise
        """
        start_time = time.time()
        
        try:
            # Store behavior
            self._recent_behaviors.append(behavior)
            self._store_behavior(behavior)
            
            # Get or create user profile
            profile = self._get_or_create_profile(behavior.user_id)
            
            # Check if we have enough data for analysis
            if profile.total_behaviors < self.config.MINIMUM_BEHAVIORS_FOR_PROFILE:
                # Accumulate behaviors for baseline
                self._update_profile_baseline(profile, behavior)
                return None
            
            # Perform anomaly detection
            anomaly = self._detect_behavioral_anomaly(behavior, profile)
            
            if anomaly:
                # Store anomaly
                self._recent_anomalies.append(anomaly)
                self._store_anomaly(anomaly)
                
                # Update profile risk score
                self._update_risk_score(profile, anomaly)
                
                self.logger.warning(
                    f"Behavioral anomaly detected for user {behavior.user_id}: "
                    f"{anomaly.anomaly_type.value} (confidence: {anomaly.confidence_score:.2f})"
                )
            
            # Update statistics
            self._behaviors_analyzed += 1
            analysis_time = (time.time() - start_time) * 1000
            self._analysis_times.append(analysis_time)
            
            return anomaly
            
        except Exception as e:
            self.logger.error(f"Error analyzing behavior: {e}")
            return None
    
    def _detect_behavioral_anomaly(
        self, 
        behavior: UserBehavior, 
        profile: UserProfile
    ) -> Optional[BehavioralAnomaly]:
        """Detect anomalies in user behavior."""
        try:
            behavior_type = behavior.behavior_type
            
            # Extract features for analysis
            features = self._extract_analysis_features(behavior)
            
            # Get baseline for comparison
            baseline = profile.baseline_features.get(behavior_type.value, {})
            if not baseline:
                return None
            
            # Calculate anomaly scores using multiple methods
            anomaly_scores = []
            
            # Statistical anomaly detection
            stat_score = self._statistical_anomaly_detection(features, baseline)
            anomaly_scores.append(stat_score)
            
            # ML-based anomaly detection
            if behavior_type.value in self._isolation_forests:
                ml_score = self._ml_anomaly_detection(features, behavior_type)
                anomaly_scores.append(ml_score)
            
            # Temporal pattern analysis
            temporal_score = self._temporal_anomaly_detection(behavior, profile)
            anomaly_scores.append(temporal_score)
            
            # Calculate overall anomaly score
            overall_score = max(anomaly_scores) if anomaly_scores else 0.0
            
            if overall_score > self.config.ANOMALY_THRESHOLD:
                # Determine anomaly type
                anomaly_type = self._classify_anomaly_type(behavior, features, baseline)
                
                # Assess risk level
                risk_level = self._assess_risk_level(overall_score, anomaly_type)
                
                # Create anomaly
                anomaly = BehavioralAnomaly(
                    anomaly_id=self._generate_anomaly_id(),
                    user_id=behavior.user_id,
                    timestamp=behavior.timestamp,
                    anomaly_type=anomaly_type,
                    risk_level=risk_level,
                    confidence_score=overall_score,
                    description=self._generate_anomaly_description(
                        anomaly_type, features, baseline
                    ),
                    features_analysis=features,
                    baseline_comparison=baseline,
                    recommended_actions=self._generate_recommendations(
                        anomaly_type, risk_level
                    )
                )
                
                return anomaly
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting behavioral anomaly: {e}")
            return None
    
    def _statistical_anomaly_detection(
        self, 
        features: Dict[str, float], 
        baseline: Dict[str, float]
    ) -> float:
        """Statistical anomaly detection using z-scores."""
        try:
            anomaly_scores = []
            
            for feature_name, value in features.items():
                if feature_name in baseline:
                    mean = baseline.get(f"{feature_name}_mean", 0.0)
                    std = baseline.get(f"{feature_name}_std", 1.0)
                    
                    # Calculate z-score
                    z_score = abs(value - mean) / max(std, 0.01)  # Avoid division by zero
                    
                    # Convert to anomaly score (0-1)
                    anomaly_score = min(z_score / 3.0, 1.0)  # 3-sigma rule
                    anomaly_scores.append(anomaly_score)
            
            return max(anomaly_scores) if anomaly_scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error in statistical anomaly detection: {e}")
            return 0.0
    
    def _ml_anomaly_detection(
        self, 
        features: Dict[str, float], 
        behavior_type: BehaviorType
    ) -> float:
        """ML-based anomaly detection using Isolation Forest."""
        try:
            model_key = behavior_type.value
            
            if model_key not in self._isolation_forests:
                return 0.0
            
            model = self._isolation_forests[model_key]
            scaler = self._scalers.get(model_key)
            
            # Prepare features
            feature_vector = np.array([list(features.values())]).reshape(1, -1)
            
            # Scale features if scaler available
            if scaler:
                feature_vector = scaler.transform(feature_vector)
            
            # Predict anomaly score
            anomaly_score = model.decision_function(feature_vector)[0]
            
            # Convert to 0-1 range (negative scores indicate anomalies)
            normalized_score = max(0.0, -anomaly_score)
            return min(normalized_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error in ML anomaly detection: {e}")
            return 0.0
    
    def _temporal_anomaly_detection(
        self, 
        behavior: UserBehavior, 
        profile: UserProfile
    ) -> float:
        """Temporal pattern anomaly detection."""
        try:
            # Analyze time-based patterns
            current_hour = behavior.timestamp.hour
            current_day = behavior.timestamp.weekday()
            
            # Get temporal baseline
            temporal_baseline = profile.baseline_features.get('temporal_patterns', {})
            
            # Check hour-of-day pattern
            typical_hours = temporal_baseline.get('typical_hours', [])
            hour_anomaly = 0.5 if current_hour not in typical_hours else 0.0
            
            # Check day-of-week pattern
            typical_days = temporal_baseline.get('typical_days', [])
            day_anomaly = 0.3 if current_day not in typical_days else 0.0
            
            # Check session frequency
            session_frequency = temporal_baseline.get('session_frequency', 1.0)
            recent_session_count = self._count_recent_sessions(behavior.user_id)
            frequency_anomaly = min(
                abs(recent_session_count - session_frequency) / max(session_frequency, 1.0),
                1.0
            ) * 0.4
            
            return max(hour_anomaly, day_anomaly, frequency_anomaly)
            
        except Exception as e:
            self.logger.error(f"Error in temporal anomaly detection: {e}")
            return 0.0
    
    def _classify_anomaly_type(
        self, 
        behavior: UserBehavior, 
        features: Dict[str, float], 
        baseline: Dict[str, float]
    ) -> AnomalyType:
        """Classify the type of behavioral anomaly."""
        try:
            # Check for temporal anomalies
            current_hour = behavior.timestamp.hour
            if current_hour < 6 or current_hour > 22:  # Outside normal hours
                return AnomalyType.TEMPORAL_ANOMALY
            
            # Check for volume anomalies
            data_volume = features.get('data_volume', 0.0)
            baseline_volume = baseline.get('data_volume_mean', 0.0)
            if data_volume > baseline_volume * 3:  # 3x normal volume
                return AnomalyType.VOLUME_ANOMALY
            
            # Check for access pattern deviations
            access_count = features.get('access_count', 0.0)
            baseline_access = baseline.get('access_count_mean', 0.0)
            if access_count > baseline_access * 2:
                return AnomalyType.ACCESS_ESCALATION
            
            # Check for location anomalies
            if behavior.source_ip and 'source_ip' in features:
                return AnomalyType.SPATIAL_ANOMALY
            
            # Default to pattern deviation
            return AnomalyType.PATTERN_DEVIATION
            
        except Exception as e:
            self.logger.error(f"Error classifying anomaly type: {e}")
            return AnomalyType.PATTERN_DEVIATION
    
    def _assess_risk_level(self, confidence_score: float, anomaly_type: AnomalyType) -> RiskLevel:
        """Assess risk level based on confidence and anomaly type."""
        # Risk multipliers for different anomaly types
        risk_multipliers = {
            AnomalyType.ACCESS_ESCALATION: 1.5,
            AnomalyType.DATA_HOARDING: 1.4,
            AnomalyType.VOLUME_ANOMALY: 1.3,
            AnomalyType.SPATIAL_ANOMALY: 1.2,
            AnomalyType.TEMPORAL_ANOMALY: 1.0,
            AnomalyType.PATTERN_DEVIATION: 1.0,
            AnomalyType.DEVICE_ANOMALY: 1.1,
            AnomalyType.UNUSUAL_LOCATION: 1.2
        }
        
        adjusted_score = confidence_score * risk_multipliers.get(anomaly_type, 1.0)
        
        if adjusted_score >= 0.9:
            return RiskLevel.CRITICAL
        elif adjusted_score >= 0.7:
            return RiskLevel.HIGH
        elif adjusted_score >= 0.5:
            return RiskLevel.MEDIUM
        elif adjusted_score >= 0.3:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    def _extract_analysis_features(self, behavior: UserBehavior) -> Dict[str, float]:
        """Extract features for anomaly analysis."""
        features = behavior.features.copy()
        
        # Add temporal features
        features['hour_of_day'] = float(behavior.timestamp.hour)
        features['day_of_week'] = float(behavior.timestamp.weekday())
        
        # Add session-based features
        if behavior.session_id:
            features['session_activity'] = self._calculate_session_activity(behavior.session_id)
        
        # Add IP-based features
        if behavior.source_ip:
            features['ip_reputation'] = self._calculate_ip_reputation(behavior.source_ip)
        
        return features
    
    def _calculate_session_activity(self, session_id: str) -> float:
        """Calculate activity level for a session."""
        # Count behaviors in this session
        session_behaviors = [
            b for b in self._recent_behaviors 
            if b.session_id == session_id
        ]
        return float(len(session_behaviors))
    
    def _calculate_ip_reputation(self, ip_address: str) -> float:
        """Calculate IP reputation score (simplified)."""
        # In practice, this would check against threat intelligence
        # For now, return neutral score
        return 0.5
    
    def _count_recent_sessions(self, user_id: str) -> int:
        """Count recent sessions for a user."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        sessions = set()
        
        for behavior in self._recent_behaviors:
            if (behavior.user_id == user_id and 
                behavior.timestamp >= cutoff_time and
                behavior.session_id):
                sessions.add(behavior.session_id)
        
        return len(sessions)
    
    def _get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile."""
        if user_id not in self._user_profiles:
            # Try to load from database
            profile = self._load_user_profile(user_id)
            if not profile:
                # Create new profile
                profile = UserProfile(
                    user_id=user_id,
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
            
            self._user_profiles[user_id] = profile
        
        return self._user_profiles[user_id]
    
    def _update_profile_baseline(self, profile: UserProfile, behavior: UserBehavior):
        """Update profile baseline with new behavior."""
        try:
            behavior_type = behavior.behavior_type.value
            
            # Initialize baseline if needed
            if behavior_type not in profile.baseline_features:
                profile.baseline_features[behavior_type] = {}
            
            baseline = profile.baseline_features[behavior_type]
            features = self._extract_analysis_features(behavior)
            
            # Update running statistics for each feature
            for feature_name, value in features.items():
                mean_key = f"{feature_name}_mean"
                std_key = f"{feature_name}_std"
                count_key = f"{feature_name}_count"
                
                # Get current statistics
                current_mean = baseline.get(mean_key, 0.0)
                current_std = baseline.get(std_key, 0.0)
                current_count = baseline.get(count_key, 0)
                
                # Update using online algorithm
                new_count = current_count + 1
                new_mean = current_mean + (value - current_mean) / new_count
                
                if new_count > 1:
                    new_std = np.sqrt(
                        ((current_count - 1) * current_std**2 + 
                         (value - current_mean) * (value - new_mean)) / (new_count - 1)
                    )
                else:
                    new_std = 0.0
                
                # Update baseline
                baseline[mean_key] = new_mean
                baseline[std_key] = new_std
                baseline[count_key] = new_count
            
            # Update temporal patterns
            self._update_temporal_patterns(profile, behavior)
            
            # Update profile
            profile.total_behaviors += 1
            profile.last_updated = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error updating profile baseline: {e}")
    
    def _update_temporal_patterns(self, profile: UserProfile, behavior: UserBehavior):
        """Update temporal patterns in profile."""
        try:
            if 'temporal_patterns' not in profile.baseline_features:
                profile.baseline_features['temporal_patterns'] = {
                    'typical_hours': [],
                    'typical_days': [],
                    'session_frequency': 0.0
                }
            
            temporal = profile.baseline_features['temporal_patterns']
            
            # Update typical hours
            hour = behavior.timestamp.hour
            typical_hours = temporal.get('typical_hours', [])
            if hour not in typical_hours:
                typical_hours.append(hour)
                temporal['typical_hours'] = typical_hours[-24:]  # Keep last 24 unique hours
            
            # Update typical days
            day = behavior.timestamp.weekday()
            typical_days = temporal.get('typical_days', [])
            if day not in typical_days:
                typical_days.append(day)
                temporal['typical_days'] = typical_days[-7:]  # Keep last 7 unique days
            
            # Update session frequency (simplified)
            temporal['session_frequency'] = temporal.get('session_frequency', 0.0) * 0.9 + 0.1
            
        except Exception as e:
            self.logger.error(f"Error updating temporal patterns: {e}")
    
    def _update_risk_score(self, profile: UserProfile, anomaly: BehavioralAnomaly):
        """Update user risk score based on anomaly."""
        try:
            # Risk score impact based on anomaly risk level
            risk_impacts = {
                RiskLevel.VERY_LOW: 0.1,
                RiskLevel.LOW: 0.2,
                RiskLevel.MEDIUM: 0.4,
                RiskLevel.HIGH: 0.6,
                RiskLevel.CRITICAL: 0.8
            }
            
            impact = risk_impacts.get(anomaly.risk_level, 0.1)
            
            # Update with exponential moving average
            profile.risk_score = profile.risk_score * 0.8 + impact * 0.2
            profile.anomaly_count += 1
            
            # Decay risk score over time
            hours_since_update = (datetime.now() - profile.last_updated).total_seconds() / 3600
            decay_factor = max(0.95 ** (hours_since_update / 24), 0.5)  # Daily decay
            profile.risk_score *= decay_factor
            
        except Exception as e:
            self.logger.error(f"Error updating risk score: {e}")
    
    def _generate_anomaly_description(
        self, 
        anomaly_type: AnomalyType, 
        features: Dict[str, float], 
        baseline: Dict[str, float]
    ) -> str:
        """Generate human-readable anomaly description."""
        descriptions = {
            AnomalyType.TEMPORAL_ANOMALY: "Unusual access time detected",
            AnomalyType.VOLUME_ANOMALY: "Abnormal data volume accessed",
            AnomalyType.ACCESS_ESCALATION: "Increased access frequency detected",
            AnomalyType.SPATIAL_ANOMALY: "Access from unusual location",
            AnomalyType.PATTERN_DEVIATION: "Deviation from normal behavior pattern",
            AnomalyType.DATA_HOARDING: "Excessive data collection behavior",
            AnomalyType.DEVICE_ANOMALY: "Access from unusual device",
            AnomalyType.UNUSUAL_LOCATION: "Geographic location anomaly"
        }
        
        base_description = descriptions.get(anomaly_type, "Behavioral anomaly detected")
        
        # Add specific details based on features
        details = []
        for feature_name, value in features.items():
            baseline_mean = baseline.get(f"{feature_name}_mean", 0.0)
            if abs(value - baseline_mean) > baseline_mean * 0.5:
                details.append(f"{feature_name}: {value:.2f} (baseline: {baseline_mean:.2f})")
        
        if details:
            return f"{base_description}. Details: {', '.join(details[:3])}"
        
        return base_description
    
    def _generate_recommendations(
        self, 
        anomaly_type: AnomalyType, 
        risk_level: RiskLevel
    ) -> List[str]:
        """Generate recommended actions for anomaly."""
        recommendations = []
        
        # Base recommendations by anomaly type
        type_recommendations = {
            AnomalyType.TEMPORAL_ANOMALY: [
                "Verify user identity through additional authentication",
                "Review access logs for the time period"
            ],
            AnomalyType.VOLUME_ANOMALY: [
                "Monitor data export activities",
                "Review data access permissions"
            ],
            AnomalyType.ACCESS_ESCALATION: [
                "Audit privilege escalation attempts",
                "Review user access permissions"
            ],
            AnomalyType.SPATIAL_ANOMALY: [
                "Verify user location through additional means",
                "Consider geographic access restrictions"
            ]
        }
        
        recommendations.extend(type_recommendations.get(anomaly_type, []))
        
        # Additional recommendations based on risk level
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.extend([
                "Escalate to security team",
                "Consider temporary access restriction",
                "Initiate detailed investigation"
            ])
        
        return recommendations
    
    def _initialize_models(self):
        """Initialize machine learning models."""
        try:
            os.makedirs(self.config.MODEL_CACHE_PATH, exist_ok=True)
            
            # Initialize models for each behavior type
            for behavior_type in BehaviorType:
                model_key = behavior_type.value
                
                # Initialize Isolation Forest
                self._isolation_forests[model_key] = IsolationForest(
                    contamination=self.config.ISOLATION_FOREST_CONTAMINATION,
                    random_state=42,
                    n_jobs=1  # Single thread for memory efficiency
                )
                
                # Initialize scaler
                self._scalers[model_key] = StandardScaler()
                
                # Initialize feature buffer
                self._feature_buffers[model_key] = collections.deque(
                    maxlen=self.config.FEATURE_SCALING_WINDOW
                )
            
            self.logger.info("ML models initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {e}")
    
    def _analysis_loop(self):
        """Main analysis loop for continuous processing."""
        while self.is_active and not self._shutdown_event.is_set():
            try:
                # Update memory usage
                self._update_memory_usage()
                
                # Train models with recent data
                self._update_models()
                
                # Clean up old data
                self._cleanup_old_data()
                
                # Sleep for analysis interval
                self._shutdown_event.wait(60)  # 1 minute
                
            except Exception as e:
                self.logger.error(f"Error in analysis loop: {e}")
                self._shutdown_event.wait(5)
    
    def _profile_update_loop(self):
        """Profile update loop for periodic maintenance."""
        while self.is_active and not self._shutdown_event.is_set():
            try:
                # Update user profiles
                for profile in self._user_profiles.values():
                    self._save_user_profile(profile)
                
                # Sleep for profile update interval
                self._shutdown_event.wait(self.config.PROFILE_UPDATE_INTERVAL_HOURS * 3600)
                
            except Exception as e:
                self.logger.error(f"Error in profile update loop: {e}")
                self._shutdown_event.wait(60)
    
    def _update_models(self):
        """Update ML models with recent data."""
        try:
            for behavior_type in BehaviorType:
                model_key = behavior_type.value
                buffer = self._feature_buffers[model_key]
                
                if len(buffer) >= 100:  # Minimum data for training
                    # Prepare training data
                    X = np.array(list(buffer))
                    
                    # Update scaler
                    scaler = self._scalers[model_key]
                    X_scaled = scaler.fit_transform(X)
                    
                    # Update model
                    model = self._isolation_forests[model_key]
                    model.fit(X_scaled)
                    
                    # Clear buffer to free memory
                    buffer.clear()
            
        except Exception as e:
            self.logger.error(f"Error updating models: {e}")
    
    def _save_models(self):
        """Save trained models to disk."""
        try:
            for behavior_type in BehaviorType:
                model_key = behavior_type.value
                
                # Save isolation forest
                model_path = os.path.join(
                    self.config.MODEL_CACHE_PATH, 
                    f"isolation_forest_{model_key}.joblib"
                )
                joblib.dump(self._isolation_forests[model_key], model_path)
                
                # Save scaler
                scaler_path = os.path.join(
                    self.config.MODEL_CACHE_PATH,
                    f"scaler_{model_key}.joblib"
                )
                joblib.dump(self._scalers[model_key], scaler_path)
            
            self.logger.info("Models saved to disk")
            
        except Exception as e:
            self.logger.error(f"Error saving models: {e}")
    
    def _load_user_profiles(self):
        """Load user profiles from database."""
        try:
            cursor = self._db_connection.cursor()
            cursor.execute("SELECT * FROM user_profiles")
            
            for row in cursor.fetchall():
                profile = UserProfile(
                    user_id=row[0],
                    created_at=datetime.fromisoformat(row[1]),
                    last_updated=datetime.fromisoformat(row[2]),
                    baseline_features=json.loads(row[3]),
                    risk_score=row[4],
                    total_behaviors=row[5],
                    anomaly_count=row[6]
                )
                self._user_profiles[profile.user_id] = profile
            
            self.logger.info(f"Loaded {len(self._user_profiles)} user profiles")
            
        except Exception as e:
            self.logger.error(f"Error loading user profiles: {e}")
    
    def _load_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load specific user profile from database."""
        try:
            cursor = self._db_connection.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return UserProfile(
                    user_id=row[0],
                    created_at=datetime.fromisoformat(row[1]),
                    last_updated=datetime.fromisoformat(row[2]),
                    baseline_features=json.loads(row[3]),
                    risk_score=row[4],
                    total_behaviors=row[5],
                    anomaly_count=row[6]
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading user profile {user_id}: {e}")
            return None
    
    def _save_user_profile(self, profile: UserProfile):
        """Save user profile to database."""
        try:
            cursor = self._db_connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_profiles 
                (user_id, created_at, last_updated, baseline_features, 
                 risk_score, total_behaviors, anomaly_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.user_id,
                profile.created_at.isoformat(),
                profile.last_updated.isoformat(),
                json.dumps(profile.baseline_features),
                profile.risk_score,
                profile.total_behaviors,
                profile.anomaly_count
            ))
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error saving user profile: {e}")
    
    def _store_behavior(self, behavior: UserBehavior):
        """Store behavior in database."""
        try:
            cursor = self._db_connection.cursor()
            cursor.execute("""
                INSERT INTO user_behaviors 
                (user_id, timestamp, behavior_type, features, metadata, 
                 session_id, source_ip, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                behavior.user_id,
                behavior.timestamp.isoformat(),
                behavior.behavior_type.value,
                json.dumps(behavior.features),
                json.dumps(behavior.metadata),
                behavior.session_id,
                behavior.source_ip,
                behavior.user_agent
            ))
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing behavior: {e}")
    
    def _store_anomaly(self, anomaly: BehavioralAnomaly):
        """Store anomaly in database."""
        try:
            cursor = self._db_connection.cursor()
            cursor.execute("""
                INSERT INTO behavioral_anomalies 
                (anomaly_id, user_id, timestamp, anomaly_type, risk_level, 
                 confidence_score, description, features_analysis, baseline_comparison)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                anomaly.anomaly_id,
                anomaly.user_id,
                anomaly.timestamp.isoformat(),
                anomaly.anomaly_type.value,
                anomaly.risk_level.value,
                anomaly.confidence_score,
                anomaly.description,
                json.dumps(anomaly.features_analysis),
                json.dumps(anomaly.baseline_comparison)
            ))
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing anomaly: {e}")
    
    def _generate_anomaly_id(self) -> str:
        """Generate unique anomaly ID."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{timestamp}_{self._anomalies_detected}_{id(self)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _update_memory_usage(self):
        """Update current memory usage estimate."""
        try:
            # Estimate memory usage
            profiles_memory = len(self._user_profiles) * 0.1  # ~100KB per profile
            behaviors_memory = len(self._recent_behaviors) * 0.005  # ~5KB per behavior
            anomalies_memory = len(self._recent_anomalies) * 0.003  # ~3KB per anomaly
            models_memory = len(self._isolation_forests) * 2.0  # ~2MB per model
            base_memory = 3.0  # Base overhead
            
            self.memory_usage_mb = (
                profiles_memory + behaviors_memory + anomalies_memory + 
                models_memory + base_memory
            )
            
        except Exception as e:
            self.logger.error(f"Error updating memory usage: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data to free memory."""
        try:
            # Clean old behaviors from database
            cutoff_date = datetime.now() - timedelta(days=self.config.BEHAVIOR_RETENTION_DAYS)
            cursor = self._db_connection.cursor()
            cursor.execute(
                "DELETE FROM user_behaviors WHERE timestamp < ?",
                (cutoff_date.isoformat(),)
            )
            
            # Clean old anomalies
            anomaly_cutoff = datetime.now() - timedelta(days=self.config.ANOMALY_RETENTION_DAYS)
            cursor.execute(
                "DELETE FROM behavioral_anomalies WHERE timestamp < ?",
                (anomaly_cutoff.isoformat(),)
            )
            
            # Limit in-memory profiles
            if len(self._user_profiles) > self.config.MAX_PROFILES_IN_MEMORY:
                # Remove least recently updated profiles
                sorted_profiles = sorted(
                    self._user_profiles.items(),
                    key=lambda x: x[1].last_updated
                )
                
                profiles_to_remove = len(self._user_profiles) - self.config.MAX_PROFILES_IN_MEMORY // 2
                for i in range(profiles_to_remove):
                    user_id, profile = sorted_profiles[i]
                    self._save_user_profile(profile)  # Save before removing
                    del self._user_profiles[user_id]
            
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.memory_usage_mb
    
    def cleanup_memory(self):
        """External interface for memory cleanup."""
        self._cleanup_old_data()
        gc.collect()
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get behavioral analysis statistics."""
        return {
            'behaviors_analyzed': self._behaviors_analyzed,
            'anomalies_detected': self._anomalies_detected,
            'user_profiles': len(self._user_profiles),
            'recent_behaviors': len(self._recent_behaviors),
            'recent_anomalies': len(self._recent_anomalies),
            'memory_usage_mb': self.memory_usage_mb,
            'avg_analysis_time_ms': (
                sum(self._analysis_times) / len(self._analysis_times)
                if self._analysis_times else 0.0
            )
        }
    
    def get_user_risk_scores(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get users with highest risk scores."""
        sorted_profiles = sorted(
            self._user_profiles.values(),
            key=lambda p: p.risk_score,
            reverse=True
        )
        
        return [
            {
                'user_id': profile.user_id,
                'risk_score': profile.risk_score,
                'anomaly_count': profile.anomaly_count,
                'total_behaviors': profile.total_behaviors,
                'last_updated': profile.last_updated.isoformat()
            }
            for profile in sorted_profiles[:limit]
        ]
    
    def get_recent_anomalies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent behavioral anomalies."""
        anomalies = list(self._recent_anomalies)[-limit:]
        return [
            {
                'anomaly_id': anomaly.anomaly_id,
                'user_id': anomaly.user_id,
                'timestamp': anomaly.timestamp.isoformat(),
                'anomaly_type': anomaly.anomaly_type.value,
                'risk_level': anomaly.risk_level.value,
                'confidence_score': anomaly.confidence_score,
                'description': anomaly.description
            }
            for anomaly in anomalies
        ]


# Export main classes and functions
__all__ = [
    'BehavioralAnalysisEngine',
    'UserBehavior',
    'BehavioralAnomaly',
    'UserProfile',
    'BehaviorType',
    'AnomalyType',
    'RiskLevel'
]
