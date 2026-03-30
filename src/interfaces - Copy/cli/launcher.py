#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #inference #memory_management #multimodal #performance #python #source_code #src/interfaces/cli/launcher.py #testing #training
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #command_line #inference #memory_management #multimodal #performance #python #source_code #src\\interfaces\\cli\\launcher.py #testing #training
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore CLI Launcher
==========================

Central launcher for ImpressionCore CLI tools and production model utilities.
Provides easy access to model testing, inference, and evaluation tools.

Features:
- Production model CLI
- Comprehensive test suite
- Model validation tools
- Performance monitoring
- Interactive model chat

Author: GitHub Copilot & ImpressionCore Team
Date: 2025-06-12
Version: 1.0.0 - Production Ready
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

# Rich CLI imports (with fallbacks)
try:
    from rich.columns import Columns  # noqa: F401
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt  # noqa: F401
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    class Console:
        def print(self, *args, **kwargs): print(*args)

console = Console()

class ImpressionCoreCLILauncher:
    """Central launcher for ImpressionCore CLI tools."""

    def __init__(self):
        """Initialize the launcher."""
        self.console = console
        self.tools = {
            'production_cli': {
                'name': 'Production Model CLI',
                'description': 'Interactive CLI for production model inference and testing',
                'script': 'src/interfaces/cli/production_model_cli.py',
                'examples': [
                    '--interactive  # Start interactive mode',
                    '--test 10      # Run 10 performance tests',
                    '--batch input.txt output.json  # Batch processing'
                ]
            },
            'multimodal_cli': {
                'name': 'Multimodal AI CLI',
                'description': 'Advanced multimodal interface (text, image, audio)',
                'script': 'src/interfaces/cli/multimodal_cli.py',
                'examples': [
                    '--interactive  # Start multimodal chat',
                    '--image photo.jpg  # Analyze an image',
                    '--audio speech.wav  # Process audio',
                    '--multimodal  # Combined input session'
                ]
            },
            'test_suite': {
                'name': 'Production Test Suite',
                'description': 'Comprehensive testing and validation suite',
                'script': 'src/interfaces/cli/production_test_suite.py',
                'examples': [
                    '--full         # Run complete test suite',
                    '--performance  # Performance benchmarks only',
                    '--memory       # Memory usage tests only',
                    '--stress       # Stress testing only'
                ]
            },
            'validation': {
                'name': 'Model Validation',
                'description': 'Basic model validation and integrity checks',
                'script': 'src/training/validate_production_model_simple.py',
                'examples': [
                    '--model_path <path>  # Validate specific model',
                    '# Quick model integrity and performance check'
                ]
            }
        }

    def display_banner(self):
        """Display ImpressionCore CLI launcher banner."""
        if RICH_AVAILABLE:
            banner = Panel(
                "[bold cyan]🧠 ImpressionCore CLI Launcher v1.0.0[/bold cyan]\n"
                "[blue]Production Model Tools & Utilities[/blue]\n\n"
                "[green]✓ Production Model Ready[/green]\n"
                "[green]✓ 749,071 Embeddings Trained[/green]\n"
                "[green]✓ 19.2% Loss Reduction Achieved[/green]\n"
                "[green]✓ GTX 1050 Ti Optimized[/green]",
                title="🚀 ImpressionCore CLI Hub",
                border_style="cyan"
            )
            self.console.print(banner)
        else:
            print("=" * 60)
            print("🧠 ImpressionCore CLI Launcher")
            print("Production Model Tools & Utilities")
            print("=" * 60)

    def display_tools_menu(self):
        """Display available tools menu."""
        if RICH_AVAILABLE:
            table = Table(title="🛠️  Available CLI Tools")
            table.add_column("Tool", style="cyan", width=20)
            table.add_column("Description", style="white", width=40)
            table.add_column("Key Features", style="dim", width=30)

            features = {
                'production_cli': 'Interactive chat, Testing, Batch processing',
                'multimodal_cli': 'Text + Image + Audio, Cross-modal reasoning',
                'test_suite': 'Memory analysis, Performance benchmarks, Stress testing',
                'validation': 'Quick validation, Integrity checks, Basic testing'
            }

            for tool_id, tool_info in self.tools.items():
                table.add_row(
                    tool_info['name'],
                    tool_info['description'],
                    features[tool_id]
                )

            self.console.print(table)
        else:
            print("\nAvailable Tools:")
            for _tool_id, tool_info in self.tools.items():
                print(f"  {tool_info['name']}: {tool_info['description']}")

    def display_quick_start(self):
        """Display quick start commands."""
        if RICH_AVAILABLE:
            quick_start = Panel(
                "[bold yellow]Quick Start Commands:[/bold yellow]\n\n"
                "[cyan]# Start interactive model chat[/cyan]\n"
                "python launcher.py production_cli --interactive\n\n"
                "[cyan]# Run performance tests[/cyan]\n"
                "python launcher.py production_cli --test 20\n\n"
                "[cyan]# Run comprehensive test suite[/cyan]\n"
                "python launcher.py test_suite --full\n\n"
                "[cyan]# Quick model validation[/cyan]\n"
                "python launcher.py validation\n\n"
                "[cyan]# Get help for specific tool[/cyan]\n"
                "python launcher.py <tool> --help",
                title="⚡ Quick Start",
                border_style="yellow"
            )
            self.console.print(quick_start)
        else:
            print("\nQuick Start:")
            print("  python launcher.py production_cli --interactive")
            print("  python launcher.py test_suite --full")
            print("  python launcher.py validation")

    def launch_tool(self, tool_name: str, tool_args: list):
        """Launch a specific tool with arguments."""
        if tool_name not in self.tools:
            self.console.print(f"[red]Error: Unknown tool '{tool_name}'[/red]")
            self.console.print("[yellow]Available tools: " + ", ".join(self.tools.keys()) + "[/yellow]")
            return 1

        tool_info = self.tools[tool_name]
        script_path = tool_info['script']

        # Check if script exists
        if not Path(script_path).exists():
            self.console.print(f"[red]Error: Script not found: {script_path}[/red]")
            return 1
          # Build command
        import subprocess
        cmd = [sys.executable, script_path, *tool_args]

        try:
            # Display launch info
            if RICH_AVAILABLE:
                self.console.print(Panel(
                    f"[bold blue]Launching:[/bold blue] {tool_info['name']}\n"
                    f"[blue]Script:[/blue] {script_path}\n"
                    f"[blue]Args:[/blue] {' '.join(tool_args) if tool_args else 'None'}",
                    title="🚀 Tool Launch",
                    border_style="blue"
                ))
            else:
                print(f"Launching: {tool_info['name']}")
                print(f"Command: {' '.join(cmd)}")

            # Execute command
            result = subprocess.run(cmd, cwd=Path.cwd())
            return result.returncode
        except Exception as e:
            self.console.print(f"[red]Error launching tool: {e!s}[/red]")
            return 1

    def interactive_mode(self):
        """Run interactive tool selection mode."""
        self.console.print("\n[bold green]Interactive Mode[/bold green]")

        while True:
            try:
                self.console.print("\n[cyan]Available commands:[/cyan]")
                self.console.print("  1. production_cli - Production Model CLI")
                self.console.print("  2. multimodal_cli - Multimodal AI CLI (Text + Image + Audio)")
                self.console.print("  3. test_suite - Comprehensive Test Suite")
                self.console.print("  4. validation - Quick Model Validation")
                self.console.print("  5. help - Show detailed help")
                self.console.print("  6. quit - Exit launcher")

                if RICH_AVAILABLE:
                    choice = Prompt.ask("\n[yellow]Select tool[/yellow]",
                                      choices=["1", "2", "3", "4", "5", "6", "quit"])
                else:
                    choice = input("\nSelect tool (1-6, quit): ").strip()

                if choice in ["6", "quit"]:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break
                elif choice == "1":
                    self.launch_tool("production_cli", ["--interactive"])
                elif choice == "2":
                    self.launch_tool("multimodal_cli", ["--interactive"])
                elif choice == "3":
                    self.launch_tool("test_suite", ["--full"])
                elif choice == "4":
                    # Add default model path for validation
                    default_model_path = "src/models/production/impressioncore_production_20250612_095354.pth"
                    self.launch_tool("validation", ["--model_path", default_model_path])
                elif choice == "5":
                    self.show_detailed_help()
                else:
                    self.console.print("[red]Invalid choice. Please try again.[/red]")

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted by user[/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e!s}[/red]")

        return 0

    def show_detailed_help(self):
        """Show detailed help for all tools."""
        for tool_id, tool_info in self.tools.items():
            if RICH_AVAILABLE:
                examples_text = "\n".join(f"  python launcher.py {tool_id} {example}"
                                        for example in tool_info['examples'])

                help_panel = Panel(
                    f"[bold blue]Description:[/bold blue] {tool_info['description']}\n"
                    f"[bold blue]Script:[/bold blue] {tool_info['script']}\n\n"
                    f"[bold blue]Examples:[/bold blue]\n{examples_text}",
                    title=f"📖 {tool_info['name']}",
                    border_style="blue"
                )
                self.console.print(help_panel)
            else:
                print(f"\n{tool_info['name']}:")
                print(f"  Description: {tool_info['description']}")
                print("  Examples:")
                for example in tool_info['examples']:
                    print(f"    python launcher.py {tool_id} {example}")


