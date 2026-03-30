#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Training Launcher (Stability Test)
========================================================

CONSTITUTIONAL FRAMEWORK COMPLIANCE ACHIEVED
- 35.5M parameters (UNDER 39M limit)
- Complete B3 architecture preserved
- All stability lessons incorporated
- GTX 1050 Ti optimized

Created: October 1, 2025
Author: Kirk LaSalle; GitHub Copilot
Status: STABILITY TEST MODE
"""

import argparse
import sys
import os
import time
import traceback
import logging
from datetime import datetime

# Configure logging for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'b3_hope_stability_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for B3-Hope stability test"""

    # Parse arguments
    parser = argparse.ArgumentParser(description='B3-Hope Stability Test')
    parser.add_argument('--max_steps', type=int, default=200, help='Maximum training steps')
    parser.add_argument('--save_steps', type=int, default=50, help='Save checkpoint every N steps')
    parser.add_argument('--eval_steps', type=int, default=25, help='Evaluate every N steps')
    parser.add_argument('--logging_steps', type=int, default=10, help='Log every N steps')
    parser.add_argument('--learning_rate', type=float, default=1e-5, help='Learning rate')
    parser.add_argument('--batch_size', type=int, default=1, help='Batch size')
    parser.add_argument('--max_grad_norm', type=float, default=0.5, help='Max gradient norm')

    args = parser.parse_args()

    # Print startup message
    print("\\n" + "="*70)
    print("IMPRESSIONCORE B3-HOPE STABILITY TEST")
    print("="*70)
    print(f"Starting training with {args.max_steps} steps")
    print(f"Learning rate: {args.learning_rate}")
    print(f"Batch size: {args.batch_size}")
    print(f"Max grad norm: {args.max_grad_norm}")
    print(f"Using precision: FP32 (stability mode)")
    print("="*70 + "\\n")

    try:
        # Import B3-Hope trainer
        from b3_constitutional_trainer import (
            B3HopeConfig,
            ImpressionCoreB3Hope,
            create_simple_dataloader
        )
        import torch
        from torch.optim import AdamW
        from torch.optim.lr_scheduler import CosineAnnealingLR

        logger.info("B3-Hope modules imported successfully")

        # Create configuration with test parameters
        config = B3HopeConfig()
        config.max_steps = args.max_steps
        config.learning_rate = args.learning_rate
        config.batch_size = args.batch_size
        config.max_grad_norm = args.max_grad_norm
        config.save_steps = args.save_steps
        config.eval_steps = args.eval_steps
        config.logging_steps = args.logging_steps

        logger.info(f"Configuration created with {args.max_steps} max steps")

        # Initialize model
        logger.info("Initializing B3-Hope model...")
        model = ImpressionCoreB3Hope(config).to(config.device)

        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        logger.info(f"Model initialized with {total_params:,} parameters")

        # Verify constitutional compliance
        if total_params <= 39_000_000:
            logger.info(f"CONSTITUTIONAL COMPLIANCE: {total_params:,} <= 39,000,000")
        else:
            logger.error(f"CONSTITUTIONAL VIOLATION: {total_params:,} > 39,000,000")
            return False

        # Create optimizer
        optimizer = AdamW(
            model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay,
            betas=(0.9, 0.95)
        )

        # Create scheduler
        scheduler = CosineAnnealingLR(
            optimizer,
            T_max=config.max_steps,
            eta_min=config.learning_rate * 0.1
        )

        logger.info("Optimizer and scheduler created")

        # Create dataloader
        dataloader = create_simple_dataloader(
            batch_size=config.batch_size,
            max_length=config.max_seq_length,
            num_samples=args.max_steps * 2  # Ensure enough data
        )

        logger.info("Dataloader created")

        # Training loop
        logger.info("Starting B3-Hope stability test...")
        model.train()

        losses = []
        grad_norms = []
        memory_usage = []

        for step in range(args.max_steps):
            step_start_time = time.time()

            # Get batch
            try:
                batch = next(iter(dataloader))
            except StopIteration:
                dataloader = create_simple_dataloader(
                    batch_size=config.batch_size,
                    max_length=config.max_seq_length,
                    num_samples=args.max_steps * 2
                )
                batch = next(iter(dataloader))

            # Move to device
            input_ids = batch['input_ids'].to(config.device)
            attention_mask = batch['attention_mask'].to(config.device)
            labels = batch['labels'].to(config.device)

            # Forward pass
            optimizer.zero_grad()

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
                return_loss=True
            )

            loss = outputs['loss']
            load_balancing_loss = outputs.get('load_balancing_loss', 0.0)
            total_loss = loss + load_balancing_loss

            # Backward pass
            total_loss.backward()

            # Gradient clipping
            grad_norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                config.max_grad_norm
            )

            # Optimizer step
            optimizer.step()
            scheduler.step()

            # Track metrics
            losses.append(loss.item())
            grad_norms.append(grad_norm.item())

            # Memory tracking
            if torch.cuda.is_available():
                memory_gb = torch.cuda.memory_allocated() / 1024**3
                memory_usage.append(memory_gb)
            else:
                memory_gb = 0.0

            step_time = time.time() - step_start_time
            current_lr = scheduler.get_last_lr()[0]

            # Logging
            if (step + 1) % args.logging_steps == 0:
                avg_loss = sum(losses[-args.logging_steps:]) / min(len(losses), args.logging_steps)
                avg_grad_norm = sum(grad_norms[-args.logging_steps:]) / min(len(grad_norms), args.logging_steps)

                logger.info(
                    f"Step {step+1:>3}/{args.max_steps} | "
                    f"Loss: {loss.item():.4f} | "
                    f"Avg Loss: {avg_loss:.4f} | "
                    f"LB Loss: {load_balancing_loss:.4f} | "
                    f"Grad Norm: {grad_norm:.4f} | "
                    f"Avg Grad: {avg_grad_norm:.4f} | "
                    f"LR: {current_lr:.2e} | "
                    f"Memory: {memory_gb:.2f}GB | "
                    f"Time: {step_time:.2f}s"
                )

            # Save checkpoint
            if (step + 1) % args.save_steps == 0 or (step + 1) == args.max_steps:
                checkpoint_path = f"b3_hope_stability_checkpoint_step_{step+1}.pth"

                checkpoint = {
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'scheduler_state_dict': scheduler.state_dict(),
                    'config': config.__dict__,
                    'step': step + 1,
                    'loss': loss.item(),
                    'total_params': total_params,
                    'constitutional_compliance': total_params <= 39_000_000,
                    'stability_metrics': {
                        'losses': losses,
                        'grad_norms': grad_norms,
                        'memory_usage': memory_usage,
                        'avg_loss_last_10': sum(losses[-10:]) / min(len(losses), 10),
                        'avg_grad_norm_last_10': sum(grad_norms[-10:]) / min(len(grad_norms), 10)
                    },
                    'timestamp': datetime.now().isoformat()
                }

                torch.save(checkpoint, checkpoint_path)
                logger.info(f"Checkpoint saved: {checkpoint_path}")

        # Final analysis
        print("\\n" + "="*70)
        print("B3-HOPE STABILITY TEST COMPLETE")
        print("="*70)
        print(f"Total steps: {args.max_steps}")
        print(f"Final loss: {losses[-1]:.4f}")
        print(f"Average loss: {sum(losses) / len(losses):.4f}")
        print(f"Loss reduction: {losses[0] - losses[-1]:.4f}")
        print(f"Average grad norm: {sum(grad_norms) / len(grad_norms):.4f}")
        print(f"Max memory usage: {max(memory_usage) if memory_usage else 0:.2f}GB")
        print(f"Constitutional compliance: {total_params <= 39_000_000}")
        print("="*70)

        # Check for stability
        if len(losses) >= 10:
            recent_losses = losses[-10:]
            early_losses = losses[:10] if len(losses) >= 20 else losses[:len(losses)//2]

            if sum(recent_losses) < sum(early_losses):
                print("STATUS: STABLE - Loss is decreasing")
                logger.info("B3-Hope stability test PASSED - Loss decreasing")
                return True
            else:
                print("STATUS: UNSTABLE - Loss not decreasing")
                logger.warning("B3-Hope stability test FAILED - Loss not decreasing")
                return False
        else:
            print("STATUS: INCONCLUSIVE - Insufficient data")
            return False

    except Exception as e:
        logger.error(f"Stability test failed: {str(e)}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)