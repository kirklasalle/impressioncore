#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #performance #python #source_code #src/scripts\b3\b3_simple_monitor.py #testing #training
**Category:** Source Code
**Status:** Active
"""



import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class SimpleDistillationMonitor:
    """Lightweight monitoring for remote distillation"""

    def __init__(self):
        self.console = Console()
        self.log_dir = Path(".")
        self.last_modified_times = {}

    def find_active_files(self) -> dict[str, Path]:
        """Find active distillation files"""
        files = {}

        # Look for recent log files
        log_patterns = [
            "b3_remote_distillation_*.log",
            "remote_distillation_*.json",
            "progressive_distillation_*.log"
        ]

        for pattern in log_patterns:
            found_files = list(self.log_dir.glob(pattern))
            if found_files:
                # Get the most recent file
                latest = max(found_files, key=lambda f: f.stat().st_mtime)
                file_type = "log" if ".log" in pattern else "metrics"
                files[file_type] = latest

        return files

    def read_recent_logs(self, log_file: Path, lines: int = 10) -> list:
        """Read recent lines from log file"""
        try:
            with open(log_file, encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if all_lines else []
        except Exception:
            return []

    def parse_metrics_file(self, metrics_file: Path) -> dict[str, Any] | None:
        """Parse the latest metrics file"""
        try:
            with open(metrics_file, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def extract_stage_info(self, logs: list) -> dict[str, Any]:
        """Extract stage information from logs"""
        stage_info = {
            "current_stage": "Unknown",
            "stage_progress": "0%",
            "api_calls": 0,
            "errors": 0,
            "last_activity": "No activity"
        }

        for line in logs:
            line = line.strip()

            if "Stage" in line and "Training" in line:
                # Extract stage info
                if "Stage 1" in line:
                    stage_info["current_stage"] = "Foundation Knowledge"
                elif "Stage 2" in line:
                    stage_info["current_stage"] = "Intermediate Integration"
                elif "Stage 3" in line:
                    stage_info["current_stage"] = "Advanced Synthesis"
                elif "Stage 4" in line:
                    stage_info["current_stage"] = "Expert Application"

                stage_info["last_activity"] = line.split(" - ")[-1] if " - " in line else line

            elif "API" in line:
                stage_info["api_calls"] += 1

            elif "Error" in line or "Failed" in line:
                stage_info["errors"] += 1
                stage_info["last_activity"] = "Error detected"

            elif "%" in line and "progress" in line.lower():
                # Try to extract progress percentage
                import re
                progress_match = re.search(r'(\d+)%', line)
                if progress_match:
                    stage_info["stage_progress"] = progress_match.group(0)

        return stage_info

    def create_status_table(self, stage_info: dict[str, Any], metrics: dict[str, Any] | None) -> Table:
        """Create status table"""
        table = Table(title="🔍 B3 Remote Distillation Status", box=box.ROUNDED)
        table.add_column("Item", style="cyan", width=20)
        table.add_column("Status", style="green", width=30)
        table.add_column("Details", style="yellow", width=40)

        # Current time
        current_time = datetime.now().strftime("%H:%M:%S")
        table.add_row("Current Time", current_time, "Live monitoring")

        # Stage information
        table.add_row("Current Stage", stage_info["current_stage"], stage_info["stage_progress"])
        table.add_row("API Calls", str(stage_info["api_calls"]), "Total in recent logs")
        table.add_row("Errors", str(stage_info["errors"]), "Recent error count")
        table.add_row("Last Activity", stage_info["last_activity"][:40], "Most recent log entry")

        # Metrics information if available
        if metrics:
            stages_completed = len(metrics.get("stages_completed", []))
            total_stages = 4  # We know there are 4 stages
            overall_progress = f"{stages_completed}/{total_stages} stages"

            table.add_row("Overall Progress", overall_progress, f"{(stages_completed/total_stages)*100:.0f}% complete")

            # Get latest benchmark if available
            stages = metrics.get("stages_completed", [])
            if stages:
                latest_stage = stages[-1]
                benchmark = latest_stage.get("benchmark_results", {})
                if benchmark:
                    avg_score = sum(benchmark.values()) / len(benchmark) if benchmark else 0
                    table.add_row("Latest Performance", f"{avg_score:.3f}", "Average benchmark score")

        return table

    def create_recent_logs_panel(self, logs: list) -> Panel:
        """Create recent logs panel"""
        if not logs:
            log_content = "No recent log entries"
        else:
            # Show last 5 lines, formatted
            recent_logs = []
            for line in logs[-5:]:
                line = line.strip()
                if line:
                    # Truncate long lines
                    if len(line) > 80:
                        line = line[:77] + "..."
                    recent_logs.append(line)

            log_content = "\n".join(recent_logs) if recent_logs else "No recent entries"

        return Panel(
            log_content,
            title="📝 Recent Log Entries",
            border_style="blue",
            box=box.ROUNDED
        )

    def monitor_once(self) -> bool:
        """Run one monitoring cycle"""
        files = self.find_active_files()

        if not files:
            self.console.print("❌ No active distillation files found")
            return False

        # Read logs
        logs = []
        if "log" in files:
            logs = self.read_recent_logs(files["log"])

        # Read metrics
        metrics = None
        if "metrics" in files:
            metrics = self.parse_metrics_file(files["metrics"])

        # Extract information
        stage_info = self.extract_stage_info(logs)

        # Create display
        status_table = self.create_status_table(stage_info, metrics)
        logs_panel = self.create_recent_logs_panel(logs)

        # Display
        self.console.clear()
        self.console.print(Panel.fit(
            "🔍 B3 Remote Distillation Monitor (Simple)\n"
            f"Monitoring files: {', '.join(f.name for f in files.values())}",
            style="bold cyan"
        ))
        self.console.print(status_table)
        self.console.print(logs_panel)
        self.console.print(f"\n⏰ Last updated: {datetime.now().strftime('%H:%M:%S')} | Press Ctrl+C to stop")

        return True

    def start_monitoring(self, refresh_interval: int = 5):
        """Start simple monitoring loop"""
        self.console.print("🚀 Starting Simple Remote Distillation Monitor...")
        self.console.print(f"📊 Refreshing every {refresh_interval} seconds")
        self.console.print("⏹️  Press Ctrl+C to stop\n")

        try:
            while True:
                success = self.monitor_once()
                if not success:
                    time.sleep(2)  # Wait longer if no files found
                else:
                    time.sleep(refresh_interval)

        except KeyboardInterrupt:
            self.console.print("\n🛑 Monitoring stopped")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Simple Remote Distillation Monitor")
    parser.add_argument("--interval", "-i", type=int, default=5,
                       help="Refresh interval in seconds (default: 5)")

    args = parser.parse_args()

    monitor = SimpleDistillationMonitor()
    monitor.start_monitoring(args.interval)


if __name__ == "__main__":
    main()
