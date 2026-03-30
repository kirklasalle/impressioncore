# Phase 2: Model & Inference Consolidation (Scaffold)

**Date:** August 23, 2025  
**Owner:** GitHub Copilot  
**Status:** Draft (Scaffold committed for iterative fill)  

## Objectives

- Establish canonical model entrypoints under `core.models` with `registry/` for discovery
- Introduce shims (added: `inference/pipelines/`) while migrating references
- Remove duplicate / stray architecture copies after verification (`impressioncore_b3_architecture - Copy.py`, etc.)
- Minimize import side-effects (avoid sys.exit in import paths)
- Prepare for unified config loading & lazy weight initialization

## Immediate Tasks

1. Inventory duplicates & mark safe deletions (retain single authoritative B3 architecture file)
2. Refactor `training/b3_unified_training_pipeline.py` to raise ImportError instead of `sys.exit(1)` for test safety
3. Register canonical B3 bridge in `core.models.registry`
4. Add lightweight smoke test invoking registry factory without full dataset load
5. Update legacy imports shim after moves

## Safety Guardrails

- All deletions first moved to `archive/` folder (or git history) before permanent removal
- Run targeted pytest subset after each deletion / move
- Maintain `inference/pipelines` shim until all external references updated

## Proposed Registry Entries

- `b3_unified_bridge`: returns `(B3UnifiedTokenizerBridge, B3Config)` instance tuple
- Future: `b3_tokenizer_system`, `b1_legacy_multimodal` (if retained), distilled variants

## Open Questions

- Confirm which diffusion-related modules remain active vs experimental
- Determine consolidation path for `training/models/` vs `core/models/` split

## Next Automation Hooks

- Extend `migration_map.py` to output planned Phase 2 file moves JSON section
- Add `--phase 2` argument stub for future CLI enhancement

## Pending Decision

- Whether to flatten `core.models.unified_tokenizer_system` into `core.tokenization` (defer to Phase 3)

---
Generated automatically as part of restructuring workflow.
