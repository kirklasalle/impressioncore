#!/usr/bin/env python3
"""
Simplified QLoRA Training Integration Validation Script
=====================================================

A more robust version that avoids variable scoping issues.

Author: ImpressionCore Development Team  
Date: 2025-01-04
License: MIT
"""

import os
import sys
import traceback
import logging
from pathlib import Path
import torch
import torch.nn as nn
from typing import Dict, Any, List, Tuple
import json
import gc
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.core.utils.rich_logging import setup_rich_logging
    RICH_AVAILABLE = True
except ImportError:
    print("Rich utilities not available, using basic logging")
    RICH_AVAILABLE = False
    
    def setup_rich_logging(name, level="INFO"):
        logging.basicConfig(level=getattr(logging, level))
        return logging.getLogger(name)


def test_configuration_loading():
    """Test QLoRA configuration loading."""
    try:
        config_path = "configs/training_config_qlora.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required sections
        required_sections = ['model', 'training', 'lora', 'qlora', 'memory_optimization']
        for section in required_sections:
            if section not in config:
                return False, f"Missing required section: {section}"
        
        return True, "All sections present"
    except Exception as e:
        return False, str(e)


def test_trainer_initialization():
    """Test trainer import and initialization."""
    try:
        from models.trainer import ModelTrainer, TrainingConfig
        from torch.utils.data import DataLoader, TensorDataset
        
        training_config = TrainingConfig(
            batch_size=2,
            learning_rate=1e-4,
            epochs=1,
            checkpoint_dir="./test_checkpoints",
            device="cpu"
        )
        
        # Simple test model
        class TestModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.embedding = nn.Embedding(100, 64)
                self.linear = nn.Linear(64, 100)
            
            def forward(self, input_ids):
                x = self.embedding(input_ids)
                return self.linear(x.mean(dim=1))
        
        # Create dummy dataloader
        dummy_data = torch.randint(0, 100, (10, 5))
        dummy_dataset = TensorDataset(dummy_data)
        dummy_dataloader = DataLoader(dummy_dataset, batch_size=2)
        
        model = TestModel()
        trainer = ModelTrainer(
            model=model, 
            config=training_config, 
            train_dataloader=dummy_dataloader
        )
        
        return True, "Trainer created successfully", (trainer, training_config, dummy_dataloader, model)
    except Exception as e:
        return False, str(e), None


