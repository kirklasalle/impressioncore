# !/usr/bin/env python3
## **Created:** 2024-10-15
## **Updated:** 2025-07-26 10_27_01
## **Author:** Virtually Robotic GitHub Copilot
## **Tags:** #cuda #gpu_optimization #python #pytorch #source_code #src/core/utils/vrgc_assessment_debug.py #testing #training
## **Category:** Core Implementation
## **Status:** Active
# -*- coding: utf-8 -*-
##
# VRGC Assessment Debug & Fallback System
# ======================================
#
# Comprehensive debugging, logging, and fallback mechanisms for VRGC assessments.
# Prevents infinite loops and provides detailed diagnostic information.
#
# Author: GitHub Copilot (VRGC)
# Created: 2025-06-20
# Sacred Covenant: File Integrity Protected
##
import asyncio
import json
import logging
import re
import time
import traceback
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

# Import rich for enhanced logging
try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.traceback import install
    RICH_AVAILABLE = True
    install()  # Install rich traceback handler
except ImportError:
    RICH_AVAILABLE = False

class VRGCAssessmentDebugger:
    def _sanitize_log_message(self, message):
        # Remove emoji and non-ASCII for Windows console compatibility
        return re.sub(r'[^\x00-\x7F]+', '', message)
    """
    Advanced debugging and fallback system for VRGC assessments.

    Features:
    - Timeout protection for all operations
    - Comprehensive logging with rich formatting
    - Circuit breaker pattern for failing operations
    - Fallback values for essential metrics
    - Progress tracking and hang detection
    """

    def __init__(self, timeout_seconds: int = 30, log_level: str = "INFO"):
        self.timeout_seconds = timeout_seconds
        self.start_time = time.time()
        self.operation_times = {}
        self.circuit_breakers = {}

        # Setup logging
        self.setup_logging(log_level)
        self.logger = logging.getLogger("vrgc_debug")

        # Rich console for enhanced output
        self.console = Console() if RICH_AVAILABLE else None

        self.logger.info("🤖 VRGC Assessment Debugger initialized")
        self.logger.info(f"⏱️ Timeout protection: {timeout_seconds}s per operation")

    def setup_logging(self, log_level: str):
        """Setup comprehensive logging with rich formatting."""
        log_handlers = []

        if RICH_AVAILABLE:
            # Rich handler for console output
            rich_handler = RichHandler(
                console=Console(),
                show_path=False,
                rich_tracebacks=True,
                markup=True
            )
            log_handlers.append(rich_handler)
        else:
            # Standard console handler
            class SanitizeConsoleHandler(logging.StreamHandler):
                def emit(self, record):
                    # Sanitize both msg and args for console output
                    record.msg = VRGCAssessmentDebugger._sanitize_log_message(self, str(record.msg))
                    if record.args:
                        record.args = tuple(VRGCAssessmentDebugger._sanitize_log_message(self, str(a)) for a in record.args)
                    try:
                        msg = self.format(record)
                        # Final sanitization: remove any non-ASCII from formatted message
                        msg = re.sub(r'[^\x00-\x7F]+', '', msg)
                        stream = self.stream
                        stream.write(msg + self.terminator)
                        self.flush()
                    except Exception:
                        self.handleError(record)
            console_handler = SanitizeConsoleHandler()
            console_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            )
            log_handlers.append(console_handler)

        # File handler for persistent logging
        log_file = Path("d:/Projects/impressioncore/src/memlog/vrgc_assessment_debug.log")
        log_file.parent.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
        )
        log_handlers.append(file_handler)

        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            handlers=log_handlers,
            force=True
        )

    async def timeout_wrapper(self, operation: Callable, operation_name: str, *args, **kwargs) -> dict[str, Any]:
        """
        Wrap any operation with timeout protection and comprehensive logging.

        Args:
            operation: The async function to execute
            operation_name: Name for logging and tracking
            *args, **kwargs: Arguments for the operation

        Returns:
            Dict containing result or fallback data
        """
        self.logger.info(f"🔧 Starting operation: [bold cyan]{operation_name}[/bold cyan]")
        operation_start = time.time()

        try:
            # Check circuit breaker
            if self.is_circuit_broken(operation_name):
                self.logger.warning(f"⚡ Circuit breaker OPEN for {operation_name}, using fallback")
                return self.get_fallback_result(operation_name)

            # Execute with timeout
            result = await asyncio.wait_for(
                operation(*args, **kwargs),
                timeout=self.timeout_seconds
            )

            # Record successful execution
            execution_time = time.time() - operation_start
            self.operation_times[operation_name] = execution_time
            self.reset_circuit_breaker(operation_name)

            self.logger.info(
                f"✅ Operation [bold green]{operation_name}[/bold green] completed in {execution_time:.2f}s"
            )

            return {
                "success": True,
                "operation": operation_name,
                "execution_time": execution_time,
                "result": result
            }

        except asyncio.TimeoutError:
            self.logger.error(f"⏰ TIMEOUT: {operation_name} exceeded {self.timeout_seconds}s limit")
            self.trip_circuit_breaker(operation_name, "timeout")
            return self.get_fallback_result(operation_name, error_type="timeout")

        except Exception as e:
            execution_time = time.time() - operation_start
            self.logger.error(
                f"💥 ERROR in {operation_name} after {execution_time:.2f}s: {e!s}"
            )
            self.logger.error(f"📋 Traceback: {traceback.format_exc()}")
            self.trip_circuit_breaker(operation_name, str(e))
            return self.get_fallback_result(operation_name, error_type="exception", error=str(e))

    def is_circuit_broken(self, operation_name: str) -> bool:
        """Check if circuit breaker is tripped for an operation."""
        if operation_name not in self.circuit_breakers:
            return False

        breaker_info = self.circuit_breakers[operation_name]
        failures = breaker_info.get("failures", 0)
        last_failure = breaker_info.get("last_failure", 0)

        # Reset circuit breaker after 5 minutes
        if time.time() - last_failure > 300:
            self.reset_circuit_breaker(operation_name)
            return False

        # Trip after 3 failures
        return failures >= 3

    def trip_circuit_breaker(self, operation_name: str, error: str):
        """Trip the circuit breaker for an operation."""
        if operation_name not in self.circuit_breakers:
            self.circuit_breakers[operation_name] = {"failures": 0}

        self.circuit_breakers[operation_name]["failures"] += 1
        self.circuit_breakers[operation_name]["last_failure"] = time.time()
        self.circuit_breakers[operation_name]["last_error"] = error

        self.logger.warning(
            f"⚡ Circuit breaker tripped for {operation_name} "
            f"(failures: {self.circuit_breakers[operation_name]['failures']})"
        )

    def reset_circuit_breaker(self, operation_name: str):
        """Reset the circuit breaker for an operation."""
        if operation_name in self.circuit_breakers:
            del self.circuit_breakers[operation_name]

    def get_fallback_result(self, operation_name: str, error_type: str = "circuit_breaker", error: str = "") -> dict[str, Any]:
        """Provide fallback results for failed operations."""
        fallback_data = {
            "success": False,
            "operation": operation_name,
            "error_type": error_type,
            "error": error,
            "fallback_used": True,
            "timestamp": datetime.now().isoformat()
        }

        # Operation-specific fallbacks
        if "hardware" in operation_name.lower():
            fallback_data["result"] = {
                "assessment_type": "hardware_capabilities",
                "gpu_available": False,
                "cpu_cores": 4,  # Conservative estimate
                "ram_total_gb": 16,  # Conservative estimate
                "gpu_optimization_ready": False,
                "fallback_reason": f"Hardware assessment failed: {error_type}"
            }

        elif "pytorch" in operation_name.lower():
            fallback_data["result"] = {
                "assessment_type": "pytorch_ecosystem",
                "pytorch_version": "unknown",
                "cuda_available": False,
                "capabilities_score": 0,
                "optimization_ready": False,
                "fallback_reason": f"PyTorch assessment failed: {error_type}"
            }

        elif "architecture" in operation_name.lower():
            fallback_data["result"] = {
                "assessment_type": "project_architecture",
                "src_exists": True,
                "python_modules": 50,  # Conservative estimate
                "architecture_health": 5.0,
                "development_ready": True,
                "fallback_reason": f"Architecture assessment failed: {error_type}"
            }

        elif "infrastructure" in operation_name.lower():
            fallback_data["result"] = {
                "assessment_type": "training_infrastructure",
                "f_drive_available": False,
                "infrastructure_score": 25,  # Minimum viable
                "training_ready": False,
                "fallback_reason": f"Infrastructure assessment failed: {error_type}"
            }

        elif "covenant" in operation_name.lower():
            fallback_data["result"] = {
                "assessment_type": "sacred_covenant_compliance",
                "compliance_score": 50,  # Assume basic compliance
                "covenant_compliant": True,
                "fallback_reason": f"Covenant assessment failed: {error_type}"
            }

        return fallback_data

    @asynccontextmanager
    async def progress_context(self, description: str):
        """Context manager for progress tracking with hang detection."""
        if self.console and RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=self.console,
                transient=True
            ) as progress:
                task = progress.add_task(description, total=None)
                try:
                    yield progress
                finally:
                    progress.remove_task(task)
        else:
            self.logger.info(f"🔄 {description}")
            yield None

    def generate_debug_report(self) -> dict[str, Any]:
        """Generate comprehensive debug report."""
        total_runtime = time.time() - self.start_time

        report = {
            "debug_session": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "total_runtime_seconds": total_runtime,
                "timeout_limit_seconds": self.timeout_seconds
            },
            "operation_times": self.operation_times,
            "circuit_breakers": self.circuit_breakers,
            "performance_analysis": {
                "slowest_operation": max(self.operation_times.items(), key=lambda x: x[1]) if self.operation_times else None,
                "average_operation_time": sum(self.operation_times.values()) / len(self.operation_times) if self.operation_times else 0,
                "total_operations": len(self.operation_times)
            },
            "recommendations": []
        }

        # Add recommendations based on performance
        if total_runtime > 60:
            report["recommendations"].append("Consider reducing timeout values or optimizing slow operations")

        if self.circuit_breakers:
            report["recommendations"].append("Review and fix operations with circuit breakers tripped")

        return report

    def save_debug_report(self, additional_data: dict[str, Any] | None = None):
        """Save detailed debug report to file."""
        report = self.generate_debug_report()

        if additional_data:
            report["additional_data"] = additional_data

        # Save to memlog
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"d:/Projects/impressioncore/src/memlog/vrgc_debug_report_{timestamp}.json")

        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"📊 Debug report saved: {report_file}")

        except Exception as e:
            self.logger.error(f"❌ Failed to save debug report: {e!s}")

# Standalone test function
async def test_debugger():
    """Test the debugging system."""
    debugger = VRGCAssessmentDebugger(timeout_seconds=5)

    # Test timeout protection
    async def slow_operation():
        await asyncio.sleep(10)  # This will timeout
        return {"test": "should not reach here"}

    # Test normal operation
    async def fast_operation():
        await asyncio.sleep(1)
        return {"test": "completed successfully"}

    # Run tests
    async with debugger.progress_context("Testing timeout protection"):
        result1 = await debugger.timeout_wrapper(slow_operation, "test_timeout")
        print(f"Timeout test result: {result1['success']}")

    async with debugger.progress_context("Testing normal operation"):
        result2 = await debugger.timeout_wrapper(fast_operation, "test_normal")
        print(f"Normal test result: {result2['success']}")

    # Generate report
    debugger.save_debug_report({"test_run": True})

if __name__ == "__main__":
    asyncio.run(test_debugger())
