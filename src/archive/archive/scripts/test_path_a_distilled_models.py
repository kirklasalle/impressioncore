"""
Test Path A Distilled Model - Conversation Quality Assessment
Tests the knowledge distillation checkpoints progressively
No interactive prompts - runs automatically
"""

import torch
import sys
from pathlib import Path
from transformers import AutoTokenizer
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from training.b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope


def test_checkpoint(checkpoint_path, checkpoint_name):
    """Test a single checkpoint"""

    print("\n" + "="*80)
    print(f"🧪 TESTING: {checkpoint_name}")
    print("="*80)
    print(f"Checkpoint: {checkpoint_path}")
    print("="*80 + "\n")

    # Test queries - same as Path C for comparison
    test_queries = [
        "Hello! How are you today?",
        "What is artificial intelligence?",
        "Explain machine learning to me",
        "What is the difference between AI and machine learning?",
        "What's the difference between deep learning and AI?",
        "How do neural networks work?",
        "What can you help me with?",
        "Thank you for your help!"
    ]

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}\n")

    # Load model
    print("Loading model...")
    config = B3HopeConfig()
    model = ImpressionCoreB3Hope(config).to(device)

    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    print("✅ Model loaded\n")

    # Load tokenizer (DialoGPT tokenizer for compatibility)
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        "microsoft/DialoGPT-medium",
        cache_dir="F:/models/teachers/dialogpt_medium"
    )
    tokenizer.pad_token = tokenizer.eos_token
    print("✅ Tokenizer loaded\n")

    # Test each query
    results = []

    print("="*80)
    print("CONVERSATION TESTS")
    print("="*80 + "\n")

    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/8] Query: \"{query}\"")

        # Tokenize
        inputs = tokenizer(
            f"Human: {query}\nAssistant:",
            return_tensors='pt',
            max_length=128,
            truncation=True,
            padding=True
        ).to(device)

        # Generate (greedy decoding - simple autoregressive)
        with torch.no_grad():
            input_ids = inputs['input_ids']
            generated = input_ids.clone()

            for _ in range(50):  # Generate up to 50 tokens
                # Forward pass
                outputs = model(
                    input_ids=generated,
                    attention_mask=torch.ones_like(generated),
                    return_loss=False
                )

                # Get next token prediction
                next_token_logits = outputs['logits'][:, -1, :]
                next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)

                # Append to sequence
                generated = torch.cat([generated, next_token], dim=1)

                # Stop if EOS token
                if next_token.item() == tokenizer.eos_token_id:
                    break

        # Decode
        response = tokenizer.decode(generated[0], skip_special_tokens=True)

        # Extract assistant response (after "Assistant:")
        if "Assistant:" in response:
            response = response.split("Assistant:")[-1].strip()

        print(f"Response: \"{response}\"\n")

        # Basic quality metrics
        words = response.split()
        unique_words = set(words)

        result = {
            'query': query,
            'response': response,
            'length': len(response),
            'word_count': len(words),
            'unique_words': len(unique_words),
            'is_empty': len(response) < 5,
            'is_repetitive': len(unique_words) < len(words) * 0.3 if len(words) > 0 else True,
            'is_generic': response.lower() in ['i', 'yes', 'no', 'ok', 'sure', 'hello']
        }
        results.append(result)

    # Summary
    print("="*80)
    print("QUALITY SUMMARY")
    print("="*80 + "\n")

    empty_count = sum(1 for r in results if r['is_empty'])
    repetitive_count = sum(1 for r in results if r['is_repetitive'])
    generic_count = sum(1 for r in results if r['is_generic'])
    quality_count = len(results) - empty_count - repetitive_count - generic_count

    avg_length = sum(r['length'] for r in results) / len(results)
    avg_words = sum(r['word_count'] for r in results) / len(results)

    print(f"Total Queries: {len(results)}")
    print(f"Quality Responses: {quality_count}/{len(results)} ({quality_count/len(results)*100:.1f}%)")
    print(f"Empty Responses: {empty_count}/{len(results)}")
    print(f"Repetitive Responses: {repetitive_count}/{len(results)}")
    print(f"Generic Responses: {generic_count}/{len(results)}")
    print(f"\nAverage Response Length: {avg_length:.1f} chars")
    print(f"Average Word Count: {avg_words:.1f} words")

    if quality_count >= len(results) * 0.8:
        print("\n✅ GOOD: Model shows quality responses")
    elif quality_count >= len(results) * 0.5:
        print("\n⚠️  MIXED: Model shows mixed quality")
    else:
        print("\n❌ POOR: Model needs improvement")

    return results


def main():
    """Test all distillation checkpoints progressively"""

    print("\n" + "="*80)
    print("🎓 PATH A: KNOWLEDGE DISTILLATION QUALITY ASSESSMENT")
    print("="*80)
    print("\nTraining: 20 epochs, 2:24:12 duration")
    print("Method: Knowledge distillation from DialoGPT-medium (354M params)")
    print("Dataset: 1,000 simple conversation pairs")
    print("Loss: 326.17 → 3.46 (98.9% reduction)")
    print("="*80 + "\n")

    # Test checkpoints progressively
    checkpoints = [
        ("F:/models/checkpoints/b3/distillation/b3_distilled_epoch5.pth", "Epoch 5 (Early)"),
        ("F:/models/checkpoints/b3/distillation/b3_distilled_epoch10.pth", "Epoch 10 (Mid)"),
        ("F:/models/checkpoints/b3/distillation/b3_distilled_epoch15.pth", "Epoch 15 (Late)"),
        ("F:/models/checkpoints/b3/distillation/b3_distilled_final.pth", "Final Model"),
    ]

    all_results = {}

    for checkpoint_path, checkpoint_name in checkpoints:
        if not Path(checkpoint_path).exists():
            print(f"\n⚠️  Checkpoint not found: {checkpoint_path}")
            continue

        results = test_checkpoint(checkpoint_path, checkpoint_name)
        all_results[checkpoint_name] = results

        input("\nPress Enter to continue to next checkpoint...")

    # Final comparison
    print("\n" + "="*80)
    print("📊 PROGRESSIVE QUALITY COMPARISON")
    print("="*80 + "\n")

    for name, results in all_results.items():
        quality_count = sum(1 for r in results if not r['is_empty'] and not r['is_repetitive'] and not r['is_generic'])
        print(f"{name}: {quality_count}/{len(results)} quality responses ({quality_count/len(results)*100:.1f}%)")

    print("\n" + "="*80)
    print("✅ TESTING COMPLETE")
    print("="*80)
    print("\nCompare these results to Path C (0.0/10.0 - gibberish)")
    print("Target: ≥7.5/10.0 coherent, relevant, college-level responses")
    print()


if __name__ == "__main__":
    main()
