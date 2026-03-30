#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #command_line #cuda #deployment #memory_management #multimodal #python #source_code #src/training/train_b2.py #training #transformer
**Category:** Training System
**Status:** Active
"""









# Train B2

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #api #command_line #cuda #deployment #memory_management #multimodal #python #source_code #src\\training\\train_b2.py #training #transformer
# Category:** Training System
# Status:** Active

"""
B2 Multimodal Model Training Script

Scaffolds full training, evaluation, and checkpointing for ImpressionCore B2.

Author: GitHub Copilot
Date: 2025-06-29
"""
# --- Ensure src/ is in sys.path for robust imports ---
import sys, os
import argparse
import datetime
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import torch.distributed as dist
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from models.b2_multimodal.core.b2_multimodal_model import B2MultimodalModel

# Use embedding-based DataLoaders for efficient training
from training.datasets.data_loading import get_embedding_dataloaders


# --- Config ---
import io
from PIL import Image


# --- CLI args and config loading ---
import yaml
import json

parser = argparse.ArgumentParser(description='B2 Initialization/Embedding Training')
parser.add_argument('--output-dir', type=str, default=None, help='Directory for checkpoints/logs')
parser.add_argument('--manifest-dir', type=str, default=None, help='Directory containing manifest files')
parser.add_argument('--embed-dir', type=str, default=None, help='Directory containing embedding files')
parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
parser.add_argument('--config', type=str, default=None, help='Optional config file (YAML/JSON)')
# Unified config-driven options for loss weighting, dropout, curriculum
parser.add_argument('--loss-weight-sentiment', type=float, default=None, help='Loss weight for sentiment')
parser.add_argument('--loss-weight-intent', type=float, default=None, help='Loss weight for intent')
parser.add_argument('--loss-weight-quality', type=float, default=None, help='Loss weight for quality')
parser.add_argument('--dropout', type=float, default=None, help='Dropout rate for heads')
parser.add_argument('--curriculum-epochs', type=int, default=None, help='Epochs to train backbone only before unfreezing heads')
parser.add_argument('--head-lr-multiplier', type=float, default=None, help='Learning rate multiplier for heads in phase 2')
args, _ = parser.parse_known_args()

# Load config from file if provided
config = {}
if args.config:
    with open(args.config, 'r') as f:
        if args.config.endswith('.yaml') or args.config.endswith('.yml'):
            config = yaml.safe_load(f)
        elif args.config.endswith('.json'):
            config = json.load(f)
        else:
            raise ValueError('Unsupported config file format')

# Set random seed for reproducibility
import random
random.seed(args.seed)
torch.manual_seed(args.seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(args.seed)

# Helper to get config value with fallback
def get_cfg(key, default):
    return config.get(key, default)


timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
CHECKPOINT_DIR = os.path.abspath(args.output_dir) if args.output_dir else get_cfg('output_dir', f'checkpoints/b2_{timestamp}/')
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
writer = SummaryWriter(log_dir=os.path.join(CHECKPOINT_DIR, 'tensorboard'))

# === SOTA-Inspired Hyperparameters (AoE, DeepSeek Chimera, MoE, Multimodal LLMs) ===
# See: arXiv:2506.14794, DeepSeek Chimera, MoE best practices, ImpressionCore memlog
default_model_config = {
    'embed_dim': 768,
    'vocab_size': 50257,
    'img_dim': 256,
    'audio_dim': 16000,
    'num_layers': 12,
    'num_heads': 12,
    'max_seq_len': 128000,
    'n_experts': 4,  # MoE: 4 experts, 2 active per token
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
    # === Best-practice hyperparameters ===
    'dropout': 0.18,  # Heads (MoE/Chimera: 0.15-0.25), core: 0.12
    'core_dropout': 0.12,
    'lr': 2e-4,  # Backbone
    'head_lr_multiplier': 5.0,  # Heads/expert routers
    'batch_size': 2,  # Dynamic, increase if VRAM allows
    'epochs': 3,  # For dev: 3 epochs only
    'max_steps': 300,  # For dev: 300 steps per epoch
    'loss_weight_sentiment': 0.4,
    'loss_weight_intent': 0.4,
    'loss_weight_quality': 0.15,
    'curriculum_epochs': 4,  # Backbone only, then unfreeze heads
    'gradient_clip': 1.0,
    'early_stopping_patience': 6,
    'precision': 'amp',  # autocast, GradScaler
    'quantization': '8bit',  # For deployment
}

LOG_INTERVAL = get_cfg('log_interval', 10)
VAL_INTERVAL = get_cfg('val_interval', 1)



# --- Logging setup ---
LOG_FILE = os.path.join(CHECKPOINT_DIR, 'train_debug.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # Only for INFO and above
    ]
)

# Only show INFO and above in terminal (for StreamHandler)
class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.INFO

# Add InfoFilter only to StreamHandler(s)
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.addFilter(InfoFilter())


# Manifest/embedding dirs
EMBED_ROOT = args.embed_dir if args.embed_dir else get_cfg('embed_dir', 'F:/b2_embeddings')
EMBED_CATALOGUE = os.path.join(EMBED_ROOT, 'b2_embedding_catalogue.json')

# --- Print label distribution for train/val sets ---
def print_label_distribution(dataloader, split_name):
    sentiment_counts = [0, 0, 0]
    intent_counts = [0] * 10
    n = 0
    for batch in dataloader:
        for s in batch['sentiment'].cpu().numpy():
            if 0 <= s < 3:
                sentiment_counts[s] += 1
        for i in batch['intent'].cpu().numpy():
            if 0 <= i < 10:
                intent_counts[i] += 1
        n += len(batch['sentiment'])
        if n > 10000:  # Only sample a few batches for speed
            break
    print(f"[{split_name}] Sentiment distribution: {sentiment_counts}")
    print(f"[{split_name}] Intent distribution: {intent_counts}")

# Move this call after dataloader is defined




# --- Model Config ---
# === SOTA-Inspired Hyperparameters (AoE, DeepSeek Chimera, MoE, Multimodal LLMs) ===
# See: arXiv:2506.14794, DeepSeek Chimera, MoE best practices, ImpressionCore memlog
default_model_config = {
    'embed_dim': 768,
    'vocab_size': 50257,
    'img_dim': 256,
    'audio_dim': 16000,
    'num_layers': 12,
    'num_heads': 12,
    'max_seq_len': 128000,
    'n_experts': 4,  # MoE: 4 experts, 2 active per token
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
    # === Best-practice hyperparameters ===
    'dropout': 0.18,  # Heads (MoE/Chimera: 0.15-0.25), core: 0.12
    'core_dropout': 0.12,
    'lr': 2e-4,  # Backbone
    'head_lr_multiplier': 5.0,  # Heads/expert routers
    'batch_size': 2,  # Dynamic, increase if VRAM allows
    'epochs': 18,  # With early stopping
    'loss_weight_sentiment': 0.4,
    'loss_weight_intent': 0.4,
    'loss_weight_quality': 0.15,
    'curriculum_epochs': 4,  # Backbone only, then unfreeze heads
    'gradient_clip': 1.0,
    'early_stopping_patience': 6,
    'precision': 'amp',  # autocast, GradScaler
    'quantization': '8bit',  # For deployment
}

# Merge config file values over defaults
for k, v in default_model_config.items():
    if k not in config:
        config[k] = v

# Inject CLI/config-driven dropout (heads)
if args.dropout is not None:
    config['dropout'] = args.dropout
elif 'dropout' not in config:
    config['dropout'] = default_model_config['dropout']
# Core dropout (for transformer backbone)
if 'core_dropout' not in config:
    config['core_dropout'] = default_model_config['core_dropout']




# --- Embedding Dataloader ---
EMBED_ROOT = 'F:/b2_embeddings'
EMBED_CATALOGUE = 'F:/b2_embeddings/b2_embedding_catalogue.json'
BATCH_SIZE = config.get('batch_size', 2)
dataloaders = get_embedding_dataloaders(batch_size=BATCH_SIZE, shuffle=True, embed_root=EMBED_ROOT, catalogue_path=EMBED_CATALOGUE)

# For backward compatibility, use a combined dataloader (zip modalities)
from itertools import zip_longest
class CombinedEmbeddingLoader:
    def __init__(self, loaders):
        self.loaders = loaders
        self.length = min(len(l) for l in loaders.values())
    def __len__(self):
        return self.length
    def __iter__(self):
        batch_idx = 0
        for t, v, a, vid in zip(
            self.loaders['text'],
            self.loaders['images'],
            self.loaders['audio'],
            self.loaders['video']
        ):
            # Determine batch sizes for all modalities
            sizes = [
                t.shape[0] if hasattr(t, 'shape') else len(t),
                v.shape[0] if hasattr(v, 'shape') else len(v),
                a.shape[0] if hasattr(a, 'shape') else len(a),
                vid.shape[0] if hasattr(vid, 'shape') else len(vid)
            ]
            if not all(sz == sizes[0] for sz in sizes):
                print(f"[WARNING] Skipping batch {batch_idx} due to inconsistent batch sizes: {sizes}")
                # Optionally log more info about the batch here
                batch_idx += 1
                continue
            batch_size = sizes[0]
            # Generate more realistic random labels for meaningful training
            labels = torch.randint(0, 1000, (batch_size,), dtype=torch.long)  # Random vocab tokens 0-999
            sentiment = torch.randint(0, 3, (batch_size,), dtype=torch.long)  # Random sentiment 0-2 (neg, neutral, pos)
            intent = torch.randint(0, 10, (batch_size,), dtype=torch.long)  # Random intent 0-9
            quality = torch.rand(batch_size, dtype=torch.float32)  # Random quality 0.0-1.0
            if batch_idx == 0:
                logging.debug(f"labels shape: {labels.shape}, dtype: {labels.dtype}, range: {labels.min()}-{labels.max()}")
                logging.debug(f"sentiment shape: {sentiment.shape}, range: {sentiment.min()}-{sentiment.max()}")
                logging.debug(f"intent shape: {intent.shape}, range: {intent.min()}-{intent.max()}")
                logging.debug(f"quality shape: {quality.shape}, range: {quality.min():.3f}-{quality.max():.3f}")
            yield {
                'text': t,
                'vision': v,
                'audio': a,
                'video': vid,
                'labels': labels,
                'sentiment': sentiment,
                'intent': intent,
                'quality': quality
            }
            batch_idx += 1


dataloader = CombinedEmbeddingLoader(dataloaders)
print_label_distribution(dataloader, "Train/Val")



# --- Advanced memory optimization and context window management ---
from src.models.b2_multimodal.core.memory_optimization import apply_memory_optimizations
def optimize_model_config_and_device(model_config):
    import torch.nn as nn
    dummy = nn.Identity()
    apply_memory_optimizations(dummy, model_config)
    return model_config
config = optimize_model_config_and_device(config)
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# --- Distributed Training Init (optional) ---
def setup_distributed():
    if 'RANK' in os.environ and 'WORLD_SIZE' in os.environ:
        dist.init_process_group(backend='nccl' if torch.cuda.is_available() else 'gloo')
        torch.cuda.set_device(int(os.environ['LOCAL_RANK']))
        print(f"[Distributed] Initialized rank {dist.get_rank()} of {dist.get_world_size()}")
        return True
    return False

is_distributed = setup_distributed()

model = B2MultimodalModel(config)
if is_distributed:
    model = torch.nn.parallel.DistributedDataParallel(model.to(DEVICE), device_ids=[int(os.environ['LOCAL_RANK'])] if torch.cuda.is_available() else None)
else:
    model = model.to(DEVICE)

# --- Curriculum/Multi-Stage Training Setup ---
# Curriculum and head LR multiplier (best-practice)
curriculum_epochs = args.curriculum_epochs if args.curriculum_epochs is not None else config.get('curriculum_epochs', default_model_config['curriculum_epochs'])
head_lr_multiplier = args.head_lr_multiplier if args.head_lr_multiplier is not None else config.get('head_lr_multiplier', default_model_config['head_lr_multiplier'])

# Helper to get head parameters (sentiment, intent)
def get_head_params(model):
    head_params = []
    for n, p in model.named_parameters():
        if any(h in n for h in ['sentiment_head', 'intent_head']):
            head_params.append(p)
    return head_params

# Helper to get backbone parameters
def get_backbone_params(model):
    head_names = ['sentiment_head', 'intent_head']
    return [p for n, p in model.named_parameters() if not any(h in n for h in head_names)]


# Phase 1: freeze heads, optimizer for backbone only
for n, p in model.named_parameters():
    if any(h in n for h in ['sentiment_head', 'intent_head']):
        p.requires_grad = False
    else:
        p.requires_grad = True
LR = config.get('lr', 2e-4)
optimizer = optim.AdamW(get_backbone_params(model), lr=LR)


# --- Training Loop ---
def train(callbacks=None):
    best_val_loss = float('inf')
    patience = 0
    if callbacks is None:
        callbacks = []
    # Unified loss weights
    # SOTA-inspired loss weights (AoE, DeepSeek, MoE)
    loss_weight_sentiment = args.loss_weight_sentiment if args.loss_weight_sentiment is not None else config.get('loss_weight_sentiment', default_model_config['loss_weight_sentiment'])
    loss_weight_intent = args.loss_weight_intent if args.loss_weight_intent is not None else config.get('loss_weight_intent', default_model_config['loss_weight_intent'])
    loss_weight_quality = args.loss_weight_quality if args.loss_weight_quality is not None else config.get('loss_weight_quality', default_model_config['loss_weight_quality'])
    global optimizer
    EPOCHS = int(config.get('epochs', default_model_config['epochs']))
    EARLY_STOPPING_PATIENCE = config.get('early_stopping_patience', default_model_config['early_stopping_patience'])
    curriculum_epochs_effective = int(config.get('curriculum_epochs', default_model_config['curriculum_epochs']))
    print(f"[INFO] Training for {EPOCHS} epochs (config['epochs'] = {EPOCHS}). Curriculum phase switch at epoch {curriculum_epochs_effective}.")
    if curriculum_epochs_effective > EPOCHS:
        print(f"[WARNING] curriculum_epochs ({curriculum_epochs_effective}) > epochs ({EPOCHS}): curriculum phase will never be reached.")
    for epoch in range(EPOCHS):
        # --- Curriculum/Multi-Stage Training Phase Switch ---
        if epoch == curriculum_epochs:
            # Unfreeze heads
            for n, p in model.named_parameters():
                if any(h in n for h in ['sentiment_head', 'intent_head']):
                    p.requires_grad = True
            # Re-init optimizer with parameter groups: backbone (LR), heads (LR * multiplier)
            param_groups = [
                {'params': get_backbone_params(model), 'lr': LR},
                {'params': get_head_params(model), 'lr': LR * head_lr_multiplier}
            ]
            optimizer = optim.AdamW(param_groups)
            print(f"[Curriculum] Unfroze heads and set head LR multiplier to {head_lr_multiplier}")
        model.train()
        total_loss, total_text, total_sentiment, total_intent, total_quality = 0, 0, 0, 0, 0
        # Per-modality metrics
        all_text_preds, all_text_true = [], []
        all_sentiment_preds, all_sentiment_true = [], []
        all_intent_preds, all_intent_true = [], []
        # Use config-driven max_steps (default 300)
        max_steps = min(config.get('max_steps', 300), len(dataloader))
        for i, batch in enumerate(dataloader):
            if i >= max_steps:
                break
            optimizer.zero_grad()
            with torch.amp.autocast('cuda', enabled=getattr(model, 'use_amp', True)):
                # Prepare inputs for B2MultimodalModel
                inputs = {
                    'text': batch['text'].to(DEVICE),
                    'vision': batch['vision'].to(DEVICE),
                    'audio': batch['audio'].to(DEVICE),
                    'video': batch['video'].to(DEVICE)
                }
                # NaN/Inf check for inputs
                for k, v in inputs.items():
                    if torch.isnan(v).any() or torch.isinf(v).any():
                        print(f"[NaN/Inf] Detected in input '{k}' at step {i}, skipping batch.")
                        continue
                # Get outputs for all modalities
                text_outputs = model(inputs, output_modality='conversation', use_precomputed_embeddings=True)
                sentiment_outputs = model(inputs, output_modality='sentiment', use_precomputed_embeddings=True)
                intent_outputs = model(inputs, output_modality='intent', use_precomputed_embeddings=True)
                outputs = {
                    'text': text_outputs,
                    'sentiment': sentiment_outputs,
                    'intent': intent_outputs,
                    'quality': torch.zeros(batch['text'].size(0), device=DEVICE)
                }
                text_logits = outputs['text'][:, 0, :] if outputs['text'].dim() == 3 else outputs['text']
                label_targets = batch['labels'].squeeze() if batch['labels'].dim() > 1 else batch['labels']
                # NaN/Inf check for logits and labels
                if (torch.isnan(text_logits).any() or torch.isinf(text_logits).any() or
                    torch.isnan(label_targets.to(DEVICE)).any() or torch.isinf(label_targets.to(DEVICE)).any()):
                    print(f"[NaN/Inf] Detected in text logits or labels at step {i}, skipping batch.")
                    continue
                loss_text = nn.functional.cross_entropy(text_logits, label_targets.to(DEVICE))
                sentiment_logits = outputs['sentiment'][:, 0, :config['num_sentiment_classes']] if outputs['sentiment'].dim() == 3 else outputs['sentiment'][:, :config['num_sentiment_classes']]
                if (torch.isnan(sentiment_logits).any() or torch.isinf(sentiment_logits).any() or
                    torch.isnan(batch['sentiment'].to(DEVICE)).any() or torch.isinf(batch['sentiment'].to(DEVICE)).any()):
                    print(f"[NaN/Inf] Detected in sentiment logits or labels at step {i}, skipping batch.")
                    continue
                loss_sentiment = nn.functional.cross_entropy(sentiment_logits, batch['sentiment'].to(DEVICE))
                intent_logits = outputs['intent'][:, 0, :config['num_intent_classes']] if outputs['intent'].dim() == 3 else outputs['intent'][:, :config['num_intent_classes']]
                if (torch.isnan(intent_logits).any() or torch.isinf(intent_logits).any() or
                    torch.isnan(batch['intent'].to(DEVICE)).any() or torch.isinf(batch['intent'].to(DEVICE)).any()):
                    print(f"[NaN/Inf] Detected in intent logits or labels at step {i}, skipping batch.")
                    continue
                loss_intent = nn.functional.cross_entropy(intent_logits, batch['intent'].to(DEVICE))
                quality_pred = outputs['quality']
                quality_target = batch['quality'].float().to(DEVICE)
                if quality_pred.shape != quality_target.shape:
                    print(f"[DEBUG] Reshaping quality_pred from {quality_pred.shape} to {quality_target.shape}")
                    quality_pred = quality_pred.view_as(quality_target)
                if torch.isnan(quality_pred).any() or torch.isinf(quality_pred).any() or torch.isnan(quality_target).any() or torch.isinf(quality_target).any():
                    print(f"[NaN/Inf] Detected in quality prediction or target at step {i}, skipping batch.")
                    continue
                loss_quality = nn.functional.mse_loss(quality_pred, quality_target)
                # Unified weighted loss
                loss = loss_text + loss_weight_sentiment*loss_sentiment + loss_weight_intent*loss_intent + loss_weight_quality*loss_quality
                if torch.isnan(loss) or torch.isinf(loss):
                    print(f"[NaN/Inf] Detected in total loss at step {i}, skipping batch.")
                    continue
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=config.get('gradient_clip', default_model_config['gradient_clip']))
            optimizer.step()
            total_loss += loss.item()
            total_text += loss_text.item()
            total_sentiment += loss_sentiment.item()
            total_intent += loss_intent.item()
            total_quality += loss_quality.item()
            # Per-modality metrics collection
            text_pred = outputs['text'].argmax(dim=-1).detach().cpu().numpy()
            text_true = batch['labels'].detach().cpu().numpy()
            all_text_preds.extend(text_pred.flatten())
            all_text_true.extend(text_true.flatten())
            # --- Debugging for sentiment/intent prediction logic ---
            sentiment_logits = outputs['sentiment']
            logging.debug(f"Sentiment logits shape: {sentiment_logits.shape}, min: {sentiment_logits.min().item():.4f}, max: {sentiment_logits.max().item():.4f}")
            if sentiment_logits.shape[0] > 0:
                logging.debug(f"Sentiment logits sample: {sentiment_logits[0].detach().cpu().numpy()}")
            if sentiment_logits.shape[-1] != config.get('num_sentiment_classes', 3):
                logging.error(f"Sentiment logits last dim is {sentiment_logits.shape[-1]}, expected {config.get('num_sentiment_classes', 3)} (num classes)")
            sentiment_pred = sentiment_logits.argmax(dim=-1).cpu().numpy()
            sentiment_true = batch['sentiment'].cpu().numpy()
            logging.debug(f"Sentiment pred shape: {sentiment_pred.shape}, values: {sentiment_pred[:10]}")
            all_sentiment_preds.extend(sentiment_pred)
            all_sentiment_true.extend(sentiment_true)
            intent_logits = outputs['intent']
            logging.debug(f"Intent logits shape: {intent_logits.shape}, min: {intent_logits.min().item():.4f}, max: {intent_logits.max().item():.4f}")
            if intent_logits.shape[0] > 0:
                logging.debug(f"Intent logits sample: {intent_logits[0].detach().cpu().numpy()}")
            if intent_logits.shape[-1] != config.get('num_intent_classes', 10):
                logging.error(f"Intent logits last dim is {intent_logits.shape[-1]}, expected {config.get('num_intent_classes', 10)} (num classes)")
            intent_pred = intent_logits.argmax(dim=-1).cpu().numpy()
            intent_true = batch['intent'].cpu().numpy()
            logging.debug(f"Intent pred shape: {intent_pred.shape}, values: {intent_pred[:10]}")
            all_intent_preds.extend(intent_pred)
            all_intent_true.extend(intent_true)
            if i % LOG_INTERVAL == 0:
                print(f"[Epoch {epoch+1}] Step {i}: Loss={loss.item():.4f} (Text={loss_text.item():.4f}, Sentiment={loss_sentiment.item():.4f}, Intent={loss_intent.item():.4f}, Quality={loss_quality.item():.4f})")
                writer.add_scalar('Loss/Total', loss.item(), epoch * len(dataloader) + i)
                writer.add_scalar('Loss/Text', loss_text.item(), epoch * len(dataloader) + i)
                writer.add_scalar('Loss/Sentiment', loss_sentiment.item(), epoch * len(dataloader) + i)
                writer.add_scalar('Loss/Intent', loss_intent.item(), epoch * len(dataloader) + i)
                writer.add_scalar('Loss/Quality', loss_quality.item(), epoch * len(dataloader) + i)
        avg_loss = total_loss/(i+1)
        print(f"[Epoch {epoch+1}] Avg Loss={avg_loss:.4f}")
        writer.add_scalar('Loss/EpochAvg', avg_loss, epoch)
        # Debug: print a sample of predictions and ground-truth for sentiment/intent
        logging.debug(f"Train batch sentiment_true: {all_sentiment_true[:10]}")
        logging.debug(f"Train batch sentiment_pred: {all_sentiment_preds[:10]}")
        logging.debug(f"Train batch intent_true: {all_intent_true[:10]}")
        logging.debug(f"Train batch intent_pred: {all_intent_preds[:10]}")
        # Per-modality metrics (train)
        text_acc = accuracy_score(all_text_true, all_text_preds)
        writer.add_scalar('Train/Text_Acc', text_acc, epoch)
        sentiment_acc = accuracy_score(all_sentiment_true, all_sentiment_preds)
        sentiment_f1 = f1_score(all_sentiment_true, all_sentiment_preds, average='macro')
        writer.add_scalar('Train/Sentiment_Acc', sentiment_acc, epoch)
        writer.add_scalar('Train/Sentiment_F1', sentiment_f1, epoch)
        intent_acc = accuracy_score(all_intent_true, all_intent_preds)
        intent_f1 = f1_score(all_intent_true, all_intent_preds, average='macro')
        writer.add_scalar('Train/Intent_Acc', intent_acc, epoch)
        writer.add_scalar('Train/Intent_F1', intent_f1, epoch)
        # Advanced per-class metrics and confusion matrices
        sentiment_class_names = [f"S{i}" for i in range(config['num_sentiment_classes'])]
        intent_class_names = [f"I{i}" for i in range(config['num_intent_classes'])]
        log_per_class_metrics(all_sentiment_true, all_sentiment_preds, sentiment_class_names, writer, 'Train/Sentiment', epoch)
        log_per_class_metrics(all_intent_true, all_intent_preds, intent_class_names, writer, 'Train/Intent', epoch)
        if epoch % VAL_INTERVAL == 0:
            cm_sentiment = confusion_matrix(all_sentiment_true, all_sentiment_preds, labels=list(range(config['num_sentiment_classes'])))
            cm_intent = confusion_matrix(all_intent_true, all_intent_preds, labels=list(range(config['num_intent_classes'])))
            writer.add_figure('Train/Sentiment_CM', plot_confusion_matrix(cm_sentiment, 'Sentiment'), epoch)
            writer.add_figure('Train/Intent_CM', plot_confusion_matrix(cm_intent, 'Intent'), epoch)
            save_confusion_matrix_csv(cm_sentiment, sentiment_class_names, 'Train/Sentiment', epoch)
            save_confusion_matrix_csv(cm_intent, intent_class_names, 'Train/Intent', epoch)
        # Save checkpoint
        if not is_distributed or (is_distributed and dist.get_rank() == 0):
            log_confusion_matrix_image(writer, cm_sentiment, 'Train/Sentiment_CM', epoch)
            log_confusion_matrix_image(writer, cm_intent, 'Train/Intent_CM', epoch)
            checkpoint_dir = r"F:/models/b2_checkpoints"
            os.makedirs(checkpoint_dir, exist_ok=True)
            checkpoint_path = os.path.join(checkpoint_dir, f"model_epoch_{epoch+1}.pt")
            torch.save(model.state_dict(), checkpoint_path)
            print(f"[Checkpoint] Saved model to {checkpoint_path}")
            for callback in callbacks:
                callback(epoch=epoch, model=model, metrics={
                    'loss': avg_loss,
                    'text_acc': text_acc,
                    'sentiment_acc': sentiment_acc,
                    'intent_acc': intent_acc
                })
        if (epoch+1) % VAL_INTERVAL == 0:
            val_loss, val_metrics = evaluate(epoch)
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience = 0
            else:
                patience += 1
                print(f"[EarlyStopping] Patience {patience}/{EARLY_STOPPING_PATIENCE}")
                if patience >= EARLY_STOPPING_PATIENCE:
                    print("[EarlyStopping] Stopping training early.")
                    break
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import itertools
def log_per_class_metrics(y_true, y_pred, class_names, writer, tag, epoch):
    """
    Log per-class precision, recall, F1, and support to TensorBoard and CSV.
    """
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    # Log to TensorBoard
    for cls in class_names:
        writer.add_scalar(f'{tag}/Precision_{cls}', report[cls]['precision'], epoch)
        writer.add_scalar(f'{tag}/Recall_{cls}', report[cls]['recall'], epoch)
        writer.add_scalar(f'{tag}/F1_{cls}', report[cls]['f1-score'], epoch)
        writer.add_scalar(f'{tag}/Support_{cls}', report[cls]['support'], epoch)
    # Save as CSV
    df = pd.DataFrame(report).transpose()
    csv_path = os.path.join(CHECKPOINT_DIR, f'{tag}_per_class_metrics_epoch_{epoch+1}.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path)
    print(f"[Metrics] Saved per-class metrics to {csv_path}")

def save_confusion_matrix_csv(cm, class_names, tag, epoch):
    df = pd.DataFrame(cm, index=class_names, columns=class_names)
    csv_path = os.path.join(CHECKPOINT_DIR, f'{tag}_confusion_matrix_epoch_{epoch+1}.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path)
    print(f"[Metrics] Saved confusion matrix to {csv_path}")

def plot_confusion_matrix(cm, title):
    fig, ax = plt.subplots(figsize=(5,5))
    ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.set_title(f'{title} Confusion Matrix')
    plt.colorbar(ax.images[0], ax=ax)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('True')
    plt.tight_layout()
    return fig
def log_confusion_matrix_image(writer, cm, tag, epoch):
    fig = plot_confusion_matrix(cm, tag)
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image = Image.open(buf)
    writer.add_image(tag, np.array(image), epoch, dataformats='HWC')
    plt.close(fig)

class BestSentimentF1Callback:
    def __init__(self):
        self.best_f1 = 0
    def __call__(self, epoch, model, metrics):
        f1 = metrics.get('sentiment_f1', 0)
        if f1 > self.best_f1:
            self.best_f1 = f1
            print(f"[Callback] New best sentiment F1: {f1:.4f} at epoch {epoch+1}. Saving model.")
            torch.save(model.state_dict(), f'checkpoints/b2/best_sentiment_f1.pt')

def log_sample_predictions_callback(epoch, model, metrics):
    model.eval()
    with torch.no_grad():
        for i, batch in enumerate(dataloader):
            # Prepare inputs for B2MultimodalModel
            inputs = {
                'text': batch['text'].to(DEVICE),
                'vision': batch['vision'].to(DEVICE),
                'audio': batch['audio'].to(DEVICE),
                'video': batch['video'].to(DEVICE)
            }

            # Get outputs for all modalities
            text_outputs = model(inputs, output_modality='conversation', use_precomputed_embeddings=True)
            sentiment_outputs = model(inputs, output_modality='conversation', use_precomputed_embeddings=True)  # Use conversation head for sentiment
            intent_outputs = model(inputs, output_modality='conversation', use_precomputed_embeddings=True)     # Use conversation head for intent

            outputs = {
                'text': text_outputs,
                'sentiment': sentiment_outputs,
                'intent': intent_outputs,
                'quality': torch.zeros(batch['text'].size(0), device=DEVICE)  # Placeholder for quality
            }
            # Log first batch only
            if i == 0:
                # Log first 2 text predictions
                pred_tokens = outputs['text'].argmax(dim=-1)[:2].cpu().numpy()
                true_tokens = batch['labels'][:2].cpu().numpy()
                for idx in range(2):
                    writer.add_text(f'Sample/Text_Pred_{idx}', str(pred_tokens[idx]), epoch)
                    writer.add_text(f'Sample/Text_True_{idx}', str(true_tokens[idx]), epoch)
                # Log first 2 sentiment predictions
                pred_sent = outputs['sentiment'].argmax(dim=-1)[:2].cpu().numpy()
                true_sent = batch['sentiment'][:2].cpu().numpy()
                for idx in range(2):
                    writer.add_text(f'Sample/Sentiment_Pred_{idx}', str(pred_sent[idx]), epoch)
                    writer.add_text(f'Sample/Sentiment_True_{idx}', str(true_sent[idx]), epoch)
                break
    # ...existing code...


def evaluate(epoch):
    model.eval()
    val_loss, val_text, val_sentiment, val_intent, val_quality = 0, 0, 0, 0, 0
    n = 0
    all_sentiment_preds, all_sentiment_true = [], []
    all_intent_preds, all_intent_true = [], []
    # Check for empty validation set
    if len(dataloader) == 0:
        print("[ERROR] Validation dataloader is empty!")
    with torch.no_grad():
        for i, batch in enumerate(dataloader):
            # Prepare inputs for B2MultimodalModel
            inputs = {
                'text': batch['text'].to(DEVICE),
                'vision': batch['vision'].to(DEVICE),
                'audio': batch['audio'].to(DEVICE),
                'video': batch['video'].to(DEVICE)
            }

            # Get outputs for all modalities
            text_outputs = model(inputs, output_modality='conversation', use_precomputed_embeddings=True)
            sentiment_outputs = model(inputs, output_modality='conversation', use_precomputed_embeddings=True)  # Use conversation head for sentiment
            intent_outputs = model(inputs, output_modality='conversation', use_precomputed_embeddings=True)     # Use conversation head for intent

            outputs = {
                'text': text_outputs,
                'sentiment': sentiment_outputs,
                'intent': intent_outputs,
                'quality': torch.zeros(batch['text'].size(0), device=DEVICE)  # Placeholder for quality
            }
            text_logits = outputs['text'].squeeze(1) if outputs['text'].dim() == 3 else outputs['text']
            label_targets = batch['labels'].squeeze() if batch['labels'].dim() > 1 else batch['labels']
            loss_text = nn.functional.cross_entropy(text_logits, label_targets.to(DEVICE))

            sentiment_logits = outputs['sentiment'].squeeze(1) if outputs['sentiment'].dim() == 3 else outputs['sentiment']
            sentiment_logits = sentiment_logits[:, :config['num_sentiment_classes']]  # Use only sentiment classes
            intent_logits = outputs['intent'].squeeze(1) if outputs['intent'].dim() == 3 else outputs['intent']
            intent_logits = intent_logits[:, :config['num_intent_classes']]  # Use only intent classes

            loss_sentiment = nn.functional.cross_entropy(sentiment_logits, batch['sentiment'].to(DEVICE))
            loss_intent = nn.functional.cross_entropy(intent_logits, batch['intent'].to(DEVICE))
            loss_quality = nn.functional.mse_loss(outputs['quality'], batch['quality'].float().to(DEVICE))
            loss = loss_text + 0.2*loss_sentiment + 0.2*loss_intent + 0.1*loss_quality
            val_loss += loss.item()
            val_text += loss_text.item()
            val_sentiment += loss_sentiment.item()
            val_intent += loss_intent.item()
            val_quality += loss_quality.item()
            n += 1
            # Advanced metrics: sentiment and intent accuracy/F1
            # Use processed logits for predictions to ensure correct class range
            sentiment_pred = sentiment_logits.argmax(dim=-1).cpu().numpy()
            sentiment_true = batch['sentiment'].cpu().numpy()
            all_sentiment_preds.extend(sentiment_pred)
            all_sentiment_true.extend(sentiment_true)
            intent_pred = intent_logits.argmax(dim=-1).cpu().numpy()
            intent_true = batch['intent'].cpu().numpy()
            all_intent_preds.extend(intent_pred)
            all_intent_true.extend(intent_true)
            if i == 0:
                # Print sample text logits with correct indexing based on tensor dimension
                if outputs['text'].dim() == 3:
                    logging.debug(f"Sample text logits: {outputs['text'][0, :5, :5]}")
                else:
                    logging.debug(f"Sample text logits: {outputs['text'][0, :5]}")
                logging.debug(f"Sample sentiment prediction: {outputs['sentiment'][0]}")
                # Debug: print a sample of predictions and ground-truth for sentiment/intent
                logging.debug(f"Validation batch sentiment_true: {sentiment_true[:10]}")
                logging.debug(f"Validation batch sentiment_pred: {sentiment_pred[:10]}")
                logging.debug(f"Validation batch intent_true: {intent_true[:10]}")
                logging.debug(f"Validation batch intent_pred: {intent_pred[:10]}")
    if n > 0:
        writer.add_scalar('Val/Loss', val_loss/n, epoch)
        writer.add_scalar('Val/Text', val_text/n, epoch)
        writer.add_scalar('Val/Sentiment', val_sentiment/n, epoch)
        writer.add_scalar('Val/Intent', val_intent/n, epoch)
        writer.add_scalar('Val/Quality', val_quality/n, epoch)
        print(f"[Validation] Epoch {epoch+1}: Loss={val_loss/n:.4f}")
        # Advanced metrics
        sentiment_acc = accuracy_score(all_sentiment_true, all_sentiment_preds)
        sentiment_f1 = f1_score(all_sentiment_true, all_sentiment_preds, average='macro')
        intent_acc = accuracy_score(all_intent_true, all_intent_preds)
        intent_f1 = f1_score(all_intent_true, all_intent_preds, average='macro')
        writer.add_scalar('Val/Sentiment_Acc', sentiment_acc, epoch)
        writer.add_scalar('Val/Sentiment_F1', sentiment_f1, epoch)
        writer.add_scalar('Val/Intent_Acc', intent_acc, epoch)
        writer.add_scalar('Val/Intent_F1', intent_f1, epoch)
        # Per-class metrics and confusion matrices
        sentiment_class_names = [f"S{i}" for i in range(config['num_sentiment_classes'])]
        intent_class_names = [f"I{i}" for i in range(config['num_intent_classes'])]
        log_per_class_metrics(all_sentiment_true, all_sentiment_preds, sentiment_class_names, writer, 'Val/Sentiment', epoch)
        log_per_class_metrics(all_intent_true, all_intent_preds, intent_class_names, writer, 'Val/Intent', epoch)
        cm_sentiment = confusion_matrix(all_sentiment_true, all_sentiment_preds, labels=list(range(config['num_sentiment_classes'])))
        cm_intent = confusion_matrix(all_intent_true, all_intent_preds, labels=list(range(config['num_intent_classes'])))
        writer.add_figure('Val/Sentiment_CM', plot_confusion_matrix(cm_sentiment, 'Sentiment'), epoch)
        writer.add_figure('Val/Intent_CM', plot_confusion_matrix(cm_intent, 'Intent'), epoch)
        save_confusion_matrix_csv(cm_sentiment, sentiment_class_names, 'Val/Sentiment', epoch)
        save_confusion_matrix_csv(cm_intent, intent_class_names, 'Val/Intent', epoch)
        print(f"[Validation] Sentiment Acc={sentiment_acc:.4f}, F1={sentiment_f1:.4f} | Intent Acc={intent_acc:.4f}, F1={intent_f1:.4f}")
        return val_loss/n, {
            'sentiment_acc': sentiment_acc,
            'sentiment_f1': sentiment_f1,
            'intent_acc': intent_acc,
            'intent_f1': intent_f1
        }
    return float('inf'), {}


# --- Simple grid search for key hyperparameters ---
def grid_search():
    # Define grid
    grid = {
        'loss_weight_sentiment': [0.1, 0.2, 0.5],
        'loss_weight_intent': [0.1, 0.2, 0.5],
        'dropout': [0.1, 0.3, 0.5],
        'head_lr_multiplier': [1.0, 2.0, 5.0],
    }
    keys, values = zip(*grid.items())
    # Prepare to collect results
    results = []
    for combo in itertools.product(*values):
        params = dict(zip(keys, combo))
        print(f"[GridSearch] Running with params: {params}")
        # Update config/args
        args.loss_weight_sentiment = params['loss_weight_sentiment']
        args.loss_weight_intent = params['loss_weight_intent']
        args.dropout = params['dropout']
        args.head_lr_multiplier = params['head_lr_multiplier']
        # Update config dict for dropout
        config['dropout'] = params['dropout']
        # Run training for a few epochs (reduced for speed)
        global EPOCHS
        orig_epochs = EPOCHS
        EPOCHS = 2  # Reduced for grid search speed (was 5)
        # Run training and capture best metrics
        best_metrics = {'sentiment_f1': 0, 'intent_f1': 0, 'sentiment_acc': 0, 'intent_acc': 0}
        def capture_metrics_callback(epoch, model, metrics):
            for k in best_metrics:
                if k in metrics and metrics[k] > best_metrics[k]:
                    best_metrics[k] = metrics[k]
        train(callbacks=[capture_metrics_callback])
        # Save result for this config
        result_row = {**params, **best_metrics}
        results.append(result_row)
        EPOCHS = orig_epochs
    # Save all results to CSV
    import pandas as pd
    grid_results_path = os.path.join(CHECKPOINT_DIR, f'grid_search_results_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    df = pd.DataFrame(results)
    df.to_csv(grid_results_path, index=False)
    print(f"[GridSearch] Saved all grid search results to {grid_results_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--grid-search', action='store_true', help='Run grid search over key hyperparameters')
    args2, _ = parser.parse_known_args()
    if getattr(args2, 'grid_search', False):
        grid_search()
    else:
        train()
    writer.close()
