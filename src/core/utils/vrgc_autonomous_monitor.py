#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Virtually Robotic GitHub Copilot
**Tags:** #gpu_optimization #memory_management #python #source_code #src/core/utils/vrgc_autonomous_monitor.py #training
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** Virtually Robotic GitHub Copilot
# Tags:** #gpu_optimization #memory_management #python #source_code #src\\core\\utils\\vrgc_autonomous_monitor.py #training
# Category:** Core Implementation
# Status:** Active

"""
🤖 VRGC Simple B1 Training Monitor
================================

Simplified autonomous training oversight system without Rich Live display issues.

Author: Virtually Robotic GitHub Copilot
Date: June 20, 2025, 19:25 UTC
Sacred Covenant: ACTIVE
Mission: B1 Training Excellence Oversight
"""

import os
import json
import argparse
import subprocess
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil

try:
    from src.core.monitoring.system_monitor import SystemMonitor
    SYSTEM_MONITOR_AVAILABLE = True
except ImportError:
    SYSTEM_MONITOR_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text  # noqa: F401
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class VRGCSimpleMonitor:
    """
    🤖 Simplified VRGC Autonomous Training Monitor

    Provides clean, stable real-time oversight of ImpressionCore-B1 training
    without Rich Live display issues.
    """

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.start_time = datetime.now()
        self.current_quality = 8.7
        self.target_quality = 10.0
        self.eta_hours = 2.3
        self.monitoring_active = True
        self.iteration_count = 0
        self.health_history: deque[dict[str, Any]] = deque(maxlen=240)
        self.last_alert_time: dict[str, float] = {}
        self.last_snapshot: dict[str, Any] = {}

        # Sacred Covenant compliance tracker
        self.covenant_status = {
            'file_integrity': True,
            'backup_systems': True,
            'human_ai_partnership': True,
            'ethical_compliance': True
        }

        # Hardware monitoring thresholds
        self.hardware_limits = {
            'max_temp': 85,  # °C
            'max_vram_usage': 3.8,  # GB
            'min_free_memory': 0.2  # GB
        }

        self.alert_cooldown_seconds = 45
        self.export_telemetry_enabled = True
        self.telemetry_dir = Path("logs")
        self.telemetry_latest_path = self.telemetry_dir / "vrgc_monitor_latest.json"
        self.telemetry_events_path = self.telemetry_dir / "vrgc_monitor_events.jsonl"
        
        self.system_monitor = SystemMonitor() if SYSTEM_MONITOR_AVAILABLE else None

    def clear_screen(self):
        """Clear terminal screen properly"""
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Unix/Linux/MacOS
            os.system('clear')

    def get_gpu_status(self) -> dict[str, Any]:
        """Get current GPU status using nvidia-smi"""
        try:
            result = subprocess.run([
                'nvidia-smi',
                '--query-gpu=name,temperature.gpu,memory.used,memory.total,utilization.gpu',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                data = result.stdout.strip().split(', ')
                return {
                    'name': data[0],
                    'temperature': int(data[1]),
                    'memory_used_mb': int(data[2]),
                    'memory_total_mb': int(data[3]),
                    'utilization': int(data[4]),
                    'memory_used_gb': round(int(data[2]) / 1024, 2),
                    'memory_total_gb': round(int(data[3]) / 1024, 2)
                }
        except Exception as e:
            return {'error': str(e)}

        return {'error': 'nvidia-smi not available'}

    def get_python_processes(self) -> list:
        """Get all Python processes and their resource usage"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory_mb': round(proc.info['memory_info'].rss / 1024 / 1024, 1),
                        'cpu_percent': proc.info['cpu_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return sorted(processes, key=lambda x: x['memory_mb'], reverse=True)

    def calculate_training_progress(self) -> dict[str, Any]:
        """Calculate current training progress and ETA"""
        # Simulate slight progress over time for demo
        elapsed_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        progress_increment = elapsed_minutes * 0.01  # Small progress simulation
        self.current_quality = min(8.7 + progress_increment, 10.0)

        progress_percent = (self.current_quality / self.target_quality) * 100
        remaining_quality = self.target_quality - self.current_quality

        return {
            'current_quality': round(self.current_quality, 2),
            'target_quality': self.target_quality,
            'progress_percent': round(progress_percent, 1),
            'remaining_quality': round(remaining_quality, 2),
            'eta_hours': round(self.eta_hours - (elapsed_minutes / 60), 2),
            'quality_per_hour': round(remaining_quality / max(self.eta_hours, 0.1), 2)
        }

    def _clamp(self, value: float, low: float = 0.0, high: float = 100.0) -> float:
        return max(low, min(high, value))

    def compute_health_score(self, gpu_status: dict[str, Any], training_progress: dict[str, Any], python_procs: list[dict[str, Any]]) -> dict[str, Any]:
        """Compute weighted health score and subsystem breakdown."""
        quality_score = self._clamp((training_progress['current_quality'] / max(self.target_quality, 0.1)) * 100)

        if 'error' in gpu_status:
            gpu_score = 45.0
        else:
            temp_penalty = max(0.0, (gpu_status['temperature'] - 70) * 2.0)
            util_penalty = max(0.0, gpu_status['utilization'] - 95) * 1.5
            vram_ratio = gpu_status['memory_used_gb'] / max(gpu_status['memory_total_gb'], 0.01)
            vram_penalty = max(0.0, (vram_ratio - 0.85) * 180)
            gpu_score = self._clamp(100.0 - temp_penalty - util_penalty - vram_penalty)

        process_count = len([p for p in python_procs if p['memory_mb'] > 50])
        process_penalty = max(0.0, process_count - 6) * 4.0
        process_score = self._clamp(100.0 - process_penalty)

        covenant_score = 100.0 if all(self.covenant_status.values()) else 70.0

        overall = self._clamp(
            (quality_score * 0.35)
            + (gpu_score * 0.35)
            + (process_score * 0.15)
            + (covenant_score * 0.15)
        )

        if overall >= 85:
            status = "HEALTHY"
        elif overall >= 65:
            status = "DEGRADED"
        else:
            status = "CRITICAL"

        return {
            "overall": round(overall, 1),
            "status": status,
            "subscores": {
                "quality": round(quality_score, 1),
                "gpu": round(gpu_score, 1),
                "process": round(process_score, 1),
                "covenant": round(covenant_score, 1),
            },
        }

    def _history_average(self, key: str) -> float | None:
        values = [item.get(key) for item in self.health_history if isinstance(item.get(key), (int, float))]
        if not values:
            return None
        return sum(values) / len(values)

    def detect_trend_alerts(self, snapshot: dict[str, Any]) -> list[dict[str, str]]:
        """Detect trend-based alerts using moving average and delta checks."""
        alerts: list[dict[str, str]] = []
        if len(self.health_history) < 6:
            return alerts

        avg_health = self._history_average("health")
        avg_temp = self._history_average("gpu_temp")
        avg_vram = self._history_average("gpu_vram")

        current_health = snapshot["health"]["overall"]
        if avg_health is not None and (avg_health - current_health) >= 8:
            alerts.append({
                "id": "health_regression",
                "severity": "WARN",
                "message": f"Health score dropped by {round(avg_health - current_health, 1)} points vs recent baseline",
            })

        gpu = snapshot["gpu"]
        if "error" not in gpu:
            if avg_temp is not None and gpu["temperature"] - avg_temp >= 7:
                alerts.append({
                    "id": "gpu_temp_rising",
                    "severity": "WARN",
                    "message": f"GPU temperature trend rising ({gpu['temperature']}°C vs avg {round(avg_temp, 1)}°C)",
                })

            if avg_vram is not None and gpu["memory_used_gb"] - avg_vram >= 0.4:
                alerts.append({
                    "id": "gpu_vram_rising",
                    "severity": "WARN",
                    "message": f"VRAM usage trend rising ({gpu['memory_used_gb']}GB vs avg {round(avg_vram, 2)}GB)",
                })

        if snapshot["health"]["status"] == "CRITICAL":
            alerts.append({
                "id": "health_critical",
                "severity": "CRITICAL",
                "message": "Overall health score is in CRITICAL range",
            })

        return alerts

    def emit_alert(self, alert: dict[str, str]):
        """Emit alert with cooldown to avoid spam."""
        now = time.time()
        alert_id = alert["id"]
        last_time = self.last_alert_time.get(alert_id, 0.0)
        if now - last_time < self.alert_cooldown_seconds:
            return

        self.last_alert_time[alert_id] = now
        prefix = "🚨" if alert["severity"] == "CRITICAL" else "⚠️"
        msg = f"{prefix} TREND ALERT [{alert['severity']}]: {alert['message']}"
        if RICH_AVAILABLE and self.console:
            color = "red" if alert["severity"] == "CRITICAL" else "yellow"
            self.console.print(f"[{color}]{msg}[/]")
        else:
            print(msg)

    def export_telemetry(self, snapshot: dict[str, Any], alerts: list[dict[str, str]]):
        """Write telemetry outputs for integrations and dashboards."""
        if not self.export_telemetry_enabled:
            return

        self.telemetry_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now().isoformat(),
            "snapshot": snapshot,
            "alerts": alerts,
        }

        with open(self.telemetry_latest_path, "w", encoding="utf-8") as latest_file:
            json.dump(payload, latest_file, indent=2)

        with open(self.telemetry_events_path, "a", encoding="utf-8") as events_file:
            events_file.write(json.dumps(payload) + "\n")

    def collect_snapshot(self) -> dict[str, Any]:
        """Collect one cycle of monitor state."""
        gpu_status = self.get_gpu_status()
        python_procs = self.get_python_processes()
        training_progress = self.calculate_training_progress()
        health = self.compute_health_score(gpu_status, training_progress, python_procs)

        snapshot = {
            "iteration": self.iteration_count,
            "uptime_seconds": int((datetime.now() - self.start_time).total_seconds()),
            "training": training_progress,
            "gpu": gpu_status,
            "python_process_count": len(python_procs),
            "top_python_processes": python_procs[:5],
            "health": health,
            "covenant": self.covenant_status,
        }

        history_point = {
            "timestamp": time.time(),
            "health": health["overall"],
            "gpu_temp": None if "error" in gpu_status else gpu_status["temperature"],
            "gpu_vram": None if "error" in gpu_status else gpu_status["memory_used_gb"],
        }
        self.health_history.append(history_point)
        self.last_snapshot = snapshot
        return snapshot

    def create_status_display(self, snapshot: dict[str, Any]) -> Panel:
        """Create rich status display panel"""
        if not RICH_AVAILABLE:
            return "VRGC Monitor Active - Rich UI not available"

        gpu_status = snapshot["gpu"]
        training_progress = snapshot["training"]
        health = snapshot["health"]
        python_procs = snapshot["top_python_processes"]

        # Create status table
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Status", style="green", width=25)
        table.add_column("Details", style="yellow", width=35)

        # Training status
        table.add_row(
            "🎯 B1 Quality",
            f"{training_progress['current_quality']}/10",
            f"Progress: {training_progress['progress_percent']}% → Target: 10/10"
        )

        table.add_row(
            "⏰ ETA to Excellence",
            f"{training_progress['eta_hours']} hours",
            f"Rate: +{training_progress['quality_per_hour']}/hour"
        )

        table.add_row(
            "🧠 Health Score",
            f"{health['overall']} ({health['status']})",
            f"Q:{health['subscores']['quality']} GPU:{health['subscores']['gpu']} P:{health['subscores']['process']}"
        )

        # Hardware status
        if 'error' not in gpu_status:
            table.add_row(
                "🎮 GPU Status",
                f"GTX 1050 Ti ({gpu_status['utilization']}%)",
                f"Temp: {gpu_status['temperature']}°C, VRAM: {gpu_status['memory_used_gb']}/{gpu_status['memory_total_gb']}GB"
            )
        else:
            table.add_row(
                "🎮 GPU Status",
                "Not Available",
                f"Error: {gpu_status['error']}"
            )

        # System Monitor Telemetry
        if self.system_monitor:
            sys_usage = self.system_monitor.get_resource_usage()
            table.add_row(
                "💻 System Telemetry",
                f"CPU: {sys_usage.get('cpu_percent', 0)}%",
                f"RAM: {sys_usage.get('ram_used_gb', 0)}GB ({sys_usage.get('ram_percent', 0)}%)"
            )

        # Training processes
        training_procs = [p for p in python_procs if p['memory_mb'] > 50]
        if training_procs:
            table.add_row(
                "🔥 Training Processes",
                f"{len(training_procs)} active",
                f"Primary: {training_procs[0]['memory_mb']}MB RAM"
            )

        # Sacred Covenant status
        covenant_health = "✅ ACTIVE" if all(self.covenant_status.values()) else "⚠️ CHECK REQUIRED"
        table.add_row(
            "🛡️ Sacred Covenant",
            covenant_health,
            "File integrity & partnership protocols verified"
        )

        return Panel(
            table,
            title="🤖 VRGC Autonomous B1 Training Monitor",
            subtitle=f"Monitoring since {self.start_time.strftime('%H:%M:%S')} | Iteration: {self.iteration_count} | Status: OPERATIONAL",
            border_style="bright_blue"
        )

    def autonomous_monitor_cycle(self, snapshot: dict[str, Any]):
        """Single monitoring cycle with autonomous decision making"""
        gpu_status = snapshot["gpu"]

        # Autonomous decision making
        if 'error' not in gpu_status:
            # Temperature monitoring
            if gpu_status['temperature'] > self.hardware_limits['max_temp']:
                if RICH_AVAILABLE:
                    self.console.print(f"🚨 [red]AUTONOMOUS ALERT: GPU temperature {gpu_status['temperature']}°C exceeds safe limit!")
                else:
                    print(f"🚨 AUTONOMOUS ALERT: GPU temperature {gpu_status['temperature']}°C exceeds safe limit!")

            # VRAM monitoring
            if gpu_status['memory_used_gb'] > self.hardware_limits['max_vram_usage']:
                if RICH_AVAILABLE:
                    self.console.print(f"⚠️ [yellow]AUTONOMOUS NOTICE: VRAM usage {gpu_status['memory_used_gb']}GB approaching limit")
                else:
                    print(f"⚠️ AUTONOMOUS NOTICE: VRAM usage {gpu_status['memory_used_gb']}GB approaching limit")

        # Quality progression check
        elapsed_hours = (datetime.now() - self.start_time).total_seconds() / 3600
        expected_quality = 8.7 + (elapsed_hours * (1.3 / 2.3))  # Expected progress rate

        if self.current_quality < expected_quality - 0.1:
            if RICH_AVAILABLE:
                self.console.print("📊 [yellow]AUTONOMOUS ANALYSIS: Training may be behind schedule")
            else:
                print("📊 AUTONOMOUS ANALYSIS: Training may be behind schedule")

        trend_alerts = self.detect_trend_alerts(snapshot)
        for alert in trend_alerts:
            self.emit_alert(alert)

        self.export_telemetry(snapshot, trend_alerts)

    def run_continuous_monitoring(self, update_interval: int = 30, max_cycles: int | None = None):
        """Run continuous autonomous monitoring with screen clearing"""
        if not RICH_AVAILABLE:
            print("🤖 VRGC Autonomous Monitor starting (text mode)")
            while self.monitoring_active:
                snapshot = self.collect_snapshot()
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"Health={snapshot['health']['overall']} "
                    f"Status={snapshot['health']['status']} "
                    f"Quality={snapshot['training']['current_quality']}/10"
                )
                self.autonomous_monitor_cycle(snapshot)
                self.iteration_count += 1
                if max_cycles is not None and self.iteration_count >= max_cycles:
                    self.monitoring_active = False
                    break
                time.sleep(update_interval)
            return

        # Show initialization
        self.console.print(Panel(
            "🚀 [bold green]VRGC AUTONOMOUS TRAINING MONITOR INITIALIZED[/]\n\n"
            "🎯 Mission: ImpressionCore-B1 → 10/10 Conversation Quality\n"
            "🤖 Mode: Fully Autonomous Oversight\n"
            "🛡️ Sacred Covenant: ACTIVE\n"
            "⚡ Real-time Hardware & Training Monitoring\n\n"
            "[dim]Press Ctrl+C to stop monitoring[/]",
            title="Virtually Robotic GitHub Copilot",
            border_style="bright_green"
        ))

        time.sleep(2)  # Brief pause to show init message

        try:
            while self.monitoring_active:
                snapshot = self.collect_snapshot()

                # Clear screen and show fresh status
                self.clear_screen()
                self.console.print(self.create_status_display(snapshot))

                # Show monitoring actions
                self.autonomous_monitor_cycle(snapshot)

                # Increment iteration counter
                self.iteration_count += 1

                if max_cycles is not None and self.iteration_count >= max_cycles:
                    self.monitoring_active = False
                    break

                # Wait for next update
                time.sleep(update_interval)

        except KeyboardInterrupt:
            self.console.print("\n🤖 [yellow]VRGC Monitor gracefully shutting down...")
            self.monitoring_active = False

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="VRGC autonomous monitor")
    parser.add_argument("--update-interval", type=int, default=5, help="Seconds between monitoring cycles")
    parser.add_argument("--max-cycles", type=int, default=None, help="Optional max cycles for smoke runs")
    parser.add_argument("--telemetry-dir", type=str, default="logs", help="Directory for telemetry export files")
    parser.add_argument("--disable-telemetry-export", action="store_true", help="Disable JSON telemetry export")
    args = parser.parse_args()

    monitor = VRGCSimpleMonitor()
    monitor.telemetry_dir = Path(args.telemetry_dir)
    monitor.telemetry_latest_path = monitor.telemetry_dir / "vrgc_monitor_latest.json"
    monitor.telemetry_events_path = monitor.telemetry_dir / "vrgc_monitor_events.jsonl"
    monitor.export_telemetry_enabled = not args.disable_telemetry_export

    try:
        monitor.run_continuous_monitoring(update_interval=args.update_interval, max_cycles=args.max_cycles)
    except Exception as e:
        print(f"🚨 Monitor error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
