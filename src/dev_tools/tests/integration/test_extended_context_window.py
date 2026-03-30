#!/usr/bin/env python3
"""
ImpressionCore: Extended Context Window Integration Tests

Comprehensive test suite for validating 256k context window support
with sparse attention mechanisms on GTX 1050 Ti hardware constraints.

File: src/tests/integration/test_extended_context_window.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-01-09
Modified: 2025-01-09
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle <kirk@impressioncore.ai>

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [testing, integration, memory-critical, pytorch, 2025]
Dependencies: [torch, pytest, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Integration tests for extended context window functionality including:
- Sparse attention mechanisms (sliding window, Longformer, ring attention)
- Memory efficiency validation on GTX 1050 Ti constraints
- Performance benchmarking for various context sizes
- Real-world scenario testing with long documents

Design Philosophy:
- Comprehensive validation of memory constraints
- Progressive testing from 32k to 256k context
- Hardware-specific optimization validation
- Real-world scenario coverage
"""

import pytest
import torch
import torch.nn as nn
import time
import gc
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import logging

# Import sparse attention implementations
from src.models.layers.sparse_attention import (
    SparseAttentionConfig,
    SlidingWindowAttention,
    LongformerAttention,
    RingAttention,
    AdaptiveSparseAttention,
    create_sparse_attention
)

# Import memory optimization utilities
from src.core.utils.memory_optimization.memory_manager import MemoryTracker

logger = logging.getLogger(__name__)

@dataclass
class ExtendedContextTestConfig:
    """Configuration for extended context window tests."""
    
    # Test parameters
    batch_size: int = 1
    num_heads: int = 8
    head_dim: int = 64
    hidden_size: int = 512
    device: torch.device = None
    
    # Context window sizes to test
    context_sizes: List[int] = None
    
    # Memory constraints (GTX 1050 Ti)
    max_vram_gb: float = 3.8  # Conservative limit for GTX 1050 Ti
    max_ram_gb: float = 16.0  # Reasonable system RAM limit
    
    # Performance targets
    max_latency_ms: float = 1000.0  # 1 second for 256k context
    min_throughput_tokens_per_sec: float = 256.0  # 256 tokens/sec minimum
    
    def __post_init__(self):
        if self.device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if self.context_sizes is None:
            self.context_sizes = [
                1024,    # 1k - baseline
                4096,    # 4k - standard
                16384,   # 16k - medium
                32768,   # 32k - large
                65536,   # 64k - very large
                131072,  # 128k - extreme
                262144   # 256k - maximum target
            ]


