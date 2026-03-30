"""Tests for guardian_thresholds module.

Created: August 22, 2025
Updated: August 22, 2025
Author: GitHub Copilot
"""
from src.core.monitoring.guardian_thresholds import guardian_thresholds


def test_defaults_present():
    th = guardian_thresholds()
    snap = th.snapshot()
    assert 'safety_fn_rate_pct' in snap
    assert snap['avg_escalation_latency_ms'] > 0
