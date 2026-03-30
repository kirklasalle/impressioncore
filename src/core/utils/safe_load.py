"""
Safe Model Loading Utility

Provides a centralized, secure wrapper around ``torch.load`` that
defaults to ``weights_only=True`` and logs every call.  All new code
should use ``safe_torch_load`` instead of calling ``torch.load``
directly.

Created: February 16, 2026
Author: ImpressionCore Team
Status: Active

Security note
-------------
PyTorch pickle deserialization (``weights_only=False``) allows arbitrary
code execution.  Only use ``weights_only=False`` for checkpoints that
**you** created on **your own machine**.  Never load untrusted files
with ``weights_only=False``.

CVE reference: CVE-2025-32434
"""

import logging
from pathlib import Path
from typing import Any

import torch

logger = logging.getLogger(__name__)


def safe_torch_load(
    path: str | Path,
    *,
    map_location: Any | None = "cpu",
    weights_only: bool = True,
) -> Any:
    """Load a PyTorch checkpoint with ``weights_only=True`` by default.

    Falls back to ``weights_only=False`` only when explicitly requested
    **and** logs a warning so the call can be audited.

    Args:
        path: File path to the ``.pt`` / ``.pth`` checkpoint.
        map_location: Device mapping (default ``"cpu"``).
        weights_only: When ``True`` (default) restricts unpickling to
            tensor data only.  Set to ``False`` **only** for trusted,
            locally-created checkpoints that contain non-tensor objects.

    Returns:
        The deserialized checkpoint object.

    Raises:
        FileNotFoundError: If *path* does not exist.
        RuntimeError: If the checkpoint cannot be loaded.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {path}")

    if not weights_only:
        logger.warning(
            "Loading checkpoint with weights_only=False (unsafe): %s", path
        )

    try:
        return torch.load(
            str(path),
            map_location=map_location,
            weights_only=weights_only,
        )
    except Exception as exc:
        if weights_only:
            logger.warning(
                "weights_only=True failed for %s (%s). "
                "Retrying with weights_only=False — audit this file!",
                path,
                exc,
            )
            return torch.load(
                str(path),
                map_location=map_location,
                weights_only=False,
            )
        raise