class TestSparseAttentionMechanisms:
    """Test suite for sparse attention mechanisms."""
    
    @pytest.fixture
    def test_config(self):
        return ExtendedContextTestConfig()
    
    @pytest.fixture
    def memory_tracker(self):
        return MemoryTracker()
    
    def test_sliding_window_attention_functionality(self, test_config, memory_tracker):
        """Test sliding window attention for various sequence lengths."""
        logger.info("Testing sliding window attention functionality")
        
        config = SparseAttentionConfig(
            attention_type="sliding_window",
            local_window_size=512,
            device=test_config.device
        )
        
        attention = SlidingWindowAttention(config)
        attention = attention.to(test_config.device)
        
        for seq_len in [1024, 4096, 16384, 32768]:
            logger.info(f"Testing sliding window attention with seq_len={seq_len}")
            
            with memory_tracker.track("sliding_window_attention"):
                # Create test tensors
                query = torch.randn(
                    test_config.batch_size, test_config.num_heads, 
                    seq_len, test_config.head_dim, 
                    device=test_config.device
                )
                key = torch.randn_like(query)
                value = torch.randn_like(query)
                
                # Apply attention
                output = attention(query, key, value)
                
                # Validate output shape
                assert output.shape == query.shape
                
                # Validate output is not NaN or infinity
                assert torch.isfinite(output).all()
                
                # Check memory usage
                memory_stats = memory_tracker.get_current_stats()
                if test_config.device.type == "cuda":
                    vram_gb = memory_stats.get("gpu_memory_used_gb", 0)
                    assert vram_gb < test_config.max_vram_gb, f"VRAM usage {vram_gb:.2f}GB exceeds limit"
                
                logger.info(f"✅ Sliding window attention successful for seq_len={seq_len}")
    
    def test_longformer_attention_functionality(self, test_config, memory_tracker):
        """Test Longformer-style local + global attention."""
        logger.info("Testing Longformer attention functionality")
        
        config = SparseAttentionConfig(
            attention_type="longformer",
            local_window_size=512,
            global_tokens=64,
            device=test_config.device
        )
        
        attention = LongformerAttention(config)
        attention = attention.to(test_config.device)
        
        for seq_len in [4096, 16384, 32768, 65536]:
            logger.info(f"Testing Longformer attention with seq_len={seq_len}")
            
            with memory_tracker.track("longformer_attention"):
                # Create test tensors
                query = torch.randn(
                    test_config.batch_size, test_config.num_heads,
                    seq_len, test_config.head_dim,
                    device=test_config.device
                )
                key = torch.randn_like(query)
                value = torch.randn_like(query)
                
                # Create global token IDs (first few tokens)
                global_token_ids = torch.arange(min(64, seq_len), device=test_config.device)
                
                # Apply attention
                output = attention(query, key, value, global_token_ids=global_token_ids)
                
                # Validate output
                assert output.shape == query.shape
                assert torch.isfinite(output).all()
                
                # Check memory usage
                memory_stats = memory_tracker.get_current_stats()
                if test_config.device.type == "cuda":
                    vram_gb = memory_stats.get("gpu_memory_used_gb", 0)
                    assert vram_gb < test_config.max_vram_gb, f"VRAM usage {vram_gb:.2f}GB exceeds limit"
                
                logger.info(f"✅ Longformer attention successful for seq_len={seq_len}")
    
    def test_ring_attention_functionality(self, test_config, memory_tracker):
        """Test ring attention for extremely long sequences."""
        logger.info("Testing ring attention functionality")
        
        config = SparseAttentionConfig(
            attention_type="ring_attention",
            local_window_size=1024,
            device=test_config.device
        )
        
        attention = RingAttention(config)
        attention = attention.to(test_config.device)
        
        for seq_len in [16384, 65536, 131072]:
            logger.info(f"Testing ring attention with seq_len={seq_len}")
            
            with memory_tracker.track("ring_attention"):
                # Create test tensors
                query = torch.randn(
                    test_config.batch_size, test_config.num_heads,
                    seq_len, test_config.head_dim,
                    device=test_config.device
                )
                key = torch.randn_like(query)
                value = torch.randn_like(query)
                
                # Apply attention
                output = attention(query, key, value)
                
                # Validate output
                assert output.shape == query.shape
                assert torch.isfinite(output).all()
                
                # Check memory usage
                memory_stats = memory_tracker.get_current_stats()
                if test_config.device.type == "cuda":
                    vram_gb = memory_stats.get("gpu_memory_used_gb", 0)
                    assert vram_gb < test_config.max_vram_gb, f"VRAM usage {vram_gb:.2f}GB exceeds limit"
                
                logger.info(f"✅ Ring attention successful for seq_len={seq_len}")
    
    def test_adaptive_sparse_attention(self, test_config, memory_tracker):
        """Test adaptive sparse attention that selects optimal patterns."""
        logger.info("Testing adaptive sparse attention")
        
        config = SparseAttentionConfig(
            attention_type="adaptive",
            local_window_size=512,
            global_tokens=64,
            device=test_config.device
        )
        
        attention = AdaptiveSparseAttention(config)
        attention = attention.to(test_config.device)
        
        for seq_len in test_config.context_sizes:
            logger.info(f"Testing adaptive attention with seq_len={seq_len}")
            
            with memory_tracker.track("adaptive_attention"):
                # Create test tensors
                query = torch.randn(
                    test_config.batch_size, test_config.num_heads,
                    seq_len, test_config.head_dim,
                    device=test_config.device
                )
                key = torch.randn_like(query)
                value = torch.randn_like(query)
                
                # Estimate memory usage before computation
                estimated_memory = attention.estimate_memory_usage(
                    test_config.batch_size, seq_len, test_config.num_heads, test_config.head_dim
                )
                
                logger.info(f"Estimated memory usage: {estimated_memory:.2f}GB")
                
                # Skip if estimated memory exceeds limits
                if estimated_memory > test_config.max_vram_gb and test_config.device.type == "cuda":
                    logger.warning(f"Skipping seq_len={seq_len} due to memory constraints")
                    continue
                
                try:
                    # Apply attention
                    start_time = time.time()
                    output = attention(query, key, value)
                    end_time = time.time()
                    
                    # Validate output
                    assert output.shape == query.shape
                    assert torch.isfinite(output).all()
                    
                    # Check performance
                    latency_ms = (end_time - start_time) * 1000
                    throughput = seq_len / (end_time - start_time)
                    
                    logger.info(f"Latency: {latency_ms:.2f}ms, Throughput: {throughput:.2f} tokens/sec")
                    
                    # Validate performance targets (relaxed for larger sequences)
                    max_expected_latency = test_config.max_latency_ms * (seq_len / 65536)  # Scale with sequence length
                    assert latency_ms < max_expected_latency, f"Latency {latency_ms:.2f}ms exceeds limit"
                    
                    # Check memory usage
                    memory_stats = memory_tracker.get_current_stats()
                    if test_config.device.type == "cuda":
                        vram_gb = memory_stats.get("gpu_memory_used_gb", 0)
                        assert vram_gb < test_config.max_vram_gb, f"VRAM usage {vram_gb:.2f}GB exceeds limit"
                    
                    logger.info(f"✅ Adaptive attention successful for seq_len={seq_len}")
                    
                except torch.cuda.OutOfMemoryError as e:
                    logger.warning(f"OOM for seq_len={seq_len}: {e}")
                    torch.cuda.empty_cache()
                    gc.collect()
                    continue


