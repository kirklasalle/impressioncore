"""Runtime Override Helper

Utility to atomically update the runtime overrides JSON file that the KD+SFT
training loop polls (IC_RUNTIME_OVERRIDES_PATH). This prevents partial write
corruption and provides a simple CLI interface.

Usage (PowerShell example):

  # Activate venv first if needed
  # .venv310\\Scripts\\Activate.ps1

  # Increase phase2 extra steps and adjust heel threshold
  python -m src.training.utils.runtime_override_helper \
    --overrides-path F:/models/checkpoints/kd_sft_phase/runtime_overrides.json \
    --set heel_eff_ratio=0.50 phase2_extra_steps=60

  # Disable KL mid-run (if already in or after heel)
  python -m src.training.utils.runtime_override_helper \
    --overrides-path F:/models/checkpoints/kd_sft_phase/runtime_overrides.json \
    --set phase2_disable_kl=true

Notes:
- Only keys present in KDConfig will be applied by the training script.
- Values are parsed as: int, float, bool (true/false), else string.
- Writes go to a temp file then replaced atomically.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import tempfile
from typing import Any


def parse_kv(arg: str) -> tuple[str, Any]:
    if '=' not in arg:
        raise argparse.ArgumentTypeError(f"Override must be key=value, got: {arg}")
    k, v = arg.split('=', 1)
    v_lower = v.lower()
    # Attempt typed parsing
    if v_lower in {"true", "false"}:
        val: Any = v_lower == "true"
    else:
        try:
            val = float(v) if '.' in v else int(v)
        except ValueError:
            val = v  # fallback string
    return k, val


def atomic_write_json(path: str, data: dict[str, Any]) -> None:
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix="._ovr_", suffix=".json")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, sort_keys=True)
        # Replace atomically
        os.replace(tmp_path, path)
    except Exception:
        # Best effort cleanup of temp
        with contextlib.suppress(OSError):
            os.remove(tmp_path)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Update KD runtime overrides JSON atomically.")
    parser.add_argument("--overrides-path", required=True, help="Path to runtime_overrides.json")
    parser.add_argument("--set", nargs="+", metavar="key=value", type=parse_kv, help="Key=value pairs to set")
    parser.add_argument("--unset", nargs="*", metavar="key", help="Keys to remove", default=None)
    args = parser.parse_args()

    overrides_path = args.overrides_path
    existing: dict[str, Any] = {}
    if os.path.exists(overrides_path):
        try:
            with open(overrides_path, encoding='utf-8') as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            print(f"[override-helper] WARNING: Existing file not valid JSON, starting fresh: {overrides_path}")
            existing = {}

    # Apply sets
    for k, v in (args.set or []):
        existing[k] = v
        print(f"[override-helper] Set {k} -> {v}")

    # Apply unsets
    if args.unset:
        for k in args.unset:
            if k in existing:
                existing.pop(k)
                print(f"[override-helper] Unset {k}")

    atomic_write_json(overrides_path, existing)
    print(f"[override-helper] Wrote overrides to {overrides_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
