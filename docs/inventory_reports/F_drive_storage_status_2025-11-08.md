# F: Drive Modalities Allocation – November 8, 2025

**Created:** November 08, 2025  
**Updated:** December 29, 2025  
**Author:** GitHub Copilot  
**Tags:** #ids #documentation #inventory #storage #datasets #docs\inventory_reports\F_drive_storage_status_2025-11-08.md  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

This report summarizes the current state of the F: drive multimodal data lake after catalog analysis on November 8, 2025. The focus is confirming Phase 1 dialog readiness, quantifying dominant storage consumers, and establishing retention plans for reproducible but bulky assets.

---

## Phase 1 Dialog Corpora Status

- Generated all missing Phase 1 JSONL corpora via `src/training/data/tools/generate_phase1_dialog_corpora.py`.
- New training files: `train_empathy.jsonl`, `train_regulator_remediation.jsonl`, `train_conflict_resolution.jsonl`.
- New validation files: `validation_regulator.jsonl`, `validation_conflict.jsonl`.
- Each record follows the manifest schema with explicit modality payloads (audio phoneme strings and face metadata where required).
- `validate_phase1_manifest.py` now exits cleanly, confirming every manifest path resolves to real data.

## Storage Summary Snapshots

| Path Segment | Files | Size |
| --- | --- | --- |
| `data/datasets` | 1,863,044 | 252.94 GB |
| `data/embeddings` | 98,399 | 30.07 GB |
| `data/datasets/vision` | 718,830 | 127.11 GB |
| `data/datasets/text` | 299,512 | 41.14 GB |
| `data/datasets/audio` | 620,028 | 17.62 GB |
| `huggingface_cache/hub` | 463 | 81.28 GB |
| `huggingface_cache/datasets` | 10 | 4.28 GB |
| `models/checkpoints` | 123 | 47.93 GB |
| `models/teachers` | 28 | 2.08 GB |

_Data source: `src/dev_tools/storage/summarize_f_drive_catalog.py` executed with depth filters (November 8, 2025)._

## Hugging Face Cache Retention Plan

1. Catalog reproducible datasets before removal (Common Voice, Librispeech, MS MARCO, Squad, etc.) using new extension filters.
2. Export a dependency map into `docs/inventory_reports/hf_cache_retention_register.md` (completed November 8, 2025 12:52 PM) that lists which training pipelines depend on each cache shard.
3. Stage the 81 GB `huggingface_cache/hub` content into `F:/models/archives/hf_cache_2025-11-08` for two-week observation; delete only after confirming pipelines recreate the shards on demand.
4. Purge stale `.incomplete` artifacts immediately—they are safe to delete because no pipeline references them.
5. Automate a monthly `summarize_f_drive_catalog.py --first-filter huggingface_cache` run to monitor regrowth.
6. Latest on-demand snapshot (November 8, 2025 1:10 PM) logged to `src/training/distillation/eval_outputs/catalog_deltas/catalog_summary_20251108_131014.txt` using the same summarizer pipeline.

## Model Checkpoint Triage

- Run `python manage_f_models.py --status` to list registered checkpoints versus loose files under `models/checkpoints`.
- Import the active Colossus and HOPE checkpoints with `manage_f_models.py --import --path F:/models/checkpoints/<checkpoint>` so lifecycle metadata lands in the managed registry.
- After import, move superseded checkpoints older than 60 days into `F:/models/archives/checkpoints_retain/` and compress using `Compress-Archive` with timestamped naming.
- Remove redundant teacher snapshots once their distilled variants are verified (`models/teachers/dialogpt_small` and `dialogpt_medium`).
- Archived the October 19–27, 2025 Colossus training sessions to `F:/models/archives/colossus/colossus_training_sessions_oct2025.zip` while registering the baseline and regulator remediation builds in managed storage (November 8, 2025). Checksum (`CACACDBD86A36A438DE1EC24E70D7B0113845D607E74DEEC4468487710CDAD4D`) recorded after successful extraction test to `F:/models/archives/colossus/verification_oct2025/`.

## Next Actions

1. Bundle the catalog summarizer with the on-demand Colossus prep workflow so every manual run emits a storage delta log (latest capture: `src/training/distillation/eval_outputs/catalog_deltas/catalog_summary_manual_20251108_130500.txt`); adjust documentation if the output path changes.
2. Cross-link the Phase 1 corpora generator script from the training playbook to keep warm-start environments reproducible.
3. Schedule the next checkpoint archival sweep after confirming new imports appear in `manage_f_models.py --status` output.