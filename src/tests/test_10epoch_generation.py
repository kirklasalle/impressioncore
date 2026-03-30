#!/usr/bin/env python3
"""Test generation from 10-epoch trained model"""

import pytest
import torch
from transformers import AutoTokenizer

pytest.importorskip("b3_constitutional_trainer", reason="Legacy root script archived")
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope

print("="*70)
print("TESTING 10-EPOCH TRAINED MODEL GENERATION")
print("="*70)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
tokenizer.pad_token = tokenizer.eos_token

# Initialize model
config = B3HopeConfig(vocab_size=len(tokenizer))
model = ImpressionCoreB3Hope(config)

# Load 10-epoch checkpoint
checkpoint_path = 'b3_10epoch_best.pth'
print(f"Loading: {checkpoint_path}")
checkpoint = torch.load(checkpoint_path, map_location='cuda', weights_only=False)
model.load_state_dict(checkpoint['model_state_dict'])
model = model.to('cuda')
model.eval()

print(f"Training loss achieved: {checkpoint['loss']:.4f}")
print(f"Epoch: {checkpoint['epoch'] + 1}")
print()

# Test prompts
test_prompts = [
    'Hello',
    'What is AI?',
    'How are you?',
    'Can you help me?',
    'Tell me about machine learning'
]

print("="*70)
print("GENERATION TESTS")
print("="*70)

for idx, prompt in enumerate(test_prompts, 1):
    text = f'USER: {prompt} AI:'
    inputs = tokenizer(text, return_tensors='pt').to('cuda')

    with torch.no_grad():
        outputs = model(inputs['input_ids'])
        logits = outputs['logits'] if isinstance(outputs, dict) else outputs

        # Generate tokens
        generated = inputs['input_ids'][0].tolist()
        for _ in range(25):
            next_logits = logits[0, -1, :]
            probs = torch.softmax(next_logits / 0.7, dim=-1)
            next_token = torch.multinomial(probs, 1).item()
            generated.append(next_token)
            if next_token == tokenizer.eos_token_id:
                break

    response = tokenizer.decode(generated, skip_special_tokens=True)
    ai_response = response.split('AI:')[1].strip() if 'AI:' in response else response

    print(f"\n[Test {idx}/{len(test_prompts)}]")
    print(f"USER: {prompt}")
    print(f"AI: {ai_response}")

print("\n" + "="*70)
print("GENERATION TESTING COMPLETE")
print("="*70)
