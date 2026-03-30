#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #deployment #docs\enhanced_ids.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active
"""






import sys
import os
import subprocess
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Set up project paths
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
DOCS_ROOT = CURRENT_DIR
SCRIPTS_ROOT = DOCS_ROOT / "scripts"

# Try to import Rich for enhanced output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.text import Text
    from rich import print as rprint
    from rich.layout import Layout
    from rich.columns import Columns
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Fallback console class
class SimpleConsole:
    @staticmethod
    def print(text, style=None):
        print(text)
    
    @staticmethod
    def rule(title="", style=None):
        print("=" * 60)
        if title:
            print(f" {title} ")
            print("=" * 60)

class EnhancedIDS:
    """Enhanced ImpressionCore Documentation System with unified tagging."""
    
    def __init__(self):
        self.version = "2.0.0-enhanced"
        self.console = Console() if HAS_RICH else SimpleConsole()
        self.unified_index = {}
        self.file_metadata = {}
        self.load_indices()
    
    def load_indices(self):
        """Load unified tag index and metadata."""
        unified_index_path = DOCS_ROOT / "unified_tags_index.yaml"
        metadata_path = DOCS_ROOT / "file_metadata.yaml"
        
        try:
            if unified_index_path.exists():
                with open(unified_index_path, 'r') as f:
                    self.unified_index = yaml.safe_load(f) or {}
                    
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.file_metadata = yaml.safe_load(f) or {}
                    
        except Exception as e:
            self.console.print(f"Warning: Could not load indices: {e}")
    
    def refresh_indices(self):
        """Refresh indices - compatibility method for MCP server."""
        # Clear current state
        self.unified_index.clear()
        self.file_metadata.clear()
        
        # Reload indices
        self.load_indices()
        
        return len(self.unified_index) > 0 or len(self.file_metadata) > 0
    
    def display_header(self):
        """Display the enhanced IDS header."""
        if HAS_RICH:
            header_text = Text()
            header_text.append("ImpressionCore Documentation System", style="bold blue")
            header_text.append(" (Enhanced)", style="bold green")
            header_text.append(f" v{self.version}", style="dim")
            
            panel = Panel(
                header_text,
                subtitle="Unified Documentation & Codebase Tracking",
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(panel)
        else:
            print("=" * 60)
            print(f"ImpressionCore Documentation System (Enhanced) v{self.version}")
            print("Unified Documentation & Codebase Tracking")
            print("=" * 60)
    
    def display_main_menu(self):
        """Display the enhanced main menu."""
        if HAS_RICH:
            # Create sections
            doc_section = Panel(
                "• Documentation Index\n"
                "• Browse by Category\n" 
                "• View Recent Updates\n"
                "• Generate Reports",
                title="📚 Documentation",
                border_style="cyan"
            )
            
            code_section = Panel(
                "• Code Index Search\n"
                "• Function/Class Lookup\n"
                "• Import Analysis\n"
                "• File Dependencies",
                title="💻 Codebase",
                border_style="green"
            )
            
            search_section = Panel(
                "• Unified Tag Search\n"
                "• Cross-Reference Lookup\n"
                "• Semantic Search\n"
                "• Advanced Filters",
                title="🔍 Search & Discovery",
                border_style="yellow"
            )
            
            tools_section = Panel(
                "• Build Indices\n"
                "• System Health Check\n"
                "• Analytics & Stats\n"
                "• Maintenance Tools",
                title="🛠️ Tools & Automation",
                border_style="red"
            )
              # Display in columns
            columns = Columns([doc_section, code_section, search_section, tools_section])
            self.console.print(columns)
        else:
            print("\nMain Menu:")
            print("-" * 30)
            print("1. Documentation Management")
            print("2. Codebase Analysis")
            print("3. Search & Discovery")
            print("4. Tools & Automation")
    
    def unified_search(self, query: str, file_type: str = "all") -> List[Tuple[str, List[str]]]:
        """Perform unified search across documentation and code."""
        results = []
        query_lower = query.lower()
        
        for file_path, tags in self.unified_index.items():
            # Filter by file type
            if file_type != "all":
                metadata = self.file_metadata.get(file_path, {})
                if metadata.get('type') != file_type:
                    continue
            
            # Check if query matches any tag
            matching_tags = [tag for tag in tags if query_lower in tag.lower()]
            
            # Also check if query matches file path or filename
            file_path_lower = file_path.lower()
            file_name = Path(file_path).name.lower()
            
            if matching_tags or query_lower in file_path_lower or query_lower in file_name:
                # If found in file path but not in tags, mark as path match
                if not matching_tags and (query_lower in file_path_lower or query_lower in file_name):
                    matching_tags = ["path_match"]
                results.append((file_path, matching_tags))
        
        return results
    
    def search_by_tag(self, tag: str, exact: bool = False) -> List[str]:
        """Search files by specific tag."""
        matching_files = []
        tag_lower = tag.lower()
        
        for file_path, tags in self.unified_index.items():
            if exact:
                if tag in tags:
                    matching_files.append(file_path)
            else:
                if any(tag_lower in t.lower() for t in tags):
                    matching_files.append(file_path)
        
        return matching_files
    
    def get_file_info(self, file_path: str) -> Dict:
        """Get detailed information about a file."""
        info = {
            'path': file_path,
            'tags': self.unified_index.get(file_path, []),
            'metadata': self.file_metadata.get(file_path, {})
        }
        
        # Add file system info
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            info['exists'] = True
            info['size'] = full_path.stat().st_size
            info['modified'] = full_path.stat().st_mtime
        else:
            info['exists'] = False
            
        return info
    
    def display_search_results(self, results: List[Tuple[str, List[str]]], title: str = "Search Results"):
        """Display search results in a formatted table."""
        if not results:
            self.console.print("No results found.")
            return
            
        if HAS_RICH:
            table = Table(title=title, show_header=True, header_style="bold blue")
            table.add_column("File", style="cyan", width=50)
            table.add_column("Type", style="yellow", width=12)
            table.add_column("Category", style="green", width=12) 
            table.add_column("Matching Tags", style="white", width=40)
            
            for file_path, matching_tags in results:
                metadata = self.file_metadata.get(file_path, {})
                file_type = metadata.get('type', 'unknown')
                category = metadata.get('category', 'unknown')
                tags_str = ", ".join(matching_tags[:5])  # Show first 5 tags
                if len(matching_tags) > 5:
                    tags_str += f" (+{len(matching_tags) - 5} more)"
                
                table.add_row(file_path, file_type, category, tags_str)
            
            self.console.print(table)
        else:
            print(f"\n{title}:")
            print("-" * 60)
            for i, (file_path, matching_tags) in enumerate(results, 1):
                metadata = self.file_metadata.get(file_path, {})
                print(f"{i}. {file_path}")
                print(f"   Type: {metadata.get('type', 'unknown')}")
                print(f"   Tags: {', '.join(matching_tags[:3])}")
                if len(matching_tags) > 3:
                    print(f"         (+{len(matching_tags) - 3} more)")
                print()
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about the unified index."""
        from collections import Counter
        
        stats = {
            'total_files': len(self.unified_index),
            'total_tags': 0,
            'file_types': Counter(),
            'categories': Counter(),
            'tag_usage': Counter(),
            'largest_files': [],
            'most_tagged_files': []
        }
        
        all_tags = []
        file_tag_counts = []
        
        for file_path, tags in self.unified_index.items():
            all_tags.extend(tags)
            file_tag_counts.append((file_path, len(tags)))
            
            metadata = self.file_metadata.get(file_path, {})
            stats['file_types'][metadata.get('type', 'unknown')] += 1
            stats['categories'][metadata.get('category', 'unknown')] += 1
        
        stats['total_tags'] = len(set(all_tags))
        stats['tag_usage'] = Counter(all_tags)
        stats['most_tagged_files'] = sorted(file_tag_counts, key=lambda x: x[1], reverse=True)[:10]
        
        return stats
    
    def display_statistics(self):
        """Display comprehensive statistics."""
        stats = self.get_statistics()
        
        if HAS_RICH:
            # Overview panel
            overview = Panel(
                f"Total Files: {stats['total_files']}\n"
                f"Total Unique Tags: {stats['total_tags']}\n"
                f"Documentation Files: {stats['file_types'].get('documentation', 0)}\n"
                f"Source Code Files: {stats['file_types'].get('source_code', 0)}",
                title="📊 Overview",
                border_style="blue"
            )
            
            # Top tags table
            tag_table = Table(title="Most Common Tags", show_header=True)
            tag_table.add_column("Tag", style="cyan")
            tag_table.add_column("Count", style="yellow")
            
            for tag, count in stats['tag_usage'].most_common(10):
                tag_table.add_row(tag, str(count))
            
            # Most tagged files table
            file_table = Table(title="Most Tagged Files", show_header=True)
            file_table.add_column("File", style="green", width=40)
            file_table.add_column("Tags", style="yellow")
            
            for file_path, tag_count in stats['most_tagged_files'][:5]:
                file_table.add_row(file_path, str(tag_count))
            
            self.console.print(overview)
            self.console.print(tag_table)
            self.console.print(file_table)
        else:
            print("\nSystem Statistics:")
            print("-" * 30)
            print(f"Total Files: {stats['total_files']}")
            print(f"Total Unique Tags: {stats['total_tags']}")
            print(f"Documentation Files: {stats['file_types'].get('documentation', 0)}")
            print(f"Source Code Files: {stats['file_types'].get('source_code', 0)}")
            
            print("\nMost Common Tags:")
            for tag, count in stats['tag_usage'].most_common(5):
                print(f"  {tag}: {count}")
    
    def interactive_search(self):
        """Interactive search interface."""
        while True:
            try:
                print("\n" + "=" * 60)
                self.console.print("🔍 Unified Search Interface", style="bold cyan" if HAS_RICH else None)
                print("-" * 30)
                print("1. Search by tag")
                print("2. Search by keyword")
                print("3. Browse by file type")
                print("4. Browse by category")
                print("5. View file details")
                print("6. Back to main menu")
                
                if HAS_RICH:
                    choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6"], default="6")
                else:
                    choice = input("Select option [6]: ").strip() or "6"
                
                if choice == "1":
                    if HAS_RICH:
                        tag = Prompt.ask("Enter tag to search")
                    else:
                        tag = input("Enter tag to search: ").strip()
                    
                    if tag:
                        results = [(f, [tag]) for f in self.search_by_tag(tag)]
                        self.display_search_results(results, f"Files with tag '{tag}'")
                        input("\nPress Enter to continue...")
                
                elif choice == "2":
                    if HAS_RICH:
                        keyword = Prompt.ask("Enter keyword to search")
                    else:
                        keyword = input("Enter keyword to search: ").strip()
                    
                    if keyword:
                        results = self.unified_search(keyword)
                        self.display_search_results(results, f"Files matching '{keyword}'")
                        input("\nPress Enter to continue...")
                
                elif choice == "3":
                    file_type = "documentation" if HAS_RICH and Prompt.confirm("Documentation files?") else "source_code"
                    results = [(f, tags) for f, tags in self.unified_index.items() 
                             if self.file_metadata.get(f, {}).get('type') == file_type]
                    self.display_search_results(results[:20], f"{file_type.title()} Files")
                    input("\nPress Enter to continue...")
                
                elif choice == "4":
                    categories = set(m.get('category', 'unknown') for m in self.file_metadata.values())
                    print(f"Available categories: {', '.join(sorted(categories))}")
                    if HAS_RICH:
                        category = Prompt.ask("Enter category")
                    else:
                        category = input("Enter category: ").strip()
                    
                    if category:
                        results = [(f, tags) for f, tags in self.unified_index.items()
                                 if self.file_metadata.get(f, {}).get('category') == category]
                        self.display_search_results(results, f"Files in '{category}' category")
                        input("\nPress Enter to continue...")
                
                elif choice == "5":
                    if HAS_RICH:
                        file_path = Prompt.ask("Enter file path")
                    else:
                        file_path = input("Enter file path: ").strip()
                    
                    if file_path:
                        info = self.get_file_info(file_path)
                        print(f"\nFile Information:")
                        print(f"Path: {info['path']}")
                        print(f"Exists: {info['exists']}")
                        print(f"Type: {info['metadata'].get('type', 'unknown')}")
                        print(f"Category: {info['metadata'].get('category', 'unknown')}")
                        print(f"Tags: {', '.join(info['tags'])}")
                        input("\nPress Enter to continue...")
                
                elif choice == "6":
                    break
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"Error: {e}")
                input("Press Enter to continue...")
    
    def rebuild_indices(self):
        """Rebuild the unified indices."""
        self.console.print("🔄 Rebuilding unified indices...")
        
        try:
            # Import and run the unified indexer
            sys.path.insert(0, str(SCRIPTS_ROOT / "automation"))
            from unified_tag_indexer import UnifiedTagIndexer
            
            indexer = UnifiedTagIndexer()
            indexer.build_unified_index()
            indexer.save_unified_index()
            indexer.save_metadata()
            
            # Reload indices
            self.load_indices()
            
            self.console.print("✅ Indices rebuilt successfully!")
            
        except Exception as e:
            self.console.print(f"❌ Error rebuilding indices: {e}")
    
    def interactive_mode(self):
        """Main interactive mode."""
        while True:
            try:
                self.display_header()
                self.display_main_menu()
                
                print("\nOptions:")
                print("1. Search & Discovery")
                print("2. View Statistics")
                print("3. Rebuild Indices")
                print("4. System Status")
                print("5. Exit")
                
                if HAS_RICH:
                    choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="5")
                else:
                    choice = input("Select option [5]: ").strip() or "5"
                
                if choice == "1":
                    self.interactive_search()
                elif choice == "2":
                    self.display_statistics()
                    input("\nPress Enter to continue...")
                elif choice == "3":
                    self.rebuild_indices()
                    input("\nPress Enter to continue...")
                elif choice == "4":
                    self.console.print(f"Enhanced IDS v{self.version}")
                    self.console.print(f"Indexed Files: {len(self.unified_index)}")
                    self.console.print(f"Rich UI: {'Available' if HAS_RICH else 'Not Available'}")
                    input("\nPress Enter to continue...")
                elif choice == "5":
                    self.console.print("Goodbye!")
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\nExiting Enhanced IDS...")
                break
            except Exception as e:
                self.console.print(f"Error: {e}")
                input("Press Enter to continue...")

    def search(self, query: str, max_results: int = 10, tags: List[str] = None) -> Dict:
        """Search method compatible with MCP server interface."""
        if tags is None:
            tags = []
        
        # Use unified_search and format results for MCP
        search_results = self.unified_search(query)
        
        # Filter by tags if specified
        if tags:
            filtered_results = []
            for file_path, matching_tags in search_results:
                if any(tag.lower() in [t.lower() for t in matching_tags] for tag in tags):
                    filtered_results.append((file_path, matching_tags))
            search_results = filtered_results
          # Format results for MCP response
        formatted_results = []
        for file_path, matching_tags in search_results[:max_results]:
            metadata = self.file_metadata.get(file_path, {})
            formatted_results.append({
                "file_path": file_path,
                "matching_tags": matching_tags,
                "metadata": metadata
            })

        return {
            "query": query,
            "results": formatted_results,
            "total_found": len(search_results),
            "requested_tags": tags,
            "search_rules": {
                "format": "Use single words ('python', 'guide') or underscore_format ('python_environment')",
                "no_spaces": "Spaces will cause 0 results - use 'administration' not 'system administration'",
                "discovery": "Use list-tags tool to find exact searchable terms",
                "examples": ["python", "environment", "python_environment", "deployment_guide", "administration"]
            },
            "input_received": f"Query: '{query}'"
        }

    def list_tags(self, category: str = None, pattern: str = None) -> List[str]:
        """List all available tags with optional filtering."""
        # Collect all unique tags
        all_tags = set()
        for tags in self.unified_index.values():
            all_tags.update(tags)
        
        tags_list = list(all_tags)
        
        # Filter by category if specified
        if category:
            category_lower = category.lower()
            tags_list = [tag for tag in tags_list if category_lower in tag.lower()]
        
        # Filter by pattern if specified
        if pattern:
            pattern_lower = pattern.lower()
            tags_list = [tag for tag in tags_list if pattern_lower in tag.lower()]
        
        return sorted(tags_list)

    def get_documentation_stats(self) -> Dict:
        """Get documentation statistics compatible with MCP server interface."""
        # Use existing get_statistics method and format for MCP
        stats = self.get_statistics()
        
        return {
            "total_files": stats['total_files'],
            "total_tags": stats['total_tags'],
            "enhanced_ids_available": True,
            "file_types": dict(stats['file_types']),
            "categories": dict(stats['categories']),
            "most_used_tags": [{"tag": tag, "count": count} 
                              for tag, count in stats['tag_usage'].most_common(10)],
            "most_tagged_files": [{"file": file_path, "tag_count": count} 
                                 for file_path, count in stats['most_tagged_files'][:5]]
        }

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Enhanced IDS with Unified Tagging')
    parser.add_argument('--search', type=str, help='Search by tag or keyword')
    parser.add_argument('--rebuild', action='store_true', help='Rebuild indices')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--type', type=str, choices=['documentation', 'source_code', 'all'], 
                       default='all', help='Filter by file type')
    
    args = parser.parse_args()
    
    ids = EnhancedIDS()
    
    if args.rebuild:
        ids.rebuild_indices()
    elif args.search:
        results = ids.unified_search(args.search, args.type)
        ids.display_search_results(results, f"Search results for '{args.search}'")
    elif args.stats:
        ids.display_statistics()
    else:
        ids.interactive_mode()

if __name__ == "__main__":
    main()
