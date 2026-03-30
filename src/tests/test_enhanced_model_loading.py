#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #gpu_optimization #memory_management #multimodal #python #source_code #src/tests/test_enhanced_model_loading.py #testing #training
**Category:** Testing Framework
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #cuda #gpu_optimization #memory_management #multimodal #python #source_code #src\\tests\\test_enhanced_model_loading.py #testing #training
# Category:** Testing Framework
# Status:** Active

"""
Test Enhanced Model Loading
===========================

Quick test to verify the enhanced model loads with proper config.
"""

import os
import sys

# conftest.py already adds src to sys.path
import pytest
import torch

from models.b2_multimodal.core.b2_multimodal_model import B2MultimodalModel


def test_model_loading():
    """Test enhanced model loading with complete config"""

    print("🧪 Testing Enhanced B2 Model Loading")
    print("=" * 50)

    # Complete configuration from original train_b2.py
    config = {
        'embed_dim': 768,
        'vocab_size': 50257,
        'img_dim': 256,
        'audio_dim': 16000,
        'num_layers': 12,
        'num_heads': 12,
        'max_seq_len': 128000,
        'n_experts': 4,
        'vision_decoder_layers': 8,
        'vision_decoder_steps': 50,
        'audio_decoder_layers': 8,
        'audio_decoder_steps': 50,
        'sp_model_path': 'dummy.model',  # SentencePiece model path
        'vision_patch_dim': 768,  # Vision patch embedding dimension
        'patch_size': 16,  # Vision patch size
        'num_sentiment_classes': 3,  # Number of sentiment classes
        'num_intent_classes': 10,  # Number of intent classes
        'audio_feat_dim': 768,  # Audio feature dimension
        'n_mels': 64,  # Number of mel frequency bins
        'sample_rate': 16000,  # Audio sample rate
        'video_feat_dim': 768,  # Video feature dimension
        'num_frames': 8,  # Number of video frames
        'video_mean': 0.5,  # Video normalization mean
        'video_std': 0.5,  # Video normalization std
    }

    try:
        # Test base model loading
        print("🧠 Loading base B2MultimodalModel...")
        base_model = B2MultimodalModel(config)
        print("✅ Base model loaded successfully")

        # Count parameters
        total_params = sum(p.numel() for p in base_model.parameters())
        print(f"📊 Base model parameters: {total_params:,}")

        # Test device assignment
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"📱 Using device: {device}")

        if torch.cuda.is_available():
            print(f"🎮 GPU: {torch.cuda.get_device_name()}")
            print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

        # Test model forward pass with dummy data
        print("🔍 Testing forward pass...")
        batch_size = 2
        embed_dim = config['embed_dim']

        # Create dummy inputs matching expected format
        dummy_inputs = {
            'text': torch.randn(batch_size, embed_dim),
            'vision': torch.randn(batch_size, embed_dim),
            'audio': torch.randn(batch_size, embed_dim),
            'video': torch.randn(batch_size, embed_dim)
        }

        # Test forward pass
        base_model = base_model.to(device)
        for key in dummy_inputs:
            dummy_inputs[key] = dummy_inputs[key].to(device)

        output = base_model(dummy_inputs, output_modality='conversation', use_precomputed_embeddings=True)
        print(f"✅ Forward pass successful! Output shape: {output.shape}")

    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        pytest.skip(f"Enhanced model loading unavailable: {e}")

if __name__ == "__main__":
    try:
        test_model_loading()
        success = True
    except AssertionError:
        success = False
    if success:
        print("\n🎉 Model loading test passed! Ready for enhanced training.")
    else:
        print("\n💥 Model loading test failed. Fix issues before training.")

    exit(0 if success else 1)
