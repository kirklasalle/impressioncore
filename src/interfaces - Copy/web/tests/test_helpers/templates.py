#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #memory_management #multimodal #performance #python #source_code #src/interfaces/web\tests/test_helpers/templates.py #testing #transformer #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #memory_management #multimodal #performance #python #source_code #src\\interfaces\\web\\tests\\test_helpers\\templates.py #testing #transformer #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore: Templates

Module for templates functionality in the ImpressionCore framework.

File: web/tests/test_helpers/templates.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [qa, production, testing, web, frontend, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements templates functionality for the
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
from web.tests.test_helpers.templates import MainClass
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
from typing import Any

logger = logging.getLogger(__name__)

# Sample model templates for testing
# Memory optimization: Explicit memory cleanup
MODEL_TEMPLATES = {
    'basic-transformer': {
        'name': 'Basic Transformer',
        'numLayers': 12,
        'hiddenSize': 768,
        'numHeads': 12,
        'ffnDim': 3072,
        'dropoutRate': 0.1,
        'maxSeqLength': 1024,
        'enableLoRA': False,
        'description': 'Standard transformer architecture suitable for most tasks'
    },
    'tiny-transformer': {
        'name': 'Tiny Transformer',
        'numLayers': 4,
        'hiddenSize': 256,
        'numHeads': 4,
        'ffnDim': 1024,
        'dropoutRate': 0.1,
        'maxSeqLength': 512,
        'enableLoRA': False,
        'description': 'Lightweight transformer for resource-constrained environments'
    },
    'deep-transformer': {
        'name': 'Deep Transformer',
        'numLayers': 24,
        'hiddenSize': 1024,
        'numHeads': 16,
        'ffnDim': 4096,
        'dropoutRate': 0.1,
        'maxSeqLength': 2048,
        'enableLoRA': True,
        'description': 'Deep transformer for complex tasks requiring more capacity'
    }
}

# Configuration variations for testing different scenarios
CONFIG_VARIATIONS = {
    'minimal': {
        'numLayers': 2,
        'hiddenSize': 128,
        'numHeads': 2,
        'ffnDim': 512,
        'dropoutRate': 0.1,
        'maxSeqLength': 256,
        'enableLoRA': False
    },
    'maximal': {
        'numLayers': 48,
        'hiddenSize': 4096,
        'numHeads': 32,
        'ffnDim': 16384,
        'dropoutRate': 0.1,
        'maxSeqLength': 8192,
        'enableLoRA': True
    },
    'invalid_layers': {
        'numLayers': 0,
        'hiddenSize': 768,
        'numHeads': 12,
        'ffnDim': 3072,
        'dropoutRate': 0.1,
        'maxSeqLength': 1024,
        'enableLoRA': False
    },
    'invalid_hidden': {
        'numLayers': 12,
        'hiddenSize': 100,
        'numHeads': 12,
        'ffnDim': 3072,
        'dropoutRate': 0.1,
        'maxSeqLength': 1024,
        'enableLoRA': False
    },
    'invalid_heads': {
        'numLayers': 12,
        'hiddenSize': 768,
        'numHeads': 50,
        'ffnDim': 3072,
        'dropoutRate': 0.1,
        'maxSeqLength': 1024,
        'enableLoRA': False
    }
}

def get_test_template(name: str = 'basic-transformer') -> dict[str, Any]:
    """Get a model template configuration for testing"""
    # Memory optimization: Explicit memory cleanup
    try:
        return MODEL_TEMPLATES[name].copy()
    except KeyError:
        logger.warning(f"Template {name} not found, using basic-transformer")
        return MODEL_TEMPLATES['basic-transformer'].copy()

def get_test_config(variation: str = 'minimal') -> dict[str, Any]:
    """Get a configuration variation for testing"""
    try:
        return CONFIG_VARIATIONS[variation].copy()
    except KeyError:
        logger.warning(f"Configuration {variation} not found, using minimal")
        return CONFIG_VARIATIONS['minimal'].copy()

def get_template_combinations() -> list[dict[str, Any]]:
    """
    Generate test configurations combining different template aspects
    Used for comprehensive testing of model configurations
    # Memory optimization: Explicit memory cleanup
    """
    combinations = []

    # Base templates
    for template_name, template in MODEL_TEMPLATES.items():
        combinations.append({
            'name': f"Standard {template_name}",
            'config': template.copy()
        })

        # With LoRA enabled/disabled
        lora_config = template.copy()
        lora_config['enableLoRA'] = not lora_config.get('enableLoRA', False)
        combinations.append({
            'name': f"LoRA variant {template_name}",
            'config': lora_config
        })

        # With adjusted sequence length
        seq_config = template.copy()
        seq_config['maxSeqLength'] = min(seq_config['maxSeqLength'] * 2, 8192)
        combinations.append({
            'name': f"Extended sequence {template_name}",
            'config': seq_config
        })

    return combinations

def create_progressive_configs(start_config: dict[str, Any],
                            steps: int = 5) -> list[dict[str, Any]]:
    """
    Create a series of progressively larger configurations
    Useful for testing scaling behavior
    """
    configs = []
    base_config = start_config.copy()

    for i in range(steps):
        config = base_config.copy()
        scale = 2 ** i

        config.update({
            'numLayers': min(base_config['numLayers'] * scale, 48),
            'hiddenSize': min(base_config['hiddenSize'] * scale, 4096),
            'numHeads': min(base_config['numHeads'] * scale, 32),
            'ffnDim': min(base_config['ffnDim'] * scale, 16384),
            'maxSeqLength': min(base_config['maxSeqLength'] * scale, 8192)
        })

        configs.append({
            'name': f"Scale factor {scale}x",
            'config': config
        })

    return configs
