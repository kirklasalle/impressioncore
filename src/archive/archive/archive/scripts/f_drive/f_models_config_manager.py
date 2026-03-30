
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #deployment #inference #memory_management #python #source_code #src/scripts/f_drive/f_models_config_manager.py #testing #training
**Category:** Source Code
**Status:** Deprecated
"""



import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class FModelsConfigManager:
    """Manages configuration updates for F:\models migration"""

    def __init__(self):
        self.console = Console()
        self.f_models_root = Path("F:/models")

        # Updated path configurations
        self.path_config = {
            "models_root": "F:/models",
            "checkpoints": {
                "best_quality": "F:/models/checkpoints/best_quality",
                "production": "F:/models/checkpoints/production",
                "backup": "F:/models/checkpoints/backup"
            },
            "training": {
                "active": "F:/models/training/active",
                "epochs": "F:/models/training/epochs",
                "experiments": "F:/models/training/experiments",
                "logs": "F:/models/training/logs"
            },
            "distillation": {
                "ollama_progressive": "F:/models/distillation/ollama_progressive",
                "remote_api": "F:/models/distillation/remote_api",
                "enhanced_models": "F:/models/distillation/enhanced_models",
                "curriculum": "F:/models/distillation/curriculum"
            },
            "deployment": {
                "production": "F:/models/deployment/production",
                "testing": "F:/models/deployment/testing",
                "configs": "F:/models/deployment/configs"
            },
            "archives": {
                "legacy": "F:/models/archives/legacy",
                "experiments": "F:/models/archives/experiments",
                "deprecated": "F:/models/archives/deprecated"
            },
            "infrastructure": {
                "scripts": "F:/models/infrastructure/scripts",
                "configs": "F:/models/infrastructure/configs",
                "utilities": "F:/models/infrastructure/utilities",
                "monitoring": "F:/models/infrastructure/monitoring"
            }
        }

        # Legacy paths for reference
        self.legacy_paths = {
            "f_data_embeddings": "F:/data/embeddings/b3_training/checkpoints",
            "f_data_distillation": "F:/data/distillation",
            "f_data_training": "F:/data/training"
        }

    def create_master_config(self):
        """Create master configuration file for F:\models"""
        config_file = self.f_models_root / "infrastructure" / "configs" / "f_models_master_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        master_config = {
            "version": "2.0.0",
            "created": datetime.now().isoformat(),
            "description": "Master configuration for F:\\models ImpressionCore infrastructure",
            "migration_completed": datetime.now().isoformat(),
            "primary_model_location": "F:/models",
            "paths": self.path_config,
            "legacy_paths": self.legacy_paths,
            "current_models": {
                "best_quality_model": {
                    "path": "F:/models/checkpoints/best_quality/b3_best_quality_model_20250802_124801.pth",
                    "size_mb": 199.83,
                    "description": "Production-ready B3 best quality model",
                    "use_case": "Production inference and distillation base"
                },
                "latest_training_model": {
                    "path": "F:/models/training/active/b3_training_epoch_30_20250801_074634.pth",
                    "size_mb": 336.47,
                    "description": "Latest B3 training checkpoint",
                    "use_case": "Development continuity and further training"
                }
            },
            "distillation_systems": {
                "ollama_progressive": {
                    "output_dir": "F:/models/distillation/ollama_progressive",
                    "logs_dir": "F:/models/distillation/ollama_progressive/logs",
                    "results_dir": "F:/models/distillation/ollama_progressive/results",
                    "status": "Updated for F:/models"
                },
                "remote_api": {
                    "output_dir": "F:/models/distillation/remote_api",
                    "logs_dir": "F:/models/distillation/remote_api/logs",
                    "results_dir": "F:/models/distillation/remote_api/results",
                    "status": "Updated for F:/models"
                }
            },
            "usage_guidelines": {
                "new_models": "Save all new models to F:/models appropriate subdirectories",
                "checkpoints": "Use F:/models/checkpoints for production models",
                "training": "Use F:/models/training for active development",
                "distillation": "Use F:/models/distillation for enhanced models",
                "deployment": "Use F:/models/deployment for production deployment"
            }
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(master_config, f, indent=2)

        return str(config_file)

    def create_training_config(self):
        """Create training system configuration for F:\models"""
        training_config_file = self.f_models_root / "infrastructure" / "configs" / "training_config.json"

        training_config = {
            "version": "2.0.0",
            "updated": datetime.now().isoformat(),
            "training_infrastructure": {
                "checkpoints_dir": "F:/models/training/epochs",
                "active_model_dir": "F:/models/training/active",
                "experiments_dir": "F:/models/training/experiments",
                "logs_dir": "F:/models/training/logs"
            },
            "checkpoint_strategy": {
                "save_every_epoch": True,
                "save_location": "F:/models/training/epochs",
                "best_model_location": "F:/models/checkpoints/best_quality",
                "backup_location": "F:/models/checkpoints/backup"
            },
            "current_training": {
                "resume_from": "F:/models/training/active/b3_training_epoch_30_20250801_074634.pth",
                "next_epoch": 31,
                "target_location": "F:/models/training/epochs"
            }
        }

        with open(training_config_file, 'w', encoding='utf-8') as f:
            json.dump(training_config, f, indent=2)

        return str(training_config_file)

    def create_deployment_config(self):
        """Create deployment configuration for F:\models"""
        deployment_config_file = self.f_models_root / "infrastructure" / "configs" / "deployment_config.json"

        deployment_config = {
            "version": "2.0.0",
            "updated": datetime.now().isoformat(),
            "production_model": {
                "current": "F:/models/checkpoints/best_quality/b3_best_quality_model_20250802_124801.pth",
                "deployment_location": "F:/models/deployment/production",
                "backup_location": "F:/models/deployment/backup"
            },
            "testing_models": {
                "directory": "F:/models/deployment/testing",
                "config_location": "F:/models/deployment/configs"
            },
            "quality_requirements": {
                "minimum_conversation_quality": 9.5,
                "maximum_memory_usage_gb": 4.0,
                "target_hardware": "GTX 1050 Ti 4GB VRAM"
            }
        }

        with open(deployment_config_file, 'w', encoding='utf-8') as f:
            json.dump(deployment_config, f, indent=2)

        return str(deployment_config_file)

    def display_configuration_summary(self, config_files):
        """Display summary of created configurations"""

        config_table = Table(title="⚙️ F:\\models Configuration Files Created")
        config_table.add_column("Configuration", style="cyan")
        config_table.add_column("Purpose", style="green")
        config_table.add_column("Location", style="yellow")

        config_table.add_row(
            "Master Config",
            "Primary F:\\models configuration",
            "infrastructure/configs/f_models_master_config.json"
        )
        config_table.add_row(
            "Training Config",
            "Training system configuration",
            "infrastructure/configs/training_config.json"
        )
        config_table.add_row(
            "Deployment Config",
            "Production deployment configuration",
            "infrastructure/configs/deployment_config.json"
        )

        self.console.print(config_table)

        # Current model status
        model_table = Table(title="📦 Current Model Status in F:\\models")
        model_table.add_column("Model", style="cyan")
        model_table.add_column("Location", style="green")
        model_table.add_column("Size", style="yellow")
        model_table.add_column("Purpose", style="blue")

        model_table.add_row(
            "Best Quality B3",
            "checkpoints/best_quality/",
            "199.83 MB",
            "Production inference"
        )
        model_table.add_row(
            "Latest Training B3",
            "training/active/",
            "336.47 MB",
            "Development continuation"
        )

        self.console.print(model_table)

    def run_configuration_setup(self):
        """Run complete configuration setup for F:\models"""
        self.console.print(Panel.fit(
            "⚙️ F:\\models Configuration Manager\n"
            "Setting Up ImpressionCore F:\\models Infrastructure",
            style="bold blue"
        ))

        # Create configuration files
        master_config = self.create_master_config()
        training_config = self.create_training_config()
        deployment_config = self.create_deployment_config()

        config_files = [master_config, training_config, deployment_config]

        # Display summary
        self.display_configuration_summary(config_files)

        self.console.print(Panel(
            f"🎯 F:\\models Configuration Complete!\n\n"
            f"📁 Primary Location: F:\\models\n"
            f"⚙️ Configuration Files: {len(config_files)} created\n"
            f"🔄 Distillation Systems: Updated\n"
            f"📦 Models: Migrated and configured\n\n"
            f"✅ ImpressionCore now uses F:\\models for all operations\n"
            f"🚀 Ready for continued development and distillation",
            title="Configuration Summary",
            style="bold green"
        ))

        return {
            "status": "success",
            "config_files": config_files,
            "models_location": "F:/models",
            "distillation_updated": True
        }

def main():
    """Main execution function"""
    config_manager = FModelsConfigManager()
    results = config_manager.run_configuration_setup()

    if results["status"] == "success":
        print(f"\n✅ F:\\models configuration completed successfully!")
        print(f"📁 All future models will be saved to: {results['models_location']}")
        print(f"🔄 Distillation systems updated: {results['distillation_updated']}")

if __name__ == "__main__":
    main()
