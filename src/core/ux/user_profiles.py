"""
Intelligent User Profiles System for ImpressionCore

This module provides adaptive user preference learning, usage pattern analysis,
and predictive optimization suggestions based on individual user behavior.

Key Features:
- ML-based user preference learning and adaptation
- Usage pattern analysis with behavioral clustering
- Performance history tracking and correlation analysis
- Predictive optimization suggestions
- Privacy-preserving local analytics

Hardware Target: GTX 1050 Ti (4GB VRAM) with scalable profile complexity
"""

import time
import json
import sqlite3
import hashlib
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import numpy as np
from collections import defaultdict, deque
import threading
from datetime import datetime, timedelta

# Machine learning imports (lightweight)
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.ensemble import RandomForestRegressor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    KMeans = None
    StandardScaler = None
    PCA = None
    RandomForestRegressor = None

# Import rich enhancements
try:
    from ..utils.rich_enhancements import create_enhanced_console
    from ..utils.rich_logging import setup_rich_logging
    from ..utils.rich_status_animation import create_status_animation
except ImportError:
    create_enhanced_console = lambda: None
    setup_rich_logging = lambda x: None
    create_status_animation = lambda x: None


class UserPersonality(str, Enum):
    """User personality profiles based on usage patterns."""
    POWER_USER = "power_user"           # Maximum performance, willing to wait
    BALANCED = "balanced"               # Balance of speed and quality
    SPEED_FOCUSED = "speed_focused"     # Prioritizes speed over quality
    QUALITY_FOCUSED = "quality_focused" # Prioritizes quality over speed
    CASUAL = "casual"                   # Simple, easy-to-use defaults
    EXPERIMENTAL = "experimental"       # Likes to try new features


class WorkloadType(str, Enum):
    """Common workload types for pattern recognition."""
    CREATIVE_WRITING = "creative_writing"
    TECHNICAL_ANALYSIS = "technical_analysis"
    CODE_GENERATION = "code_generation"
    RESEARCH_ASSISTANCE = "research_assistance"
    CASUAL_CHAT = "casual_chat"
    DOCUMENT_PROCESSING = "document_processing"
    MIXED_WORKLOAD = "mixed_workload"


class UsageContext(str, Enum):
    """Usage context for adaptive behavior."""
    FOCUSED_WORK = "focused_work"       # User is focused, can wait for quality
    QUICK_TASK = "quick_task"           # User needs fast results
    EXPLORATORY = "exploratory"        # User is exploring/experimenting
    BATCH_PROCESSING = "batch_processing"  # Processing multiple items
    INTERACTIVE = "interactive"        # Real-time conversation
    BACKGROUND = "background"          # Background/automated task


@dataclass
class UserSession:
    """Individual user session data."""
    session_id: str
    user_id: str
    start_time: float
    end_time: Optional[float] = None
    workload_type: WorkloadType = WorkloadType.MIXED_WORKLOAD
    usage_context: UsageContext = UsageContext.INTERACTIVE
    
    # Session metrics
    total_tokens_processed: int = 0
    average_latency_ms: float = 0.0
    quality_scores: List[float] = field(default_factory=list)
    memory_usage_peak_gb: float = 0.0
    user_satisfaction_rating: Optional[float] = None
    
    # Configuration used
    resolution_level: str = "adaptive"
    generation_strategy: str = "adaptive_parallel"
    memory_limit_gb: float = 3.8
    target_latency_ms: float = 200.0
    
    # User behavior
    manual_adjustments: List[Dict[str, Any]] = field(default_factory=list)
    feature_usage: Dict[str, int] = field(default_factory=dict)
    error_encounters: List[Dict[str, Any]] = field(default_factory=list)
    
    # Context information
    time_of_day: int = 0  # Hour of day (0-23)
    day_of_week: int = 0  # Day of week (0-6)
    session_duration_minutes: float = 0.0


