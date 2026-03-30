#!/usr/bin/env python3
"""
IDS Tool Interface - Integrated Search Cache for ImpressionCore Documentation System
====================================================================================

This module provides a tool-like interface for the IDS that integrates with workspace
searches to provide cached, indexed search capabilities. Acts as a local knowledge
cache to increase search efficiency and provide contextual information.

Features:
- Cached search results for faster repeated queries
- Integration with workspace semantic search
- Contextual file recommendations
- Cross-reference lookup capabilities
- Tag-based knowledge discovery

Author: GitHub Copilot
Created: 2025-06-05
Last Modified: 2025-06-05
"""

import sys
import json
import yaml
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DOCS_ROOT = PROJECT_ROOT / "docs"
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

@dataclass
class IDSQueryResult:
    """Result structure for IDS queries."""
    file_path: str
    file_type: str
    category: str
    tags: List[str]
    matching_tags: List[str]
    metadata: Dict[str, Any]
    relevance_score: float = 0.0
    cache_hit: bool = False
    related_files: List[str] = field(default_factory=list)

@dataclass
class IDSSearchResponse:
    """Response structure for IDS searches."""
    query: str
    results: List[IDSQueryResult]
    total_results: int
    search_type: str
    timestamp: str
    execution_time_ms: float
    cache_hit: bool = False
    related_queries: List[str] = field(default_factory=list)

@dataclass
class IDSCacheEntry:
    """Cache entry for search results."""
    query_hash: str
    response: IDSSearchResponse
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)

# Workspace Search Enhancement Classes
@dataclass
class WorkspaceSearchHint:
    """Hints for enhancing workspace searches."""
    suggested_files: List[str]
    related_tags: List[str]
    category_context: str
    search_strategy: str
    confidence_score: float

@dataclass
class EnhancedSearchResult:
    """Enhanced search result with IDS context."""
    file_path: str
    match_type: str  # 'direct', 'related', 'semantic'
    relevance_score: float
    ids_tags: List[str]
    category: str
    description: str
    related_files: List[str]

