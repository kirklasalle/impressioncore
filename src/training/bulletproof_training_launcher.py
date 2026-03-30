#!/usr/bin/env python3
"""
ImpressionCore-B1 Bulletproof Training Launcher
===============================================

Production launcher for bulletproof incremental multimodal training.
Uses real datasets: 400% scaled synthetic data, COCO, Common Voice.

Author: ImpressionCore Team
Date: 2025-01-06
Version: 1.1.0 - 400% Scaling Update
Hardware: NVIDIA GTX 1050 Ti (4GB VRAM) Optimized
"""

import asyncio
import sys
import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import torch

# Rich UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ImpressionCore imports
sys.path.append(str(Path(__file__).parent))
from src.training.bulletproof_incremental_trainer import BulletproofIncrementalTrainer
from src.training.multimodal_dataset_loaders import create_production_dataloaders


class ProductionTrainingLauncher:
    """
    Production launcher for ImpressionCore-B1 bulletproof training.
    
    Features:
    - Automatic dataset discovery (prioritizes 400% scaled datasets)
    - Hardware optimization
    - Real multimodal training
    - Bulletproof error handling
    - Rich progress monitoring
    """
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.logger = self._setup_logging()
        self.base_path = Path("d:/Projects/impressioncore")
        self.data_path = self.base_path / "src" / "data"
        
    def _setup_logging(self):
        """Setup production logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("ProductionLauncher")
    
    def _print_banner(self):
        """Print production launcher banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║         ImpressionCore-B1 Production Training Launcher      ║
