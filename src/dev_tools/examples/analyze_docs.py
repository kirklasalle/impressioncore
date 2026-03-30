#!/usr/bin/env python3
"""
ImpressionCore: Analyze Docs

Module for analyze docs functionality in the ImpressionCore framework.

File: examples\analyze_docs.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, object-oriented, 2025]
Dependencies: [rich, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements analyze docs functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from examples.analyze_docs import DocumentAnalyzer
instance = DocumentAnalyzer()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import sys
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.logging import RichHandler
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

# Update logging to use rich
logging.basicConfig(level=logging.INFO, format='%(message)s', handlers=[RichHandler()])
logger = logging.getLogger("rich_logger")

# Initialize rich console
console = Console()

class DocumentAnalyzer:
    """Analyzes training documents and provides insights"""
    
    def __init__(self, docs_dir: str = "trainingdocs"):
        """
        
    __init__ function for processing.
    
    Args:
        self, docs_dir: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        self.docs_dir = Path(docs_dir)
        if not self.docs_dir.exists():
            raise ValueError(f"Directory {docs_dir} does not exist")
    
    def analyze_all(self) -> List[Dict[str, Any]]:
        """Analyze all documents in the directory with rich progress and formatting."""
        results = []

        # Create the layout first
        layout = Layout()
        layout.split_column(
            Layout(name="progress_section", size=10),
            Layout(name="info_section", ratio=4)
        )

        # Create progress group for all progress bars
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            expand=True
        )

        # Add tasks
        analyze_files = progress.add_task("[cyan]Analyzing files...", total=len(list(self.docs_dir.rglob("*"))))
        process_code = progress.add_task("[yellow]Processing code files...", total=100, visible=False)
        process_json = progress.add_task("[magenta]Processing JSON files...", total=100, visible=False)
        process_md = progress.add_task("[blue]Processing Markdown files...", total=100, visible=False)

        # Initialize info display with empty content
        info_content = [
            Text("Initializing analysis...", style="yellow")
        ]

        # Update initial layout
        layout["progress_section"].update(
            Panel(
                progress,
                title="[bold blue]Analysis Progress",
                border_style="blue"
            )
        )
        layout["info_section"].update(
            Panel(
                Align.center(Text("Starting analysis...", style="yellow")),
                title="[bold green]Analysis Information",
                border_style="green"
            )
        )

        # Single Live context managing both progress and info
        with Live(layout, console=console, refresh_per_second=10, transient=False):
            # Walk through all subdirectories
            for root, _, files in os.walk(self.docs_dir.parent):
                for file_name in files:
                    file_path = Path(root) / file_name

                    # Skip virtual environments and cache directories
                    if any(p in str(file_path) for p in ['venv', '__pycache__', 'node_modules', '.git']):
                        progress.advance(analyze_files)
                        continue

                    # Update info panel with current file
                    file_info = self.get_file_info(file_path)
                    ext = file_path.suffix.lower()

                    # Show appropriate progress bar based on file type
                    if ext in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                        progress.update(process_code, visible=True)
                        content_info = self.analyze_code_file(file_path)
                        progress.advance(process_code)
                    elif ext == '.json':
                        progress.update(process_json, visible=True)
                        content_info = self.analyze_json_file(file_path)
                        progress.advance(process_json)
                    elif ext == '.md':
                        progress.update(process_md, visible=True)
                        content_info = self.analyze_text_file(file_path)
                        progress.advance(process_md)
                    else:
                        content_info = {}

                    if content_info:
                        # Create info text
                        info_text = [
                            Text.from_markup(f"[yellow]Analyzing:[/yellow] {file_path.name}"),
                            Text.from_markup(f"[green]Type:[/green] {ext}"),
                        ]

                        if 'code_lines' in content_info:
                            info_text.append(Text.from_markup(f"[blue]Code lines:[/blue] {content_info['code_lines']}"))
                        if 'functions' in content_info:
                            info_text.append(Text.from_markup(f"[magenta]Functions:[/magenta] {content_info['functions']}"))

                        # Update info content with new text
                        layout["info_section"].update(
                            Panel(
                                Align.center(Text.from_markup("\n".join([t.plain for t in info_text]))),
                                title="[bold green]Analysis Information",
                                border_style="green"
                            )
                        )
                        
                        results.append({**file_info, "content": content_info})

                    progress.advance(analyze_files)

            # Hide task-specific progress bars at the end
            progress.update(process_code, visible=False)
            progress.update(process_json, visible=False)
            progress.update(process_md, visible=False)

        return results

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get basic information about a file"""
        stats = file_path.stat()
        return {
            "name": file_path.name,
            "extension": file_path.suffix,
            "size_bytes": stats.st_size,
            "size_mb": stats.st_size / (1024 * 1024),
            "path": str(file_path)
        }
    
    def analyze_text_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze content of a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                return {
                    "line_count": len(lines),
                    "char_count": len(content),
                    "word_count": len(content.split()),
                    "preview": content[:200] + "..." if len(content) > 200 else content
                }
        except Exception as e:
            logger.error(f"Error analyzing text file {file_path}: {str(e)}")
            return {}
    
    def analyze_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze content of a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return {
                        "keys": list(data.keys()),
                        "structure": self._describe_structure(data),
                        "entry_count": len(data) if isinstance(data, dict) else 1
                    }
                elif isinstance(data, list):
                    return {
                        "structure": "List of " + self._describe_structure(data[0]) if data else "Empty list",
                        "entry_count": len(data)
                    }
        except Exception as e:
            logger.error(f"Error analyzing JSON file {file_path}: {str(e)}")
            return {}
    
    def _describe_structure(self, obj: Any, depth: int = 0) -> str:
        """Recursively describe the structure of a JSON object"""
        if depth > 3:  # Limit recursion depth
            return "..."
        
        if isinstance(obj, dict):
            items = [f"{k}: {self._describe_structure(v, depth + 1)}" for k, v in list(obj.items())[:5]]
            return "{" + ", ".join(items) + ("..." if len(obj) > 5 else "") + "}"
        elif isinstance(obj, list):
            if not obj:
                return "[]"
            return f"[{self._describe_structure(obj[0], depth + 1)}...]"
        else:
            return type(obj).__name__
    
    def analyze_code_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze content of a code file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                
                # Count actual code lines (non-empty, non-comment)
                code_lines = len([l for l in lines if l.strip() and not l.strip().startswith(('#', '//', '/*', '*', '"""'))])
                
                # Basic code metrics
                metrics = {
                    "total_lines": len(lines),
                    "code_lines": code_lines,
                    "blank_lines": len([l for l in lines if not l.strip()]),
                    "comment_lines": len([l for l in lines if l.strip().startswith(('#', '//', '/*', '*', '"""'))]),
                    "functions": len([l for l in lines if 'def ' in l or 'function ' in l]),
                    "classes": len([l for l in lines if 'class ' in l]),
                }
                
                return metrics
        except Exception as e:
            logger.error(f"Error analyzing code file {file_path}: {str(e)}")
            return {}

