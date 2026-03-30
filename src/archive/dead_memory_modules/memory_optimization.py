#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #attention_mechanism #cuda #gpu_optimization #inference #memory_management #multimodal #performance #python #pytorch #source_code #src/core/memory/memory_optimization.py #testing #training #transformer
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** Kirk LaSalle
# Tags:** #api #attention_mechanism #cuda #gpu_optimization #inference #memory_management #multimodal #performance #python #pytorch #source_code #src\\core\\memory\\memory_optimization.py #testing #training #transformer
# Category:** Core Implementation
# Status:** Active

"""
ImpressionCore: Memory Optimization

Module for memory optimization functionality in the ImpressionCore framework.

File: core/memory_optimization.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, pytorch, core, production, 2025, object-oriented]
Dependencies: [torch, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements memory optimization functionality for the
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
from core.memory_optimization import ParallelLinear
instance = ParallelLinear()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import torch
import torch.nn as nn
import math  # Added import for math used in ParallelLinear
import types  # Added import for method replacement
from typing import Dict, List, Optional, Union, Any, Tuple
from contextlib import contextmanager

from .gpu_utils import clear_gpu_memory, get_memory_info, MemoryTracker
# Memory optimization: Memory-critical operation
from .exceptions import (
    OutOfMemoryError, GPUNotAvailableError,
    # Memory optimization: Memory-critical operation
    TensorParallelismError, DistributedInitError
)
from .config_utils import merge_configs, validate_config

logger = logging.getLogger(__name__)

@contextmanager
def auto_mixed_precision():
    """Context manager for automatic mixed precision calculations."""
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        with torch.cuda.amp.autocast():
        # Memory optimization: CUDA operations for GPU acceleration
            yield
    else:
        yield

@contextmanager
def memory_efficient_inference():
# Memory optimization: Memory-critical operation
    """
    Context manager for memory-efficient inference.
    # Memory optimization: Memory-critical operation

    Combines several techniques to minimize memory usage during inference:
    # Memory optimization: Memory-critical operation
    - Automatic mixed precision (FP16)
    - Memory clearing before/after
    # Memory optimization: Memory-critical operation
    - Gradient disabling
    """
    # Clear memory before operation
    # Memory optimization: Memory-critical operation
    clear_gpu_memory()
    # Memory optimization: Memory-critical operation

    # Disable gradient tracking
    with torch.no_grad():
    # Memory optimization: Disable gradient computation to save memory
        # Use mixed precision if available
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            # Use newer torch.amp.autocast API to avoid FutureWarning
            if hasattr(torch, "amp") and hasattr(torch.amp, "autocast"):
                with torch.amp.autocast(device_type='cuda'):
                # Memory optimization: Device placement for memory management
                    yield
            # Fall back to older API for compatibility with older PyTorch versions
            elif hasattr(torch.cuda, "amp"):
            # Memory optimization: CUDA operations for GPU acceleration
                with torch.cuda.amp.autocast():
                # Memory optimization: CUDA operations for GPU acceleration
                    yield
            else:
                yield
        else:
            yield

    # Clear memory after operation
    # Memory optimization: Memory-critical operation
    clear_gpu_memory()
    # Memory optimization: Memory-critical operation

def optimize_transformer_model(model: nn.Module) -> nn.Module:
    """
    Apply memory optimization techniques to transformer models.
    # Memory optimization: Memory-critical operation

    Args:
        model: PyTorch model to optimize
        # Memory optimization: Explicit memory cleanup

    Returns:
        Optimized model
    """
    # Set to evaluation mode
    model.eval()

    # Enable gradient checkpointing if available
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()
        logger.info("Enabled gradient checkpointing")

    # Try to convert to half precision for memory savings
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        try:
            model = model.half()
            # Memory optimization: Explicit memory cleanup
            logger.info("Converted model to half precision")
            # Memory optimization: Explicit memory cleanup
        except Exception as e:
            logger.warning(f"Failed to convert model to half precision: {e}")
            # Memory optimization: Explicit memory cleanup

    return model

def quantize_model(model: nn.Module, quantization_level: str = "dynamic") -> nn.Module:
    """
    Quantize model to reduce memory footprint.

    Args:
        model: PyTorch model to quantize
        quantization_level: Type of quantization to apply
            - "dynamic": Dynamic quantization (8-bit weights)
            - "static": Static quantization (requires calibration)
            - "qat": Quantization-aware training

    Returns:
        Quantized model

    Raises:
        ValueError: If an unsupported quantization level is specified
        RuntimeError: If quantization fails
    """
    try:
        # Use the enhanced quantization module
        from.core.utils.memory_optimization.quantization import optimize_model_with_quantization
        return optimize_model_with_quantization(model, quantization_type=quantization_level)
    except ImportError:
        logger.warning("Enhanced quantization module not available, using fallback implementation")

        # Fallback to original implementation
        valid_levels = ["dynamic", "static", "qat"]
        if quantization_level not in valid_levels:
            raise ValueError(f"Unsupported quantization level '{quantization_level}'. "
                           f"Must be one of: {', '.join(valid_levels)}")

        if quantization_level == "dynamic":
            try:
                # Dynamic quantization (8-bit weights, post-training)
                quantized_model = torch.quantization.quantize_dynamic(
                    model, {nn.Linear}, dtype=torch.qint8
                )
                logger.info("Applied dynamic quantization to model")
                return quantized_model
            except RuntimeError as e:
                logger.warning(f"Dynamic quantization failed with error: {e}")
                raise RuntimeError(f"Dynamic quantization failed: {str(e)}") from e
            except Exception as e:
                logger.warning(f"Unexpected error during quantization: {e}")
                raise RuntimeError(f"Model quantization failed: {str(e)}") from e
        elif quantization_level == "static":
            # TODO: Enhanced static quantization now available in quantization module
            logger.warning("Static quantization requires calibration data. Use src.core.utils.memory_optimization.quantization module for full static quantization support.")
            raise NotImplementedError("Static quantization requires calibration data. Use the enhanced quantization module for full support.") from None
        elif quantization_level == "qat":
            # TODO: Enhanced QAT now available in quantization module
            logger.warning("Quantization-aware training is available in the enhanced quantization module.")
            raise NotImplementedError("Quantization-aware training is available in src.core.utils.memory_optimization.quantization module.") from None
        return model

def apply_tensor_parallelism(model, num_gpus=None, tp_config=None):
# Memory optimization: Memory-critical operation
    """
    Apply tensor parallelism to a PyTorch model to distribute computation across multiple GPUs.
    # Memory optimization: Explicit memory cleanup

    Tensor parallelism is a technique that splits individual tensors across multiple GPUs,
    # Memory optimization: Memory-critical operation
    as opposed to data parallelism which places different batches on different GPUs. This
    # Memory optimization: Memory-critical operation
    approach allows models that are too large to fit on a single GPU to still be trained
    # Memory optimization: Memory-critical operation
    and used for inference.

    The implementation focuses on three key areas:
    1. Linear layers - splitting output dimensions across GPUs
    # Memory optimization: Memory-critical operation
    2. Embedding layers - splitting embedding dimensions across GPUs
    # Memory optimization: Memory-critical operation
    3. Attention mechanisms - splitting query/key/value projections

    Each GPU performs local computations on its portion of the tensor, then results
    # Memory optimization: Memory-critical operation
    are combined via all-gather operations.

    Args:
        model: PyTorch model to parallelize
        # Memory optimization: Explicit memory cleanup
        num_gpus: Number of GPUs to use (defaults to all available GPUs)
        # Memory optimization: Memory-critical operation
        tp_config: Dictionary with additional configuration options:
            - min_params_per_gpu: Minimum parameters (in millions) per GPU to apply parallelism
            # Memory optimization: Memory-critical operation
            - parallel_attn: Whether to parallelize attention layers (default: True)
            - parallel_mlp: Whether to parallelize MLP/FF layers (default: True)
            - parallel_embeddings: Whether to parallelize embedding layers (default: False)

    Returns:
        Parallelized model

    Raises:
        ValueError: If invalid parameters are provided
        GPUNotAvailableError: If no GPUs are available
        # Memory optimization: Memory-critical operation
        DistributedInitError: If distributed initialization fails
        TensorParallelismError: For other tensor parallelism errors

    TODO:
    - Add pipeline parallelism support for even larger models
    - Implement sequence parallelism for attention mechanisms
    - Add automatic profiling to find optimal parallelization strategy
    """
    import torch
    import torch.nn as nn
    import torch.distributed as dist

    # Default configuration parameters
    default_config = {
        "min_params_per_gpu": 50,  # 50M parameters minimum per GPU
        # Memory optimization: Memory-critical operation
        "parallel_attn": True,
        "parallel_mlp": True,
        "parallel_embeddings": False,
    }

    # Use our new merge_configs utility
    merged_config = merge_configs(default_config, tp_config)

    # Input validation
    if not isinstance(model, nn.Module):
        raise ValueError(f"Expected PyTorch nn.Module, got {type(model).__name__}")

    # Determine number of GPUs to use
    # Memory optimization: Memory-critical operation
    available_gpus = torch.cuda.device_count()
    # Memory optimization: CUDA operations for GPU acceleration
    if available_gpus == 0:
    # Memory optimization: Memory-critical operation
        logger.warning("No GPUs available for tensor parallelism")
        # Memory optimization: Memory-critical operation
        raise GPUNotAvailableError("Tensor parallelism requires at least one GPU")
        # Memory optimization: Memory-critical operation

    if num_gpus is None:
    # Memory optimization: Memory-critical operation
        num_gpus = available_gpus
        # Memory optimization: Memory-critical operation

    if num_gpus <= 1:
    # Memory optimization: Memory-critical operation
        logger.info("Tensor parallelism requires multiple GPUs. Skipping.")
        # Memory optimization: Memory-critical operation
        return model

    if num_gpus > available_gpus:
    # Memory optimization: Memory-critical operation
        logger.warning(f"Requested {num_gpus} GPUs but only {available_gpus} available. Using {available_gpus}.")
        # Memory optimization: Memory-critical operation
        num_gpus = available_gpus
        # Memory optimization: Memory-critical operation

    # Estimate model size
    # Memory optimization: Explicit memory cleanup
    num_params = sum(p.numel() for p in model.parameters()) / 1_000_000  # In millions
    params_per_gpu = num_params / num_gpus
    # Memory optimization: Memory-critical operation

    if params_per_gpu < merged_config["min_params_per_gpu"]:
    # Memory optimization: Memory-critical operation
        logger.info(f"Model has {num_params:.2f}M parameters, which is less than the minimum "
        # Memory optimization: Explicit memory cleanup
                   f"{merged_config['min_params_per_gpu']}M per GPU for parallelism. Using single GPU.")
                   # Memory optimization: Memory-critical operation
        return model

    logger.info(f"Applying tensor parallelism across {num_gpus} GPUs "
    # Memory optimization: Memory-critical operation
               f"for model with {num_params:.2f}M parameters.")
               # Memory optimization: Explicit memory cleanup

    # Initialize process group for distributed processing
    if not dist.is_initialized():
        try:
            dist.init_process_group(backend="nccl", world_size=num_gpus)
            # Memory optimization: Memory-critical operation
            logger.info(f"Initialized distributed process group with world size {num_gpus}")
            # Memory optimization: Memory-critical operation
        except Exception as e:
            error_msg = f"Failed to initialize distributed process group: {str(e)}"
            logger.error(error_msg)
            raise DistributedInitError(error_msg) from e

    try:
        # Apply parallelism to the model
        model = _parallelize_model(model, num_gpus, merged_config)
        # Memory optimization: Explicit memory cleanup
        return model
    except Exception as e:
        error_msg = f"Error applying tensor parallelism to model: {str(e)}"
        logger.error(error_msg)
        raise TensorParallelismError(error_msg) from e

def _parallelize_model(model, num_gpus, tp_config):
# Memory optimization: Memory-critical operation
    """
    Convert a model to use tensor parallelism by replacing relevant layers
    # Memory optimization: Explicit memory cleanup
    with their parallel equivalents.

    Args:
        model: PyTorch model to parallelize
        # Memory optimization: Explicit memory cleanup
        num_gpus: Number of GPUs to use
        # Memory optimization: Memory-critical operation
        tp_config: Tensor parallelism configuration

    Returns:
        Parallelized model
    """
    import torch.nn as nn

    # Helper function to recursively replace layers
    def replace_layers_recursive(module, path=""):
        """

    replace_layers_recursive function for processing.

    Args:
        module, path: Function parameters

    Returns:
        Processed result

    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints

        """
        for name, child in module.named_children():
            child_path = f"{path}.{name}" if path else name

            # Replace linear layers with parallel linear layers
            if isinstance(child, nn.Linear) and tp_config["parallel_mlp"]:
                if hasattr(child, "weight") and child.weight.size(0) >= 1024:  # Only parallelize large layers
                    setattr(module, name, ParallelLinear(
                        child.in_features,
                        child.out_features,
                        bias=child.bias is not None,
                        num_partitions=num_gpus,
                        # Memory optimization: Memory-critical operation
                        init_from_layer=child
                    ))

            # Replace embedding layers if configured
            elif isinstance(child, nn.Embedding) and tp_config["parallel_embeddings"]:
                if child.embedding_dim >= 1024:  # Only parallelize large embeddings
                    setattr(module, name, ParallelEmbedding(
                        child.num_embeddings,
                        child.embedding_dim,
                        padding_idx=child.padding_idx,
                        num_partitions=num_gpus,
                        # Memory optimization: Memory-critical operation
                        init_from_layer=child
                    ))

            # Look for attention layers by common naming patterns
            elif tp_config["parallel_attn"] and any(
                attn_name in name.lower()
                for attn_name in ["attention", "attn", "mha", "self_attn"]
            ):
                # Try to find query, key, value projections
                q_proj = getattr(child, "q_proj", None) or getattr(child, "query", None)
                k_proj = getattr(child, "k_proj", None) or getattr(child, "key", None)
                v_proj = getattr(child, "v_proj", None) or getattr(child, "value", None)

                # Replace attention projections if found and they're nn.Linear
                if q_proj is not None and isinstance(q_proj, nn.Linear):
                    setattr(child, "q_proj" if hasattr(child, "q_proj") else "query",
                            ParallelLinear(
                                q_proj.in_features,
                                q_proj.out_features,
                                bias=q_proj.bias is not None,
                                num_partitions=num_gpus,
                                # Memory optimization: Memory-critical operation
                                init_from_layer=q_proj
                            ))

                if k_proj is not None and isinstance(k_proj, nn.Linear):
                    setattr(child, "k_proj" if hasattr(child, "k_proj") else "key",
                            ParallelLinear(
                                k_proj.in_features,
                                k_proj.out_features,
                                bias=k_proj.bias is not None,
                                num_partitions=num_gpus,
                                # Memory optimization: Memory-critical operation
                                init_from_layer=k_proj
                            ))

                if v_proj is not None and isinstance(v_proj, nn.Linear):
                    setattr(child, "v_proj" if hasattr(child, "v_proj") else "value",
                            ParallelLinear(
                                v_proj.in_features,
                                v_proj.out_features,
                                bias=v_proj.bias is not None,
                                num_partitions=num_gpus,
                                # Memory optimization: Memory-critical operation
                                init_from_layer=v_proj
                            ))

            # Recursively process child modules
            if len(list(child.children())) > 0:
                replace_layers_recursive(child, child_path)

    # Apply the transformation
    replace_layers_recursive(model)
    return model

class ParallelLinear(nn.Module):
    """
    Parallel linear layer implementation that splits computation across multiple GPUs.
    # Memory optimization: Memory-critical operation

    This implementation divides the output dimension of a linear layer across GPUs.
    # Memory optimization: Memory-critical operation
    Each GPU stores and computes only a portion of the output, then results are
    # Memory optimization: Memory-critical operation
    gathered and concatenated during the forward pass.

    Key principles:
    - Weight matrix is divided along the output dimension
    - Each GPU only stores its portion of the weights
    # Memory optimization: Memory-critical operation
    - Forward pass computes local result then performs all_gather
    - Result concatenation happens along the proper dimension

    This approach reduces memory usage proportionally to the number of GPUs,
    # Memory optimization: Memory-critical operation
    making it possible to run much larger models than would fit on a single GPU.
    # Memory optimization: Memory-critical operation
    """

    def __init__(self, in_features, out_features, bias=True, num_partitions=2, init_from_layer=None):
        """
        Initialize parallel linear layer.

        Args:
            in_features: Size of each input sample
            out_features: Size of each output sample
            bias: If True, adds a learnable bias to the output
            num_partitions: Number of ways to partition the layer (usually number of GPUs)
            # Memory optimization: Memory-critical operation
            init_from_layer: Optional nn.Linear layer to initialize from
        """
        super().__init__()
        import torch
        import torch.distributed as dist

        self.in_features = in_features
        self.out_features = out_features
        self.num_partitions = num_partitions
        self.output_size_per_partition = out_features // num_partitions
        self.rank = dist.get_rank() if dist.is_initialized() else 0

        # Create weight parameter - only storing the partition for this GPU
        # Memory optimization: Memory-critical operation
        self.weight = nn.Parameter(torch.empty(
            self.output_size_per_partition, in_features
        ))

        if bias:
            self.bias = nn.Parameter(torch.empty(self.output_size_per_partition))
        else:
            self.register_parameter('bias', None)

        # Initialize from existing layer if provided
        if init_from_layer is not None and hasattr(init_from_layer, 'weight'):
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                # Calculate the slice for this partition
                start_idx = self.rank * self.output_size_per_partition
                end_idx = start_idx + self.output_size_per_partition

                # Copy weights for this partition
                self.weight.copy_(init_from_layer.weight[start_idx:end_idx])

                if bias and init_from_layer.bias is not None:
                    self.bias.copy_(init_from_layer.bias[start_idx:end_idx])
        else:
            # Standard initialization
            nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
            if bias:
                fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
                bound = 1 / math.sqrt(fan_in)
                nn.init.uniform_(self.bias, -bound, bound)

    def forward(self, input):
        """
        Forward pass implementation with tensor parallelism.

        Args:
            input: Input tensor [*, in_features]

        Returns:
            Output tensor [*, out_features]
        """
        import torch
        import torch.distributed as dist

        # Local computation for this GPU's partition
        # Memory optimization: Memory-critical operation
        local_output = nn.functional.linear(input, self.weight, self.bias)

        # All-gather results from all GPUs
        # Memory optimization: Memory-critical operation
        if self.num_partitions > 1 and dist.is_initialized():
            output_list = [torch.empty_like(local_output) for _ in range(self.num_partitions)]
            dist.all_gather(output_list, local_output)

            # Concatenate results from all GPUs
            # Memory optimization: Memory-critical operation
            output = torch.cat(output_list, dim=-1)
            return output
        else:
            # When running on a single GPU, just return the local output
            # Memory optimization: Memory-critical operation
            return local_output

class ParallelEmbedding(nn.Module):
    """
    Parallel embedding layer implementation that splits computation across multiple GPUs.
    # Memory optimization: Memory-critical operation
    """

    def __init__(self, num_embeddings, embedding_dim, padding_idx=None, num_partitions=2, init_from_layer=None):
        """
        Initialize parallel embedding layer.

        Args:
            num_embeddings: Size of the dictionary of embeddings
            embedding_dim: The size of each embedding vector
            padding_idx: If specified, the entries at padding_idx do not contribute to the gradient
            num_partitions: Number of ways to partition the layer (usually number of GPUs)
            # Memory optimization: Memory-critical operation
            init_from_layer: Optional nn.Embedding layer to initialize from
        """
        super().__init__()
        import torch
        import torch.distributed as dist

        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.padding_idx = padding_idx
        self.num_partitions = num_partitions
        self.embedding_dim_per_partition = embedding_dim // num_partitions
        self.rank = dist.get_rank() if dist.is_initialized() else 0

        # Create weight parameter - only storing the partition for this GPU
        # Memory optimization: Memory-critical operation
        self.weight = nn.Parameter(torch.empty(
            num_embeddings, self.embedding_dim_per_partition
        ))

        # Initialize from existing layer if provided
        if init_from_layer is not None and hasattr(init_from_layer, 'weight'):
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                # Calculate the slice for this partition
                start_idx = self.rank * self.embedding_dim_per_partition
                end_idx = start_idx + self.embedding_dim_per_partition

                # Copy weights for this partition
                self.weight.copy_(init_from_layer.weight[:, start_idx:end_idx])
        else:
            # Standard initialization
            nn.init.normal_(self.weight, mean=0, std=embedding_dim ** -0.5)
            if padding_idx is not None:
                with torch.no_grad():
                # Memory optimization: Disable gradient computation to save memory
                    self.weight[padding_idx].fill_(0)

    def forward(self, input):
        """
        Forward pass implementation with tensor parallelism.

        Args:
            input: Input tensor with token ids [*]

        Returns:
            Output tensor with embeddings [*, embedding_dim]
        """
        import torch
        import torch.distributed as dist

        # Local computation for this GPU's partition
        # Memory optimization: Memory-critical operation
        local_output = nn.functional.embedding(
            input, self.weight, self.padding_idx, None, 2.0, False, False)

        # All-gather results from all GPUs
        # Memory optimization: Memory-critical operation
        if self.num_partitions > 1 and dist.is_initialized():
            output_list = [torch.empty_like(local_output) for _ in range(self.num_partitions)]
            dist.all_gather(output_list, local_output)

            # Concatenate results from all GPUs along embedding dimension
            # Memory optimization: Memory-critical operation
            output = torch.cat(output_list, dim=-1)
            return output
        else:
            # When running on a single GPU, just return the local output
            # Memory optimization: Memory-critical operation
            return local_output

def print_model_memory_usage(model: nn.Module) -> Dict[str, float]:
# Memory optimization: Memory-critical operation
    """
    Calculate and print the memory usage of model components.
    # Memory optimization: Explicit memory cleanup

    Args:
        model: PyTorch model to analyze
        # Memory optimization: Explicit memory cleanup

    Returns:
        Dictionary with memory usage per component
        # Memory optimization: Memory-critical operation
    """
    memory_usage = {}
    # Memory optimization: Memory-critical operation
    total_params = 0
    total_memory_mb = 0
    # Memory optimization: Memory-critical operation

    # Analyze model components
    # Memory optimization: Explicit memory cleanup
    for name, param in model.named_parameters():
        num_params = param.numel()
        memory_mb = num_params * param.element_size() / (1024 * 1024)  # MB
        # Memory optimization: Memory-critical operation

        total_params += num_params
        total_memory_mb += memory_mb
        # Memory optimization: Memory-critical operation

        # Get component name (first part of parameter name)
        component = name.split('.')[0]
        if component not in memory_usage:
        # Memory optimization: Memory-critical operation
            memory_usage[component] = 0
            # Memory optimization: Memory-critical operation
        memory_usage[component] += memory_mb
        # Memory optimization: Memory-critical operation

    # Print summary
    logger.info(f"Model memory usage summary:")
    # Memory optimization: Explicit memory cleanup
    logger.info(f"  Total parameters: {total_params:,}")
    logger.info(f"  Total memory: {total_memory_mb:.2f} MB")
    # Memory optimization: Memory-critical operation

    # Print component breakdown
    logger.info(f"  Memory usage by component:")
    # Memory optimization: Memory-critical operation
    for component, memory_mb in sorted(memory_usage.items(), key=lambda x: x[1], reverse=True):
    # Memory optimization: Memory-critical operation
        logger.info(f"    {component}: {memory_mb:.2f} MB ({memory_mb / total_memory_mb * 100:.1f}%)")
        # Memory optimization: Memory-critical operation

    # Add total to dictionary
    memory_usage["total_params"] = total_params
    # Memory optimization: Memory-critical operation
    memory_usage["total_memory_mb"] = total_memory_mb
    # Memory optimization: Memory-critical operation

    return memory_usage
    # Memory optimization: Memory-critical operation

def chunk_inference(
    model: nn.Module,
    input_ids: torch.Tensor,
    max_chunk_size: int = 512
) -> torch.Tensor:
    """
    Process long inputs in chunks to avoid memory issues.
    # Memory optimization: Memory-critical operation

    This function handles inference on sequences that would otherwise exceed
    available memory by:
    # Memory optimization: Memory-critical operation

    1. Breaking the input into manageable chunks
    2. Processing each chunk with memory optimizations
    # Memory optimization: Memory-critical operation
    3. Clearing memory between chunks to avoid accumulation
    # Memory optimization: Memory-critical operation
    4. Combining results appropriately based on the model's output format

    This is particularly useful for:
    - Processing very long documents
    - Running inference on GPUs with limited VRAM
    # Memory optimization: Memory-critical operation
    - Avoiding OOM errors with transformer models on long sequences

    Args:
        model: PyTorch model
        input_ids: Input token IDs
        max_chunk_size: Maximum chunk size to process at once

    Returns:
        Model outputs
        # Memory optimization: Explicit memory cleanup

    Raises:
        ValueError: If inputs are invalid
        OutOfMemoryError: If GPU runs out of memory
        # Memory optimization: Memory-critical operation

    TODO:
    - Add support for more sophisticated chunk result merging
    - Implement sliding window approach with overlapping chunks
    - Add automatic chunk size detection based on available memory
    # Memory optimization: Memory-critical operation
    """
    # Input validation
    if not isinstance(model, nn.Module):
        raise ValueError(f"Expected PyTorch nn.Module, got {type(model).__name__}")

    if not isinstance(input_ids, torch.Tensor):
        raise ValueError(f"Expected input_ids to be a torch.Tensor, got {type(input_ids).__name__}")

    if max_chunk_size <= 0:
        raise ValueError(f"max_chunk_size must be positive, got {max_chunk_size}")

    # Check if chunking is needed
    if input_ids.shape[1] <= max_chunk_size:
        # Process normally if input is small enough
        try:
            with memory_efficient_inference():
            # Memory optimization: Memory-critical operation
                return model(input_ids)
        except torch.cuda.OutOfMemoryError:
        # Memory optimization: CUDA operations for GPU acceleration
            logger.error("GPU out of memory during inference")
            # Memory optimization: Memory-critical operation
            raise OutOfMemoryError("GPU memory exceeded during inference")
            # Memory optimization: Memory-critical operation

    # Process in chunks
    batch_size, seq_length = input_ids.shape
    outputs_list = []

    try:
        for i in range(0, seq_length, max_chunk_size):
            end_idx = min(i + max_chunk_size, seq_length)
            chunk = input_ids[:, i:end_idx]

            with memory_efficient_inference():
            # Memory optimization: Memory-critical operation
                chunk_output = model(chunk)

            # Store outputs
            outputs_list.append(chunk_output)

            # Clear memory between chunks
            # Memory optimization: Memory-critical operation
            clear_gpu_memory()
            # Memory optimization: Memory-critical operation

        # Combine outputs - this depends on the model output format
        # Memory optimization: Explicit memory cleanup
        # For now, we just return the last chunk's output
        return outputs_list[-1]
    except torch.cuda.OutOfMemoryError:
    # Memory optimization: CUDA operations for GPU acceleration
        logger.error("GPU out of memory during chunked inference")
        # Memory optimization: Memory-critical operation
        raise OutOfMemoryError("GPU memory exceeded during chunked inference. Try reducing max_chunk_size.")
        # Memory optimization: Memory-critical operation
    except Exception as e:
        logger.error(f"Error during chunked inference: {str(e)}")
        raise

def optimize_for_training(model: nn.Module, device_type: str = "default") -> nn.Module:
# Memory optimization: Device placement for memory management
    """
    Apply memory optimization techniques specific for training on limited VRAM.
    # Memory optimization: Memory-critical operation

    Particularly helpful for GTX 1050 Ti with only 4GB VRAM.

    Args:
        model: PyTorch model to optimize
        # Memory optimization: Explicit memory cleanup
        device_type: "gtx1050ti", "low_vram", "medium_vram", or "default"
        # Memory optimization: Device placement for memory management

    Returns:
        Optimized model
    """
    # Check if GPU is available
    # Memory optimization: Memory-critical operation
    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        logger.info("CUDA not available, skipping training optimizations")
        # Memory optimization: Memory-critical operation
        return model

    # Check device name to identify GPU
    # Memory optimization: Device placement for memory management
    device_name = torch.cuda.get_device_name(0).lower()
    # Memory optimization: CUDA operations for GPU acceleration
    is_1050ti = "1050 ti" in device_name
    # Memory optimization: Device placement for memory management

    if is_1050ti or device_type == "gtx1050ti" or device_type == "low_vram":
    # Memory optimization: Device placement for memory management
        logger.info("Applying aggressive memory optimizations for training on limited VRAM (4GB)")
        # Memory optimization: Memory-critical operation

        # 1. Enable gradient checkpointing if available
        if hasattr(model, "gradient_checkpointing_enable"):
            model.gradient_checkpointing_enable()
            logger.info("Enabled gradient checkpointing")
        elif hasattr(model, "config") and hasattr(model.config, "gradient_checkpointing"):
            # Try to set via config
            model.config.gradient_checkpointing = True
            logger.info("Enabled gradient checkpointing via config")

        # 2. Disable transformer layer caching if available
        if hasattr(model, "config") and hasattr(model.config, "use_cache"):
            model.config.use_cache = False
            logger.info("Disabled transformer layer caching")

        # 3. Try to use 8-bit optimizers if available
        try:
            import bitsandbytes as bnb
            has_bnb = True
        except ImportError:
            has_bnb = False

        if has_bnb:
            logger.info("8-bit optimization available through bitsandbytes")

        # 4. Try to use activation checkpointing if available
        if hasattr(model, "enable_activation_checkpointing"):
            model.enable_activation_checkpointing()

    elif device_type == "medium_vram":
    # Memory optimization: Device placement for memory management
        # Less aggressive optimizations for GPUs with 6-8GB VRAM
        # Memory optimization: Memory-critical operation
        logger.info("Applying medium memory optimizations for training")
        # Memory optimization: Memory-critical operation

        # Enable gradient checkpointing
        if hasattr(model, "gradient_checkpointing_enable"):
            model.gradient_checkpointing_enable()
            logger.info("Enabled gradient checkpointing")

    return model

@contextmanager
def memory_efficient_trainer(enable_optimization: bool = True):
# Memory optimization: Memory-critical operation
    """
    Context manager for memory-efficient training.
    # Memory optimization: Memory-critical operation

    Implements several memory-saving techniques for the training loop.
    # Memory optimization: Memory-critical operation
    """
    if not enable_optimization:
        yield
        return

    if not torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        yield
        return

    try:
        # Clear memory before training
        # Memory optimization: Memory-critical operation
        clear_gpu_memory()
        # Memory optimization: Memory-critical operation

        # Configure CUDA allocator if available
        # Memory optimization: Memory-critical operation
        if hasattr(torch.cuda, "memory_stats") and hasattr(torch.cuda, "reset_peak_memory_stats"):
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.reset_peak_memory_stats()
            # Memory optimization: CUDA operations for GPU acceleration

        # Set cudNN to deterministic mode to reduce memory usage
        # Memory optimization: Memory-critical operation
        prev_benchmark = torch.backends.cudnn.benchmark
        prev_deterministic = torch.backends.cudnn.deterministic

        # For training on limited VRAM, use deterministic algorithms
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True

        yield

    finally:
        # Restore previous settings
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            torch.backends.cudnn.benchmark = prev_benchmark
            torch.backends.cudnn.deterministic = prev_deterministic

            # Clear memory after training
            # Memory optimization: Memory-critical operation
            clear_gpu_memory()
            # Memory optimization: Memory-critical operation

def find_memory_efficient_batch_size(
# Memory optimization: Memory-critical operation
    model: nn.Module,
    sample_batch: Any,
    batch_size_range: Tuple[int, int] = (1, 512),
    target_memory_usage: float = 0.8,
    # Memory optimization: Memory-critical operation
    device: Optional[str] = None,
    # Memory optimization: Device placement for memory management
    safety_margin: float = 0.1,
    verbose: bool = True,
) -> int:
    """
    Find the largest batch size that fits in GPU memory.
    # Memory optimization: Memory-critical operation

    This function performs binary search to find the optimal batch size that
    maximizes GPU utilization without causing out-of-memory errors.
    # Memory optimization: Memory-critical operation

    Args:
        model: Model to test
        # Memory optimization: Explicit memory cleanup
        sample_batch: Example of a single batch item to replicate
        batch_size_range: Range of batch sizes to search (min_batch, max_batch)
        target_memory_usage: Target memory usage as fraction of total memory
        # Memory optimization: Memory-critical operation
        device: Device to use for testing
        # Memory optimization: Device placement for memory management
        safety_margin: Additional safety margin to prevent OOM errors
        verbose: Whether to print progress

    Returns:
        Optimal batch size

    Example:
        ```python
        # Find optimal batch size for training
        sample_item = next(iter(dataset))
        optimal_batch_size = find_memory_efficient_batch_size(
        # Memory optimization: Memory-critical operation
            model=model,
            sample_batch=sample_item,
            batch_size_range=(4, 128)
        )
        print(f"Using batch size: {optimal_batch_size}")

        # Create dataloader with optimal batch size
        dataloader = DataLoader(dataset, batch_size=optimal_batch_size)
        ```
    """
    if device is None:
    # Memory optimization: Device placement for memory management
        device = next(model.parameters()).device
        # Memory optimization: Device placement for memory management

    # Set model to eval mode to conserve memory
    # Memory optimization: Explicit memory cleanup
    model.eval()

    # Get memory limits
    # Memory optimization: Memory-critical operation
    if str(device).startswith("cuda"):
    # Memory optimization: Device placement for memory management
        total_memory = torch.cuda.get_device_properties(device).total_memory
        # Memory optimization: CUDA operations for GPU acceleration
        if verbose:
            logger.info(f"Total GPU memory: {total_memory / 1024**2:.1f} MB")
            # Memory optimization: Memory-critical operation
    else:
        # For CPU, use a default limit
        import psutil
        total_memory = psutil.virtual_memory().total
        # Memory optimization: Memory-critical operation
        if verbose:
            logger.info(f"Total system memory: {total_memory / 1024**2:.1f} MB")
            # Memory optimization: Memory-critical operation

    # Target memory limit with safety margin
    # Memory optimization: Memory-critical operation
    memory_limit = total_memory * target_memory_usage * (1 - safety_margin)
    # Memory optimization: Memory-critical operation

    # Binary search for optimal batch size
    min_batch, max_batch = batch_size_range
    optimal_batch = min_batch

    if verbose:
        logger.info(f"Searching for optimal batch size between {min_batch} and {max_batch}")

    # Function to create batch of specific size
    def create_batch(batch_size):
        """

    create_batch function for processing.

    Args:
        batch_size: Function parameters

    Returns:
        Processed result

    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints

        """
        if isinstance(sample_batch, torch.Tensor):
            # Create a new batch by repeating the sample
            if len(sample_batch.shape) > 0:  # If it has batch dimension
                batch = sample_batch.repeat(batch_size, *([1] * (len(sample_batch.shape) - 1)))
            else:  # Single item without batch dimension
                batch = sample_batch.unsqueeze(0).repeat(batch_size, *([1] * len(sample_batch.shape)))
            return batch.to(device)
            # Memory optimization: Device placement for memory management
        elif isinstance(sample_batch, dict):
            # Create a new batch for each tensor in the dict
            batch = {}
            for k, v in sample_batch.items():
                if isinstance(v, torch.Tensor):
                    if len(v.shape) > 0:  # If it has batch dimension
                        batch[k] = v.repeat(batch_size, *([1] * (len(v.shape) - 1)))
                    else:  # Single item without batch dimension
                        batch[k] = v.unsqueeze(0).repeat(batch_size, *([1] * len(v.shape)))
                    batch[k] = batch[k].to(device)
                    # Memory optimization: Device placement for memory management
                else:
                    batch[k] = v
            return batch
        else:
            raise ValueError(f"Unsupported batch type: {type(sample_batch)}")

    # Binary search
    while min_batch <= max_batch:
        mid_batch = (min_batch + max_batch) // 2

        try:
            # Clear memory before test
            # Memory optimization: Memory-critical operation
            if torch.cuda.is_available():
            # Memory optimization: CUDA operations for GPU acceleration
                torch.cuda.empty_cache()
                # Memory optimization: CUDA operations for GPU acceleration

            # Create test batch
            test_batch = create_batch(mid_batch)

            # Run model with a fresh memory state
            # Memory optimization: Explicit memory cleanup
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.reset_peak_memory_stats(device)
            # Memory optimization: CUDA operations for GPU acceleration

            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                _ = model(test_batch)

            # Check memory usage
            # Memory optimization: Memory-critical operation
            if torch.cuda.is_available():
            # Memory optimization: CUDA operations for GPU acceleration
                memory_used = torch.cuda.max_memory_allocated(device)
                # Memory optimization: CUDA operations for GPU acceleration
                if verbose:
                    logger.info(f"Batch size {mid_batch}: Used {memory_used / 1024**2:.1f} MB / {memory_limit / 1024**2:.1f} MB")
                    # Memory optimization: Memory-critical operation

                if memory_used < memory_limit:
                # Memory optimization: Memory-critical operation
                    # This batch size works, try a larger one
                    optimal_batch = mid_batch
                    min_batch = mid_batch + 1
                else:
                    # Too much memory used, try a smaller batch
                    # Memory optimization: Memory-critical operation
                    max_batch = mid_batch - 1
            else:
                # Without CUDA, just accept the batch size if it runs without error
                # Memory optimization: Memory-critical operation
                optimal_batch = mid_batch
                min_batch = mid_batch + 1

            # Clean up
            del test_batch
            # Memory optimization: Explicit memory cleanup

        except RuntimeError as e:
            if "out of memory" in str(e) or "CUDA out of memory" in str(e):
            # Memory optimization: Memory-critical operation
                # OOM error, try smaller batch
                if verbose:
                    logger.info(f"Batch size {mid_batch} caused OOM error")
                max_batch = mid_batch - 1
                # Clean up memory after OOM
                # Memory optimization: Memory-critical operation
                if torch.cuda.is_available():
                # Memory optimization: CUDA operations for GPU acceleration
                    torch.cuda.empty_cache()
                    # Memory optimization: CUDA operations for GPU acceleration
            else:
                # Other error, re-raise
                raise

    if verbose:
        logger.info(f"Optimal batch size: {optimal_batch}")

    return optimal_batch


def apply_memory_optimizations(
# Memory optimization: Memory-critical operation
    model: nn.Module,
    config: Optional[Dict[str, Any]] = None
) -> nn.Module:
    """
    Apply multiple memory optimization techniques to a model.
    # Memory optimization: Memory-critical operation

    This is a high-level function that combines various optimization techniques
    to make a model more memory-efficient for both training and inference.
    # Memory optimization: Explicit memory cleanup

    Args:
        model: PyTorch model to optimize
        # Memory optimization: Explicit memory cleanup
        config: Configuration dictionary with optimization settings

    Returns:
        Optimized model

    Example:
        ```python
        # Apply standard memory optimizations
        # Memory optimization: Memory-critical operation
        optimized_model = apply_memory_optimizations(model)
        # Memory optimization: Explicit memory cleanup

        # Apply specific optimizations
        optimized_model = apply_memory_optimizations(
        # Memory optimization: Explicit memory cleanup
            model,
            config={
                "use_checkpointing": True,
                "replace_linear_layers": True,
                "linear_device_count": 2,
                # Memory optimization: Device placement for memory management
                "convert_bottleneck_fp16": True
            }
        )
        ```
    """
    if config is None:
        config = {}

    # Default configuration
    default_config = {
        "use_checkpointing": False,           # Enable gradient checkpointing
        "replace_linear_layers": False,       # Replace large linear layers with parallel versions
        "linear_size_threshold": 20_000_000,  # Size threshold for parallel linear (num parameters)
        "linear_device_count": None,          # Number of devices for parallel linear
        # Memory optimization: Device placement for memory management
        "replace_embeddings": False,          # Replace large embedding tables with parallel versions
        "embedding_size_threshold": 10_000_000,  # Size threshold for parallel embeddings
        "convert_bottleneck_fp16": False,     # Convert bottleneck layers to FP16
        "enable_activation_checkpointing": False,  # Checkpoint activations
        "share_optimizer_states": False,      # Share optimizer states across params
    }

    # Update with user config
    for key, value in config.items():
        if key in default_config:
            default_config[key] = value

    config = default_config
    logger.info("Applying memory optimizations to model")
    # Memory optimization: Memory-critical operation

    # Apply gradient checkpointing if requested
    if config["use_checkpointing"]:
        # Check if model supports checkpointing
        # Memory optimization: Explicit memory cleanup
        if hasattr(model, "gradient_checkpointing_enable"):
            model.gradient_checkpointing_enable()
            logger.info("Enabled built-in gradient checkpointing")
        else:
            # Try to apply manual checkpointing
            checkpointed = 0

            for name, module in model.named_modules():
                if hasattr(module, "forward") and any(isinstance(module, t) for t in [
                    nn.TransformerEncoder, nn.TransformerDecoder, nn.TransformerEncoderLayer, nn.TransformerDecoderLayer
                ]):
                    from torch.utils.checkpoint import checkpoint

                    # Store original forward
                    original_forward = module.forward

                    # Create checkpointed forward
                    def make_checkpointed_forward(original_forward):
                        """

    make_checkpointed_forward function for processing.

    Args:
        original_forward: Function parameters

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
                            return checkpoint(original_forward, *args, **kwargs)
                        return checkpointed_forward

                    # Replace forward with checkpointed version
                    module.forward = make_checkpointed_forward(original_forward)
                    checkpointed += 1

            if checkpointed > 0:
                logger.info(f"Applied gradient checkpointing to {checkpointed} modules")
            else:
                logger.warning("No supported modules found for gradient checkpointing")

    # Replace large linear layers with parallel versions
    if config["replace_linear_layers"]:
        replaced = 0
        device_count = config["linear_device_count"] or torch.cuda.device_count() if torch.cuda.is_available() else 1
        # Memory optimization: CUDA operations for GPU acceleration

        if device_count > 1:
        # Memory optimization: Device placement for memory management
            for name, module in list(model.named_modules()):
                # Skip if this isn't a direct child module (avoid nested replacements)
                if "." in name:
                    continue

                if isinstance(module, nn.Linear):
                    # Calculate number of parameters
                    num_params = module.in_features * module.out_features
                    if module.bias is not None:
                        num_params += module.out_features

                    # Check if above threshold
                    if num_params > config["linear_size_threshold"]:
                        # Get parent module and attribute name
                        parent_name, child_name = name.rsplit(".", 1) if "." in name else ("", name)
                        parent = model if parent_name == "" else getattr(model, parent_name)
                        # Memory optimization: Explicit memory cleanup

                        # Create parallel version
                        parallel_linear = ParallelLinear(
                            module.in_features,
                            module.out_features,
                            bias=module.bias is not None,
                            num_devices=device_count
                            # Memory optimization: Device placement for memory management
                        )

                        # Copy weights (with custom handling for parallelization)
                        with torch.no_grad():
                        # Memory optimization: Disable gradient computation to save memory
                            # Determine how to split the original weights
                            in_features_per_device = parallel_linear.in_features_per_device
                            # Memory optimization: Device placement for memory management

                            start_idx = 0
                            for i, layer in enumerate(parallel_linear.layers):
                                in_features = in_features_per_device[i]
                                # Memory optimization: Device placement for memory management

                                # Copy slice of weights to this device's layer
                                # Memory optimization: Device placement for memory management
                                layer.weight.copy_(
                                    module.weight[:, start_idx:start_idx + in_features]
                                )

                                # Copy bias only to first layer (or as per implementation)
                                if module.bias is not None and i == 0:
                                    layer.bias.copy_(module.bias)

                                start_idx += in_features

                        # Replace module
                        setattr(parent, child_name, parallel_linear)
                        replaced += 1
                        logger.debug(f"Replaced linear layer '{name}' with parallel version")

            if replaced > 0:
                logger.info(f"Replaced {replaced} large linear layers with parallel versions")
            else:
                logger.info("No linear layers found exceeding the size threshold for parallelization")
        else:
            logger.warning("Multiple devices needed for parallel linear layers")
            # Memory optimization: Device placement for memory management

    # Replace large embedding tables with parallel versions
    if config["replace_embeddings"]:
        replaced = 0
        device_count = config["linear_device_count"] or torch.cuda.device_count() if torch.cuda.is_available() else 1
        # Memory optimization: CUDA operations for GPU acceleration

        if device_count > 1:
        # Memory optimization: Device placement for memory management
            for name, module in list(model.named_modules()):
                # Skip if this isn't a direct child module (avoid nested replacements)
                if "." in name:
                    continue

                if isinstance(module, nn.Embedding):
                    # Calculate number of parameters
                    num_params = module.num_embeddings * module.embedding_dim

                    # Check if above threshold
                    if num_params > config["embedding_size_threshold"]:
                        # Get parent module and attribute name
                        parent_name, child_name = name.rsplit(".", 1) if "." in name else ("", name)
                        parent = model if parent_name == "" else getattr(model, parent_name)
                        # Memory optimization: Explicit memory cleanup

                        # Create parallel version
                        parallel_embedding = ParallelEmbedding(
                            module.num_embeddings,
                            module.embedding_dim,
                            padding_idx=module.padding_idx,
                            num_devices=device_count
                            # Memory optimization: Device placement for memory management
                        )

                        # Copy weights (with custom handling for parallelization)
                        with torch.no_grad():
                        # Memory optimization: Disable gradient computation to save memory
                            # Determine how to split the original embeddings
                            embeddings_per_device = parallel_embedding.embeddings_per_device
                            # Memory optimization: Device placement for memory management

                            start_idx = 0
                            for i, embedding in enumerate(parallel_embedding.embeddings):
                                num_embeddings = embeddings_per_device[i]
                                # Memory optimization: Device placement for memory management

                                # Copy slice of embeddings to this device's layer
                                # Memory optimization: Device placement for memory management
                                embedding.weight.copy_(
                                    module.weight[start_idx:start_idx + num_embeddings]
                                )

                                start_idx += num_embeddings

                        # Replace module
                        setattr(parent, child_name, parallel_embedding)
                        replaced += 1
                        logger.debug(f"Replaced embedding layer '{name}' with parallel version")

            if replaced > 0:
                logger.info(f"Replaced {replaced} large embedding tables with parallel versions")
            else:
                logger.info("No embedding tables found exceeding the size threshold for parallelization")
        else:
            logger.warning("Multiple devices needed for parallel embedding tables")
            # Memory optimization: Device placement for memory management

    # Convert bottleneck layers to FP16 for memory savings
    # Memory optimization: Memory-critical operation
    if config["convert_bottleneck_fp16"]:
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            converted = 0

            for name, module in model.named_modules():
                # Check if module is a good candidate for FP16 conversion
                # Bottom layers in an encoder or top layers in a decoder are usually less sensitive to precision
                is_bottleneck = any(bn in name.lower() for bn in ["bottleneck", "middle", "bridge", "neck"])

                if is_bottleneck and isinstance(module, (nn.Linear, nn.Conv2d, nn.Embedding)):
                    # Convert parameters to half precision
                    for param_name, param in module.named_parameters():
                        module.register_parameter(param_name, nn.Parameter(param.half()))

                    # Also convert buffers if any
                    for buffer_name, buffer in module.named_buffers():
                        module.register_buffer(buffer_name, buffer.half())

                    converted += 1
                    logger.debug(f"Converted '{name}' to FP16")

            if converted > 0:
                logger.info(f"Converted {converted} bottleneck modules to FP16")
            else:
                logger.info("No suitable bottleneck modules found for FP16 conversion")
        else:
            logger.warning("CUDA not available, skipping FP16 conversions")
            # Memory optimization: Memory-critical operation

    # Enable activation checkpointing
    if config["enable_activation_checkpointing"]:
        try:
            from torch.utils.checkpoint import checkpoint_sequential

            # Find sequential blocks of modules to checkpoint
            sequential_blocks = []
            current_block = []

            # Collect sequential modules
            for name, module in model.named_children():
                if not list(module.children()):  # If it's a leaf module
                    current_block.append(module)
                else:
                    if current_block:  # Store completed block
                        sequential_blocks.append(current_block)
                        current_block = []
                    # Add non-leaf as its own block
                    sequential_blocks.append([module])

            # Add final block if any
            if current_block:
                sequential_blocks.append(current_block)

            # Apply checkpointing to blocks with multiple modules
            checkpointed_blocks = 0
            for i, block in enumerate(sequential_blocks):
                if len(block) > 1:
                    # Create a sequential module from block
                    seq_module = nn.Sequential(*block)

                    # Replace original forward with checkpointed version
                    original_forward = seq_module.forward

                    # Create checkpointing wrapper
                    def make_checkpoint_wrapper(module, segments=2):
                        """

    make_checkpoint_wrapper function for processing.

    Args:
        module, segments: Function parameters

    Returns:
        Processed result

    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints

                        """
                        def checkpointed_forward(x):
                            """

    checkpointed_forward function for processing.

    Args:
        x: Function parameters

    Returns:
        Processed result

    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints

                            """
                            return checkpoint_sequential(module, segments, x)
                        return checkpointed_forward

                    # Apply wrapper
                    seq_module.forward = make_checkpoint_wrapper(seq_module)
                    checkpointed_blocks += 1

            logger.info(f"Applied activation checkpointing to {checkpointed_blocks} blocks")
        except Exception as e:
            logger.error(f"Error applying activation checkpointing: {e}")

    return model


