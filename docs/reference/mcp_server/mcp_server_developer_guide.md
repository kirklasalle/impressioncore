# ImpressionCore IDS MCP Server - Developer Guide

**Created:** June 05, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\mcp_server\mcp_server_developer_guide.md #api #command_line #documentation #memory_management #performance #security #testing #web_interface  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

> **Comprehensive Development, Testing, and Integration Reference**  
> Generated: 2025-06-05  
> Version: 1.0.0  

## Table of Contents

1. [Development Overview](#development-overview)
2. [Architecture & Design](#architecture--design)
3. [Testing Framework](#testing-framework)
4. [Detailed Usage Examples](#detailed-usage-examples)
5. [Protocol Implementation](#protocol-implementation)
6. [VS Code Integration](#vs-code-integration)
7. [Debugging & Troubleshooting](#debugging--troubleshooting)
8. [Performance Optimization](#performance-optimization)
9. [Extension Development](#extension-development)
10. [Best Practices](#best-practices)

---

## Development Overview

### Project Structure

``` text
.mcp/ids-mcp/
├── server.py                     # Main MCP server implementation
├── config.json                   # Server configuration
├── requirements.txt              # Python dependencies
├── mcp_config.json              # MCP-specific configuration
├── README.md                    # User documentation
├── DEVELOPER_GUIDE.md           # This file
├── vscode_integration_guide.md  # VS Code setup guide
├── vscode_troubleshooting.md    # VS Code troubleshooting
├── ids_mcp.log                  # Server logs
├── start_server.sh              # Unix startup script
├── start_server.bat             # Windows startup script
├── start_for_vscode.bat         # VS Code specific startup
├── check_system.py              # System verification
├── examples/                    # Basic usage examples
│   ├── basic_search.py
│   ├── tag_discovery.py
│   └── integration_test.py
├── test_vscode_integration.py   # VS Code integration test
├── test_mcp_protocol.py         # MCP protocol compliance test
├── test_vscode_simulation.py    # VS Code simulation test
└── comprehensive_demo.py        # Complete demonstration
```

### Core Components

#### 1. **IDSMCPServer Class**

```python
class IDSMCPServer:
    """Main MCP server implementing the Model Context Protocol"""
    
    def __init__(self, config_path: str = "config.json"):
        # Server initialization
        
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # MCP initialization handshake
        
    async def handle_list_tools(self) -> Dict[str, Any]:
        # Return available tools
        
    async def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Execute tool calls
```

#### 2. **IDS Integration Layer**

```python
def get_ids_system():
    """Get enhanced IDS system or fallback to basic functionality"""
    
def load_unified_index() -> Dict[str, Any]:
    """Load the unified tags index"""
    
def load_file_metadata() -> Dict[str, Any]:
    """Load file metadata information"""
```

#### 3. **Tool Implementations**

- `ids_search`: Full-text search with tag filtering
- `ids_get_file_info`: File metadata retrieval
- `ids_list_tags`: Tag enumeration and filtering
- `ids_get_system_status`: System health monitoring
- `ids_find_by_tag`: Tag-based file discovery

---

## Architecture & Design

### MCP Protocol Flow

``` text
Client Request → JSON-RPC → Server Handler → IDS System → Response
```

### Request Processing Pipeline

1. **JSON-RPC Parsing**: Parse incoming MCP messages
2. **Method Routing**: Route to appropriate handler
3. **Parameter Validation**: Validate tool arguments
4. **IDS Integration**: Interface with documentation system
5. **Response Formatting**: Format results for MCP protocol
6. **Error Handling**: Manage and report errors

### Data Flow Diagram

``` text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│   IDS MCP       │───▶│   IDS System    │
│  (VS Code)      │    │    Server       │    │  (Enhanced)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       │                       │
         │                       ▼                       ▼
         └────────────── JSON-RPC Results ──────── YAML Indices
```

---

## Testing Framework

### 1. **Protocol Compliance Testing**

#### `test_mcp_protocol.py`

```python
"""
Comprehensive MCP protocol compliance testing
Tests all protocol methods and edge cases
"""

async def test_initialize_handshake():
    """Test MCP initialization handshake"""
    
async def test_tools_list():
    """Verify all 5 tools are returned with correct schemas"""
    
async def test_tool_execution():
    """Test each tool with various parameter combinations"""
    
async def test_error_handling():
    """Verify proper error responses"""
```

**Usage Example**:
```bash
cd .mcp/ids-mcp
python test_mcp_protocol.py
```

**Expected Output**:
``` text
✅ MCP Protocol Compliance Test Results:
┌─────────────────────────────────────────┬────────┐
│ Test Case                               │ Status │
├─────────────────────────────────────────┼────────┤
│ Initialize handshake                    │ PASS   │
│ Tools list (5 tools returned)          │ PASS   │
│ Tool execution (all 5 tools)           │ PASS   │
│ Error handling                          │ PASS   │
│ Parameter validation                    │ PASS   │
└─────────────────────────────────────────┴────────┘
```

### 2. **VS Code Integration Testing**

#### `test_vscode_integration.py`

```python
"""
Simulates VS Code MCP client behavior
Tests stdio communication and tool integration
"""

def test_stdio_communication():
    """Test stdio-based JSON-RPC communication"""
    
def test_vscode_tool_calls():
    """Simulate actual VS Code tool call patterns"""
    
def test_concurrent_requests():
    """Test handling multiple simultaneous requests"""
```

**Usage Example**:
```bash
python test_vscode_integration.py
```

**Sample Output**:
``` text
🔧 VS Code Integration Test Results:
────────────────────────────────────────────

✅ Server startup: SUCCESS
✅ Tool listing: 5 tools available
✅ Search functionality: 15 results returned
✅ File info retrieval: Complete metadata
✅ Tag listing: 2,900+ tags available
✅ System status: All systems operational
✅ Tag-based search: Filtered results
✅ Error handling: Graceful degradation
✅ Resource cleanup: No memory leaks

📊 Performance Metrics:
- Average response time: 45ms
- Memory usage: 52MB
- Index load time: 1.2s
```

### 3. **Comprehensive Demonstration**

#### `comprehensive_demo.py`

```python
"""
Complete end-to-end demonstration of all IDS MCP tools
Shows real-world usage patterns and expected outputs
"""

async def demo_search_functionality():
    """Demonstrate search with various parameters"""
    
async def demo_file_operations():
    """Show file info retrieval and metadata access"""
    
async def demo_tag_operations():
    """Demonstrate tag listing and filtering"""
    
async def demo_system_monitoring():
    """Show system status and health monitoring"""
```

**Execution**:
```bash
python comprehensive_demo.py
```

**Complete Output Example**:
``` text
🚀 ImpressionCore IDS MCP Server - Comprehensive Demo
════════════════════════════════════════════════════

📋 Tool 1: Document Search (ids_search)
─────────────────────────────────────────

🔍 Query: "authentication security"
📑 Results: 8 matches found

Files found:
1. docs/api/complete_api_reference_v2.md
   Tags: [api, security, authentication, reference]
   Score: 0.95

2. docs/security/auth_implementation.md
   Tags: [security, authentication, implementation]
   Score: 0.87

[... additional results ...]

📊 Tool 2: File Information (ids_get_file_info)
──────────────────────────────────────────────

📄 File: docs/api/complete_api_reference_v2.md
📅 Last Modified: 2025-06-03 14:30:22
📏 Size: 45.2 KB
🏷️  Tags: [api, security, authentication, reference, complete]
📝 Description: Complete API reference documentation v2

🏷️  Tool 3: Tag Listing (ids_list_tags)
────────────────────────────────────────

📊 Total Tags: 2,943 unique tags
📂 Categories: 15 main categories

Security-related tags (12 found):
- authentication (45 files)
- authorization (23 files)
- security (67 files)
- encryption (18 files)
[... additional tags ...]

⚙️  Tool 4: System Status (ids_get_system_status)
──────────────────────────────────────────────────

📈 System Health: ✅ OPERATIONAL
📊 Statistics:
- Indexed Files: 1,667
- Unique Tags: 2,943
- Last Index Update: 2025-06-05 09:15:43
- Index Size: 12.3 MB
- Memory Usage: 52.1 MB

🔍 Tool 5: Tag-based Discovery (ids_find_by_tag)
─────────────────────────────────────────────────

🏷️  Tags: ["core", "architecture"]
🔗 Match Mode: ALL (AND operation)
📑 Results: 23 files match all specified tags

Matching files:
1. docs/architecture/core_design.md
2. docs/ImpressionCore/system_architecture.md
3. src/core/README.md
[... additional files ...]

✅ Demo completed successfully!
📊 All 5 tools tested and verified working
⏱️  Total execution time: 2.34 seconds
```

---

## Detailed Usage Examples

### 1. **Search Operations**

#### Basic Text Search

```python
# Search for documents containing "memory optimization"
request = {
    "name": "ids_search",
    "arguments": {
        "query": "memory optimization",
        "max_results": 10
    }
}
```

#### Tag-Filtered Search

```python
# Search within specific domains
request = {
    "name": "ids_search",
    "arguments": {
        "query": "neural network",
        "tags": ["brainsim", "models", "architecture"],
        "max_results": 15
    }
}
```

#### Advanced Search Patterns

```python
# Complex queries with multiple concepts
queries = [
    "API endpoint authentication security",
    "brain simulation memory management",
    "web frontend user interface components",
    "database schema design patterns",
    "performance optimization techniques"
]
```

### 2. **File Information Retrieval**

#### Single File Analysis

```python
# Get comprehensive file metadata
request = {
    "name": "ids_get_file_info",
    "arguments": {
        "file_path": "docs/api/complete_api_reference_v2.md"
    }
}

# Expected response structure:
{
    "file_path": "docs/api/complete_api_reference_v2.md",
    "size": 46284,
    "last_modified": "2025-06-03T14:30:22Z",
    "tags": ["api", "security", "authentication", "reference"],
    "description": "Complete API reference documentation",
    "word_count": 8542,
    "line_count": 1234,
    "language": "markdown"
}
```

#### Batch File Processing

```python
# Process multiple files
important_files = [
    "docs/prd_complete_v3.md",
    "docs/api/complete_api_reference_v2.md",
    "docs/DOCUMENTATION_INDEX.md",
    "src/core/README.md"
]

for file_path in important_files:
    info = await call_tool("ids_get_file_info", {"file_path": file_path})
    print(f"📄 {file_path}: {info['tags']}")
```

### 3. **Tag Management**

#### Tag Discovery

```python
# List all available tags
all_tags = await call_tool("ids_list_tags", {})

# Filter by category
security_tags = await call_tool("ids_list_tags", {
    "category": "security"
})

# Pattern matching
auth_tags = await call_tool("ids_list_tags", {
    "pattern": "auth"
})
```

#### Tag-based File Discovery

```python
# Find files with specific tag combinations
architectural_docs = await call_tool("ids_find_by_tag", {
    "tags": ["architecture", "design", "core"],
    "match_all": True  # AND operation
})

security_related = await call_tool("ids_find_by_tag", {
    "tags": ["security", "authentication", "authorization"],
    "match_all": False  # OR operation
})
```

### 4. **System Monitoring**

#### Health Checks

```python
# Regular system status monitoring
status = await call_tool("ids_get_system_status", {})

# Check for system issues
if status["health_status"] != "OPERATIONAL":
    print(f"⚠️ System Issue: {status['issues']}")

# Monitor performance metrics
print(f"📊 Index Size: {status['index_size']}")
print(f"⚡ Average Response Time: {status['avg_response_time']}ms")
```

---

## Protocol Implementation

### MCP Message Flow

#### 1. **Initialization Handshake**

```json
// Client → Server
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "clientInfo": {
            "name": "vscode",
            "version": "1.0.0"
        }
    }
}

// Server → Client
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": false
            }
        },
        "serverInfo": {
            "name": "ids-mcp-server",
            "version": "1.0.0"
        }
    }
}
```

#### 2. **Tool Listing**

```json
// Client → Server
{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}

// Server → Client
{
    "jsonrpc": "2.0",
    "id": 2,
    "result": {
        "tools": [
            {
                "name": "ids_search",
                "description": "Search through ImpressionCore documentation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "max_results": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            }
            // ... 4 more tools
        ]
    }
}
```

#### 3. **Tool Execution**

```json
// Client → Server
{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "ids_search",
        "arguments": {
            "query": "authentication",
            "tags": ["security"],
            "max_results": 5
        }
    }
}

// Server → Client
{
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "🔍 Search Results for 'authentication'...\n\n📄 Found 5 matches:\n..."
            }
        ],
        "isError": false
    }
}
```

### Error Handling Protocol

```json
// Error response format
{
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "❌ Error: Invalid search query parameters"
            }
        ],
        "isError": true
    }
}
```

---

## VS Code Integration

### Configuration Setup

#### 1. **VS Code Settings**

```json
// .vscode/settings.json
{
    "mcp.servers": {
        "ids-mcp": {
            "command": "python",
            "args": ["D:/Projects/impressioncore/.mcp/ids-mcp/server.py"],
            "cwd": "D:/Projects/impressioncore/.mcp/ids-mcp",
            "env": {
                "PYTHONPATH": "D:/Projects/impressioncore"
            }
        }
    },
    "mcp.defaultServer": "ids-mcp"
}
```

#### 2. **Startup Script for VS Code**

```batch
@echo off
REM start_for_vscode.bat - VS Code specific startup
cd /d "D:\Projects\impressioncore\.mcp\ids-mcp"
set PYTHONPATH=D:\Projects\impressioncore
python server.py
```

### Integration Testing

#### Manual VS Code Testing

1. **Open VS Code Insiders** with MCP extension
2. **Check server connection**: `Ctrl+Shift+P` → "MCP: Show Servers"
3. **Test tool availability**: `Ctrl+Shift+P` → "MCP: List Tools"
4. **Execute searches**: Use `@ids-mcp search documentation`
5. **Monitor logs**: Check VS Code Output panel → MCP

#### Automated VS Code Simulation

```python
# test_vscode_simulation.py
async def simulate_vscode_workflow():
    """Simulate typical VS Code MCP integration workflow"""
    
    # 1. Server initialization
    await test_server_startup()
    
    # 2. Tool discovery
    tools = await test_tool_listing()
    assert len(tools) == 5
    
    # 3. Interactive search session
    search_results = await test_interactive_search()
    
    # 4. File exploration
    file_info = await test_file_exploration()
    
    # 5. Tag-based navigation
    tagged_files = await test_tag_navigation()
    
    print("✅ VS Code simulation completed successfully")
```

---

## Debugging & Troubleshooting

### Logging Configuration

#### Server Logging

```python
# Enhanced logging setup
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("ids_mcp")
```

#### Log Analysis

```bash
# Monitor real-time logs
tail -f ids_mcp.log

# Search for specific events
grep "ERROR" ids_mcp.log
grep "search" ids_mcp.log | head -20
```

### Common Issues & Solutions

#### 1. **Server Startup Issues**

```python
# Diagnostic script
def diagnose_startup():
    """Diagnose common startup problems"""
    
    checks = [
        ("Python version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Config files", check_config_files),
        ("IDS indices", check_ids_indices),
        ("Permissions", check_permissions)
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            print(f"✅ {name}: OK")
        except Exception as e:
            print(f"❌ {name}: {e}")
```

#### 2. **VS Code Connection Issues**

```json
// Debugging VS Code integration
{
    "mcp.servers": {
        "ids-mcp": {
            "command": "python",
            "args": ["-u", "server.py"],  // Unbuffered output
            "cwd": "D:/Projects/impressioncore/.mcp/ids-mcp",
            "env": {
                "PYTHONPATH": "D:/Projects/impressioncore",
                "LOG_LEVEL": "DEBUG"  // Enable debug logging
            }
        }
    },
    "mcp.trace.server": "verbose"  // Enable MCP tracing
}
```

#### 3. **Performance Issues**

```python
# Performance monitoring
import time
import memory_profiler

class PerformanceMonitor:
    def __init__(self):
        self.timings = {}
        self.memory_usage = {}
    
    def time_operation(self, operation_name):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = memory_profiler.memory_usage()[0]
                
                result = await func(*args, **kwargs)
                
                end_time = time.time()
                end_memory = memory_profiler.memory_usage()[0]
                
                self.timings[operation_name] = end_time - start_time
                self.memory_usage[operation_name] = end_memory - start_memory
                
                return result
            return wrapper
        return decorator
```

---

## Performance Optimization

### Caching Strategies

#### 1. **Index Caching**

```python
class IndexCache:
    def __init__(self, ttl=300):  # 5 minute TTL
        self.cache = {}
        self.ttl = ttl
        self.timestamps = {}
    
    def get_unified_index(self):
        if self.is_cached("unified_index"):
            return self.cache["unified_index"]
        
        index = self.load_unified_index_from_disk()
        self.cache["unified_index"] = index
        self.timestamps["unified_index"] = time.time()
        return index
```

#### 2. **Search Result Caching**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str, tags_tuple: tuple, max_results: int):
    """Cache search results for repeated queries"""
    return perform_search(query, list(tags_tuple), max_results)
```

### Memory Management

```python
# Memory-efficient file processing
def process_large_index(index_path: str):
    """Process large indices without loading everything into memory"""
    
    with open(index_path, 'r') as f:
        for line in f:
            # Process line by line instead of loading entire file
            yield process_line(line)
```

### Concurrent Request Handling

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ConcurrentServer:
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def handle_concurrent_searches(self, requests):
        """Handle multiple search requests concurrently"""
        
        tasks = [
            asyncio.create_task(self.process_search(req))
            for req in requests
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

---

## Extension Development

### Adding New Tools

#### 1. **Tool Definition**

```python
# Add to handle_list_tools()
{
    "name": "ids_analyze_sentiment",
    "description": "Analyze sentiment of documentation content",
    "inputSchema": {
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["file_path"]
    }
}
```

#### 2. **Tool Implementation**

```python
async def handle_sentiment_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze sentiment of documentation content"""
    
    file_path = arguments.get("file_path")
    content = arguments.get("content")
    
    if not content:
        # Load content from file
        content = self.load_file_content(file_path)
    
    # Perform sentiment analysis
    sentiment_score = self.analyze_sentiment(content)
    
    return {
        "content": [{
            "type": "text",
            "text": f"📊 Sentiment Analysis for {file_path}:\n"
                   f"Score: {sentiment_score:.2f}\n"
                   f"Classification: {self.classify_sentiment(sentiment_score)}"
        }],
        "isError": False
    }
```

#### 3. **Tool Registration**

```python
# Add to handle_call_tool()
elif name == "ids_analyze_sentiment":
    return await self.handle_sentiment_analysis(arguments)
```

### Custom Integrations

#### Web API Integration

```python
class WebAPIIntegration:
    """Integrate IDS MCP server with web APIs"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def expose_search_endpoint(self):
        """Expose search functionality via REST API"""
        
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.post("/search")
        async def search_endpoint(query: str, tags: List[str] = None):
            result = await self.ids_server.handle_search({
                "query": query,
                "tags": tags or []
            })
            return result
```

#### Database Integration

```python
class DatabaseIntegration:
    """Store search analytics in database"""
    
    async def log_search_query(self, query: str, results_count: int):
        """Log search queries for analytics"""
        
        query_log = {
            "timestamp": datetime.utcnow(),
            "query": query,
            "results_count": results_count,
            "user_session": self.get_session_id()
        }
        
        await self.db.search_logs.insert_one(query_log)
```

---

## Best Practices

### Code Quality

#### 1. **Type Hints**

```python
from typing import Dict, List, Optional, Union, Any

async def search_documents(
    query: str,
    tags: Optional[List[str]] = None,
    max_results: int = 10
) -> Dict[str, Any]:
    """Search documents with proper type hints"""
    pass
```

#### 2. **Error Handling**

```python
class IDSMCPError(Exception):
    """Base exception for IDS MCP server"""
    pass

class SearchError(IDSMCPError):
    """Search operation failed"""
    pass

class IndexError(IDSMCPError):
    """Index loading or parsing failed"""
    pass

# Usage
try:
    results = await self.perform_search(query)
except SearchError as e:
    logger.error(f"Search failed: {e}")
    return self.error_response(str(e))
```

#### 3. **Input Validation**

```python
def validate_search_params(query: str, tags: List[str], max_results: int):
    """Validate search parameters"""
    
    if not query or len(query.strip()) == 0:
        raise ValueError("Query cannot be empty")
    
    if max_results <= 0 or max_results > 100:
        raise ValueError("max_results must be between 1 and 100")
    
    if tags and not all(isinstance(tag, str) for tag in tags):
        raise ValueError("All tags must be strings")
```

### Security Considerations

#### 1. **Path Traversal Prevention**

```python
import os
from pathlib import Path

def safe_file_access(file_path: str, allowed_root: str) -> bool:
    """Prevent path traversal attacks"""
    
    try:
        requested_path = Path(file_path).resolve()
        allowed_root_path = Path(allowed_root).resolve()
        
        # Check if requested path is within allowed root
        return str(requested_path).startswith(str(allowed_root_path))
    except (OSError, ValueError):
        return False
```

#### 2. **Resource Limits**

```python
class ResourceLimiter:
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_search_results = 100
        self.request_timeout = 30  # seconds
    
    def check_file_size(self, file_path: str):
        """Check if file size is within limits"""
        size = os.path.getsize(file_path)
        if size > self.max_file_size:
            raise ValueError(f"File too large: {size} bytes")
```

### Testing Best Practices

#### 1. **Comprehensive Test Coverage**

```python
import pytest
import asyncio

class TestIDSMCPServer:
    @pytest.fixture
    async def server(self):
        """Create test server instance"""
        server = IDSMCPServer("test_config.json")
        await server.initialize()
        yield server
        await server.cleanup()
    
    @pytest.mark.asyncio
    async def test_search_functionality(self, server):
        """Test search with various parameters"""
        
        # Test basic search
        result = await server.handle_search({"query": "test"})
        assert not result["isError"]
        
        # Test with tags
        result = await server.handle_search({
            "query": "test",
            "tags": ["documentation"]
        })
        assert not result["isError"]
        
        # Test error conditions
        result = await server.handle_search({"query": ""})
        assert result["isError"]
```

#### 2. **Integration Testing**

```python
async def test_full_workflow():
    """Test complete MCP workflow"""
    
    # Start server
    server = await start_test_server()
    
    # Initialize MCP connection
    init_response = await server.handle_initialize({
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}}
    })
    assert init_response["result"]["protocolVersion"] == "2024-11-05"
    
    # List tools
    tools_response = await server.handle_list_tools()
    assert len(tools_response["result"]["tools"]) == 5
    
    # Test each tool
    for tool in tools_response["result"]["tools"]:
        result = await test_tool(server, tool)
        assert not result["isError"]
```

---

## Conclusion

This developer guide provides comprehensive coverage of the ImpressionCore IDS MCP Server development, testing, and integration processes. Key takeaways:

### ✅ **Implemented Features**

- Complete MCP protocol compliance
- 5 fully functional IDS tools
- VS Code integration support
- Comprehensive testing framework
- Performance optimization
- Error handling and logging

### 🧪 **Testing Coverage**

- Protocol compliance testing
- VS Code integration simulation
- Performance benchmarking
- Error condition handling
- Concurrent request processing

### 📚 **Documentation**

- Detailed usage examples
- Integration guides
- Troubleshooting procedures
- Best practices
- Extension development

### 🚀 **Next Steps**

- Deploy in production VS Code environment
- Monitor real-world usage patterns
- Collect user feedback
- Implement additional tools as needed
- Performance optimization based on usage data

---

**Last Updated**: 2025-06-05  
**Version**: 1.0.0  
**Maintainer**: ImpressionCore Development Team
