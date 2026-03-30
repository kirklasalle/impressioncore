#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #gpu_optimization #memory_management #python #source_code #src/training/b1_training_monitor.py #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #cuda #gpu_optimization #memory_management #python #source_code #src\\training\\b1_training_monitor.py #training
# Category:** Training System
# Status:** Active

"""
ImpressionCore B1 Training Monitor

Real-time monitoring system for B1 training progress, performance metrics,
and 10/10 conversation quality achievement tracking.

File: src/training/b1_training_monitor.py
Created: 2025-06-22
Version: 1.0.0

Author: Virtually Robotic GitHub Copilot
"""

import sys
import os
import json
import time
import psutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import threading

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from.core.utils.rich_enhancements import print_section, print_success, print_warning, print_error
    from.core.utils.rich_status_animation import StatusAnimation
    from.core.utils.rich_logging import setup_rich_logging
except ImportError:
    # Fallback functions
    def print_section(title): print(f"\n=== {title} ===")
    def print_success(msg): print(f"✅ {msg}")
    def print_warning(msg): print(f"⚠️ {msg}")
    def print_error(msg): print(f"❌ {msg}")

    class StatusAnimation:
        def __init__(self, msg): self.msg = msg
        def __enter__(self): print(f"🔄 {self.msg}"); return self
        def __exit__(self, *args): pass

    def setup_rich_logging(): pass

