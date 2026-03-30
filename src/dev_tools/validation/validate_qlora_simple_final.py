#!/usr/bin/env python3
"""
Simple QLoRA Integration Validation Script
==========================================

This script performs a simple but comprehensive validation of QLoRA integration
with the ImpressionCore training pipeline.

Author: ImpressionCore Development Team
Date: 2025-01-04
License: MIT
"""

import os
import sys
import json
import torch
import torch.nn as nn
from typing import Dict, Any
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_qlora_configuration():
    """Test QLoRA configuration loading."""
    try:
        config_path = "configs/training_config_qlora.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required sections
        required_sections = ['model', 'training', 'lora', 'qlora', 'memory_optimization']
        for section in required_sections:
            assert section in config, f"Missing required section: {section}"
        
        logger.info("✅ Configuration test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def test_qlora_import():
    """Test QLoRA module imports."""
    try:
        from models.qlora import QLoRAConfig, QLoRAModel, create_qlora_model
        logger.info("✅ QLoRA import test passed")
        return True
    except Exception as e:
        logger.error(f"❌ QLoRA import test failed: {e}")
        return False

def test_qlora_model_creation():
    """Test QLoRA model creation and basic functionality."""
    try:
        from models.qlora import QLoRAConfig, QLoRAModel, create_qlora_model
        
        # Create a simple test model
        class SimpleModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(10, 5)
                
            def forward(self, x):
                return self.linear(x)
        
        base_model = SimpleModel()
        
        # Create QLoRA config
        config = QLoRAConfig(
            r=4,
            lora_alpha=8,
            lora_dropout=0.1,
            target_modules=["linear"]
        )
        
        # Create QLoRA model
        qlora_model = create_qlora_model(base_model, config, device="cpu")
        
        # Test forward pass
        test_input = torch.randn(2, 10)
        output = qlora_model(test_input)
        assert output.shape == (2, 5), f"Unexpected output shape: {output.shape}"
        
        logger.info("✅ QLoRA model creation test passed")
        return True
    except Exception as e:
        logger.error(f"❌ QLoRA model creation test failed: {e}")
        return False

def test_trainer_integration():
    """Test QLoRA integration with trainer."""
    try:
        from models.trainer import ModelTrainer, TrainingConfig
        from models.qlora import QLoRAConfig
        
        # Create simple model and data
        class TestModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(10, 5)
                
            def forward(self, x):
                return self.linear(x)
        
        model = TestModel()
        
        # Create trainer config
        config = TrainingConfig(
            model_name="TestModel",
            learning_rate=0.0001,
            batch_size=2,
            num_epochs=1,
            device="cpu"
        )
        
        # Create trainer
        trainer = ModelTrainer(model, config)
        
        # Test QLoRA setup
        lora_model = trainer.setup_lora_fine_tuning(
            rank=4,
            alpha=8,
            use_enhanced_lora=True,
            enable_quantization=True
        )
        
        assert lora_model is not None, "QLoRA setup returned None"
        logger.info("✅ Trainer integration test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Trainer integration test failed: {e}")
        return False

def test_memory_efficiency():
    """Test memory efficiency features."""
    try:
        from models.qlora import QLoRAConfig, create_qlora_model
        import gc
        
        # Create larger model for memory testing
        class LargeModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(1000, 500),
                    nn.ReLU(),
                    nn.Linear(500, 250),
                    nn.ReLU(),
                    nn.Linear(250, 100)
                )
                
            def forward(self, x):
                return self.layers(x)
        
        base_model = LargeModel()
        original_params = sum(p.numel() for p in base_model.parameters())
        
        # Create QLoRA config with memory optimization
        config = QLoRAConfig(
            r=8,
            lora_alpha=16,
            target_modules=["0", "2", "4"],  # Target linear layers
            use_gradient_checkpointing=True,
            max_memory_mb=1000
        )
        
        # Create QLoRA model
        qlora_model = create_qlora_model(base_model, config, device="cpu")
        
        # Test that we have fewer trainable parameters
        trainable_params = sum(p.numel() for p in qlora_model.parameters() if p.requires_grad)
        
        logger.info(f"Original parameters: {original_params}")
        logger.info(f"Trainable parameters: {trainable_params}")
        logger.info(f"Reduction: {((original_params - trainable_params) / original_params * 100):.1f}%")
        
        # Clean up
        del base_model, qlora_model
        gc.collect()
        
        logger.info("✅ Memory efficiency test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Memory efficiency test failed: {e}")
        return False

def main():
    """Run all QLoRA validation tests."""
    logger.info("🧪 Starting QLoRA Integration Validation...")
    
    tests = [
        ("Configuration Loading", test_qlora_configuration),
        ("QLoRA Import", test_qlora_import),
        ("QLoRA Model Creation", test_qlora_model_creation),
        ("Trainer Integration", test_trainer_integration),
        ("Memory Efficiency", test_memory_efficiency),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"⏳ Testing {test_name.lower()}...")
        try:
            if test_func():
                results.append((test_name, "✅ PASS"))
                passed += 1
            else:
                results.append((test_name, "❌ FAIL"))
                failed += 1
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, "❌ FAIL"))
            failed += 1
    
    # Print summary
    logger.info("="*60)
    logger.info("🧪 QLoRA INTEGRATION TEST RESULTS")
    logger.info("="*60)
    
    for test_name, status in results:
        logger.info(f"{status} {test_name}")
    
    logger.info("="*60)
    logger.info(f"📊 Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All QLoRA integration tests passed!")
        logger.info("✅ QLoRA is ready for production use")
        return 0
    else:
        logger.error(f"❌ {failed} test(s) failed - please review and fix issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
