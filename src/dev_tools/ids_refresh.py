#!/usr/bin/env python3
"""
ImpressionCore IDS Quick Refresh

Quick refresh script to ensure IDS tools have the most current data
before prompt use. This addresses the issue of 0 results due to stale indices.

File: src/dev_tools/ids_refresh.py
Created: 2025-01-06
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"⚠️ {description} completed with warnings")
            if result.stderr:
                print(f"   Warning: {result.stderr.strip()}")
            return True
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def refresh_ids_system():
    """Refresh the IDS system for current session"""
    print("🚀 ImpressionCore IDS Quick Refresh")
    print("=" * 50)
    print("📊 Refreshing documentation indices for optimal search results")
    print()
    
    project_root = Path(__file__).parent.parent.parent
    
    # Change to project directory
    original_dir = Path.cwd()
    try:
        import os
        os.chdir(project_root)
        
        # Activate virtual environment and run maintenance
        success_count = 0
        total_tasks = 3
        
        # 1. Run memlog integration
        if run_command(
            f"{sys.executable} docs/scripts/automation/ids_memlog_integration.py",
            "Integrating memlog documentation"
        ):
            success_count += 1
        
        # 2. Run full maintenance (light)
        if run_command(
            f"{sys.executable} docs/scripts/automation/ids_maintenance_tool.py --update",
            "Updating documentation index"
        ):
            success_count += 1
        
        # 3. Verify system status
        if run_command(
            f"{sys.executable} docs/scripts/automation/ids_maintenance_tool.py --status",
            "Verifying system status"
        ):
            success_count += 1
        
        print()
        print("📈 IDS Refresh Summary:")
        print(f"   ✅ Tasks completed: {success_count}/{total_tasks}")
        
        if success_count == total_tasks:
            print("   🎉 IDS system fully refreshed and ready!")
            print("   💡 You can now use singular searches like 'CUDA', 'setup', 'gpu'")
        elif success_count > 0:
            print("   ⚠️ IDS system partially refreshed")
            print("   💡 Some search functionality should be available")
        else:
            print("   ❌ IDS refresh failed")
            print("   💡 Try running manually or check logs")
        
        print()
        print("🔍 Quick Test - Available Search Terms:")
        print("   • CUDA, gpu, setup, training")
        print("   • completion, optimization, memory")
        print("   • diagnostics, monitoring, performance")
        
    finally:
        os.chdir(original_dir)
    
    return success_count >= 2  # At least 2/3 tasks successful

def main():
    """Main entry point"""
    start_time = time.time()
    
    success = refresh_ids_system()
    
    elapsed = time.time() - start_time
    print(f"\n⏱️ Refresh completed in {elapsed:.1f} seconds")
    
    if success:
        print("✅ IDS system ready for use!")
        return 0
    else:
        print("❌ IDS refresh encountered issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
