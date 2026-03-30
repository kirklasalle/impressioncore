"""
Temp path utilities for ImpressionCore with strict no-C: policy.

Functions:
- get_repo_root(): Path
- get_temp_dir(): Path to repo-local backups/tmp or IMPCORE_TMP_DIR if set
- set_process_temp_env(): set TEMP/TMP/TMPDIR for current process
"""
from __future__ import annotations

import os
from pathlib import Path


def get_repo_root() -> Path:
    here = Path(__file__).resolve()
    # src/core/utils/temp_paths.py -> src -> repo root
    return here.parents[3]


def _is_c_drive(p: Path) -> bool:
    try:
        drive = p.drive
        return drive.upper().startswith("C:")
    except Exception:
        return False


def get_temp_dir() -> Path:
    override = os.environ.get("IMPRESSIONCORE_TMP_DIR") or os.environ.get("IMPCORE_TMP_DIR")
    if override:
        p = Path(override).resolve()
        if _is_c_drive(p):
            raise RuntimeError("C: drive usage is prohibited for temp; set IMPCORE_TMP_DIR to a non-C: path")
        p.mkdir(parents=True, exist_ok=True)
        return p
    root = get_repo_root()
    tmp = (root / "backups" / "tmp").resolve()
    if _is_c_drive(tmp):
        raise RuntimeError("Computed tmp path is on C: drive, which is prohibited.")
    tmp.mkdir(parents=True, exist_ok=True)
    return tmp


def set_process_temp_env(path: Path | None = None) -> Path:
    p = path or get_temp_dir()
    os.environ["TEMP"] = str(p)
    os.environ["TMP"] = str(p)
    os.environ["TMPDIR"] = str(p)
    return p
