"""Training pipeline protocols and shared checkpoint data structures."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class CheckpointData:
    """Canonical checkpoint payload used by all training pipelines.

    Every ``save_checkpoint`` / ``load_checkpoint`` round-trip should
    serialise at least these fields so that pipelines are interoperable.
    """

    global_step: int
    model_state_dict: OrderedDict
    config: dict[str, Any]
    loss_history: list[float] = field(default_factory=list)
    optimizer_state_dict: OrderedDict | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_save_dict(self) -> dict[str, Any]:
        """Flatten into the dict format expected by ``torch.save``."""
        d: dict[str, Any] = {
            "global_step": self.global_step,
            "model_state_dict": self.model_state_dict,
            "config": self.config,
            "loss_history": self.loss_history,
        }
        if self.optimizer_state_dict is not None:
            d["optimizer_state_dict"] = self.optimizer_state_dict
        d.update(self.extra)
        return d

    @classmethod
    def from_save_dict(cls, d: dict[str, Any]) -> CheckpointData:
        """Reconstruct from a dict produced by ``torch.save`` / ``safe_torch_load``."""
        known = {
            "global_step", "model_state_dict", "config",
            "loss_history", "optimizer_state_dict",
        }
        extra = {k: v for k, v in d.items() if k not in known}
        return cls(
            global_step=d.get("global_step", 0),
            model_state_dict=d.get("model_state_dict", OrderedDict()),
            config=d.get("config", {}),
            loss_history=d.get("loss_history", []),
            optimizer_state_dict=d.get("optimizer_state_dict"),
            extra=extra,
        )


@runtime_checkable
class TrainingPipelineProtocol(Protocol):
    """Contract for training pipeline classes.

    Satisfied by DiverseB3Trainer, GrammarTrainer, RAGCurriculumTrainer,
    and any future pipeline that exposes these methods.
    """

    config: Any  # Pipeline-specific dataclass

    def train(self) -> None:
        """Execute the main training loop (blocking)."""
        ...

    def save_checkpoint(self, path: str, final: bool = False) -> None:
        """Persist a checkpoint to *path*."""
        ...

    def load_checkpoint(self, path: str) -> None:
        """Restore model + optimizer state from *path*."""
        ...

    @property
    def global_step(self) -> int:
        """Current training step counter."""
        ...

    @property
    def loss_history(self) -> list[float]:
        """Per-step (or per-epoch) loss values recorded so far."""
        ...
