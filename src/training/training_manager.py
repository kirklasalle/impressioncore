#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src\training\training_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [training]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Description:
Training manager for handling training state and WebSocket updates.
Handles model training, memory profiling, checkpointing, and metrics export.
Optimized for low-VRAM consumer hardware. All exports and logs are timestamped and stored in /src/memlog/improvements.

Design Philosophy:
Memory-efficient training management with real-time monitoring and automated checkpointing.
Designed to work seamlessly with ModelTrainer for comprehensive training workflows.

Memory Considerations:
- Designed for low VRAM (target: 4GB GPU)
- Uses gradient checkpointing and memory profiling
- All file exports use current system time for naming
- Integrates with memory monitoring and optimization systems

Examples:
```python
# Basic usage
manager = TrainingManager()
config = {"model_name": "test_model", "architecture": "transformer"}
if manager.initialize_training(config):
    manager.start_training()
```

Notes:
- Automatically handles checkpointing and metrics export
- Supports memory profiling and VRAM optimization
- Thread-safe training execution
"""

import os
import json
import time
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
import asyncio
import websockets
import torch
import psutil
try:
    from memory_profiler import profile
except ImportError:
    # Fallback dummy decorator
    def profile(func):
        return func
import torch.nn as nn
import torch.optim as optim
from pathlib import Path

"""
Training manager for handling training state and WebSocket updates.
Handles model training, memory profiling, checkpointing, and metrics export.
Optimized for low-VRAM consumer hardware. All exports and logs are timestamped and stored in /src/memlog/improvements.

