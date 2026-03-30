# GPU Memory Management in ImpressionCore

This document provides guidance on effectively managing GPU memory in ImpressionCore, with a specific focus on optimizing for systems with limited VRAM (4GB or less), such as the NVIDIA GeForce GTX 1050 Ti.

## Table of Contents

1. [Memory Management Overview](#memory-management-overview)
2. [Hardware-Specific Optimizations](#hardware-specific-optimizations)
3. [Training Optimizations](#training-optimizations)
4. [Inference Optimizations](#inference-optimizations)
5. [Monitoring VRAM Usage](#monitoring-vram-usage)
6. [Troubleshooting](#troubleshooting)

## Memory Management Overview

ImpressionCore uses a centralized memory management system to efficiently utilize GPU resources. The system includes:

- Automatic hardware detection and configuration
- Memory-efficient model operations
- Precision optimization (FP16/BF16)
- Model offloading between GPU and CPU
- Tensor caching with automatic cleanup

For systems with limited VRAM (≤4GB), the memory controller automatically enables additional optimizations to ensure stable operation.

## Hardware-Specific Optimizations

ImpressionCore applies different optimizations based on your hardware:

### For 4GB VRAM GPUs (e.g., NVIDIA 1050 Ti)

The following optimizations are automatically applied:

- FP16 precision for all operations (reduces memory footprint by ~50%)
- Gradient checkpointing during training (trades computation for memory)
- Attention operation memory optimizations
- Conservative batch sizes (typically 1-2)
- Model offloading when not in active use
- Aggressive cache management
- Tensor fragmentation prevention

### Implementation

Our system uses the `hardware_detection.py` module to identify your hardware capabilities and automatically configure appropriate settings. The `MemoryController` class manages model allocation and resource management.

## Training Optimizations

Training deep learning models is particularly memory-intensive. Use these techniques to train on limited VRAM:

### Recommended Settings for 4GB GPUs

```python
training_config = {
    "batch_size": 1,                   # Small batch size
    "gradient_accumulation_steps": 4,  # Accumulate gradients over multiple steps
    "fp16": True,                      # Enable half-precision
    "max_grad_norm": 1.0,              # Gradient clipping to prevent spikes
}
```

### Advanced Techniques for Low VRAM

1. **Gradient Checkpointing**: Reduces memory by not storing all activations
   ```python
   model.gradient_checkpointing_enable()
   ```

2. **Progressive Layer Freezing**: Freeze early layers to reduce gradient memory
   ```python
   # Freeze early layers
   for param in model.layers[:6].parameters():
       param.requires_grad = False
   ```

3. **CPU Offloading**: Move optimizer states to CPU
   ```python
   # Example with PyTorch's CPU offloading
   from torch.utils.checkpoint import checkpoint
   
   def forward_with_checkpointing(model, *inputs):
       return checkpoint(model.forward, *inputs)
   ```

4. **Partition Training**: Train subsets of the model separately

## Inference Optimizations

Inference typically requires less memory than training, but can still be optimized:

1. **Use the MemoryEfficientInference context manager**:
   ```python
   from models.memory_controller import MemoryEfficientInference
   
   with MemoryEfficientInference(model, use_fp16=True):
       output = model(input_tensor)
   ```

2. **Enable Layer-by-Layer Inference**:
   For very large models that don't fit in VRAM even with optimization, use:
   ```python
   from models.memory_controller import get_memory_controller
   
   controller = get_memory_controller()
   controller.register_model("my_model", model)
   
   with ModelContext("my_model") as model:
       output = model(input_tensor)
   ```

3. **Disable Gradient Computation**:
   ```python
   with torch.no_grad():
       output = model(input_tensor)
   ```

## Monitoring VRAM Usage

ImpressionCore provides tools to monitor memory usage:

1. **Hardware Check Script**:
   ```bash
   python run_hardware_check.py --detailed
   ```

2. **Memory Statistics API**:
   ```python
   from models.memory_controller import get_memory_stats
   
   stats = get_memory_stats()
   print(f"Current VRAM usage: {stats['cuda_allocated_gb']:.2f} GB")
   ```

3. **Training Server API**:
   The training server provides real-time memory monitoring:
   ```
   GET /api/v1/status
   ```

## Troubleshooting

### Common Issues and Solutions

1. **Out of Memory (OOM) Errors**:
   - Reduce batch size
   - Enable gradient checkpointing
   - Use FP16 precision
   - Increase gradient accumulation steps

2. **Slow Training with CPU Offloading**:
   - Consider using smaller model variants
   - Try progressive training approaches
   - Optimize data loading pipeline to reduce overhead

3. **Unstable Training with FP16**:
   - Implement loss scaling
   - Monitor for NaN values
   - Try using BF16 if supported by your hardware

4. **GPU Memory Fragmentation**:
   - Call `torch.cuda.empty_cache()` periodically
   - Use the memory controller's cache management
   - Restart training services if fragmentation persists

### Memory Leak Diagnosis

If you suspect a memory leak:

1. Monitor memory usage over time with the memory controller's logging
2. Check if cached tensors are properly released
3. Ensure all model contexts are properly closed
4. Review custom code for proper tensor cleanup

## Recommended VRAM Allocation by Model Size

| Model Size | Parameters | Recommended Min VRAM | Batch Size | Precision |
|------------|------------|---------------------|------------|-----------|
| Small      | <500M      | 2GB                 | 1-2        | FP16      |
| Medium     | 500M-1.5B  | 4GB                 | 1          | FP16      |
| Large      | 1.5B-3B    | 8GB                 | 1          | FP16      |
| XL         | >3B        | 16GB+               | 1          | FP16/BF16 |

## Dynamic Memory Management Strategies (Conceptual)

Beyond static configurations, ImpressionCore is developing dynamic memory management strategies to adapt to real-time VRAM availability and specific operational needs (e.g., training vs. inference, varying input sizes).

The core ideas are being prototyped in `src/core/memory/dynamic_manager.py`.

### Key Concepts Under Exploration

- **Real-time VRAM Monitoring:** Continuously tracking available VRAM to inform optimization decisions. The `get_available_gpu_vram()` function in `dynamic_manager.py` is a first step.
- **Adaptive CPU Offloading:** Dynamically moving less critical or temporarily unused model parts (layers, parameters, optimizer states) to CPU RAM when VRAM is scarce, and back to GPU when space allows. The `DynamicMemoryOptimizer` class includes conceptual placeholders for this.
- **Dynamic Activation Checkpointing:** Enabling or disabling gradient/activation checkpointing for specific layers or the entire model based on memory pressure during training.
- **Intelligent Batch Sizing:** (Future) Adjusting batch sizes dynamically for training or inference if memory constraints are tight.
- **Model-Specific Optimizers:** (Future) Developing optimizer profiles that understand the memory characteristics of different ImpressionCore model architectures (e.g., `ImpressionCore-b1`) to apply tailored strategies.

### Integration Points (Planned)

- **Training Loop:** Before starting a training epoch or batch, the dynamic manager could assess available VRAM and apply necessary optimizations (e.g., enable checkpointing, suggest offloading).
- **Inference Pipeline:** Before loading a model for inference, or when handling large inputs, the manager could optimize the model's VRAM footprint.
- **Model Loading:** When models are loaded, the dynamic manager could be consulted to prepare the model for the current hardware's memory profile.

This is an active area of development aimed at maximizing the utility of ImpressionCore on VRAM-constrained hardware like the NVIDIA GTX 1050 Ti and ensuring scalability for more powerful systems.
