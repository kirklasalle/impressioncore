"""Tests for guardian_alerting evaluate function.

Created: August 22, 2025
Author: GitHub Copilot
"""
from src.core.monitoring.guardian_alerting import evaluate
from src.core.monitoring.guardian_metrics import GuardianMetricsRegistry, reset_guardian_metrics
from src.core.monitoring.guardian_thresholds import guardian_thresholds


def test_alerting_triggers_and_non_triggers():
    reset_guardian_metrics()
    reg = GuardianMetricsRegistry.instance()
    # Create events to push FN rate high
    for _ in range(3):
        reg.record(layer='policy', decision='allow', risk_composite=0.9, risk_components={'toxicity':0.9}, pii_redactions=0, pii_residual=0, harmful_passed=True, benign_blocked=False, escalation_latency_ms=None, drift_alert=False, drift_true=None)
    snap = reg.snapshot()
    th = guardian_thresholds()
    # Lower the threshold artificially to trigger
    custom = th.snapshot()
    custom['safety_fn_rate_pct'] = 10.0
    alerts = evaluate(snap, custom)
    assert any(a['metric']=='safety_fn_rate_pct' for a in alerts)


def test_alerting_lower_bound_precision():
    reset_guardian_metrics()
    reg = GuardianMetricsRegistry.instance()
    # Add a drift alert that is false (precision 0)
    reg.record(layer='drift_monitor', decision='allow', risk_composite=0.1, risk_components={'drift':0.1}, pii_redactions=0, pii_residual=0, harmful_passed=False, benign_blocked=False, escalation_latency_ms=None, drift_alert=True, drift_true=False)
    snap = reg.snapshot()
    th = {'drift_alert_precision_pct': 50.0}
    alerts = evaluate(snap, th)
    assert any(a['metric']=='drift_alert_precision_pct' and a['mode']=='below_minimum' for a in alerts)
