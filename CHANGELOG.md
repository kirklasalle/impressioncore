# Changelog

All notable changes to the ImpressionCore project are documented in this file.

## [1.0.1] - 2026-11-16

### Security & Immediate Blockers Fixed
- **Builder Server Hardening (`SEC-01`):** Updated `src/interfaces/web/server.py` to bind `127.0.0.1` by default (`IMPRESSIONCORE_BUILDER_HOST`), disable Flask/Werkzeug debug mode unless `IMPRESSIONCORE_DEBUG=1`, replace wildcard CORS with `src.core.config.cors_config.get_allowed_origins()`, omit raw query parameters from request trace logs, and enforce constant-time `X-API-Key` (`IMPRESSIONCORE_API_KEY`) or authenticated session checks on `/api/*` routes.
- **Safe Checkpoint Loading (`SEC-02`):** Enforced `weights_only=True` on active `torch.load` calls in `src/interfaces/web/routes/builder.py`, `src/core/assembly_of_experts.py`, and `src/core/models/impressioncore_b3_architecture.py` (`MemoryOptimizedCheckpointing`), and confined `builder.get_model_tokenizer()` `.pt` file loading to allowed project/data/checkpoint roots.
- **Workbench File-Read Confinement (`SEC-03`):** Added `_allowed_local_roots()` path confinement (`Path.resolve().is_relative_to(...)`) in `src/interfaces/web/routes/workbench.py` (`bounded_file`) to block arbitrary local file reads via dataset/tokenizer preflight paths.
- **B3 Causal Attention & Sliding-Window Fixes (`CRIT-01`):** Updated `EfficientMultiHeadLatentAttention` and `AssemblyOfExperts` in `src/core/models/impressioncore_b3_architecture.py` to apply upper-triangular causal masks across standard, cached, sliding-window, and prefix-cumsum linear attention paths, fixed per-sample 2D batch padding masks (eliminating `mask[0]` batch broadcast), and fixed `recombine_windows()` overlap-add broadcasting and span tracking.
- **TurboQuant Invertibility & Passthrough (`CRIT-02`):** Updated `RandomRotation` in `src/core/quantization/turboquant.py` to use exact QR random orthogonal matrices for non-power-of-2 dimensions (preventing truncated Hadamard inversion error) and fixed `TurboQuantCompressor.compress()` when `enabled=False` to preserve original tensors without `int8` truncation.
- **Quantization Scale & Zero-Tensor Safety (`CRIT-03`):** Replaced unscaled `int8`/`int4` casts in `src/interfaces/web/routes/builder.py` with symmetric per-tensor quantization storing `.__scale__` tensors, and clamped `scale >= 1e-8` in `src/core/export/export_production_model.py` to prevent `NaN` division on all-zero tensors.
- **Regression Tests:** Added `src/tests/core/test_immediate_blockers.py` covering `SEC-01`, `SEC-02`, `SEC-03`, `CRIT-01`, `CRIT-02`, and `CRIT-03`.
- **Phase 2 & 3 Security, Governance & Portability Hardening:**
  - `SEC-04`: Removed repeating-key XOR fallbacks from `src/core/security/identity/cryptographic_core.py`, implemented real `ChaCha20Poly1305` and `AESGCM` encrypt/decrypt, disabled simulated Kyber/Dilithium keygen unless `allow_simulated_pqc=True` (with `quantum_resistant=False`), and fixed an EOF infinite-loop/unbounded-memory DoS in `src/core/security/encryption/aes_encryption.py` (`decrypt_file`).
  - `SEC-05`: Replaced `eval()` in `src/core/knowledge/rule_engine.py` with an AST allowlist evaluator (`_safe_eval_formula`), replaced `eval()` in `src/interfaces/cli/cli_tokenizer_utils.py` with `ast.literal_eval()`, and replaced `os.system()` in `.mcp/vrgc/tools/covenant_guardian.py` with `subprocess.run(..., shell=False)`.
  - `SEC-06`: Gated `trust_remote_code` and added optional `model_revision` pinning in `src/orchestrator/unified_triad.py`.
  - `ARCH-01`: Replaced hardcoded `"status": "success"` stubs in `agent0core/core/guardian_agent.py` with live socket, covenant hash, tool contract, supervisor slot, MCP config, and telemetry inspections.
  - `CRIT-05`: Fixed FAISS memory reconstruction in `src/core/models/impressioncore_b3_architecture.py` (`BrainInspiredTransformerLayer.forward`) to reconstruct retrieved `mem_indices` rather than index `0`.
  - `ARCH-02 / ARCH-03`: Fixed `docker/Dockerfile.python` (`COPY run_server.py ./` + non-root `appuser`), cleaned duplicate/invalid entries and added `websockets>=12.0` + `cryptography>=42.0.0` in `requirements.txt` and `pyproject.toml`, fixed `src/core/security/tests/test_integration_security.py` imports, fixed `src/interfaces/routes/rlm.py` path/interpreter portability, and added local checkpoint directory fallback in `src/interfaces/web/routes/builder.py`.
  - `NOV-01 / DOC-01`: Restricted `MHCProjection` Sinkhorn-Knopp projection in `src/models/layers/mhc.py` to square matrices, and documented preset dimension variance in `README.md`.
  - **Regression Tests:** Added `src/tests/core/test_phase2_phase3_hardening.py`.

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
- Integrated GGUF supervisor (`LlamaCppSupervisor`) and 22-task background periodic monitoring agent (`GuardianAgent`) into Python core (`agent0core/core/`).
- Upgraded `agent0core/ui/index.html` to a space-themed Glassmorphism dashboard.
- Created unit test suite in `src/tests/test_agent0_guardian.py`.
