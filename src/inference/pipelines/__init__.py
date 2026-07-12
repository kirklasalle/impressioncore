"""Inference Pipelines Namespace (Shim)

Phase 1: Provide stable import surface for existing references such as
`from ...inference.pipelines.multimodal_pipeline import MultimodalPipeline`.
Actual pipeline implementation already resides in `core.ai.inference.pipelines`.
This shim reduces churn until full Phase 2 consolidation.
"""
from __future__ import annotations

try:  # Re-export primary symbols if available
    from src.core.ai.inference.pipelines.multimodal_pipeline import (
        MultimodalPipeline,  # type: ignore
        create_pipeline,  # type: ignore
    )
    __all__ = ["MultimodalPipeline", "create_pipeline"]
except Exception:  # pragma: no cover - absence acceptable pre-consolidation
    __all__ = []
