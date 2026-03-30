# ImpressionCore Memory Optimization Guide

This guide provides detailed instructions for optimizing memory usage when working with ImpressionCore on hardware with limited VRAM, particularly focused on systems with GPUs like the NVIDIA GTX 1050 Ti (4GB VRAM).

## Table of Contents

1. [Understanding Memory Constraints](#understanding-memory-constraints)
2. [Memory Optimization Features](#memory-optimization-features)
3. [Configuration Options](#configuration-options)
4. [Monitoring Memory Usage](#monitoring-memory-usage)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Techniques](#advanced-techniques)

## Understanding Memory Constraints

### VRAM Requirements

ImpressionCore's multimodal capabilities require significant memory resources. However, the system is designed to run on consumer hardware with optimizations. Here are the baseline memory requirements:

| Model Component | FP32 Memory | FP16 Memory | INT8 Memory |
|-----------------|-------------|-------------|-------------|
| Text Transformer | ~2.5GB | ~1.3GB | ~0.7GB |
| Diffusion Model | ~3.2GB | ~1.6GB | ~0.8GB |
| Combined System | ~5.7GB | ~2.9GB | ~1.5GB |

### Common Memory Bottlenecks

1. **Attention Layers**: Self-attention operations scale quadratically with sequence length
2. **Activations**: Intermediate outputs can consume significant memory
3. **Optimizer States**: Training requires additional memory for gradients and optimizer states
4. **Batch Size**: Larger batches multiply memory requirements linearly

## Memory Optimization Features

ImpressionCore includes several built-in memory optimization techniques:

### 1. Gradient Checkpointing

Trades computational speed for memory efficiency by recomputing intermediate activations during backward passes rather than storing them.

```python
# Enable gradient checkpointing
from src.utils.memory_optimization import apply_gradient_checkpointing

model = apply_gradient_checkpointing(model)
```

**Impact**: Reduces memory usage by 30-40% with 20-30% slower training.

### 2. Attention Chunking

Processes large attention matrices in smaller chunks to avoid memory spikes.

```python
# Configure attention chunking
from src.utils.memory_optimization import setup_attention_chunking

model = setup_attention_chunking(model, chunk_size=128)
```

**Impact**: Enables processing of longer sequences with minimal performance impact.

### 3. Precision Control

Runs models in lower precision to reduce memory footprint.

```python
# Convert model to lower precision
from src.utils.memory_optimization import optimize_for_low_vram

model = optimize_for_low_vram(model, dtype=torch.float16)
```

**Impact**: Cuts memory usage approximately in half with minimal quality loss.

### 4. CPU Offloading

Moves less frequently accessed parameters to CPU memory.

```python
# Enable CPU offloading
from src.utils.memory_optimization import optimize_for_low_vram

model = optimize_for_low_vram(model, cpu_offload=True)
```

**Impact**: Allows running larger models at the cost of slower inference.

## Configuration Options

ImpressionCore provides a configuration system to control memory usage. Create a `config.yaml` file:

```yaml
memory:
  precision: "float16"  # Options: float32, float16, bfloat16
  gradient_checkpointing: true
  attention_chunk_size: 128  # Smaller values use less memory
  cpu_offload: false
  optimize_for_inference: true
  max_batch_size: 1
```

Or configure programmatically:

```python
from src.config import MemoryConfig

memory_config = MemoryConfig(
    precision="float16",
    gradient_checkpointing=True,
    attention_chunk_size=128,
    cpu_offload=False
)

model = load_model(memory_config=memory_config)
```

## Monitoring Memory Usage

### Built-in Monitoring

ImpressionCore includes tools to monitor memory usage:

```python
from src.utils.memory_optimization import monitor_memory_usage

# Get current memory statistics
memory_stats = monitor_memory_usage()
print(f"Current VRAM usage: {memory_stats['current_gb']:.2f} GB")
print(f"Peak VRAM usage: {memory_stats['max_gb']:.2f} GB")
```

### Memory Profiling

For detailed analysis, use the memory profiling tools:

```python
from src.utils.memory_optimization import estimate_memory_requirements

# Estimate memory requirements before loading
memory_estimate = estimate_memory_requirements(
    model_class=ImpressionTransformer,
    batch_size=1,
    seq_length=512
)
print(f"Estimated VRAM requirement: {memory_estimate['total_gb']:.2f} GB")
```

### Memory Usage Dashboard

The web interface includes a memory usage dashboard accessible at `/dashboard/memory` when running the server. This provides:

- Real-time memory monitoring
- Historical usage graphs
- Component-level breakdown
- Optimization recommendations

## Troubleshooting

### Common Issues and Solutions

#### Out of Memory Errors

If you encounter CUDA out of memory errors:

1. **Reduce precision**: Switch to FP16 or INT8

   ```python
   model = optimize_for_low_vram(model, dtype=torch.float16)
   ```

2. **Enable CPU offloading**:

   ```python
   model = optimize_for_low_vram(model, cpu_offload=True)
   ```

3. **Reduce sequence length**:

   ```python
   # Limit context length
   tokenizer.model_max_length = 256
   ```

4. **Clear cache regularly**:

   ```python
   torch.cuda.empty_cache()
   gc.collect()
   ```

#### Slow Performance

If optimizations cause unacceptable slowdowns:

1. **Adjust chunk size**: Find the optimal balance

   ```python
   # Try larger chunk sizes if performance is too slow
   model = setup_attention_chunking(model, chunk_size=256)  # Default is 128
   ```

2. **Selective offloading**: Offload only specific layers

   ```python
   # Advanced: Offload only certain layers
   from src.utils.memory_optimization import selective_cpu_offload
   
   model = selective_cpu_offload(model, layer_indices=[0, 1, 2])
   ```

## Advanced Techniques

### Model Quantization

For extreme memory constraints, quantize the model to INT8 or INT4:

```python
# Requires additional libraries
from src.utils.quantization import quantize_model

model = quantize_model(model, bits=8)  # Options: 8, 4
```

### Dynamic Batch Sizing

Automatically adjust batch size based on available memory:

```python
from src.utils.memory_optimization import DynamicBatchSizer

batch_sizer = DynamicBatchSizer(
    min_batch=1,
    max_batch=16,
    target_memory_usage=0.8  # Use up to 80% of available VRAM
)

optimal_batch_size = batch_sizer.get_batch_size()
```

### Multi-GPU Strategies

Even with limited VRAM per GPU, you can use multiple GPUs:

```python
from src.utils.distributed import setup_model_parallel

# Split model across multiple GPUs
model = setup_model_parallel(model, strategy="tensor_parallel")
```

### Custom Memory Allocation

For advanced users, customize memory allocation:

```python
import torch
torch.cuda.set_per_process_memory_fraction(0.9)  # Reserve 10% for system
```

## Hardware-Specific Recommendations

### GTX 1050 Ti (4GB VRAM)

Optimal settings for this GPU:

- Use FP16 precision
- Enable gradient checkpointing
- Set attention chunk size to 64-128
- Consider INT8 quantization for larger models
- Limit batch size to 1
- Enable CPU offloading for layers 0-3

### Summary

By applying these optimization techniques, ImpressionCore can run efficiently even on GPUs with limited VRAM like the GTX 1050 Ti. For best results, combine multiple approaches and monitor memory usage to find the optimal configuration for your specific hardware and use case.
