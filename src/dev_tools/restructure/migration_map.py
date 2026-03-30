"""Migration Map Skeleton for Source Tree Refactor.

Created: August 23, 2025
Status: Draft (No destructive operations yet)

This module declares the canonical mapping from CURRENT -> TARGET paths for the planned
directory reorganization. It intentionally does NOT execute moves unless explicitly invoked.

Usage (dry run):
    python -m dev_tools.restructure.migration_map --dry-run

Planned Execution Flow (Phase 0 only):
1. Validate all source paths exist.
2. Warn if destination path already exists (to avoid overwrites).
3. Emit ordered operations list (JSON / table) for review.

Later Phases:
 - Implement `perform_moves()` using *git-aware* moves (preferred run outside this script)
 - Add hash & size verification after each move
 - Generate rollback script from captured pre-move manifest

NOTE: Do not import heavy project modules here; keep this script side-effect free.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../src

# ---- CORE MAPPING ---------------------------------------------------------
# Each entry: old_relative_path -> new_relative_path
MIGRATION_MAP: dict[str, str] = {
    # Evaluation consolidation
    "eval": "evaluation",  # Merge into unified evaluation package
    "benchmarks": "evaluation/benchmarks",  # Benchmarks become a subfolder

    # Model consolidation (will become subpackages under model/)
    "models": "model/architectures",  # Core model architectures
    "modules": "model/modules",       # Reusable functional modules
    "tokenization": "model/tokenization",
    "brainsim": "model/brainsim",     # Active brainsim code (if retained)

    # Training subdomains
    "distillation": "training/distillation",
    "curriculum": "training/curriculum",

    # Data pipeline formation
    # (individual script files will be categorized later)

    # Deployment & ops
    "deployment": "ops/deployment",
    "management": "ops/management",

    # Phase 2 (models/inference consolidation) - planned, not yet executed
    # Duplicate B3 architecture copies will be archived under archive/models
    # Actual canonical file remains in place until final switch.
}

# Individual files at src root to relocate (pattern-based soon)
FILE_RELOCATIONS: dict[str, str] = {
    "metrics.py": "evaluation/metrics/__root_metrics.py",  # Will be split/refactored
    "production_inference.py": "inference/production/production_inference.py",
    "filters.py": "core/utils/filters.py",
    # Dataset / data build artifacts
    "build_kd_dataset.py": "data_pipeline/dataset_build/build_kd_dataset.py",
    "build_openai_faiss_index.py": "data_pipeline/dataset_build/build_openai_faiss_index.py",
    "chunk_large_text.py": "data_pipeline/chunking/chunk_large_text.py",
    "convert_teacher_outputs.py": "data_pipeline/dataset_build/convert_teacher_outputs.py",
    "generate_openai_embeddings.py": "data_pipeline/dataset_build/generate_openai_embeddings.py",
    "ollama_generate.py": "scripts/ollama_generate.py",  # CLI style
    "reorganize_media_to_raw_pipeline.py": "data_pipeline/ingestion/reorganize_media_to_raw_pipeline.py",
    # Phase 2 archival COMPLETE (entries removed from source): duplicates moved to archive/models/b3/
}

# Artifacts (non-code) to move under analysis/
ANALYSIS_ARTIFACT_PATTERNS: tuple[str, ...] = (
    "*.csv", "*_structure.txt", "F_DRIVE_*.txt", "*_analysis.txt"
)

# ---------------------------------------------------------------------------

def _path_exists(rel: str) -> bool:
    return (PROJECT_ROOT / rel).exists()


def collect_actions() -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for src_rel, dst_rel in MIGRATION_MAP.items():
        if _path_exists(src_rel):
            actions.append({
                "type": "dir_move",
                "source": src_rel,
                "target": dst_rel,
            })
    for file_rel, dst_rel in FILE_RELOCATIONS.items():
        if _path_exists(file_rel):
            actions.append({
                "type": "file_move",
                "source": file_rel,
                "target": dst_rel,
            })
    return actions


def dry_run(verbose: bool = False) -> None:
    actions = collect_actions()
    summary = {
        "total_actions": len(actions),
        "directories": sum(1 for a in actions if a["type"] == "dir_move"),
        "files": sum(1 for a in actions if a["type"] == "file_move"),
        "actions": actions,
    }
    print(json.dumps(summary, indent=2))
    if verbose:
        print("\nLegend: dir_move = directory relocation, file_move = single file relocation")


def ensure_skeleton() -> list[str]:
    """Create destination skeleton directories if missing (Phase 0 only).

    Returns list of created directories (relative paths).
    """
    created: list[str] = []
    targets = set()
    for dst in MIGRATION_MAP.values():
        targets.add(dst)
    for dst in FILE_RELOCATIONS.values():
        dir_name = os.path.dirname(dst)
        if dir_name:
            targets.add(dir_name)
    for t in sorted(targets):
        if not t or t == ".":
            continue
        full = PROJECT_ROOT / t
        if not full.exists():
            full.mkdir(parents=True, exist_ok=True)
            created.append(t)
            # Add minimal __init__.py for packages
            init_file = full / "__init__.py"
            if not init_file.exists() and "analysis" not in t:
                init_file.write_text("""# Placeholder package for migration phase.\n""")
    return created


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ImpressionCore source tree migration skeleton")
    p.add_argument("--dry-run", action="store_true", help="Output planned actions as JSON and exit")
    p.add_argument("--create-skeleton", action="store_true", help="Create destination directory skeleton only")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.create_skeleton:
        created = ensure_skeleton()
        print(json.dumps({"created_dirs": created}, indent=2))
    if args.dry_run:
        dry_run(verbose=args.verbose)
    if not args.dry_run and not args.create_skeleton:
        print("No action specified. Use --dry-run or --create-skeleton.")


if __name__ == "__main__":  # pragma: no cover
    main()
