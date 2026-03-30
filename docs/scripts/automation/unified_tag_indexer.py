#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #api #docs\scripts\automation\unified_tag_indexer.py #documentation #inference #python #pytorch #source_code #testing #training #transformer #web_interface  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** ImpressionCore Team  
**Tags:** #api #docs\scripts\automation\unified_tag_indexer.py #documentation #inference #python #pytorch #source_code #testing #training #transformer #web_interface  
**Category:** Source Code  
**Status:** Active

"""
Enhanced Tag Indexer for IDS-Tagging Integration
================================================

Extends the existing tag system to index both documentation and source code files,
creating a unified tracking system for the ImpressionCore project.

Author: GitHub Copilot
Created: 2025-01-14
Last Modified: 2025-01-14
"""

import os
import re
import sys
import ast
import yaml
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional

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

# Regex patterns for documentation
yaml_frontmatter = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL | re.MULTILINE)
hashtag_pattern = re.compile(r'#([a-zA-Z0-9_-]+)')
heading_pattern = re.compile(r'^#+\s+([A-Za-z0-9 _-]+)', re.MULTILINE)

# Patterns for code files  
import_pattern = re.compile(r'^(?:from|import)\s+([a-zA-Z0-9_.]+)', re.MULTILINE)
class_pattern = re.compile(r'^class\s+([A-Za-z0-9_]+)', re.MULTILINE)
function_pattern = re.compile(r'^def\s+([a-zA-Z0-9_]+)', re.MULTILINE)
decorator_pattern = re.compile(r'^@([a-zA-Z0-9_.]+)', re.MULTILINE)

DOCS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

DOCUMENTATION_CATEGORIES = ["user", "developer", "process", "reference", "archive", "strategic", "assets"]
CODE_CATEGORIES = ["core", "models", "training", "inference", "data", "utils", "web", "api", "tests"]

