#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #memory_management #python #source_code #src/training/f_drive_embedding_manager.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #command_line #memory_management #python #source_code #src\\training\\f_drive_embedding_manager.py #testing #training
# Category:** Training System
# Status:** Active

"""
ImpressionCore-B1: F-Drive Embedding Integration System

This module provides optimized access to the 5.7M+ embeddings stored on F: drive.
Implements memory-efficient loading, caching, and similarity search for GTX 1050 Ti.

Sacred Covenant Compliance: First Amendment PAD
Date: June 18, 2025
Target: Consumer Hardware Optimization
"""

import torch
import numpy as np
from pathlib import Path
import json
import logging
from typing import Dict, List, Tuple, Optional, Union
# import faiss  # Optional, for advanced indexing
import pickle
from dataclasses import dataclass
import gc
import psutil
from collections import OrderedDict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingEntry:
    """Single embedding entry with metadata"""
    id: str
    embedding: np.ndarray
    modality: str  # 'text', 'image', 'audio'
    metadata: Dict
    timestamp: float

class FDriveEmbeddingManager:
    """
    Memory-efficient manager for F: drive embeddings
    Optimized for GTX 1050 Ti (4GB VRAM) constraints
    """

    def __init__(self, cache_size_mb: int = 1024):
        """
        Initialize F: drive embedding manager

        Args:
            cache_size_mb: Maximum cache size in MB (default 1GB)
        """
        self.f_drive_root = Path("F:/")
        self.cache_size_mb = cache_size_mb
        self.cache = OrderedDict()  # LRU cache
        self.embedding_index = None
        self.embedding_metadata = {}
        self.total_embeddings = 0

        logger.info(f"Initialized F: drive embedding manager with {cache_size_mb}MB cache")

    def scan_embeddings(self) -> bool:
        """Scan F: drive for all embedding files"""
        try:
            logger.info("Scanning F: drive for embeddings...")

            embedding_files = []
            for ext in ['.pt', '.bin', '.safetensors', '.npy']:
                embedding_files.extend(self.f_drive_root.rglob(f"*{ext}"))

            self.total_embeddings = len(embedding_files)
            logger.info(f"Found {self.total_embeddings} embedding files")

            # Create metadata index
            for i, file_path in enumerate(embedding_files):
                self.embedding_metadata[str(file_path)] = {
                    'index': i,
                    'size': file_path.stat().st_size,
                    'modality': self._detect_modality(file_path.name),
                    'loaded': False
                }

            return True

        except Exception as e:
            logger.error(f"Failed to scan embeddings: {e}")
            return False

    def _detect_modality(self, filename: str) -> str:
        """Detect modality from filename patterns"""
        filename_lower = filename.lower()
        if any(x in filename_lower for x in ['text', 'token', 'bert', 'gpt']):
            return 'text'
        elif any(x in filename_lower for x in ['image', 'vision', 'clip', 'resnet']):
            return 'image'
        elif any(x in filename_lower for x in ['audio', 'wav', 'speech', 'sound']):
            return 'audio'
        else:
            return 'unknown'

    def load_embedding_file(self, file_path: str) -> Optional[np.ndarray]:
        """Load a single embedding file with memory management"""
        try:
            # Check cache first
            if file_path in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(file_path)
                return self.cache[file_path]

            # Load from disk
            path_obj = Path(file_path)
            if path_obj.suffix == '.pt':
                data = torch.load(file_path, map_location='cpu')
                if isinstance(data, torch.Tensor):
                    embeddings = data.numpy()
                else:
                    embeddings = data
            elif path_obj.suffix == '.npy':
                embeddings = np.load(file_path)
            else:
                logger.warning(f"Unsupported file format: {path_obj.suffix}")
                return None

            # Manage cache size
            self._manage_cache_size()

            # Add to cache
            self.cache[file_path] = embeddings
            self.embedding_metadata[file_path]['loaded'] = True

            logger.debug(f"Loaded embedding file: {file_path}")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to load embedding file {file_path}: {e}")
            return None

    def _manage_cache_size(self):
        """Maintain cache within size limits"""
        current_size_mb = self._get_cache_size_mb()

        while current_size_mb > self.cache_size_mb and self.cache:
            # Remove least recently used item
            oldest_key, oldest_value = self.cache.popitem(last=False)
            if oldest_key in self.embedding_metadata:
                self.embedding_metadata[oldest_key]['loaded'] = False
            current_size_mb = self._get_cache_size_mb()

    def _get_cache_size_mb(self) -> float:
        """Calculate current cache size in MB"""
        total_bytes = 0
        for embeddings in self.cache.values():
            if isinstance(embeddings, np.ndarray):
                total_bytes += embeddings.nbytes
        return total_bytes / (1024 * 1024)

    def search_similar(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for similar embeddings

        Args:
            query_embedding: Query vector
            top_k: Number of top results to return

        Returns:
            List of (file_path, similarity_score) tuples
        """
        try:
            results = []

            for file_path, metadata in self.embedding_metadata.items():
                embeddings = self.load_embedding_file(file_path)
                if embeddings is None:
                    continue

                # Compute similarity (cosine similarity)
                if len(embeddings.shape) == 1:
                    embeddings = embeddings.reshape(1, -1)

                similarities = np.dot(embeddings, query_embedding) / (
                    np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
                )

                max_similarity = np.max(similarities)
                results.append((file_path, float(max_similarity)))

            # Sort by similarity and return top-k
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_embedding_stats(self) -> Dict:
        """Get statistics about the embedding collection"""
        stats = {
            'total_files': self.total_embeddings,
            'cached_files': len(self.cache),
            'cache_size_mb': self._get_cache_size_mb(),
            'cache_limit_mb': self.cache_size_mb,
            'modality_distribution': {}
        }

        # Count by modality
        for metadata in self.embedding_metadata.values():
            modality = metadata['modality']
            stats['modality_distribution'][modality] = stats['modality_distribution'].get(modality, 0) + 1

        return stats

    def optimize_for_training(self) -> bool:
        """Optimize embedding access for training workloads"""
        try:
            logger.info("Optimizing F: drive embeddings for training...")

            # Pre-load most important embeddings
            text_files = [f for f, m in self.embedding_metadata.items() if m['modality'] == 'text']
            image_files = [f for f, m in self.embedding_metadata.items() if m['modality'] == 'image']

            # Load balanced sample
            max_preload = min(50, len(text_files), len(image_files))

            for file_path in text_files[:max_preload] + image_files[:max_preload]:
                self.load_embedding_file(file_path)

            logger.info(f"Pre-loaded {len(self.cache)} embedding files for training")
            return True

        except Exception as e:
            logger.error(f"Training optimization failed: {e}")
            return False

def test_f_drive_integration():
    """Test F: drive embedding integration"""
    print("🧪 Testing F: Drive Embedding Integration...")

    manager = FDriveEmbeddingManager(cache_size_mb=512)  # 512MB cache for testing

    # Test 1: Scan embeddings
    if not manager.scan_embeddings():
        print("❌ Failed to scan embeddings")
        return False

    # Test 2: Get stats
    stats = manager.get_embedding_stats()
    print(f"✅ Found {stats['total_files']} embedding files")
    print(f"📊 Modality distribution: {stats['modality_distribution']}")

    # Test 3: Optimize for training
    if manager.optimize_for_training():
        print("✅ Training optimization successful")
    else:
        print("⚠️  Training optimization failed")

    # Test 4: Memory usage
    cache_stats = manager.get_embedding_stats()
    print(f"💾 Cache usage: {cache_stats['cache_size_mb']:.2f}MB / {cache_stats['cache_limit_mb']}MB")

    return True

if __name__ == "__main__":
    test_f_drive_integration()
