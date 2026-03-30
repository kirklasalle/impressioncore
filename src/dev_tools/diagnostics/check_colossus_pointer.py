"""Utility to validate the active Colossus checkpoint pointer.

Run this after updating checkpoint pointers to ensure downstream tooling
can resolve and load the distilled Colossus model.
"""
from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

# Ensure the project root is on the import path when invoked as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

POINTER_RELATIVE_PATH = Path("src/core/config/colossus_checkpoint.pointer")

from src.integrator.colossus_model import Colossus, ColossusConfig


def main() -> None:
    console = Console()
    pointer_path = PROJECT_ROOT / POINTER_RELATIVE_PATH

    if not pointer_path.is_file():
        raise SystemExit(f"Pointer file missing: {pointer_path}")

    target = pointer_path.read_text(encoding="utf-8").strip()
    if not target:
        raise SystemExit(f"Pointer file is empty: {pointer_path}")

    target_path = Path(target)
    checkpoint_path = target_path if target_path.is_absolute() else (PROJECT_ROOT / target_path).resolve()
    if not checkpoint_path.is_file():
        raise SystemExit(
            f"Checkpoint file does not exist: {checkpoint_path}"
        )

    config = ColossusConfig(checkpoint_path=checkpoint_path, device="cpu")
    model = Colossus.load(config)

    table = Table(title="Colossus Checkpoint Validation", show_header=True)
    table.add_column("Field", justify="left")
    table.add_column("Value", justify="left")

    table.add_row("Pointer file", str(pointer_path))
    table.add_row("Resolved checkpoint", str(checkpoint_path))
    table.add_row("Vector dimension", str(config.vector_dim))
    table.add_row("Model device", str(config.device))
    table.add_row("Use learned heads", str(model.use_learned_heads))
    table.add_row("Learned mix ratio", f"{model.learned_mix_ratio:.6f}")
    table.add_row(
        "Vector projector layers",
        ", ".join(layer.__class__.__name__ for layer in model.vector_projector),
    )
    table.add_row(
        "Confidence head layers",
        ", ".join(layer.__class__.__name__ for layer in model.confidence_head),
    )

    console.print(table)


if __name__ == "__main__":  # pragma: no cover
    main()
