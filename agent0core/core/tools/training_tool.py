"""
Training Tool - B3 Model Training Control

Created: January 13, 2026
Author: ImpressionCore Team

Tool for Agent0Core to monitor and control B3 model training.
Connects to real B3TrainingIntegrator and training infrastructure.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add ImpressionCore src to path for imports
_project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_project_root / "src"))

from ..governance import require_law_compliance

logger = logging.getLogger("agent0core.tools.training")


class TrainingTool:
    """
    Tool for monitoring and controlling B3 model training.

    Supports:
    - Training status monitoring
    - Checkpoint management
    - TensorBoard log reading
    - Training configuration
    """

    name = "training_tool"
    description = "Monitor and control B3 model training"

    # Training directories
    TRAINING_DIR = _project_root / "src" / "training"
    CHECKPOINTS_DIR = Path("F:/models/impressioncore_b3")
    TENSORBOARD_DIR = Path("F:/tb_logs_b3")

    def __init__(self):
        """Initialize the training tool."""
        self._integrator = None
        self._initialized = False
        logger.info("TrainingTool initialized")

    def _lazy_load_integrator(self) -> bool:
        """Lazy load the B3 training integrator."""
        if self._integrator is not None:
            return True

        try:
            from training.b3.b3_training_integration import B3TrainingIntegrator
            self._integrator = B3TrainingIntegrator()
            logger.info("B3TrainingIntegrator loaded")
            return True
        except ImportError as e:
            logger.warning(f"B3TrainingIntegrator not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize B3TrainingIntegrator: {e}")
            return False

    @require_law_compliance
    async def execute(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a training action.

        Args:
            action: The action to perform
            params: Optional parameters

        Returns:
            Result dictionary
        """
        params = params or {}

        if action == "status":
            return await self._get_status()
        elif action == "list_checkpoints":
            return await self._list_checkpoints()
        elif action == "checkpoint_info":
            return await self._checkpoint_info(params.get("path"))
        elif action == "get_config":
            return await self._get_config()
        elif action == "tensorboard_status":
            return await self._tensorboard_status()
        elif action == "get_metrics":
            return await self._get_metrics(params.get("checkpoint"))
        elif action == "list_training_scripts":
            return await self._list_training_scripts()
        else:
            return {"error": f"Unknown action: {action}", "available_actions": [
                "status", "list_checkpoints", "checkpoint_info", "get_config",
                "tensorboard_status", "get_metrics", "list_training_scripts"
            ]}

    async def _get_status(self) -> dict[str, Any]:
        """Get current training status."""
        status = {
            "training_active": False,
            "checkpoints_dir_exists": self.CHECKPOINTS_DIR.exists(),
            "tensorboard_dir_exists": self.TENSORBOARD_DIR.exists(),
        }

        # Check for recent checkpoints
        if self.CHECKPOINTS_DIR.exists():
            checkpoints = list(self.CHECKPOINTS_DIR.glob("*.pt"))
            if checkpoints:
                latest = max(checkpoints, key=lambda f: f.stat().st_mtime)
                status["latest_checkpoint"] = str(latest.name)
                status["latest_checkpoint_time"] = datetime.fromtimestamp(
                    latest.stat().st_mtime
                ).isoformat()
                status["checkpoint_count"] = len(checkpoints)

        # Check for running training processes
        try:
            import subprocess
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe"],
                capture_output=True, text=True, timeout=5
            )
            if "b3" in result.stdout.lower() and "train" in result.stdout.lower():
                status["training_active"] = True
        except Exception:
            pass

        return status

    async def _list_checkpoints(self) -> dict[str, Any]:
        """List available training checkpoints."""
        if not self.CHECKPOINTS_DIR.exists():
            return {"error": f"Checkpoints directory not found: {self.CHECKPOINTS_DIR}"}

        checkpoints = []
        for ckpt in self.CHECKPOINTS_DIR.glob("*.pt"):
            stat = ckpt.stat()
            checkpoints.append({
                "name": ckpt.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

        # Sort by modification time (newest first)
        checkpoints.sort(key=lambda x: x["modified"], reverse=True)

        return {"checkpoints": checkpoints, "count": len(checkpoints)}

    async def _checkpoint_info(self, path: str | None) -> dict[str, Any]:
        """Get detailed info about a checkpoint."""
        if not path:
            # Use latest checkpoint
            if not self.CHECKPOINTS_DIR.exists():
                return {"error": "No checkpoints directory"}
            checkpoints = list(self.CHECKPOINTS_DIR.glob("*.pt"))
            if not checkpoints:
                return {"error": "No checkpoints found"}
            ckpt_path = max(checkpoints, key=lambda f: f.stat().st_mtime)
        else:
            ckpt_path = Path(path)
            if not ckpt_path.exists():
                ckpt_path = self.CHECKPOINTS_DIR / path

        if not ckpt_path.exists():
            return {"error": f"Checkpoint not found: {ckpt_path}"}

        info = {
            "path": str(ckpt_path),
            "name": ckpt_path.name,
            "size_mb": round(ckpt_path.stat().st_size / (1024 * 1024), 2),
            "modified": datetime.fromtimestamp(ckpt_path.stat().st_mtime).isoformat(),
        }

        try:
            import torch
            ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
            info["keys"] = list(ckpt.keys())
            if "model_state_dict" in ckpt:
                model_keys = list(ckpt["model_state_dict"].keys())
                info["model_layers"] = len(model_keys)
            if "epoch" in ckpt:
                info["epoch"] = ckpt["epoch"]
            if "step" in ckpt:
                info["step"] = ckpt["step"]
            if "loss" in ckpt:
                info["loss"] = float(ckpt["loss"])
        except Exception as e:
            info["load_error"] = str(e)

        return info

    async def _get_config(self) -> dict[str, Any]:
        """Get B3 training configuration."""
        config = {
            "model_type": "ImpressionCore B3",
            "parameters": "39M",
            "target_hardware": "GTX 1050 Ti (4GB VRAM)",
            "training_dir": str(self.TRAINING_DIR),
            "checkpoints_dir": str(self.CHECKPOINTS_DIR),
            "tensorboard_dir": str(self.TENSORBOARD_DIR),
        }

        # Try to find training config files
        config_files = list(self.TRAINING_DIR.glob("**/b3*config*.py"))
        if config_files:
            config["config_files"] = [str(f.relative_to(self.TRAINING_DIR)) for f in config_files[:5]]

        return config

    async def _tensorboard_status(self) -> dict[str, Any]:
        """Check TensorBoard log status."""
        if not self.TENSORBOARD_DIR.exists():
            return {"error": f"TensorBoard directory not found: {self.TENSORBOARD_DIR}"}

        log_dirs = [d for d in self.TENSORBOARD_DIR.iterdir() if d.is_dir()]
        events = list(self.TENSORBOARD_DIR.glob("**/events.out.tfevents.*"))

        return {
            "log_dirs": len(log_dirs),
            "event_files": len(events),
            "latest_event": max(events, key=lambda f: f.stat().st_mtime).name if events else None,
            "tensorboard_command": f"tensorboard --logdir {self.TENSORBOARD_DIR}",
        }

    async def _get_metrics(self, checkpoint: str | None) -> dict[str, Any]:
        """Get training metrics from a checkpoint."""
        # Use checkpoint_info for metrics
        return await self._checkpoint_info(checkpoint)

    async def _list_training_scripts(self) -> dict[str, Any]:
        """List available B3 training scripts."""
        b3_dir = self.TRAINING_DIR / "b3"
        if not b3_dir.exists():
            return {"error": f"B3 training directory not found: {b3_dir}"}

        scripts = []
        for script in b3_dir.glob("*.py"):
            scripts.append({
                "name": script.name,
                "size_kb": round(script.stat().st_size / 1024, 1),
            })

        scripts.sort(key=lambda x: x["name"])
        return {"scripts": scripts, "count": len(scripts), "directory": str(b3_dir)}
