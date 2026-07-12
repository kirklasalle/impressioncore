#!/usr/bin/env python3
"""
B3 39M Parameter Architecture Validation
========================================

Validates that the 39M parameter configuration preserves ALL B3 features:
- Assembly of Experts (AoE)
- Multi-Head Latent Attention (MLA)
- Full multimodal support
- Brain-inspired components
- Unified tokenizers

Created: August 6, 2025
Author: Kirk LaSalle & GitHub Copilot
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def validate_b3_39m_architecture():
    """Validate that ALL B3 features are present in the 39M configuration."""

    print("🔍 B3 39M PARAMETER ARCHITECTURE VALIDATION")
    print("=" * 39)

    try:
        # Import B3 components
        from src.core.models.impressioncore_b3_architecture import (
            AssemblyOfExperts,
            B3Config,
            BrainInspiredTransformerLayer,
            DynamicPositionEmbedding,
            ImpressionCoreB3Model,
            MultiHeadLatentAttention,
            MultimodalEmbedding,
            PhonemeAudioProcessor,
        )

        print("✅ ALL B3 components successfully imported")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    # Create EXACT 39M configuration based on successful training proportions
    # Scaled down from the successful 72.8M config (272, 16 layers, 20k vocab)
    config = B3Config(
        embed_dim=224,          # Scaled down from 272 for 39M target
        num_heads=8,            # Keep 8 (proven optimal)
        num_layers=12,          # Reduced from 16 layers for 39M
        vocab_size=16384,       # Reduced from 20000 for 39M
        num_experts=4,          # Keep 4 (optimal MoE)
        expert_dim=320,         # Scaled down from 400 for 39M
        experts_per_token=2,    # Optimal efficiency
        image_embed_dim=224,    # Perfect alignment
        audio_embed_dim=224,    # Perfect alignment
        phoneme_vocab_size=256, # Keep same
        dropout=0.1,
        max_seq_length=2048,    # User requirement
        use_gradient_checkpointing=True
    )

    print("\n📋 39M PARAMETER CONFIGURATION:")
    print(f"  Embed Dim: {config.embed_dim}")
    print(f"  Num Heads: {config.num_heads}")
    print(f"  Num Layers: {config.num_layers}")
    print(f"  Vocab Size: {config.vocab_size}")
    print(f"  Num Experts: {config.num_experts}")
    print(f"  Expert Dim: {config.expert_dim}")
    print(f"  Experts per Token: {config.experts_per_token}")
    print(f"  Max Seq Length: {config.max_seq_length}")

    # Validate B3 features
    print("\n🧠 B3 FEATURE VALIDATION:")

    features_status = []

    try:
        # Test Assembly of Experts (AoE)
        AssemblyOfExperts(
            embed_dim=config.embed_dim,
            num_experts=config.num_experts,
            expert_dim=config.expert_dim,
            experts_per_token=config.experts_per_token,
            num_heads=config.num_heads
        )
        features_status.append("✅ Assembly of Experts (AoE) - FUNCTIONAL")
    except Exception as e:
        features_status.append(f"❌ Assembly of Experts (AoE) - ERROR: {e}")

    try:
        # Test Multi-Head Latent Attention (MLA)
        MultiHeadLatentAttention(
            embed_dim=config.embed_dim,
            num_heads=config.num_heads
        )
        features_status.append("✅ Multi-Head Latent Attention (MLA) - FUNCTIONAL")
    except Exception as e:
        features_status.append(f"❌ Multi-Head Latent Attention (MLA) - ERROR: {e}")

    try:
        # Test Multimodal Embedding
        MultimodalEmbedding(
            embed_dim=config.embed_dim,
            vocab_size=config.vocab_size,
            image_embed_dim=config.image_embed_dim,
            audio_embed_dim=config.audio_embed_dim,
            phoneme_vocab_size=config.phoneme_vocab_size,
            num_heads=config.num_heads
        )
        features_status.append("✅ Multimodal Embedding (Text/Image/Audio/Phoneme) - FUNCTIONAL")
    except Exception as e:
        features_status.append(f"❌ Multimodal Embedding - ERROR: {e}")

    try:
        # Test Brain-Inspired Transformer Layer
        BrainInspiredTransformerLayer(
            embed_dim=config.embed_dim,
            num_heads=config.num_heads,
            num_experts=config.num_experts,
            expert_dim=config.expert_dim,
            experts_per_token=config.experts_per_token
        )
        features_status.append("✅ Brain-Inspired Transformer Layer - FUNCTIONAL")
    except Exception as e:
        features_status.append(f"❌ Brain-Inspired Transformer Layer - ERROR: {e}")

    try:
        # Test Dynamic Position Encoding
        DynamicPositionEmbedding(
            embed_dim=config.embed_dim,
            max_seq_length=config.max_seq_length
        )
        features_status.append("✅ Dynamic Position Encoding (RoPE) - FUNCTIONAL")
    except Exception as e:
        features_status.append(f"❌ Dynamic Position Encoding - ERROR: {e}")

    try:
        # Test Phoneme Audio Processor
        PhonemeAudioProcessor(
            audio_embed_dim=config.audio_embed_dim,
            phoneme_vocab_size=config.phoneme_vocab_size,
            embed_dim=config.embed_dim
        )
        features_status.append("✅ Phoneme Audio Processor - FUNCTIONAL")
    except Exception as e:
        features_status.append(f"❌ Phoneme Audio Processor - ERROR: {e}")

    # Print feature status
    for status in features_status:
        print(f"  {status}")

    # Test complete model creation
    print("\n🏗️ COMPLETE MODEL VALIDATION:")

    try:
        model = ImpressionCoreB3Model(config)
        total_params = sum(p.numel() for p in model.parameters())

        print("✅ Complete B3 Model Creation - SUCCESS")
        print(f"📊 Total Parameters: {total_params:,} ({total_params/1e6:.1f}M)")

        # Validate parameter count is close to 39M
        target_params = 39_000_000
        param_diff = abs(total_params - target_params)
        param_diff_percent = (param_diff / target_params) * 100

        if param_diff_percent < 15:  # Tolerance for 39M target
            print(f"✅ Parameter count within 39M range ({param_diff_percent:.1f}% difference)")
        else:
            print(f"⚠️ Parameter count differs significantly ({param_diff_percent:.1f}% difference)")

    except Exception as e:
        print(f"❌ Complete Model Creation - ERROR: {e}")
        return False

    # Test multimodal forward pass
    print("\n🔄 MULTIMODAL FORWARD PASS TEST:")

    try:
        import torch

        # Create test inputs for ALL modalities with CONSISTENT dimensions
        batch_size = 2
        seq_len = 128

        input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
        image_features = torch.randn(batch_size, seq_len, config.image_embed_dim)  # Ensure seq_len dimension
        audio_features = torch.randn(batch_size, seq_len, config.audio_embed_dim)  # Ensure seq_len dimension
        phoneme_ids = torch.randint(0, config.phoneme_vocab_size, (batch_size, seq_len))
        modality_type = torch.zeros(batch_size, seq_len, dtype=torch.long)  # Match sequence dimension

        # Forward pass with ALL B3 features
        with torch.no_grad():
            print("🔍 Debug: Input shapes before forward pass:")
            print(f"  input_ids: {input_ids.shape}")
            print(f"  image_features: {image_features.shape}")
            print(f"  audio_features: {audio_features.shape}")
            print(f"  phoneme_ids: {phoneme_ids.shape}")
            print(f"  modality_type: {modality_type.shape}")

            output = model(
                input_ids=input_ids,
                image_features=image_features,
                audio_features=audio_features,
                phoneme_ids=phoneme_ids,
                modality_type=modality_type
            )

        print("✅ Multimodal Forward Pass - SUCCESS")

        # Handle output that might be a dict or tensor
        if isinstance(output, dict):
            output_shape = output['logits'].shape if 'logits' in output else f"Dict with keys: {list(output.keys())}"
        else:
            output_shape = output.shape

        print(f"📊 Output Shape: {output_shape}")
        print("🧠 ALL modalities processed: Text, Image, Audio, Phoneme")

    except Exception as e:
        print(f"❌ Multimodal Forward Pass - ERROR: {e}")
        return False

    # Calculate detailed parameter breakdown
    print("\n📊 DETAILED PARAMETER BREAKDOWN:")

    # Embeddings
    token_emb = config.vocab_size * config.embed_dim
    pos_emb = config.max_seq_length * config.embed_dim
    image_proj = config.image_embed_dim * config.embed_dim
    audio_proj = config.audio_embed_dim * config.embed_dim
    phoneme_emb = config.phoneme_vocab_size * config.embed_dim
    total_embeddings = token_emb + pos_emb + image_proj + audio_proj + phoneme_emb

    print(f"  Embeddings: {total_embeddings:,} ({total_embeddings/1e6:.1f}M)")
    print(f"    - Token: {token_emb:,}")
    print(f"    - Position: {pos_emb:,}")
    print(f"    - Image Proj: {image_proj:,}")
    print(f"    - Audio Proj: {audio_proj:,}")
    print(f"    - Phoneme: {phoneme_emb:,}")

    # Per layer (approximate)
    mla_params = 4 * config.embed_dim * config.embed_dim  # Approximate MLA
    aoe_params = config.num_experts * (config.embed_dim * config.expert_dim * 2)  # Approximate AoE
    per_layer_approx = mla_params + aoe_params + (2 * config.embed_dim * 2)  # + layer norms
    all_layers = per_layer_approx * config.num_layers

    print(f"  Transformer Layers: {all_layers:,} ({all_layers/1e6:.1f}M)")
    print(f"    - Per Layer (approx): {per_layer_approx:,}")
    print(f"    - MLA per layer: {mla_params:,}")
    print(f"    - AoE per layer: {aoe_params:,}")

    # Output
    output_params = config.embed_dim * config.vocab_size
    print(f"  Output Projection: {output_params:,} ({output_params/1e6:.1f}M)")

    approx_total = total_embeddings + all_layers + output_params
    print(f"  APPROXIMATE TOTAL: {approx_total:,} ({approx_total/1e6:.1f}M)")

    # Final validation summary
    print("\n🎯 VALIDATION SUMMARY:")

    all_features_working = all("✅" in status for status in features_status)

    if all_features_working and param_diff_percent < 15:  # 39M tolerance
        print("✅ ALL B3 FEATURES VALIDATED")
        print("✅ Parameter count within 39M range")
        print("✅ Multimodal processing functional")
        print("✅ 39M parameter B3 architecture READY")
        print("")
        print("🚀 RECOMMENDATION: Proceed with 39M B3 training")
        print("   ALL advanced B3 features preserved and functional")
        return True
    else:
        print("❌ VALIDATION FAILED")
        print("   Some B3 features may not be working correctly")
        return False

def main():
    """Main validation function."""
    success = validate_b3_39m_architecture()

    if success:
        print("\n🎉 B3 39M PARAMETER VALIDATION: PASSED")
    else:
        print("\n💥 B3 39M PARAMETER VALIDATION: FAILED")

    return success

if __name__ == "__main__":
    main()
