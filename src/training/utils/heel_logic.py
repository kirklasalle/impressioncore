"""Heel (Sweet Spot) Detection Logic Utilities.

Extracted from kd_sft_curriculum main loop to reduce cognitive complexity.
Provides:
  - State container (dict-based) initializer
  - Metric update function computing efficiency & candidate flags

The main training loop remains responsible for side-effects (logging,
checkpointing, phase2 activation) to keep this module pure.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass
class HeelConfigView:
    heel_min_windows: int
    heel_min_eff_floor: float
    heel_eff_ratio: float
    heel_curvature_tol: float
    heel_var_ratio_max: float
    heel_peak_decay: float
    heel_hold_consec: int


def init_heel_state() -> dict[str, Any]:
    return {
        "last_raw_ce": None,
        "eff_ema": 0.0,
        "eff_peak": 0.0,
        "eff_prev": deque(maxlen=3),
        "raw_ce_history": deque(maxlen=16),
        "windows": 0,
        "heel_consec": 0,
        "heel_reported": False,
        "heel_stopped": False,
        "last_token_eff": None,
    }


def update_heel_metrics(state: dict[str, Any], cfg: HeelConfigView, *, pre_reset_raw_ce: float, supervised_tok: int) -> dict[str, Any]:
    """Update heel instrumentation metrics.

    Returns a metrics dict with:
      token_eff, eff_ratio, curvature, var_ratio, heel_cand, cand_reasons
    """
    state["windows"] += 1
    # Compute improvement delta (only positive decreases in loss)
    delta_ce = 0.0
    if state["last_raw_ce"] is not None:
        delta_ce = max(0.0, state["last_raw_ce"] - pre_reset_raw_ce)
    token_eff = delta_ce / max(1, supervised_tok)
    # EMA + peak (with decay)
    state["eff_ema"] = 0.9 * state["eff_ema"] + 0.1 * token_eff
    state["eff_peak"] = max(state["eff_peak"] * cfg.heel_peak_decay, state["eff_ema"])
    state["eff_prev"].append(state["eff_ema"])
    curvature = 0.0
    if len(state["eff_prev"]) == 3:
        a, b, c = state["eff_prev"][0], state["eff_prev"][1], state["eff_prev"][2]
        curvature = c - 2 * b + a
    state["raw_ce_history"].append(pre_reset_raw_ce)
    var_ratio = 0.0
    if len(state["raw_ce_history"]) > 4:
        vals = list(state["raw_ce_history"])
        mean_v = sum(vals) / len(vals)
        if mean_v > 0:
            var = sum((x - mean_v) ** 2 for x in vals) / len(vals)
            std = var ** 0.5
            var_ratio = std / mean_v
    eff_ratio = (token_eff / (state["eff_peak"] + 1e-12)) if state["eff_peak"] > 0 else 0.0
    cand_reasons = {
        "enough_windows": state["windows"] >= cfg.heel_min_windows,
        "above_eff_floor": token_eff >= cfg.heel_min_eff_floor,
        "eff_ratio_ok": eff_ratio <= cfg.heel_eff_ratio,
        "curvature_ok": curvature > -cfg.heel_curvature_tol,
        "var_ok": var_ratio < cfg.heel_var_ratio_max,
    }
    heel_cand = all(cand_reasons.values()) and state["eff_peak"] > 0
    if heel_cand:
        state["heel_consec"] += 1
    else:
        state["heel_consec"] = 0
    state["last_token_eff"] = token_eff
    metrics = {
        "token_eff": token_eff,
        "eff_ratio": eff_ratio,
        "curvature": curvature,
        "var_ratio": var_ratio,
        "heel_cand": heel_cand,
        "cand_reasons": cand_reasons,
    }
    state["last_raw_ce"] = pre_reset_raw_ce
    return metrics