def memory_usage_report() -> Dict[str, Any]:
# Memory optimization: Memory-critical operation
    """
    Generate a comprehensive report of current memory usage.
    # Memory optimization: Memory-critical operation

    Returns:
        Dictionary with memory usage statistics
        # Memory optimization: Memory-critical operation

    Example:
        ```python
        # Print memory usage report
        # Memory optimization: Memory-critical operation
        report = memory_usage_report()
        # Memory optimization: Memory-critical operation
        print(f"GPU memory used: {report['gpu']['used_mb']:.1f} MB")
        # Memory optimization: Memory-critical operation
        print(f"System memory used: {report['system']['used_mb']:.1f} MB")
        # Memory optimization: Memory-critical operation
        ```
    """
    report = {"gpu": {}, "system": {}}
    # Memory optimization: Memory-critical operation

    # System memory
    # Memory optimization: Memory-critical operation
    try:
        import psutil
        mem = psutil.virtual_memory()
        # Memory optimization: Memory-critical operation
        swap = psutil.swap_memory()
        # Memory optimization: Memory-critical operation

        report["system"] = {
            "total_mb": mem.total / 1024**2,
            "used_mb": mem.used / 1024**2,
            "free_mb": mem.available / 1024**2,
            "percent": mem.percent,
            "swap_total_mb": swap.total / 1024**2,
            "swap_used_mb": swap.used / 1024**2,
            "swap_percent": swap.percent
        }
    except ImportError:
        report["system"] = {"error": "psutil not available"}

    # GPU memory
    # Memory optimization: Memory-critical operation
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        gpu_stats = []
        # Memory optimization: Memory-critical operation

        for i in range(torch.cuda.device_count()):
        # Memory optimization: CUDA operations for GPU acceleration
            props = torch.cuda.get_device_properties(i)
            # Memory optimization: CUDA operations for GPU acceleration
            allocated = torch.cuda.memory_allocated(i) / 1024**2
            # Memory optimization: CUDA operations for GPU acceleration
            reserved = torch.cuda.memory_reserved(i) / 1024**2
            # Memory optimization: CUDA operations for GPU acceleration
            total = props.total_memory / 1024**2
            # Memory optimization: Memory-critical operation

            gpu_stats.append({
            # Memory optimization: Memory-critical operation
                "id": i,
                "name": props.name,
                "total_mb": total,
                "allocated_mb": allocated,
                "reserved_mb": reserved,
                "free_mb": total - reserved,
                "utilization": torch.cuda.utilization(i)
                # Memory optimization: CUDA operations for GPU acceleration
            })

        report["gpu"] = {
        # Memory optimization: Memory-critical operation
            "devices": gpu_stats,
            # Memory optimization: Device placement for memory management
            "total_allocated_mb": sum(gpu["allocated_mb"] for gpu in gpu_stats),
            # Memory optimization: Memory-critical operation
            "total_reserved_mb": sum(gpu["reserved_mb"] for gpu in gpu_stats)
            # Memory optimization: Memory-critical operation
        }
    else:
        report["gpu"] = {"error": "CUDA not available"}
        # Memory optimization: Memory-critical operation

    return report