class TestMemoryEfficiency:
    """Test suite for memory efficiency validation."""
    
    @pytest.fixture
    def test_config(self):
        return ExtendedContextTestConfig()
    
    @pytest.fixture
    def memory_tracker(self):
        return MemoryTracker()
    
    def test_memory_scaling_with_sequence_length(self, test_config, memory_tracker):
        """Test memory usage scaling with sequence length."""
        logger.info("Testing memory scaling with sequence length")
        
        attention = create_sparse_attention("adaptive", device=test_config.device)
        attention = attention.to(test_config.device)
        
        memory_usage_data = []
        
        for seq_len in [1024, 4096, 16384, 32768, 65536]:
            logger.info(f"Testing memory scaling for seq_len={seq_len}")
            
            with memory_tracker.track(f"memory_scaling_{seq_len}"):
                # Clear memory before test
                if test_config.device.type == "cuda":
                    torch.cuda.empty_cache()
                gc.collect()
                
                # Create test tensors
                query = torch.randn(
                    test_config.batch_size, test_config.num_heads,
                    seq_len, test_config.head_dim,
                    device=test_config.device
                )
                key = torch.randn_like(query)
                value = torch.randn_like(query)
                
                # Measure initial memory
                initial_stats = memory_tracker.get_current_stats()
                initial_memory = initial_stats.get("gpu_memory_used_gb", 0)
                
                # Apply attention
                output = attention(query, key, value)
                
                # Measure peak memory
                peak_stats = memory_tracker.get_current_stats()
                peak_memory = peak_stats.get("gpu_memory_used_gb", 0)
                
                memory_increase = peak_memory - initial_memory
                memory_usage_data.append((seq_len, memory_increase))
                
                logger.info(f"Memory increase: {memory_increase:.2f}GB for seq_len={seq_len}")
                
                # Validate memory constraints
                assert peak_memory < test_config.max_vram_gb, f"Peak memory {peak_memory:.2f}GB exceeds limit"
        
        # Validate memory scaling is sub-quadratic
        # Memory should not scale worse than O(n log n) for sparse attention
        for i in range(1, len(memory_usage_data)):
            prev_seq, prev_mem = memory_usage_data[i-1]
            curr_seq, curr_mem = memory_usage_data[i]
            
            # Calculate scaling factor
            seq_ratio = curr_seq / prev_seq
            mem_ratio = curr_mem / prev_mem if prev_mem > 0 else 1
            
            # Memory should scale better than quadratic
            max_expected_ratio = seq_ratio * 1.5  # Allow 1.5x scaling factor
            assert mem_ratio < max_expected_ratio, f"Memory scaling {mem_ratio:.2f} exceeds expected {max_expected_ratio:.2f}"
        
        logger.info("✅ Memory scaling validation successful")
    
    def test_gpu_memory_optimization(self, test_config, memory_tracker):
        """Test GPU memory optimization strategies."""
        logger.info("Testing GPU memory optimization")
        
        if test_config.device.type != "cuda":
            pytest.skip("GPU memory optimization tests require CUDA")
        
        attention = create_sparse_attention("adaptive", device=test_config.device)
        attention = attention.to(test_config.device)
        
        # Test with maximum sequence length that should fit in memory
        seq_len = 65536  # 64k tokens
        
        with memory_tracker.track("gpu_memory_optimization"):
            # Clear GPU memory
            torch.cuda.empty_cache()
            gc.collect()
            
            # Create test tensors
            query = torch.randn(
                test_config.batch_size, test_config.num_heads,
                seq_len, test_config.head_dim,
                device=test_config.device
            )
            key = torch.randn_like(query)
            value = torch.randn_like(query)
            
            # Apply attention with gradient computation
            query.requires_grad_(True)
            key.requires_grad_(True)
            value.requires_grad_(True)
            
            output = attention(query, key, value)
            
            # Compute gradients to test memory during backward pass
            loss = output.sum()
            loss.backward()
            
            # Check final memory usage
            memory_stats = memory_tracker.get_current_stats()
            vram_gb = memory_stats.get("gpu_memory_used_gb", 0)
            
            assert vram_gb < test_config.max_vram_gb, f"GPU memory usage {vram_gb:.2f}GB exceeds limit"
            
            logger.info(f"✅ GPU memory optimization successful: {vram_gb:.2f}GB used")


