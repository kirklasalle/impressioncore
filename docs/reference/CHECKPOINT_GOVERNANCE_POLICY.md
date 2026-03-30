# Checkpoint Governance Policy

**Created:** August 24, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team; GitHub Copilot  
**Tags:** #documentation #governance #models #checkpoints #retention #official #checkpoint_governance  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

This policy establishes a permanent, auditable, and systematic governance framework for all model checkpoints stored under `F:/models/checkpoints` within the ImpressionCore architecture. It ensures that storage usage, lineage integrity, reproducibility, and production readiness are maintained while preventing uncontrolled growth and redundancy.

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `CANONICAL_CHECKPOINT_SET.md` | Canonical (force-keep) anchors + audit summary + gaps |
| `checkpoint_governance.py` | Orchestrates inventory + retention + overrides into registry |
| `checkpoint_audit.py` | Deep per‑checkpoint hash + tensor/param stats |
| `governance_overrides.json` | Protection patterns, force_keep / force_prune, exclusions |

All modifications to canonical anchors must update both the overrides file and the canonical document, followed by a governance + audit run.

## Objectives

1. Guarantee that every retained checkpoint has a defined purpose (production, recovery, analysis, lineage, experiment anchor, distillation, KD/SFT outcome).
2. Minimize redundant artifacts while preserving phase continuity and recovery capability.
3. Provide an automated pipeline to classify, score, recommend retention, and produce human-reviewable plans.
4. Enable safe pruning with reversible archive staging and integrity validation (optional hashes).
5. Maintain a canonical `checkpoint_registry.json` registry for downstream systems (deployment, evaluation, distillation).

---

## Lifecycle Stages

| Stage | Description | Typical Roles |
|-------|-------------|---------------|
| Draft | Early exploratory / transient | step_n, epoch_n |
| Active | Currently relevant for training progression | epoch_n, phase2_epoch, recovery_step_n |
| Candidate | Awaiting governance decision (auto-flagged) | redundant finals, dense recovery intervals |
| Protected | Explicitly locked; cannot be pruned | production, flagship, teacher, best_loss, unified_final_weights_only |
| Archived | Moved to `F:/models/archives/YYYYMMDD/` but retained for historical audit | legacy finals, deprecated experiment |
| Retired | Archived and scheduled for offline cold storage or deletion | superseded large intermediates |

---

## Retention Tiers

| Tier | Definition | Examples | Minimum Kept |
|------|-----------|----------|--------------|
| Tier 0 (Critical) | Essential for runtime or reproduction | production, flagship, tokenizer assets | 100% |
| Tier 1 (Strategic) | Phase anchors, best / final checkpoints | best_loss, unified_final_step_X_weights_only | Sparse span |
| Tier 2 (Recovery) | Needed for rollback / restart | recovery_step_{early,mid,final} | 3 per long run |
| Tier 3 (Analytical) | Comparative epochs/steps | earliest, mid, latest epoch samples | 2–4 per long run |
| Tier 4 (Ancillary) | Metadata, metrics, summaries | status_snapshot_*, training_summary_* | Almost all (cheap) |
| Tier 5 (Redundant) | Dense or duplicated states | near-identical sequential steps | 0 (prune) |

---

## Governance Pipeline (Automated + Review)

1. Inventory: `checkpoint_inventory.py` generates raw and aggregated catalogs.
2. Analysis: `checkpoint_retention_analysis.py` scores and classifies artifacts.
3. Governance Orchestration: `checkpoint_governance.py` merges inventory + retention + policy overrides into a registry.
4. Review Window: Human validation of proposed `prune` set (24–48h window recommended).
5. Archive Stage (Optional Safety): Move prune candidates to `F:/models/archives/<DATE>/` (no immediate deletion).
6. Final Prune: Delete archived after retention SLA passes (default 14 days) unless flagged for restoration.
7. Registry Commit: Update `checkpoint_registry.json` with final statuses and hash set (if enabled).

---

## Classification Heuristics (Current)

- Filename pattern roles: best, final_step, unified_final, recovery_step, production, flagship, teacher, phase2_epoch, epoch, distillation, weights_only.
- Redundancy detection: temporal density + identical size clusters + duplicate directory mirroring.
- Coverage rules: Ensure presence of (a) final/production, (b) early anchor, (c) mid anchor for long trajectories, (d) recovery triad.
- Ancillary preservation: JSON/CSV metadata kept by default (tiny footprint).

Future Enhancements:

- Integrate loss/score parsing from summaries.
- Hash-based binary equivalence pruning.
- Cross-run similarity clustering.
- SLA-based aging (e.g., auto-demote candidate after N days).

---

## Registry Schema (`checkpoint_registry.json`)

```jsonc
{
  "generated_at": "Month Day, Year HH:MM:SS AM/PM",
  "root": "F:/models/checkpoints",
  "summary": { "total_files": 0, "keep": 0, "prune": 0, "protected": 0, "reclaimable_mb": 0.0 },
  "artifacts": [
    {
      "rel_path": "b3/unified_sweet_spot/unified_final_step_25_weights_only.pth",
      "role": "final_step",
      "tier": "Tier 1",
      "decision": "keep",
      "status": "Protected",
      "score": 8.15,
      "size_mb": 1930.688,
      "hash": "<optional sha256>",
      "rationale": "High-value final weights-only variant"
    }
  ],
  "policy_version": "1.0.0"
}
```

---

## Override Mechanisms

| Mechanism | File | Purpose |
|-----------|------|---------|
| Protection list | `governance_overrides.json` | Force KEEP + Protected status |
| Exclusion list | same | Ignore certain transient directories |
| Hash enable | CLI `--hash` flag | Compute SHA256 (slower) |
| Min-span enforcement | internal | Ensures early/mid/late anchors |

Override File Example (`governance_overrides.json`):

```json
{
  "protect_patterns": ["*production*", "*flagship*", "*tokenizer.json", "*vocab.json", "*merges.txt"],
  "exclude_patterns": ["temp_experiments/*"],
  "force_keep": ["b3/unified_sweet_spot/best/best_loss_step_10.pth"],
  "force_prune": ["b3/unified_sweet_spot/unified_final_step_0.pth"],
  "hash": true
}
```

---

## Operational Cadence

| Frequency | Action |
|-----------|--------|
| Daily (if active training) | Inventory scan |
| Twice Weekly | Retention analysis refresh |
| Weekly | Governance review & archive stage |
| Monthly | Final prune & cold storage export |
| Before Major Release | Full hash + registry snapshot commit |

---

## Safety & Integrity

1. No destructive operations run without `--confirm-prune` flag.
2. All prune candidates staged to archive directory first.
3. Hash mismatch triggers automatic promotion to Protected.
4. Logs stored with timestamp in governance output directory.

---

## Versioning & Evolution

Policy Version: 1.0.0  
Any structural change increments minor; semantic change increments major.

---

## Immediate Next Steps

1. Adopt `checkpoint_governance.py` in scheduled task / CI.
2. Create initial `governance_overrides.json` capturing tokenizer & production protection.
3. Run with `--hash` once to baseline duplicates.
4. Manually review first retention plan before enabling `--stage-archive` or `--confirm-prune`.

---

*This document is part of the Permanent Governance Suite for ImpressionCore model lifecycle management.*