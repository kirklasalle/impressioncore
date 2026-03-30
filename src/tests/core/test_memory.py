"""Tests for src.core.memory — verify package exports and EmbeddingMemoryStore."""
from __future__ import annotations

import numpy as np
import pytest


class TestMemoryPackageExports:
    """The memory package __init__ should export the canonical classes."""

    def test_exports_memory_manager(self):
        from src.core.memory import MemoryManager
        assert MemoryManager is not None

    def test_exports_embedding_memory_store(self):
        from src.core.memory import EmbeddingMemoryStore
        assert EmbeddingMemoryStore is not None

    def test_deprecated_alias_warns(self):
        from src.core.memory.memory_manager import MemoryManager as DeprecatedMM
        with pytest.warns(DeprecationWarning, match="EmbeddingMemoryStore"):
            DeprecatedMM(embed_dim=64)


class TestEmbeddingMemoryStore:
    """Basic functional tests for the embedding store (NumPy fallback)."""

    def test_add_and_retrieve(self):
        from src.core.memory.memory_manager import EmbeddingMemoryStore

        store = EmbeddingMemoryStore(embed_dim=8)
        embeddings = np.random.randn(10, 8).astype(np.float32)
        store.add_embeddings(embeddings)

        query = np.random.randn(1, 8).astype(np.float32)
        distances, indices = store.retrieve_memory(query, k=3)

        assert distances.shape == (1, 3)
        assert indices.shape == (1, 3)

    def test_empty_retrieve(self):
        from src.core.memory.memory_manager import EmbeddingMemoryStore

        store = EmbeddingMemoryStore(embed_dim=8)
        query = np.random.randn(1, 8).astype(np.float32)
        distances, indices = store.retrieve_memory(query, k=3)
        assert len(distances) == 0

    def test_memory_state(self):
        from src.core.memory.memory_manager import EmbeddingMemoryStore

        store = EmbeddingMemoryStore(embed_dim=16)
        state = store.get_memory_state()
        assert state["total_memories"] == 0
        assert state["embedding_dimension"] == 16

        store.add_embeddings(np.random.randn(5, 16).astype(np.float32))
        state = store.get_memory_state()
        assert state["total_memories"] == 5
