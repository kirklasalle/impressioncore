**Created:** August 23, 2025  
**Updated:** August 23, 2025  
**Author:** GitHub Copilot  
**Tags:** #restructure #architecture #planning #src\dev_tools\restructure\PLAN_STRUCTURE_MIGRATION.md  
**Category:** Development  
**Status:** Draft

# ImpressionCore Source Tree Migration Plan (Skeleton)

> This document is a concrete skeleton for the proposed directory refactor. It does NOT move files yet. It defines phases, mappings, and safeguards. Execution should be scripted and incremental to preserve history and avoid breakage.

## Objectives

1. Consolidate model-related code under `model/` (architectures, brainsim, tokenization, modules, embeddings)
2. Unify evaluation surface (`evaluation/` absorbs `eval/`, `benchmarks/`, loose metrics files)
3. Separate data acquisition & build logic into `data_pipeline/`
4. Normalize training lifecycle (loops, distillation, curriculum, optimization) under `training/`
5. Provide clean runtime layer under `inference/`
6. Introduce `ops/` for deployment, registry, management tasks
7. Remove code / data intermixing at `src/` root (datasets, analysis artifacts)

## High-Level Target Layout

```
src/
  core/                # Config, integrity, logging, shared utils
  data_pipeline/       # Ingestion → preprocessing → chunking → dataset_build
  model/               # Architectures, brainsim, tokenization, embeddings, modules
  training/            # Loops, curriculum, distillation, optimization
  inference/           # Runtime + production adapters
  evaluation/          # metrics/, benchmarks/, reports/
  pipelines/           # orchestration/, configs/
  ops/                 # deployment/, management/, model_registry/
  interfaces/          # cli/, api/, assistant/, web/
  scripts/             # Thin entrypoints only
  analysis/            # CSV/TXT reports & exploratory outputs
  experiments/         # Prototypes, spike code
  tests/               # Unified tests
  tools/               # Dev utilities (merge dev_tools/ later)
```

## Phase Breakdown

| Phase | Scope | Actions | Risk | Rollback |
|-------|-------|---------|------|----------|
| 0 | Preparation | Create skeleton dirs, add shim module, mapping script | Very Low | Delete new dirs |
| 1 | Evaluation Merge | Move `eval/`, `evaluation/`, `benchmarks/` assets → `evaluation/` | Low | Restore from git |
| 2 | Model Consolidation | Move `models/` + `modules/` + `tokenization/` + `brainsim/` → `model/` subtrees | Med | Use mapping + git mv |
| 3 | Training Normalization | Restructure `distillation/`, `curriculum/` under `training/` | Med | Revert commit |
| 4 | Data Pipeline | Move dataset builders + chunk scripts → `data_pipeline/` | Low | Revert |
| 5 | Ops & Pipelines | Move deployment & management to `ops/`, standardize `pipelines/` | Low | Revert |
| 6 | Root Cleanup | Relocate stray artifacts; enforce pre-commit guard | Med | Restore backup zip |
| 7 | Shim Removal | Remove legacy import shims after CI green & external scripts updated | Low | Revert removal |

## Migration Mapping (Initial Draft)

See `migration_map.py` for executable specification.

## Safeguards

- Run existing test suite after each phase.
- Keep `legacy_imports.py` providing old module paths for two release cycles.
- Pre-commit hook to forbid new Python files at `src/` root (defer implementation until Phase 6).

## Success Criteria

- Zero imports from deprecated roots (`models.`, `modules.`) after shim removal.
- Single evaluation runner API: `from evaluation.runner import run_all`.
- All scripts < 50 LOC delegating to internal packages.

## Open Questions / TODO

- Confirm whether `brainsim` remains active code vs reference only.
- Determine destination for large embedding generation scripts (likely `data_pipeline/dataset_build/`).
- Clarify whether `memlog/` should stay isolated (CURRENT POLICY: do not modify; leave as-is).

---
This plan file will be updated as phases complete.
