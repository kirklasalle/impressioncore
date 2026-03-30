#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #command_line #cuda #memory_management #python #source_code #src/training/setup_b2_fixed_training.py #tokenization #training #transformer
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #command_line #cuda #memory_management #python #source_code #src\\training\\setup_b2_fixed_training.py #tokenization #training #transformer
# Category:** Training System
# Status:** Active

"""
ImpressionCore B2 Fixed Scaled Training Pipeline
Fixed class mapping issues and CUDA compatibility for GTX 1050 Ti
"""

import os
import sys
import json
import time
import logging
import traceback
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from core.utils.amp_utils import autocast_context, create_grad_scaler
import transformers
from transformers import (
    AutoTokenizer, AutoModel,
    GPT2Tokenizer, GPT2LMHeadModel,
    get_linear_schedule_with_warmup
)
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
import threading
from pathlib import Path
import random
from datetime import datetime

# Rich UI imports
try:
    from rich.console import Console
    from rich.progress import Progress, TextColumn, SpinnerColumn, TimeElapsedColumn, BarColumn
    from rich.logging import RichHandler
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Initialize console
if RICH_AVAILABLE:
    console = Console()
else:
    console = None

def setup_b2_logging():
    """Setup logging for B2 training (plain text to avoid Unicode issues)"""
    log_dir = Path("logs/b2_training")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Use basic logging to avoid Unicode encoding issues
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] B2 - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / f"b2_fixed_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    )

    return logging.getLogger("B2FixedTraining")

logger = setup_b2_logging()

@dataclass
class B2FixedConfig:
    """B2 Fixed configuration with correct class mappings"""
    # B2 Model settings - conservative for stability
    model_dim: int = 256
    hidden_dim: int = 512
    num_heads: int = 4
    num_layers: int = 3  # Reduced for stability

    # B2 Training settings
    batch_size: int = 1
    max_length: int = 128
    learning_rate: float = 3e-5  # More conservative
    num_epochs: int = 3          # Reduced for quick validation
    gradient_accumulation_steps: int = 2

    # Fixed class definitions
    num_intent_classes: int = 10      # Fixed: reduced from 15
    num_sentiment_classes: int = 3    # Negative, Neutral, Positive
    num_complexity_classes: int = 3   # Low, Medium, High

    # Memory optimization
    gradient_checkpointing: bool = True
    mixed_precision: bool = True

    # Dataset settings
    num_samples: int = 500            # Reduced for validation
    conversation_quality_threshold: float = 0.7

    # Timeout settings
    batch_timeout: int = 30
    epoch_timeout: int = 600  # 10 minutes per epoch

    # B2 Paths
    b2_checkpoint_dir: str = "checkpoints/b2_fixed"
    target_conversation_quality: float = 8.0  # Realistic target

