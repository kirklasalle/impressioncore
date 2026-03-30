"""Summarise Colossus checkpoint drift metrics for quick human review.

Parses the JSONL transcripts emitted by ``colossus_checkpoint_evaluator`` and
surfaces aggregate statistics together with the highest-delta prompts. The
output defaults to a Rich-styled table when the dependency is available, but
falls back to plain text so the script remains safe in minimal environments.

Created: November 7, 2025
Author: GitHub Copilot
"""

from __future__ import annotations

import argparse
import json
import statistics as stats
from collections.abc import Iterable, Mapping
from pathlib import Path

from src.core.utils.rich_enhancements import create_panel, create_table

try:  # Rich rendering when available
    from rich.console import Console

    _CONSOLE: Console | None = Console()
except Exception:  # pragma: no cover - optional dependency
    _CONSOLE = None


def _load_transcripts(path: Path) -> list[Mapping[str, object]]:
    if not path.is_file():
        raise FileNotFoundError(f"Transcript file not found: {path}")
    entries: list[Mapping[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        record = line.strip()
        if not record:
            continue
        entries.append(json.loads(record))
    if not entries:
        raise ValueError(f"No entries parsed from transcript file: {path}")
    return entries


def _format_float(value: float, precision: int = 3) -> str:
    return f"{value:.{precision}f}"


def _summarise_deltas(entries: Iterable[Mapping[str, object]]) -> Mapping[str, float]:
    vector_deltas = [float(item["vector_delta_l2"]) for item in entries]
    confidence_deltas = [float(item["confidence_delta"]) for item in entries]
    summary = {
        "count": float(len(vector_deltas)),
        "avg_l2": stats.mean(vector_deltas),
        "median_l2": stats.median(vector_deltas),
        "p90_l2": stats.quantiles(vector_deltas, n=10)[8] if len(vector_deltas) > 1 else vector_deltas[0],
        "max_l2": max(vector_deltas),
        "avg_conf_delta": stats.mean(confidence_deltas),
        "max_conf_delta": max(confidence_deltas),
        "min_conf_delta": min(confidence_deltas),
    }
    summary["count_over_050"] = float(sum(delta > 0.5 for delta in vector_deltas))
    summary["count_conf_negative"] = float(sum(delta < 0 for delta in confidence_deltas))
    return summary


def _render_summary(summary: Mapping[str, float]) -> None:
    rows = [
        ["Prompts", int(summary["count"])],
        ["Avg ΔL2", _format_float(summary["avg_l2"])],
        ["Median ΔL2", _format_float(summary["median_l2"])],
        ["P90 ΔL2", _format_float(summary["p90_l2"])],
        ["> 0.50 ΔL2", int(summary["count_over_050"])],
        ["Avg ΔConfidence", _format_float(summary["avg_conf_delta"])],
        ["Max ΔConfidence", _format_float(summary["max_conf_delta"])],
        ["Min ΔConfidence", _format_float(summary["min_conf_delta"])],
        ["Confidence Drops", int(summary["count_conf_negative"])],
    ]
    table = create_table(["Metric", "Value"], rows, title="Colossus Drift Summary")
    panel = create_panel(table, title="Aggregate Drift Metrics")
    if _CONSOLE is not None:
        _CONSOLE.print(panel)
    else:
        print(panel)


def _render_top_entries(entries: list[Mapping[str, object]], limit: int) -> None:
    rows: list[list[str]] = []
    for item in entries[:limit]:
        vector_delta = _format_float(float(item["vector_delta_l2"]))
        confidence_delta = _format_float(float(item["confidence_delta"]))
        prompt = str(item.get("prompt", ""))
        rows.append([vector_delta, confidence_delta, prompt])
    table = create_table(["ΔL2", "ΔConfidence", "Prompt"], rows, title=f"Top {limit} Drift Prompts")
    panel = create_panel(table, title="High-Variance Prompts")
    if _CONSOLE is not None:
        _CONSOLE.print(panel)
    else:
        print(panel)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarise Colossus drift metrics from transcript JSONL files.")
    parser.add_argument("transcripts", type=Path, help="Path to transcripts JSONL produced by the evaluator.")
    parser.add_argument("--top", type=int, default=5, help="Number of prompts to surface (default: 5).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entries = _load_transcripts(args.transcripts)
    summary = _summarise_deltas(entries)
    _render_summary(summary)
    sorted_entries = sorted(entries, key=lambda item: float(item["vector_delta_l2"]), reverse=True)
    _render_top_entries(sorted_entries, limit=max(1, args.top))


if __name__ == "__main__":
    main()
