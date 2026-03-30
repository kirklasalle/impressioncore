
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #docs\scripts\maintenance\health_check_and_notification.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Deprecated
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** Kirk LaSalle  
**Tags:** #docs\scripts\maintenance\health_check_and_notification.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Deprecated

"""
ImpressionCore Documentation System - Health Check & Notification

Monitors documentation health by checking modification dates, deprecation notices,
and flagging files that need review. Provides rich visual feedback and notifications.

Author: Kirk LaSalle <kirk@impressioncore.ai>
Project: ImpressionCore Documentation System
License: MIT
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.core.utils.rich_enhancements import (
        console, print_info, print_success, print_warning, print_error,
        create_table, add_table_row, display_table, create_panel, create_progress
    )
    from src.core.utils.rich_logging import setup_rich_logging
    HAS_RICH = True
    
    # Try to import StatusAnimation separately as it might not be available
    try:
        from src.core.utils.rich_status_animation import StatusAnimation
        HAS_STATUS_ANIMATION = True
    except ImportError:
        HAS_STATUS_ANIMATION = False
        class StatusAnimation:
            def __init__(self, message="Working...", *args, **kwargs):
                self.message = message
            def __enter__(self):
                print(f"Starting: {self.message}")
                return self
            def __exit__(self, *args):
                pass
            def update(self, text):
                print(f"Status: {text}")
        
except ImportError:
    # Fallback without rich enhancements
    import logging
    logging.basicConfig(level=logging.INFO)
    HAS_RICH = False
    
    class SimpleConsole:
        @staticmethod
        def print(text, style=None):
            print(text)
    
    console = SimpleConsole()
    print_info = print_success = print_warning = print_error = print
    
    def create_table(*args, **kwargs):
        return {'columns': [], 'rows': []}
    
    def add_table_row(table, *args):
        if isinstance(table, dict) and 'rows' in table:
            table['rows'].append(args)
    
    def display_table(table):
        if isinstance(table, dict) and 'rows' in table:
            for row in table['rows']:
                print('\t'.join(str(cell) for cell in row))
    
    def create_panel(text, title=""):
        return f"\n--- {title} ---\n{text}\n"
    
    def create_progress(*args, **kwargs):
        return None
    
    def setup_rich_logging(*args, **kwargs):
        import logging
        return logging.getLogger(__name__)
    
    class StatusAnimation:
        def __init__(self, message="Working...", *args, **kwargs):
            self.message = message
        def __enter__(self):
            print(f"Starting: {self.message}")
            return self
        def __exit__(self, *args):
            pass
        def update(self, text):
            print(f"Status: {text}")

DOCS_ROOT = str(Path(__file__).parent.parent)
CATEGORIES = ["user", "developer", "process", "reference", "archive", "assets", "styles"]
REVIEW_DAYS = 90

def scan_docs():
    """Scan all documentation files and return their paths."""
    doc_paths = []
    
    print("Starting: Scanning documentation files...")
    for category in CATEGORIES:
        print(f"Status: Scanning {category} directory...")
        cat_path = os.path.join(DOCS_ROOT, category)
        if os.path.isdir(cat_path):
            for f in os.listdir(cat_path):
                if f.endswith(".md"):
                    doc_paths.append(os.path.join(cat_path, f))
    
    print_info(f"Found {len(doc_paths)} documentation files")
    return doc_paths

def check_health(doc_paths):
    """Check health status of documentation files."""
    now = datetime.now()
    flagged = []
    
    print("Starting: Checking documentation health...")
    for i, path in enumerate(doc_paths, 1):
        print(f"Status: Checking file {i}/{len(doc_paths)}: {os.path.basename(path)}")
        
        # Check modification date
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        if (now - mtime) > timedelta(days=REVIEW_DAYS):
            flagged.append({
                'path': path,
                'issue': 'Needs Review',
                'details': f"Last modified: {mtime.strftime('%Y-%m-%d')} ({(now - mtime).days} days ago)",
                'priority': 'Medium'
            })
        
        # Check archive deprecation notices
        if "archive" in path:
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                    if "> Deprecated and moved to archive" not in content:
                        flagged.append({
                            'path': path,
                            'issue': 'Missing Deprecation Notice',
                            'details': 'Archive file lacks deprecation notice',
                            'priority': 'High'
                        })
            except Exception as e:
                flagged.append({
                    'path': path,
                    'issue': 'Read Error',
                    'details': f"Could not read file: {str(e)}",
                    'priority': 'High'
                })
    
    return flagged

def display_health_report(flagged_files):
    """Display a comprehensive health report."""
    if not flagged_files:
        print_success("🎉 All documentation is healthy! No issues found.")
        return
      # Categorize issues by priority
    high_priority = [f for f in flagged_files if f['priority'] == 'High']
    medium_priority = [f for f in flagged_files if f['priority'] == 'Medium']
    
    print_warning(f"⚠️  Found {len(flagged_files)} issues in documentation")
    
    if HAS_RICH:
        # Create detailed table using ImpressionCore standardized methods
        table = create_table(title="📊 Documentation Health Report")
        
        # Add header row
        add_table_row(table, "File", "Issue", "Details", "Priority", header=True)
        
        for file_info in flagged_files:
            relative_path = os.path.relpath(file_info['path'], DOCS_ROOT)
            priority_emoji = "🔴" if file_info['priority'] == 'High' else "🟡"
            add_table_row(table,
                relative_path,
                file_info['issue'],
                file_info['details'],
                f"{priority_emoji} {file_info['priority']}"
            )
        
        display_table(table)
        
        # Summary panel
        summary_lines = [
            f"🔴 High Priority Issues: {len(high_priority)}",
            f"🟡 Medium Priority Issues: {len(medium_priority)}",
            f"📁 Total Files Checked: {len(flagged_files) + sum(1 for _ in scan_docs()) - len(flagged_files)}",
            f"⏰ Review Threshold: {REVIEW_DAYS} days"
        ]
        
        panel = create_panel(
            "\n".join(summary_lines),
            "📋 Health Summary"
        )
        console.print(panel)
    else:
        # Fallback display
        print("\n--- Documentation Health Report ---")
        for file_info in flagged_files:
            relative_path = os.path.relpath(file_info['path'], DOCS_ROOT)
            print(f"- {relative_path}")
            print(f"  Issue: {file_info['issue']}")
            print(f"  Details: {file_info['details']}")
            print(f"  Priority: {file_info['priority']}")
            print()

def main():
    """Main health check execution."""
    logger = setup_rich_logging("health_check")
    
    print_info("🏥 Starting ImpressionCore Documentation Health Check")
    
    # Scan and check documentation
    doc_paths = scan_docs()
    flagged = check_health(doc_paths)
    
    # Display results
    display_health_report(flagged)
    
    # Return exit code based on results
    if any(f['priority'] == 'High' for f in flagged):
        print_error("❌ Critical issues found! Please address high priority items.")
        return 1
    elif flagged:
        print_warning("⚠️  Some issues found, but no critical problems.")
        return 2
    else:
        print_success("✅ Documentation health check passed!")
        return 0

if __name__ == "__main__":
    exit(main())
