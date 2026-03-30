#!/usr/bin/env python3
"""
Test Phase 2 Model (KD + SFT)
=============================

Loads the final checkpoint from Phase 2 training and runs an interactive
conversation loop to verify model performance.
"""

import os
import sys
from pathlib import Path

import tiktoken
import torch

# Ensure project root is in sys.path
_file_path = Path(__file__).resolve()
_parents = _file_path.parents
_PROJECT_ROOT = _parents[3] if len(_parents) > 3 else _parents[-1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model


def load_model(checkpoint_path: str, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
    print(f"Loading model from {checkpoint_path}...")

    # Initialize config and model
    config = B3Config()
    model = ImpressionCoreB3Model(config).to(device)

    # Load checkpoint
    try:
        checkpoint = torch.load(checkpoint_path, map_location=device)
        # Handle different checkpoint formats (full training state vs model only)
        state_dict = checkpoint.get("model_state_dict", checkpoint)

        model.load_state_dict(state_dict, strict=False)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading checkpoint: {e}")
        sys.exit(1)

    model.eval()
    return model

def generate_response(model, tokenizer, prompt: str, device: str, max_new_tokens: int = 100):
    # Format prompt as per training data (Human: ...\nAssistant:)
    formatted_prompt = f"Human: {prompt}\nAssistant:"

    input_ids = tokenizer.encode(formatted_prompt)
    torch.tensor([input_ids], dtype=torch.long).to(device)

    with torch.no_grad():
        # Simple greedy generation for testing
        generated = input_ids[:]
        for _ in range(max_new_tokens):
            inputs = torch.tensor([generated], dtype=torch.long).to(device)
            outputs = model(input_ids=inputs)
            logits = outputs["logits"][:, -1, :]
            next_token = torch.argmax(logits, dim=-1).item()

            generated.append(next_token)
            if next_token == tokenizer.eot_token: # Stop if end of text (if applicable)
                break

    decoded = tokenizer.decode(generated)
    # Extract only the assistant's response
    try:
        response = decoded.split("Assistant:")[-1].strip()
    except Exception:
        response = decoded

    return response

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, help="Single prompt to test")
    args = parser.parse_args()

    checkpoint_path = r"F:\models\checkpoints\kd_sft_phase2\step_5000.pt"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    if not os.path.exists(checkpoint_path):
        print(f"Checkpoint not found at {checkpoint_path}")
        return

    model = load_model(checkpoint_path, device)
    tokenizer = tiktoken.get_encoding("gpt2")

    if args.prompt:
        response = generate_response(model, tokenizer, args.prompt, device)
        print(f"Assistant: {response}")
        return

    print("\n" + "="*50)
    print("Phase 2 Model Interactive Test")
    print("Type 'quit' or 'exit' to stop.")
    print("="*50 + "\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        response = generate_response(model, tokenizer, user_input, device)
        print(f"Assistant: {response}\n")

if __name__ == "__main__":
    main()
