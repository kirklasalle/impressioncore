#!/usr/bin/env python3
"""
ImpressionCore: Assistant Integration Tests

Comprehensive integration test suite for the personal assistant core foundation,
validating end-to-end functionality, memory constraints, and performance targets.

File: src/tests/assistant/test_assistant_integration.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-31
Modified: 2025-05-31
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [tests, integration, assistant, memory-validation, 2025]
Dependencies: [pytest, asyncio, psutil, unittest]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module provides comprehensive integration tests for the personal assistant
core foundation implemented in Phase 8B Week 1. Tests validate the complete
query processing pipeline, memory constraints, and performance targets.

Test Coverage:
1. End-to-end query processing pipeline
2. Memory usage validation under GTX 1050 Ti constraints
3. Performance benchmarks and response time validation
4. Component integration and data flow
5. Error handling and edge cases
6. Concurrent processing capabilities
7. Cache performance and memory management

Test Architecture:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Setup    │───▶│  Integration    │───▶│   Validation    │
│   & Fixtures    │    │     Tests       │    │  & Cleanup      │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Performance Targets:
- Query processing: <1 second for standard queries
- Memory usage: <100MB total for all components
- Intent recognition: >90% accuracy
- Cache hit rate: >80% for repeated queries
- Concurrent queries: 10+ simultaneous
"""

import asyncio
import json
import logging
import os
import psutil
import pytest
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from unittest.mock import Mock, patch

# Import assistant components
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from assistant import AssistantCore
from assistant.core.query_processor import QueryProcessor, QueryResult
from assistant.core.retrieval_engine import RetrievalEngine, RetrievalResult, Document
from assistant.nlp.nlu_engine import NLUEngine, NLUResult, Intent, Entity, Sentiment
from assistant.core.context_manager import ContextManager, ContextItem, ConversationTurn
from assistant.core.response_generator import ResponseGenerator, GeneratedResponse
from assistant.knowledge.uks_integration import (
    UKSIntegration, KnowledgeQuery, KnowledgeResponse, KnowledgeItem,
    KnowledgeSource, KnowledgeType, VerificationStatus
)

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Test configuration
TEST_DB_PATH = "test_assistant.db"
TEST_MEMORY_LIMIT_MB = 100  # Total memory limit for tests
PERFORMANCE_TIMEOUT = 2.0  # Maximum response time in seconds
MIN_ACCURACY_THRESHOLD = 0.90  # Minimum accuracy for intent recognition
MIN_CACHE_HIT_RATE = 0.80  # Minimum cache hit rate


@pytest.fixture
async def temp_database():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        temp_path = tmp.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
async def query_processor():
    """Create a query processor instance for testing."""
    processor = QueryProcessor()
    await processor.initialize()
    yield processor
    await processor.cleanup()


@pytest.fixture
async def retrieval_engine():
    """Create a retrieval engine instance for testing."""
    engine = RetrievalEngine()
    await engine.initialize()
    yield engine
    await engine.cleanup()


@pytest.fixture
async def nlu_engine():
    """Create an NLU engine instance for testing."""
    engine = NLUEngine()
    await engine.initialize()
    yield engine
    await engine.cleanup()


@pytest.fixture
async def context_manager(temp_database):
    """Create a context manager instance for testing."""
    config = {'database_path': temp_database}  # Pass database path in config
    manager = ContextManager(config=config)
    await manager.initialize()
    yield manager
    await manager.cleanup()


@pytest.fixture
async def response_generator():
    """Create a response generator instance for testing."""
    generator = ResponseGenerator()
    await generator.initialize()
    yield generator
    await generator.cleanup()


@pytest.fixture
async def uks_integration(temp_database):
    """Create a UKS integration instance for testing."""
    integration = UKSIntegration(database_path=temp_database)
    yield integration
    await integration.cleanup()


