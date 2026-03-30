#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #attention_mechanism #cuda #gpu_optimization #memory_management #multimodal #python #pytorch #source_code #src/training/test_trainers.py #testing #tokenization #training #transformer
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** Kirk LaSalle
# Tags:** #attention_mechanism #cuda #gpu_optimization #memory_management #multimodal #python #pytorch #source_code #src\\training\\test_trainers.py #testing #tokenization #training #transformer
# Category:** Training System
# Status:** Active

"""
ImpressionCore Trainers Test Suite

File: src/training/test_trainers.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: June 12, 2025
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, training, validation, debug, 2025]
Dependencies: [torch, transformers, rich]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Comprehensive test suite to validate both the High School Distillation Trainer
and the Multimodal Dataset Loaders. Ensures proper operation, import resolution,
and compatibility across the training pipeline.

Features:
- Import validation
- Basic functionality tests
- Memory efficiency checks
- Configuration validation
- Error handling tests
"""

import sys
import torch
import traceback
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def test_imports():
    """Test that all necessary imports work correctly."""
    print("🔧 Testing imports...")

    try:
        # Test core PyTorch imports
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
        from torch.utils.data import DataLoader, Dataset
        print("✅ PyTorch imports successful")

        # Test transformers imports
        from transformers import AutoTokenizer, AutoModel
        print("✅ Transformers imports successful")
          # Test ImpressionCore imports
        from high_school_distillation_trainer import HighSchoolDistillationTrainer, HighSchoolTrainingConfig
        print("✅ High School Trainer imports successful")

        from multimodal_dataset_loaders import MultimodalDatasetLoader
        print("✅ Multimodal Dataset Loader imports successful")
          # Test model imports
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(project_root / "src"))
        from models.impressioncore_base.b1_model import ImpressionCoreB1Model
        from core.config.model_config import ModelConfig
        print("✅ Model imports successful")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_high_school_trainer_config():
    """Test High School Trainer configuration."""
    print("\n📚 Testing High School Trainer configuration...")

    try:
        from high_school_distillation_trainer import HighSchoolTrainingConfig

        config = HighSchoolTrainingConfig()

        # Validate config attributes
        assert hasattr(config, 'model_dim'), "Missing model_dim"
        assert hasattr(config, 'num_layers'), "Missing num_layers"
        assert hasattr(config, 'batch_size'), "Missing batch_size"
        assert hasattr(config, 'teacher_model'), "Missing teacher_model"
        assert hasattr(config, 'temperature'), "Missing temperature"

        print(f"  Model dimensions: {config.model_dim}")
        print(f"  Number of layers: {config.num_layers}")
        print(f"  Batch size: {config.batch_size}")
        print(f"  Teacher model: {config.teacher_model}")
        print(f"  Temperature: {config.temperature}")
        print(f"  Grade levels: {config.grade_levels}")
        print(f"  Subject areas: {len(config.subject_areas)} subjects")

        print("✅ High School Trainer configuration valid")
        return True

    except Exception as e:
        print(f"❌ High School Trainer config failed: {e}")
        traceback.print_exc()
        return False

def test_model_creation():
    """Test model creation and basic functionality."""
    print("\n🧠 Testing model creation...")

    try:
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(project_root / "src"))
        from models.impressioncore_base.b1_model import ImpressionCoreB1Model
        from core.config.model_config import ModelConfig

        # Create model config
        model_config = ModelConfig(
            hidden_size=256,
            num_hidden_layers=4,
            num_attention_heads=8,
            max_position_embeddings=512
        )

        # Create model
        model = ImpressionCoreB1Model(model_config)

        # Test forward pass
        batch_size = 2
        seq_len = 128
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))

        with torch.no_grad():
            outputs = model(input_ids)

        assert 'logits' in outputs, "Model output missing 'logits'"
        logits = outputs['logits']

        expected_shape = (batch_size, seq_len, 50257)  # GPT-2 vocab size
        assert logits.shape == expected_shape, f"Expected shape {expected_shape}, got {logits.shape}"

        param_count = sum(p.numel() for p in model.parameters())
        print(f"  Model parameters: {param_count:,}")
        print(f"  Output shape: {logits.shape}")

        print("✅ Model creation and forward pass successful")
        return True

    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        traceback.print_exc()
        return False

