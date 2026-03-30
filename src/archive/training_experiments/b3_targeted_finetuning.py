#!/usr/bin/env python3
"""
B3-Hope Targeted Fine-Tuning System
====================================

Fine-tunes the production model on curated dataset addressing specific weaknesses:
- Uses very low learning rate (1e-6) to avoid catastrophic forgetting
- Trains for 2-3 epochs on 2,500 targeted examples
- Monitors loss and validates against baseline

Goal: Reduce fallback rate from 20% to <10% while maintaining quality

Created: October 4, 2025
Author: Kirk LaSalle; GitHub Copilot
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from b3_constitutional_trainer import ImpressionCoreB3Hope, B3HopeConfig
from transformers import AutoTokenizer
import json
from datetime import datetime
from typing import Dict, List
import os

class TargetedDataset(Dataset):
    """Dataset for targeted fine-tuning"""

    def __init__(self, data_path: str, tokenizer, max_length: int = 128):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.tokenizer = tokenizer
        self.max_length = max_length

        print(f"Loaded {len(self.data)} training examples")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        example = self.data[idx]

        # Create input: prompt + response
        full_text = f"{example['prompt']} {example['response']}"

        # Tokenize
        encoding = self.tokenizer(
            full_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()

        # Create labels (same as input_ids for causal LM)
        labels = input_ids.clone()

        # Mask padding tokens in labels
        labels[attention_mask == 0] = -100

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels,
            'category': example['category']
        }


class TargetedFineTuner:
    """Fine-tuning system for targeted improvements"""

    def __init__(
        self,
        checkpoint_path: str = "b3_massive_best.pth",
        data_path: str = "b3_targeted_training_data.json",
        learning_rate: float = 1e-6,
        epochs: int = 3,
        batch_size: int = 4
    ):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size

        print("\n" + "="*80)
        print("B3-HOPE TARGETED FINE-TUNING SYSTEM")
        print("="*80)
        print(f"\nConfiguration:")
        print(f"  Learning Rate: {learning_rate}")
        print(f"  Epochs: {epochs}")
        print(f"  Batch Size: {batch_size}")
        print(f"  Device: {self.device}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model
        print(f"\nLoading base model: {checkpoint_path}")
        self.config = B3HopeConfig()
        self.model = ImpressionCoreB3Hope(self.config)

        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)

        self.baseline_loss = checkpoint.get('train_loss', 'unknown')
        print(f"Baseline training loss: {self.baseline_loss}")
        print(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")

        # Load dataset
        print(f"\nLoading dataset: {data_path}")
        self.dataset = TargetedDataset(data_path, self.tokenizer)
        self.dataloader = DataLoader(
            self.dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0
        )

        # Setup optimizer (very low learning rate to avoid catastrophic forgetting)
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=0.01
        )

        # Loss function
        self.criterion = nn.CrossEntropyLoss(ignore_index=-100)

        print("="*80 + "\n")

        # Training history
        self.history = {
            'epoch_losses': [],
            'batch_losses': [],
            'best_loss': float('inf'),
            'best_epoch': 0
        }

    def train_epoch(self, epoch: int) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        num_batches = 0

        print(f"\n{'='*80}")
        print(f"EPOCH {epoch}/{self.epochs}")
        print(f"{'='*80}\n")

        for batch_idx, batch in enumerate(self.dataloader):
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)

            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(input_ids, attention_mask=attention_mask)

            # Calculate loss
            logits = outputs['logits']
            loss = self.criterion(
                logits.view(-1, logits.size(-1)),
                labels.view(-1)
            )

            # Backward pass
            loss.backward()

            # Gradient clipping to prevent instability
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

            self.optimizer.step()

            # Track loss
            batch_loss = loss.item()
            total_loss += batch_loss
            num_batches += 1

            self.history['batch_losses'].append(batch_loss)

            # Print progress every 50 batches
            if (batch_idx + 1) % 50 == 0:
                avg_loss = total_loss / num_batches
                print(f"Batch {batch_idx + 1}/{len(self.dataloader)}: "
                      f"loss = {batch_loss:.4f}, avg_loss = {avg_loss:.4f}")

        epoch_loss = total_loss / num_batches
        self.history['epoch_losses'].append(epoch_loss)

        print(f"\nEpoch {epoch} complete: average loss = {epoch_loss:.4f}")

        # Save if best
        if epoch_loss < self.history['best_loss']:
            self.history['best_loss'] = epoch_loss
            self.history['best_epoch'] = epoch
            self.save_checkpoint(f"b3_finetuned_best.pth", epoch, epoch_loss)
            print(f"✓ New best model saved (loss: {epoch_loss:.4f})")

        return epoch_loss

    def train(self):
        """Run complete fine-tuning"""
        print("\n" + "="*80)
        print("STARTING FINE-TUNING")
        print("="*80)

        start_time = datetime.now()

        for epoch in range(1, self.epochs + 1):
            epoch_loss = self.train_epoch(epoch)

            # Save checkpoint after each epoch
            self.save_checkpoint(f"b3_finetuned_epoch{epoch}.pth", epoch, epoch_loss)

        end_time = datetime.now()
        duration = end_time - start_time

        print("\n" + "="*80)
        print("FINE-TUNING COMPLETE")
        print("="*80)
        print(f"Total time: {duration}")
        print(f"Best epoch: {self.history['best_epoch']}")
        print(f"Best loss: {self.history['best_loss']:.4f}")
        print(f"Baseline loss: {self.baseline_loss}")
        print("="*80 + "\n")

        # Save training history
        self.save_history()

    def save_checkpoint(self, filename: str, epoch: int, loss: float):
        """Save model checkpoint"""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epoch': epoch,
            'train_loss': loss,
            'baseline_loss': self.baseline_loss,
            'config': self.config,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        torch.save(checkpoint, filename)

    def save_history(self):
        """Save training history"""
        history_file = f"b3_finetuning_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

        print(f"Training history saved to: {history_file}")


def main():
    """Main execution"""
    # Check if dataset exists
    if not os.path.exists("b3_targeted_training_data.json"):
        print("ERROR: Dataset not found!")
        print("Please run: python b3_generate_targeted_dataset.py")
        return

    # Check if base model exists
    if not os.path.exists("b3_massive_best.pth"):
        print("ERROR: Base model not found!")
        print("Please ensure b3_massive_best.pth is in the current directory")
        return

    # Create fine-tuner
    finetuner = TargetedFineTuner(
        checkpoint_path="b3_massive_best.pth",
        data_path="b3_targeted_training_data.json",
        learning_rate=1e-6,  # Very low to avoid catastrophic forgetting
        epochs=3,
        batch_size=4  # Small batch size for stability
    )

    # Run fine-tuning
    finetuner.train()

    print("\n✓ Fine-tuning complete!")
    print("✓ Best model saved as: b3_finetuned_best.pth")
    print("✓ Ready for Phase 2 evaluation")


if __name__ == "__main__":
    main()
