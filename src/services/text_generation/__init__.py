"""
ImpressionCore Text Generation Service
=====================================

Production-ready text generation with B1 model integration,
CUDA optimization, and memory management for GTX 1050 Ti.

This module provides:
- TextGenerationService: Core service for text generation
- REST API endpoints with FastAPI
- Streaming and batch generation
- Real-time VRAM monitoring
- Enterprise-grade error handling

Quick Start:
    from src.services.text_generation import create_text_generation_service
    
    # Create service
    service = create_text_generation_service()
    await service.initialize()
    
    # Generate text
    result = await service.generate_text("Hello, ImpressionCore!")
    print(result.generated_text)

API Server:
    python -m src.services.text_generation.api

Author: ImpressionCore Team
Date: 2025-01-09
Version: 1.0.0
"""

from .service import (
    TextGenerationService,
    GenerationConfig,
    GenerationResult,
    create_text_generation_service,
    text_generation_service
)

from .api import app as api_app, run_server

__all__ = [
    'TextGenerationService',
    'GenerationConfig', 
    'GenerationResult',
    'create_text_generation_service',
    'text_generation_service',
    'api_app',
    'run_server'
]

__version__ = "1.0.0"
