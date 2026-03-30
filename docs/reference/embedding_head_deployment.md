# Embedding Reconstruction Head Deployment Guide

**Created:** September 07, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team; GitHub Copilot  
**Tags:** #deployment #inference #embeddings #docs\reference\embedding_head_deployment.md  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

Two head generations are available:

| Version | Architecture (high level) | Best blended val loss | Notes |
|---------|---------------------------|-----------------------|-------|
| v1      | Linear → GELU → Linear    | ~4.3e-03 (full) / ~3.9e-03 (sample) | Stable baseline, originally deployed |
| v2      | Linear → GELU → LayerNorm → Dropout → Linear (no final norm) | 9.6584e-04 | Achieved via cosine restarts + reduced center reg |

The v2 head supersedes v1 with roughly a 4.5× reduction in blended validation loss relative to the earlier v1 benchmark. Both remain reproducible; v1 can be retained for regression checks.

Artifacts (example paths):

```text
F:/models/production/embedding_head_v1/
  ├── model.safetensors
  ├── model.torchscript.pt
  └── export_meta.json

F:/models/production/embedding_head_v2/
  ├── model.safetensors
  ├── model.torchscript.pt
  ├── model.onnx                # (if exported with --onnx)
  └── export_meta.json
```

## Loading (State Dict)

```python
from safetensors.torch import load_file
from src.training.embed_head import EmbeddingReconstructionHead
import torch
sd = load_file('F:/models/production/embedding_head_v1/model.safetensors')
model = EmbeddingReconstructionHead(dim=768, hidden=2048)
model.load_state_dict(sd)
model.cuda().eval()
out = model(torch.randn(4,768, device='cuda'))
```

## Loading (TorchScript)

```python
import torch
scripted = torch.jit.load('F:/models/production/embedding_head_v1/model.torchscript.pt')
scripted = scripted.to('cuda').eval()
out = scripted(torch.randn(4,768, device='cuda'))
```

## Integration Into Retrieval

`ProductionIndex` now supports an optional reconstruction step prior to Faiss search.

```python
from src.inference.production_index import ProductionIndex
index = ProductionIndex(
    multimodal_dir='F:/models/embeddings/b3_39m_128k/multimodal_batches',
    ckpt_path='F:/models/checkpoints/b3_39m_128k/ckpt_step_3500_20250903_124926.pt',
    recon_head_dir='F:/models/production/embedding_head_v1',
    apply_reconstruction=True
)
results = index.query_text("example query", k=5)
```

Set `apply_reconstruction=False` to bypass the head if raw encoder space is preferred.

## Export Script

Use the export utility to regenerate artifacts after retraining. Now supports optional ONNX:

```powershell
python -m src.inference.export_head `
  --ckpt-dir F:/models/checkpoints/b3/b3_39m_128k_v2_headft_long_restart `
  --out-dir F:/models/production/embedding_head_v2 `
  --onnx --force
```

## Evaluation & Comparison

Single-head evaluation (auto-detects architecture, discovers checkpoint/config):

```powershell
python -m src.evaluation.embedding_head_eval `
  --ckpt-dir F:/models/checkpoints/b3/b3_39m_128k_v2_headft_long_restart
```

Compare two heads (A baseline v1, B new v2):

```powershell
python -m src.evaluation.compare_heads `
  --ckpt-dir-a F:/models/checkpoints/b3/b3_39m_128k_v2 `
  --ckpt-dir-b F:/models/checkpoints/b3/b3_39m_128k_v2_headft_long_restart
```

The comparison outputs JSON including relative improvement percentage.

## Versioning Recommendations

- Keep each new head export in a timestamped directory: `embedding_head_v1_20250907/`.
- Maintain a `current` symlink or pointer file for production consumers.
- Document validation metrics in an index file (future enhancement).

## When to Re-Export

Re-export after:

- Significant validation loss improvement (>10% relative)
- Architectural change (e.g., adoption of v2 head parity or superiority)
- Dependency updates affecting determinism

## Future Enhancements (Planned)

- Automatic metric logging into `export_meta.json`
- Hash-based integrity verification during load
- Embedding drift monitoring between versions

---

**Constitutional Compliance:** Follows consumer hardware democracy (minimal VRAM use) and protection-first design by enabling consistent embedding alignment.