"""
Simple Conversation Test for Path C Final Model
Tests the b3_embedding_integrated_final.pth model
No interactive prompts - runs automatically
"""

import torch
import sys
from pathlib import Path
from transformers import AutoTokenizer

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from training.b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope

def test_conversation():
    """Run automated conversation test on final model"""

    print("\n" + "="*80)
    print("🧪 PATH C FINAL MODEL - CONVERSATION QUALITY TEST")
    print("="*80)
    print("\nModel: b3_embedding_integrated_final.pth")
    print("Training: 55 epochs, 4-phase curriculum (32 minutes)")
    print("Dataset: 96 B3 native embeddings (768-dim)")
    print("="*80 + "\n")

    # Test queries - mix of simple and complex
    test_queries = [
        "Hello! How are you today?",
        "What is artificial intelligence?",
        "Can you explain machine learning in simple terms?",
        "Tell me about neural networks",
        "What's the difference between deep learning and AI?",
        "How do computers understand language?",
        "Explain what a transformer model is",
        "What can you help me with?"
    ]

    checkpoint_path = "F:/models/checkpoints/b3/b3_embedding_integrated_final.pth"

    print("⏳ Loading model...")

    # Initialize model
    config = B3HopeConfig()
    model = ImpressionCoreB3Hope(config)

    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    model.eval()

    print(f"✅ Model loaded on {device}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
    tokenizer.pad_token = tokenizer.eos_token

    print("✅ Tokenizer loaded")
    print("\n" + "="*80)
    print("CONVERSATION TEST RESULTS")
    print("="*80 + "\n")

    results = []

    for idx, query in enumerate(test_queries, 1):
        print(f"[{idx}/{len(test_queries)}] Testing query...")
        print(f"👤 Human: {query}")

        # Format input
        formatted_input = f"Human: {query}\nAssistant:"
        inputs = tokenizer(formatted_input, return_tensors="pt", padding=True).to(device)

        # Generate response
        with torch.no_grad():
            generated = inputs['input_ids'].clone()

            for step in range(50):  # Max 50 tokens
                attention_mask = torch.ones_like(generated)
                outputs = model(
                    input_ids=generated,
                    attention_mask=attention_mask,
                    return_loss=False
                )

                logits = outputs['logits'][:, -1, :] / 0.8  # Temperature
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, 1)

                if next_token.item() == tokenizer.eos_token_id:
                    break

                generated = torch.cat([generated, next_token], dim=1)

        # Decode response
        full_text = tokenizer.decode(generated[0], skip_special_tokens=True)
        response = full_text[len(formatted_input):].strip()

        # Basic quality assessment
        is_empty = len(response) < 5
        is_repetitive = len(set(response.split())) < len(response.split()) * 0.3
        is_generic = response.lower() in ["i don't know", "i'm not sure", "i can't help", "hello"]

        quality_flag = "⚠️" if (is_empty or is_repetitive or is_generic) else "✅"

        print(f"🤖 B3-Hope: {response}")
        print(f"   Quality: {quality_flag}")
        print(f"   Length: {len(response)} chars, {len(response.split())} words")
        print("   " + "-"*76 + "\n")

        results.append({
            "query": query,
            "response": response,
            "empty": is_empty,
            "repetitive": is_repetitive,
            "generic": is_generic,
            "length": len(response)
        })

    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)

    total = len(results)
    empty_count = sum(1 for r in results if r['empty'])
    repetitive_count = sum(1 for r in results if r['repetitive'])
    generic_count = sum(1 for r in results if r['generic'])
    quality_count = total - empty_count - repetitive_count - generic_count

    avg_length = sum(r['length'] for r in results) / total

    print(f"\nTotal Queries: {total}")
    print(f"Quality Responses: {quality_count}/{total} ({quality_count/total*100:.1f}%)")
    print(f"Empty Responses: {empty_count}/{total} ({empty_count/total*100:.1f}%)")
    print(f"Repetitive Responses: {repetitive_count}/{total} ({repetitive_count/total*100:.1f}%)")
    print(f"Generic Responses: {generic_count}/{total} ({generic_count/total*100:.1f}%)")
    print(f"\nAverage Response Length: {avg_length:.1f} characters")

    print("\n" + "="*80)

    if quality_count >= total * 0.75:
        print("✅ GOOD: Model shows quality responses (≥75%)")
    elif quality_count >= total * 0.50:
        print("⚠️ MODERATE: Model shows some quality (50-75%)")
    else:
        print("❌ POOR: Model needs improvement (<50% quality)")

    print("="*80 + "\n")

    # Save results
    results_file = Path("docs/analysis/path_c_final_conversation_test.md")

    with open(results_file, 'w', encoding='utf-8') as f:
        f.write("# Path C Final Model - Conversation Test Results\n\n")
        f.write(f"**Date:** October 6, 2025\n")
        f.write(f"**Model:** b3_embedding_integrated_final.pth\n")
        f.write(f"**Training:** 55 epochs, 4-phase curriculum\n\n")
        f.write("## Test Results\n\n")

        for idx, result in enumerate(results, 1):
            f.write(f"### Query {idx}\n\n")
            f.write(f"**Human:** {result['query']}\n\n")
            f.write(f"**B3-Hope:** {result['response']}\n\n")
            f.write(f"- Length: {result['length']} chars\n")
            f.write(f"- Empty: {'Yes' if result['empty'] else 'No'}\n")
            f.write(f"- Repetitive: {'Yes' if result['repetitive'] else 'No'}\n")
            f.write(f"- Generic: {'Yes' if result['generic'] else 'No'}\n\n")
            f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write(f"- Total Queries: {total}\n")
        f.write(f"- Quality Responses: {quality_count}/{total} ({quality_count/total*100:.1f}%)\n")
        f.write(f"- Average Length: {avg_length:.1f} characters\n")

    print(f"📄 Results saved to: {results_file}\n")

if __name__ == "__main__":
    try:
        test_conversation()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
