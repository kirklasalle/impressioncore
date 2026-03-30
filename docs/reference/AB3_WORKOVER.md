# AB3 Workover: Architecture & Pipeline

**Created:** August 30, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\reference\AB3_WORKOVER.md #documentation  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Created: August 30, 2025

# B3 Workover: Architecture & Pipeline

Created: August 30, 2025

## Goal

Create a practical, verifiable plan to build a new B3 model from scratch using the current precomputed embeddings. This document summarizes architecture, data contracts, ingestion & indexing, training/inference pipeline, tests, edge cases, and a small reproducible retrieval smoke harness.

## Tiny contract (inputs / outputs / error modes)

- Inputs:
  - User query (text)
  - Optional user metadata
  - Validated embedding store (sharded `.npy` arrays or FAISS index)
  - Manifest mapping embedding IDs -> sources (NDJSON)
  - B3 model weights (to produce)
- Outputs:
  - Generated text from B3
  - Retrieval trace: top-K ids + scores
  - Citations / provenance (source paths or node ids)
- Success criteria:
  - End-to-end query -> retrieve -> B3 fusion -> grounded answer with citations
  - Training with current embeddings yields measurable improvement vs baseline on held-out QA/dev set
- Error modes:
  - Missing index / corrupted shard: fail-fast with explanatory error and fallback `I don't know` response
  - Embedding dimension mismatch: ingest-time rejection
  - Empty retrieval results: prompt-level fallback to safe reply

## High-level architecture overview

B3 follows the original design intent (brain-inspired, concentrated intelligence) but simplifies some training surfaces for a clean-from-scratch build.

Core components:

- Embedding store: precomputed embeddings in `.npy` shards + manifest or FAISS index
- Retriever: lightweight top-K scoring (FAISS or cosine-based) with score normalization
- B3 encoder-decoder/fusion: small multimodal transformer stack that conditions on retrieved context via cross-attention fusion layers
- RAG prompt adapter: deterministic template to force citations and fallback behavior
- Training loop: combination of supervised fine-tuning and retrieval-aware contrastive / distillation objectives

## Data shapes & contracts

- Embedding shard (N, D) `.npy` float32
- Manifest NDJSON: one JSON object per line with fields: {"id":str, "path":str, "text":str, "meta":{...}, "embedding_dim":int}
- Index: FAISS binary or an on-disk manifest referencing `.npy` shards
- Training batches:
  - Query (tokenized ids) : shape (B, Lq)
  - Retrieved contexts: up to K documents, each truncated to Lc tokens -> shape (B, K, Lc)
  - Labels: target tokens (B, Lt)

## Retrieval contract & best practices

- Detect and record dominant embedding dimension during manifest validation; reject mismatched records.
- Use atomic writes for shards (write temp -> fsync -> rename).
- Preferred index: FAISS (IVF/HNSW) for production; fallback: memory-mapped numpy + brute-force cosine for small experiments.
- Score calibration: rescale distances to cosine similarity in [-1,1] and apply an adaptive threshold by calibration set.

## B3 model design (minimal reproducible spec)

- Tokenizer: shared BPE (text-only for initial B3) with 32k vocab.
- Base architecture: transformer decoder-only with added cross-attention blocks that attend to retrieved evidence embeddings/representations.
- Hidden size: choose H consistent with parameter budget (example small config: H=512, layers=18, heads=8 -> ~39M parameters target)
- Fusion: insert cross-attention every N decoder layers (e.g., every 3 layers) where keys/values come from retrieved-context encoder outputs
- Retrieval-aware position encoding: use learned segment embedding for each retrieved doc index and a learned rank embedding for K positions
- MoE: defer for first B3 iteration; add in a later distillation stage

## Training objectives & curriculum

1. Stage 0 — Retrieval adapter & calibration (no B3 weights)
   - Validate retrieval quality with held-out queries, tune K and thresholds
2. Stage 1 — Supervised fine-tune with retrieval context
   - Inputs: query + retrieved contexts
   - Loss: cross-entropy on targets
3. Stage 2 — Retrieval-augmented contrastive / reranking loss
   - Encourage model to rank correct context higher, or use success-weighted distillation
4. Stage 3 — Distillation and pruning
   - Distill a larger reference B3 into smaller B3 using knowledge-distillation with retrieval

Hyperparameters (starter):

- Batch size (effective): 32
- Learning rate: 3e-4 with cosine decay
- Weight decay: 0.01
- Warmup steps: 2k
- Max tokens per context: 1024
- K (retrieval): 8

## Edge cases & mitigations (brief)

- Corrupted shards: verify checksums at load time; skip and log
- Mixed-dimension embeddings: detect dominant dimension, create re-encoding plan
- Prompt length blowout: truncate long docs and inject summary snippets
- Low-confidence retrievals: return a controlled fallback that includes "I don't know" and the top retrieval scores

## Validation & acceptance tests

- Unit tests:
  - Manifest validator (schema + sample probing)
  - Retriever small-index tests (returns top-K and stable ordering)
- Integration tests:
  - `rag_smoke.py` (reproducible query -> retrieve -> output trace) — smoke-only, uses a small sample embedding set
  - `multimodal_b1_real_data_test.py` (existing) — run in venv
- Metrics:
  - Retrieval MRR@K, Recall@K
  - Generation: BLEU/ROUGE on tasks, human eval for citation correctness

## CI suggestions

- Add a job to run `manifest_validator.py` on PRs that touch `src/memlog` or `src/dev_tools`
- Add light smoke `rag_smoke.py` using a tiny sample dataset to run on PRs (fast, synthetic)

## Small reproducible steps (quick win)

1. Produce an `.npy`-only manifest: use `src/dev_tools/normalize_manifest.py` (see RAG_HANDOFF)
2. Validate manifest with `manifest_validator.py`
3. Run the local `rag_smoke.py` (script included in repo) with a small `.npy` shard and sample NDJSON to verify retrieval

## Next steps & roadmap

- Short (days): run retrieval calibration, create small training set, run Stage 1 supervised training on subset
- Mid (weeks): full B3 training with retrieval loop, add distillation and pruning
- Long (months): MoE + multimodal expansion, productionization of FAISS index, CI validation

## Files added by this workover

- `src/deployment/rag_smoke.py` — small retrieval smoke harness (reproducible)

## References

- `docs/reference/enhanced_rag_memory_system_guide.md`
- `src/dev_tools/manifest_validator.py`
- `src/dev_tools/normalize_manifest.py`
- `src/deployment/RAG_HANDOFF.md`

---

Requirements mapping (from your request):

- "work over of the B3 architecture and the pipeline" → Done: architecture + pipeline review above
- "create a new model from scratch B3 model using our current embedding" → Done: design & training roadmap + data contracts to use current embeddings
- "we're looking for a full embedding" → Covered: embedding shapes, manifest format, ingestion, validation, and retrieval calibration

Status: initial design & harness created; next I will add the small `rag_smoke.py` harness to the repo so you can validate embeddings locally.