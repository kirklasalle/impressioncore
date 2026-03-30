# Pipeline run: August 30, 2025

Timestamp: August 30, 2025 09:00:00 AM

Summary

- Completed a full data cataloging and embedding mapping session. Produced safe, streaming catalogs and mapping artifacts to support training data extraction and indexing.

Artifacts (selected)

- `src/memlog/dataset_catalog_20250829.json` — line-delimited dataset catalog
- `src/memlog/dataset_catalog_summary_20250829.json` — compact summary
- `src/memlog/dataset_to_embedding_mapping.ndjson` — initial mapping
- `src/memlog/dataset_to_embedding_mapping_refined.ndjson` — refined mapping
- `src/memlog/dataset_to_embedding_mapping_refined2.ndjson` — heuristics-improved mapping
- `src/memlog/dataset_to_embedding_explicit.ndjson` — explicit per-dataset mapping
- `src/memlog/dataset_to_embedding_training_manifest.ndjson` — training manifest
- `src/memlog/embeddings_manifest.ndjson` — embedding inspection manifest
- `src/memlog/chunk_index_dataset_range_map.ndjson` — chunk map
- `src/memlog/chunk_index_dataset_range_map_improved.ndjson` — improved chunk map
- `src/memlog/faiss_sample_refined.index` — FAISS sample index
- `src/memlog/faiss_sample_refined_ids.ndjson` — FAISS ids
- `src/memlog/shards/` — shard files and `index.jsonl`

Scripts created/used (under `src/dev_tools/embedding_checks/` and `src/dev_tools/training/`)

- generate_coverage_and_examples.py
- sample_embedding_validator.py
- shape_consistency_checker.py
- build_dataset_embedding_map.py
- refine_mapping_with_batches.py
- build_chunk_range_map.py
- improve_chunk_heuristics.py
- extract_and_shard_embeddings.py
- pytorch_shard_dataset.py
- train_bootstrap.py

Notes

- All Python executions were run under the project venv: `.venv310` (Python 3.10).
- Safety: numpy `.npy` files were opened using `mmap_mode='r'` to avoid large memory allocations.
- FAISS indices were built using sampled embeddings and dominant-dimension selection to avoid mixed-dimension failures.

Next steps

- Use the produced `dataset_to_embedding_training_manifest.ndjson` and shard index for B3 training.
- Add checkpointing, evaluation, and scheduler to the `train_bootstrap.py` to move toward production training.

Responsible: GitHub Copilot (actions performed under `.venv310`)
