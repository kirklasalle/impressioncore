#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #command_line #cuda #deployment #memory_management #multimodal #python #source_code #src/training/setup_raw_data_training_corrupted_20250708_170555.py #testing #tokenization #training #transformer
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #command_line #cuda #deployment #memory_management #multimodal #python #source_code #src\\training\\setup_raw_data_training_corrupted_20250708_170555.py #testing #tokenization #training #transformer
# Category:** Training System
# Status:** Active

"""
ImpressionCore B2 Raw Data Training Setup
Comprehensive preparation for Phase 2: Raw Multimodal Data Training

This script prepares the complete pipeline for training with real multimodal data:
- Text-image-audio conversations
- End-to-end encoder training
- Production-ready deployment pipeline
"""

        # Text encoder (DialoGPT) with safetensors workaround
        text_model = AutoModel.from_pretrained(
            "microsoft/DialoGPT-small",
            use_safetensors=True,
            trust_remote_code=False
        ).to(self.device)

        # Vision encoder (CLIP) with safetensors workaround
        vision_model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32",
            use_safetensors=True,
            trust_remote_code=False
        ).to(self.device)

        # Audio encoder (Wav2Vec2) with safetensors workaround
        audio_model = Wav2Vec2Model.from_pretrained(
            "facebook/wav2vec2-base",
            use_safetensors=True,
            trust_remote_code=False
        ).to(self.device)deployment pipeline
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import time
import os
import json
import h5py  # For distillation data storage
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
from PIL import Image
import torchaudio
import torchvision.transforms as transforms
from transformers import (
    AutoTokenizer, AutoModel,
    CLIPProcessor, CLIPModel,
    Wav2Vec2Processor, Wav2Vec2Model
)
from sklearn.metrics import accuracy_score, f1_score, classification_report
import pandas as pd

# Import B2 multimodal architecture
from src.models.b2_multimodal.core.b2_multimodal_model import B2MultimodalModel
from src.core.utils.rich_enhancements import FallbackProgress, RichEnhancer
from src.core.utils.rich_logging import RichLogger
from src.core.utils.rich_status_animation import RichStatusAnimation

@dataclass
class RawDataConfig:
    """Configuration for raw data training"""
    # Model architecture
    vocab_size: int = 50257
    embed_dim: int = 768
    num_heads: int = 12
    num_layers: int = 12
    max_seq_len: int = 128000
    num_sentiment_classes: int = 3
    num_intent_classes: int = 10

    # Training parameters
    batch_size: int = 1  # Reduced for multimodal complexity
    max_epochs: int = 50
    base_lr: float = 0.00005  # Lower for end-to-end training
    classification_lr: float = 0.0002
    weight_decay: float = 0.01
    early_stopping_patience: int = 8
    gradient_accumulation_steps: int = 4  # Effective batch size = 4

    # Loss weights for raw data training
    text_loss_weight: float = 0.4
    sentiment_loss_weight: float = 1.0
    intent_loss_weight: float = 2.0
    quality_loss_weight: float = 0.3

    # Data paths
    raw_data_dir: str = "data/raw_multimodal"
    checkpoint_dir: str = "checkpoints/raw_training"
    log_dir: str = "logs/raw_training"

    # Distillation preparation paths
    phase1_outputs_dir: str = "src/training/phase1_outputs"
    phase2_prep_dir: str = "src/training/phase2_prep"
    distillation_dir: str = "src/training/distillation"

    # Distillation capture settings
    capture_representations: bool = True
    capture_attention_maps: bool = True
    capture_prediction_patterns: bool = True
    save_teacher_outputs: bool = True
    distillation_temperature: float = 3.0

    # Hardware optimization
    mixed_precision: bool = True
    gradient_checkpointing: bool = True
    max_grad_norm: float = 1.0

