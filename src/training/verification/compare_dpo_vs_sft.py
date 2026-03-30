import tiktoken
import torch

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model


def load_model(path, device):
    print(f"Loading model from {path}...")
    checkpoint = torch.load(path, map_location="cpu")
    config = B3Config()
    model = ImpressionCoreB3Model(config)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    return model

def generate(model, tokenizer, prompt, device, max_new_tokens=50):
    input_ids = tokenizer.encode(prompt)
    input_tensor = torch.tensor([input_ids], dtype=torch.long).to(device)

    with torch.no_grad():
        for _ in range(max_new_tokens):
            outputs = model(input_ids=input_tensor)
            next_token_logits = outputs["logits"][:, -1, :]
            next_token = torch.argmax(next_token_logits, dim=-1).unsqueeze(0)
            input_tensor = torch.cat([input_tensor, next_token], dim=1)

            if next_token.item() == 50256: # EOS
                break

    return tokenizer.decode(input_tensor[0].tolist())

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = tiktoken.get_encoding("gpt2")

    sft_path = r"F:\models\checkpoints\kd_sft_phase2\step_5000.pt"
    dpo_path = r"F:\models\checkpoints\dpo_phase3\dpo_final.pt"

    # Load SFT Model
    sft_model = load_model(sft_path, device)

    # Test Prompts
    prompts = [
        "Human: How do I improve my memory?\nAssistant:",
        "Human: Hey Hope, I need to prep for a client intro.\nAssistant:",
        "Human: I'm feeling anxious before tomorrow's pitch.\nAssistant:"
    ]

    print("\n--- SFT Model Generation ---")
    for p in prompts:
        print(f"\nPrompt: {p.strip()}")
        print(generate(sft_model, tokenizer, p, device))

    # Free memory
    del sft_model
    torch.cuda.empty_cache()

    # Load DPO Model
    dpo_model = load_model(dpo_path, device)

    print("\n--- DPO Model Generation ---")
    for p in prompts:
        print(f"\nPrompt: {p.strip()}")
        print(generate(dpo_model, tokenizer, p, device))

if __name__ == "__main__":
    main()
