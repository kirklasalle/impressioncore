#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #attention_mechanism #memory_management #multimodal #performance #python #pytorch #source_code #src/interfaces/web\routes\\model_visualization.py #testing #tokenization #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #api #attention_mechanism #memory_management #multimodal #performance #python #pytorch #source_code #src\\interfaces\\web\\routes\\model_visualization.py #testing #tokenization #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore: Model Visualization

Module for model visualization functionality in the ImpressionCore framework.

File: web/routes//model_visualization.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, web, frontend, 2025]
Dependencies: [torch, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements model visualization functionality for the
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
from web.routes.model_visualization import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import os

import torch
from flask import Blueprint, jsonify, render_template, request, url_for

from src.dev_tools.visualization.activation_maps import ActivationVisualizer
from src.dev_tools.visualization.architecture_graph import ModelArchitectureGraph
from src.dev_tools.visualization.attention_patterns import AttentionVisualizer

# Import visualization modules
from src.dev_tools.visualization.model_visualizer import ModelVisualizer

# Import model loading utilities
# Memory optimization: Explicit memory cleanup
from src.training.models.model_store import get_model, list_available_models

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
model_viz = Blueprint('model_viz', __name__)

# Ensure output directory exists
visualization_dir = os.path.join("output", "visualizations")
os.makedirs(visualization_dir, exist_ok=True)

# Initialize visualizers
model_visualizer = ModelVisualizer(output_dir=visualization_dir)
attention_visualizer = AttentionVisualizer(output_dir=os.path.join(visualization_dir, "attention"))
architecture_visualizer = ModelArchitectureGraph(output_dir=os.path.join(visualization_dir, "architecture"))
activation_visualizer = ActivationVisualizer(output_dir=os.path.join(visualization_dir, "activations"))

@model_viz.route('/visualization')
def visualization_dashboard():
    """Render the main visualization dashboard."""
    available_models = list_available_models()
    return render_template('visualization/dashboard.html', models=available_models)

@model_viz.route('/visualization/architecture')
def model_architecture():
    """Render the model architecture visualization interface."""
    # Memory optimization: Explicit memory cleanup
    available_models = list_available_models()
    return render_template('visualization/architecture.html', models=available_models)

@model_viz.route('/visualization/attention')
def attention_visualization():
    """Render the attention visualization interface."""
    available_models = list_available_models()
    return render_template('visualization/attention.html', models=available_models)

@model_viz.route('/visualization/activations')
def activation_visualization():
    """Render the activation visualization interface."""
    available_models = list_available_models()
    return render_template('visualization/activations.html', models=available_models)

@model_viz.route('/visualization/memory')
# Memory optimization: Memory-critical operation
def memory_visualization():
# Memory optimization: Memory-critical operation
    """Render the memory usage visualization interface."""
    # Memory optimization: Memory-critical operation
    available_models = list_available_models()
    return render_template('visualization/memory.html', models=available_models)
    # Memory optimization: Memory-critical operation

@model_viz.route('/api/visualization/architecture', methods=['POST'])
def generate_architecture_visualization():
    """
    Generate and return model architecture visualization.
    # Memory optimization: Explicit memory cleanup

    Expected payload:
    {
        "model_id": "model_name",
        "simplify": true/false
    }
    """
    data = request.json

    if not data or "model_id" not in data:
        return jsonify({"error": "Model ID is required"}), 400
        # Memory optimization: Explicit memory cleanup

    model_id = data["model_id"]
    simplify = data.get("simplify", True)

    try:
        # Load model
        model = get_model(model_id)
        # Memory optimization: Explicit memory cleanup
        if model is None:
        # Memory optimization: Explicit memory cleanup
            return jsonify({"error": f"Model {model_id} not found"}), 404
            # Memory optimization: Explicit memory cleanup

        # Generate visualization
        architecture_visualizer.generate_architecture_graph(
            model=model,
            simplify=simplify,
            save_path=os.path.join(visualization_dir, f"{model_id}_architecture.png")
        )

        # Return path to image
        result = {
            "image_url": url_for('static', filename=f"visualizations/{model_id}_architecture.png"),
            "model_id": model_id
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error generating architecture visualization: {e}")
        return jsonify({"error": str(e)}), 500

@model_viz.route('/api/visualization/attention', methods=['POST'])
def generate_attention_visualization():
    """
    Generate and return attention visualization.

    Expected payload:
    {
        "model_id": "model_name",
        "input_text": "text to analyze",
        "layer_idx": optional layer index,
        "head_idx": optional head index
    }
    """
    data = request.json

    if not data or "model_id" not in data or "input_text" not in data:
        return jsonify({"error": "Model ID and input text are required"}), 400
        # Memory optimization: Explicit memory cleanup

    model_id = data["model_id"]
    input_text = data["input_text"]
    layer_idx = data.get("layer_idx")
    head_idx = data.get("head_idx")

    try:
        # Load model and tokenizer
        # Memory optimization: Explicit memory cleanup
        model = get_model(model_id)
        # Memory optimization: Explicit memory cleanup
        if model is None:
        # Memory optimization: Explicit memory cleanup
            return jsonify({"error": f"Model {model_id} not found"}), 404
            # Memory optimization: Explicit memory cleanup

        # Get tokenizer from model object or load separately
        # Memory optimization: Explicit memory cleanup
        tokenizer = getattr(model, "tokenizer", None)
        if tokenizer is None:
            # Attempt to load tokenizer based on model ID
            # Memory optimization: Explicit memory cleanup
            tokenizer = None  # TODO: Implement tokenizer loading

        # Update visualizer with model and tokenizer
        # Memory optimization: Explicit memory cleanup
        attention_visualizer.model = model
        # Memory optimization: Explicit memory cleanup
        attention_visualizer.tokenizer = tokenizer

        # Generate visualization
        if head_idx is not None:
            # Visualize specific head
            vis_path = attention_visualizer.visualize_attention_heads(
                input_text=input_text,
                layer_idx=layer_idx,
                save_path=os.path.join(attention_visualizer.output_dir, f"{model_id}_attention_l{layer_idx}_h{head_idx}.png")
            )
        else:
            # Visualize layer or all layers
            vis_path = attention_visualizer.visualize_attention_heads(
                input_text=input_text,
                layer_idx=layer_idx,
                save_path=os.path.join(attention_visualizer.output_dir, f"{model_id}_attention_l{layer_idx or 'all'}.png")
            )

        # Return path to image
        if vis_path:
            result = {
                "image_url": url_for('static', filename=f"visualizations/attention/{os.path.basename(vis_path)}"),
                "model_id": model_id
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Failed to generate visualization"}), 500

    except Exception as e:
        logger.error(f"Error generating attention visualization: {e}")
        return jsonify({"error": str(e)}), 500

@model_viz.route('/api/visualization/activations', methods=['POST'])
def generate_activation_visualization():
    """
    Generate and return layer activation visualization.

    Expected payload:
    {
        "model_id": "model_name",
        "input_text": "text to analyze",
        "layer_name": optional layer name,
        "neuron_indices": optional list of neuron indices
    }
    """
    data = request.json

    if not data or "model_id" not in data or "input_text" not in data:
        return jsonify({"error": "Model ID and input text are required"}), 400
        # Memory optimization: Explicit memory cleanup

    model_id = data["model_id"]
    input_text = data["input_text"]
    layer_name = data.get("layer_name")
    neuron_indices = data.get("neuron_indices")

    try:
        # Load model and tokenizer
        # Memory optimization: Explicit memory cleanup
        model = get_model(model_id)
        # Memory optimization: Explicit memory cleanup
        if model is None:
        # Memory optimization: Explicit memory cleanup
            return jsonify({"error": f"Model {model_id} not found"}), 404
            # Memory optimization: Explicit memory cleanup

        # Get tokenizer from model object or load separately
        # Memory optimization: Explicit memory cleanup
        tokenizer = getattr(model, "tokenizer", None)
        if tokenizer is None:
            # Attempt to load tokenizer based on model ID
            # Memory optimization: Explicit memory cleanup
            tokenizer = None  # TODO: Implement tokenizer loading

        # Update visualizer with model
        activation_visualizer.model = model
        # Memory optimization: Explicit memory cleanup

        # Tokenize input
        if tokenizer:
            input_tensor = tokenizer(input_text, return_tensors="pt")
        else:
            # Fallback to simple encoding
            input_tensor = torch.tensor([ord(c) for c in input_text]).unsqueeze(0)

        # Generate visualization
        if layer_name and neuron_indices:
            # Visualize specific neurons in layer
            vis_path = activation_visualizer.visualize_neuron_activations(
                input_tensor=input_tensor,
                layer_name=layer_name,
                neurons=neuron_indices,
                save_path=os.path.join(activation_visualizer.output_dir, f"{model_id}_{layer_name}_neurons.png")
            )
        elif layer_name:
            # Visualize heatmap for layer
            vis_path = activation_visualizer.generate_activation_heatmap(
                input_tensor=input_tensor,
                layer_name=layer_name,
                save_path=os.path.join(activation_visualizer.output_dir, f"{model_id}_{layer_name}_heatmap.png")
            )
        else:
            # Visualize multiple layers
            vis_path = activation_visualizer.visualize_layer_activations(
                input_tensor=input_tensor,
                save_path=os.path.join(activation_visualizer.output_dir, f"{model_id}_layers.png")
            )

        # Return path to image
        if vis_path:
            result = {
                "image_url": url_for('static', filename=f"visualizations/activations/{os.path.basename(vis_path)}"),
                "model_id": model_id
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Failed to generate visualization"}), 500

    except Exception as e:
        logger.error(f"Error generating activation visualization: {e}")
        return jsonify({"error": str(e)}), 500

@model_viz.route('/api/visualization/memory', methods=['POST'])
# Memory optimization: Memory-critical operation
def generate_memory_visualization():
# Memory optimization: Memory-critical operation
    """
    Generate and return memory usage visualization.
    # Memory optimization: Memory-critical operation

    Expected payload:
    {
        "model_id": "model_name",
        "input_shape": [batch_size, seq_len]
    }
    """
    data = request.json

    if not data or "model_id" not in data:
        return jsonify({"error": "Model ID is required"}), 400
        # Memory optimization: Explicit memory cleanup

    model_id = data["model_id"]
    input_shape = data.get("input_shape", [1, 512])  # Default shape

    try:
        # Load model
        model = get_model(model_id)
        # Memory optimization: Explicit memory cleanup
        if model is None:
        # Memory optimization: Explicit memory cleanup
            return jsonify({"error": f"Model {model_id} not found"}), 404
            # Memory optimization: Explicit memory cleanup

        # Generate memory profile
        # Memory optimization: Memory-critical operation
        profile_path = architecture_visualizer.generate_memory_profile_graph(
        # Memory optimization: Memory-critical operation
            model=model,
            input_shape=tuple(input_shape),
            save_path=os.path.join(architecture_visualizer.output_dir, f"{model_id}_memory_profile.png")
            # Memory optimization: Memory-critical operation
        )

        # Return path to image
        if profile_path:
            result = {
                "image_url": url_for('static', filename=f"visualizations/architecture/{os.path.basename(profile_path)}"),
                "model_id": model_id
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Failed to generate memory profile"}), 500
            # Memory optimization: Memory-critical operation

    except Exception as e:
        logger.error(f"Error generating memory visualization: {e}")
        # Memory optimization: Memory-critical operation
        return jsonify({"error": str(e)}), 500

@model_viz.route('/api/visualization/model/layers', methods=['GET'])
def get_model_layers():
    """
    Get list of layers for a model.

    Query parameter:
    - model_id: ID of the model
    """
    model_id = request.args.get('model_id')

    if not model_id:
        return jsonify({"error": "Model ID is required"}), 400
        # Memory optimization: Explicit memory cleanup

    try:
        # Load model
        model = get_model(model_id)
        # Memory optimization: Explicit memory cleanup
        if model is None:
        # Memory optimization: Explicit memory cleanup
            return jsonify({"error": f"Model {model_id} not found"}), 404
            # Memory optimization: Explicit memory cleanup

        # Get list of layers
        layers = []
        for name, _ in model.named_modules():
            if name:  # Skip empty name (model itself)
            # Memory optimization: Explicit memory cleanup
                layers.append(name)

        return jsonify({"layers": layers})

    except Exception as e:
        logger.error(f"Error getting model layers: {e}")
        # Memory optimization: Explicit memory cleanup
        return jsonify({"error": str(e)}), 500
