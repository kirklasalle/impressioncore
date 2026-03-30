#!/usr/bin/env python3
"""
ImpressionCore: Assistant Knowledge Module

Module initialization for the personal assistant knowledge integration layer,
providing access to UKS (Unified Knowledge Store) and knowledge management.

File: src/assistant/knowledge/__init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-31
Modified: 2025-05-31
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, assistant, knowledge, init, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module provides initialization and exports for the assistant knowledge
layer, enabling easy access to UKS integration, knowledge management, and
learning capabilities.

Architecture Overview:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Assistant     │───▶│   Knowledge     │───▶│  UKS & Storage  │
│   Components    │    │   Integration   │    │   Systems       │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Available Components:
- UKSIntegration: Main knowledge integration class
- KnowledgeItem: Knowledge representation
- KnowledgeQuery: Query specification
- KnowledgeResponse: Query response
- KnowledgeCache: Memory-efficient caching
- Helper functions for common operations

Memory Considerations:
- All components optimized for GTX 1050 Ti (4GB VRAM)
- Maximum memory allocation: 25MB for knowledge layer
- Intelligent caching with LRU eviction
- Lazy loading and resource cleanup
"""

# Core UKS integration components
from .uks_integration import (
    # Main integration class
    UKSIntegration,
    
    # Data structures
    KnowledgeItem,
    KnowledgeQuery,
    KnowledgeResponse,
    KnowledgeCache,
    
    # Enums
    KnowledgeSource,
    KnowledgeType,
    VerificationStatus,
    
    # Convenience functions
    create_uks_integration,
    query_uks,
    
    # Constants
    MAX_CACHE_SIZE_MB,
    MAX_KNOWLEDGE_ITEMS,
    EMBEDDING_DIMENSION,
    CACHE_EXPIRY_HOURS
)

# Version and metadata
__version__ = "1.0.0"
__author__ = "ImpressionCore Development Team"
__license__ = "MIT"
__description__ = "Assistant Knowledge Integration for ImpressionCore"

# Hardware target information
__hardware_target__ = "NVIDIA GTX 1050 Ti (4GB VRAM)"
__memory_limit__ = "25MB maximum allocation"
__optimization_level__ = "High - Memory constrained"

# Module exports
__all__ = [
    # Main class
    "UKSIntegration",
    
    # Data structures
    "KnowledgeItem",
    "KnowledgeQuery", 
    "KnowledgeResponse",
    "KnowledgeCache",
    
    # Enums
    "KnowledgeSource",
    "KnowledgeType",
    "VerificationStatus",
    
    # Convenience functions
    "create_uks_integration",
    "query_uks",
    
    # Constants
    "MAX_CACHE_SIZE_MB",
    "MAX_KNOWLEDGE_ITEMS",
    "EMBEDDING_DIMENSION",
    "CACHE_EXPIRY_HOURS",
    
    # Metadata
    "__version__",
    "__author__",
    "__license__",
    "__description__",
    "__hardware_target__",
    "__memory_limit__",
    "__optimization_level__"
]

# Lazy loading for memory efficiency
def get_uks_integration(**kwargs):
    """
    Lazy factory function for UKS integration.
    
    Args:
        **kwargs: Arguments to pass to UKSIntegration constructor
        
    Returns:
        UKSIntegration instance
    """
    return UKSIntegration(**kwargs)

# Quick access functions
async def quick_query(query_text: str, max_results: int = 5) -> KnowledgeResponse:
    """
    Quick knowledge query with default settings.
    
    Args:
        query_text: Text to search for
        max_results: Maximum results to return
        
    Returns:
        Knowledge response
    """
    uks = await create_uks_integration()
    try:
        return await query_uks(uks, query_text, max_results=max_results)
    finally:
        await uks.cleanup()

def get_memory_usage() -> dict:
    """
    Get current memory usage information for the knowledge module.
    
    Returns:
        Dictionary with memory usage statistics
    """
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "rss_mb": memory_info.rss / (1024 * 1024),
        "vms_mb": memory_info.vms / (1024 * 1024),
        "percent": process.memory_percent(),
        "available_mb": psutil.virtual_memory().available / (1024 * 1024)
    }

# Module initialization logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"ImpressionCore Assistant Knowledge Module v{__version__} initialized")
logger.info(f"Target hardware: {__hardware_target__}")
logger.info(f"Memory limit: {__memory_limit__}")
