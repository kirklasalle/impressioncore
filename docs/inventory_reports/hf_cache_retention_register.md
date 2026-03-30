# Hugging Face Cache Retention Register – November 8, 2025

**Created:** November 08, 2025  
**Updated:** December 29, 2025  
**Author:** GitHub Copilot  
**Tags:** #ids #documentation #inventory #hf_cache #docs\inventory_reports\hf_cache_retention_register.md  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

This register tracks the 85.26 GB of Hugging Face cache artifacts resident on the F: drive as of November 8, 2025. The goal is to preserve reproducibility for critical pipelines while reclaiming space via staged archives and routine purges.

---

## Inventory Snapshot

| Cache Entry | Local Path | Size (GB) | Primary Use | Retention Decision | Review Date |
| --- | --- | --- | --- | --- | --- |
| `datasets--natural_questions` | `F:/huggingface_cache/hub/datasets--natural_questions` | 51.69 | `download_explanatory_qa_alternative.py` (Colossus nightly Q&A expansion) | Stage to `F:/models/archives/hf_cache_2025-11-08` after dependency verification; retain archive for two weeks | November 22, 2025 |
| `datasets--librispeech_asr` | `F:/huggingface_cache/hub/datasets--librispeech_asr` | 20.56 | B3 audio embedding refresh (`src/training/b3/b3_production_training.py`) | Retain in-place (critical audio backbone); schedule checksum audit | December 6, 2025 |
| `datasets/ms_marco` (processed) | `F:/huggingface_cache/datasets/ms_marco` | 3.99 | MS MARCO passage extraction (`download_explanatory_qa_alternative.py`) | Retain processed split; stage raw hub copy with natural questions archive | November 22, 2025 |
| `datasets--ms_marco` (hub) | `F:/huggingface_cache/hub/datasets--ms_marco` | 1.96 | Same as above | Stage with natural questions; delete after archive + pipeline smoke test | November 22, 2025 |
| `datasets--wikitext` | `F:/huggingface_cache/hub/datasets--wikitext` | 0.29 | WikiText-103 loaders (`src/dev_tools/scripts/miscellaneous/phase3_trust_remote_code_executor.py`) | Retain; regenerate embeddings depend on cached shards | December 6, 2025 |
| `models--gpt2` | `F:/huggingface_cache/hub/models--gpt2` | 0.51 | GPT-2 distilled teacher (fallback tokenizer scaffolding) | Retain permanently; mirror to `F:/models/checkpoints/gpt2_reference` | November 15, 2025 |
| `models--microsoft--DialoGPT-small` | `F:/huggingface_cache/hub/models--microsoft--DialoGPT-small` | 0.00¹ | Core conversational backbone, safetensors mirror under `F:/models/checkpoints` | Verify mirror; remove duplicate weights post-confirmation | November 15, 2025 |
| `datasets--squad` | `F:/huggingface_cache/hub/datasets--squad` | 0.02 | `download_squad_dataset.py` convenience cache | Safe to purge after confirming processed JSON assets exist | November 15, 2025 |

¹Displays as 0 GB when rounded; raw Metrics show 1.4 MB of metadata.

**Measurement source:** PowerShell inventory executed November 8, 2025 12:47 PM using `Get-ChildItem` with recursive `Measure-Object` aggregation.

---

## Dependency Mapping

- **Natural Questions:** Consumed by `download_explanatory_qa_alternative.py` for explanatory QA and by IDS dataset source registry (`.mcp/impressioncore-eds/config/dataset_sources.py`). Removal requires confirming nightly Colossus prep regenerates shards within 12 hours.
- **MS MARCO:** Same pipeline as above; processed splits in `F:/huggingface_cache/datasets/ms_marco` feed the QA augmentation harness. Archive raw hub files only after ensuring processed splits remain intact.
- **LibriSpeech ASR:** Referenced by B3 production training loaders for audio embeddings (`b3_production_training.py`, `b3_phase1_production_training.py`). Deletion would break audio alignment; cache must remain fully online.
- **WikiText:** Utilized by knowledge expansion scripts (`src/inference/b3_knowledge_expansion.py`) and CLI builder prototypes. Supports text embedding refresh tasks—retain until alternate mirroring is created under `F:/data/datasets/text`.
- **DialoGPT-small / GPT-2:** Provide teacher checkpoints and tokenizer metadata for conversational trainers (`b3_hope_*` scripts). Both must remain cached or mirrored before purging hub copies.

---

## Action Checklist

1. **Archive staging (Due November 10, 2025):**
   - Compress `datasets--natural_questions` and `datasets--ms_marco` hub trees into `F:/models/archives/hf_cache_2025-11-08`.
   - Log SHA256 checksums in `F:/models/archives/hf_cache_2025-11-08/checksums.txt`.

2. **Pipeline smoke tests (Due November 12, 2025):**
   - Run `python download_explanatory_qa_alternative.py --smoke natural_questions` to confirm automatic redownload works from staged archive.
   - Capture console transcript in `docs/reports/cache_retention/2025-11-12_nq_redownload.txt`.

3. **Mirror verification (Due November 15, 2025):**
   - Confirm `models--gpt2` and `models--microsoft--DialoGPT-small` are mirrored under `F:/models/checkpoints` by executing `python manage_f_models.py --status --detail mirrored`.
   - Once mirrored, trim redundant hub snapshots while keeping tokenizer JSON.

4. **Monthly audit (Due December 6, 2025):**
   - Re-run `summarize_f_drive_catalog.py` with `--first-filter huggingface_cache --group-depth 2`.
   - Update this register with delta sizes and decisions.

---

## Purge Candidates (Post-Staging)

- `.incomplete` files under `F:/huggingface_cache/hub/.locks` – delete immediately after archive staging; no pipeline dependencies.
- Residual cache metadata for `datasets--mozilla-foundation--common_voice_*` (`<1 MB` each) – keep until phoneme regeneration pipeline is mirrored to F: drive; classify as negligible footprint.
- `datasets--squad` processed tarballs (<20 MB) – purge only after verifying `F:/data/qa_datasets/squad` contains latest generated JSON files.

---

## Colossus Checkpoint Lifecycle (October 2025)

| Artifact | Action | Archive Path | Notes |
| --- | --- | --- | --- |
| `colossus` training sessions (October 19–27, 2025) | Compressed archive | `F:/models/archives/colossus/colossus_training_sessions_oct2025.zip` | Registered `20251027_154628` baseline and `20251027_135845` regulator remediation builds under managed distillation inventory before archiving remaining sessions. |

Latest on-demand catalog summary: `src/training/distillation/eval_outputs/catalog_deltas/catalog_summary_manual_20251108_130500.txt` (generated November 8, 2025 1:05 PM).

**Validation:** SHA256 `CACACDBD86A36A438DE1EC24E70D7B0113845D607E74DEEC4468487710CDAD4D` verified November 8, 2025 12:57 PM; sample extraction succeeded to `F:/models/archives/colossus/verification_oct2025/`.

---

## Follow-up Documentation

- Once archive staging completes, update `docs/inventory_reports/F_drive_storage_status_2025-11-08.md` next actions section with completion notes.
- Add IDS tag `hf_cache_register` after the first monthly audit to simplify discovery.
- Catalog delta logs recorded so far: `src/training/distillation/eval_outputs/catalog_deltas/catalog_summary_20251108_121530.json` (monitor with catalog flag) and `src/training/distillation/eval_outputs/catalog_deltas/catalog_summary_manual_20251108_130500.txt` (direct summarizer capture); update if subsequent runs relocate the output.

---

_Last reviewed November 8, 2025 12:55 PM by GitHub Copilot._