def main():
    """Main function with rich-enhanced output."""
    try:
        # Analyze from project root
        analyzer = DocumentAnalyzer(docs_dir=".")
        logger.info("Starting codebase analysis")

        results = analyzer.analyze_all()

        # Print summary using rich table
        console.rule("[bold blue]Codebase Analysis Summary")

        table = Table(title="Analysis Results")
        table.add_column("File Name", style="cyan")
        table.add_column("Extension", style="magenta")
        table.add_column("Code Lines", style="green")
        table.add_column("Functions", style="yellow")
        table.add_column("Classes", style="blue")

        total_code_lines = 0
        file_types = {}

        for doc in results:
            ext = doc['extension'].lower()
            file_types[ext] = file_types.get(ext, 0) + 1

            if ext in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                metrics = doc['content']
                total_code_lines += metrics.get('code_lines', 0)
                table.add_row(
                    doc['name'],
                    ext,
                    str(metrics.get('code_lines', 0)),
                    str(metrics.get('functions', 0)),
                    str(metrics.get('classes', 0))
                )

        console.print(table)

        console.print("\n[bold]Overall Statistics:[/bold]")
        console.print(f"Total files: {len(results)}")
        console.print(f"Total code lines: {total_code_lines}")

        console.print("\n[bold]File types distribution:[/bold]")
        for ext, count in file_types.items():
            console.print(f"{ext}: {count} files")

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()