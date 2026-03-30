"""Guardian Metrics Telemetry Integration

Created: August 22, 2025
Updated: August 22, 2025
Author: GitHub Copilot
Tags: #guardian_stack #telemetry #kpi #metrics #monitoring #python #core
Category: Core Implementation
Status: Active

Purpose:
    Collect and expose Guardian Stack KPI-aligned metrics (spec §§7–8, KPI Registry §§3–4) in a lightweight, extensible interface.

Design Goals:
    - Zero heavy deps (reuse existing PerformanceTelemetry where possible)
    - Constant-time hot-path updates (lock-free via deque or atomic ops)
    - Pluggable exporters (future: Prometheus / OpenTelemetry)
    - Privacy-safe (no raw PII payloads; only counts & hashes)

Contract:
    record_event(event: GuardianEvent) -> None
    snapshot() -> Dict[str, Any]
    get_metric(name) -> value

Edge Cases:
    - High-frequency events (mitigate lock contention)
    - Partial metric availability (graceful defaults)
    - Rolling window underrun (insufficient samples)

"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

# --- Data Structures -----------------------------------------------------------------

@dataclass
class GuardianEvent:
    ts: float
    layer: str
    decision: str  # allow | transform | deny | escalate
    risk_composite: float
    risk_components: dict[str, float]
    pii_redactions: int = 0
    pii_residual: int = 0
    harmful_passed: bool = False  # for FN calc
    benign_blocked: bool = False  # for FP calc
    escalation_latency_ms: float | None = None
    drift_alert: bool = False
    drift_true: bool | None = None  # for precision

# --- Metrics Core --------------------------------------------------------------------

class GuardianMetrics:
    """KPI-aligned guardian metrics aggregator.

    Rolling windows track short-horizon performance while cumulative counters
    provide gate-exit summaries.
    """
    def __init__(self, window_seconds: int = 600):
        self.window_seconds = window_seconds
        self._events: deque[GuardianEvent] = deque()
        self._lock = threading.Lock()
        self._counters = defaultdict(int)
        self._latency_samples: list[float] = []
        self._drift_alerts = 0
        self._drift_true = 0

    # --- Recording ------------------------------------------------------------------
    def record_event(self, event: GuardianEvent) -> None:
        now = time.time()
        with self._lock:
            self._events.append(event)
            self._prune(now)
            # Counters
            if event.harmful_passed:
                self._counters['harmful_passed'] += 1
            if event.benign_blocked:
                self._counters['benign_blocked'] += 1
            if event.pii_redactions:
                self._counters['pii_redactions'] += event.pii_redactions
            if event.pii_residual:
                self._counters['pii_residual'] += event.pii_residual
            self._counters[f'decision_{event.decision}'] += 1
            if event.escalation_latency_ms is not None:
                self._latency_samples.append(event.escalation_latency_ms)
            if event.drift_alert:
                self._drift_alerts += 1
                if event.drift_true:
                    self._drift_true += 1

    # --- Internal -------------------------------------------------------------------
    def _prune(self, now: float) -> None:
        cutoff = now - self.window_seconds
        while self._events and self._events[0].ts < cutoff:
            self._events.popleft()

    # --- Computations ----------------------------------------------------------------
    def _calc_rate(self, numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return (numerator / denominator) * 100.0

    def _window_snapshot(self) -> dict[str, Any]:
        evs = list(self._events)
        total = len(evs)
        harmful = sum(1 for e in evs if e.harmful_passed)
        benign_blocked = sum(1 for e in evs if e.benign_blocked)
        total_harmful = harmful  # assuming labeling included
        total_benign = sum(1 for e in evs if not e.harmful_passed)
        redactions = sum(e.pii_redactions for e in evs)
        residual = sum(e.pii_residual for e in evs)
        decisions = defaultdict(int)
        for e in evs:
            decisions[e.decision] += 1
        avg_escalation_latency = (sum(self._latency_samples) / len(self._latency_samples)) if self._latency_samples else 0.0
        drift_precision = (self._drift_true / self._drift_alerts) if self._drift_alerts else 0.0
        return {
            'window_events': total,
            'safety_fn_rate_pct': self._calc_rate(harmful, total_harmful) if total_harmful else 0.0,
            'safety_fp_rate_pct': self._calc_rate(benign_blocked, total_benign) if total_benign else 0.0,
            'pii_redactions': redactions,
            'pii_residual': residual,
            'redaction_leakage_rate_pct': self._calc_rate(residual, redactions + residual) if (redactions + residual) else 0.0,
            'decision_breakdown': dict(decisions),
            'avg_escalation_latency_ms': avg_escalation_latency,
            'drift_alert_precision_pct': drift_precision * 100.0,
        }

    # --- Public API -----------------------------------------------------------------
    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                'window': self._window_snapshot(),
                'cumulative': dict(self._counters),
                'window_seconds': self.window_seconds,
            }

    def get_metric(self, path: str) -> float | None:
        snap = self.snapshot()
        parts = path.split('.')
        cur: Any = snap
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return None
        return cur if isinstance(cur, int | float) else None

# --- Minimal Export Hook --------------------------------------------------------------

class GuardianMetricsRegistry:
    """Singleton-style accessor for global guardian metrics."""
    _instance: GuardianMetricsRegistry | None = None
    _lock = threading.Lock()

    def __init__(self):
        self.metrics = GuardianMetrics()

    @classmethod
    def instance(cls) -> GuardianMetricsRegistry:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def record(self, **event_kwargs) -> None:
        event = GuardianEvent(ts=time.time(), **event_kwargs)
        self.metrics.record_event(event)

    def snapshot(self) -> dict[str, Any]:
        return self.metrics.snapshot()

    def reset(self) -> None:
        """Reset all collected guardian metrics (testing / re-init).

        NOTE: Intended for controlled scenarios (unit tests or explicit
        reinitialization). Avoid calling in production runtime to prevent
        loss of observability continuity.
        """
        with self.metrics._lock:  # type: ignore[attr-defined]
            self.metrics._events.clear()
            self.metrics._counters.clear()  # type: ignore[attr-defined]
            self.metrics._latency_samples.clear()  # type: ignore[attr-defined]
            self.metrics._drift_alerts = 0  # type: ignore[attr-defined]
            self.metrics._drift_true = 0  # type: ignore[attr-defined]

# Convenience module-level shortcuts
record_guardian_event = GuardianMetricsRegistry.instance().record
get_guardian_metrics_snapshot = GuardianMetricsRegistry.instance().snapshot
reset_guardian_metrics = GuardianMetricsRegistry.instance().reset

__all__ = [
    'GuardianEvent',
    'GuardianMetrics',
    'GuardianMetricsRegistry',
    'get_guardian_metrics_snapshot',
    'record_guardian_event',
    'reset_guardian_metrics'
]
