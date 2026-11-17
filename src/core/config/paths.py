#!/usr/bin/env python3
"""
ImpressionCore: Central Path Configuration & Verification Module.

Enforces fail-fast path validation for GTX 1050 Ti model serving and training.
"""

import os
from pathlib import Path
from .data_paths import DATA_DRIVE, MODELS_ROOT, DATA_ROOT, B3_HOPE_V1_DIR

class PathConfig:
    DEFAULT_F_DRIVE = Path("F:/")
    
    @classmethod
    def get_model_dir(cls) -> Path:
        """Get production models directory with environment variable override."""
        base = Path(os.getenv("IC_MODEL_DIR", cls.DEFAULT_F_DRIVE / "models/production"))
        if not base.exists():
            raise RuntimeError(f"Critical Path Missing: Model directory {base} is inaccessible.")
        return base

    @classmethod
    def validate_environment(cls) -> None:
        """Validate all critical paths and fail-fast if any are missing."""
        drive = Path(os.getenv("IMPRESSIONCORE_DATA_DRIVE", DATA_DRIVE))
        if not drive.exists():
            raise RuntimeError(f"Critical Path Missing: Data drive {drive} is inaccessible.")
            
        required_dirs = [
            MODELS_ROOT,
            DATA_ROOT,
            B3_HOPE_V1_DIR
        ]
        
        for directory in required_dirs:
            # Apply override check if any env override was specified
            dir_path = Path(directory)
            if not dir_path.exists():
                raise RuntimeError(f"Critical Path Missing: Required directory {dir_path} is inaccessible.")
