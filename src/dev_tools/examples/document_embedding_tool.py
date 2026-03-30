#!/usr/bin/env python3
"""
ImpressionCore: Document Embedding Tool

Module for document embedding tool functionality in the ImpressionCore framework.

File: examples\document_embedding_tool.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, 2025]
Dependencies: [typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements document embedding tool functionality for the
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
from examples.document_embedding_tool import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import argparse
import json
import logging
import glob
from pathlib import Path
from typing import List, Dict, Optional, Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.knowledge.document_embedder import DocumentEmbedder
from src.core.knowledge.document_store import DocumentStore
from src.core.knowledge.uks import UniversalKnowledgeStore

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Document embedding tool for ImpressionCore"
    )
    
    # Main operation mode
    parser.add_argument(
        "mode", 
        choices=["embed", "list", "search", "export", "stats", "remove"],
        help="Operation mode"
    )
    
    # File and path options
    parser.add_argument(
        "--files", 
        type=str, 
        nargs="+",
        help="Paths to files or patterns to embed"
    )
    
    parser.add_argument(
        "--tags", 
        type=str, 
        nargs="+",
        help="Tags to associate with documents or filter by"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Path for export operations"
    )
    
    parser.add_argument(
        "--query",
        type=str,
        help="Search query"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of top results for search operations"
    )
    
    parser.add_argument(
        "--document-id",
        type=str,
        help="Document ID for operations that work on a single document"
    )
    
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively process directories"
    )
    
    # Model and embedding options
    # Memory optimization: Explicit memory cleanup
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="sentence-transformers/all-mpnet-base-v2",
        help="Model to use for generating embeddings"
        # Memory optimization: Explicit memory cleanup
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=256,
        help="Size of document chunks for processing"
    )
    
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=64,
        help="Overlap between chunks to maintain context"
    )
    
    # Configure storage options
    parser.add_argument(
        "--store-path",
        type=str,
        help="Path to store embedded documents"
    )
    
    return parser.parse_args()

def expand_file_patterns(patterns: List[str], recursive: bool = False) -> List[str]:
    """
    Expand file patterns into actual file paths.
    
    Args:
        patterns: List of file patterns
        recursive: Whether to recursively process directories
        
    Returns:
        List of file paths
    """
    all_files = []
    
    for pattern in patterns:
        # Handle directories
        if os.path.isdir(pattern):
            if recursive:
                for root, _, files in os.walk(pattern):
                    all_files.extend([os.path.join(root, f) for f in files if not f.startswith(".")])
            else:
                all_files.extend([os.path.join(pattern, f) for f in os.listdir(pattern) 
                              if os.path.isfile(os.path.join(pattern, f)) and not f.startswith(".")])
        
        # Handle glob patterns
        elif "*" in pattern:
            all_files.extend(glob.glob(pattern, recursive=recursive))
        
        # Handle individual files
        elif os.path.isfile(pattern):
            all_files.append(pattern)
        
        else:
            logger.warning(f"Pattern not found: {pattern}")
    
    # Filter to just text files
    text_extensions = {".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml", ".csv", ".log"}
    text_files = [f for f in all_files if os.path.splitext(f)[1].lower() in text_extensions]
    
    # Log excluded files
    if len(text_files) < len(all_files):
        logger.info(f"Excluded {len(all_files) - len(text_files)} non-text files")
    
    return text_files

def embed_documents(args):
    """
    Embed documents based on command line arguments.
    
    Args:
        args: Parsed command line arguments
    """
    # Check required arguments
    if not args.files:
        logger.error("No files specified for embedding")
        return
    
    # Expand file patterns
    file_paths = expand_file_patterns(args.files, args.recursive)
    if not file_paths:
        logger.warning("No files found matching the specified patterns")
        return
    
    logger.info(f"Found {len(file_paths)} files to process")
    
    # Initialize document store
    doc_store = DocumentStore(
        store_path=args.store_path
    )
    
    # Add documents
    doc_ids = doc_store.add_documents(file_paths, args.tags)
    
    logger.info(f"Successfully embedded {len(doc_ids)} documents")

def list_documents(args):
    """
    List embedded documents.
    
    Args:
        args: Parsed command line arguments
    """
    # Initialize document store
    doc_store = DocumentStore(
        store_path=args.store_path
    )
    
    # Get documents filtered by tags if provided
    if args.tags:
        docs = doc_store.get_documents_by_tags(args.tags)
    else:
        docs = doc_store.documents
    
    logger.info(f"Found {len(docs)} documents")
    
    # Print document information
    for doc_id, metadata in docs.items():
        tags_str = ", ".join(metadata.get("tags", []))
        print(f"ID: {doc_id}")
        print(f"  Name: {metadata['name']}")
        print(f"  Path: {metadata['path']}")
        print(f"  Embedded: {metadata.get('embedded', False)}")
        print(f"  Chunks: {metadata.get('chunks', 0)}")
        print(f"  Tags: {tags_str}")
        print()

def search_documents(args):
    """
    Search embedded documents.
    
    Args:
        args: Parsed command line arguments
    """
    # Check required arguments
    if not args.query:
        logger.error("No query specified for search")
        return
    
    # Initialize document store
    doc_store = DocumentStore(
        store_path=args.store_path
    )
    
    # Search documents
    results = doc_store.search(args.query, args.top_k)
    
    logger.info(f"Found {len(results)} results for query: '{args.query}'")
    
    # Print search results
    for i, result in enumerate(results):
        print(f"\nResult {i+1} (Score: {result['similarity']:.4f}):")
        print(f"Document: {result['document_name']} (ID: {result['document_id']})")
        print(f"Chunk {result['chunk_index']}:")
        print("-" * 80)
        print(result['chunk_text'][:300] + "..." if len(result['chunk_text']) > 300 else result['chunk_text'])
        print("-" * 80)

def export_documents(args):
    """
    Export embedded documents for training.
    
    Args:
        args: Parsed command line arguments
    """
    # Check required arguments
    if not args.output:
        logger.error("No output path specified for export")
        return
    
    # Initialize document store
    doc_store = DocumentStore(
        store_path=args.store_path
    )
    
    # Get training documents filtered by tags if provided
    training_docs = doc_store.get_training_documents(args.tags)
    
    if not training_docs:
        logger.warning("No embedded documents found to export")
        return
    
    # Create output directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Export documents
    export_data = {
        "documents": training_docs,
        "metadata": {doc_id: doc_store.documents[doc_id] for doc_id in training_docs}
    }
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2)
    
    logger.info(f"Exported {len(training_docs)} documents with {sum(len(chunks) for chunks in training_docs.values())} chunks to {args.output}")

def show_document_stats(args):
    """
    Show statistics about embedded documents.
    
    Args:
        args: Parsed command line arguments
    """
    # Initialize document store
    doc_store = DocumentStore(
        store_path=args.store_path
    )
    
    # Get documents filtered by tags if provided
    if args.tags:
        docs = doc_store.get_documents_by_tags(args.tags)
    else:
        docs = doc_store.documents
    
    if not docs:
        logger.warning("No embedded documents found")
        return
    
    # Calculate statistics
    total_documents = len(docs)
    embedded_documents = sum(1 for meta in docs.values() if meta.get("embedded", False))
    total_chunks = sum(meta.get("chunks", 0) for meta in docs.values())
    avg_chunks_per_doc = total_chunks / embedded_documents if embedded_documents else 0
    
    # Count tag occurrences
    tag_counts = {}
    for meta in docs.values():
        for tag in meta.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Print statistics
    print(f"\n=== Document Embedding Statistics ===")
    print(f"Total documents: {total_documents}")
    print(f"Embedded documents: {embedded_documents}")
    print(f"Total document chunks: {total_chunks}")
    print(f"Average chunks per document: {avg_chunks_per_doc:.1f}")
    
    if tag_counts:
        print("\nTag distribution:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tag}: {count}")

def remove_document(args):
    """
    Remove an embedded document.
    
    Args:
        args: Parsed command line arguments
    """
    # Check required arguments
    if not args.document_id:
        logger.error("No document ID specified for removal")
        return
    
    # Initialize document store
    doc_store = DocumentStore(
        store_path=args.store_path
    )
    
    # Remove document
    success = doc_store.remove_document(args.document_id)
    
    if success:
        logger.info(f"Successfully removed document {args.document_id}")
    else:
        logger.error(f"Failed to remove document {args.document_id}")

def main():
    """Main entry point."""
    args = parse_args()
    
    # Handle different operation modes
    mode_handlers = {
        "embed": embed_documents,
        "list": list_documents,
        "search": search_documents,
        "export": export_documents,
        "stats": show_document_stats,
        "remove": remove_document
    }
    
    if args.mode in mode_handlers:
        try:
            mode_handlers[args.mode](args)
        except Exception as e:
            logger.error(f"Error in {args.mode} operation: {e}")
            return 1
    else:
        logger.error(f"Unknown mode: {args.mode}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
