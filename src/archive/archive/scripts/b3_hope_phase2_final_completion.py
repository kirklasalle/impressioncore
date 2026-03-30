#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Phase 2 Final Completion

Created: October 2, 2025
Author: GitHub Copilot & Kirk LaSalle
Purpose: Complete the final 750 steps of Phase 2 training from checkpoint_step_750.pth

This script implements the final completion strategy for Phase 2 with proven
stability, constitutional compliance, and hardware democracy validation.
"""

import os
import sys
import json
import logging
import torch
import time
from datetime import datetime
from typing import Dict, Optional
from torch.utils.data import DataLoader

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core modules
from b3_hope_f_drive_integration import (
    ImpressionCoreB3Hope,
    B3HopeFDriveEmbeddingDataset
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(f'b3_hope_phase2_final_completion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class B3HopePhase2FinalCompletion:
    """Final completion manager for Phase 2 training"""

    def __init__(self):
        self.resume_checkpoint = "b3_hope_f_drive_production_checkpoint_step_750.pth"
        self.start_step = 750
        self.target_steps = 1500
        self.remaining_steps = self.target_steps - self.start_step

        # Proven configuration from previous runs
        self.config = {
            'learning_rate': 1e-5,
            'batch_size': 1,
            'max_grad_norm': 0.5,
            'save_every': 100,
            'precision': 'fp32',  # Proven stable
            'device': 'cuda' if torch.cuda.is_available() else 'cpu'
        }

        logger.info("Phase 2 Final Completion Manager initialized")
        logger.info(f"Resume from: {self.resume_checkpoint}")
        logger.info(f"Steps: {self.start_step} → {self.target_steps} ({self.remaining_steps} remaining)")

    def validate_resume_checkpoint(self) -> bool:
        """Validate that resume checkpoint exists and is accessible"""

        if not os.path.exists(self.resume_checkpoint):
            logger.error(f"Resume checkpoint not found: {self.resume_checkpoint}")
            return False

        try:
            # Test loading checkpoint
            checkpoint = torch.load(self.resume_checkpoint, map_location='cpu')
            required_keys = ['model_state_dict', 'optimizer_state_dict', 'step', 'loss']

            for key in required_keys:
                if key not in checkpoint:
                    logger.error(f"Missing key in checkpoint: {key}")
                    return False

            logger.info(f"Checkpoint validation successful")
            logger.info(f"Checkpoint step: {checkpoint['step']}")
            logger.info(f"Checkpoint loss: {checkpoint['loss']:.6f}")

            return True

        except Exception as e:
            logger.error(f"Checkpoint validation failed: {e}")
            return False

    def load_selected_embeddings(self) -> Dict:
        """Load the Phase 2 selected embeddings manifest"""

        manifest_files = [
            "b3_hope_phase2_optimal_embeddings_20251002_120323.json",
            # Add other potential manifest files if needed
        ]

        for manifest_file in manifest_files:
            if os.path.exists(manifest_file):
                logger.info(f"Loading embeddings manifest: {manifest_file}")

                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)

                logger.info(f"Loaded {len(manifest['selected_embeddings'])} selected embeddings")
                return manifest

        logger.error("No Phase 2 embeddings manifest found")
        raise FileNotFoundError("Phase 2 embeddings manifest required for completion")

    def create_completion_trainer(self) -> tuple:
        """Create trainer optimized for completion from checkpoint"""

        logger.info("Creating completion trainer configuration...")

        # Load embeddings manifest
        embeddings_manifest = self.load_selected_embeddings()
        selected_files = embeddings_manifest['selected_embeddings']

        logger.info(f"Training dataset size: {len(selected_files)} embeddings")

        # Create trainer with proven configuration
        trainer_config = {
            'learning_rate': self.config['learning_rate'],
            'batch_size': self.config['batch_size'],
            'max_grad_norm': self.config['max_grad_norm'],
            'mixed_precision': False,  # Use FP32 for proven stability
            'device': self.config['device']
        }

        model, optimizer, dataset, dataloader = create_f_drive_trainer(
            embedding_files=selected_files,
            **trainer_config
        )

        logger.info("Completion trainer created successfully")
        logger.info(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

        return model, optimizer, dataset, dataloader

    def execute_final_completion(self) -> bool:
        """Execute the final Phase 2 completion training"""

        logger.info("="*80)
        logger.info("STARTING B3-HOPE PHASE 2 FINAL COMPLETION")
        logger.info("="*80)

        # Validation
        if not self.validate_resume_checkpoint():
            logger.error("Checkpoint validation failed - cannot proceed")
            return False

        # Create trainer
        try:
            model, optimizer, dataset, dataloader = self.create_completion_trainer()
        except Exception as e:
            logger.error(f"Trainer creation failed: {e}")
            return False

        # Load checkpoint
        logger.info(f"Loading checkpoint: {self.resume_checkpoint}")
        checkpoint = torch.load(self.resume_checkpoint, map_location=self.config['device'])

        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        current_step = checkpoint['step']
        best_loss = checkpoint['loss']

        logger.info(f"Resumed from step {current_step} with loss {best_loss:.6f}")

        # Training configuration
        model.train()
        device = self.config['device']

        logger.info(f"Training on device: {device}")
        logger.info(f"Target steps: {self.target_steps}")
        logger.info(f"Save interval: {self.config['save_every']}")

        # Training loop
        start_time = time.time()

        try:
            for step in range(current_step + 1, self.target_steps + 1):
                # Get batch
                batch_idx = (step - 1) % len(dataloader)
                batch = list(dataloader)[batch_idx]

                # Move to device
                text_embeddings = batch['text_embeddings'].to(device)
                image_embeddings = batch['image_embeddings'].to(device)
                audio_embeddings = batch['audio_embeddings'].to(device)

                # Forward pass
                optimizer.zero_grad()

                outputs = model(
                    text_embeddings=text_embeddings,
                    image_embeddings=image_embeddings,
                    audio_embeddings=audio_embeddings
                )

                loss = outputs['loss']

                # Backward pass
                loss.backward()

                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), self.config['max_grad_norm'])

                # Optimizer step
                optimizer.step()

                # Logging
                if step % 50 == 0:
                    elapsed_time = time.time() - start_time
                    steps_completed = step - current_step
                    time_per_step = elapsed_time / steps_completed if steps_completed > 0 else 0
                    remaining_steps = self.target_steps - step
                    eta_minutes = (remaining_steps * time_per_step) / 60

                    # Memory monitoring
                    if torch.cuda.is_available():
                        memory_used = torch.cuda.memory_allocated() / (1024**3)  # GB
                        memory_percent = (memory_used / 4.0) * 100  # 4GB GTX 1050 Ti
                    else:
                        memory_used = 0
                        memory_percent = 0

                    logger.info(f"Step {step:,}/{self.target_steps:,} | "
                              f"Loss: {loss.item():.6f} | "
                              f"Memory: {memory_used:.2f}GB ({memory_percent:.1f}%) | "
                              f"ETA: {eta_minutes:.1f}min")

                # Checkpoint saving
                if step % self.config['save_every'] == 0 or step == self.target_steps:
                    checkpoint_path = f"b3_hope_f_drive_production_checkpoint_step_{step}.pth"

                    torch.save({
                        'model_state_dict': model.state_dict(),
                        'optimizer_state_dict': optimizer.state_dict(),
                        'step': step,
                        'loss': loss.item(),
                        'config': self.config,
                        'timestamp': datetime.now().isoformat()
                    }, checkpoint_path)

                    logger.info(f"Checkpoint saved: {checkpoint_path}")

                    # Update best loss
                    if loss.item() < best_loss:
                        best_loss = loss.item()

                        # Save best model
                        best_model_path = "b3_hope_f_drive_production_best_model.pth"
                        torch.save({
                            'model_state_dict': model.state_dict(),
                            'step': step,
                            'loss': loss.item(),
                            'config': self.config
                        }, best_model_path)

                        logger.info(f"New best model saved: {best_model_path} (loss: {loss.item():.6f})")

            # Completion success
            total_time = time.time() - start_time
            logger.info("="*80)
            logger.info("B3-HOPE PHASE 2 FINAL COMPLETION SUCCESSFUL!")
            logger.info("="*80)
            logger.info(f"Training completed: {self.target_steps:,} steps")
            logger.info(f"Total time: {total_time/60:.1f} minutes")
            logger.info(f"Final loss: {loss.item():.6f}")
            logger.info(f"Best loss: {best_loss:.6f}")

            return True

        except KeyboardInterrupt:
            logger.warning("Training interrupted by user")
            return False
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False

def main():
    """Main execution function"""

    completion_manager = B3HopePhase2FinalCompletion()

    # Execute final completion
    success = completion_manager.execute_final_completion()

    if success:
        logger.info("Phase 2 completion successful - ready for Phase 3 planning")
    else:
        logger.error("Phase 2 completion failed - review logs for details")

    return success

if __name__ == "__main__":
    main()