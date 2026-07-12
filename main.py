"""
ImpressionCore — Root Entry Point
==================================

This file delegates to the canonical entry point at ``src/main.py``.
The ``pyproject.toml`` ``[project.scripts]`` entry already points to
``src.main:main``; this shim exists so that ``python main.py`` from the
repo root also works.

**Audit note (June 2026):** The previous placeholder ImpressionCoreAPI
that returned ``[1,2,3,4,5]`` has been removed. All real logic now lives
exclusively in ``src/main.py``.
"""

import sys
from pathlib import Path

# Ensure the repo root is on sys.path so ``src.*`` imports resolve.
_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.main import main  # noqa: E402

if __name__ == "__main__":
    main()
