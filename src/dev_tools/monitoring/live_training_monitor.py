#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #gpu_optimization #memory_management #python #source_code #src/dev_tools/monitoring/live_training_monitor.py #testing #tokenization #training
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #cuda #gpu_optimization #memory_management #python #source_code #src/dev_tools/monitoring/live_training_monitor.py #testing #tokenization #training
# Category:** Development Tools
# Status:** Active

"""
ImpressionCore B1 Live Training Monitor

Real-time monitoring system for ImpressionCore B1 training progress,
system resources, and Sacred Covenant compliance.

File: src/dev_tools/monitoring/live_training_monitor.py
Created: 2025-06-18
Purpose: Continuous monitoring of B1 training toward 10/10 quality goal
"""

import json
import logging
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import psutil
import torch

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Rich imports for enhanced UI
try:
    from rich.columns import Columns  # noqa: F401
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn  # noqa: F401
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️ Rich not available - falling back to basic console output")

from collections.abc import Callable
from dataclasses import dataclass

# Import RichStatusAnimation with fallback
try:
    from core.utils.rich_status_animation import RichStatusAnimation
except ImportError:
    print("⚠️ RichStatusAnimation not available - using fallback")
    RichStatusAnimation = None

@dataclass
class SafetyThresholds:
    max_cpu_percent: float = 95.0
    max_memory_percent: float = 90.0
    max_disk_percent: float = 95.0
    max_gpu_memory_percent: float = 95.0
    max_runtime_hours: float = 24.0
    check_interval_seconds: float = 30.0

