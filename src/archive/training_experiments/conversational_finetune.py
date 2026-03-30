#!/usr/bin/env python3
"""
B3 Conversational Fine-tuning Script

Fine-tunes ImpressionCoreB3Model on conversational data using LoRA
for VRAM efficiency on GTX 1050 Ti.

Created: January 22, 2026
Author: ImpressionCore Team
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import json
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass
from transformers import AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("B3.ConversationalFinetune")


@dataclass
class ConvFinetuneConfig:
    """Configuration for conversational fine-tuning."""
    base_checkpoint: str = "F:/models/checkpoints/diverse_curriculum_mhc_ultra/step_1000.pt"
    output_dir: str = "F:/models/checkpoints/b3_conversational"

    # Data
    data_dirs: tuple = (
        "F:/data/conversations",
        "F:/data/qa_datasets",
        "data/conversations", # Add local synthetic data
    )
    max_samples: int = 50000
    max_seq_length: int = 256

    # Training
    batch_size: int = 2
    gradient_accumulation: int = 8
    learning_rate: float = 2e-5
    num_epochs: int = 3
    warmup_steps: int = 500

    # LoRA
    use_lora: bool = True
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05

    # Hardware
    device: str = "cuda"
    mixed_precision: bool = True
    gradient_checkpointing: bool = True


class ConversationalDataset(Dataset):
    """Dataset for conversational fine-tuning."""

    def __init__(
        self,
        data_dirs: List[str],
        tokenizer,
        max_samples: int = 50000,
        max_length: int = 256
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.conversations = []

        # Load data from multiple sources
        for data_dir in data_dirs:
            data_path = Path(data_dir)
            if not data_path.exists():
                logger.warning(f"Data directory not found: {data_dir}")
                continue

            # Load JSON files recursively
            for json_file in data_path.rglob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            self.conversations.extend(data[:max_samples - len(self.conversations)])
                        elif isinstance(data, dict) and 'conversations' in data:
                            self.conversations.extend(data['conversations'][:max_samples - len(self.conversations)])
                except Exception as e:
                    logger.warning(f"Error loading {json_file}: {e}")

                if len(self.conversations) >= max_samples:
                    break

            # Load text files (line-based dialogues)
            for txt_file in data_path.glob("*.txt"):
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # Pair consecutive lines as Q&A
                        for i in range(0, len(lines) - 1, 2):
                            if len(self.conversations) >= max_samples:
                                break
                            q = lines[i].strip()
                            a = lines[i + 1].strip() if i + 1 < len(lines) else ""
                            if q and a:
                                self.conversations.append({
                                    "input": q,
                                    "output": a
                                })
                except Exception as e:
                    logger.warning(f"Error loading {txt_file}: {e}")

        logger.info(f"Loaded {len(self.conversations)} conversations")

    def __len__(self):
        return len(self.conversations)

    def __getitem__(self, idx):
        conv = self.conversations[idx]

        # Handle different formats
        if isinstance(conv, dict):
            input_text = conv.get('input', conv.get('question', conv.get('prompt', '')))
            output_text = conv.get('output', conv.get('answer', conv.get('response', '')))
        elif isinstance(conv, list) and len(conv) >= 2:
            input_text = conv[0]
            output_text = conv[1]
        else:
            input_text = str(conv)
            output_text = ""

        # Format as prompt-response
        full_text = f"User: {input_text}\nAssistant: {output_text}"

        # Tokenize
        encoding = self.tokenizer(
            full_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze(0)
        attention_mask = encoding['attention_mask'].squeeze(0)

        # Labels: mask the input portion
        labels = input_ids.clone()
        # Find where "Assistant:" starts
        assistant_token = self.tokenizer.encode("Assistant:", add_special_tokens=False)
        for i in range(len(input_ids) - len(assistant_token)):
            if input_ids[i:i+len(assistant_token)].tolist() == assistant_token:
                labels[:i+len(assistant_token)] = -100
                break

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }


class LoRALayer(nn.Module):
    """LoRA adapter for efficient fine-tuning."""

    def __init__(self, original_layer: nn.Linear, r: int = 16, alpha: int = 32, dropout: float = 0.05):
        super().__init__()
        self.original = original_layer
        self.r = r
        self.alpha = alpha
        self.scaling = alpha / r

        # Expose weight/bias for compatibility with MultiheadAttention
        self.weight = original_layer.weight
        self.bias = original_layer.bias

        # Freeze original
        for param in self.original.parameters():
            param.requires_grad = False

        # LoRA matrices
        self.lora_A = nn.Parameter(torch.randn(r, original_layer.in_features) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(original_layer.out_features, r))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        original_out = self.original(x)
        lora_out = self.dropout(x) @ self.lora_A.T @ self.lora_B.T
        return original_out + lora_out * self.scaling


def apply_lora_to_model(model: nn.Module, config: ConvFinetuneConfig) -> nn.Module:
    """Apply LoRA adapters to model's linear layers (excluding MHA internals)."""
    lora_count = 0

    # Collect parent modules that are MultiheadAttention
    mha_modules = set()
    for name, module in model.named_modules():
        if isinstance(module, nn.MultiheadAttention):
            mha_modules.add(name)

    for name, module in list(model.named_modules()):
        # Skip if this is inside a MultiheadAttention module
        is_mha_child = any(name.startswith(mha + '.') for mha in mha_modules)
        if is_mha_child:
            continue

        # Target specific linear layers
        if isinstance(module, nn.Linear) and any(k in name for k in ['lm_head', 'quality_head', 'fusion', 'state_projection']):
            parent_name = '.'.join(name.split('.')[:-1])
            child_name = name.split('.')[-1]

            parent = model
            for part in parent_name.split('.'):
                if part:
                    parent = getattr(parent, part)

            lora_layer = LoRALayer(
                module,
                r=config.lora_r,
                alpha=config.lora_alpha,
                dropout=config.lora_dropout
            )
            setattr(parent, child_name, lora_layer)
            lora_count += 1

    logger.info(f"Applied LoRA to {lora_count} layers")
    return model


