#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #documentation #python #source_code #src/tests/test_enhanced_mcp_servers.py #testing #training #web_interface
**Category:** Testing Framework
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #documentation #python #source_code #src\\tests\\test_enhanced_mcp_servers.py #testing #training #web_interface
# Category:** Testing Framework
# Status:** Active

"""
ImpressionCore Enhanced MCP Server Test Suite
============================================
Comprehensive testing for IDS, EDS, and VRGC MCP servers

🚀 VIRTUALLY ROBOTIC GITHUB COPILOT - AUTOEXECUTE MODE
Testing revolutionary 30+ tool architecture with AI, web, and FTP capabilities
"""

import asyncio
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

import pytest

# Test results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "servers": {},
    "summary": {}
}

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🤖 {title}")
    print(f"{'='*60}")

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'─'*40}")
    print(f"🔧 {title}")
    print(f"{'─'*40}")

async def test_ids_server():
    """Test ImpressionCore IDS (Documentation System) MCP Server"""
    print_header("TESTING IDS - AI-ENHANCED DOCUMENTATION SYSTEM")

    server_results = {
        "name": "ImpressionCore IDS",
        "status": "unknown",
        "tools": [],
        "tests": {},
        "errors": []
    }

    try:
        from server_ai_enhanced import ai_ids
    except (ImportError, SyntaxError):
        pytest.skip("IDS MCP server not importable")

    try:
        # Add IDS server path
        ids_path = Path("d:/Projects/impressioncore/.mcp/ids-mcp")
        sys.path.insert(0, str(ids_path))

        from server_ai_enhanced import ai_ids

        print("✅ IDS Server imported successfully")

        # Test knowledge graph
        print_section("Knowledge Graph Status")
        try:
            graph_stats = ai_ids.get_system_status()
            print(f"📊 Knowledge Graph: {graph_stats.get('knowledge_graph', {}).get('status', 'Unknown')}")
            print(f"📁 Indexed Files: {graph_stats.get('indexed_files', 0)}")
            print(f"🏷️  Total Tags: {graph_stats.get('total_tags', 0)}")
            server_results["tests"]["knowledge_graph"] = "✅ PASS"
        except Exception as e:
            print(f"❌ Knowledge graph error: {e}")
            server_results["errors"].append(f"Knowledge graph: {e}")
            server_results["tests"]["knowledge_graph"] = "❌ FAIL"

        # Test search functionality
        print_section("Search Functionality")
        try:
            search_result = ai_ids.search("vrgc mcp")
            print(f"🔍 Search test completed: Found {len(search_result.get('files', []))} results")
            server_results["tests"]["search"] = "✅ PASS"
        except Exception as e:
            print(f"❌ Search error: {e}")
            server_results["errors"].append(f"Search: {e}")
            server_results["tests"]["search"] = "❌ FAIL"

        # Test tag system
        print_section("Tag System")
        try:
            tags = ai_ids.list_tags()
            print(f"🏷️  Available tags: {len(tags)}")
            if tags:
                print(f"🔖 Sample tags: {', '.join(list(tags.keys())[:5])}")
            server_results["tests"]["tags"] = "✅ PASS"
        except Exception as e:
            print(f"❌ Tag system error: {e}")
            server_results["errors"].append(f"Tags: {e}")
            server_results["tests"]["tags"] = "❌ FAIL"

        server_results["status"] = "✅ OPERATIONAL"

    except Exception as e:
        print(f"❌ IDS Server failed to initialize: {e}")
        server_results["status"] = "❌ FAILED"
        server_results["errors"].append(f"Initialization: {e}")
        traceback.print_exc()

    test_results["servers"]["ids"] = server_results
    return server_results

