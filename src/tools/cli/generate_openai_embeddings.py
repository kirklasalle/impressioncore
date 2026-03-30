#!/usr/bin/env python3
"""Generate OpenAI embeddings (current canonical location).

Moved from project root (generate_openai_embeddings.py) on August 23, 2025.
"""
from __future__ import annotations

import argparse
import os

from src.core.utils.openai_embeddings import generate_openai_embeddings, get_openai_api_key
from src.core.utils.rich_logging import log_error, log_info, log_success, log_warning


def parse_args():
    p = argparse.ArgumentParser(description="Generate OpenAI embeddings for provided texts.")
    p.add_argument("--text", action="append", help="Single text input (can repeat)")
    p.add_argument("--input-file", help="Path to a text file (one line per sample)")
    p.add_argument("--model", default="text-embedding-3-small", help="Embedding model name")
    p.add_argument("--batch-size", type=int, default=64, help="Batch size")
    p.add_argument("--out", default="F:/data/embeddings/impressioncore_b3/base/sample_embeddings.npy", help="Output .npy path")
    return p.parse_args()


def _load_texts(args) -> list[str]:
    texts: list[str] = []
    if args.text:
        texts.extend([t for t in args.text if t and t.strip()])
    if args.input_file and os.path.isfile(args.input_file):
        with open(args.input_file, encoding='utf-8') as f:
            for line in f:
                s = line.strip()
                if s:
                    texts.append(s)
    if not texts:
        texts = [
            "ImpressionCore is a brain-inspired AI framework.",
            "OpenAI embeddings enable efficient semantic search.",
            "This is a test sentence for embedding generation.",
        ]
        log_warning("No input supplied; using fallback demo texts.")
    return texts


def _batched(texts: list[str], model: str, batch_size: int):
    import numpy as np
    out = []
    for i in range(0, len(texts), batch_size):
        emb = generate_openai_embeddings(texts[i:i+batch_size], model=model)
        if emb is not None:
            out.append(emb)
    return np.vstack(out) if out else None


def _ensure_dir(path: str):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)


def main() -> int:
    args = parse_args()
    texts = _load_texts(args)
    log_info(f"Total texts: {len(texts)}")
    _ensure_dir(args.out)
    try:
        get_openai_api_key()
    except Exception as e:  # pragma: no cover
        log_error(f"OPENAI_API_KEY missing: {e}")
        return 1
    use_batched = len(texts) > args.batch_size
    embeddings = _batched(texts, args.model, args.batch_size) if use_batched else generate_openai_embeddings(texts, model=args.model)
    if embeddings is None:
        log_error("Embedding generation failed.")
        return 2
    import numpy as np
    np.save(args.out, embeddings)
    log_success(f"Saved embeddings shape={embeddings.shape} -> {args.out}")
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
