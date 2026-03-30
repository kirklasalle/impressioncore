#!/usr/bin/env python3
"""
Quick Conversation Quality Test
==============================

Simple script to test conversation quality of any B3-Hope checkpoint.
"""

import os

import pytest
import torch
from transformers import AutoTokenizer

pytest.importorskip("b3_constitutional_trainer", reason="Legacy root script archived")
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope


def test_conversation(checkpoint_path: str):
    """Test conversation quality"""
    print(f"🧪 Testing: {checkpoint_path}")

    # Load model
    config = B3HopeConfig()
    model = ImpressionCoreB3Hope(config)

    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    model.eval()

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
    tokenizer.pad_token = tokenizer.eos_token

    # Test prompts
    prompts = [
        "Hello",
        "How are you?",
        "What can you help me with?",
        "Tell me about yourself",
        "Thank you"
    ]

    print("\nConversation Test Results:")
    print("=" * 50)

    for prompt in prompts:
        # Simple generation
        formatted_prompt = f"Human: {prompt}\nAssistant: "
        inputs = tokenizer(formatted_prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            generated = inputs['input_ids'].clone()

            for _ in range(20):  # Short responses
                attention_mask = torch.ones_like(generated)
                outputs = model(input_ids=generated, attention_mask=attention_mask, return_loss=False)

                logits = outputs['logits'][:, -1, :] / 0.7
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)

                if next_token.item() == tokenizer.eos_token_id:
                    break

                generated = torch.cat([generated, next_token], dim=1)

        # Decode
        full_response = tokenizer.decode(generated[0], skip_special_tokens=True)
        response = full_response[len(formatted_prompt):].strip()

        print(f"Human: {prompt}")
        print(f"B3-Hope: {response}")
        print("-" * 30)

def main():
    print("🤖 Quick Conversation Quality Test")

    # Find checkpoints
    checkpoints = []
    for f in os.listdir('.'):
        if f.startswith('b3_hope') and f.endswith('.pth'):
            checkpoints.append(f)

    if not checkpoints:
        print("❌ No checkpoints found!")
        return

    # Sort by modification time (latest first)
    checkpoints.sort(key=os.path.getctime, reverse=True)

    print(f"Found {len(checkpoints)} checkpoints:")
    for i, cp in enumerate(checkpoints[:3]):  # Show top 3
        print(f"{i+1}. {cp}")

    # Test the latest one
    if checkpoints:
        latest = checkpoints[0]
        print(f"\nTesting latest: {latest}")
        test_conversation(latest)

if __name__ == "__main__":
    main()
