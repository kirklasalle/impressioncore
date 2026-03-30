"""vector_index.py

Created: August 20, 2025
Updated: August 21, 2025
Author: GitHub Copilot
Purpose: FAISS-backed vector index utilities for ImpressionCore (OpenAI embeddings workflow).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover
    faiss = None  # type: ignore
from .rich_logging import log_error, log_info, log_success, log_warning


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_mapping(mapping_path: Path) -> dict[str, Any]:
    if mapping_path.is_file():
        try:
            return json.loads(mapping_path.read_text(encoding='utf-8'))
        except Exception as e:
            log_warning(f"Failed to load mapping {mapping_path}: {e}; recreating.")
    return {"entries": [], "dim": None}

def save_mapping(mapping: dict[str, Any], mapping_path: Path) -> None:
    try:
        mapping_path.parent.mkdir(parents=True, exist_ok=True)
        mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        log_error(f"Failed saving mapping {mapping_path}: {e}")

def load_or_create_index(index_path: Path, dim: int) -> Any:
    if faiss is None:
        raise RuntimeError("faiss not available; install faiss-cpu to use vector index.")
    if index_path.is_file():
        log_info(f"Loading existing index: {index_path}")
        return faiss.read_index(str(index_path))
    log_info(f"Creating new FAISS IndexFlatL2 dim={dim}")
    return faiss.IndexFlatL2(dim)

def save_index(index: Any, index_path: Path) -> None:
    try:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(index_path))
        log_success(f"Saved index -> {index_path}")
    except Exception as e:
        log_error(f"Failed saving index {index_path}: {e}")

def add_text_embeddings_internal(index: Any, texts: list[str], embeddings: np.ndarray, mapping: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
    """Internal function for adding embeddings to index."""
    if embeddings.shape[0] != len(texts):
        raise ValueError("Mismatch: number of texts and embedding rows")
    existing_hashes = {e['hash'] for e in mapping['entries']}
    new_vecs, new_entries = [], []
    start_id = len(mapping['entries'])
    for t, vec in zip(texts, embeddings):
        h = _hash_text(t)
        if h in existing_hashes:
            continue
        new_vecs.append(vec)
        new_entries.append({"id": start_id + len(new_entries), "hash": h, "text": t})
    if new_vecs:
        vec_block = np.vstack(new_vecs).astype('float32')
        index.add(vec_block)
        mapping['entries'].extend(new_entries)
        mapping['dim'] = int(embeddings.shape[1])
        log_info(f"Added {len(new_vecs)} new vectors (total={len(mapping['entries'])}).")
    else:
        log_info("No new vectors to add (all duplicates).")
    return index, mapping

def search(index: Any, query_vec: np.ndarray, k: int = 5) -> tuple[np.ndarray, np.ndarray]:
    if query_vec.ndim == 1:
        query_vec = query_vec[None, :]
    return index.search(query_vec.astype('float32'), k)

def load_index_and_mapping(index_path: Path, mapping_path: Path) -> tuple[Any, dict[str, Any]]:
    mapping = load_mapping(mapping_path)
    dim = mapping.get('dim') or 1536
    index = load_or_create_index(index_path, dim)
    return index, mapping

def add_text_embeddings(
    index_path: Path,
    embeddings: np.ndarray,
    text_ids: list[str],
    metadata: list[dict[str, Any]]
) -> None:
    """Add text embeddings to a FAISS index with metadata."""
    mapping_path = index_path.with_suffix('.mapping.json')

    # Determine the embedding dimension from the actual embeddings
    actual_dim = embeddings.shape[1] if embeddings.ndim > 1 else embeddings.shape[0]

    # Load mapping first to check existing dim
    mapping = load_mapping(mapping_path)
    dim = mapping.get('dim') or actual_dim  # Use actual dim if not set

    # Create or load index with correct dimension
    index = load_or_create_index(index_path, dim)

    # Prepare texts for the existing function
    texts = [meta.get('text', f'text_{text_id}') for text_id, meta in zip(text_ids, metadata)]

    # Add embeddings using existing function
    index, mapping = add_text_embeddings_internal(index, texts, embeddings, mapping)


    # Add metadata to mapping entries
    for i, (text_id, meta) in enumerate(zip(text_ids, metadata)):
        entry_idx = len(mapping['entries']) - len(text_ids) + i
        if entry_idx >= 0 and entry_idx < len(mapping['entries']):
            mapping['entries'][entry_idx]['text_id'] = text_id
            mapping['entries'][entry_idx]['metadata'] = meta

    # Save index and mapping
    save_index(index, index_path)
    save_mapping(mapping, mapping_path)

def search_similar_texts(
    index_path: Path,
    query_embedding: np.ndarray,
    top_k: int = 5
) -> list[dict[str, Any]]:
    """Search for similar texts in the index."""
    mapping_path = index_path.with_suffix('.mapping.json')

    if not index_path.exists():
        log_warning(f"Index not found: {index_path}")
        return []

    # Load index and mapping
    index, mapping = load_index_and_mapping(index_path, mapping_path)

    if not mapping['entries']:
        log_warning("No entries in index mapping")
        return []

    # Search
    distances, indices = search(index, query_embedding, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < len(mapping['entries']):
            entry = mapping['entries'][idx]
            result = {
                'text': entry.get('text', ''),
                'distance': float(dist),
                'index': int(idx),
                'text_id': entry.get('text_id', f'entry_{idx}'),
                'metadata': entry.get('metadata', {})
            }
            results.append(result)

    return results
