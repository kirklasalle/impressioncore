#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\analytics\doc_analytics_backup.py #documentation #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Doc Analytics Backup

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\analytics\doc_analytics_backup.py #documentation #memory_management #python #source_code  
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
import yaml
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

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
INDEX_PATH = os.path.join(DOCS_DIR, 'DOCUMENTATION_INDEX.md')
REPORT_PATH = os.path.join(DOCS_DIR, 'developer', 'doc_analytics_report.md')
OLD_AUTO_INDEX_HEADER_STRIP = "## Discovered Documents (Automated Entry)" # Used for cleanup

TAG_PATTERN = re.compile(r'^tags:\\s*\\[(.*?)\\]', re.MULTILINE)
YAML_PATTERN = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
MD_FILE_PATTERN = re.compile(r'.*\.md$', re.IGNORECASE)

# Helper to get all markdown files in docs/
def get_all_md_files():
    md_files = []
    for root, _, files in os.walk(DOCS_DIR):
        for f in files:
            if MD_FILE_PATTERN.match(f):
                md_files.append(os.path.join(root, f))
    return md_files

# Helper to get referenced files from DOCUMENTATION_INDEX.md
def get_indexed_files():
    # Ensure INDEX_PATH is correct and accessible
    try:
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        if HAS_RICH: logger.error(f"DOCUMENTATION_INDEX.md not found at {INDEX_PATH}")
        else: print(f"ERROR: DOCUMENTATION_INDEX.md not found at {INDEX_PATH}")
        return set()
        
    links = re.findall(r'\\(([^)]+\\.md)\\)', content)
    # Paths in index are relative to DOCS_DIR.
    # Normalize link paths (e.g. replace backslashes) before joining.
    return set(os.path.normpath(os.path.join(DOCS_DIR, link.replace('\\\\', '/'))) for link in links)

# Helper to get referenced files from a list of lines (e.g., in-memory modified index)
def get_indexed_files_from_lines(lines_list):
    content = "".join(lines_list)
    links = re.findall(r'\\(([^)]+\\.md)\\)', content)
    # Paths in index are relative to DOCS_DIR.
    # Normalize link paths (e.g. replace backslashes) before joining.
    return set(os.path.normpath(os.path.join(DOCS_DIR, link.replace('\\\\', '/'))) for link in links)

# Helper to extract tags from YAML frontmatter
def extract_tags(md_path):
    with open(md_path, encoding='utf-8') as f:
        content = f.read()
    
    # First try the standard YAML frontmatter (---\n content \n---)
    yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    
    # If not found, try the malformed frontmatter with # --- format
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
    
    # If we get here, no tags were found
    return []

# Helper to get last modified date
def get_last_modified(md_path):
    return datetime.fromtimestamp(os.path.getmtime(md_path))

# Main analytics
all_md_files = get_all_md_files() # Renamed from md_files
original_indexed_files = get_indexed_files() # For reporting purposes
tag_counter = Counter()
missing_tags_report = [] # Renamed
stale_files_report = []  # Renamed
orphaned_files_report = [] # Renamed, for reporting only
now = datetime.now()
STALE_DAYS = 60

for md in all_md_files: # Use all_md_files
    tags = extract_tags(md)
    if not tags:
        # Exclude the report file itself from missing tags check
        if md != REPORT_PATH:
            missing_tags_report.append(md) # Use report variable
    else:
        tag_counter.update(tags)
    # Stale file check
    last_mod = get_last_modified(md)
    if (now - last_mod).days > STALE_DAYS:
        stale_files_report.append((md, last_mod.strftime('%Y-%m-%d'))) # Use report variable
    # Orphaned file check for reporting (based on original index)
    if md not in original_indexed_files and 'archive' not in md.lower() and md != REPORT_PATH:
        orphaned_files_report.append(md) # Use report variable


# Rich logging and animated progress

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="ImpressionCore Documentation Analytics & Tag Health Script.")
parser.add_argument(
    '--update-index',
    action='store_true',
    help='If set, appends orphaned Markdown files to DOCUMENTATION_INDEX.md.'
)
args = parser.parse_args()
# --- End Argument Parsing ---