@dataclass
class UserProfile:
    """Comprehensive user profile with learning capabilities."""
    user_id: str
    created_timestamp: float
    last_updated: float
    
    # Personality and preferences
    personality_type: UserPersonality = UserPersonality.BALANCED
    confidence_score: float = 0.5  # How confident we are in the personality classification
    
    # Learned preferences
    preferred_quality_threshold: float = 0.95
    preferred_latency_ms: float = 200.0
    preferred_memory_usage_percent: float = 80.0
    quality_vs_speed_preference: float = 0.5  # 0=speed, 1=quality
    
    # Usage patterns
    primary_workload_types: List[WorkloadType] = field(default_factory=list)
    common_usage_contexts: List[UsageContext] = field(default_factory=list)
    peak_usage_hours: List[int] = field(default_factory=list)
    average_session_duration_minutes: float = 30.0
    
    # Performance patterns
    quality_satisfaction_history: List[float] = field(default_factory=list)
    latency_tolerance_ms: float = 500.0
    memory_sensitivity: float = 0.5  # 0=not sensitive, 1=very sensitive
    
    # Feature adoption
    feature_adoption_rate: float = 0.5  # How quickly user adopts new features
    manual_control_preference: float = 0.3  # How much user likes manual control
    automation_trust_level: float = 0.7  # How much user trusts automation
    
    # Learning metadata
    total_sessions: int = 0
    total_processing_time_hours: float = 0.0
    learning_momentum: float = 0.1  # How fast we adapt to new patterns
    last_personality_update: float = 0.0


@dataclass
class UsagePattern:
    """Detected usage pattern for behavioral clustering."""
    pattern_id: str
    description: str
    frequency: float  # How often this pattern occurs
    
    # Pattern characteristics
    typical_context: UsageContext
    typical_workload: WorkloadType
    typical_session_duration: float
    typical_quality_requirement: float
    typical_latency_tolerance: float
    
    # Performance characteristics
    optimal_configuration: Dict[str, Any]
    performance_metrics: Dict[str, float]
    user_satisfaction: float


