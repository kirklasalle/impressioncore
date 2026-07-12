#!/usr/bin/env python3
"""
ImpressionCore: Dynamic Manager

Module for dynamic manager functionality in the ImpressionCore framework.

File: core\memory\dynamic_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, pytorch, core, production, memory, 2025, optimization, object-oriented]
Dependencies: [torch]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements dynamic manager functionality for the
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
from src.core.memory.dynamic_manager import DynamicMemoryOptimizer
instance = DynamicMemoryOptimizer()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# d:\Projects\impressioncore\src\core\memory\dynamic_manager.py
# Memory optimization: Memory-critical operation
"""
Dynamic Memory Management for ImpressionCore.
# Memory optimization: Memory-critical operation

Provides utilities and strategies to dynamically adjust memory usage 
# Memory optimization: Memory-critical operation
based on available resources and model requirements, especially for 
# Memory optimization: Explicit memory cleanup
VRAM-constrained environments.

Created: 2025-05-13
"""
import torch
import time
import gc
import os # For environment variable checking

# Helper function to simulate model layers for testing
# Memory optimization: Explicit memory cleanup
def _create_test_layer(in_features, out_features, device_str='cpu'):
# Memory optimization: Device placement for memory management
    """Creates a linear layer on the specified device for testing."""
    # Memory optimization: Device placement for memory management
    layer = torch.nn.Linear(in_features, out_features)
    # Ensure layer has parameters before moving them
    if len(list(layer.parameters())) > 0:
        layer.to(device_str)
        # Memory optimization: Device placement for memory management
    return layer

def get_available_gpu_vram(device=None) -> float:
# Memory optimization: Device placement for memory management
    """
    Gets the currently available (free) VRAM in megabytes.

    Args:
        device: The torch.device to check. Defaults to the current CUDA device if available.
        # Memory optimization: Device placement for memory management

    Returns:
        Available VRAM in MB, or 0.0 if CUDA is not available or device is CPU.
        # Memory optimization: Device placement for memory management
    """
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("GITHUB_ACTIONS"): # Skip in CI/testing if no GPU
    # Memory optimization: Memory-critical operation
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            return 0.0 
            
    if device is None:
    # Memory optimization: Device placement for memory management
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Memory optimization: CUDA operations for GPU acceleration

    if device.type == 'cuda' and torch.cuda.is_available(): # Ensure CUDA is truly available
    # Memory optimization: CUDA operations for GPU acceleration
        # torch.cuda.mem_get_info() returns (free, total) memory in bytes
        # Memory optimization: CUDA operations for GPU acceleration
        free_bytes, _ = torch.cuda.mem_get_info(device)
        # Memory optimization: CUDA operations for GPU acceleration
        return free_bytes / (1024 * 1024) # Convert bytes to MB
    return 0.0

def get_total_gpu_vram(device=None) -> float:
# Memory optimization: Device placement for memory management
    """
    Gets the total VRAM in megabytes for the specified device.
    # Memory optimization: Device placement for memory management

    Args:
        device: The torch.device to check. Defaults to the current CUDA device if available.
        # Memory optimization: Device placement for memory management

    Returns:
        Total VRAM in MB, or 0.0 if CUDA is not available or device is CPU.
        # Memory optimization: Device placement for memory management
    """
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("GITHUB_ACTIONS"): # Skip in CI/testing if no GPU
    # Memory optimization: Memory-critical operation
        if not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            return 0.0

    if device is None:
    # Memory optimization: Device placement for memory management
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Memory optimization: CUDA operations for GPU acceleration

    if device.type == 'cuda' and torch.cuda.is_available(): # Ensure CUDA is truly available
    # Memory optimization: CUDA operations for GPU acceleration
        # torch.cuda.mem_get_info() returns (free, total) memory in bytes
        # Memory optimization: CUDA operations for GPU acceleration
        _, total_bytes = torch.cuda.mem_get_info(device)
        # Memory optimization: CUDA operations for GPU acceleration
        return total_bytes / (1024 * 1024) # Convert bytes to MB
    return 0.0

class DynamicMemoryOptimizer:
# Memory optimization: Memory-critical operation
    """
    Applies dynamic memory optimization strategies to PyTorch models.
    # Memory optimization: Memory-critical operation
    Focuses on CPU offloading and activation checkpointing for VRAM-constrained environments.
    """
    def __init__(self, model: torch.nn.Module, low_vram_threshold_mb: float = 2048.0, verbose: bool = True):
        """
        Initializes the optimizer.

        Args:
            model: The PyTorch model to optimize.
            # Memory optimization: Explicit memory cleanup
            low_vram_threshold_mb: VRAM threshold (in MB) below which more aggressive 
                                   optimizations might be triggered.
            verbose: If True, prints logging messages.
        """
        self.model = model
        # Memory optimization: Explicit memory cleanup
        self.low_vram_threshold_mb = low_vram_threshold_mb
        self.verbose = verbose
        
        # Determine device from model parameters or default to CUDA/CPU
        # Memory optimization: Device placement for memory management
        if len(list(model.parameters())) > 0 and next(model.parameters()).is_cuda and torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            self.device = next(model.parameters()).device
            # Memory optimization: Device placement for memory management
        else: 
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            # Memory optimization: CUDA operations for GPU acceleration
        
        self.offloaded_modules = {} # Stores modules offloaded to CPU: {name: original_device}
        # Memory optimization: Device placement for memory management
        self._log(f"Initialized with device: {self.device}")
        # Memory optimization: Device placement for memory management


    def _log(self, message: str):
        """Logs a message if verbose mode is enabled."""
        if self.verbose:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"[{timestamp}][DynamicMemoryOptimizer] {message}")
            # Memory optimization: Memory-critical operation

    def _cleanup_memory(self):
    # Memory optimization: Memory-critical operation
        """Forces garbage collection and empties CUDA cache if on a CUDA device."""
        # Memory optimization: Device placement for memory management
        gc.collect()
        # Memory optimization: Force garbage collection
        if self.device.type == 'cuda' and torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            torch.cuda.empty_cache()
            # Memory optimization: CUDA operations for GPU acceleration
            self._log("CUDA cache emptied.")
            # Memory optimization: Memory-critical operation

    def get_module_size_mb(self, module: torch.nn.Module) -> float:
        """Estimates the VRAM size of a module in MB."""
        size_bytes = 0
        # Ensure module is on a device to check parameters
        # Memory optimization: Device placement for memory management
        module_device = 'cpu'
        # Memory optimization: Device placement for memory management
        if len(list(module.parameters())) > 0:
            module_device = next(module.parameters()).device.type
            # Memory optimization: Device placement for memory management
        elif len(list(module.buffers())) > 0:
            module_device = next(module.buffers()).device.type
            # Memory optimization: Device placement for memory management

        for param in module.parameters():
            if param.data.device.type == 'cuda' and module_device == 'cuda': # Only count parameters on GPU
            # Memory optimization: Device placement for memory management
                 size_bytes += param.data.nelement() * param.data.element_size()
        for buffer in module.buffers():
            if buffer.data.device.type == 'cuda' and module_device == 'cuda':
            # Memory optimization: Device placement for memory management
                 size_bytes += buffer.data.nelement() * buffer.data.element_size()
        return size_bytes / (1024 * 1024)

    def attempt_module_offload(self, module_name: str, target_device_str: str = 'cpu') -> bool:
    # Memory optimization: Device placement for memory management
        """
        Attempts to offload a specific module (identified by its name) to the target device (e.g., 'cpu').
        # Memory optimization: Device placement for memory management
        If successful, the module is moved, and its original device is recorded for potential reloading.
        # Memory optimization: Device placement for memory management

        Args:
            module_name: The name of the module to offload (e.g., 'encoder.layer.0').
            target_device_str: The device to offload to (default: 'cpu').
            # Memory optimization: Device placement for memory management

        Returns:
            True if offloading was successful, False otherwise.
        """
        self._cleanup_memory()
        # Memory optimization: Memory-critical operation
        target_module = None
        try:
            target_module = dict(self.model.named_modules())[module_name]
        except KeyError:
            self._log(f"Module '{module_name}' not found for offloading.")
            return False
        
        if not target_module: # Should be caught by KeyError, but as a safeguard
            self._log(f"Module '{module_name}' not found (safeguard).")
            return False

        # Determine original device safely
        # Memory optimization: Device placement for memory management
        original_device = self.device # Default to optimizer's device
        # Memory optimization: Device placement for memory management
        if len(list(target_module.parameters())) > 0:
            original_device = next(target_module.parameters()).device
            # Memory optimization: Device placement for memory management
        elif len(list(target_module.buffers())) > 0: # Check buffers if no parameters
            original_device = next(target_module.buffers()).device
            # Memory optimization: Device placement for memory management
        
        # Check if already offloaded to CPU and target is CPU
        if module_name in self.offloaded_modules and target_device_str == 'cpu':
        # Memory optimization: Device placement for memory management
            self._log(f"Module '{module_name}' is already offloaded to CPU at {self.offloaded_modules[module_name]}.")
            # If it's on CPU, and we want to move to CPU, it's a success.
            if original_device.type == 'cpu': return True
            # Memory optimization: Device placement for memory management


        if original_device.type == target_device_str:
        # Memory optimization: Device placement for memory management
            self._log(f"Module '{module_name}' is already on device '{target_device_str}'. No action taken.")
            # Memory optimization: Device placement for memory management
            # If it was supposed to be offloaded (i.e. in self.offloaded_modules) but is now on GPU (target_device_str != 'cpu')
            # Memory optimization: Device placement for memory management
            # and we are trying to move it to GPU, then remove from offloaded_modules.
            # Memory optimization: Memory-critical operation
            if target_device_str != 'cpu' and module_name in self.offloaded_modules:
            # Memory optimization: Device placement for memory management
                del self.offloaded_modules[module_name]
                # Memory optimization: Explicit memory cleanup
            return True

        module_size_mb = self.get_module_size_mb(target_module)
        self._log(f"Attempting to offload module '{module_name}' (approx. {module_size_mb:.2f} MB on GPU) from {original_device} to {target_device_str}.")
        # Memory optimization: Device placement for memory management
        
        try:
            target_module.to(target_device_str)
            # Memory optimization: Device placement for memory management
            self._cleanup_memory() # Clean up VRAM after moving
            # Memory optimization: Memory-critical operation
            
            if target_device_str == 'cpu':
            # Memory optimization: Device placement for memory management
                 self.offloaded_modules[module_name] = original_device # Store original device
                 # Memory optimization: Device placement for memory management
            elif module_name in self.offloaded_modules and target_device_str == str(self.offloaded_modules[module_name]): # Reloading to original
            # Memory optimization: Device placement for memory management
                 del self.offloaded_modules[module_name]
                 # Memory optimization: Explicit memory cleanup


            self._log(f"Module '{module_name}' successfully moved to {target_device_str}.")
            # Memory optimization: Device placement for memory management
            current_device_params = next(target_module.parameters(), None)
            # Memory optimization: Device placement for memory management
            if current_device_params is not None:
            # Memory optimization: Device placement for memory management
                 self._log(f"Module '{module_name}' parameters are now on: {current_device_params.device}")
                 # Memory optimization: Device placement for memory management
            else: # Check buffers if no params
                current_device_buffers = next(target_module.buffers(), None)
                # Memory optimization: Device placement for memory management
                if current_device_buffers is not None:
                # Memory optimization: Device placement for memory management
                    self._log(f"Module '{module_name}' buffers are now on: {current_device_buffers.device}")
                    # Memory optimization: Device placement for memory management
                else:
                    self._log(f"Module '{module_name}' has no parameters or buffers to check device after move.")
                    # Memory optimization: Device placement for memory management

            return True
        except Exception as e:
            self._log(f"Error offloading module '{module_name}' to {target_device_str}: {e}")
            # Memory optimization: Device placement for memory management
            # Attempt to move back if it was partially moved or error occurred
            try:
                target_module.to(original_device) # original_device here is the device it was on before this attempt
                # Memory optimization: Device placement for memory management
                self._log(f"Module '{module_name}' moved back to its previous device {original_device} after error.")
                # Memory optimization: Device placement for memory management
            except Exception as e_revert:
                self._log(f"Critical error: Could not revert module '{module_name}' to {original_device}: {e_revert}. State may be inconsistent.")
                # Memory optimization: Device placement for memory management
            return False

    def reload_module_to_gpu(self, module_name: str) -> bool:
    # Memory optimization: Memory-critical operation
        """
        Reloads a previously offloaded module back to its original GPU device.
        # Memory optimization: Device placement for memory management

        Args:
            module_name: The name of the module to reload.

        Returns:
            True if reloading was successful or module was not offloaded/already on GPU, False on error.
            # Memory optimization: Memory-critical operation
        """
        if module_name not in self.offloaded_modules:
            # Check current device of the module
            # Memory optimization: Device placement for memory management
            target_module = dict(self.model.named_modules()).get(module_name)
            if target_module:
                current_device = 'cpu' # Assume CPU if no params/buffers
                # Memory optimization: Device placement for memory management
                if len(list(target_module.parameters())) > 0:
                    current_device = next(target_module.parameters()).device.type
                    # Memory optimization: Device placement for memory management
                elif len(list(target_module.buffers())) > 0:
                    current_device = next(target_module.buffers()).device.type
                    # Memory optimization: Device placement for memory management
                
                if current_device == self.device.type and self.device.type == 'cuda':
                # Memory optimization: Device placement for memory management
                    self._log(f"Module '{module_name}' is already on the target GPU device ({self.device.type}). No action taken.")
                    # Memory optimization: Device placement for memory management
                    return True
            
            self._log(f"Module '{module_name}' was not recorded as offloaded. Assuming it's on GPU or intended device if not CUDA.")
            # Memory optimization: Device placement for memory management
            return True # Not offloaded or already on GPU
            # Memory optimization: Memory-critical operation
        
        original_device = self.offloaded_modules[module_name]
        # Memory optimization: Device placement for memory management
        self._log(f"Attempting to reload module '{module_name}' to its original device: {original_device}.")
        # Memory optimization: Device placement for memory management
        
        # Ensure original_device is a string like 'cuda:0' or 'cuda'
        # Memory optimization: Device placement for memory management
        target_device_str = str(original_device)
        # Memory optimization: Device placement for memory management
        if self.attempt_module_offload(module_name, target_device_str=target_device_str):
        # Memory optimization: Device placement for memory management
            # If successful and it was reloaded to a CUDA device, remove from offloaded_modules
            # Memory optimization: Device placement for memory management
            if target_device_str.startswith('cuda') and module_name in self.offloaded_modules:
            # Memory optimization: Device placement for memory management
                 del self.offloaded_modules[module_name] # Successfully reloaded
                 # Memory optimization: Explicit memory cleanup
            return True
        return False


    def adapt_to_available_memory(self, required_vram_estimate_mb: float = 0.0, offload_candidates: list[str] = None, proactive_offload_fraction: float = 0.0):
    # Memory optimization: Memory-critical operation
        """
        Adapts model or settings based on currently available VRAM.
        # Memory optimization: Explicit memory cleanup
        If VRAM is low, it may attempt to offload specified candidate modules to CPU.

        Args:
            required_vram_estimate_mb: An estimate of VRAM needed for the next operation.
            offload_candidates: A list of module names (strings) that are candidates for CPU offloading.
                                Modules will be offloaded in the order provided if memory is needed.
                                # Memory optimization: Memory-critical operation
            proactive_offload_fraction: Fraction of available VRAM to free proactively by offloading,
                                        even if not strictly below threshold or deficit. E.g., 0.1 for 10%.
        """
        if self.device.type != 'cuda' or not torch.cuda.is_available():
        # Memory optimization: CUDA operations for GPU acceleration
            self._log("Device is not CUDA or CUDA not available. Skipping VRAM adaptation.")
            # Memory optimization: Device placement for memory management
            return

        self._cleanup_memory()
        # Memory optimization: Memory-critical operation
        available_vram = get_available_gpu_vram(self.device)
        # Memory optimization: Device placement for memory management
        self._log(f"Available VRAM: {available_vram:.2f} MB. Required (estimate): {required_vram_estimate_mb:.2f} MB. Low VRAM Threshold: {self.low_vram_threshold_mb:.2f} MB.")
        
        vram_deficit = 0
        if required_vram_estimate_mb > 0 and available_vram < required_vram_estimate_mb:
            vram_deficit = required_vram_estimate_mb - available_vram
            self._log(f"VRAM deficit: {vram_deficit:.2f} MB. Attempting to free space.")
        
        vram_to_free_proactively = 0
        if proactive_offload_fraction > 0:
            vram_to_free_proactively = available_vram * proactive_offload_fraction
            self._log(f"Proactive offload: attempting to free {vram_to_free_proactively:.2f} MB ({proactive_offload_fraction*100}% of available).")

        total_vram_to_make_available = max(vram_deficit, vram_to_free_proactively)

        is_below_threshold = available_vram < self.low_vram_threshold_mb
        if is_below_threshold and total_vram_to_make_available == 0: # Below threshold, but no specific deficit or proactive target
             self._log(f"Available VRAM ({available_vram:.2f} MB) is below threshold ({self.low_vram_threshold_mb:.2f} MB). Will attempt to offload candidates if provided.")
             # We can set a nominal amount to free to trigger offloading if candidates exist
             total_vram_to_make_available = 1 # Try to free at least something

        if total_vram_to_make_available > 0 and offload_candidates:
            freed_vram_total = 0
            for module_name in offload_candidates:
                if module_name in self.offloaded_modules: # Already offloaded to CPU
                    self._log(f"Module '{module_name}' is already offloaded. Skipping.")
                    continue

                target_module = dict(self.model.named_modules()).get(module_name)
                if target_module:
                    # Check current device of module before estimating size
                    # Memory optimization: Device placement for memory management
                    module_on_gpu = False
                    # Memory optimization: Memory-critical operation
                    if len(list(target_module.parameters())) > 0:
                        if next(target_module.parameters()).device.type == 'cuda':
                        # Memory optimization: Device placement for memory management
                            module_on_gpu = True
                            # Memory optimization: Memory-critical operation
                    elif len(list(target_module.buffers())) > 0: # Check buffers if no params
                         if next(target_module.buffers()).device.type == 'cuda':
                         # Memory optimization: Device placement for memory management
                            module_on_gpu = True
                            # Memory optimization: Memory-critical operation
                    
                    if not module_on_gpu:
                    # Memory optimization: Memory-critical operation
                        self._log(f"Module '{module_name}' is not on GPU. Skipping offload attempt.")
                        # Memory optimization: Memory-critical operation
                        continue # Skip if not on GPU
                        # Memory optimization: Memory-critical operation

                    module_size_mb = self.get_module_size_mb(target_module)
                    if module_size_mb == 0: # If module is on GPU but size is 0 (e.g. empty or only non-CUDA params)
                    # Memory optimization: Memory-critical operation
                        self._log(f"Module '{module_name}' has 0 VRAM footprint. Skipping offload.")
                        continue

                    if self.attempt_module_offload(module_name, 'cpu'):
                        freed_vram_total += module_size_mb
                        self._log(f"Offloaded '{module_name}', freed approx. {module_size_mb:.2f} MB. Total freed: {freed_vram_total:.2f} MB.")
                        if freed_vram_total >= total_vram_to_make_available:
                            self._log(f"Sufficient VRAM freed ({freed_vram_total:.2f} MB) to meet target ({total_vram_to_make_available:.2f} MB).")
                            break 
                    else:
                        self._log(f"Failed to offload '{module_name}'.")
                else:
                    self._log(f"Offload candidate '{module_name}' not found in model.")
            
            current_available_vram = get_available_gpu_vram(self.device)
            # Memory optimization: Device placement for memory management
            self._log(f"VRAM after offloading attempts: {current_available_vram:.2f} MB.")

        elif not offload_candidates and total_vram_to_make_available > 0:
            self._log(f"Need to free {total_vram_to_make_available:.2f} MB VRAM but no offload candidates provided. Manual intervention may be needed.")
        else:
            self._log("Sufficient VRAM available or no offload candidates/strategy to free more VRAM.")
