"""Lightweight RAG smoke harness.

Creates a tiny synthetic corpus, builds an in-memory index (uses faiss if available,
falls back to numpy nearest-neighbor), runs one query, and simulates model inference
by assembling retrieved documents and printing a response with citations.

This script is safe to run on CI or a developer machine (no large model downloads,
no F: drive access). It validates the retrieval -> fusion plumbing used in RAG.
"""
from __future__ import annotations

import json
import math
import sys
from typing import List, Tuple

try:
    import numpy as np
except Exception as e:
    print("ERROR: numpy is required for this smoke test:", e)
    sys.exit(2)

try:
    import faiss
    _HAS_FAISS = True
except Exception:
    _HAS_FAISS = False


def build_index(vectors: np.ndarray):
    dim = vectors.shape[1]
    if _HAS_FAISS:
        index = faiss.IndexFlatL2(dim)
        index.add(vectors.astype('float32'))
        return ('faiss', index)
    else:
        # store vectors and do brute-force dot-prod search
        return ('numpy', vectors)


def query_index(idx, q: np.ndarray, topk: int = 3) -> List[Tuple[int, float]]:
    mode = idx[0]
    if mode == 'faiss':
        index = idx[1]
        D, I = index.search(q.astype('float32'), topk)
        # faiss returns squared L2 distances; convert to scores
        results = []
        for i, d in zip(I[0], D[0]):
            if i < 0:
                continue
            score = float(math.exp(-float(d))) if d >= 0 else 0.0
            results.append((int(i), score))
        return results
    else:
        vectors = idx[1]
        # cosine similarity
        qn = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)
        vn = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12)
        sims = (vn @ qn.T).reshape(-1)
        ids = np.argsort(-sims)[:topk]
        return [(int(i), float(sims[int(i)])) for i in ids]


def simulate_inference(query_text: str, retrieved: List[Tuple[int, float]], docs: List[str]) -> dict:
    snippets = []
    for idx, score in retrieved:
        snippets.append({
            'id': idx,
            'score': score,
            'text': docs[idx][:200]
        })
    # very small simulated generation
    response = {
        'query': query_text,
        'generated_text': f"SIMULATED_RESPONSE: based on {len(snippets)} retrieved nodes.",
        'retrieval': snippets,
    }
    return response


def main():
    print("RAG smoke: starting lightweight retrieval+fusion smoke test")

    # Tiny synthetic corpus
    docs = [
        "Document one: overview of the system and retrieval design.",
        "Document two: details about embedding dimensions and sharding.",
        "Document three: operational notes and validator reports." 
    ]

    rng = np.random.default_rng(seed=42)
    dim = 128
    vectors = rng.standard_normal((len(docs), dim)).astype('float32')

    idx = build_index(vectors)
    print(f"Index built (mode={idx[0]}) with {len(docs)} vectors, dim={dim}")

    # Query: use one of the document vectors as the query to ensure a match
    q = vectors[0:1]
    retrieved = query_index(idx, q, topk=3)

    if not retrieved:
        print("ERROR: retrieval returned no neighbors")
        sys.exit(3)

    print("Retrieved:")
    for rid, score in retrieved:
        print(f" - id={rid} score={score:.4f} text={docs[rid][:60]!r}")

    resp = simulate_inference("What is the system overview?", retrieved, docs)
    print("\nSimulated inference output:")
    print(json.dumps(resp, indent=2))

    print("RAG smoke: SUCCESS")
    sys.exit(0)


if __name__ == '__main__':
    main()
