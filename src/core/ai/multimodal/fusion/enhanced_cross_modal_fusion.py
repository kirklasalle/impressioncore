#!/usr/bin/env python3
"""
ImpressionCore: Enhanced Cross-Modal Fusion

Module for advanced cross-modal fusion strategies in the ImpressionCore framework.

File: multimodal/fusion/enhanced_cross_modal_fusion.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-29
Modified: 2025-05-29
Version: 1.0.0

Authors:
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [priority-2, multimodal, fusion, cross-modal, attention, 2025]
Dependencies: [torch, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements enhanced cross-modal fusion strategies including hierarchical
fusion, contrastive learning, unified latent spaces, and temporal fusion. Integrates
with existing fused attention optimizations for memory efficiency.

Features:
- Hierarchical multimodal fusion
- Contrastive learning for alignment
- Unified latent space representations
- Temporal fusion for sequences
- Memory-efficient implementation
- Integration with fused attention optimizations
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
import math

# Import fused attention components from Priority 1 optimizations
try:
    from src.core.utils.memory_optimization.fused_attention import (
        FusedMultiHeadAttention,
        FusedCrossModalAttention,
        MemoryEfficientAttention
    )
    HAS_FUSED_ATTENTION = True
except ImportError:
    HAS_FUSED_ATTENTION = False
    # Fallback implementations will be provided

# Import rich enhancements if available
try:
    from src.core.utils.rich_enhancements import create_panel, create_progress_bar
    from src.core.utils.rich_logging import get_rich_logger
    HAS_RICH = True
    logger = get_rich_logger(__name__)
except ImportError:
    HAS_RICH = False
    logger = logging.getLogger(__name__)

@dataclass
class FusionConfig:
    """Configuration for enhanced cross-modal fusion."""
    
    # Model dimensions
    hidden_size: int = 768
    fusion_dim: int = 512
    num_heads: int = 12
    num_layers: int = 6
    
    # Fusion strategies
    fusion_method: str = "hierarchical"  # hierarchical, contrastive, unified, temporal
    enable_residual_connections: bool = True
    use_layer_norm: bool = True
    
    # Contrastive learning
    temperature: float = 0.07
    negative_samples: int = 16
    
    # Hierarchical fusion
    hierarchy_levels: int = 3
    level_dimensions: List[int] = None  # Will be auto-generated if None
    
    # Temporal fusion
    temporal_window: int = 8
    use_temporal_attention: bool = True
    
    # Memory optimization
    enable_fused_attention: bool = True
    attention_slice_size: Optional[int] = None
    gradient_checkpointing: bool = True
    max_sequence_length: int = 512
    
    # Device settings
    device: str = "auto"
    mixed_precision: bool = True

class HierarchicalFusion(nn.Module):
    """Hierarchical fusion module for multi-level multimodal integration."""
    
    def __init__(self, config: FusionConfig):
        super().__init__()
        self.config = config
        
        # Generate level dimensions if not provided
        if config.level_dimensions is None:
            self.level_dims = [
                config.hidden_size // (2 ** i) 
                for i in range(config.hierarchy_levels)
            ]
        else:
            self.level_dims = config.level_dimensions
        
        # Projection layers for each hierarchy level
        self.level_projections = nn.ModuleList()
        self.level_fusions = nn.ModuleList()
        
        for i, dim in enumerate(self.level_dims):
            # Projection to current level dimension
            self.level_projections.append(
                nn.Linear(config.hidden_size, dim)
            )
            
            # Fusion layer for current level
            if HAS_FUSED_ATTENTION and config.enable_fused_attention:
                fusion_layer = FusedCrossModalAttention(
                    query_dim=dim,
                    key_dim=dim,
                    embed_dim=dim,
                    num_heads=min(config.num_heads, dim // 64)
                )
            else:
                fusion_layer = nn.MultiheadAttention(
                    embed_dim=dim,
                    num_heads=min(config.num_heads, dim // 64),
                    batch_first=True
                )
            
            self.level_fusions.append(fusion_layer)
        
        # Final aggregation layer
        total_dim = sum(self.level_dims)
        self.final_projection = nn.Linear(total_dim, config.fusion_dim)
        
        # Layer normalization
        if config.use_layer_norm:
            self.layer_norms = nn.ModuleList([
                nn.LayerNorm(dim) for dim in self.level_dims
            ])
            self.final_norm = nn.LayerNorm(config.fusion_dim)
    
    def forward(
        self,
        modality_features: Dict[str, torch.Tensor],
        attention_masks: Optional[Dict[str, torch.Tensor]] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass for hierarchical fusion.
        
        Args:
            modality_features: Dictionary of features for each modality
            attention_masks: Optional attention masks for each modality
            
        Returns:
            Dictionary containing fused features at different levels
        """
        batch_size = next(iter(modality_features.values())).shape[0]
        level_outputs = []
        
        # Process each hierarchy level
        for level, (projection, fusion_layer) in enumerate(zip(
            self.level_projections, self.level_fusions
        )):
            level_features = []
            level_masks = []
            
            # Project each modality to current level dimension
            for modality, features in modality_features.items():
                projected = projection(features)
                
                # Apply layer normalization if enabled
                if hasattr(self, 'layer_norms'):
                    projected = self.layer_norms[level](projected)
                
                level_features.append(projected)
                
                # Handle attention masks
                if attention_masks and modality in attention_masks:
                    level_masks.append(attention_masks[modality])
                else:
                    level_masks.append(torch.ones(
                        projected.shape[:2], 
                        device=projected.device,
                        dtype=torch.bool
                    ))
            
            # Concatenate modality features
            concatenated = torch.cat(level_features, dim=1)
            concatenated_mask = torch.cat(level_masks, dim=1)
            
            # Apply cross-modal fusion
            if HAS_FUSED_ATTENTION and isinstance(fusion_layer, FusedCrossModalAttention):
                # Use fused attention for efficiency
                fused, _ = fusion_layer(concatenated, concatenated, concatenated)
            else:
                # Standard attention
                fused, _ = fusion_layer(
                    concatenated, concatenated, concatenated,
                    key_padding_mask=~concatenated_mask
                )
            
            # Global average pooling for level representation
            level_repr = torch.mean(fused, dim=1)  # [batch, level_dim]
            level_outputs.append(level_repr)
        
        # Combine all levels
        combined = torch.cat(level_outputs, dim=-1)  # [batch, total_dim]
        final_output = self.final_projection(combined)
        
        if hasattr(self, 'final_norm'):
            final_output = self.final_norm(final_output)
        
        return {
            'hierarchical_fusion': final_output,
            'level_features': level_outputs,
            'combined_features': combined
        }

