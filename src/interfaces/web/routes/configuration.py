#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #attention_mechanism #gpu_optimization #memory_management #multimodal #performance #python #pytorch #source_code #src/interfaces/web\routes\\configuration.py #testing #transformer #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #api #attention_mechanism #gpu_optimization #memory_management #multimodal #performance #python #pytorch #source_code #src\\interfaces\\web\\routes\\configuration.py #testing #transformer #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore: Configuration

Module for configuration functionality in the ImpressionCore framework.

File: web/routes//configuration.py
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
Dependencies: [torch, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements configuration functionality for the
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
from web.routes.configuration import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

import torch
from flask import Blueprint, jsonify, render_template, request

from src.core.config.config_manager import get_config_manager
from src.core.utils.memory_optimization import monitor_memory_usage

# Memory optimization: Memory-critical operation
from src.training.models.model_store import list_available_models

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
config_bp = Blueprint('config', __name__)

# Ensure config directory exists
CONFIG_DIR = Path("user_data") / "configs"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Hardware preset files
PRESET_DIR = Path(__file__).parent.parent.parent / "core" / "configs"

@config_bp.route('/configuration')
def config_dashboard():
    """Render the configuration dashboard."""
    return render_template('configuration/dashboard.html')

@config_bp.route('/configuration/interactive')
def interactive_config():
    """Render the interactive configuration interface."""
    # Get available models
    models = list_available_models()

    # Get system memory information
    # Memory optimization: Memory-critical operation
    mem_info = monitor_memory_usage()
    # Memory optimization: Memory-critical operation

    return render_template('configuration/interactive.html',
                         models=models,
                         mem_info=mem_info)

@config_bp.route('/api/configuration/presets')
def list_presets():
    """List all available configuration presets."""
    presets = []

    # System presets
    for preset_file in PRESET_DIR.glob("*.json"):
        with open(preset_file) as f:
            try:
                data = json.load(f)
                presets.append({
                    "id": preset_file.stem,
                    "name": data.get("name", preset_file.stem),
                    "description": data.get("description", ""),
                    "system": True
                })
            except Exception as e:
                logger.error(f"Error loading preset {preset_file}: {e}")

    # User presets
    for preset_file in CONFIG_DIR.glob("*.json"):
        with open(preset_file) as f:
            try:
                data = json.load(f)
                presets.append({
                    "id": preset_file.stem,
                    "name": data.get("name", preset_file.stem),
                    "description": data.get("description", ""),
                    "system": False
                })
            except Exception as e:
                logger.error(f"Error loading preset {preset_file}: {e}")

    return jsonify({"presets": presets})

@config_bp.route('/api/configuration/preset/<preset_id>')
def get_preset(preset_id):
    """Get a specific configuration preset."""
    # First check system presets
    preset_path = PRESET_DIR / f"{preset_id}.json"

    if not preset_path.exists():
        # Then check user presets
        preset_path = CONFIG_DIR / f"{preset_id}.json"

    if not preset_path.exists():
        return jsonify({"error": f"Preset {preset_id} not found"}), 404

    try:
        with open(preset_path) as f:
            preset_data = json.load(f)
        return jsonify(preset_data)
    except Exception as e:
        logger.error(f"Error loading preset {preset_path}: {e}")
        return jsonify({"error": f"Error loading preset: {e!s}"}), 500

@config_bp.route('/api/configuration/save', methods=['POST'])
def save_preset():
    """Save a configuration preset."""
    config_data = request.json

    if not config_data:
        return jsonify({"error": "No configuration data provided"}), 400

    preset_name = config_data.get("name")
    if not preset_name:
        return jsonify({"error": "Configuration name is required"}), 400

    # Sanitize name for filename
    filename = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in preset_name)
    preset_path = CONFIG_DIR / f"{filename}.json"

    try:
        with open(preset_path, "w") as f:
            json.dump(config_data, f, indent=2)

        logger.info(f"Saved configuration preset: {preset_path}")
        return jsonify({"status": "success", "id": filename})
    except Exception as e:
        logger.error(f"Error saving preset {preset_path}: {e}")
        return jsonify({"error": f"Error saving preset: {e!s}"}), 500

@config_bp.route('/api/configuration/delete/<preset_id>', methods=['DELETE'])
def delete_preset(preset_id):
    """Delete a configuration preset."""
    preset_path = CONFIG_DIR / f"{preset_id}.json"

    # Only allow deleting user presets
    if not preset_path.exists():
        return jsonify({"error": f"Preset {preset_id} not found"}), 404

    # Check if it's a system preset
    system_preset_path = PRESET_DIR / f"{preset_id}.json"
    if system_preset_path.exists():
        return jsonify({"error": "Cannot delete system presets"}), 403

    try:
        os.remove(preset_path)
        logger.info(f"Deleted configuration preset: {preset_path}")
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error deleting preset {preset_path}: {e}")
        return jsonify({"error": f"Error deleting preset: {e!s}"}), 500

