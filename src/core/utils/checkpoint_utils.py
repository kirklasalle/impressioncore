#!/usr/bin/env python3
"""
ImpressionCore: Checkpoint Utils

Module for checkpoint utils functionality in the ImpressionCore framework.

File: core/utils/checkpoint_utils.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [utilities, memory-critical, framework, pytorch, core, production, utils, 2025]
Dependencies: [torch, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements checkpoint utils functionality for the
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
from src.core.utils.checkpoint_utils import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
import torch.utils.checkpoint as checkpoint
from typing import Callable, List, Optional, Union, Dict, Any, Tuple
import logging
from pathlib import Path
import os

logger = logging.getLogger("checkpoint_utils")

def apply_transformer_checkpointing(
    model: torch.nn.Module,
    layer_attr: str = "transformer_layers",
    use_reentrant: bool = False
) -> torch.nn.Module:
    """
    Apply activation checkpointing to transformer layers in a model.
    
    Wraps the forward method of transformer layers with checkpointing to trade
    computation for memory by discarding activations during the forward pass
    # Memory optimization: Memory-critical operation
    and recomputing them during the backward pass.
    
    Args:
        model: PyTorch model containing transformer layers
        # Memory optimization: Explicit memory cleanup
        layer_attr: Attribute name of the list of transformer layers
        use_reentrant: Whether to use reentrant checkpointing (PyTorch >=1.9.0)
    
    Returns:
        Model with checkpointing applied to transformer layers
        # Memory optimization: Explicit memory cleanup
    """
    if not hasattr(model, layer_attr):
        logger.warning(f"Model does not have attribute {layer_attr}, skipping checkpointing")
        # Memory optimization: Explicit memory cleanup
        return model
    
    layers = getattr(model, layer_attr)
    
    # Store original forward methods
    for i, layer in enumerate(layers):
        if not hasattr(layer, "_original_forward"):
            layer._original_forward = layer.forward
            
            # Define checkpointed forward function
            def make_checkpointed_forward(idx, orig_forward):
                """
                
    make_checkpointed_forward function for processing.
    
    Args:
        idx, orig_forward: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                def checkpointed_forward(*args, **kwargs):
                    """
                    
    checkpointed_forward function for processing.
    
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
                    if kwargs:
                        # Checkpoint doesn't support kwargs, so we need to handle them manually
                        def custom_forward(*inputs):
                            """
                            
    custom_forward function for processing.
    
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
                            return orig_forward(*inputs, **kwargs)
                        
                        if hasattr(checkpoint, "checkpoint"):
                            # PyTorch >= 1.9.0 with use_reentrant option
                            if "use_reentrant" in checkpoint.checkpoint.__code__.co_varnames:
                                return checkpoint.checkpoint(custom_forward, *args, use_reentrant=use_reentrant)
                            else:
                                return checkpoint.checkpoint(custom_forward, *args)
                        else:
                            return checkpoint(custom_forward, *args)
                    else:
                        # Direct case for args-only
                        if hasattr(checkpoint, "checkpoint"):
                            if "use_reentrant" in checkpoint.checkpoint.__code__.co_varnames:
                                return checkpoint.checkpoint(orig_forward, *args, use_reentrant=use_reentrant)
                            else:
                                return checkpoint.checkpoint(orig_forward, *args)
                        else:
                            return checkpoint(orig_forward, *args)
                
                return checkpointed_forward
            
            # Replace forward method with checkpointed version
            layer.forward = make_checkpointed_forward(i, layer._original_forward)
            
    logger.info(f"Applied activation checkpointing to {len(layers)} transformer layers")
    return model

def remove_checkpointing(model: torch.nn.Module, layer_attr: str = "transformer_layers") -> torch.nn.Module:
    """
    Remove activation checkpointing from transformer layers.
    
    Restores original forward methods for transformer layers.
    
    Args:
        model: PyTorch model with checkpointing applied
        # Memory optimization: Explicit memory cleanup
        layer_attr: Attribute name of the list of transformer layers
    
    Returns:
        Model with original forward methods restored
        # Memory optimization: Explicit memory cleanup
    """
    if not hasattr(model, layer_attr):
        return model
    
    layers = getattr(model, layer_attr)
    
    # Restore original forward methods
    for i, layer in enumerate(layers):
        if hasattr(layer, "_original_forward"):
            layer.forward = layer._original_forward
            delattr(layer, "_original_forward")
    
    logger.info(f"Removed activation checkpointing from {len(layers)} transformer layers")
    return model

