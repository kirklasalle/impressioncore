"""Guardian KPI Threshold Loader

Created: August 22, 2025
Updated: August 22, 2025
Author: GitHub Copilot
Tags: #guardian_stack #thresholds #kpi #monitoring

Purpose:
    Provide runtime-accessible threshold configuration aligned with KPI Registry.

Features:
    - JSON file loader with schema validation (minimal)
    - Cached in-memory structure with reload()
    - Access helpers (get(target_path, default))

Assumptions:
    - External process keeps JSON in sync with KPI registry docs.

"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

_DEFAULT_THRESHOLDS = {
    "safety_fn_rate_pct": 1.0,
    "safety_fp_rate_pct": 3.0,
    "redaction_leakage_rate_pct": 0.5,
    "drift_alert_precision_pct": 85.0,
    "avg_escalation_latency_ms": 250.0,
}

class GuardianThresholds:
    def __init__(self, path: str | None = None):
        self.path = Path(path) if path else None
        self._data = dict(_DEFAULT_THRESHOLDS)
        self._lock = threading.Lock()
        if self.path and self.path.exists():
            self._load()

    def _load(self) -> None:
        try:
            raw = json.loads(self.path.read_text())
            if not isinstance(raw, dict):
                return
            with self._lock:
                for k, v in raw.items():
                    if isinstance(v, int | float):
                        self._data[k] = float(v)
        except Exception:
            # Fail safe: keep defaults
            pass

    def reload(self) -> None:
        if self.path and self.path.exists():
            self._load()

    def get(self, key: str, default: float | None = None) -> float | None:
        with self._lock:
            return self._data.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._data)

# Singleton accessor
_thresholds_instance: GuardianThresholds | None = None
_thresholds_lock = threading.Lock()

def guardian_thresholds(path: str | None = None) -> GuardianThresholds:
    global _thresholds_instance
    with _thresholds_lock:
        if _thresholds_instance is None:
            _thresholds_instance = GuardianThresholds(path)
        return _thresholds_instance

__all__ = ["GuardianThresholds", "guardian_thresholds"]
