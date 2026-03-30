#!/usr/bin/env python3
"""
ImpressionCore: Documentation System Automation

Simple automation script to maintain the ImpressionCore documentation system.
This script provides an easy interface to analyze, enhance, and maintain
code documentation across the entire project.

File: scripts/documentation/doc_automation.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-31
Version: 1.1.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [documentation, automation, simple, production, validation]
Dependencies: [rich, pathlib, PyYAML]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Simple automation wrapper for the comprehensive documentation enhancement
system. Provides easy commands for common documentation tasks, including
validation of the documentation index and metadata checks.

Usage:
    python doc_automation.py                  # Full analysis and report (via enhance_code_docs.py)
    python doc_automation.py --quick          # Quick health check
    python doc_automation.py --enhance        # Enhance all files (via enhance_code_docs.py)
    python doc_automation.py --todos          # Extract TODO items (via enhance_code_docs.py)
    python doc_automation.py --validate-docs  # Validate DOCUMENTATION_INDEX.md and doc metadata
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Set, Dict, Tuple
import re
import datetime
import argparse
import urllib.parse

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich import print as rprint
    from core.utils.rich_logging import get_rich_logger # Assuming this function exists
    logger = get_rich_logger(__name__)
except ImportError:
    # Fallback if rich or rich_logging is not available
    class FallbackLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")

    logger = FallbackLogger()
    
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    
    def Panel(text, **kwargs):
        return text
    
    def rprint(*args, **kwargs):
        print(*args)

    class Table:
        def __init__(self, title=None): self.title = title; self.columns = []; self.rows = []
        def add_column(self, header, style=None, justify=None): self.columns.append(header)
        def add_row(self, *items): self.rows.append(items)
        def __rich_console__(self, console, options):
            if self.title: console.print(self.title)
            console.print(" | ".join(self.columns))
            for row in self.rows: console.print(" | ".join(map(str, row)))
            return ""


console = Console()
DOCS_ROOT_PATH = src_path.parent / "docs"
DOC_INDEX_FILE = DOCS_ROOT_PATH / "DOCUMENTATION_INDEX.md"
METADATA_AGE_THRESHOLD_DAYS = 90 # About 3 months

def run_enhancement_script(args: List[str]) -> bool:
    """
    Run the main enhancement script with given arguments.
    """
    script_path = Path(__file__).parent / "enhance_code_docs.py"
    logger.info(f"Running enhancement script: {script_path} with args: {args}")
    try:
        cmd = [sys.executable, str(script_path)] + args
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            logger.warning(f"Enhancement script warnings: {result.stderr}")
            console.print(f"[yellow]Enhancement Script Warnings:[/yellow]\n{result.stderr}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running documentation script {script_path}: {e}")
        console.print(f"[red]Error running documentation script:[/red]")
        console.print(f"[red]Exit code:[/red] {e.returncode}")
        if e.stdout:
            console.print(f"[red]Output:[/red] {e.stdout}")
        if e.stderr:
            console.print(f"[red]Error:[/red] {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error(f"Enhancement script not found at: {script_path}")
        console.print(f"[red]Enhancement script not found at:[/red] {script_path}")
        return False

def quick_health_check() -> None:
    """Perform a quick documentation health check."""
    logger.info("Performing quick documentation health check.")
    console.print(Panel("📊 Quick Documentation Health Check", style="bold blue"))
    
    python_files = list(src_path.rglob("*.py"))
    
    if not python_files:
        logger.warning("No Python files found in src directory for quick health check.")
        console.print("[red]No Python files found in src directory[/red]")
        return
    
    console.print(f"[green]Found {len(python_files)} Python files in src/[/green]")
    
    console.print("\n[bold]Key Documentation Files Status:[/bold]")
    key_docs_to_check = {
        "DOCUMENTATION_INDEX.md": DOC_INDEX_FILE,
        "developer/code_documentation_standards.md": DOCS_ROOT_PATH / "developer" / "code_documentation_standards.md",
        "api/complete_api_reference.md": DOCS_ROOT_PATH / "api" / "complete_api_reference.md",
        "process/implementation_status.md": DOCS_ROOT_PATH / "process" / "implementation_status.md"
    }
    
    for name, path in key_docs_to_check.items():
        if path.exists():
            console.print(f"[green]✓[/green] {name}")
            if name == "DOCUMENTATION_INDEX.md":
                try:
                    content = path.read_text(encoding='utf-8')
                    if "Last updated:" not in content[:300]: # Check near top
                         console.print(f"  [yellow]⚠[/yellow] {name} - 'Last updated:' field might be missing or not prominent.")
                except Exception as e:
                    logger.warning(f"Could not read {name} for metadata check: {e}")
        else:
            logger.warning(f"Key documentation file missing: {path}")
            console.print(f"[red]✗[/red] {name} (Missing!)")
    
    sample_files = python_files[:min(5, len(python_files))]
    console.print(f"\n[bold]Sample Python File Analysis ({len(sample_files)} files):[/bold]")
    
    for filepath in sample_files:
        try:
            content = filepath.read_text(encoding='utf-8')
            has_header = "ImpressionCore:" in content[:1000]
            has_docstring = '"""' in content[:2000] # Basic check
            
            status = "✓" if has_header and has_docstring else "⚠"
            color = "green" if has_header and has_docstring else "yellow"
            
            relative_path = filepath.relative_to(src_path.parent) # Show relative to project root
            console.print(f"[{color}]{status}[/{color}] {relative_path}")
            
        except Exception as e:
            logger.warning(f"Error analyzing sample Python file {filepath.name}: {e}")
            console.print(f"[red]✗[/red] {filepath.name} (error: {e})")

