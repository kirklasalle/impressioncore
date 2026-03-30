#!/usr/bin/env python3
"""
Comprehensive test of ALL ImpressionCore IDS MCP server tools.
Tests every available tool and documents the results.
Created: 2025-06-08
"""

import asyncio
import json
import sys
import os
import time
from datetime import datetime

# Add the server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.mcp', 'ids-mcp'))

class TestResults:
    """Track test results for documentation."""
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def add_result(self, tool_name, status, description, result=None, error=None):
        """Add a test result."""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
        self.results.append({
            "tool": tool_name,
            "status": status,
            "description": description,
            "result": result,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        })
    
    def print_summary(self):
        """Print test summary."""
        duration = time.time() - self.start_time
        print(f"\n" + "="*70)
        print(f"📊 TEST SUMMARY")
        print(f"="*70)
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
    def export_results(self, filename):
        """Export results to JSON file."""
        with open(filename, 'w') as f:
            json.dump({
                "test_summary": {
                    "total_tests": self.total_tests,
                    "passed_tests": self.passed_tests,
                    "failed_tests": self.failed_tests,
                    "success_rate": (self.passed_tests/self.total_tests)*100,
                    "duration_seconds": time.time() - self.start_time,
                    "timestamp": datetime.now().isoformat()
                },
                "test_results": self.results
            }, f, indent=2)

