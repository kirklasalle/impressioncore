#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #command_line #cuda #multimodal #python #source_code #src/training/classification_debugging_solution.py #training #transformer
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** Kirk LaSalle
# Tags:** #command_line #cuda #multimodal #python #source_code #src\\training\\classification_debugging_solution.py #training #transformer
# Category:** Training System
# Status:** Active

"""
ImpressionCore B2 Classification Task Debugging Solution
========================================================

This script provides a comprehensive solution to fix the 0% accuracy on
sentiment and intent classification tasks by addressing the root causes:

1. **Shared Output Head Issue**: Currently all tasks use the same 'conversation' head
2. **Incorrect Task Head Architecture**: No dedicated classification heads
3. **Loss Weight Imbalance**: Classification tasks are under-weighted
4. **Data Pipeline Issues**: Potential label encoding problems

Created: 2025-07-04
Author: Kirk LaSalle & GitHub Copilot
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

class ImprovedB2MultimodalModel(nn.Module):
    """
    Enhanced B2 Model with dedicated classification heads
    """
    def __init__(self, base_model, config):
        super().__init__()
        self.base_model = base_model
        self.config = config

        # Dedicated classification heads
        self.sentiment_head = nn.Sequential(
            nn.Linear(config['embed_dim'], 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, config['num_sentiment_classes'])
        )

        self.intent_head = nn.Sequential(
            nn.Linear(config['embed_dim'], 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, config['num_intent_classes'])
        )

        self.quality_head = nn.Sequential(
            nn.Linear(config['embed_dim'], 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 1)
        )

    def forward(self, inputs, output_modality='conversation', use_precomputed_embeddings=True):
        """Enhanced forward pass with proper task-specific outputs"""

        # Get base transformer output
        if hasattr(self.base_model, 'unified_embedding'):
            # Use the base model's forward method but intercept transformer output
            if use_precomputed_embeddings:
                text_emb = inputs.get('text')
                vision_emb = inputs.get('vision')
                audio_emb = inputs.get('audio')
                video_emb = inputs.get('video')

                # Ensure embeddings have the right shape
                if text_emb is not None and text_emb.dim() == 2:
                    text_emb = text_emb.unsqueeze(1)
                if vision_emb is not None and vision_emb.dim() == 2:
                    vision_emb = vision_emb.unsqueeze(1)
                if audio_emb is not None and audio_emb.dim() == 2:
                    audio_emb = audio_emb.unsqueeze(1)
                if video_emb is not None and video_emb.dim() == 2:
                    video_emb = video_emb.unsqueeze(1)

                emb_inputs = {
                    'text_emb': text_emb,
                    'vision': vision_emb,
                    'audio': audio_emb,
                    'video': video_emb,
                    'modality_type': inputs.get('modality_type', None)
                }
                unified_emb = self.base_model.unified_embedding(emb_inputs)
            else:
                unified_emb = self.base_model.unified_embedding(inputs)

            # Get transformer output
            transformer_output = self.base_model.transformer(unified_emb)
        else:
            # Fallback to base model forward
            transformer_output = self.base_model.forward(inputs, output_modality, use_precomputed_embeddings)

        # Task-specific output heads
        if output_modality == 'conversation':
            return self.base_model.conversation_head(transformer_output)
        elif output_modality == 'sentiment':
            # Use mean pooling for classification
            pooled_output = transformer_output.mean(dim=1)  # (B, seq_len, embed_dim) -> (B, embed_dim)
            return self.sentiment_head(pooled_output)
        elif output_modality == 'intent':
            # Use mean pooling for classification
            pooled_output = transformer_output.mean(dim=1)  # (B, seq_len, embed_dim) -> (B, embed_dim)
            return self.intent_head(pooled_output)
        elif output_modality == 'quality':
            # Use mean pooling for regression
            pooled_output = transformer_output.mean(dim=1)  # (B, seq_len, embed_dim) -> (B, embed_dim)
            return self.quality_head(pooled_output)
        elif output_modality == 'vision':
            return self.base_model.vision_head(transformer_output)
        elif output_modality == 'audio':
            return self.base_model.audio_head(transformer_output)
        else:
            raise ValueError(f"Unknown output_modality: {output_modality}")

class EnhancedTrainer:
    """Enhanced trainer with improved loss balancing and debugging"""

    def __init__(self, model, config, device='cuda'):
        self.model = model
        self.config = config
        self.device = device

        # Improved loss weights (give more importance to classification)
        self.loss_weights = {
            'text': 0.4,        # Reduced from 1.0
            'sentiment': 1.0,   # Increased from 0.2
            'intent': 1.0,      # Increased from 0.2
            'quality': 0.2      # Increased from 0.1
        }

        # Separate optimizers for different task heads
        self.setup_optimizers()

        # Label debugging info
        self.label_stats = {
            'sentiment': {'seen_labels': set(), 'counts': {}},
            'intent': {'seen_labels': set(), 'counts': {}}
        }

    def setup_optimizers(self):
        """Setup separate optimizers with different learning rates"""
        # Base model parameters (lower LR for stability)
        base_params = []
        if hasattr(self.model, 'base_model'):
            base_params = list(self.model.base_model.parameters())

        # Classification head parameters (higher LR for faster learning)
        classification_params = []
        if hasattr(self.model, 'sentiment_head'):
            classification_params.extend(list(self.model.sentiment_head.parameters()))
        if hasattr(self.model, 'intent_head'):
            classification_params.extend(list(self.model.intent_head.parameters()))
        if hasattr(self.model, 'quality_head'):
            classification_params.extend(list(self.model.quality_head.parameters()))

        # Create optimizers
        self.base_optimizer = torch.optim.AdamW(base_params, lr=1e-4, weight_decay=0.01)
        self.classification_optimizer = torch.optim.AdamW(classification_params, lr=5e-4, weight_decay=0.01)

    def debug_batch_data(self, batch, step_idx=0):
        """Debug batch data to identify issues"""
        debug_info = {}

        # Check shapes
        for key, value in batch.items():
            if isinstance(value, torch.Tensor):
                debug_info[f"{key}_shape"] = value.shape
                debug_info[f"{key}_dtype"] = value.dtype
                if key in ['sentiment', 'intent']:
                    unique_vals = torch.unique(value).tolist()
                    debug_info[f"{key}_unique_values"] = unique_vals
                    debug_info[f"{key}_min_max"] = (value.min().item(), value.max().item())

                    # Update label statistics
                    for val in unique_vals:
                        self.label_stats[key]['seen_labels'].add(val)
                        self.label_stats[key]['counts'][val] = self.label_stats[key]['counts'].get(val, 0) + (value == val).sum().item()

        if step_idx == 0:  # Print debug info for first batch
            print("=== BATCH DEBUG INFO ===")
            for key, value in debug_info.items():
                print(f"{key}: {value}")
            print("=== LABEL STATISTICS ===")
            for task in ['sentiment', 'intent']:
                print(f"{task.upper()}:")
                print(f"  Seen labels: {sorted(self.label_stats[task]['seen_labels'])}")
                print(f"  Label counts: {self.label_stats[task]['counts']}")
                print(f"  Expected classes: {self.config.get(f'num_{task}_classes', 'Unknown')}")

        return debug_info

    def compute_enhanced_loss(self, outputs, batch, debug=False):
        """Enhanced loss computation with better debugging"""
        losses = {}

        # Text generation loss
        text_logits = outputs['text']
        if text_logits.dim() == 3:
            text_logits = text_logits[:, 0, :]  # Take first token for classification

        label_targets = batch['labels'].squeeze() if batch['labels'].dim() > 1 else batch['labels']
        losses['text'] = F.cross_entropy(text_logits, label_targets.to(self.device))

        # Sentiment classification loss
        sentiment_logits = outputs['sentiment']
        sentiment_targets = batch['sentiment'].to(self.device)

        if debug:
            print(f"[DEBUG] Sentiment logits shape: {sentiment_logits.shape}")
            print(f"[DEBUG] Sentiment targets shape: {sentiment_targets.shape}")
            print(f"[DEBUG] Sentiment targets range: {sentiment_targets.min()}-{sentiment_targets.max()}")
            print(f"[DEBUG] Expected sentiment classes: {self.config.get('num_sentiment_classes', 'Unknown')}")

        # Validate sentiment targets are in valid range
        max_sentiment_class = self.config.get('num_sentiment_classes', 3) - 1
        if sentiment_targets.max() > max_sentiment_class:
            print(f"[WARNING] Sentiment target {sentiment_targets.max()} exceeds max class {max_sentiment_class}")
            sentiment_targets = torch.clamp(sentiment_targets, 0, max_sentiment_class)

        losses['sentiment'] = F.cross_entropy(sentiment_logits, sentiment_targets)

        # Intent classification loss
        intent_logits = outputs['intent']
        intent_targets = batch['intent'].to(self.device)

        if debug:
            print(f"[DEBUG] Intent logits shape: {intent_logits.shape}")
            print(f"[DEBUG] Intent targets shape: {intent_targets.shape}")
            print(f"[DEBUG] Intent targets range: {intent_targets.min()}-{intent_targets.max()}")
            print(f"[DEBUG] Expected intent classes: {self.config.get('num_intent_classes', 'Unknown')}")

        # Validate intent targets are in valid range
        max_intent_class = self.config.get('num_intent_classes', 10) - 1
        if intent_targets.max() > max_intent_class:
            print(f"[WARNING] Intent target {intent_targets.max()} exceeds max class {max_intent_class}")
            intent_targets = torch.clamp(intent_targets, 0, max_intent_class)

        losses['intent'] = F.cross_entropy(intent_logits, intent_targets)

        # Quality regression loss
        quality_pred = outputs['quality']
        quality_target = batch['quality'].float().to(self.device)

        if quality_pred.shape != quality_target.shape:
            quality_pred = quality_pred.view_as(quality_target)

        losses['quality'] = F.mse_loss(quality_pred, quality_target)

        # Combined loss with improved weights
        total_loss = (
            self.loss_weights['text'] * losses['text'] +
            self.loss_weights['sentiment'] * losses['sentiment'] +
            self.loss_weights['intent'] * losses['intent'] +
            self.loss_weights['quality'] * losses['quality']
        )

        return total_loss, losses

    def train_step(self, batch, step_idx=0):
        """Enhanced training step with proper task separation"""

        # Debug batch data
        if step_idx < 3:  # Debug first few batches
            self.debug_batch_data(batch, step_idx)

        # Prepare inputs
        inputs = {
            'text': batch['text'].to(self.device),
            'vision': batch['vision'].to(self.device),
            'audio': batch['audio'].to(self.device),
            'video': batch['video'].to(self.device)
        }

        # Forward pass for each task with separate outputs
        text_outputs = self.model(inputs, output_modality='conversation', use_precomputed_embeddings=True)
        sentiment_outputs = self.model(inputs, output_modality='sentiment', use_precomputed_embeddings=True)
        intent_outputs = self.model(inputs, output_modality='intent', use_precomputed_embeddings=True)
        quality_outputs = self.model(inputs, output_modality='quality', use_precomputed_embeddings=True)

        outputs = {
            'text': text_outputs,
            'sentiment': sentiment_outputs,
            'intent': intent_outputs,
            'quality': quality_outputs
        }

        # Compute enhanced loss
        total_loss, individual_losses = self.compute_enhanced_loss(
            outputs, batch, debug=(step_idx < 3)
        )

        # Backward pass
        self.base_optimizer.zero_grad()
        self.classification_optimizer.zero_grad()

        total_loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

        self.base_optimizer.step()
        self.classification_optimizer.step()

        # Compute metrics
        metrics = self.compute_step_metrics(outputs, batch)

        return total_loss.item(), individual_losses, metrics

    def compute_step_metrics(self, outputs, batch):
        """Compute detailed metrics for monitoring"""
        metrics = {}

        # Sentiment metrics
        sentiment_pred = outputs['sentiment'].argmax(dim=-1).cpu().numpy()
        sentiment_true = batch['sentiment'].cpu().numpy()
        metrics['sentiment_acc'] = accuracy_score(sentiment_true, sentiment_pred)

        # Intent metrics
        intent_pred = outputs['intent'].argmax(dim=-1).cpu().numpy()
        intent_true = batch['intent'].cpu().numpy()
        metrics['intent_acc'] = accuracy_score(intent_true, intent_pred)

        # Quality metrics
        quality_pred = outputs['quality'].cpu().numpy()
        quality_true = batch['quality'].cpu().numpy()
        metrics['quality_mse'] = np.mean((quality_pred - quality_true) ** 2)

        return metrics

def create_enhanced_model_wrapper(original_model, config):
    """Create enhanced model wrapper with dedicated classification heads"""
    enhanced_model = ImprovedB2MultimodalModel(original_model, config)
    return enhanced_model

def run_classification_debugging(model, dataloader, config, device='cuda'):
    """
    Run comprehensive classification debugging
    """
    print("🔍 STARTING CLASSIFICATION DEBUGGING SESSION")
    print("=" * 60)

    # Create enhanced model
    enhanced_model = create_enhanced_model_wrapper(model, config)
    enhanced_model = enhanced_model.to(device)

    # Create enhanced trainer
    trainer = EnhancedTrainer(enhanced_model, config, device)

    # Run debugging session
    enhanced_model.train()

    debug_results = {
        'sentiment_accuracies': [],
        'intent_accuracies': [],
        'loss_history': [],
        'label_issues': []
    }

    for step_idx, batch in enumerate(dataloader):
        if step_idx >= 10:  # Debug first 10 batches
            break

        try:
            total_loss, individual_losses, metrics = trainer.train_step(batch, step_idx)

            # Record results
            debug_results['sentiment_accuracies'].append(metrics['sentiment_acc'])
            debug_results['intent_accuracies'].append(metrics['intent_acc'])
            debug_results['loss_history'].append({
                'total': total_loss,
                'sentiment': individual_losses['sentiment'].item(),
                'intent': individual_losses['intent'].item()
            })

            print(f"Step {step_idx}: Loss={total_loss:.4f}, "
                  f"Sentiment_Acc={metrics['sentiment_acc']:.3f}, "
                  f"Intent_Acc={metrics['intent_acc']:.3f}")

        except Exception as e:
            print(f"❌ Error in step {step_idx}: {e}")
            debug_results['label_issues'].append(f"Step {step_idx}: {e}")

    # Print final debugging report
    print("\n📊 DEBUGGING RESULTS SUMMARY")
    print("=" * 60)
    print(f"Sentiment accuracy range: {min(debug_results['sentiment_accuracies']):.3f} - {max(debug_results['sentiment_accuracies']):.3f}")
    print(f"Intent accuracy range: {min(debug_results['intent_accuracies']):.3f} - {max(debug_results['intent_accuracies']):.3f}")
    print(f"Label statistics:")
    for task in ['sentiment', 'intent']:
        stats = trainer.label_stats[task]
        print(f"  {task.upper()}: {len(stats['seen_labels'])} unique labels, range: {min(stats['seen_labels']) if stats['seen_labels'] else 'None'}-{max(stats['seen_labels']) if stats['seen_labels'] else 'None'}")

    if debug_results['label_issues']:
        print(f"⚠️ Found {len(debug_results['label_issues'])} label issues:")
        for issue in debug_results['label_issues']:
            print(f"  - {issue}")

    return enhanced_model, debug_results

# Usage example for integration into your training script
if __name__ == "__main__":
    # This would be called from your main training script
    print("Classification debugging solution ready!")
    print("To use this:")
    print("1. Import this module in your train_b2.py")
    print("2. Replace your model with create_enhanced_model_wrapper()")
    print("3. Use EnhancedTrainer instead of your current training loop")
    print("4. Run run_classification_debugging() to identify issues")
