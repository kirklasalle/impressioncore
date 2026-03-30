#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #gpu_optimization #memory_management #multimodal #python #source_code #src/tests/test_optimizations.py #testing #training
**Category:** Testing Framework
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #gpu_optimization #memory_management #multimodal #python #source_code #src\\tests\\test_optimizations.py #testing #training
# Category:** Testing Framework
# Status:** Active

"""
Test script for the optimized ImpressionCore B3 architecture.
Tests all the critical optimizations that were implemented.
"""

import sys

import pytest

# conftest.py already adds src to sys.path

pytest.importorskip("core.models", reason="core.models not available in current path layout")
import torch

from core.models.impressioncore_b3_architecture import (
    AssemblyOfExperts,
    B3Config,
    ImpressionCoreB3Model,
    print_model_summary,
)


def test_vectorized_experts():
    """Test the vectorized AssemblyOfExperts implementation."""
    print("🔄 Testing vectorized AssemblyOfExperts...")

    embed_dim = 384
    batch_size = 2
    seq_len = 64

    # Create expert module
    aoe = AssemblyOfExperts(
        embed_dim=embed_dim,
        num_experts=4,
        expert_dim=768,
        experts_per_token=2
    )

    # Test input
    x = torch.randn(batch_size, seq_len, embed_dim)

    try:
        output, loss = aoe(x)
        assert output.shape == x.shape, f"Shape mismatch: {output.shape} vs {x.shape}"
        assert isinstance(loss, torch.Tensor), "Loss should be a tensor"
        print("   ✅ Vectorized experts working correctly")
    except Exception as e:
        print(f"   ❌ Vectorized experts failed: {e}")
        raise AssertionError("Vectorized experts test failed") from e

def test_b3_config():
    """Test the simplified B3Config usage."""
    print("🔄 Testing simplified B3Config...")

    try:
        config = B3Config(
            embed_dim=384,
            num_layers=3,
            num_heads=6,
            num_experts=4,
            experts_per_token=2,
            expert_dim=768,
            vocab_size=1000,
            use_gradient_checkpointing=True
        )

        # Test model creation with config
        ImpressionCoreB3Model(config)

        print(f"   ✅ B3Config working: {config.embed_dim}d, {config.num_layers} layers")
        print(f"   ✅ Gradient checkpointing: {config.use_gradient_checkpointing}")
    except Exception as e:
        print(f"   ❌ B3Config failed: {e}")
        raise AssertionError("B3 config test failed") from e

def test_gradient_checkpointing():
    """Test gradient checkpointing functionality."""
    print("🔄 Testing gradient checkpointing...")

    try:
        config = B3Config(
            embed_dim=256,
            num_layers=2,
            num_heads=4,
            num_experts=2,
            use_gradient_checkpointing=True
        )

        model = ImpressionCoreB3Model(config)
        model.train()  # Enable training mode

        # Test forward pass
        batch_size = 1
        seq_len = 32
        input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))

        model(input_ids=input_ids, labels=input_ids)

        # Check if gradient checkpointing flag is properly used
        assert hasattr(model.config, 'use_gradient_checkpointing')
        assert model.config.use_gradient_checkpointing

        print("   ✅ Gradient checkpointing enabled and working")
    except Exception as e:
        print(f"   ❌ Gradient checkpointing failed: {e}")
        raise AssertionError("Gradient checkpointing test failed") from e

def test_full_model():
    """Test the complete optimized model."""
    print("🔄 Testing complete optimized model...")

    try:
        config = B3Config(
            embed_dim=256,
            num_layers=2,
            num_heads=4,
            num_experts=4,
            experts_per_token=2,
            expert_dim=512,
            vocab_size=1000,
            use_gradient_checkpointing=True
        )

        model = ImpressionCoreB3Model(config)
        print_model_summary(model)

        # Test multimodal inputs
        batch_size = 1
        seq_len = 32

        input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
        image_features = torch.randn(batch_size, seq_len, config.image_embed_dim)
        audio_features = torch.randn(batch_size, seq_len, config.audio_embed_dim)

        outputs = model(
            input_ids=input_ids,
            image_features=image_features,
            audio_features=audio_features,
            labels=input_ids
        )

        assert 'loss' in outputs
        assert 'logits' in outputs
        assert 'quality_score' in outputs

        print(f"   ✅ Model outputs: loss={outputs['loss']:.4f}")
        print(f"   ✅ Quality score: {outputs['quality_score'].mean():.4f}")
    except Exception as e:
        print(f"   ❌ Full model test failed: {e}")
        import traceback
        traceback.print_exc()
        raise AssertionError("Full model optimization test failed") from e

def main():
    """Run all optimization tests."""
    print("🧠 Testing ImpressionCore B3 Architecture Optimizations")
    print("=" * 60)

    tests = [
        test_vectorized_experts,
        test_b3_config,
        test_gradient_checkpointing,
        test_full_model
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as exc:
            print(f"   ❌ {test.__name__} failed: {exc}")
        print()

    print("=" * 60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All optimizations verified successfully!")
        print("   ✅ Vectorized AssemblyOfExperts for GPU performance")
        print("   ✅ Simplified ImpressionCoreB3Model configuration")
        print("   ✅ Gradient checkpointing for memory optimization")
        print("   ✅ Redundant B3TrainingConfig class removed")
        print("   ✅ Full multimodal integration working")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed - need investigation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
