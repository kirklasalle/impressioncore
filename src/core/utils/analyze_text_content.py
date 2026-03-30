#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #python #source_code #src/core/utils/analyze_text_content.py
**Category:** Core Implementation
**Status:** Active
"""









# Analyze Text Content

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #api #python #source_code #src\\core\\utils\\analyze_text_content.py
# Category:** Core Implementation
# Status:** Active

import json
from pathlib import Path


def is_text_file(file_path):
    """Check if the file is a JSON or TXT file."""
    return file_path.suffix.lower() in {'.json', '.txt'}

def sample_text_from_json(file_path, max_samples=5):
    """Sample up to max_samples text entries from a JSON file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
        texts = []
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, str):
                    texts.append(v)
                elif isinstance(v, list):
                    texts.extend([x for x in v if isinstance(x, str)])
        elif isinstance(data, list):
            texts.extend([x for x in data if isinstance(x, str)])
        return texts[:max_samples]
    except Exception as e:
        return [f"[Error reading {file_path.name}: {e}]"]

def sample_text_from_txt(file_path, max_samples=5):
    """Sample up to max_samples lines from a TXT file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines[:max_samples]
    except Exception as e:
        return [f"[Error reading {file_path.name}: {e}]"]

def analyze_embedding_dir(embedding_dir, modalities=('comprehensive', 'unknown'), max_files=20):
    """
    Analyze the given embedding directory for text content in files with specified modalities.
    Args:
        embedding_dir: Root directory containing embedding files.
        modalities: Tuple of modality keywords to search for in filenames.
        max_files: Maximum number of files to sample per modality.
        max_samples: Maximum number of text samples per file.
    """
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    max_samples = 5
    embedding_dir = Path(embedding_dir)
    for modality in modalities:
        console.rule(f"[bold cyan]Analyzing modality: {modality}")
        files = list(embedding_dir.rglob(f"*{modality}*"))
        count = 0
        table = Table(title=f"{modality.capitalize()} Files", box=box.SIMPLE, show_lines=True, expand=True)
        # File column: narrow, word wrap
        table.add_column("File", style="bold yellow", width=24, no_wrap=False, overflow="fold")
        table.add_column("Sample #", style="dim", width=8, no_wrap=True)
        # Text Sample column: wide, word wrap
        table.add_column("Text Sample", style="white", no_wrap=False, overflow="fold", max_width=console.width-36)
        for file_path in files:
            if not is_text_file(file_path):
                continue
            if file_path.suffix.lower() == '.json':
                samples = sample_text_from_json(file_path, max_samples)
            else:
                samples = sample_text_from_txt(file_path, max_samples)
            for i, text in enumerate(samples):
                table.add_row(file_path.name, str(i+1), text)
            count += 1
            if count >= max_files:
                break
        if count == 0:
            console.print(Panel(f"No text files found for modality: {modality}", style="red"))
        else:
            console.print(table)

if __name__ == "__main__":
    EMBEDDING_ROOT = "F:/impressioncore-b1-embeddings-062125/"
    analyze_embedding_dir(EMBEDDING_ROOT)
