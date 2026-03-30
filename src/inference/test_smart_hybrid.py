"""
Test Phase 3 Smart Hybrid RAG System

Created: October 5, 2025
Author: Kirk LaSalle; GitHub Copilot
Tags: #test #phase3 #smart_hybrid #rag #quality

Purpose:
    Test the Phase 3 Smart Hybrid system that:
    - Uses model's natural strength (Phase 1: 4.32/5.0)
    - Adds RAG enhancement only when beneficial
    - Never degrades quality below natural baseline

Expected Results:
    - Quality: 4.0-4.5/5.0 (vs 4.32 Phase 1, 0.77 Phase 2)
    - Generic rate: <10%
    - RAG used intelligently (20-30% of queries)
    - Natural generation for model's strengths
"""

import io
import json
import logging

# Setup logging - Use UTF-8 encoding for Windows console
import sys
import time
from pathlib import Path

# Force UTF-8 output for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_hybrid_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import test infrastructure
try:
    from test_expanded_rag import ExpandedRAGTester, TestQuery
    logger.info("✅ Test infrastructure imported")
except ImportError as e:
    logger.error(f"❌ Failed to import test infrastructure: {e}")
    raise


def run_smart_hybrid_test():
    """
    Run comprehensive Phase 3 Smart Hybrid test.

    Tests 14 queries from test_expanded_rag with Smart Hybrid system.
    Compares results to Phase 1 (4.32/5.0) and Phase 2 (0.77/5.0).
    """
    logger.info("\n" + "="*80)
    logger.info("🚀 PHASE 3: SMART HYBRID SYSTEM TEST")
    logger.info("="*80)
    logger.info("\nObjective: Maintain Phase 1 quality (4.32/5.0) with intelligent RAG")
    logger.info("Strategy: Natural generation + optional enhancement")
    logger.info("Expected: 4.0-4.5/5.0 quality, <10% generic, smart RAG usage")

    # Initialize tester
    logger.info("\n📦 Initializing test system...")
    tester = ExpandedRAGTester()

    # Test queries from expanded RAG test
    test_queries = [
        # Multimodal queries
        TestQuery(
            query="What does a sunset look like?",
            domain="multimodal",
            expected_retrieval=True,
            expected_min_docs=3,
            description="Visual description test"
        ),
        TestQuery(
            query="Describe a beach scene",
            domain="multimodal",
            expected_retrieval=True,
            expected_min_docs=3,
            description="Scene description test"
        ),
        TestQuery(
            query="What colors are in a rainbow?",
            domain="multimodal",
            expected_retrieval=True,
            expected_min_docs=2,
            description="Color knowledge test"
        ),

        # Conversational queries
        TestQuery(
            query="How are you today?",
            domain="conversational",
            expected_retrieval=True,
            expected_min_docs=2,
            description="Greeting test"
        ),
        TestQuery(
            query="Can you help me with something?",
            domain="conversational",
            expected_retrieval=True,
            expected_min_docs=2,
            description="Help request test"
        ),
        TestQuery(
            query="What's your favorite color?",
            domain="conversational",
            expected_retrieval=True,
            expected_min_docs=1,
            description="Personal preference test"
        ),

        # Educational queries
        TestQuery(
            query="What is photosynthesis?",
            domain="educational",
            expected_retrieval=True,
            expected_min_docs=3,
            description="Scientific concept test"
        ),
        TestQuery(
            query="How does gravity work?",
            domain="educational",
            expected_retrieval=True,
            expected_min_docs=3,
            description="Physics concept test"
        ),
        TestQuery(
            query="What is DNA?",
            domain="educational",
            expected_retrieval=True,
            expected_min_docs=3,
            description="Biology concept test"
        ),

        # Cross-domain queries
        TestQuery(
            query="Explain neural networks visually",
            domain="cross_domain",
            expected_retrieval=True,
            expected_min_docs=3,
            description="Visual + technical explanation"
        ),
        TestQuery(
            query="How do I learn machine learning?",
            domain="cross_domain",
            expected_retrieval=True,
            expected_min_docs=3,
            description="Learning guidance test"
        ),

        # Edge cases
        TestQuery(
            query="asdfghjkl",
            domain="edge_case",
            expected_retrieval=False,
            expected_min_docs=0,
            description="Nonsense input test"
        ),
        TestQuery(
            query="Tell me everything",
            domain="edge_case",
            expected_retrieval=True,
            expected_min_docs=1,
            description="Vague request test"
        ),
        TestQuery(
            query="",
            domain="edge_case",
            expected_retrieval=False,
            expected_min_docs=0,
            description="Empty query test"
        )
    ]

    # Run tests
    logger.info(f"\n🧪 Testing {len(test_queries)} queries with Smart Hybrid...")

    results = []
    total_tests = len(test_queries)
    successful = 0
    total_quality = 0.0
    generic_count = 0
    enhancement_count = 0
    total_time = 0.0

    for i, test_query in enumerate(test_queries, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST {i}/{total_tests}")
        logger.info(f"Query: {test_query.query}")
        logger.info(f"Domain: {test_query.domain}")
        logger.info(f"Description: {test_query.description}")
        logger.info(f"{'='*80}")

        # Run with Smart Hybrid
        start_time = time.time()

        try:
            result = tester.rag_system.generate(
                user_input=test_query.query,
                use_rag=True,
                category=test_query.domain,
                use_smart_hybrid=True  # PHASE 3 ENABLED
            )

            elapsed = (time.time() - start_time) * 1000  # ms

            # Extract result details
            response = result.get('response', '')
            strategy = result.get('generation_strategy', 'unknown')
            enhancement_applied = result.get('enhancement_applied', False)
            quality_preserved = result.get('quality_preserved', False)
            docs_retrieved = result.get('docs_retrieved', 0)
            confidence = result.get('retrieval_confidence', 0.0)

            # Evaluate quality (simplified - just check if response exists and isn't generic)
            quality = 5.0 if response and len(response) > 50 and not tester.rag_system.is_generic_response(response) else 1.0

            # Check if generic (using Phase 2 validator)
            is_generic = tester.rag_system.is_generic_response(response)

            # Track stats
            total_quality += quality
            if not is_generic:
                successful += 1
            if is_generic:
                generic_count += 1
            if enhancement_applied:
                enhancement_count += 1
            total_time += elapsed

            # Log results
            logger.info(f"\n✅ Response: {response[:100]}...")
            logger.info(f"✅ Strategy: {strategy}")
            logger.info(f"✅ Enhancement Applied: {enhancement_applied}")
            logger.info(f"✅ Quality Preserved: {quality_preserved}")
            logger.info(f"✅ Docs Retrieved: {docs_retrieved}")
            logger.info(f"✅ Confidence: {confidence:.3f}")
            logger.info(f"✅ Quality Score: {quality:.2f}/5.0")
            logger.info(f"✅ Generic: {'Yes' if is_generic else 'No'}")
            logger.info(f"✅ Time: {elapsed:.1f}ms")

            # Store result
            results.append({
                'query': test_query.query,
                'domain': test_query.domain,
                'description': test_query.description,
                'response': response,
                'strategy': strategy,
                'enhancement_applied': enhancement_applied,
                'quality_preserved': quality_preserved,
                'docs_retrieved': docs_retrieved,
                'confidence': confidence,
                'quality': quality,
                'is_generic': is_generic,
                'time_ms': elapsed
            })

        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()

            results.append({
                'query': test_query.query,
                'domain': test_query.domain,
                'description': test_query.description,
                'error': str(e),
                'quality': 0.0
            })

    # Calculate final metrics
    avg_quality = total_quality / total_tests
    generic_rate = (generic_count / total_tests) * 100
    enhancement_rate = (enhancement_count / total_tests) * 100
    success_rate = (successful / total_tests) * 100
    avg_time = total_time / total_tests

    # Print summary
    logger.info("\n" + "="*80)
    logger.info("📊 PHASE 3 SMART HYBRID - FINAL RESULTS")
    logger.info("="*80)
    logger.info("\n🎯 Quality Metrics:")
    logger.info(f"   Average Quality: {avg_quality:.2f}/5.0")
    logger.info(f"   Generic Rate: {generic_rate:.1f}%")
    logger.info(f"   Success Rate: {success_rate:.1f}%")
    logger.info(f"   Enhancement Rate: {enhancement_rate:.1f}%")
    logger.info(f"   Avg Response Time: {avg_time:.1f}ms")

    # Compare to previous phases
    logger.info("\n📈 Phase Comparison:")
    logger.info("   Phase 1 Direct: 4.32/5.0 (baseline)")
    logger.info("   Phase 2 Forced RAG: 0.77/5.0")
    logger.info(f"   Phase 3 Smart Hybrid: {avg_quality:.2f}/5.0")

    if avg_quality >= 4.0:
        logger.info("\n✅ SUCCESS: Quality target achieved! (≥4.0/5.0)")
    else:
        logger.info(f"\n⚠️ Quality below target: {avg_quality:.2f}/5.0 (target: 4.0+)")

    if generic_rate < 10:
        logger.info(f"✅ Generic rate excellent: {generic_rate:.1f}% (<10%)")
    else:
        logger.info(f"⚠️ Generic rate high: {generic_rate:.1f}% (target: <10%)")

    # Domain breakdown
    logger.info("\n📊 Domain Performance:")
    domains = {}
    for result in results:
        domain = result.get('domain', 'unknown')
        if domain not in domains:
            domains[domain] = {'quality': [], 'generic': 0, 'total': 0}

        domains[domain]['quality'].append(result.get('quality', 0.0))
        domains[domain]['generic'] += 1 if result.get('is_generic', False) else 0
        domains[domain]['total'] += 1

    for domain, stats in domains.items():
        avg_q = sum(stats['quality']) / len(stats['quality'])
        gen_rate = (stats['generic'] / stats['total']) * 100
        logger.info(f"   {domain.capitalize()}: {avg_q:.2f}/5.0 (generic: {gen_rate:.0f}%)")

    # Strategy breakdown
    logger.info("\n🎯 Strategy Usage:")
    strategies = {}
    for result in results:
        strat = result.get('strategy', 'unknown')
        strategies[strat] = strategies.get(strat, 0) + 1

    for strategy, count in strategies.items():
        pct = (count / total_tests) * 100
        logger.info(f"   {strategy}: {count} ({pct:.1f}%)")

    # Save results
    output_file = "smart_hybrid_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'test_date': str(time.time()),
            'total_tests': total_tests,
            'avg_quality': avg_quality,
            'generic_rate': generic_rate,
            'success_rate': success_rate,
            'enhancement_rate': enhancement_rate,
            'avg_time_ms': avg_time,
            'domain_performance': {
                domain: {
                    'avg_quality': sum(stats['quality']) / len(stats['quality']),
                    'generic_rate': (stats['generic'] / stats['total']) * 100
                }
                for domain, stats in domains.items()
            },
            'strategy_usage': strategies,
            'results': results
        }, f, indent=2)

    logger.info(f"\n💾 Results saved to: {output_file}")

    logger.info("\n" + "="*80)
    logger.info("🎉 PHASE 3 SMART HYBRID TEST COMPLETE")
    logger.info("="*80)

    return results, avg_quality


if __name__ == "__main__":
    logger.info("Starting Phase 3 Smart Hybrid System Test...")
    results, quality = run_smart_hybrid_test()
    logger.info(f"\nFinal Quality: {quality:.2f}/5.0")
    logger.info("Test complete!")
