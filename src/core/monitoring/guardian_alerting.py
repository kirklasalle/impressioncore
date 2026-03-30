"""Guardian Alert Evaluation

Created: August 22, 2025
Updated: August 22, 2025
Author: GitHub Copilot
Tags: #guardian_stack #alerting #kpi #monitoring

Purpose:
    Evaluate guardian metrics snapshot against configured thresholds and produce
    structured alert objects for downstream routing (logging, event bus, etc.).

Design:
    - Pure function evaluate(snapshot, thresholds) -> list[dict]
    - Threshold comparison: metric >= threshold triggers ALERT unless metric is *rate to minimize*; for simplicity, treat all as upper bounds.

Extension Points:
    - Future: severity scaling, hysteresis windows, debounce logic

"""
from __future__ import annotations

from typing import Any

UPPER_BOUND_KEYS = {
    'safety_fn_rate_pct',
    'safety_fp_rate_pct',
    'redaction_leakage_rate_pct',
    'avg_escalation_latency_ms',
}
# For precision, we enforce minimum (lower bound)
LOWER_BOUND_KEYS = {
    'drift_alert_precision_pct',
}

def evaluate(snapshot: dict[str, Any], thresholds: dict[str, float]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    window = snapshot.get('window', {})
    for key, limit in thresholds.items():
        val = window.get(key)
        if val is None:
            continue
        if key in LOWER_BOUND_KEYS:
            if val < limit:
                alerts.append(_alert(key, val, limit, 'below_minimum'))
        else:  # default upper bound
            if val > limit:
                alerts.append(_alert(key, val, limit, 'above_maximum'))
    return alerts

def _alert(metric: str, value: float, threshold: float, mode: str) -> dict[str, Any]:
    return {
        'metric': metric,
        'value': value,
        'threshold': threshold,
        'mode': mode,
    }

__all__ = ['evaluate']
