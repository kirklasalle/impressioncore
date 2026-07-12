"""
ImpressionCore UX - Phase 7C Integration Module
===============================================

This module integrates all Phase 7C components (ML Adaptation, Feedback System, and 
Predictive Optimization) into a unified adaptive learning and feedback system. It provides
a single interface for coordinating intelligent user experience optimization.

Components Integrated:
- ML-Based Adaptation Engine (src/core/ux/ml_adaptation.py)
- Comprehensive Feedback System (src/core/ux/feedback_system.py)
- Predictive Optimization Engine (src/core/ux/predictive_optimizer.py)

Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Architecture: Brain-inspired multimodal framework
Focus: Unified adaptive user experience optimization

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

# Core framework imports
try:
    from src.core.utils.rich_enhancements import RichTextManager
    from src.core.utils.rich_logging import RichLogger
    from src.core.utils.rich_status_animation import RichStatusAnimation
    CORE_UTILS_AVAILABLE = True
    MemoryTracker = None  # Use simplified memory tracking
except ImportError:
    try:
        from src.core.utils.rich_enhancements import RichTextManager
        from src.core.utils.rich_logging import RichLogger
        from src.core.utils.rich_status_animation import RichStatusAnimation
        CORE_UTILS_AVAILABLE = True
        MemoryTracker = None  # Use simplified memory tracking
    except ImportError:
        CORE_UTILS_AVAILABLE = False
        RichTextManager = None
        RichLogger = logging.getLogger(__name__)
        RichStatusAnimation = None
        MemoryTracker = None

# Phase 7C component imports
try:
    from src.core.ux.ml_adaptation import (
        MLAdaptationEngine, 
        UserBehaviorPattern, 
        AdaptationParameters,
        PerformanceMetrics
    )
    from src.core.ux.feedback_system import (
        ComprehensiveFeedbackSystem,
        FeedbackType,
        SatisfactionMetrics,
        PerformanceCorrelation
    )
    from src.core.ux.predictive_optimizer import (
        PredictiveOptimizer,
        PredictionType,
        OptimizationRecommendation,
        OptimizationStrategy,
        UsagePattern
    )
except ImportError:
    try:
        from src.core.ux.ml_adaptation import (
            MLAdaptationEngine, 
            UserBehaviorPattern, 
            AdaptationParameters,
            PerformanceMetrics
        )
        from src.core.ux.feedback_system import (
            ComprehensiveFeedbackSystem,
            FeedbackType,
            SatisfactionMetrics,
            PerformanceCorrelation
        )
        from src.core.ux.predictive_optimizer import (
            PredictiveOptimizer,
            PredictionType,
            OptimizationRecommendation,
            OptimizationStrategy,
            UsagePattern
        )
    except ImportError:
        raise ImportError("Phase 7C components not available")


class AdaptiveLearningMode(Enum):
    """Modes of operation for the adaptive learning system."""
    PASSIVE = "passive"  # Only collect data, no active adaptation
    LEARNING = "learning"  # Active learning but conservative adaptation
    ADAPTIVE = "adaptive"  # Full adaptive optimization
    AGGRESSIVE = "aggressive"  # Aggressive optimization for power users


@dataclass
class SystemState:
    """Current state of the adaptive learning system."""
    timestamp: datetime
    active_users: int
    total_sessions: int
    adaptation_mode: AdaptiveLearningMode
    feedback_count: int
    prediction_accuracy: float
    system_health: str
    memory_usage: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['adaptation_mode'] = self.adaptation_mode.value
        return result


class AdaptiveLearningCoordinator:
    """
    Coordinates adaptive learning across all Phase 7C components.
    
    This coordinator:
    - Manages data flow between components
    - Coordinates adaptation decisions
    - Balances system performance with user experience
    - Provides unified interface for adaptive features
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = RichLogger("AdaptiveLearningCoordinator")
        self.rich_manager = RichTextManager()
        self.memory_tracker = MemoryTracker()
        
        # Storage configuration
        self.storage_path = Path(storage_path or "data/adaptive_learning")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize core components
        self.ml_adaptation = MLAdaptationEngine(str(self.storage_path / "ml_adaptation"))
        self.feedback_system = ComprehensiveFeedbackSystem(str(self.storage_path / "feedback"))
        self.predictive_optimizer = PredictiveOptimizer(str(self.storage_path / "predictions"))
        
        # System configuration
        self.adaptation_mode = AdaptiveLearningMode.ADAPTIVE
        self.coordination_interval = 30  # seconds
        self.min_feedback_threshold = 5  # Minimum feedback before adaptation
        
        # Coordination state
        self.user_sessions = {}
        self.adaptation_history = []
        self.performance_metrics = {
            'adaptation_accuracy': 0.0,
            'user_satisfaction': 0.0,
            'system_efficiency': 0.0,
            'prediction_accuracy': 0.0
        }
        
        # Background coordination
        self.coordination_thread = None
        self.stop_coordination = threading.Event()
        
        # Integration callbacks
        self.setup_integration_callbacks()
        
        self.logger.info("Adaptive Learning Coordinator initialized")
    
    def setup_integration_callbacks(self):
        """Set up callbacks for component integration."""
        # ML Adaptation callbacks
        def on_adaptation_update(user_id: str, parameters: AdaptationParameters):
            self._handle_adaptation_update(user_id, parameters)
        
        self.ml_adaptation.register_adaptation_callback(on_adaptation_update)
        
        # Feedback system callbacks
        def on_satisfaction_change(metrics: SatisfactionMetrics):
            self._handle_satisfaction_change(metrics)
        
        self.feedback_system.register_adaptation_callback(on_satisfaction_change)
        
        # Predictive optimizer callbacks
        def on_optimization_recommendation(recommendation: OptimizationRecommendation):
            self._handle_optimization_recommendation(recommendation)
        
        self.predictive_optimizer.register_optimization_callback(on_optimization_recommendation)
    
    def start_user_session(self, 
                          user_id: str,
                          session_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new adaptive learning session for a user.
        
        Args:
            user_id: Unique user identifier
            session_config: Optional session configuration
            
        Returns:
            Session ID for tracking
        """
        session_id = f"session_{int(time.time() * 1000)}_{user_id}"
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'start_time': datetime.now(),
            'config': session_config or {},
            'feedback_count': 0,
            'adaptations_applied': 0,
            'performance_metrics': {},
            'usage_patterns': []
        }
        
        self.user_sessions[session_id] = session_data
        
        # Initialize ML adaptation for user
        if self.adaptation_mode != AdaptiveLearningMode.PASSIVE:
            self.ml_adaptation.start_user_session(user_id, session_id)
        
        self.logger.info(f"Started adaptive learning session {session_id} for user {user_id}")
        return session_id
    
    def record_user_interaction(self,
                              session_id: str,
                              interaction_type: str,
                              interaction_data: Dict[str, Any],
                              performance_metrics: Optional[Dict[str, float]] = None) -> bool:
        """
        Record user interaction for adaptive learning.
        
        Args:
            session_id: Session identifier
            interaction_type: Type of interaction (e.g., "text_generation", "image_processing")
            interaction_data: Interaction-specific data
            performance_metrics: Performance metrics for this interaction
            
        Returns:
            True if recorded successfully
        """
        if session_id not in self.user_sessions:
            self.logger.warning(f"Unknown session: {session_id}")
            return False
        
        session = self.user_sessions[session_id]
        user_id = session['user_id']
        
        try:
            # Record behavioral feedback
            self.feedback_system.collect_behavioral_feedback(
                user_id=user_id,
                session_id=session_id,
                interaction_data={
                    'interaction_type': interaction_type,
                    'timestamp': datetime.now().isoformat(),
                    **interaction_data
                },
                performance_metrics=performance_metrics or {}
            )
            
            # Record ML adaptation data
            if self.adaptation_mode in [AdaptiveLearningMode.LEARNING, AdaptiveLearningMode.ADAPTIVE, AdaptiveLearningMode.AGGRESSIVE]:
                behavior_pattern = UserBehaviorPattern(
                    user_id=user_id,
                    session_id=session_id,
                    timestamp=datetime.now(),
                    action_type=interaction_type,
                    action_details=interaction_data,
                    performance_metrics=PerformanceMetrics(
                        response_time=performance_metrics.get('response_time_ms', 0),
                        memory_usage=performance_metrics.get('memory_usage_mb', 0),
                        cpu_usage=performance_metrics.get('cpu_usage_percent', 0),
                        quality_score=performance_metrics.get('quality_score', 0.8),
                        error_rate=performance_metrics.get('error_rate', 0.0)
                    )
                )
                
                self.ml_adaptation.learn_from_behavior(behavior_pattern)
            
            # Record usage pattern for prediction
            if interaction_type in session['config'].get('track_for_prediction', [interaction_type]):
                self._record_usage_pattern(session, interaction_type, interaction_data, performance_metrics)
            
            # Update session metrics
            session['performance_metrics'] = performance_metrics or {}
            
            self.logger.debug(f"Recorded interaction {interaction_type} for session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record user interaction: {e}")
            return False
    
    def collect_explicit_feedback(self,
                                session_id: str,
                                feedback_type: FeedbackType,
                                feedback_content: Union[str, int, float],
                                context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Collect explicit feedback from user.
        
        Args:
            session_id: Session identifier
            feedback_type: Type of feedback
            feedback_content: Feedback content
            context: Additional context
            
        Returns:
            True if collected successfully
        """
        if session_id not in self.user_sessions:
            self.logger.warning(f"Unknown session: {session_id}")
            return False
        
        session = self.user_sessions[session_id]
        user_id = session['user_id']
        
        try:
            # Collect feedback through feedback system
            feedback_id = self.feedback_system.collector.collect_explicit_feedback(
                user_id=user_id,
                session_id=session_id,
                feedback_type=feedback_type,
                content=feedback_content,
                context=context
            )
            
            # Update session feedback count
            session['feedback_count'] += 1
            
            # Trigger adaptation if enough feedback collected
            if (session['feedback_count'] >= self.min_feedback_threshold and 
                self.adaptation_mode in [AdaptiveLearningMode.ADAPTIVE, AdaptiveLearningMode.AGGRESSIVE]):
                self._trigger_adaptation_review(user_id, session_id)
            
            self.logger.info(f"Collected {feedback_type.value} feedback for session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to collect explicit feedback: {e}")
            return False
    
    def get_adaptive_recommendations(self, 
                                   user_id: str,
                                   current_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get adaptive recommendations for user configuration.
        
        Args:
            user_id: User identifier
            current_config: Current system configuration
            
        Returns:
            Adaptive recommendations including confidence scores
        """
        recommendations = {
            'ml_adaptations': {},
            'predictive_optimizations': [],
            'feedback_insights': {},
            'confidence_score': 0.0,
            'recommended_config': current_config.copy()
        }
        
        try:
            # Get ML-based adaptations
            if self.adaptation_mode != AdaptiveLearningMode.PASSIVE:
                ml_adaptations = self.ml_adaptation.get_user_adaptations(user_id)
                if ml_adaptations:
                    recommendations['ml_adaptations'] = {
                        'parameters': ml_adaptations.to_dict(),
                        'confidence': ml_adaptations.confidence_score
                    }
            
            # Get predictive optimizations
            pred_recommendations = self.predictive_optimizer.generate_optimization_recommendations(
                user_id, current_config
            )
            recommendations['predictive_optimizations'] = [
                rec.to_dict() for rec in pred_recommendations
            ]
            
            # Get satisfaction insights
            satisfaction = self.feedback_system.analyze_user_satisfaction(user_id)
            recommendations['feedback_insights'] = {
                'satisfaction_score': satisfaction.satisfaction_score,
                'trend': satisfaction.trend_direction,
                'confidence': satisfaction.confidence_level
            }
            
            # Calculate overall confidence
            confidences = []
            if recommendations['ml_adaptations']:
                confidences.append(recommendations['ml_adaptations']['confidence'])
            if recommendations['feedback_insights']:
                confidences.append(recommendations['feedback_insights']['confidence'])
            if pred_recommendations:
                confidences.extend([rec.confidence_level for rec in pred_recommendations])
            
            recommendations['confidence_score'] = np.mean(confidences) if confidences else 0.0
            
            # Generate recommended configuration
            recommendations['recommended_config'] = self._merge_recommendations(
                current_config, recommendations
            )
            
            self.logger.info(f"Generated adaptive recommendations for user {user_id} "
                           f"(confidence: {recommendations['confidence_score']:.2f})")
            
        except Exception as e:
            self.logger.error(f"Failed to get adaptive recommendations: {e}")
        
        return recommendations
    
    def apply_adaptive_configuration(self,
                                   user_id: str,
                                   session_id: str,
                                   recommended_config: Dict[str, Any]) -> bool:
        """
        Apply adaptive configuration changes.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            recommended_config: Configuration to apply
            
        Returns:
            True if applied successfully
        """
        if session_id not in self.user_sessions:
            self.logger.warning(f"Unknown session: {session_id}")
            return False
        
        try:
            session = self.user_sessions[session_id]
            
            # Apply ML adaptations
            if 'ml_parameters' in recommended_config:
                adaptation_params = AdaptationParameters(**recommended_config['ml_parameters'])
                self.ml_adaptation.apply_adaptation(user_id, adaptation_params)
            
            # Update session configuration
            session['config'].update(recommended_config)
            session['adaptations_applied'] += 1
            
            # Record adaptation in history
            self.adaptation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'session_id': session_id,
                'config_changes': recommended_config,
                'adaptation_count': session['adaptations_applied']
            })
            
            self.logger.info(f"Applied adaptive configuration for user {user_id} in session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply adaptive configuration: {e}")
            return False
    
    def _record_usage_pattern(self,
                            session: Dict[str, Any],
                            interaction_type: str,
                            interaction_data: Dict[str, Any],
                            performance_metrics: Optional[Dict[str, float]]):
        """Record usage pattern for predictive optimization."""
        try:
            # Calculate session duration so far
            session_duration = (datetime.now() - session['start_time']).total_seconds()
            
            # Record usage pattern
            self.predictive_optimizer.record_usage_pattern(
                user_id=session['user_id'],
                session_duration=session_duration,
                features_used=[interaction_type],
                resource_usage={
                    'memory_mb': performance_metrics.get('memory_usage_mb', 0),
                    'cpu_percent': performance_metrics.get('cpu_usage_percent', 0),
                    'gpu_memory_mb': performance_metrics.get('gpu_memory_mb', 0)
                },
                quality_settings=session['config'].get('quality_settings', {}),
                performance_metrics=performance_metrics or {},
                context={'interaction_type': interaction_type}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to record usage pattern: {e}")
    
    def _handle_adaptation_update(self, user_id: str, parameters: AdaptationParameters):
        """Handle ML adaptation updates."""
        self.logger.debug(f"ML adaptation update for user {user_id}: "
                         f"learning_rate={parameters.learning_rate:.4f}")
        
        # Update performance metrics
        self.performance_metrics['adaptation_accuracy'] = parameters.confidence_score
    
    def _handle_satisfaction_change(self, metrics: SatisfactionMetrics):
        """Handle satisfaction changes from feedback system."""
        self.logger.debug(f"Satisfaction change for user {metrics.user_id}: "
                         f"score={metrics.satisfaction_score:.1f}, trend={metrics.trend_direction}")
        
        # Update performance metrics
        self.performance_metrics['user_satisfaction'] = metrics.satisfaction_score / 100.0
        
        # Trigger adaptation if satisfaction is declining
        if (metrics.trend_direction == "declining" and 
            metrics.satisfaction_score < 60 and
            self.adaptation_mode == AdaptiveLearningMode.AGGRESSIVE):
            self._trigger_emergency_adaptation(metrics.user_id)
    
    def _handle_optimization_recommendation(self, recommendation: OptimizationRecommendation):
        """Handle optimization recommendations from predictive optimizer."""
        self.logger.debug(f"Optimization recommendation for user {recommendation.user_id}: "
                         f"priority={recommendation.priority}, strategy={recommendation.strategy.value}")
        
        # Auto-apply high-priority recommendations in aggressive mode
        if (recommendation.priority >= 4 and 
            self.adaptation_mode == AdaptiveLearningMode.AGGRESSIVE):
            self._auto_apply_recommendation(recommendation)
    
    def _trigger_adaptation_review(self, user_id: str, session_id: str):
        """Trigger review of adaptations for a user session."""
        try:
            session = self.user_sessions.get(session_id)
            if not session:
                return
            
            # Get current recommendations
            recommendations = self.get_adaptive_recommendations(user_id, session['config'])
            
            # Apply if confidence is high enough
            min_confidence = {
                AdaptiveLearningMode.LEARNING: 0.8,
                AdaptiveLearningMode.ADAPTIVE: 0.6,
                AdaptiveLearningMode.AGGRESSIVE: 0.4
            }.get(self.adaptation_mode, 0.8)
            
            if recommendations['confidence_score'] >= min_confidence:
                self.apply_adaptive_configuration(
                    user_id, session_id, recommendations['recommended_config']
                )
            
        except Exception as e:
            self.logger.error(f"Adaptation review failed: {e}")
    
    def _trigger_emergency_adaptation(self, user_id: str):
        """Trigger emergency adaptation for declining satisfaction."""
        self.logger.warning(f"Emergency adaptation triggered for user {user_id}")
        
        # Apply conservative optimization
        emergency_config = {
            'quality_scale': 0.9,  # Increase quality
            'response_priority': 'high',  # Prioritize responsiveness
            'error_tolerance': 'low'  # Reduce error tolerance
        }
        
        # Find active sessions for user
        for session_id, session in self.user_sessions.items():
            if session['user_id'] == user_id:
                self.apply_adaptive_configuration(user_id, session_id, emergency_config)
                break
    
    def _auto_apply_recommendation(self, recommendation: OptimizationRecommendation):
        """Auto-apply high-priority optimization recommendations."""
        try:
            # Find active session for user
            user_sessions = [
                (sid, session) for sid, session in self.user_sessions.items()
                if session['user_id'] == recommendation.user_id
            ]
            
            if user_sessions:
                session_id, session = user_sessions[0]  # Use most recent session
                
                # Convert recommendation to config changes
                config_changes = self._recommendation_to_config(recommendation)
                
                if config_changes:
                    self.apply_adaptive_configuration(
                        recommendation.user_id, session_id, config_changes
                    )
            
        except Exception as e:
            self.logger.error(f"Auto-apply recommendation failed: {e}")
    
    def _recommendation_to_config(self, recommendation: OptimizationRecommendation) -> Dict[str, Any]:
        """Convert optimization recommendation to configuration changes."""
        config_changes = {}
        
        for key, value in recommendation.recommendations.items():
            if key == 'adjust_quality_settings' and isinstance(value, dict):
                config_changes['quality_scale'] = value.get('recommended_quality_scale', 0.8)
            elif key == 'increase_memory_allocation' and isinstance(value, dict):
                config_changes['memory_allocation_mb'] = value.get('recommended', 1500)
            elif key == 'adjust_gpu_allocation' and isinstance(value, dict):
                config_changes['gpu_memory_mb'] = value.get('recommended', 1500)
        
        return config_changes
    
    def _merge_recommendations(self, 
                             current_config: Dict[str, Any],
                             recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Merge recommendations into a unified configuration."""
        merged_config = current_config.copy()
        
        # Apply ML adaptations
        if recommendations.get('ml_adaptations') and recommendations['ml_adaptations'].get('parameters'):
            ml_params = recommendations['ml_adaptations']['parameters']
            merged_config.update({
                'learning_rate': ml_params.get('learning_rate', 0.01),
                'adaptation_threshold': ml_params.get('adaptation_threshold', 0.1)
            })
        
        # Apply predictive optimizations
        for pred_rec in recommendations.get('predictive_optimizations', []):
            rec_dict = pred_rec if isinstance(pred_rec, dict) else pred_rec.to_dict()
            for key, value in rec_dict.get('recommendations', {}).items():
                if isinstance(value, dict) and 'recommended' in value:
                    config_key = key.replace('adjust_', '').replace('increase_', '')
                    merged_config[config_key] = value['recommended']
        
        return merged_config
    
    def end_user_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a user session and return summary metrics.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary with adaptive learning metrics
        """
        if session_id not in self.user_sessions:
            self.logger.warning(f"Unknown session: {session_id}")
            return {}
        
        session = self.user_sessions.pop(session_id)
        
        # Calculate session metrics
        session_duration = (datetime.now() - session['start_time']).total_seconds()
        
        summary = {
            'session_id': session_id,
            'user_id': session['user_id'],
            'duration_seconds': session_duration,
            'feedback_count': session['feedback_count'],
            'adaptations_applied': session['adaptations_applied'],
            'final_performance': session['performance_metrics'],
            'adaptive_learning_effectiveness': self._calculate_session_effectiveness(session)
        }
        
        # End ML adaptation session
        if self.adaptation_mode != AdaptiveLearningMode.PASSIVE:
            self.ml_adaptation.end_user_session(session['user_id'], session_id)
        
        self.logger.info(f"Ended adaptive learning session {session_id}, duration: {session_duration:.1f}s")
        return summary
    
    def _calculate_session_effectiveness(self, session: Dict[str, Any]) -> float:
        """Calculate adaptive learning effectiveness for a session."""
        try:
            # Base effectiveness on adaptation count and feedback
            adaptations = session['adaptations_applied']
            feedback_count = session['feedback_count']
            
            if feedback_count == 0:
                return 0.0
            
            # Effectiveness increases with successful adaptations
            effectiveness = min(1.0, (adaptations * 0.2) + (feedback_count * 0.1))
            
            # Bonus for performance improvements
            if session['performance_metrics']:
                perf_score = session['performance_metrics'].get('quality_score', 0.5)
                effectiveness *= (1.0 + perf_score * 0.2)
            
            return min(1.0, effectiveness)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate session effectiveness: {e}")
            return 0.0
    
    def get_system_state(self) -> SystemState:
        """Get current system state and health metrics."""
        try:
            # Count active users and sessions
            active_users = len(set(session['user_id'] for session in self.user_sessions.values()))
            total_sessions = len(self.user_sessions)
            
            # Get component health
            ml_status = self.ml_adaptation.get_system_status()
            feedback_status = self.feedback_system.get_system_status()
            pred_status = self.predictive_optimizer.get_system_status()
            
            # Calculate overall prediction accuracy
            prediction_accuracy = np.mean([
                self.performance_metrics.get('adaptation_accuracy', 0.0),
                self.performance_metrics.get('prediction_accuracy', 0.0)
            ])
            
            # Determine system health
            component_health = [
                ml_status.get('system_health', 'unknown'),
                feedback_status.get('system_health', 'unknown'),
                pred_status.get('system_health', 'unknown')
            ]
            
            if all(h == 'healthy' for h in component_health):
                system_health = 'healthy'
            elif any(h == 'error' for h in component_health):
                system_health = 'error'
            else:
                system_health = 'warning'
            
            return SystemState(
                timestamp=datetime.now(),
                active_users=active_users,
                total_sessions=total_sessions,
                adaptation_mode=self.adaptation_mode,
                feedback_count=feedback_status.get('feedback_collector', {}).get('total_feedback', 0),
                prediction_accuracy=prediction_accuracy,
                system_health=system_health,
                memory_usage=self.memory_tracker.get_memory_usage()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get system state: {e}")
            return SystemState(
                timestamp=datetime.now(),
                active_users=0,
                total_sessions=0,
                adaptation_mode=self.adaptation_mode,
                feedback_count=0,
                prediction_accuracy=0.0,
                system_health='error',
                memory_usage={}
            )
    
    def start_background_coordination(self):
        """Start background coordination thread."""
        if self.coordination_thread and self.coordination_thread.is_alive():
            return
        
        self.stop_coordination.clear()
        self.coordination_thread = threading.Thread(
            target=self._background_coordination_loop,
            daemon=True
        )
        self.coordination_thread.start()
        
        # Start component background processing
        self.ml_adaptation.start_background_adaptation()
        self.feedback_system.start_background_processing()
        self.predictive_optimizer.start_background_optimization()
        
        self.logger.info("Started background adaptive learning coordination")
    
    def stop_background_coordination(self):
        """Stop background coordination thread."""
        self.stop_coordination.set()
        if self.coordination_thread:
            self.coordination_thread.join(timeout=5)
        
        # Stop component background processing
        self.ml_adaptation.stop_background_adaptation()
        self.feedback_system.stop_background_processing()
        self.predictive_optimizer.stop_background_optimization()
        
        self.logger.info("Stopped background adaptive learning coordination")
    
    def _background_coordination_loop(self):
        """Background coordination processing loop."""
        while not self.stop_coordination.wait(self.coordination_interval):
            try:
                # Update performance metrics
                self._update_performance_metrics()
                
                # Clean up old sessions
                self._cleanup_old_sessions()
                
                # Optimize system resources
                self._optimize_system_resources()
                
            except Exception as e:
                self.logger.error(f"Background coordination error: {e}")
    
    def _update_performance_metrics(self):
        """Update system performance metrics."""
        try:
            # Get component metrics
            ml_status = self.ml_adaptation.get_system_status()
            feedback_status = self.feedback_system.get_system_status()
            pred_status = self.predictive_optimizer.get_system_status()
            
            # Update coordination metrics
            self.performance_metrics.update({
                'system_efficiency': self._calculate_system_efficiency(),
                'coordination_health': 1.0 if all(
                    status.get('system_health') == 'healthy' 
                    for status in [ml_status, feedback_status, pred_status]
                ) else 0.5
            })
            
        except Exception as e:
            self.logger.error(f"Performance metrics update failed: {e}")
    
    def _calculate_system_efficiency(self) -> float:
        """Calculate overall system efficiency."""
        try:
            # Base efficiency on active sessions and resource usage
            active_sessions = len(self.user_sessions)
            memory_usage = self.memory_tracker.get_memory_usage()
            
            if active_sessions == 0:
                return 1.0
            
            # Efficiency decreases with high memory usage
            memory_efficiency = 1.0 - (memory_usage.get('percent', 0) / 100.0)
            
            # Efficiency based on adaptation success rate
            recent_adaptations = self.adaptation_history[-10:] if self.adaptation_history else []
            adaptation_efficiency = len(recent_adaptations) / max(1, active_sessions)
            
            return min(1.0, (memory_efficiency + adaptation_efficiency) / 2.0)
            
        except Exception as e:
            self.logger.error(f"System efficiency calculation failed: {e}")
            return 0.5
    
    def _cleanup_old_sessions(self):
        """Clean up old sessions that may have been abandoned."""
        current_time = datetime.now()
        max_session_age = timedelta(hours=2)
        
        sessions_to_remove = []
        for session_id, session in self.user_sessions.items():
            if current_time - session['start_time'] > max_session_age:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self.end_user_session(session_id)
            self.logger.warning(f"Cleaned up abandoned session: {session_id}")
    
    def _optimize_system_resources(self):
        """Optimize system resources based on current load."""
        try:
            memory_usage = self.memory_tracker.get_memory_usage()
            active_sessions = len(self.user_sessions)
            
            # Adjust adaptation mode based on system load
            if memory_usage.get('percent', 0) > 85:
                if self.adaptation_mode == AdaptiveLearningMode.AGGRESSIVE:
                    self.adaptation_mode = AdaptiveLearningMode.ADAPTIVE
                    self.logger.info("Reduced adaptation mode due to high memory usage")
            elif memory_usage.get('percent', 0) < 50 and active_sessions > 0:
                if self.adaptation_mode == AdaptiveLearningMode.ADAPTIVE:
                    self.adaptation_mode = AdaptiveLearningMode.AGGRESSIVE
                    self.logger.info("Increased adaptation mode due to available resources")
            
        except Exception as e:
            self.logger.error(f"Resource optimization failed: {e}")


# Example usage and testing functions
def demonstrate_phase_7c_integration():
    """Demonstrate the Phase 7C integration capabilities."""
    # Initialize the coordinator
    coordinator = AdaptiveLearningCoordinator()
    
    # Start background coordination
    coordinator.start_background_coordination()
    
    # Start a user session
    user_id = "demo_user_001"
    session_id = coordinator.start_user_session(
        user_id=user_id,
        session_config={
            'quality_settings': {'resolution_scale': 0.8},
            'track_for_prediction': ['text_generation', 'image_processing']
        }
    )
    
    # Simulate user interactions
    for i in range(5):
        coordinator.record_user_interaction(
            session_id=session_id,
            interaction_type="text_generation",
            interaction_data={
                'prompt_length': 100 + i * 20,
                'generation_length': 500 + i * 100,
                'complexity': 'medium'
            },
            performance_metrics={
                'response_time_ms': 200 + i * 50,
                'memory_usage_mb': 1000 + i * 100,
                'cpu_usage_percent': 30 + i * 5,
                'quality_score': 0.8 + i * 0.02,
                'error_rate': 0.01
            }
        )
    
    # Collect explicit feedback
    coordinator.collect_explicit_feedback(
        session_id=session_id,
        feedback_type=FeedbackType.EXPLICIT_RATING,
        feedback_content=4,  # 4/5 rating
        context={'category': 'text_generation', 'satisfaction': 'good'}
    )
    
    coordinator.collect_explicit_feedback(
        session_id=session_id,
        feedback_type=FeedbackType.TEXT_FEEDBACK,
        feedback_content="The system is working well, but could be faster.",
        context={'category': 'performance'}
    )
    
    # Get adaptive recommendations
    recommendations = coordinator.get_adaptive_recommendations(user_id, {
        'quality_scale': 0.8,
        'memory_allocation_mb': 1500,
        'gpu_memory_mb': 1500
    })
    
    print(f"Generated recommendations with confidence: {recommendations['confidence_score']:.2f}")
    
    # Apply adaptive configuration
    if recommendations['confidence_score'] > 0.5:
        coordinator.apply_adaptive_configuration(
            user_id=user_id,
            session_id=session_id,
            recommended_config=recommendations['recommended_config']
        )
    
    # Get system state
    system_state = coordinator.get_system_state()
    print(f"System state: {system_state.system_health} with {system_state.active_users} active users")
    
    # End session
    session_summary = coordinator.end_user_session(session_id)
    print(f"Session effectiveness: {session_summary.get('adaptive_learning_effectiveness', 0):.2f}")
    
    # Stop background coordination
    coordinator.stop_background_coordination()
    
    return coordinator


if __name__ == "__main__":
    # Run demonstration
    system = demonstrate_phase_7c_integration()
    
    # Show final system state
    final_state = system.get_system_state()
    print(f"Final system state: {final_state.to_dict()}")
