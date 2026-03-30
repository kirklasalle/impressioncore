"""
Knowledge Tool - Document Indexing and Semantic Search

Created: January 13, 2026
Author: ImpressionCore Team

Tool for Agent0Core to index and search ImpressionCore documentation
using FAISS vector index for semantic similarity search.
"""

import logging
import sys
from pathlib import Path
from typing import Any

# Add ImpressionCore src to path for imports
_project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_project_root / "src"))

from ..governance import require_law_compliance

logger = logging.getLogger("agent0core.tools.knowledge")


class KnowledgeTool:
    """
    Tool for indexing and searching ImpressionCore documentation.

    Supports:
    - Document indexing with embeddings
    - Semantic similarity search
    - Knowledge base management
    """

    name = "knowledge_tool"
    description = "Index and search ImpressionCore documentation"

    # Paths
    DOCS_DIR = _project_root / "docs"
    SRC_DIR = _project_root / "src"
    INDEX_DIR = _project_root / "agent0core" / "knowledge" / "index"

    def __init__(self):
        """Initialize the knowledge tool."""
        self._index = None
        self._mapping = None
        self._embedder = None
        logger.info("KnowledgeTool initialized")

    def _lazy_load_vector_index(self) -> bool:
        """Lazy load the vector index utilities."""
        try:
            from core.utils.vector_index import (
                add_text_embeddings,
                load_index_and_mapping,
                search_similar_texts,
            )
            self._vector_utils = {
                "load": load_index_and_mapping,
                "add": add_text_embeddings,
                "search": search_similar_texts,
            }
            logger.info("Vector index utilities loaded")
            return True
        except ImportError as e:
            logger.warning(f"Vector index not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load vector index: {e}")
            return False

    def _get_index_path(self) -> Path:
        """Get path to the FAISS index file."""
        self.INDEX_DIR.mkdir(parents=True, exist_ok=True)
        return self.INDEX_DIR / "impressioncore.faiss"

    @require_law_compliance
    async def execute(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a knowledge action.

        Args:
            action: The action to perform
            params: Optional parameters

        Returns:
            Result dictionary
        """
        params = params or {}

        if action == "search":
            return await self._search(params.get("query", ""))
        elif action == "index_docs":
            return await self._index_docs(params.get("directory"))
        elif action == "list_indexed":
            return await self._list_indexed()
        elif action == "stats":
            return await self._get_stats()
        elif action == "clear":
            return await self._clear_index()
        else:
            return {"error": f"Unknown action: {action}", "available_actions": [
                "search", "index_docs", "list_indexed", "stats", "clear"
            ]}

    async def _search(self, query: str) -> dict[str, Any]:
        """Search for documents similar to query using VectorMemoryConnector."""
        if not query:
            return {"error": "Query is required"}

        # Try vector provider first (ImpressionCore's semantic search via DI boundary)
        try:
            from agent0core.integrations.impressioncore import get_vector_provider
            vector_memory = get_vector_provider()
            if vector_memory is None:
                raise RuntimeError("VectorMemoryProvider not registered")

            # Use the provider's search method
            raw_results = vector_memory.search(query, top_k=5)

            # Format results
            results = []
            if isinstance(raw_results, list):
                for r in raw_results:
                    if isinstance(r, dict):
                        results.append(r)
                    else:
                        results.append({"content": str(r), "score": 0.0})

            return {
                "query": query,
                "results": results,
                "count": len(results),
                "method": "vector_memory_connector",
            }
        except ImportError:
            logger.warning("VectorMemoryConnector not available, using fallback")
        except Exception as e:
            logger.warning(f"VectorMemoryConnector search failed: {e}")

        # Fall back to simple file search
        return await self._simple_search(query)

    async def _simple_search(self, query: str) -> dict[str, Any]:
        """Simple text search fallback when FAISS not available."""
        results = []
        query_lower = query.lower()

        # Search in docs directory
        for doc_path in self.DOCS_DIR.rglob("*.md"):
            try:
                content = doc_path.read_text(encoding="utf-8", errors="ignore")
                if query_lower in content.lower():
                    # Find context around match
                    idx = content.lower().find(query_lower)
                    start = max(0, idx - 100)
                    end = min(len(content), idx + len(query) + 100)
                    snippet = content[start:end]

                    results.append({
                        "file": str(doc_path.relative_to(_project_root)),
                        "snippet": snippet,
                        "type": "simple_search",
                    })
            except Exception:
                continue

        return {
            "query": query,
            "results": results[:10],  # Limit to 10
            "count": len(results),
            "method": "simple_text_search",
        }

    async def _index_docs(self, directory: str | None = None) -> dict[str, Any]:
        """Index documents from a directory."""
        target_dir = Path(directory) if directory else self.DOCS_DIR

        if not target_dir.exists():
            return {"error": f"Directory not found: {target_dir}"}

        # Count documents
        md_files = list(target_dir.rglob("*.md"))
        py_files = list(target_dir.rglob("*.py"))
        txt_files = list(target_dir.rglob("*.txt"))

        total = len(md_files) + len(py_files) + len(txt_files)

        # For now, return stats (full indexing requires embeddings API)
        return {
            "status": "ready_to_index",
            "directory": str(target_dir),
            "files": {
                "markdown": len(md_files),
                "python": len(py_files),
                "text": len(txt_files),
                "total": total,
            },
            "note": "Full indexing requires embeddings API integration",
        }

    async def _list_indexed(self) -> dict[str, Any]:
        """List indexed documents."""
        mapping_path = self._get_index_path().with_suffix(".mapping.json")

        if not mapping_path.exists():
            return {"indexed": [], "count": 0, "message": "No index found"}

        try:
            import json
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            entries = mapping.get("entries", [])

            return {
                "count": len(entries),
                "sample": entries[:5] if entries else [],
                "index_path": str(self._get_index_path()),
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_stats(self) -> dict[str, Any]:
        """Get knowledge base statistics."""
        stats = {
            "docs_dir_exists": self.DOCS_DIR.exists(),
            "index_exists": self._get_index_path().exists(),
        }

        if self.DOCS_DIR.exists():
            stats["doc_count"] = len(list(self.DOCS_DIR.rglob("*.md")))

        if self._get_index_path().exists():
            mapping_path = self._get_index_path().with_suffix(".mapping.json")
            if mapping_path.exists():
                try:
                    import json
                    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
                    stats["indexed_count"] = len(mapping.get("entries", []))
                    stats["embedding_dim"] = mapping.get("dim")
                except Exception:
                    pass

        return stats

    async def _clear_index(self) -> dict[str, Any]:
        """Clear the knowledge index."""
        index_path = self._get_index_path()
        mapping_path = index_path.with_suffix(".mapping.json")

        deleted = []
        if index_path.exists():
            index_path.unlink()
            deleted.append(str(index_path.name))
        if mapping_path.exists():
            mapping_path.unlink()
            deleted.append(str(mapping_path.name))

        return {
            "status": "cleared",
            "deleted": deleted,
        }
