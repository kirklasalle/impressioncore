import torch
from pathlib import Path
from src.core.models.impressioncore_b3_architecture import ImpressionCoreB3Model, B3Config

def create_dummy():
    print("Creating dummy B3 base model...")
    # Use small config to act as "Base" for testing the pipeline
    config = B3Config(
        vocab_size=50257,
        n_positions=1024,
        n_embd=768,
        n_layer=4,   # Small for test
        n_head=8
    )

    model = ImpressionCoreB3Model(config)

    save_path = Path("checkpoints/base/step_1000.pt")
    save_path.parent.mkdir(parents=True, exist_ok=True)

    torch.save(model.state_dict(), save_path)
    print(f"Saved dummy base model to {save_path}")

if __name__ == "__main__":
    create_dummy()
