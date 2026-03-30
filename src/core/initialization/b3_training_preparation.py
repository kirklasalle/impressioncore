#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** July-29-2025
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #attention_mechanism #cuda #memory_management #multimodal #python #source_code #src/core/initialization/b3_training_preparation.py #testing #training
**Category:** Core Implementation
**Status:** Active
"""



import json
import logging
import traceback
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

# Import B3 system components
try:
    from src.core.initialization.b3_full_initialization import (
        B3InitializationManager,  # noqa: F401
        initialize_b3_3b,
        initialize_b3_standard,
    )
    from src.core.initialization.b3_multimodal_integration import (
        B3MultimodalEmbeddingIntegrator,  # noqa: F401
        create_multimodal_training_dataset,
    )
    from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model  # noqa: F401
except ImportError as e:
    logging.warning(f"Could not import B3 components: {e}")

# Rich enhancements
try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.panel import Panel
    from rich.progress import Progress, track  # noqa: F401
    from rich.table import Table
    console = Console()

    def get_rich_logger(name):
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(console=console, rich_tracebacks=True)]
        )
        return logging.getLogger(name)
except ImportError:
    console = None
    def get_rich_logger(name):
        return logging.getLogger(name)

logger = get_rich_logger(__name__)

class B3TrainingDataset(Dataset):
    """
    Custom dataset for B3 multimodal training.
    Handles text, image, audio, and video inputs.
    """

    def __init__(self, data_dir: Path, config: B3Config, max_samples: int | None = None):
        """
        Initialize the B3 training dataset.

        Args:
            data_dir: Directory containing training data
            config: B3 configuration
            max_samples: Maximum number of samples to load
        """
        self.data_dir = Path(data_dir)
        self.config = config
        self.max_samples = max_samples

        # Load embeddings and metadata
        self.samples = self._load_samples()

        logger.info(f"📚 B3 dataset initialized with {len(self.samples)} samples")

    def _load_samples(self):
        """Load training samples from embeddings directory."""
        samples = []

        try:
            # Look for embedding files
            for modality_dir in self.data_dir.iterdir():
                if modality_dir.is_dir():
                    modality = modality_dir.name

                    # Find embedding and metadata files
                    embedding_files = list(modality_dir.glob("embeddings_*.npy"))
                    metadata_files = list(modality_dir.glob("metadata_*.json"))

                    for emb_file, meta_file in zip(embedding_files, metadata_files):
                        try:
                            # Load embeddings
                            embeddings = np.load(emb_file)

                            # Load metadata
                            with open(meta_file) as f:
                                metadata = json.load(f)

                            # Create samples
                            for _i, (embedding, meta) in enumerate(zip(embeddings, metadata)):
                                sample = {
                                    'embedding': embedding,
                                    'modality': modality,
                                    'metadata': meta,
                                    'file_path': meta.get('file_path', ''),
                                    'size': meta.get('size', 0)
                                }
                                samples.append(sample)

                                if self.max_samples and len(samples) >= self.max_samples:
                                    return samples

                        except Exception as e:
                            logger.warning(f"⚠️  Could not load {emb_file}: {e}")

            return samples

        except Exception as e:
            logger.error(f"❌ Failed to load samples: {e!s}")
            return []

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        """Get a training sample."""
        sample = self.samples[idx]

        # Create model inputs based on modality
        modality = sample['modality']
        embedding = torch.tensor(sample['embedding'], dtype=torch.float32)

        # Generate synthetic inputs for training
        batch_size = 1
        seq_length = 128

        model_inputs = {
            'input_ids': None,
            'image_features': None,
            'audio_features': None,
            'phoneme_ids': None,
            'modality_type': None
        }

        if modality == 'text':
            model_inputs['input_ids'] = torch.randint(0, self.config.vocab_size, (batch_size, seq_length))
            model_inputs['modality_type'] = torch.tensor([0])  # Text modality
        elif modality == 'image':
            model_inputs['image_features'] = torch.randn(batch_size, seq_length, self.config.image_embed_dim)
            model_inputs['modality_type'] = torch.tensor([1])  # Image modality
        elif modality == 'audio':
            model_inputs['audio_features'] = torch.randn(batch_size, seq_length, self.config.audio_embed_dim)
            model_inputs['modality_type'] = torch.tensor([2])  # Audio modality
        else:
            # Mixed modality
            model_inputs['input_ids'] = torch.randint(0, self.config.vocab_size, (batch_size, seq_length))
            model_inputs['image_features'] = torch.randn(batch_size, seq_length, self.config.image_embed_dim)
            model_inputs['modality_type'] = torch.tensor([6])  # Mixed modality

        # Create labels for language modeling
        if model_inputs['input_ids'] is not None:
            labels = model_inputs['input_ids'].clone()
        else:
            labels = torch.randint(0, self.config.vocab_size, (batch_size, seq_length))

        return {
            # model_inputs,
            'labels': labels,
            'target_embedding': embedding
        }

class B3TrainingPreparationSystem:
    """
    Comprehensive training preparation system for ImpressionCore B3.
    Handles model initialization, data preparation, and training setup.
    """

    def __init__(self, use_3b: bool = False, max_samples_per_modality: int = 1000):
        """
        Initialize the training preparation system.

        Args:
            use_3b: Whether to use 3B parameter model
            max_samples_per_modality: Maximum samples per modality for quick setup
        """
        self.use_3b = use_3b
        self.max_samples_per_modality = max_samples_per_modality
        self.start_time = datetime.now()

        # System components
        self.b3_manager = None
        self.model = None
        self.config = None
        self.device = None
        self.dataset = None
        self.dataloader = None
        self.optimizer = None
        self.scheduler = None

        # Training configuration
        self.training_config = {
            'batch_size': 4 if use_3b else 8,
            'learning_rate': 1e-4,
            'weight_decay': 0.01,
            'warmup_steps': 100,
            'max_steps': 1000,
            'gradient_accumulation_steps': 4 if use_3b else 2,
            'max_grad_norm': 1.0,
            'save_steps': 100,
            'eval_steps': 50,
            'logging_steps': 10
        }

        # Statistics
        self.stats = {
            'preparation_time': 0,
            'model_params': 0,
            'dataset_size': 0,
            'memory_usage_mb': 0,
            'training_ready': False
        }

        logger.info(f"🚀 B3 Training Preparation System initialized ({'3B' if use_3b else 'Standard'})")

    def display_preparation_banner(self):
        """Display training preparation welcome banner."""
        if console:
            banner_content = f"""
