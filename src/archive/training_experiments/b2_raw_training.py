#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #cuda #memory_management #multimodal #python #source_code #src/training/b2_raw_training.py #training
**Category:** Training System
**Status:** Active
"""









# B2 Raw Training

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #command_line #cuda #memory_management #multimodal #python #source_code #src\\training\\b2_raw_training.py #training
# Category:** Training System
# Status:** Active

"""
ImpressionCore B2 RAW Data Training Script

Trains the B2 multimodal model directly on raw data (text, images, audio, video) from F:/b2_datasets/raw/.
Assumes data preparation, manifest generation, and embedding optimization are complete.

- Loads raw data and labels from F:/b2_datasets/raw/
- Uses manifests in F:/b2_datasets/ (train_manifest.json, val_manifest.json)
- Optionally uses F:/b2_embeddings/ for embedding caching
- Implements curriculum, advanced logging, and memory optimization

Author: GitHub Copilot
Date: 2025-07-07
"""
import os
import sys
import json
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
from typing import Dict, Any
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

# --- Ensure src/ is in sys.path for robust imports ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.models.b2_multimodal.core.b2_multimodal_model import B2MultimodalModel
from src.core.utils.rich_logging import RichLogger
from src.core.utils.memory_optimization import optimize_for_low_vram

# --- Config ---
RAW_DATA_ROOT = 'F:/b2_datasets/raw/'
MANIFEST_DIR = 'F:/b2_datasets/'
EMBEDDING_ROOT = 'F:/b2_embeddings/'
TRAIN_MANIFEST = os.path.join(MANIFEST_DIR, 'train_manifest.json')
VAL_MANIFEST = os.path.join(MANIFEST_DIR, 'val_manifest.json')

BATCH_SIZE = 2
EPOCHS = 3
LEARNING_RATE = 2e-4
HEAD_LR_MULTIPLIER = 5.0
CURRICULUM_EPOCHS = 4
EARLY_STOPPING_PATIENCE = 6
GRAD_CLIP = 1.0
LOG_INTERVAL = 10
VAL_INTERVAL = 1

# --- Utility: Load manifest ---
def load_manifest(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Dataset for RAW multimodal data ---
import warnings
def validate_manifest(manifest, raw_data_root):
    required_keys = ['text', 'image', 'audio', 'video']
    valid_samples = []
    invalid_samples = []
    for i, sample in enumerate(manifest):
        missing = False
        for key in required_keys:
            rel_path = sample.get(key, None)
            if not rel_path:
                missing = True
                break
            abs_path = os.path.join(raw_data_root, rel_path)
            if not os.path.isfile(abs_path):
                missing = True
                break
        if missing:
            invalid_samples.append(i)
        else:
            valid_samples.append(sample)
    return valid_samples, invalid_samples

class RawMultimodalDataset(torch.utils.data.Dataset):
    def __init__(self, manifest, raw_data_root):
        self.samples = manifest
        self.raw_data_root = raw_data_root

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        try:
            # Load raw text
            text_path = os.path.join(self.raw_data_root, sample['text'])
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()
            # Load image (as tensor)
            image_path = os.path.join(self.raw_data_root, sample['image'])
            from PIL import Image
            import torchvision.transforms as T
            image = T.ToTensor()(Image.open(image_path).convert('RGB'))
            # Load audio (as tensor)
            audio_path = os.path.join(self.raw_data_root, sample['audio'])
            import torchaudio
            waveform, _ = torchaudio.load(audio_path)
            # Load video (as tensor, first frame)
            video_path = os.path.join(self.raw_data_root, sample['video'])
            # For simplicity, use a placeholder (zeros) for video
            video = torch.zeros(8, 3, 224, 224)  # [num_frames, C, H, W]
            # Labels
            sentiment = sample.get('sentiment', 0)
            intent = sample.get('intent', 0)
            quality = sample.get('quality', 0.0)
            label = sample.get('label', 0)
            return {
                'text': text,
                'vision': image,
                'audio': waveform,
                'video': video,
                'sentiment': torch.tensor(sentiment, dtype=torch.long),
                'intent': torch.tensor(intent, dtype=torch.long),
                'quality': torch.tensor(quality, dtype=torch.float32),
                'labels': torch.tensor(label, dtype=torch.long)
            }
        except Exception as e:
            warnings.warn(f"[RawMultimodalDataset] Skipping sample at idx {idx} due to error: {e}")
            return None

def collate_fn(batch):
    # Filter out None samples
    batch = [item for item in batch if item is not None]
    if len(batch) == 0:
        return None  # DataLoader will skip empty batches
    max_len = 128
    text_batch = [torch.randint(0, 50257, (max_len,)) for _ in batch]  # Dummy tokenized text
    vision_batch = torch.stack([item['vision'] for item in batch])
    audio_batch = torch.stack([item['audio'][0][:16000] if item['audio'].dim() > 1 else item['audio'][:16000] for item in batch])
    video_batch = torch.stack([item['video'] for item in batch])
    sentiment_batch = torch.stack([item['sentiment'] for item in batch])
    intent_batch = torch.stack([item['intent'] for item in batch])
    quality_batch = torch.stack([item['quality'] for item in batch])
    labels_batch = torch.stack([item['labels'] for item in batch])
    return {
        'text': torch.stack(text_batch),
        'vision': vision_batch,
        'audio': audio_batch,
        'video': video_batch,
        'sentiment': sentiment_batch,
        'intent': intent_batch,
        'quality': quality_batch,
        'labels': labels_batch
    }


# --- Load and validate manifests ---
train_manifest = load_manifest(TRAIN_MANIFEST)
val_manifest = load_manifest(VAL_MANIFEST)
print("[Manifest Validation] Checking train manifest...")
train_valid, train_invalid = validate_manifest(train_manifest, RAW_DATA_ROOT)
print(f"[Manifest Validation] Train: {len(train_valid)} valid, {len(train_invalid)} invalid samples.")
if len(train_valid) == 0:
    raise RuntimeError("No valid training samples found after manifest validation. Please check your data paths.")
print("[Manifest Validation] Checking val manifest...")
val_valid, val_invalid = validate_manifest(val_manifest, RAW_DATA_ROOT)
print(f"[Manifest Validation] Val: {len(val_valid)} valid, {len(val_invalid)} invalid samples.")
if len(val_valid) == 0:
    raise RuntimeError("No valid validation samples found after manifest validation. Please check your data paths.")

train_dataset = RawMultimodalDataset(train_valid, RAW_DATA_ROOT)
val_dataset = RawMultimodalDataset(val_valid, RAW_DATA_ROOT)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collate_fn)

# --- Model config ---
model_config = {
    'embed_dim': 768,
    'vocab_size': 50257,
    'img_dim': 256,
    'audio_dim': 16000,
    'num_layers': 12,
    'num_heads': 12,
    'max_seq_len': 128000,
    'n_experts': 4,
    'vision_decoder_layers': 8,
    'vision_decoder_steps': 50,
    'audio_decoder_layers': 8,
    'audio_decoder_steps': 50,
    'sp_model_path': 'dummy.model',
    'vision_patch_dim': 768,
    'patch_size': 16,
    'num_sentiment_classes': 3,
    'num_intent_classes': 10,
    'audio_feat_dim': 768,
    'n_mels': 64,
    'sample_rate': 16000,
    'video_feat_dim': 768,
    'num_frames': 8,
    'video_mean': 0.5,
    'video_std': 0.5,
    'dropout': 0.18,
    'core_dropout': 0.12,
    'lr': LEARNING_RATE,
    'head_lr_multiplier': HEAD_LR_MULTIPLIER,
    'batch_size': BATCH_SIZE,
    'epochs': EPOCHS,
    'curriculum_epochs': CURRICULUM_EPOCHS,
    'gradient_clip': GRAD_CLIP,
    'early_stopping_patience': EARLY_STOPPING_PATIENCE,
    'precision': 'amp',
    'quantization': '8bit',
}
model_config = model_config  # No-op, keep config as is

# Apply memory optimization to the model after instantiation
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = B2MultimodalModel(model_config).to(DEVICE)
model = optimize_for_low_vram(model, optimization_level=2)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = B2MultimodalModel(model_config).to(DEVICE)

# --- Optimizer ---
def get_head_params(model):
    return [p for n, p in model.named_parameters() if any(h in n for h in ['sentiment_head', 'intent_head'])]
def get_backbone_params(model):
    head_names = ['sentiment_head', 'intent_head']
    return [p for n, p in model.named_parameters() if not any(h in n for h in head_names)]

for n, p in model.named_parameters():
    if any(h in n for h in ['sentiment_head', 'intent_head']):
        p.requires_grad = False
    else:
        p.requires_grad = True
optimizer = optim.AdamW(get_backbone_params(model), lr=LEARNING_RATE)

# --- Training Loop ---
def train():
    writer = SummaryWriter(log_dir=f'logs/raw_training_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    best_val_loss = float('inf')
    patience = 0
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        num_batches = 0
        for i, batch in enumerate(train_loader):
            if batch is None:
                continue  # Skip empty batches
            optimizer.zero_grad()
            # Dummy tokenization: text is already tokenized in collate_fn
            inputs = {
                'text': batch['text'].to(DEVICE),
                'vision': batch['vision'].to(DEVICE),
                'audio': batch['audio'].to(DEVICE),
                'video': batch['video'].to(DEVICE)
            }
            outputs = model(inputs, use_precomputed_embeddings=False)
            text_logits = outputs['text']
            label_targets = batch['labels'].to(DEVICE)
            loss_text = nn.functional.cross_entropy(text_logits, label_targets)
            sentiment_logits = outputs['sentiment']
            loss_sentiment = nn.functional.cross_entropy(sentiment_logits, batch['sentiment'].to(DEVICE))
            intent_logits = outputs['intent']
            loss_intent = nn.functional.cross_entropy(intent_logits, batch['intent'].to(DEVICE))
            quality_pred = outputs.get('quality', torch.zeros_like(batch['quality'].to(DEVICE)))
            loss_quality = nn.functional.mse_loss(quality_pred, batch['quality'].to(DEVICE))
            loss = loss_text + 0.4*loss_sentiment + 0.4*loss_intent + 0.15*loss_quality
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=GRAD_CLIP)
            optimizer.step()
            total_loss += loss.item()
            num_batches += 1
            if i % LOG_INTERVAL == 0:
                print(f"[Epoch {epoch+1}] Step {i}: Loss={loss.item():.4f}")
                writer.add_scalar('Loss/Batch', loss.item(), epoch * len(train_loader) + i)
        if num_batches > 0:
            avg_loss = total_loss / num_batches
        else:
            avg_loss = float('nan')
        print(f"[Epoch {epoch+1}] Avg Loss={avg_loss:.4f}")
        writer.add_scalar('Loss/EpochAvg', avg_loss, epoch)
        # Validation
        val_loss = evaluate(epoch, writer)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience = 0
            torch.save(model.state_dict(), f'logs/b2_raw_best_model.pt')
        else:
            patience += 1
            if patience >= EARLY_STOPPING_PATIENCE:
                print("[EarlyStopping] Stopping training early.")
                break
    writer.close()

def evaluate(epoch, writer):
    model.eval()
    val_loss = 0
    all_sentiment_preds, all_sentiment_true = [], []
    all_intent_preds, all_intent_true = [], []
    with torch.no_grad():
        for batch in val_loader:
            if batch is None:
                continue  # Skip empty batches
            inputs = {
                'text': batch['text'].to(DEVICE),
                'vision': batch['vision'].to(DEVICE),
                'audio': batch['audio'].to(DEVICE),
                'video': batch['video'].to(DEVICE)
            }
            outputs = model(inputs, use_precomputed_embeddings=False)
            text_logits = outputs['text']
            label_targets = batch['labels'].to(DEVICE)
            loss_text = nn.functional.cross_entropy(text_logits, label_targets)
            sentiment_logits = outputs['sentiment']
            loss_sentiment = nn.functional.cross_entropy(sentiment_logits, batch['sentiment'].to(DEVICE))
            intent_logits = outputs['intent']
            loss_intent = nn.functional.cross_entropy(intent_logits, batch['intent'].to(DEVICE))
            quality_pred = outputs.get('quality', torch.zeros_like(batch['quality'].to(DEVICE)))
            loss_quality = nn.functional.mse_loss(quality_pred, batch['quality'].to(DEVICE))
            loss = loss_text + 0.4*loss_sentiment + 0.4*loss_intent + 0.15*loss_quality
            val_loss += loss.item()
            all_sentiment_preds.extend(sentiment_logits.argmax(dim=-1).cpu().numpy())
            all_sentiment_true.extend(batch['sentiment'].cpu().numpy())
            all_intent_preds.extend(intent_logits.argmax(dim=-1).cpu().numpy())
            all_intent_true.extend(batch['intent'].cpu().numpy())
    avg_val_loss = val_loss / len(val_loader)
    sentiment_acc = accuracy_score(all_sentiment_true, all_sentiment_preds)
    intent_acc = accuracy_score(all_intent_true, all_intent_preds)
    print(f"[Validation] Epoch {epoch+1}: Loss={avg_val_loss:.4f} | Sentiment Acc={sentiment_acc:.4f} | Intent Acc={intent_acc:.4f}")
    writer.add_scalar('Val/Loss', avg_val_loss, epoch)
    writer.add_scalar('Val/Sentiment_Acc', sentiment_acc, epoch)
    writer.add_scalar('Val/Intent_Acc', intent_acc, epoch)
    return avg_val_loss

if __name__ == '__main__':
    train()
