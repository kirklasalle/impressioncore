"""
ImpressionCore Multimodal Processing
===================================

Multimodal processing, fusion, and integration components.

File: core/ai/multimodal/__init__.py
Project: ImpressionCore
Created: 2025-01-07

Components:
- aligner.py: Cross-modal alignment utilities
- pipeline.py: Multimodal processing pipelines
- fusion/: Multimodal fusion strategies
- vision/: Vision processing components
- audio/: Audio processing components
"""

from .aligner import *
from .pipeline import *
from .unified_multimodal_processor import *

__all__ = ['aligner', 'pipeline', 'fusion', 'vision', 'audio']
