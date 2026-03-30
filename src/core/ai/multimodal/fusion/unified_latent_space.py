#!/usr/bin/env python3
"""
ImpressionCore: Unified Latent Space for Multimodal Fusion

Module for creating unified latent space representations across multiple modalities.

File: multimodal/fusion/unified_latent_space.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-29
Modified: 2025-05-29
Version: 1.0.0

Authors:
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [priority-2, multimodal, fusion, latent-space, unified, 2025]
Dependencies: [torch, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements unified latent space representations for multimodal data,
enabling seamless fusion and cross-modal understanding. Integrates with Priority 1
memory optimizations for efficient processing on constrained hardware.

Features:
- Unified latent space mapping
- Cross-modal embedding alignment
- Modality-agnostic representations
- Memory-efficient implementation
- Integration with fused attention
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
import math

# Import memory optimization components
try:
    from src.core.utils.memory_optimization.fused_attention import (
        FusedMultiHeadAttention,
        FusedCrossModalAttention,
        HAS_FUSED_ATTENTION
    )
except ImportError:
    HAS_FUSED_ATTENTION = False
    print("Warning: Fused attention not available, using standard attention")

# Rich logging if available
try:
    from src.core.utils.rich_logging import get_rich_logger
    HAS_RICH = True
    logger = get_rich_logger(__name__)
except ImportError:
    HAS_RICH = False
    logger = logging.getLogger(__name__)

@dataclass
class UnifiedLatentConfig:
    """Configuration for unified latent space."""
    
    # Model dimensions
    latent_dim: int = 512
    hidden_size: int = 768
    intermediate_dim: int = 1024
    
    # Architecture settings
    num_encoder_layers: int = 3
    num_heads: int = 8
    dropout_rate: float = 0.1
    use_layer_norm: bool = True
    
    # Modality settings
    modality_dimensions: Dict[str, int] = None  # Auto-inferred if None
    modality_weights: Dict[str, float] = None   # Equal weights if None
    
    # Fusion settings
    fusion_strategy: str = "learned_attention"  # "mean", "max", "learned_attention"
    enable_residual_connections: bool = True
    enable_gate_mechanism: bool = True
    
    # Memory optimization
    enable_fused_attention: bool = True
    use_gradient_checkpointing: bool = False
    mixed_precision: bool = True
    
    # Training settings
    temperature: float = 0.07
    contrastive_weight: float = 0.1
    reconstruction_weight: float = 0.05
    
    # Device settings
    device: str = "auto"

class ModalityEncoder(nn.Module):
    """Encoder for mapping modality-specific features to unified latent space."""
    
    def __init__(
        self,
        input_dim: int,
        latent_dim: int,
        config: UnifiedLatentConfig
    ):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.config = config
        
        # Multi-layer projection with residual connections
        self.layers = nn.ModuleList()
        dims = [input_dim, config.intermediate_dim, latent_dim]
        
        for i in range(len(dims) - 1):
            layer = nn.Sequential(
                nn.Linear(dims[i], dims[i + 1]),
                nn.LayerNorm(dims[i + 1]) if config.use_layer_norm else nn.Identity(),
                nn.GELU(),
                nn.Dropout(config.dropout_rate)
            )
            self.layers.append(layer)
        
        # Final projection to latent space
        self.final_projection = nn.Linear(latent_dim, latent_dim)
        
        # Gate mechanism for adaptive encoding
        if config.enable_gate_mechanism:
            self.gate = nn.Sequential(                nn.Linear(input_dim, latent_dim),
                nn.Sigmoid()
            )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Encode modality-specific features to unified latent space.
        
        Args:
            x: Input features [batch, seq_len, input_dim] or [batch, input_dim]
            
        Returns:
            Latent representations [batch, seq_len, latent_dim] or [batch, latent_dim]
        """
        original_shape = x.shape
        original_input = x  # Store original tensor for gate computation
        
        # Handle sequence inputs
        if x.dim() == 3:
            batch_size, seq_len, _ = x.shape
            x = x.view(-1, x.shape[-1])  # Flatten for processing
        else:
            batch_size, seq_len = x.shape[0], 1
        
        # Forward through layers with residual connections
        residual = x
        for i, layer in enumerate(self.layers):
            x = layer(x)
            
            # Residual connection if dimensions match
            if (self.config.enable_residual_connections and 
                i > 0 and residual.shape[-1] == x.shape[-1]):
                x = x + residual
            residual = x
        
        # Final projection
        latent = self.final_projection(x)
        
        # Apply gate mechanism if enabled
        if hasattr(self, 'gate'):
            # Use original input for gate computation
            if len(original_shape) == 3:
                gate_input = original_input.view(-1, original_input.shape[-1])
            else:
                gate_input = original_input
            gate_weights = self.gate(gate_input)
            latent = latent * gate_weights
        
        # Restore original shape
        if len(original_shape) == 3:
            latent = latent.view(batch_size, seq_len, self.latent_dim)
        
        # L2 normalize for stable training
        latent = F.normalize(latent, p=2, dim=-1)
        
        return latent

