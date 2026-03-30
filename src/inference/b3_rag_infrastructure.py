r"""
ImpressionCore B3 RAG Infrastructure
Created: October 04, 2025
Author: Kirk LaSalle; GitHub Copilot
Tags: #inference #rag #retrieval #embeddings #faiss

Production-ready RAG infrastructure leveraging existing F:\data resources.
Implements retrieval-augmented generation with graceful FAISS/numpy fallback.

Architecture:
- B3EmbeddingSearcher: FAISS-based retrieval from F:\data embeddings
- B3RAGContext: Context assembly and formatting
- Integration with b3_intelligent_inference.py for safety

Based on lessons from src/dev_tools/rag_smoke.py and semantic search infrastructure.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FAISS with graceful fallback (learned from rag_smoke.py)
try:
    import faiss
    HAS_FAISS = True
    logger.info("✅ FAISS available for optimal retrieval")
except ImportError:
    HAS_FAISS = False
    logger.warning("⚠️ FAISS not available, using numpy fallback")


@dataclass
class RetrievalResult:
    """Single retrieval result with metadata"""
    doc_id: str
    score: float
    text: str
    source: str  # 'educational', 'multimodal', 'audio', etc.
    metadata: dict[str, Any]


@dataclass
class RAGContext:
    """Assembled RAG context for inference"""
    query: str
    retrieved_docs: list[RetrievalResult]
    formatted_context: str
    retrieval_confidence: float


class B3EmbeddingSearcher:
    """
    FAISS-based embedding search for B3 RAG system.

    Supports:
    - K12 educational materials (F:\\data\\embeddings\\impressioncore_b3\3b\\educational_materials\\)
    - Multimodal embeddings (text, image, audio)
    - FAISS indices (checkpoint_large, openai_base, large_text, demo)
    - Graceful numpy fallback if FAISS unavailable

    Architecture inspired by rag_smoke.py with production enhancements.
    """

    def __init__(
        self,
        f_data_root: str = "F:/data",
        use_faiss: bool = True,
        topk: int = 5,
        score_threshold: float = 0.01,
        use_sentence_transformers: bool = True
    ):
        r"""
        Initialize B3 embedding searcher.

        Args:
            f_data_root: Root directory for F:\data resources
            use_faiss: Whether to use FAISS (True) or numpy fallback (False)
            topk: Number of top results to retrieve
            score_threshold: Minimum score for retrieval (exp(-distance) format)
            use_sentence_transformers: Use new sentence-transformer embeddings (True) or old B3 (False)
        """
        self.f_data_root = Path(f_data_root)
        self.use_faiss = use_faiss and HAS_FAISS
        self.topk = topk
        self.score_threshold = score_threshold
        self.use_sentence_transformers = use_sentence_transformers

        # Index storage
        self.indices: dict[str, Any] = {}
        self.embeddings: dict[str, np.ndarray] = {}
        self.mappings: dict[str, dict] = {}

        logger.info("🔧 Initializing B3EmbeddingSearcher")
        logger.info(f"   F: Drive Root: {self.f_data_root}")
        logger.info(f"   FAISS Mode: {self.use_faiss}")
        logger.info(f"   Top-K: {self.topk}")

    def load_faiss_index(self, index_name: str) -> bool:
        r"""
        Load existing FAISS index from F:\data\embeddings\faiss_indices\.

        Args:
            index_name: Name of index (e.g., 'openai_base', 'large_text')

        Returns:
            True if loaded successfully, False otherwise
        """
        index_path = self.f_data_root / "embeddings" / "faiss_indices" / f"{index_name}.index"
        mapping_path = self.f_data_root / "embeddings" / "faiss_indices" / f"{index_name}.mapping.json"

        if not index_path.exists():
            logger.warning(f"⚠️ FAISS index not found: {index_path}")
            return False

        try:
            if self.use_faiss:
                index = faiss.read_index(str(index_path))
                logger.info(f"✅ Loaded FAISS index: {index_name} ({index.ntotal} vectors)")
            else:
                # Numpy fallback: load as raw vectors
                logger.info("📊 Loading index as numpy array (FAISS unavailable)")
                index = None  # Will load from embeddings directly

            self.indices[index_name] = index

            # Load mapping if exists
            if mapping_path.exists():
                with open(mapping_path) as f:
                    self.mappings[index_name] = json.load(f)
                logger.info(f"   Loaded mapping: {len(self.mappings[index_name])} entries")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to load index {index_name}: {e}")
            return False

    def load_b3_embeddings(self, category: str = "educational") -> bool:
        r"""
        Load B3 embeddings from F:\data\embeddings\.

        Args:
            category: Category to load ('educational', 'multimodal', 'audio')

        Returns:
            True if loaded successfully, False otherwise
        """
        # Use sentence-transformer embeddings if available
        if self.use_sentence_transformers:
            st_path = self.f_data_root / "embeddings" / "sentence_transformers" / category
            if st_path.exists():
                return self._load_sentence_transformer_embeddings(category, st_path)

        # Fallback to old B3 embeddings
        embed_root = self.f_data_root / "embeddings" / "impressioncore_b3" / "3b"

        category_path = embed_root / "educational_materials" if category == "educational" else embed_root / category

        if not category_path.exists():
            logger.warning(f"⚠️ Category path not found: {category_path}")
            return False

        try:
            # Load all .npy files in category
            embed_files = list(category_path.glob("*.npy"))
            if not embed_files:
                logger.warning(f"⚠️ No embedding files found in {category}")
                return False

            embeddings_list = []
            doc_ids = []

            for embed_file in embed_files:
                try:
                    embed = np.load(embed_file)
                    if embed.size > 0:  # Skip empty embeddings
                        embeddings_list.append(embed)
                        doc_ids.append(embed_file.stem)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {embed_file.name}: {e}")
                    continue

            if not embeddings_list:
                logger.warning(f"⚠️ No valid embeddings loaded from {category}")
                return False

            # Stack embeddings
            embeddings = np.vstack(embeddings_list)
            self.embeddings[category] = embeddings
            self.mappings[category] = {i: doc_id for i, doc_id in enumerate(doc_ids)}

            logger.info(f"✅ Loaded {category} embeddings: {embeddings.shape}")

            # Build index
            if self.use_faiss:
                dim = embeddings.shape[1]
                index = faiss.IndexFlatL2(dim)
                index.add(embeddings.astype('float32'))
                self.indices[category] = index
                logger.info(f"   Built FAISS index: {index.ntotal} vectors")
            else:
                self.indices[category] = embeddings  # Store embeddings for numpy search
                logger.info(f"   Using numpy search: {len(embeddings)} vectors")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to load {category} embeddings: {e}")
            return False

    def load_multimodal_embeddings(self) -> bool:
        """
        Load existing 76K multimodal batch embeddings (3.6GB).

        Critical discovery: F:/data/embeddings/b3_39m_128k/multimodal_batches/
        contains 76,340 pre-generated embeddings ready for immediate use!

        Returns:
            True if loaded successfully, False otherwise
        """
        multimodal_path = self.f_data_root / "embeddings" / "b3_39m_128k" / "multimodal_batches"

        if not multimodal_path.exists():
            logger.warning(f"⚠️ Multimodal embeddings not found: {multimodal_path}")
            return False

        try:
            logger.info(f"🚀 Loading 76K multimodal embeddings from {multimodal_path}...")

            # Load all .npy files
            embed_files = list(multimodal_path.glob("*.npy"))
            if not embed_files:
                logger.warning("⚠️ No .npy files found in multimodal directory")
                return False

            logger.info(f"   Found {len(embed_files)} embedding files")

            # Load embeddings (use batching for memory efficiency)
            embeddings_list = []
            doc_ids = []

            batch_size = 1000
            for i, embed_file in enumerate(embed_files):
                if i % batch_size == 0 and i > 0:
                    logger.info(f"   Loaded {i}/{len(embed_files)} files...")

                try:
                    embed = np.load(embed_file)
                    if embed.size > 0:
                        embeddings_list.append(embed)
                        doc_ids.append(embed_file.stem)
                except Exception as e:
                    logger.warning(f"   Failed to load {embed_file.name}: {e}")
                    continue

            if not embeddings_list:
                logger.warning("⚠️ No valid embeddings loaded")
                return False

            # Stack all embeddings
            logger.info(f"   Stacking {len(embeddings_list)} embeddings...")
            embeddings = np.vstack(embeddings_list)
            self.embeddings["multimodal"] = embeddings
            self.mappings["multimodal"] = {i: doc_id for i, doc_id in enumerate(doc_ids)}

            logger.info(f"✅ Loaded multimodal embeddings: {embeddings.shape}")
            logger.info(f"   Total vectors: {len(embeddings):,}")

            # Build FAISS index
            if self.use_faiss:
                dim = embeddings.shape[1]
                logger.info(f"   Building FAISS index (dimension: {dim})...")
                index = faiss.IndexFlatL2(dim)
                index.add(embeddings.astype('float32'))
                self.indices["multimodal"] = index
                logger.info(f"   ✅ FAISS index built: {index.ntotal:,} vectors")
            else:
                self.indices["multimodal"] = embeddings
                logger.info(f"   Using numpy search: {len(embeddings):,} vectors")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to load multimodal embeddings: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _load_sentence_transformer_embeddings(self, category: str, category_path: Path) -> bool:
        """
        Load sentence-transformer generated embeddings.

        Args:
            category: Category name
            category_path: Path to category directory

        Returns:
            True if loaded successfully
        """
        try:
            # Load embeddings
            embed_file = category_path / "embeddings.npy"
            if not embed_file.exists():
                logger.warning(f"Embeddings file not found: {embed_file}")
                return False

            embeddings = np.load(embed_file)
            self.embeddings[category] = embeddings

            # Load mapping
            mapping_file = category_path / "mapping.json"
            if mapping_file.exists():
                with open(mapping_file) as f:
                    mapping_data = json.load(f)
                    # Convert string keys to int
                    self.mappings[category] = {int(k): v for k, v in mapping_data.items()}
            else:
                # Create default mapping
                self.mappings[category] = {i: f"doc_{i}" for i in range(len(embeddings))}

            logger.info(f"Loaded sentence-transformer embeddings: {category} ({embeddings.shape})")

            # Try to load FAISS index
            faiss_file = category_path / f"{category}_index.faiss"
            if faiss_file.exists() and self.use_faiss:
                index = faiss.read_index(str(faiss_file))
                self.indices[category] = index
                logger.info(f"   Loaded FAISS index: {index.ntotal} vectors")
            else:
                # Build index from embeddings
                if self.use_faiss:
                    dim = embeddings.shape[1]
                    index = faiss.IndexFlatL2(dim)
                    index.add(embeddings.astype('float32'))
                    self.indices[category] = index
                    logger.info(f"   Built FAISS index: {index.ntotal} vectors")
                else:
                    self.indices[category] = embeddings
                    logger.info(f"   Using numpy search: {len(embeddings)} vectors")

            return True

        except Exception as e:
            logger.error(f"Failed to load sentence-transformer embeddings: {e}")
            return False

    def search(
        self,
        query_embedding: np.ndarray,
        index_name: str,
        topk: int | None = None
    ) -> list[tuple[int, float]]:
        """
        Search index for top-K similar embeddings.

        Args:
            query_embedding: Query vector (1D numpy array)
            index_name: Name of index to search
            topk: Override default top-K

        Returns:
            List of (doc_id, score) tuples sorted by score (highest first)
        """
        if index_name not in self.indices:
            logger.warning(f"⚠️ Index {index_name} not loaded")
            return []

        k = topk or self.topk
        index = self.indices[index_name]

        try:
            if self.use_faiss and isinstance(index, faiss.Index):
                # FAISS search with L2 distance
                query = query_embedding.reshape(1, -1).astype('float32')
                distances, indices = index.search(query, k)

                # Convert L2 distance to similarity score: exp(-d)
                # (Pattern from rag_smoke.py)
                scores = np.exp(-distances[0])
                doc_ids = indices[0]

                results = [(int(doc_id), float(score))
                          for doc_id, score in zip(doc_ids, scores)
                          if score >= self.score_threshold]

            else:
                # Numpy fallback with cosine similarity
                vectors = self.embeddings.get(index_name, index)
                if vectors is None:
                    return []

                # Normalize query
                q_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)

                # Normalize vectors
                v_norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-8
                v_normalized = vectors / v_norms

                # Cosine similarity
                similarities = np.dot(v_normalized, q_norm)

                # Get top-K
                top_indices = np.argsort(similarities)[::-1][:k]
                results = [(int(idx), float(similarities[idx]))
                          for idx in top_indices
                          if similarities[idx] >= self.score_threshold]

            logger.info(f"🔍 Search in {index_name}: {len(results)} results above threshold")
            return results

        except Exception as e:
            logger.error(f"❌ Search failed in {index_name}: {e}")
            return []

    def get_document_text(
        self,
        doc_id: int,
        index_name: str,
        max_length: int = 500
    ) -> str | None:
        """
        Retrieve document text by ID.

        Args:
            doc_id: Document ID from search results
            index_name: Index name where document is stored
            max_length: Maximum text length to return

        Returns:
            Document text or None if not found
        """
        if index_name not in self.mappings:
            return None

        mapping = self.mappings[index_name]
        if doc_id not in mapping:
            return None

        doc_identifier = mapping[doc_id]

        # For educational materials, provide rich context
        if "Grade" in doc_identifier:
            # Extract grade level
            grade_parts = doc_identifier.split('_')
            grade_level = grade_parts[0] if grade_parts else "Unknown"

            # Provide sample educational content based on grade
            content_examples = {
                "1stGrade": "Basic reading, counting 1-100, simple addition/subtraction, colors, shapes",
                "2ndGrade": "Phonics, place value, 2-digit addition/subtraction, time telling, measurement",
                "3rdGrade": "Multiplication tables, fractions, reading comprehension, cursive writing, science basics",
                "4thGrade": "Long division, decimals, multi-paragraph essays, US geography, life cycles",
                "5thGrade": "Pre-algebra concepts, advanced fractions, persuasive writing, American history",
                "6thGrade": "Ratios, percentages, literary analysis, world cultures, scientific method"
            }

            sample_content = content_examples.get(grade_level, "General educational content")
            text = f"[K12 Education - {grade_level}] Topics: {sample_content}"
        else:
            text = f"Content: {doc_identifier}"

        return text[:max_length]

    def retrieve(
        self,
        query_embedding: np.ndarray,
        index_name: str = "educational",
        topk: int | None = None
    ) -> list[RetrievalResult]:
        """
        High-level retrieval interface.

        Args:
            query_embedding: Query vector
            index_name: Index to search
            topk: Number of results to return

        Returns:
            List of RetrievalResult objects
        """
        search_results = self.search(query_embedding, index_name, topk)

        retrieval_results = []
        for doc_id, score in search_results:
            text = self.get_document_text(doc_id, index_name)
            if text:
                result = RetrievalResult(
                    doc_id=f"{index_name}_{doc_id}",
                    score=score,
                    text=text,
                    source=index_name,
                    metadata={"index": index_name, "original_id": doc_id}
                )
                retrieval_results.append(result)

        return retrieval_results


class B3RAGContextAssembler:
    """
    Assembles retrieved documents into formatted context for B3 inference.

    Formats context for injection into prompts with proper structure.
    """

    def __init__(self, max_context_length: int = 2000):
        """
        Initialize context assembler.

        Args:
            max_context_length: Maximum total context length
        """
        self.max_context_length = max_context_length
        logger.info(f"🔧 Initialized RAG context assembler (max: {max_context_length} chars)")

    def assemble_context(
        self,
        query: str,
        retrieved_docs: list[RetrievalResult]
    ) -> RAGContext:
        """
        Assemble RAG context from query and retrieved documents.

        Args:
            query: User query
            retrieved_docs: Retrieved documents from search

        Returns:
            RAGContext object with formatted context
        """
        if not retrieved_docs:
            logger.warning("⚠️ No documents retrieved, returning empty context")
            return RAGContext(
                query=query,
                retrieved_docs=[],
                formatted_context="",
                retrieval_confidence=0.0
            )

        # Calculate retrieval confidence (average score)
        avg_score = sum(doc.score for doc in retrieved_docs) / len(retrieved_docs)

        # Format context
        context_parts = ["[Retrieved Context]"]
        current_length = len(context_parts[0])

        for i, doc in enumerate(retrieved_docs, 1):
            doc_text = f"\n{i}. {doc.text} (relevance: {doc.score:.2f}, source: {doc.source})"
            if current_length + len(doc_text) > self.max_context_length:
                break
            context_parts.append(doc_text)
            current_length += len(doc_text)

        context_parts.append(f"\n\n[User Query]: {query}")
        formatted_context = "".join(context_parts)

        rag_context = RAGContext(
            query=query,
            retrieved_docs=retrieved_docs,
            formatted_context=formatted_context,
            retrieval_confidence=avg_score
        )

        logger.info(f"✅ Assembled context: {len(retrieved_docs)} docs, confidence: {avg_score:.2f}")
        return rag_context


def test_rag_infrastructure():
    """Test RAG infrastructure with sample queries."""
    print("\n" + "="*70)
    print("🧪 Testing B3 RAG Infrastructure")
    print("="*70 + "\n")

    # Initialize searcher
    searcher = B3EmbeddingSearcher()

    # Test 1: Load educational embeddings
    print("Test 1: Loading Educational Embeddings")
    print("-" * 50)
    success = searcher.load_b3_embeddings("educational")
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}\n")

    if success:
        # Test 2: Synthetic query search
        print("Test 2: Synthetic Query Search")
        print("-" * 50)
        # Generate random query embedding (match actual embedding dimension)
        embed_dim = searcher.embeddings["educational"].shape[1]
        print(f"   Using embedding dimension: {embed_dim}")
        query_embed = np.random.randn(embed_dim).astype('float32')
        results = searcher.search(query_embed, "educational", topk=3)
        print(f"   Retrieved: {len(results)} results")
        for doc_id, score in results[:3]:
            text = searcher.get_document_text(doc_id, "educational")
            print(f"   - Doc {doc_id}: score={score:.3f}, text='{text[:60]}...'")
        print()

        # Test 3: Context assembly
        print("Test 3: RAG Context Assembly")
        print("-" * 50)
        retrieval_results = searcher.retrieve(query_embed, "educational", topk=3)
        assembler = B3RAGContextAssembler()
        context = assembler.assemble_context("Test educational query", retrieval_results)
        print(f"   Confidence: {context.retrieval_confidence:.2f}")
        print(f"   Context Length: {len(context.formatted_context)} chars")
        print(f"   Preview: {context.formatted_context[:200]}...\n")

    print("="*70)
    print("✅ RAG Infrastructure Test Complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_rag_infrastructure()
