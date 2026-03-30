r"""
Run ImpressionCore documentation checks locally or in CI.
- Standardizes headers/IDS notices
- Applies conservative markdown lint fixes
- Writes reports under docs/reports

Usage (Windows PowerShell):
  # From repo root
  .\.venv310\Scripts\python.exe src/dev_tools/precommit/run_doc_checks.py

Exit codes:
  0 on success
  1 on failure
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = REPO_ROOT / "docs"
REPORTS_DIR = DOCS_DIR / "reports"
PYTHON_EXE = REPO_ROOT / ".venv310" / "Scripts" / "python.exe"


def fmt_now() -> str:
    # Month Day, Year HH:MM:SS AM/PM
    return datetime.now().strftime("%B %-d, %Y %I:%M:%S %p") if sys.platform != "win32" else datetime.now().strftime("%B %#d, %Y %I:%M:%S %p")


def ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str]) -> int:
    print(f"Running: {' '.join(str(c) for c in cmd)}")
    completed = subprocess.run(cmd, cwd=REPO_ROOT)
    return completed.returncode


def main() -> int:
    ensure_reports_dir()

    if not DOCS_DIR.exists():
        print("docs/ directory not found. Nothing to do.")
        return 0

    python = str(PYTHON_EXE if PYTHON_EXE.exists() else shutil.which("python") or "python")

    # 1) Header standardization
    hdr_script = REPO_ROOT / "src" / "dev_tools" / "standardize_doc_headers.py"
    if hdr_script.exists():
        rc = run([python, str(hdr_script)])
        if rc != 0:
            print("Header standardization failed.")
            return 1
    else:
        print("standardize_doc_headers.py not found; skipping header standardization.")

    # 2) Conservative markdown lint fix
    lint_script = REPO_ROOT / "src" / "dev_tools" / "markdown_lint_fix.py"
    if lint_script.exists():
        rc = run([python, str(lint_script), "--path", str(DOCS_DIR), "--report", str(REPORTS_DIR)])
        if rc != 0:
            print("Markdown lint fix failed.")
            return 1
    else:
        print("markdown_lint_fix.py not found; skipping markdown lint fixes.")

    print(f"Doc checks complete at {fmt_now()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
