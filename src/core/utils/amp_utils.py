"""Utility helpers for migrating to the unified torch.amp API.

These helpers provide a safe way to request autocast contexts and gradient
scalers while automatically preferring the newer ``torch.amp`` interfaces.
If the current PyTorch build does not expose the unified API, they gracefully
fall back to the legacy ``torch.cuda.amp`` modules.
"""

from __future__ import annotations

from contextlib import nullcontext
from typing import Any

import torch


def create_grad_scaler(
    *,
    enabled: bool = True,
    device_type: str = "cuda",
    **kwargs: Any,
) -> torch.amp.GradScaler | None:
    """Return a device-aware GradScaler or ``None`` when disabled.

    Args:
        enabled: Whether mixed precision is active.
        device_type: Target device type (``"cuda"`` by default).
        **kwargs: Additional keyword arguments forwarded to the scaler.

    Returns:
        A configured GradScaler instance or ``None`` when AMP should be
        disabled.
    """
    if not enabled:
        return None

    if device_type == "cuda" and not torch.cuda.is_available():
        return None

    amp_namespace = getattr(torch, "amp", None)
    if amp_namespace is not None and hasattr(amp_namespace, "GradScaler"):
        return amp_namespace.GradScaler(device_type, **kwargs)

    legacy_amp = getattr(torch.cuda, "amp", None)
    if legacy_amp is not None and hasattr(legacy_amp, "GradScaler"):
        return legacy_amp.GradScaler(**kwargs)

    return None


def autocast_context(
    *,
    enabled: bool = True,
    device_type: str = "cuda",
    **kwargs: Any,
):
    """Return an autocast context manager with graceful CUDA fallbacks."""
    if not enabled:
        return nullcontext()

    if device_type == "cuda" and not torch.cuda.is_available():
        return nullcontext()

    amp_namespace = getattr(torch, "amp", None)
    if amp_namespace is not None and hasattr(amp_namespace, "autocast"):
        options = {"device_type": device_type, **kwargs}
        return amp_namespace.autocast(**options)

    legacy_amp = getattr(torch.cuda, "amp", None)
    if legacy_amp is not None and hasattr(legacy_amp, "autocast"):
        return legacy_amp.autocast()

    return nullcontext()


__all__ = ["autocast_context", "create_grad_scaler"]
