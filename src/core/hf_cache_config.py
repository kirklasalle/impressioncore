#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/hf_cache_config.py #transformer
**Category:** Core Implementation
**Status:** Active
"""


"""
HuggingFace Cache Configuration for ImpressionCore B3

This file configures HuggingFace to use the F: drive cache location
after successful relocation from C: drive.

Generated: 2025-08-01T15:14:34.134886
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# HuggingFace cache configuration
HF_CACHE_ROOT = Path(r"F:\data/huggingface_cache")
HF_DATASETS_PATH = HF_CACHE_ROOT / "datasets"
HF_HUB_PATH = HF_CACHE_ROOT / "hub"
HF_MODELS_PATH = HF_CACHE_ROOT / "models"
HF_TRANSFORMERS_PATH = HF_CACHE_ROOT / "transformers"

# Set environment variables
os.environ["HF_HOME"] = str(HF_CACHE_ROOT)
os.environ["HUGGINGFACE_HUB_CACHE"] = str(HF_HUB_PATH)
os.environ["HF_DATASETS_CACHE"] = str(HF_DATASETS_PATH)
os.environ["TRANSFORMERS_CACHE"] = str(HF_TRANSFORMERS_PATH)
os.environ["HF_TOKEN_CACHE"] = str(HF_CACHE_ROOT / "token")

# Verify cache directories exist
for cache_dir in [HF_DATASETS_PATH, HF_HUB_PATH, HF_MODELS_PATH, HF_TRANSFORMERS_PATH]:
    cache_dir.mkdir(parents=True, exist_ok=True)

logger.info("HuggingFace cache configured to use: %s", HF_CACHE_ROOT)
