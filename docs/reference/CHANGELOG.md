# Changelog

**Created:** May 10, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\CHANGELOG.md #docs\reference\changelog.md #documentation #gpu_optimization #memory_management #testing #transformer #web_interface  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# Changelog

## [Unreleased] - 2026-07-19

### Added

- WS1: Added `src/core/config/offering_manifest.py` — offering preset schema validator with startup validation.
- WS1: Added 43 new tests for offering preset schema and manifest validation (`test_offering_presets.py`, `test_offering_manifest.py`).
- WS5: Ratcheted coverage gate from 9% to 10% — M1 quality gate target reached. 649+ tests collected.

### Security

- WS6: Replaced placeholder API key verification in `src/services/text_generation/api.py` with `hmac.compare_digest` constant-time comparison.
- WS6: Added development/production mode split — auth bypassed when `IMPRESSIONCORE_API_KEY` env var is not set.

### Documentation

- Updated SAP Status Audit with current session progress.
- Updated canonical changelog with M1 execution deliverables.

## [Unreleased] - 2026-07-18

### Added

- Added canonical execution backlog: `docs/process/EXECUTION_APPENDIX_2026_2027.md`.
- Added roadmap execution extensions in `docs/development_roadmap.md` and `docs/process/development_roadmap.md`.
- Added PRD delivery addenda in `docs/prd.md` and `docs/reference/prd.md`.
- Added user/developer guide execution alignment updates.
- Added next-steps execution addenda in `docs/next_steps.md` and `docs/process/next_steps.md`.

### Documentation

- Added documentation index and IDS MCP synchronization requirements for major doc changes.
- Added immediate execution window alignment in canonical roadmap, next-steps, and PRD documents.
- Converted roadmap, next-steps, and PRD mirror files to pointer-only mode.
- Updated mirror synchronization checklist status for pointer-only transitions.

## [Unreleased] - 2025-05-17

### Fixed

- Resolved multiple import errors in `src/core/utils/memory_optimization/__init__.py` and `src/tests/test_memory.py`.
- Corrected `MockModule` output shape in `src/tests/test_memory.py` to pass `test_optimize_memory_usage`.
- Added missing `fetch_layer_to_gpu` function to `src/core/utils/memory_optimization/cpu_offload.py`.
- Created `cpu_offload.py` module in `src/core/utils/memory_optimization/`.
- Fixed relative import paths in `src/web/tests/conftest.py` and `src/user_data/web/tests/conftest.py`.
- Created `src/models/diffusion/diffusion_layers.py` and `src/models/transformer_layer.py`.

### Added

- Comments to `MockModule` and `test_optimize_memory_usage` in `src/tests/test_memory.py` for clarity after power outage incident.
