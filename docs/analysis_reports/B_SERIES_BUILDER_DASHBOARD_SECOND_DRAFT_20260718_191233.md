# B-Series Builder + Dashboard Integration Second Draft

Generated: 2026-07-18 19:12:33 (local)

## Scope

This second draft records the implementation baseline for the canonical B-series offerings and the Builder-to-Dashboard handoff path:

- B1: 39M
- B2: 50M
- B3: 504M (forensic checkpoint evidence currently closest to ~506M)

## Forensic Offering Matrix

| Offering ID | Stage | Label | Target Params | Key Evidence |
|---|---|---|---:|---|
| b1_39m | B1 | B1 Hope 39M | 39M | F:\models\production\b3_hope_v1\metadata.json and config bundle |
| b2_50m | B2 | B2 Insight 50M | 50M | src/training/scripts/train_b3_50m.py |
| b3_504m | B3 | B3 Apex 504M | 504M | F:\models\checkpoints\kd_sft_phase2\step_5000.pt (observed family around ~506M) |

## Implemented Integration

1. Canonical presets added to source-of-truth config:
   - src/core/config/presets.py
   - Added OFFERING_PRESETS with model and training defaults for b1_39m, b2_50m, b3_504m.

2. Builder API preset wiring:
   - src/interfaces/web/routes/builder.py
   - Added /api/v1/builder/model/presets for frontend and harness consumers.
   - Added preset-aware application in /api/v1/builder/model/configure.
   - Added model discovery normalization in /api/v1/models/available:
     - offering hints inferred from path/family markers.
     - top-level offering_presets summary returned with model list.

3. Builder UI offering selection:
   - src/interfaces/web/templates/unified_builder.html
   - Added additive template cards for B1/B2/B3 offerings.
   - Added frontend mapping to sync selected offering to:
     - /api/v1/builder/model/configure
     - /api/v1/builder/training/configure
   - Added selection persistence to walkthrough progress via:
     - /api/v1/builder/walkthrough/progress

4. Walkthrough offering selection:
   - src/interfaces/web/templates/walkthrough.html
   - Added additive offering-selection card with B1/B2/B3 actions.
   - Added selection persistence through existing progress endpoint.

## Dashboard/Harness Handoff Contract

The discovery endpoint now exposes normalized offering metadata for downstream UI and orchestration:

- Endpoint: /api/v1/models/available
- Additions:
  - per-model offering field when inferred
  - offering_presets collection in response payload

This allows dashboard/harness code to:

- present user-friendly B-series labels,
- group discovered checkpoints by offering,
- default workflows by declared stage (B1/B2/B3).

## C1 Colossus Placeholder

C1 (Colossus) remains documented as planned architecture and is intentionally not promoted as an active Builder offering in this draft.
Reference: docs/architecture/IMPRESSIONCORE_C_BRAIN_TRIAD_ARCHITECTURE.md

## Backup and Integrity Procedure

Before promotion to production paths:

1. Backup configuration artifacts:
   - data/knowledge/builder_model_config.json
   - data/knowledge/builder_training_config.json
   - data/knowledge/builder_walkthrough_progress.json
2. Backup selected model directories/checkpoints.
3. Record hashes for reproducibility (PowerShell):

```powershell
Get-FileHash "F:\models\production\b3_hope_v1\impressioncore_b3_hope.pt" -Algorithm SHA256
Get-FileHash "F:\models\checkpoints\kd_sft_phase2\step_5000.pt" -Algorithm SHA256
```

## Risks and Gaps

- Offering inference from model paths is heuristic and should be replaced by explicit metadata for high-assurance routing.
- The B3 504M product label is currently mapped to evidence nearest ~506M; metadata normalization remains an open follow-up.
- Unified Builder still contains demonstration training simulation logic; operational dashboards should rely on API-backed status endpoints.

## Next Refactor Targets

1. Move offering inference from path heuristics to artifact metadata files.
2. Consolidate duplicated frontend model-definition surfaces into one canonical Builder UX path.
3. Add regression tests for preset application and /api/v1/models/available payload schema.

## Documentation Propagation Status

This draft has now been propagated into project-level planning and governance docs, including:

- Roadmaps (`docs/development_roadmap.md`, `docs/process/development_roadmap.md`)
- PRDs (`docs/prd.md`, `docs/reference/prd.md`)
- User and developer guides
- Next-steps trackers
- Changelog records

Additional documentation control coverage added for:

- `docs/DOCUMENTATION_INDEX.md`
- `.mcp/ids-mcp/README.md`
- `docs/reference/mcp_server/IDS_MCP_USER_GUIDE.md`
