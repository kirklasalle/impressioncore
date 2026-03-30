"""Root script guard and relocation plan validator.

Purpose:
 1. Enforce that no new unapproved Python modules reside directly under `src/`.
 2. Allow temporary deprecation shims that are recorded in `core/management/relocation_plan.md` with a status containing 'shim phase'.
 3. Detect duplicate relocation plan entries for the same original file.
 4. Check *shim expiry* based on filesystem modified time (default 30‑day grace) to prompt removal of stale shims.
 5. Provide JSON machine‑readable reporting for CI aggregation / annotations.

CLI Examples:
    # Strict validation with duplicates + JSON output
    python -m dev_tools.ci.root_script_guard --fail-on-duplicates --json-report guard-report.json

    # Enforce expiry with custom grace period
    python -m dev_tools.ci.root_script_guard --enforce-expired --shim-grace-days 25

Exit codes:
    0 = OK
    1 = Violations detected (unauthorized root scripts, duplicates, or expired shims when enforced)

Design notes:
 - Relocation plan parsing: scan markdown table rows beginning with '|'.
 - Status field inspected for 'shim phase' (case-insensitive) to whitelist root shim files temporarily.
 - Expiry: last modified time of root shim file; age > grace triggers warning or violation (if --enforce-expired).
 - ALLOWED_ALWAYS enumerates permanent legitimate root files.
"""
from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
RELOCATION_PLAN = SRC_ROOT / "core" / "management" / "relocation_plan.md"

ALLOWED_ALWAYS: set[str] = {
    "__init__.py",
    "main.py",
    "legacy_imports.py",
}

@dataclass
class RelocationEntry:
    original: str
    target_package: str
    new_path: str
    status: str


def parse_relocation_plan(path: Path) -> list[RelocationEntry]:
    if not path.exists():
        return []
    entries: list[RelocationEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]  # drop leading/trailing empty from split
        if len(parts) != 4:
            continue
        original, target_pkg, new_path, status = parts
        if not original.endswith(".py"):
            continue
        entries.append(RelocationEntry(original, target_pkg, new_path, status))
    return entries


def collect_root_python_files(src_root: Path) -> list[str]:
    return sorted(p.name for p in src_root.glob("*.py"))


CREATED_DATE_REGEX = re.compile(r"created\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", re.IGNORECASE)


def _parse_creation_date(status: str) -> datetime | None:
    """Extract creation date from status text (Month Day, Year)."""
    m = CREATED_DATE_REGEX.search(status)
    if not m:
        return None
    raw = m.group(1)
    try:
        return datetime.strptime(raw, "%B %d, %Y").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def determine_allowed_shims(entries: Iterable[RelocationEntry]) -> set[str]:
    return {e.original for e in entries if "shim phase" in e.status.lower()}


def build_shim_creation_map(entries: Iterable[RelocationEntry]) -> dict[str, datetime | None]:
    m: dict[str, datetime | None] = {}
    for e in entries:
        if "shim phase" in e.status.lower():
            m[e.original] = _parse_creation_date(e.status)
    return m


