"""Compare Heel Stop vs Phase2 Refinement Runs

Utility script to summarize and compare two KD+SFT training runs:
- Extract heel stop / transition information
- Compute aggregate loss metrics (raw CE, KL, total) over final N windows/steps
- Summarize efficiency metrics if heel_report JSON present

Usage (PowerShell):
  .venv310\\Scripts\activate
  python -m src.training.analysis.compare_heel_runs \
    --run-a F:/models/checkpoints/kd_sft_phase \
    --run-b F:/models/checkpoints/kd_sft_phase2_rerun \
    --last-n 25 \
    --out F:/models/checkpoints/kd_sft_phase2_rerun/heel_comparison_summary.json

Design Notes:
- Pure read-only; safe to run during ongoing training (Race-safe: opens files afresh)
- Tolerates missing files (skips gracefully)
- Efficiency metrics extracted from heel_report_step_*.json if present
- If Phase2 transition report present, captures Phase2 settings in summary

"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _load_metrics_csv(run_dir: Path) -> list[dict[str, Any]]:
    path = run_dir / "training_metrics.csv"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Cast numeric fields where possible
            casted = {}
            for k, v in r.items():
                if v is None or v == "":
                    casted[k] = v
                    continue
                try:
                    if "." in v or "e" in v.lower():
                        casted[k] = float(v)
                    else:
                        casted[k] = int(v)
                except Exception:
                    casted[k] = v
            rows.append(casted)
    return rows


def _find_json(run_dir: Path, prefix: str) -> Path | None:
    for p in sorted(run_dir.glob(f"{prefix}*.json")):
        return p
    return None


def _heel_report(run_dir: Path) -> dict[str, Any] | None:
    p = _find_json(run_dir, "heel_report_step_")
    if p and p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _phase2_transition(run_dir: Path) -> dict[str, Any] | None:
    p = _find_json(run_dir, "heel_phase2_transition_step_")
    if p and p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _final_summary(run_dir: Path) -> dict[str, Any] | None:
    p = _find_json(run_dir, "final_training_summary_")
    if p and p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def summarize_run(run_dir: Path, last_n: int) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    metrics = _load_metrics_csv(run_dir)
    heel_rep = _heel_report(run_dir)
    phase2_rep = _phase2_transition(run_dir)
    final_sum = _final_summary(run_dir)

    last_slice = metrics[-last_n:] if last_n > 0 and len(metrics) >= last_n else metrics

    def avg(key: str) -> float | None:
        vals = [m[key] for m in last_slice if key in m and isinstance(m[key], int | float)]
        return sum(vals)/len(vals) if vals else None

    out = {
        "run_dir": str(run_dir),
        "total_steps_recorded": len(metrics),
        "last_n_considered": len(last_slice),
        "avg_total_loss_last_n": avg("total_loss"),
        "avg_raw_ce_last_n": avg("raw_ce"),
        "avg_kl_last_n": avg("kl_loss"),
        "avg_kl_beta_last_n": avg("kl_beta"),
        "avg_kl_ratio_last_n": avg("kl_ratio"),
    }

    if heel_rep:
        out["heel_stop_step"] = heel_rep.get("step")
        out["heel_eff_ratio"] = heel_rep.get("metrics", {}).get("eff_ratio")
        out["heel_token_eff"] = heel_rep.get("metrics", {}).get("token_eff")
        out["heel_curvature"] = heel_rep.get("metrics", {}).get("curvature")
        out["heel_var_ratio"] = heel_rep.get("metrics", {}).get("var_ratio")
    if phase2_rep:
        out["phase2_transition_step"] = phase2_rep.get("transition_step")
        out["phase2_cfg"] = phase2_rep.get("phase2_config")
    if final_sum:
        out["final_summary_kind"] = final_sum.get("stop_kind")
        out["final_summary_step"] = final_sum.get("final_step")
    return out


def compare(run_a: Path, run_b: Path, last_n: int) -> dict[str, Any]:
    a = summarize_run(run_a, last_n)
    b = summarize_run(run_b, last_n)
    out = {"run_a": a, "run_b": b}

    # Simple deltas if both have same keys
    def delta(k: str):
        if k in a and k in b and isinstance(a[k], int | float) and isinstance(b[k], int | float):
            return b[k] - a[k]
        return None

    out["deltas"] = {
        "delta_avg_total_loss_last_n": delta("avg_total_loss_last_n"),
        "delta_avg_raw_ce_last_n": delta("avg_raw_ce_last_n"),
        "delta_avg_kl_last_n": delta("avg_kl_last_n"),
        "delta_avg_kl_ratio_last_n": delta("avg_kl_ratio_last_n"),
    }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Compare two KD+SFT runs (heel stop vs phase2 refinement)")
    ap.add_argument("--run-a", required=True, help="Path to first run directory (baseline / heel stop)")
    ap.add_argument("--run-b", required=True, help="Path to second run directory (phase2)")
    ap.add_argument("--last-n", type=int, default=25, help="Number of final metric rows to average (0=all)")
    ap.add_argument("--out", help="Optional path to write JSON summary")
    args = ap.parse_args()

    summary = compare(Path(args.run_a), Path(args.run_b), args.last_n)
    text = json.dumps(summary, indent=2, sort_keys=True)
    print(text)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"[compare] Wrote summary → {out_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