Memory Implications:
- Designed for low VRAM (target: 4GB GPU)
- Uses gradient checkpointing and memory profiling
- All file exports use current system time for naming
"""

import logging
import threading
import torch
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from .trainer import ModelTrainer
try:
    from core.config.training_config import (
        DEFAULT_VRAM_TARGET, PRECISION_MODES, CHECKPOINT_INTERVAL_STEPS, METRICS_EXPORT_INTERVAL_STEPS
    )
    from core.utils.error_reporting import log_error
    from core.utils.memory_profiler import MemoryProfiler
    from core.utils.memory_utils import get_gpu_memory_usage
    from core.utils.precision_manager import PrecisionMode
except ImportError:
    from ..core.config.training_config import (
        DEFAULT_VRAM_TARGET, PRECISION_MODES, CHECKPOINT_INTERVAL_STEPS, METRICS_EXPORT_INTERVAL_STEPS
    )
    from ..core.utils.error_reporting import log_error
    from ..core.utils.memory_profiler import MemoryProfiler
    from ..core.utils.memory_utils import get_gpu_memory_usage
    from ..core.utils.precision_manager import PrecisionMode

logger = logging.getLogger(__name__)

@dataclass
class TrainingState:
    """Current state of training.
    Attributes:
        is_training (bool): Whether training is active.
        model_name (str): Name of the model.
        architecture (str): Model architecture.
        total_params (int): Total number of model parameters.
        global_step (int): Current global step.
        train_loss (float): Latest training loss.
        val_loss (Optional[float]): Latest validation loss.
        learning_rate (float): Current learning rate.
        tokens_per_second (float): Token processing speed.
        vram_usage (float): Current VRAM usage in GB.
        precision_mode (str): Precision mode (fp16, fp32, bf16).
        gradient_checkpointing (bool): Whether gradient checkpointing is enabled.
        attention_cache (bool): Whether attention caching is enabled.
        vram_target (float): Target VRAM usage in GB.
    """
    is_training: bool = False
    model_name: str = ""
    architecture: str = ""
    total_params: int = 0
    global_step: int = 0
    train_loss: float = 0.0
    val_loss: Optional[float] = None
    learning_rate: float = 0.0
    tokens_per_second: float = 0.0
    vram_usage: float = 0.0
    precision_mode: str = "fp16"
    gradient_checkpointing: bool = True
    attention_cache: bool = True
    vram_target: float = 3.5

class TrainingManager:
    """
    Manages model training state, memory profiling, checkpointing, and metrics export.
    Ensures safe, memory-efficient training on consumer hardware.
    """
    def __init__(self) -> None:
        """
        Initialize the TrainingManager and its state.
        Ensures checkpoint and log directories exist.
        """
        self.state = TrainingState()
        self.trainer: Optional[ModelTrainer] = None
        self.training_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        # Create checkpoints directory within src/training directory
        src_dir = Path(__file__).parent.parent  # Go up to src directory
        self.checkpoints_dir = src_dir / "training" / "checkpoints"
        try:
            self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log_error(f"Failed to create checkpoints directory: {e}", context="__init__")
        self._profiler = MemoryProfiler()
        self._last_checkpoint_step = 0
        self._last_metrics_export_step = 0

    def initialize_training(self, model_config: Dict[str, Any]) -> bool:
        """
        Initialize a new training session.
        Args:
            model_config (Dict[str, Any]): Model configuration dictionary.
        Returns:
            bool: True if initialization succeeds, False otherwise.
        Memory: May allocate model weights on GPU/CPU.
        """
        if not isinstance(model_config, dict):
            log_error("model_config must be a dictionary", context="initialize_training")
            return False
        try:
            self.trainer = ModelTrainer.from_config(
                model_config=model_config,
                device="cuda" if torch.cuda.is_available() else "cpu",
                mixed_precision=self.state.precision_mode == "fp16",
                target_vram_usage=self.state.vram_target
            )
            self.state.model_name = model_config.get("model_name", "Unnamed Model")
            self.state.architecture = model_config.get("architecture", "Unknown")
            self.state.total_params = sum(p.numel() for p in self.trainer.model.parameters())
            return True
        except Exception as e:
            log_error(f"Failed to initialize training: {e}", context="initialize_training")
            return False

    def start_training(self) -> bool:
        """
        Start or resume training in a separate thread.
        Returns:
            bool: True if training started, False otherwise.
        Memory: Starts memory profiler and training thread.
        """
        if not self.trainer:
            log_error("No trainer initialized", context="start_training")
            return False
        if self.state.is_training:
            logger.warning("Training already in progress")
            return True
        self._stop_event.clear()
        self.state.is_training = True
        self._profiler.start_tracking()
        self.training_thread = threading.Thread(
            target=self._training_loop,
            daemon=True
        )
        self.training_thread.start()
        return True

    def _training_loop(self) -> None:
        """
        Main training loop running in separate thread.
        Tracks memory usage, handles periodic checkpointing and metrics export.
        Ensures resource cleanup and error logging.
        Memory: Profiles RAM and VRAM usage per step.
        """
        try:
            while not self._stop_event.is_set():
                stats = self.trainer.train_step()
                self.state.global_step = stats["global_step"]
                self.state.train_loss = stats["train_loss"]
                self.state.val_loss = stats.get("val_loss")
                self.state.learning_rate = stats["learning_rate"]
                self.state.tokens_per_second = stats["tokens_per_second"]
                self.state.vram_usage = get_gpu_memory_usage()                # RAM profiling for each step - just track that we're taking a step
                pass  # Memory profiler is running in background
                # Periodic checkpointing
                if self.state.global_step - self._last_checkpoint_step >= CHECKPOINT_INTERVAL_STEPS:
                    try:
                        # Use current system time for checkpoint naming
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        checkpoint_name = f"step_{self.state.global_step}_{timestamp}.pt"
                        self.save_checkpoint(checkpoint_name)
                        self._last_checkpoint_step = self.state.global_step
                    except Exception as e:
                        log_error(f"Checkpoint save failed: {e}", context="_training_loop/checkpoint")
                # Periodic metrics export
                if self.state.global_step - self._last_metrics_export_step >= METRICS_EXPORT_INTERVAL_STEPS:
                    try:
                        metrics = self.export_metrics()
                        export_path = Path("src/memlog/improvements") / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        export_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(export_path, "w", encoding="utf-8") as f:
                            import json
                            json.dump(metrics, f, indent=2)
                        self._last_metrics_export_step = self.state.global_step
                    except Exception as e:
                        log_error(f"Metrics export failed: {e}", context="_training_loop/metrics_export")
        except Exception as e:
            log_error(f"Error in training loop: {e}", context="_training_loop")
            self.state.is_training = False
        finally:
            self._profiler.stop_tracking()
            # Generate a simple report from snapshots
            report = {
                "snapshots_count": len(self._profiler.snapshots),
                "tracking_interval": self._profiler.tracking_interval,
                "device": self._profiler.device
            }
            # Use current system time for memory profile naming
            report_path = Path("src/memlog/improvements") / f"memory_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    import json
                    json.dump(report, f, indent=2)
            except Exception as e:
                log_error(f"Failed to write memory profile: {e}", context="_training_loop/finally")

    def pause_training(self) -> None:
        """
        Pause training and ensure thread cleanup.
        Memory: Joins training thread and stops profiler.
        """
        if not self.state.is_training:
            return
        self._stop_event.set()
        if self.training_thread:
            self.training_thread.join()
        self.state.is_training = False

    def stop_training(self) -> None:
        """
        Stop training, save final checkpoint, and cleanup resources.
        Memory: Saves checkpoint and releases trainer.
        """
        self.pause_training()
        if self.trainer:
            try:
                self.save_checkpoint("final_checkpoint.pt")
            except Exception as e:
                log_error(f"Final checkpoint save failed: {e}", context="stop_training")
            self.trainer = None

    def save_checkpoint(self, filename: str) -> Path:
        """
        Save a checkpoint to the checkpoints directory.
        Args:
            filename (str): Checkpoint filename (should end with .pt).
        Returns:
            Path: Path to the saved checkpoint.
        Raises:
            RuntimeError: If no active training session.
        Memory: Serializes model weights to disk.
        """
        if not isinstance(filename, str) or not filename.endswith(".pt"):
            raise ValueError("filename must be a .pt string")
        if not self.trainer:
            raise RuntimeError("No active training session")
        checkpoint_path = self.checkpoints_dir / filename
        try:
            self.trainer.save_checkpoint(checkpoint_path)
        except Exception as e:
            log_error(f"Checkpoint save failed: {e}", context="save_checkpoint")
            raise
        return checkpoint_path

    def export_metrics(self) -> Dict[str, Any]:
        """
        Export current training metrics with export metadata.
        Returns:
            Dict[str, Any]: Metrics dictionary with export metadata.
        Raises:
            RuntimeError: If no active training session.
        Memory: Minimal impact, just serializes stats.
        """
        if not self.trainer:
            raise RuntimeError("No active training session")
        metrics = self.trainer.get_metrics_history()
        metrics["export_time"] = datetime.now().isoformat()
        metrics["model_name"] = self.state.model_name
        metrics["total_steps"] = self.state.global_step
        return metrics

    def set_vram_target(self, target_gb: float) -> None:
        """
        Update VRAM usage target for training.
        Args:
            target_gb (float): Target VRAM in GB.
        Memory: May trigger model reallocation.
        """
        if not isinstance(target_gb, (float, int)) or target_gb <= 0:
            raise ValueError("target_gb must be a positive number")
        self.state.vram_target = float(target_gb)
        if self.trainer:
            self.trainer.update_vram_target(float(target_gb))

    def set_precision_mode(self, mode: str) -> None:
        """
        Update precision mode for training.
        Args:
            mode (str): Precision mode ("fp32", "fp16", "bf16").
        Memory: May reconfigure model weights.
        """
        if mode not in ["fp32", "fp16", "bf16"]:
            raise ValueError(f"Invalid precision mode: {mode}")
        self.state.precision_mode = mode
        if self.trainer:
            # Convert string to PrecisionMode enum
            precision_enum = {
                "fp32": PrecisionMode.FP32,
                "fp16": PrecisionMode.FP16,
                "bf16": PrecisionMode.BF16
            }.get(mode.lower())
            if precision_enum:
                self.trainer.set_precision_mode(precision_enum)

    def set_gradient_checkpointing(self, enabled: bool) -> None:
        """
        Toggle gradient checkpointing for memory optimization.
        Args:
            enabled (bool): Enable or disable gradient checkpointing.
        Memory: Reduces VRAM usage if enabled.
        """
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a boolean")
        self.state.gradient_checkpointing = enabled
        if self.trainer:
            self.trainer.set_gradient_checkpointing(enabled)

    def set_attention_cache(self, enabled: bool) -> None:
        """
        Toggle attention caching for performance.
        Args:
            enabled (bool): Enable or disable attention cache.
        Memory: May increase VRAM usage if enabled.
        """
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a boolean")
        self.state.attention_cache = enabled
        if self.trainer:
            self.trainer.set_attention_cache(enabled)

    def get_current_stats(self) -> Dict[str, Any]:
        """
        Get current training statistics as a dictionary.
        Returns:
            Dict[str, Any]: Current training state.
        Memory: Minimal impact.
        """
        return asdict(self.state)