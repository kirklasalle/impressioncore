# MCP Server Search Function Fix Analysis and Solution
## Date: 2025-06-10
## Issue: Search function works once after restart, then fails

### Root Cause Analysis

Based on web search and code review, the issue appears to be:

1. **State Management Problem**: The `EnhancedIDS` instance in the MCP server doesn't refresh its indices between calls
2. **File Handle/Lock Issues**: Potential file locking on Windows when accessing YAML indices
3. **Memory State Corruption**: The unified_index and file_metadata may become corrupted after first use

### Evidence Found

1. **MCP Debugging Best Practices** (from web search):
   - "MCP servers inherit only a subset of environment variables"
   - "Server-side logging should go to stderr, not stdout"
   - "Check for JSON-RPC protocol compliance"

2. **Code Analysis**:
   - `load_indices()` is only called in `__init__`, never refreshed
   - No error handling for corrupted state between calls
   - Windows file locking issues with YAML files

### Solution Implementation

#### 1. Add State Refresh Mechanism
```python
def refresh_indices(self):
    """Force reload of all indices - fixes state corruption."""
    try:
        self.unified_index.clear()
        self.file_metadata.clear()
        self.load_indices()
        return True
    except Exception as e:
        print(f"Error refreshing indices: {e}", file=sys.stderr)
        return False
```

#### 2. Add Search Function Wrapper with Auto-Refresh
```python
def handle_search(self, query: str, max_results: int = 10, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Handle search requests with auto-refresh on failure."""
    try:
        # Try search with current state
        if self.enhanced_ids:
            result = self.enhanced_ids.search(query, max_results=max_results, tags=tags or [])
            
            # Check if results are valid
            if isinstance(result, dict) and 'results' in result:
                return result
            else:
                # Invalid result, try refresh
                print(f"Invalid search result, refreshing indices...", file=sys.stderr)
                self.enhanced_ids.refresh_indices()
                return self.enhanced_ids.search(query, max_results=max_results, tags=tags or [])
        else:
            return self._fallback_search(query, max_results)
            
    except Exception as e:
        print(f"Search error: {e}, attempting recovery...", file=sys.stderr)
        
        # Try to recover by refreshing
        if self.enhanced_ids:
            try:
                self.enhanced_ids.refresh_indices()
                return self.enhanced_ids.search(query, max_results=max_results, tags=tags or [])
            except Exception as e2:
                print(f"Recovery failed: {e2}", file=sys.stderr)
        
        # Final fallback
        return self._fallback_search(query, max_results)
```

#### 3. Enhanced Error Logging
```python
def _log_error(self, operation: str, error: Exception):
    """Enhanced error logging for debugging."""
    import traceback
    error_msg = f"[{datetime.now().isoformat()}] {operation} failed: {error}\\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr)
```

### Implementation Steps

1. **Backup Current Server**: Create backup of working server
2. **Implement Fixes**: Add refresh mechanism and error handling
3. **Test Recovery**: Verify search works after multiple calls
4. **Monitor Performance**: Ensure refresh doesn't impact performance significantly

### Testing Protocol

1. **Initial Test**: Verify search works on first call
2. **Repeated Calls**: Make 5+ sequential search calls
3. **Recovery Test**: Force error condition and verify recovery
4. **Performance Test**: Measure refresh overhead

### Expected Outcome

- ✅ Search function works reliably after multiple calls
- ✅ Auto-recovery from state corruption
- ✅ Enhanced debugging and error reporting
- ✅ Maintained compatibility with existing tools

### Monitoring

- Add performance metrics for search calls
- Log refresh operations for debugging
- Track success/failure rates over time
