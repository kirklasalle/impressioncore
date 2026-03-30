#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #deployment #python #source_code #src/training/distillation\f_drive_config.py #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #deployment #python #source_code #src\\training\\distillation\\f_drive_config.py #training
# Category:** Training System
# Status:** Active

"""
ImpressionCore F:/ Drive Configuration
F:/ Drive paths for all model outputs, training data, and artifacts

File: src/training/distillation/f_drive_config.py
Created: 2025-06-27
Version: 1.0.0

Author: Virtually Robotic GitHub Copilot
Sacred Covenant: Active - All outputs to F:/ drive for optimal storage
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class FDriveConfig:
    """
    Centralized F:/ Drive configuration for ImpressionCore B1 training

    All model outputs, checkpoints, training data, and artifacts
    are stored on the F:/ drive for optimal performance and organization.
    """

    # Base F:/ Drive Paths
    F_DRIVE_ROOT = Path("F:/")

    # Model Output Directories
    MODELS_ROOT = F_DRIVE_ROOT / "impressioncore-b1-models"
    DISTILLATION_ROOT = MODELS_ROOT / "distillation"
    CHECKPOINTS_DIR = DISTILLATION_ROOT / "checkpoints"
    TRAINED_MODELS_DIR = DISTILLATION_ROOT / "trained_models"
    LOGS_DIR = DISTILLATION_ROOT / "logs"

    # Training Data Directories
    TRAINING_DATA_ROOT = F_DRIVE_ROOT / "impressioncore-b1-training-data"
    TEACHER_KNOWLEDGE_DIR = TRAINING_DATA_ROOT / "teacher_knowledge"
    DISTILLATION_DATASETS_DIR = TRAINING_DATA_ROOT / "distillation_datasets"

    # Existing F:/ Drive Directories
    DATASETS_ROOT = F_DRIVE_ROOT / "datasets"
    EMBEDDINGS_ROOT = F_DRIVE_ROOT / "impressioncore-b1-embeddings-062125"
    UKS_OUTPUT_ROOT = F_DRIVE_ROOT / "impressioncore-b1-uks-output"

    @classmethod
    def create_all_directories(cls) -> dict[str, bool]:
        """Create all F:/ drive directories and return creation status"""

        directories = [
            cls.MODELS_ROOT,
            cls.DISTILLATION_ROOT,
            cls.CHECKPOINTS_DIR,
            cls.TRAINED_MODELS_DIR,
            cls.LOGS_DIR,
            cls.TRAINING_DATA_ROOT,
            cls.TEACHER_KNOWLEDGE_DIR,
            cls.DISTILLATION_DATASETS_DIR
        ]

        creation_status = {}

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                creation_status[str(directory)] = True
            except Exception as e:
                creation_status[str(directory)] = False
                print(f"❌ Failed to create {directory}: {e}")

        return creation_status

    @classmethod
    def get_paths_dict(cls) -> dict[str, str]:
        """Get all F:/ drive paths as dictionary for serialization"""

        return {
            "f_drive_root": str(cls.F_DRIVE_ROOT),
            "models_root": str(cls.MODELS_ROOT),
            "distillation_root": str(cls.DISTILLATION_ROOT),
            "checkpoints_dir": str(cls.CHECKPOINTS_DIR),
            "trained_models_dir": str(cls.TRAINED_MODELS_DIR),
            "logs_dir": str(cls.LOGS_DIR),
            "training_data_root": str(cls.TRAINING_DATA_ROOT),
            "teacher_knowledge_dir": str(cls.TEACHER_KNOWLEDGE_DIR),
            "distillation_datasets_dir": str(cls.DISTILLATION_DATASETS_DIR),
            "datasets_root": str(cls.DATASETS_ROOT),
            "embeddings_root": str(cls.EMBEDDINGS_ROOT),
            "uks_output_root": str(cls.UKS_OUTPUT_ROOT)
        }

    @classmethod
    def save_config_file(cls) -> str:
        """Save F:/ drive configuration to file"""

        config_data = {
            "generation_timestamp": datetime.now().isoformat(),
            "description": "ImpressionCore B1 F:/ Drive Configuration",
            "sacred_covenant": "Active - All outputs to F:/ drive",
            "paths": cls.get_paths_dict(),
            "directory_purposes": {
                "models_root": "All trained models and model artifacts",
                "checkpoints_dir": "Training checkpoints and state saves",
                "trained_models_dir": "Final trained model files ready for deployment",
                "logs_dir": "Training logs and metrics",
                "teacher_knowledge_dir": "Knowledge extracted from teacher models",
                "distillation_datasets_dir": "Datasets created for distillation training",
                "datasets_root": "Source training datasets",
                "embeddings_root": "Pre-computed embeddings and vectorized data",
                "uks_output_root": "Universal Knowledge System outputs"
            }
        }

        config_file = cls.LOGS_DIR / f"f_drive_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Ensure logs directory exists
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2, default=str)

        return str(config_file)

    @classmethod
    def validate_f_drive_setup(cls) -> dict[str, Any]:
        """Validate F:/ drive setup and return status report"""

        import shutil

        # Check F:/ drive availability
        try:
            total, used, free = shutil.disk_usage(cls.F_DRIVE_ROOT)
            drive_accessible = True
            drive_info = {
                "total_gb": total // (1024**3),
                "used_gb": used // (1024**3),
                "free_gb": free // (1024**3)
            }
        except Exception as e:
            drive_accessible = False
            drive_info = {"error": str(e)}

        # Check directory existence
        paths = cls.get_paths_dict()
        directory_status = {}

        for name, path in paths.items():
            directory_status[name] = {
                "path": path,
                "exists": Path(path).exists(),
                "is_directory": Path(path).is_dir() if Path(path).exists() else False
            }

        validation_report = {
            "timestamp": datetime.now().isoformat(),
            "f_drive_accessible": drive_accessible,
            "drive_info": drive_info,
            "directory_status": directory_status,
            "all_paths_valid": all(status["exists"] for status in directory_status.values()),
            "ready_for_training": drive_accessible and all(status["exists"] for status in directory_status.values())
        }

        return validation_report

def main():
    """Initialize and validate F:/ drive configuration"""

    print("💾 ImpressionCore F:/ Drive Configuration")
    print("🎯 Sacred Covenant: All outputs to F:/ drive")
    print("")

    # Create all directories
    print("📁 Creating F:/ drive directory structure...")
    creation_status = FDriveConfig.create_all_directories()

    successful_creates = sum(1 for success in creation_status.values() if success)
    total_dirs = len(creation_status)

    print(f"✅ Created {successful_creates}/{total_dirs} directories")

    # Validate setup
    print("\n🔍 Validating F:/ drive setup...")
    validation_report = FDriveConfig.validate_f_drive_setup()

    if validation_report["ready_for_training"]:
        print("✅ F:/ drive setup READY for training!")

        if validation_report["f_drive_accessible"]:
            drive_info = validation_report["drive_info"]
            print(f"💾 F:/ Drive Space: {drive_info['free_gb']:.1f}GB free")

    else:
        print("❌ F:/ drive setup needs attention")

    # Save configuration
    config_file = FDriveConfig.save_config_file()
    print(f"\n💾 Configuration saved: {Path(config_file).name}")

    # Display paths
    print("\n📋 F:/ Drive Path Summary:")
    paths = FDriveConfig.get_paths_dict()
    for name, path in paths.items():
        print(f"   {name}: {path}")

    return validation_report

if __name__ == "__main__":
    report = main()
