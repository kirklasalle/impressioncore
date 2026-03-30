"""Entry point for running all evaluation suites.

Usage:
    python -m evaluation              # discover + run_all
    python -m evaluation --list       # list discovered suite names
    python -m evaluation --select b3_placeholder
"""
from __future__ import annotations

import argparse
import json

from . import runner


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - thin wrapper
    """Evaluation module entrypoint.

    Args:
        argv: Optional argument vector for testability. If None, sys.argv[1:].
    Returns:
        int: Process exit code (0 success, non-zero on failure)
    """
    parser = argparse.ArgumentParser(description="Unified evaluation executor")
    parser.add_argument('--list', action='store_true', help='List discovered evaluation suite names')
    parser.add_argument('--select', nargs='*', help='Run only specified suite names')
    parser.add_argument('--json', action='store_true', help='Emit JSON output')
    args = parser.parse_args(argv)

    try:
        runner.load_legacy_suites()
        names = runner.discover()
        if args.list:
            for n in names:
                print(n)
            return 0
        results = runner.run_selected(args.select) if args.select else runner.run_all()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for k, v in results.items():
                print(f"[{k}] {v}")
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(f"Evaluation execution failed: {exc}")
        return 1


if __name__ == '__main__':  # pragma: no cover
    main()
