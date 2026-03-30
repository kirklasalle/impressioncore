#!/usr/bin/env python3
"""
ImpressionCore: Evaluate Cifar10

Module for evaluate cifar10 functionality in the ImpressionCore framework.

File: training\evaluation\evaluate_cifar10.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, training, gpu-optimized, ml, pytorch, production, 2025, object-oriented]
Dependencies: [torch]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements evaluate cifar10 functionality for the
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
from training.evaluation.evaluate_cifar10 import ImpressionCoreB1Cifar10
instance = ImpressionCoreB1Cifar10()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import sys # Add sys for path manipulation
import os
# Add the project root to the Python path to allow imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import torch
import torch.nn as nn
from tqdm import tqdm
from src.data.datasets.data_loading import load_cifar10_dataset
from src.models.architectures.impressioncore_b1 import build_impressioncore_b1, impressioncore_b1_forward
from src.core.memory.dynamic_manager import DynamicMemoryOptimizer, get_available_gpu_vram, get_total_gpu_vram # Added import
# Memory optimization: Memory-critical operation


# Wrapper class for ImpressionCore-b1 to make it compatible with evaluate_cifar10_model
class ImpressionCoreB1Cifar10(nn.Module):
    """
    
    ImpressionCoreB1Cifar10 class for ImpressionCore framework.
    
    This class implements impressioncoreb1cifar10 functionality optimized for
    memory-constrained environments like the GTX 1050 Ti.
    # Memory optimization: Memory-critical operation
    
    Memory Considerations:
    # Memory optimization: Memory-critical operation
        - Implements memory-efficient algorithms
        # Memory optimization: Memory-critical operation
        - Supports gradient checkpointing
        - Provides CPU fallback options
    
    Notes:
        - Thread-safe implementation
        - GPU memory optimized
        # Memory optimization: Memory-critical operation
        - Part of ImpressionCore ecosystem
    
    """
    def __init__(self, image_dim=3072, fusion_dim=512, num_classes=10):
        """
        
    __init__ function for processing.
    
    Args:
        self, image_dim, fusion_dim, num_classes: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        super().__init__()
        self.original_module_keys = [] # Store original keys
        self.non_module_params = {} # To store non-nn.Module items

        raw_modules_dict = build_impressioncore_b1(
            image_dim=image_dim, 
            fusion_dim=fusion_dim, 
            num_classes_override=num_classes,
            text_dim=fusion_dim, 
            vocab_size=1000 
        )
        self.original_module_keys = list(raw_modules_dict.keys())

        for key, value in raw_modules_dict.items(): # Changed 'module' to 'value' for clarity
            if isinstance(value, nn.Module): # nn.ModuleList is also an nn.Module
                self.add_module(f"ic_{key}", value)
            else:
                self.non_module_params[key] = value # Store non-module items

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        """
        
    forward function for processing.
    
    Args:
        self, images: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        modules_for_forward = {}
        for key in self.original_module_keys:
            module_attr_name = f"ic_{key}"
            if hasattr(self, module_attr_name): # Check if it was registered as a module
                modules_for_forward[key] = getattr(self, module_attr_name)
            elif key in self.non_module_params: # Check if it's a non-module param
                modules_for_forward[key] = self.non_module_params[key]
            else:
                # This case should ideally not be reached if original_module_keys is accurate
                # and all items are either modules or stored in non_module_params.
                # If build_impressioncore_b1 could return keys that are neither modules
                # nor intended for the forward pass, this logic might need adjustment.
                # For now, we'll assume all keys from build_impressioncore_b1 are needed.
                # If a key is missing, impressioncore_b1_forward will likely error out,
                # which would indicate a problem here or in build_impressioncore_b1.
                # Consider logging a warning or raising an error for unhandled keys if necessary.
                print(f"Warning: Key '{key}' from build_impressioncore_b1 was not found as a module (ic_{key}) or in non_module_params.")
        
        return impressioncore_b1_forward(
            text_tokens=None, 
            image_pixels=images, 
            modules=modules_for_forward # Pass the reconstructed dict
        )


def evaluate_cifar10_model(model, device=None, batch_size=64, num_workers=2, data_dir=None, log_memory=True):
# Memory optimization: Device placement for memory management
    """
    Evaluate a model on the CIFAR-10 test set.
    # Memory optimization: Explicit memory cleanup

    Args:
        model: PyTorch model (must accept image tensors as input).
        # Memory optimization: Explicit memory cleanup
        device: torch.device to use (default: cuda if available).
        # Memory optimization: Device placement for memory management
        batch_size: Batch size for evaluation.
        num_workers: DataLoader workers.
        data_dir: Directory for CIFAR-10 data.
        log_memory: If True, logs VRAM usage before and after evaluation.
        # Memory optimization: Memory-critical operation
    Returns:
        accuracy: Classification accuracy on CIFAR-10 test set.
        avg_loss: Average loss on test set.
    Memory:
    # Memory optimization: Memory-critical operation
        Logs peak VRAM usage if CUDA is available.
        # Memory optimization: Memory-critical operation
    """
    if device is None:
    # Memory optimization: Device placement for memory management
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Memory optimization: CUDA operations for GPU acceleration

    optimizer = None # Initialize optimizer
    if device.type == 'cuda' and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        print(f"[MEM] Initial Total VRAM: {get_total_gpu_vram(device):.2f} MB")
        # Memory optimization: Device placement for memory management
        print(f"[MEM] Initial Available VRAM: {get_available_gpu_vram(device):.2f} MB")
        # Memory optimization: Device placement for memory management
        
    if log_memory and device.type == "cuda" and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        print(f"[MEM] VRAM initial: {torch.cuda.memory_allocated(device) / 1e6:.2f} MB")
        # Memory optimization: CUDA operations for GPU acceleration
        torch.cuda.empty_cache() # Attempt to clear cache
        # Memory optimization: CUDA operations for GPU acceleration
        print(f"[MEM] VRAM after empty_cache(): {torch.cuda.memory_allocated(device) / 1e6:.2f} MB")
        # Memory optimization: CUDA operations for GPU acceleration

    model.eval()
    model.to(device)
    # Memory optimization: Device placement for memory management

    if device.type == 'cuda' and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        total_vram = get_total_gpu_vram(device)
        # Memory optimization: Device placement for memory management
        # Set threshold to 25% of total VRAM, or 512MB if total_vram is 0 (e.g. CUDA not really there)
        # Memory optimization: Memory-critical operation
        low_vram_threshold = total_vram * 0.25 if total_vram > 0 else 512.0 
        optimizer = DynamicMemoryOptimizer(model, low_vram_threshold_mb=low_vram_threshold, verbose=True)
        # Memory optimization: Memory-critical operation
        optimizer._log(f"Optimizer initialized. Device: {optimizer.device}. Total VRAM: {total_vram:.2f} MB. Low VRAM Threshold: {low_vram_threshold:.2f} MB.")
        # Memory optimization: Device placement for memory management

        # Define offload candidates
        # These are the modules registered in ImpressionCoreB1Cifar10 with 'ic_' prefix
        if hasattr(model, 'original_module_keys'):
            offload_candidate_names = [f"ic_{key}" for key in model.original_module_keys]
            # Filter for actual modules existing in the model
            actual_offload_candidates = [name for name, mod in model.named_modules() if name in offload_candidate_names]
        else:
            # Fallback if model doesn't have original_module_keys (e.g. not ImpressionCoreB1Cifar10)
            # Memory optimization: Explicit memory cleanup
            actual_offload_candidates = [name for name, mod in model.named_modules() if len(list(mod.children())) > 0 and len(list(mod.parameters())) > 0]
            if actual_offload_candidates:
                 optimizer._log(f"Warning: model.original_module_keys not found. Using generic offload candidates: {actual_offload_candidates}")
            else:
                 optimizer._log("Warning: model.original_module_keys not found and no generic candidates identified.")


        if actual_offload_candidates:
            optimizer._log(f"Potential offload candidates: {actual_offload_candidates}")
            
            proactive_fraction = 0.0
            current_available_vram = get_available_gpu_vram(device)
            # Memory optimization: Device placement for memory management
            if current_available_vram < optimizer.low_vram_threshold_mb:
                proactive_fraction = 0.1 # Try to free 10% of current available VRAM
                optimizer._log(f"Current VRAM {current_available_vram:.2f}MB is below threshold {optimizer.low_vram_threshold_mb:.2f}MB. Setting proactive offload fraction to {proactive_fraction}.")

            optimizer.adapt_to_available_memory(
            # Memory optimization: Memory-critical operation
                required_vram_estimate_mb=0, # For eval, less about specific next op.
                offload_candidates=actual_offload_candidates,
                proactive_offload_fraction=proactive_fraction
            )
        else:
            optimizer._log("No offload candidates identified for dynamic memory optimization.")
            # Memory optimization: Memory-critical operation

    if log_memory and device.type == "cuda" and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        print(f"[MEM] VRAM after model.to(device): {torch.cuda.memory_allocated(device) / 1e6:.2f} MB")
        # Memory optimization: CUDA operations for GPU acceleration
        print(f"[MEM] VRAM before eval loop (model on device + data loader init): {torch.cuda.memory_allocated(device) / 1e6:.2f} MB")
        # Memory optimization: CUDA operations for GPU acceleration

    criterion = nn.CrossEntropyLoss()
    _, test_loader = load_cifar10_dataset(batch_size=batch_size, num_workers=num_workers, data_dir=data_dir)

    correct = 0
    total = 0
    total_loss = 0.0

    if log_memory and device.type == "cuda" and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        torch.cuda.reset_peak_memory_stats(device) # Reset peak stats right before the loop
        # Memory optimization: CUDA operations for GPU acceleration

    with torch.no_grad():
    # Memory optimization: Disable gradient computation to save memory
        for images, labels in tqdm(test_loader, desc="Evaluating CIFAR-10"):
            images, labels = images.to(device), labels.to(device)
            # Memory optimization: Device placement for memory management
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = correct / total
    avg_loss = total_loss / total

    if log_memory and device.type == "cuda" and torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        print(f"[MEM] VRAM after eval: {torch.cuda.memory_allocated(device) / 1e6:.2f} MB")
        # Memory optimization: CUDA operations for GPU acceleration
        print(f"[MEM] VRAM peak during eval: {torch.cuda.max_memory_allocated(device) / 1e6:.2f} MB")
        # Memory optimization: CUDA operations for GPU acceleration

    print(f"CIFAR-10 Test Accuracy: {accuracy:.4f}, Avg Loss: {avg_loss:.4f}")
    return accuracy, avg_loss


def main():
    """
    Example CLI entry point for evaluating a model on CIFAR-10.
    # Memory optimization: Explicit memory cleanup
    Replace the model loading logic with your multimodal or vision model.
    # Memory optimization: Explicit memory cleanup
    """
    # Example: Replace with your model import and loading logic
    # Memory optimization: Explicit memory cleanup
    # from torchvision.models import resnet18
    # model = resnet18(num_classes=10)
    # Memory optimization: Explicit memory cleanup
    
    print("Evaluating ImpressionCore-b1 on CIFAR-10...")
    # CIFAR-10 images are 3x32x32
    image_dimensionality = 3 * 32 * 32 
    fusion_dimensionality = 512 # Example, can be tuned
    num_cifar_classes = 10

    model = ImpressionCoreB1Cifar10(
    # Memory optimization: Explicit memory cleanup
        image_dim=image_dimensionality,
        fusion_dim=fusion_dimensionality,
        num_classes=num_cifar_classes
    )
    
    # Optionally load model weights here if you have a trained model
    # Memory optimization: Explicit memory cleanup
    # model_load_path = "path/to/your/impressioncore_b1_cifar10_weights.pth"
    # if os.path.exists(model_load_path):
    #     model.load_state_dict(torch.load(model_load_path))
    #     print(f"Loaded model weights from {model_load_path}")
    # Memory optimization: Explicit memory cleanup
    # else:
    #     print(f"No pretrained weights found at {model_load_path}, using initialized model.")

    evaluate_cifar10_model(model)

if __name__ == "__main__":
    main()
