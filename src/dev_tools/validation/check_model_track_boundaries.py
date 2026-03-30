import argparse
import re
from pathlib import Path


MODEL_TRACK_DIRS = [
    Path("src/core/models"),
    Path("src/training"),
    Path("src/data"),
]

DISALLOWED_IMPORT_PREFIXES = (
    "src.orchestrator",
    "src.vision",
    "src.interfaces",
)

IMPORT_RE = re.compile(r"^\s*import\s+([a-zA-Z0-9_\.]+)")
FROM_IMPORT_RE = re.compile(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+")


def _extract_import_target(line: str) -> str | None:
    import_match = IMPORT_RE.match(line)
    if import_match:
        return import_match.group(1)

    from_import_match = FROM_IMPORT_RE.match(line)
    if from_import_match:
        return from_import_match.group(1)

    return None


def _is_disallowed(module_name: str) -> bool:
    return any(module_name.startswith(prefix) for prefix in DISALLOWED_IMPORT_PREFIXES)


def run_boundary_check() -> tuple[bool, list[str]]:
    """Check model-track modules for disallowed runtime and vision imports."""
    violations: list[str] = []

    for base_dir in MODEL_TRACK_DIRS:
        if not base_dir.exists():
            continue

        for py_file in base_dir.rglob("*.py"):
            try:
                lines = py_file.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue

            for line_number, line in enumerate(lines, start=1):
                target = _extract_import_target(line)
                if target and _is_disallowed(target):
                    violations.append(
                        f"{py_file.as_posix()}:{line_number} disallowed import '{target}'"
                    )

    return len(violations) == 0, violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate model-only track boundaries by blocking imports from runtime/orchestrator/vision modules."
        )
    )
    parser.parse_args()

    ok, violations = run_boundary_check()
    if ok:
        print("Model-track boundary check passed.")
        return 0

    print("Model-track boundary check failed.")
    for violation in violations:
        print(f" - {violation}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
