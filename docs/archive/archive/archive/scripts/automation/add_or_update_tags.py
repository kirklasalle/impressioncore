
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\automation\add_or_update_tags.py #documentation #gpu_optimization #memory_management #performance #python #security #source_code #testing #tokenization #training #web_interface  
**Category:** Source Code  
**Status:** Deprecated
"""









# Add Or Update Tags

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\automation\add_or_update_tags.py #documentation #gpu_optimization #memory_management #performance #python #security #source_code #testing #tokenization #training #web_interface  
**Category:** Source Code  
**Status:** Deprecated

#!/usr/bin/env python3
"""
ImpressionCore Documentation System - Tag Management

Adds or updates YAML frontmatter tags in Markdown files across the documentation system.
Automatically suggests contextual tags based on file location and content.

Author: Kirk LaSalle <kirk@impressioncore.ai>
Project: ImpressionCore Documentation System
License: MIT
"""

import os
import re
import argparse
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.core.utils.rich_enhancements import (
        console, print_info, print_success, print_warning, print_error,
        create_table, add_table_row, display_table, create_progress,
        create_panel
    )
    from src.core.utils.rich_logging import setup_rich_logging
    HAS_RICH = True
except ImportError:
    # Fallback if rich utils not available
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
        return []
    
    def add_table_row(table, *args):
        pass
    
    def display_table(table):
        pass
    
    def create_progress(*args, **kwargs):
        return None
    
    def create_panel(text, title=""):
        return f"\n--- {title} ---\n{text}\n"
    
    def setup_rich_logging(*args, **kwargs):
        import logging
        return logging.getLogger(__name__)

yaml_frontmatter = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

# Directories to scan for .md files
CATEGORIES = ["user", "developer", "process", "reference", "archive"]
DOCS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Example tag suggestions by directory and filename keywords
TAG_SUGGESTIONS = {
    'user': ['user', 'guide', 'onboarding', 'faq', 'quickstart'],
    'developer': ['developer', 'architecture', 'api', 'walkthrough', 'code', 'reference'],
    'process': ['process', 'roadmap', 'sprint', 'project', 'status', 'workflow', 'board', 'review', 'summary'],
    'reference': ['reference', 'prd', 'requirements', 'plan', 'strategy', 'changelog', 'binder', 'template', 'contract', 'benchmark', 'compatibility', 'integration', 'visualization', 'security', 'error', 'testing', 'memory', 'token', 'diffusion', 'modal', 'lora', 'trainer', 'implementation', 'impressioncore', 'knowledge', 'shared', 'shadow', 'rule', 'specialized', 'latent', 'solar', 'goodstyle', 'badstyle', 'Luke', 'Gemini', 'UKS', 'BRAINSIM3', 'GPU', 'performance', 'optimization', 'component', 'comprehensive', 'documentation', 'dummy', 'automation', 'advanced', 'api_reference', 'api_contracts', 'backend', 'frontend', 'modal-engine', 'modal_engine_tokenizer_integration', 'model', 'tokenization', 'token_converter', 'token_rate_control', 'training', 'trainer', 'visualization', 'workflow', 'web_interface', 'workspace'],
    'archive': ['archive', 'deprecated', 'obsolete', 'old', 'replaced']
}

def suggest_tags(category, filename):
    tags = set([category])
    lower = filename.lower()
    for tag in TAG_SUGGESTIONS.get(category, []):
        if tag in lower:
            tags.add(tag)
    # Add year as tag
    tags.add(str(os.environ.get('DOC_TAG_YEAR', '2025')))
    return list(tags)

def add_or_update_frontmatter(md_path, tags):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove existing frontmatter
    content_wo_frontmatter = yaml_frontmatter.sub('', content)
    # Add new frontmatter
    tag_line = ', '.join(tags)
    new_frontmatter = f"---\ntags: [{tag_line}]\n---\n"
    new_content = new_frontmatter + content_wo_frontmatter.lstrip('\n')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print_success(f"Updated tags for {md_path}: {tags}")


def check_tagging_state():
    """Scan all .md files and report tagging state."""
    missing = []
    present = []
    for category in CATEGORIES:
        dir_path = os.path.join(DOCS_ROOT, category)
        if not os.path.isdir(dir_path):
            continue
        for fname in os.listdir(dir_path):
            if not fname.endswith('.md'):
                continue
            md_path = os.path.join(dir_path, fname)
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if yaml_frontmatter.match(content):
                present.append(md_path)
            else:
                missing.append(md_path)
    return missing, present


def main():
    parser = argparse.ArgumentParser(description="Add or update tag frontmatter in Markdown files.")
    parser.add_argument('--auto', action='store_true', help='Auto-process all files with suggested tags (no prompt).')
    parser.add_argument('--missing-only', action='store_true', help='Only process files missing tag frontmatter.')
    args = parser.parse_args()

    logger = setup_rich_logging("tagging", level=os.environ.get("LOGLEVEL", "INFO"))
    print_info("Checking current tagging state...")
    missing, present = check_tagging_state()    # Show summary table with error handling for Unicode issues
    try:
        table = create_table(title="Tagging State Summary")
        if HAS_RICH:
            table.add_column("State", style="cyan")
            table.add_column("Count", style="magenta")
            table.add_row("Files with tags", str(len(present)))
            table.add_row("Files missing tags", str(len(missing)))
            console.print(table)
        else:
            print(f"Files with tags: {len(present)}")
            print(f"Files missing tags: {len(missing)}")
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        # Fallback to simple text output if Unicode issues occur
        print(f"Files with tags: {len(present)}")
        print(f"Files missing tags: {len(missing)}")
        print(f"Note: Using fallback display due to encoding issue: {e}")

    # Choose files to process
    files_to_process = []
    for category in CATEGORIES:
        dir_path = os.path.join(DOCS_ROOT, category)
        if not os.path.isdir(dir_path):
            continue
        for fname in os.listdir(dir_path):
            if not fname.endswith('.md'):
                continue
            md_path = os.path.join(dir_path, fname)
            if args.missing_only and md_path not in missing:
                continue
            files_to_process.append((category, fname, md_path))

    if not files_to_process:
        print_success("No files to process. All files are tagged!")
        return    print_info(f"Processing {len(files_to_process)} files...")
    
    log_lines = []
    try:
        if HAS_RICH:
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ) as progress:
                task = progress.add_task("Tagging files", total=len(files_to_process))
                for category, fname, md_path in files_to_process:
                    tags = suggest_tags(category, fname)
                    if args.auto:
                        add_or_update_frontmatter(md_path, tags)
                        log_lines.append(f"✓ Updated tags for {md_path}: {tags}")
                    else:
                        print_info(f"\nFile: {md_path}\nSuggested tags: {tags}")
                        user_input = input("Enter tags as comma-separated list or press Enter to accept: ")
                        if user_input.strip():
                            tags = [t.strip() for t in user_input.split(',') if t.strip()]
                        add_or_update_frontmatter(md_path, tags)
                        log_lines.append(f"✓ Updated tags for {md_path}: {tags}")
                    progress.update(task, advance=1)
        else:
            # Fallback without progress bar
            for i, (category, fname, md_path) in enumerate(files_to_process, 1):
                print(f"Processing {i}/{len(files_to_process)}: {md_path}")
                tags = suggest_tags(category, fname)
                if args.auto:
                    add_or_update_frontmatter(md_path, tags)
                    log_lines.append(f"✓ Updated tags for {md_path}: {tags}")
                else:
                    print_info(f"\nFile: {md_path}\nSuggested tags: {tags}")
                    user_input = input("Enter tags as comma-separated list or press Enter to accept: ")
                    if user_input.strip():
                        tags = [t.strip() for t in user_input.split(',') if t.strip()]
                    add_or_update_frontmatter(md_path, tags)
                    log_lines.append(f"✓ Updated tags for {md_path}: {tags}")
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        print(f"Unicode encoding issue detected, using fallback processing: {e}")
        # Fallback processing without Rich
        for i, (category, fname, md_path) in enumerate(files_to_process, 1):
            print(f"Processing {i}/{len(files_to_process)}: {md_path}")
            tags = suggest_tags(category, fname)
            if args.auto:
                add_or_update_frontmatter(md_path, tags)
                log_lines.append(f"Updated tags for {md_path}: {tags}")
            else:
                print(f"\nFile: {md_path}\nSuggested tags: {tags}")
                user_input = input("Enter tags as comma-separated list or press Enter to accept: ")
                if user_input.strip():
                    tags = [t.strip() for t in user_input.split(',') if t.strip()]
                add_or_update_frontmatter(md_path, tags)
                log_lines.append(f"Updated tags for {md_path}: {tags}")    # Display summary with Unicode error handling
    if log_lines:
        try:
            if HAS_RICH:
                console.print(create_panel("\n".join(log_lines), "Tagging Results"))
            else:
                print("\n--- Tagging Results ---")
                for line in log_lines:
                    print(line)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            print(f"\n--- Tagging Results (fallback display) ---")
            for line in log_lines:
                try:
                    print(line)
                except (UnicodeEncodeError, UnicodeDecodeError):
                    print(line.encode('ascii', 'replace').decode('ascii'))
    
    print_success("Tagging process complete.")

if __name__ == "__main__":
    main()
