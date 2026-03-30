#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #inference #python #source_code #src/tests/test_b2_fixed_inference.py #testing #tokenization #training #transformer
**Category:** Testing Framework
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #inference #python #source_code #src\\tests\\test_b2_fixed_inference.py #testing #tokenization #training #transformer
# Category:** Testing Framework
# Status:** Active

"""
Test ImpressionCore B2 Fixed Model Inference
Validates that the trained B2 model can generate responses
"""

import logging
import os
import sys

import torch
import torch.nn as nn
from transformers import GPT2Tokenizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] B2-Test - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class B2FixedModel(nn.Module):
    """B2 Fixed Model for testing inference - matches training architecture"""

    def __init__(self, config, vocab_size):
        super().__init__()
        self.config = config

        # Embedding layers (match training model)
        self.embeddings = nn.Embedding(vocab_size, config.model_dim)
        self.positional_encoding = nn.Parameter(torch.randn(1, 512, config.model_dim))

        # Transformer layers (match training model)
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

        # Fixed classification heads with correct dimensions (match training model)
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

        # Layer normalization (match training model)
        self.layer_norm = nn.LayerNorm(config.model_dim)

    def forward(self, input_ids, attention_mask=None, target_ids=None, target_attention_mask=None,
                intent_labels=None, sentiment_labels=None, complexity_labels=None, quality_scores=None):

        batch_size, seq_len = input_ids.shape

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
            'lm_logits': lm_logits
        }

def load_b2_model():
    """Load the trained B2 model"""

    # Configuration (match B2 training config exactly)
    class Config:
        model_dim = 256
        hidden_dim = 512
        num_heads = 4
        num_layers = 3
        num_intent_classes = 10
        num_sentiment_classes = 3
        num_complexity_classes = 3
        vocab_size = 50257  # GPT2 vocab size
        max_length = 128

    config = Config()

    # Load tokenizer
    logging.info("Loading tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token

    # Create model
    logging.info("Creating B2 model...")
    model = B2FixedModel(config, config.vocab_size)

    # Load best checkpoint
    checkpoint_path = "checkpoints/b2_fixed/b2_fixed_epoch_1.pth"  # Best was epoch 1 (5.1/10)

    if not os.path.exists(checkpoint_path):
        logging.error(f"Checkpoint not found: {checkpoint_path}")
        return None, None

    logging.info(f"Loading checkpoint: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])

    logging.info("Model loaded successfully!")
    logging.info(f"Training epoch: {checkpoint.get('epoch', 'Unknown')}")
    logging.info(f"Best quality: {checkpoint.get('best_quality', 'Unknown')}")

    return model, tokenizer

def _run_inference(model, tokenizer, test_prompts):
    """Test inference on sample prompts"""

    model.eval()

    logging.info("Testing B2 inference...")

    for i, prompt in enumerate(test_prompts):
        logging.info(f"\n--- Test {i+1}: {prompt} ---")

        # Tokenize
        inputs = tokenizer(
            prompt,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=64
        )

        with torch.no_grad():
            outputs = model(inputs['input_ids'], inputs['attention_mask'])

            # Get predictions
            intent_pred = torch.argmax(outputs['intent_logits'], dim=-1).item()
            sentiment_pred = torch.argmax(outputs['sentiment_logits'], dim=-1).item()
            complexity_pred = torch.argmax(outputs['complexity_logits'], dim=-1).item()
            quality_pred = outputs['quality_output'].item()

            logging.info(f"Intent: {intent_pred}/9")
            logging.info(f"Sentiment: {sentiment_pred}/2 ({'Negative' if sentiment_pred == 0 else 'Neutral' if sentiment_pred == 1 else 'Positive'})")
            logging.info(f"Complexity: {complexity_pred}/2 ({'Simple' if complexity_pred == 0 else 'Medium' if complexity_pred == 1 else 'Complex'})")
            logging.info(f"Quality: {quality_pred:.2f}/10")

            # Generate next tokens
            lm_logits = outputs['lm_logits'][0, -1, :]  # Last token logits
            next_token_probs = torch.softmax(lm_logits, dim=-1)
            top_tokens = torch.topk(next_token_probs, 3)

            logging.info("Top next tokens:")
            for j, (prob, token_id) in enumerate(zip(top_tokens.values, top_tokens.indices)):
                token = tokenizer.decode(token_id.item())
                logging.info(f"  {j+1}. '{token}' ({prob.item():.3f})")

def main():
    """Main test function"""

    logging.info("Starting B2 Fixed Model Inference Test")

    # Load model
    model, tokenizer = load_b2_model()
    if model is None:
        logging.error("Failed to load model!")
        return

    # Test prompts
    test_prompts = [
        "Hello, how are you?",
        "What is the weather like today?",
        "Can you help me with Python programming?",
        "I'm feeling sad today.",
        "Explain quantum computing.",
    ]

    # Run inference tests
    _run_inference(model, tokenizer, test_prompts)

    logging.info("\nB2 Fixed Model Inference Test Complete!")

if __name__ == "__main__":
    main()
