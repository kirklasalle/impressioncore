#!/usr/bin/env python3
"""
ImpressionCore: Model Scaling Experiment

Module for model scaling experiment functionality in the ImpressionCore framework.

File: modules\attention\model_scaling_experiment.py
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
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements model scaling experiment functionality for the
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
from modules.attention.model_scaling_experiment import ModelConfig
instance = ModelConfig()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import gc
import torch
import torch.nn as nn
import logging
import time
import signal
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.modules.attention.attention_manager import AttentionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a model to test scaling."""
    # Memory optimization: Explicit memory cleanup
    hidden_size: int
    num_layers: int
    num_heads: int
    text_seq_length: int
    image_size: Tuple[int, int]
    batch_size: int
    
    def __str__(self) -> str:
        """String representation of model configuration."""
        # Memory optimization: Explicit memory cleanup
        return (f"Model(h={self.hidden_size}, "
                f"L={self.num_layers}, "
                f"A={self.num_heads}, "
                f"S_text={self.text_seq_length}, "
                f"S_img={self.image_size}, "
                f"B={self.batch_size})")


class ScalableTransformerLayer(nn.Module):
    """A transformer layer using AttentionManager for optimized attention mechanisms."""
    def __init__(
        """
        
    __init__ function for processing.
    
    Args:
        self, hidden_size, num_heads, dropout, attention_preference: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self, 
        hidden_size: int,
        num_heads: int,
        dropout: float = 0.1,
        attention_preference: str = "balanced"
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        
        # Initialize attention with our optimized AttentionManager
        self.attention = AttentionManager(
            hidden_size=hidden_size,
            num_heads=num_heads,
            attention_preference=attention_preference,
            chunk_size=64  # Default chunk size for memory optimization
            # Memory optimization: Memory-critical operation
        )
        
        # Layer normalization and feed-forward components
        self.norm1 = nn.LayerNorm(hidden_size)
        self.norm2 = nn.LayerNorm(hidden_size)
        
        # Feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 4),
            nn.GELU(),
            nn.Linear(hidden_size * 4, hidden_size),
            nn.Dropout(dropout)
        )
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(
        self, 
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        is_2d_data: bool = False,
        height: Optional[int] = None,
        width: Optional[int] = None
    ) -> torch.Tensor:
        """Forward pass through the transformer layer."""
        # Validate input shapes
        batch_size, seq_length, hidden_dim = hidden_states.shape
        assert hidden_dim == self.hidden_size, f"Hidden dimension mismatch: {hidden_dim} != {self.hidden_size}"
        
        if attention_mask is not None:
            # Validate attention mask shape
            mask_size = attention_mask.size()
            expected_mask_size = (batch_size, seq_length)
            assert len(mask_size) == 2 and mask_size == expected_mask_size, \
                f"Attention mask shape {mask_size} doesn't match expected {expected_mask_size}"
            
            # Log attention mask shape before expand
            # logger.info(f"Attention mask shape before expand: {attention_mask.shape}") # Commented out for less verbose logs
            # Expand attention mask for multi-head attention
            # Pass the original boolean mask to AttentionManager.
        # The manager will handle conversion/formatting based on the selected attention type.
        pass # No conversion needed here, pass original mask
        # Apply attention with validated inputs
        residual = hidden_states
        hidden_states = self.norm1(hidden_states)
        
        attention_output = self.attention(
            hidden_states=hidden_states,
            attention_mask=attention_mask,
            is_2d_data=is_2d_data,
            height=height,
            width=width
        )
        
        hidden_states = residual + self.dropout(attention_output)
        
        # Feed forward network
        residual = hidden_states
        hidden_states = self.norm2(hidden_states)
        ffn_output = self.ffn(hidden_states)
        hidden_states = residual + self.dropout(ffn_output)
        
        return hidden_states


class ScalableTransformerModel(nn.Module):
    """
    A scalable transformer model for testing different sizes and configurations.
    # Memory optimization: Explicit memory cleanup
    
    This model can handle both text and image modalities using specialized attention patterns.
    # Memory optimization: Explicit memory cleanup
    """
    def __init__(
        """
        
    __init__ function for processing.
    
    Args:
        self, hidden_size, num_layers, num_heads, dropout, max_text_seq_length, vocab_size: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self,
        hidden_size: int = 768,
        num_layers: int = 12,
        num_heads: int = 12,
        dropout: float = 0.1,
        max_text_seq_length: int = 512,
        vocab_size: int = 50000,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        
        # Text embedding
        self.word_embeddings = nn.Embedding(vocab_size, hidden_size)
        self.position_embeddings = nn.Embedding(max_text_seq_length, hidden_size)
        self.token_type_embeddings = nn.Embedding(2, hidden_size)  # For text/image distinction
        
        # Image patch embedding (configurable)
        self.patch_size = 16  # Default patch size
        self.patch_embed = None  # Initialized on demand once image size is known
        
        # Embedding normalization and dropout
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.dropout = nn.Dropout(dropout)
        
        # Create transformer layers
        self.layers = nn.ModuleList([
            ScalableTransformerLayer(
                hidden_size=hidden_size,
                num_heads=num_heads,
                dropout=dropout
            ) for _ in range(num_layers)
        ])
        
        # Output pooling
        self.pooler = nn.Linear(hidden_size, hidden_size)
        self.pooler_activation = nn.Tanh()
        
        # Calculate and log parameter count
        # total_params = sum(p.numel() for p in self.parameters()) # Moved calculation to estimate_parameters
        # logger.info(f"Model initialized with {total_params:,} parameters") # Logged during estimation instead
        # Memory optimization: Explicit memory cleanup
        
    def _init_patch_embed(self, image_size: Tuple[int, int], in_channels: int = 3):
        """Initialize patch embedding for images of specified size."""
        h, w = image_size
        # Ensure divisibility by patch size
        assert h % self.patch_size == 0, f"Image height {h} must be divisible by patch size {self.patch_size}"
        assert w % self.patch_size == 0, f"Image width {w} must be divisible by patch size {self.patch_size}"
        
        # Create patch embedding
        self.patch_embed = nn.Conv2d(
            in_channels, self.hidden_size, 
            kernel_size=self.patch_size, stride=self.patch_size
        ).to(next(self.parameters()).device)
        # Memory optimization: Device placement for memory management
        
    def forward_text(
        self, 
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass for text inputs."""
        batch_size, seq_length = input_ids.shape
        device = input_ids.device
        # Memory optimization: Device placement for memory management
        
        # Create position IDs and token type IDs
        position_ids = torch.arange(seq_length, dtype=torch.long, device=device)
        # Memory optimization: Device placement for memory management
        position_ids = position_ids.unsqueeze(0).expand(batch_size, -1)
        token_type_ids = torch.zeros_like(input_ids)
        
        # Get embeddings
        word_embeds = self.word_embeddings(input_ids)
        position_embeds = self.position_embeddings(position_ids)
        token_type_embeds = self.token_type_embeddings(token_type_ids)
        
        # Combine embeddings
        embeddings = word_embeds + position_embeds + token_type_embeds
        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)
        
        # Process through transformer layers
        hidden_states = embeddings
        for layer in self.layers:
            hidden_states = layer(
                hidden_states=hidden_states,
                attention_mask=attention_mask,
                is_2d_data=False
            )
            
        # Pool output
        pooled_output = hidden_states[:, 0]  # Use CLS token
        return self.pooler_activation(self.pooler(pooled_output))
    
    def forward_image(
        self,
        images: torch.Tensor
    ) -> torch.Tensor:
        """Forward pass for image inputs."""
        batch_size, channels, height, width = images.shape
        device = images.device
        # Memory optimization: Device placement for memory management
        
        # Initialize patch embedding if not done yet
        if self.patch_embed is None:
            self._init_patch_embed((height, width), channels)
        
        # Calculate patches
        h_patches = height // self.patch_size
        w_patches = width // self.patch_size
        
        # Create patch embeddings with memory efficient reshaping
        # Memory optimization: Memory-critical operation
        patch_embeddings = self.patch_embed(images)  # [B, H, h, w]
        batch_size, hidden_dim, h_patch, w_patch = patch_embeddings.shape
        
        # More efficient reshaping that avoids intermediate copies
        patch_embeddings = patch_embeddings.permute(0, 2, 3, 1)  # [B, h, w, H]
        patch_embeddings = patch_embeddings.reshape(batch_size, h_patch * w_patch, hidden_dim)
        
        # Create CLS token more efficiently
        cls_token = torch.zeros(
            (batch_size, 1, self.hidden_size),
            device=device,
            # Memory optimization: Device placement for memory management
            dtype=patch_embeddings.dtype
        )
        embeddings = torch.cat([cls_token, patch_embeddings], dim=1)
        
        # Calculate position embeddings efficiently
        num_patches = h_patches * w_patches
        max_positions = min(num_patches + 1, self.position_embeddings.num_embeddings)
        position_ids = torch.arange(max_positions, device=device)
        # Memory optimization: Device placement for memory management
        position_embeds = self.position_embeddings(position_ids)
        position_embeds = position_embeds.unsqueeze(0).expand(batch_size, -1, -1)
        
        # Handle sequence length efficiently
        if embeddings.size(1) > max_positions:
            embeddings = embeddings[:, :max_positions, :]
            logger.info(f"Truncating sequence from {num_patches + 1} to {max_positions} tokens")
        
        # Combine embeddings efficiently
        embeddings = embeddings + position_embeds
        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)
        
        # Process through transformer layers with proper height/width info
        hidden_states = embeddings
        for layer in self.layers:
            hidden_states = layer(
                hidden_states=hidden_states,
                attention_mask=None,
                is_2d_data=True,
                height=h_patches,
                width=w_patches
            )
        
        # Pool output
        pooled_output = hidden_states[:, 0]
        return self.pooler_activation(self.pooler(pooled_output))


def measure_memory_and_time(
# Memory optimization: Memory-critical operation
    model_func,
    input_tensors: Dict[str, torch.Tensor],
    desc: str = ""
) -> Tuple[float, float]:
    """
    Measure execution time and memory usage for a model function.
    # Memory optimization: Explicit memory cleanup
    """
    device = list(input_tensors.values())[0].device
    # Memory optimization: Device placement for memory management
    
    # Clear cache before measurement
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        torch.cuda.empty_cache()
        # Memory optimization: CUDA operations for GPU acceleration
        torch.cuda.reset_peak_memory_stats()
        # Memory optimization: CUDA operations for GPU acceleration
        
    # Track initial memory
    # Memory optimization: Memory-critical operation
    start_memory = 0
    # Memory optimization: Memory-critical operation
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        torch.cuda.synchronize()
        # Memory optimization: CUDA operations for GPU acceleration
        start_memory = torch.cuda.memory_allocated() / (1024 ** 2)
        # Memory optimization: CUDA operations for GPU acceleration
    
    # Measure time
    start_time = time.time()
    with torch.no_grad():
    # Memory optimization: Disable gradient computation to save memory
        _ = model_func(**input_tensors)
    
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        torch.cuda.synchronize()
        # Memory optimization: CUDA operations for GPU acceleration
    end_time = time.time()
    
    # Calculate memory usage (Peak memory is more relevant here)
    # Memory optimization: Memory-critical operation
    peak_memory = 0
    # Memory optimization: Memory-critical operation
    if device.type == "cuda":
    # Memory optimization: Device placement for memory management
        peak_memory = torch.cuda.max_memory_allocated() / (1024 ** 2)
        # Memory optimization: CUDA operations for GPU acceleration
    
    elapsed_ms = (end_time - start_time) * 1000
    
    if desc:
        # Log peak memory instead of delta
        # Memory optimization: Memory-critical operation
        logger.info(f"{desc} - Time: {elapsed_ms:.2f}ms, Peak Memory: {peak_memory:.2f}MB")
        # Memory optimization: Memory-critical operation
    
    # Return peak memory instead of delta memory_used
    # Memory optimization: Memory-critical operation
    return elapsed_ms, peak_memory
    # Memory optimization: Memory-critical operation


def setup_experiment_logging():
    """Setup experiment-specific logging"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(os.path.dirname(__file__), "experiment_logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"scaling_experiment_{timestamp}.log")
    checkpoint_file = os.path.join(log_dir, f"checkpoint_{timestamp}.json")
    
    # Avoid adding duplicate handlers if script is re-run in same session
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == log_file for h in logger.handlers):
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
    
    return log_file, checkpoint_file

