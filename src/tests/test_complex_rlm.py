#!/usr/bin/env python3
"""
Test Complex Multi-step RLM Queries

Tests the RLM policy's ability to handle complex queries that require:
- Context chunking (CONTEXT-CHUNK)
- Semantic search (CONTEXT-SEARCH)
- Recursive decomposition (RECURSION-DEPTH)
- Multi-step reasoning

Created: January 22, 2026
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RLM.ComplexTest")


# Test cases designed to trigger multi-step policy actions
COMPLEX_TEST_CASES = [
    {
        "name": "Long Document Retrieval",
        "query": "What is the relationship between machine learning and deep learning?",
        "context": """
            Machine learning is a subset of artificial intelligence that enables systems to learn
            and improve from experience without being explicitly programmed. It focuses on the
            development of computer programs that can access data and use it to learn for themselves.

            The process begins with observations or data, such as examples, direct experience, or
            instruction, in order to look for patterns in data and make better decisions in the
            future based on the examples that we provide. The primary aim is to allow the computers
            to learn automatically without human intervention or assistance and adjust actions accordingly.

            Deep learning is a subset of machine learning that uses neural networks with many layers
            (hence "deep") to model complex patterns in data. Deep learning algorithms attempt to
            learn high-level features from data in an incremental manner. This eliminates the need
            for domain expertise and hard-core feature extraction.

            Unlike traditional machine learning algorithms that are typically limited to processing
            data in their raw form, deep learning algorithms can process unstructured data such as
            text and images, and automatically extracts the features to differentiate among
            categories. Deep learning models can achieve state-of-the-art accuracy, sometimes
            exceeding human-level performance.

            The key difference is that while machine learning algorithms have to be manually
            programmed with the features to look for, deep learning algorithms learn these
            features automatically from the data using neural networks.
        """,
        "expected_actions": ["CONTEXT-CHUNK", "CONTEXT-SEARCH", "LLM-QUERY", "ANSWER"],
        "min_steps": 2
    },
    {
        "name": "Multi-hop Reasoning",
        "query": "Based on the hierarchy described, what enables deep learning to work?",
        "context": """
            Artificial Intelligence (AI) is the broadest concept that encompasses any technique
            that enables computers to mimic human intelligence.

            Machine Learning (ML) is a subset of AI that uses statistical methods to enable
            machines to improve with experience.

            Deep Learning (DL) is a subset of machine learning that uses multi-layer neural
            networks. These neural networks are designed to work like the human brain, with
            interconnected nodes or "neurons" that process information.

            Neural networks enable deep learning to work by providing the architectural framework
            for learning complex patterns. The key is that neural networks can have many layers,
            allowing them to learn increasingly abstract representations of the data.
        """,
        "expected_actions": ["CONTEXT-SEARCH", "LLM-QUERY", "ANSWER"],
        "min_steps": 1
    },
    {
        "name": "Needle in Haystack",
        "query": "What is the secret code mentioned in the document?",
        "context": """
            This is a test document with a lot of padding text. Lorem ipsum dolor sit amet,
            consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore
            magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
            nisi ut aliquip ex ea commodo consequat.

            More padding text here to make the document longer. Duis aute irure dolor in
            reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

            THE SECRET CODE IS: ALPHA-7749-NEXUS

            More irrelevant text follows. Excepteur sint occaecat cupidatat non proident,
            sunt in culpa qui officia deserunt mollit anim id est laborum. This text is just
            padding to test the search capability.

            Additional context that is not relevant to the query at all.
        """,
        "expected_actions": ["CONTEXT-SEARCH", "ANSWER"],
        "min_steps": 1,
        "expected_answer_contains": "ALPHA-7749-NEXUS"
    }
]


def run_complex_query_tests():
    """Run all complex query test cases."""
    from src.orchestrator.nexus_context_manager import get_rlm_context_manager
    from src.orchestrator.rlm_policy_agent import PolicyAgentConfig, get_policy_agent

    # Configure for testing
    config = PolicyAgentConfig(
        max_episode_steps=10,  # Allow more steps for complex queries
        deterministic=False,   # Use sampling for diversity
    )

    agent = get_policy_agent(config)

    # Load policy
    if not agent.is_ready:
        success = agent.load_policy()
        if not success:
            logger.error("Failed to load policy!")
            return

    results = []

    for test in COMPLEX_TEST_CASES:
        logger.info(f"\n{'='*60}")
        logger.info(f"Test: {test['name']}")
        logger.info(f"Query: {test['query']}")
        logger.info(f"{'='*60}")

        # Create fresh context manager
        cm = get_rlm_context_manager()
        cm.load_context_from_string(test['context'], f"test_{test['name']}")

        # Run episode
        episode = agent.run_episode(
            query=test['query'],
            context=test['context'],
            context_manager=cm
        )

        # Generate answer
        answer_result = agent.generate_answer(
            query=test['query'],
            context=test['context'],
            context_manager=cm
        )

        # Analyze results
        actions_taken = [step['action'] for step in episode['steps']]
        total_steps = episode['total_steps']
        answer = answer_result.get('answer', '')

        # Check expectations
        meets_min_steps = total_steps >= test.get('min_steps', 1)

        # Check if expected answer is contained (if specified)
        answer_correct = True
        if 'expected_answer_contains' in test:
            answer_correct = test['expected_answer_contains'].lower() in answer.lower()

        result = {
            'name': test['name'],
            'query': test['query'],
            'actions': actions_taken,
            'steps': total_steps,
            'answer': answer[:200],
            'meets_min_steps': meets_min_steps,
            'answer_correct': answer_correct,
            'success': episode['success']
        }
        results.append(result)

        logger.info(f"Actions: {actions_taken}")
        logger.info(f"Steps: {total_steps}")
        logger.info(f"Answer: {answer[:150]}...")
        logger.info(f"Min Steps Met: {'✅' if meets_min_steps else '❌'}")
        logger.info(f"Answer Correct: {'✅' if answer_correct else '❌'}")

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")

    passed = sum(1 for r in results if r['answer_correct'] and r['success'])
    total = len(results)

    for r in results:
        status = "✅" if r['answer_correct'] and r['success'] else "❌"
        logger.info(f"{status} {r['name']}: {r['steps']} steps, actions={r['actions']}")

    logger.info(f"\nPassed: {passed}/{total}")

    return results


def test_policy_action_distribution():
    """Test what actions the policy tends to select for different query types."""
    from src.orchestrator.nexus_context_manager import get_rlm_context_manager
    from src.orchestrator.rlm_policy_agent import get_policy_agent

    agent = get_policy_agent()
    if not agent.is_ready:
        agent.load_policy()

    test_queries = [
        ("Simple factual", "What is 2+2?", "Simple math."),
        ("Definition", "What is photosynthesis?", "Photosynthesis is how plants make food."),
        ("Complex reasoning", "Why is the sky blue?", "Light scattering in atmosphere causes blue color."),
    ]

    logger.info("\nAction Distribution Test")
    logger.info("="*50)

    for name, query, context in test_queries:
        cm = get_rlm_context_manager()
        cm.load_context_from_string(context, "test")

        # Get first action (before terminal)
        agent.reset_episode()
        action, metadata = agent.get_action(query, context, cm)

        logger.info(f"{name}: First action = {action}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--distribution', action='store_true', help="Test action distribution")
    args = parser.parse_args()

    if args.distribution:
        test_policy_action_distribution()
    else:
        run_complex_query_tests()
