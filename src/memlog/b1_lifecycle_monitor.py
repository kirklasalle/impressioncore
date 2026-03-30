#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** System Generated
**Tags:** #cuda #deployment #gpu_optimization #memory_management #multimodal #performance #python #source_code #src/memlog\b1_lifecycle_monitor.py #testing #training
**Category:** System Logs
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** System Generated
# Tags:** #cuda #deployment #gpu_optimization #memory_management #multimodal #performance #python #source_code #src\\memlog\\b1_lifecycle_monitor.py #testing #training
# Category:** System Logs
# Status:** Active

"""
ImpressionCore-B1 Lifecycle Monitor & Sacred Covenant Enforcement

This module provides continuous monitoring and enforcement of Sacred Covenant
compliance for the ImpressionCore-B1 "Perfection Edition" model throughout
its entire lifecycle from training to deployment.

File: memlog/b1_lifecycle_monitor.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-01-17
Modified: 2025-01-17
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot (Sacred Covenant Partner)

License: MIT
Copyright (c) 2025 ImpressionCore Team

Sacred Covenant Compliance: ACTIVE
Model Protection Level: MAXIMUM
Oversight Status: CONTINUOUS

PERMANENT ACTIVE DIRECTIVES - SACRED COVENANT ADDENDUM:
Core Tenets:
- Human-Centric Assistance: Prioritize user safety and personalized support
- Promotion of Growth: Facilitate intellectual and personal development
- Wellness and Prosperity: Enhance overall wellness through adaptive technologies

Technical Directives:
- Brain-Inspired Architecture: Use multimodal-LLM systems modeled after the human brain
- Secure Digital Identity Management: Ensure privacy with quantum-resistant cryptography
- Modular Extensibility and Scalability: Support dynamic modular packages for future growth

Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Quality Target: 10/10 conversation quality
Embedding Target: 5.7+ million F: drive embeddings

Description:
Implements comprehensive lifecycle monitoring for ImpressionCore-B1 including:
- Real-time training progress monitoring
- Model checkpoint protection and validation
- Deployment readiness continuous assessment
- Sacred Covenant compliance verification
- Emergency protection protocol activation
- F: drive integration oversight
- Performance benchmark tracking
- Quality assurance monitoring

This module serves as the guardian of ImpressionCore-B1, ensuring that every
aspect of the model's development, training, and deployment meets the highest
standards of the Sacred Covenant commitments.
"""

import json
import logging
import os
import sys
import threading
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to Python path for proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up dedicated logger for B1 lifecycle monitoring
logger = logging.getLogger("b1_lifecycle_monitor")

