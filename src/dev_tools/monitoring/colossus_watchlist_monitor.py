#!/usr/bin/env python3
"""Scheduled monitor for Colossus checkpoint drift watchlists.

This utility wraps ``colossus_checkpoint_evaluator`` to generate metrics and
watchlist summaries suitable for CI dashboards and nightly analytics jobs.
It exits with a non-zero status when any watchlisted dimension exceeds the
configured threshold, allowing automation to flag regressions automatically.

Created: November 7, 2025
Author: GitHub Copilot
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.utils.rich_enhancements import create_panel, create_table
from src.dev_tools.storage.summarize_f_drive_catalog import summarize as summarize_catalog
from src.integrator.colossus_model import Colossus, ColossusConfig
from src.training.distillation.metrics.colossus_checkpoint_evaluator import (
    build_samples,
    evaluate_checkpoint,
    write_outputs,
)

try:  # Rich output when available
    from rich.console import Console

    _CONSOLE: Console | None = Console()
except Exception:  # pragma: no cover - optional dependency
    _CONSOLE = None


def _resolve_device(explicit: str | None) -> str:
    if explicit:
        return explicit
    return "cuda" if torch.cuda.is_available() else "cpu"


def _load_model(checkpoint: Path, device: str, vector_dim: int) -> Colossus:
    cfg = ColossusConfig(vector_dim=vector_dim, checkpoint_path=checkpoint, device=device)
    return Colossus.load(cfg)


def _print(panel: object) -> None:
    if _CONSOLE is not None:
        _CONSOLE.print(panel)
    else:
        print(panel)


def _render_summary(rows: Sequence[Sequence[object]], title: str) -> None:
    table = create_table(["Checkpoint", "Avg ΔL2", "Max ΔL2", "Avg ΔConf", "Watchlist Max", "Triggers"], rows, title=title)
    panel = create_panel(table, title="Colossus Watchlist Monitor")
    _print(panel)


def _render_alerts(alerts: Sequence[str]) -> None:
    if not alerts:
        return
    table = create_table(["Watchlist regressions detected"], [[alert] for alert in alerts])
    panel = create_panel(table, title="Alerts", border_style="red")
    _print(panel)


def _format_float(value: float) -> str:
    return f"{value:.3f}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor Colossus checkpoints for watchlist regressions.")
    parser.add_argument("--baseline", required=True, help="Baseline checkpoint path.")
    parser.add_argument("--checkpoints", nargs="+", required=True, help="Candidate checkpoint paths to evaluate.")
    parser.add_argument(
        "--teacher-data",
        action="append",
        nargs="+",
        required=True,
        help="Teacher dataset JSON files used for evaluation (option may repeat).",
    )
    parser.add_argument("--out-dir", default="src/training/distillation/eval_outputs", help="Directory for metrics outputs.")
    parser.add_argument("--vector-dim", type=int, default=256, help="Vector dimensionality (default: 256).")
    parser.add_argument("--device", help="Device override (default: auto-detect).")
    parser.add_argument("--top-k", type=int, default=8, help="Number of prompts to persist per checkpoint (default: 8).")
    parser.add_argument("--watchlist", type=int, nargs="*", default=(27, 59, 70, 83, 118, 141, 191), help="Vector dimension indices to monitor.")
    parser.add_argument("--watchlist-threshold", type=float, default=0.035, help="Alert threshold for watchlist deltas (default: 0.035).")
    parser.add_argument("--catalog-csv", type=Path, help="Optional catalog CSV for storage delta logging.")
    parser.add_argument(
        "--catalog-filter",
        action="append",
        default=None,
        help="First-level directory filters to apply when summarising the catalog (repeat to include multiple).",
    )
    parser.add_argument(
        "--catalog-group-depth",
        type=int,
        default=2,
        help="Grouping depth for catalog summarisation (default: 2).",
    )
    parser.add_argument(
        "--catalog-log-dir",
        type=Path,
        help="Directory to store catalog summary logs (defaults to <out-dir>/catalog_deltas).",
    )
    return parser.parse_args()


def main() -> int:  # pragma: no cover - CLI orchestration
    args = parse_args()
    device = _resolve_device(args.device)
    teacher_paths = [Path(p) for group in args.teacher_data for p in group]
    baseline_path = Path(args.baseline)
    checkpoint_paths = [Path(p) for p in args.checkpoints]
    out_dir = Path(args.out_dir)

    baseline_model = _load_model(baseline_path, device=device, vector_dim=args.vector_dim)
    samples = build_samples(teacher_paths, vector_dim=args.vector_dim, seed=42, baseline_model=baseline_model)
    if not samples:
        raise RuntimeError("No evaluation samples generated; check teacher dataset inputs.")

    summary_rows: list[list[str]] = []
    alerts: list[str] = []

    for checkpoint in checkpoint_paths:
        metrics, per_prompt = evaluate_checkpoint(
            checkpoint=checkpoint,
            device=device,
            vector_dim=args.vector_dim,
            samples=samples,
            top_k=args.top_k,
            watchlist=args.watchlist,
            watchlist_threshold=args.watchlist_threshold,
        )
        label = checkpoint.stem
        metrics["baseline"] = str(baseline_path)
        metrics["teacher_data"] = [str(p) for p in teacher_paths]
        write_outputs(out_dir, label, metrics, per_prompt, args.top_k)

        watchlist_max = metrics.get("watchlist_max_delta", 0.0)
        trigger_count = metrics.get("watchlist_trigger_count", 0)
        summary_rows.append(
            [
                label,
                _format_float(metrics.get("avg_l2", 0.0)),
                _format_float(metrics.get("max_l2", 0.0)),
                _format_float(metrics.get("avg_confidence_delta", 0.0)),
                _format_float(watchlist_max),
                str(trigger_count),
            ]
        )
        if trigger_count:
            prompt_list = metrics.get("watchlist_trigger_prompts", []) or []
            alerts.append(f"{label}: {trigger_count} prompts over threshold {args.watchlist_threshold:.3f} ({', '.join(prompt_list)})")

    _render_summary(summary_rows, title="Watchlist Metrics")
    _render_alerts(alerts)

    if args.catalog_csv:
        timestamp = datetime.now()
        catalog_dir = args.catalog_log_dir or (out_dir / "catalog_deltas")
        catalog_dir.mkdir(parents=True, exist_ok=True)

        totals, counts, ext_sizes = summarize_catalog(
            args.catalog_csv,
            group_depth=max(args.catalog_group_depth, 1),
            first_filters=args.catalog_filter,
        )

        summary_payload = {
            "generated_at": timestamp.strftime("%B %d, %Y %I:%M:%S %p"),
            "catalog_csv": str(args.catalog_csv),
            "group_depth": args.catalog_group_depth,
            "filters": args.catalog_filter or [],
            "totals": {segment: {"bytes": size, "files": counts.get(segment, 0)} for segment, size in totals.items()},
            "top_extensions": [
                {"extension": ext, "bytes": size}
                for ext, size in ext_sizes.most_common(10)
            ],
        }

        summary_path = catalog_dir / f"catalog_summary_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with summary_path.open("w", encoding="utf-8") as handle:
            json.dump(summary_payload, handle, indent=2)

        log_message = f"Catalog summary written to {summary_path}"
        if _CONSOLE is not None:
            _CONSOLE.log(log_message)
        else:  # pragma: no cover - fallback print
            print(log_message)

    return 2 if alerts else 0


if __name__ == "__main__":
    sys.exit(main())
