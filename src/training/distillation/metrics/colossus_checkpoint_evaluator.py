#!/usr/bin/env python3
"""Compare Colossus checkpoints against a baseline using paired teacher data."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np
import torch

from src.integrator.colossus_model import Colossus, ColossusConfig
from src.training.colossus_distillation import load_teacher_samples


@dataclass
class EvaluationSample:
    """Container holding teacher messages and cached baseline outputs."""

    prompt: str
    teacher_a_name: str
    teacher_a_response: str
    teacher_b_name: str
    teacher_b_response: str
    role_a: Any
    role_b: Any
    baseline_vector: Sequence[float]
    baseline_conf: float


def _device_arg(explicit: str | None) -> str:
    if explicit is not None:
        return explicit
    return "cuda" if torch.cuda.is_available() else "cpu"


def _load_model(checkpoint: Path, device: str, vector_dim: int) -> Colossus:
    cfg = ColossusConfig(vector_dim=vector_dim, checkpoint_path=checkpoint, device=device)
    return Colossus.load(cfg)


def _summarise_vector(values: Sequence[float], limit: int = 10) -> list[float]:
    return [float(x) for x in list(values)[:limit]]


def build_samples(
    teacher_paths: Sequence[Path],
    vector_dim: int,
    seed: int,
    baseline_model: Colossus,
) -> list[EvaluationSample]:
    samples = load_teacher_samples(teacher_paths, vector_dim=vector_dim, seed=seed, max_samples=None)
    evaluation_samples: list[EvaluationSample] = []
    for sample in samples:
        structured_a: Mapping[str, object] = sample.role_a.structured_msg
        structured_b: Mapping[str, object] = sample.role_b.structured_msg
        prompt = str(structured_a.get("prompt") or structured_b.get("prompt") or "")
        baseline_output = baseline_model.integrate(sample.role_a, sample.role_b)
        evaluation_samples.append(
            EvaluationSample(
                prompt=prompt,
                teacher_a_name=str(structured_a.get("teacher", "")),
                teacher_a_response=str(structured_a.get("response", "")),
                teacher_b_name=str(structured_b.get("teacher", "")),
                teacher_b_response=str(structured_b.get("response", "")),
                role_a=sample.role_a,
                role_b=sample.role_b,
                baseline_vector=list(baseline_output.get("summary_vector", [])),
                baseline_conf=float(baseline_output.get("confidence", 0.0)),
            )
        )
    return evaluation_samples


def evaluate_checkpoint(
    checkpoint: Path,
    device: str,
    vector_dim: int,
    samples: Sequence[EvaluationSample],
    top_k: int,
    watchlist: Sequence[int] | None,
    watchlist_threshold: float,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    model = _load_model(checkpoint, device=device, vector_dim=vector_dim)
    vector_deltas: list[float] = []
    confidence_deltas: list[float] = []
    per_prompt: list[dict[str, object]] = []

    watchlist_set = set(watchlist or [])
    watchlist_max_delta = 0.0
    watchlist_trigger_prompts: list[str] = []
    for sample in samples:
        output = model.integrate(sample.role_a, sample.role_b)
        vector = np.array(output.get("summary_vector", []), dtype=np.float32)
        baseline_vector = np.array(sample.baseline_vector, dtype=np.float32)
        if vector.shape != baseline_vector.shape:
            length = min(vector.shape[0], baseline_vector.shape[0])
            vector = vector[:length]
            baseline_vector = baseline_vector[:length]
        delta = float(np.linalg.norm(vector - baseline_vector))
        checkpoint_conf = float(output.get("confidence", 0.0))
        confidence_delta = checkpoint_conf - sample.baseline_conf
        watchlist_deltas: dict[int, float] = {}
        watchlist_triggered = False
        if watchlist_set:
            for dim in watchlist_set:
                if 0 <= dim < vector.shape[0]:
                    dim_delta = float(abs(vector[dim] - baseline_vector[dim]))
                    watchlist_deltas[dim] = dim_delta
                    if dim_delta > watchlist_max_delta:
                        watchlist_max_delta = dim_delta
                    if dim_delta > watchlist_threshold:
                        watchlist_triggered = True
        if watchlist_triggered:
            watchlist_trigger_prompts.append(sample.prompt)
        vector_deltas.append(delta)
        confidence_deltas.append(confidence_delta)
        per_prompt.append(
            {
                "prompt": sample.prompt,
                "vector_delta_l2": delta,
                "checkpoint_confidence": checkpoint_conf,
                "baseline_confidence": sample.baseline_conf,
                "confidence_delta": confidence_delta,
                "teacher_a": sample.teacher_a_name,
                "teacher_b": sample.teacher_b_name,
                "teacher_a_response": sample.teacher_a_response,
                "teacher_b_response": sample.teacher_b_response,
                "summary_vector_head": _summarise_vector(vector),
                "watchlist_deltas": watchlist_deltas,
                "watchlist_triggered": watchlist_triggered,
            }
        )

    per_prompt.sort(key=lambda item: item["vector_delta_l2"], reverse=True)
    top_entries = per_prompt[:top_k]
    metrics = {
        "checkpoint": str(checkpoint),
        "num_prompts": len(samples),
        "avg_l2": mean(vector_deltas) if vector_deltas else 0.0,
        "max_l2": top_entries[0]["vector_delta_l2"] if top_entries else 0.0,
        "max_prompt": top_entries[0]["prompt"] if top_entries else None,
        "max_conf_checkpoint": top_entries[0]["checkpoint_confidence"] if top_entries else None,
        "max_conf_baseline": top_entries[0]["baseline_confidence"] if top_entries else None,
        "avg_confidence_delta": mean(confidence_deltas) if confidence_deltas else 0.0,
    }
    if watchlist_set:
        metrics.update(
            {
                "watchlist_dims": sorted(watchlist_set),
                "watchlist_threshold": watchlist_threshold,
                "watchlist_max_delta": watchlist_max_delta,
                "watchlist_trigger_count": len(watchlist_trigger_prompts),
                "watchlist_trigger_prompts": watchlist_trigger_prompts,
            }
        )
    return metrics, per_prompt


def write_outputs(
    out_dir: Path,
    checkpoint_label: str,
    metrics: Mapping[str, object],
    per_prompt: Sequence[Mapping[str, object]],
    top_k: int,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / f"colossus_metrics_{checkpoint_label}.json"
    transcripts_path = out_dir / f"colossus_transcripts_{checkpoint_label}.jsonl"
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
    with transcripts_path.open("w", encoding="utf-8") as handle:
        for entry in per_prompt[:top_k]:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return metrics_path, transcripts_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare Colossus checkpoints against a baseline.")
    parser.add_argument("--teacher-data", nargs="+", required=True, help="Teacher dataset JSON files to evaluate.")
    parser.add_argument("--baseline", required=True, help="Baseline checkpoint path for comparison.")
    parser.add_argument("--checkpoints", nargs="+", required=True, help="One or more checkpoints to evaluate.")
    parser.add_argument("--vector-dim", type=int, default=256, help="Vector dimensionality (default: 256).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for teacher sample loading.")
    parser.add_argument("--device", help="Device override (default: auto-detect).")
    parser.add_argument("--top-k", type=int, default=5, help="Number of top-delta prompts to persist.")
    parser.add_argument("--out-dir", default="src/training/distillation/eval_outputs", help="Directory for output artifacts.")
    parser.add_argument(
        "--watchlist",
        type=int,
        nargs="*",
        help="Optional list of vector dimension indices to monitor for regression alerts.",
    )
    parser.add_argument(
        "--watchlist-threshold",
        type=float,
        default=0.035,
        help="Alert threshold for absolute delta on watchlisted dimensions (default: 0.035).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = _device_arg(args.device)
    teacher_paths = [Path(p) for p in args.teacher_data]
    baseline_path = Path(args.baseline)
    checkpoint_paths = [Path(p) for p in args.checkpoints]
    out_dir = Path(args.out_dir)

    baseline_model = _load_model(baseline_path, device=device, vector_dim=args.vector_dim)
    evaluation_samples = build_samples(teacher_paths, vector_dim=args.vector_dim, seed=args.seed, baseline_model=baseline_model)
    if not evaluation_samples:
        raise RuntimeError("No evaluation samples generated from the provided teacher data.")

    for checkpoint in checkpoint_paths:
        metrics, per_prompt = evaluate_checkpoint(
            checkpoint=checkpoint,
            device=device,
            vector_dim=args.vector_dim,
            samples=evaluation_samples,
            top_k=args.top_k,
            watchlist=args.watchlist,
            watchlist_threshold=args.watchlist_threshold,
        )
        label = checkpoint.stem
        metrics["baseline"] = str(baseline_path)
        metrics["teacher_data"] = [str(p) for p in teacher_paths]
        metrics_path, transcripts_path = write_outputs(out_dir, label, metrics, per_prompt, args.top_k)
        print(f"[ok] Metrics -> {metrics_path}")
        print(f"[ok] Top-{args.top_k} transcripts -> {transcripts_path}")


if __name__ == "__main__":
    main()
