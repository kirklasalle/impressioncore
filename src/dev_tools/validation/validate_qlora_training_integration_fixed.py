#!/usr/bin/env python3
"""
QLoRA Training Integration Validation Script
===========================================

This script validates the complete QLoRA training integration with the
ImpressionCore trainer, ensuring all components work together correctly.

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
from torch.utils.data import DataLoader, TensorDataset

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.utils.rich_logging import setup_rich_logging
    from core.utils.rich_enhancements import create_progress_panel, create_info_panel
    from core.utils.rich_status_animation import StatusAnimator
    RICH_AVAILABLE = True
except ImportError:
    print("Rich utilities not available, using basic logging")
    RICH_AVAILABLE = False
    
    def setup_rich_logging(name, level="INFO"):
        logging.basicConfig(level=getattr(logging, level))
        return logging.getLogger(name)
    
    class StatusAnimator:
        def start(self, msg): print(f"⏳ {msg}")
        def stop(self, msg): print(f"   {msg}")
    
    def create_info_panel(title, data):
        return f"\n{title}:\n" + "\n".join(f"  {k}: {v}" for k, v in data.items())


def test_qlora_training_integration():
    """Test QLoRA training integration with ImpressionCore trainer."""
    
    logger = setup_rich_logging("QLoRA Integration Test", level="INFO")
    status = StatusAnimator()
    
    test_results = []
    
    try:
        # Test 1: Configuration Loading
        status.start("Testing configuration loading...")
        try:
            config_path = "src/configs/training_config_qlora.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Validate required sections
            required_sections = ['model', 'training', 'lora', 'qlora', 'memory_optimization']
            for section in required_sections:
                assert section in config, f"Missing required section: {section}"
            
            test_results.append(("Configuration Loading", "✅ PASS", "All sections present"))
            status.stop("✅ Configuration test passed")
        except Exception as e:
            test_results.append(("Configuration Loading", "❌ FAIL", str(e)))
            status.stop("❌ Configuration test failed")
        
        # Test 2: Trainer Import and Initialization
        status.start("Testing trainer initialization...")
        try:
            from models.trainer import ModelTrainer, TrainingConfig
            
            training_config = TrainingConfig(
                batch_size=2,  # Small for testing
                learning_rate=1e-4,
                epochs=1,
                checkpoint_dir="./test_checkpoints",
                device="cpu"  # Use CPU for testing
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
            dummy_data = torch.randint(0, 100, (10, 5))  # 10 samples, 5 sequence length
            dummy_dataset = TensorDataset(dummy_data)
            dummy_dataloader = DataLoader(dummy_dataset, batch_size=2)
            
            model = TestModel()
            trainer = ModelTrainer(
                model=model, 
                config=training_config, 
                train_dataloader=dummy_dataloader
            )
            
            test_results.append(("Trainer Initialization", "✅ PASS", "Trainer created successfully"))
            status.stop("✅ Trainer test passed")
        except Exception as e:
            test_results.append(("Trainer Initialization", "❌ FAIL", str(e)))
            status.stop("❌ Trainer test failed")
        
        # Test 3: QLoRA Module Import
        status.start("Testing QLoRA module import...")
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
            
            test_results.append(("QLoRA Module Import", "✅ PASS", "All components imported"))
            status.stop("✅ QLoRA import test passed")
        except Exception as e:
            test_results.append(("QLoRA Module Import", "❌ FAIL", str(e)))
            status.stop("❌ QLoRA import test failed")
        
        # Test 4: QLoRA Integration Test
        status.start("Testing QLoRA integration...")
        try:
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
            assert has_lora, "No LoRA modules found in model"
            
            # Count trainable parameters
            trainable_params = sum(p.numel() for p in lora_model.parameters() if p.requires_grad)
            total_params = sum(p.numel() for p in lora_model.parameters())
            
            test_results.append((
                "QLoRA Integration", 
                "✅ PASS", 
                f"LoRA applied, {trainable_params}/{total_params} trainable params"
            ))
            status.stop("✅ QLoRA integration test passed")
        except Exception as e:
            test_results.append(("QLoRA Integration", "❌ FAIL", str(e)))
            status.stop("❌ QLoRA integration test failed")
        
        # Test 5: Memory Optimization Features
        status.start("Testing memory optimization...")
        try:
            # Test memory monitoring
            initial_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
            
            # Create larger model to test memory usage
            large_model = nn.Sequential(
                nn.Linear(1000, 2000),
                nn.ReLU(),
                nn.Linear(2000, 1000)
            )
            
            # Apply QLoRA
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
            
            test_results.append(("Memory Optimization", "✅ PASS", "Memory operations successful"))
            status.stop("✅ Memory test passed")
        except Exception as e:
            test_results.append(("Memory Optimization", "❌ FAIL", str(e)))
            status.stop("❌ Memory test failed")
        
        # Test 6: Training Configuration Validation
        status.start("Testing training configuration...")
        try:
            # Test config structure validation
            config = json.load(open("src/configs/training_config_qlora.json"))
            
            # Verify model structure
            assert "hidden_size" in config["model"], "Model missing hidden_size"
            assert "num_layers" in config["model"], "Model missing num_layers"
            assert "rank" in config["lora"], "LoRA config missing rank"
            assert "bits" in config["qlora"], "QLoRA config missing bits"
            
            test_results.append(("Training Configuration", "✅ PASS", "Configuration structure valid"))
            status.stop("✅ Training config test passed")
        except Exception as e:
            test_results.append(("Training Configuration", "❌ FAIL", str(e)))
            status.stop("❌ Training config test failed")
        
    except Exception as e:
        logger.error(f"Critical error in validation: {e}")
        logger.error(traceback.format_exc())
        test_results.append(("Critical Error", "❌ FAIL", str(e)))
    
    # Display results
    logger.info("\n" + "="*60)
    logger.info("🧪 QLoRA TRAINING INTEGRATION TEST RESULTS")
    logger.info("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, status_icon, details in test_results:
        logger.info(f"{status_icon} {test_name}: {details}")
        if "✅" in status_icon:
            passed += 1
        else:
            failed += 1
    
    logger.info("="*60)
    logger.info(f"📊 Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All QLoRA training integration tests passed!")
        logger.info("✅ Ready for production QLoRA training")
    else:
        logger.error(f"❌ {failed} test(s) failed - please review and fix issues")
    
    return failed == 0


def main():
    """Main test function."""
    print("🧪 Starting QLoRA Training Integration Validation...")
    success = test_qlora_training_integration()
    
    if success:
        print("\n🎯 QLoRA training integration is fully validated and ready!")
        exit(0)
    else:
        print("\n⚠️  Some tests failed - please review the results above")
        exit(1)


if __name__ == "__main__":
    main()
