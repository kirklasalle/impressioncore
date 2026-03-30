"""Phase 1 dialog warm-start launcher.

This launcher consumes the Phase 1 manifest and a compact model config to run
short smoke passes before the full curriculum is engaged.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, RandomSampler
from transformers import AutoTokenizer

# Ensure repository root is available on the import path when launched as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
from src.training.datasets.dialog_phase_dataset import DialogPhaseDataset

try:
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    Console = None  # type: ignore
    RICH_AVAILABLE = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
ARCH_KEYS = {
    "embed_dim",
    "num_heads",
    "num_layers",
    "num_experts",
    "expert_dim",
    "experts_per_token",
    "dropout",
    "image_embed_dim",
    "audio_embed_dim",
    "phoneme_vocab_size",
    "max_seq_length",
}
TRAINING_DEFAULTS = {
    "batch_size": 8,
    "learning_rate": 3e-4,
    "weight_decay": 0.01,
    "gradient_accumulation_steps": 1,
    "max_grad_norm": 1.0,
}


@dataclass
class TrainingContext:
    """Runtime training configuration."""

    batch_size: int
    learning_rate: float
    weight_decay: float
    gradient_accumulation_steps: int
    max_grad_norm: float
    max_steps: int
    device: torch.device


class SmoothedValue:
    """Track a rolling average for scalar metrics."""

    def __init__(self, window_size: int) -> None:
        self.window_size = max(1, window_size)
        self._values: deque[float] = deque(maxlen=self.window_size)

    def update(self, value: float) -> None:
        self._values.append(float(value))

    @property
    def value(self) -> float:
        if not self._values:
            return 0.0
        return sum(self._values) / len(self._values)


class RichStatusTracker:
    """Lightweight status reporter using rich when available."""

    def __init__(self, title: str) -> None:
        self.title = title
        self.console = Console() if RICH_AVAILABLE else None

    def update(self, **metrics: str) -> None:
        message = " | ".join(f"{key}: {value}" for key, value in metrics.items())
        if self.console:
            self.console.log(f"[{self.title}] {message}")
        else:
            logger.info("%s | %s", self.title, message)

    def complete(self, message: str) -> None:
        if self.console:
            self.console.log(f"[{self.title}] {message}")
        else:
            logger.info("%s | %s", self.title, message)


# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ImpressionCore dialog warm-start launcher")
    parser.add_argument(
        "--model-config",
        default="src/training/configs/models/impressioncore_c_1m.json",
        help="Path to the compact model configuration JSON.",
    )
    parser.add_argument(
        "--dataset-manifest",
        required=True,
        help="Dataset manifest JSON describing the dialog curriculum.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=200,
        help="Number of optimisation steps to execute (smoke default).",
    )
    parser.add_argument(
        "--tokenizer",
        default="microsoft/DialoGPT-small",
        help="Tokenizer identifier or local path.",
    )
    parser.add_argument(
        "--use-cuda",
        action="store_true",
        help="Explicitly request CUDA if available.",
    )
    parser.add_argument(
        "--log-interval",
        type=int,
        default=10,
        help="Progress logging interval (steps).",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------

def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# ---------------------------------------------------------------------------

def load_config(config_path: Path) -> tuple[B3Config, dict[str, float]]:
    with config_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    arch_kwargs = {key: payload[key] for key in ARCH_KEYS if key in payload}
    b3_config = B3Config(**arch_kwargs)

    training_params = {**TRAINING_DEFAULTS}
    for key in TRAINING_DEFAULTS:
        if key in payload:
            training_params[key] = payload[key]

    return b3_config, training_params


# ---------------------------------------------------------------------------

def prepare_training_context(training_params: dict[str, float], max_steps: int, use_cuda: bool) -> TrainingContext:
    device = torch.device("cuda" if use_cuda and torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.set_device(0)
        logger.info("Using CUDA device: %s", torch.cuda.get_device_name(0))
    else:
        logger.info("Running on CPU")

    return TrainingContext(
        batch_size=int(training_params["batch_size"]),
        learning_rate=float(training_params["learning_rate"]),
        weight_decay=float(training_params["weight_decay"]),
        gradient_accumulation_steps=int(training_params["gradient_accumulation_steps"]),
        max_grad_norm=float(training_params["max_grad_norm"]),
        max_steps=max_steps,
        device=device,
    )


# ---------------------------------------------------------------------------

def build_dataloader(
    manifest_path: Path,
    tokenizer_name: str,
    model_config: B3Config,
    training_ctx: TrainingContext,
) -> DataLoader:
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    if tokenizer.pad_token is None:
        fallback_token = tokenizer.eos_token or tokenizer.unk_token
        if fallback_token is None:
            raise ValueError("Tokenizer must define an eos_token or unk_token to enable padding.")
        tokenizer.pad_token = fallback_token
    tokenizer.padding_side = "right"

    dataset = DialogPhaseDataset(
        manifest_path=manifest_path,
        tokenizer=tokenizer,
        max_seq_length=model_config.max_seq_length,
    )

    sampler = RandomSampler(dataset)

    dataloader = DataLoader(
        dataset,
        batch_size=training_ctx.batch_size,
        sampler=sampler,
        collate_fn=dataset.collate_fn,
        drop_last=False,
    )

    logger.info("Constructed dataloader with %s samples", len(dataset))
    return dataloader


# ---------------------------------------------------------------------------

def run_training(
    model: ImpressionCoreB3Model,
    dataloader: DataLoader,
    training_ctx: TrainingContext,
    log_interval: int,
) -> None:
    optimiser = AdamW(
        model.parameters(),
        lr=training_ctx.learning_rate,
        weight_decay=training_ctx.weight_decay,
    )
    scaler = torch.amp.GradScaler(
        "cuda",
        enabled=training_ctx.device.type == "cuda",
    )

    loss_meter = SmoothedValue(window_size=log_interval)
    grad_meter = SmoothedValue(window_size=log_interval)
    status_tracker = RichStatusTracker("Dialog Warm Start")

    model.train()
    model.to(training_ctx.device)

    optimiser.zero_grad(set_to_none=True)

    global_step = 0
    optimiser_step = 0
    dataloader_iter = iter(dataloader)

    while optimiser_step < training_ctx.max_steps:
        try:
            batch = next(dataloader_iter)
        except StopIteration:
            dataloader_iter = iter(dataloader)
            batch = next(dataloader_iter)

        input_ids = batch["input_ids"].to(training_ctx.device)
        attention_mask = batch["attention_mask"].to(training_ctx.device)
        labels = batch["labels"].to(training_ctx.device)

        with torch.amp.autocast(
            "cuda",
            enabled=training_ctx.device.type == "cuda",
        ):
            outputs = model(input_ids=input_ids, mask=attention_mask, labels=labels)
            loss = outputs["loss"]

        if loss is None:
            continue

        scaled_loss = loss / training_ctx.gradient_accumulation_steps
        scaler.scale(scaled_loss).backward()

        global_step += 1
        loss_meter.update(loss.detach().item())

        if global_step % training_ctx.gradient_accumulation_steps == 0:
            if training_ctx.max_grad_norm > 0:
                scaler.unscale_(optimiser)
                grad_norm = nn.utils.clip_grad_norm_(model.parameters(), training_ctx.max_grad_norm)
                grad_meter.update(float(grad_norm))
            else:
                grad_meter.update(0.0)

            scaler.step(optimiser)
            scaler.update()
            optimiser.zero_grad(set_to_none=True)
            optimiser_step += 1

            if optimiser_step % log_interval == 0:
                status_tracker.update(
                    step=optimiser_step,
                    loss=f"{loss_meter.value:.4f}",
                    grad=f"{grad_meter.value:.3f}",
                )

    status_tracker.complete(
        message=f"Warm start finished after {optimiser_step} steps. Final loss {loss_meter.value:.4f}"
    )


# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    configure_logging()

    model_config, training_params = load_config(Path(args.model_config))
    ctx = prepare_training_context(training_params, args.max_steps, args.use_cuda)
    dataloader = build_dataloader(Path(args.dataset_manifest), args.tokenizer, model_config, ctx)

    model = ImpressionCoreB3Model(model_config)
    run_training(model, dataloader, ctx, args.log_interval)


if __name__ == "__main__":
    main()
