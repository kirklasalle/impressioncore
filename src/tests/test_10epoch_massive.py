"""Quick test of the 10-epoch model (saved as b3_massive_best.pth)"""
import sys

import pytest
import torch

sys.path.insert(0, '.')

# Import from the constitutional trainer file
pytest.importorskip("b3_constitutional_trainer", reason="Legacy root script archived")
from b3_constitutional_trainer import BaseTokenizer, ImpressionCoreB3Hope

print("\n" + "="*70)
print("TESTING 10-EPOCH MODEL (loss 0.0105)")
print("="*70)

# Load model
model = ImpressionCoreB3Hope()
checkpoint = torch.load('b3_massive_best.pth', map_location='cuda', weights_only=False)
model.load_state_dict(checkpoint['model_state_dict'])
model = model.to('cuda')
model.eval()

print(f"\nTraining Loss: {checkpoint['train_loss']:.4f}")
print(f"Model Parameters: {sum(p.numel() for p in model.parameters()):,}")
print(f"Device: {next(model.parameters()).device}")

# Test prompts
tokenizer = BaseTokenizer()
test_prompts = [
    "Hello",
    "How are you?",
    "What is AI?",
    "Can you help me?",
    "Explain neural networks"
]

print("\n" + "="*70)
print("GENERATION TESTS")
print("="*70)

for prompt in test_prompts:
    print(f"\nPrompt: \"{prompt}\"")

    # Encode prompt
    input_ids = tokenizer.encode(prompt)
    input_tensor = torch.tensor([[input_ids[0]]], device='cuda')

    # Generate response (greedy decoding)
    generated = [input_ids[0]]
    with torch.no_grad():
        for _ in range(50):
            outputs = model(input_tensor)
            next_token = outputs['logits'][0, -1].argmax().item()
            generated.append(next_token)
            input_tensor = torch.tensor([[next_token]], device='cuda')

    # Decode
    response = tokenizer.decode(generated)
    print(f"Response: {response}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
