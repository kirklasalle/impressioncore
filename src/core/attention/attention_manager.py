#!/usr/bin/env python3
"""
ImpressionCore: Attention Manager

Module for attention manager functionality in the ImpressionCore framework.

File: modules\attention\attention_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, 2025, object-oriented]
Dependencies: [torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements attention manager functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from modules.attention.attention_manager import AttentionManager
instance = AttentionManager()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
import torch.nn as nn
from typing import Optional, Dict, Union, Tuple, List, Any
import math
import logging
import time

from src.core.attention.sparse_attention_temp import (
    LocalAttention,
    MemoryEfficientAttention, 
    # Memory optimization: Memory-critical operation
    AxialAttention,
    AttentionRouter
)

# Import new fused attention modules
from src.core.utils.memory_optimization.fused_attention import (
    FusedMultiHeadAttention,
    FusedCrossModalAttention,
    FusedExpertAttention,
    benchmark_fused_attention
)

# Set up logging
logger = logging.getLogger(__name__)

class AttentionManager(nn.Module):
    """
    Unified attention manager that dynamically selects and routes to the optimal attention 
    mechanism based on input characteristics and hardware resources.
    
    This manager is specifically designed to optimize VRAM usage on constrained hardware
    like the NVIDIA GTX 1050 Ti (4GB VRAM) while maintaining performance.
    
    The manager can:
    1. Automatically select the best attention mechanism for given inputs
    2. Monitor VRAM usage and adapt on-the-fly
    3. Cache results for similar input patterns to improve performance
    4. Track and report memory usage statistics
    # Memory optimization: Memory-critical operation
    
    Args:
        hidden_size (int): Dimension of hidden representations
        num_heads (int): Number of attention heads
        vram_target_mb (int, optional): Target VRAM usage in MB. Defaults to 3500 (for 4GB cards)
        enable_vram_monitoring (bool, optional): Whether to actively monitor VRAM. Defaults to True
        attention_preference (str, optional): Preferred attention type when multiple are viable.
            Options: "performance", "memory", "balanced". Defaults to "balanced"
            # Memory optimization: Memory-critical operation
        chunk_size (int, optional): Memory optimization chunk size for attention computations.
        # Memory optimization: Memory-critical operation
            Defaults to 64.
    """
    
    def __init__(
        self,
        hidden_size: int,
        num_heads: int = 8,
        vram_target_mb: int = 3500,  # Target 3.5GB for 4GB cards
        enable_vram_monitoring: bool = True,
        attention_preference: str = "balanced",
        chunk_size: int = 64  # Memory optimization chunk size
    ):
        """
        Initialize the AttentionManager with support for fused attention.
        
        Args:
            hidden_size: Dimension of hidden representations
            num_heads: Number of attention heads
            vram_target_mb: Target VRAM usage in MB. Defaults to 3500 (for 4GB cards)
            enable_vram_monitoring: Whether to actively monitor VRAM. Defaults to True
            attention_preference: Preferred attention type when multiple are viable.
                Options: "performance", "memory", "balanced". Defaults to "balanced"
            chunk_size: Memory optimization chunk size for attention computations.
        
        Memory Usage:
            - Memory-efficient implementation
            - Optimized for GTX 1050 Ti constraints
        """
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        # Ensure head_dim is an integer
        assert hidden_size % num_heads == 0, "hidden_size must be divisible by num_heads"
        self.head_dim = hidden_size // num_heads
        self.vram_target_mb = vram_target_mb
        self.enable_vram_monitoring = enable_vram_monitoring
        self.attention_preference = attention_preference
        
        # Performance/memory usage stats for different attention types to inform future selections
        # Memory optimization: Memory-critical operation
        self._stats = {
            "standard": {"calls": 0, "avg_time_ms": 0, "avg_memory_mb": 0},
            # Memory optimization: Memory-critical operation
            "local": {"calls": 0, "avg_time_ms": 0, "avg_memory_mb": 0},
            # Memory optimization: Memory-critical operation
            "memory_efficient": {"calls": 0, "avg_time_ms": 0, "avg_memory_mb": 0},
            # Memory optimization: Memory-critical operation
            "axial": {"calls": 0, "avg_time_ms": 0, "avg_memory_mb": 0},
            # Memory optimization: Memory-critical operation
        }
          # Initialize all attention mechanisms
        self.standard_attention = nn.MultiheadAttention(hidden_size, num_heads, batch_first=True)
        self.local_attention = LocalAttention(
            num_heads=num_heads,
            head_dim=hidden_size // num_heads,
            hidden_size=hidden_size,
            window_size=128
        )
        self.memory_efficient_attention = MemoryEfficientAttention(hidden_size, num_heads=num_heads)
        # Memory optimization: Memory-critical operation
        self.axial_attention = None  # Initialized on demand since it needs input dimensions
        
        # Initialize fused attention mechanisms for enhanced performance
        self.fused_attention = FusedMultiHeadAttention(
            hidden_size=hidden_size,
            num_heads=num_heads,
            dropout=0.1,
            use_flash_attention=True,
            chunk_size=chunk_size
        )
        
        # Initialize cross-modal fused attention (for multimodal scenarios)
        self.fused_cross_modal_attention = None  # Initialized on demand with specific modality dimensions
        
        # Initialize expert attention (for MoE scenarios)  
        self.fused_expert_attention = None  # Initialized on demand with expert configuration
        
        # Update stats to include fused attention types
        self._stats.update({
            "fused": {"calls": 0, "avg_time_ms": 0, "avg_memory_mb": 0},
            "fused_cross_modal": {"calls": 0, "avg_time_ms": 0, "avg_memory_mb": 0},
            "fused_expert": {"calls": 0, "avg_time_ms": 0, "avg_memory_mb": 0},
        })
        
        # Cache for attention selection based on input characteristics
        self._selection_cache = {}
        
        logger.info(f"AttentionManager initialized with {hidden_size} hidden size, "
                   f"{num_heads} heads, and {vram_target_mb}MB VRAM target")
                   
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        is_2d_data: bool = False,
        height: Optional[int] = None,
        width: Optional[int] = None,
        forced_attention_type: Optional[str] = None,
    ) -> torch.Tensor:
        """
        Forward pass that automatically selects the appropriate attention mechanism.
        
        Args:
            hidden_states: Input tensor of shape [batch_size, seq_len, hidden_size]
            attention_mask: Attention mask (boolean, True=keep) of shape [batch_size, seq_len]
            is_2d_data: Whether the input data has 2D structure (images, etc.)
            height: Height of 2D input (required if is_2d_data is True)
            width: Width of 2D input (required if is_2d_data is True)            forced_attention_type: Override automatic selection with specific type:
                "standard", "local", "memory_efficient", "axial",
                "fused", "fused_cross_modal", "fused_expert"
                # Memory optimization: Memory-critical operation
                
        Returns:
            torch.Tensor: Output after applying selected attention mechanism
        """
        batch_size, seq_length, hidden_dim = hidden_states.shape
        device = hidden_states.device
        # Memory optimization: Device placement for memory management
        
        # Check available VRAM if monitoring is enabled
        available_vram_mb = self._check_available_vram() if self.enable_vram_monitoring else None
        
        # Record initial memory for statistics
        # Memory optimization: Memory-critical operation
        initial_memory = self._get_current_memory_usage() if torch.cuda.is_available() else 0
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Select appropriate attention mechanism
        if forced_attention_type:
            attention_type = forced_attention_type
        else:
            attention_type = self._select_attention_mechanism(
                seq_length, is_2d_data, available_vram_mb, height, width
            )
            
        # For timing
        start_time = time.time()
        
        output = None # Initialize output
        
        # Apply the selected attention
        if attention_type == "standard":
            # Standard MultiheadAttention requires boolean key_padding_mask (True indicates masked position).
            key_padding_mask = attention_mask.logical_not() if attention_mask is not None else None
            try:
                 output = self.standard_attention(
                     hidden_states, hidden_states, hidden_states, 
                     attn_mask=None, # Standard MHA doesn't typically use additive attn_mask here
                     key_padding_mask=key_padding_mask 
                 )[0]  # Return only the attention output, not the weights
            except Exception as e:
                 logger.error(f"Error during standard attention: {e}")
                 raise # Re-raise after logging
            
        elif attention_type == "local":
            # Assuming LocalAttention handles boolean mask (True=keep) internally or needs float mask
            # Pass original boolean mask. If it errors, we need to adjust LocalAttention or convert mask here.
            try:
                output, _ = self.local_attention(hidden_states, attention_mask=attention_mask)  # Unpack tuple (output, weights)
            except Exception as e:
                 logger.error(f"Error during local attention: {e}")
                 raise
            
        elif attention_type == "memory_efficient":
        # Memory optimization: Memory-critical operation
            # Assuming MemoryEfficientAttention handles boolean mask (True=keep) internally or needs float mask
            # Memory optimization: Memory-critical operation
            # Pass original boolean mask. If it errors, we need to adjust or convert mask here.
            try:
                output, _ = self.memory_efficient_attention(hidden_states, attention_mask=attention_mask)  # Unpack tuple (output, weights)
                # Memory optimization: Memory-critical operation
            except Exception as e:
                 logger.error(f"Error during memory efficient attention: {e}")
                 # Memory optimization: Memory-critical operation
                 raise
            
        elif attention_type == "axial":
            # Initialize axial attention if it doesn't exist or dimensions changed
            if self.axial_attention is None or not (
                hasattr(self.axial_attention, 'height') and 
                self.axial_attention.height == height and 
                self.axial_attention.width == width and
                self.axial_attention.hidden_size == hidden_dim
            ):
                if height is None or width is None:
                    # Need to account for CLS token if present when calculating size
                    num_patches = seq_length -1 if seq_length > 1 else seq_length # Assume CLS if seq_len > 1
                    if num_patches <= 0:
                         raise ValueError(f"Cannot infer dimensions for seq_length {seq_length} for Axial Attention")
                    size = int(math.sqrt(num_patches))
                    if size * size != num_patches:
                         raise ValueError(f"Cannot infer square dimensions for {num_patches} patches (seq_length {seq_length})")
                    height = width = size
                
                logger.info(f"Initializing AxialAttention with h={height}, w={width}, hidden={hidden_dim}")
                try:
                    self.axial_attention = AxialAttention(hidden_dim, height, width).to(device)
                    # Memory optimization: Device placement for memory management
                except Exception as e:
                    logger.error(f"Failed to initialize AxialAttention: {e}")
                    # Fallback to standard if Axial init fails
                    key_padding_mask = attention_mask.logical_not() if attention_mask is not None else None
                    output = self.standard_attention(hidden_states, hidden_states, hidden_states, key_padding_mask=key_padding_mask)[0]
                    attention_type = "standard"  # Track as standard attention
                    attention_type = "standard" 
                    logger.warning("Axial attention initialization failed, falling back to standard attention.")

            if attention_type == "axial" and self.axial_attention is not None: # Check if Axial is still intended and initialized
                try:
                    # AxialAttention expects input shape [B, H, h, w] and operates only on spatial tokens
                    # Input hidden_states is [B, S, H] where S = h*w + 1 (CLS token) or S = h*w
                    has_cls = seq_length == (height * width + 1)
  # Check if CLS token is present
                    cls_token = hidden_states[:, 0:1, :] if has_cls else None  # Extract CLS token if present
                    patch_tokens = hidden_states[:, 1:, :] if has_cls else hidden_states  # Exclude CLS token
                    
                    if height * width != patch_tokens.shape[1]:
                        logger.error(f"Shape mismatch: height*width ({height*width}) != patch_tokens seq_len ({patch_tokens.shape[1]})")
                        key_padding_mask = attention_mask.logical_not() if attention_mask is not None else None
                        output, _ = self.standard_attention(hidden_states, hidden_states, hidden_states, key_padding_mask=key_padding_mask)
                        attention_type = "standard"
                        attention_type = "standard" 
                        logger.warning("Axial attention shape mismatch, falling back to standard attention.")
                    else:
                        # Reshape patch tokens: [B, h*w, H] -> [B, h, w, H] -> [B, H, h, w]
                        patch_tokens_spatial = patch_tokens.reshape(batch_size, height, width, hidden_dim)
                        patch_tokens_spatial = patch_tokens_spatial.permute(0, 3, 1, 2) # [B, H, h, w]
                        
                        # Apply axial attention - Assuming AxialAttention does *not* need a mask for now.
                        axial_output_spatial, _ = self.axial_attention(patch_tokens_spatial)  # Unpack tuple (output, weights)
                        
                        # Reshape output back: [B, H, h, w] -> [B, h, w, H] -> [B, h*w, H]
                        axial_output_flat = axial_output_spatial.permute(0, 2, 3, 1) # [B, h, w, H]
                        axial_output_flat = axial_output_flat.reshape(batch_size, height * width, hidden_dim)
                        
                        # Re-attach CLS token if it existed
                        if cls_token is not None:
                            output = torch.cat([cls_token, axial_output_flat], dim=1) # [B, S, H]
                        else:
                            output = axial_output_flat # [B, h*w, H]

                except Exception as e:
                    logger.error(f"Error during axial attention: {e}")
                    # Fallback to standard if Axial forward fails
                    key_padding_mask = attention_mask.logical_not() if attention_mask is not None else None
                    output = self.standard_attention(hidden_states, hidden_states, hidden_states, key_padding_mask=key_padding_mask)[0]
                    attention_type = "standard"  # Explicitly set attention type                    attention_type = "standard" 
                    logger.warning("Axial attention forward pass failed, falling back to standard attention.")

        elif attention_type == "fused":
            # Use fused multi-head attention for enhanced performance
            try:
                output = self.fused_attention(
                    hidden_states, 
                    attention_mask=attention_mask
                )
            except Exception as e:
                logger.error(f"Error during fused attention: {e}")
                # Fallback to standard attention
                key_padding_mask = attention_mask.logical_not() if attention_mask is not None else None
                output = self.standard_attention(hidden_states, hidden_states, hidden_states, key_padding_mask=key_padding_mask)[0]
                attention_type = "standard"
                logger.warning("Fused attention failed, falling back to standard attention.")
                
        elif attention_type == "fused_cross_modal":
            # Initialize cross-modal fused attention on demand
            if self.fused_cross_modal_attention is None:
                try:
                    self.fused_cross_modal_attention = FusedCrossModalAttention(
                        hidden_size=self.hidden_size,
                        num_heads=self.num_heads,
                        dropout=0.1,
                        use_flash_attention=True
                    ).to(device)
                except Exception as e:
                    logger.error(f"Failed to initialize FusedCrossModalAttention: {e}")
                    # Fallback to standard attention
                    key_padding_mask = attention_mask.logical_not() if attention_mask is not None else None
                    output = self.standard_attention(hidden_states, hidden_states, hidden_states, key_padding_mask=key_padding_mask)[0]
                    attention_type = "standard"
                    logger.warning("Cross-modal fused attention initialization failed, falling back to standard attention.")
            
            if attention_type == "fused_cross_modal" and self.fused_cross_modal_attention is not None:
                try:
                    # For cross-modal, we assume hidden_states contains concatenated modalities
                    # This is a simplified implementation - in practice, you'd want separate inputs
                    output = self.fused_cross_modal_attention(
                        query=hidden_states,
                        key=hidden_states, 
                        value=hidden_states,
                        attention_mask=attention_mask
                    )
                except Exception as e:
                    logger.error(f"Error during cross-modal fused attention: {e}")
                    # Fallback to standard attention
                    key_padding_mask = attention_mask.logical_not() if attention_mask is not None else None
                    output = self.standard_attention(hidden_states, hidden_states, hidden_states, key_padding_mask=key_padding_mask)[0]
                    attention_type = "standard"
                    logger.warning("Cross-modal fused attention forward pass failed, falling back to standard attention.")
                    
        elif attention_type == "fused_expert":
            # Initialize expert fused attention on demand
            if self.fused_expert_attention is None:
                try:
                    self.fused_expert_attention = FusedExpertAttention(
                        hidden_size=self.hidden_size,
                        num_heads=self.num_heads,
                        num_experts=4,  # Default number of experts
                        expert_capacity=32,  # Default expert capacity
                        dropout=0.1,
                        use_flash_attention=True
                    ).to(device)
                except Exception as e:
                    logger.error(f"Failed to initialize FusedExpertAttention: {e}")
                    # Fallback to standard attention
                    key_padding_mask = attention_mask.logical_not() if attention_mask is not None else None
                    output = self.standard_attention(hidden_states, hidden_states, hidden_states, key_padding_mask=key_padding_mask)[0]
                    attention_type = "standard"
                    logger.warning("Expert fused attention initialization failed, falling back to standard attention.")
            
            if attention_type == "fused_expert" and self.fused_expert_attention is not None:
                try:
                    output = self.fused_expert_attention(
                        hidden_states,
                        attention_mask=attention_mask
                    )
                except Exception as e:
                    logger.error(f"Error during expert fused attention: {e}")
                    # Fallback to standard attention
                    key_padding_mask = attention_mask.logical_not() if attention_mask is not None else None
                    output = self.standard_attention(hidden_states, hidden_states, hidden_states, key_padding_mask=key_padding_mask)[0]
                    attention_type = "standard" 
                    logger.warning("Expert fused attention forward pass failed, falling back to standard attention.")

        else: # This handles the case where the initial attention_type is invalid
             if output is None: # Check if output wasn't set by a fallback in the axial block
                 raise ValueError(f"Unknown or failed attention type: {attention_type}")
            
        # Record time and memory stats
        # Memory optimization: Memory-critical operation
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        
        # Update statistics for the used attention type
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            # Calculate memory delta for stats, peak memory is handled elsewhere if needed
            # Memory optimization: Memory-critical operation
            memory_used = self._get_current_memory_usage() - initial_memory 
            # Memory optimization: Memory-critical operation
            self._update_stats(attention_type, elapsed_ms, memory_used)
            # Memory optimization: Memory-critical operation
            
        return output
    
    def _select_attention_mechanism(
        self,
        seq_length: int,
        is_2d_data: bool = False,
        available_vram_mb: Optional[float] = None,
        height: Optional[int] = None,
        width: Optional[int] = None
    ) -> str:
        """
        Select the most appropriate attention mechanism based on input characteristics
        and available resources.
        
        Args:
            seq_length: Length of the input sequence
            is_2d_data: Whether the input has 2D structure
            available_vram_mb: Available VRAM in MB, if known
            height: Height of 2D input
            width: Width of 2D input
              Returns:
            str: Selected attention type - "standard", "local", "memory_efficient", "axial",
                 "fused", "fused_cross_modal", "fused_expert"
            # Memory optimization: Memory-critical operation
        """
        # Check cache first for similar inputs to avoid recomputation
        cache_key = (seq_length, is_2d_data, 
                     height if is_2d_data else None, 
                     width if is_2d_data else None)
                     
        if cache_key in self._selection_cache:
            return self._selection_cache[cache_key]
              # For 2D data, prefer axial attention based on benchmarks
        if is_2d_data:
            selected = "axial"
            
        # For very short sequences, use fused attention (most efficient)
        elif seq_length <= 512:
            selected = "fused"
            
        # For medium-length sequences, decide based on VRAM and preference
        elif seq_length <= 1024:
            if self.attention_preference == "performance":
                selected = "fused"  # Fused attention provides best performance
            elif self.attention_preference == "memory":
            # Memory optimization: Memory-critical operation
                selected = "local"
            else:  # balanced
                # Fused attention provides good balance of speed and memory efficiency
                selected = "fused"
                
        # For long sequences, use fused attention or axial if very long
        # Memory optimization: Memory-critical operation
        elif seq_length <= 2048:
            selected = "fused"
            # Memory optimization: Memory-critical operation
        else:
            # For very long sequences, axial attention shows best performance in benchmarks
            selected = "axial"
              # Override based on available VRAM if we're close to target limit
        if available_vram_mb is not None and available_vram_mb < self.vram_target_mb * 0.2:
            # Critical VRAM situation - use the most memory-efficient option
            # Memory optimization: Memory-critical operation
            if is_2d_data:
                selected = "axial"  # Most efficient for 2D
            else:
                # Fused attention is memory-efficient due to kernel fusion
                # Memory optimization: Memory-critical operation
                selected = "fused" if seq_length <= 1024 else "axial"
                
        # Cache the selection for future similar inputs
        self._selection_cache[cache_key] = selected
        
        logger.debug(f"Selected {selected} attention for seq_length={seq_length}, "
                    f"is_2d_data={is_2d_data}, available_vram={available_vram_mb}MB")
                    
        return selected
    
    def _check_available_vram(self) -> Optional[float]:
        """
        Check available VRAM on the current CUDA device. Returns None if unavailable.
        # Memory optimization: Device placement for memory management
        """
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            return None
            
        try:
            # Get current VRAM stats
            device = torch.cuda.current_device()
            # Memory optimization: CUDA operations for GPU acceleration
            total_memory = torch.cuda.get_device_properties(device).total_memory / (1024 ** 2)
            # Memory optimization: CUDA operations for GPU acceleration
            # Use memory_reserved as it reflects the total managed by PyTorch
            # Memory optimization: Memory-critical operation
            reserved_memory = torch.cuda.memory_reserved(device) / (1024 ** 2)
            # Memory optimization: CUDA operations for GPU acceleration
            # Allocated is what's actively used by tensors
            allocated_memory = torch.cuda.memory_allocated(device) / (1024 ** 2) 
            # Memory optimization: CUDA operations for GPU acceleration
            
            # Available is roughly total minus what PyTorch has reserved
            available = total_memory - reserved_memory
            # Memory optimization: Memory-critical operation
            
            logger.debug(f"VRAM stats: total={total_memory:.2f}MB, "
            # Memory optimization: Memory-critical operation
                        f"reserved={reserved_memory:.2f}MB, "
                        # Memory optimization: Memory-critical operation
                        f"allocated={allocated_memory:.2f}MB, "
                        # Memory optimization: Memory-critical operation
                        f"estimated_available={available:.2f}MB")
                        
            return available
        except Exception as e:
            logger.warning(f"Error checking VRAM: {e}")
            return None
    
    def _get_current_memory_usage(self) -> float:
    # Memory optimization: Memory-critical operation
        """Get current GPU memory allocated by PyTorch in MB"""
        # Memory optimization: Memory-critical operation
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            return torch.cuda.memory_allocated() / (1024 ** 2)
            # Memory optimization: CUDA operations for GPU acceleration
        return 0.0
    
    def _update_stats(self, attention_type: str, elapsed_ms: float, memory_used_mb: float) -> None:
    # Memory optimization: Memory-critical operation
        """Update running statistics for the given attention type"""
        if attention_type not in self._stats:
            # Initialize if somehow a new type appears (e.g., fallback)
            self._stats[attention_type] = {"calls": 0, "avg_time_ms": 0, "avg_memory_mb": 0} 
            # Memory optimization: Memory-critical operation
            
        stats = self._stats[attention_type]
        n = stats["calls"]
        
        # Update running averages using numerically stable method
        stats["avg_time_ms"] = stats["avg_time_ms"] + (elapsed_ms - stats["avg_time_ms"]) / (n + 1)
        stats["avg_memory_mb"] = stats["avg_memory_mb"] + (memory_used_mb - stats["avg_memory_mb"]) / (n + 1)
        # Memory optimization: Memory-critical operation
        stats["calls"] += 1
    
    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Get performance and memory usage statistics for all attention mechanisms.
        # Memory optimization: Memory-critical operation
        
        Returns:
            Dict containing stats for each attention type
        """
        return self._stats
        
    def clear_cache(self) -> None:
        """Clear the selection cache"""
        self._selection_cache.clear()
        # Memory optimization: Memory-critical operation

    def reset_stats(self) -> None:
        """Reset the performance statistics"""
        for attention_type in self._stats:
            self._stats[attention_type] = {"calls": 0, "avg_time_ms": 0, "avg_memory_mb": 0}
            # Memory optimization: Memory-critical operation\n#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src\modules\attention\attention_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [attention, modules]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.
"""