class UnifiedTagIndexer:
    """Enhanced tag indexer for both documentation and source code files."""
    
    def __init__(self):
        self.tag_index = defaultdict(list)
        self.file_metadata = {}
        
    def extract_doc_tags(self, file_path: str) -> Set[str]:
        """Extract tags from documentation files."""
        tags = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract YAML frontmatter tags
            yaml_match = yaml_frontmatter.search(content)
            if yaml_match:
                try:
                    frontmatter = yaml.safe_load(yaml_match.group(1))
                    if isinstance(frontmatter, dict) and 'tags' in frontmatter:
                        if isinstance(frontmatter['tags'], list):
                            tags.update(frontmatter['tags'])
                        elif isinstance(frontmatter['tags'], str):
                            tags.update(frontmatter['tags'].split(','))
                except yaml.YAMLError:
                    pass
            
            # Extract hashtags
            hashtags = hashtag_pattern.findall(content)
            tags.update(hashtags)
            
            # Extract normalized headings as tags
            headings = heading_pattern.findall(content)
            for heading in headings:
                normalized = re.sub(r'[^\w\s-]', '', heading.lower())
                normalized = re.sub(r'\s+', '_', normalized.strip())
                if normalized and len(normalized) > 2:
                    tags.add(normalized)
                    
            # Add year tag
            tags.add('2025')
            
            # Add category based on file path
            rel_path = os.path.relpath(file_path, DOCS_ROOT)
            if '/' in rel_path:
                category = rel_path.split('/')[0]
                if category in DOCUMENTATION_CATEGORIES:
                    tags.add(category)
                    
        except Exception as e:
            logger.warning(f"Error extracting tags from {file_path}: {e}")
            
        return tags
    
    def extract_code_tags(self, file_path: str) -> Set[str]:
        """Extract tags from Python source code files."""
        tags = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                  # Parse AST for more reliable extraction
            try:
                # Suppress warnings during AST parsing to avoid invalid escape sequence warnings
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", SyntaxWarning)
                    tree = ast.parse(content)
                
                # Extract class names
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        tags.add(f"class_{node.name.lower()}")
                        tags.add("class")
                        
                    elif isinstance(node, ast.FunctionDef):
                        tags.add(f"func_{node.name.lower()}")
                        tags.add("function")
                        
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            module_parts = alias.name.split('.')
                            tags.add(f"import_{module_parts[0]}")
                            
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_parts = node.module.split('.')
                            tags.add(f"import_{module_parts[0]}")
                            
            except (SyntaxError, ValueError):
                # Fallback to regex for malformed files or files with syntax issues
                pass
                
            # Extract imports using regex as backup
            imports = import_pattern.findall(content)
            for imp in imports:
                module_parts = imp.split('.')
                tags.add(f"import_{module_parts[0]}")
                
            # Extract decorators
            decorators = decorator_pattern.findall(content)
            for dec in decorators:
                tags.add(f"decorator_{dec}")
                
            # Add file type tags
            if file_path.endswith('.py'):
                tags.add('python')
                tags.add('source_code')
                
            # Add category based on file path
            rel_path = os.path.relpath(file_path, SRC_ROOT)
            if '/' in rel_path:
                category = rel_path.split('/')[0]
                if category in CODE_CATEGORIES:
                    tags.add(category)
                    
            # Add framework-specific tags
            if any(keyword in content.lower() for keyword in ['pytorch', 'torch']):
                tags.add('pytorch')
            if any(keyword in content.lower() for keyword in ['transformers', 'huggingface']):
                tags.add('transformers')
            if any(keyword in content.lower() for keyword in ['flask', 'fastapi']):
                tags.add('web_framework')
                
        except Exception as e:
            logger.warning(f"Error extracting code tags from {file_path}: {e}")
            
        return tags
    
    def build_unified_index(self) -> Dict[str, List[str]]:
        """Build unified tag index for both documentation and code files."""
        print_info("🔍 Building unified tag index...")
          # Index documentation files
        doc_count = 0
        for root, dirs, files in os.walk(DOCS_ROOT):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                    
                    tags = self.extract_doc_tags(file_path)
                    if tags:
                        # Convert all tags to strings and sort
                        tag_list = sorted([str(tag) for tag in tags])
                        self.tag_index[rel_path] = tag_list
                        self.file_metadata[rel_path] = {
                            'type': 'documentation',
                            'category': rel_path.split('/')[1] if '/' in rel_path else 'root',
                            'size': os.path.getsize(file_path),
                            'modified': os.path.getmtime(file_path)
                        }
                        doc_count += 1
        
        # Index source code files
        code_count = 0
        for root, dirs, files in os.walk(SRC_ROOT):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                    
                    tags = self.extract_code_tags(file_path)
                    if tags:
                        # Convert all tags to strings and sort
                        tag_list = sorted([str(tag) for tag in tags])
                        self.tag_index[rel_path] = tag_list
                        self.file_metadata[rel_path] = {
                            'type': 'source_code',
                            'category': rel_path.split('/')[1] if '/' in rel_path else 'root',
                            'size': os.path.getsize(file_path),
                            'modified': os.path.getmtime(file_path)
                        }
                        code_count += 1
        
        print_success(f"✅ Indexed {doc_count} documentation files and {code_count} source files")
        return dict(self.tag_index)
    
    def save_unified_index(self, output_path: str = None):
        """Save the unified tag index to YAML file."""
        if output_path is None:
            output_path = os.path.join(DOCS_ROOT, 'unified_tags_index.yaml')
            
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(dict(self.tag_index), f, default_flow_style=False, sort_keys=True)
            
        print_success(f"💾 Saved unified tag index to {output_path}")
    
    def save_metadata(self, output_path: str = None):
        """Save file metadata to separate YAML file."""
        if output_path is None:
            output_path = os.path.join(DOCS_ROOT, 'file_metadata.yaml')
            
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.file_metadata, f, default_flow_style=False, sort_keys=True)
            
        print_success(f"💾 Saved file metadata to {output_path}")
    
    def search_by_tag(self, tag: str) -> List[str]:
        """Search files by tag."""
        matching_files = []
        for file_path, tags in self.tag_index.items():
            if tag.lower() in [t.lower() for t in tags]:
                matching_files.append(file_path)
        return matching_files
    
    def get_tag_statistics(self) -> Dict:
        """Get statistics about tag usage."""
        tag_counts = Counter()
        file_type_counts = Counter()
        
        for file_path, tags in self.tag_index.items():
            for tag in tags:
                tag_counts[tag] += 1
            
            if file_path in self.file_metadata:
                file_type_counts[self.file_metadata[file_path]['type']] += 1
        
        return {
            'total_files': len(self.tag_index),
            'total_tags': len(tag_counts),
            'most_common_tags': tag_counts.most_common(10),
            'file_types': dict(file_type_counts)
        }

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Tag Indexer for IDS-Tagging Integration')
    parser.add_argument('--build', action='store_true', help='Build unified tag index')
    parser.add_argument('--search', type=str, help='Search files by tag')
    parser.add_argument('--stats', action='store_true', help='Show tag statistics')
    parser.add_argument('--output', type=str, help='Output file path for index')
    
    args = parser.parse_args()
    
    indexer = UnifiedTagIndexer()
    
    if args.build:
        indexer.build_unified_index()
        indexer.save_unified_index(args.output)
        indexer.save_metadata()
        
    elif args.search:
        # Load existing index
        index_file = args.output or os.path.join(DOCS_ROOT, 'unified_tags_index.yaml')
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                indexer.tag_index = yaml.safe_load(f)
            
            results = indexer.search_by_tag(args.search)
            print_info(f"🔍 Found {len(results)} files with tag '{args.search}':")
            for file_path in results:
                print(f"  - {file_path}")
        else:
            print_error("Index file not found. Run with --build first.")
            
    elif args.stats:
        # Load existing index
        index_file = args.output or os.path.join(DOCS_ROOT, 'unified_tags_index.yaml')
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                indexer.tag_index = yaml.safe_load(f)
                
            metadata_file = os.path.join(DOCS_ROOT, 'file_metadata.yaml')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    indexer.file_metadata = yaml.safe_load(f)
            
            stats = indexer.get_tag_statistics()
            print_info("📊 Tag Index Statistics:")
            print(f"  Total Files: {stats['total_files']}")
            print(f"  Total Tags: {stats['total_tags']}")
            print(f"  File Types: {stats['file_types']}")
            print("\n  Most Common Tags:")
            for tag, count in stats['most_common_tags']:
                print(f"    {tag}: {count}")
        else:
            print_error("Index file not found. Run with --build first.")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
