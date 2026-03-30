
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\maintenance\redundancy_and_deprecation_checker.py #documentation #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Deprecated
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\maintenance\redundancy_and_deprecation_checker.py #documentation #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Deprecated

"""
ImpressionCore Documentation System - Redundancy & Deprecation Checker

Scans documentation for duplicate files, redundant content, and manages
deprecation workflow with rich visual feedback and safe archiving.

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

# File extensions by category for comprehensive scanning
CATEGORY_EXTENSIONS = {
    "user": [".md"],
    "developer": [".md"],
    "process": [".md"],
    "reference": [".md"],
    "archive": [".md"],
    "assets": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".ico"],
    "styles": [".css", ".scss", ".sass", ".less"]
}


def scan_docs():
    """Scan all documentation directories for analysis with comprehensive file type support."""
    print_info("🔍 Scanning documentation for redundancy analysis...")
    
    doc_map = {}
    total_files = 0
    
    # Create progress tracker if available
    if HAS_RICH:
        progress = create_progress()
        if progress:
            task = progress.add_task("[cyan]Scanning directories...", total=len(CATEGORIES))
    
    for category in CATEGORIES:
        cat_path = os.path.join(DOCS_ROOT, category)
        if os.path.isdir(cat_path):
            # Get allowed extensions for this category
            extensions = CATEGORY_EXTENSIONS.get(category, [".md"])
            
            # Scan for files with allowed extensions
            files = []
            for file in os.listdir(cat_path):
                if any(file.lower().endswith(ext) for ext in extensions):
                    files.append(file)
            
            doc_map[category] = files
            total_files += len(files)
            
            # Rich status update
            if len(files) > 0:
                print_info(f"📁 {category.capitalize()}: {len(files)} files")
            else:
                print_warning(f"📂 {category.capitalize()}: empty directory")
        else:
            doc_map[category] = []
            print_warning(f"❌ {category.capitalize()}: directory not found")
        
        # Update progress if available
        if HAS_RICH and 'progress' in locals() and progress:
            progress.update(task, advance=1)
    
    # Close progress if it was created
    if HAS_RICH and 'progress' in locals() and progress:
        progress.stop()
    
    print_success(f"✅ Scanned {total_files} files across {len(CATEGORIES)} categories")
    return doc_map, total_files


def find_duplicates(doc_map):
    """Find duplicate files across categories with enhanced reporting."""
    print_info("🔍 Analyzing for duplicate files...")
    
    seen = {}
    duplicates = []
    
    for category, files in doc_map.items():
        for f in files:
            if f in seen:
                duplicates.append((f, seen[f], category))
                print_warning(f"⚠️  Duplicate found: '{f}' in both '{seen[f]}' and '{category}'")
            else:
                seen[f] = category
    
    if duplicates:
        print_error(f"❌ Found {len(duplicates)} duplicate files")
        
        # Create a beautiful table for duplicates
        if HAS_RICH:
            table = create_table("File Name", "Original Location", "Duplicate Location")
            for filename, original, duplicate in duplicates:
                add_table_row(table, filename, original, duplicate)
            
            console.print("\n")
            console.print(create_panel("Duplicate Files Found", title="🚨 Redundancy Report"))
            display_table(table)
        else:
            print("\nDuplicate Files:")
            for filename, original, duplicate in duplicates:
                print(f"  {filename}: {original} -> {duplicate}")
    else:
        print_success("✅ No duplicate files found")
    
    return duplicates


def find_content_similarities(doc_map):
    """Find files with similar content (basic implementation)."""
    print_info("🔍 Checking for content similarities...")
    
    similar_files = []
    content_cache = {}
    
    # Read and compare markdown files only
    for category in ["user", "developer", "process", "reference"]:
        if category not in doc_map:
            continue
            
        for filename in doc_map[category]:
            if not filename.endswith('.md'):
                continue
                
            filepath = os.path.join(DOCS_ROOT, category, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                # Simple similarity check based on content length and first 100 chars
                content_key = (len(content), content[:100] if content else "")
                
                if content_key in content_cache and content_key[0] > 50:  # Only for non-trivial files
                    similar_files.append((
                        filename, category,
                        content_cache[content_key][0], content_cache[content_key][1]
                    ))
                else:
                    content_cache[content_key] = (filename, category)
                    
            except Exception as e:
                print_warning(f"⚠️  Could not read {filepath}: {e}")
    
    if similar_files:
        print_warning(f"⚠️  Found {len(similar_files)} potentially similar files")
        
        if HAS_RICH:
            table = create_table("File 1", "Location 1", "File 2", "Location 2")
            for file1, loc1, file2, loc2 in similar_files:
                add_table_row(table, file1, loc1, file2, loc2)
            
            console.print("\n")
            console.print(create_panel("Files with Similar Content", title="🔍 Content Analysis"))
            display_table(table)
    else:
        print_success("✅ No obviously similar content found")
    
    return similar_files


def move_to_archive(duplicates):
    """Move duplicate files to archive with proper documentation."""
    if not duplicates:
        return
    
    print_info(f"📦 Moving {len(duplicates)} duplicate files to archive...")
    
    archive_dir = os.path.join(DOCS_ROOT, "archive")
    os.makedirs(archive_dir, exist_ok=True)
    
    moved_count = 0
    
    for filename, original_cat, duplicate_cat in duplicates:
        src = os.path.join(DOCS_ROOT, duplicate_cat, filename)
        dst = os.path.join(DOCS_ROOT, "archive", filename)
        
        if os.path.exists(src):
            try:
                # Handle naming conflicts in archive
                counter = 1
                base_dst = dst
                while os.path.exists(dst):
                    name, ext = os.path.splitext(base_dst)
                    dst = f"{name}_duplicate_{counter}{ext}"
                    counter += 1
                
                # Move the file
                os.rename(src, dst)
                
                # Add deprecation notice
                with open(dst, "a", encoding="utf-8") as file:
                    file.write(f"\n\n---\n")
                    file.write(f"> **DEPRECATED**: This file was automatically moved to archive on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
                    file.write(f"> **REASON**: Duplicate of file in '{original_cat}' category\n")
                    file.write(f"> **ORIGINAL LOCATION**: {duplicate_cat}/{filename}\n")
                    file.write(f"---\n")
                
                moved_count += 1
                print_success(f"✅ Moved: {duplicate_cat}/{filename} → archive/{os.path.basename(dst)}")
                
            except Exception as e:
                print_error(f"❌ Failed to move {src}: {e}")
        else:
            print_warning(f"⚠️  File not found: {src}")
    
    if moved_count > 0:
        print_success(f"📦 Successfully archived {moved_count} duplicate files")
    else:
        print_error("❌ No files were moved to archive")


def generate_summary(doc_map, total_files, duplicates, similar_files):
    """Generate a comprehensive summary report."""
    print_info("\n📊 Generating redundancy analysis summary...")
    
    if HAS_RICH:
        # Create summary table
        summary_table = create_table("Category", "Files Found", "Status")
        
        for category in CATEGORIES:
            count = len(doc_map.get(category, []))
            status = "✅ Active" if count > 0 else "📂 Empty"
            add_table_row(summary_table, category.capitalize(), str(count), status)
        
        # Add totals row
        add_table_row(summary_table, "**TOTAL**", str(total_files), "📚 Files")
        
        # Display summary
        console.print("\n")
        console.print(create_panel(
            f"Total Files: {total_files}\n"
            f"Duplicates Found: {len(duplicates)}\n"
            f"Similar Content: {len(similar_files)}\n"
            f"Categories Scanned: {len(CATEGORIES)}",
            title="📊 Redundancy Analysis Summary"
        ))
        console.print("\n")
        display_table(summary_table)
    
    else:
        print(f"\n--- REDUNDANCY ANALYSIS SUMMARY ---")
        print(f"Total Files: {total_files}")
        print(f"Duplicates Found: {len(duplicates)}")
        print(f"Similar Content: {len(similar_files)}")
        print(f"Categories Scanned: {len(CATEGORIES)}")


def main():
    """Main execution function with comprehensive workflow."""
    if HAS_RICH:
        console.print(create_panel(
            "ImpressionCore Documentation System\nRedundancy & Deprecation Checker",
            title="🔍 IDS Maintenance Tool"
        ))
    else:
        print("=== ImpressionCore Documentation System ===")
        print("=== Redundancy & Deprecation Checker ===")
    
    try:
        # Step 1: Scan documentation
        doc_map, total_files = scan_docs()
        
        # Step 2: Find duplicates
        duplicates = find_duplicates(doc_map)
        
        # Step 3: Find similar content
        similar_files = find_content_similarities(doc_map)
        
        # Step 4: Handle duplicates if found
        if duplicates:
            print_warning("\n⚠️  Duplicate files detected!")
            response = input("Move duplicates to archive? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                move_to_archive(duplicates)
            else:
                print_info("ℹ️  Skipping archive operation")
        
        # Step 5: Generate summary
        generate_summary(doc_map, total_files, duplicates, similar_files)
        
        print_success("\n✅ Redundancy analysis completed successfully!")
        
    except Exception as e:
        print_error(f"❌ Error during analysis: {e}")
        if HAS_RICH:
            console.print_exception()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
