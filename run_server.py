"""
ImpressionCore — Root Server Entry Point Shim
================================================

This file delegates to the canonical, actively-maintained implementation at
``src/services/sse/run_server.py``. It exists so that the documented user
workflow (``python run_server.py`` from the repo root — see
docs/user_guide/complete_user_guide.md and others) continues to work
without duplicating the virtualenv/dependency/structure checks in two
places.

**Cleanup note (2026-07-01):** The relocated canonical copy at
``src/services/sse/run_server.py`` had two real path-resolution bugs
(the exact issue flagged in the June 30, 2026 audit) that were fixed
alongside this shim:
1. Its ``project_root``/``src_path`` computation only walked up 2 directory
   levels instead of 3, landing on ``src/`` instead of the true repo root.
2. It imported a non-existent ``server_new.run_server`` symbol instead of
   the real ``server.create_app`` factory.
Both bugs are now fixed in the canonical module.

Usage:
------
    python run_server.py

This performs all environment checks and starts the web server on
http://localhost:5000/ by default.
"""

import sys
from pathlib import Path

# Ensure the repo root is on sys.path so ``src.*`` imports resolve.
_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.services.sse.run_server import main  # noqa: E402

if __name__ == "__main__":
    main()