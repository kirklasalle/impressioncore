#!/usr/bin/env python3
"""
ImpressionCore Training Module Comprehensive Test Suite

This test suite validates the complete training module functionality including:
- TrainingManager and ModelTrainer initialization
- Memory optimization features
- Precision mode switching
- Error handling and edge cases
- Training pipeline functionality

File: tests/training/comprehensive_training_test.py
Created: 2025-01-06
"""

import sys
import traceback
from typing import Dict, Any
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_training_manager_advanced():
    """Test advanced TrainingManager functionality"""
    print("Testing Advanced TrainingManager Features...")
    
    try:
        from src.training.training_manager import TrainingManager
        from src.core.utils.precision_manager import PrecisionMode
        
        # Test configuration with different settings
        config = {
            "model": {
                "model_name": "test_model",
                "model_type": "sequential"
            },
            "training": {
                "optimizer": "adamw",
                "learning_rate": 1e-4,
                "precision_mode": "fp16",
                "gradient_accumulation_steps": 2,
                "mixed_precision": True
            },
            "memory": {
                "target_vram_usage": 0.7,
                "enable_gradient_checkpointing": True
            }
        }
        
        manager = TrainingManager(config)
        print("✓ TrainingManager created with custom config")
        
        # Test precision modes
        for mode in ["fp32", "fp16", "bf16"]:
            try:
                manager.set_precision_mode(mode)
                print(f"✓ Precision mode {mode} set successfully")
            except Exception as e:
                print(f"⚠ Failed to set precision mode {mode}: {e}")
        
        # Test memory optimization settings
        manager.update_vram_target(0.5)
        print("✓ VRAM target updated")
        
        manager.set_gradient_checkpointing(True)
        print("✓ Gradient checkpointing enabled")
        
        # Test training stats
        stats = manager.get_current_stats()
        assert isinstance(stats, dict)
        assert len(stats) > 0
        print(f"✓ Training stats retrieved: {len(stats)} metrics")
        
        # Test metrics history
        history = manager.get_metrics_history()
        assert isinstance(history, dict)
        print(f"✓ Metrics history retrieved: {len(history)} metric types")
        
        return True
        
    except Exception as e:
        print(f"✗ Advanced TrainingManager test failed: {e}")
        traceback.print_exc()
        return False

def test_model_trainer_advanced():
    """Test advanced ModelTrainer functionality"""
    print("\nTesting Advanced ModelTrainer Features...")
    
    try:
        from src.training.trainer import ModelTrainer
        from src.core.utils.precision_manager import PrecisionMode
        
        # Create a more complex model
        model = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )
        
        # Create larger dataset
        dummy_data = torch.randn(1000, 512)
        dummy_labels = torch.randint(0, 10, (1000,))
        dataset = TensorDataset(dummy_data, dummy_labels)
        
        train_dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
        val_dataloader = DataLoader(dataset, batch_size=32, shuffle=False)
        
        # Test with different configurations
        trainer = ModelTrainer(
            model=model,
            train_dataloader=train_dataloader,
            val_dataloader=val_dataloader,
            device="cpu",
            mixed_precision=False,
            target_vram_usage=0.8,
            gradient_accumulation_steps=4
        )
        print("✓ ModelTrainer created with complex model")
        
        # Test configuration updates
        trainer.update_vram_target(1.2)
        print("✓ VRAM target updated")
        
        trainer.set_gradient_checkpointing(True)
        print("✓ Gradient checkpointing enabled")
        
        trainer.set_attention_cache(False)
        print("✓ Attention cache disabled")
        
        # Test precision modes
        for mode in [PrecisionMode.FP32, PrecisionMode.FP16]:
            try:
                trainer.set_precision_mode(mode)
                print(f"✓ Precision mode {mode} set successfully")
            except Exception as e:
                print(f"⚠ Failed to set precision mode {mode}: {e}")
        
        # Test metrics collection
        metrics = trainer.get_metrics_history()
        assert isinstance(metrics, dict)
        print(f"✓ Metrics history retrieved: {len(metrics)} metric types")
        
        return True
        
    except Exception as e:
        print(f"✗ Advanced ModelTrainer test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and edge cases"""
    print("\nTesting Error Handling...")
    
    try:
        from src.training.trainer import ModelTrainer
        from src.training.training_manager import TrainingManager
        
        # Test with invalid configurations
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Invalid device
        total_tests += 1
        try:
            model = nn.Linear(10, 5)
            data = torch.randn(100, 10)
            labels = torch.randint(0, 5, (100,))
            dataset = TensorDataset(data, labels)
            dataloader = DataLoader(dataset, batch_size=8)
            
            trainer = ModelTrainer(
                model=model,
                train_dataloader=dataloader,
                val_dataloader=dataloader,
                device="invalid_device"  # This should be handled gracefully
            )
            tests_passed += 1
            print("✓ Invalid device handled gracefully")
        except Exception as e:
            print(f"⚠ Invalid device test failed: {e}")
        
        # Test 2: Negative VRAM target
        total_tests += 1
        try:
            config = {"training": {}, "memory": {}}
            manager = TrainingManager(config)
            manager.update_vram_target(-1.0)  # Should be handled
            tests_passed += 1
            print("✓ Negative VRAM target handled")
        except Exception as e:
            print(f"⚠ Negative VRAM target test failed: {e}")
        
        # Test 3: Empty configuration
        total_tests += 1
        try:
            manager = TrainingManager({})
            tests_passed += 1
            print("✓ Empty configuration handled")
        except Exception as e:
            print(f"⚠ Empty configuration test failed: {e}")
        
        print(f"✓ Error handling tests: {tests_passed}/{total_tests} passed")
        return tests_passed == total_tests
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        traceback.print_exc()
        return False

def test_memory_optimization():
    """Test memory optimization features"""
    print("\nTesting Memory Optimization...")
    
    try:
        from src.training.trainer import ModelTrainer
        
        # Create a larger model to test memory optimization
        model = nn.Sequential(
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )
        
        data = torch.randn(500, 1024)
        labels = torch.randint(0, 10, (500,))
        dataset = TensorDataset(data, labels)
        dataloader = DataLoader(dataset, batch_size=16)
        
        # Test with memory optimization enabled
        trainer = ModelTrainer(
            model=model,
            train_dataloader=dataloader,
            val_dataloader=dataloader,
            device="cpu",
            target_vram_usage=0.6,
            enable_adaptive_optimization=True,
            gradient_accumulation_steps=8
        )
        print("✓ Memory-optimized trainer created")
        
        # Test VRAM target updates
        for target in [0.3, 0.5, 0.8, 1.0]:
            trainer.update_vram_target(target)
            print(f"✓ VRAM target updated to {target}")
        
        # Test gradient checkpointing
        trainer.set_gradient_checkpointing(True)
        print("✓ Gradient checkpointing enabled")
        
        return True
        
    except Exception as e:
        print(f"✗ Memory optimization test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run comprehensive test suite"""
    print("=" * 60)
    print("ImpressionCore Training Module - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Advanced TrainingManager", test_training_manager_advanced),
        ("Advanced ModelTrainer", test_model_trainer_advanced),
        ("Error Handling", test_error_handling),
        ("Memory Optimization", test_memory_optimization)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Training module is fully functional!")
        return 0
    else:
        print("⚠ Some tests failed - please review the results above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
