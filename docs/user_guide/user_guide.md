# ImpressionCore: Full User Guide

## Table of Contents

1. [Introduction](#introduction)
    * [What is ImpressionCore?](#what-is-impressioncore)
    * [Core Features](#core-features)
    * [Who is this guide for?](#who-is-this-guide-for)
2. [Getting Started](#getting-started)
    * [System Requirements](#system-requirements)
    * [Installation](#installation)
        * [Prerequisites](#prerequisites)
        * [Cloning the Repository](#cloning-the-repository)
        * [Setting up the Python Environment](#setting-up-the-python-environment)
        * [Installing Dependencies](#installing-dependencies)
    * [GPU Setup (Highly Recommended)](#gpu-setup-highly-recommended)
        * [Why Use a GPU?](#why-use-a-gpu)
        * [Automatic GPU Setup](#automatic-gpu-setup)
        * [Manual GPU Setup](#manual-gpu-setup)
            * [Install NVIDIA Drivers](#1-install-nvidia-drivers)
            * [Install CUDA Toolkit](#2-install-cuda-toolkit)
            * [Install PyTorch with CUDA](#3-install-pytorch-with-cuda)
            * [Verify Installation](#4-verify-installation)
        * [GPU Troubleshooting](#gpu-troubleshooting)
        * [Notes for GTX 1050 Ti (4GB VRAM)](#notes-for-gtx-1050-ti-4gb-vram)
3. [Project Overview](#project-overview)
    * [Directory Structure](#directory-structure)
    * [Key Components](#key-components)
4. [Using the Web Interface](#using-the-web-interface)
    * [Launching the Server](#launching-the-server)
    * [Navigating the Interface](#navigating-the-interface)
        * [Introduction Page](#introduction-page)
        * [Setup Page](#setup-page)
        * [Unified Builder](#unified-builder)
        * [Tokenizer Pages](#tokenizer-pages)
        * [Walkthrough Pages](#walkthrough-pages)
5. [Tokenization Deep Dive](#tokenization-deep-dive)
    * [Understanding Tokenization](#understanding-tokenization)
    * [Text Tokenization (BPE)](#text-tokenization-bpe)
        * [How BPE Works](#how-bpe-works)
        * [Using the `BPETokenizer`](#using-the-bpetokenizer)
        * [Special Tokens](#special-tokens)
        * [Training a Text Tokenizer](#training-a-text-tokenizer)
    * [Image Tokenization (VQ)](#image-tokenization-vq)
        * [How Patch-Based VQ Works](#how-patch-based-vq-works)
        * [Using the `ImageTokenizer`](#using-the-imagetokenizer)
        * [Architecture Details](#image-tokenizer-architecture)
        * [Training an Image Tokenizer](#training-an-image-tokenizer)
    * [Working with Tokenized Content](#working-with-tokenized-content)
        * [Saving and Loading Tokens](#saving-and-loading-tokens)
        * [Analyzing Tokens](#analyzing-tokens)
    * [Advanced Tokenization](#advanced-tokenization)
        * [Multimodal Processing (`ModalEngine`)](#multimodal-processing-modalengine)
        * [Memory Efficiency (`LiteModalEngine`)](#memory-efficiency-litemodalengine)
        * [Custom Tokenizers](#custom-tokenizers)
    * [Tokenization Best Practices](#tokenization-best-practices)
6. [Command-Line Tools](#command-line-tools)
    * [General Usage](#general-usage)
    * [`tokenize_utility`](#tokenize_utility)
    * [`token_converter_tool`](#token_converter_tool)
    * [`view_tokens`](#view_tokens)
    * [`train_tokenizer`](#train_tokenizer)
7. [Training Models (Overview)](#training-models-overview)
    * [Configuration Files](#configuration-files)
    * [Data Preparation](#data-preparation)
    * [Running Training Scripts](#running-training-scripts)
    * [Monitoring Training](#monitoring-training)
    * [Checkpoint Management](#checkpoint-management)
8. [ImpressionCore Model Builder](#impressioncore-model-builder)
    * [Purpose and Overview](#purpose-and-overview)
    * [Accessing the Model Builder](#accessing-the-model-builder)
    * [Walkthrough Structure](#walkthrough-structure)
        * [Introduction](#introduction)
        * [Environment Setup](#environment-setup)
        * [Model Definition](#model-definition)
        * [Data Preparation](#data-preparation)
        * [Pretraining (Optional)](#pretraining-optional)
        * [Training Configuration](#training-configuration)
        * [Training Process](#training-process)
        * [Evaluation](#evaluation)
        * [Inference Testing](#inference-testing)
        * [Model Export and Deployment](#model-export-and-deployment)
    * [Current Status of the Model Builder](#current-status-of-the-model-builder)
    * [Technical Architecture](#technical-architecture)
    * [Future Enhancements](#future-enhancements)
    * [Best Practices for Using the Model Builder](#best-practices-for-using-the-model-builder)
9. [Examples](#examples)
10. [Contributing](#contributing)
11. [Troubleshooting](#troubleshooting)
12. [Roadmap](#roadmap)
13. [License](#license)
14. [Tokenizer](#tokenizer)
15. [Memory Manager](#memory-manager)
16. [Performance Optimizer](#performance-optimizer)
17. [Integration Testing](#integration-testing)

---

## 1. Introduction

### What is ImpressionCore?

ImpressionCore is a versatile Python library designed for efficient **tokenization** of both **text** and **images**. It serves as a foundational component for building multimodal AI models, particularly those based on transformer architectures. It provides tools for converting raw data into the discrete token representations required by these models, along with utilities for training custom tokenizers and managing tokenized data.

The core philosophy is to provide a robust and configurable system for handling the crucial first step in many AI pipelines: getting data into a format the model can understand.

### Core Features

* **Dual Tokenization:** Handles both text (using Byte-Pair Encoding - BPE) and images (using learned Patch-Based Vector Quantization - VQ).
* **Efficiency:** Designed for good compression and performance, especially relevant for image tokenization.
* **Configurability:** Uses JSON files for configuring model architectures and training parameters.
* **Training Framework:** Includes scripts and utilities to train your own text and image tokenizers on custom datasets.
* **Web Interface:** Provides an interactive web UI (served via Flask) for exploring features, setting up the environment, and experimenting with tokenizers.
* **Command-Line Tools:** Offers utilities for tokenizing content, converting token formats, and analyzing token distributions.
* **Modularity:** Built with components like `ModalEngine` for potentially extending to other modalities in the future.
* **Transformer Architecture:** Implements a brain-inspired architecture with attention mechanisms, feed-forward networks, and more.

### Who is this guide for?

This guide is intended for:

* **Developers:** Who want to integrate ImpressionCore into their AI projects.
* **Researchers:** Exploring multimodal tokenization techniques.
* **Students:** Learning about text and image processing for deep learning.
* **Users:** Who want to utilize the provided web interface and tools for tokenization tasks.

A basic understanding of Python, deep learning concepts (especially transformers), and command-line usage is beneficial.

---

## 14. Tokenizer

### Example: Tokenizing Text
```python
from src.tokenizer import Tokenizer

tokenizer = Tokenizer(config={})
text = "This is an example."
tokens = tokenizer.tokenize(text)
print(tokens)  # Output: ['This', 'is', 'an', 'example']
```

### Example: Batch Tokenization
```python
texts = ["First example.", "Second example."]
batch_tokens = tokenizer.batch_tokenize(texts)
print(batch_tokens)  # Output: [['First', 'example.'], ['Second', 'example.']]
```

### Edge Case: Empty String
```python
empty_tokens = tokenizer.tokenize("")
print(empty_tokens)  # Output: []
```

### Edge Case: Special Characters
```python
special_tokens = tokenizer.tokenize("!@#$%^&*()")
print(special_tokens)  # Output: ['!@#$%^&*()']
```

---

## 15. Memory Manager

### Example: Tracking VRAM Usage
```python
from src.memory_manager import MemoryManager
import torch

manager = MemoryManager()
tensor = torch.randn(100, 100).cuda()
manager.track_vram(tensor)
print(f"VRAM Usage: {manager.get_vram_usage()} bytes")
```

### Example: Offloading Model to CPU
```python
model = torch.nn.Linear(10, 10).cuda()
manager.offload_to_cpu(model)
```

### Example: Using Memory Tracking and Visualization
```python
import logging
import sys
import time
import psutil
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('memory_example')

# Memory tracking function
def log_memory_usage(tag=""):
    """Log the current memory usage with an optional tag."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
    memory_percent = psutil.virtual_memory().percent
    logger.info(f"Memory usage {tag}: {memory_mb:.2f} MB ({memory_percent:.1f}% of system RAM)")
    return memory_mb, memory_percent

# Create a status animation for visualizing progress
class StatusAnimation:
    """
    Display a status animation in the terminal based on completion percentage and memory usage.
    """
    def __init__(self, total_steps, description="Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()
        self.animation_chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
        self.animation_idx = 0
        # Initial memory usage
        self.initial_memory = self._get_memory_usage()[0]
        
    def _get_memory_usage(self):
        """Get current memory usage of the process in MB."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
        memory_percent = psutil.virtual_memory().percent
        return memory_mb, memory_percent
        
    def update(self, step=None, message=None):
        """Update the animation with current progress and memory usage."""
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
            
        percent = min(100, int((self.current_step / self.total_steps) * 100))
        self.animation_idx = (self.animation_idx + 1) % len(self.animation_chars)
        anim_char = self.animation_chars[self.animation_idx]
        
        msg = message if message else self.description
        elapsed = time.time() - self.start_time
        
        # Get current memory usage
        current_memory, memory_percent = self._get_memory_usage()
        memory_delta = current_memory - self.initial_memory
        
        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * percent / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Print status line with carriage return to overwrite the same line
        sys.stdout.write(f"\r{anim_char} {msg} [{bar}] {percent}% - {elapsed:.2f}s | " +
                         f"Mem: {current_memory:.1f}MB ({memory_delta:+.1f}MB, {memory_percent:.1f}%)")
        sys.stdout.flush()
        
        # If complete, add a newline
        if percent >= 100:
            sys.stdout.write("\n")
            sys.stdout.flush()
            
    def complete(self, message="Complete"):
        """Mark the task as complete and log final memory stats."""
        self.current_step = self.total_steps
        self.update(message=message)
        current_memory, memory_percent = self._get_memory_usage()
        memory_delta = current_memory - self.initial_memory
        logger.info(f"Task completed: {message} - Memory used: {current_memory:.2f}MB " +
                    f"({memory_delta:+.2f}MB delta, {memory_percent:.1f}% of system RAM)")

# Now use with MemoryManager
manager = MemoryManager()
animation = StatusAnimation(5, "Memory operations")
log_memory_usage("before operations")

animation.update(1, "Creating tensor")
tensor = torch.randn(1000, 1000).cuda()
log_memory_usage("after tensor creation")

animation.update(2, "Tracking VRAM usage")
manager.track_vram(tensor)
log_memory_usage("after VRAM tracking")

animation.update(3, "Getting VRAM report")
vram_usage = manager.get_vram_usage()
logger.info(f"VRAM Usage: {vram_usage} MB")

animation.update(4, "Offloading tensor to CPU")
manager.offload_to_cpu(tensor)
log_memory_usage("after offloading")

animation.update(5, "Verifying tensor location")
logger.info(f"Tensor still on CUDA: {tensor.is_cuda}")

animation.complete("Memory operations complete")
log_memory_usage("at end of operations")
```

### Edge Case: No CUDA Device
```python
try:
    tensor = torch.randn(100, 100)
    manager.track_vram(tensor)
except RuntimeError as e:
    print(f"Error: {e}")  # Output: Error message indicating no CUDA device available
```

---

## 16. Performance Optimizer

### Example: Multi-GPU Memory Distribution
```python
from src.performance_optimizer import PerformanceOptimizer
import torch

optimizer = PerformanceOptimizer()
tensors = [torch.randn(100, 100) for _ in range(4)]
distributed_tensors = optimizer.distribute_tensors(tensors)
for tensor in distributed_tensors:
    print(tensor.device)  # Output: cuda:0, cuda:1, ...
```

### Example: Smart Batching
```python
data = list(range(100))
batches = optimizer.smart_batching(data, batch_size=10)
print(batches)  # Output: [[0, 1, ..., 9], [10, 11, ..., 19], ...]
```

### Edge Case: Uneven Batch Size
```python
data = list(range(23))
batches = optimizer.smart_batching(data, batch_size=10)
print(batches)  # Output: [[0, 1, ..., 9], [10, 11, ..., 19], [20, 21, 22]]
```

---

## 17. Integration Testing

### Simulated Environment
To test the integration of all components, run the following script:
```python
from src.tokenizer import Tokenizer
from src.memory_manager import MemoryManager
from src.performance_optimizer import PerformanceOptimizer
import torch

# Initialize components
tokenizer = Tokenizer(config={})
manager = MemoryManager()
optimizer = PerformanceOptimizer()

# Tokenize text
text = "Integration testing example."
tokens = tokenizer.tokenize(text)
print(f"Tokens: {tokens}")

# Track VRAM usage
tensor = torch.randn(100, 100).cuda()
manager.track_vram(tensor)
print(f"VRAM Usage: {manager.get_vram_usage()} bytes")

# Offload tensor to CPU
manager.offload_to_cpu(tensor)

# Distribute tensors across GPUs
tensors = [torch.randn(100, 100) for _ in range(4)]
distributed_tensors = optimizer.distribute_tensors(tensors)
for tensor in distributed_tensors:
    print(tensor.device)
```

---

## [2025-04-16] Multimodal Evaluation & Memory Profiling Guide

### Running CIFAR-10 Evaluation

1. Ensure `torchvision` is installed.
2. Run `src/training/evaluation/evaluate_cifar10.py` to evaluate a model on CIFAR-10.
3. Review accuracy, loss, and VRAM usage in the output.

### Integrating Your Own Model

- Replace the model loading logic in `evaluate_cifar10.py` with your own vision or multimodal model.
- Ensure your model outputs logits for 10 classes (CIFAR-10 standard).

### Memory Profiling

- VRAM usage is logged before and after evaluation.
- For training/inference, add `torch.cuda.memory_summary()` or similar hooks as shown in the evaluation script.

### Hardware Target

- All pipelines are optimized for NVIDIA GTX 1050 Ti (4GB VRAM).
- For best results, use batch sizes and settings recommended in the evaluation script.

---

## Building ImpressionCore-b1: Step-by-Step

This section provides a complete, actionable guide for building the initial ImpressionCore model (ImpressionCore-b1) from scratch. Follow these steps to ensure a successful setup and training process.

### 1. Prerequisites
- Python 3.8+
- (Recommended) NVIDIA GPU with at least 4GB VRAM (e.g., GTX 1050 Ti)
- Git
- (Optional) CUDA Toolkit for GPU acceleration

### 2. Clone the Repository
```bash
git clone https://github.com/your-org/impressioncore.git
cd impressioncore
```

### 3. Set Up Python Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. (Optional) GPU Setup
- See [GPU Setup](#gpu-setup-highly-recommended) for detailed instructions.
- Run the hardware check in the web UI or:
```bash
python src/hardware_check.py
```

### 6. Launch the Web Interface
```bash
python run_server.py
```
- Open your browser to the address shown (usually http://localhost:5000)

### 7. Model Definition (ImpressionCore-b1)
- In the web UI, select the **ImpressionCore-b1** template in the Model Builder.
- Accept default parameters or adjust as needed.
- Save your configuration.

### 8. Data Preparation
- Prepare your dataset (text or images).
- (Optional) Train a tokenizer:
  - For text: use the UI or `python src/tokenizer/train_tokenizer.py --config <config.json>`
  - For images: use the UI or `python src/tokenizer/train_image_tokenizer.py --config <config.json>`
- Tokenize your data using the UI or CLI.

### 9. Training
- Start training from the web UI or:
```bash
python src/training/train.py --config <your_model_config.json>
```
- Monitor progress in the UI or terminal.

### 10. Evaluation
- Evaluate your model from the UI or:
```bash
python src/training/evaluation/evaluate_cifar10.py --model <checkpoint_path>
```
- Review metrics (Perplexity, BLEU, etc.) in the UI or terminal.

### 11. Inference
- Use the trained model for inference via the UI or:
```bash
python src/inference/infer.py --model <checkpoint_path> --input <input_file>
```

### 12. Checkpoints & Troubleshooting
- Checkpoints are saved automatically during training.
- For troubleshooting, see the [Troubleshooting](#troubleshooting) section below.

---

**Tip:** For each step, refer to the [ImpressionCore-b1 Walkthrough](walkthrough_plan.md#impressioncore-b1-walkthrough) for a summarized checklist and the main walkthrough for advanced options.