def parse_markdown_links(content: str, file_path: Path) -> Set[Path]:
    """Extracts all relative markdown links from content."""
    # Regex for [text](link.md) where link does not start with http(s):// or mailto:
    # and captures the link part. Handles links like `../file.md`, `subfolder/file.md`, `file.md`
    # It also handles links with anchors like `file.md#section`
    # Revised regex to fix unbalanced parenthesis and improve .md matching:
    links = re.findall(r"\[[^\]]*\]\(((?!https?://|mailto:)[^)\s#]+?(?:\.md|\.MD))(?:#[^)]*)?\)", content)
    
    resolved_links = set()
    # The regex now directly captures the link_target that ends with .md or .MD
    for link_target in links:
        decoded_link_target = urllib.parse.unquote(link_target)
        # Resolve relative to the directory of the current file_path
        resolved_link = (file_path.parent / decoded_link_target).resolve()
        logger.debug(f"Original link: '{link_target}', Decoded: '{decoded_link_target}', Resolved: '{resolved_link}'")
        resolved_links.add(resolved_link)
    return resolved_links

def validate_documentation_index() -> bool:
    """Validates DOCUMENTATION_INDEX.md: checks links and finds orphans."""
    logger.info(f"Starting validation of {DOC_INDEX_FILE}")
    if not DOC_INDEX_FILE.exists():
        logger.error(f"{DOC_INDEX_FILE} not found.")
        console.print(f"[red]Error: {DOC_INDEX_FILE} not found.[/red]")
        return False

    try:
        index_content = DOC_INDEX_FILE.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Could not read {DOC_INDEX_FILE}: {e}")
        console.print(f"[red]Error reading {DOC_INDEX_FILE}: {e}[/red]")
        return False

    linked_markdown_files = parse_markdown_links(index_content, DOC_INDEX_FILE)
    
    broken_links_table = Table(title="Broken Links in DOCUMENTATION_INDEX.md")
    broken_links_table.add_column("Linked Path from Index", style="magenta")
    broken_links_count = 0

    for link_path in sorted(list(linked_markdown_files)):
        try:
            # We check if the target file actually exists and is a file.
            # Links outside DOCS_ROOT_PATH are now allowed if they resolve correctly.
            if not link_path.exists() or not link_path.is_file():
                # Try to make the path relative to the project root for display
                try:
                    display_path = str(link_path.relative_to(DOCS_ROOT_PATH.parent))
                except ValueError:
                    display_path = str(link_path) # Fallback to absolute if not under project root for some reason
                broken_links_table.add_row(display_path)
                broken_links_count += 1
                logger.warning(f"Broken link in index. Resolved path: {link_path} (points to non-existent or non-file target). Exists: {link_path.exists()}, Is File: {link_path.is_file()}")
        except Exception as e: # Catch potential errors from path operations
            broken_links_table.add_row(f"Error processing link: {link_path} - {e}")
            broken_links_count += 1
            logger.warning(f"Error processing link {link_path}: {e}")


    if broken_links_count > 0:
        console.print(broken_links_table)
    else:
        console.print("[green]✓ No broken markdown links found in DOCUMENTATION_INDEX.md.[/green]")

    # Find orphaned markdown files
    all_markdown_in_docs: Set[Path] = set()
    for md_file in DOCS_ROOT_PATH.rglob("*.md"):
        # Exclude archive and the index file itself
        if "docs/archive/" not in str(md_file.as_posix()).lower() and md_file.name != DOC_INDEX_FILE.name:
            # Ensure we are dealing with files within the intended docs directory structure
            try:
                if md_file.resolve().is_relative_to(DOCS_ROOT_PATH.resolve()):
                    all_markdown_in_docs.add(md_file.resolve())
            except ValueError: # Handles cases where resolve() might lead outside expected parentage due to complex symlinks
                logger.debug(f"Skipping {md_file} from orphaned check as its resolved path is not relative to DOCS_ROOT_PATH.")


    # Files linked from index, ensuring they are also resolved for fair comparison
    # Only consider linked files that exist for the purpose of finding orphans
    # This means if a link is broken (file doesn't exist), it won't prevent a file from being listed as orphan if it exists
    # but isn't linked from anywhere else. This seems correct.
    resolved_linked_files_from_index = {p.resolve() for p in linked_markdown_files if p.exists() and p.is_file()}

    orphaned_files = all_markdown_in_docs - resolved_linked_files_from_index
    
    if orphaned_files:
        orphaned_table = Table(title="Orphaned Markdown Files in docs/ (Not linked from INDEX or links are broken)")
        orphaned_table.add_column("Orphaned File Path", style="yellow")
        for orphan in sorted(list(orphaned_files)):
            orphaned_table.add_row(str(orphan.relative_to(DOCS_ROOT_PATH.parent))) # Show relative to project
            logger.warning(f"Orphaned .md file found: {orphan}")
        console.print(orphaned_table)
    else:
        console.print("[green]✓ No orphaned markdown files found in docs/ (excluding archive).[/green]")
    
    logger.info("Documentation index validation finished.")
    # The overall validation result depends on both broken links and orphaned files within docs/
    # A link to outside docs/ that is valid (exists) is not a failure for this function anymore.
    # However, an orphaned file within docs/ is still a validation failure.
    return broken_links_count == 0 and not orphaned_files