class UserProfilesSystem:
    """
    Intelligent user profiles system with ML-based adaptation.
    
    Provides comprehensive user behavior analysis, preference learning,
    and predictive optimization based on usage patterns.
    """
    
    def __init__(self, data_directory: str = "user_profiles", enable_ml: bool = True):
        """
        Initialize the user profiles system.
        
        Args:
            data_directory: Directory to store user profile data
            enable_ml: Whether to enable machine learning features
        """
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
        
        self.enable_ml = enable_ml and ML_AVAILABLE
        if enable_ml and not ML_AVAILABLE:
            print("Warning: ML libraries not available, falling back to rule-based learning")
        
        # Database for persistent storage
        self.db_path = self.data_directory / "user_profiles.db"
        self._init_database()
        
        # In-memory caches
        self.active_profiles: Dict[str, UserProfile] = {}
        self.active_sessions: Dict[str, UserSession] = {}
        self.usage_patterns: Dict[str, List[UsagePattern]] = defaultdict(list)
        
        # ML models (if available)
        self.personality_classifier = None
        self.performance_predictor = None
        self.pattern_clusterer = None
        
        # Rich console and logging
        self.console = create_enhanced_console()
        self.logger = setup_rich_logging("user_profiles")
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Load existing profiles
        self._load_existing_profiles()
        
        # Initialize ML models
        if self.enable_ml:
            self._initialize_ml_models()
    
    def _init_database(self):
        """Initialize SQLite database for persistent storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    profile_data TEXT,
                    created_timestamp REAL,
                    last_updated REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    session_data TEXT,
                    start_time REAL,
                    end_time REAL,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    pattern_data TEXT,
                    frequency REAL,
                    last_seen REAL,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            conn.commit()
    
    def _load_existing_profiles(self):
        """Load existing user profiles from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT user_id, profile_data FROM user_profiles
                """)
                
                for user_id, profile_data in cursor.fetchall():
                    try:
                        profile_dict = json.loads(profile_data)
                        profile = UserProfile(**profile_dict)
                        self.active_profiles[user_id] = profile
                    except Exception as e:
                        if self.logger:
                            self.logger.warning(f"Failed to load profile for user {user_id}: {e}")
                
                if self.logger:
                    self.logger.info(f"Loaded {len(self.active_profiles)} user profiles")
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load profiles from database: {e}")
    
    def _initialize_ml_models(self):
        """Initialize machine learning models."""
        if not self.enable_ml:
            return
        
        try:
            # Personality classifier (will be trained with usage data)
            self.personality_classifier = RandomForestRegressor(
                n_estimators=50,
                max_depth=10,
                random_state=42
            )
            
            # Performance predictor
            self.performance_predictor = RandomForestRegressor(
                n_estimators=30,
                max_depth=8,
                random_state=42
            )
            
            # Pattern clusterer
            self.pattern_clusterer = KMeans(
                n_clusters=5,
                random_state=42,
                n_init=10
            )
            
            if self.logger:
                self.logger.info("ML models initialized successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to initialize ML models: {e}")
            self.enable_ml = False
    
    def create_user_profile(self, user_id: str, initial_preferences: Optional[Dict[str, Any]] = None) -> UserProfile:
        """
        Create a new user profile with optional initial preferences.
        
        Args:
            user_id: Unique user identifier
            initial_preferences: Optional initial preference settings
            
        Returns:
            Created user profile
        """
        with self.lock:
            if user_id in self.active_profiles:
                return self.active_profiles[user_id]
            
            # Create new profile
            now = time.time()
            profile = UserProfile(
                user_id=user_id,
                created_timestamp=now,
                last_updated=now
            )
            
            # Apply initial preferences if provided
            if initial_preferences:
                self._apply_initial_preferences(profile, initial_preferences)
            
            # Store in memory and database
            self.active_profiles[user_id] = profile
            self._save_profile_to_db(profile)
            
            if self.logger:
                self.logger.info(f"Created new user profile: {user_id}")
            
            return profile
    
    def _apply_initial_preferences(self, profile: UserProfile, preferences: Dict[str, Any]):
        """Apply initial user preferences to profile."""
        if "quality_vs_speed" in preferences:
            profile.quality_vs_speed_preference = float(preferences["quality_vs_speed"])
        
        if "personality_type" in preferences:
            try:
                profile.personality_type = UserPersonality(preferences["personality_type"])
            except ValueError:
                pass
        
        if "preferred_latency_ms" in preferences:
            profile.preferred_latency_ms = float(preferences["preferred_latency_ms"])
        
        if "preferred_quality_threshold" in preferences:
            profile.preferred_quality_threshold = float(preferences["preferred_quality_threshold"])
    
    def start_session(self, user_id: str, session_id: str, context: UsageContext = UsageContext.INTERACTIVE) -> UserSession:
        """
        Start a new user session.
        
        Args:
            user_id: User identifier
            session_id: Unique session identifier
            context: Usage context for the session
            
        Returns:
            Created user session
        """
        with self.lock:
            # Ensure user profile exists
            if user_id not in self.active_profiles:
                self.create_user_profile(user_id)
            
            # Create session
            now = time.time()
            dt = datetime.fromtimestamp(now)
            
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                start_time=now,
                usage_context=context,
                time_of_day=dt.hour,
                day_of_week=dt.weekday()
            )
            
            self.active_sessions[session_id] = session
            
            if self.logger:
                self.logger.debug(f"Started session {session_id} for user {user_id}")
            
            return session
    
    def end_session(self, session_id: str, user_satisfaction: Optional[float] = None) -> Optional[UserSession]:
        """
        End a user session and update profile with learned data.
        
        Args:
            session_id: Session identifier
            user_satisfaction: Optional user satisfaction rating (1-5)
            
        Returns:
            Ended session data
        """
        with self.lock:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            session.end_time = time.time()
            session.session_duration_minutes = (session.end_time - session.start_time) / 60.0
            
            if user_satisfaction is not None:
                session.user_satisfaction_rating = user_satisfaction
            
            # Update user profile with session data
            self._learn_from_session(session)
            
            # Save session to database
            self._save_session_to_db(session)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            if self.logger:
                self.logger.debug(f"Ended session {session_id}, duration: {session.session_duration_minutes:.1f} minutes")
            
            return session
    
    def update_session_metrics(self, session_id: str, metrics: Dict[str, Any]):
        """
        Update session metrics during active session.
        
        Args:
            session_id: Session identifier
            metrics: Dictionary of metrics to update
        """
        with self.lock:
            if session_id not in self.active_sessions:
                return
            
            session = self.active_sessions[session_id]
            
            # Update various metrics
            if "tokens_processed" in metrics:
                session.total_tokens_processed += metrics["tokens_processed"]
            
            if "latency_ms" in metrics:
                # Running average of latency
                if session.average_latency_ms == 0:
                    session.average_latency_ms = metrics["latency_ms"]
                else:
                    session.average_latency_ms = (session.average_latency_ms + metrics["latency_ms"]) / 2
            
            if "quality_score" in metrics:
                session.quality_scores.append(metrics["quality_score"])
            
            if "memory_usage_gb" in metrics:
                session.memory_usage_peak_gb = max(session.memory_usage_peak_gb, metrics["memory_usage_gb"])
            
            if "manual_adjustment" in metrics:
                session.manual_adjustments.append(metrics["manual_adjustment"])
            
            if "feature_used" in metrics:
                feature = metrics["feature_used"]
                session.feature_usage[feature] = session.feature_usage.get(feature, 0) + 1
            
            if "error" in metrics:
                session.error_encounters.append(metrics["error"])
    
    def _learn_from_session(self, session: UserSession):
        """Learn from completed session and update user profile."""
        if session.user_id not in self.active_profiles:
            return
        
        profile = self.active_profiles[session.user_id]
        
        # Update basic statistics
        profile.total_sessions += 1
        profile.total_processing_time_hours += session.session_duration_minutes / 60.0
        profile.last_updated = time.time()
        
        # Update average session duration
        alpha = min(0.3, 1.0 / profile.total_sessions)  # Adaptive learning rate
        profile.average_session_duration_minutes = (
            (1 - alpha) * profile.average_session_duration_minutes +
            alpha * session.session_duration_minutes
        )
        
        # Learn quality preferences
        if session.quality_scores:
            avg_quality = sum(session.quality_scores) / len(session.quality_scores)
            if session.user_satisfaction_rating and session.user_satisfaction_rating >= 4.0:
                # User was satisfied with this quality level
                profile.preferred_quality_threshold = (
                    (1 - alpha) * profile.preferred_quality_threshold +
                    alpha * avg_quality
                )
        
        # Learn latency tolerance
        if session.average_latency_ms > 0:
            satisfaction_factor = 1.0
            if session.user_satisfaction_rating:
                satisfaction_factor = session.user_satisfaction_rating / 5.0
            
            if satisfaction_factor >= 0.8:  # User was satisfied
                profile.latency_tolerance_ms = max(
                    profile.latency_tolerance_ms,
                    session.average_latency_ms
                )
        
        # Update usage patterns
        self._update_usage_patterns(profile, session)
        
        # Update personality classification
        self._update_personality_classification(profile, session)
        
        # Save updated profile
        self._save_profile_to_db(profile)
    
    def _update_usage_patterns(self, profile: UserProfile, session: UserSession):
        """Update usage patterns based on session data."""
        # Track workload types
        if session.workload_type not in profile.primary_workload_types:
            profile.primary_workload_types.append(session.workload_type)
        
        # Track usage contexts
        if session.usage_context not in profile.common_usage_contexts:
            profile.common_usage_contexts.append(session.usage_context)
        
        # Track peak usage hours
        hour = session.time_of_day
        if hour not in profile.peak_usage_hours:
            profile.peak_usage_hours.append(hour)
        
        # Keep lists manageable
        profile.primary_workload_types = profile.primary_workload_types[-5:]
        profile.common_usage_contexts = profile.common_usage_contexts[-5:]
        profile.peak_usage_hours = profile.peak_usage_hours[-10:]
    
    def _update_personality_classification(self, profile: UserProfile, session: UserSession):
        """Update personality classification based on session behavior."""
        # Rule-based personality inference
        manual_adjustments = len(session.manual_adjustments)
        total_features_used = sum(session.feature_usage.values())
        
        # Analyze behavior patterns
        high_manual_control = manual_adjustments > 3
        feature_explorer = total_features_used > 5
        quality_focused = (
            session.quality_scores and 
            sum(session.quality_scores) / len(session.quality_scores) > 0.9
        )
        speed_focused = session.average_latency_ms < 100
        
        # Infer personality traits
        new_personality = profile.personality_type
        
        if high_manual_control and feature_explorer:
            new_personality = UserPersonality.POWER_USER
        elif quality_focused and not speed_focused:
            new_personality = UserPersonality.QUALITY_FOCUSED
        elif speed_focused and not quality_focused:
            new_personality = UserPersonality.SPEED_FOCUSED
        elif feature_explorer:
            new_personality = UserPersonality.EXPERIMENTAL
        elif manual_adjustments == 0 and total_features_used <= 2:
            new_personality = UserPersonality.CASUAL
        else:
            new_personality = UserPersonality.BALANCED
        
        # Update personality with momentum
        if new_personality != profile.personality_type:
            # Require multiple sessions to confirm personality change
            time_since_last_update = time.time() - profile.last_personality_update
            if time_since_last_update > 3600:  # At least 1 hour
                profile.personality_type = new_personality
                profile.last_personality_update = time.time()
                profile.confidence_score = min(1.0, profile.confidence_score + 0.1)
    
    def get_optimization_recommendations(self, user_id: str, context: UsageContext = UsageContext.INTERACTIVE) -> Dict[str, Any]:
        """
        Get personalized optimization recommendations for a user.
        
        Args:
            user_id: User identifier
            context: Current usage context
            
        Returns:
            Optimization recommendations
        """
        if user_id not in self.active_profiles:
            # Return default recommendations for new users
            return self._get_default_recommendations()
        
        profile = self.active_profiles[user_id]
        
        # Base recommendations on personality type
        recommendations = self._get_personality_based_recommendations(profile.personality_type)
        
        # Customize based on learned preferences
        recommendations.update({
            "preferred_quality_threshold": profile.preferred_quality_threshold,
            "target_latency_ms": min(profile.preferred_latency_ms, profile.latency_tolerance_ms),
            "memory_usage_limit": profile.preferred_memory_usage_percent / 100.0,
        })
        
        # Context-specific adjustments
        if context == UsageContext.QUICK_TASK:
            recommendations["target_latency_ms"] *= 0.7  # Faster for quick tasks
            recommendations["preferred_quality_threshold"] *= 0.9  # Lower quality OK
        elif context == UsageContext.FOCUSED_WORK:
            recommendations["target_latency_ms"] *= 1.2  # Can wait longer
            recommendations["preferred_quality_threshold"] *= 1.05  # Higher quality
        elif context == UsageContext.BATCH_PROCESSING:
            recommendations["batch_size"] = min(4, recommendations.get("batch_size", 1) * 2)
        
        # Time-based adjustments
        current_hour = datetime.now().hour
        if current_hour in profile.peak_usage_hours:
            # User is active at this time, optimize for their preferences
            recommendations["enable_advanced_features"] = profile.feature_adoption_rate > 0.7
        
        return recommendations
    
    def _get_default_recommendations(self) -> Dict[str, Any]:
        """Get default recommendations for new users."""
        return {
            "resolution_level": "adaptive",
            "generation_strategy": "adaptive_parallel",
            "memory_limit_gb": 3.8,
            "target_latency_ms": 200.0,
            "preferred_quality_threshold": 0.95,
            "batch_size": 1,
            "enable_mixed_precision": True,
            "enable_cpu_offload": True,
            "enable_advanced_features": False
        }
    
    def _get_personality_based_recommendations(self, personality: UserPersonality) -> Dict[str, Any]:
        """Get recommendations based on personality type."""
        base_config = self._get_default_recommendations()
        
        if personality == UserPersonality.POWER_USER:
            base_config.update({
                "resolution_level": "ultra_high",
                "generation_strategy": "parallel",
                "target_latency_ms": 500.0,  # Willing to wait
                "preferred_quality_threshold": 0.98,
                "enable_advanced_features": True,
                "batch_size": 2
            })
        
        elif personality == UserPersonality.SPEED_FOCUSED:
            base_config.update({
                "resolution_level": "medium",
                "generation_strategy": "sequential",
                "target_latency_ms": 100.0,
                "preferred_quality_threshold": 0.85,
                "enable_cpu_offload": False,  # GPU only for speed
                "batch_size": 1
            })
        
        elif personality == UserPersonality.QUALITY_FOCUSED:
            base_config.update({
                "resolution_level": "ultra_high",
                "generation_strategy": "progressive_refinement",
                "target_latency_ms": 400.0,
                "preferred_quality_threshold": 0.99,
                "enable_advanced_features": True
            })
        
        elif personality == UserPersonality.CASUAL:
            base_config.update({
                "resolution_level": "adaptive",
                "generation_strategy": "adaptive_parallel",
                "target_latency_ms": 150.0,
                "preferred_quality_threshold": 0.90,
                "enable_advanced_features": False
            })
        
        elif personality == UserPersonality.EXPERIMENTAL:
            base_config.update({
                "resolution_level": "adaptive",
                "generation_strategy": "adaptive_parallel",
                "target_latency_ms": 200.0,
                "preferred_quality_threshold": 0.95,
                "enable_advanced_features": True,
                "enable_experimental_features": True
            })
        
        return base_config
    
    def predict_user_satisfaction(self, user_id: str, proposed_config: Dict[str, Any]) -> float:
        """
        Predict user satisfaction with a proposed configuration.
        
        Args:
            user_id: User identifier
            proposed_config: Configuration to evaluate
            
        Returns:
            Predicted satisfaction score (0-1)
        """
        if user_id not in self.active_profiles:
            return 0.7  # Default moderate satisfaction
        
        profile = self.active_profiles[user_id]
        
        # Rule-based satisfaction prediction
        satisfaction_score = 0.5
        
        # Quality preference matching
        proposed_quality = proposed_config.get("preferred_quality_threshold", 0.95)
        quality_diff = abs(proposed_quality - profile.preferred_quality_threshold)
        quality_satisfaction = max(0, 1 - quality_diff * 2)
        satisfaction_score += quality_satisfaction * 0.3
        
        # Latency preference matching
        proposed_latency = proposed_config.get("target_latency_ms", 200)
        if proposed_latency <= profile.latency_tolerance_ms:
            latency_satisfaction = 1.0
        else:
            latency_satisfaction = max(0, 1 - (proposed_latency - profile.latency_tolerance_ms) / 1000)
        satisfaction_score += latency_satisfaction * 0.3
        
        # Personality alignment
        personality_alignment = self._calculate_personality_alignment(
            profile.personality_type, proposed_config
        )
        satisfaction_score += personality_alignment * 0.4
        
        return min(1.0, max(0.0, satisfaction_score))
    
    def _calculate_personality_alignment(self, personality: UserPersonality, config: Dict[str, Any]) -> float:
        """Calculate how well configuration aligns with personality."""
        alignment = 0.5
        
        resolution = config.get("resolution_level", "adaptive")
        latency = config.get("target_latency_ms", 200)
        advanced_features = config.get("enable_advanced_features", False)
        
        if personality == UserPersonality.POWER_USER:
            if resolution in ["ultra_high", "high"] and advanced_features:
                alignment += 0.3
            if latency > 300:  # Willing to wait
                alignment += 0.2
        
        elif personality == UserPersonality.SPEED_FOCUSED:
            if latency < 150:
                alignment += 0.4
            if resolution in ["low", "medium"]:
                alignment += 0.1
        
        elif personality == UserPersonality.QUALITY_FOCUSED:
            if resolution in ["ultra_high", "high"]:
                alignment += 0.4
            if latency > 250:  # Quality over speed
                alignment += 0.1
        
        elif personality == UserPersonality.CASUAL:
            if resolution == "adaptive" and not advanced_features:
                alignment += 0.4
            if 100 < latency < 250:  # Reasonable speed
                alignment += 0.1
        
        return min(1.0, alignment)
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User analytics data
        """
        if user_id not in self.active_profiles:
            return {}
        
        profile = self.active_profiles[user_id]
        
        # Calculate usage statistics
        analytics = {
            "profile_summary": {
                "user_id": user_id,
                "personality_type": profile.personality_type.value,
                "confidence_score": profile.confidence_score,
                "total_sessions": profile.total_sessions,
                "total_hours": profile.total_processing_time_hours,
                "avg_session_duration": profile.average_session_duration_minutes
            },
            "preferences": {
                "quality_vs_speed": profile.quality_vs_speed_preference,
                "quality_threshold": profile.preferred_quality_threshold,
                "latency_tolerance": profile.latency_tolerance_ms,
                "memory_sensitivity": profile.memory_sensitivity,
                "feature_adoption_rate": profile.feature_adoption_rate,
                "automation_trust": profile.automation_trust_level
            },
            "usage_patterns": {
                "primary_workloads": [wl.value for wl in profile.primary_workload_types],
                "common_contexts": [ctx.value for ctx in profile.common_usage_contexts],
                "peak_hours": profile.peak_usage_hours,
                "recent_satisfaction": profile.quality_satisfaction_history[-10:] if profile.quality_satisfaction_history else []
            }
        }
        
        return analytics
    
    def _save_profile_to_db(self, profile: UserProfile):
        """Save user profile to database."""
        try:
            profile_data = json.dumps(asdict(profile), default=str)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, profile_data, created_timestamp, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (
                    profile.user_id,
                    profile_data,
                    profile.created_timestamp,
                    profile.last_updated
                ))
                conn.commit()
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save profile {profile.user_id}: {e}")
    
    def _save_session_to_db(self, session: UserSession):
        """Save user session to database."""
        try:
            session_data = json.dumps(asdict(session), default=str)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_sessions 
                    (session_id, user_id, session_data, start_time, end_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.user_id,
                    session_data,
                    session.start_time,
                    session.end_time
                ))
                conn.commit()
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save session {session.session_id}: {e}")


