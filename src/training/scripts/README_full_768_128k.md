Full 768@128k Training Scaffold
================================

What this provides

- Streaming dataset loader (text files under F:/data/datasets)
- Synthetic dataset mode for smoke testing (--smoke)
- Mixed precision support, gradient accumulation, and checkpointing to F:/models/checkpoints/b3_39m_128k
- Simple resource estimate printed at start

Quick smoke test (PowerShell)

```
& 'd:/Projects/impressioncore/.venv310/Scripts/python.exe' d:/Projects/impressioncore/src/training/scripts/train_full_768_128k.py --smoke
```

Next steps after smoke

- Wire in your advanced positional attention (RoPE scaling / ALiBi / sparse attention) into `SimpleTransformerModel`.
- Replace `StreamingTextDataset` tokenizer with your production tokenizer and tokenization pipeline.
- Add logging/metrics and distributed training (torch.distributed) for multi-GPU or multi-host runs.
