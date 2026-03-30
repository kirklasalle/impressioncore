#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #performance #python #source_code #src/scripts\b3\b3_remote_distillation_monitor.py #testing #training
**Category:** Source Code
**Status:** Active
"""



import asyncio
import json
from collections import deque
from dataclasses import dataclass

# Data Analysis
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from rich import box
from rich.align import Align

# Rich UI Components
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


@dataclass
class TrainingMetrics:
    """Training metrics data structure"""
    timestamp: str
    stage_id: int
    stage_name: str
    loss: float
    teacher_alignment: float
    performance_score: float
    knowledge_retention: float
    training_time: float
    prompts_processed: int
    api_calls_made: int
    success_rate: float
    error_count: int


@dataclass
class PromptAnalytics:
    """Prompt analytics data structure"""
    total_prompts: int
    successful_responses: int
    failed_responses: int
    average_response_time: float
    complexity_distribution: dict[str, int]
    teacher_specializations: dict[str, int]
    stage_breakdown: dict[str, int]


class RemoteDistillationMonitor:
    """Real-time monitoring system for remote distillation training"""

    def __init__(self):
        self.console = Console()
        self.monitoring = False
        self.metrics_history = deque(maxlen=1000)
        self.prompt_analytics = PromptAnalytics(0, 0, 0, 0.0, {}, {}, {})
        self.current_stage = None
        self.start_time = None
        self.last_update = None

        # File paths for monitoring
        self.log_directory = Path(".")
        self.metrics_files = []
        self.log_files = []

        # Performance tracking
        self.stage_progress = {}
        self.api_performance = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "average_response_time": 0.0,
            "rate_limits_hit": 0
        }

        self.setup_monitoring()

    def setup_monitoring(self):
        """Initialize monitoring system"""
        self.console.print(Panel.fit(
            "🔍 B3 Remote Distillation Monitor\n"
            "Real-time Training & Metrics Dashboard",
            style="bold cyan"
        ))

        # Scan for existing log files
        self.scan_log_files()

    def scan_log_files(self):
        """Scan for distillation log files to monitor"""
        patterns = [
            "b3_remote_distillation_*.log",
            "remote_distillation_*.json",
            "progressive_distillation_*.log"
        ]

        for pattern in patterns:
            files = list(self.log_directory.glob(pattern))
            if "log" in pattern:
                self.log_files.extend(files)
            elif "json" in pattern:
                self.metrics_files.extend(files)

        self.console.print(f"📁 Found {len(self.log_files)} log files and {len(self.metrics_files)} metrics files")

    def parse_log_entry(self, line: str) -> dict[str, Any] | None:
        """Parse a log entry for relevant information"""
        try:
            if "Stage" in line and "Training" in line:
                # Extract stage information
                parts = line.split(" - ")
                if len(parts) >= 3:
                    timestamp = parts[0]
                    message = parts[-1]

                    if "Stage" in message:
                        stage_info = message.split("Stage")[1].strip()
                        return {
                            "type": "stage_progress",
                            "timestamp": timestamp,
                            "message": message,
                            "stage_info": stage_info
                        }

            elif "API" in line and ("Error" in line or "Success" in line):
                # Extract API performance info
                parts = line.split(" - ")
                if len(parts) >= 3:
                    return {
                        "type": "api_call",
                        "timestamp": parts[0],
                        "message": parts[-1],
                        "success": "Success" in line
                    }

            elif "Benchmark" in line or "Performance" in line:
                # Extract performance metrics
                parts = line.split(" - ")
                if len(parts) >= 3:
                    return {
                        "type": "performance",
                        "timestamp": parts[0],
                        "message": parts[-1]
                    }

            return None

        except Exception:
            return None

    def update_metrics_from_logs(self):
        """Update metrics by reading from log files"""
        for log_file in self.log_files:
            try:
                with open(log_file, encoding='utf-8') as f:
                    lines = f.readlines()

                # Process only new lines since last update
                for line in lines[-50:]:  # Check last 50 lines for efficiency
                    entry = self.parse_log_entry(line.strip())
                    if entry:
                        self.process_log_entry(entry)

            except Exception:
                continue

    def process_log_entry(self, entry: dict[str, Any]):
        """Process a parsed log entry"""
        entry_type = entry.get("type")

        if entry_type == "stage_progress":
            self.update_stage_progress(entry)
        elif entry_type == "api_call":
            self.update_api_performance(entry)
        elif entry_type == "performance":
            self.update_performance_metrics(entry)

    def update_stage_progress(self, entry: dict[str, Any]):
        """Update stage progress information"""
        stage_info = entry.get("stage_info", "")
        timestamp = entry.get("timestamp", "")

        # Extract stage number if present
        try:
            import re
            stage_match = re.search(r'(\d+)', stage_info)
            if stage_match:
                stage_num = int(stage_match.group(1))
                self.current_stage = stage_num

                if stage_num not in self.stage_progress:
                    self.stage_progress[stage_num] = {
                        "start_time": timestamp,
                        "status": "in_progress",
                        "prompts_processed": 0,
                        "completion_percentage": 0.0
                    }
        except Exception:
            pass

    def update_api_performance(self, entry: dict[str, Any]):
        """Update API performance metrics"""
        success = entry.get("success", False)

        self.api_performance["total_calls"] += 1

        if success:
            self.api_performance["successful_calls"] += 1
        else:
            self.api_performance["failed_calls"] += 1

        # Update success rate
        total = self.api_performance["total_calls"]
        successful = self.api_performance["successful_calls"]
        self.api_performance["success_rate"] = (successful / total) * 100 if total > 0 else 0

    def update_performance_metrics(self, entry: dict[str, Any]):
        """Update performance metrics"""
        message = entry.get("message", "")
        timestamp = entry.get("timestamp", "")

        # Try to extract numeric values from performance messages
        try:
            import re
            numbers = re.findall(r'(\d+\.?\d*)', message)
            if numbers and len(numbers) >= 2:
                # Assume first number is a score, second is improvement
                score = float(numbers[0])
                improvement = float(numbers[1]) if len(numbers) > 1 else 0.0

                # Store in metrics history
                self.metrics_history.append({
                    "timestamp": timestamp,
                    "score": score,
                    "improvement": improvement,
                    "message": message
                })
        except Exception:
            pass

    def load_latest_metrics_file(self) -> dict[str, Any] | None:
        """Load the most recent metrics file"""
        if not self.metrics_files:
            return None

        # Sort by modification time and get the latest
        latest_file = max(self.metrics_files, key=lambda f: f.stat().st_mtime)

        try:
            with open(latest_file, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def create_dashboard_layout(self) -> Layout:
        """Create the monitoring dashboard layout"""
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )

        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        layout["left"].split_column(
            Layout(name="stage_progress"),
            Layout(name="api_performance")
        )

        layout["right"].split_column(
            Layout(name="metrics_table"),
            Layout(name="prompt_analytics")
        )

        return layout

    def update_header(self, layout: Layout):
        """Update dashboard header"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime = ""

        if self.start_time:
            elapsed = datetime.now() - self.start_time
            uptime = f"Uptime: {str(elapsed).split('.')[0]}"

        header_text = f"🔍 B3 Remote Distillation Monitor | {current_time} | {uptime}"

        layout["header"].update(
            Panel(
                Align.center(header_text),
                style="bold cyan",
                box=box.DOUBLE
            )
        )

    def update_stage_progress(self, layout: Layout):  # noqa: F811
        """Update stage progress panel"""
        table = Table(title="📊 Stage Progress", box=box.ROUNDED)
        table.add_column("Stage", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Progress", style="yellow")
        table.add_column("Prompts", style="blue")

        if self.stage_progress:
            for stage_id, progress in self.stage_progress.items():
                status = progress.get("status", "unknown")
                completion = progress.get("completion_percentage", 0.0)
                prompts = progress.get("prompts_processed", 0)

                status_emoji = "🟢" if status == "completed" else "🟡" if status == "in_progress" else "⚪"

                table.add_row(
                    f"Stage {stage_id}",
                    f"{status_emoji} {status}",
                    f"{completion:.1f}%",
                    str(prompts)
                )
        else:
            table.add_row("No stages", "Waiting", "0%", "0")

        layout["stage_progress"].update(Panel(table, border_style="green"))

    def update_api_performance(self, layout: Layout):  # noqa: F811
        """Update API performance panel"""
        table = Table(title="🌐 API Performance", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")

        perf = self.api_performance
        success_rate = perf.get("success_rate", 0)

        # Determine status based on success rate
        if success_rate >= 95:
            status_emoji = "🟢 Excellent"
        elif success_rate >= 80:
            status_emoji = "🟡 Good"
        else:
            status_emoji = "🔴 Poor"

        table.add_row("Total Calls", str(perf["total_calls"]), "📊")
        table.add_row("Successful", str(perf["successful_calls"]), "✅")
        table.add_row("Failed", str(perf["failed_calls"]), "❌")
        table.add_row("Success Rate", f"{success_rate:.1f}%", status_emoji)
        table.add_row("Avg Response", f"{perf['average_response_time']:.2f}s", "⏱️")

        layout["api_performance"].update(Panel(table, border_style="blue"))

    def update_metrics_table(self, layout: Layout):
        """Update metrics table"""
        table = Table(title="📈 Recent Metrics", box=box.ROUNDED)
        table.add_column("Time", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Improvement", style="yellow")
        table.add_column("Details", style="blue")

        # Show last 5 metrics
        recent_metrics = list(self.metrics_history)[-5:] if self.metrics_history else []

        for metric in recent_metrics:
            timestamp = metric.get("timestamp", "").split()[-1]  # Just time part
            score = metric.get("score", 0)
            improvement = metric.get("improvement", 0)
            message = metric.get("message", "")[:30] + "..." if len(metric.get("message", "")) > 30 else metric.get("message", "")

            table.add_row(
                timestamp,
                f"{score:.3f}",
                f"+{improvement:.1f}%",
                message
            )

        if not recent_metrics:
            table.add_row("--:--:--", "0.000", "+0.0%", "No metrics yet")

        layout["metrics_table"].update(Panel(table, border_style="magenta"))

    def update_prompt_analytics(self, layout: Layout):
        """Update prompt analytics panel"""
        table = Table(title="💬 Prompt Analytics", box=box.ROUNDED)
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Percentage", style="yellow")

        # Calculate totals
        total_prompts = self.prompt_analytics.total_prompts
        successful = self.prompt_analytics.successful_responses
        failed = self.prompt_analytics.failed_responses

        if total_prompts > 0:
            success_pct = (successful / total_prompts) * 100
            failure_pct = (failed / total_prompts) * 100
        else:
            success_pct = failure_pct = 0

        table.add_row("Total Prompts", str(total_prompts), "100%")
        table.add_row("Successful", str(successful), f"{success_pct:.1f}%")
        table.add_row("Failed", str(failed), f"{failure_pct:.1f}%")
        table.add_row("Avg Response Time", f"{self.prompt_analytics.average_response_time:.2f}s", "⏱️")

        layout["prompt_analytics"].update(Panel(table, border_style="yellow"))

    def update_footer(self, layout: Layout):
        """Update dashboard footer"""
        status_text = "🟢 Monitoring Active" if self.monitoring else "🔴 Monitoring Stopped"

        if self.last_update:
            last_update_text = f"Last Update: {self.last_update.strftime('%H:%M:%S')}"
        else:
            last_update_text = "Last Update: Never"

        footer_text = f"{status_text} | {last_update_text} | Press Ctrl+C to stop"

        layout["footer"].update(
            Panel(
                Align.center(footer_text),
                style="bold white",
                box=box.ROUNDED
            )
        )

    def update_dashboard(self, layout: Layout):
        """Update all dashboard components"""
        self.update_header(layout)
        self.update_stage_progress(layout)
        self.update_api_performance(layout)
        self.update_metrics_table(layout)
        self.update_prompt_analytics(layout)
        self.update_footer(layout)

    async def monitor_loop(self):
        """Main monitoring loop"""
        layout = self.create_dashboard_layout()

        with Live(layout, refresh_per_second=2, screen=True):
            while self.monitoring:
                try:
                    # Update metrics from logs
                    self.update_metrics_from_logs()

                    # Load latest metrics file
                    latest_metrics = self.load_latest_metrics_file()
                    if latest_metrics:
                        self.process_metrics_file(latest_metrics)

                    # Update dashboard
                    self.update_dashboard(layout)
                    self.last_update = datetime.now()

                    # Wait before next update
                    await asyncio.sleep(2)

                except KeyboardInterrupt:
                    break
                except Exception:
                    # Log error but continue monitoring
                    continue

    def process_metrics_file(self, metrics: dict[str, Any]):
        """Process loaded metrics file"""
        try:
            # Update stage progress from metrics
            stages_completed = metrics.get("stages_completed", [])

            for stage in stages_completed:
                stage_id = stage.get("stage_id", 0)
                stage_name = stage.get("stage", "Unknown")

                if stage_id not in self.stage_progress:
                    self.stage_progress[stage_id] = {}

                self.stage_progress[stage_id].update({
                    "status": "completed",
                    "name": stage_name,
                    "completion_percentage": 100.0
                })

            # Update prompt analytics
            for stage in stages_completed:
                teacher_responses = stage.get("teacher_responses", {})
                responses = teacher_responses.get("responses", {})

                for _teacher, teacher_data in responses.items():
                    prompts = teacher_data.get("prompts", [])
                    self.prompt_analytics.total_prompts += len(prompts)

                    for prompt_data in prompts:
                        if prompt_data.get("success", False):
                            self.prompt_analytics.successful_responses += 1
                        else:
                            self.prompt_analytics.failed_responses += 1

        except Exception:
            pass

    def start_monitoring(self):
        """Start the monitoring system"""
        self.monitoring = True
        self.start_time = datetime.now()

        self.console.print("🚀 Starting Remote Distillation Monitor...")
        self.console.print("📊 Dashboard will update every 2 seconds")
        self.console.print("⏹️  Press Ctrl+C to stop monitoring\n")

        try:
            asyncio.run(self.monitor_loop())
        except KeyboardInterrupt:
            self.stop_monitoring()

    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring = False
        self.console.print("\n🛑 Monitoring stopped")

        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate a final monitoring report"""
        self.console.print(Panel.fit(
            "📋 Final Monitoring Report",
            style="bold green"
        ))

        report_table = Table(title="Monitoring Summary", box=box.DOUBLE)
        report_table.add_column("Metric", style="cyan")
        report_table.add_column("Value", style="green")

        # Calculate session statistics
        total_time = datetime.now() - self.start_time if self.start_time else timedelta(0)
        stages_monitored = len(self.stage_progress)
        total_api_calls = self.api_performance["total_calls"]
        success_rate = self.api_performance.get("success_rate", 0)

        report_table.add_row("Monitoring Duration", str(total_time).split('.')[0])
        report_table.add_row("Stages Monitored", str(stages_monitored))
        report_table.add_row("Total API Calls", str(total_api_calls))
        report_table.add_row("API Success Rate", f"{success_rate:.1f}%")
        report_table.add_row("Metrics Captured", str(len(self.metrics_history)))
        report_table.add_row("Log Files Scanned", str(len(self.log_files)))

        self.console.print(report_table)

        # Save report to file
        report_data = {
            "monitoring_session": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": datetime.now().isoformat(),
                "duration_seconds": total_time.total_seconds() if self.start_time else 0,
                "stages_monitored": stages_monitored,
                "api_performance": self.api_performance,
                "metrics_captured": len(self.metrics_history),
                "stage_progress": self.stage_progress
            }
        }

        report_filename = f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2)

            self.console.print(f"💾 Report saved: {report_filename}")
        except Exception as e:
            self.console.print(f"❌ Failed to save report: {e}")


def main():
    """Main function to run the monitoring system"""
    monitor = RemoteDistillationMonitor()

    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        monitor.stop_monitoring()
    except Exception as e:
        monitor.console.print(f"❌ Monitoring error: {e}")
        monitor.stop_monitoring()


if __name__ == "__main__":
    main()
