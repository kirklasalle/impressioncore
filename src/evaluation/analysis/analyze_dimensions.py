#!/usr/bin/env python3
"""
Analyze exact dimensions from the best quality model
This will give us the precise configuration to recreate the sweet spot
"""

import os

import torch


def analyze_model_dimensions():
    """Extract exact dimensions from best quality model"""

    checkpoint_path = "F:/models/checkpoints/best_quality/b3_best_quality_model_20250802_124801.pth"

    print("🔍 Analyzing B3 Best Quality Model Dimensions")
    print("=" * 60)

    if not os.path.exists(checkpoint_path):
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        return

    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)

    # Extract key dimensions
    dims = {}

    # Text encoder dimensions
    if 'text_encoder.base_encoder.0.weight' in checkpoint:
        text_input_dim = checkpoint['text_encoder.base_encoder.0.weight'].shape[1]
        text_hidden_dim = checkpoint['text_encoder.base_encoder.0.weight'].shape[0]
        dims['text_input_dim'] = text_input_dim
        dims['text_hidden_dim'] = text_hidden_dim
        print(f"📝 Text Encoder: {text_input_dim} → {text_hidden_dim}")

    # Image encoder dimensions
    if 'image_encoder.base_encoder.0.weight' in checkpoint:
        image_input_dim = checkpoint['image_encoder.base_encoder.0.weight'].shape[1]
        image_hidden_dim = checkpoint['image_encoder.base_encoder.0.weight'].shape[0]
        dims['image_input_dim'] = image_input_dim
        dims['image_hidden_dim'] = image_hidden_dim
        print(f"🖼️  Image Encoder: {image_input_dim} → {image_hidden_dim}")

    # Audio encoder dimensions
    if 'audio_encoder.base_encoder.0.weight' in checkpoint:
        audio_input_dim = checkpoint['audio_encoder.base_encoder.0.weight'].shape[1]
        audio_hidden_dim = checkpoint['audio_encoder.base_encoder.0.weight'].shape[0]
        dims['audio_input_dim'] = audio_input_dim
        dims['audio_hidden_dim'] = audio_hidden_dim
        print(f"🎵 Audio Encoder: {audio_input_dim} → {audio_hidden_dim}")

    # Fusion attention dimensions
    if 'fusion.attention.in_proj_weight' in checkpoint:
        fusion_dim = checkpoint['fusion.attention.in_proj_weight'].shape[1]
        attention_dim = checkpoint['fusion.attention.in_proj_weight'].shape[0] // 3  # qkv combined
        dims['fusion_dim'] = fusion_dim
        dims['attention_dim'] = attention_dim
        print(f"🔗 Fusion Attention: {fusion_dim} → {attention_dim}")

    # MoE expert dimensions
    if 'moe.experts.0.0.weight' in checkpoint:
        expert_input_dim = checkpoint['moe.experts.0.0.weight'].shape[1]
        expert_hidden_dim = checkpoint['moe.experts.0.0.weight'].shape[0]
        dims['expert_input_dim'] = expert_input_dim
        dims['expert_hidden_dim'] = expert_hidden_dim
        print(f"🧠 MoE Expert: {expert_input_dim} → {expert_hidden_dim}")

    # Count experts
    expert_count = 0
    for key in checkpoint:
        if key.startswith('moe.experts.') and key.endswith('.0.weight'):
            expert_count += 1
    dims['num_experts'] = expert_count
    print(f"👥 Number of Experts: {expert_count}")

    # Gate dimensions
    if 'moe.gate.0.weight' in checkpoint:
        gate_input_dim = checkpoint['moe.gate.0.weight'].shape[1]
        gate_output_dim = checkpoint['moe.gate.0.weight'].shape[0]
        dims['gate_input_dim'] = gate_input_dim
        dims['gate_output_dim'] = gate_output_dim
        print(f"🚪 Gate Network: {gate_input_dim} → {gate_output_dim}")

    # Conversation head dimensions
    if 'conversation_head.0.weight' in checkpoint:
        conv_input_dim = checkpoint['conversation_head.0.weight'].shape[1]
        conv_hidden_dim = checkpoint['conversation_head.0.weight'].shape[0]
        dims['conv_input_dim'] = conv_input_dim
        dims['conv_hidden_dim'] = conv_hidden_dim
        print(f"💬 Conversation Head: {conv_input_dim} → {conv_hidden_dim}")

    if 'conversation_head.4.weight' in checkpoint:
        conv_output_dim = checkpoint['conversation_head.4.weight'].shape[0]
        dims['conv_output_dim'] = conv_output_dim
        print(f"💬 Conversation Output: {conv_output_dim}")

    # Calculate total parameters
    total_params = 0
    for param in checkpoint.values():
        if isinstance(param, torch.Tensor):
            total_params += param.numel()

    print(f"\n📊 TOTAL PARAMETERS: {total_params:,}")
    print(f"📏 Size: {total_params / 1_000_000:.1f}M parameters")

    # Generate configuration
    print("\n🛠️  CONFIGURATION FOR TRAINING SCRIPT:")
    print("=" * 50)
    print("B3Config(")
    for key, value in dims.items():
        print(f"    {key}={value},")
    print(")")

    return dims

if __name__ == "__main__":
    analyze_model_dimensions()
