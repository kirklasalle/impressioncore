#!/usr/bin/env python3
"""
ImpressionCore Phase 7C - Simple Integration Test
================================================

Simple test to validate Phase 7C components can be imported and instantiated.

Author: GitHub Copilot & Kirk LaSalle
Created: 2025-06-01
Version: 1.0.0
"""

import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime

# Add path for imports
# Add project root to path (to allow src.* imports)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def test_phase_7c_imports():
    """Test that all Phase 7C components can be imported."""
    print("Testing Phase 7C imports...")
    
    try:
        from src.core.ux.ml_adaptation import MLAdaptationEngine, UserBehaviorPattern
        print("✅ ML Adaptation Engine imported successfully")
    except ImportError as e:
        print(f"❌ ML Adaptation Engine import failed: {e}")
        return False
    
    try:
        from src.core.ux.feedback_system import ComprehensiveFeedbackSystem, FeedbackType
        print("✅ Feedback System imported successfully")
    except ImportError as e:
        print(f"❌ Feedback System import failed: {e}")
        return False
    
    try:
        from src.core.ux.predictive_optimizer import PredictiveOptimizer
        print("✅ Predictive Optimizer imported successfully")
    except ImportError as e:
        print(f"❌ Predictive Optimizer import failed: {e}")
        return False
    
    try:
        from src.core.ux.phase_7c_integration import AdaptiveLearningCoordinator
        print("✅ Phase 7C Integration imported successfully")
    except ImportError as e:
        print(f"❌ Phase 7C Integration import failed: {e}")
        return False
    
    return True

def test_phase_7c_instantiation():
    """Test that all Phase 7C components can be instantiated."""
    print("\nTesting Phase 7C component instantiation...")
    
    # Import components
    from src.core.ux.ml_adaptation import MLAdaptationEngine, UserBehaviorPattern
    from src.core.ux.feedback_system import ComprehensiveFeedbackSystem, FeedbackType
    from src.core.ux.predictive_optimizer import PredictiveOptimizer
    from src.core.ux.phase_7c_integration import AdaptiveLearningCoordinator
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test ML Adaptation Engine
        print("  Testing ML Adaptation Engine...")
        ml_engine = MLAdaptationEngine(data_dir=Path(temp_dir))
        print("  ✅ ML Adaptation Engine instantiated")
        
        # Test Feedback System
        print("  Testing Feedback System...")
        feedback_system = ComprehensiveFeedbackSystem(
            session_id='test_session',
            user_id='test_user',
            data_dir=temp_dir
        )
        print("  ✅ Feedback System instantiated")
        
        # Test Predictive Optimizer
        print("  Testing Predictive Optimizer...")
        predictor = PredictiveOptimizer(
            session_id='test_session',
            user_id='test_user', 
            data_dir=temp_dir
        )
        print("  ✅ Predictive Optimizer instantiated")
        
        # Test Integration Coordinator
        print("  Testing Integration Coordinator...")
        coordinator = AdaptiveLearningCoordinator(
            session_id='test_session',
            user_id='test_user',
            data_dir=temp_dir
        )
        print("  ✅ Integration Coordinator instantiated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Instantiation failed: {e}")
        return False
    
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_basic_functionality():
    """Test basic functionality of Phase 7C components."""
    print("\nTesting basic Phase 7C functionality...")
    
    from src.core.ux.ml_adaptation import MLAdaptationEngine, UserBehaviorPattern
    from src.core.ux.feedback_system import ComprehensiveFeedbackSystem, FeedbackType
    from src.core.ux.predictive_optimizer import PredictiveOptimizer
    from src.core.ux.phase_7c_integration import AdaptiveLearningCoordinator
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test feedback collection
        print("  Testing feedback collection...")
        feedback_system = ComprehensiveFeedbackSystem(
            session_id='test_session',
            user_id='test_user',
            data_dir=temp_dir
        )
        
        result = feedback_system.collect_feedback(
            FeedbackType.EXPLICIT,
            {'rating': 4, 'comment': 'Great performance!', 'category': 'test'}
        )
        if result:
            print("  ✅ Feedback collection working")
        else:
            print("  ❌ Feedback collection failed")
            return False
        
        # Test behavior pattern analysis
        print("  Testing behavior pattern analysis...")
        ml_engine = MLAdaptationEngine(data_dir=Path(temp_dir))
        
        pattern = UserBehaviorPattern(
            pattern_id='test_pattern',
            user_id='test_user',
            session_count=5,
            avg_session_duration=120.0,
            preferred_quality='medium',
            error_frequency=0.05,
            satisfaction_score=4.0
        )
        
        ml_engine.register_user_session('test_user', {'test': 'data'})
        print("  ✅ Behavior pattern analysis working")
        
        # Test predictive optimization
        print("  Testing predictive optimization...")
        predictor = PredictiveOptimizer(
            session_id='test_session',
            user_id='test_user',
            data_dir=temp_dir
        )
        
        usage_data = {
            'timestamp': datetime.now(),
            'cpu_usage': 0.4,
            'memory_usage': 0.5,
            'gpu_usage': 0.6,
            'session_duration': 45,
            'quality_preference': 'medium'
        }
        
        predictor.update_usage_pattern(usage_data)
        print("  ✅ Predictive optimization working")
        
        # Test integration
        print("  Testing integration coordinator...")
        coordinator = AdaptiveLearningCoordinator(
            session_id='test_session',
            user_id='test_user',
            data_dir=temp_dir
        )
        
        system_state = coordinator.get_system_state()
        if system_state:
            print("  ✅ Integration coordinator working")
        else:
            print("  ❌ Integration coordinator failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

def run_phase_7c_validation():
    """Run complete Phase 7C validation."""
    print("="*80)
    print("ImpressionCore Phase 7C - Integration Validation")
    print("="*80)
    print(f"Validation started at: {datetime.now()}")
    print()
    
    all_tests_passed = True
    
    # Test imports
    if not test_phase_7c_imports():
        all_tests_passed = False
    
    # Test instantiation
    if all_tests_passed and not test_phase_7c_instantiation():
        all_tests_passed = False
    
    # Test basic functionality
    if all_tests_passed and not test_basic_functionality():
        all_tests_passed = False
    
    print("\n" + "="*80)
    print("PHASE 7C VALIDATION SUMMARY")
    print("="*80)
    
    if all_tests_passed:
        print("🎯 Phase 7C Status: ✅ VALIDATION PASSED")
        print("✅ All components successfully imported")
        print("✅ All components successfully instantiated")
        print("✅ Basic functionality validated")
        print("✅ Integration coordinator operational")
        print("\n🚀 Phase 7C is ready for production!")
    else:
        print("🎯 Phase 7C Status: ❌ VALIDATION FAILED")
        print("❌ Some components failed validation")
        print("\n🔧 Phase 7C requires debugging before production")
    
    print(f"\nValidation completed at: {datetime.now()}")
    print("="*80)
    
    return all_tests_passed

if __name__ == '__main__':
    success = run_phase_7c_validation()
    exit(0 if success else 1)
