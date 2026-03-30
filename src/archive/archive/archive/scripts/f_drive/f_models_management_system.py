
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #deployment #python #source_code #src/scripts/f_drive/f_models_management_system.py #testing #training
**Category:** Source Code
**Status:** Deprecated
"""



import os
import sys
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

@dataclass
class ModelInfo:
    """Model information structure"""
    name: str
    version: str
    path: Path
    size_mb: float
    created: datetime
    modified: datetime
    type: str  # checkpoint, production, distilled, archived
    performance_score: Optional[float] = None
    training_epoch: Optional[int] = None
    parent_model: Optional[str] = None
    description: Optional[str] = None

@dataclass
class TrainingSession:
    """Training session information"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    model_name: str
    epochs_completed: int
    best_checkpoint: Optional[str]
    final_loss: Optional[float]
    status: str  # active, completed, failed, paused

class FModelsManager:
    """Centralized F:/models management system"""

    def __init__(self):
        self.console = Console()
        self.f_models_root = Path("F:/models")
        self.structure = {
            "checkpoints": self.f_models_root / "checkpoints",
            "production": self.f_models_root / "production",
            "training": self.f_models_root / "training",
            "distillation": self.f_models_root / "distillation",
            "archives": self.f_models_root / "archives",
            "deployment": self.f_models_root / "deployment",
            "experiments": self.f_models_root / "experiments"
        }

        # Create directory structure
        self.ensure_directory_structure()

        # Model registry
        self.model_registry = {}
        self.training_sessions = {}

        # Load existing registries
        self.load_registries()

    def ensure_directory_structure(self):
        """Ensure all required directories exist"""
        for name, path in self.structure.items():
            path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        subdirs = [
            "checkpoints/b3",
            "checkpoints/b2",
            "checkpoints/b1",
            "training/active",
            "training/completed",
            "training/logs",
            "distillation/ollama_progressive",
            "distillation/remote_api",
            "distillation/enhanced_models",
            "production/current",
            "production/candidates",
            "archives/deprecated",
            "archives/backups",
            "deployment/ready",
            "deployment/testing",
            "experiments/research"
        ]

        for subdir in subdirs:
            (self.f_models_root / subdir).mkdir(parents=True, exist_ok=True)

    def register_model(self, model_path: Union[str, Path], model_type: str = "checkpoint",
                      description: str = None, performance_score: float = None) -> str:
        """Register a new model in the system"""
        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        # Generate model info
        model_info = ModelInfo(
            name=model_path.stem,
            version=datetime.now().strftime("%Y%m%d_%H%M%S"),
            path=model_path,
            size_mb=round(model_path.stat().st_size / (1024 * 1024), 2),
            created=datetime.fromtimestamp(model_path.stat().st_ctime),
            modified=datetime.fromtimestamp(model_path.stat().st_mtime),
            type=model_type,
            performance_score=performance_score,
            description=description
        )

        # Extract training epoch if present in filename
        if "epoch" in model_info.name.lower():
            try:
                epoch_part = [p for p in model_info.name.split("_") if "epoch" in p.lower()]
                if epoch_part:
                    model_info.training_epoch = int(''.join(filter(str.isdigit, epoch_part[0])))
            except (ValueError, IndexError):
                pass

        # Generate unique model ID
        model_id = f"{model_info.name}_{model_info.version}"
        self.model_registry[model_id] = model_info

        self.console.print(f"✅ Model registered: {model_id} ({model_info.size_mb} MB)")
        return model_id

    def organize_model(self, model_id: str, target_type: str = None) -> Path:
        """Organize model into appropriate F:/models subdirectory"""
        if model_id not in self.model_registry:
            raise ValueError(f"Model not found in registry: {model_id}")

        model_info = self.model_registry[model_id]
        current_path = model_info.path

        # Determine target directory
        if target_type:
            model_info.type = target_type

        if model_info.type == "production":
            target_dir = self.structure["production"] / "current"
        elif model_info.type == "checkpoint":
            # Organize by model family (b3, b2, b1)
            family = "b3"  # Default
            if "b1" in model_info.name.lower():
                family = "b1"
            elif "b2" in model_info.name.lower():
                family = "b2"
            target_dir = self.structure["checkpoints"] / family
        elif model_info.type == "distilled":
            target_dir = self.structure["distillation"] / "enhanced_models"
        elif model_info.type == "archived":
            target_dir = self.structure["archives"] / "deprecated"
        else:
            target_dir = self.structure["training"] / "completed"

        # Create target path
        target_path = target_dir / current_path.name

        # Move file if needed
        if current_path != target_path:
            if not target_path.exists():
                shutil.move(str(current_path), str(target_path))
                model_info.path = target_path
                self.console.print(f"📁 Model organized: {target_path}")
            else:
                self.console.print(f"⚠️ Target already exists: {target_path}")

        return target_path

    def start_training_session(self, model_name: str) -> str:
        """Start a new training session"""
        session_id = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session = TrainingSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            model_name=model_name,
            epochs_completed=0,
            best_checkpoint=None,
            final_loss=None,
            status="active"
        )

        self.training_sessions[session_id] = session

        # Create session directory
        session_dir = self.structure["training"] / "active" / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        self.console.print(f"🚀 Training session started: {session_id}")
        return session_id

    def update_training_session(self, session_id: str, **kwargs):
        """Update training session information"""
        if session_id not in self.training_sessions:
            raise ValueError(f"Training session not found: {session_id}")

        session = self.training_sessions[session_id]
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

    def complete_training_session(self, session_id: str, final_loss: float = None,
                                 best_checkpoint: str = None):
        """Complete a training session"""
        if session_id not in self.training_sessions:
            raise ValueError(f"Training session not found: {session_id}")

        session = self.training_sessions[session_id]
        session.end_time = datetime.now()
        session.status = "completed"
        session.final_loss = final_loss
        session.best_checkpoint = best_checkpoint

        # Move from active to completed
        active_dir = self.structure["training"] / "active" / session_id
        completed_dir = self.structure["training"] / "completed" / session_id

        if active_dir.exists():
            shutil.move(str(active_dir), str(completed_dir))

        self.console.print(f"✅ Training session completed: {session_id}")

    def get_best_model(self, model_type: str = "production") -> Optional[ModelInfo]:
        """Get the best model of specified type"""
        candidates = [m for m in self.model_registry.values() if m.type == model_type]

        if not candidates:
            return None

        # Sort by performance score, then by creation date
        candidates.sort(key=lambda x: (
            x.performance_score or 0,
            x.created
        ), reverse=True)

        return candidates[0]

    def create_deployment_package(self, model_id: str, deployment_name: str = None) -> Path:
        """Create a deployment package for a model"""
        if model_id not in self.model_registry:
            raise ValueError(f"Model not found: {model_id}")

        model_info = self.model_registry[model_id]

        if not deployment_name:
            deployment_name = f"deploy_{model_info.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create deployment directory
        deploy_dir = self.structure["deployment"] / "ready" / deployment_name
        deploy_dir.mkdir(parents=True, exist_ok=True)

        # Copy model file
        model_copy = deploy_dir / model_info.path.name
        shutil.copy2(str(model_info.path), str(model_copy))

        # Create deployment manifest
        manifest = {
            "deployment_name": deployment_name,
            "model_id": model_id,
            "model_info": asdict(model_info),
            "deployment_created": datetime.now().isoformat(),
            "deployment_path": str(model_copy),
            "ready_for_production": True
        }

        manifest_file = deploy_dir / "deployment_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, default=str)

        self.console.print(f"📦 Deployment package created: {deploy_dir}")
        return deploy_dir

    def archive_old_models(self, keep_latest: int = 5, days_old: int = 30):
        """Archive old models to free up space"""
        archived_count = 0
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)

        # Group models by family and type
        model_groups = {}
        for model_id, model_info in self.model_registry.items():
            key = f"{model_info.type}_{model_info.name.split('_')[0]}"
            if key not in model_groups:
                model_groups[key] = []
            model_groups[key].append((model_id, model_info))

        # Archive old models from each group
        for group_key, models in model_groups.items():
            # Sort by creation date (newest first)
            models.sort(key=lambda x: x[1].created, reverse=True)

            # Keep latest N models, archive the rest if they're old enough
            for i, (model_id, model_info) in enumerate(models[keep_latest:], keep_latest):
                if model_info.created.timestamp() < cutoff_date:
                    # Move to archive
                    archive_path = self.structure["archives"] / "deprecated" / model_info.path.name
                    shutil.move(str(model_info.path), str(archive_path))
                    model_info.path = archive_path
                    model_info.type = "archived"
                    archived_count += 1

        self.console.print(f"📚 Archived {archived_count} old models")
        return archived_count

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics for F:/models"""
        stats = {}
        total_size = 0

        for name, path in self.structure.items():
            if path.exists():
                size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                file_count = len(list(path.rglob('*')))
                stats[name] = {
                    "size_gb": round(size / (1024**3), 2),
                    "size_mb": round(size / (1024**2), 2),
                    "file_count": file_count
                }
                total_size += size

        stats["total"] = {
            "size_gb": round(total_size / (1024**3), 2),
            "size_mb": round(total_size / (1024**2), 2),
            "directories": len(self.structure)
        }

        return stats

    def display_model_inventory(self):
        """Display comprehensive model inventory"""
        table = Table(title="🤖 F:/models Model Inventory")
        table.add_column("Model ID", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Size (MB)", style="yellow")
        table.add_column("Performance", style="magenta")
        table.add_column("Created", style="blue")
        table.add_column("Location", style="white")

        for model_id, model_info in sorted(self.model_registry.items(),
                                         key=lambda x: x[1].created, reverse=True):
            table.add_row(
                model_id[:30] + "..." if len(model_id) > 30 else model_id,
                model_info.type,
                str(model_info.size_mb),
                f"{model_info.performance_score:.3f}" if model_info.performance_score else "N/A",
                model_info.created.strftime("%Y-%m-%d %H:%M"),
                str(model_info.path.relative_to(self.f_models_root))
            )

        self.console.print(table)

    def display_storage_stats(self):
        """Display storage statistics"""
        stats = self.get_storage_stats()

        table = Table(title="💾 F:/models Storage Statistics")
        table.add_column("Directory", style="cyan")
        table.add_column("Size (GB)", style="green")
        table.add_column("Size (MB)", style="yellow")
        table.add_column("Files", style="blue")

        for name, data in stats.items():
            if name != "total":
                table.add_row(
                    name,
                    str(data["size_gb"]),
                    str(data["size_mb"]),
                    str(data["file_count"])
                )

        # Add total row
        total = stats["total"]
        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{total['size_gb']}[/bold]",
            f"[bold]{total['size_mb']}[/bold]",
            f"[bold]{total['directories']} dirs[/bold]"
        )

        self.console.print(table)

    def save_registries(self):
        """Save model and training registries"""
        # Save model registry
        registry_file = self.f_models_root / "model_registry.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump({k: asdict(v) for k, v in self.model_registry.items()},
                     f, indent=2, default=str)

        # Save training sessions
        sessions_file = self.f_models_root / "training_sessions.json"
        with open(sessions_file, 'w', encoding='utf-8') as f:
            json.dump({k: asdict(v) for k, v in self.training_sessions.items()},
                     f, indent=2, default=str)

    def load_registries(self):
        """Load existing registries"""
        # Load model registry
        registry_file = self.f_models_root / "model_registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        # Convert back to ModelInfo
                        v['path'] = Path(v['path'])
                        v['created'] = datetime.fromisoformat(v['created'])
                        v['modified'] = datetime.fromisoformat(v['modified'])
                        self.model_registry[k] = ModelInfo(**v)
            except Exception as e:
                self.console.print(f"⚠️ Could not load model registry: {e}")

        # Load training sessions
        sessions_file = self.f_models_root / "training_sessions.json"
        if sessions_file.exists():
            try:
                with open(sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        # Convert back to TrainingSession
                        v['start_time'] = datetime.fromisoformat(v['start_time'])
                        if v['end_time']:
                            v['end_time'] = datetime.fromisoformat(v['end_time'])
                        self.training_sessions[k] = TrainingSession(**v)
            except Exception as e:
                self.console.print(f"⚠️ Could not load training sessions: {e}")

def main():
    """Main execution function"""
    console = Console()

    console.print(Panel.fit(
        "🤖 F:/models Management System\n"
        "Centralized ImpressionCore Model Infrastructure",
        style="bold blue"
    ))

    # Initialize manager
    manager = FModelsManager()

    # Scan and register existing models
    console.print("🔍 Scanning for existing models...")

    # Check current best model
    best_model_path = Path("F:/models/production/b3_best_quality_model_20250802_124801.pth")
    if best_model_path.exists():
        model_id = manager.register_model(
            best_model_path,
            model_type="production",
            description="Best quality B3 model from August 2, 2025",
            performance_score=0.95
        )
        console.print(f"✅ Registered current best model: {model_id}")

    # Display current state
    manager.display_model_inventory()
    manager.display_storage_stats()

    # Save registries
    manager.save_registries()

    console.print("\n🎯 F:/models management system ready!")
    console.print("📍 All future models, checkpoints, and training will use F:/models structure")

if __name__ == "__main__":
    main()
