
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from src.core.utils import vector_index

# Setup Logger
logger = logging.getLogger("VectorMemory")

class VectorMemoryConnector:
    """
    Connects the Unified Triad to the Vector Database (FAISS).
    Handles embedding generation (using sentence-transformers if available, else fallback)
    and ingestion of visual memories.
    """
    def __init__(self, db_path: str = "src/core/vector_database_1"):
        self.db_path = Path(db_path)
        self.index_path = self.db_path / "index.faiss"
        self.model = None
        self.has_transformers = False

        # Initialize DB directory
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Try to load Sentence Transformer
        try:
            from sentence_transformers import SentenceTransformer
            # Use a lightweight model for GTX 1050 Ti compatibility
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.has_transformers = True
            logger.info("VectorMemory: Loaded 'all-MiniLM-L6-v2' on device.")
        except ImportError:
            logger.warning("VectorMemory: sentence-transformers not found. Using random/hash embeddings (Not recommended for production).")
        except Exception as e:
            logger.warning(f"VectorMemory: Failed to load model: {e}")

    def get_embedding(self, text: str) -> np.ndarray:
        """Generates a normalized embedding vector."""
        if self.has_transformers and self.model:
            embedding = self.model.encode([text])[0]
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            return embedding.reshape(1, -1)
        else:
            # Fallback: Hash-based "embedding" (Deterministic but non-semantic)
            # This allows the system to run without crashing, but retrieval will be exact-match only basically.
            # 384 dimensions to match MiniLM
            np.random.seed(hash(text) % (2**32))
            return np.random.rand(1, 384).astype(np.float32)

    def add_memory(self, text: str, snapshot_url: str | None = None, metadata: dict | None = None):
        """
        Adds a text memory (with optional snapshot) to the vector database.
        """
        if not text:
            return

        vector = self.get_embedding(text)

        meta = metadata or {}
        meta["text"] = text
        meta["snapshot_url"] = snapshot_url
        meta["timestamp"] = datetime.now().isoformat()

        # ID Generation
        mem_id = f"mem_{int(datetime.now().timestamp())}_{hash(text) % 1000}"

        # Ingest using vector_index utility
        try:
            vector_index.add_text_embeddings(
                index_path=self.index_path,
                embeddings=vector,
                text_ids=[mem_id],
                metadata=[meta]
            )
            logger.info(f"VectorMemory: Persisted memory '{text[:30]}...' with ID {mem_id}")
        except Exception as e:
            logger.error(f"VectorMemory: Write Failed: {e}")

    def add_device_profile(self, device_id: str, profile_data: dict):
        """
        Adds a camera device profile to RAG for semantic search.

        Args:
            device_id: Device identifier (VID_PID format)
            profile_data: Full profile dictionary
        """
        # Create searchable text from profile
        text = f"Camera Device: {profile_data.get('name', 'Unknown')}\n"
        text += f"Manufacturer: {profile_data.get('manufacturer', 'Unknown')}\n"
        text += f"Device ID: {device_id}\n"

        caps = profile_data.get('capabilities', {})
        text += f"Capabilities: pan={caps.get('pan')}, tilt={caps.get('tilt')}, "
        text += f"zoom={caps.get('zoom')}, motor_control={caps.get('motor_control')}\n"

        if profile_data.get('notes'):
            text += f"Notes: {profile_data['notes']}\n"

        self.add_memory(
            text=text,
            metadata={
                "type": "device_profile",
                "device_id": device_id,
                "full_profile": profile_data
            }
        )
        logger.info(f"VectorMemory: Added device profile for {device_id}")

    def add_device_document(self, device_id: str, document: str, doc_type: str = "notes"):
        """
        Adds a document to a device's RAG documentation library.

        Args:
            device_id: Device identifier (VID_PID format)
            document: Document content
            doc_type: Type of document (notes, manual, calibration, etc.)
        """
        text = f"[Device: {device_id}] [{doc_type.upper()}]\n{document}"

        self.add_memory(
            text=text,
            metadata={
                "type": "device_document",
                "device_id": device_id,
                "doc_type": doc_type
            }
        )
        logger.info(f"VectorMemory: Added {doc_type} document for {device_id}")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Semantic search across all memories (not device-specific).

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of matching results with metadata
        """
        try:
            query_vec = self.get_embedding(query)

            results = vector_index.search_similar_texts(
                index_path=self.index_path,
                query_embedding=query_vec,
                top_k=top_k
            )
            return results
        except Exception as e:
            logger.error(f"VectorMemory: Search failed: {e}")
            return []

    def search_device_docs(self, device_id: str, query: str, top_k: int = 5) -> list[dict]:

        """
        Searches device documentation in RAG.

        Args:
            device_id: Device identifier to filter by
            query: Search query
            top_k: Number of results to return

        Returns:
            List of matching document metadata
        """
        try:
            # Get embedding for query
            query_vec = self.get_embedding(query)

            # Search using vector_index
            results = vector_index.search_similar_texts(
                index_path=self.index_path,
                query_embedding=query_vec,
                top_k=top_k * 2  # Get more to filter
            )

            # Filter by device_id
            filtered = []
            for r in results:
                meta = r.get("metadata", {})
                if meta.get("device_id") == device_id:
                    filtered.append(r)
                    if len(filtered) >= top_k:
                        break

            return filtered
        except Exception as e:
            logger.error(f"VectorMemory: Search failed: {e}")
            return []

    def get_device_context(self, device_id: str) -> str:
        """
        Gets a context summary for a device to include in LLM prompts.

        Args:
            device_id: Device identifier

        Returns:
            Formatted context string
        """
        docs = self.search_device_docs(device_id, "capabilities settings notes", top_k=3)

        if not docs:
            return f"No stored context for device {device_id}."

        context = f"Device Context for {device_id}:\n"
        for doc in docs:
            text = doc.get("metadata", {}).get("text", "")[:500]
            context += f"- {text}\n"

        return context
