#!/usr/bin/env python3
"""
B3 Checkpoint Analyzer
=====================

Analyzes the actual checkpoint configuration from successful training sessions
to recreate the exact architecture that initiated the sweet spot theory.

Created: August 7, 2025
Author: Kirk LaSalle & GitHub Copilot
"""

import sys
from pathlib import Path

import torch

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def analyze_checkpoint(checkpoint_path):
    """Analyze a checkpoint file and extract configuration details."""
    print(f"🔍 Analyzing checkpoint: {checkpoint_path}")
    print("=" * 80)

    try:
        # Load the checkpoint
        checkpoint = torch.load(checkpoint_path, map_location='cpu')

        print("📋 CHECKPOINT CONTENTS:")
        for key in checkpoint:
            if isinstance(checkpoint[key], dict):
                print(f"  {key}: dict with {len(checkpoint[key])} items")
            elif isinstance(checkpoint[key], list):
                print(f"  {key}: list with {len(checkpoint[key])} items")
            else:
                print(f"  {key}: {type(checkpoint[key])}")

        # Extract configuration if available
        if 'config' in checkpoint:
            config = checkpoint['config']
            print("\n🏗️ MODEL CONFIGURATION:")
            if hasattr(config, '__dict__'):
                for attr, value in config.__dict__.items():
                    print(f"  {attr}: {value}")
            else:
                print(f"  Config type: {type(config)}")
                print(f"  Config: {config}")

        # Extract model parameter count
        if 'total_params' in checkpoint:
            total_params = checkpoint['total_params']
            print(f"\n📊 TOTAL PARAMETERS: {total_params:,} ({total_params/1e6:.1f}M)")

        # Extract training history
        if 'loss_history' in checkpoint:
            loss_history = checkpoint['loss_history']
            print("\n📈 TRAINING HISTORY:")
            print(f"  Epochs: {len(loss_history)}")
            if loss_history:
                print(f"  Initial Loss: {loss_history[0]:.6f}")
                print(f"  Final Loss: {loss_history[-1]:.6f}")
                improvement = ((loss_history[0] - loss_history[-1]) / loss_history[0] * 100)
                print(f"  Improvement: {improvement:.2f}%")

        # Analyze model state dict for architecture clues
        if 'model_state_dict' in checkpoint or 'state_dict' in checkpoint:
            state_dict_key = 'model_state_dict' if 'model_state_dict' in checkpoint else 'state_dict'
            state_dict = checkpoint[state_dict_key]

            print("\n🧠 MODEL ARCHITECTURE ANALYSIS:")

            # Extract embedding dimensions
            embed_keys = [k for k in state_dict if 'embedding' in k.lower()]
            for key in embed_keys[:5]:  # Show first 5
                shape = state_dict[key].shape
                print(f"  {key}: {shape}")

            # Extract key architectural parameters
            for key, tensor in state_dict.items():
                if 'text_encoder.embeddings.word_embeddings.weight' in key:
                    vocab_size, embed_dim = tensor.shape
                    print(f"  📝 Text Embeddings: vocab_size={vocab_size}, embed_dim={embed_dim}")
                    break

            # Count transformer layers
            layer_count = 0
            for key in state_dict:
                if 'layers.' in key and '.attention.query.weight' in key:
                    layer_num = int(key.split('layers.')[1].split('.')[0])
                    layer_count = max(layer_count, layer_num + 1)

            if layer_count > 0:
                print(f"  🏗️ Transformer Layers: {layer_count}")

            # Extract attention heads
            for key, tensor in state_dict.items():
                if 'attention.query.weight' in key:
                    hidden_size = tensor.shape[0]
                    tensor.shape[1] // 8  # Assuming 8 heads initially
                    if hidden_size % 64 == 0:  # Common head dimension
                        num_heads = hidden_size // 64
                        print(f"  🎯 Attention: hidden_size={hidden_size}, estimated_heads={num_heads}")
                    break

            # Extract MoE information
            expert_count = 0
            for key in state_dict:
                if 'experts.' in key and '.weight' in key:
                    expert_num = int(key.split('experts.')[1].split('.')[0])
                    expert_count = max(expert_count, expert_num + 1)

            if expert_count > 0:
                print(f"  🧬 MoE Experts: {expert_count}")

        return checkpoint

    except Exception as e:
        print(f"❌ Error analyzing checkpoint: {e}")
        return None

def main():
    """Main analysis function."""
    print("🚀 B3 Sweet Spot Recovery Checkpoint Analyzer")
    print("=" * 55)

    # Analyze the newly saved recovery checkpoint from step 500
    recovery_checkpoint_path = Path("F:/models/checkpoints/sweet_spot_recovery/recovery_step_500.pth")

    if not recovery_checkpoint_path.exists():
        print(f"❌ Recovery checkpoint not found: {recovery_checkpoint_path}")
        # Fallback to original best quality model
        recovery_checkpoint_path = Path("F:/models/checkpoints/best_quality/b3_best_quality_model_20250802_124801.pth")
        if not recovery_checkpoint_path.exists():
            print(f"❌ Best quality model not found: {recovery_checkpoint_path}")
            return
        print("🔄 Analyzing original best quality model instead")
    else:
        print("🎯 Analyzing STEP 500 RECOVERY CHECKPOINT")
        print("✅ This model has been trained for 500 steps from the sweet spot")
        print("✅ Loss improved from 1.303853 to 1.000170")

    latest_checkpoint = recovery_checkpoint_path

    print(f"📍 Latest checkpoint: {latest_checkpoint.name}")
    print(f"📅 Modified: {latest_checkpoint.stat().st_mtime}")
    print(f"📦 Size: {latest_checkpoint.stat().st_size / (1024*1024):.1f} MB")

    # Analyze the checkpoint
    checkpoint_data = analyze_checkpoint(latest_checkpoint)

    if checkpoint_data and 'config' in checkpoint_data:
        config = checkpoint_data['config']

        print("\n" + "="*80)
        print("🔧 RECOMMENDED TRAINING SCRIPT CONFIGURATION:")
        print("="*80)

        print("config = B3Config(")
        if hasattr(config, '__dict__'):
            for attr, value in config.__dict__.items():
                if isinstance(value, str):
                    print(f"    {attr}=\"{value}\",")
                else:
                    print(f"    {attr}={value},")
        print(")")

        # Extract parameter count for verification
        if 'total_params' in checkpoint_data:
            total_params = checkpoint_data['total_params']
            print(f"\n✅ This configuration produces: {total_params:,} parameters ({total_params/1e6:.1f}M)")

            if 35e6 <= total_params <= 45e6:
                print("🎯 This appears to be your 39M sweet spot configuration!")
            elif total_params > 50e6:
                print("⚠️ This is a scaled-up configuration - may need adjustment for 39M target")

if __name__ == "__main__":
    main()
