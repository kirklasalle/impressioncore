# ARCHITECTURE REVIEW B SERIES August 30 2025

**Created:** August 30, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\ARCHITECTURE_REVIEW_B_SERIES_August_30_2025.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

ImpressionCore — Architecture Review (B-series)
Date: August 30, 2025

Purpose

This document summarizes the current ImpressionCore architecture relevant to the B-series rollout, highlights gaps, and recommends concrete next steps to prepare the codebase and infrastructure for B-series training.

Scope

- Core runtime components under `src/core/`
- Data & embedding storage conventions (F:/ models & embeddings)
- Training and inference tooling in `src/training/` and `src/dev_tools/`

Current state (summary)

- Multimodal B3 architecture design documents exist under `docs/` (B3 architecture, distillation guides).
- Data pipeline tooling: cataloging, mapping, sharding, sample FAISS index, and a PyTorch bootstrap trainer implemented in `src/dev_tools/`.
- Storage: embeddings and models are expected under F:/ (F:/models, F:/data) per project conventions; repository holds tools to index and map files into `src/memlog/` artifacts.

Key architectural components to finalize for B-series

1. Model interface and config contract
   - Define a canonical B-series model config schema (params, dims, MoE settings, attention heads, tokenizer rules).
   - Implement a config loader in `src/core/config/` with validation and canonical defaults.

2. Data orchestration
   - Standardize dataset schema (metadata keys, modality tags, canonical path patterns) and embed the schema in `docs/reference/`.
   - Authoritative manifest generator: a single authoritative dataset→embedding manifest (ndjson) that training consumes.

3. Training harness
   - Production trainer (checkpointing, distributed-friendly hooks, float/mixed precision selection, gradient checkpointing) in `src/training/`.
   - Evaluation and metrics collectors (TensorBoard or JSONL logs) and checkpoint rotate/keep-best logic.

4. Storage & retrieval
   - Shard format (numpy shards + index.jsonl is acceptable). Consider adding Arrow/Parquet or TFRecord for faster IO if needed.
   - FAISS index management policies (build/test index for retrieval evaluation only; production indices kept in F:/models/indices).

Gaps and recommendations

- Gap: No canonical B-series config file — Create `src/core/config/b_series.yaml` and loader.
- Gap: Mapping coverage incomplete — invest in metadata enrichment (dataset provenance) to raise mapping quality above 90% for target modalities.
- Gap: Training harness needs scaling features — implement scheduler, gradient accumulation, mixed precision, and checkpoint rotation.

Immediate next steps (technical)

1. Create canonical B-series config schema and loader (small PR). 2–3 hours.
2. Freeze dataset manifest contract and add validation code (ndjson schema + small validator). 4–6 hours.
3. Harden training harness (checkpoint rotation, eval logging, mixed precision) and add CI smoke tests. 1–2 days.

Ownership

- Recommendation: assign a small working group (1–2 engineers) to own the B-series architecture sprint (2 weeks) and a reviewer for compliance with the Permanent Active Directives.