def save_checkpoint(checkpoint_file: str, current_state: Dict):
    """Save experiment progress"""
    # Convert dataclass configs to dicts for JSON serialization
    serializable_state = {
        "text": [{**result, "config": asdict(result["config"])} for result in current_state.get("text", [])],
        "image": [{**result, "config": asdict(result["config"])} for result in current_state.get("image", [])],
        "successful_configs": [{**cfg, "config": asdict(cfg["config"])} 
                             for cfg in current_state.get("successful_configs", [])],
        "target_params": current_state.get("target_params"),
        "param_range": current_state.get("param_range")
    }
    
    try:
        with open(checkpoint_file, 'w') as f:
            json.dump(serializable_state, f, indent=4) # Added indent for readability
        logger.info(f"Saved checkpoint to {checkpoint_file}")
    except Exception as e:
        logger.error(f"Failed to save checkpoint to {checkpoint_file}: {e}")


def load_checkpoint(checkpoint_file: str) -> Optional[Dict]:
    """Load experiment progress"""
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                
            # Convert dict configs back to ModelConfig objects
            restored_state = {
                "text": [{**result, "config": ModelConfig(**result["config"])} 
                        for result in checkpoint.get("text", [])],
                "image": [{**result, "config": ModelConfig(**result["config"])} 
                         for result in checkpoint.get("image", [])],
                "successful_configs": [{**cfg, "config": ModelConfig(**cfg["config"])} 
                                     for cfg in checkpoint.get("successful_configs", [])]
            }
            # Add back the parameter range and target if they existed
            if "target_params" in checkpoint:
                 restored_state["target_params"] = checkpoint["target_params"]
            if "param_range" in checkpoint:
                 restored_state["param_range"] = tuple(checkpoint["param_range"]) # Ensure it's a tuple
            return restored_state
        except Exception as e:
            logger.error(f"Failed to load or parse checkpoint {checkpoint_file}: {e}")
            return None
    return None


