"""Quick test of the distilled Stage 4 model"""
import sys

import pytest
import torch

sys.path.insert(0, '.')
pytest.importorskip("b3_constitutional_trainer", reason="Legacy root script archived")
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope
from transformers import AutoTokenizer

print("\n" + "="*70)
print("TESTING STAGE 4 DISTILLED MODEL (from llama3.2:3b teacher)")
print("="*70)

# Load model
device = torch.device('cuda')
config = B3HopeConfig()
model = ImpressionCoreB3Hope(config)

# Load checkpoint (extract only model weights)
checkpoint = torch.load('b3_distill_stage4_final.pth', map_location=device, weights_only=False)
model.load_state_dict(checkpoint['model_state_dict'])
model = model.to(device)
model.eval()

print("\nModel: ImpressionCore B3-Hope")
print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
print(f"Training Loss: {checkpoint.get('train_loss', 'N/A')}")
print(f"Device: {device}")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
tokenizer.pad_token = tokenizer.eos_token

# Test prompts
test_prompts = [
    "Hello",
    "How are you?",
    "What is AI?",
    "How does machine learning work?",
    "Explain neural networks",
    "Can you help me?",
    "What is deep learning?",
    "Tell me about Python programming",
    "How do you learn?",
    "What is your purpose?"
]

print("\n" + "="*70)
print("GENERATION TESTS")
print("="*70)

for prompt in test_prompts:
    print(f"\nUSER: {prompt}")

    # Tokenize
    inputs = tokenizer(prompt, return_tensors='pt', padding=True)
    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    # Generate
    with torch.no_grad():
        generated_ids = [input_ids[0].tolist()]

        for _ in range(50):
            outputs = model(input_ids, attention_mask=attention_mask)
            next_token_logits = outputs['logits'][0, -1, :]
            next_token = torch.argmax(next_token_logits).unsqueeze(0).unsqueeze(0)

            generated_ids[0].append(next_token.item())
            input_ids = torch.cat([input_ids, next_token], dim=1)
            attention_mask = torch.cat([attention_mask, torch.ones((1, 1), device=device)], dim=1)

    # Decode
    response = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    print(f"AI: {response[len(prompt):].strip()}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
