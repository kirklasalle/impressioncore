#!/usr/bin/env python
"""
ImpressionCore — Root CLI Build Automation Shim
=================================================

This file delegates to the canonical, actively-maintained implementation at
``src/dev_tools/automation/build_cli_automation.py``. It exists so that the
documented user workflow (``python build_cli_automation.py`` from the repo
root — see docs/user_guide/impressioncore_b1_walkthrough.md) continues to
work without duplicating logic in two places.

**Cleanup note (2026-07-01):** The previous root copy of this script was a
stale, less-developed duplicate (115 lines, no System Oversight/event-log
integration) that had drifted from the canonical version under
``src/dev_tools/automation/`` (259 lines). This shim replaces it.
"""

import sys
from pathlib import Path

# Ensure the repo root is on sys.path so ``src.*`` imports resolve.
_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.dev_tools.automation.build_cli_automation import main  # noqa: E402

if __name__ == "__main__":
    main()