class ConversationalTrainer:
    """Trainer for conversational fine-tuning."""

    def __init__(self, config: ConvFinetuneConfig):
        self.config = config
        self.device = torch.device(config.device if torch.cuda.is_available() else 'cpu')

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model (initially on CPU)
        self._load_model_cpu()

        # Freeze ALL parameters first
        for param in self.model.parameters():
            param.requires_grad = False

        # Apply LoRA if enabled
        if config.use_lora:
            self.model = apply_lora_to_model(self.model, config)

        # Move to device AFTER structural changes
        self.model = self.model.to(self.device)

        # Enable gradient checkpointing
        if config.gradient_checkpointing:
            if hasattr(self.model, 'gradient_checkpointing_enable'):
                self.model.gradient_checkpointing_enable()

        # Only train LoRA params
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        logger.info(f"Trainable params: {trainable_params:,} / {total_params:,} ({100*trainable_params/total_params:.2f}%)")

    def _load_model_cpu(self):
        """Load the base B3 model to CPU."""
        from src.core.models.impressioncore_b3_architecture import ImpressionCoreB3Model, B3Config

        config = B3Config()
        self.model = ImpressionCoreB3Model(config)

        checkpoint = torch.load(self.config.base_checkpoint, map_location='cpu')
        if isinstance(checkpoint, dict):
            state_dict = checkpoint.get('model_state_dict') or checkpoint.get('model') or checkpoint
            self.model.load_state_dict(state_dict, strict=False)

        logger.info(f"Loaded base model from {self.config.base_checkpoint}")

    def train(self):
        """Run conversational fine-tuning."""
        # Create dataset
        dataset = ConversationalDataset(
            data_dirs=list(self.config.data_dirs),
            tokenizer=self.tokenizer,
            max_samples=self.config.max_samples,
            max_length=self.config.max_seq_length
        )

        if len(dataset) == 0:
            logger.error("No training data found!")
            return

        dataloader = DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=0,
            pin_memory=True
        )

        # Optimizer - only for LoRA params
        trainable_params = [p for p in self.model.parameters() if p.requires_grad]
        optimizer = torch.optim.AdamW(trainable_params, lr=self.config.learning_rate)

        # Scheduler
        total_steps = len(dataloader) * self.config.num_epochs // self.config.gradient_accumulation
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_steps)

        # Mixed precision
        scaler = torch.amp.GradScaler('cuda') if self.config.mixed_precision else None

        # Training loop
        self.model.train()
        global_step = 0

        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for epoch in range(self.config.num_epochs):
            epoch_loss = 0.0

            for batch_idx, batch in enumerate(dataloader):
                input_ids = batch['input_ids'].to(self.device)
                labels = batch['labels'].to(self.device)

                with torch.amp.autocast('cuda', enabled=self.config.mixed_precision):
                    outputs = self.model(input_ids=input_ids, labels=labels)
                    loss = outputs['loss'] / self.config.gradient_accumulation

                if scaler:
                    scaler.scale(loss).backward()
                else:
                    loss.backward()

                epoch_loss += loss.item() * self.config.gradient_accumulation

                if (batch_idx + 1) % self.config.gradient_accumulation == 0:
                    if scaler:
                        scaler.step(optimizer)
                        scaler.update()
                    else:
                        optimizer.step()

                    optimizer.zero_grad()
                    scheduler.step()
                    global_step += 1

                    if global_step % 100 == 0:
                        avg_loss = epoch_loss / (batch_idx + 1)
                        logger.info(f"Epoch {epoch+1} Step {global_step}: Loss = {avg_loss:.4f}")

            # Save checkpoint
            self._save_checkpoint(epoch, output_dir)

        # Save final model
        final_path = output_dir / "b3_conversational_final.pt"
        self._save_checkpoint("final", output_dir)
        logger.info(f"Training complete! Saved to {output_dir}")

    def _save_checkpoint(self, epoch, output_dir: Path):
        """Save checkpoint with LoRA weights."""
        # Save only LoRA weights
        lora_state = {}
        for name, module in self.model.named_modules():
            if isinstance(module, LoRALayer):
                lora_state[f"{name}.lora_A"] = module.lora_A.data.cpu()
                lora_state[f"{name}.lora_B"] = module.lora_B.data.cpu()

        checkpoint = {
            'epoch': epoch,
            'lora_state_dict': lora_state,
            'config': vars(self.config)
        }

        save_path = output_dir / f"b3_conv_epoch_{epoch}.pt"
        torch.save(checkpoint, save_path)
        logger.info(f"Saved checkpoint: {save_path}")


def main():
    """Run conversational fine-tuning."""
    import argparse

    parser = argparse.ArgumentParser(description="B3 Conversational Fine-tuning")
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch-size', type=int, default=2)
    parser.add_argument('--lr', type=float, default=2e-5)
    parser.add_argument('--max-samples', type=int, default=50000)
    parser.add_argument('--test', action='store_true', help="Quick test with 100 samples")
    args = parser.parse_args()

    config = ConvFinetuneConfig(
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        max_samples=100 if args.test else args.max_samples
    )

    trainer = ConversationalTrainer(config)
    trainer.train()


if __name__ == "__main__":
    main()