[bold blue]🚀 IMPRESSIONCORE B3 TRAINING PREPARATION[/bold blue]
[bold yellow]Comprehensive Training System Setup[/bold yellow]

[green]🎯 Configuration:[/green]
• Model: {'3B Parameter' if self.use_3b else 'Standard (GTX 1050 Ti)'}
• Max Samples: {self.max_samples_per_modality:,} per modality
• Batch Size: {self.training_config['batch_size']}
• Learning Rate: {self.training_config['learning_rate']}

[green]📋 Preparation Steps:[/green]
• 🔧 System Environment Validation
• 🧠 B3 Model Initialization
• 🌐 Multimodal Embedding Integration
• 📚 Training Dataset Preparation
• ⚙️  Optimizer and Scheduler Setup
• 🎯 Training Readiness Validation

[bold cyan]Ready to democratize AI training![/bold cyan]
            """
            console.print(Panel(banner_content, title="B3 Training Preparation", border_style="blue"))
        else:
            logger.info("🚀 IMPRESSIONCORE B3 TRAINING PREPARATION")
            logger.info(f"Model: {'3B Parameter' if self.use_3b else 'Standard (GTX 1050 Ti)'}")

    def initialize_b3_system(self):
        """Initialize the complete B3 system."""
        logger.info("🔧 Initializing B3 system...")

        try:
            # Initialize B3 manager
            if self.use_3b:
                self.b3_manager = initialize_b3_3b()
            else:
                self.b3_manager = initialize_b3_standard()

            if not self.b3_manager:
                logger.error("❌ B3 initialization failed")
                return False

            # Get initialized components
            components = self.b3_manager.get_initialized_components()
            self.model = components['model']
            self.config = components['config']
            self.device = components['device']

            # Update statistics
            self.stats['model_params'] = components['stats']['model_params']
            self.stats['memory_usage_mb'] = components['stats']['memory_usage_mb']

            logger.info("✅ B3 system initialization complete")
            return True

        except Exception as e:
            logger.error(f"❌ B3 system initialization failed: {e!s}")
            traceback.print_exc()
            return False

    def prepare_multimodal_dataset(self):
        """Prepare multimodal training dataset."""
        logger.info("📚 Preparing multimodal training dataset...")

        try:
            # Create multimodal training dataset
            success = create_multimodal_training_dataset(
                self.b3_manager,
                self.max_samples_per_modality
            )

            if not success:
                logger.warning("⚠️  Multimodal dataset creation failed, using synthetic data")
                return self.create_synthetic_dataset()

            # Load dataset
            embeddings_path = Path("F:/ImpressionCore/embeddings") if Path("F:/").exists() else Path("./embeddings")

            if embeddings_path.exists():
                self.dataset = B3TrainingDataset(embeddings_path, self.config, max_samples=5000)
                self.stats['dataset_size'] = len(self.dataset)

                # Create dataloader
                self.dataloader = DataLoader(
                    self.dataset,
                    batch_size=self.training_config['batch_size'],
                    shuffle=True,
                    num_workers=2,
                    pin_memory=bool(torch.cuda.is_available())
                )

                logger.info(f"✅ Training dataset ready with {len(self.dataset)} samples")
                return True
            else:
                logger.warning("⚠️  No embeddings found, creating synthetic dataset")
                return self.create_synthetic_dataset()

        except Exception as e:
            logger.error(f"❌ Dataset preparation failed: {e!s}")
            return self.create_synthetic_dataset()

    def create_synthetic_dataset(self):
        """Create synthetic dataset for testing."""
        logger.info("🧪 Creating synthetic training dataset...")

        try:
            # Create synthetic samples
            samples = []
            for _i in range(1000):  # 1000 synthetic samples
                sample = {
                    'input_ids': torch.randint(0, self.config.vocab_size, (1, 128)),
                    'image_features': torch.randn(1, 128, self.config.image_embed_dim),
                    'audio_features': torch.randn(1, 128, self.config.audio_embed_dim),
                    'phoneme_ids': torch.randint(0, self.config.phoneme_vocab_size, (1, 128)),
                    'modality_type': torch.randint(0, 7, (1,)),
                    'labels': torch.randint(0, self.config.vocab_size, (1, 128)),
                    'target_embedding': torch.randn(self.config.embed_dim)
                }
                samples.append(sample)

            # Create simple dataset class
            class SyntheticDataset(Dataset):
                def __init__(self, samples):
                    self.samples = samples

                def __len__(self):
                    return len(self.samples)

                def __getitem__(self, idx):
                    return self.samples[idx]

            self.dataset = SyntheticDataset(samples)
            self.stats['dataset_size'] = len(self.dataset)

            # Create dataloader
            self.dataloader = DataLoader(
                self.dataset,
                batch_size=self.training_config['batch_size'],
                shuffle=True,
                num_workers=0  # No multiprocessing for synthetic data
            )

            logger.info(f"✅ Synthetic dataset created with {len(self.dataset)} samples")
            return True

        except Exception as e:
            logger.error(f"❌ Synthetic dataset creation failed: {e!s}")
            return False

    def setup_training_components(self):
        """Setup optimizer, scheduler, and other training components."""
        logger.info("⚙️  Setting up training components...")

        try:
            # Setup optimizer
            optimizer_params = [
                {
                    'params': [p for n, p in self.model.named_parameters() if 'embeddings' not in n],
                    'lr': self.training_config['learning_rate'],
                    'weight_decay': self.training_config['weight_decay']
                },
                {
                    'params': [p for n, p in self.model.named_parameters() if 'embeddings' in n],
                    'lr': self.training_config['learning_rate'] * 0.1,  # Lower LR for embeddings
                    'weight_decay': 0.0
                }
            ]

            self.optimizer = optim.AdamW(optimizer_params)

            # Setup scheduler
            from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
            self.scheduler = CosineAnnealingWarmRestarts(
                self.optimizer,
                T_0=self.training_config['warmup_steps'],
                T_mult=2
            )

            # Setup gradient scaler for mixed precision
            if self.training_config.get('use_mixed_precision', True):
                self.scaler = torch.cuda.amp.GradScaler()
            else:
                self.scaler = None

            logger.info("✅ Training components setup complete")
            return True

        except Exception as e:
            logger.error(f"❌ Training components setup failed: {e!s}")
            traceback.print_exc()
            return False

    def validate_training_readiness(self):
        """Validate that everything is ready for training."""
        logger.info("🎯 Validating training readiness...")

        try:
            # Check all components
            checks = {
                'B3 Manager': self.b3_manager is not None,
                'Model': self.model is not None,
                'Config': self.config is not None,
                'Device': self.device is not None,
                'Dataset': self.dataset is not None,
                'DataLoader': self.dataloader is not None,
                'Optimizer': self.optimizer is not None,
                'Scheduler': self.scheduler is not None
            }

            # Display readiness table
            if console:
                readiness_table = Table(title="Training Readiness Checklist")
                readiness_table.add_column("Component", style="cyan")
                readiness_table.add_column("Status", style="green")

                for component, status in checks.items():
                    status_emoji = "✅" if status else "❌"
                    readiness_table.add_row(component, f"{status_emoji} {status}")

                console.print(readiness_table)

            # Test forward pass
            logger.info("🧪 Testing model forward pass...")
            self.model.eval()

            try:
                # Get a sample batch
                sample_batch = next(iter(self.dataloader))

                # Move to device
                for key in sample_batch:
                    if isinstance(sample_batch[key], torch.Tensor):
                        sample_batch[key] = sample_batch[key].to(self.device)

                # Test forward pass
                with torch.no_grad():
                    outputs = self.model(**sample_batch)

                logger.info(f"✅ Forward pass successful - Loss: {outputs.get('loss', 'N/A')}")

            except Exception as e:
                logger.error(f"❌ Forward pass test failed: {e!s}")
                return False

            # Overall readiness
            all_ready = all(checks.values())
            self.stats['training_ready'] = all_ready

            if all_ready:
                logger.info("🚀 System is READY for training!")
                self.display_training_summary()
            else:
                logger.warning("⚠️  System is NOT ready for training")
                failed_checks = [name for name, status in checks.items() if not status]
                logger.warning(f"Failed checks: {', '.join(failed_checks)}")

            return all_ready

        except Exception as e:
            logger.error(f"❌ Training readiness validation failed: {e!s}")
            traceback.print_exc()
            return False

    def display_training_summary(self):
        """Display comprehensive training preparation summary."""
        end_time = datetime.now()
        self.stats['preparation_time'] = (end_time - self.start_time).total_seconds()

        if console:
            summary_content = f"""