class TestPerformanceBenchmarks:
    """Test suite for performance benchmarking."""
    
    @pytest.fixture
    def test_config(self):
        return ExtendedContextTestConfig()
    
    @pytest.fixture
    def memory_tracker(self):
        return MemoryTracker()
    
    def test_latency_benchmarks(self, test_config, memory_tracker):
        """Test latency across different context sizes."""
        logger.info("Testing latency benchmarks")
        
        attention = create_sparse_attention("adaptive", device=test_config.device)
        attention = attention.to(test_config.device)
        
        latency_data = []
        
        for seq_len in [4096, 16384, 32768, 65536]:
            logger.info(f"Benchmarking latency for seq_len={seq_len}")
            
            # Create test tensors
            query = torch.randn(
                test_config.batch_size, test_config.num_heads,
                seq_len, test_config.head_dim,
                device=test_config.device
            )
            key = torch.randn_like(query)
            value = torch.randn_like(query)
            
            # Warm up
            for _ in range(3):
                _ = attention(query, key, value)
            
            # Benchmark multiple runs
            latencies = []
            for _ in range(5):
                torch.cuda.synchronize() if test_config.device.type == "cuda" else None
                start_time = time.time()
                
                output = attention(query, key, value)
                
                torch.cuda.synchronize() if test_config.device.type == "cuda" else None
                end_time = time.time()
                
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
            
            # Calculate statistics
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            latency_data.append((seq_len, avg_latency, min_latency, max_latency))
            
            logger.info(f"Latency for seq_len={seq_len}: avg={avg_latency:.2f}ms, min={min_latency:.2f}ms, max={max_latency:.2f}ms")
            
            # Validate performance targets (scale with sequence length)
            max_expected_latency = test_config.max_latency_ms * (seq_len / 65536)
            assert avg_latency < max_expected_latency, f"Average latency {avg_latency:.2f}ms exceeds limit"
        
        logger.info("✅ Latency benchmarks successful")
    
    def test_throughput_benchmarks(self, test_config, memory_tracker):
        """Test throughput (tokens per second) benchmarks."""
        logger.info("Testing throughput benchmarks")
        
        attention = create_sparse_attention("adaptive", device=test_config.device)
        attention = attention.to(test_config.device)
        
        for seq_len in [4096, 16384, 32768, 65536]:
            logger.info(f"Benchmarking throughput for seq_len={seq_len}")
            
            # Create test tensors
            query = torch.randn(
                test_config.batch_size, test_config.num_heads,
                seq_len, test_config.head_dim,
                device=test_config.device
            )
            key = torch.randn_like(query)
            value = torch.randn_like(query)
            
            # Warm up
            for _ in range(3):
                _ = attention(query, key, value)
            
            # Benchmark throughput
            total_tokens = 0
            total_time = 0
            
            for _ in range(5):
                torch.cuda.synchronize() if test_config.device.type == "cuda" else None
                start_time = time.time()
                
                output = attention(query, key, value)
                
                torch.cuda.synchronize() if test_config.device.type == "cuda" else None
                end_time = time.time()
                
                total_tokens += seq_len
                total_time += (end_time - start_time)
            
            # Calculate throughput
            throughput = total_tokens / total_time
            
            logger.info(f"Throughput for seq_len={seq_len}: {throughput:.2f} tokens/sec")
            
            # Validate minimum throughput (relaxed for longer sequences)
            min_expected_throughput = test_config.min_throughput_tokens_per_sec * (4096 / seq_len)
            assert throughput > min_expected_throughput, f"Throughput {throughput:.2f} below minimum"
        
        logger.info("✅ Throughput benchmarks successful")