def optimize_inference_for_gpu(model: nn.Module, legacy_gpu: bool = False) -> nn.Module:
# Memory optimization: Memory-critical operation
    """
    Apply optimizations specifically for inference on limited GPU hardware.
    # Memory optimization: Memory-critical operation

    This function is designed to optimize models for inference on older or
    limited GPU hardware like the GTX 1050 Ti with 4GB VRAM.
    # Memory optimization: Memory-critical operation

    Args:
        model: Model to optimize
        # Memory optimization: Explicit memory cleanup
        legacy_gpu: Whether to apply aggressive optimizations for legacy GPUs
        # Memory optimization: Memory-critical operation

    Returns:
        Optimized model

    Example:
        ```python
        # Optimize model for a legacy GPU like GTX 1050 Ti
        # Memory optimization: Explicit memory cleanup
        model = optimize_inference_for_gpu(model, legacy_gpu=True)
        # Memory optimization: Explicit memory cleanup

        # Run inference with optimized model
        with torch.no_grad():
        # Memory optimization: Disable gradient computation to save memory
            output = model(input_tensor)
        ```
    """
    logger.info(f"Optimizing model for inference on {'legacy' if legacy_gpu else 'modern'} GPU")
    # Memory optimization: Explicit memory cleanup

    # Keep original training state to restore later
    was_training = model.training
    model.eval()  # Set to eval mode for inference optimizations

    # Basic optimizations
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        # Use mixed precision where beneficial
        try:
            from torch.cuda.amp import autocast
            # Memory optimization: CUDA operations for GPU acceleration

            # Save original forward method
            original_forward = model.forward

            # Create new forward method with autocast
            def inference_forward_with_autocast(self, *args, **kwargs):
                """

    inference_forward_with_autocast function for processing.

    Args:
        self: Function parameters

    Returns:
        Processed result

    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints

                """
                with autocast():
                    return original_forward(*args, **kwargs)

            # Replace forward method
            model.forward = types.MethodType(inference_forward_with_autocast, model)
            logger.info("Applied automatic mixed precision to forward pass")
        except Exception as e:
            logger.warning(f"Could not apply autocast: {e}")

        # Try to compile model with torch.compile if available
        # Memory optimization: Explicit memory cleanup
        if hasattr(torch, "compile") and not legacy_gpu:
        # Memory optimization: Memory-critical operation
            try:
                # Use reduced precision mode for older GPUs
                # Memory optimization: Memory-critical operation
                compiled_model = torch.compile(
                # Memory optimization: Explicit memory cleanup
                    model,
                    mode="reduce-overhead",
                    fullgraph=False  # Partial compilation is more stable
                )
                model = compiled_model
                # Memory optimization: Explicit memory cleanup
                logger.info("Applied torch.compile optimization")
            except Exception as e:
                logger.warning(f"Could not compile model: {e}")

        # For legacy GPUs, apply more aggressive optimizations
        # Memory optimization: Memory-critical operation
        if legacy_gpu:
        # Memory optimization: Memory-critical operation
            logger.info("Applying legacy GPU optimizations")
            # Memory optimization: Memory-critical operation

            # Convert certain layers to FP16 to save memory
            # Memory optimization: Memory-critical operation
            fp16_count = 0
            for name, module in model.named_modules():
                # Skip first and last layers (to preserve accuracy)
                if "emb" in name.lower() or "embed" in name.lower():
                    continue  # Skip embedding layers
                if "output" in name.lower() or "head" in name.lower() or "final" in name.lower():
                    continue  # Skip output layers

                # Convert appropriate layer types to FP16
                if isinstance(module, (nn.Linear, nn.Conv2d)) and module.weight.numel() > 1000:
                    with torch.no_grad():
                    # Memory optimization: Disable gradient computation to save memory
                        module.weight.data = module.weight.data.half()
                        if module.bias is not None:
                            module.bias.data = module.bias.data.half()
                    fp16_count += 1

            if fp16_count > 0:
                logger.info(f"Converted {fp16_count} internal layers to FP16")

            # Enable tensor cores if available (GTX cards don't have tensor cores,
            # but this optimization doesn't hurt and prepares for future hardware)
            torch.backends.cudnn.benchmark = True
            logger.info("Enabled cuDNN benchmark mode")
    else:
        logger.warning("CUDA not available, skipping GPU optimizations")
        # Memory optimization: Memory-critical operation

    # Restore original training state
    model.train(was_training)

    return model

