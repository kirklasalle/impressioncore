#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #attention_mechanism #command_line #python #source_code #src/dev_tools/prepare_b2_phase2.py #tokenization #training #transformer
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #api #attention_mechanism #command_line #python #source_code #src/dev_tools/prepare_b2_phase2.py #tokenization #training #transformer
# Category:** Development Tools
# Status:** Active

"""
ImpressionCore B2 Phase 2 Preparation
Prepares the B2 teacher model outputs for student distillation
"""

import json
import logging
import os
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import h5py
import numpy as np
import torch
import torch.nn as nn
from transformers import GPT2Tokenizer


# Setup logging
def setup_logging():
    """Setup logging for B2 Phase 2 preparation"""
    log_dir = Path("logs/b2_phase2")
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"b2_phase2_prep_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] B2-P2 - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Matching B2 model configuration
@dataclass
class B2Config:
    model_dim: int = 256
    hidden_dim: int = 512
    num_heads: int = 4
    num_layers: int = 3
    num_intent_classes: int = 10
    num_sentiment_classes: int = 3
    num_complexity_classes: int = 3
    vocab_size: int = 50257
    max_length: int = 128
    batch_size: int = 1

class B2FixedModel(nn.Module):
    """B2 Fixed Model - Teacher for distillation"""

    def __init__(self, config: B2Config, vocab_size: int):
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

        # Classification heads
        self.language_head = nn.Linear(config.model_dim, vocab_size)
        self.intent_classifier = nn.Linear(config.model_dim, config.num_intent_classes)
        self.sentiment_classifier = nn.Linear(config.model_dim, config.num_sentiment_classes)
        self.complexity_classifier = nn.Linear(config.model_dim, config.num_complexity_classes)
        self.quality_regressor = nn.Sequential(
            nn.Linear(config.model_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(config.hidden_dim // 2, 1),
            nn.Sigmoid()
        )

        # Layer normalization
        self.layer_norm = nn.LayerNorm(config.model_dim)

    def forward(self, input_ids, attention_mask=None, target_ids=None, target_attention_mask=None,
                intent_labels=None, sentiment_labels=None, complexity_labels=None, quality_scores=None):

        _, seq_len = input_ids.shape

        # Token embeddings with positional encoding
        embeddings = self.embeddings(input_ids)
        if seq_len <= 512:
            embeddings = embeddings + self.positional_encoding[:, :seq_len, :]

        # Transformer encoding
        transformer_output = self.transformer(embeddings, src_key_padding_mask=~attention_mask.bool() if attention_mask is not None else None)

        # Layer normalization
        normalized_output = self.layer_norm(transformer_output)

        # Pool for classification (mean pooling)
        pooled_output = normalized_output.mean(dim=1)

        # Classification outputs
        intent_logits = self.intent_classifier(pooled_output)
        sentiment_logits = self.sentiment_classifier(pooled_output)
        complexity_logits = self.complexity_classifier(pooled_output)
        quality_output = self.quality_regressor(pooled_output)

        # Language modeling
        lm_logits = self.language_head(normalized_output)

        return {
            'intent_logits': intent_logits,
            'sentiment_logits': sentiment_logits,
            'complexity_logits': complexity_logits,
            'quality_output': quality_output,
            'lm_logits': lm_logits,
            'hidden_states': normalized_output,
            'pooled_output': pooled_output
        }

class DistillationDataCapture:
    """Captures teacher model outputs for student distillation"""

    def __init__(self, config: B2Config, output_dir: str = "src/training/b2_phase2_prep"):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data storage
        self.teacher_outputs = []
        self.metadata = []

        logger.info(f"Distillation capture initialized: {self.output_dir}")

    def capture_teacher_output(self, input_data: dict, teacher_outputs: dict, sample_id: str):
        """Capture teacher model outputs for distillation"""

        # Extract key outputs for distillation
        capture_data = {
            'sample_id': sample_id,
            'input_ids': input_data['input_ids'].cpu().numpy(),
            'attention_mask': input_data['attention_mask'].cpu().numpy(),
            'intent_logits': teacher_outputs['intent_logits'].detach().cpu().numpy(),
            'sentiment_logits': teacher_outputs['sentiment_logits'].detach().cpu().numpy(),
            'complexity_logits': teacher_outputs['complexity_logits'].detach().cpu().numpy(),
            'quality_output': teacher_outputs['quality_output'].detach().cpu().numpy(),
            'lm_logits': teacher_outputs['lm_logits'].detach().cpu().numpy(),
            'hidden_states': teacher_outputs['hidden_states'].detach().cpu().numpy(),
            'pooled_output': teacher_outputs['pooled_output'].detach().cpu().numpy()
        }

        self.teacher_outputs.append(capture_data)

        # Metadata
        meta = {
            'sample_id': sample_id,
            'sequence_length': input_data['input_ids'].shape[1],
            'timestamp': datetime.now().isoformat(),
            'quality_score': float(teacher_outputs['quality_output'].detach().cpu().item())
        }
        self.metadata.append(meta)

        logger.info(f"Captured teacher output for sample {sample_id} (quality: {meta['quality_score']:.3f})")

    def save_distillation_dataset(self, split: str = "train"):
        """Save captured outputs as distillation dataset"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save as HDF5 for efficient loading
        h5_file = self.output_dir / f"b2_teacher_outputs_{split}_{timestamp}.h5"

        with h5py.File(h5_file, 'w') as f:
            for i, data in enumerate(self.teacher_outputs):
                grp = f.create_group(f"sample_{i}")
                for key, value in data.items():
                    if key != 'sample_id':
                        grp.create_dataset(key, data=value, compression='gzip')
                    else:
                        grp.attrs['sample_id'] = data['sample_id']

        # Save metadata as JSON
        json_file = self.output_dir / f"b2_teacher_metadata_{split}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                'metadata': self.metadata,
                'config': {
                    'model_dim': self.config.model_dim,
                    'num_samples': len(self.teacher_outputs),
                    'avg_quality': np.mean([m['quality_score'] for m in self.metadata])
                }
            }, f, indent=2)

        logger.info("Saved distillation dataset:")
        logger.info(f"  HDF5: {h5_file}")
        logger.info(f"  JSON: {json_file}")
        logger.info(f"  Samples: {len(self.teacher_outputs)}")
        logger.info(f"  Avg Quality: {np.mean([m['quality_score'] for m in self.metadata]):.3f}")

        return str(h5_file), str(json_file)

def generate_distillation_prompts():
    """Generate diverse prompts for teacher model capture"""

    prompts = [
        # Greetings and basic interaction
        "Hello! How are you today?",
        "Good morning! What can you help me with?",
        "Hi there! I hope you're doing well.",
        "Hey! Can you assist me?",
        "Good afternoon! I need some help.",

        # Questions and information seeking
        "What is the weather like today?",
        "Can you explain how machine learning works?",
        "What are the benefits of renewable energy?",
        "How do computers process information?",
        "What is the capital of France?",

        # Programming and technical
        "Can you help me with Python programming?",
        "How do I create a function in JavaScript?",
        "What is object-oriented programming?",
        "Explain the difference between lists and tuples.",
        "How do databases work?",

        # Creative and problem-solving
        "Write a short poem about nature.",
        "Help me brainstorm ideas for a project.",
        "What are some creative ways to organize tasks?",
        "Can you suggest a recipe for dinner?",
        "How can I improve my productivity?",

        # Emotional and supportive
        "I'm feeling stressed about work.",
        "Can you give me some motivation?",
        "I'm having trouble sleeping.",
        "I feel overwhelmed with tasks.",
        "I need encouragement today.",

        # Complex and analytical
        "Explain quantum computing in simple terms.",
        "What are the implications of artificial intelligence?",
        "How does the stock market work?",
        "Discuss the impact of climate change.",
        "What is the future of renewable energy?",

        # Conversational follow-ups
        "That's interesting, tell me more.",
        "Can you give me an example?",
        "I don't understand, can you clarify?",
        "What do you think about that?",
        "How does that work exactly?"
    ]

    logger.info(f"Generated {len(prompts)} distillation prompts")
    return prompts

def load_best_teacher_model():
    """Load the best B2 teacher model for distillation"""

    config = B2Config()

    # Load tokenizer
    logger.info("Loading B2 tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token

    # Create model
    logger.info("Creating B2 teacher model...")
    model = B2FixedModel(config, config.vocab_size)

    # Load best checkpoint (epoch 1 had best quality: 5.1/10)
    checkpoint_path = "checkpoints/b2_fixed/b2_fixed_epoch_1.pth"

    if not os.path.exists(checkpoint_path):
        logger.error(f"Teacher checkpoint not found: {checkpoint_path}")
        return None, None, None

    logger.info(f"Loading teacher checkpoint: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()  # Set to evaluation mode

    logger.info("Teacher model loaded successfully!")
    logger.info(f"Training epoch: {checkpoint.get('epoch', 'Unknown')}")
    logger.info(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    return model, tokenizer, config

def run_teacher_capture():
    """Run teacher model capture for distillation preparation"""

    logger.info("Starting B2 Phase 2 Teacher Capture")

    # Load teacher model
    teacher_model, tokenizer, config = load_best_teacher_model()
    if teacher_model is None:
        logger.error("Failed to load teacher model!")
        return

    # Initialize distillation capture
    capture = DistillationDataCapture(config)

    # Generate prompts
    prompts = generate_distillation_prompts()

    # Capture teacher outputs
    logger.info(f"Capturing teacher outputs for {len(prompts)} prompts...")

    with torch.no_grad():
        for i, prompt in enumerate(prompts):
            try:
                # Tokenize prompt
                inputs = tokenizer(
                    prompt,
                    return_tensors='pt',
                    padding=True,
                    truncation=True,
                    max_length=config.max_length
                )

                # Get teacher outputs
                outputs = teacher_model(inputs['input_ids'], inputs['attention_mask'])

                # Capture for distillation
                sample_id = f"prompt_{i:03d}"
                capture.capture_teacher_output(inputs, outputs, sample_id)

                if (i + 1) % 10 == 0:
                    logger.info(f"Captured {i + 1}/{len(prompts)} samples...")

            except Exception as e:
                logger.error(f"Error capturing sample {i}: {e}")
                continue

    # Save distillation dataset
    logger.info("Saving distillation dataset...")
    h5_file, json_file = capture.save_distillation_dataset("train")

    logger.info("B2 Phase 2 Teacher Capture Complete!")
    logger.info(f"Ready for student distillation with {len(capture.teacher_outputs)} samples")

    return h5_file, json_file

def main():
    """Main preparation function"""

    logger.info("ImpressionCore B2 Phase 2 Preparation Starting...")

    try:
        # Run teacher capture
        h5_file, json_file = run_teacher_capture()

        if h5_file and json_file:
            logger.info("Phase 2 preparation successful!")
            logger.info("Ready to proceed with student distillation training.")
        else:
            logger.error("Phase 2 preparation failed!")

    except Exception as e:
        logger.error(f"Phase 2 preparation error: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