class ModalityDecoder(nn.Module):
    """Decoder for reconstructing modality-specific features from latent space."""
    
    def __init__(
        self,
        latent_dim: int,
        output_dim: int,
        config: UnifiedLatentConfig
    ):
        super().__init__()
        self.latent_dim = latent_dim
        self.output_dim = output_dim
        self.config = config
        
        # Multi-layer reconstruction
        dims = [latent_dim, config.intermediate_dim, output_dim]
        self.layers = nn.ModuleList()
        
        for i in range(len(dims) - 1):
            layer = nn.Sequential(
                nn.Linear(dims[i], dims[i + 1]),
                nn.LayerNorm(dims[i + 1]) if config.use_layer_norm and i < len(dims) - 2 else nn.Identity(),
                nn.GELU() if i < len(dims) - 2 else nn.Identity(),
                nn.Dropout(config.dropout_rate) if i < len(dims) - 2 else nn.Identity()
            )
            self.layers.append(layer)
    
    def forward(self, latent: torch.Tensor) -> torch.Tensor:
        """
        Decode latent representations back to modality-specific features.
        
        Args:
            latent: Latent representations [batch, seq_len, latent_dim] or [batch, latent_dim]
            
        Returns:
            Reconstructed features [batch, seq_len, output_dim] or [batch, output_dim]
        """
        original_shape = latent.shape
        
        # Handle sequence inputs
        if latent.dim() == 3:
            batch_size, seq_len, _ = latent.shape
            latent = latent.view(-1, latent.shape[-1])
        else:
            batch_size, seq_len = latent.shape[0], 1
        
        # Forward through layers
        x = latent
        for layer in self.layers:
            x = layer(x)
        
        # Restore original shape
        if len(original_shape) == 3:
            x = x.view(batch_size, seq_len, self.output_dim)
        
        return x

