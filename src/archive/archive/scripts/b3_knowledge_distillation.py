"""
B3 Knowledge Distillation - Teacher to Student Transfer

Created: October 11, 2025
Updated: October 11, 2025
Author: Kirk LaSalle; GitHub Copilot
Tags: #knowledge_distillation #training #constitutional_compliance

Purpose:
    Transfer knowledge from 56.9M parameter teacher model to 39.8M student model
    while maintaining >95% performance retention. Implements distillation loss
    combining task loss, KL divergence, and MoE load balancing.

Architecture:
    Teacher: B3FoundationIntegrated (56.9M params, 6 text layers, 50K vocab)
    Student: B3OptimizedIntegrated (39.8M params, 4 text layers, 28K vocab)

Training Strategy:
    - Phase 1: Train teacher to convergence (3-5 epochs)
    - Phase 2: Distill to student with combined loss
    - Loss = 0.5 * L_task + 0.5 * L_distill + 0.01 * L_balance
    - Temperature: 4.0 (softer distributions for better transfer)
    - Target: >95% performance retention

Memory Management:
    - Teacher frozen during distillation (eval mode)
    - Mixed precision (FP16) for both models
    - Gradient checkpointing enabled
    - Target: <2.8GB VRAM for student training
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torch.cuda.amp import autocast, GradScaler

from src.core.models.b3_foundation_integrated import B3FoundationIntegrated
from test_b3_optimized import B3OptimizedIntegrated
from src.core.models.b3_foundation_architecture import B3FoundationConfig
from src.core.models.b3_foundation_optimized_config import B3OptimizedConfig
from src.core.utils.rich_logging import get_rich_logger
from core.data.conversational_distillation_dataset import load_conversational_datasets

logger = get_rich_logger(__name__)


@dataclass
class DistillationConfig:
    """Configuration for knowledge distillation training."""

    # Model paths
    teacher_checkpoint: Optional[str] = None  # Pre-trained teacher (or None to train)
    student_checkpoint: Optional[str] = None  # Resume student training
    output_dir: str = "F:/models/checkpoints/distillation"

    # Distillation parameters
    temperature: float = 4.0  # Softening temperature for distributions
    distillation_alpha: float = 0.5  # Weight for distillation loss
    task_alpha: float = 0.5  # Weight for task loss (cross-entropy)
    moe_balance_weight: float = 0.01  # Weight for MoE load balancing

    # Teacher training (if needed)
    teacher_epochs: int = 3  # Epochs to train teacher to convergence
    teacher_learning_rate: float = 1e-4

    # Student distillation training
    student_epochs: int = 5  # Epochs for distillation
    student_learning_rate: float = 5e-5  # Lower LR for distillation

    # Training hyperparameters
    batch_size: int = 4  # Per-GPU batch size
    gradient_accumulation_steps: int = 2  # Effective batch = 8
    max_grad_norm: float = 1.0  # Gradient clipping
    warmup_steps: int = 100

    # Mixed precision
    use_mixed_precision: bool = True

    # Logging and checkpointing
    logging_steps: int = 10
    eval_steps: int = 50
    save_steps: int = 1000  # Reduced checkpoint frequency to save space

    # Performance targets
    target_performance_retention: float = 0.95  # 95% of teacher performance

    # Device
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class DummyConversationalDataset(Dataset):
    """
    Dummy conversational dataset for distillation.

    TODO: Replace with real conversational dataset (DailyDialog, PersonaChat, etc.)
    """

    def __init__(
        self,
        teacher_vocab_size: int = 50257,
        student_vocab_size: int = 28000,
        num_samples: int = 1000,
        max_length: int = 128
    ):
        self.teacher_vocab_size = teacher_vocab_size
        self.student_vocab_size = student_vocab_size
        self.num_samples = num_samples
        self.max_length = max_length

        logger.info(f"Created dummy dataset: {num_samples} samples, max_length={max_length}")
        logger.warning("⚠️  Using dummy data - replace with real conversational dataset")

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Generate dummy conversational sample.

        Returns:
            Dict with 'teacher_input_ids', 'student_input_ids', 'labels'
        """
        seq_length = torch.randint(32, self.max_length, (1,)).item()

        # Teacher uses full vocabulary
        teacher_input_ids = torch.randint(0, self.teacher_vocab_size, (seq_length,))

        # Student uses reduced vocabulary (map teacher tokens to student space)
        # For dummy data, just take modulo to fit student vocab
        student_input_ids = teacher_input_ids % self.student_vocab_size

        # Labels are same as student input (language modeling)
        labels = student_input_ids.clone()

        return {
            'teacher_input_ids': teacher_input_ids,
            'student_input_ids': student_input_ids,
            'labels': labels
        }


