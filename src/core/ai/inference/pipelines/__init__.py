#!/usr/bin/env python3
"""
Inference Pipelines Module

This module contains inference pipelines for ImpressionCore models.

File: inference/pipelines/__init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-05
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [inference, pipelines, multimodal, 2025]
"""

from .multimodal_pipeline import MultimodalPipeline, create_pipeline

__all__ = [
    'MultimodalPipeline',
    'create_pipeline',
]

__version__ = '1.0.0'
