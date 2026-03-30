#!/usr/bin/env python3
"""Training harness and synthetic dataset generation for the Colossus integrator."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import random
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from src.integrator.colossus_model import Colossus, ColossusConfig
from src.orchestrator.message_protocol import TriMessage, pack_message

logger = logging.getLogger("colossus.distillation")


@dataclass
class ColossusDistillationConfig:
    """Hyper-parameters controlling Colossus distillation."""

    dataset_size: int = 2048
    vector_dim: int = 256
    batch_size: int = 64
    num_epochs: int = 10
    learning_rate: float = 1e-3
    min_learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    confidence_loss_weight: float = 0.25
    max_grad_norm: float = 1.0
    gradient_accumulation_steps: int = 1
    scheduler: str = "cosine"
    output_dir: Path = Path("F:/models/management/training_sessions/colossus")
    checkpoint_name: str = "colossus_distilled.pt"
    seed: int = 42
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    mix_ratio: float = 0.65
    num_workers: int = 0
    teacher_data: Optional[Sequence[Path]] = None


@dataclass
class DistillationSample:
    """Container for a single synthetic supervision example."""

    role_a: TriMessage
    role_b: TriMessage
    target_vector: Sequence[float]
    target_confidence: float


def _expand_teacher_files(paths: Sequence[Path]) -> List[Path]:
    files: List[Path] = []
    for entry in paths:
        resolved = entry.expanduser()
        if resolved.is_dir():
            files.extend(sorted(resolved.rglob("*.json")))
        elif resolved.suffix.lower() == ".json" and resolved.is_file():
            files.append(resolved)
        else:
            logger.warning("Ignoring teacher data path %s", resolved)
    return files


def _text_to_vector(text: str, vector_dim: int) -> List[float]:
    vector = torch.zeros(vector_dim, dtype=torch.float32)
    content = text.lower().split()
    if not content:
        return vector.tolist()
    for token in content:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % vector_dim
        sign = 1.0 if digest[4] & 1 else -1.0
        vector[idx] += sign
    norm = torch.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector.tolist()


def _confidence_from_text(text: str) -> float:
    if not text:
        return 0.1
    tokens = text.split()
    length_bonus = min(0.4, 0.012 * len(tokens))
    diversity = len(set(tokens)) / max(1, len(tokens))
    diversity_bonus = min(0.25, 0.3 * diversity)
    punctuation_bonus = 0.05 if any(ch in text for ch in ".?!") else 0.0
    confidence = 0.3 + length_bonus + diversity_bonus + punctuation_bonus
    return max(0.05, min(0.99, confidence))


def _create_teacher_message(teacher_name: str, prompt: str, response: str, vector_dim: int) -> TriMessage:
    provenance = f"teacher::{teacher_name}"
    structured = {
        "role": "teacher",
        "teacher": teacher_name,
        "prompt": prompt,
        "response": response,
    }
    vector = _text_to_vector(response, vector_dim)
    confidence = _confidence_from_text(response)
    return pack_message(provenance, "text", structured, vector, confidence)


def _average_vectors(vector_a: Sequence[float], vector_b: Sequence[float]) -> List[float]:
    return [float(a + b) / 2.0 for a, b in zip(vector_a, vector_b)]


def load_teacher_samples(
    paths: Sequence[Path],
    vector_dim: int,
    seed: int,
    max_samples: Optional[int],
) -> List[DistillationSample]:
    files = _expand_teacher_files(paths)
    if not files:
        logger.warning("No teacher data files discovered from %s", [str(p) for p in paths])
        return []

    prompt_map: Dict[str, Dict[str, Any]] = {}
    for file_path in files:
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Skipping teacher dataset %s: %s", file_path, exc)
            continue
        for example in payload.get("examples", []):
            prompt = example.get("prompt")
            responses = example.get("teacher_responses", {})
            if not prompt or not isinstance(responses, dict):
                continue
            store = prompt_map.setdefault(prompt, {"responses": {}, "target_confidence": None})
            target_confidence = example.get("target_confidence")
            if isinstance(target_confidence, (int, float)):
                existing = store.get("target_confidence")
                if existing is None:
                    store["target_confidence"] = float(target_confidence)
                else:
                    store["target_confidence"] = (existing + float(target_confidence)) / 2.0
            for teacher_name, response_text in responses.items():
                if not response_text:
                    continue
                store["responses"][teacher_name] = response_text

    rng = random.Random(seed)
    samples: List[DistillationSample] = []
    for prompt, entry in prompt_map.items():
        teacher_responses = entry.get("responses", {})
        conf_override = entry.get("target_confidence")
        items = [(name, text) for name, text in teacher_responses.items() if text]
        if len(items) < 2:
            continue
        pairs = list(combinations(items, 2))
        rng.shuffle(pairs)
        for (name_a, text_a), (name_b, text_b) in pairs:
            message_a = _create_teacher_message(name_a, prompt, text_a, vector_dim)
            message_b = _create_teacher_message(name_b, prompt, text_b, vector_dim)
            target_vector = _average_vectors(message_a.summary_vector, message_b.summary_vector)
            if isinstance(conf_override, float):
                target_confidence = conf_override
            else:
                target_confidence = (message_a.confidence + message_b.confidence) / 2.0
            samples.append(
                DistillationSample(
                    role_a=message_a,
                    role_b=message_b,
                    target_vector=target_vector,
                    target_confidence=target_confidence,
                )
            )

    if not samples:
        logger.warning("Teacher data parsing yielded zero paired examples")
        return []

    if max_samples and max_samples > 0 and len(samples) > max_samples:
        rng.shuffle(samples)
        samples = samples[:max_samples]

    logger.info(
        "Loaded %d teacher-derived supervision pairs from %d prompts across %d files",
        len(samples),
        len(prompt_map),
        len(files),
    )
    return samples


def _seed_everything(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _pad_vector(values: Iterable[float], vector_dim: int) -> torch.Tensor:
    data = list(values)
    if len(data) >= vector_dim:
        data = data[:vector_dim]
    else:
        data = data + [0.0] * (vector_dim - len(data))
    return torch.tensor(data, dtype=torch.float32)


def generate_synthetic_samples(config: ColossusDistillationConfig) -> List[DistillationSample]:
    """Generate synthetic teacher data that encourages stable integration behaviour."""

    samples: List[DistillationSample] = []
    vocabulary = [
        "analysis", "hypothesis", "insight", "summary", "plan",
        "creative", "narrative", "metaphor", "analogy", "refinement",
    ]
    for index in range(config.dataset_size):
        base_vector = torch.randn(config.vector_dim)
        offset = torch.randn(config.vector_dim) * 0.15
        vector_a = base_vector + offset
        vector_b = base_vector - offset
        confidence_a = random.uniform(0.35, 0.95)
        confidence_b = random.uniform(0.35, 0.95)

        token_a = random.choice(vocabulary)
        token_b = random.choice(vocabulary)
        structured_a = {
            "role": "analytical",
            "text": f"Analytical perspective incorporating {token_a} #{index}",
            "quality": confidence_a,
        }
        structured_b = {
            "role": "creative",
            "text": f"Creative expansion leveraging {token_b} #{index}",
            "quality": confidence_b,
        }
        message_a = pack_message(
            provenance="role_analytical",
            modality="text",
            structured=structured_a,
            vector=vector_a.tolist(),
            confidence=confidence_a,
        )
        message_b = pack_message(
            provenance="role_creative",
            modality="text",
            structured=structured_b,
            vector=vector_b.tolist(),
            confidence=confidence_b,
        )

        target_vector = ((vector_a + vector_b) / 2.0).tolist()
        target_confidence = (confidence_a + confidence_b) / 2.0
        samples.append(
            DistillationSample(
                role_a=message_a,
                role_b=message_b,
                target_vector=target_vector,
                target_confidence=target_confidence,
            )
        )
    return samples


class ColossusDistillationDataset(Dataset):
    """Torch dataset wrapping distillation supervision triples."""

    def __init__(self, samples: Sequence[DistillationSample], vector_dim: int):
        self.samples = list(samples)
        self.vector_dim = vector_dim

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Mapping[str, torch.Tensor]:
        sample = self.samples[index]
        feature_tensor = torch.cat(
            [
                _pad_vector(sample.role_a.summary_vector, self.vector_dim),
                _pad_vector(sample.role_b.summary_vector, self.vector_dim),
                torch.tensor(
                    [sample.role_a.confidence, sample.role_b.confidence],
                    dtype=torch.float32,
                ),
            ]
        )
        target_vector = _pad_vector(sample.target_vector, self.vector_dim)
        target_conf = torch.tensor(sample.target_confidence, dtype=torch.float32)
        return {
            "features": feature_tensor,
            "target_vector": target_vector,
            "target_confidence": target_conf,
        }


class ColossusDistillationTrainer:
    """Runs supervised distillation for the Colossus integrator heads."""

    def __init__(self, model: Colossus, dataset: ColossusDistillationDataset, config: ColossusDistillationConfig):
        self.model = model
        self.dataset = dataset
        self.config = config
        self.device = torch.device(config.device)
        self.model.to(self.device)
        self.model.vector_projector.train()
        self.model.confidence_head.train()
        self.model.model.eval()
        self._trainable_parameters = list(self.model.vector_projector.parameters()) + list(self.model.confidence_head.parameters())
        self.optimizer = torch.optim.AdamW(self._trainable_parameters, lr=config.learning_rate, weight_decay=config.weight_decay)
        self.vector_loss = nn.MSELoss()
        self.confidence_loss = nn.MSELoss()
        self.dataloader = DataLoader(
            dataset,
            batch_size=config.batch_size,
            shuffle=True,
            drop_last=False,
            num_workers=config.num_workers,
        )
        self.accum_steps = max(1, config.gradient_accumulation_steps)
        total_batches = len(self.dataloader)
        total_updates = max(1, math.ceil(total_batches / self.accum_steps) * config.num_epochs)
        if config.scheduler.lower() == "cosine":
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=total_updates,
                eta_min=config.min_learning_rate,
            )
        else:
            self.scheduler = None

    def fit(self) -> Mapping[str, float]:
        """Train the Colossus decision heads and return aggregate metrics."""

        history = {"vector_loss": [], "confidence_loss": [], "total_loss": []}
        num_batches = len(self.dataloader)
        self.optimizer.zero_grad(set_to_none=True)
        for epoch in range(1, self.config.num_epochs + 1):
            epoch_vector = 0.0
            epoch_conf = 0.0
            epoch_total = 0.0
            batches = 0
            for batch_index, batch in enumerate(self.dataloader, start=1):
                features = batch["features"].to(self.device)
                target_vector = batch["target_vector"].to(self.device)
                target_conf = batch["target_confidence"].to(self.device)

                predicted_vector = self.model.vector_projector(features)
                predicted_conf = self.model.confidence_head(features).squeeze(-1)

                loss_vector = self.vector_loss(predicted_vector, target_vector)
                loss_conf = self.confidence_loss(predicted_conf, target_conf)
                total_loss = loss_vector + self.config.confidence_loss_weight * loss_conf
                scaled_total_loss = total_loss / self.accum_steps
                scaled_total_loss.backward()
                if batch_index % self.accum_steps == 0 or batch_index == num_batches:
                    nn.utils.clip_grad_norm_(self._trainable_parameters, self.config.max_grad_norm)
                    self.optimizer.step()
                    if self.scheduler is not None:
                        self.scheduler.step()
                    self.optimizer.zero_grad(set_to_none=True)

                epoch_vector += loss_vector.detach().item()
                epoch_conf += loss_conf.detach().item()
                epoch_total += total_loss.detach().item()
                batches += 1

            mean_vector = epoch_vector / max(1, batches)
            mean_conf = epoch_conf / max(1, batches)
            mean_total = epoch_total / max(1, batches)
            history["vector_loss"].append(mean_vector)
            history["confidence_loss"].append(mean_conf)
            history["total_loss"].append(mean_total)

            logger.info(
                "Epoch %d/%d | vector %.6f | confidence %.6f | total %.6f",
                epoch,
                self.config.num_epochs,
                mean_vector,
                mean_conf,
                mean_total,
            )

        self.model.use_learned_heads = True
        self.model.learned_mix_ratio = self.config.mix_ratio
        return {
            "final_vector_loss": history["vector_loss"][-1],
            "final_confidence_loss": history["confidence_loss"][-1],
            "final_total_loss": history["total_loss"][-1],
        }

    def save_checkpoint(self, metrics: Mapping[str, float]) -> Path:
        """Persist the trained heads and return the checkpoint path."""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_path = output_dir / f"{timestamp}_{self.config.checkpoint_name}"

        payload = {
            "vector_head": self.model.vector_projector.state_dict(),
            "confidence_head": self.model.confidence_head.state_dict(),
            "meta": {
                "use_learned_heads": True,
                "learned_mix_ratio": self.model.learned_mix_ratio,
                "metrics": dict(metrics),
            },
        }
        torch.save(payload, checkpoint_path)
        self._update_pointer(checkpoint_path)
        logger.info("Saved Colossus heads to %s", checkpoint_path)
        return checkpoint_path

    def _update_pointer(self, checkpoint_path: Path) -> None:
        pointer_path = self._pointer_location()
        try:
            pointer_path.parent.mkdir(parents=True, exist_ok=True)
            pointer_path.write_text(str(checkpoint_path), encoding="utf-8")
            logger.info("Updated Colossus checkpoint pointer at %s", pointer_path)
        except OSError as exc:  # pragma: no cover - filesystem edge cases
            logger.warning("Failed to update Colossus checkpoint pointer %s: %s", pointer_path, exc)

    @staticmethod
    def _pointer_location() -> Path:
        src_root = Path(__file__).resolve().parents[1]
        return src_root / "core" / "config" / "colossus_checkpoint.pointer"


def create_trainer(config: ColossusDistillationConfig) -> ColossusDistillationTrainer:
    """Factory for trainer objects supporting teacher-derived or synthetic supervision."""

    _seed_everything(config.seed)
    samples: List[DistillationSample]
    if config.teacher_data:
        samples = load_teacher_samples(config.teacher_data, config.vector_dim, config.seed, config.dataset_size)
        if len(samples) < config.dataset_size:
            remaining = config.dataset_size - len(samples)
            logger.info("Augmenting %d teacher samples with %d synthetic samples", len(samples), remaining)
            # Create a temp config with the remaining size to generate just enough
            # Or just generate full batch and slice (easier but slightly wasteful)
            synthetic = generate_synthetic_samples(config)
            samples.extend(synthetic[:remaining])
    else:
        samples = generate_synthetic_samples(config)
    dataset = ColossusDistillationDataset(samples, config.vector_dim)
    model_config = ColossusConfig(vector_dim=config.vector_dim, device=config.device)
    model = Colossus(model_config)
    return ColossusDistillationTrainer(model, dataset, config)


def parse_args() -> ColossusDistillationConfig:
    parser = argparse.ArgumentParser(description="Distill Colossus integrator heads using synthetic data.")
    parser.add_argument("--dataset-size", type=int, default=2048, help="Number of synthetic triples to generate.")
    parser.add_argument("--vector-dim", type=int, default=256, help="Dimensionality of message summary vectors.")
    parser.add_argument("--batch-size", type=int, default=64, help="Training batch size.")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs.")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Optimizer learning rate.")
    parser.add_argument("--lr-min", type=float, default=1e-4, help="Floor for cosine annealing learning rate.")
    parser.add_argument("--confidence-weight", type=float, default=0.25, help="Weight applied to confidence loss term.")
    parser.add_argument("--mix-ratio", type=float, default=0.65, help="Blend factor between baseline and learned outputs.")
    parser.add_argument(
        "--gradient-accumulation",
        type=int,
        default=1,
        help="Number of batches to accumulate before each optimizer update.",
    )
    parser.add_argument(
        "--scheduler",
        choices=["none", "cosine"],
        default="cosine",
        help="Learning rate scheduler to apply during training.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("F:/models/management/training_sessions/colossus"),
        help="Directory for saved checkpoints (defaults to F:/models management area).",
    )
    parser.add_argument("--checkpoint-name", type=str, default="colossus_distilled.pt", help="Base filename for saved checkpoints.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--num-workers", type=int, default=0, help="Number of DataLoader worker processes.")
    parser.add_argument(
        "--teacher-data",
        action="append",
        type=Path,
        help="Path to teacher response JSON files or directories (may be provided multiple times).",
    )
    args = parser.parse_args()

    return ColossusDistillationConfig(
        dataset_size=args.dataset_size,
        vector_dim=args.vector_dim,
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        learning_rate=args.learning_rate,
        min_learning_rate=args.lr_min,
        confidence_loss_weight=args.confidence_weight,
        output_dir=args.output_dir,
        checkpoint_name=args.checkpoint_name,
        seed=args.seed,
        mix_ratio=args.mix_ratio,
        num_workers=args.num_workers,
        gradient_accumulation_steps=max(1, args.gradient_accumulation),
        scheduler=args.scheduler,
        teacher_data=tuple(args.teacher_data) if args.teacher_data else None,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    config = parse_args()
    trainer = create_trainer(config)
    metrics = trainer.fit()
    trainer.save_checkpoint(metrics)

    logger.info(
        "Training complete | vector %.6f | confidence %.6f | total %.6f",
        metrics["final_vector_loss"],
        metrics["final_confidence_loss"],
        metrics["final_total_loss"],
    )


if __name__ == "__main__":
    main()