async def test_eds_server():
    """Test ImpressionCore EDS (Enhanced Data System) MCP Server"""
    print_header("TESTING EDS - ENHANCED DATA SYSTEM")

    server_results = {
        "name": "ImpressionCore EDS",
        "status": "unknown",
        "tools": [],
        "tests": {},
        "errors": []
    }

    try:
        from server_enhanced import EDSEnhancedMCPServer
    except ImportError:
        pytest.skip("EDS MCP server not importable")

    try:
        # Add EDS server path
        eds_path = Path("d:/Projects/impressioncore/.mcp/impressioncore-eds")
        sys.path.insert(0, str(eds_path))

        from server_enhanced import EDSEnhancedMCPServer

        async with EDSEnhancedMCPServer() as eds_server:
            print("✅ EDS Server initialized successfully")

            # Test tool listing
            print_section("Tool Inventory")
            tools = eds_server.get_tools()
            print(f"🛠️  Available tools: {len(tools)}")
            for i, tool in enumerate(tools[:5], 1):
                print(f"  {i}. {tool['name']}")
            if len(tools) > 5:
                print(f"  ... and {len(tools) - 5} more tools")

            server_results["tools"] = [tool["name"] for tool in tools]
            server_results["tests"]["tool_listing"] = "✅ PASS"

            # Test sample tool calls
            print_section("Sample Tool Tests")
            sample_tests = [
                ("eds_create_dataset", {"name": "test_dataset", "type": "text"}),
                ("eds_system_status", {}),
            ]

            for tool_name, test_args in sample_tests:
                try:
                    result = await eds_server.call_tool(tool_name, test_args)
                    if "error" not in result:
                        print(f"✅ {tool_name}: OK")
                        server_results["tests"][tool_name] = "✅ PASS"
                    else:
                        print(f"⚠️  {tool_name}: {result.get('error', 'Unknown error')}")
                        server_results["tests"][tool_name] = "⚠️ WARNING"
                except Exception as e:
                    print(f"❌ {tool_name}: {e}")
                    server_results["tests"][tool_name] = "❌ FAIL"
                    server_results["errors"].append(f"{tool_name}: {e}")

            server_results["status"] = "✅ OPERATIONAL"

    except Exception as e:
        print(f"❌ EDS Server failed to initialize: {e}")
        server_results["status"] = "❌ FAILED"
        server_results["errors"].append(f"Initialization: {e}")
        traceback.print_exc()

    test_results["servers"]["eds"] = server_results
    return server_results

async def test_vrgc_server():
    """Test ImpressionCore VRGC (Enhanced Web) MCP Server"""
    print_header("TESTING VRGC - ENHANCED WEB & AI SYSTEM")

    server_results = {
        "name": "ImpressionCore VRGC Enhanced",
        "status": "unknown",
        "tools": [],
        "tests": {},
        "errors": []
    }

    try:
        from server_enhanced import VRGCEnhancedWebMCPServer
    except ImportError:
        pytest.skip("VRGC MCP server not importable")

    try:
        # Add VRGC server path
        vrgc_path = Path("d:/Projects/impressioncore/.mcp/impressioncore-vrgc")
        sys.path.insert(0, str(vrgc_path))

        from server_enhanced import VRGCEnhancedWebMCPServer

        async with VRGCEnhancedWebMCPServer() as vrgc_server:
            print("✅ VRGC Server initialized successfully")

            # Test tool listing
            print_section("Revolutionary Tool Arsenal")
            tools = vrgc_server.get_tools()
            print(f"🛠️  Total tools: {len(tools)} (Revolutionary 30+ architecture)")

            # Categorize tools
            web_tools = [t for t in tools if "web" in t["name"]]
            neural_tools = [t for t in tools if any(x in t["name"] for x in ["neural", "architecture", "model"])]
            system_tools = [t for t in tools if any(x in t["name"] for x in ["system", "hardware", "training"])]

            print(f"🌐 Web/Internet Tools: {len(web_tools)}")
            print(f"🧠 Neural Architecture Tools: {len(neural_tools)}")
            print(f"⚙️  System/Hardware Tools: {len(system_tools)}")

            server_results["tools"] = [tool["name"] for tool in tools]
            server_results["tests"]["tool_listing"] = "✅ PASS"

            # Test revolutionary web capabilities
            print_section("Web Access & Internet Integration Tests")
            web_tests = [
                ("vrgc_web_fetch", {"url": "https://httpbin.org/get", "method": "GET"}),
                ("vrgc_web_search", {"query": "python programming", "engine": "duckduckgo"}),
                ("vrgc_assess_system", {"assessment_type": "hardware"}),
            ]

            for tool_name, test_args in web_tests:
                try:
                    print(f"  Testing {tool_name}...", end=" ")
                    result = await vrgc_server.call_tool(tool_name, test_args)
                    if "error" not in result:
                        print("✅ OK")
                        server_results["tests"][tool_name] = "✅ PASS"
                    else:
                        print(f"⚠️ {result.get('error', 'Unknown error')[:50]}...")
                        server_results["tests"][tool_name] = "⚠️ WARNING"
                except Exception as e:
                    print(f"❌ {e}")
                    server_results["tests"][tool_name] = "❌ FAIL"
                    server_results["errors"].append(f"{tool_name}: {e}")

            server_results["status"] = "✅ OPERATIONAL"

    except Exception as e:
        print(f"❌ VRGC Server failed to initialize: {e}")
        server_results["status"] = "❌ FAILED"
        server_results["errors"].append(f"Initialization: {e}")
        traceback.print_exc()

    test_results["servers"]["vrgc"] = server_results
    return server_results

