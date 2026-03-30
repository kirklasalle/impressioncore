
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\tools\categorize_and_move_inbox.py #documentation #gpu_optimization #memory_management #performance #python #security #source_code #testing #tokenization #training #web_interface  
**Category:** Source Code  
**Status:** Deprecated
"""









# Categorize And Move Inbox

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\tools\categorize_and_move_inbox.py #documentation #gpu_optimization #memory_management #performance #python #security #source_code #testing #tokenization #training #web_interface  
**Category:** Source Code  
**Status:** Deprecated

"""
ImpressionCore Documentation System - Inbox Categorization Tool

Automatically categorizes and moves files from docs/inbox/ to appropriate
category directories based on filename patterns and content analysis.

Author: Kirk LaSalle <kirk@impressioncore.ai>
Project: ImpressionCore Documentation System
License: MIT
"""
import os
import sys
import shutil
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

# Configuration
DOCS_ROOT = str(Path(__file__).parent.parent.parent)
INBOX = os.path.join(DOCS_ROOT, 'inbox')

# Categorization rules
CATEGORIES = {
    'user': ['user_guide', 'onboarding', 'faq', 'quickstart', 'user-flow'],
    'developer': ['developer', 'architecture', 'api', 'walkthrough', 'code', 'frontend', 'backend'],
    'process': ['roadmap', 'sprint', 'project', 'status', 'next_steps', 'workflow', 'board', 'review', 'summary'],
    'reference': ['prd', 'requirements', 'plan', 'strategy', 'changelog', 'binder', 'template', 'contract', 'benchmark', 'compatibility', 'integration', 'visualization', 'security', 'error', 'testing', 'memory', 'token', 'diffusion', 'modal', 'lora', 'trainer', 'implementation', 'impressioncore', 'knowledge', 'shared', 'shadow', 'rule', 'specialized', 'latent', 'solar', 'goodstyle', 'badstyle', 'Luke', 'Gemini', 'UKS', 'BRAINSIM3', 'GPU', 'performance', 'optimization', 'component', 'comprehensive', 'documentation', 'dummy', 'automation', 'advanced', 'api_reference', 'api_contracts', 'modal-engine', 'modal_engine_tokenizer_integration', 'model', 'tokenization', 'token_converter', 'token_rate_control', 'training', 'trainer', 'visualization', 'workflow', 'web_interface', 'workspace'],
    'archive': ['archive', 'deprecated', 'obsolete', 'old', 'replaced'],
    'assets': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'],
    'styles': ['.css', '.scss', '.sass', '.less', '.js', '.html']
}

# Tag mapping for future YAML frontmatter enhancement
TAG_RULES = {
    'user': ['user', 'onboarding', 'faq', 'quickstart'],
    'developer': ['developer', 'architecture', 'api', 'walkthrough', 'code'],
    'process': ['roadmap', 'sprint', 'project', 'status', 'next_steps', 'workflow'],
    'reference': ['reference', 'documentation', 'specification'],
    'archive': ['archive', 'deprecated', 'obsolete'],
    'assets': ['media', 'image', 'visual'],
    'styles': ['styling', 'frontend', 'ui']
}


def categorize_file(filename):
    """Determine the appropriate category for a file based on its name and extension."""
    lower_name = filename.lower()
    
    # Check each category's keywords
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            # Check if the keyword is an extension (starts with .)
            if keyword.startswith('.'):
                if lower_name.endswith(keyword):
                    return category
            # Check if keyword appears in filename
            elif keyword in lower_name or lower_name.endswith(keyword + '.md'):
                return category
    
    # Default categorization based on file extension
    if lower_name.endswith('.md'):
        return 'reference'
    elif any(lower_name.endswith(ext) for ext in CATEGORIES['assets']):
        return 'assets'
    elif any(lower_name.endswith(ext) for ext in CATEGORIES['styles']):
        return 'styles'
    
    # Ultimate fallback
    return 'reference'


def scan_inbox():
    """Scan the inbox directory and return list of files to process."""
    if not os.path.exists(INBOX):
        print_warning(f"📂 Inbox directory not found: {INBOX}")
        os.makedirs(INBOX, exist_ok=True)
        print_info(f"✅ Created inbox directory: {INBOX}")
        return []
    
    files = []
    for item in os.listdir(INBOX):
        item_path = os.path.join(INBOX, item)
        if os.path.isfile(item_path):
            files.append(item)
        else:
            print_warning(f"⚠️  Skipping directory: {item}")
    
    return files


def ensure_category_directories():
    """Ensure all category directories exist."""
    created_dirs = []
    for category in CATEGORIES.keys():
        cat_dir = os.path.join(DOCS_ROOT, category)
        if not os.path.exists(cat_dir):
            os.makedirs(cat_dir, exist_ok=True)
            created_dirs.append(category)
    
    if created_dirs:
        print_info(f"📁 Created missing directories: {', '.join(created_dirs)}")
    
    return created_dirs


def move_files_from_inbox():
    """Process and move all files from inbox to appropriate categories."""
    print_info("🔍 Scanning inbox for files to categorize...")
    
    # Scan inbox
    inbox_files = scan_inbox()
    
    if not inbox_files:
        print_info("📭 Inbox is empty - nothing to process")
        return {
            'processed': 0,
            'moved': [],
            'errors': []
        }
    
    print_info(f"📋 Found {len(inbox_files)} files to process")
    
    # Ensure category directories exist
    ensure_category_directories()
    
    # Processing results
    moved_files = []
    error_files = []
    
    # Create progress tracker if available
    if HAS_RICH:
        progress = create_progress()
        if progress:
            task = progress.add_task("[cyan]Processing files...", total=len(inbox_files))
    
    # Process each file
    for i, filename in enumerate(inbox_files):
        # Update progress if available
        if HAS_RICH and 'progress' in locals() and progress:
            progress.update(task, advance=1, description=f"Processing {filename}")
        
        src_path = os.path.join(INBOX, filename)
        
        try:
            # Determine category
            category = categorize_file(filename)
            dest_dir = os.path.join(DOCS_ROOT, category)
            dest_path = os.path.join(dest_dir, filename)
            
            # Handle filename conflicts
            original_dest = dest_path
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_filename = f"{base}_inbox_{timestamp}{ext}"
                dest_path = os.path.join(dest_dir, new_filename)
                print_warning(f"⚠️  File exists, renaming: {filename} → {new_filename}")
            
            # Move the file
            shutil.move(src_path, dest_path)
            
            moved_files.append({
                'filename': filename,
                'category': category,
                'dest_path': os.path.relpath(dest_path, DOCS_ROOT),
                'renamed': dest_path != original_dest
            })
            
            print_success(f"✅ Moved: {filename} → {category}/")
            
        except Exception as e:
            error_files.append({
                'filename': filename,
                'error': str(e)
            })
            print_error(f"❌ Failed to move {filename}: {e}")
    
    # Close progress if it was created
    if HAS_RICH and 'progress' in locals() and progress:
        progress.stop()
    
    return {
        'processed': len(inbox_files),
        'moved': moved_files,
        'errors': error_files
    }


def display_results(results):
    """Display comprehensive processing results."""
    moved_files = results['moved']
    error_files = results['errors']
    
    # Summary statistics
    if HAS_RICH:
        summary_panel = create_panel(
            f"Files Processed: {results['processed']}\n"
            f"Successfully Moved: {len(moved_files)}\n"
            f"Errors: {len(error_files)}",
            title="📊 Processing Summary"
        )
        console.print(summary_panel)
    else:
        print(f"\n--- Processing Summary ---")
        print(f"Files Processed: {results['processed']}")
        print(f"Successfully Moved: {len(moved_files)}")
        print(f"Errors: {len(error_files)}")
    
    # Display moved files by category
    if moved_files:
        category_counts = {}
        for file_info in moved_files:
            category = file_info['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        if HAS_RICH:
            moved_table = create_table("Category", "Files Moved", "Examples")
            for category, count in sorted(category_counts.items()):
                examples = [f['filename'] for f in moved_files if f['category'] == category][:3]
                example_text = ', '.join(examples)
                if len(examples) < count:
                    example_text += f" (+{count - len(examples)} more)"
                add_table_row(moved_table, category.capitalize(), str(count), example_text)
            
            console.print("\n")
            console.print("Files Moved by Category:")
            display_table(moved_table)
        else:
            print("\nFiles moved by category:")
            for category, count in sorted(category_counts.items()):
                print(f"  {category.capitalize()}: {count} files")
    
    # Display errors if any
    if error_files:
        print_error(f"\n❌ Errors occurred during processing:")
        if HAS_RICH:
            error_table = create_table("File", "Error")
            for error_info in error_files:
                add_table_row(error_table, error_info['filename'], error_info['error'])
            display_table(error_table)
        else:
            for error_info in error_files:
                print(f"  {error_info['filename']}: {error_info['error']}")


def main():
    """Main execution function."""
    # Display header
    if HAS_RICH:
        console.print(create_panel(
            "ImpressionCore Documentation System\nInbox Categorization & File Organization Tool",
            title="📁 IDS File Management"
        ))
    else:
        print("=== ImpressionCore Documentation System ===")
        print("=== Inbox Categorization Tool ===")
    
    try:
        # Process inbox files
        results = move_files_from_inbox()
        
        # Display results
        display_results(results)
        
        # Final status
        if results['errors']:
            print_warning(f"⚠️  Processing completed with {len(results['errors'])} errors")
        elif results['moved']:
            print_success(f"🎉 Successfully processed {len(results['moved'])} files!")
        else:
            print_info("📭 No files found to process")
        
    except Exception as e:
        print_error(f"❌ Critical error during processing: {e}")
        if HAS_RICH:
            console.print_exception()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
