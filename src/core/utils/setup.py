#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #command_line #documentation #multimodal #python #source_code #src/core/utils/setup.py #testing #transformer #web_interface
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** Kirk LaSalle
# Tags:** #api #command_line #documentation #multimodal #python #source_code #src\\core\\utils\\setup.py #testing #transformer #web_interface
# Category:** Core Implementation
# Status:** Active

"""
ImpressionCore - Brain-Inspired Multimodal AI Framework
Setup configuration for the entire project including CLI and all modules.
"""

import functools
import operator
from pathlib import Path

from setuptools import find_packages, setup

# Read the README file for long description
project_root = Path(__file__).parent
readme_file = project_root / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, encoding="utf-8") as f:
        long_description = f.read()

# Read requirements
requirements_file = project_root / "requirements.txt"
install_requires = []
if requirements_file.exists():
    with open(requirements_file, encoding="utf-8") as f:
        install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Define extra requirements for optional features
extras_require = {
    'dev': [
        'pytest>=6.0',
        'pytest-cov>=2.0',
        'black>=21.0',
        'flake8>=3.8',
        'mypy>=0.900',
        'pre-commit>=2.0',
    ],
    'brainsim': [
        'networkx>=2.5',
        'scikit-learn>=1.0',
        'matplotlib>=3.3',
        'seaborn>=0.11',
    ],
    'diffusion': [
        'diffusers>=0.18.0',
        'accelerate>=0.16.0',
        'transformers>=4.21.0',
    ],
    'web': [
        'flask>=2.0',
        'fastapi>=0.68',
        'uvicorn>=0.15',
        'jinja2>=3.0',
    ],
}

# All extras combined
extras_require['all'] = functools.reduce(operator.iadd, extras_require.values(), [])

setup(
    name="impressioncore",
    version="0.1.0",
    author="Kirk LaSalle",
    author_email="kirk@impressioncore.ai",
    description="ImpressionCore: A brain-inspired multimodal AI framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/impressioncore/impressioncore",

    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # Dependencies
    install_requires=install_requires,
    extras_require=extras_require,

    # Python version requirement
    python_requires=">=3.8",

    # Entry points for CLI
    entry_points={
        "console_scripts": [
            "impressioncore-cli=cli.main:main",
            "ic-cli=cli.main:main",
            "impressioncore=cli.main:main",
        ],
    },

    # Package data
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt", "*.md"],
    },

    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    # Keywords
    keywords="ai artificial-intelligence brain-inspired multimodal machine-learning deep-learning",

    # Project URLs
    project_urls={
        "Documentation": "https://impressioncore.readthedocs.io/",
        "Source": "https://github.com/impressioncore/impressioncore",
        "Tracker": "https://github.com/impressioncore/impressioncore/issues",
    },

    # Zip safe
    zip_safe=False,
)
