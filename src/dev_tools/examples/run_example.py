#!/usr/bin/env python3
"""
ImpressionCore: Run Example

Module for run example functionality in the ImpressionCore framework.

File: examples\run_example.py
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
Dependencies: [pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements run example functionality for the
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
from examples.run_example import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import subprocess
from pathlib import Path

def run_example(script_name: str, args: list = None):
    """
    Run an example script with proper Python path setup.
    
    Args:
        script_name: Name of the example script
        args: Additional arguments for the script
    """
    if args is None:
        args = []
        
    # Add project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.copy()
    
    # Add to PYTHONPATH
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{project_root}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = project_root
    
    # Build the full command
    example_path = os.path.join(project_root, "examples", script_name)
    cmd = [sys.executable, example_path] + args
    
    print(f"Running: {' '.join(cmd)}")
    
    # Run the script
    subprocess.run(cmd, env=env)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run ImpressionCore examples")
    parser.add_argument("example", help="Name of the example script (e.g., test_tokenizers_example.py)")
    parser.add_argument("args", nargs="*", help="Additional arguments to pass to the example script")
    
    args = parser.parse_args()
    
    run_example(args.example, args.args)
    
    # Usage examples:
    # python run_example.py test_tokenizers_example.py
    # python run_example.py tokenizer_integration_example.py --text-tokenizer data/tokenizer/text_tokenizer.json
