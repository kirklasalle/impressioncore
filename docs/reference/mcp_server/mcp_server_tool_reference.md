# Enhanced IDS MCP Server - Tool Reference

**Created:** June 07, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\mcp_server\mcp_server_tool_reference.md #api #documentation #memory_management #security #testing  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Available Tools

### Basic Search & Discovery (5 tools)

#### 1. search_documents

- **Purpose**: Primary document search with query and tag filtering
- **Parameters**: query, tags (optional), max_results (optional)
- **Returns**: List of matching documents with relevance scores

#### 2. find_by_tag  

- **Purpose**: Find documents by specific tag combinations
- **Parameters**: tags (array), match_all (boolean)
- **Returns**: Files matching tag criteria

#### 3. get_file_info

- **Purpose**: Retrieve detailed metadata for specific files
- **Parameters**: file_path (string)
- **Returns**: File metadata including tags, size, modification date

#### 4. list_tags

- **Purpose**: Browse available tags with optional filtering
- **Parameters**: category (optional), pattern (optional)
- **Returns**: Available tags organized by category

#### 5. get_system_status

- **Purpose**: System health and statistics overview
- **Parameters**: None
- **Returns**: Index status, file counts, tag statistics

### Advanced Search & Analytics (3 tools)

#### 6. semantic_search

- **Purpose**: AI-powered semantic document search
- **Parameters**: query, max_results (optional)
- **Returns**: Semantically relevant documents with context

#### 7. search_with_context

- **Purpose**: Search with enhanced contextual information
- **Parameters**: query, context_files (optional), max_results (optional)
- **Returns**: Search results with additional context metadata

#### 8. get_search_analytics

- **Purpose**: Search performance and usage analytics
- **Parameters**: time_period (optional)
- **Returns**: Search statistics and performance metrics

### Index Management (3 tools)

#### 9. rebuild_index

- **Purpose**: Complete index rebuild from source files
- **Parameters**: force (optional boolean)
- **Returns**: Rebuild status and statistics

#### 10. incremental_update

- **Purpose**: Update index with recent file changes
- **Parameters**: file_paths (optional array)
- **Returns**: Update status and processed file count

#### 11. check_index_freshness

- **Purpose**: Verify index currency and identify stale entries
- **Parameters**: None
- **Returns**: Freshness report with recommendations

### Documentation Management (3 tools)

#### 12. validate_documentation

- **Purpose**: Check documentation integrity and completeness
- **Parameters**: strict_mode (optional boolean)
- **Returns**: Validation report with issues and recommendations

#### 13. generate_documentation_report

- **Purpose**: Create comprehensive documentation overview
- **Parameters**: include_analytics (optional boolean)
- **Returns**: Detailed documentation report

#### 14. export_index_data

- **Purpose**: Export index data in various formats
- **Parameters**: format (json/yaml/csv), include_content (optional)
- **Returns**: Exported data in requested format

### Bookmark Management (3 tools)

#### 15. create_bookmark

- **Purpose**: Create bookmarks for frequently accessed documents
- **Parameters**: file_path, title, description (optional), tags (optional)
- **Returns**: Created bookmark details

#### 16. manage_bookmarks_list

- **Purpose**: List, update, or delete existing bookmarks
- **Parameters**: action (list/update/delete), bookmark_id (optional), updates (optional)
- **Returns**: Bookmark list or operation result

#### 17. get_bookmark_analytics

- **Purpose**: Bookmark usage statistics and insights
- **Parameters**: time_period (optional)
- **Returns**: Usage analytics and popular bookmarks

## Tool Categories Summary

| Category | Count | Primary Use Cases |
|----------|-------|-------------------|
| Basic Search | 5 | Document discovery, file info, tag browsing |
| Advanced Search | 3 | Semantic search, contextual results, analytics |
| Index Management | 3 | Maintenance, updates, freshness checks |
| Documentation Management | 3 | Validation, reporting, data export |
| Bookmark Management | 3 | Quick access, organization, usage tracking |

## Usage Examples

### Basic Document Search

```json
{
  "method": "search_documents",
  "params": {
    "query": "authentication security",
    "tags": ["security", "api"],
    "max_results": 10
  }
}
```

### Semantic Search

```json
{
  "method": "semantic_search", 
  "params": {
    "query": "How to implement user authentication",
    "max_results": 5
  }
}
```

### Create Bookmark

```json
{
  "method": "create_bookmark",
  "params": {
    "file_path": "docs/api/authentication.md",
    "title": "Authentication Guide",
    "description": "Primary authentication implementation guide",
    "tags": ["auth", "security", "api"]
  }
}
```

### Rebuild Index

```json
{
  "method": "rebuild_index",
  "params": {
    "force": false
  }
}
```

## Integration Notes

- All tools return standardized JSON responses
- Error handling included for all operations
- Logging provided for debugging and monitoring
- Performance optimized for large documentation sets
- Compatible with MCP (Model Context Protocol) standard

## Performance Characteristics

- **Search Operations**: Near-instantaneous for most queries
- **Index Operations**: 10-30 seconds for full rebuild
- **Memory Usage**: Optimized for large document collections
- **Concurrency**: Thread-safe for multiple simultaneous requests

---

**Server File**: `server_enhanced.py`  
**Test Suite**: `test_enhanced_ids.py`  
**Reference Implementation**: `server_enhanced_clean.py`
