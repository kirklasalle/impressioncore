Embedding sample validator
==========================

Purpose
-------

Quickly validate a small sample of `.npy` embedding files referenced by the repository's line-delimited dataset catalog (`src/memlog/dataset_catalog_20250829.json`). The validator is conservative and uses numpy's mmap mode to avoid high memory use.

Files added
-----------

- `sample_embedding_validator.py` - script to discover `.npy` paths from known catalog paths and inspect shape/dtype using mmap.

Usage
-----

Run from the repository root. Example (PowerShell):

```powershell
python src/dev_tools/embedding_checks/sample_embedding_validator.py --sample 20
```

Notes & next steps
------------------

- If your catalog is stored at a different path, modify `CATALOG_PATHS` inside the script or create a small file with absolute `.npy` paths and adapt the script.
- After a successful sample run, consider writing a follow-up script to validate consistency across all batched `.npy` files (shapes, dims, dtype) and to build a small FAISS/HNSW index for a sample subset.

Safety
------

This script never loads full arrays into memory; it uses mmap and only queries `shape` and `dtype` to stay safe on machines with limited RAM/VRAM.