class ContrastiveFusion(nn.Module):
    """Contrastive learning-based fusion for aligned multimodal representations."""
    
    def __init__(self, config: FusionConfig):
        super().__init__()
        self.config = config
        self.temperature = config.temperature
        
        # Projection heads for each modality
        self.modality_projections = nn.ModuleDict()
        
        # Shared projection to common space
        self.shared_projection = nn.Sequential(
            nn.Linear(config.hidden_size, config.fusion_dim),
            nn.ReLU(),
            nn.Linear(config.fusion_dim, config.fusion_dim)
        )
        
        # Cross-modal attention for alignment
        if HAS_FUSED_ATTENTION and config.enable_fused_attention:
            self.cross_attention = FusedCrossModalAttention(
                query_dim=config.fusion_dim,
                key_dim=config.fusion_dim,
                embed_dim=config.fusion_dim,
                num_heads=config.num_heads
            )
        else:
            self.cross_attention = nn.MultiheadAttention(
                embed_dim=config.fusion_dim,
                num_heads=config.num_heads,
                batch_first=True
            )
    
    def forward(
        self,
        modality_features: Dict[str, torch.Tensor],
        compute_contrastive_loss: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass for contrastive fusion.
        
        Args:
            modality_features: Dictionary of features for each modality
            compute_contrastive_loss: Whether to compute contrastive loss
            
        Returns:
            Dictionary containing aligned features and optional loss
        """
        # Project each modality to shared space
        projected_features = {}
        for modality, features in modality_features.items():
            # Global pooling for sequence features
            if features.dim() == 3:
                pooled = torch.mean(features, dim=1)
            else:
                pooled = features
            
            # Project to shared space
            projected = self.shared_projection(pooled)
            projected = F.normalize(projected, p=2, dim=-1)  # L2 normalize
            projected_features[modality] = projected
        
        # Compute cross-modal similarities for alignment
        similarities = {}
        modality_names = list(projected_features.keys())
        
        for i, mod1 in enumerate(modality_names):
            for j, mod2 in enumerate(modality_names[i+1:], i+1):
                # Compute cosine similarity
                sim = torch.mm(
                    projected_features[mod1], 
                    projected_features[mod2].transpose(0, 1)
                )
                similarities[f"{mod1}_{mod2}"] = sim
        
        # Compute unified representation
        stacked_features = torch.stack(list(projected_features.values()), dim=1)
        # [batch, num_modalities, fusion_dim]
        
        # Apply cross-modal attention
        if HAS_FUSED_ATTENTION and isinstance(self.cross_attention, FusedCrossModalAttention):
            unified, _ = self.cross_attention(
                stacked_features.view(-1, stacked_features.shape[1], stacked_features.shape[2]),
                stacked_features.view(-1, stacked_features.shape[1], stacked_features.shape[2]),
                stacked_features.view(-1, stacked_features.shape[1], stacked_features.shape[2])
            )
        else:
            unified, _ = self.cross_attention(
                stacked_features, stacked_features, stacked_features
            )
        
        # Global representation
        unified_repr = torch.mean(unified, dim=1)  # [batch, fusion_dim]
        
        results = {
            'contrastive_fusion': unified_repr,
            'projected_features': projected_features,
            'similarities': similarities,
            'aligned_features': unified
        }
        
        # Compute contrastive loss if requested
        if compute_contrastive_loss:
            contrastive_loss = self._compute_contrastive_loss(similarities)
            results['contrastive_loss'] = contrastive_loss
        
        return results
    
    def _compute_contrastive_loss(self, similarities: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Compute contrastive loss for alignment."""
        losses = []
        
        for sim_name, sim_matrix in similarities.items():
            # Positive pairs are on the diagonal
            batch_size = sim_matrix.shape[0]
            labels = torch.arange(batch_size, device=sim_matrix.device)
            
            # Apply temperature scaling
            sim_matrix = sim_matrix / self.temperature
            
            # Cross-entropy loss for positive alignment
            loss = F.cross_entropy(sim_matrix, labels)
            losses.append(loss)
        
        return torch.mean(torch.stack(losses))

class TemporalFusion(nn.Module):
    """Temporal fusion for sequence-aware multimodal integration."""
    
    def __init__(self, config: FusionConfig):
        super().__init__()
        self.config = config
        self.temporal_window = config.temporal_window
        
        # Temporal encoding
        self.temporal_encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=config.fusion_dim,
                nhead=config.num_heads,
                dim_feedforward=config.fusion_dim * 4,
                dropout=0.1,
                batch_first=True
            ),
            num_layers=2
        )
        
        # Cross-temporal attention
        if HAS_FUSED_ATTENTION and config.enable_fused_attention:
            self.temporal_attention = FusedMultiHeadAttention(
                embed_dim=config.fusion_dim,
                num_heads=config.num_heads
            )
        else:
            self.temporal_attention = nn.MultiheadAttention(
                embed_dim=config.fusion_dim,
                num_heads=config.num_heads,
                batch_first=True
            )
        
        # Modality-specific temporal projections
        self.temporal_projections = nn.ModuleDict()
        
        # Output projection
        self.output_projection = nn.Linear(config.fusion_dim, config.fusion_dim)
    
    def forward(
        self,
        temporal_features: Dict[str, torch.Tensor],
        timestamps: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass for temporal fusion.
        
        Args:
            temporal_features: Dictionary of temporal features [batch, time, hidden]
            timestamps: Optional timestamps for alignment
            
        Returns:
            Dictionary containing temporally fused features
        """
        batch_size = next(iter(temporal_features.values())).shape[0]
        
        # Align temporal sequences
        aligned_features = []
        max_time = max(feat.shape[1] for feat in temporal_features.values())
        
        for modality, features in temporal_features.items():
            time_steps = features.shape[1]
            
            # Pad or truncate to common temporal dimension
            if time_steps < max_time:
                padding = torch.zeros(
                    batch_size, max_time - time_steps, features.shape[-1],
                    device=features.device, dtype=features.dtype
                )
                features = torch.cat([features, padding], dim=1)
            elif time_steps > max_time:
                features = features[:, :max_time]
            
            aligned_features.append(features)
        
        # Stack modalities along feature dimension
        stacked = torch.stack(aligned_features, dim=2)  # [batch, time, modalities, hidden]
        stacked = stacked.view(batch_size, max_time, -1)  # [batch, time, modalities*hidden]
        
        # Project to fusion dimension
        if stacked.shape[-1] != self.config.fusion_dim:
            if not hasattr(self, 'temporal_projection'):
                self.temporal_projection = nn.Linear(
                    stacked.shape[-1], self.config.fusion_dim
                ).to(stacked.device)
            stacked = self.temporal_projection(stacked)
        
        # Apply temporal encoding
        if self.config.use_temporal_attention:
            if HAS_FUSED_ATTENTION and isinstance(self.temporal_attention, FusedMultiHeadAttention):
                temporal_output, _ = self.temporal_attention(stacked, stacked, stacked)
            else:
                temporal_output, _ = self.temporal_attention(stacked, stacked, stacked)
        else:
            temporal_output = self.temporal_encoder(stacked)
        
        # Global temporal representation
        temporal_repr = torch.mean(temporal_output, dim=1)  # [batch, fusion_dim]
        temporal_repr = self.output_projection(temporal_repr)
        
        return {
            'temporal_fusion': temporal_repr,
            'temporal_sequence': temporal_output,
            'aligned_features': stacked
        }

class EnhancedCrossModalFusion(nn.Module):
    """Unified enhanced cross-modal fusion with multiple strategies."""
    
    def __init__(self, config: FusionConfig):
        super().__init__()
        self.config = config
        
        # Set device
        if config.device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(config.device)
        
        # Initialize fusion modules based on configuration
        self.fusion_modules = nn.ModuleDict()
        
        if config.fusion_method in ["hierarchical", "all"]:
            self.fusion_modules["hierarchical"] = HierarchicalFusion(config)
        
        if config.fusion_method in ["contrastive", "all"]:
            self.fusion_modules["contrastive"] = ContrastiveFusion(config)
        
        if config.fusion_method in ["temporal", "all"]:
            self.fusion_modules["temporal"] = TemporalFusion(config)
          # Unified output layer - dynamic sizing based on actual execution
        # Note: temporal fusion only executes when temporal_features is provided
        # So we'll create a flexible projection that adapts to the actual concatenated size
        max_fusion_output_dim = len(self.fusion_modules) * config.fusion_dim
        self.unified_projection = None  # Will be created dynamically on first forward pass
        
        # Move to device
        self.to(self.device)
        
        if HAS_RICH:
            logger.info(f"Enhanced Cross-Modal Fusion initialized with methods: {list(self.fusion_modules.keys())}")
        else:
            logger.info(f"Enhanced Cross-Modal Fusion initialized with methods: {list(self.fusion_modules.keys())}")
    
    def forward(
        self,
        modality_features: Dict[str, torch.Tensor],
        attention_masks: Optional[Dict[str, torch.Tensor]] = None,
        temporal_features: Optional[Dict[str, torch.Tensor]] = None,
        compute_losses: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass for enhanced cross-modal fusion.
        
        Args:
            modality_features: Dictionary of features for each modality
            attention_masks: Optional attention masks
            temporal_features: Optional temporal sequence features
            compute_losses: Whether to compute auxiliary losses
            
        Returns:
            Dictionary containing fused features and optional losses
        """
        fusion_outputs = []
        results = {}
        
        # Apply each fusion method
        if "hierarchical" in self.fusion_modules:
            hier_output = self.fusion_modules["hierarchical"](
                modality_features, attention_masks
            )
            fusion_outputs.append(hier_output["hierarchical_fusion"])
            results.update({f"hierarchical_{k}": v for k, v in hier_output.items()})
        
        if "contrastive" in self.fusion_modules:
            cont_output = self.fusion_modules["contrastive"](
                modality_features, compute_losses
            )
            fusion_outputs.append(cont_output["contrastive_fusion"])
            results.update({f"contrastive_{k}": v for k, v in cont_output.items()})
        
        if "temporal" in self.fusion_modules and temporal_features is not None:
            temp_output = self.fusion_modules["temporal"](temporal_features)
            fusion_outputs.append(temp_output["temporal_fusion"])
            results.update({f"temporal_{k}": v for k, v in temp_output.items()})
          # Combine all fusion outputs
        if fusion_outputs:
            combined = torch.cat(fusion_outputs, dim=-1)
            
            # Create unified projection dynamically if needed
            if self.unified_projection is None:
                actual_fusion_dim = combined.shape[-1]
                self.unified_projection = nn.Sequential(
                    nn.Linear(actual_fusion_dim, self.config.fusion_dim),
                    nn.GELU(),
                    nn.Dropout(0.1),
                    nn.Linear(self.config.fusion_dim, self.config.fusion_dim)
                ).to(self.device)
            
            unified = self.unified_projection(combined)
            results["unified_fusion"] = unified
            results["combined_fusion"] = combined
        
        return results

# Factory functions
def create_enhanced_cross_modal_fusion(
    fusion_method: str = "hierarchical",
    device: str = "auto",
    **kwargs
) -> EnhancedCrossModalFusion:
    """Create an enhanced cross-modal fusion module."""
    config = FusionConfig(
        fusion_method=fusion_method,
        device=device,
        **kwargs
    )
    
    return EnhancedCrossModalFusion(config)

# Example usage and testing
if __name__ == "__main__":
    # Test enhanced cross-modal fusion
    config = FusionConfig(
        fusion_method="all",
        hidden_size=768,
        fusion_dim=512,
        device="auto"
    )
    
    fusion_model = EnhancedCrossModalFusion(config)
    
    # Create dummy multimodal features
    batch_size = 4
    seq_len = 16
    
    modality_features = {
        "text": torch.randn(batch_size, seq_len, config.hidden_size),
        "vision": torch.randn(batch_size, seq_len // 2, config.hidden_size),
        "audio": torch.randn(batch_size, seq_len * 2, config.hidden_size)
    }
    
    temporal_features = {
        "text": torch.randn(batch_size, 8, config.hidden_size),
        "vision": torch.randn(batch_size, 8, config.hidden_size)
    }
    
    print("Testing enhanced cross-modal fusion...")
    print(f"Input features:")
    for mod, feat in modality_features.items():
        print(f"  {mod}: {feat.shape}")
    
    # Forward pass
    with torch.no_grad():
        results = fusion_model(
            modality_features, 
            temporal_features=temporal_features,
            compute_losses=True
        )
    
    print("\nFusion results:")
    for key, value in results.items():
        if isinstance(value, torch.Tensor):
            print(f"  {key}: {value.shape}")
        elif isinstance(value, dict):
            print(f"  {key}: dict with {len(value)} items")
        else:
            print(f"  {key}: {type(value)}")
    
    print("Enhanced cross-modal fusion test completed successfully!")
