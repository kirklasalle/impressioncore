#!/usr/bin/env python3
"""
ImpressionCore Training Storage Manager
Dedicated storage management for the 476GB ImpressionCore drive (F:)

This module manages storage requirements for serious model training operations,
including data preparation, model checkpoints, and training artifacts.

Author: GitHub Copilot
Date: 2025-06-13
Target Hardware: NVIDIA GTX 1050 Ti (4GB VRAM), 32GB RAM, 476GB dedicated training drive
"""

import os
import sys
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class StorageRequirement:
    """Storage requirement specification for training components"""
    component: str
    description: str
    min_size_gb: float
    recommended_size_gb: float
    max_size_gb: float
    priority: int  # 1=critical, 2=important, 3=optional

@dataclass
class DriveInfo:
    """Drive information and capacity"""
    drive_letter: str
    total_gb: float
    free_gb: float
    used_gb: float
    filesystem: str
    label: str

class TrainingStorageManager:
    """Manages storage for ImpressionCore model training operations"""
    
    def __init__(self, training_drive: str = "F:", project_root: str = None):
        self.training_drive = training_drive
        self.training_path = Path(f"/{training_drive.lower().rstrip(':')}")
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        # Storage allocations for training components
        self.storage_requirements = [
            StorageRequirement("training_data", "Raw training datasets", 10.0, 50.0, 200.0, 1),
            StorageRequirement("processed_data", "Preprocessed and tokenized data", 5.0, 25.0, 100.0, 1),
            StorageRequirement("model_checkpoints", "Model checkpoints during training", 2.0, 20.0, 80.0, 1),
            StorageRequirement("embeddings", "Pre-computed embeddings", 1.0, 10.0, 50.0, 2),
            StorageRequirement("validation_data", "Validation and test datasets", 2.0, 10.0, 30.0, 2),
            StorageRequirement("logs_metrics", "Training logs and metrics", 0.5, 2.0, 10.0, 2),
            StorageRequirement("temp_cache", "Temporary processing cache", 5.0, 15.0, 50.0, 3),
            StorageRequirement("backup_models", "Model backups and snapshots", 5.0, 30.0, 100.0, 3),
        ]
          # Initialize directory structure
        self.setup_training_directories()
    
    def get_drive_info(self, drive_path: str) -> DriveInfo:
        """Get comprehensive drive information"""
        try:
            # For Windows F: drive, use the proper path
            if drive_path.startswith('/f') or drive_path.startswith('\\f'):
                drive_path = "F:\\"
            
            total, used, free = shutil.disk_usage(drive_path)
            return DriveInfo(
                drive_letter=drive_path,
                total_gb=total / (1024**3),
                free_gb=free / (1024**3),
                used_gb=used / (1024**3),
                filesystem="NTFS",
                label="ImpressionCore"
            )
        except Exception as e:
            print(f"Error getting drive info for {drive_path}: {e}")
            return DriveInfo(drive_path, 0, 0, 0, "Unknown", "Unknown")
    
    def setup_training_directories(self):
        """Setup the training directory structure on the dedicated drive"""
        directories = [
            "training_data/raw",
            "training_data/processed",
            "training_data/validation",
            "models/checkpoints",
            "models/final",
            "models/backup",
            "embeddings/cache",
            "embeddings/precomputed",
            "logs/training",
            "logs/metrics",
            "logs/tensorboard",
            "temp/processing",
            "temp/cache",
            "experiments",
            "datasets/custom",
            "datasets/public"
        ]
        
        base_path = self.training_path / "ImpressionCore_Training"
        
        for directory in directories:
            dir_path = base_path / directory
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Created directory: {dir_path}")
            except Exception as e:
                print(f"✗ Failed to create directory {dir_path}: {e}")
    
    def calculate_storage_plan(self) -> Dict:
        """Calculate optimal storage allocation based on available space"""
        drive_info = self.get_drive_info(str(self.training_path))
        available_space = drive_info.free_gb
        
        # Calculate different scenarios
        scenarios = {
            "conservative": 0.4,  # Use 40% of available space
            "balanced": 0.6,     # Use 60% of available space
            "aggressive": 0.8    # Use 80% of available space
        }
        
        storage_plan = {
            "drive_info": asdict(drive_info),
            "scenarios": {}
        }
        
        for scenario_name, usage_factor in scenarios.items():
            usable_space = available_space * usage_factor
            scenario_plan = {
                "total_allocated_gb": usable_space,
                "components": {}
            }
            
            # Allocate space based on priorities
            remaining_space = usable_space
            
            # Priority 1 (Critical) - allocate recommended amounts
            for req in [r for r in self.storage_requirements if r.priority == 1]:
                allocated = min(req.recommended_size_gb, remaining_space * 0.3)
                scenario_plan["components"][req.component] = {
                    "allocated_gb": allocated,
                    "description": req.description,
                    "priority": req.priority
                }
                remaining_space -= allocated
            
            # Priority 2 (Important) - allocate based on remaining space
            priority2_reqs = [r for r in self.storage_requirements if r.priority == 2]
            if priority2_reqs and remaining_space > 0:
                space_per_p2 = remaining_space * 0.5 / len(priority2_reqs)
                for req in priority2_reqs:
                    allocated = min(req.recommended_size_gb, space_per_p2)
                    scenario_plan["components"][req.component] = {
                        "allocated_gb": allocated,
                        "description": req.description,
                        "priority": req.priority
                    }
                    remaining_space -= allocated
            
            # Priority 3 (Optional) - use remaining space
            priority3_reqs = [r for r in self.storage_requirements if r.priority == 3]
            if priority3_reqs and remaining_space > 0:
                space_per_p3 = remaining_space / len(priority3_reqs)
                for req in priority3_reqs:
                    allocated = min(req.max_size_gb, space_per_p3)
                    scenario_plan["components"][req.component] = {
                        "allocated_gb": allocated,
                        "description": req.description,
                        "priority": req.priority
                    }
                    remaining_space -= allocated
            
            scenario_plan["reserved_space_gb"] = remaining_space
            storage_plan["scenarios"][scenario_name] = scenario_plan
        
        return storage_plan
    
    def estimate_training_data_size(self, model_type: str = "multimodal_llm") -> Dict:
        """Estimate data requirements for different model types"""
        
        training_estimates = {
            "small_llm": {
                "description": "Small language model (1-3B parameters)",
                "training_data_gb": 20,
                "processed_data_gb": 10,
                "checkpoints_gb": 15,
                "total_gb": 45
            },
            "medium_llm": {
                "description": "Medium language model (7-13B parameters)",
                "training_data_gb": 100,
                "processed_data_gb": 50,
                "checkpoints_gb": 40,
                "total_gb": 190
            },
            "multimodal_llm": {
                "description": "Multimodal LLM (text + vision)",
                "training_data_gb": 150,
                "processed_data_gb": 75,
                "checkpoints_gb": 60,
                "vision_data_gb": 50,
                "total_gb": 335
            },
            "specialized_model": {
                "description": "Specialized domain model",
                "training_data_gb": 30,
                "processed_data_gb": 15,
                "checkpoints_gb": 20,
                "total_gb": 65
            }
        }
        
        return training_estimates.get(model_type, training_estimates["multimodal_llm"])
    
    def create_training_workspace(self, project_name: str, model_type: str = "multimodal_llm"):
        """Create a dedicated training workspace for a specific project"""
        
        workspace_path = self.training_path / "ImpressionCore_Training" / "experiments" / project_name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create project structure
        project_dirs = [
            "data/raw",
            "data/processed",
            "data/validation",
            "models/checkpoints",
            "models/final",
            "logs",
            "configs",
            "scripts",
            "results"
        ]
        
        for directory in project_dirs:
            dir_path = workspace_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create project configuration
        config = {
            "project_name": project_name,
            "model_type": model_type,
            "created_timestamp": timestamp,
            "workspace_path": str(workspace_path),
            "estimated_requirements": self.estimate_training_data_size(model_type),
            "storage_allocation": self.calculate_storage_plan()
        }
        
        config_file = workspace_path / "project_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Created training workspace: {workspace_path}")
        return workspace_path, config
    
    def generate_storage_report(self) -> str:
        """Generate comprehensive storage analysis report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        drive_info = self.get_drive_info(str(self.training_path))
        storage_plan = self.calculate_storage_plan()
        
        report = f"""