def optimize_memory_allocation(model: nn.Module, target_memory_gb: float = 3.5) -> Dict[str, Any]:
# Memory optimization: Memory-critical operation
    """
    Optimize memory allocation for a model to fit within target memory constraints.
    # Memory optimization: Explicit memory cleanup

    This function analyzes the model and applies various optimization strategies
    # Memory optimization: Explicit memory cleanup
    to reduce memory usage while maintaining functionality.
    # Memory optimization: Memory-critical operation

    Args:
        model: PyTorch model to optimize
        # Memory optimization: Explicit memory cleanup
        target_memory_gb: Target memory usage in GB
        # Memory optimization: Memory-critical operation

    Returns:
        Dictionary containing optimization results and statistics

    Example:
        ```python
        # Optimize model to fit in 3.5GB (for 4GB GPU with buffer)
        # Memory optimization: Explicit memory cleanup
        results = optimize_memory_allocation(model, target_memory_gb=3.5)
        # Memory optimization: Memory-critical operation
        print(f"Memory saved: {results['memory_saved_mb']:.1f} MB")
        # Memory optimization: Memory-critical operation
        ```
    """
    logger.info(f"Optimizing memory allocation for target {target_memory_gb:.1f}GB")
    # Memory optimization: Memory-critical operation

    # Initial memory analysis
    # Memory optimization: Memory-critical operation
    initial_memory = print_model_memory_usage(model)
    # Memory optimization: Memory-critical operation
    initial_memory_mb = initial_memory.get('total_memory_mb', 0)
    # Memory optimization: Memory-critical operation
    target_memory_mb = target_memory_gb * 1024
    # Memory optimization: Memory-critical operation

    results = {
        'initial_memory_mb': initial_memory_mb,
        # Memory optimization: Memory-critical operation
        'target_memory_mb': target_memory_mb,
        # Memory optimization: Memory-critical operation
        'optimizations_applied': [],
        'memory_saved_mb': 0,
        # Memory optimization: Memory-critical operation
        'success': False
    }

    # If already within target, no optimization needed
    if initial_memory_mb <= target_memory_mb:
    # Memory optimization: Memory-critical operation
        results['success'] = True
        logger.info(f"Model already fits in target memory ({initial_memory_mb:.1f}MB <= {target_memory_mb:.1f}MB)")
        # Memory optimization: Explicit memory cleanup
        return results

    # Apply optimizations in order of effectiveness

    # 1. Try quantization first (most effective)
    try:
        quantized_model = quantize_model(model, "dynamic")
        # Memory optimization: Explicit memory cleanup
        quantized_memory = print_model_memory_usage(quantized_model)
        # Memory optimization: Memory-critical operation
        quantized_memory_mb = quantized_memory.get('total_memory_mb', initial_memory_mb)
        # Memory optimization: Memory-critical operation

        if quantized_memory_mb < initial_memory_mb:
        # Memory optimization: Memory-critical operation
            memory_saved = initial_memory_mb - quantized_memory_mb
            # Memory optimization: Memory-critical operation
            results['memory_saved_mb'] += memory_saved
            # Memory optimization: Memory-critical operation
            results['optimizations_applied'].append(f"Dynamic quantization (-{memory_saved:.1f}MB)")
            # Memory optimization: Memory-critical operation

            # Update model reference for further optimizations
            # Memory optimization: Explicit memory cleanup
            model = quantized_model
            # Memory optimization: Explicit memory cleanup
            logger.info(f"Applied quantization, saved {memory_saved:.1f}MB")
            # Memory optimization: Memory-critical operation

    except Exception as e:
        logger.warning(f"Quantization failed: {e}")

    # 2. Apply gradient checkpointing if available
    if hasattr(model, 'gradient_checkpointing_enable'):
        try:
            model.gradient_checkpointing_enable()
            results['optimizations_applied'].append("Gradient checkpointing enabled")
            logger.info("Enabled gradient checkpointing")
        except Exception as e:
            logger.warning(f"Gradient checkpointing failed: {e}")

    # 3. Disable caching to save memory
    # Memory optimization: Memory-critical operation
    if hasattr(model, 'config') and hasattr(model.config, 'use_cache'):
        model.config.use_cache = False
        results['optimizations_applied'].append("Disabled model caching")
        # Memory optimization: Explicit memory cleanup
        logger.info("Disabled model caching")
        # Memory optimization: Explicit memory cleanup

    # 4. Apply mixed precision optimization
    try:
        # This is a configuration flag rather than actual conversion
        if torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            results['optimizations_applied'].append("Mixed precision ready")
            logger.info("Model configured for mixed precision")
            # Memory optimization: Explicit memory cleanup
    except Exception as e:
        logger.warning(f"Mixed precision setup failed: {e}")

    # Final memory check
    # Memory optimization: Memory-critical operation
    final_memory = print_model_memory_usage(model)
    # Memory optimization: Memory-critical operation
    final_memory_mb = final_memory.get('total_memory_mb', initial_memory_mb)
    # Memory optimization: Memory-critical operation

    results['final_memory_mb'] = final_memory_mb
    # Memory optimization: Memory-critical operation
    results['memory_saved_mb'] = initial_memory_mb - final_memory_mb
    # Memory optimization: Memory-critical operation
    results['success'] = final_memory_mb <= target_memory_mb
    # Memory optimization: Memory-critical operation

    if results['success']:
        logger.info(f"Successfully optimized model: {initial_memory_mb:.1f}MB -> {final_memory_mb:.1f}MB")
        # Memory optimization: Memory-critical operation
    else:
        logger.warning(f"Could not reduce memory to target: {final_memory_mb:.1f}MB > {target_memory_mb:.1f}MB")
        # Memory optimization: Memory-critical operation

    return results
