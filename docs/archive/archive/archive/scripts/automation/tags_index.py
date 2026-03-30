
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #command_line #docs\scripts\automation\tags_index.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Tags Index

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** ImpressionCore Team  
**Tags:** #command_line #docs\scripts\automation\tags_index.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active

import os
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.core.utils.rich_enhancements import (
        console, print_info, print_success, print_warning, print_error,
        create_table, add_table_row, display_table
    )
    from src.core.utils.rich_logging import setup_rich_logging
    HAS_RICH = True
    logger = setup_rich_logging(__name__)
except ImportError:
    # Fallback if rich utils not available
    class SimpleConsole:
        @staticmethod
        def print(text, style=None):
            print(text)
    
    console = SimpleConsole()
    print_info = print_success = print_warning = print_error = print
    
    def create_table(*args, **kwargs):
        return []
    
    def add_table_row(table, *args):
        pass
    
    def display_table(table):
        pass
    
    HAS_RICH = False
    logger = print

# Regex for YAML frontmatter and in-body tags/hashtags/headings
yaml_frontmatter = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL | re.MULTILINE)
hashtag_pattern = re.compile(r'#([a-zA-Z0-9_-]+)')
heading_pattern = re.compile(r'^#+\s+([A-Za-z0-9 _-]+)', re.MULTILINE)
CATEGORIES = ["user", "developer", "process", "reference", "archive"]
DOCS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def extract_all_tags(md_path):
    tags = set()
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 1. YAML frontmatter
    yaml_match = yaml_frontmatter.search(content)
    if yaml_match:
        for line in yaml_match.group(1).splitlines():
            if line.strip().startswith('tags:'):
                tag_str = line.split(':', 1)[1].strip().strip('[]')
                tags.update(t.strip().strip("'\"") for t in tag_str.split(',') if t.strip())
    # 2. Hashtags in body
    tags.update(hashtag_pattern.findall(content))
    # 3. Headings as tags (optional, only if short)
    for heading in heading_pattern.findall(content):
        heading_tag = heading.strip().lower().replace(' ', '_')
        if 2 <= len(heading_tag) <= 32:
            tags.add(heading_tag)
    return sorted(tags)


def build_tag_index():
    tag_index = {}
    for category in CATEGORIES:
        dir_path = os.path.join(DOCS_ROOT, category)
        if not os.path.isdir(dir_path):
            continue
        for fname in os.listdir(dir_path):
            if not fname.endswith('.md'):
                continue
            md_path = os.path.join(dir_path, fname)
            tags = extract_all_tags(md_path)
            tag_index[f"{category}/{fname}"] = tags
    return tag_index

def search_by_tag(tag):
    tag_index = build_tag_index()
    results = [path for path, tags in tag_index.items() if tag in tags]
    return results


def print_tag_table(tag_index, sort=True, wrap=6):
    """Print a formatted table of tags using rich enhancements."""
    # Flatten all tags and count
    tag_counter = Counter()
    tag_files = defaultdict(list)
    for path, tags in tag_index.items():
        for tag in tags:
            tag_counter[tag] += 1
            if len(tag_files[tag]) < 3:
                tag_files[tag].append(path)
    
    tags = sorted(tag_counter) if sort else list(tag_counter)
    
    if HAS_RICH:
        table = create_table("Tag Usage Analysis", ["Tag", "Count", "Example Files (up to 3)"])
        for tag in tags:
            files = ', '.join(tag_files[tag])
            add_table_row(table, [tag, str(tag_counter[tag]), files])
        display_table(table)
    else:
        # Fallback to simple print
        print("\n| Tag | Count | Example Files (up to 3) |")
        print("|------|-------|-------------------------|")
        for i, tag in enumerate(tags):
            files = ', '.join(tag_files[tag])
            print(f"| {tag:16} | {tag_counter[tag]:5} | {files} |")
            if (i+1) % wrap == 0:
                print("|------|-------|-------------------------|")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="ImpressionCore Tag Index Tool")
    parser.add_argument('--table', action='store_true', help='Print tag table')
    parser.add_argument('--sort', action='store_true', help='Sort tags alphabetically')
    parser.add_argument('--wrap', type=int, default=6, help='Wrap table every N rows')
    parser.add_argument('--interactive', action='store_true', help='Enable interactive search mode')
    args = parser.parse_args()

    print_info("Building tag index from documentation files...")
    tag_index = build_tag_index()
    
    tags_file = os.path.join(DOCS_ROOT, 'tags_index.yaml')
    with open(tags_file, 'w', encoding='utf-8') as f:
        for path, tags in tag_index.items():
            f.write(f'{path}: {tags}\n')
    
    print_success(f"Tag index written to tags_index.yaml.")

    if args.table:
        print_tag_table(tag_index, sort=args.sort, wrap=args.wrap)

    # Simple CLI search - only if interactive mode enabled
    if args.interactive:
        print_info("Interactive tag search mode enabled. Type 'exit' to quit.")
        while True:
            tag = input("Search for tag (or 'exit'): ").strip()
            if tag == 'exit':
                break
            results = search_by_tag(tag)
            if results:
                print_success(f"Files with tag '{tag}':")
                for r in results:
                    print(f"  - {r}")
            else:
                print_warning(f"No files found with tag '{tag}'")

if __name__ == "__main__":
    main()
