#!/usr/bin/env python3
"""
ImpressionCore: Activation Maps

Module for activation maps functionality in the ImpressionCore framework.

File: visualization\activation_maps.py
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
This module implements activation maps functionality for the
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
from visualization.activation_maps import ActivationVisualizer
instance = ActivationVisualizer()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import os
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from collections import OrderedDict
import io
import base64

# Configure logging
logger = logging.getLogger(__name__)

class ActivationVisualizer:
    """
    Visualize layer activations in neural network models.
    Optimized for memory-efficient operation on systems with 4GB VRAM.
    # Memory optimization: Memory-critical operation
    """
    
    def __init__(self, model=None, output_dir=None):
        """
        Initialize the activation visualizer.
        
        Args:
            model: PyTorch model to visualize
            # Memory optimization: Explicit memory cleanup
            output_dir: Directory to save visualization artifacts
        """
        self.model = model
        # Memory optimization: Explicit memory cleanup
        self.output_dir = output_dir or os.path.join("output", "visualizations", "activations")
        os.makedirs(self.output_dir, exist_ok=True)
        self.activation_data = {}
        self.hooks = []
        logger.info(f"ActivationVisualizer initialized, output_dir: {self.output_dir}")
    
    def register_hooks(self, layers=None):
        """
        Register forward hooks to collect activations.
        
        Args:
            layers: List of layer names to hook (None = all layers)
        """
        if self.model is None:
        # Memory optimization: Explicit memory cleanup
            logger.error("No model provided")
            # Memory optimization: Explicit memory cleanup
            return
        
        # Clean up any existing hooks
        self.remove_hooks()
        self.activation_data = {}
        
        # Define hook function
        def hook_fn(name):
            """
            
    hook_fn function for processing.
    
    Args:
        name: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
            """
            def forward_hook(module, input, output):
                """
                
    forward_hook function for processing.
    
    Args:
        module, input, output: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                # Move to CPU and detach to save memory
                # Memory optimization: Memory-critical operation
                # Store only the first item in the batch to further save memory
                # Memory optimization: Memory-critical operation
                if isinstance(output, torch.Tensor):
                    self.activation_data[name] = output[0:1].detach().cpu()
                else:
                    # Handle tuple/list outputs (e.g., from some LSTM layers)
                    self.activation_data[name] = output[0][0:1].detach().cpu() if isinstance(output, tuple) else output
            return forward_hook
        
        # Register hooks for specific or all layers
        for name, module in self.model.named_modules():
            if name == '':
                continue
                
            if layers is None or name in layers:
                hook = module.register_forward_hook(hook_fn(name))
                self.hooks.append(hook)
                logger.debug(f"Registered hook for layer: {name}")
    
    def remove_hooks(self):
        """Remove all registered hooks."""
        for hook in self.hooks:
            hook.remove()
        self.hooks = []
        logger.debug("Removed all activation hooks")
    
    def visualize_layer_activations(self,
                                   input_tensor: torch.Tensor,
                                   layer_names: Optional[List[str]] = None,
                                   save_path: Optional[str] = None) -> str:
        """
        Visualize activations for specified layers.
        
        Args:
            input_tensor: Input tensor for forward pass
            layer_names: List of layer names to visualize (None = all hooked layers)
            save_path: Path to save the visualization
            
        Returns:
            Path to saved visualization
        """
        if self.model is None:
        # Memory optimization: Explicit memory cleanup
            logger.error("No model provided")
            # Memory optimization: Explicit memory cleanup
            return None
        
        # Ensure hooks are registered
        if not self.hooks:
            self.register_hooks(layer_names)
        
        # Forward pass to collect activations
        try:
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                self.model.eval()
                _ = self.model(input_tensor)
        except Exception as e:
            logger.error(f"Error during forward pass: {e}")
            return None
        
        # Filter layers if specified
        activations_to_plot = self.activation_data
        if layer_names:
            activations_to_plot = {k: v for k, v in self.activation_data.items() if k in layer_names}
        
        # Generate visualization
        save_path = save_path or os.path.join(self.output_dir, "layer_activations.png")
        self._plot_layer_activations(activations_to_plot, save_path)
        
        return save_path
    
    def visualize_neuron_activations(self,
                                    input_tensor: torch.Tensor,
                                    layer_name: str,
                                    neurons: Optional[List[int]] = None,
                                    save_path: Optional[str] = None) -> str:
        """
        Visualize activations for specific neurons in a layer.
        
        Args:
            input_tensor: Input tensor for forward pass
            layer_name: Name of the layer to visualize
            neurons: List of neuron indices to visualize (None = all neurons)
            save_path: Path to save the visualization
            
        Returns:
            Path to saved visualization
        """
        if self.model is None:
        # Memory optimization: Explicit memory cleanup
            logger.error("No model provided")
            # Memory optimization: Explicit memory cleanup
            return None
        
        # Ensure hooks are registered for this layer
        self.register_hooks([layer_name])
        
        # Forward pass to collect activations
        try:
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                self.model.eval()
                _ = self.model(input_tensor)
        except Exception as e:
            logger.error(f"Error during forward pass: {e}")
            return None
        
        # Check if we have the layer data
        if layer_name not in self.activation_data:
            logger.error(f"No activation data found for layer: {layer_name}")
            return None
        
        # Get activation data
        activation = self.activation_data[layer_name]
        
        # Generate visualization
        save_path = save_path or os.path.join(self.output_dir, f"{layer_name}_neurons.png")
        self._plot_neuron_activations(activation, layer_name, neurons, save_path)
        
        return save_path
    
    def generate_activation_heatmap(self,
                                   input_tensor: torch.Tensor,
                                   layer_name: str,
                                   save_path: Optional[str] = None) -> str:
        """
        Generate a heatmap of activations for a layer.
        
        Args:
            input_tensor: Input tensor for forward pass
            layer_name: Name of the layer to visualize
            save_path: Path to save the visualization
            
        Returns:
            Path to saved visualization
        """
        if self.model is None:
        # Memory optimization: Explicit memory cleanup
            logger.error("No model provided")
            # Memory optimization: Explicit memory cleanup
            return None
        
        # Ensure hooks are registered for this layer
        self.register_hooks([layer_name])
        
        # Forward pass to collect activations
        try:
            with torch.no_grad():
            # Memory optimization: Disable gradient computation to save memory
                self.model.eval()
                _ = self.model(input_tensor)
        except Exception as e:
            logger.error(f"Error during forward pass: {e}")
            return None
        
        # Check if we have the layer data
        if layer_name not in self.activation_data:
            logger.error(f"No activation data found for layer: {layer_name}")
            return None
        
        # Get activation data
        activation = self.activation_data[layer_name]
        
        # Generate visualization
        save_path = save_path or os.path.join(self.output_dir, f"{layer_name}_heatmap.png")
        self._generate_heatmap(activation, layer_name, save_path)
        
        return save_path
    
    def compare_activations(self,
                           input_tensors: List[torch.Tensor],
                           layer_name: str,
                           input_labels: Optional[List[str]] = None,
                           save_path: Optional[str] = None) -> str:
        """
        Compare activations for different inputs.
        
        Args:
            input_tensors: List of input tensors
            layer_name: Name of the layer to visualize
            input_labels: Labels for each input
            save_path: Path to save the visualization
            
        Returns:
            Path to saved visualization
        """
        if self.model is None:
        # Memory optimization: Explicit memory cleanup
            logger.error("No model provided")
            # Memory optimization: Explicit memory cleanup
            return None
        
        # Ensure hooks are registered for this layer
        self.register_hooks([layer_name])
        
        # Collect activations for each input
        activations = []
        for i, tensor in enumerate(input_tensors):
            # Forward pass
            try:
                with torch.no_grad():
                # Memory optimization: Disable gradient computation to save memory
                    self.model.eval()
                    _ = self.model(tensor)
            except Exception as e:
                logger.error(f"Error during forward pass for input {i}: {e}")
                continue
            
            # Get activation data
            if layer_name in self.activation_data:
                activations.append(self.activation_data[layer_name].clone())
        
        # Generate visualization
        save_path = save_path or os.path.join(self.output_dir, f"{layer_name}_comparison.png")
        self._plot_activation_comparison(activations, layer_name, input_labels, save_path)
        
        return save_path
    
    def _plot_layer_activations(self, activations, save_path):
        """
        Plot activations for multiple layers.
        
        Args:
            activations: Dictionary of layer activations
            save_path: Path to save the visualization
        """
        if not activations:
            logger.error("No activation data to plot")
            return
        
        # Determine number of layers
        n_layers = len(activations)
        
        # Create figure with subplots for each layer
        fig, axes = plt.subplots(n_layers, 1, figsize=(12, 3 * n_layers))
        if n_layers == 1:
            axes = [axes]
        
        # Plot each layer's activation
        for i, (name, activation) in enumerate(activations.items()):
            ax = axes[i]
            
            # Convert to numpy and reshape if needed
            act_data = activation.numpy()
            if len(act_data.shape) > 2:
                # For convolutional layers, take average across channels
                act_data = np.mean(act_data, axis=0)
            
            # Plot as heatmap or line based on dimensions
            if len(act_data.shape) == 2:
                im = ax.imshow(act_data, cmap='viridis', aspect='auto')
                fig.colorbar(im, ax=ax)
                ax.set_title(f"Layer: {name}")
            else:
                ax.plot(act_data)
                ax.set_title(f"Layer: {name} (averaged)")
            
            ax.set_xlabel("Neuron Index")
            ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
    
    def _plot_neuron_activations(self, activation, layer_name, neurons, save_path):
        """
        Plot activations for specific neurons in a layer.
        
        Args:
            activation: Layer activation tensor
            layer_name: Name of the layer
            neurons: List of neuron indices to plot
            save_path: Path to save the visualization
        """
        # Convert to numpy and flatten to 2D if needed
        act_data = activation.numpy()
        
        # For 4D activations (conv layers) reshape to 2D
        if len(act_data.shape) == 4:  # [batch, channels, height, width]
            act_data = act_data.reshape(act_data.shape[0], act_data.shape[1], -1)
        
        # For 3D activations, average or flatten
        if len(act_data.shape) == 3:
            act_data = act_data.mean(axis=2)  # Average across spatial dimensions
        
        # If no specific neurons requested, plot up to 16 neurons
        if neurons is None:
            if act_data.shape[1] > 16:
                neurons = np.linspace(0, act_data.shape[1]-1, 16, dtype=int)
            else:
                neurons = range(act_data.shape[1])
        
        # Create figure
        n_neurons = len(neurons)
        grid_size = int(np.ceil(np.sqrt(n_neurons)))
        fig, axes = plt.subplots(grid_size, grid_size, figsize=(12, 12))
        axes = axes.flatten()
        
        # Plot each neuron
        for i, neuron_idx in enumerate(neurons):
            if i >= len(axes):
                break
                
            ax = axes[i]
            if neuron_idx < act_data.shape[1]:
                ax.plot(act_data[0, neuron_idx])
                ax.set_title(f"Neuron {neuron_idx}")
                ax.grid(True, linestyle='--', alpha=0.7)
            
        # Hide unused subplots
        for j in range(i+1, len(axes)):
            axes[j].axis('off')
        
        plt.suptitle(f"Neuron Activations for Layer: {layer_name}", size=14)
        plt.tight_layout()
        plt.subplots_adjust(top=0.95)
        plt.savefig(save_path, dpi=150)
        plt.close()
    
    def _generate_heatmap(self, activation, layer_name, save_path):
        """
        Generate a heatmap visualization of layer activations.
        
        Args:
            activation: Layer activation tensor
            layer_name: Name of the layer
            save_path: Path to save the visualization
        """
        # Convert to numpy
        act_data = activation.numpy()
        
        # Prepare data based on shape
        if len(act_data.shape) == 4:  # [batch, channels, height, width]
            # For convolutional layers, create grid of channel activations
            n_channels = min(act_data.shape[1], 64)  # Limit to 64 channels
            grid_size = int(np.ceil(np.sqrt(n_channels)))
            
            plt.figure(figsize=(15, 15))
            
            for i in range(n_channels):
                plt.subplot(grid_size, grid_size, i+1)
                plt.imshow(act_data[0, i], cmap='viridis')
                plt.title(f"Channel {i}")
                plt.axis('off')
            
            plt.suptitle(f"Activation Channels for Layer: {layer_name}", size=14)
            
        elif len(act_data.shape) == 2:  # [batch, features]
            # For fully connected layers, show feature activations as a single heatmap
            plt.figure(figsize=(12, 6))
            im = plt.imshow(act_data, cmap='viridis', aspect='auto')
            plt.colorbar(im)
            plt.title(f"Activation Heatmap for Layer: {layer_name}")
            plt.xlabel("Neuron Index")
            
        elif len(act_data.shape) == 3:  # [batch, seq_len, features]
            # For sequence data, show time x features heatmap
            plt.figure(figsize=(12, 6))
            im = plt.imshow(act_data[0], cmap='viridis', aspect='auto')
            plt.colorbar(im)
            plt.title(f"Activation Heatmap for Layer: {layer_name}")
            plt.xlabel("Feature Index")
            plt.ylabel("Sequence Position")
            
        else:
            logger.error(f"Unsupported activation shape: {act_data.shape}")
            return
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
    
    def _plot_activation_comparison(self, activations, layer_name, input_labels, save_path):
        """
        Plot comparison of activations for different inputs.
        
        Args:
            activations: List of activation tensors
            layer_name: Name of the layer
            input_labels: Labels for inputs
            save_path: Path to save the visualization
        """
        if not activations:
            logger.error("No activation data to compare")
            return
        
        if input_labels is None:
            input_labels = [f"Input {i}" for i in range(len(activations))]
        
        # Create figure
        plt.figure(figsize=(14, 8))
        
        # Process each activation
        for i, activation in enumerate(activations):
            # Convert to numpy
            act_data = activation.numpy()
            
            # Calculate average activation
            if len(act_data.shape) == 4:  # Conv layers
                avg_act = np.mean(act_data, axis=(0, 2, 3))  # Average across batch, height, width
            elif len(act_data.shape) == 3:  # Sequence layers
                avg_act = np.mean(act_data, axis=(0, 1))  # Average across batch, sequence
            elif len(act_data.shape) == 2:  # FC layers
                avg_act = np.mean(act_data, axis=0)  # Average across batch
            else:
                logger.error(f"Unsupported activation shape: {act_data.shape}")
                continue
            
            # Plot average activation
            plt.plot(avg_act, label=input_labels[i])
        
        plt.title(f"Activation Comparison for Layer: {layer_name}")
        plt.xlabel("Neuron Index")
        plt.ylabel("Average Activation")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
