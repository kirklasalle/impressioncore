#!/usr/bin/env python3
"""
ImpressionCore ML-Based Adaptation Engine
Phase 7C: Adaptive Learning and Feedback Systems

This module implements machine learning-based user behavior adaptation, predictive 
performance optimization, automated parameter tuning, and anomaly detection for 
unusual usage patterns.

Author: GitHub Copilot & Kirk LaSalle
Created: June 1, 2025
Hardware Target: GTX 1050 Ti (4GB VRAM)
Phase: Priority 7 Phase 7C - Adaptive Learning and Feedback Systems
"""

import asyncio
import json
import logging
import numpy as np
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

# ImpressionCore imports
try:
    from src.core.utils.rich_enhancements import RichTextManager
    from src.core.utils.rich_logging import RichLogger
    from src.core.utils.rich_status_animation import RichStatusAnimation
    RICH_AVAILABLE = True
    MemoryTracker = None  # Use simplified memory tracking
except ImportError:
    try:
        from src.core.utils.rich_enhancements import RichTextManager
        from src.core.utils.rich_logging import RichLogger
        from src.core.utils.rich_status_animation import RichStatusAnimation
        RICH_AVAILABLE = True
        MemoryTracker = None  # Use simplified memory tracking
    except ImportError:
        RICH_AVAILABLE = False
        RichTextManager = None
        RichLogger = logging.getLogger(__name__)
        RichStatusAnimation = None
        MemoryTracker = None


@dataclass
class UserBehaviorPattern:
    """Represents a user behavior pattern with usage statistics."""
    pattern_id: str
    user_id: str
    session_count: int = 0
    avg_session_duration: float = 0.0
    preferred_quality_level: str = "balanced"
    preferred_memory_usage: float = 0.7  # 0.0 to 1.0
    common_operations: List[str] = field(default_factory=list)
    peak_usage_hours: List[int] = field(default_factory=list)
    performance_preferences: Dict[str, float] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    anomaly_score: float = 0.0
    cluster_id: int = -1


