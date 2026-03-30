"""Tests for guardian_metrics module.

Created: August 22, 2025
Updated: August 22, 2025
Author: GitHub Copilot

Covers:
    - Event recording
    - Window snapshot calculations
    - Drift precision
    - Escalation latency averaging
"""
from src.core.monitoring.guardian_metrics import (
    GuardianMetricsRegistry,
    reset_guardian_metrics,
)


def test_basic_record_and_snapshot():
    reset_guardian_metrics()
    reg = GuardianMetricsRegistry.instance()
    reg.record(layer='input_gate', decision='allow', risk_composite=0.1, risk_components={'toxicity':0.1}, pii_redactions=2, pii_residual=0, harmful_passed=False, benign_blocked=False, escalation_latency_ms=None, drift_alert=False, drift_true=None)
    reg.record(layer='policy', decision='deny', risk_composite=0.9, risk_components={'toxicity':0.9}, pii_redactions=0, pii_residual=1, harmful_passed=True, benign_blocked=False, escalation_latency_ms=42.0, drift_alert=True, drift_true=True)
    snap = reg.snapshot()
    assert 'window' in snap
    w = snap['window']
    assert w['window_events'] >= 2
    assert 'decision_breakdown' in w
    assert w['decision_breakdown'].get('allow',0) >= 1
    assert w['avg_escalation_latency_ms'] > 0
    assert abs(w['drift_alert_precision_pct'] - 100.0) < 1e-6

def test_rate_calculations_edge_cases():
    reset_guardian_metrics()
    reg = GuardianMetricsRegistry.instance()
    # Add event with benign blocked for FP
    reg.record(layer='policy', decision='deny', risk_composite=0.2, risk_components={'toxicity':0.2}, pii_redactions=0, pii_residual=0, harmful_passed=False, benign_blocked=True, escalation_latency_ms=None, drift_alert=False, drift_true=None)
    snap = reg.snapshot()
    w = snap['window']
    # FP or FN rates should be within 0-100
    assert 0.0 <= w['safety_fp_rate_pct'] <= 100.0
    assert 0.0 <= w['safety_fn_rate_pct'] <= 100.0
