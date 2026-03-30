# Canonical Checkpoint Set & Audit (Baseline Wrap-Up)

**Created:** August 24, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team; GitHub Copilot  
**Tags:** #documentation #models #checkpoints #canonical #retention #canonical_checkpoint_set  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

This document captures the baseline state of the checkpoint governance and audit system after consolidation / cleanup (August 24, 2025). It locks a minimal, stable foundation so broader documentation refresh and future enhancements can proceed incrementally.

---

## 1. Implemented Components (Baseline)

| Component | File | Purpose |
|-----------|------|---------|
| Inventory (pre-existing) | `src/core/models/management/checkpoint_inventory.py` | Raw recursive listing + aggregates |
| Retention Analysis (pre-existing) | `checkpoint_retention_analysis.py` | Heuristic scoring & keep/prune decision basis |
| Governance Orchestrator | `checkpoint_governance.py` | Consolidates retention, overrides, tiers, registry generation |
| Governance Overrides | `governance_overrides.json` | Canonical allowlist (force_keep), protection & exclusion patterns |
| Audit (new) | `checkpoint_audit.py` | Deep per‑checkpoint metadata + tensor/param stats + hashes |
| Policy | `CHECKPOINT_GOVERNANCE_POLICY.md` | Permanent governance objectives & lifecycle |

---

## 2. Canonical (Force-Keep) Checkpoint List

Current retained canonical anchors: 15  
Expected canonical total (override target): 15  
Completeness Status: 15 / 15 (FULL)

These are enforced via `force_keep` in `governance_overrides.json` and tagged as canonical anchors during governance runs:

```text
b1/b1_checkpoint_epoch_45_quality_0.00_1.pth
b1/b1_working_checkpoint_epoch_015_quality_0.00_1.pth
b1/distillation_checkpoint_epoch_75_quality_0.00_1.pth
b1/flagship/impressioncore_b1_flagship_1.pth
b3/unified_sweet_spot/unified_final_step_20_weights_only.pth
b3/unified_sweet_spot/best/best_loss_step_0.pth
b3/b3_ollama_enhanced/b3_ollama_enhanced_final_step_5000.pth
b3/b3_ollama_enhanced/b3_ollama_enhanced_stage_2_step_5500.pth
b3/sweet_spot_recovery/recovery_step_500.pth
b3/sweet_spot_recovery/recovery_step_4000.pth
b3/phase2/checkpoints/b3_phase2_epoch_1_20250806_135110.pth
b3/phase2/checkpoints/b3_phase2_epoch_6_20250806_032749.pth
b3/b3_training/b3_training_epoch_50_20250805_184808.pth
b3/b2_fixed_epoch_2.pth
b2/b2_teacher_model.pth (MISSING on disk at last audit)
```

Removed / deferred (previously considered, not presently in allowlist):

```text
b3/unified_sweet_spot/unified_final_step_8_weights_only.pth
b3/unified_sweet_spot/unified_final_step_25_weights_only.pth
```

---

## 3. Audit & Registry Output (Summary)

Latest audit (`checkpoint_audit.py --hash`) produced for 15 entries. Governance registry now includes:

- `canonical_anchor` boolean per artifact
- `canonical_expected` & `canonical_gap` in summary when `expected_canonical_total` provided
- Duplicate hash grouping section (`duplicate_hash_groups`) if hashing enabled

| Metric | Range / Examples |
|--------|------------------|
| Parameter Counts | 101.527M (training epoch 50) → 645.222M (phase2 epoch 1) |
| Mid‑sized Distillation | 129.638M (distillation epoch 75) |
| Large Recovery / Final / Best Variants | 506.045M (multiple: best, final, recovery, stage_2) |
| Phase2 Expansion | 645.222M (phase2 epoch 1) |
| Hashing | SHA256 per file (first 12 chars in summary; full in detailed sections) |
| Missing | `b2/b2_teacher_model.pth` not found (logged as missing) |

Files failing deep load show Unpickling/Runtime errors (likely alternate serialization). Future enhancement: integrate project-specific load routines.

Artifacts:

```text
temp/checkpoint_governance/checkpoint_registry.(json|md)
temp/checkpoint_audit/audit_checkpoints.(json|md)
```

---

## 4. Minimal Usage Commands

```bash
python src/core/models/management/checkpoint_governance.py --root F:/models/checkpoints --out d:/Projects/impressioncore/temp/checkpoint_governance
python src/core/models/management/checkpoint_audit.py --root F:/models/checkpoints --overrides src/core/models/management/governance_overrides.json --out d:/Projects/impressioncore/temp/checkpoint_audit --hash
```

No pruning or staging is currently executed by default (safety-first baseline).

---

## 5. Known Gaps / Deferred Enhancements

| Area | Gap | Planned Direction |
|------|-----|-------------------|
| Canonical Count | 15 active (target finalized at 15) | Revisit deferred variants later |
| Missing File | `b2/b2_teacher_model.pth` absent | Confirm path or adjust allowlist |
| Serialization Diversity | Some models not loadable via direct `torch.load` | Add custom loader / safetensors support |
| Redundancy Metrics | Duplicate grouping now in registry when hashing enabled | Extend to non-canonical + size savings calc |
| Registry Schema | Canonical flag only implicit via status | Persist explicit `canonical_anchor` boolean |
| Documentation Sync | Policy + new audit doc not yet cross-linked | Add links after broader doc review |

---

## 6. Next Light Actions (Optional)

1. Verify teacher model location; update or remove from allowlist if truly deprecated.
2. (Deferred) Optionally reintroduce weights_only variants if strategic value emerges.
3. Capture a memlog entry (see template below) to finalize this phase.
4. (Optional) Implement size-based savings estimation from duplicate hash grouping.

---

## 7. Memlog Entry Template (Do Not Auto-Write)

```text
Date: August 24, 2025
Category: Checkpoint Governance Baseline Consolidation
Summary: Established minimal canonical checkpoint governance & audit system. Implemented orchestration (`checkpoint_governance.py`), deep audit (`checkpoint_audit.py`), and refined overrides with 15 canonical anchors (teacher model path missing; two weights_only candidates deferred). Generated registry & audit reports (hash + param stats). Deferred advanced loaders, duplication analysis, and extended documentation until post-cleanup review.
Retained Canonical: 15 (see CANONICAL_CHECKPOINT_SET.md)
Deferred: custom loaders, duplicate hashing, re-adding 2 weight-only variants, teacher model path validation.
Next Steps: Validate missing teacher checkpoint; finalize canonical count; integrate canonical flag into registry schema; refresh documentation links.
```

---

*End of baseline consolidation document.*