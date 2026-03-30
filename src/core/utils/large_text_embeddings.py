"""
large_text_embeddings.py

Created: August 21, 2025
Author: GitHub Copilot
Purpose: Complete pipeline for processing large text files into embeddings with intelligent chunking.

This integrates text chunking, OpenAI embeddings, and FAISS indexing for comprehensive large text processing.
"""

import hashlib
import json
import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.utils.openai_embeddings import generate_openai_embeddings, generate_openai_embeddings_batched
from src.core.utils.rich_logging import log_error, log_info, log_success, log_warning
from src.core.utils.text_chunking import ChunkingConfig, TextChunker, estimate_embedding_cost
from src.core.utils.vector_index import add_text_embeddings, search_similar_texts


class LargeTextProcessor:
    """Process large text files with chunking, embeddings, and indexing."""

    def __init__(
        self,
        chunking_config: ChunkingConfig | None = None,
        embedding_model: str = "text-embedding-3-small",
        batch_size: int = 10,
        cache_dir: Path | None = None
    ):
        self.chunking_config = chunking_config or ChunkingConfig()
        self.embedding_model = embedding_model
        self.batch_size = batch_size
        self.cache_dir = cache_dir or Path("data/embeddings/cache")
        self.chunker = TextChunker(self.chunking_config)

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def process_file(
        self,
        file_path: str | Path,
        document_id: str | None = None,
        save_chunks: bool = True,
        update_index: bool = True,
        index_path: Path | None = None
    ) -> dict[str, int | float | list]:
        """Complete processing pipeline for a large text file."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Generate document ID if not provided
        if not document_id:
            document_id = file_path.stem

        log_info(f"Processing large text file: {file_path}")
        log_info(f"Document ID: {document_id}")

        # Step 1: Load and chunk the text
        start_time = time.time()

        try:
            text = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            log_warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
            text = file_path.read_text(encoding='latin-1')

        chunks = self.chunker.chunk_text(text)
        chunk_time = time.time() - start_time

        log_info(f"Created {len(chunks)} chunks in {chunk_time:.2f}s")

        # Step 2: Estimate costs
        cost_info = estimate_embedding_cost(chunks, self.embedding_model)
        log_info(f"Estimated embedding cost: ${cost_info['estimated_cost_usd']:.4f}")

        # Step 3: Generate embeddings in batches
        log_info("Generating embeddings...")
        embed_start = time.time()

        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = generate_openai_embeddings_batched(
            texts=chunk_texts,
            model=self.embedding_model,
            batch_size=self.batch_size
        )

        embed_time = time.time() - embed_start
        log_info(f"Generated {len(embeddings)} embeddings in {embed_time:.2f}s")

        # Step 4: Create metadata for each chunk
        chunk_metadata = []
        for i, (chunk, _embedding) in enumerate(zip(chunks, embeddings)):
            metadata = {
                "document_id": document_id,
                "chunk_id": i,
                "text": chunk["text"],
                "token_count": chunk["token_count"],
                "char_count": chunk["char_count"],
                "strategy": chunk["strategy"],
                "file_path": str(file_path),
                "chunk_hash": hashlib.sha256(chunk["text"].encode()).hexdigest()[:16]
            }
            chunk_metadata.append(metadata)

        # Step 5: Save chunks if requested
        if save_chunks:
            chunk_file = self.cache_dir / f"{document_id}_chunks.json"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk_metadata, f, indent=2, ensure_ascii=False)
            log_info(f"Saved chunk metadata to {chunk_file}")

        # Step 6: Update FAISS index if requested
        if update_index:
            if index_path is None:
                index_path = Path("data/embeddings/faiss_indices/large_text.index")

            log_info("Updating FAISS index...")
            index_start = time.time()

            # Create text identifiers for FAISS
            text_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]

            try:
                add_text_embeddings(
                    index_path=index_path,
                    embeddings=embeddings,
                    text_ids=text_ids,
                    metadata=chunk_metadata
                )
                index_time = time.time() - index_start
                log_success(f"Updated FAISS index in {index_time:.2f}s")
            except Exception as e:
                log_error(f"Failed to update index: {e}")
                index_time = 0
        else:
            index_time = 0

        # Step 7: Prepare results
        total_time = time.time() - start_time

        results = {
            "document_id": document_id,
            "file_path": str(file_path),
            "total_chunks": len(chunks),
            "total_tokens": sum(chunk["token_count"] for chunk in chunks),
            "total_characters": len(text),
            "embedding_model": self.embedding_model,
            "chunking_strategy": self.chunking_config.chunk_strategy,
            "processing_times": {
                "chunking": chunk_time,
                "embeddings": embed_time,
                "indexing": index_time,
                "total": total_time
            },
            "cost_estimate": cost_info,
            "chunk_metadata": chunk_metadata if not save_chunks else None,
            "embeddings": embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
        }

        log_success(f"Processing complete! Total time: {total_time:.2f}s")
        return results

    def search_document(
        self,
        query: str,
        document_id: str | None = None,
        top_k: int = 5,
        index_path: Path | None = None
    ) -> list[dict]:
        """Search within processed documents."""
        if index_path is None:
            index_path = Path("data/embeddings/faiss_indices/large_text.index")

        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")

        log_info(f"Searching for: '{query}'")

        # Generate query embedding
        query_embedding = generate_openai_embeddings([query], self.embedding_model)[0]

        # Search the index
        results = search_similar_texts(
            index_path=index_path,
            query_embedding=query_embedding,
            top_k=top_k * 2 if document_id else top_k  # Get more results for filtering
        )

        # Filter by document_id if specified
        if document_id:
            filtered_results = []
            for result in results:
                if result.get("metadata", {}).get("document_id") == document_id:
                    filtered_results.append(result)
                    if len(filtered_results) >= top_k:
                        break
            results = filtered_results

        log_info(f"Found {len(results)} relevant chunks")
        return results

    def process_multiple_files(
        self,
        file_paths: list[str | Path],
        document_ids: list[str] | None = None,
        index_path: Path | None = None
    ) -> dict[str, dict]:
        """Process multiple files into a single index."""
        results = {}

        if document_ids and len(document_ids) != len(file_paths):
            raise ValueError("document_ids length must match file_paths length")

        for i, file_path in enumerate(file_paths):
            doc_id = document_ids[i] if document_ids else Path(file_path).stem

            try:
                result = self.process_file(
                    file_path=file_path,
                    document_id=doc_id,
                    update_index=True,
                    index_path=index_path
                )
                results[doc_id] = result
                log_success(f"Processed {doc_id}: {result['total_chunks']} chunks")

            except Exception as e:
                log_error(f"Failed to process {file_path}: {e}")
                results[doc_id] = {"error": str(e)}

        return results


def process_large_text_file(
    file_path: str | Path,
    output_dir: Path | None = None,
    config_name: str = "large_corpus",
    embedding_model: str = "text-embedding-3-small"
) -> dict:
    """Convenience function for processing a single large text file."""
    from src.core.utils.text_chunking import CONFIGS

    config = CONFIGS.get(config_name, ChunkingConfig())

    if output_dir:
        cache_dir = output_dir / "cache"
        index_path = output_dir / "index.faiss"
    else:
        cache_dir = None
        index_path = None

    processor = LargeTextProcessor(
        chunking_config=config,
        embedding_model=embedding_model,
        cache_dir=cache_dir
    )

    return processor.process_file(
        file_path=file_path,
        update_index=True,
        index_path=index_path
    )


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="Process large text files with chunking and embeddings")
    parser.add_argument("file_path", help="Path to text file to process")
    parser.add_argument("--output-dir", help="Output directory for results")
    parser.add_argument("--config", default="large_corpus", help="Chunking configuration")
    parser.add_argument("--model", default="text-embedding-3-small", help="Embedding model")
    parser.add_argument("--document-id", help="Document identifier")

    args = parser.parse_args()

    try:
        result = process_large_text_file(
            file_path=args.file_path,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            config_name=args.config,
            embedding_model=args.model
        )

        print("\nProcessing Results:")
        print(f"Document: {result['document_id']}")
        print(f"Chunks: {result['total_chunks']}")
        print(f"Tokens: {result['total_tokens']:,}")
        print(f"Cost: ${result['cost_estimate']['estimated_cost_usd']:.4f}")
        print(f"Time: {result['processing_times']['total']:.2f}s")

    except Exception as e:
        log_error(f"Processing failed: {e}")
        sys.exit(1)