# Use ImpressionCore rich enhancements if available
if HAS_RICH:
    logger = setup_rich_logging("doc_analytics", level=20)
    create_header("ImpressionCore Documentation Analytics", subtitle="Rich Logging & Visual Enhancements Enabled")
    print_info("Scanning documentation files...")
    progress, task_id = create_progress_bar("Scanning Markdown files", total=len(all_md_files), unit="files") # Use all_md_files
    for i in range(len(all_md_files)): # Use all_md_files
        progress.update(task_id, completed=i+1)
        time.sleep(0.002)
    progress.stop()
    print_success(f"Total Markdown files: {len(all_md_files)}") # Use all_md_files
    print_success(f"Files missing tags: {len(missing_tags_report)}") # Use report variable
    if missing_tags_report: # Use report variable
        print_warning("Files reported as missing tags (based on initial scan):")
        for f_path in missing_tags_report: # Use report variable
            print_warning(f"  - {os.path.relpath(f_path, DOCS_DIR)}")
    print_info(f"Stale files (> {STALE_DAYS} days): {len(stale_files_report)}") # Use report variable
    print_info(f"Orphaned files (not in DOCUMENTATION_INDEX.md, based on initial scan): {len(orphaned_files_report)}") # Use report variable

    # --- Update Index if flag is set ---
    if args.update_index:
        if HAS_RICH:
            print_info(f"Starting --update-index process...")

        # 1. Read current index content
        try:
            with open(INDEX_PATH, 'r', encoding='utf-8') as f:
                initial_index_lines = f.readlines()
        except FileNotFoundError:
            initial_index_lines = [
                "---\\n", "tags: [index, documentation, 2025]\\n", "---\\n\\n",
                "# ImpressionCore Documentation Index\\n\\n",
                "_Last updated: " + datetime.now().strftime('%Y-%m-%d') + "_\\n\\n"
            ]

        # 2. Clean up old auto-generated section from initial_index_lines to create working_index_lines
        working_index_lines = []
        old_section_header_found_and_removed = False
        if HAS_RICH: logger.info(f"Attempting to clean section starting with: '{OLD_AUTO_INDEX_HEADER_STRIP}' from DOCUMENTATION_INDEX.md")

        for i, line_content in enumerate(initial_index_lines):
            # Debugging for the specific header
            stripped_line_for_debug = line_content.strip() # For debug comparison
            if "Discovered Documents (Automated Entry)" in line_content: # Broader check for logging
                 logger.info(f"DEBUG_SCAN: Line {i+1} (raw snippet): {repr(line_content[:100])}...")
                 logger.info(f"DEBUG_SCAN: Line {i+1} (stripped snippet for debug): '{stripped_line_for_debug[:100]}...'")
                 logger.info(f"DEBUG_SCAN: Target header: '{OLD_AUTO_INDEX_HEADER_STRIP}'")
                 match_result = (OLD_AUTO_INDEX_HEADER_STRIP in line_content)
                 logger.info(f"DEBUG_SCAN: 'in line_content' check result: {match_result}")

            # The primary check: if the target header is in the current line_content, skip this entire line.
            # This assumes the entire "Discovered Documents (Automated Entry)" section,
            # including all its bullet points, is part of this single line_content if the header is present.
            if OLD_AUTO_INDEX_HEADER_STRIP in line_content:
                if HAS_RICH: 
                    logger.info(f"Found old auto-index header signature within line {i+1}. Skipping this entire line.")
                    logger.debug(f"Full content of skipped line (snippet): {repr(line_content[:200])}...")
                old_section_header_found_and_removed = True
                continue  # Skip this line entirely
            
            working_index_lines.append(line_content)

        if old_section_header_found_and_removed and HAS_RICH:
            print_success(f"Successfully processed and removed line(s) containing '{OLD_AUTO_INDEX_HEADER_STRIP}' from in-memory index.")
        elif HAS_RICH:
            print_warning(f"Old auto-index header signature '{OLD_AUTO_INDEX_HEADER_STRIP}' was NOT found in any line during cleanup pass.")
            logger.info("Contents of initial_index_lines (first 10 lines for brevity if long):")
            for k, initial_line in enumerate(initial_index_lines[:10]):
                logger.info(f"  Initial Index Line {k+1}: {repr(initial_line)}")
        
        # Ensure the last line of working_index_lines has a newline if it's not empty
        if working_index_lines and working_index_lines[-1] and not working_index_lines[-1].endswith('\\n'):
            working_index_lines[-1] += '\\n'


        # 3. Determine orphans based on this *cleaned* working_index_lines
        indexed_files_after_cleanup = get_indexed_files_from_lines(working_index_lines)
        orphans_to_add_to_index = []
        for md_file_path in all_md_files:
            if (md_file_path not in indexed_files_after_cleanup and
                'archive' not in md_file_path.lower() and
                md_file_path != REPORT_PATH):
                orphans_to_add_to_index.append(md_file_path)
        
        if HAS_RICH:
            print_info(f"Orphaned files to be processed for index update: {len(orphans_to_add_to_index)}")
            if not orphans_to_add_to_index and old_section_header_found_and_removed:
                 print_info("No new orphans to add after cleaning. Index might be up to date or files were only in the old section.")
            elif not orphans_to_add_to_index:
                 print_info("No orphaned files to add to the index.")

        if orphans_to_add_to_index:
            if HAS_RICH:
                print_info(f"Categorizing and updating {os.path.basename(INDEX_PATH)} with {len(orphans_to_add_to_index)} orphaned files...")
            # The following block (categorization and writing) will now use:
            # - `orphans_to_add_to_index` as the source of orphans.
            # - `working_index_lines` as the base for `index_lines` to be modified.
            # It should NOT re-read or re-clean for OLD_AUTO_INDEX_HEADER_STRIP.

            # KNOWN_CATEGORIES_MD and DEFAULT_ORPHAN_HEADER_MD are defined globally or correctly scoped.
            KNOWN_CATEGORIES_MD = { # Maps parent dir (lowercase) to Markdown Header string
                "api": "\\n## API Documentation\\n",
                "developer": "\\n## Developer Documentation\\n",
                "implementation-plans": "\\n## Implementation Plans\\n",
                "process": "\\n## Process Documentation\\n",
                "reference": "\\n## Reference Materials\\n",
                "technical": "\\n## Technical Documentation\\n",
                "user": "\\n## User Guides\\n",
                "user_guide": "\\n## User Guides\\n", # Merged with "user" effectively by logic below
                "impressioncore": "\\n## ImpressionCore General\\n", # For docs in docs/ImpressionCore/
                "uks_documentation_html": "\\n## UKS Documentation (HTML Export Reference)\\n" # Special case
            }
            DEFAULT_ORPHAN_HEADER_MD = "\\n## Other Discovered Documents\\n"
            DEFAULT_CATEGORY_KEY = "_default_orphans_"


            categorized_orphans = defaultdict(list)
            for orphan_path in orphans_to_add_to_index: # USE orphans_to_add_to_index
                relative_path = os.path.relpath(orphan_path, DOCS_DIR)
                parent_dir_parts = os.path.dirname(relative_path).split(os.sep)
                
                assigned_category_key = None
                if parent_dir_parts and parent_dir_parts[0]: # Check if there is a parent directory
                    top_level_parent_dir = parent_dir_parts[0].lower()
                    if top_level_parent_dir in KNOWN_CATEGORIES_MD:
                        assigned_category_key = top_level_parent_dir
                
                if assigned_category_key:
                    categorized_orphans[assigned_category_key].append(orphan_path)
                else:
                    categorized_orphans[DEFAULT_CATEGORY_KEY].append(orphan_path)

            # 3. Read current index content -> This step is now effectively done, `working_index_lines` is our starting point.
            # The original code had:
            # try:
            #     with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            #         index_lines = f.readlines()
            # except FileNotFoundError:
            #     index_lines = [ ... ]
            # This should be replaced by:
            index_lines = list(working_index_lines) # Start with the already cleaned lines

            # 4. Clean up old auto-generated section -> This was done to create working_index_lines.
            # The original code had:
            # cleaned_lines = []
            # in_old_auto_section = False
            # for line in index_lines: ...
            # index_lines = cleaned_lines
            # This specific cleanup for OLD_AUTO_INDEX_HEADER_STRIP should NOT be repeated here.
            # The `index_lines` variable is already the result of this cleanup.

            # Ensure the file ends with a newline if it's not empty and content was added
            if index_lines and not index_lines[-1].endswith('\\n'):
                index_lines[-1] = index_lines[-1] + '\\n'
            if not index_lines and (categorized_orphans or DEFAULT_CATEGORY_KEY in categorized_orphans) : # If index was empty or became empty
                if not any(line.strip() == "---" for line in index_lines): # Add frontmatter if truly empty
                     index_lines.extend([
                    "---\\n", "tags: [index, documentation, 2025]\\n", "---\\n\\n",
                    "# ImpressionCore Documentation Index\\n\\n",
                     "_Last updated: " + datetime.now().strftime('%Y-%m-%d') + "_\\n\\n"
                ])


            # 5. Add categorized orphans to the index content
            
            # Consolidate user_guide into user for KNOWN_CATEGORIES_MD keys
            effective_known_categories = {k:v for k,v in KNOWN_CATEGORIES_MD.items()}
            if "user_guide" in categorized_orphans and "user" in effective_known_categories:
                categorized_orphans["user"].extend(categorized_orphans.pop("user_guide", []))
                if "user_guide" in effective_known_categories: # Avoid duplicate processing if user_guide was a distinct key
                    del effective_known_categories["user_guide"]


            categories_to_process = list(effective_known_categories.items())
            if DEFAULT_CATEGORY_KEY in categorized_orphans and categorized_orphans[DEFAULT_CATEGORY_KEY]:
                categories_to_process.append((DEFAULT_CATEGORY_KEY, DEFAULT_ORPHAN_HEADER_MD))

            for category_key, section_header_md_val in categories_to_process:
                orphans_in_cat = categorized_orphans.get(category_key)
                if not orphans_in_cat:
                    continue

                current_section_header_strip = section_header_md_val.strip()
                
                # Prepare links for this category
                md_links_for_section = []
                for orphan_path in orphans_in_cat: # This `orphans_in_cat` comes from `categorized_orphans` which uses `orphans_to_add_to_index`
                    relative_orphan_path = os.path.relpath(orphan_path, DOCS_DIR).replace('\\\\', '/')
                    link_title = os.path.splitext(os.path.basename(relative_orphan_path))[0].replace('_', ' ').title()
                    md_link = f"- [{link_title}]({relative_orphan_path})\\n"
                    
                    # Check if link already exists anywhere in the current index_lines to avoid duplicates
                    link_exists = any(md_link.strip() in line.strip() for line in index_lines)
                    if not link_exists:
                        md_links_for_section.append(md_link)
                
                if not md_links_for_section:
                    continue

                # Find or add section header
                header_line_idx = -1
                for i, line in enumerate(index_lines):
                    if line.strip() == current_section_header_strip:
                        header_line_idx = i
                        break
                
                if header_line_idx != -1: # Header found, insert links
                    insert_point = header_line_idx + 1
                    # Find where the section ends (next '##' or EOF)
                    for j in range(insert_point, len(index_lines)):
                        if index_lines[j].strip().startswith("## "):
                            insert_point = j
                            break
                    else: # No more sections, end of list
                        insert_point = len(index_lines)
                    
                    # Ensure a blank line after the header if not already present
                    if insert_point == header_line_idx + 1 and index_lines[header_line_idx+1:insert_point] and index_lines[header_line_idx+1].strip() != "":
                        index_lines.insert(insert_point, "\\n")
                        insert_point +=1
                    elif insert_point == header_line_idx +1: # Header is the last line or followed by blank
                         if not index_lines[header_line_idx].endswith("\\n\\n"): # Ensure header itself has a blank line after
                              index_lines[header_line_idx] = index_lines[header_line_idx].rstrip() + "\\n\\n"


                    index_lines[insert_point:insert_point] = md_links_for_section
                else: # Header not found, append new section to the end
                    if index_lines and index_lines[-1].strip() != "": # Ensure blank line before new section
                        index_lines.append("\\n")
                    index_lines.append(section_header_md_val) # This includes \\n at start and end
                    if not section_header_md_val.endswith("\\n"): # Ensure header itself has a blank line after
                        index_lines[-1] = index_lines[-1].rstrip() + "\\n\\n"
                    elif not section_header_md_val.endswith("\\n\\n"): # Needs two newlines
                        index_lines[-1] = index_lines[-1].rstrip() + "\\n"


                    index_lines.extend(md_links_for_section)
            
            # 6. Write the updated content back
            try:
                with open(INDEX_PATH, 'w', encoding='utf-8') as f:
                    f.writelines(index_lines)
                if HAS_RICH:
                    print_success(f"Successfully updated {os.path.basename(INDEX_PATH)} with categorized orphaned files.")
                else:
                    print(f"Successfully updated {os.path.basename(INDEX_PATH)} with categorized orphaned files.")
            except Exception as e:
                if HAS_RICH:
                    print_error(f"Error writing updated {os.path.basename(INDEX_PATH)}: {e}")
                else:
                    print(f"Error writing updated {os.path.basename(INDEX_PATH)}: {e}")
    # --- End Update Index ---

    # Top tags table
    print_info("Top 10 Most Used Tags:")
    top_tags = tag_counter.most_common(10)
    table = create_table("Top 10 Tags", ["Tag", "Count"])
    for tag, count in top_tags:
        add_table_row(table, tag, str(count))
    display_table(table)

    # Least used tags table
    print_info("Least Used Tags:")
    least_tags = tag_counter.most_common()[-10:]
    table2 = create_table("Least Used Tags", ["Tag", "Count"])
    for tag, count in least_tags:
        add_table_row(table2, tag, str(count))
    display_table(table2)

    print_success("Documentation analytics complete! 🎉")