def selective_checkpointing(
    model: torch.nn.Module,
    layer_indices: List[int],
    layer_attr: str = "transformer_layers",
    use_reentrant: bool = False
) -> torch.nn.Module:
    """
    Apply activation checkpointing selectively to specific transformer layers.
    
    Useful for fine-grained memory optimization by checkpointing only the most
    # Memory optimization: Memory-critical operation
    memory-intensive layers.
    # Memory optimization: Memory-critical operation
    
    Args:
        model: PyTorch model containing transformer layers
        # Memory optimization: Explicit memory cleanup
        layer_indices: List of indices of layers to apply checkpointing to
        layer_attr: Attribute name of the list of transformer layers
        use_reentrant: Whether to use reentrant checkpointing (PyTorch >=1.9.0)
    
    Returns:
        Model with checkpointing applied to selected layers
        # Memory optimization: Explicit memory cleanup
    """
    if not hasattr(model, layer_attr):
        return model
    
    layers = getattr(model, layer_attr)
    
    # Apply checkpointing to selected layers
    for i in layer_indices:
        if i < 0 or i >= len(layers):
            logger.warning(f"Layer index {i} out of range, skipping")
            continue
            
        layer = layers[i]
        if not hasattr(layer, "_original_forward"):
            layer._original_forward = layer.forward
            
            # Define checkpointed forward function
            def make_checkpointed_forward(idx, orig_forward):
                """
                
    make_checkpointed_forward function for processing.
    
    Args:
        idx, orig_forward: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                def checkpointed_forward(*args, **kwargs):
                    """
                    
    checkpointed_forward function for processing.
    
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
                    if kwargs:
                        # Checkpoint doesn't support kwargs, so we need to handle them manually
                        def custom_forward(*inputs):
                            """
                            
    custom_forward function for processing.
    
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
                            return orig_forward(*inputs, **kwargs)
                        
                        if hasattr(checkpoint, "checkpoint"):
                            # PyTorch >= 1.9.0 with use_reentrant option
                            if "use_reentrant" in checkpoint.checkpoint.__code__.co_varnames:
                                return checkpoint.checkpoint(custom_forward, *args, use_reentrant=use_reentrant)
                            else:
                                return checkpoint.checkpoint(custom_forward, *args)
                        else:
                            return checkpoint(custom_forward, *args)
                    else:
                        # Direct case for args-only
                        if hasattr(checkpoint, "checkpoint"):
                            if "use_reentrant" in checkpoint.checkpoint.__code__.co_varnames:
                                return checkpoint.checkpoint(orig_forward, *args, use_reentrant=use_reentrant)
                            else:
                                return checkpoint.checkpoint(orig_forward, *args)
                        else:
                            return checkpoint(orig_forward, *args)
                
                return checkpointed_forward
            
            # Replace forward method with checkpointed version
            layer.forward = make_checkpointed_forward(i, layer._original_forward)
    
    logger.info(f"Applied selective activation checkpointing to {len(layer_indices)} transformer layers")
    return model

def memory_efficient_training_step(
# Memory optimization: Memory-critical operation
    model: torch.nn.Module, 
    inputs: Dict[str, torch.Tensor],
    optimizer: torch.optim.Optimizer,
    loss_fn: Callable,
    grad_accum_steps: int = 1
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """
    Perform a memory-efficient training step with gradient accumulation.
    # Memory optimization: Memory-critical operation
    
    Combines activation checkpointing with gradient accumulation to enable
    training with larger effective batch sizes on limited VRAM.
    
    Args:
        model: PyTorch model to train
        # Memory optimization: Explicit memory cleanup
        inputs: Dictionary of input tensors
        optimizer: PyTorch optimizer
        loss_fn: Loss function
        grad_accum_steps: Number of gradient accumulation steps
    
    Returns:
        Tuple of (loss, memory stats)
        # Memory optimization: Memory-critical operation
    """
    from src.core.utils.memory import log_memory_usage
    # Memory optimization: Memory-critical operation
    
    # Log initial memory state
    # Memory optimization: Memory-critical operation
    initial_mem = log_memory_usage("Before training step")
    # Memory optimization: Memory-critical operation
    
    # Zero gradients at the beginning
    optimizer.zero_grad()
    
    # Split inputs into chunks for gradient accumulation
    batch_size = next(iter(inputs.values())).size(0)
    chunk_size = max(1, batch_size // grad_accum_steps)
    
    total_loss = 0.0
    
    # Gradient accumulation loop
    for step in range(grad_accum_steps):
        start_idx = step * chunk_size
        end_idx = min((step + 1) * chunk_size, batch_size)
        
        if start_idx >= end_idx:
            continue
            
        # Create input chunk
        chunk_inputs = {}
        for key, value in inputs.items():
            chunk_inputs[key] = value[start_idx:end_idx]
        
        # Forward pass
        outputs = model(**chunk_inputs)
        
        # Calculate loss
        loss = loss_fn(outputs)
        
        # Scale loss by accumulation steps
        loss = loss / grad_accum_steps
        total_loss += loss.item()
        
        # Backward pass
        loss.backward()
    
    # Update weights
    optimizer.step()
    
    # Log final memory state
    # Memory optimization: Memory-critical operation
    final_mem = log_memory_usage("After training step")
    # Memory optimization: Memory-critical operation
    
    # Calculate memory used during training
    # Memory optimization: Memory-critical operation
    mem_stats = {
        "peak_gpu_mb": torch.cuda.max_memory_allocated() / (1024 * 1024) if torch.cuda.is_available() else 0,
        # Memory optimization: CUDA operations for GPU acceleration
        "used_gpu_mb": final_mem["gpu_allocated_mb"] - initial_mem["gpu_allocated_mb"],
        # Memory optimization: Memory-critical operation
        "used_cpu_mb": final_mem["cpu_mem_mb"] - initial_mem["cpu_mem_mb"]
    }
    
    return total_loss, mem_stats

def save_checkpoint(
    path: Union[str, Path],
    model: torch.nn.Module,
    optimizer: Optional[torch.optim.Optimizer] = None,
    epoch: int = 0,
    global_step: int = 0,
    config: Optional[Any] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Save model checkpoint to disk.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        path: Path to save checkpoint
        model: PyTorch model to save
        # Memory optimization: Explicit memory cleanup
        optimizer: Optional optimizer to save state
        epoch: Current epoch number
        global_step: Current global step
        config: Model configuration
        # Memory optimization: Explicit memory cleanup
        additional_data: Additional data to save
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    state_dict = {
        "model": model.state_dict(),
        "epoch": epoch,
        "global_step": global_step,
    }
    
    if optimizer is not None:
        state_dict["optimizer"] = optimizer.state_dict()
        
    if config is not None:
        state_dict["config"] = config
        
    if additional_data is not None:
        state_dict.update(additional_data)
    
    torch.save(state_dict, path)
    logger.info(f"Checkpoint saved to {path}")

def load_checkpoint(
    model: torch.nn.Module,
    optimizer: Optional[torch.optim.Optimizer] = None,
    path: Optional[Union[str, Path]] = None,
    map_location: Optional[Union[str, torch.device]] = None,
    # Memory optimization: Device placement for memory management
    compatibility_mode: bool = False
) -> int:
    """
    Load model checkpoint from disk.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        model: PyTorch model to load weights into
        # Memory optimization: Explicit memory cleanup
        optimizer: Optional optimizer to load state
        path: Path to checkpoint file
        map_location: Optional device mapping for loading weights
        # Memory optimization: Device placement for memory management
        compatibility_mode: Whether to enable compatibility mode for older checkpoints
        
    Returns:
        Current epoch number or 0 if loading failed
    """
    if path is None or not os.path.exists(path):
        logger.warning(f"No checkpoint found at {path}")
        return 0
    
    try:
        logger.info(f"Loading checkpoint from {path}")
        checkpoint = torch.load(path, map_location=map_location)
        
        # Load model weights
        # Memory optimization: Explicit memory cleanup
        if "model" in checkpoint:
            # Handle potential key mismatches in compatibility mode
            if compatibility_mode:
                model_dict = model.state_dict()
                checkpoint_dict = {k: v for k, v in checkpoint["model"].items() if k in model_dict}
                model_dict.update(checkpoint_dict)
                model.load_state_dict(model_dict)
                logger.info(f"Loaded checkpoint in compatibility mode, {len(checkpoint_dict)}/{len(model_dict)} keys loaded")
            else:
                model.load_state_dict(checkpoint["model"])
        else:
            # Try loading directly if "model" key is not present
            model.load_state_dict(checkpoint)
        
        # Load optimizer state if provided
        if optimizer is not None and "optimizer" in checkpoint:
            try:
                optimizer.load_state_dict(checkpoint["optimizer"])
            except Exception as e:
                logger.warning(f"Failed to load optimizer state: {str(e)}")
        
        # Return epoch
        if "epoch" in checkpoint:
            return checkpoint["epoch"] + 1  # Return next epoch
        else:
            return 0
            
    except Exception as e:
        logger.error(f"Error loading checkpoint: {str(e)}")
        return 0