async def test_ids_tools():
    """Test ALL ImpressionCore IDS tools comprehensively."""
    test_tracker = TestResults()
    
    print("🚀 COMPREHENSIVE ImpressionCore IDS MCP Tools Testing")
    print("="*70)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        # Import the server class
        from server import IDSMCPServer
        
        # Initialize the server
        print("🔧 Initializing server...")
        server = IDSMCPServer()
        print("✅ Server initialized successfully!")
        
        # TEST 1: Get System Status
        print("\n🔍 TEST 1: get-system-status")
        try:
            result = await server.handle_call_tool("get-system-status", {})
            print(f"✅ System Status Retrieved")
            if 'system_info' in result:
                info = result['system_info']
                print(f"   📊 Files indexed: {info.get('total_files', 'Unknown')}")
                print(f"   🏷️  Total tags: {info.get('total_tags', 'Unknown')}")
            test_tracker.add_result("get-system-status", "PASS", "Retrieved system status", result)
        except Exception as e:
            print(f"❌ System status error: {e}")
            test_tracker.add_result("get-system-status", "FAIL", "Failed to get system status", error=e)
        
        # TEST 2: List Available Tags
        print("\n🏷️  TEST 2: list-tags")
        try:
            result = await server.handle_call_tool("list-tags", {})
            tags = result.get('tags', [])
            print(f"✅ Found {len(tags)} tags")
            if tags:
                print("📋 Sample tags:")
                for tag in tags[:10]:  # Show first 10 tags
                    print(f"   • {tag}")
                if len(tags) > 10:
                    print(f"   ... and {len(tags) - 10} more")
            test_tracker.add_result("list-tags", "PASS", f"Retrieved {len(tags)} tags", result)
        except Exception as e:
            print(f"❌ List tags error: {e}")
            test_tracker.add_result("list-tags", "FAIL", "Failed to list tags", error=e)
        
        # TEST 3: Search Documentation
        print("\n🔍 TEST 3: search")
        try:
            search_params = {
                "query": "authentication",
                "max_results": 5
            }
            result = await server.handle_call_tool("search", search_params)
            results = result.get('results', [])
            print(f"✅ Found {len(results)} results for 'authentication'")
            for i, res in enumerate(results, 1):
                file_path = res.get('file_path', 'Unknown')
                score = res.get('relevance_score', 0)
                print(f"   {i}. {file_path} (score: {score:.2f})")
            test_tracker.add_result("search", "PASS", f"Found {len(results)} results for 'authentication'", result)
        except Exception as e:
            print(f"❌ Search error: {e}")
            test_tracker.add_result("search", "FAIL", "Failed to search documentation", error=e)

        # TEST 4: Find Files by Tag
        print("\n🏷️  TEST 4: find-by-tag")
        try:
            tag_params = {
                "tags": ["api"],
                "match_all": False
            }
            result = await server.handle_call_tool("find-by-tag", tag_params)
            files = result.get('files', [])
            print(f"✅ Found {len(files)} files with 'api' tag")
            for i, file_path in enumerate(files[:5], 1):  # Show first 5
                print(f"   {i}. {file_path}")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more")
            test_tracker.add_result("find-by-tag", "PASS", f"Found {len(files)} files with 'api' tag", result)
        except Exception as e:
            print(f"❌ Find by tag error: {e}")
            test_tracker.add_result("find-by-tag", "FAIL", "Failed to find files by tag", error=e)
        
        # TEST 5: Get Documentation Stats
        print("\n📊 TEST 5: get-documentation-stats")
        try:
            result = await server.handle_call_tool("get-documentation-stats", {})
            print("✅ Documentation statistics retrieved")
            if 'statistics' in result:
                stats = result['statistics']
                print(f"   📁 Total files: {stats.get('total_files', 'Unknown')}")
                print(f"   🏷️  Total tags: {stats.get('total_tags', 'Unknown')}")
                print(f"   📏 Average file size: {stats.get('average_file_size', 'Unknown')}")
            test_tracker.add_result("get-documentation-stats", "PASS", "Retrieved documentation statistics", result)
        except Exception as e:
            print(f"❌ Documentation stats error: {e}")
            test_tracker.add_result("get-documentation-stats", "FAIL", "Failed to get documentation stats", error=e)
        
        # TEST 6: Get File Info
        print("\n📄 TEST 6: get-file-info")
        try:
            # Use a known file from the project
            file_params = {
                "file_path": "docs/DOCUMENTATION_INDEX.md"
            }
            result = await server.handle_call_tool("get-file-info", file_params)
            print("✅ File info retrieved")
            if 'file_info' in result:
                info = result['file_info']
                print(f"   📁 File: {info.get('file_path', 'Unknown')}")
                print(f"   📏 Size: {info.get('size_bytes', 'Unknown')} bytes")
                print(f"   🏷️  Tags: {len(info.get('tags', []))}")
            test_tracker.add_result("get-file-info", "PASS", "Retrieved file information", result)
        except Exception as e:
            print(f"❌ File info error: {e}")
            test_tracker.add_result("get-file-info", "FAIL", "Failed to get file info", error=e)
        
        # TEST 7: Search Content
        print("\n🔍 TEST 7: search-content")
        try:
            search_params = {
                "query": "ImpressionCore",
                "max_results": 3
            }
            result = await server.handle_call_tool("search-content", search_params)
            results = result.get('results', [])
            print(f"✅ Found {len(results)} content matches for 'ImpressionCore'")
            for i, res in enumerate(results, 1):
                file_path = res.get('file_path', 'Unknown')
                print(f"   {i}. {file_path}")
            test_tracker.add_result("search-content", "PASS", f"Found {len(results)} content matches", result)
        except Exception as e:
            print(f"❌ Search content error: {e}")
            test_tracker.add_result("search-content", "FAIL", "Failed to search content", error=e)
        
        # TEST 8: Get Recent Changes
        print("\n📅 TEST 8: get-recent-changes")
        try:
            params = {
                "days": 7
            }
            result = await server.handle_call_tool("get-recent-changes", params)
            changes = result.get('recent_changes', [])
            print(f"✅ Found {len(changes)} recent changes (last 7 days)")
            for i, change in enumerate(changes[:5], 1):
                file_path = change.get('file_path', 'Unknown')
                print(f"   {i}. {file_path}")
            test_tracker.add_result("get-recent-changes", "PASS", f"Found {len(changes)} recent changes", result)
        except Exception as e:
            print(f"❌ Recent changes error: {e}")
            test_tracker.add_result("get-recent-changes", "FAIL", "Failed to get recent changes", error=e)
        
        # TEST 9: Manage Tags (list)
        print("\n🏷️  TEST 9: manage-tags (list)")
        try:
            params = {
                "action": "list"
            }
            result = await server.handle_call_tool("manage-tags", params)
            print("✅ Tag management (list) completed")
            test_tracker.add_result("manage-tags", "PASS", "Tag management list operation", result)
        except Exception as e:
            print(f"❌ Manage tags error: {e}")
            test_tracker.add_result("manage-tags", "FAIL", "Failed to manage tags", error=e)
        
        # TEST 10: Validate Index
        print("\n🔍 TEST 10: validate-index")
        try:
            result = await server.handle_call_tool("validate-index", {})
            print("✅ Index validation completed")
            if 'validation_results' in result:
                validation = result['validation_results']
                print(f"   ✅ Valid: {validation.get('is_valid', 'Unknown')}")
                print(f"   📊 Issues found: {len(validation.get('issues', []))}")
            test_tracker.add_result("validate-index", "PASS", "Index validation completed", result)
        except Exception as e:
            print(f"❌ Validate index error: {e}")
            test_tracker.add_result("validate-index", "FAIL", "Failed to validate index", error=e)
        
        # TEST 11: Export Data
        print("\n📤 TEST 11: export-data")
        try:
            params = {
                "format": "json",
                "include_content": False
            }
            result = await server.handle_call_tool("export-data", params)
            print("✅ Data export completed")
            if 'export_info' in result:
                info = result['export_info']
                print(f"   📁 Exported to: {info.get('file_path', 'Unknown')}")
                print(f"   📊 Records exported: {info.get('records_exported', 'Unknown')}")
            test_tracker.add_result("export-data", "PASS", "Data export completed", result)
        except Exception as e:
            print(f"❌ Export data error: {e}")
            test_tracker.add_result("export-data", "FAIL", "Failed to export data", error=e)
        
        # TEST 12: Bookmark Management (list)
        print("\n🔖 TEST 12: bookmark-management (list)")
        try:
            params = {
                "action": "list"
            }
            result = await server.handle_call_tool("bookmark-management", params)
            bookmarks = result.get('bookmarks', [])
            print(f"✅ Found {len(bookmarks)} bookmarks")
            for i, bookmark in enumerate(bookmarks[:3], 1):
                title = bookmark.get('title', 'Unknown')
                print(f"   {i}. {title}")
            test_tracker.add_result("bookmark-management", "PASS", f"Retrieved {len(bookmarks)} bookmarks", result)
        except Exception as e:
            print(f"❌ Bookmark management error: {e}")
            test_tracker.add_result("bookmark-management", "FAIL", "Failed to manage bookmarks", error=e)
        
        # TEST 13: Analyze Documentation
        print("\n📈 TEST 13: analyze-documentation")
        try:
            result = await server.handle_call_tool("analyze-documentation", {})
            print("✅ Documentation analysis completed")
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"   📊 Overall score: {analysis.get('overall_score', 'Unknown')}")
                print(f"   📈 Completeness: {analysis.get('completeness_score', 'Unknown')}")
            test_tracker.add_result("analyze-documentation", "PASS", "Documentation analysis completed", result)
        except Exception as e:
            print(f"❌ Analyze documentation error: {e}")
            test_tracker.add_result("analyze-documentation", "FAIL", "Failed to analyze documentation", error=e)
        
        # TEST 14: Backup System
        print("\n💾 TEST 14: backup-system")
        try:
            result = await server.handle_call_tool("backup-system", {})
            print("✅ System backup completed")
            if 'backup_info' in result:
                info = result['backup_info']
                print(f"   📁 Backup location: {info.get('backup_path', 'Unknown')}")
                print(f"   📊 Files backed up: {info.get('files_backed_up', 'Unknown')}")
            test_tracker.add_result("backup-system", "PASS", "System backup completed", result)
        except Exception as e:
            print(f"❌ Backup system error: {e}")
            test_tracker.add_result("backup-system", "FAIL", "Failed to backup system", error=e)
        
        # TEST 15: Rebuild Index
        print("\n🔧 TEST 15: rebuild-index")
        try:
            params = {
                "target": "tags"  # Only rebuild tags to be safe
            }
            result = await server.handle_call_tool("rebuild-index", params)
            print("✅ Index rebuild completed")
            if 'rebuild_info' in result:
                info = result['rebuild_info']
                print(f"   📊 Items rebuilt: {info.get('items_rebuilt', 'Unknown')}")
                print(f"   ⏱️  Duration: {info.get('duration_seconds', 'Unknown')} seconds")
            test_tracker.add_result("rebuild-index", "PASS", "Index rebuild completed", result)
        except Exception as e:
            print(f"❌ Rebuild index error: {e}")
            test_tracker.add_result("rebuild-index", "FAIL", "Failed to rebuild index", error=e)
        
        # Print comprehensive summary
        test_tracker.print_summary()
        
        # Export results for documentation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"src/memlog/ids_tools_test_results_{timestamp}.json"
        test_tracker.export_results(results_file)
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        print("\n🎉 Comprehensive ImpressionCore IDS MCP Tools Testing Complete!")
        
    except Exception as e:
        print(f"❌ Failed to initialize server: {e}")
        import traceback
        traceback.print_exc()
        test_tracker.add_result("server-init", "FAIL", "Failed to initialize server", error=e)

if __name__ == "__main__":
    asyncio.run(test_ids_tools())
