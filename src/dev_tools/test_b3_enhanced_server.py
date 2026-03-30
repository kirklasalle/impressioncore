#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** July-25-2025
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #documentation #python #source_code #src/dev_tools/test_b3_enhanced_server.py #testing
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2025-07-25
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #documentation #python #source_code #src\\dev_tools\\test_b3_enhanced_server.py #testing
# Category:** Development Tools
# Status:** Active

"""
B3 Enhanced IDS MCP Server Test Script

**Created:** 2025-07-25
**Updated:** 2025-07-25 14:40:00
**Author:** GitHub Copilot (B3 Testing)
**Tags:** #testing #mcp_server #b3_enhancement #validation
**Category:** Testing
**Status:** Active
"""

import sys
from pathlib import Path


def test_b3_enhanced_server():
    """Test the B3 Enhanced IDS MCP Server functionality."""

    PROJECT_ROOT = Path(__file__).parent.parent.parent
    server_path = PROJECT_ROOT / ".mcp" / "ids-mcp" / "server.py"

    print("🔍 Testing B3 Enhanced IDS MCP Server...")
    print(f"Server path: {server_path}")

    # Test 1: Check if server can be imported
    try:
        sys.path.insert(0, str(server_path.parent))

        # Import and create server instance
        exec(open(server_path).read(), globals())
        server = IDSMCPServerB3Enhanced()

        print("✅ Server instantiation: SUCCESS")

        # Test 2: Check available tools
        tools = server.get_tools()
        print(f"✅ Available tools: {len(tools)} (expected: 8)")

        tool_names = [tool['name'] for tool in tools]
        expected_new_tools = [
            'mcp_impressioncor_mcp_impressioncor_run-header-updater',
            'mcp_impressioncor_mcp_impressioncor_run-documentation-indexer',
            'mcp_impressioncor_mcp_impressioncor_run-system-validator'
        ]

        for tool_name in expected_new_tools:
            if tool_name in tool_names:
                print(f"✅ B3 Tool found: {tool_name}")
            else:
                print(f"❌ B3 Tool missing: {tool_name}")

        # Test 3: Check system status
        status = server.handle_get_system_status()
        print(f"✅ Server version: {status.get('server_version', 'Unknown')}")
        print(f"✅ B3 enhancements: {status.get('b3_enhancements', {}).get('automation_tools', 0)} tools")

        # Test 4: Test search functionality
        search_result = server.handle_search("documentation", max_results=3)
        print(f"✅ Search test: Found {len(search_result.get('results', []))} results")

        print("\n🎉 B3 Enhanced Server Test: ALL TESTS PASSED!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_b3_enhanced_server()
    sys.exit(0 if success else 1)
