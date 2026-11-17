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

## [1.0.1] - 2026-11-16

### Security & Immediate Blockers Fixed

- **Builder Server Hardening (`SEC-01`):** `src/interfaces/web/server.py` now binds `127.0.0.1` by default (`IMPRESSIONCORE_BUILDER_HOST`), disables Werkzeug debug mode unless `IMPRESSIONCORE_DEBUG=1`, replaces wildcard CORS with `get_allowed_origins()`, strips query parameter dumps from trace logs, and enforces `X-API-Key` (`IMPRESSIONCORE_API_KEY`) or session authentication on `/api/*`.
- **Safe Checkpoint Loading (`SEC-02`):** Enforced `weights_only=True` on active checkpoint loads in `src/interfaces/web/routes/builder.py`, `src/core/assembly_of_experts.py`, and `src/core/models/impressioncore_b3_architecture.py`, with allowed-root path confinement in `builder.get_model_tokenizer()`.
- **Workbench File-Read Confinement (`SEC-03`):** Confined `workbench.bounded_file()` in `src/interfaces/web/routes/workbench.py` to resolved project/data/checkpoint/configured roots.
- **B3 Causal Attention & Sliding-Window Fixes (`CRIT-01`):** Enforced causal masking and per-sample 2D padding masks across `EfficientMultiHeadLatentAttention` (standard, cached, sliding-window, and prefix-cumsum linear attention) and `AssemblyOfExperts.routing_attention`, and fixed `recombine_windows()` span tracking and `(1, seq_len, 1)` normalization.
- **TurboQuant Invertibility & Passthrough (`CRIT-02`):** Fixed `RandomRotation` in `src/core/quantization/turboquant.py` to use exact QR orthogonal matrices on non-power-of-2 dimensions and preserved float tensors when `enabled=False`.
- **Quantization Scale & Zero-Tensor Safety (`CRIT-03`):** Replaced destructive `int8`/`int4` casts in `builder.py` with scale-preserving symmetric quantization (`__scale__`) and clamped `scale >= 1e-8` in `src/core/export/export_production_model.py`.
- **Verification:** Added `src/tests/core/test_immediate_blockers.py`.
- **Phase 2 & 3 Security, Governance & Portability Hardening:** Hardened `cryptographic_core.py` (real `ChaCha20Poly1305` / `AESGCM`, removed XOR fallback, gated simulated PQC `SEC-04`), replaced `eval()`/`os.system()` (`SEC-05`), gated `trust_remote_code` in `unified_triad.py` (`SEC-06`), replaced `GuardianAgent` stubs with real runtime checks (`ARCH-01`), fixed FAISS index reconstruction (`CRIT-05`), repaired `Dockerfile.python` / `requirements.txt` / `pyproject.toml` / `test_integration_security.py` / `rlm.py` / `builder.py` checkpoint fallback (`ARCH-02`, `ARCH-03`), restricted `MHCProjection` Sinkhorn-Knopp to square matrices (`NOV-01`), and added `README.md` preset matrix alignment note (`DOC-01`) with regression tests in `src/tests/core/test_phase2_phase3_hardening.py`.

## [Unreleased] - 2026-11-02

### Fixed

- Repaired local sensory browser/API authentication with a guarded loopback
  same-origin gateway, server-only credentials, HTTP/media/WebSocket coverage,
  CORS-correct errors and owned-child supervision.
- Real model failures, missing/mock readiness and empty/failed generation now
  fail explicitly. Existing InternVL2-1B produced a real browser reply; external
  pretrained identity is distinguished from native B-series execution.
- Added explicit camera Start/Stop and stream health. Fixed SDK frame-release
  buffer starvation, truthful RGB/IR and physical/logical identity, and normal
  stopped-state health polling.
- Added optional `speech` dependency setup and verified cached CPU Whisper
  readiness without enabling microphone listening.

### Added

- Native measured run identity, explicit prefix objective, schema-2 checkpoint
  identity and hashed export manifest; unsupported offering executions remain
  unavailable/uncertified rather than silently relabelled.
- Focused runtime/auth/sensor/native regressions, local gateway boundary tests,
  scoped frontend lint configuration and successful real browser checks.
