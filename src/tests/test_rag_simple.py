"""
Simple RAG test without emojis for Windows compatibility
"""
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

pytest.importorskip("b3_rag_inference", reason="Legacy root script archived")
from b3_rag_inference import B3RAGInference

print("\n" + "="*70)
print("ImpressionCore B3 RAG-Enhanced Inference Test")
print("="*70 + "\n")

# Initialize system
print("Initializing RAG system...")
system = B3RAGInference(
    enable_rag=True,
    topk_retrieval=3,
    min_retrieval_confidence=0.3
)

# Test queries
test_queries = [
    "What are the basics of arithmetic?",
    "Explain fractions for elementary students",
    "Hello, how are you?"
]

print("\nRunning test queries...\n")

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*70}")
    print(f"Query {i}: '{query}'")
    print("-"*70)

    result = system.generate(query, max_length=50)

    print(f"Response: {result.response}")
    print(f"Quality: {result.quality_score:.2f}/5.0")
    print(f"RAG Used: {result.retrieval_used}")
    if result.retrieval_used:
        print(f"  - Docs Retrieved: {result.num_docs_retrieved}")
        print(f"  - Retrieval Confidence: {result.retrieval_confidence:.2f}")
        print(f"  - Context Length: {result.rag_context_length} chars")
    print(f"Fallback: {result.used_fallback}")
    print(f"Time: {result.processing_time_ms:.1f}ms")

# Print statistics
print("\n" + "="*70)
print("Session Statistics")
print("="*70)
stats = system.get_statistics()
for key, value in stats.items():
    print(f"  {key}: {value}")
print("="*70 + "\n")
