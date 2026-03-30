"""
ImpressionCore UX - Predictive Optimization Engine
==================================================

This module implements a predictive optimization engine that uses machine learning to forecast
usage patterns, optimize resource allocation, and provide proactive system adjustments. It
integrates with the feedback system and ML adaptation engine to create a comprehensive
predictive user experience optimization framework.

Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Architecture: Brain-inspired multimodal framework
Focus: Proactive system optimization through predictive analytics

Key Features:
- Usage pattern forecasting using time series analysis
- Proactive resource allocation optimization
- Predictive quality scaling based on user preferences
- Smart caching and prefetching strategies
- Integration with feedback and adaptation systems
- Memory-optimized predictive models for constrained hardware

Author: GitHub Copilot & Kirk LaSalle
Created: 2025-06-01
Version: 1.0.0
"""

import json
import time
import logging
import asyncio
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import defaultdict, deque
import sqlite3
import pickle
import hashlib

# Core framework imports
try:
    from src.core.utils.rich_enhancements import RichTextManager
    from src.core.utils.rich_logging import RichLogger
    from src.core.utils.rich_status_animation import RichStatusAnimation
    CORE_UTILS_AVAILABLE = True
    MemoryTracker = None  # Use simplified memory tracking
except ImportError:
    try:
        from core.utils.rich_enhancements import RichTextManager
        from core.utils.rich_logging import RichLogger
        from core.utils.rich_status_animation import RichStatusAnimation
        CORE_UTILS_AVAILABLE = True
        MemoryTracker = None  # Use simplified memory tracking
    except ImportError:
        CORE_UTILS_AVAILABLE = False
        RichTextManager = None
        RichLogger = logging.getLogger(__name__)
        RichStatusAnimation = None
        MemoryTracker = None

# ML/Statistical imports
try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Predictive optimization will use fallback methods.")

try:
    import scipy.stats as stats
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy not available. Some optimization features will be limited.")


class PredictionType(Enum):
    """Types of predictions the system can make."""
    USAGE_PATTERN = "usage_pattern"
    RESOURCE_DEMAND = "resource_demand"
    QUALITY_PREFERENCE = "quality_preference"
    PERFORMANCE_REQUIREMENT = "performance_requirement"
    FEATURE_DEMAND = "feature_demand"
    SESSION_DURATION = "session_duration"
    ERROR_LIKELIHOOD = "error_likelihood"


class OptimizationStrategy(Enum):
    """Optimization strategies for different scenarios."""
    PERFORMANCE_FOCUSED = "performance_focused"
    QUALITY_FOCUSED = "quality_focused"
    MEMORY_FOCUSED = "memory_focused"
    BALANCED = "balanced"
    USER_ADAPTIVE = "user_adaptive"
    PREDICTIVE = "predictive"


@dataclass
class UsagePattern:
    """Represents a usage pattern for prediction."""
    user_id: str
    timestamp: datetime
    session_duration: float
    features_used: List[str]
    resource_usage: Dict[str, float]
    quality_settings: Dict[str, float]
    performance_metrics: Dict[str, float]
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert usage pattern to feature vector for ML."""
        features = []
        
        # Time-based features
        hour = self.timestamp.hour
        day_of_week = self.timestamp.weekday()
        features.extend([hour, day_of_week])
        
        # Session features
        features.append(self.session_duration)
        features.append(len(self.features_used))
        
        # Resource features
        features.extend([
            self.resource_usage.get('memory_mb', 0),
            self.resource_usage.get('cpu_percent', 0),
            self.resource_usage.get('gpu_memory_mb', 0)
        ])
        
        # Quality features
        features.extend([
            self.quality_settings.get('resolution_scale', 1.0),
            self.quality_settings.get('processing_speed', 1.0),
            self.quality_settings.get('precision_level', 1.0)
        ])
        
        # Performance features
        features.extend([
            self.performance_metrics.get('response_time_ms', 0),
            self.performance_metrics.get('throughput_ops_sec', 0),
            self.performance_metrics.get('error_rate', 0)
        ])
        
        return np.array(features, dtype=np.float32)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsagePattern':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class PredictionResult:
    """Result of a prediction operation."""
    prediction_id: str
    prediction_type: PredictionType
    user_id: str
    timestamp: datetime
    predicted_values: Dict[str, float]
    confidence_score: float
    time_horizon: timedelta
    model_version: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['time_horizon'] = self.time_horizon.total_seconds()
        result['prediction_type'] = self.prediction_type.value
        return result


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation based on predictions."""
    recommendation_id: str
    user_id: str
    timestamp: datetime
    strategy: OptimizationStrategy
    recommendations: Dict[str, Any]
    expected_improvement: Dict[str, float]
    confidence_level: float
    priority: int  # 1=low, 5=critical
    expires_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['expires_at'] = self.expires_at.isoformat()
        result['strategy'] = self.strategy.value
        return result


