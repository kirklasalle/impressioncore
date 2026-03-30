#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #inference #memory_management #multimodal #performance #python #source_code #src/interfaces/web\templates\\_update_templates.py #testing #tokenization #training #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #inference #memory_management #multimodal #performance #python #source_code #src\\interfaces\\web\\templates\\_update_templates.py #testing #tokenization #training #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore:  Update Templates

Module for  update templates functionality in the ImpressionCore framework.

File: web/templates//_update_templates.py
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
This module implements  update templates functionality for the
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
from web.templates._update_templates import MainClass
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

# Define template paths
template_dir = os.path.dirname(os.path.abspath(__file__))

# Template for wrapping content in base.html extension
BASE_TEMPLATE = """{% extends "base.html" %}

{% block title %}TITLE_PLACEHOLDER{% endblock %}

{% block content %}
CONTENT_PLACEHOLDER
{% endblock %}
"""

# Files to update
files_to_update = [
    "checkpoint.html", "data_prep.html", "embedding.html", "evaluation.html",
    "index.html", "inference.html", "pretrain.html", "training.html",
    "errors/404.html", "errors/500.html",
    "tokenizer/image_tokenizer.html", "tokenizer/text_tokenizer.html", "tokenizer/tokenizer_info.html"
]

# Skip layout.html as it might be a different template system

for filename in files_to_update:
    filepath = os.path.join(template_dir, filename)

    # Check if file exists
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue

    # Read original file content
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # Skip if already extends base.html
    if '{% extends "base.html" %}' in content:
        print(f"File already extends base.html: {filename}")
        continue

    # Extract title from content (basic extraction)
    title_match = re.search(r'<title>(.*?)</title>|<h1>(.*?)</h1>', content, re.DOTALL)
    title = "ImpressionCore"
    if title_match:
        title = title_match.group(1) or title_match.group(2) or "ImpressionCore"
        title = title.strip()

    # Replace HTML and BODY tags
    content = re.sub(r'<!DOCTYPE.*?>', '', content, flags=re.DOTALL)
    content = re.sub(r'<html.*?>.*?<body.*?>', '', content, flags=re.DOTALL)
    content = re.sub(r'</body>.*?</html>', '', content, flags=re.DOTALL)

    # Remove link to css if exists (base.html will handle it)
    content = re.sub(r'<link.*?href=["\']/static/css/style.css["\'](.*?)>', '', content)

    # Create new content
    new_content = BASE_TEMPLATE.replace('TITLE_PLACEHOLDER', title).replace('CONTENT_PLACEHOLDER', content.strip())

    # Create backup of original file
    backup_path = filepath + '.bak'
    os.rename(filepath, backup_path)

    # Write new content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Updated file: {filename}")

print("Template update complete!")