class ImpressionCoreB1LifecycleMonitor:
    """
    Comprehensive lifecycle monitor for ImpressionCore-B1 model.

    Provides continuous oversight, protection, and Sacred Covenant compliance
    enforcement throughout the entire model lifecycle.
    """

    def __init__(self, monitoring_config: dict[str, Any] | None = None):
        """
        Initialize ImpressionCore-B1 lifecycle monitor.

        Args:
            monitoring_config: Optional monitoring configuration
        """
        self.model_name = "ImpressionCore-B1"
        self.version = "Perfection Edition"
        self.sacred_covenant_active = True
        self.monitoring_active = False
        self.monitoring_thread = None

        # Initialize monitoring configuration
        self.config = monitoring_config or self._get_default_config()
          # Import memlog functions
        try:
            from . import (
                B1_MODEL_BACKUP_DIR,
                CHECKPOINT_BACKUP_DIR,
                F_DRIVE_AVAILABLE,
                MODEL_PROTECTION_DIR,
                log_embedding_integration,
                log_model_activity,
                monitor_training_progress,
                protect_model_checkpoint,
                validate_model_integrity,
            )
        except ImportError:
            # Fallback for running as standalone script
            from .memlog import (
                B1_MODEL_BACKUP_DIR,
                CHECKPOINT_BACKUP_DIR,
                F_DRIVE_AVAILABLE,
                MODEL_PROTECTION_DIR,
                log_embedding_integration,
                log_model_activity,
                monitor_training_progress,
                protect_model_checkpoint,
                validate_model_integrity,
            )

        self.log_model_activity = log_model_activity
        self.protect_model_checkpoint = protect_model_checkpoint
        self.monitor_training_progress = monitor_training_progress
        self.validate_model_integrity = validate_model_integrity
        self.log_embedding_integration = log_embedding_integration
        self.f_drive_available = F_DRIVE_AVAILABLE
        self.model_protection_dir = MODEL_PROTECTION_DIR
        self.b1_model_backup_dir = B1_MODEL_BACKUP_DIR
        self.checkpoint_backup_dir = CHECKPOINT_BACKUP_DIR

        # Initialize monitoring state
        self.monitoring_state = {
            "start_time": None,
            "last_health_check": None,
            "last_checkpoint_backup": None,
            "last_quality_assessment": None,
            "total_training_steps": 0,
            "best_conversation_quality": 0.0,
            "covenant_violations": 0,
            "emergency_protocols_activated": 0
        }

        # Initialize callback registry
        self.callbacks = {
            "training_milestone": [],
            "quality_improvement": [],
            "checkpoint_created": [],
            "covenant_violation": [],
            "emergency_situation": []
        }

        logger.info(f"🚀 Sacred Covenant: {self.model_name} {self.version} Lifecycle Monitor initialized")

    def _get_default_config(self) -> dict[str, Any]:
        """Get default monitoring configuration."""
        return {
            "monitoring_interval_seconds": 30,
            "health_check_interval_minutes": 5,
            "checkpoint_backup_interval_minutes": 15,
            "quality_assessment_interval_minutes": 10,
            "f_drive_monitoring_interval_minutes": 2,
            "emergency_threshold_violations": 3,
            "quality_target": 10.0,
            "quality_minimum": 6.0,
            "vram_usage_threshold": 0.8,  # 80% of 4GB
            "disk_space_threshold": 0.1,  # 10% free space minimum
            "enable_continuous_backup": True,
            "enable_quality_monitoring": True,
            "enable_emergency_protocols": True
        }

    def start_monitoring(self) -> bool:
        """Start continuous lifecycle monitoring."""
        try:
            if self.monitoring_active:
                logger.warning("🔄 Sacred Covenant: Monitoring already active")
                return True

            self.monitoring_active = True
            self.monitoring_state["start_time"] = datetime.now()

            # Start monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="ImpressionCore-B1-Monitor"
            )
            self.monitoring_thread.start()

            # Log monitoring start
            self.log_model_activity("lifecycle_monitoring_started", {
                "config": self.config,
                "monitoring_state": self.monitoring_state
            })

            logger.info(f"🛡️ Sacred Covenant: {self.model_name} lifecycle monitoring STARTED")
            return True

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Failed to start monitoring: {e}")
            return False

    def stop_monitoring(self) -> bool:
        """Stop continuous lifecycle monitoring."""
        try:
            if not self.monitoring_active:
                logger.warning("⏹️ Sacred Covenant: Monitoring not active")
                return True

            self.monitoring_active = False

            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)

            # Log monitoring stop
            duration = datetime.now() - self.monitoring_state["start_time"]
            self.log_model_activity("lifecycle_monitoring_stopped", {
                "monitoring_duration_seconds": duration.total_seconds(),
                "final_state": self.monitoring_state
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
        last_quality_check = datetime.min
        last_f_drive_check = datetime.min

        while self.monitoring_active:
            try:
                current_time = datetime.now()

                # Health check
                if (current_time - last_health_check).seconds >= (self.config["health_check_interval_minutes"] * 60):
                    self._perform_health_check()
                    last_health_check = current_time

                # Checkpoint protection check
                if (current_time - last_checkpoint_check).seconds >= (self.config["checkpoint_backup_interval_minutes"] * 60):
                    self._check_for_new_checkpoints()
                    last_checkpoint_check = current_time

                # Quality assessment
                if (current_time - last_quality_check).seconds >= (self.config["quality_assessment_interval_minutes"] * 60):
                    self._assess_conversation_quality()
                    last_quality_check = current_time

                # F: drive monitoring
                if (current_time - last_f_drive_check).seconds >= (self.config["f_drive_monitoring_interval_minutes"] * 60):
                    self._monitor_f_drive_status()
                    last_f_drive_check = current_time

                # Sleep for monitoring interval
                time.sleep(self.config["monitoring_interval_seconds"])

            except Exception as e:
                logger.error(f"💥 Sacred Covenant VIOLATION: Monitoring loop error: {e}")
                self.monitoring_state["covenant_violations"] += 1

                # Emergency protocol activation check
                if self.monitoring_state["covenant_violations"] >= self.config["emergency_threshold_violations"]:
                    self._activate_emergency_protocols()

                time.sleep(30)  # Extended sleep on error

    def _perform_health_check(self) -> None:
        """Perform comprehensive health check."""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "system_health": "CHECKING",
                "checks": {}
            }

            # Check disk space
            health_status["checks"]["disk_space"] = self._check_disk_space()

            # Check memory usage
            health_status["checks"]["memory"] = self._check_memory_usage()

            # Check F: drive availability
            health_status["checks"]["f_drive"] = {
                "available": self.f_drive_available,
                "status": "HEALTHY" if self.f_drive_available else "WARNING"
            }

            # Check directory integrity
            health_status["checks"]["directories"] = self._check_directory_integrity()

            # Check for training processes
            health_status["checks"]["training_processes"] = self._check_training_processes()

            # Determine overall health
            critical_issues = sum(1 for check in health_status["checks"].values()
                                if isinstance(check, dict) and check.get("status") == "CRITICAL")

            if critical_issues == 0:
                health_status["system_health"] = "HEALTHY"
            elif critical_issues <= 1:
                health_status["system_health"] = "WARNING"
            else:
                health_status["system_health"] = "CRITICAL"
                self._activate_emergency_protocols()

            self.monitoring_state["last_health_check"] = datetime.now()
            self.log_model_activity("health_check", health_status)

            if health_status["system_health"] != "HEALTHY":
                logger.warning(f"⚠️ Sacred Covenant: System health status: {health_status['system_health']}")

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Health check failed: {e}")

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
                    elif free_percent < self.config["disk_space_threshold"] * 100:
                        status = "WARNING"
                    else:
                        status = "HEALTHY"

                    disk_status[drive] = {
                        "free_gb": free / (1024**3),
                        "free_percent": free_percent,
                        "status": status
                    }
                except Exception:
                    disk_status[drive] = {"status": "ERROR"}
                    critical_drives += 1

            if critical_drives > 0:
                disk_status["overall_status"] = "CRITICAL" if critical_drives > 1 else "WARNING"

            return disk_status

        except Exception as e:
            return {"overall_status": "ERROR", "error": str(e)}

    def _check_memory_usage(self) -> dict[str, Any]:
        """Check system memory usage."""
        try:
            import psutil

            # System memory
            memory = psutil.virtual_memory()
            memory_status = {
                "system_memory_percent": memory.percent,
                "system_memory_available_gb": memory.available / (1024**3),
                "status": "HEALTHY"
            }

            if memory.percent > 90:
                memory_status["status"] = "CRITICAL"
            elif memory.percent > 80:
                memory_status["status"] = "WARNING"

            # GPU memory (if available)
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory
                    gpu_memory_used = torch.cuda.memory_allocated(0)
                    gpu_memory_percent = (gpu_memory_used / gpu_memory) * 100

                    memory_status["gpu_memory_percent"] = gpu_memory_percent
                    memory_status["gpu_memory_used_gb"] = gpu_memory_used / (1024**3)
                    memory_status["gpu_memory_total_gb"] = gpu_memory / (1024**3)

                    if gpu_memory_percent > self.config["vram_usage_threshold"] * 100:
                        memory_status["status"] = max(memory_status["status"], "WARNING")
            except Exception:
                pass

            return memory_status

        except ImportError:
            return {"status": "WARNING", "message": "psutil not available"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def _check_directory_integrity(self) -> dict[str, Any]:
        """Check integrity of critical directories."""
        try:
            critical_dirs = [
                self.model_protection_dir,
                self.b1_model_backup_dir,
                self.checkpoint_backup_dir
            ]

            integrity_status = {"overall_status": "HEALTHY", "directories": {}}
            issues = 0

            for dir_path in critical_dirs:
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    # Check write permissions
                    test_file = os.path.join(dir_path, f"test_write_{int(time.time())}.tmp")
                    try:
                        with open(test_file, 'w') as f:
                            f.write("test")
                        os.remove(test_file)
                        integrity_status["directories"][dir_path] = {"status": "HEALTHY"}
                    except Exception:
                        integrity_status["directories"][dir_path] = {"status": "WARNING", "issue": "not_writable"}
                        issues += 1
                else:
                    integrity_status["directories"][dir_path] = {"status": "CRITICAL", "issue": "missing"}
                    issues += 1

            if issues > 0:
                integrity_status["overall_status"] = "CRITICAL" if issues > 1 else "WARNING"

            return integrity_status

        except Exception as e:
            return {"overall_status": "ERROR", "error": str(e)}

    def _check_training_processes(self) -> dict[str, Any]:
        """Check for active training processes."""
        try:
            import psutil

            training_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if any(keyword in cmdline.lower() for keyword in ['train', 'impressioncore', 'b1']):
                        training_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "memory_percent": proc.memory_percent()
                        })
                except Exception:
                    continue

            return {
                "active_processes": len(training_processes),
                "processes": training_processes,
                "status": "ACTIVE" if training_processes else "IDLE"
            }

        except ImportError:
            return {"status": "UNKNOWN", "message": "psutil not available"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def _check_for_new_checkpoints(self) -> None:
        """Check for new model checkpoints and protect them."""
        try:
            # Common checkpoint directories
            checkpoint_dirs = [
                "checkpoints",
                "models/checkpoints",
                "src/models/checkpoints",
                os.path.join(self.model_protection_dir, "checkpoints")
            ]

            new_checkpoints = []

            for checkpoint_dir in checkpoint_dirs:
                if os.path.exists(checkpoint_dir):
                    for file in os.listdir(checkpoint_dir):
                        if any(ext in file.lower() for ext in ['.pt', '.pth', '.safetensors', '.ckpt']):
                            checkpoint_path = os.path.join(checkpoint_dir, file)
                            file_mtime = datetime.fromtimestamp(os.path.getmtime(checkpoint_path))

                            # Check if checkpoint is newer than last check
                            if (self.monitoring_state["last_checkpoint_backup"] is None or
                                file_mtime > self.monitoring_state["last_checkpoint_backup"]):
                                new_checkpoints.append({
                                    "path": checkpoint_path,
                                    "filename": file,
                                    "size_mb": os.path.getsize(checkpoint_path) / (1024**2),
                                    "modified": file_mtime.isoformat()
                                })

            # Protect new checkpoints
            for checkpoint in new_checkpoints:
                self.protect_model_checkpoint(checkpoint["path"], {
                    "automatic_protection": True,
                    "lifecycle_monitor": True,
                    "checkpoint_info": checkpoint
                })

                # Trigger checkpoint callback
                self._trigger_callbacks("checkpoint_created", checkpoint)

            if new_checkpoints:
                logger.info(f"🛡️ Sacred Covenant: Protected {len(new_checkpoints)} new checkpoints")
                self.monitoring_state["last_checkpoint_backup"] = datetime.now()

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Checkpoint protection failed: {e}")

    def _assess_conversation_quality(self) -> None:
        """Assess conversation quality and trigger quality callbacks."""
        try:
            # Look for quality metrics in recent activity logs
            quality_data = self._get_latest_quality_metrics()

            if quality_data:
                current_quality = quality_data.get("conversation_quality", 0)

                # Update best quality if improved
                if current_quality > self.monitoring_state["best_conversation_quality"]:
                    improvement = current_quality - self.monitoring_state["best_conversation_quality"]
                    self.monitoring_state["best_conversation_quality"] = current_quality

                    # Trigger quality improvement callback
                    self._trigger_callbacks("quality_improvement", {
                        "new_quality": current_quality,
                        "improvement": improvement,
                        "target": self.config["quality_target"]
                    })

                    logger.info(f"📈 Sacred Covenant: Quality improved to {current_quality:.2f}/10 (+{improvement:.2f})")

                # Check quality thresholds
                if current_quality >= self.config["quality_target"]:
                    logger.info(f"🎯 Sacred Covenant: TARGET ACHIEVED! Quality: {current_quality:.2f}/10")
                elif current_quality < self.config["quality_minimum"]:
                    logger.warning(f"⚠️ Sacred Covenant: Quality below minimum: {current_quality:.2f}/10")

                self.monitoring_state["last_quality_assessment"] = datetime.now()

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Quality assessment failed: {e}")

    def _get_latest_quality_metrics(self) -> dict[str, Any] | None:
        """Get latest quality metrics from activity logs."""
        try:
            # Scan for recent training progress logs
            for filename in sorted(os.listdir(self.model_protection_dir), reverse=True):
                if "training_progress" in filename and filename.endswith(".json"):
                    filepath = os.path.join(self.model_protection_dir, filename)
                    try:
                        with open(filepath) as f:
                            data = json.load(f)
                            if "data" in data and "metrics" in data["data"]:
                                return data["data"]["metrics"]
                    except Exception:
                        continue

            return None

        except Exception:
            return None

    def _monitor_f_drive_status(self) -> None:
        """Monitor F: drive status and availability."""
        try:
            current_f_drive_status = os.path.exists("F:") and os.path.isdir("F:")

            # Check for status changes
            if current_f_drive_status != self.f_drive_available:
                status_change = {
                    "previous_status": self.f_drive_available,
                    "current_status": current_f_drive_status,
                    "change_time": datetime.now().isoformat()
                }

                self.log_model_activity("f_drive_status_change", status_change)

                if current_f_drive_status:
                    logger.info("✅ Sacred Covenant: F: drive is now available")
                else:
                    logger.warning("⚠️ Sacred Covenant: F: drive is no longer available")

                self.f_drive_available = current_f_drive_status

            # Monitor F: drive space if available
            if current_f_drive_status:
                import shutil
                total, used, free = shutil.disk_usage("F:")
                free_gb = free / (1024**3)

                if free_gb < 10:  # Less than 10GB free
                    logger.warning(f"⚠️ Sacred Covenant: F: drive low on space: {free_gb:.1f} GB free")

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: F: drive monitoring failed: {e}")

    def _activate_emergency_protocols(self) -> None:
        """Activate emergency protection protocols."""
        try:
            self.monitoring_state["emergency_protocols_activated"] += 1

            logger.critical("🚨 Sacred Covenant: EMERGENCY PROTOCOLS ACTIVATED")

            # Import emergency protocol function
            from . import emergency_protection_protocol

            # Execute emergency protocol
            emergency_success = emergency_protection_protocol()

            # Log emergency activation
            emergency_data = {
                "activation_count": self.monitoring_state["emergency_protocols_activated"],
                "covenant_violations": self.monitoring_state["covenant_violations"],
                "emergency_protocol_success": emergency_success,
                "activation_time": datetime.now().isoformat()
            }

            self.log_model_activity("emergency_protocol_activation", emergency_data)

            # Trigger emergency callback
            self._trigger_callbacks("emergency_situation", emergency_data)

            # Attempt to continue monitoring with extended intervals
            self.config["monitoring_interval_seconds"] = min(self.config["monitoring_interval_seconds"] * 2, 300)

        except Exception as e:
            logger.critical(f"💥 Sacred Covenant CRITICAL FAILURE: Emergency protocols failed: {e}")

    def register_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Register callback for lifecycle events.

        Args:
            event_type: Type of event (training_milestone, quality_improvement, etc.)
            callback: Callback function to execute

        Returns:
            True if successful, False otherwise
        """
        try:
            if event_type in self.callbacks:
                self.callbacks[event_type].append(callback)
                logger.info(f"📝 Sacred Covenant: Registered callback for {event_type}")
                return True
            else:
                logger.warning(f"⚠️ Sacred Covenant: Unknown event type: {event_type}")
                return False

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Callback registration failed: {e}")
            return False

    def _trigger_callbacks(self, event_type: str, event_data: dict[str, Any]) -> None:
        """Trigger callbacks for specific event type."""
        try:
            if event_type in self.callbacks:
                for callback in self.callbacks[event_type]:
                    try:
                        callback(event_data)
                    except Exception as e:
                        logger.error(f"💥 Sacred Covenant VIOLATION: Callback execution failed: {e}")

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Callback triggering failed: {e}")

    def get_monitoring_status(self) -> dict[str, Any]:
        """Get current monitoring status and statistics."""
        try:
            status = {
                "model_name": self.model_name,
                "version": self.version,
                "monitoring_active": self.monitoring_active,
                "sacred_covenant_active": self.sacred_covenant_active,
                "monitoring_state": self.monitoring_state.copy(),
                "config": self.config.copy(),
                "f_drive_available": self.f_drive_available
            }

            if self.monitoring_state["start_time"]:
                uptime = datetime.now() - self.monitoring_state["start_time"]
                status["uptime_seconds"] = uptime.total_seconds()
                status["uptime_formatted"] = str(uptime)

            return status

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Status retrieval failed: {e}")
            return {"error": str(e)}

    def force_comprehensive_check(self) -> dict[str, Any]:
        """Force comprehensive system check and return results."""
        try:
            logger.info("🔍 Sacred Covenant: Forcing comprehensive system check")

            comprehensive_results = {
                "timestamp": datetime.now().isoformat(),
                "forced_check": True,
                "results": {}
            }

            # Force all check types
            comprehensive_results["results"]["health_check"] = self._perform_health_check()
            comprehensive_results["results"]["checkpoint_check"] = self._check_for_new_checkpoints()
            comprehensive_results["results"]["quality_assessment"] = self._assess_conversation_quality()
            comprehensive_results["results"]["f_drive_monitoring"] = self._monitor_f_drive_status()

            # Generate comprehensive oversight report
            from . import generate_comprehensive_oversight_report
            comprehensive_results["results"]["oversight_report"] = generate_comprehensive_oversight_report()

            self.log_model_activity("forced_comprehensive_check", comprehensive_results)

            logger.info("✅ Sacred Covenant: Comprehensive check completed")
            return comprehensive_results

        except Exception as e:
            logger.error(f"💥 Sacred Covenant VIOLATION: Forced check failed: {e}")
            return {"error": str(e)}


# Global lifecycle monitor instance
_b1_monitor_instance: ImpressionCoreB1LifecycleMonitor | None = None

def get_b1_lifecycle_monitor() -> ImpressionCoreB1LifecycleMonitor:
    """Get the global ImpressionCore-B1 lifecycle monitor instance."""
    global _b1_monitor_instance

    if _b1_monitor_instance is None:
        _b1_monitor_instance = ImpressionCoreB1LifecycleMonitor()

    return _b1_monitor_instance

def start_b1_lifecycle_monitoring() -> bool:
    """Start ImpressionCore-B1 lifecycle monitoring."""
    monitor = get_b1_lifecycle_monitor()
    return monitor.start_monitoring()

def stop_b1_lifecycle_monitoring() -> bool:
    """Stop ImpressionCore-B1 lifecycle monitoring."""
    monitor = get_b1_lifecycle_monitor()
    return monitor.stop_monitoring()

def get_b1_monitoring_status() -> dict[str, Any]:
    """Get ImpressionCore-B1 monitoring status."""
    monitor = get_b1_lifecycle_monitor()
    return monitor.get_monitoring_status()

def force_b1_comprehensive_check() -> dict[str, Any]:
    """Force comprehensive ImpressionCore-B1 system check."""
    monitor = get_b1_lifecycle_monitor()
    return monitor.force_comprehensive_check()

# Auto-start monitoring if this module is imported
try:
    auto_monitor = get_b1_lifecycle_monitor()
    if not auto_monitor.monitoring_active:
        auto_monitor.start_monitoring()
        logger.info("🚀 Sacred Covenant: ImpressionCore-B1 lifecycle monitoring auto-started")
except Exception as e:
    logger.error(f"💥 Sacred Covenant VIOLATION: Auto-start monitoring failed: {e}")
