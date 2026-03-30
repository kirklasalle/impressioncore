#!/usr/bin/env python3
"""
ImpressionCore Storage Management System
Monitors and manages storage requirements for model training.
"""

import os
import shutil
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import psutil

class StorageManager:
    """Manages storage requirements and optimization for model training."""
    
    def __init__(self, project_root: str = "d:/Projects/impressioncore", backup_drive: str = "E:"):
        self.project_root = Path(project_root)
        self.primary_drive = "D:"
        self.backup_drive = backup_drive
        
        # Primary storage paths
        self.data_dir = self.project_root / "data"
        self.models_dir = self.project_root / "models"
        self.checkpoints_dir = self.project_root / "checkpoints"
        self.logs_dir = self.project_root / "logs"
        
        # Backup storage paths (500GB drive)
        self.backup_root = Path(f"{backup_drive}/impressioncore_training")
        self.backup_data_dir = self.backup_root / "data"
        self.backup_models_dir = self.backup_root / "models"
        self.backup_checkpoints_dir = self.backup_root / "checkpoints"
        
        # Storage thresholds (in GB)
        self.min_free_space = 50  # Minimum free space to maintain
        self.training_space_needed = 500  # Minimum space needed for training
        self.checkpoint_retention = 5  # Number of checkpoints to keep
        
        # Training data size estimates (in GB)
        self.training_requirements = {
            "small_model": 7.5,
            "medium_model": 35,
            "large_model": 135,
            "knowledge_distillation": 108,
            "text_corpus": 50,
            "image_dataset": 200,
            "multimodal_dataset": 300
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for storage operations."""
        log_file = self.project_root / "src/memlog/storage_management.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_drive_usage(self) -> Dict[str, Dict[str, float]]:
        """Get usage statistics for all drives."""
        drives = {}
        
        # Get all available drives
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                drive_letter = partition.mountpoint.split(':')[0]
                
                drives[drive_letter] = {
                    'total_gb': usage.total / (1024**3),
                    'used_gb': usage.used / (1024**3),
                    'free_gb': usage.free / (1024**3),
                    'percent_used': (usage.used / usage.total) * 100
                }
            except PermissionError:
                continue
                
        return drives
    
    def analyze_storage_requirements(self) -> Dict[str, float]:
        """Analyze current and projected storage requirements."""
        requirements = {
            'current_project_size': self.get_directory_size(self.project_root),
            'training_data_needed': 300,  # GB
            'model_weights_needed': 50,   # GB
            'checkpoints_needed': 30,     # GB
            'working_space_needed': 100,  # GB
            'total_needed': 0
        }
        
        requirements['total_needed'] = sum([
            requirements['training_data_needed'],
            requirements['model_weights_needed'],
            requirements['checkpoints_needed'],
            requirements['working_space_needed']
        ])
        
        return requirements
    
    def get_directory_size(self, path: Path) -> float:
        """Get directory size in GB."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
        except (OSError, FileNotFoundError):
            pass
        
        return total_size / (1024**3)  # Convert to GB
    
    def check_training_readiness(self) -> Tuple[bool, List[str]]:
        """Check if system is ready for training based on storage."""
        drives = self.get_drive_usage()
        requirements = self.analyze_storage_requirements()
        issues = []
        
        # Find drive with most free space
        best_drive = max(drives.keys(), key=lambda x: drives[x]['free_gb'])
        best_drive_free = drives[best_drive]['free_gb']
        
        if best_drive_free < requirements['total_needed']:
            issues.append(f"Insufficient storage: Need {requirements['total_needed']:.1f}GB, have {best_drive_free:.1f}GB")
        
        if best_drive_free < self.training_space_needed:
            issues.append(f"Training space insufficient: Need {self.training_space_needed}GB minimum")
        
        # Check if any drive is critically low
        for drive, stats in drives.items():
            if stats['free_gb'] < self.min_free_space:
                issues.append(f"Drive {drive}: critically low space ({stats['free_gb']:.1f}GB free)")
        
        return len(issues) == 0, issues
    
    def optimize_storage(self):
        """Optimize storage by cleaning up unnecessary files."""
        self.logger.info("Starting storage optimization...")
        
        # Clean old checkpoints
        self.cleanup_old_checkpoints()
        
        # Clean temporary files
        self.cleanup_temp_files()
        
        # Clean old logs
        self.cleanup_old_logs()
        
        self.logger.info("Storage optimization completed")
    
    def cleanup_old_checkpoints(self):
        """Clean up old checkpoint files, keeping only the most recent ones."""
        if not self.checkpoints_dir.exists():
            return
        
        # Get all checkpoint files
        checkpoint_files = list(self.checkpoints_dir.glob("*.pt"))
        checkpoint_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Keep only the most recent checkpoints
        if len(checkpoint_files) > self.checkpoint_retention:
            for old_checkpoint in checkpoint_files[self.checkpoint_retention:]:
                try:
                    old_checkpoint.unlink()
                    self.logger.info(f"Deleted old checkpoint: {old_checkpoint.name}")
                except OSError as e:
                    self.logger.error(f"Failed to delete {old_checkpoint}: {e}")
    
    def cleanup_temp_files(self):
        """Clean up temporary files and caches."""
        temp_patterns = [
            "**/*.tmp",
            "**/*.temp",
            "**/__pycache__",
            "**/.*cache*"
        ]
        
        for pattern in temp_patterns:
            for temp_file in self.project_root.glob(pattern):
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                    elif temp_file.is_dir():
                        shutil.rmtree(temp_file)
                    self.logger.info(f"Cleaned up: {temp_file}")
                except OSError as e:
                    self.logger.error(f"Failed to clean {temp_file}: {e}")
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up log files older than specified days."""
        if not self.logs_dir.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        
        for log_file in self.logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log: {log_file.name}")
                except OSError as e:
                    self.logger.error(f"Failed to delete {log_file}: {e}")
    
    def recommend_storage_setup(self) -> Dict[str, str]:
        """Recommend optimal storage configuration."""
        drives = self.get_drive_usage()
        requirements = self.analyze_storage_requirements()
        
        # Find best drive for each purpose
        best_drive_for_data = max(drives.keys(), key=lambda x: drives[x]['free_gb'])
        
        recommendations = {
            'training_data': f"{best_drive_for_data}: drive (most free space: {drives[best_drive_for_data]['free_gb']:.1f}GB)",
            'model_storage': f"{best_drive_for_data}: drive",
            'checkpoints': f"{best_drive_for_data}: drive",
            'urgent_action': "NONE"
        }
        
        if drives[best_drive_for_data]['free_gb'] < requirements['total_needed']:
            recommendations['urgent_action'] = f"ADD {requirements['total_needed'] - drives[best_drive_for_data]['free_gb']:.1f}GB STORAGE"
        
        return recommendations
    
    def generate_storage_report(self) -> str:
        """Generate a comprehensive storage report."""
        drives = self.get_drive_usage()
        requirements = self.analyze_storage_requirements()
        ready, issues = self.check_training_readiness()
        recommendations = self.recommend_storage_setup()
        
        report = f"""
=== IMPRESSIONCORE STORAGE ANALYSIS REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CURRENT DRIVE STATUS:
"""
        
        for drive, stats in drives.items():
            report += f"  {drive}: Drive - {stats['free_gb']:.1f}GB free / {stats['total_gb']:.1f}GB total ({stats['percent_used']:.1f}% used)\n"
        
        report += f"""
STORAGE REQUIREMENTS:
  Current Project Size: {requirements['current_project_size']:.1f}GB
  Training Data Needed: {requirements['training_data_needed']:.1f}GB
  Model Weights Needed: {requirements['model_weights_needed']:.1f}GB
  Checkpoints Needed: {requirements['checkpoints_needed']:.1f}GB
  Working Space Needed: {requirements['working_space_needed']:.1f}GB
  TOTAL NEEDED: {requirements['total_needed']:.1f}GB

TRAINING READINESS: {"✓ READY" if ready else "✗ NOT READY"}
"""
        
        if issues:
            report += "\nISSUES FOUND:\n"
            for issue in issues:
                report += f"  - {issue}\n"
        
        report += f"""
RECOMMENDATIONS:
  Training Data: {recommendations['training_data']}
  Model Storage: {recommendations['model_storage']}  
  Checkpoints: {recommendations['checkpoints']}
  Urgent Action: {recommendations['urgent_action']}

"""
        
        return report
    
    def analyze_multi_drive_setup(self) -> Dict:
        """Analyze storage setup including the 500GB backup drive."""
        drives = self.get_drive_usage()
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "drives": drives,
            "primary_drive": self.primary_drive,
            "backup_drive": self.backup_drive,
            "storage_strategy": "single_drive",  # Default
            "recommendations": [],
            "training_feasibility": {}
        }
        
        # Get specific drive info
        primary_info = drives.get("D", {})
        backup_info = drives.get(self.backup_drive.replace(":", ""), {})
        
        primary_free = primary_info.get("free_gb", 0)
        backup_free = backup_info.get("free_gb", 0)
        total_free = primary_free + backup_free
        
        # Analyze each training scenario
        for scenario, required_gb in self.training_requirements.items():
            feasible_primary = primary_free >= required_gb
            feasible_backup = backup_free >= required_gb
            feasible_combined = total_free >= required_gb
            
            analysis["training_feasibility"][scenario] = {
                "required_gb": required_gb,
                "primary_only": feasible_primary,
                "backup_only": feasible_backup,
                "multi_drive": feasible_combined,
                "recommended_drive": self.primary_drive if feasible_primary else self.backup_drive
            }
        
        # Storage strategy recommendations
        if primary_free < 100:  # Less than 100GB free on primary
            analysis["storage_strategy"] = "multi_drive"
            analysis["recommendations"].append(f"⚠️ Primary drive low on space ({primary_free:.1f}GB free)")
            analysis["recommendations"].append(f"✅ Use {self.backup_drive} (500GB) for training data")
        
        if backup_free >= 400:  # Plenty of space on backup
            analysis["recommendations"].append(f"💾 Backup drive has {backup_free:.1f}GB free - excellent for large training runs")
        
        # Specific recommendations
        if total_free >= 500:
            analysis["recommendations"].append("✅ Sufficient total storage for large-scale training")
        else:
            analysis["recommendations"].append("❌ May need additional storage for very large models")
        
        return analysis
    
    def setup_backup_drive_structure(self) -> Dict[str, Path]:
        """Setup directory structure on the 500GB backup drive."""
        self.logger.info(f"Setting up training structure on {self.backup_drive}")
        
        directories = {
            "root": self.backup_root,
            "data": self.backup_data_dir,
            "models": self.backup_models_dir,
            "checkpoints": self.backup_checkpoints_dir,
            "training_cache": self.backup_root / "cache",
            "logs": self.backup_root / "logs",
            "exports": self.backup_root / "exports"
        }
        
        # Create all directories
        for name, path in directories.items():
            try:
                path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created: {path}")
            except Exception as e:
                self.logger.error(f"Failed to create {path}: {e}")
        
        # Create a README file explaining the structure
        readme_content = f"""# ImpressionCore Training Data - {self.backup_drive}

This directory contains training data and models for ImpressionCore.

## Structure:
- data/: Training datasets
- models/: Trained model files
- checkpoints/: Training checkpoints
- cache/: Temporary training cache
- logs/: Training logs
- exports/: Final exported models

## Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
## Drive Capacity: 500GB
## Purpose: Large-scale model training storage
"""
        
        readme_path = self.backup_root / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        return directories
    
    def recommend_storage_strategy(self, training_type: str = "knowledge_distillation") -> Dict:
        """Recommend optimal storage strategy for specific training type."""
        analysis = self.analyze_multi_drive_setup()
        drives = analysis["drives"]
        
        required_gb = self.training_requirements.get(training_type, 100)
        
        strategy = {
            "training_type": training_type,
            "required_space_gb": required_gb,
            "recommended_setup": {},
            "data_placement": {},
            "performance_notes": []
        }
        
        primary_free = drives.get("D", {}).get("free_gb", 0)
        backup_free = drives.get(self.backup_drive.replace(":", ""), {}).get("free_gb", 0)
        
        if primary_free >= required_gb:
            # Primary drive can handle it
            strategy["recommended_setup"] = {
                "primary_drive": "training_data + models + checkpoints",
                "backup_drive": "backup copies + archives",
                "performance": "optimal"
            }
            strategy["data_placement"]["training_data"] = self.data_dir
            strategy["data_placement"]["models"] = self.models_dir
            strategy["data_placement"]["checkpoints"] = self.checkpoints_dir
            
        elif backup_free >= required_gb:
            # Use backup drive for training
            strategy["recommended_setup"] = {
                "primary_drive": "code + configs + small files",
                "backup_drive": "training_data + models + checkpoints",
                "performance": "good (may have slightly slower I/O)"
            }
            strategy["data_placement"]["training_data"] = self.backup_data_dir
            strategy["data_placement"]["models"] = self.backup_models_dir
            strategy["data_placement"]["checkpoints"] = self.backup_checkpoints_dir
            
            strategy["performance_notes"].append(f"Using {self.backup_drive} for training data")
            strategy["performance_notes"].append("Consider SSD if backup drive is HDD")
            
        else:
            # Need to split across drives
            strategy["recommended_setup"] = {
                "primary_drive": "active training data + current model",
                "backup_drive": "archived data + old checkpoints + exports",
                "performance": "requires active management"
            }
            strategy["performance_notes"].append("⚠️ Need to actively manage data between drives")
            strategy["performance_notes"].append("Consider cleanup of old data")
        
        return strategy

def main():
    """Main function to run storage analysis."""
    storage_manager = StorageManager()
    
    print("=== IMPRESSIONCORE STORAGE ANALYSIS ===")
    print(storage_manager.generate_storage_report())
    
    # Optimize storage
    storage_manager.optimize_storage()
    
    # Save report to file
    report_file = storage_manager.project_root / "src/memlog/storage_analysis_report.txt"
    with open(report_file, 'w') as f:
        f.write(storage_manager.generate_storage_report())
    
    print(f"\nDetailed report saved to: {report_file}")

if __name__ == "__main__":
    main()
