"""
IDS Tool for Agent0Core

SAL-native tool for documentation search, validation, and management.
Integrates with both FAISS semantic search and keyword-based IDS.

Created: January 18, 2026
Author: Agent0 (SAL)
"""
import logging
import sys
from pathlib import Path
from typing import Any

# Add project paths
_project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_project_root / "src"))

from ..governance import require_law_compliance

logger = logging.getLogger("agent0core.tools.ids")


class IDSTool:
    """
    SAL-native IDS Tool for Agent0.

    Provides:
    - Hybrid search (semantic + keyword)
    - Document validation
    - Header analysis
    """

    name = "ids"
    description = "Documentation system search and management"

    def __init__(self):
        self._vector_connector = None
        self._enhanced_ids = None
        logger.info("IDSTool initialized")

    def _lazy_load_vector(self):
        """Lazy load vector connector for semantic search."""
        if self._vector_connector is None:
            try:
                from agent0core.integrations.impressioncore import get_vector_provider
                provider = get_vector_provider()
                if provider is None:
                    logger.warning("IDSTool: VectorMemoryProvider not registered")
                    return False
                self._vector_connector = provider
                logger.info("IDSTool: Vector connector loaded via DI boundary")
            except Exception as e:
                logger.warning(f"IDSTool: Vector connector not available: {e}")
        return self._vector_connector is not None

    def _lazy_load_ids(self):
        """Lazy load enhanced IDS for keyword search."""
        if self._enhanced_ids is None:
            try:
                sys.path.insert(0, str(_project_root / "docs"))
                from enhanced_ids import EnhancedIDS
                self._enhanced_ids = EnhancedIDS()
                logger.info("IDSTool: EnhancedIDS loaded")
            except Exception as e:
                logger.warning(f"IDSTool: EnhancedIDS not available: {e}")
        return self._enhanced_ids is not None

    @require_law_compliance
    async def execute(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute an IDS action.

        Actions:
        - search: Hybrid semantic + keyword search
        - validate: Check document health
        - stats: Get documentation statistics
        - list_tags: List available tags
        """
        params = params or {}

        if action == "search":
            return await self._hybrid_search(params.get("query", ""), params.get("limit", 10))
        elif action == "validate":
            return await self._validate_doc(params.get("path", ""))
        elif action == "stats":
            return await self._get_stats()
        elif action == "list_tags":
            return await self._list_tags(params.get("category"))
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    async def _hybrid_search(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Perform hybrid semantic + keyword search."""
        results = []

        # 1. Semantic search via FAISS
        if self._lazy_load_vector():
            try:
                semantic_results = self._vector_connector.search(query, top_k=limit)
                for r in semantic_results:
                    meta = r.get("metadata", {})
                    if meta.get("type") == "documentation":
                        results.append({
                            "source": "semantic",
                            "path": meta.get("file_path", ""),
                            "title": meta.get("title", ""),
                            "relevance": 1.0 - r.get("distance", 0) / 10,
                            "excerpt": r.get("text", "")[:200]
                        })
            except Exception as e:
                logger.warning(f"Semantic search failed: {e}")

        # 2. Keyword search via EnhancedIDS
        if self._lazy_load_ids():
            try:
                keyword_results = self._enhanced_ids.search(query, max_results=limit)
                for r in keyword_results.get("results", []):
                    # Avoid duplicates
                    path = r.get("file_path", "")
                    if not any(res["path"] == path for res in results):
                        results.append({
                            "source": "keyword",
                            "path": path,
                            "title": Path(path).stem.replace("_", " ").title(),
                            "relevance": 0.8,
                            "tags": r.get("matching_tags", [])
                        })
            except Exception as e:
                logger.warning(f"Keyword search failed: {e}")

        # Sort by relevance
        results.sort(key=lambda x: x.get("relevance", 0), reverse=True)

        return {
            "status": "success",
            "query": query,
            "total": len(results),
            "results": results[:limit]
        }

    async def _validate_doc(self, path: str) -> dict[str, Any]:
        """Validate a document's health (header, structure, etc.)."""
        doc_path = _project_root / "docs" / path

        if not doc_path.exists():
            return {"status": "error", "message": f"Document not found: {path}"}

        issues = []
        content = doc_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')

        # Check for header
        has_created = any(line.startswith('**Created:**') or 'created:' in line.lower() for line in lines[:15])
        has_updated = any(line.startswith('**Updated:**') or 'updated:' in line.lower() for line in lines[:15])
        has_tags = any(line.startswith('**Tags:**') or 'tags:' in line.lower() for line in lines[:15])

        if not has_created:
            issues.append("Missing 'Created' date")
        if not has_updated:
            issues.append("Missing 'Updated' date")
        if not has_tags:
            issues.append("Missing 'Tags'")

        # Check for title
        has_title = any(line.startswith('# ') for line in lines[:10])
        if not has_title:
            issues.append("Missing H1 title")

        return {
            "status": "success",
            "path": path,
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendation": "Update header to match IDS standard" if issues else "Document is healthy"
        }

    async def _get_stats(self) -> dict[str, Any]:
        """Get documentation statistics."""
        docs_dir = _project_root / "docs"

        total_md = len(list(docs_dir.rglob("*.md")))
        total_dirs = len([d for d in docs_dir.iterdir() if d.is_dir()])

        # Check FAISS index
        faiss_count = 0
        if self._lazy_load_vector():
            try:
                index_path = Path("src/core/vector_database_1/index.faiss.mapping.json")
                if index_path.exists():
                    import json
                    mapping = json.loads(index_path.read_text())
                    faiss_count = len(mapping.get("entries", []))
            except (OSError, ValueError, KeyError):
                pass

        return {
            "status": "success",
            "total_markdown_files": total_md,
            "total_directories": total_dirs,
            "faiss_indexed": faiss_count,
            "search_backends": ["semantic (FAISS)", "keyword (EnhancedIDS)"]
        }

    async def _list_tags(self, category: str | None = None) -> dict[str, Any]:
        """List available IDS tags."""
        if not self._lazy_load_ids():
            return {"status": "error", "message": "EnhancedIDS not available"}

        try:
            tags_info = self._enhanced_ids.list_tags(category=category)
            return {"status": "success", **tags_info}
        except Exception as e:
            return {"status": "error", "message": str(e)}
