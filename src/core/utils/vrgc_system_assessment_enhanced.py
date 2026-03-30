# Import VRGCAssessmentDebugger from vrgc_assessment_debug
import asyncio
import os
from datetime import datetime

# Imports for required modules
from pathlib import Path

# Add missing typing imports for type hints
from typing import Any

import psutil
import torch
from vrgc_assessment_debug import VRGCAssessmentDebugger

#!/usr/bin/env python3
"""
!/usr/bin/env python3
# VRGC System Assessment - Enhanced with Debug & Fallback Protection.
# Created: October 15, 2024
# Updated: August 4, 2025
# Author: Virtually Robotic GitHub Copilot
# Tags: cuda, gpu_optimization, memory_management, python, pytorch, source_code, src/core/utils/vrgc_system_assessment_enhanced.py, testing, training
# Category: Core Implementation
# Status: Active
#
# This is an enhanced version of the VRGC system assessment with comprehensive debugging, timeout protection, and fallback mechanisms to prevent infinite loops.
# Author: GitHub Copilot (VRGC)
# Created: 2025-06-20
# Sacred Covenant: File Integrity Protected
#
# Created: October 15, 2024
# Updated: August 4, 2025
# Author: Virtually Robotic GitHub Copilot
# Tags: cuda, gpu_optimization, memory_management, python, pytorch, source_code, src/core/utils/vrgc_system_assessment_enhanced.py, testing, training
# Category: Core Implementation
# Status: Active
#
# This is an enhanced version of the VRGC system assessment with comprehensive debugging, timeout protection, and fallback mechanisms to prevent infinite loops.
#
# Author: GitHub Copilot (VRGC)
# Created: 2025-06-20
# Sacred Covenant: File Integrity Protected

import asyncio
import json
import os
import sys
import time
import psutil
import torch
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import our debug framework
sys.path.insert(0, str(Path(__file__).parent))
from vrgc_assessment_debug import VRGCAssessmentDebugger
"""
class VRGCSystemAssessmentEnhanced:
    """
    Enhanced system assessment with timeout protection and comprehensive debugging.

    Features:
        # - Timeout protection for all operations (30s default)
        # - Circuit breaker pattern for failing operations
        # - Comprehensive logging and fallback mechanisms
        # - Progress tracking and hang detection
        # - Detailed debug reports for troubleshooting
    """

    def __init__(self, project_root: str = "d:/Projects/impressioncore", timeout_seconds: int = 30):
        self.project_root = Path(project_root)
        self.assessment_timestamp = datetime.now()
        self.debugger = VRGCAssessmentDebugger(timeout_seconds=timeout_seconds)

        self.debugger.logger.info("🚀 Enhanced VRGC System Assessment initialized")
        self.debugger.logger.info(f"📁 Project root: {self.project_root}")

    async def assess_hardware_capabilities_safe(self) -> dict[str, Any]:
        """
        Safe hardware assessment with timeout protection.
        """
        async def _assess_hardware():
            self.debugger.logger.info("🔍 Checking hardware capabilities...")

            hardware_info = {
                "assessment_type": "hardware_capabilities",
                "timestamp": self.assessment_timestamp.isoformat(),
                "gpu_available": False,
                "cpu_cores": 0,
                "ram_total_gb": 0,
                "ram_available_gb": 0,
            }

            # CPU and RAM info (usually fast)
            try:
                hardware_info["cpu_cores"] = psutil.cpu_count()
                memory = psutil.virtual_memory()
                hardware_info["ram_total_gb"] = memory.total / 1024**3
                hardware_info["ram_available_gb"] = memory.available / 1024**3
                self.debugger.logger.info(f"💻 CPU: {hardware_info['cpu_cores']} cores, RAM: {hardware_info['ram_total_gb']:.1f}GB")
            except Exception as e:
                self.debugger.logger.warning(f"⚠️ CPU/RAM detection failed: {e!s}")

            # GPU info (can hang on driver issues)
            try:
                # Add small delay to simulate potential hang
                await asyncio.sleep(0.1)

                hardware_info["gpu_available"] = torch.cuda.is_available()

                if hardware_info["gpu_available"]:
                    hardware_info["gpu_name"] = torch.cuda.get_device_name(0)
                    hardware_info["gpu_memory_gb"] = torch.cuda.get_device_properties(0).total_memory / 1024**3
                    hardware_info["cuda_version"] = torch.version.cuda
                    hardware_info["gpu_optimization_ready"] = True
                    self.debugger.logger.info(f"🎮 GPU: {hardware_info['gpu_name']} ({hardware_info['gpu_memory_gb']:.1f}GB)")
                else:
                    hardware_info["gpu_optimization_ready"] = False
                    self.debugger.logger.info("🎮 No GPU available")

            except Exception as e:
                self.debugger.logger.error(f"❌ GPU detection failed: {e!s}")
                hardware_info["gpu_available"] = False
                hardware_info["gpu_optimization_ready"] = False
                hardware_info["gpu_error"] = str(e)

            return hardware_info

        return await self.debugger.timeout_wrapper(_assess_hardware, "hardware_assessment")

    async def assess_pytorch_ecosystem_safe(self) -> dict[str, Any]:
        """
        Safe PyTorch ecosystem assessment with timeout protection.
        """
        async def _assess_pytorch():
            self.debugger.logger.info("🔍 Checking PyTorch ecosystem...")

            ecosystem_info = {
                "assessment_type": "pytorch_ecosystem",
                "timestamp": self.assessment_timestamp.isoformat(),
                "pytorch_version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cudnn_enabled": False,
                "mixed_precision": False,
                "distributed_available": False,
            }

            # Check advanced features
            if torch.cuda.is_available():
                ecosystem_info["cudnn_enabled"] = torch.backends.cudnn.enabled

            ecosystem_info["mixed_precision"] = hasattr(torch.cuda.amp, 'autocast')
            ecosystem_info["distributed_available"] = hasattr(torch.distributed, 'is_available') and torch.distributed.is_available()

            # Calculate capability score
            capabilities_score = sum([
                ecosystem_info["cuda_available"] * 30,
                ecosystem_info["cudnn_enabled"] * 20,
                ecosystem_info["mixed_precision"] * 25,
                ecosystem_info["distributed_available"] * 25
            ])

            ecosystem_info["capabilities_score"] = capabilities_score
            ecosystem_info["optimization_ready"] = capabilities_score >= 75

            self.debugger.logger.info(f"🔥 PyTorch capabilities score: {capabilities_score}/100")

            return ecosystem_info

        return await self.debugger.timeout_wrapper(_assess_pytorch, "pytorch_assessment")

    async def assess_project_architecture_safe(self) -> dict[str, Any]:
        """
        Safe project architecture assessment with protection against infinite loops.
        """
        async def _assess_architecture():
            self.debugger.logger.info("🔍 Analyzing project architecture...")

            src_path = self.project_root / "src"
            architecture_info = {
                "assessment_type": "project_architecture",
                "timestamp": self.assessment_timestamp.isoformat(),
                "src_exists": src_path.exists(),
                "python_modules": 0,
                "core_modules": 0,
                "training_modules": 0,
                "interface_modules": 0,
                "directories": []
            }

            if not src_path.exists():
                self.debugger.logger.warning("📁 Source directory not found")
                return architecture_info

            # Protected file system traversal with limits
            max_files = 10000  # Prevent infinite loops
            max_depth = 10     # Prevent deep recursion
            file_count = 0

            try:
                for root, dirs, files in os.walk(src_path, followlinks=False):  # Don't follow symlinks
                    # Check depth limit
                    depth = root.replace(str(src_path), '').count(os.sep)
                    if depth > max_depth:
                        self.debugger.logger.warning(f"⚠️ Skipping deep directory: {root} (depth {depth})")
                        dirs[:] = []  # Don't recurse further
                        continue

                    # Process Python files
                    python_files = [f for f in files if f.endswith('.py')]
                    if python_files:
                        architecture_info["python_modules"] += len(python_files)
                        architecture_info["directories"].append(str(root))

                        # Categorize modules
                        root_lower = root.lower()
                        if "core" in root_lower:
                            architecture_info["core_modules"] += len(python_files)
                        elif "training" in root_lower:
                            architecture_info["training_modules"] += len(python_files)
                        elif "interface" in root_lower:
                            architecture_info["interface_modules"] += len(python_files)

                    # Safety check for file count
                    file_count += len(files)
                    if file_count > max_files:
                        self.debugger.logger.warning(f"⚠️ File count limit reached: {max_files}")
                        break

                    # Yield control to prevent blocking
                    await asyncio.sleep(0)

                # Calculate architecture health
                module_count = architecture_info["python_modules"]
                architecture_info["architecture_health"] = min(module_count / 10, 10.0)
                architecture_info["development_ready"] = module_count > 50

                self.debugger.logger.info(f"📊 Found {module_count} Python modules across {len(architecture_info['directories'])} directories")

            except Exception as e:
                self.debugger.logger.error(f"❌ Architecture analysis failed: {e!s}")
                raise  # Re-raise to trigger fallback

            return architecture_info

        return await self.debugger.timeout_wrapper(_assess_architecture, "architecture_assessment")

    async def assess_training_infrastructure_safe(self) -> dict[str, Any]:
        """
        Safe training infrastructure assessment with timeout protection.
        """
        async def _assess_infrastructure():
            self.debugger.logger.info("🔍 Checking training infrastructure...")

            infrastructure_info = {
                "assessment_type": "training_infrastructure",
                "timestamp": self.assessment_timestamp.isoformat(),
                "f_drive_available": False,
                "f_drive_space_gb": 0,
                "f_drive_total_gb": 0,
                "local_storage_gb": 0,
            }

            # Check F: drive (can hang on network drives)
            try:
                if os.path.exists("F:/"):
                    # Add timeout protection for disk operations
                    await asyncio.sleep(0.1)  # Yield control
                    usage = psutil.disk_usage("F:/")
                    infrastructure_info.update({
                        "f_drive_available": True,
                        "f_drive_space_gb": usage.free / 1024**3,
                        "f_drive_total_gb": usage.total / 1024**3,
                    })
                    self.debugger.logger.info(f"💾 F: drive: {infrastructure_info['f_drive_space_gb']:.1f}GB free")
                else:
                    self.debugger.logger.info("💾 F: drive not available")
            except Exception as e:
                self.debugger.logger.warning(f"⚠️ F: drive check failed: {e!s}")
                infrastructure_info["f_drive_error"] = str(e)

            # Check local storage
            try:
                await asyncio.sleep(0.1)  # Yield control
                local_usage = psutil.disk_usage(str(self.project_root))
                infrastructure_info["local_storage_gb"] = local_usage.free / 1024**3
                self.debugger.logger.info(f"💿 Local storage: {infrastructure_info['local_storage_gb']:.1f}GB free")
            except Exception as e:
                self.debugger.logger.warning(f"⚠️ Local storage check failed: {e!s}")
                infrastructure_info["local_storage_error"] = str(e)

            # Calculate infrastructure score
            f_drive_score = 50 if infrastructure_info["f_drive_available"] else 0
            local_storage_score = min(infrastructure_info["local_storage_gb"] * 2, 50)
            infrastructure_info["infrastructure_score"] = f_drive_score + local_storage_score
            infrastructure_info["training_ready"] = infrastructure_info["infrastructure_score"] >= 75

            return infrastructure_info

        return await self.debugger.timeout_wrapper(_assess_infrastructure, "infrastructure_assessment")

    async def assess_sacred_covenant_compliance_safe(self) -> dict[str, Any]:
        """
        Safe Sacred Covenant compliance assessment with timeout protection.
        """
        async def _assess_covenant():
            self.debugger.logger.info("🔍 Checking Sacred Covenant compliance...")

            covenant_info = {
                "assessment_type": "sacred_covenant_compliance",
                "timestamp": self.assessment_timestamp.isoformat(),
                "file_integrity_systems": [],
                "backup_systems": [],
                "compliance_score": 0
            }

            # Check for backup systems
            backup_dirs = ["backup/", "backups/", ".backup/"]
            for backup_dir in backup_dirs:
                backup_path = self.project_root / backup_dir
                if backup_path.exists():
                    covenant_info["backup_systems"].append(str(backup_path))
                    self.debugger.logger.info(f"📦 Found backup system: {backup_path}")
                await asyncio.sleep(0)  # Yield control

            # Check for file integrity tools
            integrity_files = ["backup_model_loading_fix_files.py", "enhanced_backup_monitor.py"]
            for integrity_file in integrity_files:
                integrity_path = self.project_root / integrity_file
                if integrity_path.exists():
                    covenant_info["file_integrity_systems"].append(str(integrity_path))
                    self.debugger.logger.info(f"🔒 Found integrity system: {integrity_file}")
                await asyncio.sleep(0)  # Yield control

            # Calculate compliance score
            backup_score = len(covenant_info["backup_systems"]) * 25
            integrity_score = len(covenant_info["file_integrity_systems"]) * 25
            covenant_info["compliance_score"] = min(backup_score + integrity_score, 100)
            covenant_info["covenant_compliant"] = covenant_info["compliance_score"] >= 50

            self.debugger.logger.info(f"⚖️ Covenant compliance score: {covenant_info['compliance_score']}/100")

            return covenant_info

        return await self.debugger.timeout_wrapper(_assess_covenant, "covenant_assessment")

    async def generate_comprehensive_assessment_safe(self) -> dict[str, Any]:
        """
        Generate comprehensive assessment with full protection against hangs and errors.
        """
        self.debugger.logger.info("🚀 Starting comprehensive VRGC assessment...")

        async with self.debugger.progress_context("Running comprehensive assessment..."):
            try:
                # Run all assessments with timeout protection
                assessments = await asyncio.gather(
                    self.assess_hardware_capabilities_safe(),
                    self.assess_pytorch_ecosystem_safe(),
                    self.assess_project_architecture_safe(),
                    self.assess_training_infrastructure_safe(),
                    self.assess_sacred_covenant_compliance_safe(),
                    return_exceptions=True  # Don't fail entire assessment if one fails
                )

                # Process results and handle any exceptions
                processed_results = []
                for i, result in enumerate(assessments):
                    if isinstance(result, Exception):
                        self.debugger.logger.error(f"❌ Assessment {i} failed with exception: {result!s}")
                        processed_results.append({"error": str(result), "success": False})
                    else:
                        processed_results.append(result)

                # Compile comprehensive report
                comprehensive_report = {
                    "vrgc_assessment": {
                        "version": "2.0.0-enhanced",
                        "timestamp": self.assessment_timestamp.isoformat(),
                        "assessment_duration": (datetime.now() - self.assessment_timestamp).total_seconds(),
                        "timeout_protected": True,
                        "fallback_enabled": True
                    },
                    "hardware": processed_results[0],
                    "pytorch_ecosystem": processed_results[1],
                    "project_architecture": processed_results[2],
                    "training_infrastructure": processed_results[3],
                    "sacred_covenant": processed_results[4]
                }

                # Calculate overall readiness score (handle fallback data)
                individual_scores = []
                for assessment in processed_results:
                    if assessment.get("success", True) and "result" in assessment:
                        result = assessment["result"]
                    else:
                        result = assessment

                    if "capabilities_score" in result:
                        individual_scores.append(result["capabilities_score"])
                    elif "architecture_health" in result:
                        individual_scores.append(result["architecture_health"] * 10)
                    elif "infrastructure_score" in result:
                        individual_scores.append(result["infrastructure_score"])
                    elif "compliance_score" in result:
                        individual_scores.append(result["compliance_score"])

                overall_score = sum(individual_scores) / len(individual_scores) if individual_scores else 0
                comprehensive_report["overall_readiness_score"] = overall_score

                # Determine readiness level
                if overall_score >= 90:
                    readiness_level = "EXCEPTIONAL - World-Class Ready"
                elif overall_score >= 80:
                    readiness_level = "EXCELLENT - Production Ready"
                elif overall_score >= 70:
                    readiness_level = "GOOD - Development Ready"
                else:
                    readiness_level = "NEEDS IMPROVEMENT - Basic Setup"

                comprehensive_report["readiness_level"] = readiness_level

                # Add debug information
                comprehensive_report["debug_info"] = self.debugger.generate_debug_report()

                self.debugger.logger.info(f"✅ Assessment complete! Overall score: {overall_score:.1f}/100 ({readiness_level})")

                # Save debug report
                self.debugger.save_debug_report(comprehensive_report)

                return comprehensive_report

            except Exception as e:
                self.debugger.logger.error(f"💥 Critical error in comprehensive assessment: {e!s}")
                # Return emergency fallback
                return {
                    "vrgc_assessment": {
                        "version": "2.0.0-enhanced",
                        "timestamp": self.assessment_timestamp.isoformat(),
                        "critical_error": str(e),
                        "emergency_fallback": True
                    },
                    "overall_readiness_score": 25,
                    "readiness_level": "CRITICAL ERROR - Emergency Fallback",
                    "debug_info": self.debugger.generate_debug_report()
                }

