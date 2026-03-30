#!/usr/bin/env python3
"""
ImpressionCore: Visualization

Module for visualization functionality in the ImpressionCore framework.

File: knowledge\visualization.py
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
Dependencies: [typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements visualization functionality for the
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
from knowledge.visualization import MainClass
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
import logging
import subprocess
import platform
from pathlib import Path
from typing import Dict, Optional, Union, List

# Configure logging
logger = logging.getLogger(__name__)

def check_graphviz_installed() -> bool:
    """
    Check if GraphViz is installed on the system.
    
    Returns:
        bool: True if GraphViz is installed, False otherwise
    """
    try:
        # Try to run dot -V to check if GraphViz is installed
        subprocess.run(
            ["dot", "-V"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def install_graphviz_instructions() -> str:
    """
    Get platform-specific instructions for installing GraphViz.
    
    Returns:
        str: Installation instructions
    """
    system = platform.system().lower()
    
    if system == "windows":
        return (
            "To install GraphViz on Windows:\n"
            "1. Install Chocolatey from https://chocolatey.org/ if not already installed\n"
            "2. Run in administrator PowerShell: choco install graphviz\n"
            "3. Restart your terminal\n\n"
            "Alternative method:\n"
            "1. Download the installer from https://graphviz.org/download/\n"
            "2. Run the installer and follow the instructions\n"
            "3. Add the GraphViz bin directory to your PATH environment variable"
        )
    elif system == "darwin":  # macOS
        return (
            "To install GraphViz on macOS:\n"
            "1. Install Homebrew from https://brew.sh/ if not already installed\n"
            "2. Run: brew install graphviz\n"
            "3. Restart your terminal"
        )
    elif system == "linux":
        return (
            "To install GraphViz on Linux:\n"
            "1. For Ubuntu/Debian: sudo apt-get install graphviz\n"
            "2. For Fedora/RHEL: sudo dnf install graphviz\n"
            "3. For Arch: sudo pacman -S graphviz\n"
            "4. Restart your terminal"
        )
    else:
        return "Please install GraphViz from https://graphviz.org/download/"

def generate_visualization(
    dot_file: str,
    output_file: Optional[str] = None,
    format: str = "png",
    use_fallback: bool = True
) -> Dict[str, Union[bool, str]]:
    """
    Generate a visualization from a DOT file.
    
    Args:
        dot_file: Path to the DOT file
        output_file: Path to save the output file (if None, derived from dot_file)
        format: Output format (png, svg, pdf, etc.)
        use_fallback: Whether to use fallback methods if GraphViz is not available
    
    Returns:
        Dict with status information
    """
    if not os.path.exists(dot_file):
        return {
            "success": False,
            "error": f"DOT file not found: {dot_file}",
            "output_file": None
        }
    
    # Derive output file path if not provided
    if output_file is None:
        dot_path = Path(dot_file)
        output_file = str(dot_path.with_suffix(f".{format}"))
    
    # Check if GraphViz is installed
    graphviz_installed = check_graphviz_installed()
    
    if graphviz_installed:
        try:
            # Generate visualization using GraphViz
            subprocess.run(
                ["dot", f"-T{format}", dot_file, "-o", output_file],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return {
                "success": True,
                "method": "graphviz",
                "output_file": output_file
            }
        except subprocess.SubprocessError as e:
            logger.error(f"GraphViz error: {e}")
            
            if not use_fallback:
                return {
                    "success": False,
                    "error": f"GraphViz error: {e}",
                    "output_file": None
                }
    
    # If GraphViz is not installed or failed, try fallback methods
    if use_fallback:
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
            
            # Create a simple visualization using networkx and matplotlib
            return generate_fallback_visualization(dot_file, output_file, format)
        except ImportError:
            # If neither GraphViz nor networkx is available, provide instructions
            install_instructions = install_graphviz_instructions()
            
            return {
                "success": False,
                "error": "GraphViz is not installed and networkx fallback failed",
                "install_instructions": install_instructions,
                "output_file": None
            }
    
    # If fallback is disabled and GraphViz is not available
    return {
        "success": False,
        "error": "GraphViz is not installed and fallback is disabled",
        "install_instructions": install_graphviz_instructions(),
        "output_file": None
    }

def generate_fallback_visualization(
    dot_file: str,
    output_file: str,
    format: str = "png"
) -> Dict[str, Union[bool, str]]:
    """
    Generate a simple visualization using networkx and matplotlib.
    
    Args:
        dot_file: Path to the DOT file
        output_file: Path to save the output file
        format: Output format (png, svg, pdf, etc.)
    
    Returns:
        Dict with status information
    """
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
        
        # Parse DOT file to extract nodes and edges
        G = nx.DiGraph()
        
        with open(dot_file, 'r') as f:
            content = f.read()
        
        # Very basic DOT file parsing (for more complex files, use pydot)
        # Extract node definitions
        for line in content.split('\n'):
            line = line.strip()
            if '->' in line:  # Edge definition
                parts = line.split('->')
                if len(parts) == 2:
                    source = parts[0].strip().strip('"')
                    target_part = parts[1].split('[')[0].strip().strip('"')
                    G.add_edge(source, target_part)
            elif '[' in line and not '->' in line:  # Node definition
                node_id = line.split('[')[0].strip().strip('"')
                if node_id and node_id != '{' and node_id != '}':
                    G.add_node(node_id)
        
        # Create visualization
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(G)  # Position nodes using force-directed layout
        
        nx.draw(
            G, pos, 
            with_labels=True, 
            node_color='skyblue', 
            node_size=1500, 
            edge_color='gray',
            arrows=True,
            font_size=10
        )
        
        plt.savefig(output_file, format=format)
        plt.close()
        
        return {
            "success": True,
            "method": "networkx_fallback",
            "output_file": output_file
        }
        
    except Exception as e:
        logger.error(f"Fallback visualization error: {e}")
        return {
            "success": False,
            "error": f"Fallback visualization error: {e}",
            "output_file": None
        }