# ImpressionCore Training Storage Analysis Report
Generated: {timestamp}

## Drive Information
- **Drive**: {drive_info.drive_letter} ({drive_info.label})
- **Total Capacity**: {drive_info.total_gb:.1f} GB
- **Available Space**: {drive_info.free_gb:.1f} GB
- **Used Space**: {drive_info.used_gb:.1f} GB
- **Filesystem**: {drive_info.filesystem}

## Storage Requirements Analysis

### Critical Components (Priority 1)
"""
        
        for req in [r for r in self.storage_requirements if r.priority == 1]:
            report += f"- **{req.component}**: {req.description}\n"
            report += f"  - Min: {req.min_size_gb}GB, Recommended: {req.recommended_size_gb}GB, Max: {req.max_size_gb}GB\n"
        
        report += "\n### Important Components (Priority 2)\n"
        for req in [r for r in self.storage_requirements if r.priority == 2]:
            report += f"- **{req.component}**: {req.description}\n"
            report += f"  - Min: {req.min_size_gb}GB, Recommended: {req.recommended_size_gb}GB, Max: {req.max_size_gb}GB\n"
        
        report += "\n### Optional Components (Priority 3)\n"
        for req in [r for r in self.storage_requirements if r.priority == 3]:
            report += f"- **{req.component}**: {req.description}\n"
            report += f"  - Min: {req.min_size_gb}GB, Recommended: {req.recommended_size_gb}GB, Max: {req.max_size_gb}GB\n"
        
        report += "\n## Storage Allocation Scenarios\n"
        
        for scenario_name, scenario in storage_plan["scenarios"].items():
            report += f"\n### {scenario_name.title()} Scenario ({scenario['total_allocated_gb']:.1f}GB)\n"
            for component, details in scenario["components"].items():
                report += f"- **{component}**: {details['allocated_gb']:.1f}GB - {details['description']}\n"
            report += f"- **Reserved Space**: {scenario['reserved_space_gb']:.1f}GB\n"
        
        report += "\n## Model Training Estimates\n"
        
        model_types = ["small_llm", "medium_llm", "multimodal_llm", "specialized_model"]
        for model_type in model_types:
            estimate = self.estimate_training_data_size(model_type)
            report += f"\n### {estimate['description']}\n"
            report += f"- Training Data: {estimate['training_data_gb']}GB\n"
            report += f"- Processed Data: {estimate['processed_data_gb']}GB\n"
            report += f"- Checkpoints: {estimate['checkpoints_gb']}GB\n"
            if 'vision_data_gb' in estimate:
                report += f"- Vision Data: {estimate['vision_data_gb']}GB\n"
            report += f"- **Total Estimated**: {estimate['total_gb']}GB\n"
        
        report += f"\n## Recommendations\n"
        report += f"- **Available Space**: {drive_info.free_gb:.1f}GB is excellent for serious model training\n"
        report += f"- **Recommended Scenario**: Balanced (uses ~{storage_plan['scenarios']['balanced']['total_allocated_gb']:.0f}GB)\n"
        report += f"- **Multiple Projects**: Can support 2-3 medium-scale training projects simultaneously\n"
        report += f"- **Backup Strategy**: Reserve 20% of space for model backups and snapshots\n"
        
        return report
    
    def cleanup_training_artifacts(self, older_than_days: int = 30):
        """Clean up old training artifacts to free space"""
        cutoff_time = datetime.now().timestamp() - (older_than_days * 24 * 3600)
        
        cleanup_paths = [
            self.training_path / "ImpressionCore_Training" / "temp",
            self.training_path / "ImpressionCore_Training" / "logs" / "training",
        ]
        
        total_freed = 0
        
        for path in cleanup_paths:
            if path.exists():
                for item in path.rglob("*"):
                    if item.is_file() and item.stat().st_mtime < cutoff_time:
                        try:
                            size = item.stat().st_size
                            item.unlink()
                            total_freed += size
                            print(f"Deleted: {item}")
                        except Exception as e:
                            print(f"Failed to delete {item}: {e}")
        
        print(f"Cleanup complete. Freed {total_freed / (1024**3):.2f}GB")
        return total_freed

def main():
    """Main function for standalone execution"""
    print("🚀 ImpressionCore Training Storage Manager")
    print("=" * 50)
    
    # Initialize storage manager
    manager = TrainingStorageManager()
    
    # Generate and display report
    report = manager.generate_storage_report()
    print(report)
    
    # Save report to file
    report_path = manager.project_root / "src" / "memlog" / f"storage_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📊 Full report saved to: {report_path}")
    
    # Create a sample training workspace
    workspace_path, config = manager.create_training_workspace("historic_gpu_distillation", "multimodal_llm")
    print(f"\n🏗️  Sample workspace created: {workspace_path}")

if __name__ == "__main__":
    main()
