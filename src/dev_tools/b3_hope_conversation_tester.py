#!/usr/bin/env python3
"""
ImpressionCore B3-Hope Conversation Tester
==========================================

Test the latest trained B3-Hope model for conversation capability
"""

import logging
import os

import torch

# Import B3-Hope architecture
from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope
from transformers import AutoTokenizer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def load_model_from_checkpoint(checkpoint_path: str):
    """Load B3-Hope model from checkpoint"""

    logger.info(f"Loading model from: {checkpoint_path}")

    # Check if checkpoint exists
    if not os.path.exists(checkpoint_path):
        logger.error(f"Checkpoint not found: {checkpoint_path}")
        return None, None

    # Load checkpoint
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        logger.info("Checkpoint loaded successfully")

        # Create model with config
        config = B3HopeConfig()
        model = ImpressionCoreB3Hope(config)

        # Load state dict
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
            logger.info("Model state loaded from 'model_state_dict'")
        elif 'model' in checkpoint:
            model.load_state_dict(checkpoint['model'])
            logger.info("Model state loaded from 'model'")
        else:
            model.load_state_dict(checkpoint)
            logger.info("Model state loaded directly from checkpoint")

        # Get device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        model.eval()

        # Load tokenizer
        try:
            tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
            tokenizer.pad_token = tokenizer.eos_token
        except Exception as e:
            logger.warning(f"Could not load DialoGPT tokenizer: {e}")
            logger.info("Attempting alternative tokenizer...")
            try:
                tokenizer = AutoTokenizer.from_pretrained("gpt2")
                tokenizer.pad_token = tokenizer.eos_token
            except Exception as e2:
                logger.error(f"Could not load any tokenizer: {e2}")
                return None, None

        # Get model info
        total_params = sum(p.numel() for p in model.parameters())
        logger.info(f"Model loaded: {total_params:,} parameters on {device}")

        return model, tokenizer

    except Exception as e:
        logger.error(f"Error loading checkpoint: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def simple_generate(model, tokenizer, prompt: str, max_new_tokens: int = 50, temperature: float = 0.7):
    """Simple text generation"""

    device = next(model.parameters()).device

    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=256)
    input_ids = inputs['input_ids'].to(device)
    inputs['attention_mask'].to(device)

    # Generate
    with torch.no_grad():
        generated = input_ids.clone()

        for _ in range(max_new_tokens):
            # Create attention mask
            current_attention_mask = torch.ones_like(generated)

            try:
                # Forward pass (text-only)
                outputs = model(
                    input_ids=generated,
                    attention_mask=current_attention_mask,
                    return_loss=False
                )

                # Get logits and sample next token
                logits = outputs['logits'][:, -1, :] / temperature
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)

                # Stop if EOS
                if next_token.item() == tokenizer.eos_token_id:
                    break

                # Append token
                generated = torch.cat([generated, next_token], dim=1)

            except Exception as e:
                logger.error(f"Generation error: {e}")
                break

    # Decode response
    generated_text = tokenizer.decode(generated[0], skip_special_tokens=True)
    response = generated_text[len(prompt):].strip()

    return response

def test_conversation():
    """Test conversation capability"""

    logger.info("🤖 ImpressionCore B3-Hope Conversation Test")
    logger.info("=" * 60)

    # Latest checkpoint
    checkpoint_path = "b3_hope_f_drive_production_checkpoint_step_1500.pth"

    # Load model
    model, tokenizer = load_model_from_checkpoint(checkpoint_path)

    if model is None:
        logger.error("❌ Failed to load model")
        return

    logger.info("✅ Model loaded successfully!")

    # Test prompts
    test_prompts = [
        "Hello, how are you today?",
        "What is artificial intelligence?",
        "Tell me about yourself.",
        "What can you help me with?",
        "Complete this sentence: The future of AI is"
    ]

    logger.info("\n🎯 Testing Conversation Capability:")
    logger.info("=" * 40)

    for i, prompt in enumerate(test_prompts, 1):
        logger.info(f"\n💬 Test {i}/5: {prompt}")

        try:
            response = simple_generate(
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                max_new_tokens=30,
                temperature=0.7
            )

            logger.info(f"🤖 Response: {response}")

            # Basic quality check
            if len(response.strip()) > 0:
                logger.info("✅ Response generated")
            else:
                logger.warning("⚠️ Empty response")

        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")

    logger.info("\n🎊 Conversation test completed!")

    # Memory usage
    if torch.cuda.is_available():
        memory_used = torch.cuda.max_memory_allocated() / (1024**3)
        logger.info(f"💾 Peak GPU memory: {memory_used:.2f}GB")

def main():
    test_conversation()

if __name__ == "__main__":
    main()
