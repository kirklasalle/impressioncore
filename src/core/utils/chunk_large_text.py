"""Legacy chunk_large_text entry point consolidated.

This wraps core text chunking utilities (see text_chunking.TextChunker) and provides
backward compatible CLI for simple splitting.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .text_chunking import ChunkingConfig, TextChunker


def main():
    ap = argparse.ArgumentParser(description="Simple large text chunking using TextChunker")
    ap.add_argument("input", type=str, help="Input text file")
    ap.add_argument("output", type=str, help="Output directory for chunk files")
    ap.add_argument("--max-tokens", type=int, default=7000)
    ap.add_argument("--overlap", type=int, default=200)
    ap.add_argument("--strategy", type=str, default="semantic", choices=["semantic","fixed","sentence","paragraph"])
    args = ap.parse_args()

    cfg = ChunkingConfig(max_tokens=args.max_tokens, overlap_tokens=args.overlap, chunk_strategy=args.strategy)
    chunker = TextChunker(cfg)
    text = Path(args.input).read_text(encoding="utf-8")

    if cfg.chunk_strategy == "sentence":
        chunks = chunker.chunk_by_sentences(text)
    elif cfg.chunk_strategy == "paragraph":
        chunks = chunker.chunk_by_paragraphs(text)
    else:  # semantic or fixed fallback to semantic method
        chunks = chunker.chunk_semantic(text) if hasattr(chunker, 'chunk_semantic') else chunker.chunk_by_paragraphs(text)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(chunks):
        (out_dir / f"chunk_{i:04d}.txt").write_text(c, encoding="utf-8")
    print(f"Wrote {len(chunks)} chunks to {out_dir}")


if __name__ == "__main__":
    main()
