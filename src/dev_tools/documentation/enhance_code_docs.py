#!/usr/bin/env python3
"""
ImpressionCore: Code Documentation Enhancement System

This script automatically enhances code documentation across the ImpressionCore
project by adding standardized headers, improving docstrings, and implementing
a comprehensive tagging system.

File: scripts/documentation/enhance_code_docs.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [documentation, automation, code-enhancement, production]
Dependencies: [rich, pathlib, ast, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Comprehensive code documentation enhancement system that automatically:
- Adds standardized file headers to Python files
- Enhances docstrings with proper formatting and examples
- Implements consistent tagging system
- Extracts and categorizes TODO items
- Generates documentation health reports

Design Philosophy:
- Automated but configurable enhancement
- Preserves existing documentation while improving it
- Focuses on memory optimization documentation
- Ensures consistency across the entire codebase

TODO:
- Add support for JavaScript/TypeScript files
- Implement docstring quality scoring
- Add integration with git hooks
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import argparse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Rich imports for beautiful terminal output
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich import print as rprint

__version__ = "1.0.0"
__author__ = "Kirk LaSalle & GitHub Copilot"
__license__ = "MIT"
__status__ = "Production"

console = Console()

@dataclass
class FileAnalysis:
    """Analysis results for a Python file."""
    filepath: Path
    has_header: bool
    has_module_docstring: bool
    missing_docstrings: List[str]
    todo_items: List[Dict[str, Any]]
    tags: List[str]
    complexity_score: int
    memory_docs: bool
    examples_present: bool

@dataclass
class DocumentationStats:
    """Overall documentation statistics."""
    total_files: int
    files_with_headers: int
    files_with_docstrings: int
    total_functions: int
    documented_functions: int
    total_classes: int
    documented_classes: int
    total_todos: int
    memory_documented_files: int

class CodeDocumentationEnhancer:
    """
    Comprehensive code documentation enhancement system.
    
    This class provides automated enhancement of Python code documentation
    including standardized headers, improved docstrings, and consistent tagging.
    
    Attributes:
        project_root (Path): Root directory of the ImpressionCore project
        src_dir (Path): Source code directory
        config (Dict[str, Any]): Configuration for enhancement process
        stats (DocumentationStats): Documentation statistics
    
    Memory Considerations:
        - Processes files incrementally to minimize memory usage
        - Uses AST parsing for efficient code analysis
        - Implements progress tracking for large codebases
    
    Examples:
        >>> enhancer = CodeDocumentationEnhancer()
        >>> enhancer.analyze_project()
        >>> enhancer.generate_report()
        >>> enhancer.enhance_all_files()
      Notes:        - Preserves existing documentation while enhancing it
        - Creates backups before making changes
        - Supports dry-run mode for safe testing
    """
    
    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        """
        Initialize the documentation enhancer.
        
        Args:
            project_root (Optional[Path]): Root directory of project.
                                         Defaults to auto-detection.
            verbose (bool): Enable verbose output for debugging.
        """
        self.project_root = project_root or self._find_project_root()
        self.src_dir = self.project_root / "src"
        self.docs_dir = self.project_root / "docs"
        self.verbose = verbose
        
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Project root: {self.project_root}")
            console.print(f"[cyan]Debug:[/cyan] Source directory: {self.src_dir}")
            console.print(f"[cyan]Debug:[/cyan] Docs directory: {self.docs_dir}")
        
        self.config = {
            "author": "Kirk LaSalle & GitHub Copilot",
            "license": "MIT",
            "copyright": "2025 ImpressionCore Team",
            "hardware_target": "NVIDIA GTX 1050 Ti (4GB VRAM)",
            "project_name": "ImpressionCore - Brain-Inspired Multimodal AI Framework"
        }
        
        self.stats = DocumentationStats(
            total_files=0, files_with_headers=0, files_with_docstrings=0,
            total_functions=0, documented_functions=0, total_classes=0,
            documented_classes=0, total_todos=0, memory_documented_files=0
        )

    def _find_project_root(self) -> Path:
        """Find the project root directory by looking for key files."""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / "src").exists() and (current / "docs").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def analyze_file(self, filepath: Path) -> FileAnalysis:
        """
        Analyze a Python file for documentation quality.
        
        Args:
            filepath (Path): Path to the Python file to analyze
        
        Returns:
            FileAnalysis: Comprehensive analysis of the file
          Raises:
            ValueError: If file is not a Python file
            FileNotFoundError: If file doesn't exist
        """
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Analyzing file: {filepath}")
            
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if filepath.suffix != ".py":
            raise ValueError(f"Not a Python file: {filepath}")
        
        content = filepath.read_text(encoding='utf-8-sig')  # utf-8-sig handles BOM
        
        # Remove any remaining BOM characters that might cause issues
        if content.startswith('\ufeff'):
            content = content[1:]
        
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] File size: {len(content)} characters")
          # Parse AST for analysis
        try:
            tree = ast.parse(content)
            if self.verbose:
                console.print(f"[cyan]Debug:[/cyan] AST parsing successful")
        except SyntaxError as e:
            console.print(f"[red]Syntax error in {filepath}: {e}[/red]")
            if self.verbose and e.text:
                # Clean the error text to avoid Unicode issues
                error_text = str(e.text).encode('ascii', 'replace').decode('ascii')
                console.print(f"[cyan]Debug:[/cyan] Line {e.lineno}: {error_text}")
            return FileAnalysis(
                filepath=filepath, has_header=False, has_module_docstring=False,
                missing_docstrings=[], todo_items=[], tags=[], complexity_score=0,
                memory_docs=False, examples_present=False
            )
        
        # Analyze file structure
        has_header = self._has_standard_header(content)
        has_module_docstring = self._has_module_docstring(tree)
        missing_docstrings = self._find_missing_docstrings(tree)
        todo_items = self._extract_todos(content)
        tags = self._extract_tags(content)
        complexity_score = self._calculate_complexity(tree)
        memory_docs = self._has_memory_documentation(content)
        examples_present = self._has_examples(content)
        
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Analysis results:")
            console.print(f"  - Has header: {has_header}")
            console.print(f"  - Has module docstring: {has_module_docstring}")
            console.print(f"  - Missing docstrings: {len(missing_docstrings)}")
            console.print(f"  - TODO items: {len(todo_items)}")
            console.print(f"  - Tags: {tags}")
            console.print(f"  - Complexity score: {complexity_score}")
            console.print(f"  - Memory docs: {memory_docs}")
            console.print(f"  - Examples present: {examples_present}")
        
        return FileAnalysis(
            filepath=filepath,
            has_header=has_header,
            has_module_docstring=has_module_docstring,
            missing_docstrings=missing_docstrings,
            todo_items=todo_items,
            tags=tags,
            complexity_score=complexity_score,
            memory_docs=memory_docs,
            examples_present=examples_present
        )

    def _has_standard_header(self, content: str) -> bool:
        """Check if the file content has a standard header."""
        # Simplified check for now
        return "ImpressionCore" in content and "License: MIT" in content

    def _has_module_docstring(self, tree: ast.AST) -> bool:
        """Check if the module has a docstring."""
        return isinstance(tree, ast.Module) and ast.get_docstring(tree) is not None

    def _find_missing_docstrings(self, tree: ast.AST) -> List[str]:
        """Find functions and classes missing docstrings."""
        missing = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    missing.append(f"{node.name} (line {node.lineno})")
        return missing

    def _extract_todos(self, content: str) -> List[Dict[str, Any]]:
        """Extract TODO items from comments."""
        todos = []
        # Regex to find TODOs with optional priority and description
        # Example: # TODO(high): Fix this bug
        # Example: # TODO: Implement feature
        todo_pattern = re.compile(r"#\s*TODO(?:\((?P<priority>[^)]+)\))?:\s*(?P<description>.+)", re.IGNORECASE)
        
        for i, line_content in enumerate(content.splitlines()):
            match = todo_pattern.search(line_content)
            if match:
                priority = match.group('priority') or 'medium' # Default priority
                description = match.group('description').strip()
                todos.append({"line": i + 1, "priority": priority, "description": description})
        return todos

    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from the header or comments."""
        tags = []
        # Example: Tags: [tag1, tag2, another-tag]
        tag_pattern = re.compile(r"Tags:\s*\[([^]]+)\]", re.IGNORECASE)
        match = tag_pattern.search(content)
        if match:
            tags_str = match.group(1)
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        return tags

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate a simple complexity score (e.g., number of nodes)."""
        return sum(1 for _ in ast.walk(tree))

    def _has_memory_documentation(self, content: str) -> bool:
        """Check for memory-related documentation."""
        memory_keywords = [
            "memory", "VRAM", "RAM", "optimization", "hardware target", 
            "GTX 1050 Ti", "resource usage", "efficiency"
        ]
        return any(keyword.lower() in content.lower() for keyword in memory_keywords)

    def _has_examples(self, content: str) -> bool:
        """Check if docstrings or comments contain examples."""
        example_indicators = ["Example:", "Examples:", ">>>"]
        return any(indicator in content for indicator in example_indicators)

    def generate_standard_header(self, filepath: Path, analysis: Optional[FileAnalysis] = None) -> str:
        """
        Generate a standardized file header.
        
        Args:
            filepath (Path): Path to the file
            analysis (Optional[FileAnalysis]): Pre-computed analysis of the file
        
        Returns:
            str: The generated header string
        """
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Generating header for: {filepath}")

        relative_path = filepath.relative_to(self.project_root)
        module_name = filepath.stem
        created_date = datetime.now().strftime("%Y-%m-%d") # Use current date for new headers
        
        # Attempt to get existing tags or generate default
        tags = analysis.tags if analysis and analysis.tags else self._generate_default_tags(filepath)
        tags_str = f"[{', '.join(tags)}]" if tags else "[]"

        header = f'''#!/usr/bin/env python3
\"\"\"
{self.config['project_name']}

File: {relative_path}
Project: {self.config['project_name']}
Created: {created_date}
Modified: {created_date}
Version: 1.0.0

Authors:
- {self.config['author']}

License: {self.config['license']}
Copyright (c) {self.config['copyright']}

Tags: {tags_str}
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: {self.config['hardware_target']}

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.
\"\"\"
'''
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Generated header:\\n{header}")
        return header

    def _generate_default_tags(self, filepath: Path) -> List[str]:
        """Generate default tags based on file path."""
        tags = []
        try:
            relative_path = filepath.relative_to(self.src_dir)
            parts = list(relative_path.parts[:-1]) # Directory parts
            if parts:
                tags.extend(parts)
            if filepath.stem.startswith("test_"):
                tags.append("testing")
            elif "util" in filepath.stem.lower() or "helper" in filepath.stem.lower():
                tags.append("utility")
            elif "config" in filepath.stem.lower():
                tags.append("configuration")
            
            # Add parent directory as a tag if not too generic
            if relative_path.parent and relative_path.parent.name != '.':
                 if relative_path.parent.name not in ['src', 'lib', 'components']: # Avoid overly generic tags
                    tags.append(relative_path.parent.name)

        except ValueError: # filepath might not be under self.src_dir (e.g. top-level scripts)
            tags.append("script")

        return list(set(tags)) # Remove duplicates

    def enhance_file_documentation(self, filepath: Path, dry_run: bool = False) -> bool:
        """
        Enhance documentation for a single file.
        
        Args:
            filepath (Path): Path to the file to enhance
            dry_run (bool): If True, don't actually modify files
        
        Returns:
            bool: True if file was modified (or would be in dry_run)
        """
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Enhancing file: {filepath}, Dry run: {dry_run}")
            
        try:
            analysis = self.analyze_file(filepath)
            content = filepath.read_text(encoding='utf-8')
            original_content = content # Keep a copy for comparison
            modified = False
            
            # Add header if missing
            if not analysis.has_header:
                if self.verbose:
                    console.print(f"[cyan]Debug:[/cyan] Header missing, generating new header.")
                header = self.generate_standard_header(filepath, analysis)
                
                # Find where to insert header (after shebang/encoding if present)
                lines = content.split('\\n')
                insert_line = 0
                
                for i, line in enumerate(lines):
                    if line.startswith('#!') or 'coding:' in line or 'encoding:' in line:
                        insert_line = i + 1
                    elif line.strip() == "" and insert_line == 0 and i < 2: # Allow empty lines before first import/code after shebang
                        insert_line = i +1
                    elif line.strip() != "": # Stop at first non-empty, non-directive line
                        break 
                
                # Insert header
                # Ensure there's a blank line after the header's triple quotes if content follows immediately
                if lines[insert_line:]: # If there's content after insertion point
                    if lines[insert_line].strip() != "" and not header.endswith("\\n\\n"):
                         header += "\\n" 

                lines.insert(insert_line, header)
                content = '\\n'.join(lines)
                modified = True
                if self.verbose:
                    console.print(f"[cyan]Debug:[/cyan] Header added. Content length: {len(content)}")
            
            # TODO: Add docstring enhancement logic here
            # For now, we only add headers.
            
            # Write changes if not dry run and content actually changed
            if modified and content != original_content:
                if not dry_run:
                    # Create backup
                    backup_dir = self.project_root / "src" / "backup_before_commenting"
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    
                    relative_backup_path = filepath.relative_to(self.project_root)
                    backup_file_path = backup_dir / relative_backup_path
                    backup_file_path.parent.mkdir(parents=True, exist_ok=True)

                    # In case of rerunning on already backed up files
                    if filepath.suffix == '.bak': 
                        console.print(f"[yellow]Skipping backup for already backed up file:[/yellow] {filepath}")
                    else:
                        backup_file_path_with_bak = backup_file_path.with_suffix(filepath.suffix + '.bak')
                        if self.verbose:
                             console.print(f"[cyan]Debug:[/cyan] Backing up to: {backup_file_path_with_bak}")
                        filepath.rename(backup_file_path_with_bak)
                    
                    # Write enhanced file
                    filepath.write_text(content, encoding='utf-8')
                    if self.verbose:
                        console.print(f"[cyan]Debug:[/cyan] File written: {filepath}")
                    
                    console.print(f"[green]Enhanced:[/green] {filepath}")
                else:
                    console.print(f"[yellow]Would enhance (dry run):[/yellow] {filepath}")
                return True
            elif modified and content == original_content:
                if self.verbose:
                    console.print(f"[cyan]Debug:[/cyan] Content was marked modified but no actual changes. Skipping write for {filepath}")
                return False # No actual change
            else:
                if self.verbose:
                    console.print(f"[cyan]Debug:[/cyan] No modifications needed for {filepath}")
                return False

        except FileNotFoundError:
            console.print(f"[red]Error: File not found {filepath}[/red]")
            return False
        except ValueError as e: # For non-python files
            console.print(f"[yellow]Skipping non-Python file or error during analysis {filepath}: {e}[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]Unexpected error enhancing {filepath}: {e}[/red]")
            if self.verbose:
                import traceback
                console.print(f"[cyan]Debug:[/cyan] Traceback:\\n{traceback.format_exc()}")
            return False

    def analyze_project(self) -> None:
        """Analyze all Python files in the project."""
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Starting project analysis...")
            
        self.analyses: Dict[Path, FileAnalysis] = {}
        py_files = list(self.src_dir.rglob("*.py"))
        # Also include top-level python scripts in project_root
        py_files.extend(list(self.project_root.glob("*.py")))
        
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Found {len(py_files)} Python files to analyze.")

        self.stats = DocumentationStats(0,0,0,0,0,0,0,0,0) # Reset stats

        with Progress(console=console) as progress:
            task = progress.add_task("[cyan]Analyzing files...[/cyan]", total=len(py_files))
            for filepath in py_files:
                if "backup_before_commenting" in filepath.parts: # Skip backup directory
                    progress.update(task, advance=1)
                    if self.verbose:
                        console.print(f"[cyan]Debug:[/cyan] Skipping backup file: {filepath}")
                    continue
                try:
                    analysis = self.analyze_file(filepath)
                    self.analyses[filepath] = analysis
                    
                    # Update stats
                    self.stats.total_files += 1
                    if analysis.has_header: self.stats.files_with_headers += 1
                    if analysis.has_module_docstring: self.stats.files_with_docstrings += 1
                    # TODO: More detailed stats for functions/classes
                    self.stats.total_todos += len(analysis.todo_items)
                    if analysis.memory_docs: self.stats.memory_documented_files +=1

                except Exception as e:
                    console.print(f"[red]Error analyzing {filepath}: {e}[/red]")
                progress.update(task, advance=1)
        
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Project analysis complete. Analyzed {len(self.analyses)} files.")

    def enhance_all_files(self, dry_run: bool = False) -> None:
        """Enhance documentation for all Python files in the project."""
        if not hasattr(self, 'analyses') or not self.analyses:
            console.print("[yellow]No analysis data. Running project analysis first.[/yellow]")
            self.analyze_project()

        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Starting enhancement for all files. Dry run: {dry_run}")

        modified_count = 0
        error_count = 0
        
        files_to_enhance = list(self.analyses.keys())

        with Progress(console=console) as progress:
            task = progress.add_task("[cyan]Enhancing files...[/cyan]", total=len(files_to_enhance))
            for filepath in files_to_enhance:
                if self.enhance_file_documentation(filepath, dry_run=dry_run):
                    modified_count +=1
                else:
                    # Check if it was an error or just no modification needed
                    # A bit heuristic: if analyze_file returned an empty FileAnalysis, it was likely a syntax error
                    if self.analyses[filepath].complexity_score == 0 and not self.analyses[filepath].has_header and not self.analyses[filepath].has_module_docstring:
                         error_count +=1
                progress.update(task, advance=1)
        
        console.print(f"[green]Enhancement complete.[/green]")
        console.print(f"  Processed: {len(files_to_enhance)} files")
        console.print(f"  Enhanced: {modified_count} files")
        if error_count > 0:
            console.print(f"  Errors: [red]{error_count} files[/red] (syntax errors or other issues prevented processing)")
        if dry_run:
            console.print(f"[yellow]Dry run mode: No actual changes were made.[/yellow]")
        
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Enhancement process finished.")

    def generate_report(self) -> None:
        """Generate and print a documentation health report."""
        if not hasattr(self, 'analyses') or not self.analyses:
            console.print("[yellow]No analysis data. Run analysis first.[/yellow]")
            return
            
        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Generating documentation report...")

        # Update stats based on current analyses
        self.stats.total_files = len(self.analyses)
        self.stats.files_with_headers = sum(1 for analysis in self.analyses.values() if analysis.has_header)
        self.stats.files_with_docstrings = sum(1 for analysis in self.analyses.values() if analysis.has_module_docstring) # Module docstring
        self.stats.total_todos = sum(len(analysis.todo_items) for analysis in self.analyses.values())
        self.stats.memory_documented_files = sum(1 for analysis in self.analyses.values() if analysis.memory_docs)
        # TODO: Add function/class level docstring stats if _find_missing_docstrings is used to populate more detailed stats

        table = Table(title="ImpressionCore Documentation Health Report")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Percentage", style="green")

        table.add_row("Total Python Files", str(self.stats.total_files), "100%")
        if self.stats.total_files > 0:
            header_percent = (self.stats.files_with_headers / self.stats.total_files) * 100
            docstring_percent = (self.stats.files_with_docstrings / self.stats.total_files) * 100
            memory_docs_percent = (self.stats.memory_documented_files / self.stats.total_files) * 100
            
            table.add_row("Files with Standard Headers", str(self.stats.files_with_headers), f"{header_percent:.1f}%")
            table.add_row("Files with Module Docstrings", str(self.stats.files_with_docstrings), f"{docstring_percent:.1f}%")
            # table.add_row("Total Functions", str(self.stats.total_functions)) # Needs more detailed parsing
            # table.add_row("Documented Functions", str(self.stats.documented_functions))
            table.add_row("Files with Memory Optimization Docs", str(self.stats.memory_documented_files), f"{memory_docs_percent:.1f}%")
            table.add_row("Total TODO Items", str(self.stats.total_todos), "-")
        
        console.print(Panel(table, border_style="blue"))

        # List files needing attention
        needs_header = [Path(fp).name for fp, analysis in self.analyses.items() if not analysis.has_header][:5]
        needs_docstring = [Path(fp).name for fp, analysis in self.analyses.items() if not analysis.has_module_docstring][:5]
        
        if needs_header:
            rprint(Panel(f"[bold yellow]Files missing headers (first 5):[/bold yellow]\\n{', '.join(needs_header)}", title="Action Items", border_style="yellow"))
        if needs_docstring:
            rprint(Panel(f"[bold yellow]Files missing module docstrings (first 5):[/bold yellow]\\n{', '.join(needs_docstring)}", title="Action Items", border_style="yellow"))

        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Report generation complete.")
            
    def extract_todos_to_file(self, output_dir: Optional[Path] = None) -> None:
        """Extract all TODO items into a markdown file."""
        if not hasattr(self, 'analyses') or not self.analyses:
            console.print("[yellow]No analysis data. Run analysis first.[/yellow]")
            return

        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] Extracting TODOs to file...")

        output_dir = output_dir or (self.project_root / "docs" / "developer")
        output_dir.mkdir(parents=True, exist_ok=True)
        todo_file_path = output_dir / "project_todos.md"

        all_todos = []
        for filepath, analysis in self.analyses.items():
            for todo in analysis.todo_items:
                all_todos.append({
                    "file": str(filepath.relative_to(self.project_root)),
                    "line": todo["line"],
                    "priority": todo["priority"],
                    "description": todo["description"]
                })
        
        # Sort by priority (e.g., high, medium, low), then by file
        priority_map = {'high': 0, 'medium': 1, 'low': 2}
        all_todos.sort(key=lambda x: (priority_map.get(x['priority'].lower(), 3), x['file']))

        md_content = "# Project TODO List\\n\\n"\
                     f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n"\
                     "This list is automatically extracted from TODO comments in the codebase.\\n\\n"

        current_priority = None
        for todo in all_todos:
            if todo['priority'].capitalize() != current_priority:
                current_priority = todo['priority'].capitalize()
                md_content += f"## {current_priority} Priority\\n\\n"
            
            md_content += f"- **{todo['description']}**\\n"
            md_content += f"  - `File`: {todo['file']}\\n"
            md_content += f"  - `Line`: {todo['line']}\\n\\n"
            
        todo_file_path.write_text(md_content, encoding='utf-8')
        console.print(f"[green]TODO list saved to:[/green] {todo_file_path}")

        if self.verbose:
            console.print(f"[cyan]Debug:[/cyan] TODO extraction complete.")

def main():
    """Main function for the documentation enhancement script."""
    parser = argparse.ArgumentParser(description="Enhance ImpressionCore code documentation")
    parser.add_argument("--analyze", action="store_true", help="Analyze project documentation")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze documentation, no enhancements")
    parser.add_argument("--enhance", action="store_true", help="Enhance all files")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no changes)")
    parser.add_argument("--extract-todos", action="store_true", help="Extract TODO items")
    parser.add_argument("--file", type=str, help="Enhance specific file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output for debugging")
    
    args = parser.parse_args()
    
    # Initialize enhancer with verbose option
    enhancer = CodeDocumentationEnhancer(verbose=args.verbose)
    
    # Handle analyze-only flag - just analysis and report, no other actions
    if args.analyze_only:
        enhancer.analyze_project()
        enhancer.generate_report()
        return
    
    if args.analyze or not any([args.enhance, args.extract_todos, args.file]):
        enhancer.analyze_project()
        enhancer.generate_report()
    
    if args.extract_todos:
        if not hasattr(enhancer, 'analyses') or not enhancer.analyses: # Ensure analyses is run
            enhancer.analyze_project()
        enhancer.extract_todos_to_file()
    
    if args.enhance:
        # analyze_project is called by enhance_all_files if needed
        enhancer.enhance_all_files(dry_run=args.dry_run)
    
    if args.file:
        filepath = Path(args.file)
        if filepath.exists():
            # For single file enhancement, we might not have full project analysis
            # but enhance_file_documentation calls analyze_file internally.
            enhancer.enhance_file_documentation(filepath, dry_run=args.dry_run)
        else:
            console.print(f"[red]File not found: {filepath}[/red]")

if __name__ == "__main__":
    main()