def main():
    """Main launcher entry point."""
    parser = argparse.ArgumentParser(
        description="ImpressionCore CLI Launcher - Central hub for production model tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Tools:
  production_cli  : Interactive CLI for model inference and testing
  test_suite      : Comprehensive testing and validation suite
  validation      : Quick model validation and integrity checks

Examples:
  python launcher.py                                    # Interactive mode
  python launcher.py production_cli --interactive       # Start model chat
  python launcher.py production_cli --test 20           # Run 20 tests
  python launcher.py test_suite --full                  # Complete test suite
  python launcher.py test_suite --performance           # Performance only
  python launcher.py validation                         # Quick validation
  python launcher.py <tool> --help                      # Tool-specific help

Quick Start:
  python launcher.py production_cli --interactive       # Best for beginners
  python launcher.py test_suite --full                  # Comprehensive testing
        """
    )

    parser.add_argument('tool', nargs='?', help='Tool to launch (production_cli, test_suite, validation)')
    parser.add_argument('args', nargs='*', help='Arguments to pass to the tool')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--no-banner', action='store_true', help='Skip banner display')

    args = parser.parse_args()

    # Initialize launcher
    launcher = ImpressionCoreCLILauncher()

    # Display banner
    if not args.no_banner:
        launcher.display_banner()
        launcher.display_tools_menu()

    # Handle different modes
    if args.interactive or not args.tool:
        # Interactive mode or no tool specified
        if not args.no_banner:
            launcher.display_quick_start()
        return launcher.interactive_mode()
    elif args.tool:
        # Launch specific tool
        return launcher.launch_tool(args.tool, args.args)
    else:
        # Show help
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