def run_model_scaling_experiment(
    device: torch.device,
    # Memory optimization: Device placement for memory management
    vram_target: float = 3500.0,
    safety_margin: float = 0.8,
    include_text: bool = True,
    include_image: bool = True,
    checkpoint_file: Optional[str] = None
) -> Dict:
    """Run a model scaling experiment targeting 0.5B-3.0B parameters."""
    # Memory optimization: Explicit memory cleanup
    actual_target = vram_target * safety_margin
    logger.info(f"Running model scaling experiment (0.5B-3.0B parameters) on {device}")
    # Memory optimization: Device placement for memory management
    logger.info(f"Target VRAM: {vram_target:.2f}MB (using {actual_target:.2f}MB with safety margin)")
    
    # Revised configurations targeting 0.5B - 3.0B parameters with d_head=64
    hidden_sizes = [1536, 2048, 2560, 3072] 
    layer_multipliers = {
        1536: [16, 24, 32, 40, 48],      # Approx 0.5B - 1.5B
        2048: [12, 18, 24, 30, 36, 42],  # Approx 0.7B - 2.2B
        2560: [8, 12, 16, 20, 24, 28],   # Approx 0.7B - 2.3B
        3072: [6, 8, 12, 16, 20]       # Approx 0.8B - 2.6B
    }
    # head_divisors dictionary removed, num_heads will be calculated directly
    
    # Sequence length for testing
    text_seq_lengths = [512] if include_text else []
    image_sizes = [(224, 224)] if include_image else []
    
    results = {
        "text": [],
        "image": [],
        "successful_configs": [],
        "target_params": 3.0,  # Target 3B parameters (upper bound)
        "param_range": (0.5, 3.0)  # New range: 0.5B to 3.0B parameters
    }

    def estimate_parameters(config: ModelConfig) -> Optional[float]:
        """Estimate number of parameters for a configuration more accurately."""
        h = config.hidden_size
        l = config.num_layers
        
        # More detailed calculation:
        attention_params = l * 4 * h**2 # QKV projection (3*h*h) + Output projection (h*h)
        ffn_params = l * 8 * h**2       # FFN (h*4h + 4h*h)
        layer_norm_params = l * 2 * 2 * h # 2 LayerNorms per layer, each with 2*h params (scale/bias)
        total_params = attention_params + ffn_params + layer_norm_params
        
        # Add embedding parameters (rough estimate)
        vocab_size = 50000
        max_pos = 512 # Use max_text_seq_length from config if available? For now, fixed 512.
        embedding_params = h * vocab_size + h * max_pos 
        
        # Add patch embedding if image
        if config.image_size != (0, 0):
             patch_size = 16 # Assuming patch size 16
             num_patches = (config.image_size[0] // patch_size) * (config.image_size[1] // patch_size)
             patch_embed_params = h * (patch_size**2 * 3) # Input channels = 3
             # Add patch embed weights + position embeds for patches + CLS token pos embed
             embedding_params += patch_embed_params + h * (num_patches + 1) 

        total_params += embedding_params
        total_params /= 1e9 # Convert to billions

        if results["param_range"][0] <= total_params <= results["param_range"][1]:
            logger.info(f"Configuration {config} has {total_params:.3f}B parameters - IN RANGE")
            return total_params
        else:
            logger.info(f"Skipping {config} - Parameters {total_params:.3f}B outside range {results['param_range']}")
            return None # Return None if outside range

    
    def should_test_config(config: ModelConfig) -> bool:
        """Determine if configuration is worth testing"""
        # Add logic here if needed to skip certain configs based on prior knowledge
        return True

    # Helper to check if within memory target
    # Memory optimization: Memory-critical operation
    def is_within_memory_target(peak_memory):
    # Memory optimization: Memory-critical operation
        """
        
    is_within_memory_target function for processing.
    # Memory optimization: Memory-critical operation
    
    Args:
        peak_memory: Function parameters
        # Memory optimization: Memory-critical operation
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        return peak_memory <= actual_target
        # Memory optimization: Memory-critical operation

    
    def cleanup_gpu():
    # Memory optimization: Memory-critical operation
        """Helper to clean up GPU memory between tests"""
        # Memory optimization: Memory-critical operation
        if device.type == "cuda":
        # Memory optimization: Device placement for memory management
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
            # Don't reset peak stats here, do it before each measurement
            gc.collect()
            # Memory optimization: Force garbage collection

    # --- Start of Corrected Indented Block ---
    # Test text configurations
    if include_text:
        logger.info("Testing text model configurations...")
        # Memory optimization: Explicit memory cleanup
        for hidden_size in hidden_sizes:
            # Ensure hidden_size is compatible with d_head=64 and has layers defined
            if hidden_size not in layer_multipliers or hidden_size % 64 != 0: 
                logger.debug(f"Skipping hidden_size {hidden_size} due to incompatibility or missing layer definition.")
                continue 
            for num_layers in layer_multipliers[hidden_size]:
                num_heads = hidden_size // 64 # Calculate num_heads based on fixed d_head=64
                for seq_length in text_seq_lengths:
                    config = ModelConfig(
                        hidden_size=hidden_size,
                        num_layers=num_layers,
                        num_heads=num_heads, # Use calculated num_heads
                        text_seq_length=seq_length,
                        image_size=(0, 0), # No image
                        batch_size=1
                    )
                    
                    if not should_test_config(config):
                        continue
                    
                    estimated_params = estimate_parameters(config)
                    if estimated_params is None: # Check if None (means outside range)
                        continue 

                    logger.info(f"Testing text model: {config}")
                    
                    try:
                        cleanup_gpu() # Clean before test
                        # Memory optimization: Memory-critical operation
                        # Reset peak memory stats before this specific test
                        # Memory optimization: Memory-critical operation
                        if device.type == "cuda":
                        # Memory optimization: Device placement for memory management
                            torch.cuda.reset_peak_memory_stats()
                            # Memory optimization: CUDA operations for GPU acceleration

                        # Initialize model and move to device
                        # Memory optimization: Device placement for memory management
                        model_start_time = time.time()
                        model = ScalableTransformerModel(
                        # Memory optimization: Explicit memory cleanup
                            hidden_size=config.hidden_size,
                            num_layers=config.num_layers,
                            num_heads=config.num_heads,
                            max_text_seq_length=config.text_seq_length
                        ).to(device)
                        # Memory optimization: Device placement for memory management
                        model_init_time = time.time() - model_start_time
                        logger.info(f"Model initialization time: {model_init_time:.2f} seconds")
                        # Memory optimization: Explicit memory cleanup
                        
                        # Generate dummy input
                        input_ids = torch.randint(0, 50000, (config.batch_size, config.text_seq_length)).to(device)
                        # Memory optimization: Device placement for memory management
                        attention_mask = torch.ones((config.batch_size, config.text_seq_length), dtype=torch.bool).to(device)
                        # Memory optimization: Device placement for memory management
                        input_tensors = {"input_ids": input_ids, "attention_mask": attention_mask}
                        
                        # Measure memory and time (now returns peak memory)
                        # Memory optimization: Memory-critical operation
                        forward_time, peak_memory = measure_memory_and_time(
                        # Memory optimization: Memory-critical operation
                            model_func=model.forward_text,
                            input_tensors=input_tensors,
                            desc=f"Text {config}"
                        )
                        
                        # Check if within VRAM target
                        within_vram = is_within_memory_target(peak_memory)
                        # Memory optimization: Memory-critical operation
                        
                        result_entry = {
                            "config": config,
                            "modality": "text",
                            # "memory_usage_mb": memory_usage, # Removed delta memory
                            # Memory optimization: Memory-critical operation
                            "forward_time_ms": forward_time,
                            "peak_vram_mb": peak_memory,
                            # Memory optimization: Memory-critical operation
                            "within_vram_target": within_vram,
                            "estimated_params_b": estimated_params,
                            "model_init_time_sec": model_init_time
                        }
                        results["text"].append(result_entry)
                        
                        if within_vram:
                            results["successful_configs"].append(result_entry)
                            logger.info(f"✅ Text model {config} within VRAM target ({peak_memory:.2f}MB)")
                            # Memory optimization: Explicit memory cleanup
                        else:
                            logger.warning(f"-- Text model {config} exceeded VRAM target ({peak_memory:.2f}MB)")
                            # Memory optimization: Explicit memory cleanup
                        
                        del model, input_ids, attention_mask, input_tensors # Cleanup tensors and model
                        # Memory optimization: Explicit memory cleanup
                        
                    except torch.cuda.OutOfMemoryError as e:
                    # Memory optimization: CUDA operations for GPU acceleration
                        logger.error(f"OOM Error testing text model {config}: {e}")
                        # Memory optimization: Explicit memory cleanup
                        results["text"].append({
                            "config": config,
                            "modality": "text",
                            "error": "OOM",
                            "estimated_params_b": estimated_params
                        })
                    except Exception as e:
                        logger.error(f"Error testing text model {config}: {e}")
                        # Memory optimization: Explicit memory cleanup
                        results["text"].append({
                            "config": config,
                            "modality": "text",
                            "error": str(e),
                            "estimated_params_b": estimated_params
                        })
                    finally:
                         cleanup_gpu() # Ensure cleanup happens after each try
                         # Memory optimization: Memory-critical operation

    # Test image configurations
    if include_image:
        logger.info("Testing image model configurations...")
        # Memory optimization: Explicit memory cleanup
        for hidden_size in hidden_sizes:
            # Ensure hidden_size is compatible with d_head=64 and has layers defined
            if hidden_size not in layer_multipliers or hidden_size % 64 != 0: 
                logger.debug(f"Skipping hidden_size {hidden_size} due to incompatibility or missing layer definition.")
                continue
            for num_layers in layer_multipliers[hidden_size]:
                num_heads = hidden_size // 64 # Calculate num_heads based on fixed d_head=64
                for img_size in image_sizes:
                    config = ModelConfig(
                        hidden_size=hidden_size,
                        num_layers=num_layers,
                        num_heads=num_heads, # Use calculated num_heads
                        text_seq_length=0, # No text
                        image_size=img_size,
                        batch_size=1
                    )
                        
                    if not should_test_config(config):
                        continue
                     
                    estimated_params = estimate_parameters(config)
                    if estimated_params is None: # Check if None (means outside range)
                        continue 
                
                    logger.info(f"Testing image model: {config}")
                    
                    try:
                        cleanup_gpu() # Clean before test
                        # Memory optimization: Memory-critical operation
                        # Reset peak memory stats before this specific test
                        # Memory optimization: Memory-critical operation
                        if device.type == "cuda":
                        # Memory optimization: Device placement for memory management
                            torch.cuda.reset_peak_memory_stats()
                            # Memory optimization: CUDA operations for GPU acceleration

                        # Initialize model
                        model_start_time = time.time()
                        model = ScalableTransformerModel(
                        # Memory optimization: Explicit memory cleanup
                            hidden_size=config.hidden_size,
                            num_layers=config.num_layers,
                            num_heads=config.num_heads
                        ).to(device)
                        # Memory optimization: Device placement for memory management
                        model_init_time = time.time() - model_start_time
                        logger.info(f"Model initialization time: {model_init_time:.2f} seconds")
                        # Memory optimization: Explicit memory cleanup
                        
                        # Generate dummy input
                        dummy_image = torch.randn((config.batch_size, 3, img_size[0], img_size[1])).to(device)
                        # Memory optimization: Device placement for memory management
                        input_tensors = {"images": dummy_image}
                        
                        # Measure time and memory (now returns peak memory)
                        # Memory optimization: Memory-critical operation
                        forward_time, peak_memory = measure_memory_and_time(
                        # Memory optimization: Memory-critical operation
                            model_func=model.forward_image,
                            input_tensors=input_tensors,
                            desc=f"Image {config}"
                        )
                        
                        # Check memory usage
                        # Memory optimization: Memory-critical operation
                        within_vram = is_within_memory_target(peak_memory)
                        # Memory optimization: Memory-critical operation
                        
                        result_entry = {
                            "config": config,
                            "modality": "image",
                            # "memory_usage_mb": memory_usage, # Removed delta memory
                            # Memory optimization: Memory-critical operation
                            "forward_time_ms": forward_time,
                            "peak_vram_mb": peak_memory,
                            # Memory optimization: Memory-critical operation
                            "within_vram_target": within_vram,
                            "estimated_params_b": estimated_params,
                            "model_init_time_sec": model_init_time
                        }
                        results["image"].append(result_entry)
                        
                        if is_within_memory_target(peak_memory):
                        # Memory optimization: Memory-critical operation
                            results["successful_configs"].append(result_entry)
                            logger.info(f"✅ Image model {config} within VRAM target ({peak_memory:.2f}MB)")
                            # Memory optimization: Explicit memory cleanup
                        else:
                            logger.warning(f"❌ Image model {config} exceeded VRAM target ({peak_memory:.2f}MB)")
                            # Memory optimization: Explicit memory cleanup

                        del model, dummy_image, input_tensors # Cleanup
                        # Memory optimization: Explicit memory cleanup
                                                
                    except torch.cuda.OutOfMemoryError as e:
                    # Memory optimization: CUDA operations for GPU acceleration
                        logger.error(f"OOM Error testing image model {config}: {e}")
                        # Memory optimization: Explicit memory cleanup
                        results["image"].append({
                            "config": config,
                            "modality": "image",
                            "error": "OOM",
                            "estimated_params_b": estimated_params
                        })
                    except Exception as e:
                        logger.error(f"Error testing image model {config}: {e}")
                        # Memory optimization: Explicit memory cleanup
                        results["image"].append({
                            "config": config,
                            "modality": "image",
                            "error": str(e),
                            "estimated_params_b": estimated_params
                        })
                    finally:
                        cleanup_gpu() # Ensure cleanup happens after each try
                        # Memory optimization: Memory-critical operation
    # --- End of Corrected Indented Block ---

    return results


def visualize_scaling_results(results: Dict):
    """
    Visualize the scaling experiment results, plotting memory usage vs. model size.
    # Memory optimization: Explicit memory cleanup
    """
    log_dir = os.path.join(os.path.dirname(__file__), "experiment_logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Ensure results dictionary has the expected keys
    if "text" not in results or "image" not in results:
        logger.error("Results dictionary is missing 'text' or 'image' keys. Cannot visualize.")
        return
        
    all_configs = results.get("text", []) + results.get("image", [])
    if not all_configs:
         logger.warning("No configurations found in results to visualize.")
         return

    # Filter out entries without estimated_params_b or peak_vram_mb
    valid_configs = [cfg for cfg in all_configs if cfg.get("estimated_params_b") is not None and cfg.get("peak_vram_mb") is not None]
    
    if not valid_configs:
        logger.warning("No valid configurations with parameter and memory data found for visualization.")
        # Memory optimization: Memory-critical operation
        return

    params = [cfg["estimated_params_b"] for cfg in valid_configs]
    memory = [cfg["peak_vram_mb"] for cfg in valid_configs]
    # Memory optimization: Memory-critical operation
    colors = ['green' if cfg.get("within_vram_target") else 'red' for cfg in valid_configs]
    labels = [f'{cfg["modality"].capitalize()} {"Success" if cfg.get("within_vram_target") else "Fail"}' for cfg in valid_configs]

    # Create scatter plot using unique labels for legend
    plt.figure(figsize=(12, 7))
    unique_labels = sorted(list(set(labels)))
    label_colors = {'Text Success': 'green', 'Text Fail': 'red', 'Image Success': 'blue', 'Image Fail': 'orange'} # Adjusted colors for clarity

    for label in unique_labels:
        indices = [i for i, lbl in enumerate(labels) if lbl == label]
        if not indices: continue # Skip if no data for this label
        plt.scatter(
            [params[i] for i in indices], 
            [memory[i] for i in indices], 
            # Memory optimization: Memory-critical operation
            color=label_colors.get(label, 'gray'), # Use gray for unexpected labels
            label=label
        )

    plt.title('Model Scaling Experiment - Peak VRAM vs. Estimated Parameters')
    # Memory optimization: Explicit memory cleanup
    plt.xlabel('Estimated Parameters (Billions)')
    plt.ylabel('Peak VRAM Usage (MB)')
    plt.legend(loc='upper left')
    plt.grid(True)
    
    plot_filename = os.path.join(log_dir, 'combined_scaling_results.png')
    try:
        plt.savefig(plot_filename)
        logger.info(f"Combined scaling results plot saved to {plot_filename}")
    except Exception as e:
        logger.error(f"Failed to save plot {plot_filename}: {e}")
    finally:
        plt.close()


def main():
    """
    
    main function for processing.
    
    Args:
        No arguments: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
    """
    parser = argparse.ArgumentParser(description="Run model scaling experiments.")
    # Memory optimization: Explicit memory cleanup
    parser.add_argument('--device', type=str, default='cuda', choices=['cpu', 'cuda'],
    # Memory optimization: Device placement for memory management
                        help="Device to run experiments on (cpu or cuda).")
                        # Memory optimization: Device placement for memory management
    parser.add_argument('--vram-target', type=float, default=3500.0,
                        help="Target VRAM usage in MB.")
    parser.add_argument('--safety-margin', type=float, default=0.8, # Adjusted default back to 0.8 as per original command
                        help="Safety margin for VRAM target (e.g., 0.8 for 80% target).")
    parser.add_argument('--no-text', action='store_false', dest='include_text', default=True,
                        help="Exclude text model experiments.")
                        # Memory optimization: Explicit memory cleanup
    parser.add_argument('--no-image', action='store_false', dest='include_image', default=True,
                        help="Exclude image model experiments.")
                        # Memory optimization: Explicit memory cleanup
    parser.add_argument('--fresh', action='store_true', 
                        help="Start a fresh experiment, ignoring checkpoints.")
    
    args = parser.parse_args()
    
    device = torch.device(args.device)
    # Memory optimization: Device placement for memory management
    if args.device == 'cuda' and not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.warning("CUDA device requested but not available, falling back to CPU.")
        # Memory optimization: Device placement for memory management
        device = torch.device('cpu')
        # Memory optimization: Device placement for memory management
        
    if device.type == 'cuda':
    # Memory optimization: Device placement for memory management
         try:
             logger.info(f"Using GPU: {torch.cuda.get_device_name(0)} with {torch.cuda.get_device_properties(0).total_memory / (1024**2):.2f}MB VRAM")
             # Memory optimization: CUDA operations for GPU acceleration
         except Exception as e:
             logger.error(f"Could not get CUDA device info: {e}")
             # Memory optimization: Device placement for memory management
             device = torch.device('cpu') # Fallback if info fails
             # Memory optimization: Device placement for memory management
             logger.info("Falling back to CPU.")
    else:
         logger.info("Using CPU")

    log_file, checkpoint_file = setup_experiment_logging()
    logger.info(f"Experiment logs will be saved to: {log_file}")
    logger.info(f"Experiment checkpoints will be saved to: {checkpoint_file}")
    
    results = None # Initialize results
    if not args.fresh:
        logger.info(f"Attempting to load experiment progress from checkpoint: {checkpoint_file}")
        results = load_checkpoint(checkpoint_file)
        if results:
             logger.info("Successfully loaded checkpoint.")
             # Re-apply command line args for modality inclusion if checkpoint exists
             # This allows overriding checkpoint settings for text/image inclusion
             if not args.include_text:
                 results['text'] = []
                 results['successful_configs'] = [cfg for cfg in results.get('successful_configs', []) if cfg['modality'] != 'text']
             if not args.include_image:
                 results['image'] = []
                 results['successful_configs'] = [cfg for cfg in results.get('successful_configs', []) if cfg['modality'] != 'image']
             logger.info(f"Running with include_text={args.include_text}, include_image={args.include_image} based on args.")
        else:
             logger.info("No valid checkpoint found or failed to load.")

    if results is None: # Run experiment if no checkpoint loaded or --fresh is used
        logger.info("Starting a new experiment run.")
        results = run_model_scaling_experiment(
            device=device,
            # Memory optimization: Device placement for memory management
            vram_target=args.vram_target,
            safety_margin=args.safety_margin,
            include_text=args.include_text,
            include_image=args.include_image,
            checkpoint_file=checkpoint_file # Pass checkpoint file for saving within experiment
        )
        
    if results:
        logger.info("Visualizing results...")
        visualize_scaling_results(results)
        logger.info("Saving final checkpoint...")
        save_checkpoint(checkpoint_file, results) # Final save after visualization
    else:
        logger.warning("No results generated or loaded, skipping visualization and final save.")

if __name__ == '__main__':
    main()\n#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src\modules\attention\model_scaling_experiment.py
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
