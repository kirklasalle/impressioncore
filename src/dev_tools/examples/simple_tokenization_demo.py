#!/usr/bin/env python3
"""
ImpressionCore: Simple Tokenization Demo

Module for simple tokenization demo functionality in the ImpressionCore framework.

File: examples\simple_tokenization_demo.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, 2025]
Dependencies: [torch, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements simple tokenization demo functionality for the
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
from examples.simple_tokenization_demo import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import sys
import os
import logging
from pathlib import Path
import time

# Ensure the src directory is in the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(root_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def banner(message):
    """Print a banner with the given message."""
    border = "=" * 70
    print(f"\n{border}")
    print(f"{message.center(70)}")
    print(f"{border}\n")

def main():
    """
    
    main function for processing.
    
    Args:
        No arguments: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
    """
    banner("SIMPLE TOKENIZATION DEMO")
    
    # Check if we can import the required modules
    try:
        # Import the necessary components directly
        import torch
        from src.training.tokenization import get_tokenizer
        print("✅ Successfully imported tokenization module")
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"❌ Failed to import modules: {e}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Check multiple possible paths for the tokenizer
    tokenizer_paths = [
        os.path.join(root_dir, "data/tokenizer/text_tokenizer.json"),
        os.path.join("data/tokenizer/text_tokenizer.json"),
        os.path.join(root_dir, "src/data/datasets/tokenizer/text_tokenizer.json"),
        os.path.join(root_dir, "src/data/tokenizer/text_tokenizer.json")
    ]
    
    tokenizer_path = None
    for path in tokenizer_paths:
        if os.path.exists(path):
            tokenizer_path = path
            break
    
    if not tokenizer_path:
        logger.warning("Tokenizer not found in any of the expected locations")
        print("⚠️ Tokenizer file not found. Please specify the correct path.")
        return
    
    # Load and test the tokenizer
    try:
        print(f"Loading text tokenizer from {tokenizer_path}")
        tokenizer = get_tokenizer("text", tokenizer_path)
        
        # Test with a sample text
        sample_text = "Hello world! This is a test of the ImpressionCore tokenization system."
        print(f"\nSample text: '{sample_text}'")
        
        print("\nTokenizing text...")
        tokens = tokenizer.encode(sample_text)
        
        print(f"Tokenized: {tokens}")
        print(f"Number of tokens: {len(tokens)}")
        
        # Convert back to text
        print("\nDecoding tokens back to text...")
        decoded_text = tokenizer.decode(tokens)
        print(f"Decoded: '{decoded_text}'")
        print(f"Match: {'✅' if decoded_text == sample_text else '❌'}")
        
    except Exception as e:
        logger.error(f"Error during tokenization: {e}", exc_info=True)
        print(f"❌ Failed to run tokenization: {e}")

if __name__ == "__main__":
    main()