@pytest.fixture
async def full_assistant_pipeline(
    query_processor, retrieval_engine, nlu_engine, 
    context_manager, response_generator, uks_integration
):
    """Create a complete assistant pipeline for integration testing."""
    return {
        'query_processor': query_processor,
        'retrieval_engine': retrieval_engine,
        'nlu_engine': nlu_engine,
        'context_manager': context_manager,
        'response_generator': response_generator,
        'uks_integration': uks_integration
    }


class MemoryMonitor:
    """Monitor memory usage during tests."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        self.peak_memory = self.initial_memory
        self.measurements = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start memory monitoring in background thread."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop memory monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                memory_info = self.process.memory_info()
                current_memory = memory_info.rss
                self.peak_memory = max(self.peak_memory, current_memory)
                self.measurements.append({
                    'timestamp': time.time(),
                    'rss': current_memory,
                    'vms': memory_info.vms
                })
                time.sleep(0.1)  # Monitor every 100ms
            except Exception as e:
                logger.warning(f"Memory monitoring error: {e}")
                break
    
    def get_memory_delta_mb(self) -> float:
        """Get memory increase since monitoring started."""
        return (self.peak_memory - self.initial_memory) / (1024 * 1024)
    
    def get_current_memory_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def assert_memory_limit(self, limit_mb: float):
        """Assert that memory usage is within limit."""
        delta_mb = self.get_memory_delta_mb()
        assert delta_mb <= limit_mb, (
            f"Memory usage exceeded limit: {delta_mb:.1f}MB > {limit_mb}MB"
        )


class TestAssistantIntegration:
    """Integration tests for the personal assistant core foundation."""
      @pytest.mark.asyncio
    async def test_end_to_end_query_processing(self, full_assistant_pipeline):
        """Test complete end-to-end query processing pipeline."""
        pipeline = full_assistant_pipeline
        memory_monitor = MemoryMonitor()
        
        try:
            memory_monitor.start_monitoring()
            
            # Test query
            test_query = "What is artificial intelligence and how does it work?"
            
            # Step 1: Query Processing
            start_time = time.time()
            processed_query = await pipeline['query_processor'].process_query(test_query)
            query_time = time.time() - start_time
            
            assert isinstance(processed_query, QueryResult)
            assert processed_query.original_query == test_query
            assert query_time < 0.5, f"Query processing too slow: {query_time:.3f}s"
            
            # Step 2: NLU Processing
            start_time = time.time()
            nlu_result = await pipeline['nlu_engine'].process_text(test_query)
            nlu_time = time.time() - start_time
            
            assert isinstance(nlu_result, NLUResult)
            assert nlu_result.intent.category is not None
            assert nlu_time < 0.5, f"NLU processing too slow: {nlu_time:.3f}s"
            
            # Step 3: Context Processing
            start_time = time.time()
            conversation_turn = ConversationTurn(
                turn_id="test_turn_1",
                user_input=test_query,
                processed_query=processed_query,
                nlu_result=nlu_result,
                timestamp=time.time()
            )
            await pipeline['context_manager'].add_conversation_turn(conversation_turn)
            context_time = time.time() - start_time
            
            assert context_time < 0.2, f"Context processing too slow: {context_time:.3f}s"
            
            # Step 4: Knowledge Retrieval
            start_time = time.time()
            knowledge_query = KnowledgeQuery(
                query_text=test_query,
                intent=nlu_result.intent.category,
                entities=[e.text for e in nlu_result.entities],
                max_results=5
            )
            knowledge_response = await pipeline['uks_integration'].query_knowledge(knowledge_query)
            knowledge_time = time.time() - start_time
            
            assert isinstance(knowledge_response, KnowledgeResponse)
            assert knowledge_time < 0.5, f"Knowledge retrieval too slow: {knowledge_time:.3f}s"
            
            # Step 5: Response Generation
            start_time = time.time()
            response = await pipeline['response_generator'].generate_response(
                processed_query=processed_query,
                nlu_result=nlu_result,
                context=await pipeline['context_manager'].get_current_context(),
                knowledge_items=knowledge_response.items
            )
            response_time = time.time() - start_time
            
            assert isinstance(response, GeneratedResponse)
            assert len(response.text) > 0
            assert response_time < 0.5, f"Response generation too slow: {response_time:.3f}s"
            
            # Verify total processing time
            total_time = query_time + nlu_time + context_time + knowledge_time + response_time
            assert total_time < PERFORMANCE_TIMEOUT, (
                f"Total processing time exceeded limit: {total_time:.3f}s > {PERFORMANCE_TIMEOUT}s"
            )            
            logger.info(f"End-to-end processing completed in {total_time:.3f}s")
            
        finally:
            memory_monitor.stop_monitoring()
            memory_monitor.assert_memory_limit(TEST_MEMORY_LIMIT_MB)
    
    @pytest.mark.asyncio
    async def test_memory_constraints_validation(self, full_assistant_pipeline):
        """Test that all components stay within memory constraints."""
        pipeline = await full_assistant_pipeline
        memory_monitor = MemoryMonitor()
        
        try:
            memory_monitor.start_monitoring()
            
            # Process multiple queries to stress test memory usage
            test_queries = [
                "What is machine learning?",
                "How do neural networks work?",
                "Explain deep learning algorithms",
                "What are transformers in AI?",
                "How does natural language processing work?",
                "What is computer vision?",
                "Explain reinforcement learning",
                "How do chatbots understand language?",
                "What is artificial general intelligence?",
                "How does speech recognition work?"
            ]
            
            responses = []
            for i, query in enumerate(test_queries):
                logger.info(f"Processing query {i+1}/{len(test_queries)}: {query[:50]}...")
                
                # Process query through full pipeline
                processed_query = await pipeline['query_processor'].process_query(query)
                nlu_result = await pipeline['nlu_engine'].process_text(query)
                
                # Add to context
                turn = ConversationTurn(
                    turn_id=f"test_turn_{i+1}",
                    user_input=query,
                    processed_query=processed_query,
                    nlu_result=nlu_result,
                    timestamp=time.time()
                )
                await pipeline['context_manager'].add_conversation_turn(turn)
                
                # Query knowledge
                knowledge_query = KnowledgeQuery(
                    query_text=query,
                    intent=nlu_result.intent.category,
                    max_results=3
                )
                knowledge_response = await pipeline['uks_integration'].query_knowledge(knowledge_query)
                
                # Generate response
                response = await pipeline['response_generator'].generate_response(
                    processed_query=processed_query,
                    nlu_result=nlu_result,
                    context=await pipeline['context_manager'].get_current_context(),
                    knowledge_items=knowledge_response.items
                )
                
                responses.append(response)
                  # Check memory after each query
                current_memory = memory_monitor.get_current_memory_mb()
                logger.debug(f"Memory after query {i+1}: {current_memory:.1f}MB")
            
            # Verify all responses generated successfully
            assert len(responses) == len(test_queries)
            for response in responses:
                assert isinstance(response, GeneratedResponse)
                assert len(response.text) > 0
            
            logger.info(f"Processed {len(test_queries)} queries successfully")
            
        finally:
            memory_monitor.stop_monitoring()
            memory_delta = memory_monitor.get_memory_delta_mb()
            logger.info(f"Total memory increase: {memory_delta:.1f}MB")
            memory_monitor.assert_memory_limit(TEST_MEMORY_LIMIT_MB)
    
    @pytest.mark.asyncio
    async def test_concurrent_query_processing(self, full_assistant_pipeline):
        """Test concurrent processing of multiple queries."""
        pipeline = await full_assistant_pipeline
        memory_monitor = MemoryMonitor()
        
        try:
            memory_monitor.start_monitoring()
            
            # Concurrent test queries
            concurrent_queries = [
                "What is AI?",
                "How does ML work?",
                "Explain NLP",
                "What is computer vision?",
                "How do chatbots work?",
                "What is deep learning?",
                "Explain neural networks",
                "What is reinforcement learning?",
                "How does speech recognition work?",
                "What is natural language understanding?"
            ]
            
            async def process_single_query(query: str, query_id: int) -> dict:
                """Process a single query and return timing info."""
                start_time = time.time()
                
                try:
                    # Process through pipeline
                    processed_query = await pipeline['query_processor'].process_query(query)
                    nlu_result = await pipeline['nlu_engine'].process_text(query)
                    
                    # Add to context with unique turn ID
                    turn = ConversationTurn(
                        turn_id=f"concurrent_turn_{query_id}",
                        user_input=query,
                        processed_query=processed_query,
                        nlu_result=nlu_result,
                        timestamp=time.time()
                    )
                    await pipeline['context_manager'].add_conversation_turn(turn)
                    
                    # Query knowledge
                    knowledge_query = KnowledgeQuery(
                        query_text=query,
                        intent=nlu_result.intent.category,
                        max_results=2
                    )
                    knowledge_response = await pipeline['uks_integration'].query_knowledge(knowledge_query)
                    
                    # Generate response
                    response = await pipeline['response_generator'].generate_response(
                        processed_query=processed_query,
                        nlu_result=nlu_result,
                        context=await pipeline['context_manager'].get_current_context(),
                        knowledge_items=knowledge_response.items
                    )
                    
                    processing_time = time.time() - start_time
                    
                    return {
                        'query_id': query_id,
                        'query': query,
                        'success': True,
                        'processing_time': processing_time,
                        'response': response,
                        'error': None
                    }
                    
                except Exception as e:
                    processing_time = time.time() - start_time
                    return {
                        'query_id': query_id,
                        'query': query,
                        'success': False,
                        'processing_time': processing_time,
                        'response': None,
                        'error': str(e)
                    }
            
            # Process all queries concurrently
            start_time = time.time()
            tasks = [
                process_single_query(query, i) 
                for i, query in enumerate(concurrent_queries)
            ]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Analyze results
            successful_results = [r for r in results if r['success']]
            failed_results = [r for r in results if not r['success']]
            
            assert len(successful_results) >= len(concurrent_queries) * 0.9, (
                f"Too many failures: {len(failed_results)}/{len(concurrent_queries)}"
            )
            
            avg_processing_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
            max_processing_time = max(r['processing_time'] for r in successful_results)
            
            assert avg_processing_time < PERFORMANCE_TIMEOUT, (
                f"Average processing time too high: {avg_processing_time:.3f}s"
            )
            
            assert max_processing_time < PERFORMANCE_TIMEOUT * 2, (
                f"Maximum processing time too high: {max_processing_time:.3f}s"
            )
            
            logger.info(f"Concurrent processing: {len(successful_results)}/{len(concurrent_queries)} successful")
            logger.info(f"Total time: {total_time:.3f}s, Avg per query: {avg_processing_time:.3f}s")
            
            # Log any failures
            for result in failed_results:
                logger.warning(f"Query {result['query_id']} failed: {result['error']}")
            
        finally:
            memory_monitor.stop_monitoring()
            memory_monitor.assert_memory_limit(TEST_MEMORY_LIMIT_MB * 1.5)  # Allow more for concurrent
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, uks_integration):
        """Test cache performance and hit rates."""
        # Test queries (some repeated to test caching)
        test_queries = [
            "What is artificial intelligence?",
            "How does machine learning work?",
            "What is artificial intelligence?",  # Repeat
            "Explain neural networks",
            "How does machine learning work?",  # Repeat
            "What is deep learning?",
            "What is artificial intelligence?",  # Repeat again
            "How do computers understand language?",
            "Explain neural networks",  # Repeat
            "What is computer vision?"
        ]
        
        response_times = []
        cache_hits = 0
        
        for query in test_queries:
            start_time = time.time()
            
            knowledge_query = KnowledgeQuery(
                query_text=query,
                max_results=5
            )
            response = await uks_integration.query_knowledge(knowledge_query)
            
            processing_time = time.time() - start_time
            response_times.append(processing_time)
            
            if response.cache_hit:
                cache_hits += 1
        
        # Calculate statistics
        total_queries = len(test_queries)
        cache_hit_rate = cache_hits / total_queries
        avg_response_time = sum(response_times) / len(response_times)
        
        # Get UKS statistics
        uks_stats = uks_integration.get_statistics()
        
        logger.info(f"Cache hit rate: {cache_hit_rate:.2%}")
        logger.info(f"Average response time: {avg_response_time:.3f}s")
        logger.info(f"UKS cache stats: {uks_stats['cache_statistics']}")
        
        # Assertions
        assert cache_hit_rate >= 0.3, f"Cache hit rate too low: {cache_hit_rate:.2%}"
        assert avg_response_time < 0.5, f"Average response time too high: {avg_response_time:.3f}s"
        
        # Verify that cached queries are faster
        if cache_hits > 0:
            cached_times = []
            non_cached_times = []
            
            for i, query in enumerate(test_queries):
                # Simple heuristic: if this exact query appeared before, it was likely cached
                if query in test_queries[:i]:
                    cached_times.append(response_times[i])
                else:
                    non_cached_times.append(response_times[i])
            
            if cached_times and non_cached_times:
                avg_cached_time = sum(cached_times) / len(cached_times)
                avg_non_cached_time = sum(non_cached_times) / len(non_cached_times)
                
                logger.info(f"Cached avg: {avg_cached_time:.3f}s, Non-cached avg: {avg_non_cached_time:.3f}s")
                
                # Cached queries should generally be faster
                assert avg_cached_time <= avg_non_cached_time * 1.5, (
                    "Cached queries not significantly faster"
                )
    
    @pytest.mark.asyncio
    async def test_intent_recognition_accuracy(self, nlu_engine):
        """Test intent recognition accuracy with known test cases."""
        # Test cases with expected intents
        test_cases = [
            ("What is artificial intelligence?", "question"),
            ("Hello there!", "greeting"),
            ("Create a reminder for tomorrow", "task_creation"),
            ("Search for machine learning papers", "search"),
            ("Thank you for your help", "gratitude"),
            ("How are you doing today?", "greeting"),
            ("Find information about neural networks", "search"),
            ("Set up a meeting for next week", "task_creation"),
            ("What's the weather like?", "weather"),
            ("Can you help me with this problem?", "question"),
            ("Good morning!", "greeting"),
            ("I need to schedule an appointment", "task_creation"),
            ("Look up the definition of deep learning", "search"),
            ("That was very helpful", "gratitude"),
            ("Explain how transformers work", "question")
        ]
        
        correct_predictions = 0
        total_predictions = len(test_cases)
        results = []
        
        for query, expected_intent in test_cases:
            nlu_result = await nlu_engine.process_text(query)
            predicted_intent = nlu_result.intent.category
            
            is_correct = predicted_intent == expected_intent
            if is_correct:
                correct_predictions += 1
            
            results.append({
                'query': query,
                'expected': expected_intent,
                'predicted': predicted_intent,
                'correct': is_correct,
                'confidence': nlu_result.intent.confidence
            })
            
            logger.debug(f"Query: '{query}' | Expected: {expected_intent} | Predicted: {predicted_intent} | Correct: {is_correct}")
        
        accuracy = correct_predictions / total_predictions
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        
        logger.info(f"Intent recognition accuracy: {accuracy:.2%} ({correct_predictions}/{total_predictions})")
        logger.info(f"Average confidence: {avg_confidence:.3f}")
        
        # Log incorrect predictions for analysis
        incorrect = [r for r in results if not r['correct']]
        if incorrect:
            logger.warning(f"Incorrect predictions: {len(incorrect)}")
            for result in incorrect:                logger.warning(f"  '{result['query']}': expected {result['expected']}, got {result['predicted']}")
        
        # Assertions
        assert accuracy >= MIN_ACCURACY_THRESHOLD, (
            f"Intent recognition accuracy too low: {accuracy:.2%} < {MIN_ACCURACY_THRESHOLD:.2%}"
        )
        
        assert avg_confidence >= 0.7, (
            f"Average confidence too low: {avg_confidence:.3f}"
        )
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, full_assistant_pipeline):
        """Test error handling and recovery in the assistant pipeline."""
        pipeline = await full_assistant_pipeline
        
        # Test cases that might cause errors
        error_test_cases = [
            "",  # Empty query
            "a" * 10000,  # Very long query
            "🤖🚀💻🎯🔥",  # Only emojis
            None,  # None input (should be handled gracefully)
            "SELECT * FROM users; DROP TABLE users;",  # SQL injection attempt
            "\x00\x01\x02invalid\x03characters",  # Invalid characters
        ]
        
        successful_recoveries = 0
        
        for i, test_input in enumerate(error_test_cases):
            try:
                logger.info(f"Testing error case {i+1}: {repr(test_input)}")
                
                # Try to process the problematic input
                if test_input is not None:
                    processed_query = await pipeline['query_processor'].process_query(test_input)
                    nlu_result = await pipeline['nlu_engine'].process_text(test_input)
                    
                    # Should handle gracefully without crashing
                    assert processed_query is not None
                    assert nlu_result is not None
                    
                    logger.info(f"Error case {i+1} handled gracefully")
                    successful_recoveries += 1
                else:
                    # None input should raise appropriate error
                    with pytest.raises((ValueError, TypeError)):
                        await pipeline['query_processor'].process_query(test_input)
                    successful_recoveries += 1
                
            except Exception as e:
                logger.warning(f"Error case {i+1} failed with: {type(e).__name__}: {e}")
                # Some errors are expected, but they shouldn't crash the system
                if "gracefully" in str(e).lower() or "handled" in str(e).lower():
                    successful_recoveries += 1
        
        recovery_rate = successful_recoveries / len(error_test_cases)
        logger.info(f"Error recovery rate: {recovery_rate:.2%}")
        
        # Should handle most error cases gracefully
        assert recovery_rate >= 0.7, f"Error recovery rate too low: {recovery_rate:.2%}"
    
    @pytest.mark.asyncio
    async def test_context_persistence_and_retrieval(self, context_manager):
        """Test context persistence and retrieval across multiple turns."""
        # Simulate a multi-turn conversation
        conversation_turns = [
            "Hello, I'm working on a machine learning project",
            "Can you help me understand neural networks?",
            "What about deep learning algorithms?",
            "How do they relate to what we discussed earlier?",
            "Thank you for the explanation"
        ]
        
        # Add conversation turns
        for i, user_input in enumerate(conversation_turns):
            # Create mock processed query and NLU result
            processed_query = QueryResult(
                original_query=user_input,
                cleaned_query=user_input.lower(),
                query_type="question",
                intent="question" if "?" in user_input else "statement",
                entities=[],
                metadata={}
            )
            
            nlu_result = NLUResult(
                original_text=user_input,
                intent=Intent(category="question", confidence=0.8),
                entities=[],
                sentiment=Sentiment(polarity=0.0, subjectivity=0.5),
                confidence=0.8,
                processing_time=0.1,
                metadata={}
            )
            
            turn = ConversationTurn(
                turn_id=f"test_turn_{i+1}",
                user_input=user_input,
                processed_query=processed_query,
                nlu_result=nlu_result,
                timestamp=time.time()
            )
            
            await context_manager.add_conversation_turn(turn)
        
        # Test context retrieval
        current_context = await context_manager.get_current_context()
        conversation_history = await context_manager.get_conversation_history(limit=10)
        
        # Verify context persistence
        assert len(conversation_history) == len(conversation_turns)
        assert current_context is not None
        
        # Test context search
        search_results = await context_manager.search_context("machine learning", limit=5)
        assert len(search_results) > 0        
        # Verify chronological order
        timestamps = [turn.timestamp for turn in conversation_history]
        assert timestamps == sorted(timestamps), "Conversation history not in chronological order"
        
        logger.info(f"Context test completed: {len(conversation_history)} turns persisted")
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, full_assistant_pipeline):
        """Comprehensive performance benchmarking of the assistant pipeline."""
        pipeline = await full_assistant_pipeline
        memory_monitor = MemoryMonitor()
        
        # Benchmark queries of different complexities
        benchmark_queries = [
            # Simple queries
            ("What is AI?", "simple"),
            ("Hello", "simple"),
            ("Thanks", "simple"),
            
            # Medium complexity
            ("How does machine learning work in practice?", "medium"),
            ("Can you explain neural networks and their applications?", "medium"),
            ("What are the benefits of deep learning algorithms?", "medium"),
            
            # Complex queries
            ("I'm working on a computer vision project using convolutional neural networks and need help understanding how transfer learning works with pre-trained models like ResNet and VGG for image classification tasks", "complex"),
            ("Explain the mathematical foundations of transformer architectures, including self-attention mechanisms, positional encoding, and how they differ from recurrent neural networks in natural language processing applications", "complex")
        ]
        
        benchmark_results = {
            'simple': [],
            'medium': [],
            'complex': []
        }
        
        try:
            memory_monitor.start_monitoring()
            
            for query, complexity in benchmark_queries:
                logger.info(f"Benchmarking {complexity} query: {query[:50]}...")
                
                start_time = time.time()
                
                # Full pipeline processing
                processed_query = await pipeline['query_processor'].process_query(query)
                nlu_result = await pipeline['nlu_engine'].process_text(query)
                
                turn = ConversationTurn(
                    turn_id=f"benchmark_{complexity}_{len(benchmark_results[complexity])}",
                    user_input=query,
                    processed_query=processed_query,
                    nlu_result=nlu_result,
                    timestamp=time.time()
                )
                await pipeline['context_manager'].add_conversation_turn(turn)
                
                knowledge_query = KnowledgeQuery(
                    query_text=query,
                    intent=nlu_result.intent.category,
                    max_results=5
                )
                knowledge_response = await pipeline['uks_integration'].query_knowledge(knowledge_query)
                
                response = await pipeline['response_generator'].generate_response(
                    processed_query=processed_query,
                    nlu_result=nlu_result,
                    context=await pipeline['context_manager'].get_current_context(),
                    knowledge_items=knowledge_response.items
                )
                
                processing_time = time.time() - start_time
                current_memory = memory_monitor.get_current_memory_mb()
                
                benchmark_results[complexity].append({
                    'query': query,
                    'processing_time': processing_time,
                    'memory_mb': current_memory,
                    'response_length': len(response.text),
                    'knowledge_items': len(knowledge_response.items),
                    'cache_hit': knowledge_response.cache_hit
                })
                
                logger.debug(f"{complexity.capitalize()} query processed in {processing_time:.3f}s")
        
        finally:
            memory_monitor.stop_monitoring()
        
        # Analyze benchmark results
        for complexity, results in benchmark_results.items():
            if not results:
                continue
                
            avg_time = sum(r['processing_time'] for r in results) / len(results)
            max_time = max(r['processing_time'] for r in results)
            avg_memory = sum(r['memory_mb'] for r in results) / len(results)
            
            logger.info(f"{complexity.capitalize()} queries:")
            logger.info(f"  Average time: {avg_time:.3f}s")
            logger.info(f"  Maximum time: {max_time:.3f}s")
            logger.info(f"  Average memory: {avg_memory:.1f}MB")
            
            # Performance assertions based on complexity
            if complexity == "simple":
                assert avg_time < 0.5, f"Simple queries too slow: {avg_time:.3f}s"
                assert max_time < 1.0, f"Simple query max time too high: {max_time:.3f}s"
            elif complexity == "medium":
                assert avg_time < 1.0, f"Medium queries too slow: {avg_time:.3f}s"
                assert max_time < 2.0, f"Medium query max time too high: {max_time:.3f}s"
            elif complexity == "complex":
                assert avg_time < 2.0, f"Complex queries too slow: {avg_time:.3f}s"
                assert max_time < 4.0, f"Complex query max time too high: {max_time:.3f}s"
            
            # Memory assertions
            assert avg_memory < TEST_MEMORY_LIMIT_MB, (
                f"{complexity} queries exceed memory limit: {avg_memory:.1f}MB"
            )
        
        # Overall performance summary
        all_times = [r['processing_time'] for results in benchmark_results.values() for r in results]
        overall_avg = sum(all_times) / len(all_times)
        overall_max = max(all_times)
        
        logger.info(f"Overall performance: avg={overall_avg:.3f}s, max={overall_max:.3f}s")
        memory_monitor.assert_memory_limit(TEST_MEMORY_LIMIT_MB)


class TestComponentInteraction:
    """Test interactions between different assistant components."""
    
    @pytest.mark.asyncio
    async def test_query_processor_nlu_integration(self, query_processor, nlu_engine):
        """Test integration between query processor and NLU engine."""
        test_query = "Can you help me find information about machine learning algorithms?"
        
        # Process query
        processed_query = await query_processor.process_query(test_query)
        
        # Process with NLU
        nlu_result = await nlu_engine.process_text(test_query)
        
        # Verify compatibility
        assert processed_query.original_query == nlu_result.original_text
        assert processed_query.intent == nlu_result.intent.category
        
        # Verify entities are captured by both
        if processed_query.entities and nlu_result.entities:
            processed_entities = set(processed_query.entities)
            nlu_entities = set(e.text for e in nlu_result.entities)
            
            # Should have some overlap
            overlap = processed_entities.intersection(nlu_entities)
            assert len(overlap) > 0, "No entity overlap between processors"
    
    @pytest.mark.asyncio
    async def test_context_knowledge_integration(self, context_manager, uks_integration):
        """Test integration between context manager and knowledge system."""
        # Add some context
        context_item = ContextItem(
            item_id="test_context_1",
            content="User is interested in machine learning",
            context_type="user_profile",
            source="conversation",
            timestamp=time.time()
        )
        await context_manager.add_context_item(context_item)
        
        # Query knowledge with context
        knowledge_query = KnowledgeQuery(
            query_text="machine learning algorithms",
            context={"user_interests": ["machine learning"]},
            max_results=5
        )
        
        knowledge_response = await uks_integration.query_knowledge(knowledge_query)
        
        # Verify knowledge response considers context
        assert isinstance(knowledge_response, KnowledgeResponse)
        assert len(knowledge_response.items) >= 0
    
    @pytest.mark.asyncio
    async def test_response_generation_integration(
        self, response_generator, nlu_engine, context_manager, uks_integration
    ):
        """Test response generation with all input sources."""
        query = "What are the applications of neural networks?"
        
        # Get inputs from all sources
        nlu_result = await nlu_engine.process_text(query)
        
        # Add to context
        processed_query = QueryResult(
            original_query=query,
            cleaned_query=query.lower(),
            query_type="question",
            intent=nlu_result.intent.category,
            entities=[e.text for e in nlu_result.entities],
            metadata={}
        )
        
        turn = ConversationTurn(
            turn_id="integration_test",
            user_input=query,
            processed_query=processed_query,
            nlu_result=nlu_result,
            timestamp=time.time()
        )
        await context_manager.add_conversation_turn(turn)
        
        # Get knowledge
        knowledge_query = KnowledgeQuery(
            query_text=query,
            intent=nlu_result.intent.category,
            max_results=3
        )
        knowledge_response = await uks_integration.query_knowledge(knowledge_query)
        
        # Generate response
        response = await response_generator.generate_response(
            processed_query=processed_query,
            nlu_result=nlu_result,
            context=await context_manager.get_current_context(),
            knowledge_items=knowledge_response.items
        )
        
        # Verify response quality
        assert isinstance(response, GeneratedResponse)
        assert len(response.text) > 0
        assert response.confidence > 0.0
        
        # Response should be relevant to the query
        query_words = set(query.lower().split())
        response_words = set(response.text.lower().split())
        
        # Should have some word overlap (basic relevance check)
        overlap = query_words.intersection(response_words)
        assert len(overlap) > 0, "Response has no word overlap with query"


if __name__ == "__main__":
    """Run integration tests directly."""
    import pytest
    
    # Configure logging for test execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests with detailed output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--log-cli-level=INFO"
    ])
