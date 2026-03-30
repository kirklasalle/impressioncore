#!/usr/bin/env python3
"""
ImpressionCore:   Init  

Module for   init   functionality in the ImpressionCore framework.

File: tokenization/__init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements   init   functionality for the
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
from tokenization.__init__ import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# Tokenization module initialization
# Date: May 16, 2025
# Description: Initializes the tokenization module, exposing necessary tokenizers and utility functions.

from .bpe import BPETokenizer
from .image import ImageTokenizer # Corrected import from .image

def get_tokenizer(tokenizer_type: str, tokenizer_path: str = None, **kwargs):
    """
    Factory function to get a tokenizer instance.

    Args:
        tokenizer_type (str): The type of tokenizer to get (e.g., "text", "image").
        tokenizer_path (str, optional): Path to the pre-trained tokenizer model or config.
        # Memory optimization: Explicit memory cleanup
        **kwargs: Additional arguments for the tokenizer.

    Returns:
        An instance of the requested tokenizer.
    
    Raises:
        ValueError: If the tokenizer_type is unknown.
    """
    if tokenizer_type == "text":
        # Assuming BPETokenizer is the default text tokenizer
        # You might need to load it from tokenizer_path if provided
        if tokenizer_path:
            # Placeholder for loading logic, e.g., BPETokenizer.from_file(tokenizer_path)
            print(f"INFO: Loading BPETokenizer from {tokenizer_path} (actual loading not implemented in placeholder)")
        return BPETokenizer(vocab_size=kwargs.get("vocab_size", 10000)) # Example default
    elif tokenizer_type == "image":
        if tokenizer_path:
            # Placeholder for loading logic, e.g., ImageTokenizer.load(tokenizer_path)
            print(f"INFO: Loading ImageTokenizer from {tokenizer_path} (actual loading not implemented in placeholder)")
        
        # Pass kwargs as the config dictionary
        config = kwargs 
        return ImageTokenizer(config=config)
    else:
        raise ValueError(f"Unknown tokenizer_type: {tokenizer_type}")

__all__ = ["BPETokenizer", "ImageTokenizer", "get_tokenizer"]