║           🚀 400% SCALED MULTIMODAL TRAINING 🚀            ║
╠══════════════════════════════════════════════════════════════╣
║  📊 40+ Samples/Modality  🎯 GTX 1050 Ti Optimized         ║
║  🧠 Text + Image + Audio  🛡️ Bulletproof Error Handling   ║
║  ⚡ CUDA Acceleration     📈 Rich Progress Monitoring       ║
╚══════════════════════════════════════════════════════════════╝
"""
        if self.console:
            panel = Panel(
                banner,
                title="🚀 ImpressionCore-B1 400% Scaled Training",
                subtitle="Real Datasets, Real Training",
                style="bold blue"
            )
            self.console.print(panel)
        else:
            print(banner)        
        print(f"Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base Path: {self.base_path}")
        print()
    
    def discover_datasets(self) -> Dict[str, str]:
        """Discover available datasets for training with 400% scaling priority."""
        self.logger.info("🔍 Discovering datasets for bulletproof training...")
        
        datasets = {}
        dataset_info = []
        
        # Priority 1: 400% Scaled Real-World Datasets (40+ samples per modality)
        scaled_real_path = self.data_path / "real_datasets" / "synthetic_scaled"
        if scaled_real_path.exists():
            text_path = scaled_real_path / "text_samples"
            images_path = scaled_real_path / "images"
            audio_path = scaled_real_path / "audio"
            
            if all(p.exists() for p in [text_path, images_path, audio_path]):
                # Count samples
                text_count = len(list(text_path.glob("*.txt")))
                image_count = len(list(images_path.glob("*.jpg")))
                audio_count = len(list(audio_path.glob("*.wav")))
                
                if text_count >= 30 and image_count >= 30 and audio_count >= 30:
                    datasets["text"] = str(text_path)
                    datasets["images"] = str(images_path)
                    datasets["audio"] = str(audio_path)
                    
                    dataset_info.extend([
                        f"📝 Text: {text_count} files (400% scaled)",
                        f"🖼️  Images: {image_count} images (400% scaled)", 
                        f"🎵 Audio: {audio_count} files (400% scaled)"
                    ])
                    
                    self.logger.info(f"✅ Using 400% scaled datasets: {text_count}+{image_count}+{audio_count} samples")
                
        # Priority 2: COCO Real-World Images (if 400% scaled not available)
        if not datasets.get("images"):
            coco_path = self.data_path / "real_datasets" / "coco" / "val2017"
            if coco_path.exists():
                coco_images = list(coco_path.glob("*.jpg"))
                if len(coco_images) >= 10:  # At least 10 images
                    datasets["images"] = str(coco_path)
                    dataset_info.append(f"🌍 COCO Images: {len(coco_images)} real-world images")
                    self.logger.info(f"✅ Using COCO real-world images: {len(coco_images)} samples")
        
        # Priority 3: Common Voice Audio (if 400% scaled not available)
        if not datasets.get("audio"):
            cv_path = self.data_path / "real_datasets" / "common_voice"
            if cv_path.exists():
                # Check for extracted Common Voice data
                for lang_dir in cv_path.glob("*/clips"):
                    audio_files = list(lang_dir.glob("*.mp3"))
                    if len(audio_files) >= 10:  # At least 10 audio files
                        datasets["audio"] = str(lang_dir.parent)
                        dataset_info.append(f"🎤 Common Voice: {len(audio_files)} real audio samples")
                        self.logger.info(f"✅ Using Common Voice real audio: {len(audio_files)} samples")
                        break
        
        # Priority 4: Fallback to original minimal datasets
        if not all(k in datasets for k in ["text", "images", "audio"]):
            minimal_path = self.data_path / "minimal_datasets"
            if minimal_path.exists():
                if "text" not in datasets:
                    text_path = minimal_path / "text_samples"
                    if text_path.exists():
                        text_count = len(list(text_path.glob("*.txt")))
                        if text_count > 0:
                            datasets["text"] = str(text_path)
                            dataset_info.append(f"📝 Text: {text_count} files (minimal fallback)")
                
                if "images" not in datasets:
                    images_path = minimal_path / "images"
                    if images_path.exists():
                        image_count = len(list(images_path.glob("*.jpg")))
                        if image_count > 0:
                            datasets["images"] = str(images_path)
                            dataset_info.append(f"🖼️  Images: {image_count} images (minimal fallback)")
                
                if "audio" not in datasets:
                    audio_path = minimal_path / "audio"
                    if audio_path.exists():
                        audio_count = len(list(audio_path.glob("*.wav")))
                        if audio_count > 0:
                            datasets["audio"] = str(audio_path)
                            dataset_info.append(f"🎵 Audio: {audio_count} files (minimal fallback)")
        
        # Display discovered datasets
        if self.console and dataset_info:
            table = Table(title="🔍 Discovered Datasets", style="bold")
            table.add_column("Modality", style="cyan", width=15)
            table.add_column("Details", style="green")
            
            for info in dataset_info:
                emoji_split = info.split(": ", 1)
                if len(emoji_split) == 2:
                    table.add_row(emoji_split[0], emoji_split[1])
                else:
                    table.add_row("Unknown", info)
            
            self.console.print(table)
        else:
            print("\n🔍 Discovered Datasets:")
            for info in dataset_info:
                print(f"  {info}")
        
        # Verify we have all modalities
        if not all(k in datasets for k in ["text", "images", "audio"]):
            missing = [k for k in ["text", "images", "audio"] if k not in datasets]
            self.logger.warning(f"⚠️  Missing datasets for: {missing}. Creating dummy datasets...")
            datasets.update(self._create_dummy_dataset_config())
        
        return datasets
    
    def _create_dummy_dataset_config(self) -> Dict[str, str]:
        """Create dummy dataset configuration for testing."""
        self.logger.info("📦 Creating dummy datasets for missing modalities...")
        return {
            'use_dummy_data': True,
            'text_samples': 1000,
            'image_samples': 500,
            'audio_samples': 300
        }
    
    def create_training_config(self, datasets: Dict[str, str], args) -> Dict[str, Any]:
        """Create bulletproof training configuration."""
        config = {
            # Model architecture optimized for GTX 1050 Ti
            "model": {
                "hidden_size": 512,
                "num_layers": 6,
                "num_heads": 8,
                "vocab_size": 50257,
                "max_position_embeddings": 2048
            },
            
            # Training parameters for 4GB VRAM
            "training": {
                "epochs": args.epochs,
                "batch_size": 2,  # Small batch for 4GB VRAM
                "gradient_accumulation_steps": 4,  # Effective batch size of 8
                "learning_rate": 5e-5,
                "weight_decay": 0.01,
                "warmup_steps": 100,
                "save_steps": 500,
                "eval_steps": 250,
                "logging_steps": 50,
                "max_grad_norm": 1.0,
                "fp16": True,  # Use mixed precision
                "dataloader_num_workers": 2,
                "save_total_limit": 3
            },
            
            # Dataset configuration
            "datasets": datasets,
            
            # Hardware optimization
            "hardware": {
                "device": "cuda" if torch.cuda.is_available() else "cpu",
                "memory_efficient": True,
                "gradient_checkpointing": True,
                "use_cache": False  # Disable KV cache to save memory
            },
            
            # Output configuration
            "output": {
                "output_dir": str(self.base_path / "training_outputs"),
                "run_name": f"bulletproof_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "tensorboard_dir": str(self.base_path / "tensorboard_logs"),
                "save_model": True,
                "save_optimizer": False  # Save memory
            }
        }
        
        return config
    
    def run_training(self, config: Dict[str, Any]):
        """Run bulletproof training with error handling."""
        self.logger.info("🚀 Starting bulletproof incremental training...")
        
        try:
            # Initialize trainer
            trainer = BulletproofIncrementalTrainer()
              # Create dataloaders
            if self.console:
                with self.console.status("[bold blue]Creating dataloaders...") as status:
                    dataloaders = create_production_dataloaders(config["datasets"])
                    status.update("[bold green]Dataloaders created successfully!")
            else:
                print("📊 Creating dataloaders...")
                dataloaders = create_production_dataloaders(config["datasets"])
                print("✅ Dataloaders created successfully!")
              # Start training
            if self.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    training_task = progress.add_task("[bold blue]Training in progress...", total=None)
                    
                    results = trainer.train_multimodal_incremental(dataloaders)
            else:
                print("🎯 Starting training...")
                results = trainer.train_multimodal_incremental(dataloaders)
            
            self.logger.info("✅ Training completed successfully!")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Training failed: {str(e)}")
            if self.console:
                self.console.print(f"[bold red]❌ Training failed: {str(e)}[/bold red]")
            else:
                print(f"❌ Training failed: {str(e)}")
            raise
    
    def print_results(self, results: Dict[str, Any]):
        """Print training results."""
        if not results:
            return
            
        if self.console:
            # Create results table
            table = Table(title="🎯 Training Results", style="bold")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in results.items():
                if isinstance(value, float):
                    table.add_row(key, f"{value:.4f}")
                else:
                    table.add_row(key, str(value))
            
            self.console.print(table)
        else:
            print("\n🎯 Training Results:")
            for key, value in results.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")


def main():
    """Main entry point for production training."""
    parser = argparse.ArgumentParser(description="ImpressionCore-B1 Bulletproof Training Launcher")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=2, help="Training batch size")
    parser.add_argument("--learning-rate", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--output-dir", type=str, help="Output directory for models")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create launcher
    launcher = ProductionTrainingLauncher()
    
    # Print banner
    launcher._print_banner()
    
    try:
        # Discover datasets
        datasets = launcher.discover_datasets()
        
        # Create training config
        config = launcher.create_training_config(datasets, args)
        
        # Override config with command line args
        if args.output_dir:
            config["output"]["output_dir"] = args.output_dir
        if args.batch_size != 2:
            config["training"]["batch_size"] = args.batch_size
        if args.learning_rate != 5e-5:
            config["training"]["learning_rate"] = args.learning_rate
          # Run training
        results = launcher.run_training(config)
        
        # Print results
        launcher.print_results(results)
        
        print("\n🎉 ImpressionCore-B1 training completed successfully!")
        print(f"📁 Models saved to: {config['output']['output_dir']}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Training failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
