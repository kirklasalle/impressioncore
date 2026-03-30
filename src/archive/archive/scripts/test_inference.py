#!/usr/bin/env python3
"""
ImpressionCore B3 Inference Test Script
Test the trained model for text generation and conversation
"""

import torch
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from b3_constitutional_trainer import B3ConstitutionalTrainer

def simple_generate(model, tokenizer, input_ids, max_new_tokens=50, temperature=0.7, device='cuda'):
    """Simple generation function for our B3 model"""
    model.eval()

    with torch.no_grad():
        generated = input_ids.clone()

        for _ in range(max_new_tokens):
            # Prepare batch for model
            batch = {
                'input_ids': generated,
                'attention_mask': torch.ones_like(generated),
                'image_embeddings': torch.zeros(generated.size(0), 768, device=device),
                'audio_embeddings': torch.zeros(generated.size(0), 768, device=device),
                'labels': generated
            }

            # Get model outputs
            outputs = model(
                input_ids=batch['input_ids'],
                image_features=batch['image_embeddings'],
                audio_features=batch['audio_embeddings'],
                mask=batch['attention_mask']
            )

            # Get next token logits
            logits = outputs['logits'][:, -1, :] / temperature

            # Sample next token
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, 1)

            # Stop if EOS token
            if next_token.item() == tokenizer.eos_token_id:
                break

            # Append token
            generated = torch.cat([generated, next_token], dim=1)

    return generated


def test_inference():
    """Test inference with our best checkpoint"""

    print("🤖 ImpressionCore B3 Inference Test")
    print("=" * 50)

    # Best checkpoint path - use the latest Phase 2 checkpoint
    checkpoint_path = "b3_hope_f_drive_production_checkpoint_step_1500.pth"

    if not os.path.exists(checkpoint_path):
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        return

    print(f"📁 Loading checkpoint: {checkpoint_path}")

    try:
        # Create trainer (will load model architecture)
        trainer = B3ConstitutionalTrainer(checkpoint_path=checkpoint_path)

        # Setup model and optimizer
        trainer.setup_model_and_optimizer()

        # Initialize tokenizers
        trainer.tokenizer_system.initialize_tokenizers()

        # Access model and tokenizer after initialization
        if not hasattr(trainer, 'model'):
            print("❌ Model not found in trainer")
            return

        model = trainer.model
        tokenizer = trainer.tokenizer_system.output_tokenizer

        print(f"✅ Model loaded: {sum(p.numel() for p in model.parameters())/1e6:.1f}M params")
        print(f"✅ Device: {trainer.device}")

        # Set to eval mode
        model.eval()

        # Test prompts
        test_prompts = [
            "Hello, how are you?",
            "What is artificial intelligence?",
            "Tell me about yourself.",
            "Complete this sentence: The future of AI is"
        ]

        print("\n🎯 Testing Text Generation:")
        print("=" * 30)

        with torch.no_grad():
            for prompt in test_prompts:
                print(f"\n💬 Prompt: {prompt}")

                # Tokenize input
                inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)
                inputs = {k: v.to(trainer.device) for k, v in inputs.items()}

                # Generate using our simple function
                try:
                    with torch.amp.autocast(device_type='cuda', enabled=False):  # Use FP32 for stability
                        outputs = simple_generate(
                            model=model,
                            tokenizer=tokenizer,
                            input_ids=inputs['input_ids'],
                            max_new_tokens=50,
                            temperature=0.7,
                            device=trainer.device
                        )

                    # Decode response
                    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    response = generated_text[len(prompt):].strip()

                    print(f"🤖 Response: {response}")

                except Exception as e:
                    print(f"❌ Generation error: {e}")
                    import traceback
                    traceback.print_exc()

        print("\n✅ Inference test completed!")

    except Exception as e:
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inference()