def test_multimodal_loader():
    """Test multimodal dataset loader."""
    print("\n🎭 Testing multimodal dataset loader...")

    try:
        from multimodal_dataset_loaders import MultimodalDatasetLoader

        # Create config
        config = {
            'max_text_length': 128,
            'batch_size': 2,
            'pin_memory': True
        }

        # Create loader
        loader = MultimodalDatasetLoader(config)

        # Test text transform
        sample_text = "This is a test sentence for the multimodal loader."
        text_result = loader.text_transform(sample_text)

        assert 'input_ids' in text_result, "Missing input_ids"
        assert 'attention_mask' in text_result, "Missing attention_mask"
        assert 'labels' in text_result, "Missing labels"

        print(f"  Text processing successful")
        print(f"  Input shape: {text_result['input_ids'].shape}")
        print(f"  Attention mask shape: {text_result['attention_mask'].shape}")

        print("✅ Multimodal loader basic functionality working")
        return True

    except Exception as e:
        print(f"❌ Multimodal loader test failed: {e}")
        traceback.print_exc()
        return False

def test_memory_efficiency():
    """Test memory efficiency and GPU compatibility."""
    print("\n💾 Testing memory efficiency...")

    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"  Testing on device: {device}")

        if torch.cuda.is_available():
            # Check VRAM
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"  Total VRAM: {total_memory:.2f} GB")

            # Test memory allocation
            initial_memory = torch.cuda.memory_allocated() / 1024**3            # Create small model for testing
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))
            sys.path.insert(0, str(project_root / "src"))
            from models.impressioncore_base.b1_model import ImpressionCoreB1Model
            from core.config.model_config import ModelConfig

            model_config = ModelConfig(
                hidden_size=128,
                num_hidden_layers=2,
                num_attention_heads=4,
                max_position_embeddings=256
            )

            model = ImpressionCoreB1Model(model_config).to(device)

            # Test forward pass
            input_ids = torch.randint(0, 1000, (1, 64)).to(device)

            with torch.no_grad():
                outputs = model(input_ids)

            peak_memory = torch.cuda.max_memory_allocated() / 1024**3
            print(f"  Peak memory usage: {peak_memory:.3f} GB")

            # Cleanup
            del model, outputs, input_ids
            torch.cuda.empty_cache()

        print("✅ Memory efficiency test completed")
        return True

    except Exception as e:
        print(f"❌ Memory efficiency test failed: {e}")
        traceback.print_exc()
        return False

def test_knowledge_distillation_components():
    """Test knowledge distillation specific components."""
    print("\n🎓 Testing knowledge distillation components...")

    try:
        from high_school_distillation_trainer import HighSchoolTrainingConfig

        config = HighSchoolTrainingConfig()

        # Test loss functions
        import torch.nn as nn
        import torch.nn.functional as F

        distillation_loss = nn.KLDivLoss(reduction='batchmean')
        task_loss = nn.CrossEntropyLoss()

        # Test temperature scaling
        batch_size, seq_len, vocab_size = 2, 10, 1000
        student_logits = torch.randn(batch_size, seq_len, vocab_size)
        teacher_logits = torch.randn(batch_size, seq_len, vocab_size)
        targets = torch.randint(0, vocab_size, (batch_size, seq_len))

        # Apply temperature scaling
        temperature = config.temperature
        student_soft = F.log_softmax(student_logits / temperature, dim=-1)
        teacher_soft = F.softmax(teacher_logits / temperature, dim=-1)

        # Compute losses
        distill_loss = distillation_loss(student_soft, teacher_soft) * (temperature ** 2)
        hard_loss = task_loss(student_logits.view(-1, vocab_size), targets.view(-1))

        # Combined loss
        total_loss = config.alpha * distill_loss + config.beta * hard_loss

        print(f"  Distillation loss: {distill_loss.item():.4f}")
        print(f"  Hard loss: {hard_loss.item():.4f}")
        print(f"  Total loss: {total_loss.item():.4f}")
        print(f"  Temperature: {temperature}")
        print(f"  Alpha (distill weight): {config.alpha}")
        print(f"  Beta (task weight): {config.beta}")

        print("✅ Knowledge distillation components working")
        return True

    except Exception as e:
        print(f"❌ Knowledge distillation test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run comprehensive test suite."""
    print("🚀 ImpressionCore Trainers Test Suite")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print("=" * 50)

    tests = [
        ("Import Validation", test_imports),
        ("High School Trainer Config", test_high_school_trainer_config),
        ("Model Creation", test_model_creation),
        ("Multimodal Loader", test_multimodal_loader),
        ("Memory Efficiency", test_memory_efficiency),
        ("Knowledge Distillation", test_knowledge_distillation_components),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*50)
    print("🏁 TEST SUMMARY")
    print("="*50)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Trainers are ready for use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
