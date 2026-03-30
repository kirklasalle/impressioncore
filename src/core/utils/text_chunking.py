"""
text_chunking.py

Created: August 21, 2025
Author: GitHub Copilot
Purpose: Intelligent text chunking strategies for OpenAI embeddings and large text processing.

Key insights from OpenAI embeddings documentation:
- text-embedding-3-small: 1536 dimensions, 8191 token limit
- text-embedding-3-large: 3072 dimensions, 8191 token limit
- Best practices: semantic chunking over fixed-size chunking
- Overlap strategies improve retrieval quality
"""

import re
from dataclasses import dataclass
from pathlib import Path

import tiktoken

from .rich_logging import log_info, log_warning


@dataclass
class ChunkingConfig:
    """Configuration for text chunking strategies."""
    max_tokens: int = 7000  # Leave buffer below 8191 limit
    overlap_tokens: int = 200  # Overlap between chunks for context preservation
    chunk_strategy: str = "semantic"  # "semantic", "fixed", "sentence", "paragraph"
    model_name: str = "text-embedding-3-small"  # For tokenizer selection
    preserve_structure: bool = True  # Maintain document structure when possible
    min_chunk_size: int = 100  # Minimum tokens per chunk


class TextChunker:
    """Intelligent text chunking for OpenAI embeddings."""

    def __init__(self, config: ChunkingConfig | None = None):
        self.config = config or ChunkingConfig()
        self.encoding = tiktoken.encoding_for_model(self.config.model_name)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using OpenAI's tokenizer."""
        return len(self.encoding.encode(text))

    def chunk_by_sentences(self, text: str) -> list[str]:
        """Chunk text by sentences with token limits and overlap."""
        # Split into sentences using multiple delimiters
        sentences = re.split(r'[.!?]+\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = ""
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            # If adding this sentence exceeds limit, save current chunk
            if current_tokens + sentence_tokens > self.config.max_tokens and current_chunk:
                chunks.append(current_chunk.strip())

                # Start new chunk with overlap
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = overlap_text + " " + sentence if overlap_text else sentence
                current_tokens = self.count_tokens(current_chunk)
            else:
                current_chunk += " " + sentence if current_chunk else sentence
                current_tokens += sentence_tokens

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return [c for c in chunks if self.count_tokens(c) >= self.config.min_chunk_size]

    def chunk_by_paragraphs(self, text: str) -> list[str]:
        """Chunk text by paragraphs with smart overflow handling."""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        chunks = []
        current_chunk = ""
        current_tokens = 0

        for paragraph in paragraphs:
            para_tokens = self.count_tokens(paragraph)

            # If paragraph itself is too large, split it by sentences
            if para_tokens > self.config.max_tokens:
                # Process current chunk first
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                    current_tokens = 0

                # Split large paragraph
                para_chunks = self.chunk_by_sentences(paragraph)
                chunks.extend(para_chunks)
                continue

            # Check if adding paragraph exceeds limit
            if current_tokens + para_tokens > self.config.max_tokens and current_chunk:
                chunks.append(current_chunk.strip())

                # Start new chunk with overlap
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = overlap_text + "\n\n" + paragraph if overlap_text else paragraph
                current_tokens = self.count_tokens(current_chunk)
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
                current_tokens += para_tokens

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return [c for c in chunks if self.count_tokens(c) >= self.config.min_chunk_size]

    def chunk_semantic(self, text: str) -> list[str]:
        """Semantic chunking that preserves meaning and context."""
        # First try paragraph-based chunking (best for semantic coherence)
        if '\n\n' in text:
            chunks = self.chunk_by_paragraphs(text)
        else:
            # Fallback to sentence-based chunking
            chunks = self.chunk_by_sentences(text)

        # Post-process: merge very small chunks with neighbors
        return self._merge_small_chunks(chunks)

    def chunk_fixed_size(self, text: str) -> list[str]:
        """Fixed-size chunking with word boundary preservation."""
        tokens = self.encoding.encode(text)
        chunks = []

        start_idx = 0
        while start_idx < len(tokens):
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.config.max_tokens, len(tokens))

            # Extract chunk tokens
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)

            # Ensure we don't break words (find last complete word)
            if end_idx < len(tokens):
                chunk_text = self._trim_to_word_boundary(chunk_text)

            chunks.append(chunk_text)

            # Calculate overlap for next chunk
            overlap_tokens = min(self.config.overlap_tokens, len(chunk_tokens) // 2)
            start_idx = end_idx - overlap_tokens

        return [c for c in chunks if self.count_tokens(c) >= self.config.min_chunk_size]

    def chunk_text(self, text: str) -> list[dict[str, str | int]]:
        """Main chunking method that returns chunks with metadata."""
        if not text.strip():
            return []

        # Select chunking strategy
        if self.config.chunk_strategy == "semantic":
            chunks = self.chunk_semantic(text)
        elif self.config.chunk_strategy == "sentence":
            chunks = self.chunk_by_sentences(text)
        elif self.config.chunk_strategy == "paragraph":
            chunks = self.chunk_by_paragraphs(text)
        elif self.config.chunk_strategy == "fixed":
            chunks = self.chunk_fixed_size(text)
        else:
            log_warning(f"Unknown strategy {self.config.chunk_strategy}, using semantic")
            chunks = self.chunk_semantic(text)

        # Add metadata to chunks
        chunk_data = []
        for i, chunk in enumerate(chunks):
            chunk_data.append({
                "text": chunk,
                "chunk_id": i,
                "token_count": self.count_tokens(chunk),
                "char_count": len(chunk),
                "strategy": self.config.chunk_strategy
            })

        log_info(f"Created {len(chunk_data)} chunks using {self.config.chunk_strategy} strategy")
        return chunk_data

    def _get_overlap(self, text: str) -> str:
        """Extract overlap text from end of current chunk."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= self.config.overlap_tokens:
            return text

        overlap_tokens = tokens[-self.config.overlap_tokens:]
        overlap_text = self.encoding.decode(overlap_tokens)

        # Trim to sentence boundary if possible
        sentences = re.split(r'[.!?]+\s+', overlap_text)
        if len(sentences) > 1:
            # Use complete sentences for overlap
            return '. '.join(sentences[1:])  # Skip potentially truncated first sentence

        return overlap_text

    def _trim_to_word_boundary(self, text: str) -> str:
        """Trim text to last complete word boundary."""
        if not text:
            return text

        # Find last space or punctuation
        for i in range(len(text) - 1, -1, -1):
            if text[i] in ' \t\n.,;:!?':
                return text[:i+1].rstrip()

        return text  # No boundary found, return as-is

    def _merge_small_chunks(self, chunks: list[str]) -> list[str]:
        """Merge chunks that are too small with their neighbors."""
        if not chunks:
            return chunks

        merged = []
        i = 0

        while i < len(chunks):
            current_chunk = chunks[i]
            current_tokens = self.count_tokens(current_chunk)

            # If chunk is too small and we can merge with next
            if (current_tokens < self.config.min_chunk_size and
                i + 1 < len(chunks)):

                next_chunk = chunks[i + 1]
                combined = current_chunk + "\n\n" + next_chunk
                combined_tokens = self.count_tokens(combined)

                # If combined chunk is within limits, merge
                if combined_tokens <= self.config.max_tokens:
                    merged.append(combined)
                    i += 2  # Skip next chunk as it's merged
                    continue

            merged.append(current_chunk)
            i += 1

        return merged


def chunk_file(
    file_path: str | Path,
    config: ChunkingConfig | None = None
) -> list[dict[str, str | int]]:
    """Chunk a text file using specified strategy."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        text = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        log_warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
        text = file_path.read_text(encoding='latin-1')

    chunker = TextChunker(config)
    return chunker.chunk_text(text)


def estimate_embedding_cost(
    chunks: list[dict[str, str | int]],
    model: str = "text-embedding-3-small"
) -> dict[str, int | float]:
    """Estimate cost for embedding generation."""
    total_tokens = sum(chunk["token_count"] for chunk in chunks)

    # OpenAI pricing (as of Jan 2024, verify current rates)
    pricing = {
        "text-embedding-3-small": 0.00002,  # $0.02 per 1M tokens
        "text-embedding-3-large": 0.00013,  # $0.13 per 1M tokens
        "text-embedding-ada-002": 0.0001,   # $0.10 per 1M tokens
    }

    rate = pricing.get(model, pricing["text-embedding-3-small"])
    estimated_cost = total_tokens * rate

    return {
        "total_chunks": len(chunks),
        "total_tokens": total_tokens,
        "estimated_cost_usd": estimated_cost,
        "model": model,
        "avg_tokens_per_chunk": total_tokens / len(chunks) if chunks else 0
    }


# Example usage configurations
CONFIGS = {
    "academic_paper": ChunkingConfig(
        max_tokens=6000,
        overlap_tokens=300,
        chunk_strategy="semantic",
        preserve_structure=True
    ),
    "documentation": ChunkingConfig(
        max_tokens=5000,
        overlap_tokens=200,
        chunk_strategy="paragraph",
        preserve_structure=True
    ),
    "conversation": ChunkingConfig(
        max_tokens=4000,
        overlap_tokens=100,
        chunk_strategy="sentence",
        preserve_structure=False
    ),
    "large_corpus": ChunkingConfig(
        max_tokens=7000,
        overlap_tokens=300,
        chunk_strategy="semantic",
        preserve_structure=True,
        min_chunk_size=200
    )
}
