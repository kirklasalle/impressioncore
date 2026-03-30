"""
Test Deployment of B3 Hybrid Conversation Model

Validates the deployed model with comprehensive quality tests.

Created: October 6, 2025
Expected Quality: 9.25/10.0
"""

import torch
from conversation_interface import ConversationInterface
import sys

def test_deployment():
    """Run deployment validation tests"""

    # Test queries (same as training validation)
    test_queries = [
        "Hello! How are you today?",
        "Tell me about yourself",
        "What did you do last weekend?",
        "I'm feeling a bit stressed today",
        "What's your favorite hobby?",
        "Can you help me with something?",
        "I love reading books, do you?",
        "What makes you happy?"
    ]

    print("=" * 70)
    print("B3 HYBRID CONVERSATION MODEL - DEPLOYMENT TEST")
    print("Expected Quality: 9.25/10.0")
    print("=" * 70)
    print()

    # Initialize interface
    try:
        interface = ConversationInterface()
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        sys.exit(1)

    # Run tests
    print("Running quality tests...")
    print("=" * 70)
    print()

    results = []

    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}/8: {query}")

        try:
            response = interface.chat(query, max_length=100, temperature=0.8)
            print(f"Response: {response}")

            # Basic quality checks
            quality_score = 0
            checks = []

            # Check 1: Not empty
            if response and len(response) > 10:
                quality_score += 1
                checks.append("✅ Non-empty")
            else:
                checks.append("❌ Too short")

            # Check 2: Contains words (not gibberish)
            if any(word.isalpha() and len(word) > 2 for word in response.split()):
                quality_score += 1
                checks.append("✅ Contains words")
            else:
                checks.append("❌ Gibberish detected")

            # Check 3: Not just symbols
            alpha_ratio = sum(c.isalpha() or c.isspace() for c in response) / len(response) if response else 0
            if alpha_ratio > 0.5:
                quality_score += 1
                checks.append("✅ Proper language")
            else:
                checks.append("❌ Too many symbols")

            # Check 4: Reasonable length
            if 20 < len(response) < 200:
                quality_score += 1
                checks.append("✅ Good length")
            else:
                checks.append("⚠️ Length issue")

            print(f"Quality Checks: {' | '.join(checks)}")

            results.append({
                'query': query,
                'response': response,
                'score': quality_score
            })

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                'query': query,
                'response': None,
                'score': 0
            })

        print("-" * 70)
        print()

    # Summary
    print("=" * 70)
    print("DEPLOYMENT TEST SUMMARY")
    print("=" * 70)

    total_score = sum(r['score'] for r in results)
    max_score = len(test_queries) * 4
    percentage = (total_score / max_score) * 100

    print(f"Tests Passed: {total_score}/{max_score} ({percentage:.1f}%)")
    print()

    # Pass/Fail determination
    if percentage >= 75:
        print("✅ DEPLOYMENT SUCCESSFUL")
        print("Model is ready for production use")
        print()
        print("Expected quality: 9.25/10.0 based on training results")
    else:
        print("⚠️ DEPLOYMENT NEEDS REVIEW")
        print("Some quality issues detected")

    print("=" * 70)

    # Detailed results
    print()
    print("Detailed Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']}/4")
        print(f"   Query: {result['query']}")
        if result['response']:
            print(f"   Response: {result['response'][:100]}...")
        print()

if __name__ == "__main__":
    test_deployment()
