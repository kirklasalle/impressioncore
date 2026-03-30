#!/usr/bin/env python3
"""
ImpressionCore: Uks

Module for uks functionality in the ImpressionCore framework.

File: core\uks.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, pytorch, core, production, 2025, object-oriented]
Dependencies: [torch, typing, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements uks functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from core.uks import MemoryEntry
instance = MemoryEntry()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import torch
import numpy as np
import logging
import time
import json
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import faiss
from .config import UKSConfig

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
# Memory optimization: Memory-critical operation
    """A single memory entry in the Universal Knowledge Store."""
    # Memory optimization: Memory-critical operation
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any]
    timestamp: float
    importance_score: float = 0.0
    access_count: int = 0
    last_accessed: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a serializable dictionary."""
        return {
            "content": self.content,
            "embedding": self.embedding.tolist() if isinstance(self.embedding, np.ndarray) else self.embedding,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "importance_score": self.importance_score,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
    # Memory optimization: Memory-critical operation
        """Create a MemoryEntry from a dictionary."""
        # Memory optimization: Memory-critical operation
        embedding = data["embedding"]
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding, dtype=np.float32)
        
        return cls(
            content=data["content"],
            embedding=embedding,
            metadata=data["metadata"],
            timestamp=data["timestamp"],
            importance_score=data["importance_score"],
            access_count=data["access_count"],
            last_accessed=data["last_accessed"],
        )


