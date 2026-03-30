# B SERIES ROLLOUT PLAN August 30 2025

**Created:** August 30, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\B_SERIES_ROLLOUT_PLAN_August_30_2025.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

B-series Rollout Plan — ImpressionCore
Date: August 30, 2025

Objective

Launch the B-series initial rollout: validate data, finalize B3 model config, and run the first production training pass using the prepared shards.

Phases

Phase 0 — Preparation (1 week)

- Finalize B-series config schema and training hyperparameter defaults.
- Freeze dataset manifest contract and collect missing provenance metadata.
- Run aggressive mapping pass and manual spot-checks to get mapping coverage >= 90% for target modalities.

Phase 1 — Dry-run training (1–2 weeks)

- Use `train_bootstrap.py` extended harness for multi-epoch dry-run with small subset (10–50k vectors).
- Validate checkpointing, evaluation loop, and logging.
- Run retrieval + generation sanity checks using FAISS sample index.

Phase 2 — Full training (2–4 weeks)

- Scale up to full dataset shards, enable mixed precision, gradient accumulation, and longer schedules.
- Continuous monitoring, checkpointing, and early stopping based on validation metrics.

Phase 3 — Distillation & Validation (1–2 weeks)

- Run distillation pipelines (if applicable) and validate outputs against quality baselines.

Success metrics

- Training stability: no catastrophic OOMs; loss curves stable and improving on validation.
- Mapping coverage: >= 90% for target modalities.
- Model performance: metric thresholds to be defined by the working group (example: retrieval MRR, generation perplexity).

Risk & mitigations

- Risk: incomplete provenance metadata leading to incorrect mapping. Mitigation: conservative inclusion rules and manual spot-checking.
- Risk: mixed-dimension embeddings produce indexing errors. Mitigation: enforce encoder metadata and dimension checks before FAISS builds.

Governance

- Appoint an owner for the B-series working group and a reviewer responsible for compliance with Permanent Active Directives.

Immediate deliverables (this week)

1. `src/core/config/b_series.yaml` (schema stub)
2. Validator for `dataset_to_embedding_training_manifest.ndjson`
3. Aggressive mapping report (suggestions) and curated pass to raise coverage