class UnifiedLatentSpace(nn.Module):
    """Unified latent space for multimodal representations."""
    
    def __init__(self, config: UnifiedLatentConfig):
        super().__init__()
        self.config = config
        
        # Set device
        if config.device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(config.device)
        
        # Modality encoders and decoders
        self.encoders = nn.ModuleDict()
        self.decoders = nn.ModuleDict()
        
        # Will be populated when first called with modality features
        self.modality_dims = config.modality_dimensions or {}
        
        # Cross-modal attention for fusion
        if HAS_FUSED_ATTENTION and config.enable_fused_attention:
            self.cross_modal_attention = FusedCrossModalAttention(
                query_dim=config.latent_dim,
                key_dim=config.latent_dim,
                embed_dim=config.latent_dim,
                num_heads=config.num_heads
            )
        else:
            self.cross_modal_attention = nn.MultiheadAttention(
                embed_dim=config.latent_dim,
                num_heads=config.num_heads,
                batch_first=True
            )
        
        # Learned fusion weights
        if config.fusion_strategy == "learned_attention":
            self.fusion_attention = nn.MultiheadAttention(
                embed_dim=config.latent_dim,
                num_heads=1,
                batch_first=True
            )
        
        # Unified representation projector
        self.unified_projector = nn.Sequential(
            nn.Linear(config.latent_dim, config.latent_dim),
            nn.LayerNorm(config.latent_dim),
            nn.GELU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.latent_dim, config.latent_dim)
        )
        
        # Move to device
        self.to(self.device)
        
        if HAS_RICH:
            logger.info(f"UnifiedLatentSpace initialized with latent_dim={config.latent_dim}")
        else:
            logger.info(f"UnifiedLatentSpace initialized with latent_dim={config.latent_dim}")
    
    def _ensure_modality_encoders(self, modality_features: Dict[str, torch.Tensor]):
        """Ensure encoders and decoders exist for all modalities."""
        for modality, features in modality_features.items():
            input_dim = features.shape[-1]
            
            if modality not in self.encoders:
                # Create encoder
                encoder = ModalityEncoder(
                    input_dim=input_dim,
                    latent_dim=self.config.latent_dim,
                    config=self.config
                ).to(self.device)
                
                # Create decoder
                decoder = ModalityDecoder(
                    latent_dim=self.config.latent_dim,
                    output_dim=input_dim,
                    config=self.config
                ).to(self.device)
                
                self.encoders[modality] = encoder
                self.decoders[modality] = decoder
                self.modality_dims[modality] = input_dim
    
    def encode_modalities(
        self,
        modality_features: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """
        Encode all modalities to unified latent space.
        
        Args:
            modality_features: Dictionary of modality features
            
        Returns:
            Dictionary of latent representations for each modality
        """
        # Ensure encoders exist
        self._ensure_modality_encoders(modality_features)
        
        latent_features = {}
        for modality, features in modality_features.items():
            # Move to device
            features = features.to(self.device)
            
            # Encode to latent space
            latent = self.encoders[modality](features)
            latent_features[modality] = latent
        
        return latent_features
    
    def fuse_latent_representations(
        self,
        latent_features: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Fuse latent representations into unified representation.
        
        Args:
            latent_features: Dictionary of latent features for each modality
            
        Returns:
            Unified latent representation
        """
        if self.config.fusion_strategy == "mean":
            # Simple averaging
            stacked = torch.stack(list(latent_features.values()), dim=0)
            return torch.mean(stacked, dim=0)
        
        elif self.config.fusion_strategy == "max":
            # Element-wise maximum
            stacked = torch.stack(list(latent_features.values()), dim=0)
            return torch.max(stacked, dim=0)[0]
        
        elif self.config.fusion_strategy == "learned_attention":
            # Learned attention fusion
            modality_names = list(latent_features.keys())
            
            # Handle different sequence lengths
            max_seq_len = max(feat.shape[1] if feat.dim() == 3 else 1 
                             for feat in latent_features.values())
            
            aligned_features = []
            for modality in modality_names:
                feat = latent_features[modality]
                
                # Handle sequence dimension
                if feat.dim() == 2:
                    feat = feat.unsqueeze(1)  # Add sequence dimension
                
                # Align sequence length
                current_len = feat.shape[1]
                if current_len < max_seq_len:
                    padding = torch.zeros(
                        feat.shape[0], max_seq_len - current_len, feat.shape[2],
                        device=feat.device, dtype=feat.dtype
                    )
                    feat = torch.cat([feat, padding], dim=1)
                elif current_len > max_seq_len:
                    feat = feat[:, :max_seq_len]
                
                aligned_features.append(feat)
            
            # Stack modalities
            stacked = torch.stack(aligned_features, dim=1)  # [batch, modalities, seq, latent]
            batch_size, num_modalities, seq_len, latent_dim = stacked.shape
            
            # Reshape for attention
            stacked = stacked.view(batch_size, num_modalities * seq_len, latent_dim)
            
            # Apply cross-modal attention
            if HAS_FUSED_ATTENTION and isinstance(self.cross_modal_attention, FusedCrossModalAttention):
                fused, attention_weights = self.cross_modal_attention(
                    stacked, stacked, stacked
                )
            else:
                fused, attention_weights = self.cross_modal_attention(
                    stacked, stacked, stacked
                )
            
            # Global pooling for unified representation
            unified = torch.mean(fused, dim=1)  # [batch, latent_dim]
            
            return unified
        
        else:
            raise ValueError(f"Unknown fusion strategy: {self.config.fusion_strategy}")
    
    def decode_to_modalities(
        self,
        unified_latent: torch.Tensor,
        target_modalities: Optional[List[str]] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Decode unified latent representation back to modality-specific features.
        
        Args:
            unified_latent: Unified latent representation
            target_modalities: List of modalities to decode to (all if None)
            
        Returns:
            Dictionary of reconstructed modality features
        """
        if target_modalities is None:
            target_modalities = list(self.decoders.keys())
        
        reconstructed = {}
        for modality in target_modalities:
            if modality in self.decoders:
                reconstructed[modality] = self.decoders[modality](unified_latent)
        
        return reconstructed
    
    def forward(
        self,
        modality_features: Dict[str, torch.Tensor],
        return_reconstructions: bool = False,
        return_latent_features: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass for unified latent space processing.
        
        Args:
            modality_features: Dictionary of modality features
            return_reconstructions: Whether to return reconstructed features
            return_latent_features: Whether to return individual latent features
            
        Returns:
            Dictionary containing unified representation and optional outputs
        """
        # Encode modalities to latent space
        latent_features = self.encode_modalities(modality_features)
        
        # Fuse latent representations
        unified_latent = self.fuse_latent_representations(latent_features)
        
        # Apply unified projector
        unified_representation = self.unified_projector(unified_latent)
        
        results = {
            'unified_latent': unified_representation,
            'raw_unified': unified_latent
        }
        
        if return_latent_features:
            results['modality_latents'] = latent_features
        
        if return_reconstructions:
            reconstructions = self.decode_to_modalities(unified_representation)
            results['reconstructions'] = reconstructions
        
        return results
    
    def compute_contrastive_loss(
        self,
        latent_features: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """Compute contrastive loss for cross-modal alignment."""
        modalities = list(latent_features.keys())
        if len(modalities) < 2:
            return torch.tensor(0.0, device=self.device)
        
        losses = []
        for i, mod1 in enumerate(modalities):
            for mod2 in modalities[i+1:]:
                # Get features
                feat1 = latent_features[mod1]
                feat2 = latent_features[mod2]
                
                # Global pooling if sequence features
                if feat1.dim() == 3:
                    feat1 = torch.mean(feat1, dim=1)
                if feat2.dim() == 3:
                    feat2 = torch.mean(feat2, dim=1)
                
                # Compute cosine similarity
                similarities = torch.mm(feat1, feat2.transpose(0, 1))
                similarities = similarities / self.config.temperature
                
                # Positive pairs are on diagonal
                batch_size = similarities.shape[0]
                labels = torch.arange(batch_size, device=self.device)
                
                # Cross-entropy loss
                loss = F.cross_entropy(similarities, labels)
                losses.append(loss)
        
        return torch.mean(torch.stack(losses)) if losses else torch.tensor(0.0, device=self.device)
    
    def compute_reconstruction_loss(
        self,
        original_features: Dict[str, torch.Tensor],
        reconstructed_features: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """Compute reconstruction loss for autoencoders."""
        losses = []
        
        for modality in original_features:
            if modality in reconstructed_features:
                original = original_features[modality]
                reconstructed = reconstructed_features[modality]
                
                # MSE loss
                loss = F.mse_loss(reconstructed, original)
                losses.append(loss)
        
        return torch.mean(torch.stack(losses)) if losses else torch.tensor(0.0, device=self.device)

# Factory function
def create_unified_latent_space(
    latent_dim: int = 512,
    device: str = "auto",
    **kwargs
) -> UnifiedLatentSpace:
    """Create a unified latent space module."""
    config = UnifiedLatentConfig(
        latent_dim=latent_dim,
        device=device,
        **kwargs
    )
    
    return UnifiedLatentSpace(config)

# Example usage and testing
if __name__ == "__main__":
    # Test unified latent space
    config = UnifiedLatentConfig(
        latent_dim=256,
        hidden_size=512,
        device="auto"
    )
    
    latent_space = UnifiedLatentSpace(config)
    
    # Create dummy multimodal features
    batch_size = 4
    modality_features = {
        "text": torch.randn(batch_size, 16, 768),
        "vision": torch.randn(batch_size, 8, 512),
        "audio": torch.randn(batch_size, 32, 256)
    }
    
    print("Testing unified latent space...")
    print(f"Input features:")
    for mod, feat in modality_features.items():
        print(f"  {mod}: {feat.shape}")
    
    # Forward pass
    with torch.no_grad():
        results = latent_space(
            modality_features,
            return_reconstructions=True,
            return_latent_features=True
        )
    
    print("\nUnified latent space results:")
    for key, value in results.items():
        if isinstance(value, torch.Tensor):
            print(f"  {key}: {value.shape}")
        elif isinstance(value, dict):
            print(f"  {key}: dict with {len(value)} items")
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, torch.Tensor):
                    print(f"    {sub_key}: {sub_value.shape}")
    
    print("Unified latent space test completed successfully!")
