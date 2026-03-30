"""
Phase 2 Tier 1+2 - Complete Validation Test

Tests the full Phase 2 implementation:
- Tier 1: Dialogue format prompts
- Tier 2: Response validation & retry logic

Expected: Quality improvement from 0.62 → 2.0-2.5/5.0
Generic response rate reduction from 100% → <30%

Created: October 4, 2025 9:00 PM
Author: GitHub Copilot
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.inference.b3_rag_inference import B3RAGInference


def test_phase2_complete():
    """
    Test Phase 2 Tier 1+2: Dialogue prompts + retry logic.

    Compare Phase 1 (system prompts) vs Phase 2 (dialogue + validation) on
    the same queries that showed generic responses in previous tests.
    """
    print("="*80)
    print("PHASE 2 TIER 1+2: COMPLETE VALIDATION TEST")
    print("="*80)
    print("\nDialogue Format + Response Validation + Retry Logic")
    print()

    # Initialize system
    print("Initializing B3 RAG system...")
    rag_system = B3RAGInference(
        model_path="F:/models/checkpoints/b3/b3_massive_final.pth",
        f_data_root="F:/data"
    )
    print("✅ System initialized")
    print()

    # Test queries - focus on cases that had 100% generic in Phase 1
    test_cases = [
        {
            'query': "Show me pictures of cats",
            'category': "multimodal",
            'phase1_generic': True,
            'phase1_quality': 0.57
        },
        {
            'query': "What does a sunset look like?",
            'category': "multimodal",
            'phase1_generic': True,
            'phase1_quality': 0.51
        },
        {
            'query': "Describe a mountain landscape",
            'category': "multimodal",
            'phase1_generic': True,
            'phase1_quality': 0.65
        },
        {
            'query': "How do you greet someone in the morning?",
            'category': "conversational",
            'phase1_generic': True,
            'phase1_quality': 0.51
        },
        {
            'query': "What's a good way to ask for help?",
            'category': "conversational",
            'phase1_generic': True,
            'phase1_quality': 0.65
        },
        {
            'query': "What are the basics of arithmetic?",
            'category': "educational",
            'phase1_generic': True,
            'phase1_quality': 0.57
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        query = test_case['query']
        category = test_case['category']

        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_cases)}: {category.upper()}")
        print(f"Query: \"{query}\"")
        print(f"Phase 1 Baseline: Generic={test_case['phase1_generic']}, Quality={test_case['phase1_quality']}")
        print(f"{'='*80}\n")

        # Test with Phase 2 (retry enabled)
        print("--- PHASE 2: Dialogue + Validation + Retry ---")
        start_time = time.time()
        result_phase2 = rag_system.generate(
            user_input=query,
            use_rag=True,
            category=category,
            max_length=150,
            use_retry=True  # Enable full Phase 2 logic
        )
        phase2_time = time.time() - start_time

        # Extract results
        response = result_phase2['response']
        attempts = result_phase2.get('attempts', 1)
        retry_reason = result_phase2.get('retry_reason', 'none')
        strategy = result_phase2.get('prompt_strategy', 'unknown')
        is_generic = result_phase2.get('is_generic', False)
        uses_context = result_phase2.get('uses_context', False)

        print("\n📊 Phase 2 Results:")
        print(f"   Response: {response}")
        print(f"   RAG Used: {result_phase2['rag_used']}")
        print(f"   Docs Retrieved: {result_phase2['docs_retrieved']}")
        print(f"   Confidence: {result_phase2.get('retrieval_confidence', 0):.3f}")
        print(f"   Attempts: {attempts}")
        print(f"   Strategy: {strategy}")
        print(f"   Retry Reason: {retry_reason}")
        print(f"   Time: {phase2_time:.2f}s")
        print(f"   Generic: {'⚠️ YES' if is_generic else '✅ NO'}")
        print(f"   Uses Context: {'✅ YES' if uses_context else '⚠️ NO'}")

        # Assess quality improvement
        improved = test_case['phase1_generic'] and not is_generic

        print("\n🔍 Assessment:")
        print("   Phase 1 Generic: YES")
        print(f"   Phase 2 Generic: {'YES' if is_generic else 'NO'}")
        print(f"   Improvement: {'✅ YES' if improved else '❌ NO'}")
        print(f"   Context Usage: {'✅ YES' if uses_context else '⚠️ NO'}")

        results.append({
            'query': query,
            'category': category,
            'phase1_generic': test_case['phase1_generic'],
            'phase1_quality': test_case['phase1_quality'],
            'phase2_response': response,
            'phase2_generic': is_generic,
            'phase2_uses_context': uses_context,
            'phase2_time': phase2_time,
            'attempts': attempts,
            'strategy': strategy,
            'improved': improved
        })

    # Summary
    print(f"\n\n{'='*80}")
    print("PHASE 2 COMPLETE VALIDATION SUMMARY")
    print(f"{'='*80}\n")

    total_tests = len(results)
    phase1_generic_count = sum(1 for r in results if r['phase1_generic'])
    phase2_generic_count = sum(1 for r in results if r['phase2_generic'])
    improvements = sum(1 for r in results if r['improved'])
    context_usage = sum(1 for r in results if r['phase2_uses_context'])

    print(f"Total Tests: {total_tests}")
    print(f"Phase 1 Generic Responses: {phase1_generic_count}/{total_tests} (100.0%) [baseline]")
    print(f"Phase 2 Generic Responses: {phase2_generic_count}/{total_tests} ({phase2_generic_count/total_tests*100:.1f}%)")
    print(f"Improvements: {improvements}/{total_tests} ({improvements/total_tests*100:.1f}%)")
    print(f"Context Usage: {context_usage}/{total_tests} ({context_usage/total_tests*100:.1f}%)")

    avg_attempts = sum(r['attempts'] for r in results) / total_tests
    avg_time = sum(r['phase2_time'] for r in results) / total_tests

    print(f"\nAvg Attempts: {avg_attempts:.1f}")
    print(f"Avg Time: {avg_time:.2f}s")

    # Strategy breakdown
    strategies = {}
    for r in results:
        strategy = r['strategy']
        strategies[strategy] = strategies.get(strategy, 0) + 1

    print("\nStrategy Distribution:")
    for strategy, count in sorted(strategies.items()):
        print(f"   {strategy}: {count}/{total_tests} ({count/total_tests*100:.1f}%)")

    # Assessment
    print(f"\n{'='*80}")
    print("ASSESSMENT")
    print(f"{'='*80}\n")

    generic_reduction = (phase1_generic_count - phase2_generic_count) / phase1_generic_count * 100

    print(f"Generic Response Reduction: {generic_reduction:.1f}%")
    print("   Target: >= 50% reduction (from 100% to <50%)")
    print(f"   Achieved: {'✅ YES' if generic_reduction >= 50 else '❌ NO'}")

    print(f"\nContext Usage Rate: {context_usage/total_tests*100:.1f}%")
    print("   Target: >= 70%")
    print(f"   Achieved: {'✅ YES' if context_usage >= total_tests*0.7 else '❌ NO'}")

    # Final verdict
    print(f"\n{'='*80}")
    print("VERDICT")
    print(f"{'='*80}\n")

    if generic_reduction >= 50 and context_usage >= total_tests * 0.7:
        print("✅ PHASE 2 SUCCESS: Quality optimization working!")
        print("   - Generic responses reduced by >= 50%")
        print("   - Context usage >= 70%")
        print("   - Ready for full expanded RAG test (14 queries)")
        print("\nNext Steps:")
        print("1. Run full expanded RAG test suite")
        print("2. Expected quality: 0.62 → 2.0-2.5/5.0")
        print("3. If successful, proceed to Phase 3 optimizations")
    elif generic_reduction >= 30 or context_usage >= total_tests * 0.5:
        print("⚠️ PHASE 2 PARTIAL: Some improvement but not target")
        print(f"   - Generic reduction: {generic_reduction:.1f}% (target: 50%)")
        print(f"   - Context usage: {context_usage/total_tests*100:.1f}% (target: 70%)")
        print("\nNext Steps:")
        print("1. Consider Tier 3 (context-forced generation)")
        print("2. Try alternative model architectures")
        print("3. Review dialogue examples for quality")
    else:
        print("❌ PHASE 2 INSUFFICIENT: Retry logic not helping")
        print(f"   - Generic reduction: {generic_reduction:.1f}% (target: 50%)")
        print(f"   - Context usage: {context_usage/total_tests*100:.1f}% (target: 70%)")
        print("\nNext Steps:")
        print("1. CRITICAL: Model replacement required")
        print("2. Current B3-Hope cannot follow instructions")
        print("3. Consider instruction-tuned alternatives")
        print("4. OR: Fine-tune B3 on RAG instruction dataset")


if __name__ == "__main__":
    test_phase2_complete()
