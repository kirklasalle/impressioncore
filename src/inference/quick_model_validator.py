"""
Quick Model Checkpoint Validator
Tests alternative model checkpoints to find Phase 1 quality baseline

Created: October 5, 2025
Purpose: Identify which checkpoint produces 4.32/5.0 quality with substantive answers
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from b3_intelligent_inference import B3IntelligentInference

# Test queries - simple, diverse set
TEST_QUERIES = [
    "What does a sunset look like?",
    "How are you today?",
    "What is photosynthesis?",
    "Tell me about the ocean",
    "Describe a rainbow"
]

# Model checkpoints to test (in priority order)
MODEL_CHECKPOINTS = [
    "F:/models/checkpoints/b3/b3_massive_final.pth",           # Oct 3, 10:05 AM
    "F:/models/checkpoints/b3/b3_distill_stage4_final.pth",    # Oct 4, 3:25 AM
    "F:/models/checkpoints/b3/b3_finetuned_epoch1.pth",        # Oct 4, 8:19 AM
    "F:/models/checkpoints/b3/b3_distill_stage3_final.pth",    # Oct 3, 10:46 PM
    "F:/models/checkpoints/b3/b3_finetuned_best.pth",          # Oct 4, 8:32 AM (current - known bad)
]

def is_generic_response(response: str) -> bool:
    """Check if response is a generic clarification request"""
    generic_patterns = [
        "could you rephrase",
        "could you tell me more",
        "could you provide more",
        "what specifically",
        "tell me more",
        "provide more details",
        "add more details",
        "could you clarify",
        "can you elaborate",
        "i'd like to help",
        "i'd be happy to help",
        "that's an interesting question",
        "great question"
    ]

    response_lower = response.lower()
    return any(pattern in response_lower for pattern in generic_patterns)

def evaluate_response_quality(query: str, response: str) -> tuple[float, bool]:
    """
    Evaluate response quality
    Returns: (quality_score, is_substantive)
    """
    is_generic = is_generic_response(response)

    # Check for substantive content
    has_description = any(word in response.lower() for word in
                         ['colors', 'appears', 'looks', 'features', 'process', 'contains', 'includes'])
    has_detail = len(response.split()) > 15
    any(char.isupper() for char in response[1:])  # Proper nouns

    if is_generic:
        return 1.0, False

    if has_description and has_detail:
        return 4.5, True
    elif has_description or has_detail:
        return 3.5, True
    else:
        return 2.5, True

def test_model_checkpoint(model_path: str) -> dict:
    """Test a single model checkpoint with sample queries"""

    print(f"\n{'='*80}")
    print(f"Testing: {Path(model_path).name}")
    print(f"{'='*80}")

    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return {
            'model': Path(model_path).name,
            'status': 'not_found',
            'avg_quality': 0.0,
            'generic_rate': 100.0,
            'responses': []
        }

    # Get file info
    file_size_mb = os.path.getsize(model_path) / (1024 * 1024)
    file_time = datetime.fromtimestamp(os.path.getmtime(model_path))
    print(f"Size: {file_size_mb:.2f} MB")
    print(f"Modified: {file_time.strftime('%b %d, %Y %I:%M %p')}")

    try:
        # Initialize inference system
        print("\n🔄 Loading model...")
        inference_system = B3IntelligentInference(
            checkpoint_path=model_path
        )
        print("✅ Model loaded successfully")

        # Test queries
        results = []
        qualities = []
        generic_count = 0

        for i, query in enumerate(TEST_QUERIES, 1):
            print(f"\n--- Query {i}/{len(TEST_QUERIES)} ---")
            print(f"Q: {query}")

            start_time = time.time()
            result = inference_system.generate_with_fallback(query, max_tokens=50, temperature=0.9, verbose=False)
            response = result['response']
            elapsed_ms = (time.time() - start_time) * 1000

            quality, is_substantive = evaluate_response_quality(query, response)
            qualities.append(quality)

            if not is_substantive:
                generic_count += 1

            # Truncate long responses for display
            display_response = response if len(response) <= 100 else response[:97] + "..."

            print(f"A: {display_response}")
            print(f"Quality: {quality:.1f}/5.0 | Substantive: {is_substantive} | Time: {elapsed_ms:.0f}ms")

            results.append({
                'query': query,
                'response': response,
                'quality': quality,
                'is_substantive': is_substantive,
                'time_ms': elapsed_ms
            })

        avg_quality = sum(qualities) / len(qualities)
        generic_rate = (generic_count / len(TEST_QUERIES)) * 100

        # Summary
        print(f"\n{'='*80}")
        print(f"SUMMARY: {Path(model_path).name}")
        print(f"{'='*80}")
        print(f"Average Quality:  {avg_quality:.2f}/5.0")
        print(f"Generic Rate:     {generic_rate:.0f}%")
        print(f"Substantive:      {len(TEST_QUERIES) - generic_count}/{len(TEST_QUERIES)}")

        if avg_quality >= 4.0 and generic_rate <= 20:
            print("✅ EXCELLENT - This model produces Phase 1 quality!")
        elif avg_quality >= 3.5 and generic_rate <= 40:
            print("⚠️  GOOD - This model is usable but could be better")
        elif avg_quality >= 2.5:
            print("⚠️  FAIR - This model produces some substantive content")
        else:
            print("❌ POOR - This model produces mostly generic responses")

        return {
            'model': Path(model_path).name,
            'model_path': model_path,
            'status': 'tested',
            'avg_quality': avg_quality,
            'generic_rate': generic_rate,
            'substantive_count': len(TEST_QUERIES) - generic_count,
            'file_size_mb': file_size_mb,
            'file_modified': file_time.isoformat(),
            'responses': results
        }

    except Exception as e:
        print(f"❌ Error testing model: {e}")
        import traceback
        traceback.print_exc()

        return {
            'model': Path(model_path).name,
            'status': 'error',
            'error': str(e),
            'avg_quality': 0.0,
            'generic_rate': 100.0,
            'responses': []
        }

def main():
    """Test all model checkpoints and identify Phase 1 quality model"""

    print("="*80)
    print("MODEL CHECKPOINT VALIDATOR")
    print("="*80)
    print(f"Testing {len(MODEL_CHECKPOINTS)} model checkpoints")
    print("Target: ≥4.0/5.0 quality, ≤20% generic rate (Phase 1 baseline: 4.32/5.0)")
    print()

    all_results = []

    for checkpoint in MODEL_CHECKPOINTS:
        result = test_model_checkpoint(checkpoint)
        all_results.append(result)

        # If we found an excellent model, note it
        if result['status'] == 'tested' and result['avg_quality'] >= 4.0:
            print(f"\n🎯 FOUND PHASE 1 QUALITY MODEL: {result['model']}")
            print(f"   Quality: {result['avg_quality']:.2f}/5.0")
            print(f"   Generic Rate: {result['generic_rate']:.0f}%")

    # Final summary
    print(f"\n{'='*80}")
    print("FINAL COMPARISON")
    print(f"{'='*80}")
    print(f"{'Model':<40} {'Quality':>10} {'Generic':>10} {'Status':>15}")
    print("-"*80)

    for result in all_results:
        if result['status'] == 'tested':
            quality_str = f"{result['avg_quality']:.2f}/5.0"
            generic_str = f"{result['generic_rate']:.0f}%"

            if result['avg_quality'] >= 4.0:
                status = "✅ EXCELLENT"
            elif result['avg_quality'] >= 3.5:
                status = "⚠️  GOOD"
            elif result['avg_quality'] >= 2.5:
                status = "⚠️  FAIR"
            else:
                status = "❌ POOR"
        else:
            quality_str = "N/A"
            generic_str = "N/A"
            status = f"❌ {result['status'].upper()}"

        print(f"{result['model']:<40} {quality_str:>10} {generic_str:>10} {status:>15}")

    # Recommendation
    print(f"\n{'='*80}")
    print("RECOMMENDATION")
    print(f"{'='*80}")

    best_models = [r for r in all_results
                   if r['status'] == 'tested' and r['avg_quality'] >= 4.0]

    if best_models:
        best = max(best_models, key=lambda x: x['avg_quality'])
        print(f"✅ Use this model for Phase 3: {best['model']}")
        print(f"   Path: {best['model_path']}")
        print(f"   Quality: {best['avg_quality']:.2f}/5.0")
        print(f"   Generic Rate: {best['generic_rate']:.0f}%")
        print("\n   Update b3_rag_inference.py line 88 to use this model path.")
    else:
        print("⚠️  No model achieved Phase 1 quality (≥4.0/5.0)")
        print("   Need to investigate Phase 1 original configuration")

        # Show best available
        tested = [r for r in all_results if r['status'] == 'tested']
        if tested:
            best_available = max(tested, key=lambda x: x['avg_quality'])
            print(f"\n   Best available: {best_available['model']}")
            print(f"   Quality: {best_available['avg_quality']:.2f}/5.0")
            print(f"   Generic Rate: {best_available['generic_rate']:.0f}%")

    print()

if __name__ == "__main__":
    main()