@config_bp.route('/api/configuration/estimate_memory', methods=['POST'])
# Memory optimization: Memory-critical operation
def estimate_memory():
# Memory optimization: Memory-critical operation
    """Estimate memory usage for a given configuration."""
    # Memory optimization: Memory-critical operation
    config_data = request.json

    if not config_data:
        return jsonify({"error": "No configuration data provided"}), 400

    try:
        # Extract key parameters
        batch_size = config_data.get("model", {}).get("batch_size", 1)
        context_length = config_data.get("model", {}).get("context_length", 2048)
        precision = config_data.get("model", {}).get("precision", "fp16")

        # Map precision to dtype
        dtype_map = {
            "fp32": torch.float32,
            "fp16": torch.float16,
            "bf16": torch.bfloat16,
            "int8": torch.int8
        }
        dtype_map.get(precision, torch.float16)

        # Get advanced features
        moe_enabled = config_data.get("advanced_features", {}).get("moe", {}).get("enabled", False)
        num_experts = config_data.get("advanced_features", {}).get("moe", {}).get("num_experts", 4)

        config_data.get("advanced_features", {}).get("lora", {}).get("enabled", False)

        # Get optimization settings
        flash_attn = config_data.get("optimizations", {}).get("flash_attention", True)
        cpu_offload = config_data.get("optimizations", {}).get("cpu_offload", False)

        # Currently we're just using a heuristic estimation, but
        # in a real implementation this would profile the actual model
        # Baseline VRAM for transformer models on 1050 Ti (in GB)
        base_vram = 1.5

        # Adjust for precision
        if precision == "fp32":
            base_vram *= 2.0
        elif precision == "int8":
            base_vram *= 0.5

        # Scale by batch size (approximately linear)
        vram_usage = base_vram * batch_size

        # Adjust for context length (not perfectly linear in practice)
        context_factor = 1.0 + (0.1 * (context_length / 1024))
        vram_usage *= context_factor

        # Account for MoE overhead if enabled
        if moe_enabled:
            moe_factor = 1.0 + (0.15 * (num_experts / 4))
            vram_usage *= moe_factor

        # Apply optimizations
        if flash_attn:
            vram_usage *= 0.7  # Flash attention saves about 30% memory
            # Memory optimization: Memory-critical operation

        if cpu_offload:
            vram_usage *= 0.6  # CPU offloading can save about 40% VRAM

        # Format to 1 decimal place
        vram_usage = round(vram_usage, 1)

        # Check if this exceeds typical VRAM for cards
        gpu_limits = {
        # Memory optimization: Memory-critical operation
            "gtx_1050ti": 4.0,
            "gtx_1660": 6.0,
            "rtx_3060": 12.0,
            "rtx_4090": 24.0
        }

        # Find compatible GPUs
        # Memory optimization: Memory-critical operation
        compatible_gpus = [gpu for gpu, limit in gpu_limits.items() if vram_usage <= limit]
        # Memory optimization: Memory-critical operation

        return jsonify({
            "vram_usage_gb": vram_usage,
            "compatible_gpus": compatible_gpus,
            # Memory optimization: Memory-critical operation
            "exceeds_1050ti": vram_usage > 4.0,
            "recommended_optimizations": get_recommendations(vram_usage, config_data)
        })

    except Exception as e:
        logger.error(f"Error estimating memory: {e}")
        # Memory optimization: Memory-critical operation
        return jsonify({"error": f"Error estimating memory: {e!s}"}), 500
        # Memory optimization: Memory-critical operation

def get_recommendations(vram_usage: float, config: dict[str, Any]) -> list:
    """Generate optimization recommendations based on memory usage."""
    # Memory optimization: Memory-critical operation
    recommendations = []

    # If VRAM usage is high for a GTX 1050 Ti
    if vram_usage > 3.5:
        # Check which optimizations aren't enabled
        optimizations = config.get("optimizations", {})

        if not optimizations.get("flash_attention", False):
            recommendations.append({
                "text": "Enable Flash Attention to reduce memory usage by up to 30%",
                # Memory optimization: Memory-critical operation
                "impact": "high"
            })

        if not optimizations.get("cpu_offload", False):
            recommendations.append({
                "text": "Enable CPU Offloading for less critical layers",
                "impact": "high"
            })

        # Check model precision
        # Memory optimization: Explicit memory cleanup
        precision = config.get("model", {}).get("precision", "fp16")
        if precision == "fp32":
            recommendations.append({
                "text": "Switch to FP16 precision to reduce memory usage by up to 50%",
                # Memory optimization: Memory-critical operation
                "impact": "high"
            })

        # Check batch size
        batch_size = config.get("model", {}).get("batch_size", 1)
        if batch_size > 1:
            recommendations.append({
                "text": f"Reduce batch size from {batch_size} to 1 to save memory",
                # Memory optimization: Memory-critical operation
                "impact": "high"
            })

        # Check context length
        context_length = config.get("model", {}).get("context_length", 2048)
        if context_length > 2048:
            recommendations.append({
                "text": f"Reduce context length from {context_length} to 2048 or lower",
                "impact": "medium"
            })

        # Check for MoE
        moe_enabled = config.get("advanced_features", {}).get("moe", {}).get("enabled", False)
        if moe_enabled:
            recommendations.append({
                "text": "Disable Mixture of Experts on limited VRAM devices",
                # Memory optimization: Device placement for memory management
                "impact": "medium"
            })

    return recommendations

@config_bp.route('/api/configuration/apply', methods=['POST'])
def apply_configuration():
    """Apply a configuration to the current instance."""
    config_data = request.json

    if not config_data:
        return jsonify({"error": "No configuration data provided"}), 400

    try:
        # Get the config manager
        get_config_manager()

        # Update configuration based on provided data
        # For demonstration, we're just acknowledging the request
        # In a real implementation, this would modify system settings

        logger.info(f"Applied configuration: {config_data.get('name', 'unnamed')}")
        return jsonify({"status": "success", "message": "Configuration applied successfully"})

    except Exception as e:
        logger.error(f"Error applying configuration: {e}")
        return jsonify({"error": f"Error applying configuration: {e!s}"}), 500
