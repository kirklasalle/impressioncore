#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/modules/phoneme_embedding/__init__.py #tokenization
**Category:** Source Code
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src/modules/phoneme_embedding/__init__.py #tokenization
# Category:** Source Code
# Status:** Active

"""
ImpressionCore: Phoneme Embedding Module

This module provides phoneme processing implementations
by importing from the core phoneme embedding directory.
"""

from ...core.phoneme_embedding.config import PhonemeEmbeddingConfig
from ...core.phoneme_embedding.phoneme_embedder import PhonemeTokenizer
from ...core.phoneme_embedding.phoneme_extractor import PhonemeExtractor
from ...core.phoneme_embedding.phoneme_to_sound import PhonemeToSoundSynthesizer

__all__ = [
    'PhonemeEmbeddingConfig',
    'PhonemeExtractor',
    'PhonemeToSoundSynthesizer',
    'PhonemeTokenizer'
]
