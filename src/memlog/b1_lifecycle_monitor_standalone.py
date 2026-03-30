#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** System Generated
**Tags:** #cuda #deployment #gpu_optimization #memory_management #python #pytorch #source_code #src/memlog\b1_lifecycle_monitor_standalone.py #testing
**Category:** System Logs
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** System Generated
# Tags:** #cuda #deployment #gpu_optimization #memory_management #python #pytorch #source_code #src\\memlog\\b1_lifecycle_monitor_standalone.py #testing
# Category:** System Logs
# Status:** Active

"""
ImpressionCore-B1 Lifecycle Monitor - Standalone Version
Simplified lifecycle monitor for immediate deployment without dependencies
"""

import json
import logging
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('b1_lifecycle_monitor.log')
    ]
)

logger = logging.getLogger("B1LifecycleMonitor")

class B1LifecycleMonitorStandalone:
    """Standalone ImpressionCore-B1 lifecycle monitor."""

    def __init__(self):
        """Initialize standalone B1 lifecycle monitor."""
        self.model_name = "ImpressionCore-B1"
        self.version = "Perfection Edition"
        self.sacred_covenant_active = True
        self.monitoring_active = False
        self.monitoring_thread = None
        self.start_time = None

        # Initialize directories
        self.project_root = project_root
        self.memlog_dir = self.project_root / "src" / "memlog"
        self.logs_dir = self.memlog_dir / "logs"
        self.checkpoints_dir = self.project_root / "checkpoints"

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.checkpoints_dir.mkdir(exist_ok=True)

        # Check F: drive availability
        self.f_drive_available = os.path.exists("F:") and os.path.isdir("F:")

        logger.info(f"🚀 Sacred Covenant: {self.model_name} {self.version} Monitor initialized")
        logger.info(f"📂 Project Root: {self.project_root}")
        logger.info(f"💾 F: Drive Available: {self.f_drive_available}")

    def start_monitoring(self) -> bool:
        """Start continuous lifecycle monitoring."""
        try:
            if self.monitoring_active:
                logger.warning("🔄 Sacred Covenant: Monitoring already active")
                return True

            self.monitoring_active = True
            self.start_time = datetime.now()

            # Log monitoring start
            self._log_activity("lifecycle_monitoring_started", {
                "start_time": self.start_time.isoformat(),
                "f_drive_available": self.f_drive_available
            })

            # Start monitoring in background thread
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="B1-LifecycleMonitor"
            )
            self.monitoring_thread.start()

            logger.info(f"🛡️ Sacred Covenant: {self.model_name} lifecycle monitoring STARTED")
            return True

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Failed to start monitoring: {e}")
            return False

    def stop_monitoring(self) -> bool:
        """Stop lifecycle monitoring."""
        try:
            if not self.monitoring_active:
                logger.warning("⏹️ Sacred Covenant: Monitoring not active")
                return True

            self.monitoring_active = False

            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)

            # Log monitoring stop
            if self.start_time:
                duration = datetime.now() - self.start_time
                self._log_activity("lifecycle_monitoring_stopped", {
                    "duration_seconds": duration.total_seconds()
                })

            logger.info(f"⏹️ Sacred Covenant: {self.model_name} lifecycle monitoring STOPPED")
            return True

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Failed to stop monitoring: {e}")
            return False

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        logger.info("🔄 Sacred Covenant: Entering continuous monitoring loop")

        last_health_check = datetime.min
        last_checkpoint_check = datetime.min
        last_f_drive_check = datetime.min

        while self.monitoring_active:
            try:
                current_time = datetime.now()

                # Health check every 5 minutes
                if (current_time - last_health_check).seconds >= 300:
                    self._perform_health_check()
                    last_health_check = current_time

                # Checkpoint check every 15 minutes
                if (current_time - last_checkpoint_check).seconds >= 900:
                    self._check_checkpoints()
                    last_checkpoint_check = current_time

                # F: drive check every 2 minutes
                if (current_time - last_f_drive_check).seconds >= 120:
                    self._check_f_drive()
                    last_f_drive_check = current_time

                # Sleep for 30 seconds
                time.sleep(30)

            except Exception as e:
                logger.error(f"💥 Sacred Covenant VIOLATION: Monitoring loop error: {e}")
                time.sleep(60)  # Extended sleep on error

    def _perform_health_check(self) -> dict[str, Any]:
        """Perform system health check."""
        try:
            health_data = {
                "timestamp": datetime.now().isoformat(),
                "system_health": "CHECKING",
                "checks": {}
            }

            # Check disk space
            health_data["checks"]["disk_space"] = self._check_disk_space()

            # Check memory usage
            health_data["checks"]["memory"] = self._check_memory_usage()

            # Check directory integrity
            health_data["checks"]["directories"] = self._check_directories()

            # Determine overall health
            critical_issues = sum(1 for check in health_data["checks"].values()
                                if isinstance(check, dict) and check.get("status") == "CRITICAL")

            if critical_issues == 0:
                health_data["system_health"] = "HEALTHY"
            elif critical_issues <= 1:
                health_data["system_health"] = "WARNING"
            else:
                health_data["system_health"] = "CRITICAL"

            self._log_activity("health_check", health_data)

            if health_data["system_health"] != "HEALTHY":
                logger.warning(f"⚠️ Sacred Covenant: System health: {health_data['system_health']}")

            return health_data

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Health check failed: {e}")
            return {"system_health": "ERROR", "error": str(e)}

    def _check_disk_space(self) -> dict[str, Any]:
        """Check disk space on critical drives."""
        try:
            import shutil
            drives = ["C:", "D:"]
            if self.f_drive_available:
                drives.append("F:")

            disk_status = {"overall_status": "HEALTHY"}
            critical_drives = 0

            for drive in drives:
                try:
                    total, used, free = shutil.disk_usage(drive)
                    free_percent = (free / total) * 100

                    if free_percent < 5:
                        status = "CRITICAL"
                        critical_drives += 1
                    elif free_percent < 10:
                        status = "WARNING"
                    else:
                        status = "HEALTHY"

                    disk_status[drive] = {
                        "free_gb": round(free / (1024**3), 2),
                        "free_percent": round(free_percent, 2),
                        "status": status
                    }
                except Exception as e:
                    disk_status[drive] = {"status": "ERROR", "error": str(e)}
                    critical_drives += 1

            if critical_drives > 0:
                disk_status["overall_status"] = "CRITICAL" if critical_drives > 1 else "WARNING"

            return disk_status

        except Exception as e:
            return {"overall_status": "ERROR", "error": str(e)}

    def _check_memory_usage(self) -> dict[str, Any]:
        """Check system memory usage."""
        try:
            # Basic memory check using OS
            memory_status = {"status": "HEALTHY"}

            # Try to get GPU memory if available
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory
                    gpu_memory_used = torch.cuda.memory_allocated(0)
                    gpu_memory_percent = (gpu_memory_used / gpu_memory) * 100

                    memory_status.update({
                        "gpu_memory_percent": round(gpu_memory_percent, 2),
                        "gpu_memory_used_gb": round(gpu_memory_used / (1024**3), 2),
                        "gpu_memory_total_gb": round(gpu_memory / (1024**3), 2)
                    })

                    if gpu_memory_percent > 80:
                        memory_status["status"] = "WARNING"
            except ImportError:
                memory_status["gpu_status"] = "PyTorch not available"

            return memory_status

        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def _check_directories(self) -> dict[str, Any]:
        """Check integrity of critical directories."""
        try:
            critical_dirs = [
                self.memlog_dir,
                self.logs_dir,
                self.checkpoints_dir
            ]

            dir_status = {"overall_status": "HEALTHY", "directories": {}}
            issues = 0

            for dir_path in critical_dirs:
                dir_name = str(dir_path.relative_to(self.project_root))

                if dir_path.exists() and dir_path.is_dir():
                    # Check write permissions
                    test_file = dir_path / f"test_write_{int(time.time())}.tmp"
                    try:
                        test_file.write_text("test")
                        test_file.unlink()
                        dir_status["directories"][dir_name] = {"status": "HEALTHY"}
                    except Exception:
                        dir_status["directories"][dir_name] = {"status": "WARNING", "issue": "not_writable"}
                        issues += 1
                else:
                    # Create missing directory
                    try:
                        dir_path.mkdir(parents=True, exist_ok=True)
                        dir_status["directories"][dir_name] = {"status": "CREATED"}
                    except Exception:
                        dir_status["directories"][dir_name] = {"status": "CRITICAL", "issue": "cannot_create"}
                        issues += 1

            if issues > 0:
                dir_status["overall_status"] = "CRITICAL" if issues > 1 else "WARNING"

            return dir_status

        except Exception as e:
            return {"overall_status": "ERROR", "error": str(e)}

    def _check_checkpoints(self) -> None:
        """Check for new model checkpoints."""
        try:
            checkpoint_files = []
            checkpoint_extensions = ['.pt', '.pth', '.safetensors', '.ckpt']

            # Search for checkpoints in multiple locations
            search_dirs = [
                self.checkpoints_dir,
                self.project_root / "models",
                self.project_root / "src" / "models"
            ]

            for search_dir in search_dirs:
                if search_dir.exists():
                    for file_path in search_dir.rglob("*"):
                        if any(file_path.suffix.lower() == ext for ext in checkpoint_extensions):
                            file_stats = file_path.stat()
                            checkpoint_files.append({
                                "path": str(file_path),
                                "name": file_path.name,
                                "size_mb": round(file_stats.st_size / (1024**2), 2),
                                "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                            })

            if checkpoint_files:
                self._log_activity("checkpoint_scan", {
                    "checkpoints_found": len(checkpoint_files),
                    "checkpoints": checkpoint_files[-5:]  # Log only latest 5
                })
                logger.info(f"🔍 Sacred Covenant: Found {len(checkpoint_files)} checkpoint files")

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Checkpoint scan failed: {e}")

    def _check_f_drive(self) -> None:
        """Monitor F: drive status."""
        try:
            current_f_drive_status = os.path.exists("F:") and os.path.isdir("F:")

            if current_f_drive_status != self.f_drive_available:
                status_change = {
                    "previous_status": self.f_drive_available,
                    "current_status": current_f_drive_status,
                    "change_time": datetime.now().isoformat()
                }

                self._log_activity("f_drive_status_change", status_change)

                if current_f_drive_status:
                    logger.info("✅ Sacred Covenant: F: drive is now available")
                else:
                    logger.warning("⚠️ Sacred Covenant: F: drive is no longer available")

                self.f_drive_available = current_f_drive_status

            # Check F: drive space if available
            if current_f_drive_status:
                import shutil
                total, used, free = shutil.disk_usage("F:")
                free_gb = free / (1024**3)

                if free_gb < 10:
                    logger.warning(f"⚠️ Sacred Covenant: F: drive low on space: {free_gb:.1f} GB free")

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: F: drive monitoring failed: {e}")

    def _log_activity(self, activity_type: str, data: dict[str, Any]) -> None:
        """Log activity to file."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "activity_type": activity_type,
                "model": self.model_name,
                "version": self.version,
                "data": data
            }

            # Save to daily log file
            log_filename = f"b1_lifecycle_{datetime.now().strftime('%Y%m%d')}.json"
            log_path = self.logs_dir / log_filename

            # Append to log file
            if log_path.exists():
                with open(log_path) as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(log_entry)

            with open(log_path, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Activity logging failed: {e}")

    def get_status(self) -> dict[str, Any]:
        """Get current monitoring status."""
        status = {
            "model_name": self.model_name,
            "version": self.version,
            "monitoring_active": self.monitoring_active,
            "sacred_covenant_active": self.sacred_covenant_active,
            "f_drive_available": self.f_drive_available,
            "project_root": str(self.project_root)
        }

        if self.start_time:
            uptime = datetime.now() - self.start_time
            status["uptime_seconds"] = uptime.total_seconds()
            status["uptime_formatted"] = str(uptime)

        return status

    def force_health_check(self) -> dict[str, Any]:
        """Force immediate comprehensive health check."""
        logger.info("🔍 Sacred Covenant: Forcing comprehensive health check")
        return self._perform_health_check()


def main():
    """Main function to run the lifecycle monitor."""
    monitor = B1LifecycleMonitorStandalone()

    try:
        # Start monitoring
        if monitor.start_monitoring():
            logger.info("🚀 Sacred Covenant: B1 Lifecycle Monitor running")
            logger.info("📊 Monitor Status:")
            status = monitor.get_status()
            for key, value in status.items():
                logger.info(f"   {key}: {value}")

            # Keep running until interrupted
            while monitor.monitoring_active:
                time.sleep(10)

        else:
            logger.error("💥 Sacred Covenant VIOLATION: Failed to start monitoring")

    except KeyboardInterrupt:
        logger.info("🛑 Sacred Covenant: Shutdown requested by user")
    except Exception as e:
        logger.error(f"💥 Sacred Covenant VIOLATION: Monitor crashed: {e}")
    finally:
        monitor.stop_monitoring()
        logger.info("👋 Sacred Covenant: B1 Lifecycle Monitor shutdown complete")


if __name__ == "__main__":
    main()
