#!/usr/bin/env python3
"""
Quick fix script for vocab_size() TypeError in ImpressionCore B1 model.
This script replaces all instances of .vocab_size() with .vocab_size
Enhanced with rich progress indicators for better user experience.
"""
from datetime import datetime
import sys
import os

# Try to import rich for enhanced output (graceful fallback if not available)
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich import print as rprint
    console = Console()
    use_rich = True
except ImportError:
    console = None
    use_rich = False
    rprint = print

def fix_vocab_size_issue():
    """
    Fix vocab_size() method calls to property access.
    
    Memory-efficient function that replaces all instances of .vocab_size() 
    with .vocab_size in the B1 unified model file.
    """
    file_path = r"D:\Projects\impressioncore\src\models\impressioncore-base\b1_unified_model.py"
    
    if use_rich:
        console.print(Panel.fit(
            "[bold blue]ImpressionCore B1 Model Fix Script[/bold blue]\n"
            "[green]Resolving vocab_size() TypeError[/green]\n"
            f"[dim]Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            border_style="blue"
        ))
    else:
        print("=== ImpressionCore B1 Model Fix Script ===")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        error_msg = f"Error: File not found - {file_path}"
        if use_rich:
            console.print(f"[red]{error_msg}[/red]")
        else:
            print(error_msg)
        sys.exit(1)
    
    try:
        if use_rich:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                # Read file
                task1 = progress.add_task("Reading B1 model file...", total=100)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                progress.update(task1, completed=50)
                
                # Count occurrences
                occurrences = content.count('.vocab_size()')
                progress.update(task1, description=f"Found {occurrences} instances to fix...")
                progress.update(task1, completed=75)
                
                # Apply fix
                updated_content = content.replace('.vocab_size()', '.vocab_size')
                progress.update(task1, completed=90)
                
                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                progress.update(task1, description="✓ Fixed vocab_size() calls", completed=100)
                
            console.print(f"[green]✓ Successfully fixed {occurrences} vocab_size() method calls[/green]")
        else:
            print("Reading B1 model file...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            occurrences = content.count('.vocab_size()')
            print(f"Found {occurrences} instances to fix...")
            
            # Apply fix
            updated_content = content.replace('.vocab_size()', '.vocab_size')
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✓ Successfully fixed {occurrences} vocab_size() method calls")
            
    except Exception as e:
        error_msg = f"Error during fix operation: {e}"
        if use_rich:
            console.print(f"[red]{error_msg}[/red]")
        else:
            print(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    fix_vocab_size_issue()
