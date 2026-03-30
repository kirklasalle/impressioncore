#!/usr/bin/env python3
"""
ImpressionCore Phase 7C - Comprehensive Test Suite
==================================================

Comprehensive testing for Phase 7C: Adaptive Learning and Feedback Systems
Tests all three core components and their integration:
- ML-Based Adaptation Engine
- Comprehensive Feedback System  
- Predictive Optimization Engine
- Phase 7C Integration Module

Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Focus: Production readiness validation with performance testing

Author: GitHub Copilot & Kirk LaSalle
Created: 2025-06-01
Version: 1.0.0
"""

import unittest
import asyncio
import tempfile
import json
import time
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sqlite3
import os
import sys

# Add src to path for imports
# Add project root to path (to allow src.* imports)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import Phase 7C components
try:
    from core.ux.ml_adaptation import (
        MLAdaptationEngine, 
        UserBehaviorPattern, 
        AdaptationParameters,
        PerformanceMetrics,
        BehaviorPatternAnalyzer,
        PredictiveOptimizer as MLPredictiveOptimizer
    )
    from core.ux.feedback_system import (
        ComprehensiveFeedbackSystem,
        FeedbackType,
        SentimentAnalyzer,
        FeedbackAnalyzer,
        FeedbackCollector
    )
    from core.ux.predictive_optimizer import (
        PredictiveOptimizer,
        TimeSeriesPredictor,
        ResourceOptimizer,
        SmartCache
    )
    from core.ux.phase_7c_integration import (
        AdaptiveLearningCoordinator,
        AdaptationMode,
        SystemState
    )
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_SUCCESSFUL = False


