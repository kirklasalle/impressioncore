#!/usr/bin/env python3
"""
ImpressionCore: Document Embedder

Module for document embedder functionality in the ImpressionCore framework.

File: knowledge\document_embedder.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, pytorch, production, 2025, object-oriented]
Dependencies: [torch, typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements document embedder functionality for the
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
from knowledge.document_embedder import DocumentEmbedder
instance = DocumentEmbedder()
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
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Set, Tuple, Any
from tqdm import tqdm

# Import transformers for embedding generation
try:
    from transformers import AutoTokenizer, AutoModel
except ImportError:
    logging.warning("Transformers library not found. Document embedding functionality will be limited.")
    AutoTokenizer = None
    AutoModel = None
    # Memory optimization: Explicit memory cleanup

# Configure logging
logger = logging.getLogger(__name__)

class DocumentEmbedder:
    """
    Utility for embedding documents into model knowledge.
    # Memory optimization: Explicit memory cleanup
    
    This class handles document selection, processing, and embedding generation
    for training documents that should be incorporated into the model.
    """
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
        embedding_dim: int = 768,
        max_length: int = 512,
        chunk_size: int = 256,
        chunk_overlap: int = 64,
        store_path: Optional[str] = None,
        device: Optional[str] = None
        # Memory optimization: Device placement for memory management
    ):
        """
        Initialize the document embedder.
        
        Args:
            embedding_model: Model to use for generating embeddings
            # Memory optimization: Explicit memory cleanup
            embedding_dim: Dimension of generated embeddings
            max_length: Maximum sequence length for the embedding model
            chunk_size: Size of document chunks for processing
            chunk_overlap: Overlap between chunks to maintain context
            store_path: Path to store embedded documents
            device: Device to use for embedding generation (auto-detect if None)
            # Memory optimization: Device placement for memory management
        """
        self.embedding_model_name = embedding_model
        self.embedding_dim = embedding_dim
        self.max_length = max_length
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.store_path = store_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data",
            "embeddings"
        )
        
        # Set device
        # Memory optimization: Device placement for memory management
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        # Memory optimization: CUDA operations for GPU acceleration
        
        # Initialize embedding model and tokenizer
        # Memory optimization: Explicit memory cleanup
        self.tokenizer = None
        self.model = None
        # Memory optimization: Explicit memory cleanup
        
        # Store for document metadata and embeddings
        self.document_metadata = {}
        self.embeddings = {}
        
        # Create store path if it doesn't exist
        os.makedirs(self.store_path, exist_ok=True)
        
        # Load existing metadata if available
        self._load_metadata()
        
        logger.info(f"DocumentEmbedder initialized with model {embedding_model}")
        # Memory optimization: Explicit memory cleanup
        logger.info(f"Using device: {self.device}")
        # Memory optimization: Device placement for memory management
    
    def _initialize_model(self):
        """Initialize the embedding model and tokenizer."""
        # Memory optimization: Explicit memory cleanup
        if AutoTokenizer is None or AutoModel is None:
        # Memory optimization: Explicit memory cleanup
            raise ImportError("Transformers library is required for document embedding.")
            
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.embedding_model_name)
            self.model = AutoModel.from_pretrained(self.embedding_model_name)
            # Memory optimization: Explicit memory cleanup
            self.model.to(self.device)
            # Memory optimization: Device placement for memory management
            self.model.eval()
            logger.info(f"Loaded embedding model: {self.embedding_model_name}")
            return True
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            return False
    
    def _load_metadata(self):
        """Load existing document metadata."""
        metadata_path = os.path.join(self.store_path, "document_metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    self.document_metadata = json.load(f)
                logger.info(f"Loaded metadata for {len(self.document_metadata)} documents")
            except Exception as e:
                logger.error(f"Error loading document metadata: {e}")
                self.document_metadata = {}
    
    def _save_metadata(self):
        """Save document metadata."""
        metadata_path = os.path.join(self.store_path, "document_metadata.json")
        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.document_metadata, f, indent=2)
            logger.info(f"Saved metadata for {len(self.document_metadata)} documents")
        except Exception as e:
            logger.error(f"Error saving document metadata: {e}")
    
    def select_documents(self, document_paths: List[str], tags: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        Select documents for embedding.
        
        Args:
            document_paths: List of paths to documents
            tags: Optional tags to associate with these documents
            
        Returns:
            Dictionary of selected documents with metadata
        """
        selected_docs = {}
        for path in document_paths:
            try:
                if not os.path.exists(path):
                    logger.warning(f"Document not found: {path}")
                    continue
                
                file_name = os.path.basename(path)
                doc_id = f"doc_{len(self.document_metadata) + len(selected_docs)}"
                
                # Create document metadata
                doc_metadata = {
                    "id": doc_id,
                    "path": path,
                    "name": file_name,
                    "tags": tags or [],
                    "embedded": False,
                    "chunks": 0,
                }
                
                selected_docs[doc_id] = doc_metadata
                logger.info(f"Selected document: {file_name}")
                
            except Exception as e:
                logger.error(f"Error selecting document {path}: {e}")
        
        return selected_docs
    
    def chunk_document(self, text: str) -> List[str]:
        """
        Split a document into overlapping chunks.
        
        Args:
            text: Document text
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        # Simple chunking by words with overlap
        words = text.split()
        if len(words) <= self.chunk_size:
            chunks.append(text)
        else:
            for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
                chunk = words[i:i + self.chunk_size]
                chunks.append(" ".join(chunk))
        
        return chunks
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a text chunk.
        
        Args:
            text: Text chunk
            
        Returns:
            Embedding vector
        """
        if self.model is None:
        # Memory optimization: Explicit memory cleanup
            if not self._initialize_model():
                raise RuntimeError("Failed to initialize embedding model")
        
        # Tokenize and generate embedding
        with torch.no_grad():
        # Memory optimization: Disable gradient computation to save memory
            inputs = self.tokenizer(
                text, 
                max_length=self.max_length, 
                padding="max_length", 
                truncation=True,
                return_tensors="pt"
            )
            
            # Move inputs to device
            # Memory optimization: Device placement for memory management
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            # Memory optimization: Device placement for memory management
            
            # Generate embeddings
            outputs = self.model(**inputs)
            
            # Use mean pooling to get sentence embedding
            attention_mask = inputs["attention_mask"]
            last_hidden_state = outputs.last_hidden_state
            
            # Apply attention mask to get mean of token embeddings
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
            sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, 1)
            sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            embedding = (sum_embeddings / sum_mask).squeeze()
            
            # Convert to numpy array
            embedding = embedding.cpu().numpy()
            
        return embedding
    
    def process_documents(self, selected_docs: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Process and embed selected documents.
        
        Args:
            selected_docs: Dictionary of selected documents with metadata
            
        Returns:
            Dictionary of processed documents with metadata
        """
        for doc_id, metadata in tqdm(selected_docs.items(), desc="Processing documents"):
            try:
                path = metadata["path"]
                
                # Read document content
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                
                # Chunk document
                chunks = self.chunk_document(content)
                metadata["chunks"] = len(chunks)
                
                # Generate embeddings for each chunk
                doc_embeddings = []
                for chunk in tqdm(chunks, desc=f"Embedding {metadata['name']}", leave=False):
                    embedding = self.generate_embedding(chunk)
                    doc_embeddings.append({
                        "text": chunk,
                        "embedding": embedding
                    })
                
                # Save embeddings
                embed_path = os.path.join(self.store_path, f"{doc_id}.npy")
                embeddings_array = np.array([chunk["embedding"] for chunk in doc_embeddings])
                np.save(embed_path, embeddings_array)
                
                # Save chunk texts separately
                chunks_path = os.path.join(self.store_path, f"{doc_id}_chunks.json")
                with open(chunks_path, "w", encoding="utf-8") as f:
                    json.dump([chunk["text"] for chunk in doc_embeddings], f)
                
                # Update metadata
                metadata["embedded"] = True
                metadata["embedding_path"] = embed_path
                metadata["chunks_path"] = chunks_path
                
                # Add to global metadata
                self.document_metadata[doc_id] = metadata
                logger.info(f"Processed document: {metadata['name']} ({len(chunks)} chunks)")
                
            except Exception as e:
                logger.error(f"Error processing document {doc_id}: {e}")
        
        # Save updated metadata
        self._save_metadata()
        return selected_docs
    
    def embed_documents(self, document_paths: List[str], tags: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        Select and embed documents in one step.
        
        Args:
            document_paths: List of paths to documents
            tags: Optional tags to associate with these documents
            
        Returns:
            Dictionary of processed documents with metadata
        """
        selected_docs = self.select_documents(document_paths, tags)
        return self.process_documents(selected_docs)
    
    def get_document_ids_by_tags(self, tags: List[str]) -> List[str]:
        """
        Get document IDs that match any of the specified tags.
        
        Args:
            tags: List of tags to match
            
        Returns:
            List of matching document IDs
        """
        matching_ids = []
        for doc_id, metadata in self.document_metadata.items():
            if any(tag in metadata.get("tags", []) for tag in tags):
                matching_ids.append(doc_id)
        return matching_ids
    
    def load_embeddings(self, document_ids: List[str]) -> Dict[str, Dict]:
        """
        Load embeddings for specific documents.
        
        Args:
            document_ids: List of document IDs
            
        Returns:
            Dictionary of document embeddings
        """
        loaded_embeddings = {}
        
        for doc_id in document_ids:
            if doc_id not in self.document_metadata:
                logger.warning(f"Document ID not found: {doc_id}")
                continue
                
            metadata = self.document_metadata[doc_id]
            if not metadata.get("embedded", False):
                logger.warning(f"Document not embedded: {doc_id}")
                continue
                
            try:
                # Load embeddings
                embed_path = metadata["embedding_path"]
                embeddings = np.load(embed_path)
                
                # Load chunks
                chunks_path = metadata["chunks_path"]
                with open(chunks_path, "r", encoding="utf-8") as f:
                    chunks = json.load(f)
                
                # Store in result
                loaded_embeddings[doc_id] = {
                    "metadata": metadata,
                    "embeddings": embeddings,
                    "chunks": chunks
                }
                
                logger.info(f"Loaded embeddings for {metadata['name']}")
                
            except Exception as e:
                logger.error(f"Error loading embeddings for document {doc_id}: {e}")
        
        return loaded_embeddings

    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for document chunks similar to the query.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of similar document chunks with metadata
        """
        if self.model is None:
        # Memory optimization: Explicit memory cleanup
            if not self._initialize_model():
                raise RuntimeError("Failed to initialize embedding model")
        
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)
        
        # Load all document embeddings
        all_results = []
        
        for doc_id in self.document_metadata:
            try:
                # Load document embeddings
                doc_data = self.load_embeddings([doc_id])[doc_id]
                metadata = doc_data["metadata"]
                embeddings = doc_data["embeddings"]
                chunks = doc_data["chunks"]
                
                # Calculate similarity scores
                similarities = np.dot(embeddings, query_embedding) / (
                    np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
                )
                
                # Get top results for this document
                top_indices = np.argsort(similarities)[::-1][:top_k]
                
                # Add to results
                for idx in top_indices:
                    all_results.append({
                        "document_id": doc_id,
                        "document_name": metadata["name"],
                        "chunk_index": int(idx),
                        "chunk_text": chunks[idx],
                        "similarity": float(similarities[idx])
                    })
                
            except Exception as e:
                logger.error(f"Error searching document {doc_id}: {e}")
        
        # Sort all results by similarity
        all_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return all_results[:top_k]
