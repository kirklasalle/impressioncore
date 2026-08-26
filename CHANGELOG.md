# Changelog

All notable changes to the ImpressionCore project are documented in this file.

## [Unreleased] - 2026-08-26

### Added & Governance
- **10 Laws Authoritative Alignment:** Unified and standardized Kirk LaSalle's 10 Permanent Active Directives across all core governance, covenant, and architecture files (`COPILOT_SACRED_COVENANT.md`, `COPILOT_PRIME_DIRECTIVE.md`, `Permanent_Active_Directives.txt`, `src/interfaces/api_state.py`, `docs/developer/ARCHITECTURE.md`, `docs/reference/Permanent_Active_Directives.md`).
- **Canonical Model Offering Presets:** Added full architecture and training definitions for `b1_39m` (B1 Hope 39M), `b2_50m` (B2 Insight 50M), `b3_504m` (B3 Apex 504M), and `b3_3b` (B3 Ultra 3B MoE) in `src/core/config/presets.py` and frontend `src/interfaces/builder_client/src/lib/constants.js`.
- **Model Definition Auto-Population:** Enhanced React Builder client (`ModelDefinitionPage.jsx`) to auto-populate all architectural and training defaults dynamically when any preset profile is chosen.
- **Model Building & Profile Walkthrough Guide:** Appended comprehensive 10-step model building walkthrough to `docs/user/user_guide.md` and `docs/user_guide.md`, detailing full pipeline instructions from GPU preflight to quantized production deployment.
- **Model Developer Guide:** Authored complete architectural, mathematical, and implementation guide for all models in `docs/developer/model_developer_guide.md`.
- **Model User Guide & Operator Manual:** Authored canonical operator and user manual for building, tuning, and packaging models in `docs/user/model_user_guide.md`.
- **Models Deep Technical Audit & 2026-2027 Roadmap:** Authored comprehensive architectural audit across B1 (39M), B2 (50M), B3 Apex (504M), B3 Ultra (3B MoE), and C1 Triad Plane with production GGUF, INT8/FP16 mixed precision, GQA, and MCP roadmap in `docs/analysis_reports/impressioncore_models_deep_audit_and_roadmap_2026.md`.
- **README & User Guide Overhaul with Detailed Illustrations:** Completely revised `README.md`, `docs/user/user_guide.md`, and `docs/user_guide.md` to incorporate the 2026 canonical model lineup (`b1_39m`, `b2_50m`, `b3_504m`, `b3_3b`, `c1_triad`), Kirk LaSalle's 10 Permanent Active Directives, Unified Model Builder & Live Visualizer features, Agent0Core GGUF supervision, and 4 high-detail technical illustrations (`impressioncore_hero_architecture.png`, `model_lineup_and_builder_flow.png`, `cognitive_triad_orchestration.png`, `builder_ui_interactive_suite.png`).
- **Automated Builder Verification Suite:** Authored `src/dev_tools/exercise_builder_site.py` for automated end-to-end exercising of all 9 builder site functions and real model build verification.

### Fixed & Security
- Fixed sparse attention temporary module import in `src/core/attention/attention_manager.py`.
- Enforced API key middleware authentication on `/v1/system/status` in `src/interfaces/triad_api.py`.
- Updated Fourth Law enforcement phrasing across API state and reference directives.

## [Unreleased] - 2026-07-19

### Added
- Integrated GGUF supervisor (`LlamaCppSupervisor`) and 22-task background periodic monitoring agent (`GuardianAgent`) into Python core (`agent0core/core/`).
- Upgraded `agent0core/ui/index.html` to a space-themed Glassmorphism dashboard.
- Created unit test suite in `src/tests/test_agent0_guardian.py`.