else:
    print("\\n=== ImpressionCore Documentation Analytics ===\\n")
    print(f"Total Markdown files: {len(all_md_files)}") # Use all_md_files
    print(f"Files missing tags: {len(missing_tags_report)}") # Use report variable
    if missing_tags_report: # Use report variable
        print("Files reported as missing tags:")
        for f_path in missing_tags_report: # Use report variable
            print(f"  - {os.path.relpath(f_path, DOCS_DIR)}")
    print(f"Stale files (> {STALE_DAYS} days): {len(stale_files_report)}") # Use report variable
    print(f"Orphaned files (not in DOCUMENTATION_INDEX.md): {len(orphaned_files_report)}") # Use report variable
    print("\\nTop 10 Most Used Tags:")
    top_tags = tag_counter.most_common(10)
    for tag, count in top_tags:
        print(f"  {tag}: {count}")
    print("\\nLeast Used Tags:")
    least_tags = tag_counter.most_common()[-10:]
    for tag, count in least_tags:
        print(f"  {tag}: {count}")
    print("\\nDocumentation analytics complete!\\n")

# Optionally write report
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write("# ImpressionCore Documentation Analytics Report\n\n")
    f.write(f"_Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}_\\n\\n")
    f.write(f"**Total Markdown files:** {len(all_md_files)}\\n\\n") # Use all_md_files
    f.write(f"**Files missing tags:** {len(missing_tags_report)}\\n") # Use report variable
    for m in missing_tags_report: # Use report variable
        f.write(f"  - {os.path.relpath(m, DOCS_DIR)}\\n")
    f.write(f"\\n**Stale files (> {STALE_DAYS} days):** {len(stale_files_report)}\\n") # Use report variable
    for m, d in stale_files_report: # Use report variable
        f.write(f"  - {os.path.relpath(m, DOCS_DIR)} (last updated {d})\\n")
    f.write(f"\\n**Orphaned files (not in DOCUMENTATION_INDEX.md, based on initial scan):** {len(orphaned_files_report)}\\n") # Use report variable
    for m in orphaned_files_report: # Use report variable
        f.write(f"  - {os.path.relpath(m, DOCS_DIR)}\\n")
    f.write(f"\\n**Top 10 Most Used Tags:**\\n")
    for tag, count in tag_counter.most_common(10):
        f.write(f"  - {tag}: {count}\\n")
    f.write(f"\\n**Least Used Tags:**\\n")
    for tag, count in tag_counter.most_common()[-10:]:
        f.write(f"  - {tag}: {count}\\n")
    f.write("\n---\n")
    f.write("For details, see the tag table and DOCUMENTATION_INDEX.md.\n")
