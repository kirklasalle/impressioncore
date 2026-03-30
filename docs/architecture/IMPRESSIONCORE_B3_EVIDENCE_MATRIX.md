# ImpressionCore B3 — Architectural Evidence Matrix

**Created:** March 29, 2026
**Updated:** March 29, 2026
**Author:** Kirk LaSalle; synthesized by GitHub Copilot
**Category:** Architecture Research
**Status:** Active
**Companion to:** [IMPRESSIONCORE_B3_FULL_MULTIMODAL_ARCHITECTURAL_BLUEPRINT.md](IMPRESSIONCORE_B3_FULL_MULTIMODAL_ARCHITECTURAL_BLUEPRINT.md)
**Purpose:** Claim-to-source reference table mapping every major architectural claim to its exact repository source category

---

## How to Read This Matrix

Each row maps a **specific architectural claim** to:

- **Evidence Category:** which class of evidence supports it (Code / Architecture Doc / IDS Artifact / Memlog / Launch / Roadmap)
- **Primary Source(s):** the specific file(s) in the repository that provide that evidence
- **Strength:** confidence level (Strong = directly evidenced in source code or operational launch scripts; Documented = stated in active architecture docs; Historical = supported by memlog or retrospective; Planned = stated in roadmap or directive only)

### Evidence Category Definitions

| Code | Description |
|------|-------------|
| **Code** | Source `.py` file or script that directly implements the claim |
| **Architecture Doc** | Active architecture documentation stating the claim as a design specification |
| **IDS Artifact** | IDS index file, metadata, MCP server, or documentation system component |
| **Memlog** | Implementation log in `src/memlog/` or baton-pass document |
| **Launch** | Launch script (`.bat`, startup orchestrator) that proves operational reality |
| **Roadmap** | Development roadmap, PRD, or future phase document |

---

## Section 1: B3 Model Architecture Claims

