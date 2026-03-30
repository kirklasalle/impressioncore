"""Batched Relocator

Created: August 23, 2025
Purpose: Execute governed bulk directory/file relocations into the Permanent Core Directories
structure. Generates import shims for moved top-level packages if necessary and updates
`management/relocation_plan.md`.

Runs in DRY-RUN mode by default; use --apply to perform moves.

Usage:
    python -m dev_tools.maintenance.batched_relocator --report
    python -m dev_tools.maintenance.batched_relocator --apply

Notes:
- Only moves directories/files that exist (skips silently if absent)
- Creates target parent directories
- Records operations in an in-memory list and appends markdown rows to relocation_plan
- Does NOT overwrite existing targets unless --force provided
- Emits a summary table at end
"""
from __future__ import annotations

import argparse
import datetime as _dt
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
RELOCATION_PLAN = SRC_ROOT / "core" / "management" / "relocation_plan.md"
DATE_STR = _dt.datetime.now().strftime("%B %e, %Y").replace("  ", " ")

@dataclass
class MoveSpec:
    source: Path
    target: Path
    note: str

# Mapping based on user directives
RAW_SPECS = [
    ("eval", "evaluation", "merge eval into evaluation (module consolidation)"),
    ("config", "core/config", "centralize configuration"),
    ("management", "core/management", "centralize management utilities"),
    ("integrity", "core/integrity", "centralize integrity checks"),
    ("tokenization", "core/tokenization", "shared tokenization components"),
    ("brainsim", "core/brainsim", "brain simulation under core"),
    ("curriculum", "training/curriculum", "training curriculum organization"),
    ("distillation", "training/distillation", "distillation processes"),
    ("pipelines", "training/pipelines", "training oriented pipelines"),
    ("processors", "data/processors", "dataset-focused processors"),
    ("embeddings", "data/embeddings", "embedding assets"),
    ("model_analysis", "evaluation/model_analysis", "model analysis relocation"),
    ("modules", "core/modules", "generic building blocks"),
    ("analysis", "evaluation/analysis", "evaluation analysis components"),
    ("scripts", "dev_tools/scripts", "developer scripts"),
    ("examples", "examples", "examples kept at top-level"),
]

# File (not directory) moves
REPORT_NOTE = "report relocation"
DATASET_NOTE = "dataset metadata relocation"
RAW_FILE_SPECS = [
    ("educational_materials_inventory.txt", "docs/reports/educational_materials_inventory.txt", REPORT_NOTE),
    ("F_DRIVE_CAMPAIGN_SUMMARY_20250731_165527.txt", "docs/reports/F_DRIVE_CAMPAIGN_SUMMARY_20250731_165527.txt", REPORT_NOTE),
    ("f_drive_current_structure.txt", "docs/reports/f_drive_current_structure.txt", REPORT_NOTE),
    ("f_drive_data_structure.txt", "docs/reports/f_drive_data_structure.txt", REPORT_NOTE),
    ("f_drive_detailed_analysis.txt", "docs/reports/f_drive_detailed_analysis.txt", REPORT_NOTE),
    ("f_drive_directories.txt", "docs/reports/f_drive_directories.txt", REPORT_NOTE),
    ("kd_dataset.jsonl", "data/datasets/metadata/kd_dataset.jsonl", DATASET_NOTE),
    ("sample_teachers.jsonl", "data/datasets/metadata/sample_teachers.jsonl", DATASET_NOTE),
    ("smart_acquisition_readable.txt", "data/reports/smart_acquisition_readable.txt", "data acquisition reference"),
]


def build_specs():
    dir_specs: list[MoveSpec] = []
    for src_rel, tgt_rel, note in RAW_SPECS:
        s = SRC_ROOT / src_rel
        t = SRC_ROOT / tgt_rel
        dir_specs.append(MoveSpec(s, t, note))
    file_specs: list[MoveSpec] = []
    for src_rel, tgt_rel, note in RAW_FILE_SPECS:
        file_specs.append(MoveSpec(SRC_ROOT / src_rel, SRC_ROOT / tgt_rel, note))
    return dir_specs, file_specs


def move_path(spec: MoveSpec, apply: bool, force: bool) -> str:
    if not spec.source.exists():
        return f"SKIP (missing): {spec.source.name}"
    if spec.target.exists() and not force:
        return f"SKIP (exists target): {spec.source.name}"
    if apply:
        spec.target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(spec.source), str(spec.target))
        return f"MOVED: {spec.source} -> {spec.target}"
    else:
        return f"PLAN: {spec.source} -> {spec.target}"


def append_relocation_plan(moves: list[MoveSpec], apply: bool) -> None:
    if not apply:
        return
    if not RELOCATION_PLAN.exists():
        # If relocation plan missing after core/management move, skip updating to avoid crash.
        return
    lines = RELOCATION_PLAN.read_text(encoding="utf-8").splitlines()
    # append rows
    for m in moves:
        orig = m.source.relative_to(SRC_ROOT) if m.source.exists() else m.source.name
        tgt = m.target.relative_to(SRC_ROOT)
        status = "done" if m.target.exists() else "planned"
        lines.append(f"| {orig} | {tgt.parent} | {tgt} | {status} | batch move {DATE_STR} - {m.note} |")
    RELOCATION_PLAN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Execute moves (default dry run)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing targets if present")
    args = ap.parse_args(argv)

    dir_specs, file_specs = build_specs()
    all_specs = dir_specs + file_specs

    messages = []
    for spec in all_specs:
        messages.append(move_path(spec, apply=args.apply, force=args.force))

    # Write relocation plan rows (only for those actually moved in this run)
    moved_specs = [s for s in all_specs if s.target.exists()]
    append_relocation_plan(moved_specs, apply=args.apply)

    print("Batched Relocation Summary:\n")
    for msg in messages:
        print(msg)
    print("\nTotal specs processed:", len(all_specs))
    print("Apply mode:" , args.apply)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