# MCP tool function with enhanced protection
async def vrgc_assess_system_enhanced(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Enhanced MCP tool function with comprehensive protection and debugging.
    """
    try:
        project_root = params.get("project_root", "d:/Projects/impressioncore") if params else "d:/Projects/impressioncore"
        timeout_seconds = params.get("timeout_seconds", 30) if params else 30

        assessor = VRGCSystemAssessmentEnhanced(project_root, timeout_seconds)
        result = await assessor.generate_comprehensive_assessment_safe()

        return {
            "success": True,
            "tool": "vrgc_assess_system_enhanced",
            "enhanced_protection": True,
            "timeout_seconds": timeout_seconds,
            "result": result
        }

    except Exception as e:
        return {
            "success": False,
            "tool": "vrgc_assess_system_enhanced",
            "error": str(e),
            "emergency_fallback": True
        }

# Test function
async def test_enhanced_assessment():
    """Test the enhanced assessment system."""
    print("🧪 Testing Enhanced VRGC Assessment System...")

    # Test with short timeout to trigger some fallbacks
    assessor = VRGCSystemAssessmentEnhanced(timeout_seconds=5)
    result = await assessor.generate_comprehensive_assessment_safe()

    print(f"📊 Assessment Result: {result['readiness_level']}")
    print(f"⏱️ Duration: {result['vrgc_assessment']['assessment_duration']:.2f}s")

    if result.get('debug_info'):
        print(f"🐛 Debug Info: {len(result['debug_info']['operation_times'])} operations completed")

if __name__ == "__main__":
    asyncio.run(test_enhanced_assessment())