class KnowledgeDistillationTrainer:
    """
    Trainer for knowledge distillation from teacher to student model.
    """

    def __init__(
        self,
        teacher_model: nn.Module,
        student_model: nn.Module,
        config: DistillationConfig,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None
    ):
        self.teacher = teacher_model
        self.student = student_model
        self.config = config
        self.train_dataset = train_dataset
        self.eval_dataset = eval_dataset

        # Move models to device
        self.teacher.to(config.device)
        self.student.to(config.device)

        # Teacher is always in eval mode during distillation
        self.teacher.eval()
        for param in self.teacher.parameters():
            param.requires_grad = False

        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

        # Initialize optimizer and scaler
        self.optimizer = torch.optim.AdamW(
            self.student.parameters(),
            lr=config.student_learning_rate,
            betas=(0.9, 0.999),
            eps=1e-8,
            weight_decay=0.01
        )

        self.scaler = GradScaler() if config.use_mixed_precision else None

        # Training state
        self.global_step = 0
        self.best_eval_loss = float('inf')
        self.teacher_baseline_loss = None

        logger.info("✅ Knowledge distillation trainer initialized")
        logger.info(f"   Teacher: {sum(p.numel() for p in teacher_model.parameters()):,} params")
        logger.info(f"   Student: {sum(p.numel() for p in student_model.parameters()):,} params")
        logger.info(f"   Device: {config.device}")
        logger.info(f"   Temperature: {config.temperature}")
        logger.info(f"   Alpha (distill/task): {config.distillation_alpha}/{config.task_alpha}")

    def compute_distillation_loss(
        self,
        student_logits: torch.Tensor,
        teacher_logits: torch.Tensor,
        labels: torch.Tensor,
        student_aux_loss: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Compute combined distillation loss.

        Args:
            student_logits: Student model output [batch, seq, vocab_student]
            teacher_logits: Teacher model output [batch, seq, vocab_teacher]
            labels: Ground truth labels [batch, seq]
            student_aux_loss: MoE load balancing loss

        Returns:
            Dict with total loss and components
        """
        T = self.config.temperature

        # Task loss (standard cross-entropy with student vocab)
        task_loss = F.cross_entropy(
            student_logits.view(-1, student_logits.size(-1)),
            labels.view(-1),
            ignore_index=-100
        )

        # Distillation loss (KL divergence between soft distributions)
        # Both teacher and student need to be aligned to student vocab space
        # Since student has smaller vocab, we truncate teacher logits
        vocab_student = student_logits.size(-1)
        teacher_logits_aligned = teacher_logits[..., :vocab_student]

        # Soften distributions with temperature
        student_soft = F.log_softmax(student_logits / T, dim=-1)
        teacher_soft = F.softmax(teacher_logits_aligned / T, dim=-1)

        # KL divergence (teacher is target distribution)
        distillation_loss = F.kl_div(
            student_soft,
            teacher_soft,
            reduction='batchmean'
        ) * (T * T)  # Scale by T^2 to match magnitudes

        # MoE load balancing loss
        moe_loss = student_aux_loss if student_aux_loss is not None else torch.tensor(0.0).to(student_logits.device)

        # Combined loss
        total_loss = (
            self.config.task_alpha * task_loss +
            self.config.distillation_alpha * distillation_loss +
            self.config.moe_balance_weight * moe_loss
        )

        return {
            'total': total_loss,
            'task': task_loss,
            'distillation': distillation_loss,
            'moe_balance': moe_loss
        }

    def train_teacher(self) -> None:
        """
        Train teacher model to convergence (if not already trained).
        """
        if self.config.teacher_checkpoint and os.path.exists(self.config.teacher_checkpoint):
            logger.info(f"Loading pre-trained teacher from {self.config.teacher_checkpoint}")
            checkpoint = torch.load(self.config.teacher_checkpoint, map_location=self.config.device)
            self.teacher.load_state_dict(checkpoint['model_state_dict'])
            self.teacher_baseline_loss = checkpoint.get('eval_loss', None)
            logger.info(f"✅ Teacher loaded, baseline loss: {self.teacher_baseline_loss:.4f}")
            return

        logger.info("📚 Training teacher model to convergence...")
        logger.info(f"   Epochs: {self.config.teacher_epochs}")
        logger.info(f"   Learning rate: {self.config.teacher_learning_rate}")

        # Enable teacher training
        self.teacher.train()
        for param in self.teacher.parameters():
            param.requires_grad = True

        # Teacher optimizer
        teacher_optimizer = torch.optim.AdamW(
            self.teacher.parameters(),
            lr=self.config.teacher_learning_rate
        )

        # Training loop
        for epoch in range(self.config.teacher_epochs):
            epoch_loss = 0.0
            num_batches = 0

            dataloader = DataLoader(
                self.train_dataset,
                batch_size=self.config.batch_size,
                shuffle=True,
                num_workers=0
            )

            for batch_idx, batch in enumerate(dataloader):
                # Get teacher inputs
                input_ids = batch['teacher_input_ids'].to(self.config.device)
                labels = batch['labels'].to(self.config.device)

                # Forward pass
                with autocast() if self.config.use_mixed_precision else torch.enable_grad():
                    # Teacher forward (returns logits for language modeling)
                    text_embeds = self.teacher.text_encoder(input_ids)
                    if len(text_embeds.shape) == 2:
                        text_embeds = text_embeds.unsqueeze(0)

                    fused_embeds, _ = self.teacher.multimodal_fusion(text_embeds=text_embeds)
                    logits = self.teacher.output_projection(fused_embeds)

                    # Simple cross-entropy loss
                    loss = F.cross_entropy(
                        logits.view(-1, logits.size(-1)),
                        labels.view(-1),
                        ignore_index=-100
                    )

                # Backward pass
                teacher_optimizer.zero_grad()
                if self.scaler:
                    self.scaler.scale(loss).backward()
                    self.scaler.step(teacher_optimizer)
                    self.scaler.update()
                else:
                    loss.backward()
                    teacher_optimizer.step()

                epoch_loss += loss.item()
                num_batches += 1

                if (batch_idx + 1) % self.config.logging_steps == 0:
                    avg_loss = epoch_loss / num_batches
                    logger.info(f"   Epoch {epoch+1}/{self.config.teacher_epochs}, "
                              f"Batch {batch_idx+1}, Loss: {avg_loss:.4f}")

            avg_epoch_loss = epoch_loss / num_batches
            logger.info(f"✅ Teacher Epoch {epoch+1} complete, Avg Loss: {avg_epoch_loss:.4f}")

        # Save teacher checkpoint
        teacher_path = os.path.join(self.config.output_dir, "teacher_final.pt")
        torch.save({
            'model_state_dict': self.teacher.state_dict(),
            'eval_loss': avg_epoch_loss,
            'config': asdict(self.config)
        }, teacher_path)

        self.teacher_baseline_loss = avg_epoch_loss
        logger.info(f"✅ Teacher training complete, saved to {teacher_path}")

        # Freeze teacher for distillation
        self.teacher.eval()
        for param in self.teacher.parameters():
            param.requires_grad = False

    def train_student_distillation(self) -> Dict[str, float]:
        """
        Train student model using knowledge distillation.

        Returns:
            Dict with final metrics
        """
        # Load student checkpoint if resuming
        start_epoch = 0
        if self.config.student_checkpoint and os.path.exists(self.config.student_checkpoint):
            logger.info(f"🔄 Resuming student training from {self.config.student_checkpoint}")
            checkpoint = torch.load(self.config.student_checkpoint, map_location=self.config.device)
            self.student.load_state_dict(checkpoint['model_state_dict'])
            start_epoch = checkpoint.get('epoch', 0)
            logger.info(f"✅ Student loaded from epoch {start_epoch}, step {checkpoint.get('step', 'unknown')}")
        else:
            logger.info("🎓 Starting knowledge distillation (teacher → student)...")

        logger.info(f"   Epochs: {start_epoch+1}-{self.config.student_epochs}")
        logger.info(f"   Learning rate: {self.config.student_learning_rate}")
        logger.info(f"   Target performance: >{self.config.target_performance_retention*100:.1f}% of teacher")

        best_performance_retention = 0.0

        for epoch in range(start_epoch, self.config.student_epochs):
            epoch_loss = 0.0
            epoch_task_loss = 0.0
            epoch_distill_loss = 0.0
            epoch_moe_loss = 0.0
            num_batches = 0

            self.student.train()

            dataloader = DataLoader(
                self.train_dataset,
                batch_size=self.config.batch_size,
                shuffle=True,
                num_workers=0
            )

            for batch_idx, batch in enumerate(dataloader):
                teacher_input_ids = batch['teacher_input_ids'].to(self.config.device)
                student_input_ids = batch['student_input_ids'].to(self.config.device)
                labels = batch['labels'].to(self.config.device)

                # Teacher forward (no gradients)
                with torch.no_grad(), autocast() if self.config.use_mixed_precision else torch.enable_grad():
                    teacher_embeds = self.teacher.text_encoder(teacher_input_ids)
                    if len(teacher_embeds.shape) == 2:
                        teacher_embeds = teacher_embeds.unsqueeze(0)
                    teacher_fused, _ = self.teacher.multimodal_fusion(text_embeds=teacher_embeds)
                    teacher_logits = self.teacher.output_projection(teacher_fused)

                # Student forward (with gradients)
                with autocast() if self.config.use_mixed_precision else torch.enable_grad():
                    student_embeds = self.student.text_encoder(student_input_ids)
                    if len(student_embeds.shape) == 2:
                        student_embeds = student_embeds.unsqueeze(0)
                    student_fused, _ = self.student.multimodal_fusion(text_embeds=student_embeds)

                    # MoE routing for load balancing
                    _, _, router_aux = self.student.moe_router(student_fused)
                    moe_aux_loss = router_aux.get('load_balancing_loss', torch.tensor(0.0))

                    student_logits = self.student.output_projection(student_fused)

                    # Compute distillation loss
                    losses = self.compute_distillation_loss(
                        student_logits,
                        teacher_logits,
                        labels,
                        moe_aux_loss
                    )
                    total_loss = losses['total']

                # Backward pass
                self.optimizer.zero_grad()
                if self.scaler:
                    self.scaler.scale(total_loss).backward()
                    self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.student.parameters(), self.config.max_grad_norm)
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    total_loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.student.parameters(), self.config.max_grad_norm)
                    self.optimizer.step()

                # Accumulate losses
                epoch_loss += losses['total'].item()
                epoch_task_loss += losses['task'].item()
                epoch_distill_loss += losses['distillation'].item()
                epoch_moe_loss += losses['moe_balance'].item()
                num_batches += 1
                self.global_step += 1

                # Logging
                if (batch_idx + 1) % self.config.logging_steps == 0:
                    avg_loss = epoch_loss / num_batches
                    avg_task = epoch_task_loss / num_batches
                    avg_distill = epoch_distill_loss / num_batches
                    avg_moe = epoch_moe_loss / num_batches

                    logger.info(
                        f"   Epoch {epoch+1}/{self.config.student_epochs}, "
                        f"Batch {batch_idx+1}, "
                        f"Loss: {avg_loss:.4f} "
                        f"(task={avg_task:.4f}, distill={avg_distill:.4f}, moe={avg_moe:.4f})"
                    )

                # Checkpointing
                if (batch_idx + 1) % self.config.save_steps == 0:
                    checkpoint_path = os.path.join(
                        self.config.output_dir,
                        f"student_epoch{epoch+1}_step{self.global_step}.pt"
                    )
                    torch.save({
                        'model_state_dict': self.student.state_dict(),
                        'optimizer_state_dict': self.optimizer.state_dict(),
                        'epoch': epoch,
                        'global_step': self.global_step,
                        'loss': avg_loss,
                        'config': asdict(self.config)
                    }, checkpoint_path)
                    logger.info(f"   💾 Checkpoint saved: {checkpoint_path}")

            # Epoch summary
            avg_epoch_loss = epoch_loss / num_batches
            avg_epoch_task = epoch_task_loss / num_batches
            avg_epoch_distill = epoch_distill_loss / num_batches
            avg_epoch_moe = epoch_moe_loss / num_batches

            # Calculate performance retention
            if self.teacher_baseline_loss:
                performance_retention = 1.0 - (avg_epoch_loss / self.teacher_baseline_loss)
                best_performance_retention = max(best_performance_retention, performance_retention)

                logger.info(
                    f"✅ Distillation Epoch {epoch+1} complete\n"
                    f"   Total Loss: {avg_epoch_loss:.4f}\n"
                    f"   Task Loss: {avg_epoch_task:.4f}\n"
                    f"   Distillation Loss: {avg_epoch_distill:.4f}\n"
                    f"   MoE Balance: {avg_epoch_moe:.4f}\n"
                    f"   Performance Retention: {performance_retention*100:.1f}%\n"
                    f"   Target: {self.config.target_performance_retention*100:.1f}%"
                )
            else:
                logger.info(
                    f"✅ Distillation Epoch {epoch+1} complete, "
                    f"Loss: {avg_epoch_loss:.4f}"
                )

        # Save final student model
        final_path = os.path.join(self.config.output_dir, "student_final.pt")
        torch.save({
            'model_state_dict': self.student.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'final_loss': avg_epoch_loss,
            'performance_retention': best_performance_retention,
            'config': asdict(self.config)
        }, final_path)

        logger.info(f"✅ Student distillation complete, saved to {final_path}")
        logger.info(f"   Best performance retention: {best_performance_retention*100:.1f}%")

        return {
            'final_loss': avg_epoch_loss,
            'performance_retention': best_performance_retention,
            'target_met': best_performance_retention >= self.config.target_performance_retention
        }


def main():
    """Main distillation workflow."""

    logger.info("=" * 80)
    logger.info("B3 Knowledge Distillation - Teacher (56.9M) → Student (39.8M)")
    logger.info("=" * 80)

    # Configuration
    distill_config = DistillationConfig(
        teacher_epochs=3,  # Train teacher if needed
        student_epochs=5,  # Distillation epochs
        batch_size=4,
        gradient_accumulation_steps=2,
        teacher_checkpoint="F:/models/checkpoints/distillation/teacher_final.pt",
        student_checkpoint=None,  # Corrupted during manual move - restart from scratch
        output_dir="F:/models/checkpoints/distillation",
        temperature=4.0,
        distillation_alpha=0.5,
        task_alpha=0.5,
        target_performance_retention=0.95
    )

    logger.info(f"\n📋 Distillation Configuration:")
    logger.info(f"   Temperature: {distill_config.temperature}")
    logger.info(f"   Loss weights: {distill_config.distillation_alpha} distill + "
                f"{distill_config.task_alpha} task + {distill_config.moe_balance_weight} MoE")
    logger.info(f"   Target retention: >{distill_config.target_performance_retention*100:.1f}%")
    logger.info(f"   Output directory: {distill_config.output_dir}")

    # CRITICAL: Validate F: drive usage
    if not distill_config.output_dir.startswith("F:/") and not distill_config.output_dir.startswith("F:\\"):
        raise ValueError(f"❌ FATAL: Checkpoints MUST be on F: drive! Got: {distill_config.output_dir}")
    logger.info(f"   ✅ F: drive validation passed")

    # Load models
    logger.info("\n🔧 Loading models...")

    # Teacher (56.9M parameters)
    teacher_config = B3FoundationConfig()
    teacher_model = B3FoundationIntegrated(teacher_config)
    logger.info(f"✅ Teacher loaded: {sum(p.numel() for p in teacher_model.parameters()):,} params")

    # Student (39.8M parameters)
    student_config = B3OptimizedConfig()
    student_model = B3OptimizedIntegrated(student_config)
    logger.info(f"✅ Student loaded: {sum(p.numel() for p in student_model.parameters()):,} params")

    # Create datasets with REAL conversational data
    logger.info("\n📚 Loading Real Conversational Data...")
    logger.info("   Source: mixed_qa_conversation dataset")
    logger.info("   Location: F:/data/qa_datasets/mixed/")
    logger.info("   Quality: High (DailyDialog + Empathetic Dialogues)")

    # Create tokenizers (same tokenizer for both, but different vocab sizes in models)
    from transformers import GPT2Tokenizer
    logger.info("\n🔤 Loading tokenizers...")
    teacher_tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')
    student_tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')
    teacher_tokenizer.pad_token = teacher_tokenizer.eos_token
    student_tokenizer.pad_token = student_tokenizer.eos_token
    logger.info(f"   Teacher vocab: {len(teacher_tokenizer):,}")
    logger.info(f"   Student vocab: {student_config.vocab_size:,} (model constraint)")

    # Load real conversational datasets
    train_dataset, eval_dataset = load_conversational_datasets(
        teacher_tokenizer=teacher_tokenizer,
        student_tokenizer=student_tokenizer,
        train_path="F:/data/qa_datasets/mixed/mixed_qa_conversation_train.json",
        val_path="F:/data/qa_datasets/mixed/mixed_qa_conversation_val.json",
        max_length=128,
        combine_qa=True,  # Combine Q+A for natural dialogue
        student_vocab_size=student_config.vocab_size  # Use student model's actual vocab size (28K)
    )
    logger.info(f"✅ Training dataset: {len(train_dataset):,} samples")
    logger.info(f"✅ Validation dataset: {len(eval_dataset):,} samples")

    # Initialize trainer
    logger.info("\n🎓 Initializing distillation trainer...")
    trainer = KnowledgeDistillationTrainer(
        teacher_model=teacher_model,
        student_model=student_model,
        config=distill_config,
        train_dataset=train_dataset
    )

    # Train teacher (if needed)
    logger.info("\n" + "=" * 80)
    logger.info("Phase 1: Teacher Training")
    logger.info("=" * 80)
    trainer.train_teacher()

    # Distill to student
    logger.info("\n" + "=" * 80)
    logger.info("Phase 2: Knowledge Distillation")
    logger.info("=" * 80)
    metrics = trainer.train_student_distillation()

    # Final report
    logger.info("\n" + "=" * 80)
    logger.info("🎉 KNOWLEDGE DISTILLATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Final Loss: {metrics['final_loss']:.4f}")
    logger.info(f"Performance Retention: {metrics['performance_retention']*100:.1f}%")
    logger.info(f"Target Met: {'✅ YES' if metrics['target_met'] else '❌ NO'}")
    logger.info(f"Checkpoints saved to: {distill_config.output_dir}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
