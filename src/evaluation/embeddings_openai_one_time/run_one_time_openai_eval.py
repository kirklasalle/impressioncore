"""One-time OpenAI vs Local Checkpoint Embedding Evaluation Harness (Initial Skeleton)
Created: August 17, 2025
Author: GitHub Copilot

CURRENT STATUS: Skeleton – local checkpoint embedding uses placeholder random encoder.
You must replace DummyEncoder logic in model_utils.load_checkpoint with real model construction.

Usage (after installing requirements and setting OPENAI_API_KEY env var):
    python -m src.evaluation.embeddings_openai_one_time.run_one_time_openai_eval \
        --queries sample_queries.txt --output reports/embedding_eval_one_time

This first round focuses on producing OpenAI embeddings for a provided query list and
placeholder local embeddings to validate pipeline flow.
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np

from .config import BASE_OUTPUT_DIR, CHECKPOINTS, OPENAI_MODEL_SMALL, OPENAI_QUERY_ONLY, VECTORS_DIR
from .model_utils import embed_texts, load_checkpoint
from .openai_client import fetch_embeddings


def read_queries(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


def ensure_dirs():
    os.makedirs(VECTORS_DIR, exist_ok=True)


def save_json(path: str, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def run_initial_session(query_file: str):
    ensure_dirs()
    queries = read_queries(query_file)
    print(f"[INFO] Loaded {len(queries)} queries")

    # OpenAI embeddings (small)
    print("[INFO] Fetching OpenAI small embeddings (query-only)")
    oa_vectors = fetch_embeddings(queries, model=OPENAI_MODEL_SMALL)
    oa_arr = np.array(oa_vectors, dtype=np.float32)
    np.save(os.path.join(VECTORS_DIR, "openai_small_query_embeddings.npy"), oa_arr)

    # Local checkpoints
    for cfg in CHECKPOINTS:
        print(f"[INFO] Loading checkpoint: {cfg.label}")
        model = load_checkpoint(cfg)
        print(f"[INFO] Encoding queries with {cfg.label}")
        local_emb = embed_texts(model, queries)
        np.save(os.path.join(VECTORS_DIR, f"{cfg.label.lower()}_query_embeddings.npy"), local_emb.cpu().numpy())

    manifest = {
        "queries": len(queries),
        "checkpoints": [c.label for c in CHECKPOINTS],
        "openai_model_small": OPENAI_MODEL_SMALL,
        "query_only": OPENAI_QUERY_ONLY,
    }
    save_json(os.path.join(BASE_OUTPUT_DIR, "session_manifest.json"), manifest)
    print("[DONE] Initial embedding session complete (placeholder local embeddings).")


def build_arg_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", required=True, help="Path to newline-delimited query file")
    return ap


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    run_initial_session(args.queries)