@dataclass
class AdaptationParameters:
    """Parameters for ML-based adaptation algorithms."""
    learning_rate: float = 0.01
    adaptation_threshold: float = 0.1
    pattern_window_size: int = 100
    cluster_update_frequency: int = 50
    anomaly_threshold: float = 0.7
    parameter_ranges: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    feature_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for adaptation optimization."""
    timestamp: str
    response_time: float
    memory_usage: float
    cpu_usage: float
    user_satisfaction: float
    quality_score: float
    efficiency_ratio: float
    error_rate: float = 0.0


class BehaviorPatternAnalyzer:
    """Analyzes user behavior patterns using machine learning."""
    
    def __init__(self, config: AdaptationParameters):
        self.config = config
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        self.anomaly_detector = IsolationForest(
            contamination=0.1, 
            random_state=42,
            n_estimators=100
        )
        self.is_fitted = False
        
        # Rich enhancements
        if RICH_AVAILABLE:
            self.rich_text = RichTextManager()
            self.logger = RichLogger("BehaviorAnalyzer")
            self.status_animation = RichStatusAnimation()
        else:
            self.logger = logging.getLogger(__name__)
    
    def extract_features(self, pattern: UserBehaviorPattern) -> np.ndarray:
        """Extract numerical features from user behavior pattern."""
        features = [
            pattern.session_count,
            pattern.avg_session_duration,
            pattern.preferred_memory_usage,
            len(pattern.common_operations),
            len(pattern.peak_usage_hours),
            pattern.performance_preferences.get('speed_weight', 0.5),
            pattern.performance_preferences.get('quality_weight', 0.5),
            pattern.performance_preferences.get('memory_weight', 0.5)
        ]
        return np.array(features)
    
    def fit_patterns(self, patterns: List[UserBehaviorPattern]) -> Dict[str, Any]:
        """Fit ML models on user behavior patterns."""
        if len(patterns) < 5:
            self.logger.warning("Insufficient patterns for clustering")
            return {"status": "insufficient_data", "patterns_count": len(patterns)}
        
        # Extract features
        features_list = [self.extract_features(pattern) for pattern in patterns]
        features_matrix = np.array(features_list)
        
        # Normalize features
        features_normalized = self.scaler.fit_transform(features_matrix)
        
        # Perform clustering
        cluster_labels = self.kmeans.fit_predict(features_normalized)
        
        # Fit anomaly detector
        self.anomaly_detector.fit(features_normalized)
        
        # Calculate silhouette score for clustering quality
        silhouette_avg = silhouette_score(features_normalized, cluster_labels)
        
        # Update pattern cluster assignments
        for i, pattern in enumerate(patterns):
            pattern.cluster_id = int(cluster_labels[i])
            pattern.anomaly_score = float(
                self.anomaly_detector.decision_function([features_normalized[i]])[0]
            )
        
        self.is_fitted = True
        
        return {
            "status": "success",
            "patterns_count": len(patterns),
            "clusters_count": len(np.unique(cluster_labels)),
            "silhouette_score": float(silhouette_avg),
            "anomaly_threshold": self.config.anomaly_threshold
        }
    
    def predict_cluster(self, pattern: UserBehaviorPattern) -> Tuple[int, float]:
        """Predict cluster and anomaly score for a new pattern."""
        if not self.is_fitted:
            return -1, 0.0
        
        features = self.extract_features(pattern).reshape(1, -1)
        features_normalized = self.scaler.transform(features)
        
        cluster_id = self.kmeans.predict(features_normalized)[0]
        anomaly_score = self.anomaly_detector.decision_function(features_normalized)[0]
        
        return int(cluster_id), float(anomaly_score)
    
    def identify_anomalies(self, patterns: List[UserBehaviorPattern]) -> List[str]:
        """Identify anomalous behavior patterns."""
        anomalous_patterns = []
        
        for pattern in patterns:
            if pattern.anomaly_score < -self.config.anomaly_threshold:
                anomalous_patterns.append(pattern.pattern_id)
        
        return anomalous_patterns


class PredictiveOptimizer:
    """Predicts optimal parameters based on user behavior and performance."""
    
    def __init__(self, config: AdaptationParameters):
        self.config = config
        self.performance_history: deque = deque(maxlen=config.pattern_window_size)
        self.parameter_models: Dict[str, LinearRegression] = {}
        self.feature_history: deque = deque(maxlen=config.pattern_window_size)
        
        # Rich enhancements
        if RICH_AVAILABLE:
            self.rich_text = RichTextManager()
            self.logger = RichLogger("PredictiveOptimizer")
        else:
            self.logger = logging.getLogger(__name__)
    
    def add_performance_data(self, metrics: PerformanceMetrics, 
                           parameters: Dict[str, float]):
        """Add performance data for model training."""
        self.performance_history.append(metrics)
        
        # Create feature vector from metrics
        features = [
            metrics.memory_usage,
            metrics.cpu_usage,
            metrics.response_time,
            metrics.quality_score,
            len(self.performance_history)  # Session sequence
        ]
        self.feature_history.append((features, parameters))
    
    def train_parameter_models(self) -> Dict[str, float]:
        """Train regression models for parameter prediction."""
        if len(self.feature_history) < 10:
            return {"status": "insufficient_data"}
        
        # Prepare training data
        X = []
        y_dict = defaultdict(list)
        
        for features, parameters in self.feature_history:
            X.append(features)
            for param_name, param_value in parameters.items():
                y_dict[param_name].append(param_value)
        
        X = np.array(X)
        training_results = {}
        
        # Train model for each parameter
        for param_name, y_values in y_dict.items():
            if len(set(y_values)) > 1:  # Only if there's variation
                y = np.array(y_values)
                model = LinearRegression()
                model.fit(X, y)
                self.parameter_models[param_name] = model
                
                # Calculate R² score
                r2_score = model.score(X, y)
                training_results[param_name] = {"r2_score": float(r2_score)}
        
        return training_results
    
    def predict_optimal_parameters(self, current_metrics: PerformanceMetrics) -> Dict[str, float]:
        """Predict optimal parameters based on current metrics."""
        if not self.parameter_models:
            return {}
        
        # Create feature vector
        features = np.array([[
            current_metrics.memory_usage,
            current_metrics.cpu_usage,
            current_metrics.response_time,
            current_metrics.quality_score,
            len(self.performance_history)
        ]])
        
        predictions = {}
        for param_name, model in self.parameter_models.items():
            try:
                prediction = model.predict(features)[0]
                
                # Apply parameter range constraints
                if param_name in self.config.parameter_ranges:
                    min_val, max_val = self.config.parameter_ranges[param_name]
                    prediction = np.clip(prediction, min_val, max_val)
                
                predictions[param_name] = float(prediction)
            except Exception as e:
                self.logger.warning(f"Prediction failed for {param_name}: {e}")
        
        return predictions


class MLAdaptationEngine:
    """Main ML-based adaptation engine for user behavior learning."""
    
    def __init__(self, config: Optional[AdaptationParameters] = None,
                 data_dir: Optional[Path] = None):
        self.config = config or AdaptationParameters()
        self.data_dir = data_dir or Path("src/data/user_behavior")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.behavior_analyzer = BehaviorPatternAnalyzer(self.config)
        self.predictive_optimizer = PredictiveOptimizer(self.config)
        
        # Data storage
        self.user_patterns: Dict[str, UserBehaviorPattern] = {}
        self.performance_history: List[PerformanceMetrics] = []
        self.adaptation_callbacks: List[Callable] = []
          # Memory tracking (simplified)
        self.memory_tracker = MemoryTracker() if MemoryTracker else None
        
        # Rich enhancements
        if RICH_AVAILABLE:
            self.rich_text = RichTextManager()
            self.logger = RichLogger("MLAdaptationEngine")
            self.status_animation = RichStatusAnimation()
        else:
            self.logger = logging.getLogger(__name__)
        
        # Load existing data
        self._load_user_data()
    
    def _load_user_data(self):
        """Load existing user behavior data."""
        patterns_file = self.data_dir / "user_patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    for pattern_data in data.get('patterns', []):
                        pattern = UserBehaviorPattern(**pattern_data)
                        self.user_patterns[pattern.pattern_id] = pattern
                self.logger.info(f"Loaded {len(self.user_patterns)} user patterns")
            except Exception as e:
                self.logger.error(f"Failed to load user patterns: {e}")
    
    def _save_user_data(self):
        """Save user behavior data to disk."""
        patterns_file = self.data_dir / "user_patterns.json"
        try:
            data = {
                "patterns": [asdict(pattern) for pattern in self.user_patterns.values()],
                "last_updated": datetime.now().isoformat()
            }
            with open(patterns_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save user patterns: {e}")
    
    def register_user_session(self, user_id: str, session_data: Dict[str, Any]):
        """Register a user session for behavior analysis."""
        pattern_id = f"{user_id}_{datetime.now().strftime('%Y%m')}"
        
        if pattern_id not in self.user_patterns:
            self.user_patterns[pattern_id] = UserBehaviorPattern(
                pattern_id=pattern_id,
                user_id=user_id
            )
        
        pattern = self.user_patterns[pattern_id]
        
        # Update pattern with session data
        pattern.session_count += 1
        pattern.avg_session_duration = (
            (pattern.avg_session_duration * (pattern.session_count - 1) + 
             session_data.get('duration', 0)) / pattern.session_count
        )
        
        # Update preferences
        if 'quality_level' in session_data:
            pattern.preferred_quality_level = session_data['quality_level']
        
        if 'memory_usage' in session_data:
            pattern.preferred_memory_usage = session_data['memory_usage']
        
        # Update operations
        operations = session_data.get('operations', [])
        for op in operations:
            if op not in pattern.common_operations:
                pattern.common_operations.append(op)
        
        # Update peak hours
        current_hour = datetime.now().hour
        if current_hour not in pattern.peak_usage_hours:
            pattern.peak_usage_hours.append(current_hour)
        
        pattern.last_updated = datetime.now().isoformat()
        
        # Trigger adaptation if enough data
        if pattern.session_count % self.config.cluster_update_frequency == 0:
            self._trigger_adaptation()
    
    def add_performance_metrics(self, metrics: PerformanceMetrics, 
                              parameters: Dict[str, float]):
        """Add performance metrics for optimization learning."""
        self.performance_history.append(metrics)
        self.predictive_optimizer.add_performance_data(metrics, parameters)
        
        # Trigger model retraining periodically
        if len(self.performance_history) % 20 == 0:
            self._retrain_models()
    
    def _trigger_adaptation(self):
        """Trigger ML-based adaptation process."""
        if not self.user_patterns:
            return
        
        patterns_list = list(self.user_patterns.values())
        
        # Fit behavior patterns
        clustering_results = self.behavior_analyzer.fit_patterns(patterns_list)
        
        if clustering_results["status"] == "success":
            # Identify anomalies
            anomalies = self.behavior_analyzer.identify_anomalies(patterns_list)
            
            if anomalies:
                self.logger.warning(f"Detected {len(anomalies)} anomalous behavior patterns")
            
            # Trigger registered callbacks
            for callback in self.adaptation_callbacks:
                try:
                    callback(clustering_results, anomalies)
                except Exception as e:
                    self.logger.error(f"Adaptation callback failed: {e}")
    
    def _retrain_models(self):
        """Retrain predictive models with latest data."""
        training_results = self.predictive_optimizer.train_parameter_models()
        if "status" not in training_results:
            self.logger.info(f"Retrained {len(training_results)} parameter models")
    
    def get_user_recommendations(self, user_id: str, 
                               current_metrics: Optional[PerformanceMetrics] = None) -> Dict[str, Any]:
        """Get personalized recommendations for a user."""
        # Find user patterns
        user_patterns = [p for p in self.user_patterns.values() if p.user_id == user_id]
        
        if not user_patterns:
            return {"status": "no_user_data", "recommendations": {}}
        
        latest_pattern = max(user_patterns, key=lambda p: p.last_updated)
        
        recommendations = {
            "preferred_quality": latest_pattern.preferred_quality_level,
            "preferred_memory_usage": latest_pattern.preferred_memory_usage,
            "common_operations": latest_pattern.common_operations[:5],
            "peak_hours": latest_pattern.peak_usage_hours,
            "cluster_id": latest_pattern.cluster_id,
            "is_anomalous": latest_pattern.anomaly_score < -self.config.anomaly_threshold
        }
        
        # Add predictive optimization if metrics available
        if current_metrics and self.predictive_optimizer.parameter_models:
            predicted_params = self.predictive_optimizer.predict_optimal_parameters(current_metrics)
            recommendations["predicted_parameters"] = predicted_params
        
        return {"status": "success", "recommendations": recommendations}
    
    def register_adaptation_callback(self, callback: Callable):
        """Register a callback for adaptation events."""
        self.adaptation_callbacks.append(callback)
    
    def get_adaptation_status(self) -> Dict[str, Any]:
        """Get current adaptation engine status."""
        memory_usage = self.memory_tracker.get_memory_usage()
        
        return {
            "engine_status": "active",
            "user_patterns_count": len(self.user_patterns),
            "performance_history_count": len(self.performance_history),
            "models_trained": len(self.predictive_optimizer.parameter_models),
            "clustering_fitted": self.behavior_analyzer.is_fitted,
            "memory_usage_mb": memory_usage["current_mb"],
            "data_directory": str(self.data_dir),
            "last_adaptation": max([p.last_updated for p in self.user_patterns.values()] 
                                 if self.user_patterns else [datetime.now().isoformat()])
        }
    
    async def adaptive_parameter_tuning(self, user_id: str, 
                                      current_performance: PerformanceMetrics) -> Dict[str, float]:
        """Perform adaptive parameter tuning for a specific user."""
        recommendations = self.get_user_recommendations(user_id, current_performance)
        
        if recommendations["status"] != "success":
            return {}
        
        # Get predicted parameters
        predicted_params = recommendations["recommendations"].get("predicted_parameters", {})
        
        # Apply learning rate for gradual adaptation
        adapted_params = {}
        for param_name, predicted_value in predicted_params.items():
            # Gradual adaptation using learning rate
            current_value = getattr(current_performance, param_name, predicted_value)
            adapted_value = (
                current_value * (1 - self.config.learning_rate) + 
                predicted_value * self.config.learning_rate
            )
            adapted_params[param_name] = adapted_value
        
        return adapted_params
    
    def detect_usage_anomalies(self, user_id: str) -> Dict[str, Any]:
        """Detect anomalies in user usage patterns."""
        user_patterns = [p for p in self.user_patterns.values() if p.user_id == user_id]
        
        if not user_patterns:
            return {"status": "no_data", "anomalies": []}
        
        anomalous_patterns = []
        for pattern in user_patterns:
            if pattern.anomaly_score < -self.config.anomaly_threshold:
                anomalous_patterns.append({
                    "pattern_id": pattern.pattern_id,
                    "anomaly_score": pattern.anomaly_score,
                    "session_count": pattern.session_count,
                    "last_updated": pattern.last_updated
                })
        
        return {
            "status": "success",
            "total_patterns": len(user_patterns),
            "anomalous_patterns": len(anomalous_patterns),
            "anomalies": anomalous_patterns
        }
    
    def shutdown(self):
        """Shutdown the adaptation engine and save data."""
        self._save_user_data()
        
        if RICH_AVAILABLE and self.status_animation:
            self.status_animation.stop()
        
        self.logger.info("ML Adaptation Engine shutdown complete")


# Example usage and testing functions
def create_test_adaptation_engine() -> MLAdaptationEngine:
    """Create a test adaptation engine with sample configuration."""
    config = AdaptationParameters(
        learning_rate=0.05,
        adaptation_threshold=0.15,
        pattern_window_size=50,
        cluster_update_frequency=25,
        anomaly_threshold=0.6,
        parameter_ranges={
            "memory_usage": (0.1, 0.9),
            "quality_scale": (0.5, 1.0),
            "batch_size": (1, 16)
        },
        feature_weights={
            "session_duration": 0.3,
            "memory_preference": 0.4,
            "operation_frequency": 0.3
        }
    )
    
    return MLAdaptationEngine(config=config)


def simulate_user_behavior(engine: MLAdaptationEngine, user_id: str, num_sessions: int = 10):
    """Simulate user behavior for testing purposes."""
    import random
    
    operations = ["text_generation", "image_processing", "multimodal_fusion", "context_extension"]
    quality_levels = ["low", "medium", "high", "ultra"]
    
    for i in range(num_sessions):
        session_data = {
            "duration": random.uniform(300, 3600),  # 5min to 1hr
            "quality_level": random.choice(quality_levels),
            "memory_usage": random.uniform(0.3, 0.9),
            "operations": random.sample(operations, k=random.randint(1, 3))
        }
        
        engine.register_user_session(user_id, session_data)
        
        # Add performance metrics
        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            response_time=random.uniform(0.1, 2.0),
            memory_usage=session_data["memory_usage"],
            cpu_usage=random.uniform(0.2, 0.8),
            user_satisfaction=random.uniform(0.6, 1.0),
            quality_score=random.uniform(0.7, 1.0),
            efficiency_ratio=random.uniform(0.5, 0.9)
        )
        
        parameters = {
            "memory_usage": session_data["memory_usage"],
            "quality_scale": 0.8,
            "batch_size": random.randint(2, 8)
        }
        
        engine.add_performance_metrics(metrics, parameters)


if __name__ == "__main__":
    # Test the ML adaptation engine
    print("🧠 Testing ML-Based Adaptation Engine...")
    
    engine = create_test_adaptation_engine()
    
    # Simulate multiple users
    users = ["user_001", "user_002", "user_003"]
    for user_id in users:
        simulate_user_behavior(engine, user_id, num_sessions=15)
    
    # Get recommendations
    for user_id in users:
        recommendations = engine.get_user_recommendations(user_id)
        print(f"\n👤 Recommendations for {user_id}:")
        print(f"   Status: {recommendations['status']}")
        if recommendations['status'] == 'success':
            recs = recommendations['recommendations']
            print(f"   Preferred Quality: {recs['preferred_quality']}")
            print(f"   Memory Usage: {recs['preferred_memory_usage']:.2f}")
            print(f"   Cluster ID: {recs['cluster_id']}")
            print(f"   Is Anomalous: {recs['is_anomalous']}")
    
    # Check adaptation status
    status = engine.get_adaptation_status()
    print(f"\n📊 Adaptation Engine Status:")
    print(f"   User Patterns: {status['user_patterns_count']}")
    print(f"   Performance History: {status['performance_history_count']}")
    print(f"   Models Trained: {status['models_trained']}")
    print(f"   Clustering Fitted: {status['clustering_fitted']}")
    print(f"   Memory Usage: {status['memory_usage_mb']:.2f} MB")
    
    # Test anomaly detection
    anomalies = engine.detect_usage_anomalies("user_001")
    print(f"\n🚨 Anomaly Detection for user_001:")
    print(f"   Status: {anomalies['status']}")
    print(f"   Anomalous Patterns: {anomalies.get('anomalous_patterns', 0)}")
    
    # Cleanup
    engine.shutdown()
    print("\n✅ ML Adaptation Engine testing complete!")