class TestMLAdaptationEngine(unittest.TestCase):
    """Test suite for ML-Based Adaptation Engine component."""
    
    def setUp(self):
        """Set up test environment."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required imports not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'session_id': 'test_session',
            'user_id': 'test_user',
            'data_dir': self.temp_dir,
            'adaptation_threshold': 0.1,
            'max_cluster_size': 10,
            'behavior_window': 100
        }
        
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)    def test_ml_adaptation_engine_initialization(self):
        """Test ML adaptation engine initializes correctly."""
        engine = MLAdaptationEngine(
            data_dir=Path(self.test_config['data_dir'])
        )
        
        self.assertIsNotNone(engine)
        self.assertIsInstance(engine.behavior_analyzer, BehaviorPatternAnalyzer)
        self.assertIsInstance(engine.predictive_optimizer, MLPredictiveOptimizer)
    
    def test_behavior_pattern_creation(self):
        """Test behavior pattern creation and analysis."""
        engine = MLAdaptationEngine(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        # Create test pattern
        pattern = UserBehaviorPattern(
            user_id='test_user',
            session_count=10,
            avg_session_duration=300.0,
            preferred_quality='high',
            interaction_frequency=0.8,
            error_rate=0.05,
            satisfaction_score=4.2
        )
        
        result = engine.analyze_behavior_pattern(pattern)
        self.assertIsNotNone(result)
        self.assertIn('classification', result)
        self.assertIn('confidence', result)
        self.assertIn('recommendations', result)
    
    def test_anomaly_detection(self):
        """Test anomaly detection in user behavior."""
        engine = MLAdaptationEngine(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        # Create normal and anomalous patterns
        normal_pattern = UserBehaviorPattern(
            user_id='test_user',
            session_count=10,
            avg_session_duration=300.0,
            preferred_quality='medium',
            interaction_frequency=0.6,
            error_rate=0.03,
            satisfaction_score=4.0
        )
        
        anomalous_pattern = UserBehaviorPattern(
            user_id='test_user',
            session_count=1,
            avg_session_duration=10.0,  # Extremely short
            preferred_quality='high',
            interaction_frequency=5.0,  # Extremely high
            error_rate=0.8,  # Very high error rate
            satisfaction_score=1.0  # Very low satisfaction
        )
        
        # Train with normal pattern
        engine.update_behavior_pattern(normal_pattern)
        
        # Test anomaly detection
        normal_result = engine.detect_anomaly(normal_pattern)
        anomalous_result = engine.detect_anomaly(anomalous_pattern)
        
        self.assertIsInstance(normal_result, dict)
        self.assertIsInstance(anomalous_result, dict)
        self.assertIn('is_anomaly', normal_result)
        self.assertIn('is_anomaly', anomalous_result)


class TestFeedbackSystem(unittest.TestCase):
    """Test suite for Comprehensive Feedback System component."""
    
    def setUp(self):
        """Set up test environment."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required imports not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'session_id': 'test_session',
            'user_id': 'test_user',
            'data_dir': self.temp_dir
        }
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_feedback_system_initialization(self):
        """Test feedback system initializes correctly."""
        system = ComprehensiveFeedbackSystem(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        self.assertIsNotNone(system)
        self.assertEqual(system.session_id, self.test_config['session_id'])
        self.assertEqual(system.user_id, self.test_config['user_id'])
        self.assertIsInstance(system.sentiment_analyzer, SentimentAnalyzer)
        self.assertIsInstance(system.feedback_analyzer, FeedbackAnalyzer)
        self.assertIsInstance(system.feedback_collector, FeedbackCollector)
    
    def test_feedback_collection(self):
        """Test feedback collection functionality."""
        system = ComprehensiveFeedbackSystem(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        # Test explicit feedback
        explicit_feedback = {
            'rating': 4,
            'comment': 'Great performance, very responsive!',
            'category': 'performance'
        }
        
        result = system.collect_feedback(
            feedback_type=FeedbackType.EXPLICIT,
            data=explicit_feedback
        )
        
        self.assertTrue(result)
        
        # Test implicit feedback
        implicit_feedback = {
            'action': 'quality_adjustment',
            'value': 'increase',
            'response_time': 0.5,
            'success': True
        }
        
        result = system.collect_feedback(
            feedback_type=FeedbackType.IMPLICIT,
            data=implicit_feedback
        )
        
        self.assertTrue(result)
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis functionality."""
        system = ComprehensiveFeedbackSystem(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        # Test positive sentiment
        positive_text = "This is amazing! I love how fast and accurate it is."
        positive_result = system.analyze_sentiment(positive_text)
        
        self.assertIsInstance(positive_result, dict)
        self.assertIn('sentiment', positive_result)
        self.assertIn('confidence', positive_result)
        self.assertIn('scores', positive_result)
        
        # Test negative sentiment
        negative_text = "This is terrible, slow and full of errors."
        negative_result = system.analyze_sentiment(negative_text)
        
        self.assertIsInstance(negative_result, dict)
        self.assertIn('sentiment', negative_result)
        
        # Positive should be more positive than negative
        self.assertGreater(
            positive_result['scores'].get('positive', 0),
            negative_result['scores'].get('positive', 0)
        )
    
    def test_feedback_analysis(self):
        """Test feedback analysis and correlation."""
        system = ComprehensiveFeedbackSystem(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        # Add multiple feedback entries
        feedback_data = [
            {'rating': 5, 'comment': 'Excellent!', 'category': 'overall'},
            {'rating': 4, 'comment': 'Very good', 'category': 'performance'},
            {'rating': 3, 'comment': 'Okay', 'category': 'usability'},
            {'rating': 2, 'comment': 'Poor', 'category': 'reliability'},
            {'rating': 1, 'comment': 'Terrible', 'category': 'overall'}
        ]
        
        for feedback in feedback_data:
            system.collect_feedback(FeedbackType.EXPLICIT, feedback)
        
        # Analyze feedback trends
        analysis = system.analyze_feedback_trends()
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('overall_satisfaction', analysis)
        self.assertIn('trend_direction', analysis)
        self.assertIn('category_breakdown', analysis)


class TestPredictiveOptimizer(unittest.TestCase):
    """Test suite for Predictive Optimization Engine component."""
    
    def setUp(self):
        """Set up test environment."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required imports not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'session_id': 'test_session',
            'user_id': 'test_user',
            'data_dir': self.temp_dir
        }
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_predictive_optimizer_initialization(self):
        """Test predictive optimizer initializes correctly."""
        optimizer = PredictiveOptimizer(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        self.assertIsNotNone(optimizer)
        self.assertEqual(optimizer.session_id, self.test_config['session_id'])
        self.assertEqual(optimizer.user_id, self.test_config['user_id'])
        self.assertIsInstance(optimizer.time_series_predictor, TimeSeriesPredictor)
        self.assertIsInstance(optimizer.resource_optimizer, ResourceOptimizer)
        self.assertIsInstance(optimizer.smart_cache, SmartCache)
    
    def test_usage_pattern_prediction(self):
        """Test usage pattern prediction functionality."""
        optimizer = PredictiveOptimizer(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        # Generate mock usage data
        usage_data = []
        base_time = datetime.now()
        for i in range(24):  # 24 hours of data
            usage_data.append({
                'timestamp': base_time + timedelta(hours=i),
                'cpu_usage': 0.3 + 0.2 * np.sin(i * np.pi / 12),  # Daily pattern
                'memory_usage': 0.4 + 0.1 * np.sin(i * np.pi / 12),
                'gpu_usage': 0.5 + 0.3 * np.sin(i * np.pi / 12),
                'session_duration': 30 + 20 * np.sin(i * np.pi / 12),
                'quality_preference': 'medium'
            })
        
        # Train predictor
        for data in usage_data:
            optimizer.update_usage_pattern(data)
        
        # Make predictions
        predictions = optimizer.predict_usage_patterns(
            prediction_horizon_hours=6
        )
        
        self.assertIsInstance(predictions, dict)
        self.assertIn('resource_demand', predictions)
        self.assertIn('quality_preferences', predictions)
        self.assertIn('session_patterns', predictions)
    
    def test_resource_optimization(self):
        """Test resource optimization functionality."""
        optimizer = PredictiveOptimizer(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        # Test resource allocation optimization
        current_demand = {
            'cpu_usage': 0.7,
            'memory_usage': 0.8,
            'gpu_usage': 0.9  # High GPU usage
        }
        
        predicted_demand = {
            'cpu_usage': 0.8,
            'memory_usage': 0.9,
            'gpu_usage': 0.95  # Even higher predicted
        }
        
        optimization = optimizer.optimize_resource_allocation(
            current_demand=current_demand,
            predicted_demand=predicted_demand
        )
        
        self.assertIsInstance(optimization, dict)
        self.assertIn('recommendations', optimization)
        self.assertIn('priority_actions', optimization)
        self.assertIn('resource_adjustments', optimization)
    
    def test_smart_caching(self):
        """Test smart caching functionality."""
        optimizer = PredictiveOptimizer(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        # Test cache operations
        cache_key = "test_model_weights"
        cache_data = np.random.random((100, 100))  # Mock tensor data
        
        # Store in cache
        store_result = optimizer.smart_cache_store(cache_key, cache_data)
        self.assertTrue(store_result)
        
        # Retrieve from cache
        retrieved_data = optimizer.smart_cache_get(cache_key)
        self.assertIsNotNone(retrieved_data)
        
        # Test cache predictions
        access_patterns = [
            {'key': cache_key, 'access_time': datetime.now(), 'hit': True},
            {'key': cache_key, 'access_time': datetime.now(), 'hit': True},
            {'key': 'other_key', 'access_time': datetime.now(), 'hit': False}
        ]
        
        for pattern in access_patterns:
            optimizer.update_cache_access_pattern(pattern)
        
        prefetch_recommendations = optimizer.get_prefetch_recommendations()
        self.assertIsInstance(prefetch_recommendations, list)


class TestPhase7CIntegration(unittest.TestCase):
    """Test suite for Phase 7C Integration Module."""
    
    def setUp(self):
        """Set up test environment."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required imports not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'session_id': 'test_integration_session',
            'user_id': 'test_user',
            'data_dir': self.temp_dir
        }
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_integration_initialization(self):
        """Test Phase 7C integration initializes correctly."""
        coordinator = AdaptiveLearningCoordinator(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        self.assertIsNotNone(coordinator)
        self.assertEqual(coordinator.session_id, self.test_config['session_id'])
        self.assertEqual(coordinator.user_id, self.test_config['user_id'])
        self.assertIsInstance(coordinator.ml_adaptation, MLAdaptationEngine)
        self.assertIsInstance(coordinator.feedback_system, ComprehensiveFeedbackSystem)
        self.assertIsInstance(coordinator.predictive_optimizer, PredictiveOptimizer)
    
    @unittest.skipIf(not IMPORTS_SUCCESSFUL, "Required imports not available")
    def test_async_adaptation_session(self):
        """Test asynchronous adaptation session management."""
        async def run_test():
            coordinator = AdaptiveLearningCoordinator(
                session_id=self.test_config['session_id'],
                user_id=self.test_config['user_id'],
                data_dir=self.test_config['data_dir']
            )
            
            # Start adaptation session
            session_result = await coordinator.start_adaptation_session(
                mode=AdaptationMode.LEARNING
            )
            
            self.assertTrue(session_result)
            self.assertIsNotNone(coordinator.current_session)
            
            # Simulate user interaction
            interaction_data = {
                'action': 'quality_adjustment',
                'value': 'increase',
                'timestamp': datetime.now(),
                'success': True,
                'response_time': 0.3
            }
            
            adaptation_result = await coordinator.process_user_interaction(
                interaction_data
            )
            
            self.assertIsInstance(adaptation_result, dict)
            self.assertIn('adaptations_applied', adaptation_result)
            
            # End session
            end_result = await coordinator.end_adaptation_session()
            self.assertTrue(end_result)
        
        # Run async test
        asyncio.run(run_test())
    
    def test_cross_component_integration(self):
        """Test integration between all Phase 7C components."""
        coordinator = AdaptiveLearningCoordinator(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'],
            data_dir=self.test_config['data_dir']
        )
        
        # Test feedback → ML adaptation flow
        feedback_data = {
            'rating': 2,
            'comment': 'Too slow, needs optimization',
            'category': 'performance'
        }
        
        feedback_result = coordinator.feedback_system.collect_feedback(
            FeedbackType.EXPLICIT, feedback_data
        )
        self.assertTrue(feedback_result)
        
        # Test ML adaptation → prediction flow
        behavior_data = {
            'session_count': 5,
            'avg_session_duration': 120.0,
            'preferred_quality': 'high',
            'interaction_frequency': 0.8,
            'error_rate': 0.1,
            'satisfaction_score': 2.0  # Low satisfaction
        }
        
        # This should trigger adaptive responses
        system_state = coordinator.get_system_state()
        self.assertIsInstance(system_state, SystemState)
        self.assertIsNotNone(system_state.health_metrics)
    
    def test_emergency_adaptation_triggers(self):
        """Test emergency adaptation triggers."""
        coordinator = AdaptiveLearningCoordinator(
            session_id=self.test_config['session_id'],
            user_id=self.test_config['user_id'], 
            data_dir=self.test_config['data_dir']
        )
        
        # Simulate declining performance
        poor_feedback = [
            {'rating': 1, 'comment': 'Very slow', 'category': 'performance'},
            {'rating': 1, 'comment': 'Keeps crashing', 'category': 'reliability'},
            {'rating': 2, 'comment': 'Frustrating', 'category': 'usability'}
        ]
        
        for feedback in poor_feedback:
            coordinator.feedback_system.collect_feedback(
                FeedbackType.EXPLICIT, feedback
            )
        
        # Check if emergency adaptations are triggered
        emergency_status = coordinator.check_emergency_adaptation_triggers()
        self.assertIsInstance(emergency_status, dict)
        self.assertIn('emergency_triggered', emergency_status)
        self.assertIn('trigger_reasons', emergency_status)


class TestPerformanceAndMemory(unittest.TestCase):
    """Test suite for performance and memory optimization validation."""
    
    def setUp(self):
        """Set up performance test environment.""" 
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required imports not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.performance_config = {
            'session_id': 'perf_test_session',
            'user_id': 'perf_test_user',
            'data_dir': self.temp_dir,
            'max_memory_mb': 512,  # GTX 1050 Ti constraint
            'max_response_time_ms': 1000
        }
    
    def tearDown(self):
        """Clean up performance test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_memory_usage_constraints(self):
        """Test that Phase 7C components stay within memory constraints."""
        import psutil
        import gc
        
        # Start memory measurement
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Initialize all components
        coordinator = AdaptiveLearningCoordinator(
            session_id=self.performance_config['session_id'],
            user_id=self.performance_config['user_id'],
            data_dir=self.performance_config['data_dir']
        )
        
        # Measure memory after initialization
        post_init_memory = process.memory_info().rss / 1024 / 1024  # MB
        init_overhead = post_init_memory - initial_memory
        
        # Run intensive operations
        for i in range(10):
            # Heavy feedback processing
            coordinator.feedback_system.collect_feedback(
                FeedbackType.EXPLICIT,
                {'rating': i % 5 + 1, 'comment': f'Test comment {i}', 'category': 'test'}
            )
            
            # ML adaptation with behavior patterns
            behavior = UserBehaviorPattern(
                user_id='test_user',
                session_count=i + 1,
                avg_session_duration=float(100 + i * 10),
                preferred_quality='medium',
                interaction_frequency=0.5 + i * 0.05,
                error_rate=0.01 + i * 0.001,
                satisfaction_score=3.0 + i * 0.2
            )
            coordinator.ml_adaptation.analyze_behavior_pattern(behavior)
            
            # Predictive optimization
            usage_data = {
                'timestamp': datetime.now(),
                'cpu_usage': 0.3 + i * 0.05,
                'memory_usage': 0.4 + i * 0.03,
                'gpu_usage': 0.5 + i * 0.04,
                'session_duration': 30 + i * 5,
                'quality_preference': 'medium'
            }
            coordinator.predictive_optimizer.update_usage_pattern(usage_data)
        
        # Force garbage collection
        gc.collect()
        
        # Final memory measurement
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_overhead = final_memory - initial_memory
        
        print(f"Memory usage - Initial: {initial_memory:.1f}MB, "
              f"Post-init: {post_init_memory:.1f}MB, Final: {final_memory:.1f}MB")
        print(f"Init overhead: {init_overhead:.1f}MB, Total overhead: {total_overhead:.1f}MB")
        
        # Assert memory constraints
        self.assertLess(
            total_overhead, 
            self.performance_config['max_memory_mb'],
            f"Memory usage {total_overhead:.1f}MB exceeds limit {self.performance_config['max_memory_mb']}MB"
        )
    
    def test_response_time_performance(self):
        """Test response time performance for Phase 7C operations."""
        coordinator = AdaptiveLearningCoordinator(
            session_id=self.performance_config['session_id'],
            user_id=self.performance_config['user_id'],
            data_dir=self.performance_config['data_dir']
        )
        
        # Test feedback collection performance
        start_time = time.time()
        feedback_result = coordinator.feedback_system.collect_feedback(
            FeedbackType.EXPLICIT,
            {'rating': 4, 'comment': 'Performance test', 'category': 'test'}
        )
        feedback_time = (time.time() - start_time) * 1000  # ms
        
        # Test ML adaptation performance
        start_time = time.time()
        behavior = UserBehaviorPattern(
            user_id='test_user',
            session_count=5,
            avg_session_duration=200.0,
            preferred_quality='medium',
            interaction_frequency=0.6,
            error_rate=0.05,
            satisfaction_score=3.8
        )
        adaptation_result = coordinator.ml_adaptation.analyze_behavior_pattern(behavior)
        adaptation_time = (time.time() - start_time) * 1000  # ms
        
        # Test predictive optimization performance
        start_time = time.time()
        usage_data = {
            'timestamp': datetime.now(),
            'cpu_usage': 0.4,
            'memory_usage': 0.5,
            'gpu_usage': 0.6,
            'session_duration': 45,
            'quality_preference': 'medium'
        }
        coordinator.predictive_optimizer.update_usage_pattern(usage_data)
        prediction_time = (time.time() - start_time) * 1000  # ms
        
        max_time = self.performance_config['max_response_time_ms']
        
        # Assert performance constraints
        self.assertLess(feedback_time, max_time, 
                       f"Feedback processing {feedback_time:.1f}ms exceeds {max_time}ms")
        self.assertLess(adaptation_time, max_time,
                       f"ML adaptation {adaptation_time:.1f}ms exceeds {max_time}ms") 
        self.assertLess(prediction_time, max_time,
                       f"Prediction {prediction_time:.1f}ms exceeds {max_time}ms")
        
        print(f"Performance - Feedback: {feedback_time:.1f}ms, "
              f"Adaptation: {adaptation_time:.1f}ms, Prediction: {prediction_time:.1f}ms")


def run_comprehensive_tests():
    """Run all Phase 7C tests with detailed reporting."""
    print("="*80)
    print("ImpressionCore Phase 7C - Comprehensive Test Suite")
    print("="*80)
    print(f"Test execution started at: {datetime.now()}")
    print(f"Imports successful: {IMPORTS_SUCCESSFUL}")
    print()
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ Cannot run tests - required imports failed")
        return False
    
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestMLAdaptationEngine,
        TestFeedbackSystem, 
        TestPredictiveOptimizer,
        TestPhase7CIntegration,
        TestPerformanceAndMemory
    ]
    
    for test_class in test_classes:
        tests = test_loader.loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    print("Running Phase 7C comprehensive tests...")
    print("-" * 80)
    
    result = runner.run(test_suite)
    
    print("\n" + "="*80)
    print("PHASE 7C TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    print(f"\n🎯 Phase 7C Testing Status: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"Test execution completed at: {datetime.now()}")
    print("="*80)
    
    return success


if __name__ == '__main__':
    run_comprehensive_tests()
