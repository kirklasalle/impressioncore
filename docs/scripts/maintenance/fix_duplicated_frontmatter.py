#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #docs\scripts\maintenance\fix_duplicated_frontmatter.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Fix Duplicated Frontmatter

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** Kirk LaSalle  
**Tags:** #docs\scripts\maintenance\fix_duplicated_frontmatter.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore Documentation Frontmatter Cleaner

This script cleans up and standardizes YAML frontmatter in Markdown files:
- Removes duplicate frontmatter blocks
- Fixes malformed frontmatter (# --- format)
- Ensures only one standard frontmatter block at the top of each file

Usage: python fix_duplicated_frontmatter.py [--all]

Author: Kirk LaSalle <kirk@impressioncore.ai>
Project: ImpressionCore Documentation System
License: MIT
"""
import os
import re
import argparse
import sys
from pathlib import Path
from datetime import datetime

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

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Regular expressions for finding different frontmatter formats
YAML_STANDARD = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL)
YAML_MALFORMED = re.compile(r'^#\s*---\s*\n(.*?)\n---', re.DOTALL)
ANY_FRONTMATTER = re.compile(r'(^(?:#\s*)?---\s*\n.*?\n---)', re.DOTALL | re.MULTILINE)

def find_all_markdown_files():
    """Get all markdown files in the docs directory"""
    md_files = []
    for root, _, files in os.walk(DOCS_DIR):
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
    return md_files

def extract_tags_from_content(content):
    """Extract tags from either standard or malformed frontmatter"""
    tags = []
    
    # Try standard format first
    match = YAML_STANDARD.search(content)
    if not match:
        # Try malformed format
        match = YAML_MALFORMED.search(content)
        
    if match:
        yaml_block = match.group(1)
        for line in yaml_block.splitlines():
            if line.strip().startswith('tags:'):
                tag_str = line.split(':', 1)[1].strip()
                tag_str = tag_str.strip('[]')
                tags = [t.strip().strip("'\"") for t in tag_str.split(',') if t.strip()]
                break
    
    return tags

def has_duplicate_frontmatter(content):
    """Check if content has multiple frontmatter blocks"""
    return len(re.findall(r'(?:#\s*)?---\s*\n.*?\n---', content, re.DOTALL)) > 1

def clean_frontmatter(file_path):
    """Clean up and standardize frontmatter in a markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if there are multiple frontmatter blocks
    multiple_blocks = has_duplicate_frontmatter(content)
    
    # Extract tags from existing frontmatter
    tags = extract_tags_from_content(content)
    
    if not tags:
        print_warning(f"No tags found in {file_path}")
        return False
    
    # Remove all frontmatter blocks
    content_without_frontmatter = ANY_FRONTMATTER.sub('', content).lstrip()
    
    # Create new standardized frontmatter
    tag_str = ', '.join(tags)
    new_frontmatter = f"---\ntags: [{tag_str}]\n---\n\n"
    
    # Assemble the new content
    new_content = new_frontmatter + content_without_frontmatter
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return multiple_blocks

def main():
    """Main execution function with enhanced interface."""
    parser = argparse.ArgumentParser(description="Fix duplicated or malformed YAML frontmatter in Markdown files")
    parser.add_argument('--all', action='store_true', help='Process all MD files, not just those with duplicate frontmatter')
    args = parser.parse_args()
    
    # Display header
    if HAS_RICH:
        console.print(create_panel(
            "ImpressionCore Documentation System\nFrontmatter Cleaner & Standardizer",
            title="📝 IDS Maintenance Tool"
        ))
    else:
        print("=== ImpressionCore Documentation System ===")
        print("=== Frontmatter Cleaner & Standardizer ===")
    
    # Find all markdown files
    md_files = find_all_markdown_files()
    print_info(f"🔍 Found {len(md_files)} Markdown files to analyze")
    
    if not md_files:
        print_warning("⚠️  No Markdown files found to process")
        return 0
    
    fixed_files = 0
    processed_files = 0
    issues_found = []
    
    # Create progress tracker if available
    if HAS_RICH:
        progress = create_progress()
        if progress:
            task = progress.add_task("[cyan]Processing files...", total=len(md_files))
    
    # Process each file
    for i, md_file in enumerate(md_files):
        relative_path = os.path.relpath(md_file, DOCS_DIR)
        
        # Update progress if available
        if HAS_RICH and 'progress' in locals() and progress:
            progress.update(task, advance=1, description=f"Processing {os.path.basename(md_file)}")
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if this file needs processing
            has_issues = has_duplicate_frontmatter(content)
            if args.all or has_issues:
                was_fixed = clean_frontmatter(md_file)
                processed_files += 1
                
                if was_fixed:
                    fixed_files += 1
                    issues_found.append((relative_path, "Duplicate frontmatter removed"))
                    print_success(f"✅ Fixed duplicate frontmatter in {relative_path}")
                else:
                    print_info(f"📝 Standardized frontmatter in {relative_path}")
            
        except Exception as e:
            print_error(f"❌ Error processing {relative_path}: {e}")
            issues_found.append((relative_path, f"Error: {e}"))
    
    # Close progress if it was created
    if HAS_RICH and 'progress' in locals() and progress:
        progress.stop()
    
    # Display results
    print_info(f"\n📊 Processing completed:")
    print_info(f"   • Total files analyzed: {len(md_files)}")
    print_info(f"   • Files processed: {processed_files}")
    print_success(f"   • Files fixed: {fixed_files}")
    
    # Create detailed summary table
    if HAS_RICH and (fixed_files > 0 or issues_found):
        summary_table = create_table("File", "Action Taken")
        
        for file_path, action in issues_found:
            add_table_row(summary_table, file_path, action)
        
        console.print("\n")
        console.print(create_panel("Processing Results", title="📋 Detailed Report"))
        display_table(summary_table)
    
    # Final summary
    if fixed_files > 0:
        print_success(f"\n🎉 Successfully fixed {fixed_files} files with frontmatter issues!")
    else:
        print_info("\n✅ No frontmatter issues found - all files are properly formatted")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
