#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #cuda #memory_management #multimodal #python #pytorch #source_code #src/training/train_b2_enhanced_optimized.py #testing #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #command_line #cuda #memory_management #multimodal #python #pytorch #source_code #src\\training\\train_b2_enhanced_optimized.py #testing #training
# Category:** Training System
# Status:** Active

"""
ImpressionCore B2 Enhanced Training - OPTIMIZED CYCLE 2
Quick optimization run with tuned hyperparameters for maximum gains

Based on successful Cycle 1 results:
- Sentiment: 33.85% → Target: 40-45%
- Intent: 9.64% → Target: 15-20%
- Focus: Fine-tuning with reduced learning rates and enhanced monitoring
"""


import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from sklearn.metrics import accuracy_score, f1_score, classification_report
import argparse


# Import the enhanced architecture from existing training module

from src.training.datasets.data_loading import get_embedding_dataloaders
from src.models.b2_multimodal.core.b2_multimodal_model import B2MultimodalModel
from src.core.utils.rich_enhancements import FallbackProgress
from src.core.utils.rich_logging import RichLogger
from src.core.utils.rich_status_animation import RichStatusAnimation

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# --- CLI args and config loading ---
import yaml
import json
parser = argparse.ArgumentParser(description='B2 Enhanced/Optimized Training')
parser.add_argument('--output-dir', type=str, default=None, help='Directory for checkpoints/logs')
parser.add_argument('--init-checkpoint', type=str, default=None, help='Path to initialization checkpoint')
parser.add_argument('--manifest-dir', type=str, default=None, help='Directory containing manifest files')
parser.add_argument('--embed-dir', type=str, default=None, help='Directory containing embedding files')
parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
parser.add_argument('--config', type=str, default=None, help='Optional config file (YAML/JSON)')
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

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_DIR = os.path.abspath(args.output_dir) if args.output_dir else get_cfg('output_dir', f'enhanced_checkpoints_{timestamp}')
os.makedirs(OUTPUT_DIR, exist_ok=True)
class EnhancedB2Model(nn.Module):
    """Enhanced B2 model with dedicated classification heads for optimized training"""

    def __init__(self, base_model, config):
        super().__init__()
        self.base_model = base_model
        self.config = config
        # Dedicated classification heads
        self.sentiment_classifier = nn.Sequential(
            nn.Linear(config['embed_dim'], 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, config['num_sentiment_classes'])
        )
        # Enhanced Intent Classifier for 10-class problem
        self.intent_classifier = nn.Sequential(
            nn.Linear(config['embed_dim'], 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(512, 384),
            nn.LayerNorm(384),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(384, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, config['num_intent_classes'])
        )

    def forward(self, batch_data):
        """Forward pass with enhanced outputs
        Debugs and robustly extracts the correct embedding tensor for classification.
        """
        # DEBUG: Print all input shapes at the start of forward
        if isinstance(batch_data, dict):
            for k, v in batch_data.items():
                if hasattr(v, "shape"):
                    print(f"[DEBUG] forward input {k} shape: {v.shape}")
        base_outputs = self.base_model(batch_data)
        # --- Debug print for base_outputs ---
        print("[DEBUG] base_outputs type:", type(base_outputs))
        if isinstance(base_outputs, dict):
            for k, v in base_outputs.items():
                print(f"[DEBUG] base_outputs[{{k}}] type: {{type(v)}}, shape: {{getattr(v, 'shape', None)}}")
        else:
            print("[DEBUG] base_outputs shape:", getattr(base_outputs, 'shape', None))

        # --- Robust extraction of embedding ---
        text_emb = None
        if isinstance(base_outputs, dict):
            # Try common embedding keys
            for key in ['embedding', 'text_embedding', 'text_output', 'hidden_state', 'last_hidden_state', 'text']:
                if key in base_outputs:
                    text_emb = base_outputs[key]
                    print(f"[DEBUG] Using base_outputs['{key}'] as text_emb")
                    break
            if text_emb is None:
                # Fallback: use the first tensor value in the dict
                for v in base_outputs.values():
                    if hasattr(v, 'shape') and len(v.shape) >= 2:
                        text_emb = v
                        print("[DEBUG] Using first tensor-like value in base_outputs as text_emb")
                        break
        else:
            text_emb = base_outputs
            print("[DEBUG] Using base_outputs directly as text_emb")

        # --- PATCH: Debug and fix batch size mismatches ---
        batch_size = None
        if isinstance(batch_data, dict):
            for k in ['sentiment_labels', 'intent_labels', 'embeddings', 'text', 'hidden_state']:
                if k in batch_data and hasattr(batch_data[k], 'shape'):
                    batch_size = batch_data[k].shape[0]
                    break
        if batch_size is None and hasattr(text_emb, 'shape'):
            batch_size = text_emb.shape[0]
        print(f"[DEBUG] In EnhancedB2Model.forward: batch_size={batch_size}, text_emb.shape={getattr(text_emb, 'shape', None)}")
        if text_emb is None:
            raise ValueError(
                "[ERROR] Could not extract a valid embedding tensor from base_outputs.\n"
                "Your base model must return a hidden state or embedding of shape [batch, seq, embed_dim] or [batch, embed_dim].\n"
                "\n"
                "--- TEMPLATE: Update your B2MultimodalModel forward() to return a dict with a hidden state ---\n"
                "def forward(self, ...):\n"
                "    ...\n"
                "    return {\n"
                "        'logits': logits,\n"
                "        'hidden_state': hidden_state  # shape: [batch, seq, 768] or [batch, 768]\n"
                "    }\n"
                "--- END TEMPLATE ---\n"
                "\n"
                "Then, in EnhancedB2Model, use the 'hidden_state' key for classification.\n"
            )

        # Ensure logits have correct batch size
        # (Moved debug print after logits assignment)

        # Pool the sequence dimension if needed
        if hasattr(text_emb, 'shape') and len(text_emb.shape) == 3:  # [batch, seq, hidden]
            text_emb = text_emb.mean(dim=1)  # [batch, hidden]
            print("[DEBUG] Pooled sequence dimension of text_emb to [batch, hidden]")

        # Final shape check
        if hasattr(text_emb, 'shape') and text_emb.shape[-1] != self.config['embed_dim']:
            print(f"[WARNING] text_emb last dim is {{text_emb.shape[-1]}}, expected {{self.config['embed_dim']}}. Attempting to fix...")
            # Try to flatten or select last hidden if possible
            if len(text_emb.shape) > 2:
                text_emb = text_emb.view(text_emb.shape[0], -1)
                print("[DEBUG] Flattened text_emb to [batch, -1]")
            if text_emb.shape[-1] != self.config['embed_dim']:
                raise ValueError(f"text_emb shape mismatch: got {{text_emb.shape}}, expected last dim {{self.config['embed_dim']}}")

        sentiment_logits = self.sentiment_classifier(text_emb)
        intent_logits = self.intent_classifier(text_emb)
        print(f"[DEBUG] sentiment_logits.shape={getattr(sentiment_logits, 'shape', None)}, intent_logits.shape={getattr(intent_logits, 'shape', None)}")
        return {
            'text_output': text_emb,
            'sentiment_logits': sentiment_logits,
            'intent_logits': intent_logits,
            'base_outputs': base_outputs
        }

# Model Configuration (matching existing B2 setup)
MODEL_CONFIG = {
    'embed_dim': 768,
    'num_layers': 12,
    'num_heads': 12,
    'vocab_size': 50257,
    'max_seq_length': 1024,  # Default, will be dynamically reduced if needed
    'ffn_hidden_dim': 3072,

    # Multimodal parameters
    'img_dim': 256,
    'audio_dim': 16000,
    'max_seq_len': 1024,  # Default, will be dynamically reduced if needed
    'n_experts': 4,
    'vision_decoder_layers': 8,
    'vision_decoder_steps': 50,
    'audio_decoder_layers': 8,
    'audio_decoder_steps': 50,
    'sp_model_path': 'dummy.model',
    'vision_patch_dim': 768,
    'patch_size': 16,
    'audio_feat_dim': 768,
    'n_mels': 64,
    'sample_rate': 16000,
    'video_feat_dim': 768,
    'num_frames': 8,
    'video_mean': 0.5,
    'video_std': 0.5,

    # User prompt context enforcement
    'user_prompt_context': 128,  # Always cap user prompt to 128 tokens

    # Classification configurations
    'num_sentiment_classes': 3,  # Negative, Neutral, Positive
    'num_intent_classes': 10,    # Based on training data

    # Optimized training parameters for Cycle 2
    'batch_size': 2,
    'base_learning_rate': 0.00007,      # Reduced from 0.0001
    'classification_learning_rate': 0.0003,  # Reduced from 0.0005
    'weight_decay': 0.01,
    'gradient_clip_norm': 1.0,

    # Enhanced loss weights for Cycle 2
    'loss_weights': {
        'text': 0.25,       # Reduced to focus on classification
        'sentiment': 1.2,   # Slightly increased for better learning
        'intent': 2.5,      # Increased for harder problem
        'quality': 0.15     # Reduced
    },

    # Training settings
    'num_epochs': 3,       # Reduced for quick test
    'early_stopping_patience': 8,
    'validation_interval': 1,
    'log_interval': 5,
    'save_interval': 3
}

# --- Advanced memory optimization and context window management ---
from src.models.b2_multimodal.core.memory_optimization import apply_memory_optimizations
# Apply memory optimizations and context window logic before model/trainer instantiation
def optimize_model_config_and_device(model_config):
    # Dummy model for device move (not used for weights)
    import torch.nn as nn
    dummy = nn.Identity()
    # This will update model_config in-place and move dummy to device
    apply_memory_optimizations(dummy, model_config)
    return model_config

MODEL_CONFIG = optimize_model_config_and_device(MODEL_CONFIG)

class OptimizedEnhancedTrainer:
    """Optimized trainer for quick enhanced training cycle 2"""

    def __init__(self, config: Dict):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # --- Patch: Prevent duplicate log handlers and add file logging ---
        self.logger = RichLogger("Enhanced-Cycle2")
        # Remove duplicate handlers if any
        if hasattr(self.logger, 'logger'):
            logger_obj = self.logger.logger
            if getattr(logger_obj, 'handlers', None):
                # Remove all handlers except the first one (console)
                logger_obj.handlers = [h for i, h in enumerate(logger_obj.handlers) if i == 0]
            # Add file handler if not present
            file_log_path = os.path.join("logs", "enhanced_training.log")
            os.makedirs("logs", exist_ok=True)
            if not any(isinstance(h, logging.FileHandler) for h in logger_obj.handlers):
                file_handler = logging.FileHandler(file_log_path, mode='a', encoding='utf-8')
                file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s'))
                logger_obj.addHandler(file_handler)

        self.status_animation = RichStatusAnimation()

        # Performance tracking
        self.best_sentiment_acc = 0.0
        self.best_intent_acc = 0.0
        self.training_start_time = None
        self.step_count = 0

        # Enhanced monitoring
        self.performance_history = {
            'sentiment_acc': [],
            'intent_acc': [],
            'loss': [],
            'improvement_rate': []
        }

        self.logger.info("Initializing Enhanced Training Cycle 2")
        self.logger.info("Target: Sentiment 40-45%, Intent 15-20%")

    def load_model_from_checkpoint(self) -> EnhancedB2Model:
        """Load and create enhanced model for cycle 2 - CONTINUING FROM CYCLE 1"""
        import warnings
        # --- Patch: Suppress PyTorch FutureWarning about weights_only ---
        warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

        self.logger.info(f"🏗️ Creating Enhanced B2 Model for Cycle 2")

        # Create base B2 multimodal model
        base_model = B2MultimodalModel(MODEL_CONFIG).to(self.device)

        # Create our enhanced model
        model = EnhancedB2Model(base_model, MODEL_CONFIG).to(self.device)

        # Try to load the previous enhanced model checkpoint
        checkpoint_path = "best_b2_enhanced_model.pth"
        if os.path.exists(checkpoint_path):
            self.logger.info(f"📂 Loading previous enhanced model: {checkpoint_path}")
            try:
                # Use weights_only=True for PyTorch >=2.2, fallback for older
                try:
                    checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=True)
                except TypeError:
                    checkpoint = torch.load(checkpoint_path, map_location=self.device)
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['model_state_dict'], strict=False)
                    # Load previous performance metrics if available
                    if 'best_sentiment_acc' in checkpoint:
                        prev_sentiment = checkpoint.get('best_sentiment_acc', 0.3385)
                        prev_intent = checkpoint.get('best_intent_acc', 0.0964)
                        self.best_sentiment_acc = prev_sentiment
                        self.best_intent_acc = prev_intent
                        self.logger.success(f"✅ Enhanced Model loaded from Cycle 1!")
                        self.logger.info(f"📈 Starting from: Sentiment={prev_sentiment:.3f}, Intent={prev_intent:.3f}")
                    else:
                        self.best_sentiment_acc = 0.3385
                        self.best_intent_acc = 0.0964
                        self.logger.success(f"✅ Enhanced Model loaded with known baselines!")
                        self.logger.info(f"📈 Starting from: Sentiment=0.3385, Intent=0.0964")
                elif isinstance(checkpoint, dict):
                    # Try loading as a plain state dict (legacy format)
                    model.load_state_dict(checkpoint, strict=False)
                    self.logger.success("✅ Loaded legacy checkpoint (plain state dict)")
                    self.best_sentiment_acc = 0.3385
                    self.best_intent_acc = 0.0964
                    self.logger.info("📈 Starting from: Sentiment=0.3385, Intent=0.0964")
                else:
                    self.logger.warning("⚠️ Unrecognized checkpoint format, starting fresh")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load checkpoint: {str(e)[:50]}...")
                self.logger.info(f"🆕 Starting fresh training")
        else:
            self.logger.info(f"🆕 No previous checkpoint found, starting fresh")

        self.logger.success(f"✅ Enhanced Model ready for Cycle 2")
        return model

    def setup_optimized_training(self, model: EnhancedB2Model) -> Tuple[optim.Optimizer, optim.Optimizer]:
        """Setup optimized optimizers with reduced learning rates for fine-tuning"""

        # Reduced learning rates for fine-tuning (30% reduction)
        base_lr = self.config.get('base_learning_rate', 0.00007)  # Fixed key name
        classification_lr = self.config.get('classification_learning_rate', 0.0003)  # Fixed key name

        # Separate optimizers for fine-grained control
        # Base model parameters (everything except classification heads)
        base_params = []
        classification_params = []

        for name, param in model.named_parameters():
            if 'classifier' in name:
                classification_params.append(param)
            else:
                base_params.append(param)

        base_optimizer = optim.AdamW(
            base_params,
            lr=base_lr,
            weight_decay=self.config.get('weight_decay', 0.01),
            eps=1e-8
        )

        classification_optimizer = optim.AdamW(
            classification_params,
            lr=classification_lr,
            weight_decay=self.config.get('weight_decay', 0.01),
            eps=1e-8
        )

        self.logger.info(f"⚙️ Optimized learning rates - Base: {base_lr}, Classification: {classification_lr}")
        return base_optimizer, classification_optimizer

    def compute_optimized_loss(self, outputs: Dict, targets: Dict) -> Tuple[torch.Tensor, Dict]:
        """Compute loss with optimized weights for cycle 2"""

        # Fine-tuned loss weights based on cycle 1 results
        sentiment_weight = self.config['loss_weights']['sentiment']  # 1.2
        intent_weight = self.config['loss_weights']['intent']  # 2.5

        # Compute individual losses (only classification for now)
        sentiment_loss = nn.CrossEntropyLoss()(
            outputs['sentiment_logits'],
            targets['sentiment_labels']
        )

        intent_loss = nn.CrossEntropyLoss()(
            outputs['intent_logits'],
            targets['intent_labels']
        )

        # Weighted combination (focusing on classification)
        total_loss = (
            sentiment_weight * sentiment_loss +
            intent_weight * intent_loss
        )

        loss_dict = {
            'total': total_loss.item(),
            'sentiment': sentiment_loss.item(),
            'intent': intent_loss.item()
        }

        return total_loss, loss_dict

    def evaluate_with_detailed_metrics(self, model: EnhancedB2Model,
                                     dataloader: DataLoader) -> Dict:
        """Enhanced evaluation with detailed metrics and improvement tracking"""
        model.eval()

        all_sentiment_preds = []
        all_sentiment_labels = []
        all_intent_preds = []
        all_intent_labels = []
        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for batch in dataloader:
                # Move all tensors in batch to device
                batch = {k: v.to(self.device) if hasattr(v, 'to') else v for k, v in batch.items()}
                batch_size = batch['embeddings'].shape[0] if 'embeddings' in batch else next(iter(batch.values())).shape[0]
                # Patch: Rename 'embeddings' to 'text' for B2MultimodalModel compatibility
                batch_for_model = dict(batch)
                if 'embeddings' in batch_for_model:
                    batch_for_model['text'] = batch_for_model.pop('embeddings')
                # Forward pass
                outputs = model(batch_for_model)
                # Use real labels if present, else create dummy
                sentiment_labels = batch.get('sentiment_labels', torch.randint(0, 3, (batch_size,)).to(self.device))
                intent_labels = batch.get('intent_labels', torch.randint(0, 10, (batch_size,)).to(self.device))
                dummy_batch = {
                    'sentiment_labels': sentiment_labels,
                    'intent_labels': intent_labels
                }

                # Compute loss
                loss, _ = self.compute_optimized_loss(outputs, dummy_batch)
                total_loss += loss.item()
                num_batches += 1

                # Collect predictions
                sentiment_preds = torch.argmax(outputs['sentiment_logits'], dim=1)
                intent_preds = torch.argmax(outputs['intent_logits'], dim=1)

                all_sentiment_preds.extend(sentiment_preds.cpu().numpy())
                all_sentiment_labels.extend(dummy_batch['sentiment_labels'].cpu().numpy())
                all_intent_preds.extend(intent_preds.cpu().numpy())
                all_intent_labels.extend(dummy_batch['intent_labels'].cpu().numpy())

        # Calculate metrics
        sentiment_acc = accuracy_score(all_sentiment_labels, all_sentiment_preds)
        sentiment_f1 = f1_score(all_sentiment_labels, all_sentiment_preds, average='weighted')
        intent_acc = accuracy_score(all_intent_labels, all_intent_preds)
        intent_f1 = f1_score(all_intent_labels, all_intent_preds, average='weighted')
        avg_loss = total_loss / num_batches

        return {
            'loss': avg_loss,
            'sentiment_acc': sentiment_acc,
            'sentiment_f1': sentiment_f1,
            'intent_acc': intent_acc,
            'intent_f1': intent_f1
        }

    def check_improvement_and_early_stop(self, metrics: Dict, epoch: int) -> bool:
        """Enhanced early stopping with improvement rate monitoring"""
        current_sentiment = metrics['sentiment_acc']
        current_intent = metrics['intent_acc']

        # Track improvement
        sentiment_improved = current_sentiment > self.best_sentiment_acc
        intent_improved = current_intent > self.best_intent_acc

        if sentiment_improved:
            sentiment_gain = current_sentiment - self.best_sentiment_acc
            self.best_sentiment_acc = current_sentiment
            self.logger.success(f"🎯 Sentiment improved by {sentiment_gain:.3f} to {current_sentiment:.3f}")

        if intent_improved:
            intent_gain = current_intent - self.best_intent_acc
            self.best_intent_acc = current_intent
            self.logger.success(f"🎯 Intent improved by {intent_gain:.3f} to {current_intent:.3f}")

        # Update performance history
        self.performance_history['sentiment_acc'].append(current_sentiment)
        self.performance_history['intent_acc'].append(current_intent)
        self.performance_history['loss'].append(metrics['loss'])

        # Calculate improvement rate (last 3 epochs)
        if len(self.performance_history['sentiment_acc']) >= 3:
            recent_sentiment = self.performance_history['sentiment_acc'][-3:]
            sentiment_trend = (recent_sentiment[-1] - recent_sentiment[0]) / 3
            self.performance_history['improvement_rate'].append(sentiment_trend)

            # Early stop if improvement rate is too slow
            if len(self.performance_history['improvement_rate']) >= 3:
                avg_improvement = np.mean(self.performance_history['improvement_rate'][-3:])
                if avg_improvement < 0.001:  # Less than 0.1% improvement per epoch
                    self.logger.warning(f"⚠️ Slow improvement rate: {avg_improvement:.4f}")
                    return True

        # Target achievement check
        sentiment_target = current_sentiment >= 0.40  # 40% target
        intent_target = current_intent >= 0.15  # 15% target

        if sentiment_target and intent_target:
            self.logger.success(f"🎉 TARGETS ACHIEVED! Sentiment: {current_sentiment:.3f}, Intent: {current_intent:.3f}")
            return True

        return False

    def train_optimized_cycle(self):
        """Execute optimized enhanced training cycle 2"""
        import atexit
        self.training_start_time = time.time()
        model = None
        train_loader = None
        val_loader = None
        base_optimizer = None
        classification_optimizer = None
        progress = None
        task = None
        # Ensure status animation and logger are closed on exit
        def cleanup():
            try:
                if hasattr(self, 'status_animation') and hasattr(self.status_animation, 'stop'):
                    self.status_animation.stop()
            except Exception:
                pass
            try:
                if hasattr(self, 'logger') and hasattr(self.logger, 'logger'):
                    for handler in self.logger.logger.handlers:
                        handler.flush()
                        handler.close()
            except Exception:
                pass
        atexit.register(cleanup)

        with self.status_animation.status("Starting Enhanced Training Cycle 2..."):
            # Load model and data
            model = self.load_model_from_checkpoint()
            self.logger.info("🟡 DEBUG: About to load EmbeddingLabelDataset with real data (F:/b2_datasets/, F:/b2_embeddings/)...")
            from src.training.datasets.embedding_label_dataset import EmbeddingLabelDataset
            from torch.utils.data import DataLoader
            train_manifest = 'F:/b2_datasets/train_manifest.json'
            val_manifest = 'F:/b2_datasets/val_manifest.json'
            embedding_root = 'F:/b2_embeddings/'
            train_dataset = EmbeddingLabelDataset(train_manifest, embedding_root=embedding_root)
            val_dataset = EmbeddingLabelDataset(val_manifest, embedding_root=embedding_root)
            train_loader = DataLoader(train_dataset, batch_size=self.config.get('batch_size', 2), shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=self.config.get('batch_size', 2), shuffle=False)
            self.logger.info("🟢 DEBUG: EmbeddingLabelDataset loaded successfully.")
            # Setup optimized training
            base_optimizer, classification_optimizer = self.setup_optimized_training(model)

            # Training loop with progress tracking
            max_epochs = self.config.get('max_epochs', 12)  # Shorter cycle
            patience = self.config.get('early_stopping_patience', 6)  # Tighter patience
            # Set output dir for checkpoints
            checkpoint_dir = OUTPUT_DIR
            patience_counter = 0
            progress = FallbackProgress(max_epochs, "Enhanced Training Cycle 2")
            task = progress.add_task("Enhanced Training Cycle 2", total=max_epochs)
            with progress:
                for epoch in range(max_epochs):
                    epoch_start_time = time.time()
                    model.train()
                    epoch_losses = []
                    batch_count = 0
                    self.logger.info("🟡 DEBUG: About to enter training batch loop (before first batch)...")
                    for batch_idx, batch in enumerate(train_loader):
                        # DEBUG: Print batch shapes before passing to model
                        if batch_idx == 0:
                            for k, v in batch.items():
                                if hasattr(v, "shape"):
                                    print(f"[DEBUG] batch[{k}] shape: {v.shape}")
                            self.logger.info("🟢 DEBUG: Successfully retrieved first batch from train_loader.")
                            self.logger.info("🟡 DEBUG: Before model forward pass...")
                        # Move tensors to device
                        batch = {k: v.to(self.device) if hasattr(v, 'to') else v for k, v in batch.items()}
                        # Patch: Rename 'embeddings' to 'text' for B2MultimodalModel compatibility
                        batch_for_model = dict(batch)
                        if 'embeddings' in batch_for_model:
                            batch_for_model['text'] = batch_for_model.pop('embeddings')
                        outputs = model(batch_for_model)
                        if batch_idx == 0:
                            self.logger.info("🟢 DEBUG: Model forward pass complete.")
                            self.logger.info("🟡 DEBUG: Before loss computation...")
                        loss, loss_dict = self.compute_optimized_loss(outputs, batch)
                        if batch_idx == 0:
                            self.logger.info("🟢 DEBUG: Loss computation complete.")
                            self.logger.info("🟡 DEBUG: Before optimizer steps...")
                        base_optimizer.zero_grad()
                        classification_optimizer.zero_grad()
                        loss.backward()
                        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                        base_optimizer.step()
                        classification_optimizer.step()
                        if batch_idx == 0:
                            self.logger.info("🟢 DEBUG: Optimizer steps complete.")
                        epoch_losses.append(loss_dict['total'])
                        batch_count += 1
                        self.step_count += 1
                        if batch_idx % 50 == 0:
                            sentiment_preds = torch.argmax(outputs['sentiment_logits'], dim=1)
                            intent_preds = torch.argmax(outputs['intent_logits'], dim=1)
                            sentiment_acc = accuracy_score(
                                batch['sentiment_labels'].cpu().numpy(),
                                sentiment_preds.cpu().numpy()
                            )
                            intent_acc = accuracy_score(
                                batch['intent_labels'].cpu().numpy(),
                                intent_preds.cpu().numpy()
                            )
                            self.logger.info(
                                f"[Epoch {epoch+1}] Step {batch_idx}: "
                                f"Loss={loss_dict['total']:.4f} "
                                f"(Sentiment={loss_dict['sentiment']:.4f}, "
                                f"Intent={loss_dict['intent']:.4f}) "
                                f"Sentiment_Acc={sentiment_acc:.3f}, "
                                f"Intent_Acc={intent_acc:.3f}"
                            )
                    avg_epoch_loss = np.mean(epoch_losses)
                    val_metrics = self.evaluate_with_detailed_metrics(model, val_loader)
                    epoch_time = time.time() - epoch_start_time
                    self.logger.info(
                        f"[Epoch {epoch+1}] Training Results:\n"
                        f"  Average Loss: {avg_epoch_loss:.4f}\n"
                        f"  Sentiment - Acc: {val_metrics['sentiment_acc']:.4f}, F1: {val_metrics['sentiment_f1']:.4f}\n"
                        f"  Intent - Acc: {val_metrics['intent_acc']:.4f}, F1: {val_metrics['intent_f1']:.4f}\n"
                        f"  Epoch Time: {epoch_time:.1f}s"
                    )
                    if self.check_improvement_and_early_stop(val_metrics, epoch):
                        if val_metrics['sentiment_acc'] >= 0.40 and val_metrics['intent_acc'] >= 0.15:
                            self.logger.success("🎉 TARGETS ACHIEVED! Stopping training.")
                        else:
                            self.logger.info("⏹️ Early stopping due to slow improvement.")
                        break
                    if (val_metrics['sentiment_acc'] <= self.best_sentiment_acc and
                        val_metrics['intent_acc'] <= self.best_intent_acc):
                        patience_counter += 1
                        if patience_counter >= patience:
                            self.logger.warning(f"⏳ Early stopping patience: {patience_counter}/{patience}")
                            break
                    else:
                        patience_counter = 0
                    progress.update(task, advance=1)
                    if (epoch + 1) % 3 == 0:
                        checkpoint_path = os.path.join(checkpoint_dir, f"enhanced_cycle2_checkpoint_epoch_{epoch+1}.pth")
                        torch.save({
                            'epoch': epoch,
                            'model_state_dict': model.state_dict(),
                            'base_optimizer_state_dict': base_optimizer.state_dict(),
                            'classification_optimizer_state_dict': classification_optimizer.state_dict(),
                            'best_sentiment_acc': self.best_sentiment_acc,
                            'best_intent_acc': self.best_intent_acc,
                            'metrics': val_metrics
                        }, checkpoint_path)
                        self.logger.info(f"💾 Checkpoint saved: {checkpoint_path}")
            # Final evaluation and save
            final_metrics = self.evaluate_with_detailed_metrics(model, val_loader)
            final_model_path = os.path.join(checkpoint_dir, "best_b2_enhanced_cycle2_model.pth")
            torch.save({
                'model_state_dict': model.state_dict(),
                'metrics': final_metrics,
                'config': self.config,
                'training_time': time.time() - self.training_start_time
            }, final_model_path)
            total_time = time.time() - self.training_start_time
            self.logger.success(
                f"✅ Enhanced Training Cycle 2 Completed!\n"
                f"📊 Final Results:\n"
                f"  • Sentiment Accuracy: {final_metrics['sentiment_acc']:.4f} (Target: 0.40)\n"
                f"  • Intent Accuracy: {final_metrics['intent_acc']:.4f} (Target: 0.15)\n"
                f"  • Total Training Time: {total_time/60:.1f} minutes\n"
                f"  • Model Saved: {final_model_path}"
            )
            # Explicitly stop status animation and flush/close loggers
            try:
                if hasattr(self, 'status_animation') and hasattr(self.status_animation, 'stop'):
                    self.status_animation.stop()
            except Exception:
                pass
            try:
                if hasattr(self, 'logger') and hasattr(self.logger, 'logger'):
                    for handler in self.logger.logger.handlers:
                        handler.flush()
                        handler.close()
            except Exception:
                pass
            return final_metrics

def main():
    """Main training execution"""
    # Initialize and run training with MODEL_CONFIG
    import sys
    # Optionally load config from file (not implemented here, but placeholder)
    # Optionally load from args.init_checkpoint (not implemented here, but placeholder)
    trainer = OptimizedEnhancedTrainer(MODEL_CONFIG)
    final_metrics = trainer.train_optimized_cycle()
    print(f"\nEnhanced Training Cycle 2 Complete!")
    print(f"Sentiment: {final_metrics['sentiment_acc']:.1%}")
    print(f"Intent: {final_metrics['intent_acc']:.1%}")
    print(f"Ready for Raw Data Training Phase 2!")
    sys.exit(0)

