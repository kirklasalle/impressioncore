#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #performance #python #source_code #src/scripts\b3\b3_metrics_dashboard.py #testing #training
**Category:** Source Code
**Status:** Active
"""



import asyncio
import contextlib
import json
import statistics
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


class MetricsDashboard:
    """Advanced metrics dashboard for remote distillation"""

    def __init__(self):
        self.console = Console()
        self.metrics_history = deque(maxlen=100)
        self.api_call_history = deque(maxlen=50)
        self.prompt_analytics = {
            "total_prompts": 0,
            "successful_prompts": 0,
            "failed_prompts": 0,
            "average_response_time": 0.0,
            "prompts_by_stage": defaultdict(int),
            "prompts_by_teacher": defaultdict(int),
            "error_types": defaultdict(int),
            "response_times": deque(maxlen=20)
        }

        self.stage_metrics = {
            1: {"name": "Foundation Knowledge", "status": "pending", "start_time": None, "metrics": {}},
            2: {"name": "Intermediate Integration", "status": "pending", "start_time": None, "metrics": {}},
            3: {"name": "Advanced Synthesis", "status": "pending", "start_time": None, "metrics": {}},
            4: {"name": "Expert Application", "status": "pending", "start_time": None, "metrics": {}}
        }

        self.current_stage = None
        self.monitoring_start = datetime.now()
        self.last_file_check = {}

        # Performance tracking
        self.performance_trends = {
            "academic_reasoning": deque(maxlen=10),
            "technical_knowledge": deque(maxlen=10),
            "creative_synthesis": deque(maxlen=10),
            "practical_application": deque(maxlen=10),
            "conversation_quality": deque(maxlen=10)
        }

    def scan_for_files(self) -> dict[str, list[Path]]:
        """Scan for distillation-related files"""
        files = {
            "logs": [],
            "metrics": [],
            "configs": []
        }

        log_dir = Path(".")

        # Scan for different file types
        patterns = {
            "logs": ["*.log", "*distillation*.log"],
            "metrics": ["*distillation*.json", "*metrics*.json"],
            "configs": ["*config*.json", "*settings*.json"]
        }

        for file_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                found_files = list(log_dir.glob(pattern))
                files[file_type].extend(found_files)

        # Remove duplicates and sort by modification time
        for file_type in files:
            files[file_type] = sorted(list(set(files[file_type])),
                                    key=lambda f: f.stat().st_mtime, reverse=True)

        return files

    def parse_log_for_api_calls(self, log_file: Path) -> list[dict[str, Any]]:
        """Parse log file for API call information"""
        api_calls = []

        try:
            # Check if file was modified since last check
            mod_time = log_file.stat().st_mtime
            last_check = self.last_file_check.get(str(log_file), 0)

            if mod_time <= last_check:
                return []  # No new content

            self.last_file_check[str(log_file)] = mod_time

            with open(log_file, encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines[-20:]:  # Check last 20 lines for new entries
                line = line.strip()

                # Look for API call patterns
                if any(keyword in line.lower() for keyword in ['api', 'request', 'response', 'openrouter']):
                    call_info = self.extract_api_call_info(line)
                    if call_info:
                        api_calls.append(call_info)

                # Look for prompt patterns
                elif any(keyword in line.lower() for keyword in ['prompt', 'teacher', 'response']):
                    prompt_info = self.extract_prompt_info(line)
                    if prompt_info:
                        self.update_prompt_analytics(prompt_info)

        except Exception:
            pass

        return api_calls

    def extract_api_call_info(self, line: str) -> dict[str, Any] | None:
        """Extract API call information from log line"""
        try:
            # Look for common API patterns
            call_info = {
                "timestamp": datetime.now(),
                "success": False,
                "response_time": 0.0,
                "error_type": None,
                "details": line
            }

            # Check for success/failure indicators
            if any(success_word in line.lower() for success_word in ['success', 'completed', '200']):
                call_info["success"] = True
            elif any(error_word in line.lower() for error_word in ['error', 'failed', '401', '400', '500']):
                call_info["success"] = False

                # Extract error type
                if "401" in line:
                    call_info["error_type"] = "Authentication"
                elif "400" in line:
                    call_info["error_type"] = "Bad Request"
                elif "500" in line:
                    call_info["error_type"] = "Server Error"
                else:
                    call_info["error_type"] = "Unknown"

            # Try to extract response time
            import re
            time_match = re.search(r'(\d+\.?\d*)\s*(?:s|sec|seconds)', line)
            if time_match:
                call_info["response_time"] = float(time_match.group(1))

            # Extract timestamp if present
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            if timestamp_match:
                with contextlib.suppress(Exception):
                    call_info["timestamp"] = datetime.strptime(timestamp_match.group(1), "%Y-%m-%d %H:%M:%S")

            return call_info

        except Exception:
            return None

    def extract_prompt_info(self, line: str) -> dict[str, Any] | None:
        """Extract prompt information from log line"""
        try:
            prompt_info = {
                "timestamp": datetime.now(),
                "stage": self.current_stage or 1,
                "teacher": "unknown",
                "success": False,
                "response_time": 0.0
            }

            # Extract stage information
            import re
            stage_match = re.search(r'stage\s*(\d+)', line.lower())
            if stage_match:
                prompt_info["stage"] = int(stage_match.group(1))

            # Extract teacher type
            if "reasoning" in line.lower():
                prompt_info["teacher"] = "reasoning_expert"
            elif "knowledge" in line.lower():
                prompt_info["teacher"] = "knowledge_specialist"
            elif "synthesis" in line.lower():
                prompt_info["teacher"] = "synthesis_master"
            elif "application" in line.lower():
                prompt_info["teacher"] = "application_expert"

            # Check success
            if any(word in line.lower() for word in ['success', 'completed', 'response']):
                prompt_info["success"] = True

            # Extract response time
            time_match = re.search(r'(\d+\.?\d*)\s*(?:s|sec|seconds)', line)
            if time_match:
                prompt_info["response_time"] = float(time_match.group(1))

            return prompt_info

        except Exception:
            return None

    def update_prompt_analytics(self, prompt_info: dict[str, Any]):
        """Update prompt analytics with new information"""
        self.prompt_analytics["total_prompts"] += 1

        if prompt_info["success"]:
            self.prompt_analytics["successful_prompts"] += 1
        else:
            self.prompt_analytics["failed_prompts"] += 1

        # Update stage and teacher counts
        stage = prompt_info["stage"]
        teacher = prompt_info["teacher"]

        self.prompt_analytics["prompts_by_stage"][f"Stage {stage}"] += 1
        self.prompt_analytics["prompts_by_teacher"][teacher] += 1

        # Update response times
        response_time = prompt_info["response_time"]
        if response_time > 0:
            self.prompt_analytics["response_times"].append(response_time)

            # Calculate average
            times = list(self.prompt_analytics["response_times"])
            self.prompt_analytics["average_response_time"] = statistics.mean(times) if times else 0.0

    def load_latest_metrics(self) -> dict[str, Any] | None:
        """Load the latest metrics file"""
        files = self.scan_for_files()

        if not files["metrics"]:
            return None

        latest_metrics_file = files["metrics"][0]  # Already sorted by modification time

        try:
            with open(latest_metrics_file, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def update_stage_metrics(self, metrics_data: dict[str, Any]):
        """Update stage metrics from loaded data"""
        if not metrics_data:
            return

        stages_completed = metrics_data.get("stages_completed", [])

        for stage_data in stages_completed:
            stage_id = stage_data.get("stage_id")
            if stage_id in self.stage_metrics:
                self.stage_metrics[stage_id]["status"] = "completed"
                self.stage_metrics[stage_id]["metrics"] = stage_data.get("benchmark_results", {})

                # Update performance trends
                benchmark_results = stage_data.get("benchmark_results", {})
                for benchmark_name, score in benchmark_results.items():
                    if benchmark_name in self.performance_trends:
                        self.performance_trends[benchmark_name].append(score)

        # Update current stage
        if stages_completed:
            latest_stage = max(stage["stage_id"] for stage in stages_completed)
            self.current_stage = min(latest_stage + 1, 4)  # Next stage or 4 if all completed

    def create_dashboard_layout(self) -> Layout:
        """Create the main dashboard layout"""
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )

        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="center"),
            Layout(name="right")
        )

        return layout

    def update_header(self, layout: Layout):
        """Update dashboard header"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed = datetime.now() - self.monitoring_start
        elapsed_str = str(elapsed).split('.')[0]

        header_text = f"📊 B3 Remote Distillation Metrics Dashboard | {current_time} | Runtime: {elapsed_str}"

        layout["header"].update(
            Panel(
                Align.center(header_text),
                style="bold cyan",
                box=box.DOUBLE
            )
        )

    def create_stage_overview(self) -> Panel:
        """Create stage overview panel"""
        table = Table(title="🎯 Stage Overview", box=box.ROUNDED)
        table.add_column("Stage", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Status", style="green")
        table.add_column("Performance", style="yellow")

        for stage_id, stage_info in self.stage_metrics.items():
            name = stage_info["name"]
            status = stage_info["status"]

            # Status emoji
            if status == "completed":
                status_display = "✅ Completed"
            elif status == "in_progress":
                status_display = "🟡 In Progress"
            else:
                status_display = "⚪ Pending"

            # Performance summary
            metrics = stage_info.get("metrics", {})
            if metrics:
                avg_score = sum(metrics.values()) / len(metrics)
                performance = f"{avg_score:.3f}"
            else:
                performance = "--"

            table.add_row(f"Stage {stage_id}", name, status_display, performance)

        return Panel(table, border_style="green")

    def create_api_analytics(self) -> Panel:
        """Create API analytics panel"""
        table = Table(title="🌐 API Analytics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")

        # Calculate API statistics
        total_calls = len(self.api_call_history)
        successful_calls = sum(1 for call in self.api_call_history if call.get("success", False))
        failed_calls = total_calls - successful_calls

        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0

        # Average response time
        response_times = [call.get("response_time", 0) for call in self.api_call_history if call.get("response_time", 0) > 0]
        avg_response_time = statistics.mean(response_times) if response_times else 0

        # Status assessment
        if success_rate >= 95:
            status_emoji = "🟢 Excellent"
        elif success_rate >= 80:
            status_emoji = "🟡 Good"
        else:
            status_emoji = "🔴 Poor"

        table.add_row("Total API Calls", str(total_calls), "📊")
        table.add_row("Successful", str(successful_calls), "✅")
        table.add_row("Failed", str(failed_calls), "❌")
        table.add_row("Success Rate", f"{success_rate:.1f}%", status_emoji)
        table.add_row("Avg Response", f"{avg_response_time:.2f}s", "⏱️")

        return Panel(table, border_style="blue")

    def create_prompt_analytics_panel(self) -> Panel:
        """Create prompt analytics panel"""
        analytics = self.prompt_analytics

        table = Table(title="💬 Prompt Analytics", box=box.ROUNDED)
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Percentage", style="yellow")

        total = analytics["total_prompts"]
        successful = analytics["successful_prompts"]
        failed = analytics["failed_prompts"]

        success_pct = (successful / total * 100) if total > 0 else 0
        failure_pct = (failed / total * 100) if total > 0 else 0

        table.add_row("Total Prompts", str(total), "100%")
        table.add_row("Successful", str(successful), f"{success_pct:.1f}%")
        table.add_row("Failed", str(failed), f"{failure_pct:.1f}%")
        table.add_row("Avg Response Time", f"{analytics['average_response_time']:.2f}s", "⏱️")

        # Add stage breakdown
        if analytics["prompts_by_stage"]:
            table.add_row("", "", "")  # Separator
            for stage, count in analytics["prompts_by_stage"].items():
                stage_pct = (count / total * 100) if total > 0 else 0
                table.add_row(stage, str(count), f"{stage_pct:.1f}%")

        return Panel(table, border_style="magenta")

    def create_performance_trends(self) -> Panel:
        """Create performance trends panel"""
        table = Table(title="📈 Performance Trends", box=box.ROUNDED)
        table.add_column("Benchmark", style="cyan")
        table.add_column("Latest", style="green")
        table.add_column("Trend", style="yellow")
        table.add_column("Change", style="blue")

        for benchmark_name, scores in self.performance_trends.items():
            if not scores:
                continue

            latest_score = scores[-1]

            if len(scores) >= 2:
                previous_score = scores[-2]
                change = latest_score - previous_score

                if change > 0:
                    trend = "📈 Up"
                    change_str = f"+{change:.3f}"
                elif change < 0:
                    trend = "📉 Down"
                    change_str = f"{change:.3f}"
                else:
                    trend = "➡️ Stable"
                    change_str = "0.000"
            else:
                trend = "➡️ New"
                change_str = "--"

            # Format benchmark name
            display_name = benchmark_name.replace("_", " ").title()

            table.add_row(display_name, f"{latest_score:.3f}", trend, change_str)

        return Panel(table, border_style="yellow")

    def update_footer(self, layout: Layout):
        """Update dashboard footer"""
        files = self.scan_for_files()
        file_count = sum(len(file_list) for file_list in files.values())

        footer_text = f"📁 Monitoring {file_count} files | 🔄 Auto-refresh | Press Ctrl+C to stop"

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

        # Left column: Stage overview and API analytics
        stage_panel = self.create_stage_overview()
        api_panel = self.create_api_analytics()

        left_layout = Layout()
        left_layout.split_column(Layout(stage_panel), Layout(api_panel))
        layout["left"].update(left_layout)

        # Center column: Performance trends
        performance_panel = self.create_performance_trends()
        layout["center"].update(performance_panel)

        # Right column: Prompt analytics
        prompt_panel = self.create_prompt_analytics_panel()
        layout["right"].update(prompt_panel)

        self.update_footer(layout)

    async def monitoring_loop(self):
        """Main monitoring loop"""
        layout = self.create_dashboard_layout()

        with Live(layout, refresh_per_second=1, screen=True):
            while True:
                try:
                    # Scan for new log entries
                    files = self.scan_for_files()

                    # Process log files for API calls
                    for log_file in files["logs"]:
                        api_calls = self.parse_log_for_api_calls(log_file)
                        self.api_call_history.extend(api_calls)

                    # Load latest metrics
                    latest_metrics = self.load_latest_metrics()
                    if latest_metrics:
                        self.update_stage_metrics(latest_metrics)

                    # Update dashboard
                    self.update_dashboard(layout)

                    # Wait before next update
                    await asyncio.sleep(2)

                except KeyboardInterrupt:
                    break
                except Exception:
                    # Continue monitoring even if there are errors
                    await asyncio.sleep(1)

    def start_monitoring(self):
        """Start the metrics dashboard"""
        self.console.print("🚀 Starting B3 Remote Distillation Metrics Dashboard...")
        self.console.print("📊 Live metrics and API tracking")
        self.console.print("⏹️  Press Ctrl+C to stop\n")

        try:
            asyncio.run(self.monitoring_loop())
        except KeyboardInterrupt:
            self.console.print("\n🛑 Dashboard stopped")


def main():
    """Main function"""
    dashboard = MetricsDashboard()
    dashboard.start_monitoring()


if __name__ == "__main__":
    main()
