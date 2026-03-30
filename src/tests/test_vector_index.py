"""test_vector_index.py

Created: August 20, 2025
Author: GitHub Copilot
Purpose: Basic tests for FAISS vector index utilities (skips if faiss not installed or no API key).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.utils.openai_embeddings import generate_openai_embeddings_batched, get_openai_api_key
from src.core.utils.vector_index import (
    add_text_embeddings,
    load_index_and_mapping,
    save_index,
    save_mapping,
    search,
)

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover
    faiss = None  # type: ignore

@pytest.mark.skipif(faiss is None, reason="faiss not installed")
@pytest.mark.skipif(not get_openai_api_key(), reason="OPENAI_API_KEY not set")
def test_basic_index_roundtrip(tmp_path: Path):
    texts = ["alpha", "beta", "gamma"]
    embs = generate_openai_embeddings_batched(texts, batch_size=3)
    import numpy as np
    arr = np.asarray(embs, dtype='float32')
    index_path = tmp_path / "test.index"
    mapping_path = tmp_path / "mapping.json"
    index, mapping = load_index_and_mapping(index_path, mapping_path)
    index, mapping = add_text_embeddings(index, texts, arr, mapping)
    save_index(index, index_path)
    save_mapping(mapping, mapping_path)
    # Reload
    index2, mapping2 = load_index_and_mapping(index_path, mapping_path)
    assert len(mapping2['entries']) == 3
    # Query vector (use first embedding)
    _D, I = search(index2, arr[0], k=2)
    assert I.shape[1] == 2
    assert I[0,0] == 0  # nearest should be itself
