"""Model backend protocols for forward pass and configuration contracts."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import torch


@runtime_checkable
class ModelConfigProtocol(Protocol):
    """Serializable model configuration.

    All B3 config dataclasses (B3Config, B3FoundationConfig, …) satisfy this.
    """

    def to_dict(self) -> dict[str, Any]:
        """Serialize the config to a plain dict."""
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelConfigProtocol:
        """Reconstruct a config from a plain dict."""
        ...


@runtime_checkable
class ModelBackendProtocol(Protocol):
    """Contract for neural network model backends (nn.Module subclasses).

    Both B3Foundation and ImpressionCoreB3Model satisfy this protocol.
    The ``forward`` signature allows keyword-only modality tensors so that
    callers can pass any subset.
    """

    config: Any  # ModelConfigProtocol or compatible dataclass

    def forward(
        self,
        input_ids: torch.Tensor | None = None,
        attention_mask: torch.Tensor | None = None,
        labels: torch.Tensor | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run a forward pass.

        Returns a dict with at least ``"logits"`` (Tensor) and optionally
        ``"loss"`` (Tensor | None), ``"hidden_states"`` (Tensor), and
        any auxiliary outputs.
        """
        ...

    def get_memory_usage(self) -> float:
        """Total parameter memory in GB."""
        ...

    def gradient_checkpointing_enable(self) -> None:
        """Activate gradient checkpointing to reduce VRAM at training time."""
        ...
