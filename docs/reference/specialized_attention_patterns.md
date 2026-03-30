# Specialized Attention Patterns

**Created:** March 30, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\specialized_attention_patterns.md #attention_mechanism #documentation #gpu_optimization #memory_management #multimodal #performance #transformer  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# Specialized Attention Patterns in ImpressionCore

This document provides an overview of the specialized attention mechanisms implemented in ImpressionCore to optimize memory usage and performance on limited hardware (specifically targeting NVIDIA GTX 1050 Ti with 4GB VRAM).

## Overview

Transformer-based models typically use full self-attention with O(n²) complexity, which becomes prohibitively expensive in terms of memory and computation for long sequences. ImpressionCore implements several specialized attention patterns to address this limitation:

1. **Local Attention**: Restricts attention to a window around each token
2. **Memory-Efficient Attention**: Uses chunking to reduce peak memory usage
3. **Axial Attention**: Factorizes 2D attention into separate horizontal and vertical operations
4. **Dynamic Attention Routing**: Automatically selects the optimal attention mechanism

## Benchmark Results

Our benchmarking on the NVIDIA GTX 1050 Ti (4GB VRAM) shows the following performance characteristics:

| Attention Method | Sequence Length | Processing Time | Memory Usage |
|------------------|-----------------|-----------------|--------------|
| Standard         | 512             | 3.40 ms         | 22.50 MB     |
| Local            | 4096            | 119.14 ms       | 381.00 MB    |
| Memory-Efficient | 4096            | 114.51 ms       | 306.00 MB    |
| Axial            | 4096            | 29.87 ms        | 62.00 MB     |

Key findings:

- Axial Attention provides the best performance for long sequences and 2D data
- Standard Attention works well for short sequences (≤512 tokens)
- Memory-Efficient Attention offers good performance for medium-length sequences
- Local Attention uses less memory than standard attention but is slower

## Usage Guide

### Basic Usage with AttentionManager

The `AttentionManager` class automatically selects the most appropriate attention mechanism based on input characteristics and available hardware resources:

```python
from src.modules.attention.attention_manager import AttentionManager

# Initialize the attention manager
attention_manager = AttentionManager(
    hidden_size=768,
    num_heads=8,
    vram_target_mb=3500,  # Target for 4GB cards
    attention_preference="balanced"  # Options: "performance", "memory", "balanced"
)

# Use the attention manager in your forward pass
output = attention_manager(
    hidden_states=input_tensor,
    attention_mask=mask,
    is_2d_data=False,  # Set to True for image-like data
    height=None,      # Required for 2D data
    width=None        # Required for 2D data
)
```

### Direct Usage of Specific Attention Mechanisms

You can also use specific attention mechanisms directly:

```python
from src.modules.attention.sparse_attention import (
    LocalAttention,
    MemoryEfficientAttention,
    AxialAttention
)

# Local attention (sliding window)
local_attn = LocalAttention(
    hidden_size=768,
    window_size=128,
    add_global_tokens=True
)

# Memory-efficient attention (chunked processing)
mem_efficient_attn = MemoryEfficientAttention(
    hidden_size=768,
    num_heads=8,
    chunk_size=512
)

# Axial attention (for 2D data)
axial_attn = AxialAttention(
    hidden_size=768,
    height=64,
    width=64
)
```

### Integrating with Transformer Layers

Here's how to integrate the `AttentionManager` into a transformer layer:

```python
import torch.nn as nn
from src.modules.attention.attention_manager import AttentionManager

class TransformerLayerWithDynamicAttention(nn.Module):
    def __init__(self, hidden_size=768, num_heads=8, dropout=0.1):
        super().__init__()
        self.attention_manager = AttentionManager(
            hidden_size=hidden_size,
            num_heads=num_heads
        )
        self.norm1 = nn.LayerNorm(hidden_size)
        self.norm2 = nn.LayerNorm(hidden_size)
        self.feed_forward = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 4),
            nn.GELU(),
            nn.Linear(hidden_size * 4, hidden_size),
            nn.Dropout(dropout)
        )
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, hidden_states, attention_mask=None, is_2d_data=False):
        # Apply attention with auto-selected mechanism
        attention_output = self.attention_manager(
            hidden_states=self.norm1(hidden_states),
            attention_mask=attention_mask,
            is_2d_data=is_2d_data
        )
        
        # Residual connection after attention
        hidden_states = hidden_states + self.dropout(attention_output)
        
        # Feed forward network with residual
        ff_output = self.feed_forward(self.norm2(hidden_states))
        hidden_states = hidden_states + self.dropout(ff_output)
        
        return hidden_states
```

## Memory Optimization Recommendations

For optimal performance on limited VRAM hardware (like NVIDIA GTX 1050 Ti), follow these guidelines:

1. **Data Type Selection**:
   - Use Axial Attention for 2D data (images, feature maps)
   - Use Memory-Efficient Attention for medium to long sequences
   - Use Standard Attention only for short sequences

2. **Sequence Length Management**:
   - Keep sequence lengths as short as possible
   - Consider chunking very long inputs and processing them separately

3. **VRAM Monitoring**:
   - Enable VRAM monitoring in AttentionManager to dynamically adjust
   - Consider setting a lower `vram_target_mb` (e.g., 3000MB) to leave room for other operations

4. **Multimodal Processing**:
   - For multimodal inputs, process each modality with its optimal attention type
   - Use the AttentionManager with appropriate `is_2d_data` flags

## Advanced Features

### Attention Statistics Collection

The `AttentionManager` collects runtime statistics on each attention mechanism's performance and memory usage:

```python
# After forward passes through the attention manager
stats = attention_manager.get_stats()
print(stats)  # Shows calls, avg_time_ms, and avg_memory_mb for each mechanism
```

### Forced Attention Type

You can override the automatic selection mechanism:

```python
output = attention_manager(
    hidden_states=input_tensor,
    attention_mask=mask,
    forced_attention_type="axial"  # Options: "standard", "local", "memory_efficient", "axial"
)
```

### Cache Management

For repeated operations with similar inputs, the manager caches selection decisions:

```python
# Clear the selection cache if input characteristics change significantly
attention_manager.clear_cache()
```

## Implementation Details

### AttentionRouter

The `AttentionRouter` class (used internally by `AttentionManager`) uses the following heuristics:

- For sequence length ≤ 512: Standard Attention
- For sequence length ≤ 2048: Memory-Efficient Attention
- For sequence length > 2048: Axial Attention
- For 2D data: Always Axial Attention
- When VRAM is critically low: Prioritize memory efficiency over speed

### Memory Monitoring

The system continuously monitors VRAM usage (when enabled) and can dynamically switch to more memory-efficient attention mechanisms if available VRAM drops below 20% of the target threshold.

## Limitations

- Axial Attention works best when sequence length is a perfect square
- Local Attention may not capture long-range dependencies effectively
- VRAM monitoring has minimal overhead but isn't completely free

## Future Improvements

- Implement block-sparse attention patterns
- Add support for sliding window attention with variable window sizes
- Explore kernel optimizations specific to older GPU architectures
- Add quantization-aware attention mechanisms
