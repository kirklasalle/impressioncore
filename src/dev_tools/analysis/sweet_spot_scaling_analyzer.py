"""
Sweet Spot Scaling Analyzer

Parses available logs and manual datapoints to summarize (N parameters, loss, tokens, VRAM)
and computes simple local scaling indicators. Produces JSON and Markdown reports in docs/reports/.

Usage:
  python -m src.dev_tools.analysis.sweet_spot_scaling_analyzer \
    --logs d:/Projects/impressioncore/sweet_spot_recovery_training.log \
    --manual d:/Projects/impressioncore/docs/reports/manual_scaling_points.json

Outputs:
  docs/reports/sweet_spot_scaling_analysis.json
  docs/reports/sweet_spot_scaling_analysis.md
"""

from __future__ import annotations

import argparse
import contextlib
import json
import math
import os
import re
from dataclasses import asdict, dataclass
from typing import Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REPORTS_DIR = os.path.join(REPO_ROOT, "docs", "reports")


@dataclass
class Point:
    N_params: float
    loss: float | None
    tokens: float | None
    vram_mb: float | None
    source: str
    note: str | None = None


def ensure_reports_dir() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)


def parse_log(path: str) -> list[Point]:
    pts: list[Point] = []
    if not os.path.exists(path):
        return pts
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        return pts

    # Extract parameter count
    m_params = re.search(r"Total Parameters:\s*([0-9,]+)", text)
    N_params = None
    if m_params:
        try:
            N_params = float(m_params.group(1).replace(",", ""))
        except Exception:
            N_params = None

    # Find best/min loss reported
    losses = []
    for m in re.finditer(r"Loss:\s*([0-9]+\.[0-9]+)", text):
        with contextlib.suppress(Exception):
            losses.append(float(m.group(1)))
    best_loss = min(losses) if losses else None

    # Rough VRAM capture (current VRAM per step; take max)
    vram_vals = []
    for m in re.finditer(r"VRAM:\s*([0-9]+)MB", text):
        with contextlib.suppress(Exception):
            vram_vals.append(float(m.group(1)))
    vram_mb = max(vram_vals) if vram_vals else None

    if N_params is not None:
        pts.append(Point(N_params=N_params, loss=best_loss, tokens=None, vram_mb=vram_mb, source=f"log:{os.path.basename(path)}"))
    return pts


def load_manual_points(path: str) -> list[Point]:
    pts: list[Point] = []
    if not os.path.exists(path):
        return pts
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return pts
    for d in data:
        pts.append(Point(
            N_params=float(d.get("N_params")),
            loss=d.get("loss"),
            tokens=d.get("tokens"),
            vram_mb=d.get("vram_mb"),
            source=str(d.get("source", "manual")),
            note=d.get("note"),
        ))
    return pts


def compute_local_slope(points: list[Point]) -> float | None:
    # Fit slope for log(loss) vs log(N) for valid finite pairs; requires >=2 valid points
    valid = [(p.N_params, p.loss) for p in points if p.loss is not None and p.loss > 0 and p.N_params > 0]
    if len(valid) < 2:
        return None
    xs = [math.log(v[0]) for v in valid]
    ys = [math.log(v[1]) for v in valid]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    if den == 0:
        return None
    slope = num / den
    return slope  # expected negative if loss decreases with N


def main() -> int:
    ap = argparse.ArgumentParser(description="Sweet Spot Scaling Analyzer")
    ap.add_argument("--logs", nargs="*", default=[], help="Paths to training log files to parse")
    ap.add_argument("--manual", default=os.path.join(REPO_ROOT, "docs", "reports", "manual_scaling_points.json"), help="Path to manual datapoints JSON")
    args = ap.parse_args()

    ensure_reports_dir()

    points: list[Point] = []
    for lp in args.logs:
        points.extend(parse_log(lp))
    points.extend(load_manual_points(args.manual))

    # Deduplicate by (N, source) best-loss preference
    points.sort(key=lambda p: (p.N_params, (p.loss if p.loss is not None else float("inf"))))

    slope = compute_local_slope(points)
    summary: dict[str, Any] = {
        "points": [asdict(p) for p in points],
        "local_log_slope_loss_vs_params": slope,
        "interpretation": (
            "negative slope => loss falls with params (expected under adequate data); "
            "positive slope => anomaly (likely under-training/data mismatch)"
        ),
    }

    # Write JSON
    json_path = os.path.join(REPO_ROOT, "docs", "reports", "sweet_spot_scaling_analysis.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Write Markdown report
    md_path = os.path.join(REPO_ROOT, "docs", "reports", "sweet_spot_scaling_analysis.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Sweet Spot Scaling Analysis\n\n")
        f.write("Generated automatically.\n\n")
        f.write("## Data Points\n\n")
        for p in points:
            f.write(f"- N={p.N_params:.1f} params; loss={p.loss if p.loss is not None else 'NA'}; "
                    f"VRAM={p.vram_mb if p.vram_mb is not None else 'NA'} MB; source={p.source}"
                    + (f"; note={p.note}" if p.note else "") + "\n")
        f.write("\n## Local scaling indicator\n\n")
        if slope is None:
            f.write("Insufficient comparable points to estimate a slope.\n\n")
        else:
            f.write(f"log(loss) vs log(N) slope: {slope:.3f} ")
            if slope < 0:
                f.write("(loss decreases with parameters within observed range)\n\n")
            else:
                f.write("(anomalous: loss increases with parameters; likely data/compute mismatch)\n\n")
        f.write("## Guidance\n\n")
        f.write("- Co-scale data tokens with parameter increases to stay compute-optimal.\n")
        f.write("- Measure tokens seen and wall-clock to compare fairly across N.\n")
        f.write("- Prefer active-parameter accounting for MoE when judging compute.\n")
        f.write("- Use early-stop based on improvement-per-hour to avoid wasted runs.\n")

    print(f"Wrote {json_path}\nWrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
