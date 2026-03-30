"""Spot-check Colossus baseline vs. candidate outputs for high-drift prompts.

Loads the teacher dataset, replays the top-Δ prompts captured in the evaluator
transcripts, and prints a side-by-side comparison of vector and confidence
outputs for the baseline and candidate checkpoints.

Created: November 7, 2025
Author: GitHub Copilot
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from src.core.utils.rich_enhancements import create_panel, create_table
from src.integrator.colossus_model import Colossus, ColossusConfig
from src.training.colossus_distillation import DistillationSample, load_teacher_samples

try:  # Rich console is optional but desirable for readability
    from rich.console import Console

    _CONSOLE: Console | None = Console()
except Exception:  # pragma: no cover - environments without rich
    _CONSOLE = None


@dataclass(frozen=True)
class PromptKey:
    prompt: str
    teacher_a: str
    teacher_b: str

    @classmethod
    def from_sample(cls, sample: DistillationSample) -> PromptKey:
        structured_a = sample.role_a.structured_msg
        structured_b = sample.role_b.structured_msg
        return cls(
            prompt=str(structured_a.get("prompt", "")),
            teacher_a=str(structured_a.get("teacher", "")),
            teacher_b=str(structured_b.get("teacher", "")),
        )

    @classmethod
    def from_entry(cls, entry: Mapping[str, object]) -> PromptKey:
        return cls(
            prompt=str(entry.get("prompt", "")),
            teacher_a=str(entry.get("teacher_a", "")),
            teacher_b=str(entry.get("teacher_b", "")),
        )

    def swapped(self) -> PromptKey:
        return PromptKey(prompt=self.prompt, teacher_a=self.teacher_b, teacher_b=self.teacher_a)


def _load_transcripts(path: Path, top: int) -> list[Mapping[str, object]]:
    if not path.is_file():
        raise FileNotFoundError(f"Transcript file not found: {path}")
    entries: list[Mapping[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = line.strip()
            if not payload:
                continue
            data = json.loads(payload)
            entries.append(data)
    if not entries:
        raise ValueError(f"No entries parsed from transcript file: {path}")
    entries.sort(key=lambda item: float(item.get("vector_delta_l2", 0.0)), reverse=True)
    return entries[:top]


def _build_sample_lookup(paths: Sequence[Path], vector_dim: int) -> dict[PromptKey, DistillationSample]:
    samples = load_teacher_samples(paths, vector_dim=vector_dim, seed=42, max_samples=None)
    lookup: dict[PromptKey, DistillationSample] = {}
    for sample in samples:
        key = PromptKey.from_sample(sample)
        lookup[key] = sample
        lookup[key.swapped()] = sample  # accommodate reversed teacher orderings
    return lookup


def _load_model(path: Path, vector_dim: int, device: str) -> Colossus:
    cfg = ColossusConfig(vector_dim=vector_dim, checkpoint_path=path, device=device)
    return Colossus.load(cfg)


def _extract_vector(payload: Mapping[str, object]) -> np.ndarray:
    vector = np.array(payload.get("summary_vector", []), dtype=np.float32)
    return vector


def _format_float(value: float, precision: int = 3) -> str:
    return f"{value:.{precision}f}"


def _print(panel: object) -> None:
    if _CONSOLE is not None:
        _CONSOLE.print(panel)
    else:
        print(panel)


def _compare_samples(
    baseline: Colossus,
    candidate: Colossus,
    sample: DistillationSample,
    label: str,
    vector_dim: int,
) -> Mapping[str, object]:
    baseline_out = baseline.integrate(sample.role_a, sample.role_b)
    candidate_out = candidate.integrate(sample.role_a, sample.role_b)

    vec_base = _extract_vector(baseline_out)
    vec_candidate = _extract_vector(candidate_out)
    length = min(len(vec_base), len(vec_candidate), vector_dim)
    vec_base = vec_base[:length]
    vec_candidate = vec_candidate[:length]
    delta = vec_candidate - vec_base

    l2 = float(np.linalg.norm(delta))
    top_indices = np.argsort(np.abs(delta))[::-1][:3]
    top_dims = [(int(idx), float(delta[idx])) for idx in top_indices]

    return {
        "label": label,
        "baseline_conf": float(baseline_out.get("confidence", 0.0)),
        "candidate_conf": float(candidate_out.get("confidence", 0.0)),
        "confidence_delta": float(candidate_out.get("confidence", 0.0) - baseline_out.get("confidence", 0.0)),
        "l2": l2,
        "summary_head_baseline": vec_base[:10].tolist(),
        "summary_head_candidate": vec_candidate[:10].tolist(),
        "summary_head_delta": delta[:10].tolist(),
        "top_dims": top_dims,
    }


def _render_results(prompt: str, metrics: Mapping[str, object]) -> None:
    rows = [
        ["Baseline Conf.", _format_float(metrics["baseline_conf"], 3)],
        ["Candidate Conf.", _format_float(metrics["candidate_conf"], 3)],
        ["Δ Confidence", _format_float(metrics["confidence_delta"], 3)],
        ["Δ L2", _format_float(metrics["l2"], 3)],
        ["Top Δ dims", ", ".join(f"{idx}:{_format_float(delta, 3)}" for idx, delta in metrics["top_dims"])],
    ]
    table = create_table(["Metric", "Value"], rows, title=prompt)
    panel = create_panel(table, title="Colossus Spot Check")
    _print(panel)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Spot-check Colossus prompts for drift against a baseline checkpoint.")
    parser.add_argument("--transcripts", type=Path, required=True, help="Transcripts JSONL produced by the evaluator.")
    parser.add_argument("--teacher-data", action="append", type=Path, required=True, help="Teacher dataset used during evaluation.")
    parser.add_argument("--baseline", type=Path, required=True, help="Baseline checkpoint path.")
    parser.add_argument("--checkpoint", type=Path, required=True, help="Candidate checkpoint path to inspect.")
    parser.add_argument("--vector-dim", type=int, default=256, help="Vector dimensionality (default: 256).")
    parser.add_argument("--device", type=str, default=None, help="Device override (default: auto).")
    parser.add_argument("--top", type=int, default=8, help="Number of prompts to inspect (default: 8).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    transcript_entries = _load_transcripts(args.transcripts, top=args.top)
    sample_lookup = _build_sample_lookup(tuple(args.teacher_data), vector_dim=args.vector_dim)

    baseline_model = _load_model(args.baseline, vector_dim=args.vector_dim, device=device)
    candidate_model = _load_model(args.checkpoint, vector_dim=args.vector_dim, device=device)

    for entry in transcript_entries:
        key = PromptKey.from_entry(entry)
        sample = sample_lookup.get(key)
        if sample is None:
            sample = sample_lookup.get(key.swapped())
        if sample is None:
            raise KeyError(f"No teacher sample found for prompt '{key.prompt}' with teachers {key.teacher_a}/{key.teacher_b}")
        metrics = _compare_samples(
            baseline=baseline_model,
            candidate=candidate_model,
            sample=sample,
            label=key.prompt,
            vector_dim=args.vector_dim,
        )
        _render_results(key.prompt, metrics)


if __name__ == "__main__":
    main()