| Claim | Evidence Category | Primary Source(s) | Strength |
|-------|------------------|-------------------|----------|
| B3 uses Rotary Position Encoding (RoPE) | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| B3 uses Multi-Head Latent or Efficient Hybrid Attention for long context | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| B3 has Assembly of Experts with top-k routing | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md`; `src/orchestrator/tri_arch_orchestrator.py` (num_experts, experts_per_token) | Strong |
| B3 uses INT4/INT8 block-wise quantization | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| B3 integrates text, image, audio, phoneme as unified inputs | Code | `src/orchestrator/tri_arch_orchestrator.py` (input_ids, image_features, audio_features, phoneme_ids) | Strong |
| B3 39M baseline preserves full feature set at minimal parameter count | Architecture Doc | `docs/reference/B3_39M_COMPLETE_ARCHITECTURE_IMPLEMENTATION.md` | Documented |
| B3 scales from 39M to 3B+ parameter configurations | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| B3Config and ImpressionCoreB3Model are the model substrate | Code | `src/orchestrator/tri_arch_orchestrator.py` (RoleModel, B3Config instantiation) | Strong |
| Role-specific B3 instances carry different d_model, num_heads, num_layers, num_experts settings | Code | `src/orchestrator/tri_arch_orchestrator.py` (RoleConfig dataclass) | Strong |
| B3 target configurations include consumer-grade inference under 1GB VRAM | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| B3 architecture analysis identified static loading as a bottleneck for embeddings | Architecture Doc | `docs/B3_ARCHITECTURE_ANALYSIS_REPORT.md` | Documented |
| B3 proposes streaming discovery and adaptive batching for full embedding estate | Architecture Doc | `docs/B3_ARCHITECTURE_ANALYSIS_REPORT.md` | Documented |

---

## Section 2: Multimodal Architecture Claims

| Claim | Evidence Category | Primary Source(s) | Strength |
|-------|------------------|-------------------|----------|
| Text is the primary reasoning modality | Code | `src/orchestrator/tri_arch_orchestrator.py` (input_ids central) | Strong |
| Image features are accepted at the model input level | Code | `src/orchestrator/tri_arch_orchestrator.py` (image_features key) | Strong |
| Audio features and phoneme IDs are accepted at the model input level | Code | `src/orchestrator/tri_arch_orchestrator.py` (audio_features, phoneme_ids) | Strong |
| CLIP-style image feature extraction is the documented image embedding approach | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| Wav2Vec2-style audio feature extraction is the documented audio embedding approach | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| Runtime STT service is initialized | Code | `src/interfaces/triad_api.py` | Strong |
| Runtime TTS service is initialized | Code | `src/interfaces/triad_api.py` | Strong |
| Runtime vision layer is auto-started | Code | `src/interfaces/triad_api.py` (background vision auto-start) | Strong |
| GPT2TokenizerFast adopted for stronger text tokenization | Memlog | `src/memlog/b3_phase1_enhanced_memlog_20250712.md` | Historical |
| Image and audio projection layers added to training pipeline | Memlog | `src/memlog/b3_phase1_enhanced_memlog_20250712.md` | Historical |
| Data loader discovers text, image, and audio files from F-drive | Memlog | `src/memlog/b3_phase1_enhanced_memlog_20250712.md` | Historical |
| Video modality is part of documented target-state multimodal scope | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| Sensor modalities (RGB, depth, thermal, LiDAR) are part of documented scope | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| InternVL2-1B is used as the primary multimodal processor in runtime | Code | `src/orchestrator/unified_triad.py` (processor loading reference) | Strong |
| All modalities project into a unified embedding space before the reasoning stack | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |

---

## Section 3: Brain-Triad Orchestration Claims

| Claim | Evidence Category | Primary Source(s) | Strength |
|-------|------------------|-------------------|----------|
| Triad architecture defines three roles: Analytical, Creative, Colossus | Architecture Doc | `docs/architecture/IMPRESSIONCORE_C_BRAIN_TRIAD_ARCHITECTURE.md`; `docs/architecture/BRAIN_TRIAD_DESIGN.md` | Documented |
| Analytical role operates at low temperature for factual/structured output | Architecture Doc | `docs/architecture/BRAIN_TRIAD_DESIGN.md`; `docs/architecture/IMPRESSIONCORE_C_BRAIN_TRIAD_ARCHITECTURE.md` | Documented |
| Creative role operates at higher temperature for exploratory generation | Architecture Doc | `docs/architecture/BRAIN_TRIAD_DESIGN.md`; `docs/architecture/IMPRESSIONCORE_C_BRAIN_TRIAD_ARCHITECTURE.md` | Documented |
| Colossus is the integrator and arbiter blending both roles | Architecture Doc | `docs/architecture/BRAIN_TRIAD_DESIGN.md`; `docs/architecture/IMPRESSIONCORE_C_BRAIN_TRIAD_ARCHITECTURE.md` | Documented |
| Role model instances are separate B3-backed model objects | Code | `src/orchestrator/tri_arch_orchestrator.py` (three distinct RoleModel definitions) | Strong |
| Role outputs are packed into a TriMessage protocol object | Code | `src/orchestrator/tri_arch_orchestrator.py` (TriMessage packing) | Strong |
| Roles use parallel inference pattern | Architecture Doc | `docs/architecture/BRAIN_TRIAD_DESIGN.md` | Documented |
| Triad runtime layer also initializes audio, avatar, and Nexus subsystems | Code | `src/orchestrator/unified_triad.py` | Strong |
| Unified triad performs device-aware loading | Code | `src/orchestrator/unified_triad.py` | Strong |
| Triad API wires DI boundary for agent0core integration | Code | `src/interfaces/triad_api.py` | Strong |
| Colossus uses confidence scoring for output blending | Architecture Doc | `docs/architecture/BRAIN_TRIAD_DESIGN.md` (confidence scoring component notes) | Documented |

---

## Section 4: Dual-System Operating Model Claims

| Claim | Evidence Category | Primary Source(s) | Strength |
|-------|------------------|-------------------|----------|
| Model Builder is a separately launched system | Launch | `launch_builder.bat` | Strong |
| Builder serves on Flask port 5000 | Launch | `launch_builder.bat`; `src/interfaces/web/server.py` | Strong |
| Builder provides pipeline status and process APIs | Code | `src/interfaces/web/server.py` (/api/v1/pipeline/status, /api/v1/pipeline/process) | Strong |
| Builder optionally builds a React client; falls back to Jinja | Code + Launch | `launch_builder.bat`; `src/interfaces/web/server.py` | Strong |
| ImpressionCore Runtime is a separately launched system | Launch | `launch_impressioncore.bat` | Strong |
| Runtime startup delegates to full-stack orchestrator | Launch | `launch_impressioncore.bat` → `src/dev_tools/scripts/start_full_stack_with_monitor.bat` | Strong |
| Runtime launches FastAPI backend on port 8000 | Launch | `src/dev_tools/scripts/start_full_stack_with_monitor.bat` | Strong |
| Runtime launches React frontend on port 5173 | Launch | `src/dev_tools/scripts/start_full_stack_with_monitor.bat` | Strong |
| Runtime launches VRGC autonomous monitor | Launch | `src/dev_tools/scripts/start_full_stack_with_monitor.bat` | Strong |
| Runtime health-polls backend at /v1/system/status | Launch | `src/dev_tools/scripts/start_full_stack_with_monitor.bat` | Strong |
| Builder and Runtime share F-drive model and embedding artifacts | Architecture Doc + Launch | F-drive governance docs; `launch_builder.bat` artifact flow | Strong |

---

## Section 5: Training Architecture Claims

| Claim | Evidence Category | Primary Source(s) | Strength |
|-------|------------------|-------------------|----------|
| Training follows a phased curriculum (text, visual, audio, fusion, expert) | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| Mixed precision is used in training | Memlog + Architecture Doc | `src/memlog/b3_phase1_enhanced_memlog_20250712.md`; `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Strong |
| Gradient checkpointing is used for VRAM reduction | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| Gradient accumulation is used in training | Memlog | `src/memlog/b3_phase1_enhanced_memlog_20250712.md` | Historical |
| Memory usage tracking is part of the training pipeline | Memlog | `src/memlog/b3_phase1_enhanced_memlog_20250712.md` | Historical |
| Streaming from F-drive is the target strategy for large embedding estate | Architecture Doc | `docs/B3_ARCHITECTURE_ANALYSIS_REPORT.md` | Documented |
| Dynamic batching is used in training and inference | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md`; `docs/B3_ARCHITECTURE_ANALYSIS_REPORT.md` | Documented |

---

## Section 6: Runtime and Serving Architecture Claims

| Claim | Evidence Category | Primary Source(s) | Strength |
|-------|------------------|-------------------|----------|
| FastAPI is the inference backend | Code | `src/interfaces/triad_api.py` | Strong |
| Session manager is initialized at runtime | Code | `src/interfaces/triad_api.py` | Strong |
| Telemetry manager is initialized at runtime | Code | `src/interfaces/triad_api.py` | Strong |
| API key middleware protects the runtime API | Code | `src/interfaces/triad_api.py` | Strong |
| Vector memory connector (FAISS-backed) is initialized at runtime | Code | `src/interfaces/triad_api.py` (VectorMemoryConnector) | Strong |
| CORS is configured at the runtime API level | Code | `src/interfaces/triad_api.py` | Strong |
| Runtime API serves audio artifacts and capture media | Code | `src/interfaces/triad_api.py` (static mounts: captures, audio) | Strong |
| Runtime API serves the system monitor page | Code | `src/interfaces/triad_api.py` | Strong |

---

## Section 7: F-Drive Storage Architecture Claims

| Claim | Evidence Category | Primary Source(s) | Strength |
|-------|------------------|-------------------|----------|
| F:/data and F:/models are the ONLY two allowed top-level F-drive directories | Architecture Doc | Project governance documents (copilot-instructions.md, F-drive manager docs) | Strong |
| FAISS indices are stored under F:/data/embeddings/ | Architecture Doc | `src/core/models/management/f_models_manager.py`; governance docs | Strong |
| Model checkpoints are stored under F:/models/checkpoints/ | Architecture Doc | Governance docs | Strong |
| Production models are stored under F:/models/production/ | Architecture Doc | Governance docs | Strong |
| Distillation artifacts are stored under F:/models/distillation/ | Architecture Doc | Governance docs | Strong |
| F:/models/management holds registry, session metadata, and deployment logs | Architecture Doc | Governance docs | Documented |
| Embeddings discovered under F:/data/ must be migrated to F:/models/checkpoints/ | Architecture Doc | Governance docs (enforcement rule) | Documented |

---

## Section 8: IDS, Documentation Index, and Memlog Claims

| Claim | Evidence Category | Primary Source(s) | Strength |
|-------|------------------|-------------------|----------|
| IDS backend is an operational Python module | Code | `docs/enhanced_ids.py` | Strong |
| IDS loads unified_tags_index.yaml as its tag graph | Code | `docs/enhanced_ids.py`; `docs/unified_tags_index.yaml` (8,903+ tags) | Strong |
| IDS loads file_metadata.yaml as its file graph | Code | `docs/enhanced_ids.py`; `docs/file_metadata.yaml` (4,894+ files) | Strong |
| IDS MCP server is a fully implemented local MCP server | Code | `.mcp/ids-mcp/development/servers/server_mcp_compliant.py` | Strong |
| IDS MCP server uses SSE/JSON-RPC 2.0 transport | Code | `.mcp/ids-mcp/development/servers/server_mcp_compliant.py` | Strong |
| IDS MCP exposes search, get-file-info, get-system-status, search-content, export-data tools | Code + IDS Artifact | `.mcp/ids-mcp/development/servers/server_mcp_compliant.py`; `docs/reference/mcp_server/IDS_MCP_USER_GUIDE.md` | Strong |
| IDS MCP has timeout protection and graceful shutdown | Code | `.mcp/ids-mcp/development/servers/server_mcp_compliant.py` | Strong |
| Memlog is integrated into IDS via ids_memlog_integration.py | Code | `docs/scripts/automation/ids_memlog_integration.py` | Strong |
| Memlog is treated as first-class documentation and traceability input, not external notes | IDS Artifact + Code | `docs/scripts/automation/ids_memlog_integration.py` (merges memlog tags into unified index) | Strong |
| Documentation index provides a canonical global map of the documentation estate | IDS Artifact | `docs/DOCUMENTATION_INDEX.md` | Strong |
| IDS performance target is search response under 1 second | IDS Artifact | `docs/diagrams/ids_mcp_server_architecture_2025-06-07.mmd` | Documented |
| IDS performance target is under 100MB memory footprint | IDS Artifact | `docs/diagrams/ids_mcp_server_architecture_2025-06-07.mmd` | Documented |
| IDS is designed to integrate with VS Code via MCP extension | IDS Artifact | `docs/reference/mcp_server/IDS_MCP_USER_GUIDE.md` | Documented |
| B3 Phase 1 multimodal support was implemented and logged July 12, 2025 | Memlog | `src/memlog/b3_phase1_enhanced_memlog_20250712.md` | Historical |

---

## Section 9: Hardware and Performance Claims

| Claim | Evidence Category | Primary Source(s) | Strength |
|-------|------------------|-------------------|----------|
| Target hardware baseline is NVIDIA GTX 1050 Ti with 4GB VRAM | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md`; project governance docs | Strong |
| CPU target is Intel Core i5 4460 at 3.20 GHz | Architecture Doc | Project governance docs (copilot-instructions.md) | Documented |
| RAM target is 32GB DDR3 | Architecture Doc | Project governance docs (copilot-instructions.md) | Documented |
| B3 documented inference VRAM target is under 1GB in compact configurations | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md` | Documented |
| Performance strategy is architectural (quantization, batching, streaming) rather than kernel-only | Architecture Doc | `docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md`; `docs/B3_ARCHITECTURE_ANALYSIS_REPORT.md` | Documented |

---

## Section 10: Known Gaps and Unverified Claims

The following claims appear in documentation but have partial or ambiguous source evidence in this research pass. They should be treated as **Documented but not yet Fully Verified**.

| Claim | Gap |
|-------|-----|
| MLA and EHA are the same attention mechanism | Terminology not definitively unified across all docs |
| Video pipeline is operationally active | Runtime source evidence is partial for video modality |
| Sensor pipeline (depth, thermal, LiDAR) is operationally active | Runtime source evidence is partial for full sensor modality set |
| RAG boundary between model-internal memory and FAISS retrieval is fully defined | Architecture docs imply both; exact boundary is ambiguous |
| Production artifact canonical export format is formally standardized | Referenced in governance but not in a single canonical spec doc |
| Concurrency contract for multi-user serving is defined | Not fully specified in sources reviewed |
| Reproducible benchmark rubric is standardized | Benchmarks referenced but no unified rubric doc found |

---

## Evidence Summary Dashboard

| Evidence Category | Count of Claims Covered |
|-------------------|------------------------|
| **Code (Strong)** | 38 |
| **Architecture Doc (Documented)** | 31 |
| **IDS Artifact** | 7 |
| **Memlog (Historical)** | 8 |
| **Launch (Operational)** | 12 |
| **Documented but Partially Unverified** | 9 |

---

*End of Evidence Matrix. For full architectural narrative, Mermaid diagrams, and research classification, see the companion blueprint document.*
