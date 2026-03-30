# ImpressionCore Archive Index

**Created:** August 23, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #archive_index #documentation #governance #deprecation #traceability  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Central index of all archived (deprecated / superseded) source and documentation assets. Complements `DOCUMENTATION_INDEX.md` and is maintained automatically by the archive scanner.

## Purpose

1. Single authoritative list of archived files for compliance & traceability.
2. Preserve historical evolution without polluting active source tree.
3. Provide rationale & timestamp for each archive action.
4. Enable automated integrity checks (no orphan archived markers left in active tree).

## Recent Archive Moves (Most Recent First)

| Date | Original Path | Archived Path | Reason | Method |
|------|---------------|---------------|--------|--------|
| August 23, 2025 | src/training/b1_enhanced_training_executor.py | src/archive/training/b1_enhanced_training_executor.py | Superseded by B3 unified training | automated |
| August 23, 2025 | src/models/b2_multimodal/core/b2_multimodal_model.py | src/archive/models/b2_multimodal/core/b2_multimodal_model.py | Superseded by B3 architecture | automated |
| August 23, 2025 | impressioncore_b1_cli.py | src/archive/interfaces/cli/impressioncore_b1_cli.py | Legacy B1 CLI replaced | manual |

## Automatic Scanner

Implemented in `src/dev_tools/archive/archive_scanner.py`. It:

- Scans `src/` for markers: `DEPRECATED / ARCHIVED`, `Status:** Archived`, `Status: Archived`, or top-level docstring containing `Archived`.
- Ignores anything already under `src/archive/`.
- Produces a structured report and (optionally) updates this file & relocation plan.

## Data Schema

Each archive record uses:

```json
{
  "original_path": "src/path/file.py",
  "archived_path": "src/archive/path/file.py",
  "archived_on": "August 23, 2025",
  "reason": "Superseded by ...",
  "detection": "docstring|status_field|marker"
}
```

## Integrity Checks

- No active file should contain `DEPRECATED / ARCHIVED` after relocation.
- All archived moves must be reflected in: `ARCHIVE_INDEX.md` + `src/management/relocation_plan.md`.
- Scanner exit code non-zero if mismatches found.

## Maintenance Workflow

1. Run scanner dry-run: `python src/dev_tools/archive/archive_scanner.py --report`.
2. Review planned moves.
3. Execute with `--apply` to perform archival (creates dirs, writes stub shims if `--shim`).
4. Commit changes; CI (future) validates zero stray archive markers.

## Planned Enhancements

- CI GitHub Action integration.
- JSONL ledger: `docs/archive/archive_log.jsonl`.
- Tag-based grouping (model, training, cli, dataset).
- Restore helper script with reverse mapping.

## Full Historical Log

Future automated append section below this line.

---
*End of manually curated section.*