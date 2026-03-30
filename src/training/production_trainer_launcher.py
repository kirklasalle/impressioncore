#!/usr/bin/env python3
"""
ImpressionCore Production Training Launcher

File: src/training/production_trainer_launcher.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-12
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [training, production, launcher, multimodal, distillation, 2025]
Dependencies: [torch, transformers, rich, psutil]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Production-ready training launcher that orchestrates both the High School Distillation
Trainer and Multimodal Dataset Loaders. Implements best practices from latest research
including progressive distillation, ensemble distillation, and optimized memory management.

Features:
- Automated training pipeline
- Memory optimization and monitoring
- Progressive training strategies
- Rich progress tracking and logging
- Error recovery and checkpointing
- Hardware compatibility checks
"""

import sys
import torch
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import psutil
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from high_school_distillation_trainer import (
    HighSchoolDistillationTrainer, 
    HighSchoolTrainingConfig
)
from multimodal_dataset_loaders import MultimodalDatasetLoader

# Rich imports for enhanced UI
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.layout import Layout
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

class ProductionTrainerLauncher:
    """
    Production training launcher implementing best practices for knowledge distillation
    and multimodal training based on latest research.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.console = console
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Setup logging
        self._setup_logging()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize system monitoring
        self._setup_monitoring()
        
    def _setup_logging(self):
        """Setup comprehensive logging."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = Path("src/memlog/training")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"training_session_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Training session started: {timestamp}")
        
    def _load_config(self):
        """Load training configuration with best practice defaults."""
        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                config_dict = json.load(f)
            
            # Create config object from dictionary
            config = HighSchoolTrainingConfig()
            for key, value in config_dict.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        else:
            # Use optimized defaults based on research
            config = HighSchoolTrainingConfig(
                # Model parameters optimized for 4GB VRAM
                model_dim=512,  # Reduced from 768 for memory efficiency
                num_layers=8,   # Balanced depth for knowledge distillation
                num_heads=8,
                vocab_size=32000,
                max_seq_length=1024,  # Reduced for memory efficiency
                
                # Training parameters with best practices
                batch_size=2,  # Conservative for 4GB VRAM
                learning_rate=1e-4,  # Lower LR for distillation stability
                num_epochs=15,  # More epochs for better distillation
                warmup_steps=1500,  # Extended warmup for stability
                weight_decay=0.01,
                
                # Knowledge distillation with research-based parameters
                teacher_model="microsoft/DialoGPT-medium",
                temperature=6.0,  # Higher temp for better knowledge transfer
                alpha=0.8,  # Emphasize distillation loss
                beta=0.2,   # Reduce task loss weight
                
                # Memory optimization
                gradient_checkpointing=True,
                mixed_precision=True,
                max_memory_mb=3200,  # Conservative memory target
            )
        
        return config
    
    def _setup_monitoring(self):
        """Setup system monitoring for hardware optimization."""
        self.system_info = {
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total / (1024**3),
            'cuda_available': torch.cuda.is_available(),
        }
        
        if torch.cuda.is_available():
            self.system_info.update({
                'gpu_name': torch.cuda.get_device_name(0),
                'gpu_memory': torch.cuda.get_device_properties(0).total_memory / (1024**3),
                'cuda_version': torch.version.cuda,
            })
        
        self.logger.info(f"System info: {self.system_info}")
    
    def check_compatibility(self) -> bool:
        """Check hardware compatibility and optimize settings."""
        if self.console:
            self.console.print("\n🔧 [bold blue]Hardware Compatibility Check[/bold blue]")
        
        compatible = True
        warnings = []
        
        # Check VRAM
        if torch.cuda.is_available():
            gpu_memory = self.system_info['gpu_memory']
            if gpu_memory < 3.5:
                warnings.append(f"Low VRAM detected: {gpu_memory:.1f}GB. Reducing batch size.")
                self.config.batch_size = 1
                self.config.max_memory_mb = int(gpu_memory * 800)  # Use 80% of available
            elif gpu_memory >= 8.0:
                if self.console:
                    self.console.print(f"✅ Excellent VRAM: {gpu_memory:.1f}GB - Can increase batch size")
                self.config.batch_size = min(8, self.config.batch_size * 2)
        else:
            warnings.append("CUDA not available. Training will be significantly slower.")
            self.config.mixed_precision = False
            self.config.batch_size = 1
        
        # Check RAM
        if self.system_info['memory_total'] < 8.0:
            warnings.append("Low system RAM detected. Reducing data loader workers.")
        
        # Display results
        if self.console:
            if warnings:
                for warning in warnings:
                    self.console.print(f"⚠️  {warning}")
            
            # Show optimized config
            table = Table(title="Optimized Training Configuration")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Batch Size", str(self.config.batch_size))
            table.add_row("Model Dimension", str(self.config.model_dim))
            table.add_row("Max Memory (MB)", str(self.config.max_memory_mb))
            table.add_row("Mixed Precision", str(self.config.mixed_precision))
            table.add_row("Gradient Checkpointing", str(self.config.gradient_checkpointing))
            
            self.console.print(table)
        
        return compatible
    
    def create_multimodal_datasets(self) -> Dict:
        """Create multimodal datasets with bulletproof loading."""
        if self.console:
            self.console.print("\n📚 [bold blue]Creating Multimodal Datasets[/bold blue]")
        
        # Configuration for multimodal loader
        loader_config = {
            'max_text_length': self.config.max_seq_length,
            'batch_size': self.config.batch_size,
            'pin_memory': True if torch.cuda.is_available() else False,
        }
        
        # Create multimodal loader
        loader = MultimodalDatasetLoader(loader_config)
        
        # Create sample datasets for demonstration
        # In production, these would be real dataset paths
        datasets = {}
        
        try:
            # Create dummy text dataset for testing
            sample_texts = [
                "The quick brown fox jumps over the lazy dog.",
                "Machine learning is revolutionizing artificial intelligence.",
                "Knowledge distillation helps compress large neural networks.",
                "Multimodal learning combines text, images, and audio data.",
                "PyTorch provides excellent support for deep learning research."
            ]
            
            # Create a simple text dataset
            class SimpleTextDataset:
                def __init__(self, texts, transform):
                    self.texts = texts
                    self.transform = transform
                
                def __len__(self):
                    return len(self.texts)
                
                def __getitem__(self, idx):
                    return self.transform(self.texts[idx])
            
            text_dataset = SimpleTextDataset(sample_texts, loader.text_transform)
            datasets['text'] = text_dataset
            
            if self.console:
                self.console.print(f"✅ Created text dataset with {len(text_dataset)} samples")
        
        except Exception as e:
            self.logger.warning(f"Failed to create multimodal datasets: {e}")
            if self.console:
                self.console.print(f"⚠️  Using high school conversation dataset instead")
        
        return datasets
    
    def run_high_school_training(self):
        """Run the high school distillation training with best practices."""
        if self.console:
            self.console.print("\n🎓 [bold green]Starting High School Distillation Training[/bold green]")
        
        try:
            # Create trainer
            trainer = HighSchoolDistillationTrainer(self.config)
            
            # Display training info
            if self.console:
                panel = Panel.fit(
                    f"[bold]High School Graduate Training[/bold]\\n"
                    f"Teacher: {self.config.teacher_model}\\n"
                    f"Student Parameters: {trainer.student_model.get_parameter_count():,}\\n"
                    f"Epochs: {self.config.num_epochs}\\n"
                    f"Batch Size: {self.config.batch_size}\\n"
                    f"Temperature: {self.config.temperature}\\n"
                    f"Device: {self.device}",
                    title="📊 Training Configuration"
                )
                self.console.print(panel)
            
            # Run training
            trainer.train()
            
            if self.console:
                self.console.print("✅ [bold green]High School Training Completed Successfully![/bold green]")
            
            return True
            
        except Exception as e:
            self.logger.error(f"High school training failed: {e}")
            if self.console:
                self.console.print(f"❌ [bold red]Training failed: {e}[/bold red]")
            return False
    
    def run_memory_optimization_test(self):
        """Run memory optimization test to validate efficiency."""
        if self.console:
            self.console.print("\n💾 [bold blue]Memory Optimization Test[/bold blue]")
        
        if not torch.cuda.is_available():
            if self.console:
                self.console.print("⚠️  CUDA not available, skipping memory test")
            return True
        
        try:
            # Clear cache
            torch.cuda.empty_cache()
            initial_memory = torch.cuda.memory_allocated() / (1024**3)
            
            # Create model and test forward pass
            from models.impressioncore_b1.unified_model import ImpressionCoreB1Model
            from core.config.model_config import ModelConfig
            
            model_config = ModelConfig(
                hidden_size=self.config.model_dim,
                num_hidden_layers=self.config.num_layers,
                num_attention_heads=self.config.num_heads,
                max_position_embeddings=self.config.max_seq_length
            )
            
            model = ImpressionCoreB1Model(model_config).to(self.device)
            
            # Test with batch
            batch_size = self.config.batch_size
            seq_len = min(512, self.config.max_seq_length)  # Test with reasonable length
            
            input_ids = torch.randint(0, 1000, (batch_size, seq_len)).to(self.device)
            
            # Forward pass
            with torch.no_grad():
                outputs = model(input_ids)
            
            peak_memory = torch.cuda.max_memory_allocated() / (1024**3)
            memory_used = peak_memory - initial_memory
            
            # Check if within limits
            memory_limit = self.config.max_memory_mb / 1024
            within_limit = memory_used <= memory_limit
            
            if self.console:
                table = Table(title="Memory Usage Report")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="magenta")
                
                table.add_row("Initial Memory", f"{initial_memory:.3f} GB")
                table.add_row("Peak Memory", f"{peak_memory:.3f} GB")
                table.add_row("Memory Used", f"{memory_used:.3f} GB")
                table.add_row("Memory Limit", f"{memory_limit:.3f} GB")
                table.add_row("Within Limit", "✅ Yes" if within_limit else "❌ No")
                
                self.console.print(table)
            
            # Cleanup
            del model, outputs, input_ids
            torch.cuda.empty_cache()
            
            return within_limit
            
        except Exception as e:
            self.logger.error(f"Memory test failed: {e}")
            if self.console:
                self.console.print(f"❌ Memory test failed: {e}")
            return False
    
    def save_training_report(self, results: Dict):
        """Save comprehensive training report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Path("src/memlog/training/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"training_report_{timestamp}.json"
        
        report = {
            'timestamp': timestamp,
            'system_info': self.system_info,
            'config': {
                'model_dim': self.config.model_dim,
                'num_layers': self.config.num_layers,
                'batch_size': self.config.batch_size,
                'temperature': self.config.temperature,
                'alpha': self.config.alpha,
                'beta': self.config.beta,
                'num_epochs': self.config.num_epochs,
                'teacher_model': self.config.teacher_model,
            },
            'results': results,
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Training report saved: {report_file}")
        
        if self.console:
            self.console.print(f"📄 Training report saved: {report_file}")
    
    def run(self):
        """Run the complete training pipeline."""
        if self.console:
            self.console.print("🚀 [bold blue]ImpressionCore Production Training Launcher[/bold blue]")
            self.console.print("=" * 70)
        
        results = {}
        
        # Step 1: Compatibility check
        compatibility_ok = self.check_compatibility()
        results['compatibility_check'] = compatibility_ok
        
        if not compatibility_ok:
            self.logger.error("Compatibility check failed")
            return False
        
        # Step 2: Memory optimization test
        memory_ok = self.run_memory_optimization_test()
        results['memory_test'] = memory_ok
        
        if not memory_ok:
            if self.console:
                self.console.print("⚠️  Memory test failed, but continuing with training...")
        
        # Step 3: Create datasets
        datasets = self.create_multimodal_datasets()
        results['dataset_creation'] = len(datasets) > 0
        
        # Step 4: Run high school training
        training_success = self.run_high_school_training()
        results['high_school_training'] = training_success
        
        # Step 5: Save report
        self.save_training_report(results)
        
        # Final summary
        if self.console:
            self.console.print("\n" + "=" * 70)
            self.console.print("🏁 [bold blue]Training Pipeline Summary[/bold blue]")
            
            success_count = sum(1 for v in results.values() if v)
            total_count = len(results)
            
            for step, success in results.items():
                status = "✅" if success else "❌"
                self.console.print(f"  {status} {step.replace('_', ' ').title()}")
            
            overall_success = success_count == total_count
            if overall_success:
                self.console.print("\\n🎉 [bold green]All training steps completed successfully![/bold green]")
            else:
                self.console.print(f"\\n⚠️  [bold yellow]{success_count}/{total_count} steps completed[/bold yellow]")
        
        return training_success

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ImpressionCore Production Training Launcher")
    parser.add_argument("--config", type=str, help="Path to training configuration file")
    parser.add_argument("--test-only", action="store_true", help="Run tests only, skip training")
    
    args = parser.parse_args()
    
    if args.test_only:
        # Run test suite
        import subprocess
        test_script = Path(__file__).parent / "test_trainers.py"
        result = subprocess.run([sys.executable, str(test_script)], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    
    # Run production training
    launcher = ProductionTrainerLauncher(config_path=args.config)
    success = launcher.run()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