[bold green]🎉 TRAINING PREPARATION COMPLETE![/bold green]

[bold yellow]⏱️  Preparation Metrics:[/bold yellow]
• Preparation Time: {self.stats['preparation_time']:.1f} seconds
• Model Parameters: {self.stats['model_params']:,}
• Dataset Size: {self.stats['dataset_size']:,} samples
• Memory Usage: {self.stats['memory_usage_mb']:.1f}MB

[bold yellow]🎯 Training Configuration:[/bold yellow]
• Batch Size: {self.training_config['batch_size']}
• Learning Rate: {self.training_config['learning_rate']}
• Max Steps: {self.training_config['max_steps']:,}
• Gradient Accumulation: {self.training_config['gradient_accumulation_steps']}

[bold yellow]🧠 Model Architecture:[/bold yellow]
• Type: ImpressionCore B3 {'3B' if self.use_3b else 'Standard'}
• Embed Dim: {self.config.embed_dim}
• Layers: {self.config.num_layers}
• Attention Heads: {self.config.num_heads}
• Experts: {self.config.num_experts}

[bold cyan]🚀 Ready to start training![/bold cyan]
[bold cyan]Use: python training_script.py[/bold cyan]
            """
            console.print(Panel(summary_content, title="Training Preparation Summary", border_style="green"))
        else:
            logger.info("🎉 TRAINING PREPARATION COMPLETE!")
            logger.info(f"⏱️  Time: {self.stats['preparation_time']:.1f}s")
            logger.info(f"📊 Dataset: {self.stats['dataset_size']:,} samples")
            logger.info(f"🧠 Parameters: {self.stats['model_params']:,}")
            logger.info("🚀 Ready to start training!")

    def full_preparation(self):
        """
        Execute complete training preparation.

        Returns:
            bool: True if preparation successful, False otherwise
        """
        logger.info("🚀 Starting ImpressionCore B3 training preparation...")

        try:
            self.display_preparation_banner()

            # Step 1: Initialize B3 System
            if not self.initialize_b3_system():
                return False

            # Step 2: Prepare Multimodal Dataset
            if not self.prepare_multimodal_dataset():
                return False

            # Step 3: Setup Training Components
            if not self.setup_training_components():
                return False

            # Step 4: Validate Training Readiness
            if not self.validate_training_readiness():
                return False

            logger.info("🎉 ImpressionCore B3 training preparation SUCCESSFUL!")
            return True

        except Exception as e:
            logger.error(f"❌ Training preparation FAILED: {e!s}")
            traceback.print_exc()
            return False

    def get_training_components(self):
        """
        Get all training components.

        Returns:
            dict: Dictionary containing all training components
        """
        return {
            'model': self.model,
            'config': self.config,
            'device': self.device,
            'dataset': self.dataset,
            'dataloader': self.dataloader,
            'optimizer': self.optimizer,
            'scheduler': self.scheduler,
            'scaler': getattr(self, 'scaler', None),
            'training_config': self.training_config,
            'stats': self.stats
        }

def prepare_b3_for_training(use_3b: bool = False, max_samples: int = 1000):
    """
    Prepare B3 system for training.

    Args:
        use_3b: Whether to use 3B parameter model
        max_samples: Maximum samples per modality

    Returns:
        B3TrainingPreparationSystem: Prepared training system or None if failed
    """
    logger.info("🚀 Preparing B3 for training...")

    try:
        prep_system = B3TrainingPreparationSystem(use_3b, max_samples)
        success = prep_system.full_preparation()

        if success:
            logger.info("✅ B3 training preparation complete!")
            return prep_system
        else:
            logger.error("❌ B3 training preparation failed!")
            return None

    except Exception as e:
        logger.error(f"❌ Training preparation failed: {e!s}")
        traceback.print_exc()
        return None

def main():
    """Main training preparation function."""
    import argparse

    parser = argparse.ArgumentParser(description="ImpressionCore B3 Training Preparation")
    parser.add_argument("--3b", action="store_true", help="Use 3B parameter model")
    parser.add_argument("--max-samples", type=int, default=1000, help="Max samples per modality")
    parser.add_argument("--quick", action="store_true", help="Quick preparation with minimal data")

    args = parser.parse_args()

    try:
        # Quick mode uses fewer samples
        max_samples = 100 if args.quick else args.max_samples

        # Prepare training system
        prep_system = prepare_b3_for_training(args._3b, max_samples)

        if prep_system:
            logger.info("[OK] B3 training preparation successful!")
            logger.info("Model: %s", '3B Parameter' if args._3b else 'Standard')
            logger.info("Dataset: %s samples", f"{prep_system.stats['dataset_size']:,}")
            logger.info("Memory: %.1fMB", prep_system.stats['memory_usage_mb'])
            logger.info("[START] Ready for training!")

            # Save preparation state
            components = prep_system.get_training_components()
            torch.save({
                'model_state_dict': components['model'].state_dict(),
                'config': components['config'].to_dict(),
                'training_config': components['training_config'],
                'stats': components['stats']
            }, 'b3_training_preparation.pth')

            logger.info("Training preparation saved to: b3_training_preparation.pth")
        else:
            logger.error("[ERROR] B3 training preparation failed!")
            return 1

        return 0

    except Exception as e:
        logger.error(f"❌ Main execution failed: {e!s}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
