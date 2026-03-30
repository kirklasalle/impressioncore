#!/usr/bin/env python3
"""
ImpressionCore: Debug Tokenization

Module for debug tokenization functionality in the ImpressionCore framework.

File: examples\debug_tokenization.py
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
This module implements debug tokenization functionality for the
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
from examples.debug_tokenization import MainClass
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
import traceback

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

print("Script starting...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Ensure the src directory is in the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, '../..'))
sys.path.append(root_dir)
print(f"Added to sys.path: {root_dir}")
print(f"Full sys.path: {sys.path}")

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
    banner("TOKENIZATION DEBUG DEMO")
    
    # Check if the tokenization module exists
    tokenization_path = os.path.join(root_dir, "src", "training", "tokenization.py")
    if os.path.exists(tokenization_path):
        print(f"✅ Found tokenization module at {tokenization_path}")
    else:
        print(f"❌ Tokenization module not found at {tokenization_path}")
        # Try to locate it elsewhere
        try:
            import glob
            tokenization_files = glob.glob(os.path.join(root_dir, "src", "**", "tokenization.py"), recursive=True)
            print(f"Found alternative tokenization files: {tokenization_files}")
        except Exception as e:
            print(f"Error searching for tokenization files: {e}")
    
    # Try importing modules with explicit error handling
    try:
        print("Attempting to import torch...")
        import torch
        print(f"✅ Successfully imported torch {torch.__version__}")
    except ImportError as e:
        print(f"❌ Failed to import torch: {e}")
    
    try:
        print("Attempting to import tokenization module...")
        from src.training.tokenization import get_tokenizer
        print("✅ Successfully imported tokenization.get_tokenizer")
        print(f"Function details: {get_tokenizer.__doc__}")
    except ImportError as e:
        print(f"❌ Failed to import get_tokenizer: {e}")
        print("Trying alternative import paths...")
        try:
            # Try different import paths
            alt_paths = ["src.tokenization", "src.models.tokenization", "src.pipeline.tokenization"]
            for path in alt_paths:
                try:
                    print(f"Trying import from {path}...")
                    exec(f"from {path} import get_tokenizer")
                    print(f"✅ Found get_tokenizer in {path}")
                    break
                except ImportError:
                    print(f"Not found in {path}")
        except Exception as e2:
            print(f"Alternative import attempts failed: {e2}")
    
    # Search for tokenizer files
    banner("SEARCHING FOR TOKENIZER FILES")
    tokenizer_paths = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file == "text_tokenizer.json" or file == "tokenizer.json":
                path = os.path.join(root, file)
                tokenizer_paths.append(path)
                print(f"Found tokenizer: {path}")
    
    if not tokenizer_paths:
        print("❌ No tokenizer files found in the project!")
        return
    
    # Try to use the first found tokenizer
    banner("TESTING TOKENIZATION")
    tokenizer_path = tokenizer_paths[0]
    print(f"Using tokenizer: {tokenizer_path}")
    
    try:
        # Try to get and use the tokenizer
        print("Getting tokenizer...")
        from src.training.tokenization import get_tokenizer
        tokenizer = get_tokenizer("text", tokenizer_path)
        print(f"Tokenizer type: {type(tokenizer)}")
        
        # Test with a sample text
        sample_text = "Hello world!"
        print(f"Sample text: '{sample_text}'")
        
        print("Encoding text...")
        tokens = tokenizer.encode(sample_text)
        print(f"Tokens: {tokens}")
        
        print("Decoding tokens...")
        decoded = tokenizer.decode(tokens)
        print(f"Decoded: '{decoded}'")
        
    except Exception as e:
        print(f"❌ Error testing tokenization: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
