"""
B3-Hope Improved Generator - Using Training-Compatible Generation Method

This generator uses the SAME format and approach as training to ensure
the model generates text the way it was taught during training.

Key Insight: The model was trained with "USER: {text} AI: {response}" format.
We need to generate using the SAME format and let the model complete the response.

Author: ImpressionCore Team
Created: October 2, 2025
"""

import logging
import sys
from pathlib import Path

import torch
from transformers import AutoTokenizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load DialoGPT tokenizer
logger.info("Loading DialoGPT tokenizer...")
tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
tokenizer.pad_token = tokenizer.eos_token
logger.info(f"Tokenizer loaded: vocab_size={len(tokenizer)}")

def load_trained_model(checkpoint_path='b3_gpu_extensive_best.pth'):
    """Load the best trained B3-Hope model"""
    logger.info(f"Loading trained model from {checkpoint_path}...")

    # Import model
    sys.path.insert(0, str(Path(__file__).parent))
    from b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope

    # Create model
    config = B3HopeConfig()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ImpressionCoreB3Hope(config)
    model = model.to(device)

    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)

    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
        logger.info(f"✅ Loaded checkpoint from epoch {checkpoint.get('epoch', 'unknown')}")
        logger.info(f"   Final loss: {checkpoint.get('loss', 'unknown'):.4f}")
    else:
        model.load_state_dict(checkpoint)
        logger.info("✅ Loaded model state dict")

    model.eval()

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Model parameters: {total_params:,}")
    logger.info(f"Device: {device}")

    return model, device

def generate_response_improved(model, device, prompt, max_new_tokens=50):
    """
    Generate response using training-compatible method

    The model was trained with format: "USER: {input} AI: {output}"
    So we provide: "USER: {prompt} AI:" and let it complete the response.
    """

    # Format EXACTLY like training
    formatted_input = f"USER: {prompt} AI:"

    # Tokenize
    input_ids = tokenizer.encode(formatted_input, return_tensors='pt').to(device)
    input_length = input_ids.shape[1]

    logger.debug(f"Input: {formatted_input}")
    logger.debug(f"Input tokens: {input_ids.shape}")

    with torch.no_grad():
        # Generate using the model's forward pass
        generated_ids = input_ids.clone()

        for step in range(max_new_tokens):
            # Get model output for current sequence
            output_dict = model(generated_ids)
            logits = output_dict['logits']  # Extract logits from dict

            # Get logits for next token (last position)
            next_token_logits = logits[:, -1, :]

            # Apply temperature for sampling diversity
            temperature = 0.7
            next_token_logits = next_token_logits / temperature

            # Get top-k tokens
            top_k = 40
            top_k_values, top_k_indices = torch.topk(next_token_logits, top_k)

            # Sample from top-k
            probs = torch.softmax(top_k_values, dim=-1)
            next_token_idx = torch.multinomial(probs, num_samples=1)
            next_token = top_k_indices.gather(-1, next_token_idx)

            # Append to sequence
            generated_ids = torch.cat([generated_ids, next_token], dim=-1)

            # Check for EOS or if we've generated enough
            if next_token.item() == tokenizer.eos_token_id:
                logger.debug(f"EOS token generated at step {step}")
                break

            # Check if response is complete (simple heuristic: sentence ending)
            if step > 10:  # Minimum length
                decoded_so_far = tokenizer.decode(generated_ids[0][input_length:], skip_special_tokens=True)
                if decoded_so_far.strip().endswith(('.', '!', '?')):
                    logger.debug(f"Sentence ending detected at step {step}")
                    break

    # Decode the generated part only (after "AI:")
    full_generated = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

    # Extract just the AI response
    if "AI:" in full_generated:
        response = full_generated.split("AI:")[-1].strip()
    else:
        response = full_generated[len(formatted_input):].strip()

    logger.debug(f"Generated response: {response}")

    return response

def test_improved_generation():
    """Test improved generation method"""

    logger.info("="*70)
    logger.info("B3-HOPE IMPROVED GENERATION TESTING")
    logger.info("Using training-compatible generation method")
    logger.info("="*70)

    # Load model
    model, device = load_trained_model()

    # Test prompts from training data (should be best)
    training_prompts = [
        "Hello",
        "What is AI?",
        "How does machine learning work?",
        "Can you help me?",
        "Explain neural networks",
    ]

    # Test unseen variations (generalization)
    unseen_prompts = [
        "Hi there",
        "Tell me about artificial intelligence",
        "I need assistance",
        "What are neural networks?",
        "Good afternoon",
    ]

    logger.info("\n" + "="*70)
    logger.info("TESTING WITH TRAINING PROMPTS (Should work best)")
    logger.info("="*70)

    for i, prompt in enumerate(training_prompts, 1):
        logger.info(f"\n[Test {i}/{len(training_prompts)}]")
        logger.info(f"USER: {prompt}")

        try:
            response = generate_response_improved(model, device, prompt, max_new_tokens=60)
            logger.info(f"AI: {response}")
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()

    logger.info("\n" + "="*70)
    logger.info("TESTING WITH UNSEEN VARIATIONS (Generalization)")
    logger.info("="*70)

    for i, prompt in enumerate(unseen_prompts, 1):
        logger.info(f"\n[Test {i}/{len(unseen_prompts)}]")
        logger.info(f"USER: {prompt}")

        try:
            response = generate_response_improved(model, device, prompt, max_new_tokens=60)
            logger.info(f"AI: {response}")
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()

    logger.info("\n" + "="*70)
    logger.info("✅ Improved generation testing complete!")
    logger.info("="*70)

def interactive_chat():
    """Interactive chat mode"""

    logger.info("\n" + "="*70)
    logger.info("INTERACTIVE CHAT MODE - IMPROVED GENERATOR")
    logger.info("Type 'quit' to exit")
    logger.info("="*70 + "\n")

    # Load model
    model, device = load_trained_model()

    while True:
        try:
            user_input = input("\nYOU: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                logger.info("Exiting interactive mode...")
                break

            if not user_input:
                continue

            response = generate_response_improved(model, device, user_input, max_new_tokens=60)
            print(f"AI: {response}")

        except KeyboardInterrupt:
            logger.info("\nExiting interactive mode...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='B3-Hope Improved Generator')
    parser.add_argument('--interactive', action='store_true', help='Start interactive chat mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.interactive:
        interactive_chat()
    else:
        test_improved_generation()