- [Repair evidence and remaining release gates](../analysis_reports/BUILDER_PLATFORM_AUDIT_20261102.md#repair-addendum--november-2-2026),
  synchronized operator guidance, status notices and prioritized backlog.

## [Unreleased] - 2026-08-26

### Added & Governance
- **10 Laws Authoritative Alignment:** Unified and standardized Kirk LaSalle's 10 Permanent Active Directives across all core governance, covenant, and architecture files (`COPILOT_SACRED_COVENANT.md`, `COPILOT_PRIME_DIRECTIVE.md`, `Permanent_Active_Directives.txt`, `src/interfaces/api_state.py`, `docs/developer/ARCHITECTURE.md`, `docs/reference/Permanent_Active_Directives.md`).
- **Canonical Model Offering Presets:** Added full architecture and training definitions for `b1_39m` (B1 Hope 39M), `b2_50m` (B2 Insight 50M), `b3_504m` (B3 Apex 504M), and `b3_3b` (B3 Ultra 3B MoE) in `src/core/config/presets.py` and frontend `src/interfaces/builder_client/src/lib/constants.js`.
- **Model Definition Auto-Population:** Enhanced React Builder client (`ModelDefinitionPage.jsx`) to auto-populate all architectural and training defaults dynamically when any preset profile is chosen.
- **Model Building & Profile Walkthrough Guide:** Appended comprehensive 10-step model building walkthrough to `docs/user/user_guide.md` and `docs/user_guide.md`, detailing full pipeline instructions from GPU preflight to quantized production deployment.
- **Model Developer Guide:** Authored complete architectural, mathematical, and implementation guide for all models in `docs/developer/model_developer_guide.md`.
- **Model User Guide & Operator Manual:** Authored canonical operator and user manual for building, tuning, and packaging models in `docs/user/model_user_guide.md`.
- **Models Deep Technical Audit & 2026-2027 Roadmap:** Authored comprehensive architectural audit across B1 (39M), B2 (50M), B3 Apex (504M), B3 Ultra (3B MoE), and C1 Triad Plane with production GGUF, INT8/FP16 mixed precision, GQA, and MCP roadmap in `docs/analysis_reports/impressioncore_models_deep_audit_and_roadmap_2026.md`.
- **README & User Guide Overhaul with Detailed Illustrations & Clean Live UI Galleries:** Completely revised `README.md`, `docs/user/user_guide.md`, and `docs/user_guide.md` to incorporate the 2026 canonical model lineup (`b1_39m`, `b2_50m`, `b3_504m`, `b3_3b`, `c1_triad`), Kirk LaSalle's 10 Permanent Active Directives, Unified Model Builder & Live Visualizer features, Agent0Core GGUF supervision, 4 high-detail technical illustrations, and complete galleries of pristine live screenshots from the running ImpressionCore Builder (`builder_live_*`), clean vision tracking (`screenshot53-frontend-kinect.png`), and hardware validation (`TaskManager-GPU_Performance_Screenshot.png`), while purging debug error-annotated images (`screenshot30-snapshot-LLMresponse.png`).
- **Automated Builder Verification Suite:** Authored `src/dev_tools/exercise_builder_site.py` for automated end-to-end exercising of all 9 builder site functions and real model build verification.

### Fixed & Security
- Fixed sparse attention temporary module import in `src/core/attention/attention_manager.py`.
- Enforced API key middleware authentication on `/v1/system/status` in `src/interfaces/triad_api.py`.
- Updated Fourth Law enforcement phrasing across API state and reference directives.

## [Unreleased] - 2026-07-19

### Added

- WS1: Added `src/core/config/offering_manifest.py` — offering preset schema validator with startup validation.
- WS1: Added 43 new tests for offering preset schema and manifest validation (`test_offering_presets.py`, `test_offering_manifest.py`).
- WS5: Ratcheted coverage gate from 9% to 10% — M1 quality gate target reached. 649+ tests collected.
- WS4: Integrated GGUF model supervisor (`LlamaCppSupervisor`) and 22-task background periodic monitoring agent (`GuardianAgent`) into Python core (`agent0core/core/`).
- WS4: Exposed supervisor and guardian routes via FastAPI server in `agent0core/api.py`, including slots management, model loading/unloading, and task control (run/toggle).
- WS4: Upgraded `agent0core/ui/index.html` to a premium space-themed Glassmorphism dashboard featuring real-time telemetry, model load controls, task controls, and real-time logs.
- WS5: Created unit test suite in `src/tests/test_agent0_guardian.py` verifying slots config, task toggling, and direct self-healing. Passed all 5 tests.

### Security

- WS6: Replaced placeholder API key verification in `src/services/text_generation/api.py` with `hmac.compare_digest` constant-time comparison.
- WS6: Added development/production mode split — auth bypassed when `IMPRESSIONCORE_API_KEY` env var is not set.
- WS6: Integrated directive integrity self-healing in GuardianAgent to restore active directives from backups on detection of modification or missing files.

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
