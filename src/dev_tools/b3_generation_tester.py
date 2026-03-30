"""
B3-Hope Generation Tester
Tests the conversational generation capabilities of trained B3-Hope model

This script loads the best trained checkpoint and tests neural generation
quality with diverse prompts to ensure TRUE neural generation, not templates.

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
logger.info(f"Tokenizer loaded: vocab_size={len(tokenizer)}, pad_token={tokenizer.pad_token}")

def load_trained_model(checkpoint_path='b3_distill_stage4_final.pth'):
    """Load the best trained B3-Hope model (Stage 4 distilled from llama3.2:3b)"""
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

def generate_response(model, device, prompt, max_length=100, temperature=0.8, top_k=50, top_p=0.9):
    """Generate a response using the trained model"""

    # Format prompt
    formatted_prompt = f"USER: {prompt} AI:"

    # Tokenize
    input_ids = tokenizer.encode(formatted_prompt, return_tensors='pt').to(device)

    with torch.no_grad():
        # Get model output
        output_dict = model(input_ids)
        logits = output_dict['logits']  # Extract logits from dict

        # Start with input tokens
        generated = input_ids

        # Generate tokens one at a time
        for _ in range(max_length):
            # Get logits for next token
            next_token_logits = logits[:, -1, :]

            # Apply temperature
            next_token_logits = next_token_logits / temperature

            # Apply top-k filtering
            if top_k > 0:
                indices_to_remove = next_token_logits < torch.topk(next_token_logits, top_k)[0][..., -1, None]
                next_token_logits[indices_to_remove] = float('-inf')

            # Apply top-p (nucleus) filtering
            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                indices_to_remove = sorted_indices[sorted_indices_to_remove]
                next_token_logits[:, indices_to_remove] = float('-inf')

            # Sample next token
            probs = torch.softmax(next_token_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            # Append to generated sequence
            generated = torch.cat([generated, next_token], dim=-1)

            # Break if EOS token generated
            if next_token.item() == tokenizer.eos_token_id:
                break

            # Get logits for next iteration if not at end
            if _ < max_length - 1:
                output_dict = model(generated)
                logits = output_dict['logits']

    # Decode generated text
    generated_text = tokenizer.decode(generated[0], skip_special_tokens=True)

    # Extract AI response (after "AI:")
    response = generated_text.split("AI:")[-1].strip() if "AI:" in generated_text else generated_text.strip()

    return response

def test_generation():
    """Test generation with diverse prompts"""

    logger.info("="*70)
    logger.info("B3-HOPE GENERATION TESTING")
    logger.info("="*70)

    # Load model
    model, device = load_trained_model()

    # Test prompts - diverse topics to test generalization
    test_prompts = [
        # Greetings
        "Hello",
        "Good morning",
        "How are you?",

        # Questions
        "What is AI?",
        "How does machine learning work?",
        "Explain neural networks",

        # Help requests
        "Can you help me?",
        "I need advice",
        "I'm confused",

        # Complex questions
        "What is deep learning?",
        "Tell me about Python",
        "Explain gradient descent",

        # Multi-topic
        "What is your purpose?",
        "How do you learn?",
        "Are you intelligent?",

        # Unseen variations (to test generalization)
        "Hey, what's up?",
        "Could you explain overfitting?",
        "I want to understand neural networks better",
    ]

    logger.info(f"\nTesting generation with {len(test_prompts)} diverse prompts...")
    logger.info("="*70)

    for i, prompt in enumerate(test_prompts, 1):
        logger.info(f"\n[Test {i}/{len(test_prompts)}]")
        logger.info(f"USER: {prompt}")

        try:
            response = generate_response(
                model, device, prompt,
                max_length=80,
                temperature=0.8,
                top_k=50,
                top_p=0.9
            )
            logger.info(f"AI: {response}")

        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()

    logger.info("\n" + "="*70)
    logger.info("✅ Generation testing complete!")
    logger.info("="*70)

def interactive_chat():
    """Interactive chat mode for manual testing"""

    logger.info("\n" + "="*70)
    logger.info("INTERACTIVE CHAT MODE")
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

            response = generate_response(
                model, device, user_input,
                max_length=80,
                temperature=0.8,
                top_k=50,
                top_p=0.9
            )

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

    parser = argparse.ArgumentParser(description='B3-Hope Generation Tester')
    parser.add_argument('--interactive', action='store_true', help='Start interactive chat mode')
    parser.add_argument('--checkpoint', type=str, default='b3_gpu_extensive_best.pth',
                       help='Path to checkpoint file')

    args = parser.parse_args()

    if args.interactive:
        interactive_chat()
    else:
        test_generation()
