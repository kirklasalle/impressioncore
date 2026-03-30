# F: Drive 500GB Optimization Plan for ImpressionCore + ImpressionCoreB3-Colossus

**Date:** February 21, 2026  
**Scope:** Dedicated `F:/` for project data and models  
**Constraint:** Single 500GB-class volume (`476.94 GB` formatted capacity)

---

## 1) Canonical Top-Level Contract (Enforced)

`F:/` must contain exactly two project directories:

- `F:/data` — all modality data, datasets, embeddings, indices, caches, catalogs, data reports
- `F:/models` — model artifacts only: checkpoints, deployable models, distillation outputs, model metadata/logs

This contract is now aligned with active code paths and operational docs.

---

## 2) Current Measured State (Audit Snapshot)

From `python src/tools/f_drive_audit.py`:

- Drive total: `476.94 GB`
- Drive used: `424.24 GB`
- Drive free: `52.70 GB`

### `F:/data` usage (`375.96 GB`)

- `raw`: `196.68 GB`
- `huggingface_cache`: `79.68 GB`
- `processed`: `49.65 GB`
- `embeddings`: `33.81 GB`
- `datasets`: `15.80 GB`
- Other subdirs are negligible

### `F:/models` usage (`42.03 GB`)

- `checkpoints`: `36.72 GB`
- `production`: `1.89 GB`
- `teachers`: `1.94 GB`
- `base`: `1.08 GB`
- Remaining model subdirs are low usage

---

## 3) Critical Capacity Findings

1. **Headroom is tight**: only `52.70 GB` free (~11% of formatted capacity).
2. **Primary pressure is in `F:/data`**, especially:
   - `raw` (`196.68 GB`)
   - `huggingface_cache` (`79.68 GB`)
   - `processed` (`49.65 GB`)
3. **Model storage is healthy today** (`42.03 GB`), but checkpoint growth can spike quickly during long runs.

---

## 4) Target Capacity Budget (Basic → World Class)

### Basic Standard (minimum stable)

- Keep `>= 15%` free space at all times (`>= 71.5 GB` free)
- Hard limit checkpoints retained per run
- Clear stale package/model caches monthly

### Strong Standard (production-ready)

- Keep `>= 20%` free (`>= 95.4 GB` free)
- Enforce rolling retention for raw/processed snapshots
- Maintain manifest-backed provenance for every model checkpoint and embedding index

### World Class Standard (recommended target)

- Keep `>= 25%` free (`>= 119 GB` free)
- Tiered storage policy with strict lifecycle:
  - Hot (`0-14 days`): active run artifacts
  - Warm (`15-60 days`): recent validated assets
  - Cold (`>60 days`): archive/export + prune local copy
- Weekly automated quota/audit report with trend lines

---

## 5) Directory Design Enhancements

### `F:/data` enhancements

- Keep and standardize:
  - `raw/` by modality: `raw/text`, `raw/audio`, `raw/video`, `raw/vision`
  - `datasets/` curated and training-ready sets
  - `processed/` transient transforms with lifecycle tags
  - `embeddings/` all vector stores + FAISS indices + manifests
  - `catalogs/` inventories, hashes, lineage
  - `system/` data-side telemetry
- Add policy docs/manifests:
  - `F:/data/catalogs/storage_policy.json`
  - `F:/data/catalogs/retention_windows.json`

### `F:/models` enhancements

- Keep and standardize:
  - `checkpoints/` training snapshots
  - `production/` deployable validated models only
  - `deployment/` release bundles
  - `base/`, `teachers/`, `distillation/`, `experiments/`, `training/`, `management/`
- Require manifest sidecar per checkpoint/model:
  - SHA256, source dataset manifest, trainer version, eval metrics, promotion status

---

## 6) High-Impact Improvements (Immediate)

1. **Cache pressure reduction**
   - Prune `F:/data/huggingface_cache` aggressively with a pinned allowlist for active models.
2. **Checkpoint retention cap**
   - Keep `N` latest + `M` milestone checkpoints; auto-delete intermediate snapshots.
3. **Raw data dedupe**
   - Content hash dedupe for large raw corpora before new ingest.
4. **Processed data TTL**
   - Expire processed artifacts older than retention window unless pinned.
5. **Embedding lineage**
   - Every index references exact input manifest + model/version hash.

---

## 7) What Was Implemented in This Pass

