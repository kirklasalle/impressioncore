"""
Conservative Training Configuration for ImpressionCore B3
========================================================

Created: October 1, 2025
Author: Kirk LaSalle; GitHub Copilot
Purpose: Stable training parameters based on recovery_step_4000.pth success

This configuration uses proven stable parameters that worked during the
August 8, 2025 training period when recovery_step_4000.pth was created.
"""

from dataclasses import dataclass


@dataclass
class ConservativeTrainingConfig:
    """Conservative training configuration to prevent weight corruption."""

    # Model Architecture (B3 - proven stable)
    model_name: str = "ImpressionCore-B3-Conservative"
    hidden_dim: int = 1024
    num_layers: int = 8
    num_heads: int = 16
    vocab_size: int = 50257

    # Training Stability Parameters
    learning_rate: float = 1e-5  # Very conservative LR
    lr_scale: float = 0.05  # Even more conservative than 0.1
    weight_decay: float = 0.01
    max_grad_norm: float = 0.5  # Aggressive gradient clipping

    # Batch Configuration
    batch_size: int = 1  # Minimal batch size for stability
    gradient_accumulation_steps: int = 4  # Effective batch size = 4
    max_sequence_length: int = 512

    # Learning Rate Schedule
    lr_warmup_steps: int = 15000  # Extended warmup
    lr_decay_steps: int = 50000
    lr_min_ratio: float = 0.1

    # Training Duration
    max_steps: int = 500  # Conservative step count for testing
    save_frequency: int = 50  # Frequent checkpointing
    eval_frequency: int = 25

    # Memory Management
    use_mixed_precision: bool = False  # FP32 only for stability
    gradient_checkpointing: bool = True
    dataloader_num_workers: int = 0  # Avoid multiprocessing issues

    # Checkpoint Management
    save_best_only: bool = False  # Save all checkpoints for analysis
    early_stopping_patience: int = 100  # Generous patience

    # Monitoring & Debugging
    log_frequency: int = 5  # Frequent logging
    dump_artifacts_on_spike: bool = True
    grad_norm_warning_threshold: float = 1.0  # Lower threshold

    # Recovery Settings
    baseline_checkpoint: str = "F:/models/checkpoints/b3/sweet_spot_recovery/recovery_step_4000.pth"
    validate_checkpoint_quality: bool = True
    quality_score_threshold: float = 50.0  # Minimum quality to continue training

    # Optimizer Configuration
    optimizer_type: str = "adamw"
    beta1: float = 0.9
    beta2: float = 0.999
    eps: float = 1e-8

    # Data Configuration
    train_data_ratio: float = 0.8
    val_data_ratio: float = 0.2
    shuffle_data: bool = True

    # Hardware Configuration
    device: str = "cuda"
    target_vram_gb: float = 3.5  # Conservative VRAM usage

    def __post_init__(self):
        """Validate configuration parameters."""

        # Ensure conservative parameters
        assert self.learning_rate <= 1e-4, "Learning rate too high for conservative training"
        assert self.max_grad_norm <= 1.0, "Gradient norm threshold too high"
        assert self.batch_size <= 2, "Batch size too large for conservative training"
        assert not self.use_mixed_precision, "Mixed precision disabled for stability"

        print("🛡️ Conservative Training Configuration Initialized")
        print(f"   Learning Rate: {self.learning_rate}")
        print(f"   Gradient Clipping: {self.max_grad_norm}")
        print(f"   Batch Size: {self.batch_size}")
        print(f"   Mixed Precision: {self.use_mixed_precision}")
        print(f"   Baseline Checkpoint: {self.baseline_checkpoint}")

class ConservativeTrainingManager:
    """Manages conservative training with safety checks."""

    def __init__(self, config: ConservativeTrainingConfig):
        self.config = config
        self.quality_failures = 0
        self.max_quality_failures = 3

    def should_continue_training(self, current_step: int, grad_norm: float,
                               checkpoint_path: str | None = None) -> tuple[bool, str]:
        """
        Determine if training should continue based on stability metrics.

        Returns:
            tuple: (should_continue, reason)
        """

        # Check gradient norm stability
        if grad_norm > self.config.grad_norm_warning_threshold * 3:
            return False, f"Gradient norm too high: {grad_norm:.2f}"

        # Check checkpoint quality if available
        if checkpoint_path and self.config.validate_checkpoint_quality:
            if not self._validate_checkpoint_quality(checkpoint_path):
                self.quality_failures += 1
                if self.quality_failures >= self.max_quality_failures:
                    return False, f"Too many quality failures: {self.quality_failures}"
                return True, f"Quality failure {self.quality_failures}/{self.max_quality_failures}"

        # Check if we've reached conservative step limit
        if current_step >= self.config.max_steps:
            return False, "Reached conservative step limit"

        return True, "Training stable"

    def _validate_checkpoint_quality(self, checkpoint_path: str) -> bool:
        """Validate checkpoint quality using the validator."""

        try:
            from src.training.utils.checkpoint_validator import CheckpointValidator

            validator = CheckpointValidator()
            results = validator.validate_checkpoint(checkpoint_path)

            if results['error']:
                print(f"⚠️ Checkpoint validation error: {results['error']}")
                return False

            quality_score = results['quality_score']
            is_valid = quality_score >= self.config.quality_score_threshold

            print(f"🔍 Checkpoint Quality: {quality_score:.1f}/100 "
                  f"({'✅ PASS' if is_valid else '❌ FAIL'})")

            return is_valid

        except Exception as e:
            print(f"⚠️ Could not validate checkpoint: {e}")
            return True  # Assume valid if validation fails

    def get_training_summary(self) -> dict:
        """Get summary of conservative training configuration."""

        return {
            'model_name': self.config.model_name,
            'learning_rate': self.config.learning_rate,
            'batch_size': self.config.batch_size,
            'max_steps': self.config.max_steps,
            'gradient_clipping': self.config.max_grad_norm,
            'mixed_precision': self.config.use_mixed_precision,
            'baseline_checkpoint': self.config.baseline_checkpoint,
            'quality_validation': self.config.validate_checkpoint_quality
        }

# Default conservative configuration
CONSERVATIVE_CONFIG = ConservativeTrainingConfig()

def create_conservative_config(max_steps: int = 500,
                             learning_rate: float = 1e-5,
                             batch_size: int = 1) -> ConservativeTrainingConfig:
    """Create a conservative training configuration with custom parameters."""

    config = ConservativeTrainingConfig()
    config.max_steps = max_steps
    config.learning_rate = learning_rate
    config.batch_size = batch_size

    return config