# Factory function
def create_user_profiles_system(data_directory: str = "user_profiles", enable_ml: bool = True) -> UserProfilesSystem:
    """
    Factory function to create a UserProfilesSystem instance.
    
    Args:
        data_directory: Directory to store user profile data
        enable_ml: Whether to enable machine learning features
        
    Returns:
        Configured UserProfilesSystem instance
    """
    return UserProfilesSystem(data_directory, enable_ml)


# Example usage
if __name__ == "__main__":
    async def main():
        profiles_system = create_user_profiles_system()
        
        # Create a user profile
        user_id = "test_user"
        profile = profiles_system.create_user_profile(user_id)
        
        # Start a session
        session = profiles_system.start_session(user_id, "session_1")
        
        # Simulate some session activity
        profiles_system.update_session_metrics("session_1", {
            "tokens_processed": 1000,
            "latency_ms": 150,
            "quality_score": 0.95,
            "memory_usage_gb": 2.1
        })
        
        # End session with satisfaction rating
        profiles_system.end_session("session_1", user_satisfaction=4.5)
        
        # Get recommendations
        recommendations = profiles_system.get_optimization_recommendations(user_id)
        print("Recommendations:", recommendations)
        
        # Get analytics
        analytics = profiles_system.get_user_analytics(user_id)
        print("Analytics:", analytics)
    
    # asyncio.run(main())
