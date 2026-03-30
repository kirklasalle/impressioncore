#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\scripts\tools\ids_coordinator.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** ImpressionCore Team  
**Tags:** #docs\scripts\tools\ids_coordinator.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore IDS Integration & Status Script

A lightweight script that provides a unified interface to existing IDS tools
and creates necessary documentation for new environment setups.

This script complements the existing IDS automation without duplicating functionality.

Created: 2025-01-06
Author: ImpressionCore Development Team
IDS Tags: ids_integration, status_check, automation_coordinator, development_tools
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

class IDSIntegrationCoordinator:
    """Coordinates IDS tools and provides unified status interface."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.docs_dir = self.project_root / "docs"
        self.memlog_dir = self.project_root / "src" / "memlog"
        self.scripts_dir = self.docs_dir / "scripts" / "automation"
        
        # Define available IDS tools
        self.ids_tools = {
            "initializer": self.scripts_dir / "initialize_impressioncore_documentation_system.py",
            "maintenance": self.scripts_dir / "ids_maintenance_tool.py",
            "memlog_integration": self.scripts_dir / "ids_memlog_integration.py",
            "tag_manager": self.scripts_dir / "add_or_update_tags.py",
            "environment_docs": self.docs_dir / "scripts" / "tools" / "environment_documentation_generator.py"
        }
    
    def check_tool_availability(self) -> Dict[str, bool]:
        """Check which IDS tools are available."""
        availability = {}
        for tool_name, tool_path in self.ids_tools.items():
            availability[tool_name] = tool_path.exists()
        return availability
    
    def run_ids_status(self) -> Dict:
        """Get current IDS system status."""
        try:
            cmd = [sys.executable, str(self.ids_tools["maintenance"]), "--status"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                # Try to parse JSON output from the last line
                lines = result.stdout.strip().split('\n')
                for line in reversed(lines):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
            
            return {"error": "Could not get status", "output": result.stdout, "stderr": result.stderr}
            
        except Exception as e:
            return {"error": str(e)}
    
    def run_environment_documentation(self) -> bool:
        """Generate environment documentation using our tool."""
        try:
            if not self.ids_tools["environment_docs"].exists():
                print("❌ Environment documentation tool not found")
                return False
            
            cmd = [sys.executable, str(self.ids_tools["environment_docs"])]
            result = subprocess.run(cmd, cwd=self.project_root)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running environment documentation: {e}")
            return False
    
    def run_ids_maintenance(self) -> bool:
        """Run IDS maintenance to update tags and indices."""
        try:
            cmd = [sys.executable, str(self.ids_tools["maintenance"]), "--update"]
            result = subprocess.run(cmd, cwd=self.project_root)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running IDS maintenance: {e}")
            return False
    
    def integrate_memlog(self) -> bool:
        """Integrate memlog tags into IDS."""
        try:
            cmd = [sys.executable, str(self.ids_tools["memlog_integration"])]
            result = subprocess.run(cmd, cwd=self.project_root)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error integrating memlog: {e}")
            return False
    
    def display_status_summary(self):
        """Display comprehensive IDS status summary."""
        print("🔍 ImpressionCore IDS Integration & Status")
        print("=" * 50)
        
        # Check tool availability
        print("\n📋 Tool Availability:")
        availability = self.check_tool_availability()
        for tool_name, available in availability.items():
            status = "✅" if available else "❌"
            print(f"   {status} {tool_name}: {'Available' if available else 'Missing'}")
        
        # Get IDS status
        print("\n📊 System Status:")
        status = self.run_ids_status()
        
        if "error" not in status:
            print(f"   ✅ Documentation files: {status.get('documentation_files', 'N/A')}")
            print(f"   ✅ Memlog files: {status.get('memlog_files', 'N/A')}")
            print(f"   ✅ Source files: {status.get('source_files', 'N/A')}")
            print(f"   ✅ Total files: {status.get('total_files', 'N/A')}")
            print(f"   ✅ Total tags: {status.get('total_tags', 'N/A')}")
            print(f"   ✅ Documentation index: {'Exists' if status.get('doc_index_exists') else 'Missing'}")
            print(f"   ✅ Tags index: {'Exists' if status.get('tags_index_exists') else 'Missing'}")
        else:
            print(f"   ❌ Error getting status: {status.get('error')}")
        
        # Environment info
        print(f"\n🐍 Python Environment:")
        print(f"   ✅ Python: {sys.version.split()[0]}")
        print(f"   ✅ Virtual environment: {'Yes' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'No'}")
        
        print(f"\n📍 Project Root: {self.project_root}")
        print(f"📁 Documentation: {self.docs_dir}")
        print(f"📝 Memlog: {self.memlog_dir}")
    
    def run_full_initialization(self) -> bool:
        """Run complete IDS initialization and documentation."""
        print("🚀 Running Full IDS Initialization & Documentation")
        print("=" * 60)
        
        success = True
        
        # Step 1: Generate environment documentation
        print("\n1️⃣  Generating environment documentation...")
        if self.run_environment_documentation():
            print("   ✅ Environment documentation created")
        else:
            print("   ⚠️  Environment documentation failed (continuing)")
            success = False
        
        # Step 2: Run IDS maintenance
        print("\n2️⃣  Running IDS maintenance...")
        if self.run_ids_maintenance():
            print("   ✅ IDS maintenance completed")
        else:
            print("   ⚠️  IDS maintenance failed (continuing)")
            success = False
        
        # Step 3: Integrate memlog
        print("\n3️⃣  Integrating memlog tags...")
        if self.integrate_memlog():
            print("   ✅ Memlog integration completed")
        else:
            print("   ⚠️  Memlog integration failed (continuing)")
            success = False
        
        # Step 4: Final status
        print("\n4️⃣  Final status check...")
        self.display_status_summary()
        
        return success

def main():
    """Main entry point."""
    coordinator = IDSIntegrationCoordinator()
    
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        
        if action == "status":
            coordinator.display_status_summary()
        elif action == "init":
            success = coordinator.run_full_initialization()
            return 0 if success else 1
        elif action == "env-docs":
            success = coordinator.run_environment_documentation()
            return 0 if success else 1
        elif action == "maintenance":
            success = coordinator.run_ids_maintenance()
            return 0 if success else 1
        else:
            print(f"Unknown action: {action}")
            print("Available actions: status, init, env-docs, maintenance")
            return 1
    else:
        # Default: show status
        coordinator.display_status_summary()
        
        # Ask if user wants to run initialization
        print("\n❓ Would you like to run full IDS initialization? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes']:
                success = coordinator.run_full_initialization()
                return 0 if success else 1
        except KeyboardInterrupt:
            print("\n👋 Cancelled by user")
    
    return 0

if __name__ == "__main__":
    exit(main())
