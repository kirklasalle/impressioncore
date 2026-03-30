"""
Phase 3: Offline preference optimization (DPO/ORPO) skeleton.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PrefOptConfig:
    lr: float = 5e-5
    micro_batch: int = 1
    accum_steps: int = 32
    epochs: int = 1


def run_offline_pref_opt(config: PrefOptConfig) -> None:
    # NOTE: implement pair loader and DPO/ORPO objective (pending)
    print("[offline_pref_opt] Starting offline preference optimization with config:", config)
    print("[offline_pref_opt] NOTE: This is a scaffold. Implement training logic.")
