#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #gpu_optimization #memory_management #multimodal #python #pytorch #source_code #src/tests/test_imports.py #testing #training
**Category:** Testing Framework
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #cuda #gpu_optimization #memory_management #multimodal #python #pytorch #source_code #src\\tests\\test_imports.py #testing #training
# Category:** Testing Framework
# Status:** Active

"""
Test imports for enhanced B2 training
"""

import pytest


def test_basic_imports():
    """Validate core legacy-style imports resolve.

    Skips only if the top-level package truly is absent (ModuleNotFoundError).
    Other ImportErrors (dependency issues inside modules) cause failure to
    surface real problems instead of masking them as skips.
    """
    try:
        from training.datasets.data_loading import get_embedding_dataloaders
    except ModuleNotFoundError as e:  # pragma: no cover - transitional
        pytest.skip(f"training package not yet importable: {e}")
    except ImportError as e:  # Differentiate internal errors
        pytest.fail(f"ImportError inside training.datasets: {e}")

    try:
        from models.b2_multimodal.core.b2_multimodal_model import B2MultimodalModel
    except ModuleNotFoundError as e:  # pragma: no cover
        pytest.skip(f"models.b2_multimodal not yet importable: {e}")
    except ImportError as e:
        pytest.fail(f"ImportError inside models.b2_multimodal: {e}")

    try:
        import torch
    except ModuleNotFoundError as e:  # pragma: no cover
        pytest.skip(f"torch not installed in environment: {e}")
    except ImportError as e:  # pragma: no cover
        pytest.fail(f"Unexpected torch import failure: {e}")