def check_markdown_file_metadata() -> bool:
    """Checks metadata (Last updated, Responsible) for all .md files in docs/."""
    logger.info("Starting markdown file metadata check.")
    files_to_check = [
        p for p in DOCS_ROOT_PATH.rglob("*.md") 
        if "docs/archive/" not in str(p.as_posix()).lower() # Exclude archive
    ]
    
    # Also check files linked from the index that might be outside DOCS_ROOT_PATH
    # but only if they are markdown files and not already in files_to_check
    if DOC_INDEX_FILE.exists():
        try:
            index_content = DOC_INDEX_FILE.read_text(encoding="utf-8")
            linked_files_from_index = parse_markdown_links(index_content, DOC_INDEX_FILE)
            for linked_file in linked_files_from_index:
                if linked_file.exists() and linked_file.is_file() and linked_file.suffix.lower() == '.md':
                    # Check if it's already in the list to avoid duplicates
                    already_added = False
                    for existing_file_path in files_to_check:
                        if existing_file_path.resolve() == linked_file.resolve():
                            already_added = True
                            break
                    if not already_added:
                        files_to_check.append(linked_file)
                        logger.debug(f"Added linked file {linked_file} to metadata check list.")
        except Exception as e:
            logger.error(f"Could not parse DOC_INDEX_FILE for metadata check of linked files: {e}")

    metadata_issues_table = Table(title=f"Markdown File Metadata Issues (Threshold: {METADATA_AGE_THRESHOLD_DAYS} days old for 'Last updated')")
    metadata_issues_table.add_column("File Path", style="cyan")
    metadata_issues_table.add_column("Issue Type", style="red")
    metadata_issues_table.add_column("Details", style="yellow")
    issues_found_count = 0

    # Use a set to ensure we process each unique resolved path only once
    processed_paths_for_metadata: Set[Path] = set()

    for md_file_orig_path in sorted(files_to_check, key=lambda p: p.resolve()):
        md_file = md_file_orig_path.resolve()
        if md_file in processed_paths_for_metadata:
            continue
        processed_paths_for_metadata.add(md_file)

        try:
            content = md_file.read_text(encoding="utf-8")
            # Basic frontmatter parsing or string search
            
            last_updated_match = re.search(r"^(?:Last updated|Updated): *(\d{4}-\d{2}-\d{2})", content, re.MULTILINE | re.IGNORECASE)
            responsible_match = re.search(r"^(?:Responsible|Author[s]?): *(@\S+|[^\n]+)", content, re.MULTILINE | re.IGNORECASE)

            file_display_path = str(md_file_orig_path.relative_to(DOCS_ROOT_PATH.parent) if md_file_orig_path.is_relative_to(DOCS_ROOT_PATH.parent) else md_file_orig_path)

            if not last_updated_match:
                metadata_issues_table.add_row(file_display_path, "Missing Metadata", "'Last updated: YYYY-MM-DD' not found or malformed.")
                logger.warning(f"Missing 'Last updated' in {md_file}")
                issues_found_count +=1
            else:
                try:
                    last_updated_date_str = last_updated_match.group(1)
                    last_updated_date = datetime.datetime.strptime(last_updated_date_str, "%Y-%m-%d").date()
                    if (datetime.date.today() - last_updated_date).days > METADATA_AGE_THRESHOLD_DAYS:
                        metadata_issues_table.add_row(
                            file_display_path, 
                            "Outdated Metadata", 
                            f"'Last updated: {last_updated_date_str}' is older than {METADATA_AGE_THRESHOLD_DAYS} days."
                        )
                        logger.warning(f"Outdated 'Last updated' in {md_file}: {last_updated_date_str}")
                        issues_found_count +=1
                except ValueError:
                    metadata_issues_table.add_row(file_display_path, "Malformed Metadata", f"'Last updated: {last_updated_match.group(1)}' is not a valid date format (YYYY-MM-DD).")
                    logger.warning(f"Malformed 'Last updated' in {md_file}: {last_updated_match.group(1)}")
                    issues_found_count +=1


            if not responsible_match:
                metadata_issues_table.add_row(file_display_path, "Missing Metadata", "'Responsible: @Username' or 'Author(s): Text' not found or malformed.")
                logger.warning(f"Missing 'Responsible' or 'Author(s)' in {md_file}")
                issues_found_count +=1
            elif not responsible_match.group(1).startswith("@") and "@" not in responsible_match.group(1):
                # If it's not an @Username, it could be a name. We'll be more lenient here for now.
                # But if it's clearly not an @ handle and also doesn't look like a name, it might be an issue.
                # For now, just ensure it's not empty if it's not an @ handle.
                if not responsible_match.group(1).strip():
                    metadata_issues_table.add_row(file_display_path, "Malformed Metadata", "'Responsible/Author(s)' field is present but empty.")
                    logger.warning(f"Empty 'Responsible/Author(s)' field in {md_file}")
                    issues_found_count +=1
        
        except Exception as e:
            file_display_path_err = str(md_file_orig_path.relative_to(DOCS_ROOT_PATH.parent) if md_file_orig_path.is_relative_to(DOCS_ROOT_PATH.parent) else md_file_orig_path)
            metadata_issues_table.add_row(file_display_path_err, "Read/Parse Error", str(e))
            logger.error(f"Error reading or parsing metadata for {md_file}: {e}")
            issues_found_count +=1

    if issues_found_count > 0:
        console.print(metadata_issues_table)
    else:
        console.print("[green]✓ No metadata issues found in markdown files (including linked files, excluding archive).[/green]")
    
    logger.info("Markdown file metadata check finished.")
    return issues_found_count == 0