class TimeSeriesPredictor:
    """Time series predictor for usage patterns and trends."""
    
    def __init__(self, window_size: int = 24):
        self.logger = RichLogger("TimeSeriesPredictor")
        self.memory_tracker = MemoryTracker()
        
        self.window_size = window_size
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        
        # Initialize models if available
        if SKLEARN_AVAILABLE:
            self.default_model = RandomForestRegressor(
                n_estimators=50,  # Reduced for memory constraints
                max_depth=10,
                random_state=42,
                n_jobs=1  # Single thread for memory efficiency
            )
        else:
            self.default_model = None
    
    def prepare_time_series_data(self, 
                               usage_patterns: List[UsagePattern],
                               target_feature: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare time series data for training.
        
        Args:
            usage_patterns: Historical usage patterns
            target_feature: Feature to predict
            
        Returns:
            Tuple of (X, y) arrays for training
        """
        if len(usage_patterns) < self.window_size + 1:
            raise ValueError(f"Need at least {self.window_size + 1} patterns for time series")
        
        # Sort by timestamp
        sorted_patterns = sorted(usage_patterns, key=lambda x: x.timestamp)
        
        # Extract feature vectors
        feature_vectors = [pattern.to_feature_vector() for pattern in sorted_patterns]
        
        # Extract target values
        target_values = []
        for pattern in sorted_patterns:
            if target_feature in pattern.resource_usage:
                target_values.append(pattern.resource_usage[target_feature])
            elif target_feature in pattern.performance_metrics:
                target_values.append(pattern.performance_metrics[target_feature])
            elif target_feature == 'session_duration':
                target_values.append(pattern.session_duration)
            else:
                target_values.append(0.0)
        
        # Create sliding windows
        X, y = [], []
        for i in range(len(feature_vectors) - self.window_size):
            # Use window of feature vectors as input
            window_features = np.concatenate(feature_vectors[i:i+self.window_size])
            X.append(window_features)
            
            # Target is the next value
            y.append(target_values[i + self.window_size])
        
        return np.array(X), np.array(y)
    
    def train_predictor(self, 
                       usage_patterns: List[UsagePattern],
                       target_features: List[str]) -> Dict[str, float]:
        """
        Train time series predictors for specified target features.
        
        Args:
            usage_patterns: Training data
            target_features: Features to predict
            
        Returns:
            Training performance metrics
        """
        training_results = {}
        
        if not self.default_model:
            self.logger.warning("No ML models available for training")
            return training_results
        
        for target_feature in target_features:
            try:
                # Prepare data
                X, y = self.prepare_time_series_data(usage_patterns, target_feature)
                
                if len(X) < 10:  # Need minimum samples
                    continue
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train model
                model = RandomForestRegressor(
                    n_estimators=30,  # Reduced for memory
                    max_depth=8,
                    random_state=42,
                    n_jobs=1
                )
                model.fit(X_train_scaled, y_train)
                
                # Evaluate
                y_pred = model.predict(X_test_scaled)
                mse = mean_squared_error(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                
                # Store model and scaler
                self.models[target_feature] = model
                self.scalers[target_feature] = scaler
                
                training_results[target_feature] = {
                    'mse': mse,
                    'mae': mae,
                    'samples': len(X)
                }
                
                self.logger.info(f"Trained predictor for {target_feature}: MAE={mae:.4f}")
                
            except Exception as e:
                self.logger.error(f"Failed to train predictor for {target_feature}: {e}")
        
        return training_results
    
    def predict_values(self, 
                      recent_patterns: List[UsagePattern],
                      target_features: List[str],
                      time_horizon: timedelta) -> Dict[str, Tuple[float, float]]:
        """
        Predict future values based on recent patterns.
        
        Args:
            recent_patterns: Recent usage patterns for context
            target_features: Features to predict
            time_horizon: How far into the future to predict
            
        Returns:
            Dictionary of {feature: (predicted_value, confidence)}
        """
        predictions = {}
        
        if len(recent_patterns) < self.window_size:
            self.logger.warning("Insufficient recent patterns for prediction")
            return predictions
        
        # Sort patterns by timestamp
        sorted_patterns = sorted(recent_patterns, key=lambda x: x.timestamp)
        recent_patterns = sorted_patterns[-self.window_size:]
        
        for target_feature in target_features:
            if target_feature not in self.models:
                continue
            
            try:
                # Prepare input features
                feature_vectors = [pattern.to_feature_vector() for pattern in recent_patterns]
                X = np.concatenate(feature_vectors).reshape(1, -1)
                
                # Scale features
                scaler = self.scalers[target_feature]
                X_scaled = scaler.transform(X)
                
                # Make prediction
                model = self.models[target_feature]
                prediction = model.predict(X_scaled)[0]
                
                # Calculate confidence (simplified)
                # In a production system, you'd use more sophisticated confidence measures
                if hasattr(model, 'predict_proba'):
                    confidence = 0.8  # RandomForest doesn't have predict_proba for regression
                else:
                    confidence = 0.7
                
                # Adjust confidence based on time horizon
                horizon_hours = time_horizon.total_seconds() / 3600
                confidence *= max(0.3, 1.0 - (horizon_hours / 168))  # Decay over week
                
                predictions[target_feature] = (prediction, confidence)
                
            except Exception as e:
                self.logger.error(f"Prediction failed for {target_feature}: {e}")
        
        return predictions


class ResourceOptimizer:
    """Optimizes resource allocation based on predictions and user preferences."""
    
    def __init__(self):
        self.logger = RichLogger("ResourceOptimizer")
        self.memory_tracker = MemoryTracker()
        
        # Optimization constraints for GTX 1050 Ti
        self.hardware_constraints = {
            'max_gpu_memory_mb': 3800,  # Leave 200MB buffer
            'max_cpu_usage_percent': 85,
            'max_ram_usage_mb': 8000,
            'target_response_time_ms': 500
        }
        
        # Optimization objectives weights
        self.objective_weights = {
            'performance': 0.4,
            'quality': 0.3,
            'memory_efficiency': 0.2,
            'user_satisfaction': 0.1
        }
    
    def optimize_resource_allocation(self, 
                                   predicted_demand: Dict[str, float],
                                   user_preferences: Dict[str, float],
                                   current_usage: Dict[str, float]) -> Dict[str, Any]:
        """
        Optimize resource allocation based on predicted demand.
        
        Args:
            predicted_demand: Predicted resource demand
            user_preferences: User preference weights
            current_usage: Current resource usage
            
        Returns:
            Optimized resource allocation configuration
        """
        try:
            # Define optimization variables
            variables = {
                'gpu_memory_allocation': predicted_demand.get('gpu_memory_mb', 1000),
                'cpu_threads': min(4, predicted_demand.get('cpu_cores', 2)),
                'batch_size': predicted_demand.get('batch_size', 32),
                'quality_scale': user_preferences.get('quality_preference', 0.8),
                'processing_threads': min(8, predicted_demand.get('processing_threads', 4))
            }
            
            # Apply constraints
            variables['gpu_memory_allocation'] = min(
                variables['gpu_memory_allocation'],
                self.hardware_constraints['max_gpu_memory_mb']
            )
            
            # Optimize for user preferences
            if user_preferences.get('performance_priority', 0.5) > 0.7:
                # Performance-focused optimization
                variables['batch_size'] = min(variables['batch_size'], 16)  # Faster response
                variables['processing_threads'] = min(variables['processing_threads'], 6)
            elif user_preferences.get('quality_priority', 0.5) > 0.7:
                # Quality-focused optimization
                variables['quality_scale'] = min(1.0, variables['quality_scale'] * 1.2)
                variables['gpu_memory_allocation'] *= 1.1  # More memory for quality
            
            # Memory-constrained optimization
            if current_usage.get('memory_usage_percent', 0) > 70:
                variables['gpu_memory_allocation'] *= 0.9
                variables['batch_size'] = max(8, variables['batch_size'] // 2)
            
            # Calculate expected performance
            expected_performance = self._calculate_expected_performance(variables)
            
            optimization_result = {
                'resource_allocation': variables,
                'expected_performance': expected_performance,
                'constraints_applied': self.hardware_constraints,
                'optimization_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Optimized resource allocation: GPU={variables['gpu_memory_allocation']}MB, "
                           f"Quality={variables['quality_scale']:.2f}")
            
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Resource optimization failed: {e}")
            return self._get_default_allocation()
    
    def _calculate_expected_performance(self, variables: Dict[str, float]) -> Dict[str, float]:
        """Calculate expected performance metrics for given allocation."""
        # Simplified performance estimation
        gpu_efficiency = min(1.0, variables['gpu_memory_allocation'] / 2000)
        cpu_efficiency = variables['cpu_threads'] / 4.0
        quality_impact = variables['quality_scale']
        
        return {
            'expected_response_time_ms': 200 / (gpu_efficiency * cpu_efficiency),
            'expected_throughput': gpu_efficiency * cpu_efficiency * quality_impact * 10,
            'expected_memory_usage_mb': variables['gpu_memory_allocation'] * 1.2,
            'expected_quality_score': quality_impact * 0.9
        }
    
    def _get_default_allocation(self) -> Dict[str, Any]:
        """Get default resource allocation for fallback."""
        return {
            'resource_allocation': {
                'gpu_memory_allocation': 1500,
                'cpu_threads': 2,
                'batch_size': 16,
                'quality_scale': 0.8,
                'processing_threads': 4
            },
            'expected_performance': {
                'expected_response_time_ms': 400,
                'expected_throughput': 5.0,
                'expected_memory_usage_mb': 1800,
                'expected_quality_score': 0.7
            }
        }


class SmartCache:
    """Smart caching system with predictive prefetching."""
    
    def __init__(self, max_cache_size_mb: int = 512):
        self.logger = RichLogger("SmartCache")
        self.memory_tracker = MemoryTracker()
        
        self.max_cache_size_mb = max_cache_size_mb
        self.cache = {}
        self.access_patterns = defaultdict(list)
        self.prefetch_queue = deque()
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'prefetch_hits': 0,
            'evictions': 0
        }
    
    def predict_access_patterns(self, 
                              usage_patterns: List[UsagePattern]) -> List[str]:
        """
        Predict likely cache keys to prefetch based on usage patterns.
        
        Args:
            usage_patterns: Recent usage patterns
            
        Returns:
            List of predicted cache keys to prefetch
        """
        predicted_keys = []
        
        # Analyze feature usage patterns
        feature_counts = defaultdict(int)
        for pattern in usage_patterns:
            for feature in pattern.features_used:
                feature_counts[feature] += 1
        
        # Predict most likely features to be accessed
        sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
        predicted_keys.extend([f"feature_{feature}" for feature, _ in sorted_features[:5]])
        
        # Time-based predictions
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Work hours
            predicted_keys.extend(["model_weights_work", "config_optimized"])
        else:
            predicted_keys.extend(["model_weights_personal", "config_standard"])
        
        return predicted_keys[:10]  # Limit to top 10 predictions
    
    def prefetch_predicted_items(self, predicted_keys: List[str]):
        """Prefetch items based on predictions."""
        for key in predicted_keys:
            if key not in self.cache and len(self.prefetch_queue) < 20:
                self.prefetch_queue.append(key)
        
        self.logger.debug(f"Queued {len(predicted_keys)} items for prefetching")
    
    def get_cache_recommendations(self) -> Dict[str, Any]:
        """Get cache optimization recommendations."""
        hit_rate = self.stats['hits'] / max(1, self.stats['hits'] + self.stats['misses'])
        
        recommendations = {
            'current_hit_rate': hit_rate,
            'cache_size_mb': self._estimate_cache_size(),
            'recommended_actions': []
        }
        
        if hit_rate < 0.7:
            recommendations['recommended_actions'].append({
                'action': 'increase_cache_size',
                'reason': 'Low hit rate indicates insufficient cache capacity'
            })
        
        if len(self.prefetch_queue) > 15:
            recommendations['recommended_actions'].append({
                'action': 'optimize_prefetching',
                'reason': 'High prefetch queue suggests aggressive prefetching'
            })
        
        return recommendations
    
    def _estimate_cache_size(self) -> float:
        """Estimate current cache size in MB."""
        # Simplified size estimation
        return len(self.cache) * 0.5  # Assume 0.5MB per cache entry


class PredictiveOptimizer:
    """
    Main predictive optimization engine that coordinates all optimization components.
    
    This system provides:
    - Usage pattern forecasting
    - Proactive resource allocation
    - Predictive quality scaling
    - Smart caching with prefetching
    - Integration with feedback and adaptation systems
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = RichLogger("PredictiveOptimizer")
        self.rich_manager = RichTextManager()
        self.memory_tracker = MemoryTracker()
        
        # Storage configuration
        self.storage_path = Path(storage_path or "data/predictions")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.time_series_predictor = TimeSeriesPredictor()
        self.resource_optimizer = ResourceOptimizer()
        self.smart_cache = SmartCache()
        
        # Database for predictions storage
        self.db_path = self.storage_path / "predictions.db"
        self._initialize_database()
        
        # Usage pattern storage
        self.usage_patterns = deque(maxlen=1000)  # Keep recent patterns
        
        # Prediction cache
        self.prediction_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Background optimization
        self.optimization_thread = None
        self.stop_optimization = threading.Event()
        self.optimization_interval = 120  # Every 2 minutes
        
        # Optimization callbacks
        self.optimization_callbacks: List[Callable[[OptimizationRecommendation], None]] = []
        
        self.logger.info("Predictive Optimizer initialized")
    
    def _initialize_database(self):
        """Initialize SQLite database for predictions storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        prediction_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        prediction_type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        predicted_values TEXT NOT NULL,
                        confidence_score REAL,
                        time_horizon REAL,
                        model_version TEXT,
                        context TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS usage_patterns (
                        pattern_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        session_duration REAL,
                        features_used TEXT,
                        resource_usage TEXT,
                        quality_settings TEXT,
                        performance_metrics TEXT,
                        context TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS optimization_recommendations (
                        recommendation_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        strategy TEXT NOT NULL,
                        recommendations TEXT NOT NULL,
                        expected_improvement TEXT,
                        confidence_level REAL,
                        priority INTEGER,
                        expires_at TEXT
                    )
                """)
                
                # Create indexes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_predictions ON predictions (user_id, timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_patterns ON usage_patterns (user_id, timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_recommendations ON optimization_recommendations (user_id, expires_at)")
                
                conn.commit()
                self.logger.info("Predictions database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize predictions database: {e}")
    
    def record_usage_pattern(self, 
                           user_id: str,
                           session_duration: float,
                           features_used: List[str],
                           resource_usage: Dict[str, float],
                           quality_settings: Dict[str, float],
                           performance_metrics: Dict[str, float],
                           context: Optional[Dict[str, Any]] = None) -> str:
        """
        Record a usage pattern for analysis and prediction.
        
        Args:
            user_id: User identifier
            session_duration: Duration of the session in seconds
            features_used: List of features used in the session
            resource_usage: Resource usage metrics
            quality_settings: Quality configuration used
            performance_metrics: Performance metrics achieved
            context: Additional context information
            
        Returns:
            Pattern ID
        """
        pattern = UsagePattern(
            user_id=user_id,
            timestamp=datetime.now(),
            session_duration=session_duration,
            features_used=features_used,
            resource_usage=resource_usage,
            quality_settings=quality_settings,
            performance_metrics=performance_metrics,
            context=context or {}
        )
        
        # Add to in-memory storage
        self.usage_patterns.append(pattern)
        
        # Store in database
        pattern_id = self._store_usage_pattern(pattern)
        
        # Update predictions if we have enough data
        user_patterns = [p for p in self.usage_patterns if p.user_id == user_id]
        if len(user_patterns) >= 10:
            self._update_user_predictions(user_id)
        
        self.logger.debug(f"Recorded usage pattern for user {user_id}")
        return pattern_id
    
    def _store_usage_pattern(self, pattern: UsagePattern) -> str:
        """Store usage pattern in database."""
        try:
            pattern_id = f"pat_{int(time.time() * 1000)}_{pattern.user_id}"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO usage_patterns (
                        pattern_id, user_id, timestamp, session_duration,
                        features_used, resource_usage, quality_settings,
                        performance_metrics, context
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern_id,
                    pattern.user_id,
                    pattern.timestamp.isoformat(),
                    pattern.session_duration,
                    json.dumps(pattern.features_used),
                    json.dumps(pattern.resource_usage),
                    json.dumps(pattern.quality_settings),
                    json.dumps(pattern.performance_metrics),
                    json.dumps(pattern.context)
                ))
                conn.commit()
            
            return pattern_id
            
        except Exception as e:
            self.logger.error(f"Failed to store usage pattern: {e}")
            return ""
    
    def predict_future_usage(self, 
                           user_id: str,
                           time_horizon: timedelta = timedelta(hours=1),
                           prediction_types: Optional[List[PredictionType]] = None) -> Dict[PredictionType, PredictionResult]:
        """
        Predict future usage patterns for a user.
        
        Args:
            user_id: User to predict for
            time_horizon: How far into the future to predict
            prediction_types: Types of predictions to make
            
        Returns:
            Dictionary of prediction results by type
        """
        if prediction_types is None:
            prediction_types = [
                PredictionType.RESOURCE_DEMAND,
                PredictionType.QUALITY_PREFERENCE,
                PredictionType.SESSION_DURATION
            ]
        
        predictions = {}
        
        # Get user's historical patterns
        user_patterns = [p for p in self.usage_patterns if p.user_id == user_id]
        
        if len(user_patterns) < 5:
            self.logger.warning(f"Insufficient data for predictions for user {user_id}")
            return predictions
        
        for prediction_type in prediction_types:
            try:
                prediction = self._make_prediction(user_id, user_patterns, prediction_type, time_horizon)
                if prediction:
                    predictions[prediction_type] = prediction
                    
            except Exception as e:
                self.logger.error(f"Prediction failed for {prediction_type}: {e}")
        
        return predictions
    
    def _make_prediction(self, 
                        user_id: str,
                        user_patterns: List[UsagePattern],
                        prediction_type: PredictionType,
                        time_horizon: timedelta) -> Optional[PredictionResult]:
        """Make a specific type of prediction."""
        if prediction_type == PredictionType.RESOURCE_DEMAND:
            return self._predict_resource_demand(user_id, user_patterns, time_horizon)
        elif prediction_type == PredictionType.QUALITY_PREFERENCE:
            return self._predict_quality_preference(user_id, user_patterns, time_horizon)
        elif prediction_type == PredictionType.SESSION_DURATION:
            return self._predict_session_duration(user_id, user_patterns, time_horizon)
        else:
            return None
    
    def _predict_resource_demand(self, 
                               user_id: str,
                               user_patterns: List[UsagePattern],
                               time_horizon: timedelta) -> Optional[PredictionResult]:
        """Predict future resource demand."""
        try:
            # Extract resource usage trends
            memory_usage = [p.resource_usage.get('memory_mb', 0) for p in user_patterns]
            cpu_usage = [p.resource_usage.get('cpu_percent', 0) for p in user_patterns]
            gpu_usage = [p.resource_usage.get('gpu_memory_mb', 0) for p in user_patterns]
            
            # Simple trend analysis
            if len(memory_usage) >= 3:
                memory_trend = np.polyfit(range(len(memory_usage)), memory_usage, 1)[0]
                cpu_trend = np.polyfit(range(len(cpu_usage)), cpu_usage, 1)[0]
                gpu_trend = np.polyfit(range(len(gpu_usage)), gpu_usage, 1)[0]
            else:
                memory_trend = cpu_trend = gpu_trend = 0
            
            # Project forward
            hours_ahead = time_horizon.total_seconds() / 3600
            predicted_memory = max(0, np.mean(memory_usage) + (memory_trend * hours_ahead))
            predicted_cpu = max(0, min(100, np.mean(cpu_usage) + (cpu_trend * hours_ahead)))
            predicted_gpu = max(0, np.mean(gpu_usage) + (gpu_trend * hours_ahead))
            
            # Calculate confidence based on data consistency
            memory_std = np.std(memory_usage)
            confidence = max(0.3, 1.0 - (memory_std / max(1, np.mean(memory_usage))))
            
            prediction = PredictionResult(
                prediction_id=f"pred_{int(time.time() * 1000)}_{user_id}",
                prediction_type=PredictionType.RESOURCE_DEMAND,
                user_id=user_id,
                timestamp=datetime.now(),
                predicted_values={
                    'memory_mb': predicted_memory,
                    'cpu_percent': predicted_cpu,
                    'gpu_memory_mb': predicted_gpu
                },
                confidence_score=confidence,
                time_horizon=time_horizon,
                model_version="trend_analysis_v1"
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Resource demand prediction failed: {e}")
            return None
    
    def _predict_quality_preference(self,
                                  user_id: str,
                                  user_patterns: List[UsagePattern],
                                  time_horizon: timedelta) -> Optional[PredictionResult]:
        """Predict user's quality preferences."""
        try:
            # Extract quality settings trends
            quality_scales = [p.quality_settings.get('resolution_scale', 1.0) for p in user_patterns]
            speed_preferences = [p.quality_settings.get('processing_speed', 1.0) for p in user_patterns]
            precision_levels = [p.quality_settings.get('precision_level', 1.0) for p in user_patterns]
            
            # Calculate averages and trends
            avg_quality = np.mean(quality_scales)
            avg_speed = np.mean(speed_preferences)
            avg_precision = np.mean(precision_levels)
            
            # Analyze time-of-day patterns
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 17:  # Work hours - higher quality preference
                quality_modifier = 1.1
            else:  # Personal time - balanced preference
                quality_modifier = 1.0
            
            predicted_quality = min(1.0, avg_quality * quality_modifier)
            predicted_speed = avg_speed
            predicted_precision = min(1.0, avg_precision * quality_modifier)
            
            confidence = 0.7  # Moderate confidence for quality preferences
            
            prediction = PredictionResult(
                prediction_id=f"pred_{int(time.time() * 1000)}_{user_id}",
                prediction_type=PredictionType.QUALITY_PREFERENCE,
                user_id=user_id,
                timestamp=datetime.now(),
                predicted_values={
                    'quality_scale': predicted_quality,
                    'speed_preference': predicted_speed,
                    'precision_level': predicted_precision
                },
                confidence_score=confidence,
                time_horizon=time_horizon,
                model_version="pattern_analysis_v1"
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Quality preference prediction failed: {e}")
            return None
    
    def _predict_session_duration(self,
                                user_id: str,
                                user_patterns: List[UsagePattern],
                                time_horizon: timedelta) -> Optional[PredictionResult]:
        """Predict session duration."""
        try:
            # Extract session durations
            durations = [p.session_duration for p in user_patterns]
            
            # Analyze patterns
            avg_duration = np.mean(durations)
            std_duration = np.std(durations)
            
            # Time-based adjustments
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 17:  # Work hours - longer sessions
                duration_modifier = 1.2
            elif 18 <= current_hour <= 22:  # Evening - medium sessions
                duration_modifier = 1.0
            else:  # Night/early morning - shorter sessions
                duration_modifier = 0.8
            
            predicted_duration = avg_duration * duration_modifier
            
            # Confidence based on consistency
            cv = std_duration / max(1, avg_duration)  # Coefficient of variation
            confidence = max(0.4, 1.0 - cv)
            
            prediction = PredictionResult(
                prediction_id=f"pred_{int(time.time() * 1000)}_{user_id}",
                prediction_type=PredictionType.SESSION_DURATION,
                user_id=user_id,
                timestamp=datetime.now(),
                predicted_values={
                    'session_duration_seconds': predicted_duration,
                    'confidence_interval_lower': predicted_duration * 0.8,
                    'confidence_interval_upper': predicted_duration * 1.2
                },
                confidence_score=confidence,
                time_horizon=time_horizon,
                model_version="temporal_analysis_v1"
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Session duration prediction failed: {e}")
            return None
    
    def generate_optimization_recommendations(self,
                                            user_id: str,
                                            current_config: Dict[str, Any],
                                            predictions: Optional[Dict[PredictionType, PredictionResult]] = None) -> List[OptimizationRecommendation]:
        """
        Generate optimization recommendations based on predictions.
        
        Args:
            user_id: User to optimize for
            current_config: Current system configuration
            predictions: Prediction results to base recommendations on
            
        Returns:
            List of optimization recommendations
        """
        if predictions is None:
            predictions = self.predict_future_usage(user_id)
        
        recommendations = []
        
        try:
            # Resource optimization recommendation
            if PredictionType.RESOURCE_DEMAND in predictions:
                resource_rec = self._generate_resource_recommendation(
                    user_id, current_config, predictions[PredictionType.RESOURCE_DEMAND]
                )
                if resource_rec:
                    recommendations.append(resource_rec)
            
            # Quality optimization recommendation
            if PredictionType.QUALITY_PREFERENCE in predictions:
                quality_rec = self._generate_quality_recommendation(
                    user_id, current_config, predictions[PredictionType.QUALITY_PREFERENCE]
                )
                if quality_rec:
                    recommendations.append(quality_rec)
            
            # Cache optimization recommendation
            cache_rec = self._generate_cache_recommendation(user_id, current_config)
            if cache_rec:
                recommendations.append(cache_rec)
            
            self.logger.info(f"Generated {len(recommendations)} optimization recommendations for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate optimization recommendations: {e}")
        
        return recommendations
    
    def _generate_resource_recommendation(self,
                                        user_id: str,
                                        current_config: Dict[str, Any],
                                        prediction: PredictionResult) -> Optional[OptimizationRecommendation]:
        """Generate resource optimization recommendation."""
        try:
            predicted_memory = prediction.predicted_values.get('memory_mb', 0)
            predicted_gpu = prediction.predicted_values.get('gpu_memory_mb', 0)
            
            current_memory = current_config.get('memory_allocation_mb', 1000)
            current_gpu = current_config.get('gpu_memory_mb', 1500)
            
            recommendations = {}
            expected_improvement = {}
            priority = 1
            
            # Memory optimization
            if predicted_memory > current_memory * 1.2:
                recommendations['increase_memory_allocation'] = {
                    'current': current_memory,
                    'recommended': min(2000, predicted_memory * 1.1),
                    'reason': 'Predicted memory demand exceeds current allocation'
                }
                expected_improvement['memory_efficiency'] = 0.15
                priority = max(priority, 3)
            
            # GPU memory optimization
            if predicted_gpu > current_gpu * 1.1:
                max_gpu = self.resource_optimizer.hardware_constraints['max_gpu_memory_mb']
                recommendations['adjust_gpu_allocation'] = {
                    'current': current_gpu,
                    'recommended': min(max_gpu, predicted_gpu * 1.05),
                    'reason': 'Predicted GPU memory demand increase'
                }
                expected_improvement['gpu_efficiency'] = 0.10
                priority = max(priority, 4)
            
            if not recommendations:
                return None
            
            return OptimizationRecommendation(
                recommendation_id=f"rec_{int(time.time() * 1000)}_{user_id}",
                user_id=user_id,
                timestamp=datetime.now(),
                strategy=OptimizationStrategy.PREDICTIVE,
                recommendations=recommendations,
                expected_improvement=expected_improvement,
                confidence_level=prediction.confidence_score,
                priority=priority,
                expires_at=datetime.now() + timedelta(hours=2)
            )
            
        except Exception as e:
            self.logger.error(f"Resource recommendation generation failed: {e}")
            return None
    
    def _generate_quality_recommendation(self,
                                       user_id: str,
                                       current_config: Dict[str, Any],
                                       prediction: PredictionResult) -> Optional[OptimizationRecommendation]:
        """Generate quality optimization recommendation."""
        try:
            predicted_quality = prediction.predicted_values.get('quality_scale', 0.8)
            current_quality = current_config.get('quality_scale', 0.8)
            
            recommendations = {}
            expected_improvement = {}
            priority = 1
            
            quality_diff = predicted_quality - current_quality
            
            if abs(quality_diff) > 0.1:
                recommendations['adjust_quality_settings'] = {
                    'current_quality_scale': current_quality,
                    'recommended_quality_scale': predicted_quality,
                    'adjustment_type': 'increase' if quality_diff > 0 else 'decrease',
                    'reason': f'Predicted quality preference change: {quality_diff:+.2f}'
                }
                
                if quality_diff > 0:
                    expected_improvement['quality_satisfaction'] = min(0.2, abs(quality_diff))
                    priority = 2
                else:
                    expected_improvement['performance_speed'] = min(0.15, abs(quality_diff))
                    priority = 3
                
                return OptimizationRecommendation(
                    recommendation_id=f"rec_{int(time.time() * 1000)}_{user_id}",
                    user_id=user_id,
                    timestamp=datetime.now(),
                    strategy=OptimizationStrategy.USER_ADAPTIVE,
                    recommendations=recommendations,
                    expected_improvement=expected_improvement,
                    confidence_level=prediction.confidence_score,
                    priority=priority,
                    expires_at=datetime.now() + timedelta(hours=4)
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Quality recommendation generation failed: {e}")
            return None
    
    def _generate_cache_recommendation(self,
                                     user_id: str,
                                     current_config: Dict[str, Any]) -> Optional[OptimizationRecommendation]:
        """Generate cache optimization recommendation."""
        try:
            cache_recommendations = self.smart_cache.get_cache_recommendations()
            
            if cache_recommendations['current_hit_rate'] < 0.6:
                return OptimizationRecommendation(
                    recommendation_id=f"rec_{int(time.time() * 1000)}_{user_id}",
                    user_id=user_id,
                    timestamp=datetime.now(),
                    strategy=OptimizationStrategy.PERFORMANCE_FOCUSED,
                    recommendations={
                        'optimize_cache': {
                            'current_hit_rate': cache_recommendations['current_hit_rate'],
                            'recommended_actions': cache_recommendations['recommended_actions'],
                            'reason': 'Low cache hit rate affecting performance'
                        }
                    },
                    expected_improvement={'cache_performance': 0.25},
                    confidence_level=0.8,
                    priority=2,
                    expires_at=datetime.now() + timedelta(hours=6)
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Cache recommendation generation failed: {e}")
            return None
    
    def _update_user_predictions(self, user_id: str):
        """Update predictions for a user based on latest data."""
        try:
            # Get recent patterns
            user_patterns = [p for p in self.usage_patterns if p.user_id == user_id]
            recent_patterns = sorted(user_patterns, key=lambda x: x.timestamp)[-50:]  # Last 50 patterns
            
            # Update time series models if we have enough data
            if len(recent_patterns) >= 25:
                target_features = ['memory_mb', 'cpu_percent', 'session_duration']
                self.time_series_predictor.train_predictor(recent_patterns, target_features)
                
                self.logger.debug(f"Updated predictions for user {user_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to update predictions for user {user_id}: {e}")
    
    def start_background_optimization(self):
        """Start background optimization thread."""
        if self.optimization_thread and self.optimization_thread.is_alive():
            return
        
        self.stop_optimization.clear()
        self.optimization_thread = threading.Thread(
            target=self._background_optimization_loop,
            daemon=True
        )
        self.optimization_thread.start()
        self.logger.info("Started background predictive optimization")
    
    def stop_background_optimization(self):
        """Stop background optimization thread."""
        self.stop_optimization.set()
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        self.logger.info("Stopped background predictive optimization")
    
    def _background_optimization_loop(self):
        """Background optimization processing loop."""
        while not self.stop_optimization.wait(self.optimization_interval):
            try:
                # Get active users
                active_users = set(p.user_id for p in list(self.usage_patterns)[-100:])
                
                for user_id in active_users:
                    # Generate recommendations
                    recommendations = self.generate_optimization_recommendations(user_id, {})
                    
                    # Process high-priority recommendations
                    for rec in recommendations:
                        if rec.priority >= 4:  # High priority
                            for callback in self.optimization_callbacks:
                                try:
                                    callback(rec)
                                except Exception as e:
                                    self.logger.error(f"Optimization callback failed: {e}")
                
            except Exception as e:
                self.logger.error(f"Background optimization error: {e}")
    
    def register_optimization_callback(self, callback: Callable[[OptimizationRecommendation], None]):
        """Register callback for optimization recommendations."""
        self.optimization_callbacks.append(callback)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            status = {
                'predictive_optimizer': {
                    'total_usage_patterns': len(self.usage_patterns),
                    'unique_users': len(set(p.user_id for p in self.usage_patterns)),
                    'prediction_cache_size': len(self.prediction_cache),
                    'background_optimization_running': self.optimization_thread and self.optimization_thread.is_alive()
                },
                'time_series_predictor': {
                    'trained_models': len(self.time_series_predictor.models),
                    'available_features': list(self.time_series_predictor.models.keys()),
                    'sklearn_available': SKLEARN_AVAILABLE
                },
                'resource_optimizer': {
                    'hardware_constraints': self.resource_optimizer.hardware_constraints,
                    'objective_weights': self.resource_optimizer.objective_weights
                },
                'smart_cache': self.smart_cache.get_cache_recommendations(),
                'memory_usage': self.memory_tracker.get_memory_usage(),
                'system_health': 'healthy'
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {'system_health': 'error', 'error': str(e)}


# Example usage and testing functions
def demonstrate_predictive_optimizer():
    """Demonstrate the predictive optimization engine capabilities."""
    # Initialize system
    optimizer = PredictiveOptimizer()
    
    # Simulate usage pattern recording
    user_id = "test_user_001"
    
    # Record several usage patterns
    for i in range(10):
        optimizer.record_usage_pattern(
            user_id=user_id,
            session_duration=300 + i * 30,  # Increasing session times
            features_used=["text_generation", "image_processing"],
            resource_usage={
                "memory_mb": 1000 + i * 50,
                "cpu_percent": 30 + i * 2,
                "gpu_memory_mb": 1200 + i * 100
            },
            quality_settings={
                "resolution_scale": 0.8,
                "processing_speed": 1.0,
                "precision_level": 0.9
            },
            performance_metrics={
                "response_time_ms": 200 + i * 10,
                "throughput_ops_sec": 10 - i * 0.5,
                "error_rate": 0.01
            }
        )
    
    # Generate predictions
    predictions = optimizer.predict_future_usage(user_id, timedelta(hours=2))
    print(f"Generated {len(predictions)} predictions")
    
    # Generate optimization recommendations
    recommendations = optimizer.generate_optimization_recommendations(user_id, {})
    print(f"Generated {len(recommendations)} optimization recommendations")
    
    # Get system status
    status = optimizer.get_system_status()
    print(f"System status: {status}")
    
    return optimizer


if __name__ == "__main__":
    # Run demonstration
    system = demonstrate_predictive_optimizer()
    
    # Show system status
    import pprint
    pprint.pprint(system.get_system_status())
