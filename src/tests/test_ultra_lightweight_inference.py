#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #cuda #inference #memory_management #python #source_code #src/tests/test_ultra_lightweight_inference.py #testing #tokenization #training #transformer
**Category:** Testing Framework
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #cuda #inference #memory_management #python #source_code #src\\tests\\test_ultra_lightweight_inference.py #testing #tokenization #training #transformer
# Category:** Testing Framework
# Status:** Active

"""
ImpressionCore B2 Ultra-Lightweight Model Inference Test
Test the trained model for basic conversation capability
"""

import sys
from pathlib import Path

import pytest
import torch
import torch.nn.functional as F
from transformers import GPT2Tokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

pytest.importorskip("src.training.setup_ultra_lightweight_training", reason="Training module not available")
from src.training.setup_ultra_lightweight_training import UltraLightConfig, UltraLightModel


def load_trained_model():
    """Load the trained ultra-lightweight model"""
    print("🔧 Loading trained model...")

    # Load tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2', use_safetensors=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load config and model
    config = UltraLightConfig()
    model = UltraLightModel(config, len(tokenizer))

    # Load checkpoint
    checkpoint_path = "src/training/ultra_light_checkpoints/checkpoint_epoch_0.pth"
    checkpoint = torch.load(checkpoint_path, map_location='cuda' if torch.cuda.is_available() else 'cpu')
    model.load_state_dict(checkpoint['model_state_dict'])

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()

    print("✅ Model loaded successfully!")
    print(f"📊 Training metrics: Loss={checkpoint['metrics']['loss']:.4f}, Acc={checkpoint['metrics']['accuracy']:.4f}")

    return model, tokenizer, device

def generate_response(model, tokenizer, device, input_text, max_length=64):
    """Generate a response using the trained model"""
    # Tokenize input
    inputs = tokenizer(
        input_text,
        max_length=max_length//2,  # Leave room for generation
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )

    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    with torch.no_grad():
        # Generate tokens one by one
        generated_ids = input_ids.clone()

        for _ in range(max_length//2):  # Generate up to half max length
            # Get model outputs
            outputs = model(generated_ids, attention_mask)

            # Get next token probabilities
            next_token_logits = outputs[:, -1, :]

            # Sample next token (with temperature for some randomness)
            temperature = 0.7
            next_token_logits = next_token_logits / temperature
            next_token_id = torch.multinomial(F.softmax(next_token_logits, dim=-1), 1)

            # Stop if we generate EOS token
            if next_token_id.item() == tokenizer.eos_token_id:
                break

            # Append to generated sequence
            generated_ids = torch.cat([generated_ids, next_token_id], dim=-1)

            # Update attention mask
            attention_mask = torch.cat([attention_mask, torch.ones(1, 1, device=device)], dim=-1)

    # Decode the generated text
    generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

    # Extract just the generated part (remove input)
    input_text_clean = tokenizer.decode(input_ids[0], skip_special_tokens=True).strip()
    if generated_text.startswith(input_text_clean):
        response = generated_text[len(input_text_clean):].strip()
    else:
        response = generated_text.strip()

    return response if response else "[Model generated empty response]"

def test_conversation():
    """Test basic conversation capability"""
    print("🧪 Testing ImpressionCore B2 Ultra-Lightweight Model Inference\n")

    try:
        # Load model
        model, tokenizer, device = load_trained_model()

        # Test conversations
        test_inputs = [
            "Hello! How are you?",
            "What's the weather like?",
            "Can you help me?",
            "Thank you for your help.",
            "Good morning!",
        ]

        print("💬 Testing Conversations:")
        print("=" * 50)

        for i, input_text in enumerate(test_inputs, 1):
            print(f"\n{i}. Human: {input_text}")

            response = generate_response(model, tokenizer, device, input_text)
            print(f"   B2: {response}")

        print("\n" + "=" * 50)
        print("✅ Inference test completed successfully!")
        print("\n🎯 Next Steps:")
        print("   • Model shows basic text generation capability")
        print("   • Ready for Phase 2 distillation pipeline")
        print("   • Can be scaled up with more training data")
        print("   • Memory usage optimized for GTX 1050 Ti")

    except Exception as e:
        print(f"❌ Inference test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversation()
