#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\ids.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** ImpressionCore Team  
**Tags:** #docs\ids.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore Documentation System (IDS) - Unified Interface
==============================================================

Single entry point for all IDS documentation management functions.
Provides a rich menu interface for accessing all documentation tools.

Author: IDS System
Created: 2024-12-06
Last Modified: 2024-12-06
"""

import sys
import subprocess
import argparse
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


# Script Categories and Mappings
SCRIPT_CATEGORIES = {
    "automation": {
        "description": "Core IDS automation scripts",
        "scripts": {
            "ids_coordinator": {
                "file": "initialize_impressioncore_documentation_system.py",
                "description": "Main IDS coordinator and initialization"
            },
            "tag_management": {
                "file": "add_or_update_tags.py", 
                "description": "Add or update tags in documentation"
            },
            "tag_indexing": {
                "file": "tags_index.py",
                "description": "Tag indexing and YAML generation"
            }
        }
    },
    "maintenance": {
        "description": "System maintenance and cleanup",
        "scripts": {
            "health_check": {
                "file": "health_check_and_notification.py",
                "description": "Documentation system health monitoring"
            },
            "inventory_update": {
                "file": "inventory_and_index_update.py", 
                "description": "Documentation inventory management"
            },
            "redundancy_checker": {
                "file": "redundancy_and_deprecation_checker.py",
                "description": "Duplicate and redundant content detection"
            },
            "frontmatter_fix": {
                "file": "fix_duplicated_frontmatter.py",
                "description": "Fix duplicated frontmatter in documents"
            }
        }
    },
    "analytics": {
        "description": "Documentation analytics and insights",
        "scripts": {
            "doc_analytics": {
                "file": "doc_analytics.py",
                "description": "Advanced documentation analytics and reporting"
            }
        }
    },
    "tools": {
        "description": "Utility tools and helpers",
        "scripts": {
            "inbox_categorization": {
                "file": "categorize_and_move_inbox.py",
                "description": "Categorize and organize inbox documents"
            }
        }
    }
}


class IDSInterface:
    """Unified interface for ImpressionCore Documentation System"""
    
    def __init__(self):
        self.console = Console() if HAS_RICH else SimpleConsole()
        self.version = "1.0.0"
    
    def display_header(self):
        """Display the main header"""
        if HAS_RICH:
            header = Panel(
                Text("ImpressionCore Documentation System (IDS)\nUnified Interface", 
                     style="bold blue", justify="center"),
                title="IDS v1.0.0",
                border_style="blue"
            )
            self.console.print(header)
        else:
            print("\n" + "=" * 60)
            print("  ImpressionCore Documentation System (IDS)")
            print("             Unified Interface v1.0.0")
            print("=" * 60)
    
    def display_main_menu(self):
        """Display the main menu options"""
        if HAS_RICH:
            table = Table(title="Available Functions", show_header=True, header_style="bold magenta")
            table.add_column("Category", style="cyan", width=15)
            table.add_column("Description", style="white", width=40)
            table.add_column("Scripts", style="green", width=8)
            
            for category, info in SCRIPT_CATEGORIES.items():
                script_count = len(info["scripts"])
                table.add_row(category.title(), info["description"], str(script_count))
            
            self.console.print(table)
        else:
            print("\nAvailable Functions:")
            print("-" * 40)
            for i, (category, info) in enumerate(SCRIPT_CATEGORIES.items(), 1):
                script_count = len(info["scripts"])
                print(f"{i}. {category.title()}: {info['description']} ({script_count} scripts)")
    
    def display_category_menu(self, category: str):
        """Display scripts in a specific category"""
        if category not in SCRIPT_CATEGORIES:
            self.console.print(f"[red]Error: Category '{category}' not found[/red]" if HAS_RICH 
                             else f"Error: Category '{category}' not found")
            return
        
        category_info = SCRIPT_CATEGORIES[category]
        
        if HAS_RICH:
            table = Table(title=f"{category.title()} Scripts", show_header=True, header_style="bold cyan")
            table.add_column("Option", style="yellow", width=8)
            table.add_column("Script", style="green", width=25)
            table.add_column("Description", style="white", width=40)
            
            for i, (key, script_info) in enumerate(category_info["scripts"].items(), 1):
                table.add_row(str(i), key, script_info["description"])
            
            self.console.print(table)
        else:
            print(f"\n{category.title()} Scripts:")
            print("-" * 40)
            for i, (key, script_info) in enumerate(category_info["scripts"].items(), 1):
                print(f"{i}. {key}: {script_info['description']}")
    
    def run_script(self, category: str, script_key: str, args: List[str] = None):
        """Execute a specific script"""
        if category not in SCRIPT_CATEGORIES:
            self.console.print(f"Error: Category '{category}' not found")
            return False
        
        if script_key not in SCRIPT_CATEGORIES[category]["scripts"]:
            self.console.print(f"Error: Script '{script_key}' not found in category '{category}'")
            return False
        
        script_info = SCRIPT_CATEGORIES[category]["scripts"][script_key]
        script_path = SCRIPTS_ROOT / category / script_info["file"]
        
        if not script_path.exists():
            self.console.print(f"Error: Script file not found: {script_path}")
            return False
        
        try:
            # Build command
            cmd = [sys.executable, str(script_path)]
            if args:
                cmd.extend(args)
            
            self.console.print(f"Executing: {script_info['description']}")
            self.console.print(f"Command: {' '.join(cmd)}")
            
            # Run the script
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
            
            if result.returncode == 0:
                self.console.print("✓ Script completed successfully")
                if result.stdout:
                    print("\nOutput:")
                    print(result.stdout)
            else:
                self.console.print(f"✗ Script failed with return code {result.returncode}")
                if result.stderr:
                    print("\nError:")
                    print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            self.console.print(f"Error executing script: {e}")
            return False
    
    def list_all_scripts(self):
        """List all available scripts"""
        if HAS_RICH:
            table = Table(title="All IDS Scripts", show_header=True, header_style="bold blue")
            table.add_column("Category", style="cyan", width=12)
            table.add_column("Key", style="yellow", width=20)
            table.add_column("File", style="green", width=35)
            table.add_column("Description", style="white", width=35)
            
            for category, category_info in SCRIPT_CATEGORIES.items():
                for key, script_info in category_info["scripts"].items():
                    table.add_row(
                        category,
                        key,
                        script_info["file"],
                        script_info["description"]
                    )
            
            self.console.print(table)
        else:
            print("\nAll IDS Scripts:")
            print("=" * 80)
            for category, category_info in SCRIPT_CATEGORIES.items():
                print(f"\n{category.upper()}:")
                for key, script_info in category_info["scripts"].items():
                    print(f"  {key}: {script_info['file']}")
                    print(f"    {script_info['description']}")
    
    def show_status(self):
        """Show system status"""
        if HAS_RICH:
            panel = Panel(
                f"IDS Version: {self.version}\n"
                f"Project Root: {PROJECT_ROOT}\n"
                f"Docs Root: {DOCS_ROOT}\n"
                f"Scripts Root: {SCRIPTS_ROOT}\n"
                f"Rich UI: {'Available' if HAS_RICH else 'Not Available'}\n"
                f"Total Categories: {len(SCRIPT_CATEGORIES)}\n"
                f"Total Scripts: {sum(len(cat['scripts']) for cat in SCRIPT_CATEGORIES.values())}",
                title="System Status",
                border_style="green"
            )
            self.console.print(panel)
        else:
            print("\nSystem Status:")
            print("-" * 30)
            print(f"IDS Version: {self.version}")
            print(f"Project Root: {PROJECT_ROOT}")
            print(f"Docs Root: {DOCS_ROOT}")
            print(f"Scripts Root: {SCRIPTS_ROOT}")
            print(f"Rich UI: {'Available' if HAS_RICH else 'Not Available'}")
            print(f"Total Categories: {len(SCRIPT_CATEGORIES)}")
            print(f"Total Scripts: {sum(len(cat['scripts']) for cat in SCRIPT_CATEGORIES.values())}")
    
    def interactive_mode(self):
        """Run in interactive mode"""
        while True:
            try:
                self.display_header()
                self.display_main_menu()
                
                if HAS_RICH:
                    print("\nOptions:")
                    print("• Enter category name (automation, maintenance, analytics, tools)")
                    print("• 'editor' - Open Documentation Editor")  # New option
                    print("• 'list' - Show all scripts")
                    print("• 'status' - Show system status") 
                    print("• 'exit' or 'quit' - Exit program")
                    
                    choice = Prompt.ask("\nSelect option", default="exit").lower().strip()
                else:
                    print("\nOptions:")
                    print("• Enter category name (automation, maintenance, analytics, tools)")
                    print("• 'editor' - Open Documentation Editor")  # New option
                    print("• 'list' - Show all scripts")
                    print("• 'status' - Show system status")
                    print("• 'exit' or 'quit' - Exit program")
                    
                    choice = input("\nSelect option [exit]: ").lower().strip()
                    if not choice:
                        choice = "exit"
                
                # Handle exit conditions
                if choice in ['exit', 'quit', 'q']:
                    self.console.print("Goodbye!" if HAS_RICH else "Goodbye!")
                    break
                  # New: Launch Documentation Editor
                elif choice == 'editor':
                    self.console.print("Launching Enhanced Documentation Editor..." if HAS_RICH else "Launching Enhanced Documentation Editor...")
                    editor_path = PROJECT_ROOT / 'src' / 'dev_tools' / 'doc_viewer' / 'markdown_viewer_enhanced.py'
                    if not editor_path.exists():
                        self.console.print(f"[red]Editor not found at {editor_path}[/red]" if HAS_RICH else f"Editor not found at {editor_path}")
                        input("Press Enter to continue...")
                        continue
                    try:
                        import os
                        env = os.environ.copy()
                        src_path = str(PROJECT_ROOT / 'src')
                        # Prepend src_path to PYTHONPATH for import resolution
                        env['PYTHONPATH'] = src_path + os.pathsep + env.get('PYTHONPATH', '')
                        subprocess.Popen([sys.executable, str(editor_path)], cwd=PROJECT_ROOT, env=env)
                        self.console.print("Editor launched in a new window." if HAS_RICH else "Editor launched in a new window.")
                    except Exception as e:
                        self.console.print(f"[red]Failed to launch editor: {e}[/red]" if HAS_RICH else f"Failed to launch editor: {e}")
                    input("Press Enter to continue...")
                
                # Handle special commands
                elif choice == 'list':
                    self.list_all_scripts()
                    input("\nPress Enter to continue...")
                
                elif choice == 'status':
                    self.show_status()
                    input("\nPress Enter to continue...")
                
                # Handle category selection
                elif choice in SCRIPT_CATEGORIES:
                    self.category_interactive_mode(choice)
                
                else:
                    self.console.print(f"Invalid option: {choice}")
                    input("Press Enter to continue...")
                    
            except KeyboardInterrupt:
                self.console.print("\n\nExiting IDS...")
                break
            except Exception as e:
                self.console.print(f"Error: {e}")
                input("Press Enter to continue...")
    
    def category_interactive_mode(self, category: str):
        """Interactive mode for a specific category"""
        while True:
            try:
                print("\n" + "=" * 60)
                self.display_category_menu(category)
                
                print(f"\nOptions for {category.title()}:")
                print("• Enter script number to run")
                print("• 'back' - Return to main menu")
                print("• 'exit' - Exit program")
                
                if HAS_RICH:
                    choice = Prompt.ask("Select option", default="back").lower().strip()
                else:
                    choice = input("Select option [back]: ").lower().strip()
                    if not choice:
                        choice = "back"
                
                if choice in ['back', 'b']:
                    break
                elif choice in ['exit', 'quit', 'q']:
                    return "exit"
                elif choice.isdigit():
                    script_num = int(choice)
                    scripts = list(SCRIPT_CATEGORIES[category]["scripts"].keys())
                    if 1 <= script_num <= len(scripts):
                        script_key = scripts[script_num - 1]
                        self.run_script(category, script_key)
                        input("\nPress Enter to continue...")
                    else:
                        self.console.print("Invalid script number")
                        input("Press Enter to continue...")
                else:
                    self.console.print(f"Invalid option: {choice}")
                    input("Press Enter to continue...")
                    
            except KeyboardInterrupt:
                return "exit"
            except Exception as e:
                self.console.print(f"Error: {e}")
                input("Press Enter to continue...")
        
        return "continue"


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ImpressionCore Documentation System (IDS)")
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--list", action="store_true", help="List all available scripts")
    parser.add_argument("--run", nargs=2, metavar=("CATEGORY", "SCRIPT"), 
                       help="Run specific script: --run category script_key")
    parser.add_argument("--interactive", action="store_true", default=True,
                       help="Run in interactive mode (default)")
    
    args = parser.parse_args()
    
    ids = IDSInterface()
    
    # Handle command line arguments
    if args.version:
        print(f"IDS Version: {ids.version}")
        return
    
    if args.status:
        ids.show_status()
        return
    
    if args.list:
        ids.list_all_scripts()
        return
    
    if args.run:
        category, script_key = args.run
        success = ids.run_script(category, script_key)
        sys.exit(0 if success else 1)
    
    # Default to interactive mode
    if len(sys.argv) == 1 or args.interactive:
        ids.interactive_mode()


if __name__ == "__main__":
    main()
