"""B1 Performance Benchmark (archived reference)

Original file: `benchmarks/b1_performance_suite.py`
Status: Archived reference (B-1 tier). Logic retained without modification aside
from updated relative imports to reflect new package location.
"""
from __future__ import annotations

import logging

# NOTE: Original header and rich descriptive docstring omitted for brevity in migration.
import time
import tracemalloc
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil
import torch

try:  # Adjusted import paths may change after full refactor
    from src.core.utils.rich_enhancements import EnhancedDisplay  # type: ignore
    from src.core.utils.rich_logging import setup_rich_logging  # type: ignore
    from src.core.utils.rich_status_animation import StatusAnimation  # type: ignore
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from training.models.architectures.b1.b1_model import ImpressionCoreB1Model  # type: ignore
    B1_COMPONENTS_AVAILABLE = True
except ImportError:
    B1_COMPONENTS_AVAILABLE = False

try:
    from memory_profiler import profile  # type: ignore  # noqa: F401
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False


class B1PerformanceBenchmark:
    def __init__(self, output_dir: str | None = None):
        self.output_dir = Path(output_dir or "evaluation/benchmarks/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.start_time = datetime.now()
        self.benchmark_results = {}
        if RICH_AVAILABLE:
            self.display = EnhancedDisplay()
            self.logger = setup_rich_logging("b1_benchmark")
            self.status_animation = StatusAnimation()
        else:
            self.display = None
            self.logger = logging.getLogger("b1_benchmark")
            self.status_animation = None
        self.hardware_info = self._detect_hardware()
        self.logger.info("[ARCHIVE] B1 Performance Benchmark Initialized")

    def _detect_hardware(self) -> dict[str, Any]:
        hardware = {
            "cpu": {"cores": psutil.cpu_count()},
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            },
            "gpu": {"available": torch.cuda.is_available(), "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0},
        }
        if hardware["gpu"]["available"]:
            hardware["gpu"]["name"] = torch.cuda.get_device_name(0)
            hardware["gpu"]["memory_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        return hardware

    # Truncated: retain core benchmark methods selectively (instantiation only preserved for archive)
    def benchmark_b1_model_instantiation(self) -> dict[str, Any]:
        results = {"test_name": "B1 Model Instantiation", "success": False}
        if not B1_COMPONENTS_AVAILABLE:
            results["error"] = "B1 components unavailable"
            return results
        try:
            tracemalloc.start()
            start_time = time.time()
            model = ImpressionCoreB1Model(input_dim=512, hidden_dim=768, num_layers=4, chunk_size=128)
            if torch.cuda.is_available():
                model = model.cuda()
            param_count = sum(p.numel() for p in model.parameters())
            instantiation_time = time.time() - start_time
            _, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            results.update({
                "success": True,
                "parameters": param_count,
                "instantiation_time_s": round(instantiation_time, 3),
                "peak_memory_mb": round(peak_memory / (1024 * 1024), 2),
            })
        except Exception as e:
            results["error"] = str(e)
        return results

    def run_minimal_archive_suite(self) -> dict[str, Any]:
        return {"b1_model_instantiation": self.benchmark_b1_model_instantiation()}

__all__ = ["B1PerformanceBenchmark"]
