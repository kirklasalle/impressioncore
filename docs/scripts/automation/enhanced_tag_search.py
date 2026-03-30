#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\automation\enhanced_tag_search.py #documentation #inference #python #source_code #training  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** Kirk LaSalle  
**Tags:** #api #docs\scripts\automation\enhanced_tag_search.py #documentation #inference #python #source_code #training  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore Documentation System - Enhanced Tag Search and Indexing

Advanced tagging system for document and code references with quick search capabilities.
This is the core component for the IDS search functionality.

Author: Kirk LaSalle <kirk@impressioncore.ai>
Project: ImpressionCore Documentation System
License: MIT
Created: 2025-06-05
"""

import os
import re
import sys
import json
import yaml
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional
import argparse

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.core.utils.rich_enhancements import (
        console, print_info, print_success, print_warning, print_error,
        create_table, add_table_row, display_table, create_panel, create_header,
        create_progress_bar, create_spinner
    )
    from src.core.utils.rich_logging import setup_rich_logging
    from src.core.utils.rich_status_animation import StatusAnimation
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
    
    def create_panel(text, title):
        print(f"\n=== {title} ===")
        print(text)
        print("=" * (len(title) + 8))
    
    def create_header(title, subtitle=None):
        print(f"\n{'='*50}")
        print(f"  {title}")
        if subtitle:
            print(f"  {subtitle}")
        print(f"{'='*50}")
    
    def create_progress_bar(*args, **kwargs):
        return None
    
    def create_spinner(*args, **kwargs):
        return None
    
    class StatusAnimation:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def update(self, *args):
            pass
    
    HAS_RICH = False
    logger = print

# Configuration
DOCS_ROOT = Path(__file__).parent.parent.parent.parent / "docs"
SRC_ROOT = Path(__file__).parent.parent.parent.parent / "src"
CATEGORIES = ["user", "developer", "process", "reference", "archive", "api", "technical", "strategic"]
SOURCE_CATEGORIES = ["src", "core", "utils", "models", "data", "training", "inference"]

# Regex patterns
yaml_frontmatter = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL | re.MULTILINE)
hashtag_pattern = re.compile(r'#([a-zA-Z0-9_-]+)')
heading_pattern = re.compile(r'^#+\s+([A-Za-z0-9 _-]+)', re.MULTILINE)
comment_tag_pattern = re.compile(r'#\s*(?:Tags?|TAG):\s*\[([^\]]+)\]', re.IGNORECASE)
python_class_pattern = re.compile(r'^class\s+([A-Za-z0-9_]+)', re.MULTILINE)
python_function_pattern = re.compile(r'^def\s+([A-Za-z0-9_]+)', re.MULTILINE)


class EnhancedTagIndexer:
    """Enhanced tag indexing system for ImpressionCore documentation and code."""
    
    def __init__(self):
        self.tag_index = {}
        self.reverse_index = defaultdict(list)  # tag -> list of files
        self.code_index = {}  # For Python code files
        self.category_stats = defaultdict(int)
        
    def extract_doc_tags(self, file_path: Path) -> Set[str]:
        """Extract tags from markdown documentation files."""
        tags = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return tags        
        # 1. YAML frontmatter tags
        yaml_match = yaml_frontmatter.search(content)
        if yaml_match:
            try:
                frontmatter = yaml.safe_load(yaml_match.group(1))
                if isinstance(frontmatter, dict) and 'tags' in frontmatter:
                    yaml_tags = frontmatter['tags']
                    if isinstance(yaml_tags, list):
                        # Handle mixed types in tag lists (strings, integers, etc.)
                        tags.update(str(tag).strip() for tag in yaml_tags if str(tag).strip())
                    elif isinstance(yaml_tags, str):
                        tags.update(tag.strip() for tag in yaml_tags.split(',') if tag.strip())
            except yaml.YAMLError:
                # Fallback to simple parsing
                for line in yaml_match.group(1).splitlines():
                    if line.strip().startswith('tags:'):
                        tag_str = line.split(':', 1)[1].strip().strip('[]')
                        # Handle mixed types in simple parsing too
                        tags.update(str(t).strip().strip("'\"") for t in tag_str.split(',') if str(t).strip())
        
        # 2. Hashtags in body
        tags.update(hashtag_pattern.findall(content))
        
        # 3. Headings as tags (selective)
        for heading in heading_pattern.findall(content):
            heading_tag = heading.strip().lower().replace(' ', '_').replace('-', '_')
            if 3 <= len(heading_tag) <= 25 and '_' not in heading_tag[:2]:
                tags.add(heading_tag)
        
        # 4. File-based tags
        stem = file_path.stem.lower()
        tags.add(stem)
        
        # 5. Category tags
        relative_path = file_path.relative_to(DOCS_ROOT)
        if len(relative_path.parts) > 1:
            tags.add(relative_path.parts[0])  # Category
        
        return tags
    
    def extract_code_tags(self, file_path: Path) -> Dict[str, any]:
        """Extract tags and metadata from Python code files."""
        metadata = {
            'tags': set(),
            'classes': [],
            'functions': [],
            'imports': [],
            'description': ''
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return metadata
        
        # Extract tags from comments
        tag_matches = comment_tag_pattern.findall(content)
        for match in tag_matches:
            tags_str = match.strip()
            metadata['tags'].update(tag.strip() for tag in tags_str.split(',') if tag.strip())
        
        # Extract classes and functions
        metadata['classes'] = python_class_pattern.findall(content)
        metadata['functions'] = python_function_pattern.findall(content)
        
        # Extract imports
        import_lines = [line.strip() for line in content.split('\n') 
                       if line.strip().startswith(('import ', 'from '))]
        metadata['imports'] = import_lines[:10]  # Limit to first 10
        
        # Extract description from docstring
        docstring_match = re.search(r'"""([^"]+)"""', content, re.DOTALL)
        if docstring_match:
            metadata['description'] = docstring_match.group(1).strip()[:200]  # First 200 chars
        
        # Add automatic tags
        metadata['tags'].add(file_path.stem.lower())
        metadata['tags'].add('python')
        
        # Add parent directory as tag
        relative_path = file_path.relative_to(SRC_ROOT)
        if len(relative_path.parts) > 1:
            metadata['tags'].add(relative_path.parts[0])
        
        return metadata
    
    def build_documentation_index(self):
        """Build index for documentation files."""
        print_info("Indexing documentation files...")
        
        for category in CATEGORIES:
            category_path = DOCS_ROOT / category
            if not category_path.exists():
                continue
                
            for md_file in category_path.glob('**/*.md'):
                try:
                    tags = self.extract_doc_tags(md_file)
                    relative_path = str(md_file.relative_to(DOCS_ROOT))
                    
                    self.tag_index[relative_path] = {
                        'type': 'documentation',
                        'tags': sorted(tags),
                        'category': category,
                        'file_size': md_file.stat().st_size,
                        'modified': md_file.stat().st_mtime
                    }
                    
                    # Update reverse index
                    for tag in tags:
                        self.reverse_index[tag].append(relative_path)
                    
                    self.category_stats[category] += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing {md_file}: {e}")
    
    def build_code_index(self):
        """Build index for Python source code files."""
        print_info("Indexing Python source code...")
        
        for py_file in SRC_ROOT.glob('**/*.py'):
            try:
                metadata = self.extract_code_tags(py_file)
                relative_path = str(py_file.relative_to(SRC_ROOT))
                
                self.code_index[relative_path] = {
                    'type': 'source_code',
                    'tags': sorted(metadata['tags']),
                    'classes': metadata['classes'],
                    'functions': metadata['functions'],
                    'imports': metadata['imports'][:5],  # Limit for size
                    'description': metadata['description'],
                    'file_size': py_file.stat().st_size,
                    'modified': py_file.stat().st_mtime
                }
                
                # Update reverse index
                for tag in metadata['tags']:
                    self.reverse_index[tag].append(f"src/{relative_path}")
                
            except Exception as e:
                logger.warning(f"Error processing {py_file}: {e}")
    
    def search_tags(self, query: str, case_sensitive: bool = False) -> List[Tuple[str, Dict]]:
        """Search for files by tag."""
        if not case_sensitive:
            query = query.lower()
        
        results = []
        
        # Exact match
        if query in self.reverse_index:
            for file_path in self.reverse_index[query]:
                if file_path.startswith('src/'):
                    file_info = self.code_index.get(file_path[4:], {})
                else:
                    file_info = self.tag_index.get(file_path, {})
                results.append((file_path, file_info))
        
        # Partial match
        for tag in self.reverse_index:
            if query in tag.lower() if not case_sensitive else query in tag:
                if tag != query:  # Avoid duplicates from exact match
                    for file_path in self.reverse_index[tag]:
                        if file_path.startswith('src/'):
                            file_info = self.code_index.get(file_path[4:], {})
                        else:
                            file_info = self.tag_index.get(file_path, {})
                        results.append((file_path, file_info))
        
        # Remove duplicates and sort
        unique_results = {}
        for path, info in results:
            if path not in unique_results:
                unique_results[path] = info
        
        return sorted(unique_results.items())
    
    def search_content(self, query: str) -> List[Tuple[str, Dict]]:
        """Search within file content (classes, functions, descriptions)."""
        results = []
        query_lower = query.lower()
        
        # Search code files
        for file_path, metadata in self.code_index.items():
            match_score = 0
            
            # Check classes
            for class_name in metadata.get('classes', []):
                if query_lower in class_name.lower():
                    match_score += 10
            
            # Check functions
            for func_name in metadata.get('functions', []):
                if query_lower in func_name.lower():
                    match_score += 5
            
            # Check description
            description = metadata.get('description', '')
            if query_lower in description.lower():
                match_score += 2
            
            if match_score > 0:
                metadata['match_score'] = match_score
                results.append((f"src/{file_path}", metadata))
        
        # Sort by match score
        return sorted(results, key=lambda x: x[1].get('match_score', 0), reverse=True)
    
    def generate_tag_statistics(self) -> Dict:
        """Generate comprehensive tag usage statistics."""
        stats = {
            'total_files': len(self.tag_index) + len(self.code_index),
            'total_tags': len(self.reverse_index),
            'documentation_files': len(self.tag_index),
            'source_files': len(self.code_index),
            'category_breakdown': dict(self.category_stats),
            'top_tags': [],
            'orphaned_files': [],
            'heavily_tagged_files': []
        }
        
        # Top tags by usage
        tag_counts = {tag: len(files) for tag, files in self.reverse_index.items()}
        stats['top_tags'] = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Files with no tags
        for file_path, metadata in self.tag_index.items():
            if not metadata.get('tags'):
                stats['orphaned_files'].append(file_path)
        
        # Heavily tagged files (more than 15 tags)
        for file_path, metadata in self.tag_index.items():
            if len(metadata.get('tags', [])) > 15:
                stats['heavily_tagged_files'].append((file_path, len(metadata.get('tags', []))))
        
        return stats
    
    def save_indices(self):
        """Save all indices to files."""
        try:
            # Save main tag index
            with open(DOCS_ROOT / 'tags_index.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(self.tag_index, f, default_flow_style=False, allow_unicode=True)
            
            # Save code index
            with open(DOCS_ROOT / 'code_index.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(self.code_index, f, default_flow_style=False, allow_unicode=True)
            
            # Save reverse index (for fast searches)
            reverse_index_dict = {tag: files for tag, files in self.reverse_index.items()}
            with open(DOCS_ROOT / 'reverse_tag_index.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(reverse_index_dict, f, default_flow_style=False, allow_unicode=True)
            
            # Save unified index (simple format for backwards compatibility)            with open(DOCS_ROOT / 'unified_tags_index.yaml', 'w', encoding='utf-8') as f:
                unified = {}
                for file_path, metadata in self.tag_index.items():
                    unified[file_path] = metadata.get('tags', [])
                for file_path, metadata in self.code_index.items():
                    unified[f"src/{file_path}"] = metadata.get('tags', [])
                yaml.dump(unified, f, default_flow_style=False, allow_unicode=True)
            
            print_success("All indices saved successfully.")
            
        except Exception as e:
            print_error(f"Error saving indices: {e}")

    def load_indices(self):
        """Load all indices from files."""
        try:
            # Load main tag index
            tags_file = DOCS_ROOT / 'tags_index.yaml'
            if tags_file.exists():
                with open(tags_file, 'r', encoding='utf-8') as f:
                    self.tag_index = yaml.safe_load(f) or {}
            
            # Load code index
            code_file = DOCS_ROOT / 'code_index.yaml'
            if code_file.exists():
                with open(code_file, 'r', encoding='utf-8') as f:
                    self.code_index = yaml.safe_load(f) or {}
            
            # Load reverse index
            reverse_file = DOCS_ROOT / 'reverse_tag_index.yaml'
            if reverse_file.exists():
                with open(reverse_file, 'r', encoding='utf-8') as f:
                    reverse_data = yaml.safe_load(f) or {}
                    self.reverse_index = defaultdict(list)
                    for tag, files in reverse_data.items():
                        self.reverse_index[tag] = files
            else:
                # Rebuild reverse index from main indices
                self.reverse_index = defaultdict(list)
                for file_path, metadata in self.tag_index.items():
                    for tag in metadata.get('tags', []):
                        self.reverse_index[tag].append(file_path)
                for file_path, metadata in self.code_index.items():
                    for tag in metadata.get('tags', []):
                        self.reverse_index[tag].append(f"src/{file_path}")
            
            print_info(f"Loaded indices: {len(self.tag_index)} docs, {len(self.code_index)} code files")
            return True
            
        except Exception as e:
            print_warning(f"Error loading indices: {e}")
            return False
    
    def display_statistics(self):
        """Display comprehensive statistics."""
        stats = self.generate_tag_statistics()
        
        if HAS_RICH:
            # Main statistics panel
            stats_text = f"""
Total Files Indexed: {stats['total_files']}
Documentation Files: {stats['documentation_files']}
Source Code Files: {stats['source_files']}
Total Unique Tags: {stats['total_tags']}
"""
            console.print(create_panel(stats_text, "Index Statistics"))
              # Top tags table
            table = create_table("Top 15 Most Used Tags", ["Tag", "File Count", "Percentage"])
            total_files = stats['total_files']
            for tag, count in stats['top_tags'][:15]:
                percentage = f"{(count/total_files)*100:.1f}%"
                add_table_row(table, tag, str(count), percentage)
            display_table(table)
            
            # Category breakdown
            if stats['category_breakdown']:
                table = create_table("Documentation Categories", ["Category", "File Count"])
                for category, count in sorted(stats['category_breakdown'].items()):
                    add_table_row(table, category, str(count))
                display_table(table)
                
        else:
            # Fallback text display
            print("\n=== Index Statistics ===")
            print(f"Total Files Indexed: {stats['total_files']}")
            print(f"Documentation Files: {stats['documentation_files']}")
            print(f"Source Code Files: {stats['source_files']}")
            print(f"Total Unique Tags: {stats['total_tags']}")
            
            print("\n=== Top Tags ===")
            for i, (tag, count) in enumerate(stats['top_tags'][:10], 1):
                print(f"{i:2d}. {tag:20} ({count} files)")


    def display_search_results_enhanced(self, results: List[Tuple[str, Dict]], 
                                       search_type: str, query: str) -> None:
        """Display search results with enhanced formatting and separate sections."""
        if not results:
            print_warning(f"No files found matching {search_type} '{query}'")
            return
        
        # Separate documentation and source code results
        doc_results = []
        code_results = []
        
        for file_path, metadata in results:
            if file_path.startswith('src/'):
                code_results.append((file_path, metadata))
            else:
                doc_results.append((file_path, metadata))
        
        # Display header with animation
        if HAS_RICH:
            create_header(
                f"Search Results for '{query}'",
                f"Found {len(results)} files ({len(doc_results)} docs, {len(code_results)} code)"
            )
        
        # Documentation section
        if doc_results:
            self._display_documentation_section(doc_results, search_type)
        
        # Source code section  
        if code_results:
            self._display_code_section(code_results, search_type)
        
        # Summary statistics
        if HAS_RICH:
            self._display_search_summary(doc_results, code_results, search_type)
    
    def _display_documentation_section(self, doc_results: List[Tuple[str, Dict]], 
                                     search_type: str) -> None:
        """Display documentation results in a rich table."""
        if not doc_results:
            return
            
        if HAS_RICH:
            console.print()
            doc_panel = create_panel(
                f"Found {len(doc_results)} documentation files",
                "📚 Documentation Files"
            )
            console.print(doc_panel)
            
            # Create table for documentation
            doc_table = create_table(
                "Documentation Results", 
                ["File Path", "Category", "Tags", "Description"]
            )
            
            for file_path, metadata in doc_results[:20]:  # Limit display
                category = self._get_file_category(file_path)
                tags = ", ".join(metadata.get('tags', [])[:5])  # Show first 5 tags
                if len(metadata.get('tags', [])) > 5:
                    tags += "..."
                description = metadata.get('description', '')[:60]
                if len(metadata.get('description', '')) > 60:
                    description += "..."
                
                add_table_row(doc_table, file_path, category, tags, description)
            
            display_table(doc_table)
            
            if len(doc_results) > 20:
                print_info(f"... and {len(doc_results) - 20} more documentation files")
        else:
            print(f"\n=== Documentation Files ({len(doc_results)}) ===")
            for file_path, metadata in doc_results:
                print(f"  {file_path}")
    
    def _display_code_section(self, code_results: List[Tuple[str, Dict]], 
                            search_type: str) -> None:
        """Display source code results in a rich table."""
        if not code_results:
            return
            
        if HAS_RICH:
            console.print()
            code_panel = create_panel(
                f"Found {len(code_results)} source code files",
                "🐍 Source Code Files"
            )
            console.print(code_panel)
            
            # Create table for source code
            code_table = create_table(
                "Source Code Results",
                ["File Path", "Classes", "Functions", "Score", "Description"]
            )
            
            for file_path, metadata in code_results[:20]:  # Limit display
                classes = ", ".join(metadata.get('classes', [])[:3])
                if len(metadata.get('classes', [])) > 3:
                    classes += "..."
                    
                functions = ", ".join(metadata.get('functions', [])[:3])
                if len(metadata.get('functions', [])) > 3:
                    functions += "..."
                
                score = str(metadata.get('match_score', ''))
                description = metadata.get('description', '')[:50]
                if len(metadata.get('description', '')) > 50:
                    description += "..."
                
                add_table_row(code_table, file_path, classes, functions, score, description)
            
            display_table(code_table)
            
            if len(code_results) > 20:
                print_info(f"... and {len(code_results) - 20} more source code files")
        else:
            print(f"\n=== Source Code Files ({len(code_results)}) ===")
            for file_path, metadata in code_results:
                score = metadata.get('match_score', '')
                print(f"  {file_path} {f'(score: {score})' if score else ''}")
    
    def _display_search_summary(self, doc_results: List[Tuple[str, Dict]], 
                              code_results: List[Tuple[str, Dict]], 
                              search_type: str) -> None:
        """Display search summary statistics."""
        if not HAS_RICH:
            return
            
        console.print()
        
        # Category breakdown for documentation
        doc_categories = {}
        for file_path, _ in doc_results:
            category = self._get_file_category(file_path)
            doc_categories[category] = doc_categories.get(category, 0) + 1
        
        # Module breakdown for source code
        code_modules = {}
        for file_path, _ in code_results:
            if 'src/' in file_path:
                parts = file_path.split('/')
                if len(parts) > 2:
                    module = parts[1]  # First directory after src/
                    code_modules[module] = code_modules.get(module, 0) + 1
        
        # Create summary table
        summary_table = create_table(
            "Search Summary",
            ["Type", "Count", "Top Categories/Modules"]
        )
        
        # Documentation summary
        doc_top = sorted(doc_categories.items(), key=lambda x: x[1], reverse=True)[:3]
        doc_top_str = ", ".join([f"{cat}({cnt})" for cat, cnt in doc_top])
        add_table_row(summary_table, "Documentation", str(len(doc_results)), doc_top_str)
        
        # Source code summary
        code_top = sorted(code_modules.items(), key=lambda x: x[1], reverse=True)[:3] 
        code_top_str = ", ".join([f"{mod}({cnt})" for mod, cnt in code_top])
        add_table_row(summary_table, "Source Code", str(len(code_results)), code_top_str)
        
        display_table(summary_table)
    
    def _get_file_category(self, file_path: str) -> str:
        """Extract category from file path."""
        if '/' in file_path:
            return file_path.split('/')[0]
        elif '\\' in file_path:
            return file_path.split('\\')[0]
        return "root"

def interactive_search_mode(indexer: EnhancedTagIndexer):
    """Run interactive search mode."""
    # Check if we're in a proper interactive terminal
    if not sys.stdin.isatty():
        print_error("Interactive mode requires a proper terminal (TTY). Cannot run with piped input.")
        print_info("Use --search or --content flags for non-interactive searching.")
        return
    
    print_info("Enhanced Tag Search - Interactive Mode")
    print_info("Commands: 'tags <query>', 'content <query>', 'stats', 'help', 'exit'")
    
    while True:
        try:
            user_input = input("\nSearch> ").strip()
            
            if not user_input or user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'help':
                print("""
Commands:
  tags <query>     - Search by tag name
  content <query>  - Search within file content (classes, functions, etc.)
  stats           - Show index statistics
  help            - Show this help
  exit            - Exit interactive mode
""")
            elif user_input.lower() == 'stats':
                indexer.display_statistics()
                
            elif user_input.startswith('tags '):
                query = user_input[5:].strip()
                results = indexer.search_tags(query)
                indexer.display_search_results_enhanced(results, "tag", query)
                    
            elif user_input.startswith('content '):
                query = user_input[8:].strip()
                results = indexer.search_content(query)
                indexer.display_search_results_enhanced(results, "content", query)
            else:
                print_warning("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print_error(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Enhanced Tag Search and Indexing for ImpressionCore")
    parser.add_argument('--build', action='store_true', help='Build/rebuild all indices')
    parser.add_argument('--stats', action='store_true', help='Display index statistics')
    parser.add_argument('--search', type=str, help='Search for files by tag')
    parser.add_argument('--content', type=str, help='Search within file content')
    parser.add_argument('--interactive', action='store_true', help='Enter interactive search mode')
    parser.add_argument('--docs-only', action='store_true', help='Index only documentation files')
    parser.add_argument('--code-only', action='store_true', help='Index only source code files')
    
    args = parser.parse_args()
    
    indexer = EnhancedTagIndexer()
    
    # Check if we need to build or load indices
    need_indices = args.stats or args.search or args.content or args.interactive
    
    if args.build or not any([args.stats, args.search, args.content, args.interactive]):
        # Build indices
        if not args.code_only:
            indexer.build_documentation_index()
        if not args.docs_only:
            indexer.build_code_index()
        indexer.save_indices()
        
        if not any([args.stats, args.search, args.content, args.interactive]):
            indexer.display_statistics()
    elif need_indices:
        # Load existing indices for search operations
        if not indexer.load_indices():
            print_error("No indices found. Please run with --build first.")
            return
    
    if args.stats:
        indexer.display_statistics()
    
    if args.search:
        results = indexer.search_tags(args.search)
        indexer.display_search_results_enhanced(results, "tag", args.search)
    
    if args.content:
        results = indexer.search_content(args.content)
        indexer.display_search_results_enhanced(results, "content", args.content)
    
    if args.interactive:
        interactive_search_mode(indexer)


if __name__ == "__main__":
    main()
