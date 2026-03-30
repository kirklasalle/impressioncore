**Created:** November 7, 2025
**Updated:** November 7, 2025
**Author:** GitHub Copilot
**Tags:** #ids #standardized_header #src\memlog\b3_training\dialog_phase1_export_20251107_174129.md #training #datasets
**Category:** System Logs
**Status:** Active

# Dialog Phase 1 Shard Export — November 7, 2025 12:41:29 PM

## Summary

- Source manifest: `D:/Projects/impressioncore/src/training/configs/datasets/dialog_phase1_manifest.json`
- Export root: `F:/data/datasets/dialog/phase1`
- Export manifest: `F:/data/datasets/dialog/phase1/dialog_phase1_manifest.json`
- Export tool: `python -m src.training.datasets.dialog_phase_dataset --manifest ... --output-root ... --overwrite`
- Shards copied: 4 (train ×3, validation ×1)
- Operation mode: Full export (dry-run verified beforehand)

## Shard Inventory

| Split | Destination | Records |
| --- | --- | --- |
| train | `F:/data/datasets/dialog/phase1/train/train_core.jsonl` | 21 |
| train | `F:/data/datasets/dialog/phase1/train/train_supportive.jsonl` | 20 |
| train | `F:/data/datasets/dialog/phase1/train/train_strategic.jsonl` | 20 |
| validation | `F:/data/datasets/dialog/phase1/validation/validation_core.jsonl` | 5 |

## Follow-Up

- Updated local manifest to reference the exported shards for Phase 1 warm-start workflows.
- Next verification step: run `dialog_phase1_warm_start.py` against the new manifest to confirm loader access to F:/ sources.
- Archive this report in memlog for future shard provenance audits.
