# Shim Lifecycle & Removal Procedure

**Created:** August 24, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #documentation #governance #refactoring #shims #maintenance  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

This document defines the authoritative lifecycle for temporary relocation shims placed in the `src/` root during the structural cleanup and re‑organization initiative.

## Purpose

Relocation shims provide a short grace period after moving a legacy root‑level module into its canonical package so that:

1. Import paths in in‑flight branches do not break immediately.
2. Developers receive a clear DeprecationWarning pointing to the new location.
3. CI can enforce eventual removal to keep the `src/` root clean (permanent directory governance).

## Shim Definition

A shim file is a minimal root `src/<name>.py` module that:

- Emits a `DeprecationWarning` on import.
- Imports (and/or re‑exports) the new canonical implementation.
- Is recorded in `src/core/management/relocation_plan.md` with a status containing: `done (shim phase; created Month Day, Year)`

Example status line: `done (shim phase; created August 24, 2025)`

## Grace Period

Default grace period: **30 days** (configurable via repository variable `STRUCTURE_SHIM_GRACE_DAYS`).

During the grace period:

- CI allows the shim (counts it but not a violation).
- Upcoming expirations (within N days threshold, default 5) are surfaced in reports & PR comments.

After grace (> N days):

- The shim is marked expired.
- CI fails (`--enforce-expired` active) to prevent further merges introducing new debt.
- Auto‑removal PR workflow may open a branch proposing removal.

## Lifecycle States

1. `shim phase` (active grace) – present in root, status includes creation date.
2. `expired` (detected by guard) – not a separate status string; guard calculates from creation date.
3. `retired` (removed) – status updated to: `retired (removed Month Day, Year)` after PR merges.

## Removal Procedure (Manual)

1. Identify expired shims via guard PR comment / badge / weekly reminder.
2. Remove the root shim file(s): `git rm src/<shim>.py`.
3. Edit `relocation_plan.md`: replace status cell text from `done (shim phase; created ...)` to `retired (removed Month Day, Year)`.
4. Commit with message: `chore: retire expired shim <name>`.
5. Open PR; CI guard will pass since file no longer present.

## Automated Removal PR

If enabled, the `shim-auto-removal` workflow will:

1. Run guard (non‑enforcing) on `push` to `main`.
2. Parse `removal_suggestions` from `guard_report.json`.
3. Create branch `chore/remove-expired-shims-YYYYMMDD`.
4. Delete each expired shim file.
5. Update each line in relocation plan to a `retired (removed Month Day, Year)` status.
6. Commit, push, and open a PR referencing any existing “Expired shims removal” issue.

## CI Enforcement Summary

| Aspect | Mechanism |
|--------|-----------|
| Duplicate entries | Guard fails if duplicates found (with `--fail-on-duplicates`) |
| Unauthorized root scripts | Guard fails immediately |
| Expired shims | Guard fails with `--enforce-expired` |
| Upcoming expirations | Reported (not failing) within threshold window |
| Weekly reminder | Scheduled workflow surfaces upcoming & expired list |

## Configuration

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `STRUCTURE_SHIM_GRACE_DAYS` | Repository Variable | 30 | Override grace period for expiry |
| `--upcoming-threshold` | CLI flag | 5 | Days before expiry to flag upcoming |

## Rationale

This disciplined time‑boxed shim strategy prevents indefinite drift while providing a safe migration window, aligning with the Permanent Directory Governance rules and file integrity mandates.

## Future Enhancements (Optional)

- Per‑shim custom grace tagging in relocation plan.
- Auto‑generated CHANGELOG entries on retirement.
- Dashboard aggregation of lifecycle metrics.

---
Document maintained under structural governance; update timestamps using mandated date format (`Month Day, Year`).