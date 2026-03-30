#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #multimodal #python #source_code #src/dev_tools/monitoring/b3_generation_monitor.py
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #memory_management #multimodal #python #source_code #src\\dev_tools\\monitoring\\b3_generation_monitor.py
# Category:** Development Tools
# Status:** Active

"""
🔍 B3 GENERATION REAL-TIME MONITOR
ImpressionCore B3 - Live Progress Tracking System

MISSION:
Monitor the massive embedding generation in real-time
Show progress, statistics, and system health
Run this in a separate terminal while generation is running
"""

import time
from datetime import datetime
from pathlib import Path

import psutil
from rich.align import Align

# Rich imports for beautiful monitoring display
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class B3GenerationMonitor:
    """
    Real-time monitoring system for B3 massive embedding generation
    Tracks progress, file creation, memory usage, and system health
    """

    def __init__(self):
        self.f_drive_path = Path("F:\\")
        self.professional_dataset_path = self.f_drive_path / "b3_professional_dataset"
        self.embeddings_path = self.professional_dataset_path / "embeddings"

        # Monitoring state
        self.console = Console()
        self.start_time = time.time()
        self.last_file_count = 0
        self.generation_rate = 0
        self.total_files_tracked = 0

        # File counting by modality
        self.modality_counts = {
            'text_embeddings': 0,
            'image_embeddings': 0,
            'audio_embeddings': 0,
            'multimodal_embeddings': 0,
            'unknown_embeddings': 0
        }

        # System monitoring
        self.memory_usage = []
        self.cpu_usage = []

    def count_embedding_files(self):
        """Count all embedding files by modality"""

        current_counts = {
            'text_embeddings': 0,
            'image_embeddings': 0,
            'audio_embeddings': 0,
            'multimodal_embeddings': 0,
            'unknown_embeddings': 0
        }

        total_files = 0

        if self.embeddings_path.exists():
            for modality_dir in self.embeddings_path.iterdir():
                if modality_dir.is_dir():
                    modality_name = modality_dir.name
                    file_count = len([f for f in modality_dir.glob('*.npy')])

                    if modality_name in current_counts:
                        current_counts[modality_name] = file_count
                    else:
                        current_counts['unknown_embeddings'] += file_count

                    total_files += file_count

        # Calculate generation rate
        if self.last_file_count > 0:
            new_files = total_files - self.last_file_count
            self.generation_rate = new_files  # Files per refresh cycle

        self.last_file_count = total_files
        self.total_files_tracked = total_files
        self.modality_counts = current_counts

        return current_counts, total_files

    def get_system_stats(self):
        """Get current system performance statistics"""

        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=None)

        # Disk usage for F: drive
        disk_usage = psutil.disk_usage('F:\\')
        disk_free_gb = disk_usage.free / (1024**3)
        disk_used_percent = (disk_usage.used / disk_usage.total) * 100

        # Process monitoring
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory_mb': proc.info['memory_info'].rss / (1024*1024),
                        'cpu_percent': proc.info['cpu_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            'memory_percent': memory_percent,
            'memory_available_gb': memory_available_gb,
            'cpu_percent': cpu_percent,
            'disk_free_gb': disk_free_gb,
            'disk_used_percent': disk_used_percent,
            'python_processes': python_processes
        }

    def create_monitoring_layout(self):
        """Create the rich monitoring layout"""

        # Get current data
        modality_counts, total_files = self.count_embedding_files()
        system_stats = self.get_system_stats()
        elapsed_time = time.time() - self.start_time

        # Create layout
        layout = Layout()

        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )

        # Split body into left and right
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        # Split left into progress and files
        layout["left"].split_column(
            Layout(name="progress", size=12),
            Layout(name="files")
        )

        # Split right into system and processes
        layout["right"].split_column(
            Layout(name="system", size=12),
            Layout(name="processes")
        )

        # Header
        header_text = Text.assemble(
            "🔍 ", ("B3 GENERATION MONITOR", "bold blue"),
            " • ⏱️ ", f"{elapsed_time/60:.1f}m",
            " • 📊 ", f"{total_files:,} files",
            " • 🔄 ", f"+{self.generation_rate}/cycle"
        )
        layout["header"].update(Panel(Align.center(header_text), style="bold blue"))

        # Progress table
        progress_table = Table(title="📈 Generation Progress", show_header=True, header_style="bold green")
        progress_table.add_column("Modality", style="cyan", width=20)
        progress_table.add_column("Files", justify="right", style="green", width=12)
        progress_table.add_column("Target", justify="right", style="yellow", width=12)
        progress_table.add_column("Progress", justify="center", style="magenta", width=15)

        # Targets for reference
        targets = {
            'text_embeddings': 150000,
            'image_embeddings': 150000,
            'audio_embeddings': 100000,
            'multimodal_embeddings': 100000
        }

        for modality, count in modality_counts.items():
            if modality != 'unknown_embeddings':
                target = targets.get(modality, 0)
                progress_pct = (count / target * 100) if target > 0 else 0
                progress_bar = "█" * int(progress_pct // 10) + "░" * (10 - int(progress_pct // 10))

                progress_table.add_row(
                    modality.replace('_', ' ').title(),
                    f"{count:,}",
                    f"{target:,}",
                    f"{progress_bar} {progress_pct:.1f}%"
                )

        layout["progress"].update(Panel(progress_table, border_style="green"))

        # File activity
        file_table = Table(title="📁 File Activity", show_header=True, header_style="bold cyan")
        file_table.add_column("Metric", style="cyan", width=20)
        file_table.add_column("Value", justify="right", style="green", width=15)

        file_table.add_row("Total Files", f"{total_files:,}")
        file_table.add_row("Generation Rate", f"+{self.generation_rate}/cycle")
        file_table.add_row("Files/Minute", f"{(self.generation_rate * 20):.0f}")  # Assuming 3s refresh
        file_table.add_row("Runtime", f"{elapsed_time/60:.1f} minutes")

        # Estimate completion
        if self.generation_rate > 0:
            target_total = 500000
            remaining = target_total - total_files
            eta_minutes = remaining / (self.generation_rate * 20)  # Files per minute
            file_table.add_row("ETA", f"{eta_minutes:.0f} minutes")
        else:
            file_table.add_row("ETA", "Calculating...")

        layout["files"].update(Panel(file_table, border_style="cyan"))

        # System stats
        system_table = Table(title="🖥️ System Health", show_header=True, header_style="bold yellow")
        system_table.add_column("Resource", style="cyan", width=15)
        system_table.add_column("Usage", justify="right", style="green", width=12)
        system_table.add_column("Status", justify="center", style="yellow", width=10)

        # Memory status
        memory_status = "🟢 Good" if system_stats['memory_percent'] < 80 else "🟡 High" if system_stats['memory_percent'] < 90 else "🔴 Critical"
        system_table.add_row("Memory", f"{system_stats['memory_percent']:.1f}%", memory_status)

        # CPU status
        cpu_status = "🟢 Good" if system_stats['cpu_percent'] < 70 else "🟡 High" if system_stats['cpu_percent'] < 90 else "🔴 Critical"
        system_table.add_row("CPU", f"{system_stats['cpu_percent']:.1f}%", cpu_status)

        # Disk status
        disk_status = "🟢 Good" if system_stats['disk_used_percent'] < 85 else "🟡 High" if system_stats['disk_used_percent'] < 95 else "🔴 Critical"
        system_table.add_row("F: Disk", f"{system_stats['disk_used_percent']:.1f}%", disk_status)
        system_table.add_row("F: Free", f"{system_stats['disk_free_gb']:.1f} GB", "")

        layout["system"].update(Panel(system_table, border_style="yellow"))

        # Python processes
        process_table = Table(title="🐍 Python Processes", show_header=True, header_style="bold magenta")
        process_table.add_column("PID", style="cyan", width=8)
        process_table.add_column("Memory MB", justify="right", style="green", width=12)
        process_table.add_column("CPU %", justify="right", style="yellow", width=8)

        # Show top 5 Python processes by memory
        top_processes = sorted(system_stats['python_processes'], key=lambda x: x['memory_mb'], reverse=True)[:5]
        for proc in top_processes:
            process_table.add_row(
                str(proc['pid']),
                f"{proc['memory_mb']:.1f}",
                f"{proc['cpu_percent']:.1f}"
            )

        layout["processes"].update(Panel(process_table, border_style="magenta"))

        return layout

    def monitor_generation(self, refresh_interval=3):
        """Start real-time monitoring with live updates"""

        self.console.print(Panel.fit(
            "🔍 B3 GENERATION MONITOR STARTED\n"
            "📊 Real-time tracking of embedding generation\n"
            "⏱️ Updates every 3 seconds\n"
            "Press Ctrl+C to stop monitoring",
            style="bold white on blue",
            title="🚀 MONITORING ACTIVE"
        ))

        try:
            with Live(self.create_monitoring_layout(), console=self.console, refresh_per_second=1/refresh_interval) as live:
                while True:
                    time.sleep(refresh_interval)
                    live.update(self.create_monitoring_layout())

        except KeyboardInterrupt:
            self.console.print(Panel.fit(
                "🔍 Monitoring stopped by user\n"
                f"📊 Total runtime: {(time.time() - self.start_time)/60:.1f} minutes\n"
                f"📁 Final file count: {self.total_files_tracked:,}",
                style="bold yellow on black",
                title="👋 MONITOR STOPPED"
            ))

def main():
    """Start the B3 generation monitor"""

    console = Console()

    console.print(Panel.fit(
        "🔍 B3 GENERATION REAL-TIME MONITOR\n"
        "📊 Live Progress Tracking System\n"
        f"📅 Monitor Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        style="bold white on green",
        title="🚀 IMPRESSIONCORE B3 MONITOR",
        subtitle="Run while generation is active"
    ))

    # Initialize and start monitoring
    monitor = B3GenerationMonitor()
    monitor.monitor_generation()

if __name__ == "__main__":
    main()