- Moved `F:/models/embeddings` to `F:/data/embeddings/models_embeddings`
- Moved `F:/data/training/checkpoints` to `F:/models/checkpoints/data_training_checkpoints`
- Moved `F:/data/english-grammar` to `F:/data/datasets/english-grammar`
- Updated active code/config paths to match migration:
  - `src/training/data/grammar_rag_loader.py`
  - `src/core/models/impressioncore_b3_architecture.py`
  - `src/training/configs/models/b3_slim32m_sanity.json`
  - `src/deployment/inspect_grammar_data.py`
  - `src/deployment/ingest_grammar_corpus.py`
  - `src/data/cleanup_grammar.py`
  - `src/data/inspect_oed.py`
  - `src/deployment/verify_loss_alignment.py`
  - `src/data/pipelines/embed_f_drive_full.py`
  - `src/core/config/b3_pretraining_config.yaml`

---

## 8) Next Engineering Actions (Priority)

1. Add weekly **quota monitor** task outputting top growth drivers.
2. Add **promotion gate**: checkpoint → production requires metrics threshold + manifest completeness.
3. Add **cold export workflow** for >60-day artifacts to external archive.

### Implemented: Retention Automation

- New utility: `src/tools/f_drive_retention_manager.py`
- Modes:
  - Dry-run (default): plans cleanup only
  - Enforce (`--enforce`): executes deletions
- Current dry-run command:
  - `python src/tools/f_drive_retention_manager.py --target-free-gb 95 --preview-limit 20`
- Dry-run result snapshot:
  - `free_gb=52.70`, target `95.00`, shortfall `42.30`
  - `plan_reclaimable_gb=104.70`
  - by reason: `hf_cache_age=79.68 GB`, `processed_age=24.64 GB`, `checkpoint_overflow=0.37 GB`
  - planned reclaim for target: `42.70 GB` (meets shortfall)

### Executed: First Enforced Cleanup Pass

- Command:
  - `python src/tools/f_drive_retention_manager.py --target-free-gb 95 --preview-limit 20 --enforce`
- Enforcement outcome:
  - `processed_candidates=106047`
  - `reclaimed_gb=42.70`
  - `target_shortfall_gb=42.30`
- Post-cleanup audit (`python src/tools/f_drive_audit.py`):
  - `DRIVE_USED_GB=381.43`
  - `DRIVE_FREE_GB=95.50`
  - `F:/data` reduced to `333.26 GB`
  - `F:/models` unchanged at `42.03 GB`

---

## 9) Success Criteria

- `F:/` remains exactly two top-level directories (`data`, `models`)
- Active source code references no deprecated F-drive paths
- Free capacity maintained above chosen floor (target: world class `>=25%`)
- Every production model and major embedding index has reproducible lineage metadata

---

## 10) Builder Integration (Complete World-Class Walkthrough)

### Backend APIs wired into Builder

- `GET /api/v1/builder/features`
  - Returns complete catalog for Pipeline, Knowledge, Advanced sections, and supported backend functions (active/stub).
- `GET /api/v1/builder/storage/status`
  - Returns live `F:/` totals, `F:/data` + `F:/models` subdirectory summaries, and contract checks.
- `POST /api/v1/builder/storage/retention`
  - Runs retention in dry-run or enforce mode through Builder.
  - Supports: `target_free_gb`, `hf_cache_age_days`, `processed_age_days`, `keep_checkpoints_per_dir`, `preview_limit`, `enforce`.

### Builder Client wiring

- API client now exposes:
  - `getBuilderFeatures()`
  - `getBuilderStorageStatus()`
  - `runBuilderStorageRetention(payload)`
- Walkthrough UI now includes:
  - Full feature/function coverage cards
  - Live F-drive capacity control panel
  - Retention preview and enforce actions
  - Supported function inventory with status labels

### Dedicated Storage Module (Builder UI)

- New page route: `/storage-control`
- Sidebar integration under **Advanced → Storage Control**
- Preset policies included:
  - **Basic** (`72 GB` free target)
  - **Strong** (`95 GB` free target)
  - **World-Class** (`119 GB` free target)
- Operations exposed in page:
  - Live status refresh (`F:/` total/used/free)
  - Contract check (`/data` + `/models`)
  - Retention preview (dry-run)
  - Retention enforce (cleanup execution)
  - Top directory usage views for both `F:/data` and `F:/models`

### Files Updated for Builder Integration

- `src/interfaces/web/server.py`
  - Added Builder feature-catalog and storage management endpoints.
- `src/interfaces/builder_client/src/lib/api.js`
  - Added new client calls for Builder feature/storage APIs.
- `src/interfaces/builder_client/src/pages/WalkthroughPage.jsx`
  - Upgraded to complete walkthrough + storage operations console.
- `src/interfaces/builder_client/src/pages/StorageControlPage.jsx`
  - Dedicated world-class storage operations page with policy presets.
- `src/interfaces/builder_client/src/main.jsx`
  - Added route mapping for `/storage-control`.
- `src/interfaces/builder_client/src/lib/constants.js`
  - Added sidebar nav entry for Storage Control.
