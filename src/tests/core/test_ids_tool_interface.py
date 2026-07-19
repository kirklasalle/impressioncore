"""Unit tests for src.core.utils.ids_tool_interface."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.core.utils.ids_tool_interface import (
    IDSCacheEntry,
    IDSQueryResult,
    IDSSearchResponse,
    IDSToolInterface,
    IDSWorkspaceEnhancer,
)


@pytest.fixture
def mock_ids_interface():
    with patch("src.core.utils.ids_tool_interface.IDSToolInterface.load_indices", return_value=True):
        interface = IDSToolInterface()
        interface.unified_index = {
            "src/core/utils/paths.py": ["path", "config", "core"],
            "src/interfaces/web/server.py": ["api", "web", "server", "core"],
            "docs/ARCHITECTURE.md": ["docs", "architecture", "overview"],
        }
        interface.file_metadata = {
            "src/core/utils/paths.py": {
                "type": "source_code",
                "category": "core",
                "title": "Paths Configuration",
                "description": "Configures paths",
            },
            "src/interfaces/web/server.py": {
                "type": "source_code",
                "category": "interfaces",
                "title": "Web Server",
                "description": "API Server interface",
            },
            "docs/ARCHITECTURE.md": {
                "type": "documentation",
                "category": "docs",
                "title": "System Architecture",
                "description": "Architecture overview",
            },
        }
        interface._build_cross_references()
        interface.workspace_enhancer = IDSWorkspaceEnhancer(interface)
        return interface


def test_calculate_relevance(mock_ids_interface):
    metadata = {"title": "Test Path Config", "type": "source_code"}
    score = mock_ids_interface._calculate_relevance("path", ["path", "config"], metadata)
    assert score > 0.3


def test_calculate_tag_similarity(mock_ids_interface):
    enhancer = mock_ids_interface.workspace_enhancer
    sim = enhancer._calculate_tag_similarity(["a", "b", "c"], ["b", "c", "d"])
    assert sim == 0.5  # intersection (2) / union (4) = 0.5


def test_calculate_dependency_score(mock_ids_interface):
    enhancer = mock_ids_interface.workspace_enhancer
    score = enhancer._calculate_dependency_score(
        "src/core/utils/paths.py", "src/core/utils/logging.py", {}
    )
    assert score == 0.8  # same directory


def test_calculate_file_similarity(mock_ids_interface):
    enhancer = mock_ids_interface.workspace_enhancer
    m1 = {"type": "source_code", "category": "core", "title": "Paths Configuration"}
    m2 = {"type": "source_code", "category": "core", "title": "Logging Configuration"}
    similarity = enhancer._calculate_file_similarity(m1, m2)
    assert similarity > 0.5


def test_query_unified(mock_ids_interface):
    response = mock_ids_interface.query("architecture", search_type="unified")
    assert isinstance(response, IDSSearchResponse)
    assert response.total_results == 1
    assert response.results[0].file_path == "docs/ARCHITECTURE.md"


def test_query_tag(mock_ids_interface):
    response = mock_ids_interface.query("core", search_type="tag")
    assert response.total_results == 2


def test_query_file(mock_ids_interface):
    response = mock_ids_interface.query("server.py", search_type="file")
    assert response.total_results == 1
    assert response.results[0].file_path == "src/interfaces/web/server.py"


def test_get_statistics(mock_ids_interface):
    stats = mock_ids_interface.get_statistics()
    assert stats["total_files"] == 3
    assert "core" in stats["categories"]


def test_format_results_json(mock_ids_interface):
    response = mock_ids_interface.query("core", search_type="tag")
    json_str = mock_ids_interface.format_results_json(response)
    data = json.loads(json_str)
    assert data["total_results"] == 2


def test_format_results_table(mock_ids_interface):
    response = mock_ids_interface.query("core", search_type="tag")
    table_str = mock_ids_interface.format_results_table(response)
    assert "src/core/utils/paths.py" in table_str


def test_workspace_enhancer_queries(mock_ids_interface):
    enhancer = mock_ids_interface.workspace_enhancer
    hint = enhancer.enhance_search_query("api server")
    assert "src/interfaces/web/server.py" in hint.suggested_files
    assert hint.confidence_score > 0.0


def test_workspace_enhancer_suggest_patterns(mock_ids_interface):
    enhancer = mock_ids_interface.workspace_enhancer
    patterns = enhancer.suggest_file_patterns("docs")
    assert any("docs" in p or "md" in p for p in patterns)


def test_workspace_enhancer_get_context_files(mock_ids_interface):
    enhancer = mock_ids_interface.workspace_enhancer
    files = enhancer.get_context_files("src/core/utils/paths.py")
    assert isinstance(files, list)


def test_workspace_enhancer_suggestions(mock_ids_interface):
    enhancer = mock_ids_interface.workspace_enhancer
    suggestions = enhancer.smart_search_suggestions("arch")
    assert "architecture" in suggestions