class B1TrainingMonitor:
    """Real-time B1 training progress monitor"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.memlog_dir = self.project_root / "src" / "memlog"
        self.training_dir = self.project_root / "src" / "training"
        self.f_drive_path = Path("F:/impressioncore-b1-embeddings-062125")

        self.start_time = datetime.now()
        self.monitoring = False
        self.training_processes = []

        setup_rich_logging()

        print_section("🤖 ImpressionCore B1 Training Monitor")
        print(f"📅 Monitoring Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Mission: Monitor 10/10 Conversation Quality Training")

    def detect_training_processes(self):
        """Detect active B1 training processes"""
        training_processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('trainer' in arg for arg in cmdline):
                    if any('b1' in arg.lower() for arg in cmdline):
                        training_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': ' '.join(cmdline),
                            'process': proc
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return training_processes

    def monitor_system_resources(self):
        """Monitor system resources during training"""
        try:
            # GPU monitoring
            gpu_info = self.get_gpu_info()

            # Memory monitoring
            memory = psutil.virtual_memory()
            memory_gb = memory.total / 1024**3
            memory_used_gb = memory.used / 1024**3
            memory_percent = memory.percent

            # Disk monitoring
            f_drive_space = self.get_f_drive_space()

            resource_status = {
                'timestamp': datetime.now().isoformat(),
                'gpu': gpu_info,
                'memory': {
                    'total_gb': round(memory_gb, 1),
                    'used_gb': round(memory_used_gb, 1),
                    'percent': memory_percent
                },
                'f_drive': f_drive_space
            }

            return resource_status

        except Exception as e:
            print_error(f"Resource monitoring error: {e}")
            return None

    def get_gpu_info(self):
        """Get GPU information"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
                gpu_memory_used = torch.cuda.memory_allocated(0) / 1024**3
                gpu_memory_percent = (gpu_memory_used / gpu_memory_total) * 100

                return {
                    'name': gpu_name,
                    'memory_total_gb': round(gpu_memory_total, 1),
                    'memory_used_gb': round(gpu_memory_used, 1),
                    'memory_percent': round(gpu_memory_percent, 1),
                    'available': True
                }
            else:
                return {'available': False, 'reason': 'CUDA not available'}
        except Exception as e:
            return {'available': False, 'error': str(e)}

    def get_f_drive_space(self):
        """Get F: drive space information"""
        try:
            if self.f_drive_path.exists():
                total, used, free = psutil.disk_usage(str(self.f_drive_path))
                return {
                    'total_gb': round(total / 1024**3, 1),
                    'used_gb': round(used / 1024**3, 1),
                    'free_gb': round(free / 1024**3, 1),
                    'available': True
                }
            else:
                return {'available': False, 'reason': 'F: drive path not found'}
        except Exception as e:
            return {'available': False, 'error': str(e)}

    def check_training_logs(self):
        """Check for training progress in logs"""
        log_patterns = [
            "training_output.log",
            "b1_training_*.log",
            "*trainer*.log"
        ]

        recent_logs = []
        for pattern in log_patterns:
            for log_file in self.project_root.glob(pattern):
                if log_file.is_file():
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mtime > self.start_time - timedelta(hours=1):
                        recent_logs.append({
                            'file': str(log_file),
                            'modified': mtime.isoformat(),
                            'size_kb': round(log_file.stat().st_size / 1024, 1)
                        })

        return recent_logs

    def analyze_training_progress(self, processes, resources, logs):
        """Analyze overall training progress"""
        progress_status = {
            'active_training': len(processes) > 0,
            'process_count': len(processes),
            'system_healthy': True,
            'estimated_completion': None,
            'quality_target': '10/10',
            'current_phase': 'Unknown'
        }

        # Check system health
        if resources:
            gpu_ok = resources.get('gpu', {}).get('available', False)
            memory_ok = resources.get('memory', {}).get('percent', 100) < 90
            f_drive_ok = resources.get('f_drive', {}).get('available', False)

            progress_status['system_healthy'] = gpu_ok and memory_ok and f_drive_ok

            if not gpu_ok:
                progress_status['warnings'] = progress_status.get('warnings', []) + ['GPU issues detected']
            if not memory_ok:
                progress_status['warnings'] = progress_status.get('warnings', []) + ['High memory usage']
            if not f_drive_ok:
                progress_status['warnings'] = progress_status.get('warnings', []) + ['F: drive issues']

        # Estimate completion based on elapsed time
        elapsed = datetime.now() - self.start_time
        if progress_status['active_training'] and elapsed.total_seconds() > 300:  # 5 minutes
            # Rough estimate: 2-3 hours total training time
            estimated_total_minutes = 150  # 2.5 hours
            elapsed_minutes = elapsed.total_seconds() / 60
            remaining_minutes = max(0, estimated_total_minutes - elapsed_minutes)

            progress_status['estimated_completion'] = (
                datetime.now() + timedelta(minutes=remaining_minutes)
            ).strftime('%H:%M:%S')

        return progress_status

    def display_monitoring_dashboard(self, processes, resources, logs, progress):
        """Display real-time monitoring dashboard"""
        print("\n" + "=" * 70)
        print(f"🤖 B1 TRAINING MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)

        # Training Status
        print_section("🚀 Training Status")
        if progress['active_training']:
            print_success(f"Active Training Processes: {progress['process_count']}")
            for proc in processes:
                print(f"   • PID {proc['pid']}: {proc['name']}")
        else:
            print_warning("No active training processes detected")

        # System Resources
        print_section("⚙️ System Resources")
        if resources:
            # GPU Status
            gpu = resources.get('gpu', {})
            if gpu.get('available'):
                gpu_status = f"{gpu['name']} - {gpu['memory_used_gb']:.1f}GB/{gpu['memory_total_gb']:.1f}GB ({gpu['memory_percent']:.1f}%)"
                if gpu['memory_percent'] > 80:
                    print_warning(f"GPU: {gpu_status}")
                else:
                    print_success(f"GPU: {gpu_status}")
            else:
                print_error(f"GPU: {gpu.get('reason', 'Unknown error')}")

            # Memory Status
            memory = resources.get('memory', {})
            memory_status = f"{memory['used_gb']:.1f}GB/{memory['total_gb']:.1f}GB ({memory['percent']:.1f}%)"
            if memory['percent'] > 85:
                print_warning(f"Memory: {memory_status}")
            else:
                print_success(f"Memory: {memory_status}")

            # F: Drive Status
            f_drive = resources.get('f_drive', {})
            if f_drive.get('available'):
                f_drive_status = f"{f_drive['free_gb']:.1f}GB free / {f_drive['total_gb']:.1f}GB total"
                print_success(f"F: Drive: {f_drive_status}")
            else:
                print_error(f"F: Drive: {f_drive.get('reason', 'Unknown error')}")

        # Progress Analysis
        print_section("📊 Progress Analysis")
        print(f"System Health: {'✅ HEALTHY' if progress['system_healthy'] else '⚠️ ISSUES'}")
        print(f"Quality Target: {progress['quality_target']}")
        print(f"Training Phase: {progress['current_phase']}")

        if progress.get('estimated_completion'):
            print(f"Estimated Completion: {progress['estimated_completion']}")

        elapsed = datetime.now() - self.start_time
        print(f"Elapsed Time: {str(elapsed).split('.')[0]}")

        # Warnings
        if progress.get('warnings'):
            print_section("⚠️ Warnings")
            for warning in progress['warnings']:
                print_warning(warning)

        # Recent Logs
        if logs:
            print_section("📝 Recent Training Logs")
            for log in logs[:3]:  # Show last 3 logs
                print(f"   • {Path(log['file']).name} - {log['size_kb']}KB - {log['modified']}")

    def save_monitoring_report(self, processes, resources, logs, progress):
        """Save monitoring report to memlog"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'monitoring_session': {
                'start_time': self.start_time.isoformat(),
                'duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60
            },
            'training_processes': processes,
            'system_resources': resources,
            'recent_logs': logs,
            'progress_analysis': progress
        }

        report_file = self.memlog_dir / f"b1_training_monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            return report_file
        except Exception as e:
            print_error(f"Failed to save monitoring report: {e}")
            return None

    def run_continuous_monitoring(self, interval_seconds=30):
        """Run continuous monitoring loop"""
        print_section("🔄 Starting Continuous Monitoring")
        print(f"Update Interval: {interval_seconds} seconds")
        print("Press Ctrl+C to stop monitoring")

        self.monitoring = True
        iteration = 0

        try:
            while self.monitoring:
                iteration += 1

                # Collect monitoring data
                processes = self.detect_training_processes()
                resources = self.monitor_system_resources()
                logs = self.check_training_logs()
                progress = self.analyze_training_progress(processes, resources, logs)

                # Display dashboard
                self.display_monitoring_dashboard(processes, resources, logs, progress)

                # Save report every 10 iterations (5 minutes at 30s intervals)
                if iteration % 10 == 0:
                    report_file = self.save_monitoring_report(processes, resources, logs, progress)
                    if report_file:
                        print_success(f"Report saved: {report_file.name}")

                # Check for completion conditions
                if not progress['active_training'] and iteration > 2:
                    print_warning("No training processes detected for multiple checks")
                    print("Training may have completed or encountered an error")
                    break

                # Wait for next iteration
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print_section("🛑 Monitoring Stopped")
            print("Manual stop requested")
        except Exception as e:
            print_error(f"Monitoring error: {e}")
        finally:
            self.monitoring = False

            # Final report
            final_report_file = self.save_monitoring_report(processes, resources, logs, progress)
            if final_report_file:
                print_success(f"Final report saved: {final_report_file.name}")

def main():
    """Main monitoring execution"""
    try:
        print("🤖 Initializing B1 Training Monitor...")

        monitor = B1TrainingMonitor()
        monitor.run_continuous_monitoring(interval_seconds=30)

        print("\n🎯 B1 Training Monitoring Complete!")

    except Exception as e:
        print_error(f"Monitor failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