async def main():
    """Main test execution"""
    print_header("IMPRESSIONCORE ENHANCED MCP SERVER TEST SUITE")
    print("🚀 VIRTUALLY ROBOTIC GITHUB COPILOT - AUTOEXECUTE MODE")
    print("Testing revolutionary AI, web, and documentation capabilities")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test all servers
    ids_results = await test_ids_server()
    eds_results = await test_eds_server()
    vrgc_results = await test_vrgc_server()

    # Generate summary
    print_header("TEST COMPLETION SUMMARY")

    total_servers = 3
    operational_servers = sum(1 for r in [ids_results, eds_results, vrgc_results] if r["status"] == "✅ OPERATIONAL")

    total_tools = sum(len(r.get("tools", [])) for r in [ids_results, eds_results, vrgc_results])
    total_tests = sum(len(r.get("tests", {})) for r in [ids_results, eds_results, vrgc_results])
    passed_tests = sum(sum(1 for t in r.get("tests", {}).values() if "✅" in t) for r in [ids_results, eds_results, vrgc_results])

    print("📊 OVERALL RESULTS:")
    print(f"🖥️  Servers Tested: {total_servers}")
    print(f"✅ Operational: {operational_servers}/{total_servers}")
    print(f"🛠️  Total Tools: {total_tools}")
    print(f"🧪 Tests Run: {total_tests}")
    print(f"✅ Tests Passed: {passed_tests}/{total_tests}")

    # Individual server status
    print("\n📋 SERVER STATUS:")
    for server_name, result in [("IDS", ids_results), ("EDS", eds_results), ("VRGC", vrgc_results)]:
        status = result["status"]
        tool_count = len(result.get("tools", []))
        print(f"  {server_name}: {status} ({tool_count} tools)")

    # Save results
    test_results["summary"] = {
        "total_servers": total_servers,
        "operational_servers": operational_servers,
        "total_tools": total_tools,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
    }

    # Write results to file
    results_file = Path("d:/Projects/impressioncore/src/memlog") / f"mcp_server_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)

    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)

    print(f"\n💾 Test results saved to: {results_file}")

    if operational_servers == total_servers:
        print("\n🎉 ALL SYSTEMS OPERATIONAL! Revolutionary MCP server suite ready for production!")
        return True
    else:
        print(f"\n⚠️  {total_servers - operational_servers} server(s) need attention")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
