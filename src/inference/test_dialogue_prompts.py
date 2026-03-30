"""
Phase 2 Tier 1 - Dialogue Prompt Smoke Test

Quick test to verify dialogue prompt format implementation.
Tests multimodal and conversational categories with Phase 2 dialogue prompts
vs Phase 1 system prompts.

Expected: Dialogue prompts show context usage through examples, potentially
reducing generic responses.

Created: October 4, 2025 8:45 PM
Author: GitHub Copilot
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.inference.b3_rag_inference import B3RAGInference


def test_dialogue_vs_system_prompt():
    """
    Compare dialogue format (Phase 2) vs system prompt (Phase 1) on key queries.

    Focus on multimodal and conversational categories where RAG usage was 100%.
    """
    print("="*80)
    print("PHASE 2 TIER 1: DIALOGUE PROMPT SMOKE TEST")
    print("="*80)
    print()

    # Initialize system
    print("Initializing B3 RAG system...")
    rag_system = B3RAGInference(
        model_path="F:/models/checkpoints/b3/b3_massive_final.pth",
        f_data_root="F:/data"
    )
    print("✅ System initialized")
    print()

    # Test queries - focus on multimodal and conversational
    test_cases = [
        {
            'query': "Show me pictures of cats",
            'category': "multimodal",
            'description': "Multimodal query - 100% RAG in Phase 1"
        },
        {
            'query': "What does a sunset look like?",
            'category': "multimodal",
            'description': "Multimodal visual description"
        },
        {
            'query': "How do you greet someone in the morning?",
            'category': "conversational",
            'description': "Conversational query - 100% RAG in Phase 1"
        },
        {
            'query': "What's a good way to ask for help?",
            'category': "conversational",
            'description': "Conversational social advice"
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        query = test_case['query']
        category = test_case['category']
        description = test_case['description']

        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_cases)}: {description}")
        print(f"Query: \"{query}\"")
        print(f"Category: {category}")
        print(f"{'='*80}\n")

        # Test with Phase 1 system prompt
        print("--- PHASE 1: System Prompt Format ---")
        start_time = time.time()
        result_phase1 = rag_system.generate(
            user_input=query,
            use_rag=True,
            category=category,
            max_length=150,
            use_dialogue_prompt=False  # Phase 1
        )
        phase1_time = time.time() - start_time

        print("\n📊 Phase 1 Results:")
        print(f"   Response: {result_phase1['response']}")
        print(f"   RAG Used: {result_phase1['rag_used']}")
        print(f"   Docs Retrieved: {result_phase1['docs_retrieved']}")
        print(f"   Confidence: {result_phase1.get('retrieval_confidence', 0):.3f}")
        print(f"   Time: {phase1_time:.2f}s")
        print(f"   Strategy: {result_phase1.get('prompt_strategy', 'unknown')}")

        # Check if generic
        phase1_generic = any(phrase in result_phase1['response'].lower() for phrase in [
            "i'm here to help",
            "what would you like to know",
            "could you tell me more",
            "what specifically",
            "i'd be happy to help"
        ])
        print(f"   Generic: {'⚠️ YES' if phase1_generic else '✅ NO'}")

        print("\n" + "-"*80 + "\n")

        # Test with Phase 2 dialogue prompt
        print("--- PHASE 2: Dialogue Format ---")
        start_time = time.time()
        result_phase2 = rag_system.generate(
            user_input=query,
            use_rag=True,
            category=category,
            max_length=150,
            use_dialogue_prompt=True  # Phase 2
        )
        phase2_time = time.time() - start_time

        print("\n📊 Phase 2 Results:")
        print(f"   Response: {result_phase2['response']}")
        print(f"   RAG Used: {result_phase2['rag_used']}")
        print(f"   Docs Retrieved: {result_phase2['docs_retrieved']}")
        print(f"   Confidence: {result_phase2.get('retrieval_confidence', 0):.3f}")
        print(f"   Time: {phase2_time:.2f}s")
        print(f"   Strategy: {result_phase2.get('prompt_strategy', 'unknown')}")

        # Check if generic
        phase2_generic = any(phrase in result_phase2['response'].lower() for phrase in [
            "i'm here to help",
            "what would you like to know",
            "could you tell me more",
            "what specifically",
            "i'd be happy to help"
        ])
        print(f"   Generic: {'⚠️ YES' if phase2_generic else '✅ NO'}")

        # Compare
        print("\n🔍 Comparison:")
        print(f"   Phase 1 Generic: {'YES' if phase1_generic else 'NO'}")
        print(f"   Phase 2 Generic: {'YES' if phase2_generic else 'NO'}")
        print(f"   Improvement: {'✅ YES' if phase1_generic and not phase2_generic else '❌ NO'}")
        print(f"   Time Difference: {phase2_time - phase1_time:+.2f}s")

        results.append({
            'query': query,
            'category': category,
            'phase1_response': result_phase1['response'],
            'phase1_generic': phase1_generic,
            'phase1_time': phase1_time,
            'phase2_response': result_phase2['response'],
            'phase2_generic': phase2_generic,
            'phase2_time': phase2_time,
            'improved': phase1_generic and not phase2_generic
        })

    # Summary
    print(f"\n\n{'='*80}")
    print("SMOKE TEST SUMMARY")
    print(f"{'='*80}\n")

    total_tests = len(results)
    phase1_generic_count = sum(1 for r in results if r['phase1_generic'])
    phase2_generic_count = sum(1 for r in results if r['phase2_generic'])
    improvements = sum(1 for r in results if r['improved'])

    print(f"Total Tests: {total_tests}")
    print(f"Phase 1 Generic Responses: {phase1_generic_count}/{total_tests} ({phase1_generic_count/total_tests*100:.1f}%)")
    print(f"Phase 2 Generic Responses: {phase2_generic_count}/{total_tests} ({phase2_generic_count/total_tests*100:.1f}%)")
    print(f"Improvements: {improvements}/{total_tests} ({improvements/total_tests*100:.1f}%)")

    avg_phase1_time = sum(r['phase1_time'] for r in results) / total_tests
    avg_phase2_time = sum(r['phase2_time'] for r in results) / total_tests
    print(f"\nAvg Time Phase 1: {avg_phase1_time:.2f}s")
    print(f"Avg Time Phase 2: {avg_phase2_time:.2f}s")
    print(f"Time Difference: {avg_phase2_time - avg_phase1_time:+.2f}s")

    # Assessment
    print(f"\n{'='*80}")
    print("ASSESSMENT")
    print(f"{'='*80}\n")

    if improvements >= total_tests * 0.5:
        print("✅ TIER 1 SUCCESS: Dialogue prompts show significant improvement")
        print("   Proceed to Tier 2 (validation & retry logic)")
    elif improvements >= total_tests * 0.25:
        print("⚠️ TIER 1 PARTIAL: Some improvement, but not significant")
        print("   Proceed to Tier 2 with caution")
    else:
        print("❌ TIER 1 INSUFFICIENT: Dialogue prompts don't help")
        print("   Consider alternative strategies (model replacement)")

    print("\nNext Steps:")
    if improvements > 0:
        print("1. Implement Tier 2 validation & retry logic")
        print("2. Combine dialogue prompts with response validation")
        print("3. Expected: Further quality improvement with retry on generic responses")
    else:
        print("1. Review example quality in dialogue prompts")
        print("2. Try stronger context-forced generation")
        print("3. Consider model replacement if no improvement")


if __name__ == "__main__":
    test_dialogue_vs_system_prompt()