class MultimodalRawDataset(Dataset):
    """Dataset for raw multimodal conversations"""

    def __init__(self, data_dir: str, config: RawDataConfig, split: str = "train"):
        self.data_dir = Path(data_dir)
        self.config = config
        self.split = split

        # Initialize processors
        self.text_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        # Fix padding token issue for DialoGPT
        if self.text_tokenizer.pad_token is None:
            self.text_tokenizer.pad_token = self.text_tokenizer.eos_token

        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.wav2vec_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")

        # Load data manifest
        self.data_manifest = self._load_data_manifest()

        # Image transforms
        self.image_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        print(f"Loaded {len(self.data_manifest)} {split} samples")

    def _load_data_manifest(self) -> List[Dict]:
        """Load data manifest with multimodal conversation samples"""
        manifest_path = self.data_dir / f"{self.split}_manifest.json"

        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                return json.load(f)
        else:
            # Generate sample manifest for demonstration
            return self._generate_sample_manifest()

    def _generate_sample_manifest(self) -> List[Dict]:
        """Generate sample manifest for testing (replace with real data loading)"""
        # This is a template - replace with actual data loading logic
        sample_data = []

        for i in range(1000):  # Sample size
            sample = {
                'conversation_id': f"conv_{i:04d}",
                'text': f"Sample conversation {i} about various topics",
                'image_path': f"images/sample_{i:04d}.jpg",  # Path to conversation image
                'audio_path': f"audio/sample_{i:04d}.wav",   # Path to conversation audio
                'sentiment_label': np.random.randint(0, 3),  # 0: negative, 1: neutral, 2: positive
                'intent_label': np.random.randint(0, 10),    # 10 intent classes
                'quality_score': np.random.uniform(0.1, 1.0), # Quality rating
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'source': 'generated',
                    'speaker_id': f"speaker_{i % 10}"
                }
            }
            sample_data.append(sample)

        # Save for future use
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.data_dir / f"{self.split}_manifest.json", 'w') as f:
            json.dump(sample_data, f, indent=2)

        return sample_data

    def __len__(self) -> int:
        return len(self.data_manifest)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        sample = self.data_manifest[idx]

        # Process text
        text_encoding = self.text_tokenizer(
            sample['text'],
            max_length=512,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        # Process image (with fallback for missing files)
        image_path = self.data_dir / sample['image_path']
        if image_path.exists():
            try:
                image = Image.open(image_path).convert('RGB')
                image_tensor = self.image_transform(image)
            except Exception:
                # Fallback: random image tensor
                image_tensor = torch.randn(3, 224, 224)
        else:
            # Generate placeholder image for testing
            image_tensor = torch.randn(3, 224, 224)

        # Process audio (with fallback for missing files)
        audio_path = self.data_dir / sample['audio_path']
        if audio_path.exists():
            try:
                waveform, sample_rate = torchaudio.load(audio_path)
                # Resample to 16kHz if needed
                if sample_rate != 16000:
                    resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                    waveform = resampler(waveform)
                # Take first channel and pad/truncate to fixed length
                audio_tensor = waveform[0][:16000 * 10]  # 10 seconds max
                if audio_tensor.shape[0] < 16000 * 10:
                    audio_tensor = torch.nn.functional.pad(
                        audio_tensor, (0, 16000 * 10 - audio_tensor.shape[0])
                    )
            except Exception:
                # Fallback: random audio tensor
                audio_tensor = torch.randn(16000 * 10)
        else:
            # Generate placeholder audio for testing
            audio_tensor = torch.randn(16000 * 10)  # 10 seconds of random audio

        return {
            'input_ids': text_encoding['input_ids'].squeeze(),
            'attention_mask': text_encoding['attention_mask'].squeeze(),
            'image': image_tensor,
            'audio': audio_tensor,
            'sentiment_labels': torch.tensor(sample['sentiment_label'], dtype=torch.long),
            'intent_labels': torch.tensor(sample['intent_label'], dtype=torch.long),
            'quality_scores': torch.tensor(sample['quality_score'], dtype=torch.float),
            'conversation_id': sample['conversation_id']
        }

class RawDataTrainer:
    """Trainer for raw multimodal data"""

    def __init__(self, config: RawDataConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Initialize rich UI components
        self.logger = RichLogger("RawDataTraining")
        self.progress_manager = None  # Will be initialized when needed
        self.status_animation = RichStatusAnimation()

        # Initialize distillation capture system
        self.distillation_capture = DistillationCapture(config)

        # Setup directories
        os.makedirs(config.checkpoint_dir, exist_ok=True)
        os.makedirs(config.log_dir, exist_ok=True)

        # Training state
        self.global_step = 0
        self.best_metrics = {'sentiment_acc': 0.0, 'intent_acc': 0.0}

        self.logger.info("🚀 Raw Data Training Initialization Complete")
        self.logger.info(f"📊 Distillation capture: {'✅ ENABLED' if config.capture_representations else '❌ DISABLED'}")
        self.logger.info(f"🎯 Teacher outputs will be saved to: {config.phase1_outputs_dir}")

    def setup_model(self):
        """Setup model for raw data training"""

        self.logger.info("⚠️ Using simplified model setup for raw data training")

        # For now, we'll use the external encoders directly and create a simple wrapper
        # This bypasses the B2MultimodalModel initialization issues

        class SimpleMultimodalWrapper(nn.Module):
            def __init__(self, config):
                super().__init__()
                self.config = config

                # Simple classification heads
                self.sentiment_classifier = nn.Linear(768, config['num_sentiment_classes'])
                self.intent_classifier = nn.Linear(768, config['num_intent_classes'])
                self.quality_regressor = nn.Linear(768, 1)
                self.text_projection = nn.Linear(768, config['vocab_size'])

            def forward(self, input_ids=None, embeddings=None):
                # Use the provided embeddings
                if embeddings is not None:
                    # Pool embeddings (simple mean pooling)
                    pooled = embeddings.mean(dim=1)  # [batch, 768]
                else:
                    # Fallback to random embeddings for testing
                    pooled = torch.randn(input_ids.size(0), 768).to(input_ids.device)

                return {
                    'sentiment_logits': self.sentiment_classifier(pooled),
                    'intent_logits': self.intent_classifier(pooled),
                    'quality_scores': self.quality_regressor(pooled),
                    'text_logits': self.text_projection(pooled).unsqueeze(1).repeat(1, input_ids.size(1), 1)
                }

            def gradient_checkpointing_enable(self):
                # Placeholder for gradient checkpointing
                pass

        # Create config for simple model
        model_config = {
            'vocab_size': self.config.vocab_size,
            'embed_dim': self.config.embed_dim,
            'num_sentiment_classes': self.config.num_sentiment_classes,
            'num_intent_classes': self.config.num_intent_classes
        }

        model = SimpleMultimodalWrapper(model_config).to(self.device)
        self.logger.info("✅ Simple multimodal wrapper created successfully")

        return model

    def setup_multimodal_encoders(self):
        """Setup multimodal encoders with safetensors workaround"""

        # Text encoder (DialoGPT) with safetensors workaround
        text_model = AutoModel.from_pretrained(
            "microsoft/DialoGPT-small",
            use_safetensors=True,
            trust_remote_code=False
        ).to(self.device)

        # Vision encoder (CLIP) with safetensors workaround
        vision_model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32",
            use_safetensors=True,
            trust_remote_code=False
        ).to(self.device)

        # Audio encoder (Wav2Vec2) with safetensors workaround
        audio_model = Wav2Vec2Model.from_pretrained(
            "facebook/wav2vec2-base",
            use_safetensors=True,
            trust_remote_code=False
        ).to(self.device)

        return {
            'text': text_model,
            'vision': vision_model,
            'audio': audio_model
        }

    def setup_data_loaders(self) -> Tuple[DataLoader, DataLoader]:
        """Setup training and validation data loaders"""

        # Training dataset
        train_dataset = MultimodalRawDataset(
            self.config.raw_data_dir,
            self.config,
            split="train"
        )

        # Validation dataset (20% of training data for now)
        val_size = len(train_dataset) // 5
        train_size = len(train_dataset) - val_size

        train_dataset, val_dataset = torch.utils.data.random_split(
            train_dataset, [train_size, val_size]
        )

        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True
        )

        self.logger.info(f"📊 Data loaders ready - Train: {len(train_dataset)}, Val: {len(val_dataset)}")
        return train_loader, val_loader

    def process_multimodal_batch(self, batch: Dict, encoders: Dict) -> Dict:
        """Process a multimodal batch through encoders"""

        # Process text through DialoGPT
        text_outputs = encoders['text'](
            input_ids=batch['input_ids'],
            attention_mask=batch['attention_mask']
        )
        text_embeddings = text_outputs.last_hidden_state  # [batch, seq_len, 768]

        # Process images through CLIP vision encoder
        vision_outputs = encoders['vision'].vision_model(pixel_values=batch['image'])
        vision_embeddings = vision_outputs.last_hidden_state  # [batch, 197, 768]

        # Process audio through Wav2Vec2
        audio_outputs = encoders['audio'](batch['audio'])
        audio_embeddings = audio_outputs.last_hidden_state  # [batch, time_steps, 768]

        # Combine embeddings (concatenate along sequence dimension)
        combined_embeddings = torch.cat([
            text_embeddings,
            vision_embeddings,
            audio_embeddings
        ], dim=1)  # [batch, total_seq_len, 768]

        return {
            'embeddings': combined_embeddings,
            'text_embeddings': text_embeddings,
            'vision_embeddings': vision_embeddings,
            'audio_embeddings': audio_embeddings
        }

    def train_raw_data_epoch(self, model, encoders, train_loader, optimizer, epoch=0, scaler=None):
        """Train one epoch with raw multimodal data"""
        model.train()
        for encoder in encoders.values():
            encoder.train()

        epoch_losses = []
        sentiment_preds_all = []
        sentiment_labels_all = []
        intent_preds_all = []
        intent_labels_all = []

        for batch_idx, batch in enumerate(train_loader):
            # Move batch to device
            for key in batch:
                if isinstance(batch[key], torch.Tensor):
                    batch[key] = batch[key].to(self.device)

            # Gradient accumulation
            optimizer.zero_grad()

            with torch.amp.autocast('cuda', enabled=self.config.mixed_precision):
                # Process through multimodal encoders
                multimodal_outputs = self.process_multimodal_batch(batch, encoders)

                # Forward through main model
                model_outputs = model(
                    input_ids=batch['input_ids'],
                    embeddings=multimodal_outputs['embeddings']
                )

                # 🎯 DISTILLATION CAPTURE: Capture teacher outputs for Phase 2
                if self.config.capture_representations:
                    # Enhance model_outputs with multimodal representations for distillation
                    enhanced_outputs = {**model_outputs}
                    enhanced_outputs.update({
                        'text_hidden_states': multimodal_outputs.get('text_features'),
                        'image_patch_embeddings': multimodal_outputs.get('image_features'),
                        'audio_frame_features': multimodal_outputs.get('audio_features'),
                        'unified_repr': multimodal_outputs.get('embeddings')
                    })

                    self.distillation_capture.capture_forward_pass(
                        enhanced_outputs, batch, self.global_step, epoch
                    )

                # Compute loss
                loss = self._compute_raw_data_loss(model_outputs, batch)
                loss = loss / self.config.gradient_accumulation_steps  # Scale for accumulation

            # Backward pass with mixed precision
            if scaler:
                scaler.scale(loss).backward()
            else:
                loss.backward()

            # Gradient accumulation step
            if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                if scaler:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(
                        list(model.parameters()) +
                        [p for encoder in encoders.values() for p in encoder.parameters()],
                        self.config.max_grad_norm
                    )
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    torch.nn.utils.clip_grad_norm_(
                        list(model.parameters()) +
                        [p for encoder in encoders.values() for p in encoder.parameters()],
                        self.config.max_grad_norm
                    )
                    optimizer.step()

                self.global_step += 1

            # Collect metrics
            epoch_losses.append(loss.item() * self.config.gradient_accumulation_steps)

            sentiment_preds = torch.argmax(model_outputs['sentiment_logits'], dim=1)
            intent_preds = torch.argmax(model_outputs['intent_logits'], dim=1)

            sentiment_preds_all.extend(sentiment_preds.cpu().numpy())
            sentiment_labels_all.extend(batch['sentiment_labels'].cpu().numpy())
            intent_preds_all.extend(intent_preds.cpu().numpy())
            intent_labels_all.extend(batch['intent_labels'].cpu().numpy())

            # Log progress
            if batch_idx % 100 == 0:
                current_sentiment_acc = accuracy_score(
                    sentiment_labels_all[-len(sentiment_preds):],
                    sentiment_preds_all[-len(sentiment_preds):]
                )
                current_intent_acc = accuracy_score(
                    intent_labels_all[-len(intent_preds):],
                    intent_preds_all[-len(intent_preds):]
                )

                self.logger.info(
                    f"Step {self.global_step}: Loss={loss.item():.4f}, "
                    f"Sentiment_Acc={current_sentiment_acc:.3f}, "
                    f"Intent_Acc={current_intent_acc:.3f}"
                )

        # Epoch metrics
        avg_loss = np.mean(epoch_losses)
        sentiment_acc = accuracy_score(sentiment_labels_all, sentiment_preds_all)
        intent_acc = accuracy_score(intent_labels_all, intent_preds_all)

        # 🎯 DISTILLATION CAPTURE: Save epoch data for Phase 2
        if self.config.save_teacher_outputs:
            training_metrics = {
                'loss': avg_loss,
                'sentiment_acc': sentiment_acc,
                'intent_acc': intent_acc,
                'global_step': self.global_step
            }
            self.distillation_capture.save_epoch_data(epoch, training_metrics)
            self.logger.info(f"📊 Teacher outputs saved for epoch {epoch}")

        return {
            'loss': avg_loss,
            'sentiment_acc': sentiment_acc,
            'intent_acc': intent_acc
        }

    def _compute_raw_data_loss(self, outputs: Dict, targets: Dict) -> torch.Tensor:
        """Compute loss for raw data training"""

        text_loss = nn.CrossEntropyLoss()(
            outputs['text_logits'].view(-1, outputs['text_logits'].size(-1)),
            targets['input_ids'].view(-1)
        )

        sentiment_loss = nn.CrossEntropyLoss()(
            outputs['sentiment_logits'],
            targets['sentiment_labels']
        )

        intent_loss = nn.CrossEntropyLoss()(
            outputs['intent_logits'],
            targets['intent_labels']
        )

        # Fix tensor shape mismatch for quality loss
        quality_pred = outputs['quality_scores'].squeeze()
        quality_target = targets['quality_scores']

        # Ensure both tensors have same shape
        if quality_pred.dim() == 0:
            quality_pred = quality_pred.unsqueeze(0)
        if quality_target.dim() == 0:
            quality_target = quality_target.unsqueeze(0)

        quality_loss = nn.MSELoss()(quality_pred, quality_target)

        total_loss = (
            self.config.text_loss_weight * text_loss +
            self.config.sentiment_loss_weight * sentiment_loss +
            self.config.intent_loss_weight * intent_loss +
            self.config.quality_loss_weight * quality_loss
        )

        return total_loss

    def start_raw_training(self):
        """Main training loop for raw data"""

        with self.status_animation.status("🔧 Setting up raw data training..."):
            # Setup model and encoders
            model = self.setup_model()
            encoders = self.setup_multimodal_encoders()

            # Setup data loaders
            train_loader, val_loader = self.setup_data_loaders()

            # Setup optimizer for all parameters
            all_params = list(model.parameters())
            for encoder in encoders.values():
                all_params.extend(encoder.parameters())

            optimizer = optim.AdamW(
                all_params,
                lr=self.config.base_lr,
                weight_decay=self.config.weight_decay
            )

            # Mixed precision scaler
            scaler = torch.cuda.amp.GradScaler() if self.config.mixed_precision else None

        self.logger.success("✅ Raw data training setup complete!")
        self.logger.info(f"🎯 Training with {sum(p.numel() for p in all_params):,} parameters")

        # Training loop
        best_combined_acc = 0.0
        patience_counter = 0

        # Initialize progress manager for training
        self.progress_manager = FallbackProgress(
            total=self.config.max_epochs,
            description="Raw Data Training"
        )

        with self.progress_manager:
            for epoch in range(self.config.max_epochs):
                epoch_start = time.time()

                # Training
                train_metrics = self.train_raw_data_epoch(
                    model, encoders, train_loader, optimizer, epoch, scaler
                )

                # Validation
                val_metrics = self.evaluate_raw_data(model, encoders, val_loader)

                epoch_time = time.time() - epoch_start

                # Log epoch results
                self.logger.info(
                    f"\n[Epoch {epoch+1}/{self.config.max_epochs}] Results:\n"
                    f"  Train - Loss: {train_metrics['loss']:.4f}, "
                    f"Sentiment: {train_metrics['sentiment_acc']:.3f}, "
                    f"Intent: {train_metrics['intent_acc']:.3f}\n"
                    f"  Val - Loss: {val_metrics['loss']:.4f}, "
                    f"Sentiment: {val_metrics['sentiment_acc']:.3f}, "
                    f"Intent: {val_metrics['intent_acc']:.3f}\n"
                    f"  Time: {epoch_time:.1f}s"
                )

                # Check for improvement
                combined_acc = val_metrics['sentiment_acc'] + val_metrics['intent_acc']
                if combined_acc > best_combined_acc:
                    best_combined_acc = combined_acc
                    patience_counter = 0

                    # Save best model
                    self.save_checkpoint(model, encoders, optimizer, epoch, val_metrics, "best")
                    self.logger.success(f"🎉 New best model! Combined accuracy: {combined_acc:.3f}")
                else:
                    patience_counter += 1

                # Early stopping
                if patience_counter >= self.config.early_stopping_patience:
                    self.logger.warning(f"⏹️ Early stopping triggered after {patience_counter} epochs")
                    break

                # Regular checkpoint
                if (epoch + 1) % 5 == 0:
                    self.save_checkpoint(model, encoders, optimizer, epoch, val_metrics, f"epoch_{epoch+1}")

                self.progress_manager.update(advance=1)

        self.logger.success("🎉 Raw data training completed!")
        return val_metrics

    def evaluate_raw_data(self, model, encoders, val_loader):
        """Evaluate model on validation data"""
        model.eval()
        for encoder in encoders.values():
            encoder.eval()

        all_losses = []
        all_sentiment_preds = []
        all_sentiment_labels = []
        all_intent_preds = []
        all_intent_labels = []

        with torch.no_grad():
            for batch in val_loader:
                for key in batch:
                    if isinstance(batch[key], torch.Tensor):
                        batch[key] = batch[key].to(self.device)

                # Process batch
                multimodal_outputs = self.process_multimodal_batch(batch, encoders)
                model_outputs = model(
                    input_ids=batch['input_ids'],
                    embeddings=multimodal_outputs['embeddings']
                )

                loss = self._compute_raw_data_loss(model_outputs, batch)
                all_losses.append(loss.item())

                # Collect predictions
                sentiment_preds = torch.argmax(model_outputs['sentiment_logits'], dim=1)
                intent_preds = torch.argmax(model_outputs['intent_logits'], dim=1)

                all_sentiment_preds.extend(sentiment_preds.cpu().numpy())
                all_sentiment_labels.extend(batch['sentiment_labels'].cpu().numpy())
                all_intent_preds.extend(intent_preds.cpu().numpy())
                all_intent_labels.extend(batch['intent_labels'].cpu().numpy())

        return {
            'loss': np.mean(all_losses),
            'sentiment_acc': accuracy_score(all_sentiment_labels, all_sentiment_preds),
            'intent_acc': accuracy_score(all_intent_labels, all_intent_preds),
            'sentiment_f1': f1_score(all_sentiment_labels, all_sentiment_preds, average='weighted'),
            'intent_f1': f1_score(all_intent_labels, all_intent_preds, average='weighted')
        }

    def save_checkpoint(self, model, encoders, optimizer, epoch, metrics, name):
        """Save training checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'encoder_state_dicts': {name: encoder.state_dict() for name, encoder in encoders.items()},
            'optimizer_state_dict': optimizer.state_dict(),
            'metrics': metrics,
            'config': self.config,
            'global_step': self.global_step
        }

        checkpoint_path = os.path.join(self.config.checkpoint_dir, f"raw_training_{name}.pth")
        torch.save(checkpoint, checkpoint_path)
        self.logger.info(f"💾 Checkpoint saved: {checkpoint_path}")

class DistillationCapture:
    """
    Comprehensive system for capturing teacher model outputs for Phase 2 distillation
    Implements the data capture strategy from DISTILLATION_PREPARATION_COMPREHENSIVE_GUIDE.md
    """

    def __init__(self, config: RawDataConfig):
        self.config = config
        self.setup_directories()
        self.current_epoch = 0

        # Capture containers
        self.representations_buffer = []
        self.predictions_buffer = []
        self.attention_buffer = []
        self.metadata_buffer = []

    def setup_directories(self):
        """Create directory structure for distillation outputs"""
        dirs = [
            self.config.phase1_outputs_dir,
            f"{self.config.phase1_outputs_dir}/representations",
            f"{self.config.phase1_outputs_dir}/predictions",
            f"{self.config.phase1_outputs_dir}/attention_maps",
            f"{self.config.phase1_outputs_dir}/metadata",
            self.config.phase2_prep_dir,
            f"{self.config.phase2_prep_dir}/teacher_data",
            f"{self.config.phase2_prep_dir}/student_targets",
            f"{self.config.phase2_prep_dir}/validation",
            self.config.distillation_dir,
            f"{self.config.distillation_dir}/loss_functions",
            f"{self.config.distillation_dir}/schedulers",
            f"{self.config.distillation_dir}/metrics"
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def capture_forward_pass(self, model_outputs: Dict, batch: Dict,
                           step: int, epoch: int) -> None:
        """Capture all teacher outputs during forward pass"""

        if not self.config.capture_representations:
            return

        timestamp = datetime.now().isoformat()

        # 1. Capture intermediate representations
        if self.config.capture_representations:
            representations = {
                'text_features': {
                    'hidden_states': model_outputs.get('text_hidden_states'),
                    'attention_weights': model_outputs.get('text_attention_weights'),
                    'pooled_output': model_outputs.get('text_pooled')
                },
                'image_features': {
                    'patch_embeddings': model_outputs.get('image_patch_embeddings'),
                    'cls_token': model_outputs.get('image_cls_token'),
                    'attention_maps': model_outputs.get('image_attention_maps')
                },
                'audio_features': {
                    'frame_features': model_outputs.get('audio_frame_features'),
                    'temporal_attention': model_outputs.get('audio_attention')
                },
                'fusion_features': {
                    'cross_modal_attention': model_outputs.get('cross_modal_attention'),
                    'unified_representation': model_outputs.get('unified_repr')
                }
            }

            self.representations_buffer.append({
                'step': step,
                'epoch': epoch,
                'timestamp': timestamp,
                'representations': representations
            })

        # 2. Capture prediction patterns with temperature scaling
        if self.config.capture_prediction_patterns:
            # Apply temperature scaling for soft targets
            temp = self.config.distillation_temperature

            predictions = {
                'text_logits_soft': torch.softmax(model_outputs['text_logits'] / temp, dim=-1),
                'sentiment_logits_soft': torch.softmax(model_outputs['sentiment_logits'] / temp, dim=-1),
                'intent_logits_soft': torch.softmax(model_outputs['intent_logits'] / temp, dim=-1),
                'quality_scores': model_outputs['quality_scores'],
                'confidence_scores': {
                    'text_confidence': torch.max(torch.softmax(model_outputs['text_logits'], dim=-1), dim=-1)[0],
                    'sentiment_confidence': torch.max(torch.softmax(model_outputs['sentiment_logits'], dim=-1), dim=-1)[0],
                    'intent_confidence': torch.max(torch.softmax(model_outputs['intent_logits'], dim=-1), dim=-1)[0]
                }
            }

            self.predictions_buffer.append({
                'step': step,
                'epoch': epoch,
                'timestamp': timestamp,
                'predictions': predictions,
                'batch_metadata': {
                    'batch_size': batch['input_ids'].shape[0],
                    'sequence_length': batch['input_ids'].shape[1]
                }
            })

        # 3. Capture attention maps
        if self.config.capture_attention_maps and 'attention_weights' in model_outputs:
            self.attention_buffer.append({
                'step': step,
                'epoch': epoch,
                'timestamp': timestamp,
                'attention_maps': model_outputs['attention_weights']
            })

    def save_epoch_data(self, epoch: int, training_metrics: Dict) -> None:
        """Save captured data for the epoch"""

        if not self.config.save_teacher_outputs:
            return

        epoch_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save representations as HDF5 for efficiency
        if self.representations_buffer:
            repr_file = f"{self.config.phase1_outputs_dir}/representations/epoch_{epoch}_{epoch_timestamp}.h5"
            with h5py.File(repr_file, 'w') as f:
                for i, data in enumerate(self.representations_buffer):
                    group = f.create_group(f"step_{data['step']}")
                    group.attrs['timestamp'] = data['timestamp']
                    group.attrs['epoch'] = data['epoch']

                    # Save each representation tensor
                    for modality, features in data['representations'].items():
                        mod_group = group.create_group(modality)
                        for feat_name, tensor in features.items():
                            if tensor is not None:
                                mod_group.create_dataset(feat_name, data=tensor.cpu().numpy())

        # Save predictions as JSON for metadata + HDF5 for tensors
        if self.predictions_buffer:
            pred_file = f"{self.config.phase1_outputs_dir}/predictions/epoch_{epoch}_{epoch_timestamp}.h5"
            meta_file = f"{self.config.phase1_outputs_dir}/metadata/epoch_{epoch}_{epoch_timestamp}.json"

            metadata = []
            with h5py.File(pred_file, 'w') as f:
                for i, data in enumerate(self.predictions_buffer):
                    group = f.create_group(f"step_{data['step']}")

                    # Save prediction tensors
                    for pred_name, tensor in data['predictions'].items():
                        if isinstance(tensor, torch.Tensor):
                            group.create_dataset(pred_name, data=tensor.cpu().numpy())
                        elif isinstance(tensor, dict):
                            # Handle nested tensors (confidence scores)
                            conf_group = group.create_group(pred_name)
                            for conf_name, conf_tensor in tensor.items():
                                conf_group.create_dataset(conf_name, data=conf_tensor.cpu().numpy())

                    # Collect metadata
                    metadata.append({
                        'step': data['step'],
                        'epoch': data['epoch'],
                        'timestamp': data['timestamp'],
                        'batch_metadata': data['batch_metadata']
                    })

            # Save metadata
            with open(meta_file, 'w') as f:
                json.dump({
                    'epoch': epoch,
                    'timestamp': epoch_timestamp,
                    'training_metrics': training_metrics,
                    'steps_data': metadata,
                    'distillation_config': {
                        'temperature': self.config.distillation_temperature,
                        'capture_settings': {
                            'representations': self.config.capture_representations,
                            'attention_maps': self.config.capture_attention_maps,
                            'prediction_patterns': self.config.capture_prediction_patterns
                        }
                    }
                }, f, indent=2)

        # Clear buffers for next epoch
        self.representations_buffer = []
        self.predictions_buffer = []
        self.attention_buffer = []

    def prepare_distillation_dataset(self, output_path: str) -> None:
        """Prepare consolidated dataset for Phase 2 distillation"""

        teacher_data_dir = f"{self.config.phase2_prep_dir}/teacher_data"
        os.makedirs(teacher_data_dir, exist_ok=True)

        # Consolidate all epoch data into distillation-ready format
        # This will be implemented based on specific Phase 2 requirements
        print(f"🎯 Preparing distillation dataset at {teacher_data_dir}")
        print(f"📊 Teacher outputs will be consolidated for student training")

def main():
    """Main execution for raw data training setup"""

    # Configuration
    config = RawDataConfig(
        batch_size=1,  # Start small for multimodal complexity
        max_epochs=50,
        base_lr=0.00005,
        classification_lr=0.0002,
        gradient_accumulation_steps=4,  # Effective batch size = 4
        mixed_precision=True,
        gradient_checkpointing=True
    )

    print("🚀 ImpressionCore B2 Raw Data Training Setup")
    print("=" * 50)

    # Initialize trainer
    trainer = RawDataTrainer(config)

    # Option to start training immediately or just setup
    print("\nSetup complete! Ready to begin raw data training.")
    print("📊 This will train on real multimodal conversations")
    print("🎯 Target: 70-85% sentiment, 60-75% intent accuracy")
    print("⏱️ Estimated time: 6-12 hours for full training")

    return trainer

if __name__ == "__main__":
    trainer = main()
    # Start training immediately:
    trainer.start_raw_training()