class IDSWorkspaceEnhancer:
    """
    Enhances workspace searches using IDS intelligence.
    Acts as a smart layer over existing search capabilities.
    """
    
    def __init__(self, ids_interface: 'IDSToolInterface'):
        self.ids = ids_interface
        self.search_history = []
        self.context_cache = {}
    
    def enhance_search_query(self, query: str, search_context: str = "") -> WorkspaceSearchHint:
        """
        Enhance a search query using IDS knowledge.
        
        Args:
            query: Original search query
            search_context: Additional context about what user is looking for
            
        Returns:
            WorkspaceSearchHint with suggestions for better search
        """
        # Get IDS results for the query
        ids_response = self.ids.query(query, search_type="unified", limit=10)
        
        # Extract file suggestions
        suggested_files = []
        related_tags = set()
        categories = set()
        
        for result in ids_response.results:
            suggested_files.append(result.file_path)
            related_tags.update(result.tags)
            categories.add(result.category)
        
        # Generate additional related tags using semantic expansion
        expanded_tags = self._expand_search_terms(query, list(related_tags))
        related_tags.update(expanded_tags)
        
        # Determine primary category
        primary_category = max(categories, key=lambda c: sum(1 for r in ids_response.results if r.category == c)) if categories else "unknown"
        
        # Suggest search strategy
        strategy = self._suggest_search_strategy(query, len(suggested_files), primary_category)
        
        # Calculate confidence
        confidence = min(len(suggested_files) / 10.0, 1.0)
        
        return WorkspaceSearchHint(
            suggested_files=suggested_files[:10],
            related_tags=list(related_tags)[:15],
            category_context=primary_category,
            search_strategy=strategy,
            confidence_score=confidence
        )
    
    def suggest_file_patterns(self, query: str) -> List[str]:
        """
        Suggest file patterns for grep/file searches based on IDS knowledge.
        
        Args:
            query: Search query
            
        Returns:
            List of file patterns to search
        """
        patterns = []
        
        # Get relevant files from IDS
        ids_response = self.ids.query(query, search_type="unified", limit=20)
        
        # Extract file patterns
        file_extensions = set()
        directory_patterns = set()
        
        for result in ids_response.results:
            path_parts = result.file_path.split('/')
            
            # Extract extension
            if '.' in path_parts[-1]:
                ext = '.' + path_parts[-1].split('.')[-1]
                file_extensions.add(f"**/*{ext}")
            
            # Extract directory patterns
            if len(path_parts) > 1:
                # Get first two directory levels
                dir_pattern = '/'.join(path_parts[:2]) + "/**/*"
                directory_patterns.add(dir_pattern)
        
        # Combine patterns
        patterns.extend(list(file_extensions)[:5])
        patterns.extend(list(directory_patterns)[:5])
        
        return patterns
    
    def get_context_files(self, current_file: str, context_type: str = "related") -> List[str]:
        """
        Get contextually related files based on current file.
        
        Args:
            current_file: Current file being worked on
            context_type: Type of context ('related', 'dependencies', 'similar')
            
        Returns:
            List of related file paths
        """
        if current_file not in self.ids.unified_index:
            return []
        
        current_tags = self.ids.unified_index[current_file]
        current_metadata = self.ids.file_metadata.get(current_file, {})
        
        related_files = []
        
        for file_path, tags in self.ids.unified_index.items():
            if file_path == current_file:
                continue
                
            metadata = self.ids.file_metadata.get(file_path, {})
            
            # Calculate relationship score
            if context_type == "related":
                score = self._calculate_tag_similarity(current_tags, tags)
            elif context_type == "dependencies":
                score = self._calculate_dependency_score(current_file, file_path, metadata)
            elif context_type == "similar":
                score = self._calculate_file_similarity(current_metadata, metadata)
            else:
                score = 0
            
            if score > 0.2:  # Threshold for relevance
                related_files.append((file_path, score))
        
        # Sort by score and return top matches
        related_files.sort(key=lambda x: x[1], reverse=True)
        return [f[0] for f in related_files[:10]]
    
    def smart_search_suggestions(self, partial_query: str) -> List[str]:
        """
        Provide smart search suggestions based on partial input.
        
        Args:
            partial_query: Partial search term
            
        Returns:
            List of suggested complete search terms
        """
        suggestions = set()
        partial_lower = partial_query.lower()
        
        # Search through tags
        for file_path, tags in self.ids.unified_index.items():
            for tag in tags:
                if partial_lower in tag.lower():
                    suggestions.add(tag)
        
        # Search through metadata
        for file_path, metadata in self.ids.file_metadata.items():
            for key, value in metadata.items():
                if isinstance(value, str) and partial_lower in value.lower():
                    # Extract relevant words
                    words = value.split()
                    for word in words:
                        if partial_lower in word.lower():
                            suggestions.add(word)
        
        return sorted(list(suggestions))[:10]
    
    def _expand_search_terms(self, query: str, existing_tags: List[str]) -> List[str]:
        """Expand search terms using tag relationships."""
        expanded = set()
        query_words = query.lower().split()
        
        # Find tags that contain query words
        for tag in existing_tags:
            tag_words = tag.lower().split('_')
            if any(word in tag_words for word in query_words):
                # Add related words from this tag
                expanded.update(tag_words)
        
        return list(expanded)
    
    def _suggest_search_strategy(self, query: str, result_count: int, category: str) -> str:
        """Suggest optimal search strategy."""
        if result_count == 0:
            return "broaden_search"
        elif result_count > 20:
            return "narrow_search"
        elif category == "source_code":
            return "code_focused"
        elif category == "documentation":
            return "doc_focused"
        else:
            return "balanced"
    
    def _calculate_tag_similarity(self, tags1: List[str], tags2: List[str]) -> float:
        """Calculate similarity between two sets of tags."""
        if not tags1 or not tags2:
            return 0.0
        
        set1 = set(tags1)
        set2 = set(tags2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_dependency_score(self, file1: str, file2: str, metadata2: Dict) -> float:
        """Calculate dependency relationship score."""
        # Simple heuristic based on file paths and types
        path1_parts = file1.split('/')
        path2_parts = file2.split('/')
        
        # Same directory = higher score
        if len(path1_parts) > 1 and len(path2_parts) > 1:
            if path1_parts[:-1] == path2_parts[:-1]:
                return 0.8
            elif path1_parts[0] == path2_parts[0]:
                return 0.4
        
        return 0.1
    
    def _calculate_file_similarity(self, metadata1: Dict, metadata2: Dict) -> float:
        """Calculate file similarity based on metadata."""
        score = 0.0
        
        # Same type
        if metadata1.get('type') == metadata2.get('type'):
            score += 0.3
        
        # Same category
        if metadata1.get('category') == metadata2.get('category'):
            score += 0.4
        
        # Similar titles/descriptions
        title1 = metadata1.get('title', '').lower()
        title2 = metadata2.get('title', '').lower()
        if title1 and title2:
            common_words = set(title1.split()) & set(title2.split())
            if common_words:
                score += 0.3
        
        return score

class IDSToolInterface:
    """
    Tool-like interface for the ImpressionCore Documentation System.
    
    This class provides programmatic access to IDS functionality,
    allowing direct queries and searches through the documentation
    and codebase indices.
    """
    
    def __init__(self):
        """Initialize the IDS tool interface."""
        self.console = Console() if HAS_RICH else None
        self.unified_index = {}
        self.file_metadata = {}
        self.reverse_tag_index = {}
        # Add workspace enhancer
        self.workspace_enhancer = None
        self.load_indices()
        # Initialize enhancer after indices are loaded
        if self.unified_index:
            self.workspace_enhancer = IDSWorkspaceEnhancer(self)
    
    def _build_cross_references(self):
        """Build cross-reference mappings for related file discovery."""
        # Build category-based relationships
        self.category_files: Dict[str, List[str]] = {}
        self.tag_relationships: Dict[str, Set[str]] = {}
        
        for file_path, tags in self.unified_index.items():
            metadata = self.file_metadata.get(file_path, {})
            category = metadata.get('category', 'unknown')
            
            # Group by category
            if category not in self.category_files:
                self.category_files[category] = []
            self.category_files[category].append(file_path)
            
            # Build tag co-occurrence relationships
            for tag in tags:
                if tag not in self.tag_relationships:
                    self.tag_relationships[tag] = set()
                self.tag_relationships[tag].update(tags)
                self.tag_relationships[tag].discard(tag)  # Remove self-reference
    
    def load_indices(self) -> bool:
        """
        Load all IDS indices and metadata.
        
        Returns:
            bool: True if indices loaded successfully, False otherwise
        """
        try:
            # Load unified tags index
            unified_path = DOCS_ROOT / "unified_tags_index.yaml"
            if unified_path.exists():
                with open(unified_path, 'r', encoding='utf-8') as f:
                    self.unified_index = yaml.safe_load(f) or {}
            
            # Load file metadata
            metadata_path = DOCS_ROOT / "file_metadata.yaml"
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.file_metadata = yaml.safe_load(f) or {}
            
            # Load reverse tag index
            reverse_path = DOCS_ROOT / "reverse_tag_index.yaml"
            if reverse_path.exists():
                with open(reverse_path, 'r', encoding='utf-8') as f:
                    self.reverse_tag_index = yaml.safe_load(f) or {}
            
            return True
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error loading indices: {e}[/red]")
            return False
    
    def query(self, 
              search_term: str, 
              search_type: str = "unified",
              file_type: str = "all",
              category: str = "all",
              exact_match: bool = False,
              limit: int = 50) -> IDSSearchResponse:
        """
        Main query interface for IDS searches.
        
        Args:
            search_term: The term to search for
            search_type: Type of search ('unified', 'tag', 'keyword', 'file')
            file_type: Filter by file type ('documentation', 'source_code', 'all')
            category: Filter by category
            exact_match: Whether to use exact matching
            limit: Maximum number of results to return
            
        Returns:
            IDSSearchResponse: Structured response with results
        """
        start_time = datetime.now()
        
        results = []
        
        if search_type == "unified":
            results = self._unified_search(search_term, file_type, category, exact_match)
        elif search_type == "tag":
            results = self._tag_search(search_term, exact_match)
        elif search_type == "keyword":
            results = self._keyword_search(search_term, file_type, category)
        elif search_type == "file":
            results = self._file_search(search_term)
        
        # Apply limit
        if limit > 0:
            results = results[:limit]
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return IDSSearchResponse(
            query=search_term,
            results=results,
            total_results=len(results),
            search_type=search_type,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time
        )
    
    def _unified_search(self, 
                       search_term: str, 
                       file_type: str = "all",
                       category: str = "all",
                       exact_match: bool = False) -> List[IDSQueryResult]:
        """Perform unified search across tags and metadata."""
        results = []
        search_lower = search_term.lower()
        
        for file_path, tags in self.unified_index.items():
            # Get file metadata
            metadata = self.file_metadata.get(file_path, {})
            
            # Apply filters
            if file_type != "all" and metadata.get('type') != file_type:
                continue
            if category != "all" and metadata.get('category') != category:
                continue
            
            # Find matching tags
            matching_tags = []
            if exact_match:
                matching_tags = [tag for tag in tags if tag == search_term]
            else:
                matching_tags = [tag for tag in tags if search_lower in tag.lower()]
            
            # Check metadata for matches
            if not matching_tags:
                # Check title, description, etc.
                searchable_fields = ['title', 'description', 'summary']
                for field in searchable_fields:
                    if field in metadata:
                        field_value = str(metadata[field]).lower()
                        if (exact_match and search_term in field_value) or \
                           (not exact_match and search_lower in field_value):
                            matching_tags.append(f"metadata:{field}")
                            break
            
            if matching_tags:
                # Calculate relevance score
                relevance = self._calculate_relevance(search_term, matching_tags, metadata)
                
                result = IDSQueryResult(
                    file_path=file_path,
                    file_type=metadata.get('type', 'unknown'),
                    category=metadata.get('category', 'unknown'),
                    tags=tags,
                    matching_tags=matching_tags,
                    metadata=metadata,
                    relevance_score=relevance
                )
                results.append(result)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results
    
    def _tag_search(self, tag: str, exact_match: bool = False) -> List[IDSQueryResult]:
        """Search for files by specific tag."""
        results = []
        
        if exact_match and tag in self.reverse_tag_index:
            # Use reverse index for exact matches
            file_paths = self.reverse_tag_index[tag]
            for file_path in file_paths:
                if file_path in self.unified_index:
                    metadata = self.file_metadata.get(file_path, {})
                    result = IDSQueryResult(
                        file_path=file_path,
                        file_type=metadata.get('type', 'unknown'),
                        category=metadata.get('category', 'unknown'),
                        tags=self.unified_index[file_path],
                        matching_tags=[tag],
                        metadata=metadata,
                        relevance_score=1.0
                    )
                    results.append(result)
        else:
            # Fuzzy search through all files
            tag_lower = tag.lower()
            for file_path, tags in self.unified_index.items():
                matching_tags = [t for t in tags if tag_lower in t.lower()]
                if matching_tags:
                    metadata = self.file_metadata.get(file_path, {})
                    relevance = len(matching_tags) / len(tags) if tags else 0
                    
                    result = IDSQueryResult(
                        file_path=file_path,
                        file_type=metadata.get('type', 'unknown'),
                        category=metadata.get('category', 'unknown'),
                        tags=tags,
                        matching_tags=matching_tags,
                        metadata=metadata,
                        relevance_score=relevance
                    )
                    results.append(result)
        
        return results
    
    def _keyword_search(self, keyword: str, file_type: str = "all", category: str = "all") -> List[IDSQueryResult]:
        """Search for keyword in file content and metadata."""
        results = []
        keyword_lower = keyword.lower()
        
        for file_path, tags in self.unified_index.items():
            metadata = self.file_metadata.get(file_path, {})
            
            # Apply filters
            if file_type != "all" and metadata.get('type') != file_type:
                continue
            if category != "all" and metadata.get('category') != category:
                continue
            
            # Search in tags
            matching_tags = [tag for tag in tags if keyword_lower in tag.lower()]
            
            # Search in metadata
            metadata_matches = []
            for key, value in metadata.items():
                if isinstance(value, str) and keyword_lower in value.lower():
                    metadata_matches.append(f"metadata:{key}")
            
            if matching_tags or metadata_matches:
                all_matches = matching_tags + metadata_matches
                relevance = self._calculate_relevance(keyword, all_matches, metadata)
                
                result = IDSQueryResult(
                    file_path=file_path,
                    file_type=metadata.get('type', 'unknown'),
                    category=metadata.get('category', 'unknown'),
                    tags=tags,
                    matching_tags=all_matches,
                    metadata=metadata,
                    relevance_score=relevance
                )
                results.append(result)
        
        return results
    
    def _file_search(self, filename: str) -> List[IDSQueryResult]:
        """Search for files by filename or path."""
        results = []
        filename_lower = filename.lower()
        
        for file_path in self.unified_index:
            if filename_lower in file_path.lower():
                metadata = self.file_metadata.get(file_path, {})
                tags = self.unified_index[file_path]
                
                # Higher relevance for exact filename matches
                path_parts = file_path.lower().split('/')
                relevance = 1.0 if any(filename_lower == part for part in path_parts) else 0.5
                
                result = IDSQueryResult(
                    file_path=file_path,
                    file_type=metadata.get('type', 'unknown'),
                    category=metadata.get('category', 'unknown'),
                    tags=tags,
                    matching_tags=[f"filename:{filename}"],
                    metadata=metadata,
                    relevance_score=relevance
                )
                results.append(result)
        
        return results
    
    def _calculate_relevance(self, search_term: str, matching_tags: List[str], metadata: Dict) -> float:
        """Calculate relevance score for search results."""
        score = 0.0
        
        # Base score for having matches
        score += 0.3
        
        # Score based on number of matching tags
        score += min(len(matching_tags) * 0.1, 0.4)
        
        # Boost for exact matches
        search_lower = search_term.lower()
        for tag in matching_tags:
            if search_lower == tag.lower():
                score += 0.3
                break
        
        # Boost for title matches
        if 'title' in metadata:
            title = metadata['title'].lower()
            if search_lower in title:
                score += 0.2
        
        # Boost for recent files
        if 'last_modified' in metadata:
            # This would need proper date parsing
            score += 0.1
        
        return min(score, 1.0)
    
    def get_file_details(self, file_path: str) -> Optional[IDSQueryResult]:
        """
        Get detailed information about a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            IDSQueryResult or None if file not found
        """
        if file_path not in self.unified_index:
            return None
        
        metadata = self.file_metadata.get(file_path, {})
        tags = self.unified_index[file_path]
        
        return IDSQueryResult(
            file_path=file_path,
            file_type=metadata.get('type', 'unknown'),
            category=metadata.get('category', 'unknown'),
            tags=tags,
            matching_tags=tags,  # All tags are "matching" for file details
            metadata=metadata,
            relevance_score=1.0
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the IDS.
        
        Returns:
            Dict containing various statistics
        """
        from collections import Counter
        
        total_files = len(self.unified_index)
        all_tags = []
        file_types = Counter()
        categories = Counter()
        
        for file_path, tags in self.unified_index.items():
            all_tags.extend(tags)
            metadata = self.file_metadata.get(file_path, {})
            file_types[metadata.get('type', 'unknown')] += 1
            categories[metadata.get('category', 'unknown')] += 1
        
        return {
            'total_files': total_files,
            'total_unique_tags': len(set(all_tags)),
            'file_types': dict(file_types),
            'categories': dict(categories),
            'most_common_tags': dict(Counter(all_tags).most_common(10)),
            'index_status': 'loaded' if self.unified_index else 'empty'
        }
    
    def format_results_json(self, response: IDSSearchResponse) -> str:
        """Format search results as JSON string."""
        # Convert dataclasses to dict for JSON serialization
        results_dict = []
        for result in response.results:
            results_dict.append({
                'file_path': result.file_path,
                'file_type': result.file_type,
                'category': result.category,
                'tags': result.tags,
                'matching_tags': result.matching_tags,
                'metadata': result.metadata,
                'relevance_score': result.relevance_score
            })
        
        response_dict = {
            'query': response.query,
            'results': results_dict,
            'total_results': response.total_results,
            'search_type': response.search_type,
            'timestamp': response.timestamp,
            'execution_time_ms': response.execution_time_ms
        }
        
        return json.dumps(response_dict, indent=2, ensure_ascii=False)
    
    def format_results_table(self, response: IDSSearchResponse) -> str:
        """Format search results as a formatted table string."""
        if not response.results:
            return "No results found."
        
        if HAS_RICH and self.console:
            # Use Rich table formatting
            table = Table(title=f"Search Results for '{response.query}'")
            table.add_column("File", style="cyan", width=40)
            table.add_column("Type", style="yellow", width=10)
            table.add_column("Category", style="green", width=12)
            table.add_column("Matching Tags", style="white", width=30)
            table.add_column("Score", style="magenta", width=8)
            
            for result in response.results[:20]:  # Limit display
                tags_str = ", ".join(result.matching_tags[:3])
                if len(result.matching_tags) > 3:
                    tags_str += f" (+{len(result.matching_tags) - 3})"
                
                table.add_row(
                    result.file_path,
                    result.file_type,
                    result.category,
                    tags_str,
                    f"{result.relevance_score:.2f}"
                )
            
            # Capture table output
            from io import StringIO
            console = Console(file=StringIO(), width=120)
            console.print(table)
            return console.file.getvalue()
        else:
            # Simple text formatting
            output = f"Search Results for '{response.query}'\n"
            output += "=" * 60 + "\n"
            
            for i, result in enumerate(response.results[:20], 1):
                output += f"{i}. {result.file_path}\n"
                output += f"   Type: {result.file_type} | Category: {result.category}\n"
                output += f"   Tags: {', '.join(result.matching_tags[:3])}\n"
                output += f"   Score: {result.relevance_score:.2f}\n\n"
            
            return output

    def enhance_workspace_search(self, query: str, search_context: str = "") -> WorkspaceSearchHint:
        """
        Enhance workspace search capabilities using IDS intelligence.
        
        Args:
            query: Search query
            search_context: Additional context
            
        Returns:
            WorkspaceSearchHint with enhanced search suggestions
        """
        if not self.workspace_enhancer:
            # Fallback if enhancer not available
            return WorkspaceSearchHint(
                suggested_files=[],
                related_tags=[],
                category_context="unknown",
                search_strategy="basic",
                confidence_score=0.0
            )
        
        return self.workspace_enhancer.enhance_search_query(query, search_context)
    
    def get_file_patterns_for_search(self, query: str) -> List[str]:
        """Get file patterns optimized for the search query."""
        if not self.workspace_enhancer:
            return ["**/*"]
        
        return self.workspace_enhancer.suggest_file_patterns(query)
    
    def get_contextual_files(self, current_file: str, context_type: str = "related") -> List[str]:
        """Get files related to the current context."""
        if not self.workspace_enhancer:
            return []
        
        return self.workspace_enhancer.get_context_files(current_file, context_type)
    
    def suggest_search_completions(self, partial_query: str) -> List[str]:
        """Get intelligent search suggestions for partial queries."""
        if not self.workspace_enhancer:
            return []
        
        return self.workspace_enhancer.smart_search_suggestions(partial_query)
    
    def get_search_optimization_advice(self, query: str, result_count: int = 0) -> Dict[str, str]:
        """
        Get advice on how to optimize search queries.
        
        Args:
            query: Current search query
            result_count: Number of results from current search
            
        Returns:
            Dictionary with optimization advice
        """
        advice = {}
        
        # Basic query analysis
        if len(query.split()) == 1:
            advice["suggestion"] = "Try adding more specific terms or context"
            advice["example"] = f"{query} implementation" if query else "specific_term"
        
        # Result count analysis
        if result_count == 0:
            ids_results = self.query(query, limit=5)
            if ids_results.total_results > 0:
                advice["ids_hint"] = f"IDS found {ids_results.total_results} related files"
                advice["suggested_files"] = [r.file_path for r in ids_results.results[:3]]
            else:
                advice["suggestion"] = "Try broader terms or check spelling"
        elif result_count > 50:
            advice["suggestion"] = "Results too broad, try adding specific terms"
            # Get category context from IDS
            hint = self.enhance_workspace_search(query)
            if hint.category_context != "unknown":
                advice["category_filter"] = f"Consider focusing on {hint.category_context} files"
        
        return advice

# Enhanced convenience functions for workspace integration
def ids_enhance_search(query: str, search_context: str = "") -> Dict[str, Any]:
    """
    Enhance a workspace search query using IDS intelligence.
    
    Args:
        query: Search query
        search_context: Additional context
        
    Returns:
        Dictionary with enhanced search information
    """
    ids = IDSToolInterface()
    hint = ids.enhance_workspace_search(query, search_context)
    
    return {
        'suggested_files': hint.suggested_files,
        'related_tags': hint.related_tags,
        'category_context': hint.category_context,
        'search_strategy': hint.search_strategy,
        'confidence_score': hint.confidence_score,
        'file_patterns': ids.get_file_patterns_for_search(query)
    }

def ids_get_related_files(current_file: str, context_type: str = "related") -> List[str]:
    """Get files related to the current file using IDS intelligence."""
    ids = IDSToolInterface()
    return ids.get_contextual_files(current_file, context_type)

def ids_suggest_search_terms(partial_query: str) -> List[str]:
    """Get intelligent search term suggestions."""
    ids = IDSToolInterface()
    return ids.suggest_search_completions(partial_query)

def ids_optimize_search(query: str, result_count: int = 0) -> Dict[str, str]:
    """Get search optimization advice."""
    ids = IDSToolInterface()
    return ids.get_search_optimization_advice(query, result_count)

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="IDS Tool Interface")
    parser.add_argument("search_term", help="Term to search for")
    parser.add_argument("--type", default="unified", choices=["unified", "tag", "keyword", "file"],
                       help="Search type")
    parser.add_argument("--file-type", default="all", choices=["all", "documentation", "source_code"],
                       help="File type filter")
    parser.add_argument("--format", default="table", choices=["json", "table"],
                       help="Output format")
    
    args = parser.parse_args()
    
    # Create IDS interface instance
    ids = IDSToolInterface()
      # Perform search using the query method
    search_results = ids.query(
        search_term=args.search_term,
        search_type=args.type,
        file_type=args.file_type,
        limit=20
    )
      # Format and display results
    if args.format == "json":
        # Convert results to JSON format
        json_results = {
            "query": args.search_term,
            "type": args.type,
            "file_type": args.file_type,
            "total_results": search_results.total_results,
            "results": [
                {
                    "file_path": result.file_path,
                    "category": result.category,
                    "file_type": result.file_type,
                    "tags": result.tags,
                    "relevance_score": result.relevance_score,
                    "matching_tags": result.matching_tags
                }
                for result in search_results.results
            ]
        }
        print(json.dumps(json_results, indent=2))
    else:
        # Table format
        print(f"\n🔍 IDS Search Results for '{args.search_term}'")
        print("=" * 80)
        print(f"Search type: {args.type} | File type: {args.file_type}")
        print(f"Total results: {search_results.total_results}")
        print("\nResults:")
        print("-" * 80)
        
        for i, result in enumerate(search_results.results, 1):
            print(f"{i:2d}. {result.file_path}")
            print(f"    Category: {result.category} | Type: {result.file_type}")
            print(f"    Tags: {', '.join(result.tags[:5])}")
            if hasattr(result, 'relevance_score') and result.relevance_score is not None:
                print(f"    Score: {result.relevance_score:.3f}")
            print()

# Practical Use Case Examples and Integration Patterns
class IDSPracticalUsage:
    """
    Demonstrates practical use cases for IDS-enhanced workspace searches.
    This shows how the IDS tool interface integrates with common search scenarios.
    """
    
    def __init__(self):
        self.ids = IDSToolInterface()
    
    def demonstrate_enhanced_semantic_search(self, query: str):
        """
        Example: How IDS enhances semantic search operations.
        
        Before: semantic_search("memory management")
        After: IDS-enhanced semantic search with targeted files
        """
        print(f"🔍 Enhanced Semantic Search for: '{query}'")
        print("=" * 60)
        
        # Step 1: Get IDS enhancement hints
        enhancement = self.ids.enhance_workspace_search(query, "looking for implementation details")
        
        print("📋 IDS Enhancement Analysis:")
        print(f"   Strategy: {enhancement.search_strategy}")
        print(f"   Category: {enhancement.category_context}")
        print(f"   Confidence: {enhancement.confidence_score:.2f}")
        print(f"   Suggested files ({len(enhancement.suggested_files)}):")
        for i, file_path in enumerate(enhancement.suggested_files[:5], 1):
            print(f"      {i}. {file_path}")
        
        print(f"\n🏷️ Related Tags ({len(enhancement.related_tags)}):")
        print(f"   {', '.join(enhancement.related_tags[:10])}")
        
        # Step 2: Get optimized file patterns
        patterns = self.ids.get_file_patterns_for_search(query)
        print(f"\n📁 Optimized File Patterns:")
        for pattern in patterns:
            print(f"   {pattern}")
        
        return enhancement
    
    def demonstrate_contextual_file_discovery(self, current_file: str):
        """
        Example: How IDS finds related files when working on a specific file.
        
        Use case: User is editing memory/uks.py and wants to find related files
        """
        print(f"📂 Contextual File Discovery for: {current_file}")
        print("=" * 60)
        
        # Get different types of related files
        contexts = ["related", "dependencies", "similar"]
        
        for context_type in contexts:
            related_files = self.ids.get_contextual_files(current_file, context_type)
            print(f"\n🔗 {context_type.title()} Files:")
            for i, file_path in enumerate(related_files[:5], 1):
                # Get file metadata for context
                file_info = self.ids.get_file_details(file_path)
                if file_info:
                    print(f"   {i}. {file_path}")
                    print(f"      Type: {file_info.file_type} | Category: {file_info.category}")
                    print(f"      Tags: {', '.join(file_info.tags[:3])}")
        
        return related_files
    
    def demonstrate_intelligent_grep_search(self, search_term: str):
        """
        Example: How IDS optimizes grep searches by suggesting where to look.
        
        Before: grep_search("class Definition", isRegexp=False)
        After: IDS-guided grep with targeted patterns and files
        """
        print(f"🔍 Intelligent Grep Search for: '{search_term}'")
        print("=" * 60)
        
        # Get IDS guidance
        enhancement = self.ids.enhance_workspace_search(search_term, "looking for class definitions")
        
        print("🎯 IDS Recommendations:")
        print(f"   Primary files to search ({len(enhancement.suggested_files[:10])}):")
        for file_path in enhancement.suggested_files[:10]:
            print(f"      {file_path}")
        
        # Get file patterns for grep
        patterns = self.ids.get_file_patterns_for_search(search_term)
        print(f"\n📋 Suggested includePattern for grep_search:")
        for pattern in patterns[:3]:
            print(f"      includePattern: {pattern}")
        
        # Search optimization advice
        advice = self.ids.get_search_optimization_advice(search_term)
        if advice:
            print(f"\n💡 Search Optimization Tips:")
            for key, value in advice.items():
                print(f"   {key}: {value}")
        
        return enhancement, patterns
    
    def demonstrate_file_search_enhancement(self, filename_pattern: str):
        """
        Example: How IDS enhances file_search operations.
        
        Before: file_search("**/*memory*.py")
        After: IDS suggests better patterns and related files
        """
        print(f"📁 Enhanced File Search for: '{filename_pattern}'")
        print("=" * 60)
        
        # Use IDS to find files matching the pattern concept
        ids_results = self.ids.query(filename_pattern, search_type="file", limit=20)
        
        print(f"🎯 IDS Found {ids_results.total_results} matching files:")
        for i, result in enumerate(ids_results.results[:10], 1):
            print(f"   {i}. {result.file_path}")
            print(f"      Category: {result.category} | Type: {result.file_type}")
        
        # Suggest improved patterns
        patterns = self.ids.get_file_patterns_for_search(filename_pattern)
        print(f"\n📋 Improved Search Patterns:")
        for pattern in patterns:
            print(f"      {pattern}")
        
        return ids_results
    
    def demonstrate_auto_completion(self, partial_query: str):
        """
        Example: How IDS provides intelligent auto-completion.
        
        Use case: User types "mem" and wants suggestions
        """
        print(f"✨ Auto-completion for: '{partial_query}'")
        print("=" * 60)
        
        suggestions = self.ids.suggest_search_completions(partial_query)
        
        print(f"💭 Smart Suggestions ({len(suggestions)}):")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        # For each suggestion, show what files it would find
        print(f"\n📊 Preview of results for top suggestions:")
        for suggestion in suggestions[:3]:
            preview = self.ids.query(suggestion, limit=3)
            print(f"   '{suggestion}' → {preview.total_results} files")
            for result in preview.results:
                print(f"      - {result.file_path}")
        
        return suggestions

def demonstrate_workflow_integration():
    """
    Show how IDS integrates into a typical development workflow.
    """
    print("🚀 IDS Integration Workflow Example")
    print("=" * 80)
    
    usage = IDSPracticalUsage()
    
    # Scenario 1: Developer wants to understand memory management
    print("\n📋 Scenario 1: Understanding Memory Management")
    print("-" * 50)
    enhancement = usage.demonstrate_enhanced_semantic_search("memory management")
    
    # Scenario 2: Working on UKS implementation, need related files
    print("\n📋 Scenario 2: Working on UKS, Finding Related Files")
    print("-" * 50)
    related = usage.demonstrate_contextual_file_discovery("src/core/brainsim/memory/uks.py")
    
    # Scenario 3: Looking for specific class implementations
    print("\n📋 Scenario 3: Finding Class Implementations")
    print("-" * 50)
    grep_info = usage.demonstrate_intelligent_grep_search("class MemoryManager")
    
    # Scenario 4: Auto-completion while typing
    print("\n📋 Scenario 4: Smart Auto-completion")
    print("-" * 50)
    suggestions = usage.demonstrate_auto_completion("neural")
    
    return {
        'enhancement': enhancement,
        'related_files': related,
        'grep_guidance': grep_info,
        'suggestions': suggestions
    }

def show_before_after_comparison():
    """
    Direct comparison of searches before and after IDS enhancement.
    """
    print("🔄 Before vs After: IDS Enhancement Impact")
    print("=" * 80)
    
    scenarios = [
        {
            'query': 'brain simulation',
            'before': 'semantic_search("brain simulation") → searches entire workspace',
            'after': 'IDS suggests 15 specific files in brainsim/ and related docs'
        },
        {
            'query': 'memory optimization',
            'before': 'grep_search("memory optimization", isRegexp=False) → 500+ files',
            'after': 'IDS suggests src/memory_manager/** and core/utils/** patterns'
        },
        {
            'query': 'API endpoints',
            'before': 'file_search("**/*api*.py") → finds all API-related files',
            'after': 'IDS distinguishes between API definitions, implementations, and docs'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['query']}")
        print(f"   Before: {scenario['before']}")
        print(f"   After:  {scenario['after']}")
    
    # Show actual IDS enhancement for one example
    ids = IDSToolInterface()
    print(f"\n🎯 Live Example: 'brain simulation'")
    enhancement = ids.enhance_workspace_search("brain simulation")
    print(f"   IDS found {len(enhancement.suggested_files)} relevant files")
    print(f"   Strategy: {enhancement.search_strategy}")
    print(f"   Category focus: {enhancement.category_context}")
    print(f"   Confidence: {enhancement.confidence_score:.2f}")

# Integration helper functions that I would use in practice
def enhanced_semantic_search(query: str, context: str = ""):
    """
    My enhanced semantic_search that uses IDS intelligence.
    
    This is how I would modify my search approach to leverage IDS.
    """
    ids = IDSToolInterface()
    
    # Get IDS enhancement first
    enhancement = ids.enhance_workspace_search(query, context)
    
    # If IDS has high confidence, search suggested files first
    if enhancement.confidence_score > 0.7:
        print(f"🎯 IDS High Confidence: Searching {len(enhancement.suggested_files)} targeted files")
        # In practice, I would use semantic_search with includePattern for these files
        for file_path in enhancement.suggested_files[:5]:
            print(f"   Priority: {file_path}")
    
    # Use enhanced query with related tags
    enhanced_query = f"{query} {' '.join(enhancement.related_tags[:3])}"
    print(f"🔍 Enhanced query: {enhanced_query}")
    
    return enhancement

def enhanced_grep_search(query: str, context: str = ""):
    """
    My enhanced grep_search that uses IDS patterns.
    """
    ids = IDSToolInterface()
    
    # Get optimized patterns
    patterns = ids.get_file_patterns_for_search(query)
    enhancement = ids.enhance_workspace_search(query, context)
    
    print(f"📋 IDS Optimization for grep_search:")
    print(f"   Recommended includePattern: {patterns[0] if patterns else '**/*'}")
    print(f"   Strategy: {enhancement.search_strategy}")
    
    # Get search advice
    advice = ids.get_search_optimization_advice(query)
    if advice:
        print(f"   Advice: {advice.get('suggestion', 'None')}")
    
    return patterns[0] if patterns else "**/*"

def enhanced_file_search(filename_hint: str):
    """
    My enhanced file_search using IDS knowledge.
    """
    ids = IDSToolInterface()
    
    # First check if IDS knows about files matching this hint
    ids_results = ids.query(filename_hint, search_type="file")
    
    if ids_results.total_results > 0:
        print(f"🎯 IDS found {ids_results.total_results} files matching '{filename_hint}':")
        for result in ids_results.results[:5]:
            print(f"   {result.file_path}")
        
        # Get the most relevant pattern
        patterns = ids.get_file_patterns_for_search(filename_hint)
        return patterns[0] if patterns else f"**/*{filename_hint}*"
    else:
        print(f"🔍 IDS has no matches, using standard pattern")
        return f"**/*{filename_hint}*"