class ImpressionCoreLiveMonitor:
    """Unified advanced live monitoring system for ImpressionCore B1/B2 training."""
    def __init__(self, project_root: Path | None = None, thresholds: SafetyThresholds | None = None):
        self.project_root = project_root or Path.cwd()
        self.monitoring_active = False
        self.monitor_thread = None
        self.console = Console() if RICH_AVAILABLE else None
        self.status = RichStatusAnimation() if (RICH_AVAILABLE and RichStatusAnimation) else None

        # Monitoring configuration
        self.update_interval = 2.0  # seconds (UI refresh)
        self.quality_target = 10.0
        self.vram_target_gb = 4.0  # GTX 1050 Ti limit
        self.thresholds = thresholds or SafetyThresholds()

        # Data storage
        self.metrics_history = []
        self.alerts = []
        self.start_time = None
        self.training_metrics = {
            "epoch": 0,
            "step": 0,
            "loss": 0.0,
            "learning_rate": 0.0,
            "samples_processed": 0,
            "estimated_completion": None
        }
        self.shutdown_callbacks: list[Callable] = []

        # File paths
        self.training_dir = self.project_root / "src/training"
        self.models_dir = self.training_dir / "models/trained"
        self.exports_dir = self.project_root / "exports/production_models"
        self.logs_dir = self.project_root / "src/dev_tools/logs"

        # Create logs directory
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()

        # Setup signal handlers for graceful shutdown
        import signal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def add_shutdown_callback(self, callback: Callable):
        self.shutdown_callbacks.append(callback)

    def _signal_handler(self, signum, frame):
        self.logger.warning(f"Received signal {signum}, initiating graceful shutdown")
        self.stop_monitoring()

    def update_training_metrics(self, **kwargs):
        self.training_metrics.update(kwargs)
        self.logger.info(f"Training update: {self.training_metrics}")

    def get_training_summary(self) -> dict[str, Any]:
        system_summary = self.get_metrics_summary()
        return {
            "training_metrics": self.training_metrics,
            "system_metrics": system_summary,
            "status": "running" if self.monitoring_active else "stopped"
        }

    def get_metrics_summary(self) -> dict[str, Any]:
        if not self.metrics_history:
            return {}
        recent_metrics = self.metrics_history[-10:]
        return {
            "total_readings": len(self.metrics_history),
            "runtime_hours": (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0,
            "avg_cpu_percent": sum(m['system']['cpu_percent'] for m in recent_metrics) / len(recent_metrics),
            "avg_memory_percent": sum(m['system']['memory']['percent'] for m in recent_metrics) / len(recent_metrics),
            "max_cpu_percent": max(m['system']['cpu_percent'] for m in self.metrics_history),
            "max_memory_percent": max(m['system']['memory']['percent'] for m in self.metrics_history),
            "current_disk_gb": recent_metrics[-1]['system']['disk_usage']['project']['used_gb'] if recent_metrics and 'project' in recent_metrics[-1]['system']['disk_usage'] else 0
        }

    def _check_safety_thresholds(self, metrics: dict[str, Any]) -> list[str]:
        violations = []
        cpu = metrics['system']['cpu_percent']
        mem = metrics['system']['memory']['percent']
        disk = metrics['system']['disk_usage'].get('project', {}).get('percent_used', 0)
        gpu = metrics.get('gpu', {}).get('utilization_percent', 0)
        runtime = (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0
        if cpu > self.thresholds.max_cpu_percent:
            violations.append(f"CPU usage: {cpu:.1f}% > {self.thresholds.max_cpu_percent}%")
        if mem > self.thresholds.max_memory_percent:
            violations.append(f"Memory usage: {mem:.1f}% > {self.thresholds.max_memory_percent}%")
        if disk > self.thresholds.max_disk_percent:
            violations.append(f"Disk usage: {disk:.1f}% > {self.thresholds.max_disk_percent}%")
        if gpu > self.thresholds.max_gpu_memory_percent:
            violations.append(f"GPU memory: {gpu:.1f}% > {self.thresholds.max_gpu_memory_percent}%")
        if runtime > self.thresholds.max_runtime_hours:
            violations.append(f"Runtime: {runtime:.1f}h > {self.thresholds.max_runtime_hours}h")
        return violations

    def _emergency_shutdown(self, reason: str):
        self.logger.error(f"EMERGENCY SHUTDOWN: {reason}")
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Shutdown callback failed: {e}")
        self.save_metrics_history()
        self.monitoring_active = False
        if self.status:
            self.status.stop_animation()
        self.logger.error("Emergency shutdown completed")

    def save_metrics_history(self):
        if not self.metrics_history:
            return
        filename = f"metrics_history_live_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.logs_dir / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.metrics_history, f, indent=2)
            self.logger.info(f"Metrics history saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save metrics history: {e}")

    def _monitoring_loop(self):
        if self.status:
            self.status.start_animation("Live Monitoring Active")
        while self.monitoring_active:
            try:
                metrics = self.get_system_metrics()
                self.metrics_history.append(metrics)
                violations = self._check_safety_thresholds(metrics)
                if violations:
                    violation_text = "; ".join(violations)
                    self.logger.warning(f"Safety threshold violations: {violation_text}")
                    if len(violations) > 2 or any("CPU" in v and "95" in v for v in violations):
                        self._emergency_shutdown(f"Critical safety violations: {violation_text}")
                        break
                # Log periodic summary
                if len(self.metrics_history) % 10 == 0:
                    self.logger.info(f"Status: {metrics}")
                # Cleanup old metrics (keep last 1000)
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                time.sleep(self.thresholds.check_interval_seconds)
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)
        if self.status:
            self.status.stop_animation()

    def start_monitoring(self):
        if self.monitoring_active:
            self.logger.warning("Monitoring already running")
            return
        self.monitoring_active = True
        self.start_time = datetime.now()
        self.logger.info("Starting live monitoring")
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()
        return monitoring_thread

    def stop_monitoring(self):
        if not self.monitoring_active:
            return
        self.logger.info("Stopping live monitoring")
        self.monitoring_active = False
        if self.status:
            self.status.stop_animation()
        self.save_metrics_history()
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Shutdown callback failed: {e}")

    def setup_logging(self):
        """Setup logging for the monitoring system."""
        log_file = self.logs_dir / f"live_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Fix Windows console encoding for emoji support
        try:
            import sys
            if sys.platform == 'win32':
                import codecs
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
        except Exception:
            pass  # Fallback gracefully

    def get_system_metrics(self) -> dict[str, Any]:
        """Collect comprehensive system metrics."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': dict(psutil.virtual_memory()._asdict()),
                'disk_usage': {}
            },
            'gpu': {},
            'training': {},
            'files': {}
        }

        # Disk usage for key directories
        for path_name, path in [('project', self.project_root), ('f_drive', Path('F:/'))]:
            if path.exists():
                disk = psutil.disk_usage(str(path))
                metrics['system']['disk_usage'][path_name] = {
                    'total_gb': disk.total / (1024**3),
                    'used_gb': disk.used / (1024**3),
                    'free_gb': disk.free / (1024**3),
                    'percent_used': (disk.used / disk.total) * 100
                }

        # GPU metrics
        if torch.cuda.is_available():
            try:
                device = torch.cuda.current_device()
                metrics['gpu'] = {
                    'device_name': torch.cuda.get_device_name(device),
                    'memory_allocated_gb': torch.cuda.memory_allocated(device) / (1024**3),
                    'memory_reserved_gb': torch.cuda.memory_reserved(device) / (1024**3),
                    'memory_total_gb': torch.cuda.get_device_properties(device).total_memory / (1024**3),                    'utilization_percent': (torch.cuda.memory_allocated(device) / torch.cuda.get_device_properties(device).total_memory) * 100
                }
            except Exception as e:
                metrics['gpu']['error'] = str(e)
          # Training process detection - More specific detection for actual ImpressionCore training
        training_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                name = proc.info.get('name', '').lower()

                # Only detect actual training processes, not the monitor itself or unrelated processes
                is_training_process = False

                if cmdline and name == 'python.exe':
                    # Check for specific training script patterns
                    cmdline_str = ' '.join(str(arg) for arg in cmdline).lower()
                      # Look for actual training scripts (not just any mention of "training")
                    training_indicators = [
                        'train_impressioncore_b1.py',
                        'train_impressioncore_optimized.py',
                        'train_diffusion.py',
                        'trainer.py',
                        'training_manager.py',
                        'train_model.py',
                        'train_small.py',
                        'train_documents.py',
                        'train_with_documents.py',
                        'train_vae.py',
                        'train_tokenizer.py',
                        '-m src.training',  # Module execution
                        'src/training/trainer',  # Training module scripts
                        'src.training.trainer',  # Python module path
                    ]

                    # Exclude the monitor itself and other monitoring tools
                    exclusions = [
                        'live_training_monitor',
                        'monitor.py',
                        'monitoring/',
                        'dev_tools/',
                    ]

                    # Check if it matches training indicators but not exclusions
                    has_training_indicator = any(indicator in cmdline_str for indicator in training_indicators)
                    has_exclusion = any(exclusion in cmdline_str for exclusion in exclusions)

                    is_training_process = has_training_indicator and not has_exclusion

                if is_training_process:
                    training_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_mb': proc.info['memory_info'].rss / (1024**2) if proc.info['memory_info'] else 0,
                        'cmdline': ' '.join(str(arg) for arg in cmdline[:3])  # First few args for identification
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        metrics['training']['processes'] = training_processes
        metrics['training']['active'] = len(training_processes) > 0

        # File system monitoring
        metrics['files'] = {
            'models_count': len(list(self.models_dir.glob('*.pt'))) if self.models_dir.exists() else 0,
            'exports_count': len(list(self.exports_dir.glob('*'))) if self.exports_dir.exists() else 0,
            'latest_model': self.get_latest_model_info(),
            'f_drive_embeddings': self.check_f_drive_embeddings()
        }

        return metrics

    def get_latest_model_info(self) -> dict[str, Any] | None:
        """Get information about the latest trained model."""
        if not self.models_dir.exists():
            return None

        model_files = list(self.models_dir.glob('*.pt'))
        if not model_files:
            return None

        latest_model = max(model_files, key=lambda f: f.stat().st_mtime)
        return {
            'name': latest_model.name,
            'size_mb': latest_model.stat().st_size / (1024**2),
            'modified': datetime.fromtimestamp(latest_model.stat().st_mtime).isoformat()
        }

    def check_f_drive_embeddings(self) -> dict[str, Any]:
        """Check F: drive embedding status."""
        f_embeddings = Path('F:/embeddings')
        if not f_embeddings.exists():
            return {'status': 'not_found', 'count': 0}

        try:
            embedding_files = list(f_embeddings.glob('**/*.pt'))
            return {
                'status': 'available',
                'count': len(embedding_files),
                'total_size_gb': sum(f.stat().st_size for f in embedding_files) / (1024**3)
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def create_dashboard_layout(self, metrics: dict[str, Any]) -> Layout:
        """Create the Rich dashboard layout."""
        if not RICH_AVAILABLE:
            return None

        layout = Layout()

        # Split into sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )

        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        layout["left"].split_column(
            Layout(name="system", ratio=2),
            Layout(name="training", ratio=1)
        )

        layout["right"].split_column(
            Layout(name="gpu", ratio=1),
            Layout(name="files", ratio=1)
        )

        # Header
        header_text = Text("🤖 ImpressionCore B1 Live Training Monitor", style="bold blue")
        header_text.append(" - Target: 10/10 Quality - GTX 1050 Ti Optimized", style="dim")
        layout["header"].update(Panel(header_text, border_style="blue"))

        # System metrics
        system_table = Table(title="System Resources", border_style="green")
        system_table.add_column("Metric", style="cyan")
        system_table.add_column("Value", style="white")
        system_table.add_column("Status", style="green")

        cpu_status = "🔥" if metrics['system']['cpu_percent'] > 80 else "✅"
        system_table.add_row("CPU Usage", f"{metrics['system']['cpu_percent']:.1f}%", cpu_status)

        memory_gb = metrics['system']['memory']['used'] / (1024**3)
        memory_total_gb = metrics['system']['memory']['total'] / (1024**3)
        memory_percent = metrics['system']['memory']['percent']
        memory_status = "🔥" if memory_percent > 80 else "✅"
        system_table.add_row("RAM Usage", f"{memory_gb:.1f}GB / {memory_total_gb:.1f}GB ({memory_percent:.1f}%)", memory_status)

        # Disk usage
        if 'project' in metrics['system']['disk_usage']:
            disk = metrics['system']['disk_usage']['project']
            disk_status = "🔥" if disk['percent_used'] > 90 else "✅"
            system_table.add_row("Project Disk", f"{disk['free_gb']:.1f}GB free", disk_status)

        if 'f_drive' in metrics['system']['disk_usage']:
            f_disk = metrics['system']['disk_usage']['f_drive']
            f_status = "✅" if f_disk['free_gb'] > 100 else "⚠️"
            system_table.add_row("F: Drive", f"{f_disk['free_gb']:.1f}GB free", f_status)

        layout["system"].update(Panel(system_table, border_style="green"))

        # GPU metrics
        gpu_table = Table(title="GPU Status (GTX 1050 Ti)", border_style="yellow")
        gpu_table.add_column("Metric", style="cyan")
        gpu_table.add_column("Value", style="white")
        gpu_table.add_column("Status", style="yellow")

        if 'error' not in metrics['gpu']:
            vram_used = metrics['gpu']['memory_allocated_gb']
            vram_total = metrics['gpu']['memory_total_gb']
            vram_percent = metrics['gpu']['utilization_percent']
            vram_status = "🔥" if vram_percent > 90 else "✅"

            gpu_table.add_row("VRAM Usage", f"{vram_used:.2f}GB / {vram_total:.2f}GB ({vram_percent:.1f}%)", vram_status)
            gpu_table.add_row("Device", metrics['gpu']['device_name'], "✅")
        else:
            gpu_table.add_row("Status", "Error", "❌")
            gpu_table.add_row("Details", metrics['gpu']['error'], "❌")

        layout["gpu"].update(Panel(gpu_table, border_style="yellow"))

        # Training status
        training_table = Table(title="Training Status", border_style="magenta")
        training_table.add_column("Metric", style="cyan")
        training_table.add_column("Value", style="white")
        training_table.add_column("Status", style="magenta")

        training_active = metrics['training']['active']
        training_status = "🔄" if training_active else "⏸️"
        training_table.add_row("Training Active", "Yes" if training_active else "No", training_status)
        training_table.add_row("Active Processes", str(len(metrics['training']['processes'])), training_status)

        # Show process details
        for proc in metrics['training']['processes'][:3]:  # Show up to 3 processes
            training_table.add_row(f"PID {proc['pid']}", f"{proc['name']} ({proc['memory_mb']:.1f}MB)", "🔄")

        layout["training"].update(Panel(training_table, border_style="magenta"))

        # File system status
        files_table = Table(title="File System", border_style="blue")
        files_table.add_column("Metric", style="cyan")
        files_table.add_column("Value", style="white")
        files_table.add_column("Status", style="blue")

        files_table.add_row("Model Files", str(metrics['files']['models_count']), "📁")
        files_table.add_row("Export Dirs", str(metrics['files']['exports_count']), "📦")

        if metrics['files']['latest_model']:
            model = metrics['files']['latest_model']
            files_table.add_row("Latest Model", f"{model['name']} ({model['size_mb']:.1f}MB)", "🏆")

        f_embeddings = metrics['files']['f_drive_embeddings']
        if f_embeddings['status'] == 'available':
            files_table.add_row("F: Embeddings", f"{f_embeddings['count']} files ({f_embeddings['total_size_gb']:.1f}GB)", "💾")
        else:
            files_table.add_row("F: Embeddings", f_embeddings['status'], "❌")

        layout["files"].update(Panel(files_table, border_style="blue"))

        # Footer
        uptime = timedelta(seconds=int((datetime.now() - self.start_time).total_seconds())) if self.start_time else "Unknown"
        footer_text = Text(f"🕒 Uptime: {uptime} | 🎯 Sacred Covenant Active | 🔄 Update: {self.update_interval}s", style="dim")
        layout["footer"].update(Panel(footer_text, border_style="dim"))

        return layout

    def save_metrics_history(self, metrics: dict[str, Any]):  # noqa: F811
        """Save metrics to history file."""
        self.metrics_history.append(metrics)

        # Keep only last 1000 entries to prevent excessive memory usage
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]

        # Save to file every 10 minutes
        if len(self.metrics_history) % 300 == 0:  # Every 300 updates at 2s interval
            history_file = self.logs_dir / f"metrics_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(history_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)

    def check_alerts(self, metrics: dict[str, Any]):
        """Check for alert conditions."""
        alerts = []

        # High CPU usage
        if metrics['system']['cpu_percent'] > 90:
            alerts.append(f"🔥 High CPU usage: {metrics['system']['cpu_percent']:.1f}%")

        # High memory usage
        if metrics['system']['memory']['percent'] > 90:
            alerts.append(f"🔥 High memory usage: {metrics['system']['memory']['percent']:.1f}%")

        # GPU memory near limit
        if 'error' not in metrics['gpu'] and metrics['gpu']['utilization_percent'] > 95:
            alerts.append(f"🔥 GPU memory critical: {metrics['gpu']['utilization_percent']:.1f}%")

        # Low disk space
        for disk_name, disk_info in metrics['system']['disk_usage'].items():
            if disk_info['percent_used'] > 95:
                alerts.append(f"💾 Low disk space on {disk_name}: {disk_info['free_gb']:.1f}GB free")

        # F: drive embedding issues
        if metrics['files']['f_drive_embeddings']['status'] != 'available':
            alerts.append("❌ F: drive embeddings not accessible")

        # Log new alerts
        for alert in alerts:
            if alert not in self.alerts:
                self.logger.warning(f"ALERT: {alert}")
                self.alerts.append(alert)

        # Clear resolved alerts
        self.alerts = [alert for alert in self.alerts if alert in alerts]

    def monitor_loop(self):
        """Main monitoring loop."""
        self.logger.info("🚀 Starting ImpressionCore B1 Live Monitor")
        self.start_time = datetime.now()

        if RICH_AVAILABLE:
            with Live(console=self.console, refresh_per_second=0.5) as live:
                while self.monitoring_active:
                    try:
                        # Collect metrics
                        metrics = self.get_system_metrics()

                        # Check for alerts
                        self.check_alerts(metrics)

                        # Save to history
                        self.save_metrics_history(metrics)

                        # Update display
                        dashboard = self.create_dashboard_layout(metrics)
                        live.update(dashboard)

                        # Wait for next update
                        time.sleep(self.update_interval)

                    except KeyboardInterrupt:
                        self.logger.info("👋 Monitor stopped by user")
                        break
                    except Exception as e:
                        self.logger.error(f"Monitor error: {e}")
                        time.sleep(self.update_interval)
        else:
            # Fallback to basic console output
            while self.monitoring_active:
                try:
                    metrics = self.get_system_metrics()
                    self.check_alerts(metrics)
                    self.save_metrics_history(metrics)

                    # Basic console output
                    print(f"\n🤖 ImpressionCore B1 Monitor - {datetime.now().strftime('%H:%M:%S')}")
                    print(f"CPU: {metrics['system']['cpu_percent']:.1f}% | RAM: {metrics['system']['memory']['percent']:.1f}%")
                    if 'error' not in metrics['gpu']:
                        print(f"GPU: {metrics['gpu']['utilization_percent']:.1f}% VRAM")
                    print(f"Training: {'Active' if metrics['training']['active'] else 'Inactive'}")

                    time.sleep(self.update_interval)

                except KeyboardInterrupt:
                    print("\n👋 Monitor stopped by user")
                    break
                except Exception as e:
                    print(f"Monitor error: {e}")
                    time.sleep(self.update_interval)

    def start_monitoring(self):  # noqa: F811
        """Start the monitoring system."""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

        print("🚀 ImpressionCore B1 Live Monitor started!")
        print("🎯 Monitoring toward 10/10 quality goal on GTX 1050 Ti")
        print("🔒 Sacred Covenant compliance active")
        print("Press Ctrl+C to stop monitoring")

    def stop_monitoring(self):  # noqa: F811
        """Stop the monitoring system."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("🛑 Monitoring stopped")

    def get_summary_report(self) -> dict[str, Any]:
        """Generate a summary report of the monitoring session."""
        if not self.metrics_history:
            return {"error": "No metrics data available"}

        total_runtime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        # Calculate averages
        avg_cpu = sum(m['system']['cpu_percent'] for m in self.metrics_history) / len(self.metrics_history)
        avg_memory = sum(m['system']['memory']['percent'] for m in self.metrics_history) / len(self.metrics_history)

        gpu_metrics = [m for m in self.metrics_history if 'error' not in m['gpu']]
        avg_gpu = sum(m['gpu']['utilization_percent'] for m in gpu_metrics) / len(gpu_metrics) if gpu_metrics else 0

        return {
            'session_start': self.start_time.isoformat() if self.start_time else None,
            'total_runtime_seconds': total_runtime,
            'total_updates': len(self.metrics_history),
            'averages': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory,
                'gpu_percent': avg_gpu
            },
            'alerts_count': len(set(self.alerts)),
            'training_detected': any(m['training']['active'] for m in self.metrics_history)
        }

def main():
    """Main function to run the live monitor."""
    monitor = ImpressionCoreLiveMonitor()

    try:
        monitor.start_monitoring()

        # Keep main thread alive
        while monitor.monitoring_active:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down monitor...")
    finally:
        monitor.stop_monitoring()

        # Show summary
        summary = monitor.get_summary_report()
        if 'error' not in summary:
            print("\n📊 Monitoring Session Summary:")
            print(f"   Runtime: {summary['total_runtime_seconds']:.0f} seconds")
            print(f"   Updates: {summary['total_updates']}")
            print(f"   Avg CPU: {summary['averages']['cpu_percent']:.1f}%")
            print(f"   Avg RAM: {summary['averages']['memory_percent']:.1f}%")
            print(f"   Avg GPU: {summary['averages']['gpu_percent']:.1f}%")
            print(f"   Training Detected: {summary['training_detected']}")
            print(f"   Total Alerts: {summary['alerts_count']}")

if __name__ == "__main__":
    main()
