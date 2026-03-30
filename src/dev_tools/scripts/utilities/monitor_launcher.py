#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #python #source_code #src/scripts/utilities/monitor_launcher.py #testing #training
**Category:** Source Code
**Status:** Active
"""



import os
import subprocess
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


class MonitorLauncher:
    """Launcher for various monitoring tools"""

    def __init__(self):
        self.console = Console()
        self.monitors = {
            "1": {
                "name": "Simple Monitor",
                "description": "Lightweight monitoring with basic status",
                "script": "b3_simple_monitor.py",
                "features": ["Basic status", "Recent logs", "Quick overview"]
            },
            "2": {
                "name": "Full Dashboard",
                "description": "Comprehensive real-time monitoring dashboard",
                "script": "b3_remote_distillation_monitor.py",
                "features": ["Live dashboard", "API tracking", "Performance metrics", "Stage progress"]
            },
            "3": {
                "name": "Metrics Dashboard",
                "description": "Advanced metrics and API analytics",
                "script": "b3_metrics_dashboard.py",
                "features": ["API analytics", "Prompt tracking", "Performance trends", "Error analysis"]
            }
        }

    def show_welcome(self):
        """Show welcome screen"""
        self.console.print(Panel.fit(
            "🔍 B3 Remote Distillation Monitor Launcher\n"
            "Choose your monitoring tool for remote distillation training",
            style="bold cyan"
        ))

    def show_monitor_options(self):
        """Show available monitoring options"""
        table = Table(title="Available Monitoring Tools", show_header=True, header_style="bold magenta")
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Name", style="green", width=20)
        table.add_column("Description", style="white", width=40)
        table.add_column("Features", style="yellow", width=30)

        for option_id, monitor in self.monitors.items():
            features_str = ", ".join(monitor["features"])
            table.add_row(
                option_id,
                monitor["name"],
                monitor["description"],
                features_str
            )

        table.add_row("4", "Test API", "Test OpenRouter API connection", "Quick API validation")
        table.add_row("5", "Run Distillation", "Start remote distillation process", "Full distillation pipeline")
        table.add_row("q", "Quit", "Exit launcher", "")

        self.console.print(table)

    def check_script_exists(self, script_name: str) -> bool:
        """Check if monitoring script exists"""
        return os.path.exists(script_name)

    def launch_monitor(self, script_name: str):
        """Launch a monitoring script"""
        if not self.check_script_exists(script_name):
            self.console.print(f"❌ Script not found: {script_name}")
            return False

        self.console.print(f"🚀 Launching {script_name}...")
        self.console.print("⏹️  Press Ctrl+C in the monitor to stop it\n")

        try:
            # Launch the script
            subprocess.run([sys.executable, script_name], check=False)
            return True
        except Exception as e:
            self.console.print(f"❌ Failed to launch {script_name}: {e}")
            return False

    def test_api(self):
        """Test API connection"""
        if self.check_script_exists("test_api.py"):
            self.console.print("🔬 Testing API connection...")
            try:
                subprocess.run([sys.executable, "test_api.py"], check=False)
                return True
            except Exception as e:
                self.console.print(f"❌ API test failed: {e}")
                return False
        else:
            self.console.print("❌ test_api.py not found")
            return False

    def run_distillation(self):
        """Run remote distillation"""
        distillation_scripts = [
            "b3_remote_distillation_system.py",
            "remote_distillation_launcher.py"
        ]

        for script in distillation_scripts:
            if self.check_script_exists(script):
                self.console.print(f"🚀 Starting remote distillation: {script}")
                try:
                    subprocess.run([sys.executable, script], check=False)
                    return True
                except Exception as e:
                    self.console.print(f"❌ Failed to start distillation: {e}")
                    return False

        self.console.print("❌ No distillation scripts found")
        return False

    def show_recommendations(self):
        """Show recommendations for different use cases"""
        recommendations = Panel(
            "💡 Recommendations:\n\n"
            "• 🔰 **First time users**: Start with Simple Monitor (#1)\n"
            "• 📊 **Detailed tracking**: Use Full Dashboard (#2)\n"
            "• 🔬 **API analysis**: Use Metrics Dashboard (#3)\n"
            "• 🧪 **Having issues?**: Test API first (#4)\n"
            "• 🚀 **Ready to train?**: Run Distillation (#5)",
            title="Usage Guide",
            border_style="green"
        )
        self.console.print(recommendations)

    def run(self):
        """Main launcher loop"""
        self.show_welcome()

        while True:
            self.console.print()
            self.show_monitor_options()
            self.console.print()
            self.show_recommendations()
            self.console.print()

            choice = Prompt.ask(
                "Select monitoring tool",
                choices=["1", "2", "3", "4", "5", "q"],
                default="1"
            )

            if choice == "q":
                self.console.print("👋 Goodbye!")
                break
            elif choice == "4":
                self.test_api()
                input("\nPress Enter to continue...")
            elif choice == "5":
                self.run_distillation()
                input("\nPress Enter to continue...")
            elif choice in self.monitors:
                monitor = self.monitors[choice]
                script = monitor["script"]

                self.console.print(f"\n🎯 Selected: {monitor['name']}")
                self.console.print(f"📝 Description: {monitor['description']}")
                self.console.print(f"✨ Features: {', '.join(monitor['features'])}\n")

                confirm = Prompt.ask("Launch this monitor?", choices=["y", "n"], default="y")

                if confirm == "y":
                    self.launch_monitor(script)
                    input("\nPress Enter to continue...")
            else:
                self.console.print("❌ Invalid choice")


def main():
    """Main function"""
    launcher = MonitorLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
