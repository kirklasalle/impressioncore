"""Evaluation Metrics Package (Phase 1 Skeleton)

Holds metric tracking utilities migrated from root-level `metrics.py`.
During migration, provides backward-compatible import path through `legacy_imports` if needed.
"""

from .best_model_tracker import BestModelTracker  # re-export

__all__ = ["BestModelTracker"]
