"""
B3 pipeline orchestrator: runs Phase 0→5 in sequence or by selection.

Currently stubs out phases 1–3; extend to phases 4–5.
"""
from __future__ import annotations

import argparse

try:
    from .pipelines.multimodal_alignment import AlignmentConfig, run_alignment
    from .pipelines.kd_sft_curriculum import KDConfig, run_kd_sft
    from .pipelines.offline_pref_opt import PrefOptConfig, run_offline_pref_opt
    from .config_loader import load_all, from_section
except Exception:  # pragma: no cover - script mode fallback
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from pipelines.multimodal_alignment import AlignmentConfig, run_alignment
    from pipelines.kd_sft_curriculum import KDConfig, run_kd_sft
    from pipelines.offline_pref_opt import PrefOptConfig, run_offline_pref_opt
    from config_loader import load_all, from_section


PHASES = {
    "1_alignment": (AlignmentConfig, run_alignment),
    "2_kd_sft": (KDConfig, run_kd_sft),
    "3_pref_opt": (PrefOptConfig, run_offline_pref_opt),
}


def main():
    ap = argparse.ArgumentParser(description="Orchestrate B3 training pipeline")
    ap.add_argument("phase", choices=PHASES.keys(), help="Which phase to run")
    ap.add_argument("--config", default="src/config/b3_training.yaml", help="Path to YAML config")
    args = ap.parse_args()

    cfg_cls, fn = PHASES[args.phase]
    # Load YAML and construct config matching the phase
    data = load_all(args.config)
    section = {
        "1_alignment": "alignment",
        "2_kd_sft": "kd_sft",
        "3_pref_opt": "pref_opt",
    }[args.phase]
    cfg = from_section(data, section, cfg_cls)
    fn(cfg)


if __name__ == "__main__":
    main()
