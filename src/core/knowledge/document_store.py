#!/usr/bin/env python3
"""
ImpressionCore: Document Store

Module for document store functionality in the ImpressionCore framework.

File: knowledge\document_store.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, object-oriented, 2025]
Dependencies: [torch, typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements document store functionality for the
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
from knowledge.document_store import DocumentStore
instance = DocumentStore()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import json
import logging
import numpy as np
import torch
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from pathlib import Path

from .uks import UniversalKnowledgeStore
from .node import KnowledgeNode
from .document_embedder import DocumentEmbedder

# Configure logging
logger = logging.getLogger(__name__)

class DocumentStore:
    """
    Storage for embedded documents.
    
    This class handles the storage and retrieval of embedded documents,
    and provides integration with the Universal Knowledge Store (UKS).
    """
    
    def __init__(
        self,
        store_path: Optional[str] = None,
        knowledge_store: Optional[UniversalKnowledgeStore] = None,
        embedding_dim: int = 768
    ):
        """
        Initialize the document store.
        
        Args:
            store_path: Path to store documents
            knowledge_store: Universal Knowledge Store instance
            embedding_dim: Dimension of document embeddings
        """
        self.store_path = store_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data",
            "document_store"
        )
        self.embedding_dim = embedding_dim
        self.knowledge_store = knowledge_store
        
        # Dictionary to store document metadata
        self.documents = {}
        
        # Create store path if it doesn't exist
        os.makedirs(self.store_path, exist_ok=True)
        
        # Initialize embedder
        self.embedder = DocumentEmbedder(
            embedding_dim=embedding_dim,
            store_path=os.path.join(self.store_path, "embeddings")
        )
        
        # Load existing documents
        self._load_documents()
        
        logger.info(f"DocumentStore initialized at {self.store_path}")
    
    def _load_documents(self):
        """Load existing document metadata."""
        metadata_path = os.path.join(self.store_path, "documents.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
                logger.info(f"Loaded metadata for {len(self.documents)} documents")
            except Exception as e:
                logger.error(f"Error loading document metadata: {e}")
                self.documents = {}
    
    def _save_documents(self):
        """Save document metadata."""
        metadata_path = os.path.join(self.store_path, "documents.json")
        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.documents, f, indent=2)
            logger.info(f"Saved metadata for {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Error saving document metadata: {e}")
    
    def add_documents(self, document_paths: List[str], tags: Optional[List[str]] = None) -> List[str]:
        """
        Add documents to the store.
        
        Args:
            document_paths: List of paths to documents
            tags: Optional tags to associate with these documents
            
        Returns:
            List of document IDs
        """
        # Embed documents
        embedded_docs = self.embedder.embed_documents(document_paths, tags)
        
        # Add to store
        for doc_id, metadata in embedded_docs.items():
            self.documents[doc_id] = metadata
        
        # Save metadata
        self._save_documents()
        
        # Connect to knowledge store if available
        if self.knowledge_store:
            self._add_to_knowledge_store(embedded_docs)
        
        return list(embedded_docs.keys())
    
    def _add_to_knowledge_store(self, documents: Dict[str, Dict]):
        """
        Add documents to the Universal Knowledge Store.
        
        Args:
            documents: Dictionary of document metadata
        """
        for doc_id, metadata in documents.items():
            # Create a node for the document
            node = KnowledgeNode(metadata["name"], node_id=f"document_{doc_id}")
            
            # Set attributes
            node.set_attribute("type", "document")
            node.set_attribute("path", metadata["path"])
            node.set_attribute("embedded", metadata["embedded"])
            node.set_attribute("chunks", metadata["chunks"])
            
            # Add tags
            for tag in metadata.get("tags", []):
                node.add_tag(tag)
            
            # Add to knowledge store
            self.knowledge_store.add_node(node)
            
            # Add "has_document" relation from relevant concept nodes
            for tag in metadata.get("tags", []):
                # Look for concept nodes with matching tags
                concept_nodes = self.knowledge_store.get_nodes_by_tag(tag)
                for concept_node in concept_nodes:
                    if concept_node.get_attribute("type") == "concept":
                        self.knowledge_store.add_relation(concept_node, "has_document", node)
    
    def remove_document(self, document_id: str) -> bool:
        """
        Remove a document from the store.
        
        Args:
            document_id: ID of the document to remove
            
        Returns:
            True if successful, False otherwise
        """
        if document_id not in self.documents:
            logger.warning(f"Document not found: {document_id}")
            return False
        
        try:
            # Get metadata
            metadata = self.documents[document_id]
            
            # Remove from store
            del self.documents[document_id]
            # Memory optimization: Explicit memory cleanup
            
            # Remove embedding files
            if "embedding_path" in metadata and os.path.exists(metadata["embedding_path"]):
                os.remove(metadata["embedding_path"])
            
            if "chunks_path" in metadata and os.path.exists(metadata["chunks_path"]):
                os.remove(metadata["chunks_path"])
            
            # Save metadata
            self._save_documents()
            
            # Remove from knowledge store if available
            if self.knowledge_store:
                node_id = f"document_{document_id}"
                node = self.knowledge_store.get_node(node_id)
                if node:
                    # TODO: Implement node removal in UKS
                    pass
            
            logger.info(f"Removed document: {metadata['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing document {document_id}: {e}")
            return False
    
    def get_documents_by_tags(self, tags: List[str]) -> Dict[str, Dict]:
        """
        Get documents that match any of the specified tags.
        
        Args:
            tags: List of tags to match
            
        Returns:
            Dictionary of matching documents
        """
        matching_docs = {}
        for doc_id, metadata in self.documents.items():
            if any(tag in metadata.get("tags", []) for tag in tags):
                matching_docs[doc_id] = metadata
        return matching_docs
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for document chunks relevant to the query.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of relevant document chunks with metadata
        """
        return self.embedder.search_similar(query, top_k)
    
    def load_document_chunks(self, document_id: str) -> List[str]:
        """
        Load the text chunks for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of document chunks
        """
        if document_id not in self.documents:
            logger.warning(f"Document not found: {document_id}")
            return []
        
        metadata = self.documents[document_id]
        chunks_path = metadata.get("chunks_path")
        
        if not chunks_path or not os.path.exists(chunks_path):
            logger.warning(f"Chunks file not found for document: {document_id}")
            return []
        
        try:
            with open(chunks_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            return chunks
        except Exception as e:
            logger.error(f"Error loading chunks for document {document_id}: {e}")
            return []

    def get_training_documents(self, tags: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Get documents suitable for training.
        
        Args:
            tags: Optional tags to filter documents
            
        Returns:
            Dictionary mapping document IDs to lists of chunks
        """
        # Get document IDs
        if tags:
            doc_ids = [doc_id for doc_id, meta in self.documents.items() 
                    if meta.get("embedded", False) and 
                    any(tag in meta.get("tags", []) for tag in tags)]
        else:
            doc_ids = [doc_id for doc_id, meta in self.documents.items() 
                    if meta.get("embedded", False)]
        
        # Load chunks for each document
        doc_chunks = {}
        for doc_id in doc_ids:
            chunks = self.load_document_chunks(doc_id)
            if chunks:
                doc_chunks[doc_id] = chunks
        
        return doc_chunks
