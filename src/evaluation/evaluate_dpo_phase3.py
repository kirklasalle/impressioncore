import os

import tiktoken
import torch

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model


def generate_response(model, tokenizer, prompt, max_new_tokens=50, device="cuda"):
    model.eval()
    input_ids = tokenizer.encode(prompt)
    input_tensor = torch.tensor([input_ids], dtype=torch.long).to(device)

    generated = input_ids.copy()

    with torch.no_grad():
        for _ in range(max_new_tokens):
            outputs = model(input_ids=input_tensor)
            logits = outputs["logits"][:, -1, :]
            next_token = torch.argmax(logits, dim=-1).item()

            generated.append(next_token)
            input_tensor = torch.tensor([generated], dtype=torch.long).to(device)

            if next_token == 50256: # EOS token for GPT-2
                break

    return tokenizer.decode(generated)

def main():
    checkpoint_path = r"F:\models\checkpoints\dpo_phase3\dpo_final.pt"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Loading DPO Phase 3 model from {checkpoint_path}...")

    if not os.path.exists(checkpoint_path):
        print(f"Error: Checkpoint not found at {checkpoint_path}")
        return

    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    config = B3Config()
    model = ImpressionCoreB3Model(config)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)

    tokenizer = tiktoken.get_encoding("gpt2")

    test_prompts = [
        "Hello, how are you?",
        "What is artificial intelligence?",
        "Can you help me write a poem?",
        "Explain quantum computing in simple terms.",
        "I'm feeling sad today."
    ]

    print("\nStarting Evaluation...\n")

    for prompt in test_prompts:
        print(f"Prompt: {prompt}")
        response = generate_response(model, tokenizer, f"Human: {prompt}\nAssistant:", max_new_tokens=50, device=device)
        # Extract just the assistant part if possible, or print full
        print(f"Response: {response}")
        print("-" * 50)

if __name__ == "__main__":
    main()