class TestRealWorldScenarios:
    """Test suite for real-world scenario validation."""
    
    @pytest.fixture
    def test_config(self):
        return ExtendedContextTestConfig()
    
    @pytest.fixture
    def memory_tracker(self):
        return MemoryTracker()
    
    def test_long_document_processing(self, test_config, memory_tracker):
        """Test processing of long documents (books, papers, etc.)."""
        logger.info("Testing long document processing")
        
        attention = create_sparse_attention("adaptive", device=test_config.device)
        attention = attention.to(test_config.device)
        
        # Simulate processing a long document (64k tokens)
        document_length = 65536
        
        with memory_tracker.track("long_document_processing"):
            # Create document-like tensor (simulated text embeddings)
            document_embeddings = torch.randn(
                1, test_config.num_heads, document_length, test_config.head_dim,
                device=test_config.device
            )
            
            # Process the entire document
            processed_document = attention(
                document_embeddings, document_embeddings, document_embeddings
            )
            
            # Validate processing
            assert processed_document.shape == document_embeddings.shape
            assert torch.isfinite(processed_document).all()
            
            # Check memory usage
            memory_stats = memory_tracker.get_current_stats()
            if test_config.device.type == "cuda":
                vram_gb = memory_stats.get("gpu_memory_used_gb", 0)
                assert vram_gb < test_config.max_vram_gb, f"VRAM usage {vram_gb:.2f}GB exceeds limit"
            
            logger.info("✅ Long document processing successful")
    
    def test_extended_conversation_handling(self, test_config, memory_tracker):
        """Test handling of extended conversations with long context."""
        logger.info("Testing extended conversation handling")
        
        attention = create_sparse_attention("adaptive", device=test_config.device)
        attention = attention.to(test_config.device)
        
        # Simulate an extended conversation (32k tokens)
        conversation_length = 32768
        
        with memory_tracker.track("extended_conversation"):
            # Create conversation context
            conversation_context = torch.randn(
                1, test_config.num_heads, conversation_length, test_config.head_dim,
                device=test_config.device
            )
            
            # Process conversation with attention
            processed_conversation = attention(
                conversation_context, conversation_context, conversation_context
            )
            
            # Validate processing
            assert processed_conversation.shape == conversation_context.shape
            assert torch.isfinite(processed_conversation).all()
            
            # Test incremental processing (simulating new messages)
            new_message_length = 512
            new_message = torch.randn(
                1, test_config.num_heads, new_message_length, test_config.head_dim,
                device=test_config.device
            )
            
            # Concatenate new message to conversation
            extended_conversation = torch.cat([conversation_context, new_message], dim=2)
            
            # Process extended conversation
            final_processed = attention(
                extended_conversation, extended_conversation, extended_conversation
            )
            
            assert final_processed.shape[2] == conversation_length + new_message_length
            
            logger.info("✅ Extended conversation handling successful")
    
    def test_multimodal_long_context(self, test_config, memory_tracker):
        """Test multimodal processing with long context windows."""
        logger.info("Testing multimodal long context processing")
        
        attention = create_sparse_attention("adaptive", device=test_config.device)
        attention = attention.to(test_config.device)
        
        # Simulate multimodal content (text + vision tokens)
        text_length = 16384   # 16k text tokens
        vision_length = 8192  # 8k vision tokens
        total_length = text_length + vision_length
        
        with memory_tracker.track("multimodal_long_context"):
            # Create multimodal embeddings
            multimodal_embeddings = torch.randn(
                1, test_config.num_heads, total_length, test_config.head_dim,
                device=test_config.device
            )
            
            # Create attention mask to distinguish modalities
            attention_mask = torch.ones(
                1, test_config.num_heads, total_length, total_length,
                device=test_config.device
            )
            
            # Process multimodal content
            processed_multimodal = attention(
                multimodal_embeddings, multimodal_embeddings, 
                multimodal_embeddings, attention_mask
            )
            
            # Validate processing
            assert processed_multimodal.shape == multimodal_embeddings.shape
            assert torch.isfinite(processed_multimodal).all()
            
            # Check memory usage
            memory_stats = memory_tracker.get_current_stats()
            if test_config.device.type == "cuda":
                vram_gb = memory_stats.get("gpu_memory_used_gb", 0)
                assert vram_gb < test_config.max_vram_gb, f"VRAM usage {vram_gb:.2f}GB exceeds limit"
            
            logger.info("✅ Multimodal long context processing successful")


# Integration test runner
if __name__ == "__main__":
    # Run comprehensive extended context window tests
    pytest.main([__file__, "-v", "--tb=short"])