def find_duplicates(entries: Iterable[RelocationEntry]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for e in entries:
        counts[e.original] = counts.get(e.original, 0) + 1
    return {k: v for k, v in counts.items() if v > 1}


def _compute_expiry(
    allowed_shims: set[str],
    creation_map: dict[str, datetime | None],
    grace_days: int,
    enforce_expired: bool,
) -> tuple[list[str], list[str], dict[str, int]]:
    """Return (warnings, expiry_violations, age_map) for allowed shim files.

    Age is computed from explicit creation date if present; otherwise file mtime fallback.
    A shim is *expired* when its age in whole days strictly exceeds ``grace_days``.
    """
    warnings: list[str] = []
    violations: list[str] = []
    age_map: dict[str, int] = {}
    now_dt = datetime.now(timezone.utc)
    for shim in sorted(allowed_shims):
        fpath = SRC_ROOT / shim
        if not fpath.exists():
            continue
        created_dt = creation_map.get(shim)
        if created_dt is None:
            # fallback to mtime
            created_dt = datetime.fromtimestamp(fpath.stat().st_mtime, tz=timezone.utc)
        age_days = (now_dt - created_dt).days
        age_map[shim] = age_days
        if age_days > grace_days:
            msg = f"Shim '{shim}' expired (age_days={age_days} > grace_days={grace_days})"
            warnings.append(msg)
            if enforce_expired:
                violations.append(
                    f"Expired shim: {shim} (age_days={age_days} > grace_days={grace_days})"
                )
    return warnings, violations, age_map


def validate_structure_detailed(
    *,
    fail_on_duplicates: bool = False,
    shim_grace_days: int = 30,
    enforce_expired: bool = False,
) -> tuple[bool, str, dict[str, Any]]:
    """Detailed validation returning meta suitable for JSON reporting.

    Returns: (ok, message, meta)
    meta keys: entries, duplicates, allowed_shims, root_files, violations, expiry_warnings, timestamp
    """
    entries = parse_relocation_plan(RELOCATION_PLAN)
    duplicates = find_duplicates(entries)
    allowed_shims = determine_allowed_shims(entries)
    creation_map = build_shim_creation_map(entries)
    root_files = collect_root_python_files(SRC_ROOT)

    violations: list[str] = []
    for fname in root_files:
        if fname in ALLOWED_ALWAYS:
            continue
        if fname in allowed_shims:
            continue
        if any(e.original == fname for e in entries):
            violations.append(
                f"Root file '{fname}' present but status not shim phase; should be removed or marked."
            )
        else:
            violations.append(f"Unauthorized root Python file: {fname}")

    if fail_on_duplicates and duplicates:
        for dup, count in duplicates.items():
            violations.append(f"Duplicate relocation plan entry for '{dup}' (count={count})")

    expiry_warnings, expiry_violations, age_map = _compute_expiry(
        allowed_shims, creation_map, shim_grace_days, enforce_expired
    )
    violations.extend(expiry_violations)

    ok = not violations
    message = "Structure OK" if ok else "\n".join(violations)
    meta: dict[str, Any] = {
        "root_files": root_files,
        "allowed_shims": sorted(allowed_shims),
        "duplicates": duplicates,
        "violations": violations,
        "expiry_warnings": expiry_warnings,
        "shim_age_days": age_map,
        "removal_suggestions": [
            f"git rm src/{shim} # expired shim" for shim in sorted(age_map) if age_map[shim] > shim_grace_days
        ],
    "timestamp": datetime.now(timezone.utc).isoformat(),
        "grace_days": shim_grace_days,
        "enforce_expired": enforce_expired,
    }
    return ok, message, meta


def validate_structure(fail_on_duplicates: bool = False) -> tuple[bool, str]:
    # Backwards compatible wrapper for existing tests.
    ok, message, _ = validate_structure_detailed(
        fail_on_duplicates=fail_on_duplicates
    )
    return ok, message


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate root script structure and relocation plan")
    parser.add_argument("--fail-on-duplicates", action="store_true", help="Treat duplicate relocation entries as errors")
    parser.add_argument("--json-report", nargs="?", const="-", help="Write JSON report to file (or stdout if '-')")
    parser.add_argument("--shim-grace-days", type=int, default=30, help="Grace period in days before shim expiry warnings")
    parser.add_argument("--enforce-expired", action="store_true", help="Treat expired shims as violations (fail build)")
    parser.add_argument("--badge-json", nargs="?", const="badge.json", help="Emit a shields.io compatible badge JSON (default badge.json)")
    parser.add_argument("--upcoming-threshold", type=int, default=5, help="Days before expiry to flag upcoming shim expiry in JSON")
    args = parser.parse_args(argv)

    ok, message, meta = validate_structure_detailed(
        fail_on_duplicates=args.fail_on_duplicates,
        shim_grace_days=args.shim_grace_days,
        enforce_expired=args.enforce_expired,
    )

    # Derive upcoming expirations (age within grace but within threshold window)
    upcoming: list[str] = []
    for shim, age in meta.get("shim_age_days", {}).items():
        remaining = meta["grace_days"] - age
        if 0 <= remaining <= args.upcoming_threshold:
            upcoming.append(f"{shim} (in {remaining}d)")
    meta["upcoming_expirations"] = upcoming

    # Always print human message
    print(message)

    if args.json_report is not None:
        report = {
            "ok": ok,
            "message": message,
            **meta,
        }
        serialized = json.dumps(report, indent=2, sort_keys=True)
        if args.json_report == "-":
            print(serialized)
        else:
            Path(args.json_report).write_text(serialized, encoding="utf-8")
            print(f"JSON report written to {args.json_report}")

    if args.badge_json is not None:
        badge_color = "brightgreen" if ok else "red"
        expired_count = sum(1 for a in meta.get("shim_age_days", {}).values() if a > meta["grace_days"])
        label = "structure"
        message_badge = "ok" if ok else f"violations:{len(meta['violations'])}"
        if expired_count:
            message_badge += f"|expired:{expired_count}"
        badge = {
            "schemaVersion": 1,
            "label": label,
            "message": message_badge,
            "color": badge_color,
        }
        Path(args.badge_json).write_text(json.dumps(badge, indent=2), encoding="utf-8")
        print(f"Badge JSON written to {args.badge_json}")

    return 0 if ok else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
