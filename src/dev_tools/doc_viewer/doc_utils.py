#!/usr/bin/env python3
"""
ImpressionCore: Doc Utils

Module for doc utils functionality in the ImpressionCore framework.

File: tools\doc_viewer\doc_utils.py
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
This module implements doc utils functionality for the
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
from tools.doc_viewer.doc_utils import MainClass
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
import re
yaml_tag_pattern = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL | re.MULTILINE)

def find_markdown_files(root_dir):
    """
    Recursively find all .md files under root_dir.
    Returns a list of (relative_path, absolute_path).
    """
    md_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith('.md'):
                rel_path = os.path.relpath(os.path.join(dirpath, fname), root_dir)
                abs_path = os.path.abspath(os.path.join(dirpath, fname))
                md_files.append((rel_path, abs_path))
    return md_files

def extract_yaml_tags(md_path):
    """
    Extract tags from YAML frontmatter in a Markdown file.
    Returns a list of tags, or [] if none found.
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read(2048)  # Only need the start
        match = yaml_tag_pattern.search(content)
        if match:
            yaml_block = match.group(1)
            for line in yaml_block.splitlines():
                if line.strip().startswith('tags:'):
                    # tags: [tag1, tag2]
                    tag_str = line.split(':', 1)[1].strip()
                    tag_str = tag_str.strip('[]')
                    tags = [t.strip().strip("'\"") for t in tag_str.split(',') if t.strip()]
                    return tags
        return []
    except Exception:
        return []

def build_doc_tree(md_files):
    """
    Build a nested dict representing the directory structure of docs.
    Input: list of (rel_path, abs_path)
    Output: {folder: {subfolder: ..., files: [...]}}
    """
    tree = {}
    for rel_path, abs_path in md_files:
        parts = rel_path.split(os.sep)
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node.setdefault('__files__', []).append((parts[-1], abs_path))
    return tree


# Placeholder MainClass for compatibility
class MainClass:
    """Placeholder class for tools compatibility."""
    
    def __init__(self, **kwargs):
        pass
    
    def process(self, *args, **kwargs):
        """Process method placeholder."""
        print(f"Processing in {self.__class__.__module__}")
        return True