class B2FixedDataset(Dataset):
    """Fixed B2 dataset with correct class mappings"""

    def __init__(self, config: B2FixedConfig, tokenizer):
        self.config = config
        self.tokenizer = tokenizer
        self.data = self._generate_fixed_data()

        logger.info(f"B2 Dataset initialized with {len(self.data)} conversations")

    def _generate_fixed_data(self) -> List[Dict]:
        """Generate fixed conversation data with correct class indices"""

        # Fixed conversation templates
        templates = [
            {"user": "Hello! How are you today?", "assistant": "I'm doing well, thank you! How can I help you?", "intent": 0, "sentiment": 2, "complexity": 1},
            {"user": "Can you help me with a programming question?", "assistant": "Of course! I'd be happy to help with programming. What's your question?", "intent": 1, "sentiment": 2, "complexity": 2},
            {"user": "I'm feeling stressed about work.", "assistant": "I understand that work stress can be challenging. Would you like to talk about what's bothering you?", "intent": 2, "sentiment": 1, "complexity": 2},
            {"user": "What's the weather like?", "assistant": "I don't have access to current weather data, but I recommend checking a weather app.", "intent": 3, "sentiment": 1, "complexity": 1},
            {"user": "Can you explain machine learning?", "assistant": "Machine learning is a way to teach computers to learn patterns from data, similar to how humans learn from experience.", "intent": 4, "sentiment": 1, "complexity": 2},
            {"user": "Tell me a joke!", "assistant": "Why don't scientists trust atoms? Because they make up everything! Hope that made you smile.", "intent": 5, "sentiment": 2, "complexity": 1},
            {"user": "I need advice on my career.", "assistant": "Career decisions are important. What specific aspect of your career are you thinking about?", "intent": 6, "sentiment": 1, "complexity": 2},
            {"user": "How do I cook pasta?", "assistant": "To cook pasta: boil water, add salt, add pasta, cook for package time, then drain. Simple and effective!", "intent": 7, "sentiment": 2, "complexity": 1},
            {"user": "I'm having relationship problems.", "assistant": "Relationships can be challenging. Sometimes talking through issues can help. What's on your mind?", "intent": 8, "sentiment": 1, "complexity": 2},
            {"user": "Thank you for your help!", "assistant": "You're very welcome! I'm glad I could help. Feel free to ask if you need anything else.", "intent": 9, "sentiment": 2, "complexity": 1},
        ]

        sample_data = []

        for i in range(self.config.num_samples):
            template = templates[i % len(templates)]

            # Add natural variations
            variations = [
                template,
                {**template, "user": template["user"] + " Please help me with this."},
                {**template, "assistant": template["assistant"] + " Let me know if you need more information."},
            ]

            selected = random.choice(variations)

            # Create conversation text
            conversation_text = f"Human: {selected['user']}\nAssistant: {selected['assistant']}"

            # Calculate quality score
            quality_score = min(0.7 + random.uniform(0, 0.3), 1.0)

            sample = {
                'conversation_id': f"b2_fixed_{i:05d}",
                'text': conversation_text,
                'user_input': selected['user'],
                'assistant_response': selected['assistant'],
                'intent_label': selected['intent'],        # 0-9 (10 classes)
                'sentiment_label': selected['sentiment'],  # 0-2 (3 classes)
                'complexity_label': selected['complexity'], # 0-2 (3 classes)
                'quality_score': quality_score
            }
            sample_data.append(sample)

        # Validate class ranges
        intent_labels = [s['intent_label'] for s in sample_data]
        sentiment_labels = [s['sentiment_label'] for s in sample_data]
        complexity_labels = [s['complexity_label'] for s in sample_data]

        logger.info(f"Generated {len(sample_data)} B2 samples")
        logger.info(f"Intent range: {min(intent_labels)}-{max(intent_labels)} (expected 0-{self.config.num_intent_classes-1})")
        logger.info(f"Sentiment range: {min(sentiment_labels)}-{max(sentiment_labels)} (expected 0-{self.config.num_sentiment_classes-1})")
        logger.info(f"Complexity range: {min(complexity_labels)}-{max(complexity_labels)} (expected 0-{self.config.num_complexity_classes-1})")

        return sample_data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # Tokenize with B2 length
        input_encoding = self.tokenizer(
            item['text'],
            max_length=self.config.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        target_encoding = self.tokenizer(
            item['assistant_response'],
            max_length=self.config.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': input_encoding['input_ids'].squeeze(),
            'attention_mask': input_encoding['attention_mask'].squeeze(),
            'target_ids': target_encoding['input_ids'].squeeze(),
            'target_attention_mask': target_encoding['attention_mask'].squeeze(),
            'intent_labels': torch.tensor(item['intent_label'], dtype=torch.long),
            'sentiment_labels': torch.tensor(item['sentiment_label'], dtype=torch.long),
            'complexity_labels': torch.tensor(item['complexity_label'], dtype=torch.long),
            'quality_scores': torch.tensor(item['quality_score'], dtype=torch.float),
            'conversation_id': item['conversation_id']
        }

class B2FixedModel(nn.Module):
    """Fixed B2 model with correct class dimensions"""

    def __init__(self, config: B2FixedConfig, vocab_size: int):
        super().__init__()
        self.config = config

        # Embedding layers
        self.embeddings = nn.Embedding(vocab_size, config.model_dim)
        self.positional_encoding = nn.Parameter(torch.randn(1, 512, config.model_dim))

        # Transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.model_dim,
            nhead=config.num_heads,
            dim_feedforward=config.hidden_dim,
            dropout=0.1,
            activation='gelu',
            batch_first=True,
            norm_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=config.num_layers)

        # Fixed classification heads with correct dimensions
        self.language_head = nn.Linear(config.model_dim, vocab_size)
        self.intent_classifier = nn.Linear(config.model_dim, config.num_intent_classes)     # 10 classes
        self.sentiment_classifier = nn.Linear(config.model_dim, config.num_sentiment_classes) # 3 classes
        self.complexity_classifier = nn.Linear(config.model_dim, config.num_complexity_classes) # 3 classes
        self.quality_regressor = nn.Sequential(
            nn.Linear(config.model_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(config.hidden_dim // 2, 1),
            nn.Sigmoid()
        )

        # Layer normalization
        self.layer_norm = nn.LayerNorm(config.model_dim)

        # Initialize weights
        self.apply(self._init_weights)

        logger.info(f"B2 Model created with fixed dimensions:")
        logger.info(f"  Intent classes: {config.num_intent_classes}")
        logger.info(f"  Sentiment classes: {config.num_sentiment_classes}")
        logger.info(f"  Complexity classes: {config.num_complexity_classes}")

    def _init_weights(self, module):
        """Initialize model weights"""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.ones_(module.weight)
            torch.nn.init.zeros_(module.bias)

    def forward(self, input_ids, attention_mask=None):
        batch_size, seq_len = input_ids.shape

        # Get embeddings with positional encoding
        x = self.embeddings(input_ids)
        if seq_len <= 512:
            x = x + self.positional_encoding[:, :seq_len, :]

        # Apply layer normalization
        x = self.layer_norm(x)

        # Create attention mask for transformer
        if attention_mask is not None:
            attention_mask = attention_mask.bool()
            attention_mask = ~attention_mask  # Invert for transformer

        # Apply transformer
        transformer_output = self.transformer(x, src_key_padding_mask=attention_mask)

        # Pool for classification tasks (mean pooling)
        if attention_mask is not None:
            mask_expanded = (~attention_mask).unsqueeze(-1).expand(transformer_output.size()).float()
            pooled = (transformer_output * mask_expanded).sum(dim=1) / mask_expanded.sum(dim=1)
        else:
            pooled = transformer_output.mean(dim=1)

        # Generate outputs
        outputs = {
            'language_logits': self.language_head(transformer_output),
            'intent_logits': self.intent_classifier(pooled),
            'sentiment_logits': self.sentiment_classifier(pooled),
            'complexity_logits': self.complexity_classifier(pooled),
            'quality_scores': self.quality_regressor(pooled).squeeze(-1),
            'hidden_states': transformer_output,
            'pooled_output': pooled
        }

        return outputs

class B2FixedTrainer:
    """Fixed B2 trainer with proper error handling"""

    def __init__(self, config: B2FixedConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.amp_enabled = bool(
            self.config.mixed_precision and self.device.type == "cuda" and torch.cuda.is_available()
        )
        if self.config.mixed_precision and not self.amp_enabled:
            logger.warning(
                "Mixed precision requested but CUDA is unavailable; running with standard precision instead."
            )

        # Setup directories
        self._setup_directories()

        # Initialize components
        self._initialize_tokenizer()
        self._initialize_model()
        self._initialize_training_components()

        logger.info("B2 Fixed Training Initialization Complete")
        logger.info(f"Target conversation quality: {config.target_conversation_quality}/10")

    def _setup_directories(self):
        """Setup B2 directories"""
        dirs = [
            self.config.b2_checkpoint_dir,
            "logs/b2_training"
        ]

        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def _initialize_tokenizer(self):
        """Initialize tokenizer"""
        logger.info("Loading B2 tokenizer...")

        try:
            self.tokenizer = GPT2Tokenizer.from_pretrained(
                'gpt2',
                use_safetensors=True,
                trust_remote_code=False
            )

            # Add padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            logger.info("B2 tokenizer loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load B2 tokenizer: {e}")
            raise

    def _initialize_model(self):
        """Initialize B2 model"""
        logger.info("Building B2 fixed model...")

        try:
            vocab_size = len(self.tokenizer)
            self.model = B2FixedModel(self.config, vocab_size)
            self.model.to(self.device)

            # Print model statistics
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

            logger.info(f"B2 Model parameters: {total_params:,} total, {trainable_params:,} trainable")
            logger.info(f"B2 Model size: {total_params * 4 / 1e6:.1f} MB (FP32)")

        except Exception as e:
            logger.error(f"Failed to initialize B2 model: {e}")
            raise

    def _initialize_training_components(self):
        """Initialize training components"""
        # Dataset and dataloader
        self.dataset = B2FixedDataset(self.config, self.tokenizer)
        self.dataloader = DataLoader(
            self.dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=0,
            pin_memory=True
        )

        # Optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=0.01
        )

        # Scheduler
        total_steps = len(self.dataloader) * self.config.num_epochs
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=total_steps // 10,
            num_training_steps=total_steps
        )

        # Mixed precision scaler
        self.scaler = create_grad_scaler(
            enabled=self.amp_enabled,
            device_type=self.device.type,
        )
        if self.amp_enabled and self.scaler is None:
            logger.warning(
                "Mixed precision requested but GradScaler unavailable; falling back to standard precision."
            )
            self.amp_enabled = False

        # Loss functions
        self.language_criterion = nn.CrossEntropyLoss(ignore_index=self.tokenizer.pad_token_id)
        self.intent_criterion = nn.CrossEntropyLoss()
        self.sentiment_criterion = nn.CrossEntropyLoss()
        self.complexity_criterion = nn.CrossEntropyLoss()
        self.quality_criterion = nn.MSELoss()

        logger.info(f"B2 Training components initialized")
        logger.info(f"  Dataset: {len(self.dataset)} conversations")
        logger.info(f"  Batches per epoch: {len(self.dataloader)}")
        logger.info(f"  Total training steps: {total_steps}")

    def training_step(self, batch) -> Dict[str, float]:
        """Single B2 training step"""
        self.model.train()

        try:
            # Move batch to device
            for key in batch:
                if isinstance(batch[key], torch.Tensor):
                    batch[key] = batch[key].to(self.device)

            # Forward pass
            with autocast_context(enabled=self.amp_enabled, device_type=self.device.type):
                outputs = self.model(batch['input_ids'], batch['attention_mask'])
                loss_dict = self._compute_loss(outputs, batch)

            total_loss = loss_dict['total_loss']

            # Backward pass
            self.optimizer.zero_grad()

            if self.amp_enabled and self.scaler is not None:
                self.scaler.scale(total_loss).backward()
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                total_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()

            self.scheduler.step()

            # Calculate metrics
            with torch.no_grad():
                intent_acc = (torch.argmax(outputs['intent_logits'], dim=1) == batch['intent_labels']).float().mean()
                sentiment_acc = (torch.argmax(outputs['sentiment_logits'], dim=1) == batch['sentiment_labels']).float().mean()
                complexity_acc = (torch.argmax(outputs['complexity_logits'], dim=1) == batch['complexity_labels']).float().mean()
                quality_mae = torch.abs(outputs['quality_scores'] - batch['quality_scores']).mean()

            # Memory cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            return {
                'total_loss': total_loss.item(),
                'language_loss': loss_dict['language_loss'].item(),
                'intent_loss': loss_dict['intent_loss'].item(),
                'sentiment_loss': loss_dict['sentiment_loss'].item(),
                'complexity_loss': loss_dict['complexity_loss'].item(),
                'quality_loss': loss_dict['quality_loss'].item(),
                'intent_accuracy': intent_acc.item(),
                'sentiment_accuracy': sentiment_acc.item(),
                'complexity_accuracy': complexity_acc.item(),
                'quality_mae': quality_mae.item()
            }

        except torch.cuda.OutOfMemoryError as e:
            logger.warning(f"CUDA OOM in batch, skipping: {e}")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return {'total_loss': float('inf'), 'intent_accuracy': 0.0, 'sentiment_accuracy': 0.0}

        except Exception as e:
            logger.error(f"Training step error: {e}")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return {'total_loss': float('inf'), 'intent_accuracy': 0.0, 'sentiment_accuracy': 0.0}

    def _compute_loss(self, outputs: Dict, batch: Dict) -> Dict[str, torch.Tensor]:
        """Compute B2 multi-task loss"""

        # Language modeling loss
        language_loss = self.language_criterion(
            outputs['language_logits'].view(-1, outputs['language_logits'].size(-1)),
            batch['target_ids'].view(-1)
        )

        # Classification losses
        intent_loss = self.intent_criterion(outputs['intent_logits'], batch['intent_labels'])
        sentiment_loss = self.sentiment_criterion(outputs['sentiment_logits'], batch['sentiment_labels'])
        complexity_loss = self.complexity_criterion(outputs['complexity_logits'], batch['complexity_labels'])

        # Quality regression loss
        quality_loss = self.quality_criterion(outputs['quality_scores'], batch['quality_scores'])

        # Weighted combination
        total_loss = (
            0.4 * language_loss +
            0.2 * intent_loss +
            0.15 * sentiment_loss +
            0.1 * complexity_loss +
            0.15 * quality_loss
        )

        return {
            'total_loss': total_loss,
            'language_loss': language_loss,
            'intent_loss': intent_loss,
            'sentiment_loss': sentiment_loss,
            'complexity_loss': complexity_loss,
            'quality_loss': quality_loss
        }

    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train one B2 epoch"""
        epoch_metrics = {
            'total_loss': [], 'language_loss': [], 'intent_loss': [], 'sentiment_loss': [],
            'complexity_loss': [], 'quality_loss': [], 'intent_accuracy': [],
            'sentiment_accuracy': [], 'complexity_accuracy': [], 'quality_mae': []
        }

        successful_batches = 0
        start_time = time.time()

        for batch_idx, batch in enumerate(self.dataloader):
            # Check timeout
            if time.time() - start_time > self.config.epoch_timeout:
                logger.warning(f"Epoch {epoch} timed out, stopping early")
                break

            metrics = self.training_step(batch)

            if metrics['total_loss'] != float('inf'):
                for key in epoch_metrics:
                    if key in metrics:
                        epoch_metrics[key].append(metrics[key])
                successful_batches += 1

            # Log progress
            if batch_idx % 50 == 0 and successful_batches > 0:
                avg_loss = np.mean(epoch_metrics['total_loss'])
                avg_intent_acc = np.mean(epoch_metrics['intent_accuracy'])
                logger.info(f"B2 Batch {batch_idx}: Loss={avg_loss:.4f}, Intent_Acc={avg_intent_acc:.3f}")

        # Calculate epoch averages
        epoch_results = {}
        for key in epoch_metrics:
            if epoch_metrics[key]:
                epoch_results[key] = np.mean(epoch_metrics[key])
            else:
                epoch_results[key] = 0.0

        epoch_results['successful_batches'] = successful_batches
        epoch_results['total_batches'] = len(self.dataloader)

        return epoch_results

    def save_checkpoint(self, epoch: int, metrics: Dict[str, float]):
        """Save B2 checkpoint"""
        try:
            checkpoint_path = Path(self.config.b2_checkpoint_dir) / f"b2_fixed_epoch_{epoch}.pth"

            checkpoint = {
                'epoch': epoch,
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'scheduler_state_dict': self.scheduler.state_dict(),
                'metrics': metrics,
                'config': self.config.__dict__,
                'b2_version': 'fixed_classes'
            }

            torch.save(checkpoint, checkpoint_path)
            logger.info(f"B2 checkpoint saved: {checkpoint_path}")

        except Exception as e:
            logger.error(f"Failed to save B2 checkpoint: {e}")

    def start_training(self):
        """Start B2 fixed training"""
        logger.info("Starting B2 Fixed Training Pipeline")
        logger.info(f"Dataset: {len(self.dataset)} conversations")
        logger.info(f"Model: {sum(p.numel() for p in self.model.parameters()):,} parameters")
        logger.info(f"Epochs: {self.config.num_epochs}")
        logger.info(f"Target Quality: {self.config.target_conversation_quality}/10")

        try:
            best_quality_score = 0.0

            for epoch in range(self.config.num_epochs):
                logger.info(f"Starting B2 epoch {epoch + 1}/{self.config.num_epochs}")

                # Train epoch
                epoch_metrics = self.train_epoch(epoch)

                # Calculate conversation quality estimate
                conversation_quality = (
                    epoch_metrics['intent_accuracy'] * 3 +
                    epoch_metrics['sentiment_accuracy'] * 2 +
                    epoch_metrics['complexity_accuracy'] * 2 +
                    (1 - epoch_metrics['quality_mae']) * 3
                )  # Scale to ~10 point scale

                # Log results
                logger.info(f"B2 Epoch {epoch + 1} Results:")
                logger.info(f"  Total Loss: {epoch_metrics['total_loss']:.4f}")
                logger.info(f"  Intent Accuracy: {epoch_metrics['intent_accuracy']:.3f}")
                logger.info(f"  Sentiment Accuracy: {epoch_metrics['sentiment_accuracy']:.3f}")
                logger.info(f"  Complexity Accuracy: {epoch_metrics['complexity_accuracy']:.3f}")
                logger.info(f"  Quality MAE: {epoch_metrics['quality_mae']:.3f}")
                logger.info(f"  Conversation Quality Estimate: {conversation_quality:.1f}/10")
                logger.info(f"  Successful Batches: {epoch_metrics['successful_batches']}/{epoch_metrics['total_batches']}")

                # Save checkpoint
                self.save_checkpoint(epoch, epoch_metrics)

                # Track best quality
                if conversation_quality > best_quality_score:
                    best_quality_score = conversation_quality
                    logger.info(f"New best B2 conversation quality: {best_quality_score:.1f}/10")

                # Memory cleanup
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

            # Final summary
            logger.info("B2 fixed training completed successfully!")
            logger.info(f"Best conversation quality achieved: {best_quality_score:.1f}/10")
            if best_quality_score >= self.config.target_conversation_quality:
                logger.info("TARGET ACHIEVED! Ready for Phase 2 distillation")
            else:
                logger.info("Good progress made. Consider additional training or parameter tuning.")

        except KeyboardInterrupt:
            logger.info("B2 training interrupted by user")
        except Exception as e:
            logger.error(f"B2 training failed: {e}")
            traceback.print_exc()
            raise

def main():
    """Main B2 training function"""
    try:
        # Initialize config
        config = B2FixedConfig()

        # Create trainer
        trainer = B2FixedTrainer(config)

        # Start training
        trainer.start_training()

    except KeyboardInterrupt:
        logger.info("B2 training interrupted by user")
    except Exception as e:
        logger.error(f"B2 fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
