#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #docs\scripts\analytics\doc_analytics.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Doc Analytics

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** Kirk LaSalle  
**Tags:** #docs\scripts\analytics\doc_analytics.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore Documentation Analytics & Tag Health Script

Scans all Markdown files in docs/ and reports:
- Files missing tags
- Tag usage frequency (most/least used tags)
- Docs not updated in X days
- Orphaned docs (not referenced in DOCUMENTATION_INDEX.md)

Outputs a summary table to the console and optionally to docs/developer/doc_analytics_report.md.

Author: Kirk LaSalle <kirk@impressioncore.ai>
Project: ImpressionCore Documentation System
License: MIT
"""
import os
import re
import sys
import time
import argparse
from datetime import datetime, timedelta
from collections import Counter, defaultdict
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

# Configuration
DOCS_DIR = str(Path(__file__).parent.parent.parent)
INDEX_PATH = os.path.join(DOCS_DIR, 'DOCUMENTATION_INDEX.md')
REPORT_PATH = os.path.join(DOCS_DIR, 'developer', 'doc_analytics_report.md')
STALE_DAYS = 60

# Patterns
TAG_PATTERN = re.compile(r'^tags:\s*\[(.*?)\]', re.MULTILINE)
YAML_PATTERN = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
MD_FILE_PATTERN = re.compile(r'.*\.md$', re.IGNORECASE)


def get_all_md_files():
    """Get all markdown files in the documentation directory."""
    md_files = []
    for root, _, files in os.walk(DOCS_DIR):
        for f in files:
            if MD_FILE_PATTERN.match(f):
                md_files.append(os.path.join(root, f))
    return md_files


def get_indexed_files():
    """Get files referenced in DOCUMENTATION_INDEX.md."""
    try:
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print_error(f"DOCUMENTATION_INDEX.md not found at {INDEX_PATH}")
        return set()
        
    links = re.findall(r'\(([^)]+\.md)\)', content)
    # Paths in index are relative to DOCS_DIR
    return set(os.path.normpath(os.path.join(DOCS_DIR, link.replace('\\', '/'))) for link in links)


def extract_tags(md_path):
    """Extract tags from YAML frontmatter in a markdown file."""
    try:
        with open(md_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print_warning(f"Could not read {md_path}: {e}")
        return []
    
    # Try standard YAML frontmatter (---\n content \n---)
    yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    
    # If not found, try malformed frontmatter with # --- format
    if not yaml_match:
        yaml_match = re.search(r'^#\s*---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        
    if yaml_match:
        yaml_block = yaml_match.group(1)
        for line in yaml_block.splitlines():
            if line.strip().startswith('tags:'):
                tag_str = line.split(':', 1)[1].strip()
                tag_str = tag_str.strip('[]')
                tags = [t.strip().strip("'\"") for t in tag_str.split(',') if t.strip()]
                return tags
    
    return []


def get_last_modified(md_path):
    """Get the last modified date of a file."""
    return datetime.fromtimestamp(os.path.getmtime(md_path))


def analyze_documentation():
    """Perform comprehensive documentation analysis."""
    print_info("🔍 Starting documentation analysis...")
    
    # Get all files
    all_md_files = get_all_md_files()
    indexed_files = get_indexed_files()
    
    print_info(f"📁 Found {len(all_md_files)} markdown files")
    print_info(f"📋 Found {len(indexed_files)} indexed files")
    
    # Initialize tracking variables
    tag_counter = Counter()
    missing_tags_files = []
    stale_files = []
    orphaned_files = []
    now = datetime.now()
    
    # Create progress tracker if available
    if HAS_RICH:
        progress = create_progress()
        if progress:
            task = progress.add_task("[cyan]Analyzing files...", total=len(all_md_files))
    
    # Analyze each file
    for i, md_file in enumerate(all_md_files):
        # Update progress if available
        if HAS_RICH and 'progress' in locals() and progress:
            progress.update(task, advance=1, description=f"Analyzing {os.path.basename(md_file)}")
        
        # Skip the report file itself
        if md_file == REPORT_PATH:
            continue
            
        # Extract and count tags
        tags = extract_tags(md_file)
        if not tags:
            missing_tags_files.append(md_file)
        else:
            tag_counter.update(tags)
        
        # Check for stale files
        last_mod = get_last_modified(md_file)
        if (now - last_mod).days > STALE_DAYS:
            stale_files.append((md_file, last_mod.strftime('%Y-%m-%d')))
        
        # Check for orphaned files
        if md_file not in indexed_files and 'archive' not in md_file.lower():
            orphaned_files.append(md_file)
    
    # Close progress if it was created
    if HAS_RICH and 'progress' in locals() and progress:
        progress.stop()
    
    return {
        'all_files': all_md_files,
        'indexed_files': indexed_files,
        'tag_counter': tag_counter,
        'missing_tags': missing_tags_files,
        'stale_files': stale_files,
        'orphaned_files': orphaned_files
    }


def display_analysis_results(analysis_data):
    """Display comprehensive analysis results."""
    all_files = analysis_data['all_files']
    tag_counter = analysis_data['tag_counter']
    missing_tags = analysis_data['missing_tags']
    stale_files = analysis_data['stale_files']
    orphaned_files = analysis_data['orphaned_files']
    
    # Summary statistics
    if HAS_RICH:
        summary_panel = create_panel(
            f"Total Markdown Files: {len(all_files)}\n"
            f"Files Missing Tags: {len(missing_tags)}\n"
            f"Stale Files (>{STALE_DAYS} days): {len(stale_files)}\n"
            f"Orphaned Files: {len(orphaned_files)}\n"
            f"Unique Tags Found: {len(tag_counter)}",
            title="📊 Documentation Analysis Summary"
        )
        console.print(summary_panel)
    else:
        print(f"\n--- Documentation Analysis Summary ---")
        print(f"Total Markdown Files: {len(all_files)}")
        print(f"Files Missing Tags: {len(missing_tags)}")
        print(f"Stale Files (>{STALE_DAYS} days): {len(stale_files)}")
        print(f"Orphaned Files: {len(orphaned_files)}")
        print(f"Unique Tags Found: {len(tag_counter)}")      # Display missing tags
    if missing_tags:
        print_warning(f"\n⚠️  Files missing tags ({len(missing_tags)}):")
        if HAS_RICH:
            missing_table = create_table(columns=["Document Name", "Location"])
            for file_path in missing_tags[:10]:  # Show first 10
                relative_path = os.path.relpath(file_path, DOCS_DIR)
                add_table_row(missing_table, os.path.basename(file_path), relative_path)
            display_table(missing_table)
            if len(missing_tags) > 10:
                print_info(f"... and {len(missing_tags) - 10} more files")
        else:
            for file_path in missing_tags[:5]:
                print(f"  - {os.path.relpath(file_path, DOCS_DIR)}")
            if len(missing_tags) > 5:
                print(f"  ... and {len(missing_tags) - 5} more")      # Display stale files
    if stale_files:
        print_warning(f"\n📅 Stale files (not updated in {STALE_DAYS}+ days):")
        if HAS_RICH:
            stale_table = create_table(columns=["Document Path", "Last Modified"])
            for file_path, last_mod in stale_files[:10]:  # Show first 10
                relative_path = os.path.relpath(file_path, DOCS_DIR)
                add_table_row(stale_table, relative_path, last_mod)
            display_table(stale_table)
            if len(stale_files) > 10:
                print_info(f"... and {len(stale_files) - 10} more files")
        else:
            for file_path, last_mod in stale_files[:5]:
                print(f"  - {os.path.relpath(file_path, DOCS_DIR)} ({last_mod})")
            if len(stale_files) > 5:
                print(f"  ... and {len(stale_files) - 5} more")      # Display orphaned files
    if orphaned_files:
        print_warning(f"\n🔗 Orphaned files (not in DOCUMENTATION_INDEX.md):")
        if HAS_RICH:
            orphan_table = create_table(columns=["Document Name", "Location"])
            for file_path in orphaned_files[:10]:  # Show first 10
                relative_path = os.path.relpath(file_path, DOCS_DIR)
                add_table_row(orphan_table, os.path.basename(file_path), relative_path)
            display_table(orphan_table)
            if len(orphaned_files) > 10:
                print_info(f"... and {len(orphaned_files) - 10} more files")
        else:
            for file_path in orphaned_files[:5]:
                print(f"  - {os.path.relpath(file_path, DOCS_DIR)}")
            if len(orphaned_files) > 5:
                print(f"  ... and {len(orphaned_files) - 5} more")
    
    # Display tag statistics
    if tag_counter:
        print_info("\n🏷️  Tag Usage Statistics:")
          # Top tags
        top_tags = tag_counter.most_common(10)
        if HAS_RICH:
            top_table = create_table(columns=["Rank", "Tag", "Usage Count"])
            for i, (tag, count) in enumerate(top_tags, 1):
                add_table_row(top_table, str(i), tag, str(count))
            
            console.print("\nTop 10 Most Used Tags:")
            display_table(top_table)
        else:
            print("\nTop 10 Most Used Tags:")
            for i, (tag, count) in enumerate(top_tags, 1):
                print(f"  {i}. {tag}: {count} uses")          # Least used tags (single use)
        single_use_tags = [tag for tag, count in tag_counter.items() if count == 1]
        if single_use_tags:
            print_warning(f"\n📝 Tags used only once ({len(single_use_tags)} tags):")
            if HAS_RICH and len(single_use_tags) <= 20:
                single_table = create_table(columns=["Single-Use Tag"])
                for tag in sorted(single_use_tags)[:20]:
                    add_table_row(single_table, tag)
                display_table(single_table)
            else:
                for tag in sorted(single_use_tags)[:10]:
                    print(f"  - {tag}")
                if len(single_use_tags) > 10:
                    print(f"  ... and {len(single_use_tags) - 10} more")


def generate_report(analysis_data):
    """Generate a detailed markdown report."""
    print_info("📄 Generating detailed report...")
    
    # Ensure the developer directory exists
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    
    try:
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write("tags: [analytics, documentation, report, generated]\n")
            f.write("---\n\n")
            f.write("# ImpressionCore Documentation Analytics Report\n\n")
            f.write(f"_Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC_\n\n")
            
            # Summary section
            f.write("## Summary\n\n")
            f.write(f"- **Total Markdown Files**: {len(analysis_data['all_files'])}\n")
            f.write(f"- **Files Missing Tags**: {len(analysis_data['missing_tags'])}\n")
            f.write(f"- **Stale Files**: {len(analysis_data['stale_files'])}\n")
            f.write(f"- **Orphaned Files**: {len(analysis_data['orphaned_files'])}\n")
            f.write(f"- **Unique Tags**: {len(analysis_data['tag_counter'])}\n\n")
            
            # Detailed sections would go here...
            f.write("## Files Missing Tags\n\n")
            for file_path in analysis_data['missing_tags']:
                relative_path = os.path.relpath(file_path, DOCS_DIR)
                f.write(f"- `{relative_path}`\n")
            
            f.write("\n## Tag Usage Statistics\n\n")
            top_tags = analysis_data['tag_counter'].most_common(20)
            for tag, count in top_tags:
                f.write(f"- **{tag}**: {count} uses\n")
        
        print_success(f"✅ Report generated: {os.path.relpath(REPORT_PATH, DOCS_DIR)}")
        
    except Exception as e:
        print_error(f"❌ Failed to generate report: {e}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="ImpressionCore Documentation Analytics & Tag Health Script")
    parser.add_argument('--update-index', action='store_true', 
                       help='Update DOCUMENTATION_INDEX.md with orphaned files')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate detailed markdown report')
    args = parser.parse_args()
    
    # Display header
    if HAS_RICH:
        console.print(create_panel(
            "ImpressionCore Documentation System\nAnalytics & Tag Health Checker",
            title="📊 IDS Analytics Tool"
        ))
    else:
        print("=== ImpressionCore Documentation System ===")
        print("=== Analytics & Tag Health Checker ===")
    
    try:
        # Perform analysis
        analysis_data = analyze_documentation()
        
        # Display results
        display_analysis_results(analysis_data)
        
        # Generate report if requested
        if args.generate_report:
            generate_report(analysis_data)
        
        # Update index if requested
        if args.update_index:
            print_info("\n🔄 Index update functionality would be implemented here")
            # This would be a simplified version of the complex index update logic
        
        print_success("\n✅ Documentation analytics completed successfully!")
        
    except Exception as e:
        print_error(f"❌ Error during analysis: {e}")
        if HAS_RICH:
            console.print_exception()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
