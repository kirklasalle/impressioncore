# DATA EMBEDDING REQUIREMENTS B SERIES August 30 2025

**Created:** August 30, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\DATA_EMBEDDING_REQUIREMENTS_B_SERIES_August_30_2025.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

ImpressionCore — Data & Embedding Requirements (B-series)
Date: August 30, 2025

Purpose

Define the minimal data and embedding requirements for the B-series training rollout: modalities, file formats, metadata, and recommended storage policies.

Modalities and minimal schema

- Text
  - File types: .txt, .jsonl (one document per line), canonicalized to UTF-8 NFC.
  - Required metadata: id, source, split (train/val/test), language, timestamp.

- Image
  - File types: .jpg/.png for raw, embeddings as .npy (float32, 1×D or N×D).
  - Metadata: id, source, width, height, color_space, transform notes.

- Audio
  - File types: .wav for raw, embeddings as .npy; preferred sample rate noted in metadata.
  - Metadata: id, source, duration_ms, sample_rate.

- Video (optional for B-series initial)
  - Prefer pre-extracted frame embeddings (.npy) and clip-level metadata.

Embedding format and conventions

- Format: NumPy .npy, dtype float32. Accept 1-D vector per file or 2-D array per file (N×D) for batch-sharded embeddings.
- Naming: use consistent basename patterns. Example: datasetX_chunk_00001.npy or datasetX.embed. Ensure chunk numbers are zero-padded.
- Dimension consistency: embeddings for a given model/encoder must share a dimension D. If mixed dims exist, store a small manifest indicating encoder type per embedding file.

Storage & indexing

- Centralized storage: F:/models and F:/data for large artifacts; always emit a lightweight NDJSON manifest into `src/memlog/` with fields: {id, path, dtype, shape, encoder, created_at}.
- Sharding: produce shards of predictable size (10k vectors recommended) and accompanying `index.jsonl` mapping dataset entries to shard/offset.
- Index: FAISS indices should be built from curated subsets (sampling) and stored under `F:/models/indices/` with versioned names.

Provenance & validation

- Every embedding must record: original data id, encoder name+version, preprocessing steps, and timestamp.
- Provide validator scripts that can sample and open .npy files via mmap to check dtype and shape without full load.

Acceptance criteria for training

1. A validated training manifest (`dataset_to_embedding_training_manifest.ndjson`) exists with >= 90% mapping for target modalities.
2. All selected embeddings are float32 and have a documented encoder field.
3. Shards are accessible via `index.jsonl` and loadable by `ShardDataset` without OOM on GTX 1050 Ti (4GB VRAM) for the planned batch sizes.