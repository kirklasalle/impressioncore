768@128k Training Scaffold
===========================

Purpose
-------

Small scaffold to validate a 768-d Transformer with an extendable positional embedding scheme intended for large-context (128k) support. This is a smoke/test harness only — not a full training pipeline.

Quick smoke test (PowerShell)
-----------------------------

From the repository root, run in the project's venv (PowerShell):

```
& 'd:/Projects/impressioncore/.venv310/Scripts/python.exe' d:/Projects/impressioncore/src/training/scripts/train_768_128k_scaffold.py --smoke
```

Notes
-----

- The scaffold uses automatic interpolation to extend positional embeddings at runtime. For production, prefer RoPE/xpos/ALiBi implementations tailored to long-context efficiency.
- After validating the smoke run, I can scaffold a fuller training loop with checkpointing, dataset streaming (F:/data/datasets), and a resource estimate for training on consumer GPUs.
