#!/usr/bin/env python3
"""
B3 Phase 2 Production Training Script - Conservative Scaling from Proven Baseline
===============================================================================

CONSERVATIVE APPROACH: Scale from proven 101.5M (Phase 1) to ~150M parameters
Target: 1.5x scaling with memory efficiency on GTX 1050 Ti (4GB VRAM)

Based on Phase 1 SUCCESS:
- Baseline: 101.5M parameters, 0.001187 loss, 1570MB VRAM
- Target: ~150M parameters, <2.5GB VRAM, similar convergence quality

Created: August 4, 2025
Updated: August 6, 2025
Author: Kirk LaSalle & GitHub Copilot
Tags: #src/training/b3_phase2_production_training.py #training #phase2 #conservative
Status: Ready for Conservative Scaling Testing
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import autocast, GradScaler
from torch.nn.utils import clip_grad_norm_
import math
import logging
from datetime import datetime
from pathlib import Path
import json
import time
from typing import Dict, Any, Optional, List, Tuple
import shutil

# Add src to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from core.utils.rich_enhancements import create_rich_console, create_progress_bar
from core.utils.rich_logging import setup_rich_logging
from core.utils.rich_status_animation import RichStatusManager

# Setup rich console and logging
console = create_rich_console()
logger = setup_rich_logging("B3_Phase2_Production_Training")

class B3MixtureOfExpertsV2(nn.Module):
    """Enhanced Mixture of Experts for Phase 2 - Conservative Scaling."""

    def __init__(self, hidden_dim: int, expert_dim: int, num_experts: int, active_experts: int):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.expert_dim = expert_dim
        self.num_experts = num_experts
        self.active_experts = active_experts

        # Enhanced router with better initialization
        self.router = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, num_experts)
        )

        # Expert networks with improved architecture
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, expert_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(expert_dim, expert_dim),
                nn.ReLU(),
                nn.Linear(expert_dim, hidden_dim)
            ) for _ in range(num_experts)
        ])

        # Load balancing loss coefficient
        self.load_balance_loss_coef = 0.01

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_size, seq_len, _ = x.shape
        x_flat = x.view(-1, self.hidden_dim)

        # Route to experts
        router_logits = self.router(x_flat)
        router_probs = torch.softmax(router_logits, dim=-1)

        # Select top-k experts
        topk_probs, topk_indices = torch.topk(router_probs, self.active_experts, dim=-1)
        topk_probs = topk_probs / topk_probs.sum(dim=-1, keepdim=True)

        # Compute expert outputs
        output = torch.zeros_like(x_flat)
        for i in range(self.active_experts):
            expert_idx = topk_indices[:, i]
            expert_prob = topk_probs[:, i].unsqueeze(-1)

            # Process through selected experts
            for expert_id in range(self.num_experts):
                mask = (expert_idx == expert_id)
                if mask.any():
                    expert_input = x_flat[mask]
                    expert_output = self.experts[expert_id](expert_input)
                    output[mask] += expert_prob[mask] * expert_output

        # Load balancing loss
        expert_usage = router_probs.mean(dim=0)
        load_balance_loss = (expert_usage * torch.log(expert_usage + 1e-8)).sum()

        output = output.view(batch_size, seq_len, self.hidden_dim)
        return output, self.load_balance_loss_coef * load_balance_loss

class B3TransformerBlockV2(nn.Module):
    """Enhanced Transformer block for Phase 2 - Conservative Scaling."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        hidden_dim = config['hidden_dim']
        num_heads = config['num_heads']

        # Multi-head attention with improved configuration
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_heads,
            dropout=config['dropout'],
            batch_first=True
        )

        # Enhanced mixture of experts
        self.moe = B3MixtureOfExpertsV2(
            hidden_dim=hidden_dim,
            expert_dim=config['expert_dim'],
            num_experts=config['num_experts'],
            active_experts=config['active_experts']
        )

        # Layer norms with improved initialization
        self.norm1 = nn.LayerNorm(hidden_dim, eps=1e-6)
        self.norm2 = nn.LayerNorm(hidden_dim, eps=1e-6)

        # Dropout with residual scaling
        self.dropout = nn.Dropout(config['dropout'])
        self.residual_scale = math.sqrt(0.5)  # Scale residual connections

    def forward(self, x: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        # Self-attention with residual connection
        residual = x
        x = self.norm1(x)
        attn_output, _ = self.attention(x, x, x, attn_mask=attention_mask)
        x = residual + self.dropout(attn_output) * self.residual_scale

        # MoE with residual connection
        residual = x
        x = self.norm2(x)
        moe_output, load_balance_loss = self.moe(x)
        x = residual + self.dropout(moe_output) * self.residual_scale

        return x, load_balance_loss

class B3ModelV2(nn.Module):
    """ImpressionCore B3 Model V2 - Phase 2 Conservative Scaling."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config

        # Enhanced embeddings with better initialization
        self.token_embedding = nn.Embedding(config['vocab_size'], config['hidden_dim'])
        self.position_embedding = nn.Embedding(config['max_seq_length'], config['hidden_dim'])

        # Embedding dropout
        self.embedding_dropout = nn.Dropout(config['dropout'])

        # Transformer blocks
        self.blocks = nn.ModuleList([
            B3TransformerBlockV2(config) for _ in range(config['num_layers'])
        ])

        # Output layers with improved architecture
        self.norm = nn.LayerNorm(config['hidden_dim'], eps=1e-6)
        self.output_projection = nn.Linear(config['hidden_dim'], config['vocab_size'])

        # Initialize weights with improved strategy
        self.apply(self._init_weights)

        # Gradient checkpointing support
        self.gradient_checkpointing = False

    def _init_weights(self, module):
        """Initialize model weights with improved strategy."""
        if isinstance(module, nn.Linear):
            # Use Xavier/Glorot initialization for better convergence
            torch.nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.ones_(module.weight)
            torch.nn.init.zeros_(module.bias)

    def gradient_checkpointing_enable(self):
        """Enable gradient checkpointing for memory efficiency."""
        self.gradient_checkpointing = True

    def gradient_checkpointing_disable(self):
        """Disable gradient checkpointing."""
        self.gradient_checkpointing = False

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        batch_size, seq_len = input_ids.shape

        # Create position ids
        position_ids = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, -1)

        # Embeddings with dropout
        token_embeds = self.token_embedding(input_ids)
        position_embeds = self.position_embedding(position_ids)
        x = self.embedding_dropout(token_embeds + position_embeds)

        # Create attention mask for transformer
        if attention_mask is not None:
            attention_mask = attention_mask.bool()
            # Convert to transformer format
            attention_mask = attention_mask.logical_not()
            attention_mask = attention_mask.float() * -10000.0

        # Transformer blocks with load balancing
        total_load_balance_loss = 0.0

        for block in self.blocks:
            if self.gradient_checkpointing and self.training:
                # Use gradient checkpointing
                def create_custom_forward(module):
                    def custom_forward(*inputs):
                        return module(*inputs)
                    return custom_forward

                x, load_balance_loss = torch.utils.checkpoint.checkpoint(
                    create_custom_forward(block), x, attention_mask
                )
            else:
                x, load_balance_loss = block(x, attention_mask)

            total_load_balance_loss += load_balance_loss

        # Output projection
        x = self.norm(x)
        logits = self.output_projection(x)

        return {
            'logits': logits,
            'load_balance_loss': total_load_balance_loss
        }

    def count_parameters(self) -> int:
        """Count total trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

def load_phase1_checkpoint(checkpoint_path: str) -> Dict[str, Any]:
    """Load Phase 1 checkpoint for initialization."""
    if not os.path.exists(checkpoint_path):
        console.print(f"⚠️ Phase 1 checkpoint not found: {checkpoint_path}")
        return None

    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    console.print(f"✅ Loaded Phase 1 checkpoint: {checkpoint_path}")
    console.print(f"📊 Phase 1 Loss: {checkpoint.get('final_loss', 'Unknown')}")
    console.print(f"🧠 Phase 1 Parameters: {checkpoint.get('total_parameters', 'Unknown')}")

    return checkpoint

def create_enhanced_dataset(config: Dict[str, Any], num_samples: int = 3000) -> List[Dict[str, torch.Tensor]]:
    """Create enhanced dataset for Phase 2 training."""
    dataset = []
    seq_length = config['max_seq_length']
    vocab_size = config['vocab_size']

    console.print(f"📚 Creating enhanced dataset with {num_samples} samples...")

    for i in range(num_samples):
        # More diverse token sequences
        if i % 3 == 0:
            # Pattern 1: Random with structure
            input_ids = torch.randint(0, vocab_size // 2, (seq_length,))
        elif i % 3 == 1:
            # Pattern 2: Higher frequency tokens
            input_ids = torch.randint(vocab_size // 2, vocab_size, (seq_length,))
        else:
            # Pattern 3: Mixed distribution
            input_ids = torch.randint(0, vocab_size, (seq_length,))

        # Create realistic attention mask (some padding)
        if i % 10 == 0:  # 10% have padding
            real_length = torch.randint(seq_length // 2, seq_length, (1,)).item()
            attention_mask = torch.zeros_like(input_ids)
            attention_mask[:real_length] = 1
        else:
            attention_mask = torch.ones_like(input_ids)

        # Labels are shifted input_ids
        labels = input_ids.clone()

        dataset.append({
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        })

    return dataset

def get_memory_info() -> Dict[str, float]:
    """Get current GPU memory information."""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3  # GB
        reserved = torch.cuda.memory_reserved() / 1024**3   # GB
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB

        return {
            'allocated_gb': allocated,
            'reserved_gb': reserved,
            'total_gb': total,
            'allocated_mb': allocated * 1024,
            'reserved_mb': reserved * 1024,
            'total_mb': total * 1024,
            'utilization_percent': (allocated / total) * 100
        }
    return {}

def create_optimizer_and_scheduler(model: nn.Module, config: Dict[str, Any], num_training_steps: int):
    """Create optimizer and learning rate scheduler."""
    # Different learning rates for different components
    param_groups = []

    # Lower learning rate for embedding layers
    embedding_params = []
    other_params = []

    for name, param in model.named_parameters():
        if 'embedding' in name:
            embedding_params.append(param)
        else:
            other_params.append(param)

    param_groups = [
        {'params': embedding_params, 'lr': config['learning_rate'] * 0.5},  # Lower LR for embeddings
        {'params': other_params, 'lr': config['learning_rate']}
    ]

    optimizer = optim.AdamW(
        param_groups,
        weight_decay=config.get('weight_decay', 0.01),
        betas=(0.9, 0.95),  # Slightly different beta2 for better convergence
        eps=1e-8
    )

    # Enhanced warmup scheduler
    def lr_lambda(step):
        if step < config['warmup_steps']:
            return step / config['warmup_steps']
        else:
            # Cosine decay with minimum learning rate
            progress = (step - config['warmup_steps']) / (num_training_steps - config['warmup_steps'])
            min_lr_ratio = 0.1
            return min_lr_ratio + (1 - min_lr_ratio) * 0.5 * (1 + math.cos(math.pi * progress))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    return optimizer, scheduler

def train_epoch_v2(model: nn.Module,
                   dataset: List[Dict[str, torch.Tensor]],
                   optimizer: torch.optim.Optimizer,
                   scheduler: torch.optim.lr_scheduler._LRScheduler,
                   scaler: GradScaler,
                   config: Dict[str, Any],
                   epoch: int,
                   device: torch.device) -> Dict[str, float]:
    """Enhanced training loop for Phase 2."""
    model.train()
    total_loss = 0.0
    total_load_balance_loss = 0.0
    num_batches = 0
    batch_size = config['batch_size']
    gradient_accumulation = config['gradient_accumulation_steps']
    max_grad_norm = config['max_grad_norm']

    # Create progress bar
    num_steps = len(dataset) // batch_size
    progress = create_progress_bar(f"Epoch {epoch}", num_steps)

    optimizer.zero_grad()

    for step in range(0, len(dataset), batch_size):
        batch_data = dataset[step:step + batch_size]

        # Prepare batch
        input_ids = torch.stack([item['input_ids'] for item in batch_data]).to(device)
        attention_mask = torch.stack([item['attention_mask'] for item in batch_data]).to(device)
        labels = torch.stack([item['labels'] for item in batch_data]).to(device)

        # Forward pass with mixed precision
        with autocast():
            outputs = model(input_ids, attention_mask)
            logits = outputs['logits']
            load_balance_loss = outputs['load_balance_loss']

            # Calculate language modeling loss
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()

            criterion = nn.CrossEntropyLoss()
            lm_loss = criterion(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))

            # Total loss with load balancing
            total_batch_loss = lm_loss + load_balance_loss

            # Scale loss for gradient accumulation
            loss = total_batch_loss / gradient_accumulation

        # Backward pass
        scaler.scale(loss).backward()

        # Update weights every gradient_accumulation steps
        if (step // batch_size + 1) % gradient_accumulation == 0:
            # Gradient clipping
            scaler.unscale_(optimizer)
            grad_norm = clip_grad_norm_(model.parameters(), max_grad_norm)

            # Optimizer step
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            optimizer.zero_grad()

        total_loss += lm_loss.item()
        total_load_balance_loss += load_balance_loss.item()
        num_batches += 1

        # Update progress
        progress.update(1)

        # Memory monitoring (every 30 steps for Phase 2)
        if num_batches % 30 == 0:
            memory_info = get_memory_info()
            if memory_info:
                console.print(f"  Memory: {memory_info['allocated_mb']:.0f}MB / {memory_info['total_mb']:.0f}MB "
                            f"({memory_info['utilization_percent']:.1f}%)")

            # Check for memory pressure
            if memory_info and memory_info['utilization_percent'] > 85:
                console.print("⚠️ High memory usage detected - consider reducing batch size")

    progress.close()

    avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
    avg_load_balance_loss = total_load_balance_loss / num_batches if num_batches > 0 else 0.0

    return {
        'loss': avg_loss,
        'load_balance_loss': avg_load_balance_loss,
        'total_loss': avg_loss + avg_load_balance_loss,
        'learning_rate': scheduler.get_last_lr()[0] if scheduler else config['learning_rate']
    }

def main():
    """Main Phase 2 training function - Conservative Scaling."""

    # Device setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    console.print(f"🚀 Using device: {device}")

    if torch.cuda.is_available():
        console.print(f"GPU: {torch.cuda.get_device_name()}")
        memory_info = get_memory_info()
        console.print(f"Total VRAM: {memory_info['total_gb']:.1f}GB")

    # CONSERVATIVE B3 Phase 2 Configuration
    # 1.5x scaling from proven Phase 1 (101.5M → ~150M parameters)
    config = {
        # Model architecture (CONSERVATIVE SCALING from Phase 1)
        "vocab_size": 50257,        # Keep same
        "hidden_dim": 896,          # +128 from 768 (Phase 1)
        "num_heads": 14,            # +2 from 12 (Phase 1)
        "num_layers": 10,           # +2 from 8 (Phase 1)
        "expert_dim": 1152,         # +128 from 1024 (Phase 1)
        "num_experts": 4,           # Keep same (proven stable)
        "active_experts": 2,        # Keep same (proven stable)
        "dropout": 0.1,             # Keep same
        "max_seq_length": 512,      # Keep same

        # Training parameters (ADJUSTED for larger model)
        "batch_size": 3,            # Reduced from 4 for memory
        "learning_rate": 4e-5,      # Slightly reduced for stability
        "weight_decay": 0.01,       # Keep same
        "epochs": 60,               # More epochs for convergence
        "warmup_steps": 1500,       # More warmup for larger model
        "max_samples": 3000,        # More training data
        "gradient_accumulation_steps": 5,  # Effective batch size 15
        "max_grad_norm": 1.0,       # Keep same

        # Optimization settings (MEMORY FOCUSED)
        "mixed_precision": True,    # Essential for Phase 2
        "gradient_checkpointing": True,  # Essential for memory
        "save_every_epochs": 15,    # Less frequent saves
        "memory_target_mb": 2500,   # Target <2.5GB VRAM
    }

    console.print("🧠 ImpressionCore B3 Phase 2 Production Training")
    console.print("📊 CONSERVATIVE SCALING from Phase 1 Success")
    console.print(f"🎯 Target Parameters: ~150M (1.5x from 101.5M)")
    console.print(f"💾 Memory Target: <2.5GB VRAM (62% of GTX 1050 Ti)")
    console.print("")

    # Load Phase 1 checkpoint for reference
    phase1_checkpoint_path = "outputs/b3_phase1_training/b3_phase1_final.pt"
    phase1_checkpoint = load_phase1_checkpoint(phase1_checkpoint_path)

    # Create model
    console.print("🏗️ Creating B3 Phase 2 model...")
    model = B3ModelV2(config).to(device)

    # Count parameters
    total_params = model.count_parameters()
    console.print(f"📈 Model Parameters: {total_params:,} ({total_params/1e6:.1f}M)")

    # Validate scaling
    if phase1_checkpoint:
        phase1_params = phase1_checkpoint.get('total_parameters', 101500000)
        scaling_ratio = total_params / phase1_params
        console.print(f"📊 Scaling Ratio: {scaling_ratio:.2f}x from Phase 1")

        if scaling_ratio > 2.0:
            console.print("⚠️ WARNING: Scaling ratio >2x may be too aggressive!")
            return

    # Enable gradient checkpointing for memory efficiency
    if config['gradient_checkpointing']:
        model.gradient_checkpointing_enable()
        console.print("✅ Gradient checkpointing enabled")

    # Memory check before training
    model_memory = get_memory_info()
    if model_memory and model_memory['allocated_mb'] > config['memory_target_mb']:
        console.print(f"❌ Model memory {model_memory['allocated_mb']:.0f}MB exceeds target {config['memory_target_mb']}MB")
        console.print("Consider reducing model size or enabling more aggressive optimizations")
        return

    # Create enhanced dataset
    console.print("📚 Creating enhanced training dataset...")
    dataset = create_enhanced_dataset(config, config['max_samples'])
    console.print(f"📝 Dataset size: {len(dataset)} samples")

    # Create optimizer and scheduler
    num_training_steps = (len(dataset) // config['batch_size']) * config['epochs']
    optimizer, scheduler = create_optimizer_and_scheduler(model, config, num_training_steps)

    # Mixed precision scaler
    scaler = GradScaler() if config['mixed_precision'] else None

    # Training setup
    start_time = time.time()
    best_loss = float('inf')
    training_history = []

    # Create output directory
    output_dir = Path("outputs/b3_phase2_production")
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n🚀 Starting Phase 2 Conservative Scaling - {config['epochs']} epochs")
    console.print("=" * 70)

    # Pre-training memory baseline
    torch.cuda.empty_cache()
    baseline_memory = get_memory_info()
    console.print(f"📊 Baseline memory: {baseline_memory.get('allocated_mb', 0):.0f}MB")

    # Training loop
    for epoch in range(1, config['epochs'] + 1):
        epoch_start = time.time()

        console.print(f"\n📖 Epoch {epoch}/{config['epochs']}")

        # Train epoch
        train_metrics = train_epoch_v2(
            model=model,
            dataset=dataset,
            optimizer=optimizer,
            scheduler=scheduler,
            scaler=scaler,
            config=config,
            epoch=epoch,
            device=device
        )

        epoch_time = time.time() - epoch_start

        # Log metrics
        current_loss = train_metrics['loss']
        load_balance_loss = train_metrics['load_balance_loss']
        total_loss = train_metrics['total_loss']
        current_lr = train_metrics['learning_rate']

        console.print(f"💯 LM Loss: {current_loss:.6f} | LB Loss: {load_balance_loss:.6f} | Total: {total_loss:.6f}")
        console.print(f"📚 LR: {current_lr:.2e} | Time: {epoch_time:.1f}s")

        # Memory info
        memory_info = get_memory_info()
        if memory_info:
            console.print(f"🧠 Memory: {memory_info['allocated_mb']:.0f}MB / {memory_info['total_mb']:.0f}MB "
                        f"({memory_info['utilization_percent']:.1f}%)")

            # Memory warning
            if memory_info['utilization_percent'] > 90:
                console.print("🚨 CRITICAL: Memory usage >90% - Risk of OOM!")
            elif memory_info['utilization_percent'] > 80:
                console.print("⚠️ WARNING: Memory usage >80%")

        # Track best loss
        if current_loss < best_loss:
            best_loss = current_loss
            console.print(f"🎉 New best loss: {best_loss:.6f}")

        # Save training history
        training_history.append({
            'epoch': epoch,
            'lm_loss': current_loss,
            'load_balance_loss': load_balance_loss,
            'total_loss': total_loss,
            'learning_rate': current_lr,
            'epoch_time': epoch_time,
            'memory_usage_mb': memory_info.get('allocated_mb', 0) if memory_info else 0
        })

        # Save checkpoint
        if epoch % config['save_every_epochs'] == 0:
            checkpoint_path = output_dir / f"checkpoint_epoch_{epoch}.pt"
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'lm_loss': current_loss,
                'total_loss': total_loss,
                'config': config,
                'training_history': training_history
            }, checkpoint_path)
            console.print(f"💾 Checkpoint saved: {checkpoint_path}")

        # Early stopping check
        if epoch > 20 and current_loss > 5.0:  # Phase 1 achieved 0.001187
            console.print(f"⚠️ Loss {current_loss:.6f} not converging well - consider adjusting")

    # Training completion
    total_time = time.time() - start_time

    console.print("\n" + "=" * 70)
    console.print("🎉 PHASE 2 CONSERVATIVE SCALING COMPLETE!")
    console.print(f"⏱️ Total time: {total_time/3600:.1f} hours")
    console.print(f"🏆 Best loss: {best_loss:.6f}")
    console.print(f"📊 Final loss: {current_loss:.6f}")
    console.print(f"🧠 Final memory: {memory_info.get('allocated_mb', 0):.0f}MB")

    # Phase 1 comparison
    if phase1_checkpoint:
        phase1_loss = phase1_checkpoint.get('final_loss', 0.001187)
        console.print(f"📈 Phase 1 loss: {phase1_loss:.6f}")
        improvement = (phase1_loss - current_loss) / phase1_loss * 100
        console.print(f"📊 Loss change: {improvement:+.1f}%")

    # Save final model
    final_model_path = output_dir / "b3_phase2_final.pt"
    torch.save({
        'model_state_dict': model.state_dict(),
        'config': config,
        'final_lm_loss': current_loss,
        'final_total_loss': total_loss,
        'best_loss': best_loss,
        'total_parameters': total_params,
        'training_time_hours': total_time / 3600,
        'training_history': training_history,
        'phase1_comparison': {
            'phase1_loss': phase1_checkpoint.get('final_loss') if phase1_checkpoint else None,
            'phase1_params': phase1_checkpoint.get('total_parameters') if phase1_checkpoint else None,
            'scaling_ratio': total_params / phase1_checkpoint.get('total_parameters', 1) if phase1_checkpoint else None
        }
    }, final_model_path)

    # Save training metrics
    metrics_path = output_dir / "training_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump({
            'config': config,
            'final_metrics': {
                'final_lm_loss': current_loss,
                'final_total_loss': total_loss,
                'best_loss': best_loss,
                'total_parameters': total_params,
                'training_time_hours': total_time / 3600
            },
            'training_history': training_history
        }, f, indent=2)

    console.print(f"💾 Final model saved: {final_model_path}")
    console.print(f"📊 Metrics saved: {metrics_path}")

    # Success validation
    success_threshold = 0.1  # More lenient than Phase 1 initially
    if current_loss < success_threshold:
        console.print(f"\n🎯 SUCCESS: Loss {current_loss:.6f} below threshold {success_threshold}")
        console.print("✅ Phase 2 conservative scaling validated!")
    else:
        console.print(f"\n⚠️ Loss {current_loss:.6f} above threshold {success_threshold}")
        console.print("Consider further optimization or parameter adjustment")

    return {
        'final_lm_loss': current_loss,
        'final_total_loss': total_loss,
        'best_loss': best_loss,
        'total_parameters': total_params,
        'training_time_hours': total_time / 3600,
        'model_path': str(final_model_path),
        'metrics_path': str(metrics_path)
    }

if __name__ == "__main__":
    try:
        # Set up environment
        os.environ['CUDA_LAUNCH_BLOCKING'] = '1'  # For better error reporting

        # Run training
        results = main()

        console.print("\n🎊 Phase 2 Conservative Scaling completed!")
        console.print("🔥 ImpressionCore B3 Phase 2 - Ready for evaluation!")

    except KeyboardInterrupt:
        console.print("\n⚠️ Training interrupted by user")
    except Exception as e:
        console.print(f"\n❌ Training failed: {str(e)}")
        logger.exception("Training failed")
        raise
