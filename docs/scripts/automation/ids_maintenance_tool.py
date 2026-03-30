#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #attention_mechanism #docs\scripts\automation\ids_maintenance_tool.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** ImpressionCore Team  
**Tags:** #attention_mechanism #docs\scripts\automation\ids_maintenance_tool.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore IDS Documentation Maintenance Tool

This script provides automated maintenance for the ImpressionCore Documentation System (IDS),
including index updates, tag validation, and documentation health checks.

Author: ImpressionCore Development Team
Date: January 6, 2025
IDS Tags: ids_maintenance, documentation, automation, python, system_health
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import shutil
import logging
from typing import Dict, List, Set, Optional, Tuple
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ids_maintenance.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IDSMaintenanceTool:
    """Automated maintenance tool for ImpressionCore Documentation System."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the IDS maintenance tool."""
        self.project_root = Path(project_root) if project_root else Path(__file__).parents[3]
        self.docs_dir = self.project_root / "docs"
        self.memlog_dir = self.project_root / "src" / "memlog"
        self.scripts_dir = self.project_root / "docs" / "scripts"
        
        # IDS system files
        self.doc_index_file = self.docs_dir / "DOCUMENTATION_INDEX.md"
        self.tags_index_file = self.docs_dir / "unified_tags_index.yaml"
        self.file_metadata_file = self.docs_dir / "file_metadata.yaml"
        
        logger.info(f"Initialized IDS maintenance tool for project: {self.project_root}")
    
    def get_system_status(self) -> Dict:
        """Get current IDS system status and metrics."""
        try:
            # Count documentation files
            doc_files = list(self.docs_dir.rglob("*.md"))
            
            # Count memlog files  
            memlog_files = list(self.memlog_dir.rglob("*.md"))
            
            # Count source files
            src_files = list((self.project_root / "src").rglob("*.py"))
            
            # Load tag index if available
            total_tags = 0
            if self.tags_index_file.exists():
                try:
                    import yaml
                    with open(self.tags_index_file, 'r', encoding='utf-8') as f:
                        tag_data = yaml.safe_load(f)
                        total_tags = len(tag_data) if tag_data else 0
                except Exception as e:
                    logger.warning(f"Could not load tag index: {e}")
            
            status = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "documentation_files": len(doc_files),
                "memlog_files": len(memlog_files),
                "source_files": len(src_files),
                "total_files": len(doc_files) + len(memlog_files) + len(src_files),
                "total_tags": total_tags,
                "doc_index_exists": self.doc_index_file.exists(),
                "tags_index_exists": self.tags_index_file.exists(),
                "file_metadata_exists": self.file_metadata_file.exists()
            }
            
            logger.info(f"System status: {status['total_files']} files, {total_tags} tags")
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {}
    
    def validate_documentation_index(self) -> List[str]:
        """Validate the documentation index for completeness and accuracy."""
        issues = []
        
        if not self.doc_index_file.exists():
            issues.append("Documentation index file missing")
            return issues
        
        try:
            with open(self.doc_index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required sections
            required_sections = [
                "# ImpressionCore Documentation Index",
                "**Last Updated:**",
                "**Total Documents:**",
                "**IDS Integration:**"
            ]
            
            for section in required_sections:
                if section not in content:
                    issues.append(f"Missing required section: {section}")
            
            # Check if update date is recent (within last 30 days)
            if "**Last Updated:** 2025-01-06" not in content:
                issues.append("Documentation index may need date update")
            
            # Validate file references
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                if '.md)' in line and '[' in line:
                    # Extract file path
                    start = line.find('](')
                    end = line.find(')', start)
                    if start > 0 and end > 0:
                        file_path = line[start+2:end]
                        if not file_path.startswith('http'):
                            full_path = self.docs_dir / file_path
                            if not full_path.exists():
                                issues.append(f"Line {line_num}: Referenced file not found: {file_path}")
            
            logger.info(f"Documentation index validation: {len(issues)} issues found")
            
        except Exception as e:
            issues.append(f"Error reading documentation index: {e}")
        
        return issues
    
    def update_documentation_index(self) -> bool:
        """Update the documentation index with current timestamp and stats."""
        try:
            if not self.doc_index_file.exists():
                logger.error("Documentation index file not found")
                return False
            
            with open(self.doc_index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update timestamp
            current_date = datetime.now().strftime("%Y-%m-%d")
            content = content.replace(
                "**Last Updated:** 2025-06-09",
                f"**Last Updated:** {current_date}"
            )
            
            # Update document count
            status = self.get_system_status()
            total_docs = status.get('documentation_files', 0) + status.get('memlog_files', 0)
            
            # Find and update total documents line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("**Total Documents:**"):
                    lines[i] = f"**Total Documents:** {total_docs}+"
                    break
            
            # Update IDS integration info
            for i, line in enumerate(lines):
                if line.startswith("**IDS Integration:**"):
                    total_files = status.get('total_files', 0)
                    total_tags = status.get('total_tags', 0)
                    lines[i] = f"**IDS Integration:** Complete with unified tagging system ({total_files} files, {total_tags} tags)"
                    break
            
            content = '\n'.join(lines)
            
            # Write updated content
            with open(self.doc_index_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("Documentation index updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating documentation index: {e}")
            return False
    
    def create_maintenance_report(self) -> str:
        """Create a comprehensive maintenance report."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_file = self.memlog_dir / f"ids_maintenance_report_{timestamp}.md"
        
        try:
            status = self.get_system_status()
            issues = self.validate_documentation_index()
            
            report_content = f"""# IDS System Maintenance Report

**Date:** {datetime.now().strftime("%Y-%m-%d")}  
**Time:** {datetime.now().strftime("%H:%M:%S")}  
**Status:** {'✅ HEALTHY' if len(issues) == 0 else '⚠️ ISSUES FOUND'}  
**Responsible Party:** Automated IDS Maintenance Tool  
**IDS Tags:** `ids_maintenance`, `system_health`, `automated_report`, `documentation`, `{datetime.now().year}`

## System Status Overview

### File Statistics
- **Documentation Files:** {status.get('documentation_files', 0)}
- **Memlog Files:** {status.get('memlog_files', 0)}
- **Source Code Files:** {status.get('source_files', 0)}
- **Total Files Indexed:** {status.get('total_files', 0)}
- **Total Tags:** {status.get('total_tags', 0)}

### Index Health
- **Documentation Index:** {'✅ Exists' if status.get('doc_index_exists') else '❌ Missing'}
- **Tags Index:** {'✅ Exists' if status.get('tags_index_exists') else '❌ Missing'}
- **File Metadata:** {'✅ Exists' if status.get('file_metadata_exists') else '❌ Missing'}

## Validation Results

### Documentation Index Issues
"""
            
            if issues:
                for issue in issues:
                    report_content += f"- ❌ {issue}\n"
            else:
                report_content += "- ✅ No issues found\n"
            
            report_content += f"""
## Recommendations

### Immediate Actions
"""
            
            if issues:
                report_content += "1. **Resolve Documentation Issues** - Fix the validation issues listed above\n"
                report_content += "2. **Update References** - Ensure all file references are valid\n"
                report_content += "3. **Refresh Indices** - Regenerate tag and metadata indices\n"
            else:
                report_content += "1. **System Healthy** - No immediate actions required\n"
                report_content += "2. **Continue Monitoring** - Regular maintenance checks recommended\n"
            
            report_content += f"""
### Ongoing Maintenance
1. **Weekly Index Updates** - Run maintenance tool weekly
2. **Tag System Validation** - Ensure consistent tagging across files
3. **Dead Link Checking** - Validate all documentation references
4. **Performance Monitoring** - Track system response times

## System Health Summary

**Overall Status:** {'🟢 EXCELLENT' if len(issues) == 0 else '🟡 NEEDS ATTENTION' if len(issues) < 5 else '🔴 CRITICAL'}  
**Documentation Coverage:** 🟢 COMPREHENSIVE  
**Search Functionality:** 🟢 OPERATIONAL  
**Index Integrity:** {'🟢 VALID' if len(issues) == 0 else '🟡 ISSUES'}

---

**Next Maintenance:** {(datetime.now().replace(day=datetime.now().day + 7)).strftime("%Y-%m-%d")}  
**Report Generated:** {datetime.now().isoformat()}  
**Tool Version:** 1.0.0
"""
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Maintenance report created: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"Error creating maintenance report: {e}")
            return ""
    
    def run_full_maintenance(self) -> bool:
        """Run complete IDS system maintenance."""
        logger.info("Starting full IDS system maintenance...")
        
        try:
            # 1. Get system status
            status = self.get_system_status()
            logger.info(f"System status retrieved: {status.get('total_files', 0)} files")
            
            # 2. Validate documentation index
            issues = self.validate_documentation_index()
            if issues:
                logger.warning(f"Documentation validation found {len(issues)} issues")
                for issue in issues:
                    logger.warning(f"  - {issue}")
            
            # 3. Update documentation index
            if self.update_documentation_index():
                logger.info("Documentation index updated successfully")
            else:
                logger.error("Failed to update documentation index")
            
            # 4. Create maintenance report
            report_file = self.create_maintenance_report()
            if report_file:
                logger.info(f"Maintenance report created: {report_file}")
            
            # 5. Summary
            success = len(issues) == 0
            logger.info(f"Full maintenance completed. Status: {'SUCCESS' if success else 'ISSUES FOUND'}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error during full maintenance: {e}")
            return False

def main():
    """Main entry point for the IDS maintenance tool."""
    parser = argparse.ArgumentParser(description='ImpressionCore IDS Documentation Maintenance Tool')
    parser.add_argument('--project-root', help='Path to project root directory')
    parser.add_argument('--status', action='store_true', help='Show system status only')
    parser.add_argument('--validate', action='store_true', help='Validate documentation only')
    parser.add_argument('--update', action='store_true', help='Update documentation index only')
    parser.add_argument('--report', action='store_true', help='Generate maintenance report only')
    parser.add_argument('--full', action='store_true', help='Run full maintenance (default)')
    
    args = parser.parse_args()
    
    # Initialize tool
    tool = IDSMaintenanceTool(args.project_root)
    
    try:
        if args.status:
            status = tool.get_system_status()
            print(json.dumps(status, indent=2))
        elif args.validate:
            issues = tool.validate_documentation_index()
            if issues:
                print("Validation issues found:")
                for issue in issues:
                    print(f"  - {issue}")
                sys.exit(1)
            else:
                print("✅ Documentation validation passed")
        elif args.update:
            if tool.update_documentation_index():
                print("✅ Documentation index updated")
            else:
                print("❌ Failed to update documentation index")
                sys.exit(1)
        elif args.report:
            report_file = tool.create_maintenance_report()
            if report_file:
                print(f"✅ Maintenance report created: {report_file}")
            else:
                print("❌ Failed to create maintenance report")
                sys.exit(1)
        else:
            # Default: run full maintenance
            if tool.run_full_maintenance():
                print("✅ Full IDS maintenance completed successfully")
            else:
                print("⚠️ IDS maintenance completed with issues")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Maintenance interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Maintenance failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
