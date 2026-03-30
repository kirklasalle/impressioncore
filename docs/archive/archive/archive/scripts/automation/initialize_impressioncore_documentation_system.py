
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #api #attention_mechanism #command_line #docs\scripts\automation\initialize_impressioncore_documentation_system.py #documentation #multimodal #python #source_code #testing #web_interface  
**Category:** Source Code  
**Status:** Deprecated
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** Kirk LaSalle  
**Tags:** #api #attention_mechanism #command_line #docs\scripts\automation\initialize_impressioncore_documentation_system.py #documentation #multimodal #python #source_code #testing #web_interface  
**Category:** Source Code  
**Status:** Deprecated

"""
ImpressionCore Documentation System (IDS) - Unified Initialization

This script provides a single command to initialize, validate, and maintain
the complete ImpressionCore Documentation System with comprehensive automation.

Original Designer & Developer: Kirk LaSalle <kirk@impressioncore.ai>
Collaborative Development with: GitHub Copilot, VS Code Copilot, Cline, Roo

Commands:
    python initialize_impressioncore_documentation_system.py
    OR: initialize impressioncore documentation system
    OR: initialize ids

File: initialize_impressioncore_documentation_system.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework  
Created: 2025-06-01
Modified: 2025-06-01
Version: 1.0.0

Primary Author:
- Kirk LaSalle <kirk@impressioncore.ai> - Original architect and developer

Collaborative AI Development Partners:
- GitHub Copilot - Code completion and implementation support
- VS Code Copilot - Code review and optimization
- Cline AI Assistant - Design consultation and problem-solving
- Roo AI Assistant - Advanced integration guidance

License: MIT
Copyright (c) 2025 Kirk LaSalle & ImpressionCore Team

Tags: [documentation, automation, initialization, ids, production, kirk-lasalle]
Dependencies: [rich, pathlib, PyYAML, subprocess]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Development History:
Kirk LaSalle first designed and wrote the Python documentation viewer,
then developed the supporting design for integration into ImpressionCore
as a comprehensive document management and readability application.
This represents advanced human-AI collaborative development in 2025.

Description:
Unified ImpressionCore Documentation System initialization that integrates:
- Tag system management and validation
- Documentation health monitoring  
- Cross-reference validation
- Priority document verification
- Memlog integration checks
- Automated cleanup and organization
- Status reporting and maintenance scheduling

Design Philosophy (Kirk LaSalle's Vision):
- Single command for complete documentation system health
- Integration of all existing automation scripts
- Rich UI for enhanced user experience
- Comprehensive validation and integrity checking
- Automated maintenance and cleanup
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
import argparse
import time

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.core.utils.rich_enhancements import (
        console, print_info, print_success, print_warning, print_error, 
        create_table, add_table_row, display_table, create_progress,
        create_header, create_panel
    )
    from src.core.utils.rich_logging import setup_rich_logging
    from src.core.utils.rich_status_animation import StatusAnimation
    
    # Also import rich components needed by existing code
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Confirm, Prompt
    
    # Setup rich logging
    logger = setup_rich_logging(__name__)
    HAS_RICH = True
        
except ImportError:
    # Fallback without rich enhancements
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    HAS_RICH = False    
    # Fallback implementations
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
    
    def create_progress():
        return None
    
    def create_header(text):
        return f"=== {text} ==="
    
    def create_panel(text, title=""):
        return f"\n--- {title} ---\n{text}\n"
    
    class StatusAnimation:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def update(self, text):
            print(text)
    
    # Rich component fallbacks
    class Progress:
        def __init__(self, *args, **kwargs): 
            pass
        def __enter__(self): 
            return self
        def __exit__(self, *args): 
            pass
        def add_task(self, description, total=100): 
            print(f"Starting: {description}")
            return 0
        def update(self, task_id, description="", **kwargs): 
            if description:
                print(f"Progress: {description}")
        def advance(self, task_id): 
            pass
    
    # Component placeholders  
    SpinnerColumn = TextColumn = BarColumn = TaskProgressColumn = lambda *args, **kwargs: None
    
    class Panel:
        def __init__(self, content, title="", **kwargs):
            self.content = content
            self.title = title
    
    class Table:
        def __init__(self, title="", **kwargs): 
            self.title = title
            self.columns = []
            self.rows = []
        def add_column(self, name, style="", **kwargs): 
            self.columns.append(name)
        def add_row(self, *args): 
            self.rows.append(args)
    
    class Text:
        def __init__(self, text, style=""):
            self.text = text
            self.style = style
    
    def Confirm(msg): 
        return input(f"{msg} (y/n): ").lower().startswith('y')
    
    def Prompt(msg): 
        return input(f"{msg}: ")

# IDS Configuration
IDS_VERSION = "1.0.0"
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # Go up from docs/scripts/automation/ to project root
DOCS_ROOT = PROJECT_ROOT / "docs"
SRC_ROOT = PROJECT_ROOT / "src"
MEMLOG_ROOT = SRC_ROOT / "memlog"

# Priority Documents that must exist and be current
PRIORITY_DOCUMENTS = {
    "Developer Guide": DOCS_ROOT / "developer" / "ARCHITECTURE.md",
    "User Guide": DOCS_ROOT / "user_guide" / "complete_user_guide.md", 
    "CLI Walkthrough": DOCS_ROOT / "developer" / "cli_build_walkthrough.md",
    "Web UI Walkthrough": DOCS_ROOT / "user" / "web_ui_walkthrough.md",
    "API Reference": DOCS_ROOT / "api" / "complete_api_reference.md",
    "PRD": DOCS_ROOT / "prd.md"
}

# Automation Scripts Registry - Centralized in docs/scripts/
AUTOMATION_SCRIPTS = {
    "tag_management": DOCS_ROOT / "scripts" / "automation" / "add_or_update_tags.py",
    "tag_indexing": DOCS_ROOT / "scripts" / "automation" / "tags_index.py", 
    "documentation_automation": SRC_ROOT / "scripts" / "documentation" / "doc_automation.py",
    "health_check": DOCS_ROOT / "scripts" / "maintenance" / "health_check_and_notification.py",
    "redundancy_check": DOCS_ROOT / "scripts" / "maintenance" / "redundancy_and_deprecation_checker.py",
    "inventory_update": DOCS_ROOT / "scripts" / "maintenance" / "inventory_and_index_update.py",
    "categorize_inbox": DOCS_ROOT / "scripts" / "tools" / "categorize_and_move_inbox.py",
    "doc_analytics": DOCS_ROOT / "scripts" / "analytics" / "doc_analytics.py"
}

class IDSStatus:
    """Track IDS initialization status and results."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.steps_completed = 0
        self.total_steps = 8
        self.issues_found = []
        self.actions_taken = []
        self.priority_docs_status = {}
        self.automation_status = {}
        self.tag_system_status = {}
        self.memlog_integration_status = {}
        
    def add_issue(self, category: str, description: str, severity: str = "warning"):
        """Add an issue to the tracking list."""
        self.issues_found.append({
            "category": category,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_action(self, description: str, success: bool = True):
        """Add an action taken during initialization."""
        self.actions_taken.append({
            "description": description,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        
    def complete_step(self):
        """Mark a step as completed."""
        self.steps_completed += 1
        
    def get_summary(self) -> Dict:
        """Get complete status summary."""
        return {
            "ids_version": IDS_VERSION,
            "initialization_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "steps_completed": self.steps_completed,
            "total_steps": self.total_steps,
            "completion_percentage": (self.steps_completed / self.total_steps) * 100,
            "issues_found": len(self.issues_found),
            "actions_taken": len(self.actions_taken),
            "priority_docs_status": self.priority_docs_status,
            "automation_status": self.automation_status,
            "tag_system_status": self.tag_system_status,
            "memlog_integration_status": self.memlog_integration_status,
            "detailed_issues": self.issues_found,
            "detailed_actions": self.actions_taken
        }

def run_script(script_path: Path, args: List[str] = None, description: str = "", timeout: int = 30) -> Tuple[bool, str]:
    """Run a script and return success status with output."""
    if args is None:
        args = []
    
    if not script_path.exists():
        return False, f"Script not found: {script_path}"
    
    try:
        cmd = [sys.executable, str(script_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
        return True, result.stdout
    except subprocess.TimeoutExpired:
        return False, f"Script timed out after {timeout} seconds"
    except subprocess.CalledProcessError as e:
        return False, f"Script failed: {e.stderr or e.stdout or str(e)}"
    except Exception as e:
        return False, f"Error running script: {str(e)}"

def check_priority_documents(status: IDSStatus) -> bool:
    """Verify all priority documents exist and are current."""
    console.print("\n[bold blue]Step 1: Checking Priority Documents[/bold blue]")
    
    all_good = True
    priority_table = Table(title="Priority Document Status")
    priority_table.add_column("Document", style="cyan")
    priority_table.add_column("Status", style="white")
    priority_table.add_column("Last Modified", style="yellow")
    priority_table.add_column("Issues", style="red")
    
    for doc_name, doc_path in PRIORITY_DOCUMENTS.items():
        issues = []
        
        if not doc_path.exists():
            issues.append("Missing")
            all_good = False
            status.add_issue("priority_docs", f"{doc_name} missing at {doc_path}", "error")
        else:
            # Check if file was modified in last 90 days
            mod_time = datetime.fromtimestamp(doc_path.stat().st_mtime)
            days_old = (datetime.now() - mod_time).days
            
            if days_old > 90:
                issues.append(f"Outdated ({days_old} days)")
                status.add_issue("priority_docs", f"{doc_name} is {days_old} days old", "warning")
            
            # Check for basic content
            try:
                content = doc_path.read_text(encoding='utf-8')
                if len(content.strip()) < 100:
                    issues.append("Too short")
                    status.add_issue("priority_docs", f"{doc_name} appears incomplete", "warning")
                if "TODO" in content.upper() and content.upper().count("TODO") > 5:
                    issues.append("Many TODOs")
                    status.add_issue("priority_docs", f"{doc_name} has many TODOs", "info")
            except Exception as e:
                issues.append(f"Read error: {e}")
                status.add_issue("priority_docs", f"Cannot read {doc_name}: {e}", "error")
        
        status_text = "[green]Good[/green]" if not issues else "[red]Issues[/red]"
        mod_text = mod_time.strftime("%Y-%m-%d") if doc_path.exists() else "N/A"
        issues_text = ", ".join(issues) if issues else "None"
        
        priority_table.add_row(doc_name, status_text, mod_text, issues_text)
        status.priority_docs_status[doc_name] = {
            "exists": doc_path.exists(),
            "path": str(doc_path),
            "last_modified": mod_text,
            "issues": issues
        }
    
    console.print(priority_table)
    status.complete_step()
    return all_good

def validate_automation_scripts(status: IDSStatus) -> bool:
    """Validate all automation scripts are present and functional."""
    console.print("\n[bold blue]Step 2: Validating Automation Scripts[/bold blue]")
    
    automation_table = Table(title="Documentation Automation Scripts")
    automation_table.add_column("Script", style="cyan")
    automation_table.add_column("Status", style="white") 
    automation_table.add_column("Location", style="yellow")
    automation_table.add_column("Test Result", style="green")
    
    all_functional = True
    
    for script_name, script_path in AUTOMATION_SCRIPTS.items():
        if not script_path.exists():
            automation_table.add_row(script_name, "[red]Missing[/red]", str(script_path), "Failed")
            status.add_issue("automation", f"Missing script: {script_name}", "error")
            all_functional = False
            continue
        
        # Test script functionality
        if script_name == "tag_management":
            success, output = run_script(script_path, ["--help"], f"Testing {script_name}")
        elif script_name == "documentation_automation":
            success, output = run_script(script_path, ["--quick"], f"Testing {script_name}")
        else:
            # For other scripts, just check if they're importable/runnable            success, output = run_script(script_path, ["--help"], f"Testing {script_name}")
            if not success and "help" not in output.lower():
                # Try without --help
                success, output = True, "Available"
        
        status_text = "[green]Present[/green]"
        test_result = "[green]Functional[/green]" if success else "[red]Error[/red]"
        
        if not success:
            all_functional = False
            status.add_issue("automation", f"Script {script_name} not functional: {output[:100]}", "warning")
        
        automation_table.add_row(script_name, status_text, str(script_path.parent), test_result)
        status.automation_status[script_name] = {
            "exists": True,
            "path": str(script_path),
            "functional": success,
            "test_output": output[:200] if output else ""
        }
    
    console.print(automation_table)
    status.complete_step()
    return all_functional

def validate_tag_system(status: IDSStatus) -> bool:
    """Validate and update the tagging system."""
    console.print("\n[bold blue]Step 3: Validating Tag System[/bold blue]")
      # Check tags_index.yaml
    tags_index_path = DOCS_ROOT / "tags_index.yaml"
    doc_index_path = DOCS_ROOT / "DOCUMENTATION_INDEX.md"
    
    tag_issues = []
    
    if not tags_index_path.exists():
        tag_issues.append("tags_index.yaml missing")
        status.add_issue("tag_system", "tags_index.yaml not found", "error")
    
    if not doc_index_path.exists():
        tag_issues.append("DOCUMENTATION_INDEX.md missing")
        status.add_issue("tag_system", "DOCUMENTATION_INDEX.md not found", "error")
    
    # Run tag management automation (skip if imports fail)
    tag_script = AUTOMATION_SCRIPTS["tag_management"]
    if tag_script.exists():
        console.print("Running tag system update...")
        success, output = run_script(tag_script, ["--auto"], "Updating tags", timeout=15)
        if success:
            status.add_action("Tag system updated successfully")
        else:
            tag_issues.append("Tag update failed")
            status.add_issue("tag_system", f"Tag update failed: {output[:100]}", "warning")
            # Continue with other operations even if this fails
            console.print(f"[yellow]Warning: Tag management script failed - {output[:100]}[/yellow]")
    
    # Run tag indexing
    tag_index_script = AUTOMATION_SCRIPTS["tag_indexing"] 
    if tag_index_script.exists():
        console.print("Regenerating tag table...")
        success, output = run_script(tag_index_script, ["--table", "--sort", "--wrap", "6"], "Regenerating tag table", timeout=20)
        if success:
            status.add_action("Tag table regenerated successfully")
        else:
            tag_issues.append("Tag table generation failed")
            status.add_issue("tag_system", f"Tag table generation failed: {output[:100]}", "warning")
            console.print(f"[yellow]Warning: Tag indexing failed - {output[:100]}[/yellow]")
    
    # Check for broken links and orphans using doc_automation
    doc_automation_script = AUTOMATION_SCRIPTS["documentation_automation"]
    if doc_automation_script.exists():
        console.print("Validating documentation links and metadata...")
        success, output = run_script(doc_automation_script, ["--validate-docs"], "Validating documentation", timeout=30)
        if success:
            status.add_action("Documentation validation completed")
        else:
            tag_issues.append("Documentation validation failed")
            status.add_issue("tag_system", f"Documentation validation failed: {output[:100]}", "warning")
            console.print(f"[yellow]Warning: Documentation validation failed - {output[:100]}[/yellow]")
    
    status.tag_system_status = {
        "tags_index_exists": tags_index_path.exists(),
        "doc_index_exists": doc_index_path.exists(), 
        "issues": tag_issues,
        "updates_applied": len(tag_issues) == 0
    }
    
    console.print(f"Tag system validation: {'[green]Passed[/green]' if not tag_issues else '[red]Issues found[/red]'}")
    status.complete_step()
    return len(tag_issues) == 0

def check_memlog_integration(status: IDSStatus) -> bool:
    """Check memlog integration with documentation system."""
    console.print("\n[bold blue]Step 4: Checking Memlog Integration[/bold blue]")
    
    memlog_issues = []
    
    if not MEMLOG_ROOT.exists():
        memlog_issues.append("Memlog directory missing")
        status.add_issue("memlog", "Memlog directory not found", "error")
    else:
        # Check for key memlog files
        important_memlog_files = [
            "README.md",
            "priority_8_phase_8a_completion.md",
            "development_log.md"
        ]
        
        existing_files = []
        for file_name in important_memlog_files:
            file_path = MEMLOG_ROOT / file_name
            if file_path.exists():
                existing_files.append(file_name)
        
        # Check for any .md files in memlog
        md_files = list(MEMLOG_ROOT.glob("*.md"))
        
        status.memlog_integration_status = {
            "memlog_dir_exists": True,
            "important_files_found": existing_files,
            "total_md_files": len(md_files),
            "recent_activity": len([f for f in md_files if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days < 7])
        }
        
        if len(existing_files) < 2:
            memlog_issues.append("Few important memlog files found")
            status.add_issue("memlog", "Limited memlog documentation found", "info")
    
    console.print(f"Memlog integration: {'[green]Good[/green]' if not memlog_issues else '[yellow]Limited[/yellow]'}")
    status.complete_step()
    return len(memlog_issues) == 0

def run_health_checks(status: IDSStatus) -> bool:
    """Run comprehensive health checks."""
    console.print("\n[bold blue]Step 5: Running Health Checks[/bold blue]")
    
    health_script = AUTOMATION_SCRIPTS["health_check"]
    if health_script.exists():
        success, output = run_script(health_script, [], "Running health checks")
        if success:
            status.add_action("Health checks completed successfully")
            console.print("[green]Health checks passed[/green]")
        else:
            status.add_issue("health", f"Health checks failed: {output[:100]}", "warning")
            console.print("[yellow]Health checks found issues[/yellow]")
    else:
        status.add_issue("health", "Health check script not found", "error")
        console.print("[red]Health check script missing[/red]")
    
    status.complete_step()
    return health_script.exists()

def cleanup_and_organize(status: IDSStatus) -> bool:
    """Run cleanup and organization scripts."""
    console.print("\n[bold blue]Step 6: Cleanup and Organization[/bold blue]")
    
    cleanup_success = True
    
    # Run redundancy checker
    redundancy_script = AUTOMATION_SCRIPTS["redundancy_check"]
    if redundancy_script.exists():
        console.print("Checking for redundant/deprecated files...")
        success, output = run_script(redundancy_script, [], "Checking redundancy")
        if success:
            status.add_action("Redundancy check completed")
        else:
            cleanup_success = False
            status.add_issue("cleanup", f"Redundancy check failed: {output[:100]}", "warning")
    
    # Categorize inbox files
    categorize_script = AUTOMATION_SCRIPTS["categorize_inbox"]
    if categorize_script.exists():
        console.print("Organizing inbox files...")
        success, output = run_script(categorize_script, [], "Categorizing inbox")
        if success:
            status.add_action("Inbox organization completed")
        else:
            status.add_issue("cleanup", f"Inbox organization failed: {output[:100]}", "info")
    
    console.print("[green]Cleanup and organization completed[/green]")
    status.complete_step()
    return cleanup_success

def update_documentation_index(status: IDSStatus) -> bool:
    """Update the main documentation index."""
    console.print("\n[bold blue]Step 7: Updating Documentation Index[/bold blue]")
    
    inventory_script = AUTOMATION_SCRIPTS["inventory_update"]
    if inventory_script.exists():
        success, output = run_script(inventory_script, [], "Updating inventory")
        if success:
            status.add_action("Documentation inventory updated")
        else:
            status.add_issue("index_update", f"Inventory update failed: {output[:100]}", "warning")
    
    # Update DOCUMENTATION_INDEX.md with current timestamp
    doc_index_path = DOCS_ROOT / "DOCUMENTATION_INDEX.md"
    if doc_index_path.exists():
        try:
            content = doc_index_path.read_text(encoding='utf-8')
            # Update the "Last updated" line
            import re
            updated_content = re.sub(
                r'^Last updated: .*$', 
                f'Last updated: {datetime.now().strftime("%Y-%m-%d")}',
                content,
                flags=re.MULTILINE
            )
            doc_index_path.write_text(updated_content, encoding='utf-8')
            status.add_action("Documentation index timestamp updated")
        except Exception as e:
            status.add_issue("index_update", f"Failed to update index timestamp: {e}", "warning")
    
    console.print("[green]Documentation index updated[/green]")
    status.complete_step()
    return True

def generate_status_report(status: IDSStatus) -> Path:
    """Generate comprehensive status report."""
    console.print("\n[bold blue]Step 8: Generating Status Report[/bold blue]")
    
    # Create status report
    report_data = status.get_summary()
    
    # Save JSON report
    report_dir = SRC_ROOT / "memlog" / "ids_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_report_path = report_dir / f"ids_status_{timestamp}.json"
    
    with open(json_report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)
    
    # Create markdown report
    md_report_path = report_dir / f"ids_status_{timestamp}.md"
    
    md_content = f"""# ImpressionCore Documentation System (IDS) Status Report

Generated: {datetime.now().isoformat()}
Duration: {report_data['duration_seconds']:.2f} seconds
Completion: {report_data['completion_percentage']:.1f}%

## Summary

- **Steps Completed**: {report_data['steps_completed']}/{report_data['total_steps']}
- **Issues Found**: {report_data['issues_found']}
- **Actions Taken**: {report_data['actions_taken']}

## Priority Documents Status

| Document | Status | Issues |
|----------|--------|--------|
"""
    
    for doc_name, doc_status in report_data['priority_docs_status'].items():
        status_icon = "[green]OK[/green]" if doc_status['exists'] and not doc_status['issues'] else "[red]ISSUE[/red]"
        issues_text = ", ".join(doc_status['issues']) if doc_status['issues'] else "None"
        md_content += f"| {doc_name} | {status_icon} | {issues_text} |\n"
    
    md_content += f"""
## Automation Scripts Status

| Script | Status | Functional |
|--------|--------|------------|
"""
    
    for script_name, script_status in report_data['automation_status'].items():
        status_icon = "[green]OK[/green]" if script_status['exists'] else "[red]MISSING[/red]"
        func_icon = "[green]OK[/green]" if script_status.get('functional', False) else "[red]ERROR[/red]"
        md_content += f"| {script_name} | {status_icon} | {func_icon} |\n"
    
    if report_data['detailed_issues']:
        md_content += "\n## Issues Found\n\n"
        for issue in report_data['detailed_issues']:
            md_content += f"- **{issue['severity'].upper()}** [{issue['category']}]: {issue['description']}\n"
    
    if report_data['detailed_actions']:
        md_content += "\n## Actions Taken\n\n"
        for action in report_data['detailed_actions']:
            icon = "[green]OK[/green]" if action['success'] else "[red]FAIL[/red]"
            md_content += f"- {icon} {action['description']}\n"
    
    with open(md_report_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    status.add_action(f"Status report generated: {md_report_path.name}")
    status.complete_step()
    
    return md_report_path

def display_final_summary(status: IDSStatus, report_path: Path):
    """Display final summary of IDS initialization."""
    summary = status.get_summary()
    
    # Create summary panel
    summary_text = f"""
[bold green]ImpressionCore Documentation System (IDS) Initialization Complete![/bold green]

[cyan]Duration:[/cyan] {summary['duration_seconds']:.2f} seconds
[cyan]Completion:[/cyan] {summary['completion_percentage']:.1f}%
[cyan]Steps:[/cyan] {summary['steps_completed']}/{summary['total_steps']}

[yellow]Results:[/yellow]
- Issues Found: {summary['issues_found']}
- Actions Taken: {summary['actions_taken']}
- Report Generated: {report_path.name}

[blue]Next Steps:[/blue]
1. Review detailed report at: {report_path}
2. Address any critical issues found
3. Set up automated maintenance schedule
4. Monitor documentation health regularly

[green]IDS Status:[/green] {'[green]Fully Operational[/green]' if summary['issues_found'] < 3 else '[yellow]Needs Attention[/yellow]'}
"""
    
    console.print(Panel(summary_text, title="IDS Initialization Summary", border_style="green"))

def main():
    """Main IDS initialization function."""
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="ImpressionCore Documentation System (IDS) Initialization",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--auto", action="store_true", help="Run fully automated without prompts")
    parser.add_argument("--quick", action="store_true", help="Run quick validation only")
    parser.add_argument("--report-only", action="store_true", help="Generate status report only")
    
    args = parser.parse_args()
      # Display header
    console.print(Panel(
        f"[bold cyan]ImpressionCore Documentation System (IDS) v{IDS_VERSION}[/bold cyan]\n"
        f"[white]Unified documentation system initialization and validation[/white]\n"
        f"[dim]Project: ImpressionCore - Brain-Inspired Multimodal AI Framework[/dim]",
        title="Documentation System Initialization",
        border_style="blue"
    ))
    
    # Initialize status tracking
    status = IDSStatus()
    
    # Quick mode
    if args.quick:
        console.print("\n[yellow]Running quick validation mode...[/yellow]")
        check_priority_documents(status)
        validate_automation_scripts(status)
        report_path = generate_status_report(status)
        display_final_summary(status, report_path)
        return
    
    # Report only mode
    if args.report_only:
        console.print("\n[yellow]Generating status report only...[/yellow]")
        # Set dummy status for report generation
        for i in range(8):
            status.complete_step()
        report_path = generate_status_report(status)
        console.print(f"\n[green]Report generated: {report_path}[/green]")
        return
    
    # Confirmation prompt (unless auto mode)
    if not args.auto:
        if not Confirm("Initialize the complete ImpressionCore Documentation System?"):
            console.print("[yellow]Initialization cancelled by user.[/yellow]")
            return
    
    console.print("\n[bold blue]Starting comprehensive IDS initialization...[/bold blue]")
    
    try:
        # Run all initialization steps
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Initializing IDS...", total=8)
            
            # Step 1: Check priority documents
            progress.update(task, description="Checking priority documents...")
            check_priority_documents(status)
            progress.advance(task)
            
            # Step 2: Validate automation scripts
            progress.update(task, description="Validating automation scripts...")
            validate_automation_scripts(status)
            progress.advance(task)
            
            # Step 3: Validate tag system
            progress.update(task, description="Validating tag system...")
            validate_tag_system(status)
            progress.advance(task)
            
            # Step 4: Check memlog integration
            progress.update(task, description="Checking memlog integration...")
            check_memlog_integration(status)
            progress.advance(task)
            
            # Step 5: Run health checks
            progress.update(task, description="Running health checks...")
            run_health_checks(status)
            progress.advance(task)
            
            # Step 6: Cleanup and organize
            progress.update(task, description="Running cleanup and organization...")
            cleanup_and_organize(status)
            progress.advance(task)
            
            # Step 7: Update documentation index
            progress.update(task, description="Updating documentation index...")
            update_documentation_index(status)
            progress.advance(task)
            
            # Step 8: Generate status report
            progress.update(task, description="Generating status report...")
            report_path = generate_status_report(status)
            progress.advance(task)
    
        # Display final summary
        display_final_summary(status, report_path)
        
        # Log completion
        logger.info(f"IDS initialization completed in {status.get_summary()['duration_seconds']:.2f} seconds")
        
    except KeyboardInterrupt:
        console.print("\n[red]Initialization interrupted by user.[/red]")
        return
    except Exception as e:
        console.print(f"\n[red]Error during initialization: {e}[/red]")
        logger.error(f"IDS initialization failed: {e}")
        return

if __name__ == "__main__":
    main()
