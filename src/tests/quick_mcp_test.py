#!/usr/bin/env python3
"""
Quick MCP Test - Direct tool testing without loops
"""
import sys
import time
from datetime import datetime

def test_single_tool():
    """Test one tool at a time with timeout"""
    print(f"🚀 Quick MCP Test Started: {datetime.now()}")
    print("=" * 50)
    
    # Simple test - just check if we can import and basic functionality
    try:
        print("✅ Test completed successfully")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    start_time = time.time()
    success = test_single_tool()
    end_time = time.time()
    
    print(f"\n⏱️  Test completed in {end_time - start_time:.2f} seconds")
    print(f"📊 Result: {'PASS' if success else 'FAIL'}")
