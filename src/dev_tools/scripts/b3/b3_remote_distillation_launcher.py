#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts\b3\b3_remote_distillation_launcher.py
**Category:** Source Code
**Status:** Active
"""



import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel


def main():
    """Main launcher function"""
    console = Console()

    console.print(Panel.fit(
        "🚀 B3 Remote Distillation Launcher\n"
        "Starting remote teacher model distillation...",
        style="bold green"
    ))

    # Check if remote distillation system exists
    remote_script = Path("b3_remote_distillation_system.py")

    if not remote_script.exists():
        console.print("❌ Remote distillation system not found!")
        console.print("Expected: b3_remote_distillation_system.py")
        return

    # Import and run the remote system
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))

        # Import the remote system
        from b3_remote_config import RemoteDistillationConfig
        from b3_remote_distillation_system import B3RemoteDistillationSystem

        # Load API key from configuration
        console.print("🔑 Loading API configuration...")
        try:
            config_path = Path("../../../logs/training/remote_distillation_config.json")
            if config_path.exists():
                config = RemoteDistillationConfig.load_from_file(str(config_path))
                api_key = config.openrouter.api_key
                console.print("✅ Loaded API key from configuration file")
            else:
                console.print("❌ Configuration file not found")
                return
        except Exception as e:
            console.print(f"❌ Failed to load configuration: {e}")
            return

        # Create and run the system
        console.print("🌐 Initializing remote distillation system...")
        system = B3RemoteDistillationSystem(api_key)

        console.print("🎯 Starting progressive remote distillation...")
        results = system.run_complete_remote_pipeline()

        if results.get("status") != "failed":
            console.print("✅ Remote distillation completed successfully!")
        else:
            console.print(f"❌ Remote distillation failed: {results.get('error')}")

    except ImportError as e:
        console.print(f"❌ Failed to import remote distillation system: {e}")
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