def main():
    """Main function with simple command interface."""
    
    parser = argparse.ArgumentParser(
        description="ImpressionCore Documentation Automation System",
        formatter_class=argparse.RawTextHelpFormatter # To allow newlines in help
    )
    parser.add_argument("--quick", action="store_true", help="Perform a quick documentation health check.")
    parser.add_argument("--enhance", action="store_true", help="Enhance all files (calls enhance_code_docs.py --enhance). Requires review.")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode for --enhance operation.")
    parser.add_argument("--todos", action="store_true", help="Extract TODO items (calls enhance_code_docs.py --analyze --extract-todos).")
    parser.add_argument(
        "--validate-docs", 
        action="store_true", 
        help="Validate DOCUMENTATION_INDEX.md for broken links & orphans,\nand check all .md files for 'Last updated' & 'Responsible' metadata."
    )
    parser.add_argument(
        "--full-analysis",
        action="store_true",
        help="Run full documentation analysis (calls enhance_code_docs.py --analyze)."
    )
    
    args = parser.parse_args()
    
    console.print(Panel("🚀 ImpressionCore Documentation System", style="bold blue"))
    logger.info("ImpressionCore Documentation System script started.")

    if not any(vars(args).values()): # If no arguments are passed, default to --full-analysis
        logger.info("No arguments provided, defaulting to --full-analysis.")
        args.full_analysis = True


    if args.quick:
        quick_health_check()
    
    if args.todos:
        logger.info("Executing TODO extraction.")
        console.print("[bold blue]Extracting TODO items...[/bold blue]")
        if run_enhancement_script(["--analyze", "--extract-todos"]):
            console.print("[green]TODO extraction completed[/green]")
        else:
            logger.error("TODO extraction script failed.")
    
    if args.enhance:
        logger.info(f"Executing documentation enhancement. Dry run: {args.dry_run}")
        console.print("[bold blue]Enhancing documentation...[/bold blue]")
        enhance_args = ["--enhance"]
        if args.dry_run:
            enhance_args.append("--dry-run")
        
        if run_enhancement_script(enhance_args):
            console.print("[green]Documentation enhancement completed[/green]")
        else:
            logger.error("Documentation enhancement script failed.")

    if args.validate_docs:
        console.print("[bold blue]Validating documentation index and metadata...[/bold blue]")
        index_ok = validate_documentation_index()
        metadata_ok = check_markdown_file_metadata()
        if index_ok and metadata_ok:
            console.print("\n[bold green]✓ All documentation validation checks passed![/bold green]")
        else:
            console.print("\n[bold red]✗ Some documentation validation checks failed. Please review output.[/bold red]")
            logger.warning("Documentation validation checks failed.")
            
    if args.full_analysis: # Changed from default to explicit flag
        logger.info("Executing full documentation analysis.")
        console.print("[bold blue]Running full documentation analysis (via enhance_code_docs.py)...[/bold blue]")
        if run_enhancement_script(["--analyze"]):
            console.print("\n[bold green]Full analysis completed![/bold green]")
        else:
            logger.error("Full analysis script failed.")

    logger.info("ImpressionCore Documentation System script finished.")

if __name__ == "__main__":
    main()
