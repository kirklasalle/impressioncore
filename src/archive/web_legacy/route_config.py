#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #inference #memory_management #multimodal #performance #python #source_code #src/interfaces/web\route_config.py #testing #tokenization #training #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #inference #memory_management #multimodal #performance #python #source_code #src\\interfaces\\web\\route_config.py #testing #tokenization #training #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore: Route Config

Module for route config functionality in the ImpressionCore framework.

File: web/route_config.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [frontend, production, web, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements route config functionality for the
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
from web.route_config import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# Route mapping with both hyphen and underscore variants
ROUTE_MAP = {
    # Home/intro routes
    "home": "/",
    "intro": "/intro",

    # Setup routes
    "setup": ["/setup"],

    # Model definition
    # Memory optimization: Explicit memory cleanup
    "define_model": ["/define-model", "/define_model"],

    # Data preparation
    "data_prep": ["/data-prep", "/data_prep"],

    # Pretraining
    "pretrain": ["/pretrain"],

    # Training
    "training": ["/training", "/train-model", "/train_model"],

    # Tokenizer
    "tokenizer": ["/tokenizer"],

    # Embedding
    "embedding": ["/embedding", "/extract-embedding", "/extract_embedding"],

    # Evaluation
    "evaluation": ["/evaluation", "/evaluate-model", "/evaluate_model"],

    # Inference
    "inference": ["/inference"],

    # Checkpoint management
    "checkpoint": ["/checkpoint", "/manage-checkpoint", "/manage_checkpoint"],
}

# Group routes by section for the navigation bar
NAV_SECTIONS = [
    {"id": "intro", "title": "Introduction", "icon": "info-circle"},
    {"id": "setup", "title": "Environment Setup", "icon": "gear"},
    {"id": "define_model", "title": "Define Model", "icon": "diagram-3"},
    {"id": "data_prep", "title": "Data Preparation", "icon": "database"},
    {"id": "tokenizer", "title": "Tokenizer", "icon": "hash"},
    {"id": "pretrain", "title": "Pretraining", "icon": "reception-4"},
    {"id": "training", "title": "Training", "icon": "cpu"},
    {"id": "embedding", "title": "Embedding", "icon": "box"},
    {"id": "evaluation", "title": "Evaluation", "icon": "graph-up"},
    {"id": "inference", "title": "Inference", "icon": "lightning"},
    {"id": "checkpoint", "title": "Checkpoint Management", "icon": "save"},
]

def get_all_route_paths():
    """Return all route paths as a flat list."""
    all_routes = []
    for routes in ROUTE_MAP.values():
        if isinstance(routes, list):
            all_routes.extend(routes)
        else:
            all_routes.append(routes)
    return all_routes

def get_canonical_route(section_id):
    """Get the canonical (primary) route for a given section ID."""
    routes = ROUTE_MAP.get(section_id)
    if isinstance(routes, list):
        return routes[0]  # First route is the canonical one
    return routes
