import pytest
import torch

pytest.importorskip("src.training.conversational_finetune", reason="Training module not available")
from transformers import AutoTokenizer

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
from src.training.conversational_finetune import ConvFinetuneConfig, apply_lora_to_model


def test_conversational_b3():
    print("Initializing Conversational B3 Test...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Paths
    base_path = "F:/models/checkpoints/diverse_curriculum_mhc_ultra/step_1000.pt"
    lora_path = "F:/models/checkpoints/b3_conversational/b3_conv_epoch_final.pt"

    print("Loading Base Model...")
    config = B3Config()
    model = ImpressionCoreB3Model(config)

    # Load base weights
    checkpoint = torch.load(base_path, map_location='cpu') # Load to CPU first
    if isinstance(checkpoint, dict):
        state_dict = checkpoint.get('model_state_dict') or checkpoint.get('model') or checkpoint
        model.load_state_dict(state_dict, strict=False)

    # Apply LoRA Structure
    print("Applying LoRA Structure...")
    ft_config = ConvFinetuneConfig(lora_r=16, lora_alpha=32)
    model = apply_lora_to_model(model, ft_config)

    # Load LoRA Weights
    print(f"Loading LoRA weights from {lora_path}...")
    lora_checkpoint = torch.load(lora_path, map_location='cpu')
    lora_state = lora_checkpoint['lora_state_dict']

    # Load state dict strictly (should match LoRA params only)
    # Since model is (Base + LoRA), and lora_state is just (LoRA), we need to load carefully.
    # The keys in lora_state match the full model keys (e.g. layers.0.attn.lora_A).
    missing, unexpected = model.load_state_dict(lora_state, strict=False)
    print(f"LoRA Load: {len(missing)} missing (Base weights), {len(unexpected)} unexpected.")

    model.to(device)
    model.eval()

    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
    tokenizer.pad_token = tokenizer.eos_token

    # Test Prompts
    prompts = [
        "Hello, who are you?",
        "What is the meaning of life?",
        "Explain quantum entanglement.",
        "Write a python function to add two numbers."
    ]

    print("\n--- Generation Test ---")

    for prompt in prompts:
        full_prompt = f"User: {prompt}\nAssistant:"
        inputs = tokenizer(full_prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=50,
                temperature=0.7,
                top_k=40
            )

        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = generated.replace(full_prompt, "").strip()

        print(f"\nUser: {prompt}")
        print(f"B3: {response}")
        print("-" * 20)

if __name__ == "__main__":
    test_conversational_b3()
