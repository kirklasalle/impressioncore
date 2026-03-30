"""
B3 Optimized Model Builder - Test Parameter Count
=================================================

Created: October 11, 2025
Author: Kirk LaSalle; GitHub Copilot

Quick test to build optimized model and validate parameter count.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


import torch
import torch.nn as nn
from typing import Optional, Tuple, Dict, Any

from src.core.models.b3_foundation_optimized_config import B3OptimizedConfig
from src.core.models.b3_multimodal_encoders import TextEncoder, MultimodalFusion
from src.core.models.b3_foundation import (
    AssemblyOfExperts,
    MixtureOfExpertsRouter,
    MultiHeadLatentAttention,
    BrainSimAdapter
)


class B3OptimizedIntegrated(nn.Module):
    def _log_parameter_count(self):
        """Log detailed parameter breakdown."""
        def count_params(module):
            return sum(p.numel() for p in module.parameters())
        text_params = count_params(self.text_encoder)
        fusion_params = count_params(self.multimodal_fusion)
        aoe_params = count_params(self.assembly_of_experts)
        router_params = count_params(self.moe_router)
        attn_params = count_params(self.multi_head_attention)
        brain_params = count_params(self.brainsim_adapter)
        output_params = count_params(self.output_projection) + count_params(self.output_layer_norm)
        encoder_total = text_params + fusion_params
        core_total = aoe_params + router_params + attn_params + brain_params + output_params
        grand_total = encoder_total + core_total
        print("\n" + "=" * 80)
        print("📊 B3 Optimized Model Parameter Breakdown:")
        print("-" * 80)
        print(f"  TextEncoder              : {text_params:>12,} ({text_params/grand_total*100:>5.2f}%)")
        print(f"  MultimodalFusion         : {fusion_params:>12,} ({fusion_params/grand_total*100:>5.2f}%)")
        print(f"  TOTAL ENCODERS           : {encoder_total:>12,} ({encoder_total/grand_total*100:>5.2f}%)")
        print("-" * 80)
        print(f"  AssemblyOfExperts        : {aoe_params:>12,} ({aoe_params/grand_total*100:>5.2f}%)")
        print(f"  MoERouter                : {router_params:>12,} ({router_params/grand_total*100:>5.2f}%)")
        print(f"  MultiHeadAttention       : {attn_params:>12,} ({attn_params/grand_total*100:>5.2f}%)")
        print(f"  BrainSimAdapter          : {brain_params:>12,} ({brain_params/grand_total*100:>5.2f}%)")
        print(f"  OutputProjection         : {output_params:>12,} ({output_params/grand_total*100:>5.2f}%)")
        print(f"  TOTAL CORE               : {core_total:>12,} ({core_total/grand_total*100:>5.2f}%)")
        print("-" * 80)
        print(f"  GRAND TOTAL              : {grand_total:>12,} parameters")
        print(f"  TARGET (Constitutional)  : {self.config.target_parameters:>12,} parameters")
        diff = grand_total - self.config.target_parameters
        diff_pct = abs(diff) / self.config.target_parameters * 100
        if diff > 0:
            print(f"  OVER TARGET              : {diff:>12,} (+{diff_pct:.1f}%)")
        elif diff < 0:
            print(f"  UNDER TARGET             : {abs(diff):>12,} (-{diff_pct:.1f}%)")
        else:
            print(f"  ✅ EXACT TARGET MATCH")
        print("=" * 80)
        # Constitutional compliance check
        if diff_pct <= 5.0:
            print(f"✅ Constitutional compliance: Within 5% of target")
        else:
            print(f"⚠️  Need further optimization: {diff_pct:.1f}% from target")
    """Optimized B3 with 39M parameter target."""

    def __init__(self, config: B3OptimizedConfig):
        super().__init__()
        self.config = config

        print("\n🔧 Building Optimized B3 Model...")
        print(f"   Target: {config.target_parameters:,} parameters")
        print(f"   d_model: {config.d_model}")
        print(f"   vocab_size: {config.vocab_size:,}")
        print(f"   text_layers: {config.text_num_hidden_layers}")

        # Text encoder with optimized config
        self.text_encoder = TextEncoder(config)

        # Multimodal fusion
        self.multimodal_fusion = MultimodalFusion(config)

        # Assembly of Experts (will auto-scale to d_model=320)
        self.assembly_of_experts = AssemblyOfExperts(config)

        # MoE Router
        self.moe_router = MixtureOfExpertsRouter(config)

        # Multi-Head Attention
        self.multi_head_attention = MultiHeadLatentAttention(config)

        # BrainSim Adapter
        self.brainsim_adapter = BrainSimAdapter(config)

        # Output projection (to compressed vocab)
        self.output_projection = nn.Linear(config.d_model, config.vocab_size)
        self.output_layer_norm = nn.LayerNorm(config.d_model)

        print("✅ Model components initialized")

        # Count parameters
        self._log_parameter_count()

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        memory_state: Optional[torch.Tensor] = None,
        return_aux_outputs: bool = False,
        return_loss: bool = False
    ) -> Dict[str, Any]:
        """
        Forward pass for B3OptimizedIntegrated student model.
        Args:
            input_ids: Token IDs (batch_size, seq_len)
            attention_mask: Optional attention mask
            memory_state: Optional BrainSim memory state
            return_aux_outputs: Whether to return auxiliary outputs
        Returns:
            dict with keys:
                'logits': Output logits (batch_size, seq_len, vocab_size)
                'aux_outputs': Optional auxiliary outputs dict
        """
        batch_size, seq_len = input_ids.shape
        # Text encoding
        text_embeds = self.text_encoder(input_ids)
        # Fusion
        fused_embeds, modality_info = self.multimodal_fusion(text_embeds=text_embeds)
        # MoE routing
        expert_weights, expert_indices, router_aux = self.moe_router(fused_embeds)
        # Assembly of Experts
        expert_output, aoe_aux = self.assembly_of_experts(
            fused_embeds,
            expert_weights,
            expert_indices
        )
        # Multi-Head Attention
        attention_output, attention_aux = self.multi_head_attention(
            expert_output,
            attention_mask=attention_mask
        )
        # BrainSim Adapter
        adapted_output, adapter_aux = self.brainsim_adapter(
            attention_output,
            memory_state=memory_state
        )
        # Output projection
        logits = self.output_projection(self.output_layer_norm(adapted_output))
        aux_outputs = None
        if return_aux_outputs:
            aux_outputs = {
                "router": router_aux,
                "assembly_of_experts": aoe_aux,
                "attention": attention_aux,
                "brainsim_adapter": adapter_aux,
                "load_balancing_loss": router_aux["load_balancing_loss"]
            }
        # Return as dict for compatibility with tester
        return {"logits": logits, "aux_outputs": aux_outputs}
        """Log detailed parameter breakdown."""
        def count_params(module):
            return sum(p.numel() for p in module.parameters())

        text_params = count_params(self.text_encoder)
        fusion_params = count_params(self.multimodal_fusion)
        aoe_params = count_params(self.assembly_of_experts)
        router_params = count_params(self.moe_router)
        attn_params = count_params(self.multi_head_attention)
        brain_params = count_params(self.brainsim_adapter)
        output_params = count_params(self.output_projection) + count_params(self.output_layer_norm)

        encoder_total = text_params + fusion_params
        core_total = aoe_params + router_params + attn_params + brain_params + output_params
        grand_total = encoder_total + core_total

        print("\n" + "=" * 80)
        print("📊 B3 Optimized Model Parameter Breakdown:")
        print("-" * 80)
        print(f"  TextEncoder              : {text_params:>12,} ({text_params/grand_total*100:>5.2f}%)")
        print(f"  MultimodalFusion         : {fusion_params:>12,} ({fusion_params/grand_total*100:>5.2f}%)")
        print(f"  TOTAL ENCODERS           : {encoder_total:>12,} ({encoder_total/grand_total*100:>5.2f}%)")
        print("-" * 80)
        print(f"  AssemblyOfExperts        : {aoe_params:>12,} ({aoe_params/grand_total*100:>5.2f}%)")
        print(f"  MoERouter                : {router_params:>12,} ({router_params/grand_total*100:>5.2f}%)")
        print(f"  MultiHeadAttention       : {attn_params:>12,} ({attn_params/grand_total*100:>5.2f}%)")
        print(f"  BrainSimAdapter          : {brain_params:>12,} ({brain_params/grand_total*100:>5.2f}%)")
        print(f"  OutputProjection         : {output_params:>12,} ({output_params/grand_total*100:>5.2f}%)")
        print(f"  TOTAL CORE               : {core_total:>12,} ({core_total/grand_total*100:>5.2f}%)")
        print("-" * 80)
        print(f"  GRAND TOTAL              : {grand_total:>12,} parameters")
        print(f"  TARGET (Constitutional)  : {self.config.target_parameters:>12,} parameters")

        diff = grand_total - self.config.target_parameters
        diff_pct = abs(diff) / self.config.target_parameters * 100

        if diff > 0:
            print(f"  OVER TARGET              : {diff:>12,} (+{diff_pct:.1f}%)")
        elif diff < 0:
            print(f"  UNDER TARGET             : {abs(diff):>12,} (-{diff_pct:.1f}%)")
        else:
            print(f"  ✅ EXACT TARGET MATCH")

        print("=" * 80)

        # Constitutional compliance check
        if diff_pct <= 5.0:
            print(f"✅ Constitutional compliance: Within 5% of target")
        else:
            print(f"⚠️  Need further optimization: {diff_pct:.1f}% from target")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("B3 Optimized Model - Parameter Count Test")
    print("=" * 80)

    # Create optimized config
    config = B3OptimizedConfig()

    # Build optimized model
    model = B3OptimizedIntegrated(config)

    # Test forward pass
    print("\n" + "=" * 80)
    print("Testing Forward Pass")
    print("=" * 80)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    print(f"✅ Model moved to {device}")

    # Create dummy input
    batch_size = 2
    seq_length = 32
    input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_length)).to(device)

    print(f"✅ Input created: {input_ids.shape}")

    # Forward pass (simplified - just encoders for now)
    with torch.no_grad():
        # Text encoding
        text_embeds, _ = model.text_encoder(input_ids)
        print(f"✅ Text encoded: {text_embeds.shape}")

        # Add batch dimension if needed for fusion
        if len(text_embeds.shape) == 2:
            text_embeds = text_embeds.unsqueeze(0)  # (seq, d_model) -> (1, seq, d_model)

        # Fusion
        fused_embeds, modality_info = model.multimodal_fusion(text_embeds=text_embeds)
        print(f"✅ Fusion complete: {fused_embeds.shape}")

        # MoE routing
        expert_weights, expert_indices, router_aux = model.moe_router(fused_embeds)
        print(f"✅ MoE routing: {expert_weights.shape}, load_balance={router_aux['load_balancing_loss']:.4f}")

        # Output projection
        logits = model.output_projection(model.output_layer_norm(fused_embeds))
        print(f"✅ Output logits: {logits.shape}")

    # Memory report
    if torch.cuda.is_available():
        print("\n" + "=" * 80)
        print("Memory Report")
        print("=" * 80)
        allocated = torch.cuda.memory_allocated() / 1024**2
        reserved = torch.cuda.memory_reserved() / 1024**2
        print(f"GPU allocated: {allocated:.1f} MB")
        print(f"GPU reserved: {reserved:.1f} MB")
        print(f"Target inference: {config.target_vram_inference_mb} MB")

        if allocated < config.target_vram_inference_mb:
            print(f"✅ Memory target MET ({allocated:.1f} < {config.target_vram_inference_mb})")
        else:
            print(f"⚠️  Over memory target ({allocated:.1f} > {config.target_vram_inference_mb})")

    print("\n" + "=" * 80)
    print("✅ Optimized Model Test Complete")
    print("=" * 80)