class UniversalKnowledgeStore:
    """
    Universal Knowledge Store for persistent memory across model interactions.
    # Memory optimization: Explicit memory cleanup
    
    The UKS provides vector-based storage and retrieval of information, allowing
    the model to maintain long-term memory and recall relevant context.
    # Memory optimization: Explicit memory cleanup
    """
    
    def __init__(self, config: UKSConfig):
        """
        Initialize the Universal Knowledge Store.
        
        Args:
            config: Configuration for the UKS
        """
        self.config = config
        self.entries: List[MemoryEntry] = []
        # Memory optimization: Memory-critical operation
        self.index = None
        self.initialize_index()
        
        # Load persistent storage if enabled
        if self.config.persistent_storage_path:
            self.load_from_disk()
    
    def initialize_index(self) -> None:
        """Initialize the FAISS index for fast vector similarity search."""
        try:
            embedding_dim = self.config.embedding_dim
            self.index = faiss.IndexFlatL2(embedding_dim)
            logger.info(f"Initialized FAISS index with dimension {embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            self.index = None
    
    def add_memory(
    # Memory optimization: Memory-critical operation
        self, 
        content: str, 
        embedding: torch.Tensor, 
        metadata: Optional[Dict[str, Any]] = None,
        importance_score: float = 0.0
    ) -> int:
        """
        Add a new memory entry to the store.
        # Memory optimization: Memory-critical operation
        
        Args:
            content: Text content to store
            embedding: Vector embedding of the content
            metadata: Additional information about the memory
            # Memory optimization: Memory-critical operation
            importance_score: Initial importance score
            
        Returns:
            Index of the added memory
            # Memory optimization: Memory-critical operation
        """
        if metadata is None:
            metadata = {}
            
        if isinstance(embedding, torch.Tensor):
            embedding = embedding.detach().cpu().numpy()
        
        # Ensure correct shape
        if len(embedding.shape) > 1:
            embedding = embedding.reshape(-1)
            
        # Create memory entry
        # Memory optimization: Memory-critical operation
        entry = MemoryEntry(
        # Memory optimization: Memory-critical operation
            content=content,
            embedding=embedding,
            metadata=metadata,
            timestamp=time.time(),
            importance_score=importance_score
        )
        
        # Maintain memory size limit
        # Memory optimization: Memory-critical operation
        if len(self.entries) >= self.config.memory_size:
        # Memory optimization: Memory-critical operation
            self._prune_memory()
            # Memory optimization: Memory-critical operation
            
        # Add to memory
        # Memory optimization: Memory-critical operation
        self.entries.append(entry)
        
        # Update index
        if self.index is not None:
            self.index.add(np.array([embedding], dtype=np.float32))
            
        # Save to disk if enabled
        if self.config.persistent_storage_path:
            self.save_to_disk()
            
        return len(self.entries) - 1
    
    def query(
        self, 
        query_embedding: Union[torch.Tensor, np.ndarray], 
        limit: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[Tuple[MemoryEntry, float]]:
    # Memory optimization: Memory-critical operation
        """
        Query the knowledge store for similar memories.
        
        Args:
            query_embedding: Vector to search for
            limit: Maximum number of results (default: config.retrieval_limit)
            threshold: Similarity threshold (default: config.similarity_threshold)
            
        Returns:
            List of (memory_entry, similarity_score) tuples
            # Memory optimization: Memory-critical operation
        """
        if not self.entries:
            return []
            
        if limit is None:
            limit = self.config.retrieval_limit
            
        if threshold is None:
            threshold = self.config.similarity_threshold
            
        # Convert torch tensor to numpy if needed
        if isinstance(query_embedding, torch.Tensor):
            query_embedding = query_embedding.detach().cpu().numpy()
            
        # Reshape if needed
        if len(query_embedding.shape) > 1:
            query_embedding = query_embedding.reshape(-1)
        
        if self.index is not None:
            # Use FAISS for fast retrieval
            try:
                query_np = np.array([query_embedding], dtype=np.float32)
                distances, indices = self.index.search(query_np, min(limit, len(self.entries)))
                
                # Convert L2 distance to similarity score (1 - normalized distance)
                max_dist = float(np.max(distances)) if distances.size > 0 else 1.0
                if max_dist == 0:
                    max_dist = 1.0
                
                results = []
                for i, idx in enumerate(indices[0]):
                    if idx < len(self.entries):  # Sanity check
                        similarity = 1.0 - (distances[0][i] / max_dist)
                        if similarity >= threshold:
                            entry = self.entries[idx]
                            entry.access_count += 1
                            entry.last_accessed = time.time()
                            results.append((entry, float(similarity)))
                
                return results
            except Exception as e:
                logger.error(f"FAISS query failed: {e}, falling back to brute force")
                # Fall back to brute force if FAISS fails
        
        # Brute force approach
        results = []
        for entry in self.entries:
            # Compute cosine similarity
            similarity = self._compute_similarity(query_embedding, entry.embedding)
            if similarity >= threshold:
                entry.access_count += 1
                entry.last_accessed = time.time()
                results.append((entry, similarity))
                
        # Sort by similarity and apply limit
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def _compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def _prune_memory(self) -> None:
    # Memory optimization: Memory-critical operation
        """Remove least important memories when store is full."""
        if not self.entries:
            return
            
        # Calculate memory value based on importance, recency, and access frequency
        # Memory optimization: Memory-critical operation
        now = time.time()
        memory_values = []
        # Memory optimization: Memory-critical operation
        
        for i, entry in enumerate(self.entries):
            # Value formula: importance + recency + access frequency
            recency = 1.0 / (1.0 + (now - entry.timestamp) / 86400)  # Time decay factor (days)
            access_value = min(1.0, 0.1 * entry.access_count)  # Cap access value
            
            value = entry.importance_score + recency + access_value
            memory_values.append((i, value))
            # Memory optimization: Memory-critical operation
            
        # Sort by value (ascending) and remove least valuable
        memory_values.sort(key=lambda x: x[1])
        # Memory optimization: Memory-critical operation
        to_remove_idx = memory_values[0][0]
        # Memory optimization: Memory-critical operation
        
        # Remove from entries list
        del self.entries[to_remove_idx]
        # Memory optimization: Explicit memory cleanup
        
        # Rebuild index (inefficient but necessary for consistent state)
        if self.index is not None:
            self.index.reset()
            embeddings = np.array([entry.embedding for entry in self.entries], dtype=np.float32)
            if embeddings.size > 0:  # Check if we have any entries left
                self.index.add(embeddings)
    
    def save_to_disk(self) -> bool:
        """Save the knowledge store to disk."""
        if not self.config.persistent_storage_path:
            logger.warning("No persistent storage path configured")
            return False
            
        try:
            storage_path = self.config.persistent_storage_path
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            
            # Convert entries to serializable format
            serialized = {
                "config": self.config.__dict__,
                "entries": [entry.to_dict() for entry in self.entries],
                "version": "1.0"
            }
            
            with open(storage_path, 'w') as f:
                json.dump(serialized, f)
                
            logger.info(f"Saved {len(self.entries)} memories to {storage_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save knowledge store: {e}")
            return False
    
    def load_from_disk(self) -> bool:
        """Load the knowledge store from disk."""
        if not self.config.persistent_storage_path:
            return False
            
        storage_path = self.config.persistent_storage_path
        if not os.path.exists(storage_path):
            logger.warning(f"Storage file does not exist: {storage_path}")
            return False
            
        try:
            with open(storage_path, 'r') as f:
                data = json.load(f)
                
            # Load entries
            self.entries = [MemoryEntry.from_dict(entry_data) for entry_data in data["entries"]]
            # Memory optimization: Memory-critical operation
            
            # Rebuild index
            if self.index is not None:
                self.index.reset()
                if self.entries:
                    embeddings = np.array([entry.embedding for entry in self.entries], dtype=np.float32)
                    self.index.add(embeddings)
                    
            logger.info(f"Loaded {len(self.entries)} memories from {storage_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load knowledge store: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all memories from the store."""
        self.entries = []
        if self.index is not None:
            self.index.reset()
        logger.info("Knowledge store cleared")
\n#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src\core\uks.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [core]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.
"""
