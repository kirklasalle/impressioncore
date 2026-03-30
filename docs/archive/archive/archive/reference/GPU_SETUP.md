# ⚠️ ARCHIVED FILE

**Created:** March 05, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\archive\archive\reference\GPU_SETUP.md #attention_mechanism #cuda #deployment #docs\reference\gpu_setup.md #documentation #gpu_optimization #inference #memory_management #performance #pytorch #testing #training #web_interface [reference, 2025]  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

# Gpu Setup

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #attention_mechanism #cuda #deployment #docs\reference\gpu_setup.md #documentation #gpu_optimization #inference #memory_management #performance #pytorch #testing #training #web_interface  
**Category:** Reference Documentation  
**Status:** Active

---
tags: [reference, 2025]
---

# GPU Setup Guide

This guide provides detailed instructions for setting up and optimizing your GPU environment for ImpressionCore.

## Hardware Compatibility

ImpressionCore supports a range of NVIDIA GPUs, with specific optimizations for legacy hardware:

| GPU Class | VRAM | Examples | Recommended Use |
|-----------|------|----------|-----------------|
| Legacy | 4-6GB | GTX 1050 Ti, GTX 1060, GTX 1650 | Inference, limited training |
| Mid-range | 8-12GB | RTX 2060, RTX 3060, RTX 4060 | Training, inference |
| High-end | 16GB+ | RTX 3080, RTX 3090, RTX 4090 | Full training, research |

### Special Considerations for Legacy GPUs (4GB VRAM)

ImpressionCore is specifically optimized to run on GPUs with limited VRAM, such as the GTX 1050 Ti (4GB). The following techniques are automatically applied:

- **Gradient checkpointing** to reduce memory requirements during backpropagation
- **Attention chunking** to process attention operations in memory-efficient chunks
- **Precision reduction** using FP16 or int8 quantization where appropriate
- **Layer offloading** to CPU when necessary

## CUDA Installation

### Windows

1. Download the CUDA Toolkit from [NVIDIA's website](https://developer.nvidia.com/cuda-downloads)
2. Select your version of Windows and download the installer
3. Run the installer and follow the prompts
4. Verify installation by running:

```bash
nvcc --version
```

### Linux

1. Update your package list:

```bash
sudo apt update
```

2. Install the CUDA toolkit:

```bash
sudo apt install nvidia-cuda-toolkit
```

3. Verify installation:

```bash
nvcc --version
```

## PyTorch Installation

For optimal compatibility, install PyTorch with CUDA support:

### Windows

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Linux

```bash
pip install torch torchvision torchaudio
```

## Environment Testing

Test your GPU setup with the included hardware check utility:

```bash
python run_hardware_check.py
```

Expected output:

``` text
===== HARDWARE CHECK =====
GPU detected: NVIDIA GeForce GTX 1050 Ti
CUDA available: True
CUDA version: 11.8
VRAM total: 4.00 GB
VRAM free: 3.89 GB
PyTorch CUDA: True
===== COMPATIBILITY =====
Memory-optimized mode: ENABLED
Attention chunking: ENABLED
Gradient checkpointing: ENABLED
Precision reduction: ENABLED (FP16)
```

## Web Interface GPU Setup

The ImpressionCore web interface now includes a dedicated GPU setup page accessible from multiple entry points:

1. From the sidebar navigation under "Setup & Configuration"
2. From the dependencies page via the "Configure GPU Environment" button
3. From the hardware check page when GPU optimizations are recommended

### GPU Setup Interface Features

The GPU setup page provides:

- **Hardware Detection**: Automatically detects your GPU and CUDA installation
- **Interactive Optimization**: Allows toggling of different memory optimization techniques
- **Visual Memory Calculator**: Shows estimated memory usage with current settings
- **Driver Management**: Provides links to appropriate drivers for your hardware
- **Configuration Presets**: Optimal settings for different GPU classes
- **Compatibility Warnings**: Alerts for potential issues with your hardware setup

### Memory Optimization Controls

The interface allows fine-tuning of memory optimization settings:

- **Gradient Checkpointing**: Trading computation for memory (slight performance impact)
- **Attention Chunking**: Processing attention in smaller chunks (moderate performance impact)
- **Precision Control**: FP32/FP16/Int8 options with quality/performance tradeoffs
- **Layer Offloading**: CPU offload settings for extremely memory-constrained scenarios
- **Batch Size Control**: Adjust training and inference batch sizes for your hardware
- **Activation Caching**: Memory-efficient activation handling during training

## Benchmarking

The GPU setup page includes a benchmarking tool to evaluate your hardware's performance:

1. **Inference Benchmark**: Measures tokens/second for text generation
2. **Small Training Benchmark**: Tests training step time with a small batch
3. **Memory Pressure Test**: Evaluates stability under near-maximum memory usage

Results are saved and can be compared across different optimization settings.

## Troubleshooting

### CUDA Not Detected

If CUDA is not detected:

1. Verify your GPU is CUDA-capable
2. Check that drivers are properly installed
3. Ensure PyTorch was installed with CUDA support
4. Try running with `CUDA_VISIBLE_DEVICES=0` environment variable

### Out of Memory Errors

If you encounter out-of-memory errors:

1. Enable all memory optimizations in the GPU Setup page
2. Reduce batch sizes for training and inference
3. Use a smaller model configuration
4. Enable CPU offloading for some layers

### Poor Performance

If performance is unexpectedly low:

1. Check for thermal throttling using GPU monitoring tools
2. Ensure other applications aren't using the GPU
3. Update to the latest GPU drivers
4. Verify your power settings are set to maximum performance

## Next Steps

After configuring your GPU environment:

1. Proceed to model definition to create a model configuration suitable for your hardware
2. Review the training guide for hardware-specific training recommendations
3. Check the inference optimization guide for deployment best practices

---

*Note: This documentation is regularly updated as new optimizations and features are added to improve compatibility with various GPU configurations, including legacy hardware like the GTX 1050 Ti (4GB VRAM).*
