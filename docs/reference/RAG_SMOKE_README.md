# RAG Smoke Harness

**Created:** August 30, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\reference\RAG_SMOKE_README.md #documentation  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Run `src/deployment/rag_smoke.py` to execute a small retrieval-only smoke test. The script will use a sample manifest at `src/memlog/sample_manifest.ndjson` if present, loading the first `.npy` shard it references; otherwise it falls back to synthetic embeddings.

Run from project root using the venv Python:

```powershell
D:/Projects/impressioncore/.venv310/Scripts/python.exe src/deployment/rag_smoke.py
```

The script prints a JSON trace with top-K ids and cosine scores.