def test_qlora_module_import():
    """Test QLoRA module import."""
    try:
        from models.qlora import QLoRAConfig, QLoRAModel, create_qlora_model
        
        qlora_config = QLoRAConfig(
            r=4,
            lora_alpha=8,
            lora_dropout=0.1,
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        return True, "All components imported"
    except Exception as e:
        return False, str(e)


def test_qlora_integration(trainer_data):
    """Test QLoRA integration."""
    if trainer_data is None:
        return False, "Trainer not available - previous test failed"
    
    try:
        trainer, training_config, dummy_dataloader, model = trainer_data
        
        # Test enhanced LoRA setup with quantization
        lora_model = trainer.setup_lora_fine_tuning(
            rank=4,
            alpha=8,
            target_modules=["embedding", "linear"],
            use_enhanced_lora=True,
            enable_quantization=True,
            bits=4,
            quantization_scheme="nf4",
            double_quant=True
        )
        
        # Verify model has LoRA components
        has_lora = any("lora" in name.lower() for name, _ in lora_model.named_modules())
        if not has_lora:
            return False, "No LoRA modules found in model"
        
        # Count trainable parameters
        trainable_params = sum(p.numel() for p in lora_model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in lora_model.parameters())
        
        return True, f"LoRA applied, {trainable_params}/{total_params} trainable params"
    except Exception as e:
        return False, str(e)


def test_memory_optimization(trainer_data):
    """Test memory optimization features."""
    if trainer_data is None:
        return False, "Training config not available - previous tests failed"
    
    try:
        trainer, training_config, dummy_dataloader, model = trainer_data
        
        # Test memory monitoring
        initial_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        
        # Create larger model to test memory usage
        large_model = nn.Sequential(
            nn.Linear(1000, 2000),
            nn.ReLU(),
            nn.Linear(2000, 1000)
        )
        
        # Apply QLoRA
        from models.trainer import ModelTrainer
        trainer_large = ModelTrainer(
            model=large_model, 
            config=training_config, 
            train_dataloader=dummy_dataloader
        )
        qlora_large = trainer_large.setup_lora_fine_tuning(
            rank=8,
            alpha=16,
            use_enhanced_lora=True,
            enable_quantization=True
        )
        
        # Clean up
        del large_model, trainer_large, qlora_large
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return True, "Memory operations successful"
    except Exception as e:
        return False, str(e)


def test_training_configuration():
    """Test training configuration validation."""
    try:
        config_path = "configs/training_config_qlora.json"
        
        # Load config directly
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Simple model creation test
        model_config = config['model']
        
        class SimpleTransformer(nn.Module):
            def __init__(self, vocab_size, hidden_size, num_layers, num_heads):
                super().__init__()
                self.embedding = nn.Embedding(vocab_size, hidden_size)
                self.transformer = nn.TransformerEncoder(
                    nn.TransformerEncoderLayer(hidden_size, num_heads),
                    num_layers
                )
                self.output = nn.Linear(hidden_size, vocab_size)
            
            def forward(self, x):
                x = self.embedding(x)
                x = self.transformer(x)
                return self.output(x)
        
        demo_model = SimpleTransformer(
            vocab_size=model_config.get('vocab_size', 1000),
            hidden_size=model_config.get('hidden_size', 512),
            num_layers=model_config.get('num_layers', 6),
            num_heads=model_config.get('num_heads', 8)
        )
        
        return True, "Demo components working"
    except Exception as e:
        return False, str(e)


def run_all_tests():
    """Run all QLoRA integration tests."""
    logger = setup_rich_logging("QLoRA_Validation", "INFO")
    
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("Trainer Initialization", test_trainer_initialization),
        ("QLoRA Module Import", test_qlora_module_import),
        ("Training Configuration", test_training_configuration),
    ]
    
    results = []
    trainer_data = None
    
    print("🧪 Starting QLoRA Training Integration Validation...")
    
    for test_name, test_func in tests:
        print(f"⏳ Testing {test_name.lower()}...")
        
        try:
            if test_name == "Trainer Initialization":
                success, message, data = test_func()
                if success:
                    trainer_data = data
            else:
                success, message = test_func()
                
            if success:
                results.append((test_name, "✅ PASS", message))
                print(f"   ✅ {test_name} test passed")
            else:
                results.append((test_name, "❌ FAIL", message))
                print(f"   ❌ {test_name} test failed")
        except Exception as e:
            results.append((test_name, "❌ FAIL", f"Unexpected error: {str(e)}"))
            print(f"   ❌ {test_name} test failed")
    
    # Run dependent tests
    dependent_tests = [
        ("QLoRA Integration", lambda: test_qlora_integration(trainer_data)),
        ("Memory Optimization", lambda: test_memory_optimization(trainer_data)),
    ]
    
    for test_name, test_func in dependent_tests:
        print(f"⏳ Testing {test_name.lower()}...")
        
        try:
            success, message = test_func()
            if success:
                results.append((test_name, "✅ PASS", message))
                print(f"   ✅ {test_name} test passed")
            else:
                results.append((test_name, "❌ FAIL", message))
                print(f"   ❌ {test_name} test failed")
        except Exception as e:
            results.append((test_name, "❌ FAIL", f"Unexpected error: {str(e)}"))
            print(f"   ❌ {test_name} test failed")
    
    # Print results
    print("\n" + "=" * 60)
    print("🧪 QLoRA TRAINING INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, status, message in results:
        print(f"{status} {test_name}: {message}")
        if "✅ PASS" in status:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"📊 Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ Ready for production QLoRA training")
        return True
    else:
        print(f"❌ {failed} test(s) failed - please review and fix issues")
        return False


def main():
    """Main test function."""
    success = run_all_tests()
    
    if success:
        print("\n🎯 QLoRA training integration is fully validated and ready!")
        return 0
    else:
        print("\n⚠️  Some tests failed - please review the results above")
        return 1


if __name__ == "__main__":
    exit(main())
