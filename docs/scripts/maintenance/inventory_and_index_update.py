#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\maintenance\inventory_and_index_update.py #documentation #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\maintenance\inventory_and_index_update.py #documentation #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore Documentation System - Inventory & Index Update

Scans all documentation files, updates inventory counts, and regenerates 
the main documentation index with rich visual feedback.

Author: Kirk LaSalle <kirk@impressioncore.ai>
Project: ImpressionCore Documentation System  
License: MIT
"""

import os
import sys
from datetime import datetime
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
    
    def add_table_row(table, *args, **kwargs):
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

DOCS_ROOT = str(Path(__file__).parent.parent.parent)
CATEGORIES = ["user", "developer", "process", "reference", "archive", "assets", "styles"]


def scan_docs():
    """Scan all documentation directories and create file inventory."""
    print_info("📊 Starting documentation inventory scan...")
    
    # Define file extensions for different categories
    CATEGORY_EXTENSIONS = {
        "user": [".md"],
        "developer": [".md"], 
        "process": [".md"],
        "reference": [".md"],
        "archive": [".md"],
        "assets": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".ico"],
        "styles": [".css", ".scss", ".sass", ".less"]
    }
    
    doc_map = {}
    total_files = 0
    
    for category in CATEGORIES:
        cat_path = os.path.join(DOCS_ROOT, category)
        if os.path.isdir(cat_path):
            # Get appropriate extensions for this category
            extensions = CATEGORY_EXTENSIONS.get(category, [".md"])
            
            # Count files with appropriate extensions
            files = []
            for f in os.listdir(cat_path):
                if any(f.lower().endswith(ext) for ext in extensions):
                    files.append(f)
            
            doc_map[category] = files
            total_files += len(files)
            
            # Show appropriate file type description
            if category == "assets":
                file_type = "media files"
            elif category == "styles": 
                file_type = "style files"
            else:
                file_type = "documentation files"
                
            print_info(f"📁 {category.capitalize()}: {len(files)} {file_type}")
        else:
            doc_map[category] = []
            print_warning(f"⚠️  Directory not found: {category}")
    
    print_success(f"✅ Scan complete! Total: {total_files} files across all categories")
    return doc_map, total_files

def update_index(doc_map, total_files):
    """Update the main documentation index with current inventory."""
    print_info("📝 Updating documentation index...")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    index_path = os.path.join(DOCS_ROOT, "DOCUMENTATION_INDEX.md")
    
    try:
        with open(index_path, "w", encoding="utf-8") as idx:
            # Write header
            idx.write("# ImpressionCore Documentation Index\n\n")
            idx.write(f"**Last Updated:** {now}  \n")
            idx.write(f"**Total Documents:** {total_files}  \n")
            idx.write(f"**Categories:** {len([cat for cat in CATEGORIES if doc_map.get(cat)])}  \n\n")
            
            # Write table of contents
            idx.write("## Table of Contents\n\n")
            for category in CATEGORIES:
                if doc_map.get(category):
                    file_count = len(doc_map[category])
                    idx.write(f"- [{category.capitalize()}](#{category}) ({file_count} files)\n")
            idx.write("\n---\n\n")
              # Write detailed sections
            for category in CATEGORIES:
                files = doc_map.get(category, [])
                if files:
                    idx.write(f"## {category.capitalize()}\n\n")
                    
                    # Add category-specific description
                    if category == "assets":
                        idx.write(f"*{len(files)} media files in this category*\n\n")
                    elif category == "styles":
                        idx.write(f"*{len(files)} style files in this category*\n\n")
                    else:
                        idx.write(f"*{len(files)} documentation files in this category*\n\n")
                    
                    for f in sorted(files):
                        file_path = f"{category}/{f}"
                        
                        # Handle different file types for display names
                        if category in ["assets", "styles"]:
                            # For assets and styles, keep original filename but make it readable
                            display_name = f.replace('_', ' ').replace('-', ' ')
                        else:
                            # For markdown files, remove .md extension and format
                            display_name = f.replace('.md', '').replace('_', ' ').title()
                        
                        idx.write(f"- [{display_name}]({file_path})\n")
                    idx.write("\n")
        
        print_success(f"✅ Index updated successfully: {index_path}")
        return True
        
    except Exception as e:
        print_error(f"❌ Error updating index: {str(e)}")
        return False

def display_inventory_summary(doc_map, total_files):
    """Display a rich summary of the documentation inventory."""
    if HAS_RICH:
        # Create inventory table
        table = create_table(title="📊 Documentation Inventory Summary")
          # Add header
        try:
            add_table_row(table, "Category", "Files", "Status", header=True)
        except TypeError:
            # Fallback doesn't support header parameter
            add_table_row(table, "Category", "Files", "Status")
        
        for category in CATEGORIES:
            files = doc_map.get(category, [])
            file_count = len(files)
            
            if file_count > 0:
                status = "✅ Active"
                count_display = str(file_count)
            else:
                status = "📂 Empty"
                count_display = "0"
            
            add_table_row(table, category.capitalize(), count_display, status)
        
        # Add total row
        add_table_row(table, "TOTAL", str(total_files), f"📄 {total_files} files")
        
        display_table(table)
        
        # Summary panel
        summary_lines = [
            f"📊 Total Documentation Files: {total_files}",
            f"📁 Active Categories: {len([cat for cat in CATEGORIES if doc_map.get(cat)])}",
            f"📝 Index Location: docs/DOCUMENTATION_INDEX.md",
            f"🕒 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        panel = create_panel(
            "\n".join(summary_lines),
            "📋 Inventory Summary"
        )
        console.print(panel)
    else:
        # Fallback display
        print("\n--- Documentation Inventory Summary ---")
        for category in CATEGORIES:
            files = doc_map.get(category, [])
            print(f"{category.capitalize()}: {len(files)} files")
        print(f"TOTAL: {total_files} files")

def main():
    """Main inventory and index update execution."""
    logger = setup_rich_logging("inventory_update")
    
    print_info("🔄 Starting ImpressionCore Documentation Inventory Update")
    
    # Scan documentation
    doc_map, total_files = scan_docs()
    
    # Display inventory summary
    display_inventory_summary(doc_map, total_files)
    
    # Update index
    success = update_index(doc_map, total_files)
    
    if success:
        print_success("🎉 Documentation inventory and index update completed successfully!")
        return 0
    else:
        print_error("❌ Documentation update failed!")
        return 1

if __name__ == "__main__":
    exit(main())
