"""
ImpressionCore B3 Sweet Spot Recovery Training Script
====================================================

This script recovers and continues training from the best quality checkpoint
that contains all embedding work and was identified as the "sweet spot" model.

Created: August 4, 2025
Author: Kirk LaSalle & GitHub Copilot
"""

import logging
import os

import torch
import torch.nn as nn
import torch.optim as optim

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sweet_spot_recovery_training.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import B3 architecture from the src directory
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from core.models.b3_unified_integration import UnifiedTokenizerSystem
from core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model


class SweetSpotRecoveryTrainer:
    """
    Recovery trainer for the sweet spot B3 model configuration.
    Loads the best quality checkpoint and continues training.
    """

    def __init__(self):
        """Initialize the trainer with the exact sweet spot configuration."""

        # Device setup for GTX 1050 Ti optimization
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"🎯 Using device: {self.device}")

        if torch.cuda.is_available():
            logger.info(f"🚀 GPU: {torch.cuda.get_device_name()}")
            logger.info(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")

        # Exact configuration matching the best quality checkpoint
        # Based on analysis of b3_best_quality_model_20250802_124801.pth
        self.config = B3Config(
            embed_dim=768,
            num_heads=12,
            num_layers=8,
            vocab_size=50257,
            num_experts=8,
            expert_dim=2048,
            experts_per_token=2,
            dropout=0.1,
            image_embed_dim=768,
            audio_embed_dim=768,
            phoneme_vocab_size=256,
            max_seq_length=4096,
            use_gradient_checkpointing=True
        )

        # Training configuration optimized for GTX 1050 Ti
        self.training_config = {
            'batch_size': 2,  # Small batch for VRAM efficiency
            'learning_rate': 5e-5,  # Conservative learning rate
            'weight_decay': 0.01,
            'warmup_steps': 100,
            'max_steps': 5000,
            'save_every': 500,
            'log_every': 10,
            'gradient_accumulation_steps': 4,  # Effective batch size of 8
            'max_grad_norm': 1.0,
            'fp16': True  # Mixed precision for VRAM efficiency
        }

        # Checkpoint paths
        self.best_quality_path = "F:/models/checkpoints/best_quality/b3_best_quality_model_20250802_124801.pth"
        self.save_dir = "F:/models/checkpoints/sweet_spot_recovery"
        os.makedirs(self.save_dir, exist_ok=True)

        # Initialize model and tokenizer
        self.model = None
        self.tokenizer = None
        self.optimizer = None
        self.scaler = torch.cuda.amp.GradScaler() if self.training_config['fp16'] else None

    def setup_model(self):
        """Set up the B3 model with the exact configuration."""
        logger.info("🔧 Setting up B3 model with sweet spot configuration...")

        # Create model with exact configuration
        self.model = ImpressionCoreB3Model(self.config).to(self.device)

        # Load the best quality checkpoint
        logger.info(f"📦 Loading checkpoint: {self.best_quality_path}")
        if os.path.exists(self.best_quality_path):
            checkpoint = torch.load(self.best_quality_path, map_location=self.device, weights_only=True)
            self.model.load_state_dict(checkpoint, strict=False)
            logger.info("✅ Successfully loaded best quality checkpoint!")
        else:
            logger.error(f"❌ Checkpoint not found: {self.best_quality_path}")
            raise FileNotFoundError(f"Best quality checkpoint not found at {self.best_quality_path}")

        # Count parameters
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

        logger.info("📊 Model Statistics:")
        logger.info(f"   Total Parameters: {total_params:,}")
        logger.info(f"   Trainable Parameters: {trainable_params:,}")
        logger.info(f"   Model Size: {total_params * 4 / (1024**2):.1f}MB")

        # Setup optimizer
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.training_config['learning_rate'],
            weight_decay=self.training_config['weight_decay']
        )

        # Setup tokenizer
        self.tokenizer = UnifiedTokenizerSystem()

        logger.info("✅ Model setup complete!")

    def create_dummy_data(self, batch_size: int):
        """Create dummy multimodal data for testing."""
        return {
            'input_ids': torch.randint(0, 1000, (batch_size, 512)).to(self.device),
            'image_features': torch.randn(batch_size, 196, 768).to(self.device),
            'audio_features': torch.randn(batch_size, 100, 768).to(self.device),
            'target': torch.randn(batch_size, 512, 50257).to(self.device)  # Vocab size for logits
        }

    def training_step(self, batch: dict[str, torch.Tensor]) -> float:
        """Execute a single training step."""
        self.model.train()

        if self.training_config['fp16']:
            with torch.cuda.amp.autocast():
                outputs = self.model(
                    input_ids=batch['input_ids'],
                    image_features=batch['image_features'],
                    audio_features=batch['audio_features']
                )

                # Extract logits from model output dictionary
                logits = outputs['logits']
                # Simple MSE loss for demonstration
                loss = nn.MSELoss()(logits, batch['target'])
        else:
            outputs = self.model(
                input_ids=batch['input_ids'],
                image_features=batch['image_features'],
                audio_features=batch['audio_features']
            )

            # Extract logits from model output dictionary
            logits = outputs['logits']
            loss = nn.MSELoss()(logits, batch['target'])

        # Backward pass with gradient scaling
        if self.training_config['fp16']:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()

        return loss.item()

    def train(self):
        """Main training loop."""
        logger.info("🚀 Starting Sweet Spot Recovery Training!")
        logger.info(f"📊 Training Configuration: {self.training_config}")

        # Training metrics
        step = 0
        accumulated_loss = 0.0
        best_loss = float('inf')

        # Training loop
        while step < self.training_config['max_steps']:
            # Create batch
            batch = self.create_dummy_data(self.training_config['batch_size'])

            # Training step
            loss = self.training_step(batch)
            accumulated_loss += loss

            # Gradient accumulation
            if (step + 1) % self.training_config['gradient_accumulation_steps'] == 0:
                # Gradient clipping
                if self.training_config['fp16']:
                    self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.training_config['max_grad_norm'])

                # Optimizer step
                if self.training_config['fp16']:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    self.optimizer.step()

                self.optimizer.zero_grad()

            step += 1

            # Logging
            if step % self.training_config['log_every'] == 0:
                avg_loss = accumulated_loss / self.training_config['log_every']

                # Memory monitoring
                if torch.cuda.is_available():
                    memory_used = torch.cuda.memory_allocated() / 1024**2
                    memory_cached = torch.cuda.memory_reserved() / 1024**2
                    logger.info(f"📈 Step {step:4d} | Loss: {avg_loss:.6f} | "
                              f"VRAM: {memory_used:.0f}MB | Cached: {memory_cached:.0f}MB")
                else:
                    logger.info(f"📈 Step {step:4d} | Loss: {avg_loss:.6f}")

                # Track best loss
                if avg_loss < best_loss:
                    best_loss = avg_loss
                    logger.info(f"🎯 New best loss: {best_loss:.6f}")

                accumulated_loss = 0.0

            # Save checkpoint
            if step % self.training_config['save_every'] == 0:
                self.save_checkpoint(step, loss)

        logger.info(f"✅ Training complete! Best loss: {best_loss:.6f}")

    def save_checkpoint(self, step: int, loss: float):
        """Save training checkpoint."""
        checkpoint_path = os.path.join(self.save_dir, f"recovery_step_{step}.pth")

        torch.save({
            'step': step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': loss,
            'config': self.config.__dict__,
            'training_config': self.training_config
        }, checkpoint_path)

        logger.info(f"💾 Checkpoint saved: {checkpoint_path}")

def main():
    """Main execution function."""
    logger.info("🎯 ImpressionCore B3 Sweet Spot Recovery Training")
    logger.info("=" * 60)

    try:
        # Initialize trainer
        trainer = SweetSpotRecoveryTrainer()

        # Setup model
        trainer.setup_model()

        # Start training
        trainer.train()

        logger.info("🎉 Sweet spot recovery training completed successfully!")

    except Exception as e:
        logger.error(f"❌ Training failed: {e!s}")
        raise

if __name__ == "__main__":
    main()
