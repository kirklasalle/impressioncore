#!/usr/bin/env python3
"""
ImpressionCore: Priority 2 Integration Tests

Comprehensive integration tests for Priority 2 Enhanced Multimodal Integration.

File: tests/integration/test_priority_2_multimodal_integration.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-29
Modified: 2025-05-29
Version: 1.0.0

Authors:
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [priority-2, integration-tests, multimodal, fusion, 2025]
Dependencies: [pytest, torch, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
Integration tests for Priority 2 multimodal enhancements including:
- Advanced audio processing pipeline
- Enhanced vision-language integration  
- Cross-modal fusion strategies
- Unified latent space implementations
- Memory efficiency validation
- Performance benchmarking

Test Categories:
1. Component Integration Tests
2. End-to-End Pipeline Tests
3. Memory Efficiency Tests
4. Performance Benchmark Tests
5. Real-World Scenario Tests
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
import time
import psutil
import gc
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings

# Import Priority 2 components
try:
    from src.core.ai.multimodal.audio.advanced_audio_feature_extractor import (
        AdvancedAudioFeatureExtractor,
        AudioFeatureConfig,
        create_advanced_audio_extractor
    )
    from src.core.ai.multimodal.vision.enhanced_vision_language import (
        EnhancedVisionLanguageProcessor,
        VisionLanguageConfig,
        create_enhanced_vision_language_processor
    )
    from src.core.ai.multimodal.fusion.enhanced_cross_modal_fusion import (
        EnhancedCrossModalFusion,
        FusionConfig,
        create_enhanced_cross_modal_fusion
    )
    from src.core.ai.multimodal.fusion.unified_latent_space import (
        UnifiedLatentSpace,
        UnifiedLatentConfig,
        create_unified_latent_space
    )
    PRIORITY_2_AVAILABLE = True
except ImportError as e:
    PRIORITY_2_AVAILABLE = False
    print(f"Priority 2 components not available: {e}")

# Import Priority 1 optimizations
try:
    from src.core.utils.memory_optimization.fused_attention import (
        FusedMultiHeadAttention,
        FusedCrossModalAttention,
        HAS_FUSED_ATTENTION
    )
    PRIORITY_1_AVAILABLE = True
except ImportError:
    PRIORITY_1_AVAILABLE = False
    HAS_FUSED_ATTENTION = False

# Rich logging if available
try:
    from src.core.utils.rich_logging import get_rich_logger
    HAS_RICH = True
    logger = get_rich_logger(__name__)
except ImportError:
    HAS_RICH = False
    import logging
    logger = logging.getLogger(__name__)

@dataclass
class IntegrationTestConfig:
    """Configuration for integration tests."""
    
    # Test parameters
    batch_size: int = 2
    audio_duration: float = 5.0  # seconds
    image_size: Tuple[int, int] = (224, 224)
    text_seq_len: int = 32
    # Model dimensions
    hidden_size: int = 768  # Must be divisible by num_attention_heads (12)
    latent_dim: int = 256
    fusion_dim: int = 384
    
    # Performance thresholds
    memory_threshold_mb: float = 3500.0  # Max VRAM usage for GTX 1050 Ti
    latency_threshold_ms: float = 200.0  # Max processing latency
    
    # Device settings
    device: str = "auto"

class MemoryMonitor:
    """Monitor memory usage during tests."""
    
    def __init__(self):
        self.start_memory = None
        self.peak_memory = 0
        
    def start(self):
        """Start memory monitoring."""
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            self.start_memory = torch.cuda.memory_allocated()
        else:
            self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
    def get_peak_memory_mb(self) -> float:
        """Get peak memory usage in MB."""
        if torch.cuda.is_available():
            return torch.cuda.max_memory_allocated() / 1024 / 1024
        else:
            return psutil.Process().memory_info().rss / 1024 / 1024

class PerformanceTimer:
    """Timer for performance measurements."""
    
    def __init__(self):
        self.start_time = None
        
    def start(self):
        """Start timing."""
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        self.start_time = time.perf_counter()
        
    def stop(self) -> float:
        """Stop timing and return elapsed time in milliseconds."""
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        elapsed = (time.perf_counter() - self.start_time) * 1000
        return elapsed

# Fixtures
@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return IntegrationTestConfig()

@pytest.fixture
def device():
    """Device fixture."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

@pytest.fixture
def sample_multimodal_data(test_config, device):
    """Generate sample multimodal data."""
    batch_size = test_config.batch_size
    
    # Audio data (simulated waveform)
    audio_samples = int(16000 * test_config.audio_duration)  # 16kHz for 5 seconds
    audio_data = torch.randn(batch_size, audio_samples, device=device)
    
    # Vision data (RGB images)
    vision_data = torch.randn(
        batch_size, 3, test_config.image_size[0], test_config.image_size[1],
        device=device
    )
    
    # Text data (token embeddings)
    text_data = torch.randn(batch_size, test_config.text_seq_len, test_config.hidden_size, device=device)
    
    return {
        'audio': audio_data,
        'vision': vision_data,
        'text': text_data
    }

# Component Tests
@pytest.mark.skipif(not PRIORITY_2_AVAILABLE, reason="Priority 2 components not available")
class TestAdvancedAudioProcessing:
    """Test advanced audio processing components."""
    
    def test_audio_feature_extractor_creation(self, test_config):
        """Test audio feature extractor creation."""
        config = AudioFeatureConfig(
            sample_rate=16000,
            max_duration=test_config.audio_duration,
            device=test_config.device
        )
        
        extractor = AdvancedAudioFeatureExtractor(config)
        assert extractor is not None
        assert extractor.config.sample_rate == 16000
        
    def test_audio_feature_extraction(self, test_config, sample_multimodal_data):
        """Test audio feature extraction."""
        audio_data = sample_multimodal_data['audio']
        
        config = AudioFeatureConfig(
            sample_rate=16000,
            max_duration=test_config.audio_duration,
            device=test_config.device
        )
        
        extractor = AdvancedAudioFeatureExtractor(config)
          # Test feature extraction
        with torch.no_grad():
            features = extractor.extract_features(
                audio_data,
                feature_types=['mel', 'mfcc', 'spectrogram']
            )
        
        # Features are returned with different key names
        expected_keys = ['mel_spectrogram', 'mfcc', 'spectrogram']
        for key in expected_keys:
            assert any(key in feat_key for feat_key in features.keys()), f"Expected feature type {key} not found in {list(features.keys())}"
        
        # Check shapes
        for feature_type, feature_tensor in features.items():
            assert feature_tensor.shape[0] == test_config.batch_size
            assert len(feature_tensor.shape) == 3  # [batch, time, features]
            
    def test_audio_embedding_extraction(self, test_config, sample_multimodal_data):
        """Test audio embedding extraction."""
        audio_data = sample_multimodal_data['audio']
        
        config = AudioFeatureConfig(
            sample_rate=16000,
            max_duration=test_config.audio_duration,
            device=test_config.device
        )
        
        extractor = AdvancedAudioFeatureExtractor(config)
        
        # Test embedding extraction
        with torch.no_grad():
            embeddings = extractor.extract_embeddings(
                audio_data,
                embedding_dim=test_config.latent_dim
            )
        
        assert embeddings.shape == (test_config.batch_size, test_config.latent_dim)
        
        # Check L2 normalization
        norms = torch.norm(embeddings, p=2, dim=-1)
        assert torch.allclose(norms, torch.ones_like(norms), atol=1e-5)

@pytest.mark.skipif(not PRIORITY_2_AVAILABLE, reason="Priority 2 components not available")
class TestEnhancedVisionLanguage:
    """Test enhanced vision-language processing."""
    
    def test_vision_language_processor_creation(self, test_config):
        """Test vision-language processor creation."""
        config = VisionLanguageConfig(
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            device=test_config.device
        )
        
        processor = EnhancedVisionLanguageProcessor(config)
        assert processor is not None
        
    def test_vision_processing(self, test_config, sample_multimodal_data):
        """Test vision processing."""
        vision_data = sample_multimodal_data['vision']
        
        config = VisionLanguageConfig(
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            device=test_config.device
        )
        
        processor = EnhancedVisionLanguageProcessor(config)        # Test vision encoding
        with torch.no_grad():
            vision_features = processor.encode_images(vision_data)
        
        assert vision_features['cls_token'].shape[0] == test_config.batch_size
        assert vision_features['cls_token'].shape[-1] == test_config.hidden_size
        
    def test_cross_modal_fusion(self, test_config, sample_multimodal_data):
        """Test cross-modal fusion."""
        vision_data = sample_multimodal_data['vision']
        text_data = sample_multimodal_data['text']
        
        config = VisionLanguageConfig(
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            device=test_config.device
        )
        
        processor = EnhancedVisionLanguageProcessor(config)        # Test cross-modal fusion
        with torch.no_grad():
            vision_features = processor.encode_images(vision_data)
            # For cross-modal fusion, we need to call the forward method
            results = processor.forward(vision_data, text_data)
        
        assert results['fused_text'].shape[0] == test_config.batch_size
        assert results['fused_text'].shape[-1] == test_config.hidden_size

@pytest.mark.skipif(not PRIORITY_2_AVAILABLE, reason="Priority 2 components not available")
class TestEnhancedCrossModalFusion:
    """Test enhanced cross-modal fusion strategies."""
    
    def test_fusion_module_creation(self, test_config):
        """Test fusion module creation."""
        config = FusionConfig(
            fusion_method="all",
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            device=test_config.device
        )
        
        fusion_model = EnhancedCrossModalFusion(config)
        assert fusion_model is not None
        assert "hierarchical" in fusion_model.fusion_modules
        assert "contrastive" in fusion_model.fusion_modules
        assert "temporal" in fusion_model.fusion_modules
    
    def test_hierarchical_fusion(self, test_config, sample_multimodal_data, device):
        """Test hierarchical fusion."""
        # Prepare features with consistent device placement
        modality_features = {
            'text': sample_multimodal_data['text'],
            'vision': torch.randn(test_config.batch_size, 196, test_config.hidden_size, device=device),  # Simulated ViT features
            'audio': torch.randn(test_config.batch_size, 64, test_config.hidden_size, device=device)  # Simulated audio features
        }        
        config = FusionConfig(
            fusion_method="hierarchical",
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            device=test_config.device
        )
        
        fusion_model = EnhancedCrossModalFusion(config)
        fusion_model = fusion_model.to(device)  # Ensure model is on correct device
        
        # Test hierarchical fusion
        with torch.no_grad():
            results = fusion_model(modality_features)
        
        assert 'unified_fusion' in results
        assert results['unified_fusion'].shape == (test_config.batch_size, test_config.fusion_dim)
        
    def test_contrastive_fusion(self, test_config, sample_multimodal_data, device):
        """Test contrastive fusion."""
        # Prepare features with consistent device placement
        modality_features = {
            'text': sample_multimodal_data['text'],
            'vision': torch.randn(test_config.batch_size, 196, test_config.hidden_size, device=device),
            'audio': torch.randn(test_config.batch_size, 64, test_config.hidden_size, device=device)
        }
        
        config = FusionConfig(
            fusion_method="contrastive",
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            device=test_config.device
        )        
        fusion_model = EnhancedCrossModalFusion(config)
        fusion_model = fusion_model.to(device)  # Ensure model is on correct device
        
        # Test contrastive fusion with loss computation
        with torch.no_grad():
            results = fusion_model(modality_features, compute_losses=True)
        
        assert 'unified_fusion' in results
        assert 'contrastive_contrastive_loss' in results
        assert results['unified_fusion'].shape == (test_config.batch_size, test_config.fusion_dim)

@pytest.mark.skipif(not PRIORITY_2_AVAILABLE, reason="Priority 2 components not available")
class TestUnifiedLatentSpace:
    """Test unified latent space implementations."""
    
    def test_latent_space_creation(self, test_config):
        """Test unified latent space creation."""
        config = UnifiedLatentConfig(
            latent_dim=test_config.latent_dim,
            hidden_size=test_config.hidden_size,
            device=test_config.device
        )
        
        latent_space = UnifiedLatentSpace(config)
        assert latent_space is not None
        
    def test_modality_encoding(self, test_config, sample_multimodal_data):
        """Test modality encoding to unified latent space."""
        # Prepare features
        modality_features = {
            'text': sample_multimodal_data['text'],
            'vision': torch.randn(test_config.batch_size, 196, test_config.hidden_size),
            'audio': torch.randn(test_config.batch_size, 64, test_config.hidden_size)
        }
        
        config = UnifiedLatentConfig(
            latent_dim=test_config.latent_dim,
            hidden_size=test_config.hidden_size,
            device=test_config.device
        )
        
        latent_space = UnifiedLatentSpace(config)
        
        # Test encoding
        with torch.no_grad():
            latent_features = latent_space.encode_modalities(modality_features)
        
        for modality in modality_features:
            assert modality in latent_features
            assert latent_features[modality].shape[-1] == test_config.latent_dim
            
    def test_unified_representation(self, test_config, sample_multimodal_data):
        """Test unified representation generation."""
        # Prepare features
        modality_features = {
            'text': sample_multimodal_data['text'],
            'vision': torch.randn(test_config.batch_size, 196, test_config.hidden_size),
            'audio': torch.randn(test_config.batch_size, 64, test_config.hidden_size)
        }
        
        config = UnifiedLatentConfig(
            latent_dim=test_config.latent_dim,
            hidden_size=test_config.hidden_size,
            device=test_config.device
        )
        
        latent_space = UnifiedLatentSpace(config)
        
        # Test full forward pass
        with torch.no_grad():
            results = latent_space(
                modality_features,
                return_reconstructions=True,
                return_latent_features=True
            )
        
        assert 'unified_latent' in results
        assert 'modality_latents' in results
        assert 'reconstructions' in results
        assert results['unified_latent'].shape == (test_config.batch_size, test_config.latent_dim)

# Integration Tests
@pytest.mark.skipif(not PRIORITY_2_AVAILABLE, reason="Priority 2 components not available")
class TestEndToEndIntegration:
    """Test end-to-end multimodal processing pipeline."""
    
    def test_complete_multimodal_pipeline(self, test_config, sample_multimodal_data):
        """Test complete multimodal processing pipeline."""
        # Initialize all components
        audio_config = AudioFeatureConfig(            sample_rate=16000,
            max_duration=test_config.audio_duration,
            device=test_config.device
        )
        audio_extractor = AdvancedAudioFeatureExtractor(audio_config)
        
        vision_config = VisionLanguageConfig(
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            device=test_config.device
        )
        vision_processor = EnhancedVisionLanguageProcessor(vision_config)
        
        fusion_config = FusionConfig(
            fusion_method="all",
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            device=test_config.device
        )
        fusion_model = EnhancedCrossModalFusion(fusion_config)
        
        latent_config = UnifiedLatentConfig(
            latent_dim=test_config.latent_dim,
            hidden_size=test_config.hidden_size,
            device=test_config.device
        )
        latent_space = UnifiedLatentSpace(latent_config)
        
        # End-to-end processing
        with torch.no_grad():
            # Step 1: Extract audio embeddings
            audio_embeddings = audio_extractor.extract_embeddings(
                sample_multimodal_data['audio'],
                embedding_dim=test_config.hidden_size
            )
              # Step 2: Process vision
            vision_results = vision_processor.encode_images(sample_multimodal_data['vision'])
            vision_features = vision_results['cls_token']  # Use CLS token for pooled representation            # Step 3: Prepare features for fusion (ensure all are 3D for hierarchical fusion)
            modality_features = {
                'text': sample_multimodal_data['text'],  # Keep as 3D: [batch, seq_len, hidden]
                'vision': vision_features.unsqueeze(1),  # Convert CLS token to 3D: [batch, 1, hidden]
                'audio': audio_embeddings.unsqueeze(1) if audio_embeddings.dim() == 2 else audio_embeddings  # Ensure 3D
            }
            
            # Step 4: Cross-modal fusion
            fusion_results = fusion_model(modality_features)
            
            # Step 5: Unified latent space
            latent_results = latent_space(modality_features)
        
        # Verify results
        assert 'unified_fusion' in fusion_results
        assert 'unified_latent' in latent_results
        assert fusion_results['unified_fusion'].shape[0] == test_config.batch_size
        assert latent_results['unified_latent'].shape[0] == test_config.batch_size
        
        if HAS_RICH:
            logger.info("✅ End-to-end multimodal pipeline test passed")
        else:
            logger.info("End-to-end multimodal pipeline test passed")

# Memory and Performance Tests
@pytest.mark.skipif(not PRIORITY_2_AVAILABLE, reason="Priority 2 components not available")
class TestMemoryEfficiency:
    """Test memory efficiency of Priority 2 components."""
    
    def test_memory_usage_under_constraints(self, test_config, sample_multimodal_data):
        """Test memory usage under GTX 1050 Ti constraints."""
        monitor = MemoryMonitor()
        monitor.start()
        
        # Create components with memory optimization
        fusion_config = FusionConfig(
            fusion_method="hierarchical",
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            enable_fused_attention=HAS_FUSED_ATTENTION,
            device=test_config.device
        )
        
        fusion_model = EnhancedCrossModalFusion(fusion_config)
        
        # Prepare larger batch for memory stress test
        large_batch_size = 8
        modality_features = {
            'text': torch.randn(large_batch_size, 32, test_config.hidden_size),
            'vision': torch.randn(large_batch_size, 196, test_config.hidden_size),
            'audio': torch.randn(large_batch_size, 64, test_config.hidden_size)
        }
        
        # Move to device
        device = torch.device(test_config.device if test_config.device != "auto" 
                            else ("cuda" if torch.cuda.is_available() else "cpu"))
        
        for key in modality_features:
            modality_features[key] = modality_features[key].to(device)
        
        # Forward pass
        with torch.no_grad():
            results = fusion_model(modality_features)
        
        # Check memory usage
        peak_memory = monitor.get_peak_memory_mb()
        
        if torch.cuda.is_available():
            assert peak_memory < test_config.memory_threshold_mb, \
                f"Memory usage {peak_memory:.1f}MB exceeds threshold {test_config.memory_threshold_mb}MB"
        
        if HAS_RICH:
            logger.info(f"✅ Memory usage test passed: {peak_memory:.1f}MB")
        else:
            logger.info(f"Memory usage test passed: {peak_memory:.1f}MB")
    
    def test_gradient_accumulation_memory(self, test_config):
        """Test memory efficiency with gradient accumulation."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available for memory test")
        
        monitor = MemoryMonitor()
        monitor.start()
        
        # Create model with gradient checkpointing
        fusion_config = FusionConfig(
            fusion_method="contrastive",
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            enable_fused_attention=HAS_FUSED_ATTENTION,
            device="cuda"
        )
        
        fusion_model = EnhancedCrossModalFusion(fusion_config)
        
        # Simulate gradient accumulation
        accumulation_steps = 4
        micro_batch_size = 2
        
        for step in range(accumulation_steps):
            modality_features = {
                'text': torch.randn(micro_batch_size, 32, test_config.hidden_size, device='cuda'),
                'vision': torch.randn(micro_batch_size, 196, test_config.hidden_size, device='cuda'),
                'audio': torch.randn(micro_batch_size, 64, test_config.hidden_size, device='cuda')
            }
            
            # Forward pass with gradient computation
            results = fusion_model(modality_features, compute_losses=True)
            
            if 'contrastive_contrastive_loss' in results:
                loss = results['contrastive_contrastive_loss'] / accumulation_steps
                loss.backward()
        
        peak_memory = monitor.get_peak_memory_mb()
        
        assert peak_memory < test_config.memory_threshold_mb, \
            f"Memory usage with gradient accumulation {peak_memory:.1f}MB exceeds threshold"
        
        if HAS_RICH:
            logger.info(f"✅ Gradient accumulation memory test passed: {peak_memory:.1f}MB")
        else:
            logger.info(f"Gradient accumulation memory test passed: {peak_memory:.1f}MB")

@pytest.mark.skipif(not PRIORITY_2_AVAILABLE, reason="Priority 2 components not available")
class TestPerformanceBenchmarks:
    """Test performance benchmarks for Priority 2 components."""
    
    def test_inference_latency(self, test_config, sample_multimodal_data):
        """Test inference latency benchmarks."""
        timer = PerformanceTimer()
        
        # Create fusion model
        fusion_config = FusionConfig(
            fusion_method="hierarchical",
            hidden_size=test_config.hidden_size,
            fusion_dim=test_config.fusion_dim,
            enable_fused_attention=HAS_FUSED_ATTENTION,
            device=test_config.device
        )
        
        fusion_model = EnhancedCrossModalFusion(fusion_config)
          # Prepare features
        modality_features = {
            'text': sample_multimodal_data['text'],  # Keep 3D: (batch_size, seq_len, hidden_size)
            'vision': torch.randn(test_config.batch_size, 196, test_config.hidden_size),
            'audio': torch.randn(test_config.batch_size, 64, test_config.hidden_size)
        }
        
        # Move to device
        device = torch.device(test_config.device if test_config.device != "auto" 
                            else ("cuda" if torch.cuda.is_available() else "cpu"))
        
        for key in modality_features:
            modality_features[key] = modality_features[key].to(device)
        
        # Warmup
        for _ in range(3):
            with torch.no_grad():
                _ = fusion_model(modality_features)
        
        # Benchmark
        timer.start()
        for _ in range(10):
            with torch.no_grad():
                results = fusion_model(modality_features)
        latency = timer.stop() / 10  # Average latency
        
        assert latency < test_config.latency_threshold_ms, \
            f"Inference latency {latency:.1f}ms exceeds threshold {test_config.latency_threshold_ms}ms"
        
        if HAS_RICH:
            logger.info(f"✅ Inference latency test passed: {latency:.1f}ms")
        else:
            logger.info(f"Inference latency test passed: {latency:.1f}ms")
    
    def test_throughput_benchmark(self, test_config):
        """Test throughput benchmarks."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available for throughput test")
        
        timer = PerformanceTimer()
        
        # Create unified latent space model
        latent_config = UnifiedLatentConfig(
            latent_dim=test_config.latent_dim,
            hidden_size=test_config.hidden_size,
            device="cuda"
        )
        
        latent_space = UnifiedLatentSpace(latent_config)
        
        # Test different batch sizes
        batch_sizes = [1, 2, 4, 8]
        throughputs = []
        
        for batch_size in batch_sizes:
            modality_features = {
                'text': torch.randn(batch_size, 32, test_config.hidden_size, device='cuda'),
                'vision': torch.randn(batch_size, 196, test_config.hidden_size, device='cuda'),
                'audio': torch.randn(batch_size, 64, test_config.hidden_size, device='cuda')
            }
            
            # Warmup
            for _ in range(3):
                with torch.no_grad():
                    _ = latent_space(modality_features)
            
            # Benchmark
            num_iterations = 20
            timer.start()
            for _ in range(num_iterations):
                with torch.no_grad():
                    results = latent_space(modality_features)
            
            elapsed_ms = timer.stop()
            throughput = (batch_size * num_iterations) / (elapsed_ms / 1000)  # samples/second
            throughputs.append(throughput)
        
        # Log throughput results
        for batch_size, throughput in zip(batch_sizes, throughputs):
            if HAS_RICH:
                logger.info(f"Batch size {batch_size}: {throughput:.1f} samples/second")
            else:
                logger.info(f"Batch size {batch_size}: {throughput:.1f} samples/second")
        
        # Verify reasonable throughput
        max_throughput = max(throughputs)
        assert max_throughput > 10.0, f"Throughput too low: {max_throughput:.1f} samples/second"

# Real-World Scenario Tests
@pytest.mark.skipif(not PRIORITY_2_AVAILABLE, reason="Priority 2 components not available")
class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_streaming_audio_processing(self, test_config):
        """Test streaming audio processing scenario."""
        # Create audio extractor with streaming configuration
        config = AudioFeatureConfig(
            sample_rate=16000,
            max_duration=1.0,  # Short chunks for streaming
            device=test_config.device
        )
        
        extractor = AdvancedAudioFeatureExtractor(config)
        
        # Simulate streaming audio chunks
        chunk_duration = 1.0  # 1 second chunks
        num_chunks = 5
        chunk_samples = int(16000 * chunk_duration)
        
        embeddings = []
        
        for chunk_idx in range(num_chunks):
            # Generate audio chunk
            audio_chunk = torch.randn(1, chunk_samples)
            
            with torch.no_grad():
                chunk_embedding = extractor.extract_embeddings(
                    audio_chunk,
                    embedding_dim=test_config.latent_dim
                )
            
            embeddings.append(chunk_embedding)
        
        # Verify all chunks processed
        assert len(embeddings) == num_chunks
        for embedding in embeddings:
            assert embedding.shape == (1, test_config.latent_dim)
        
        if HAS_RICH:
            logger.info(f"✅ Streaming audio processing test passed: {num_chunks} chunks")
        else:
            logger.info(f"Streaming audio processing test passed: {num_chunks} chunks")
    
    def test_multimodal_search_scenario(self, test_config, sample_multimodal_data):
        """Test multimodal search/retrieval scenario."""
        # Create unified latent space for search
        latent_config = UnifiedLatentConfig(
            latent_dim=test_config.latent_dim,
            hidden_size=test_config.hidden_size,
            fusion_strategy="learned_attention",
            device=test_config.device
        )
        
        latent_space = UnifiedLatentSpace(latent_config)
        
        # Create query and database samples
        num_db_samples = 10
        
        # Query sample
        query_features = {
            'text': sample_multimodal_data['text'][:1],  # Single query
            'vision': torch.randn(1, 196, test_config.hidden_size),
            'audio': torch.randn(1, 64, test_config.hidden_size)
        }
        
        # Database samples
        db_features = {
            'text': torch.randn(num_db_samples, 32, test_config.hidden_size),
            'vision': torch.randn(num_db_samples, 196, test_config.hidden_size),
            'audio': torch.randn(num_db_samples, 64, test_config.hidden_size)
        }
        
        with torch.no_grad():
            # Encode query
            query_results = latent_space(query_features)
            query_embedding = query_results['unified_latent']
            
            # Encode database
            db_results = latent_space(db_features)
            db_embeddings = db_results['unified_latent']
            
            # Compute similarities
            similarities = torch.mm(query_embedding, db_embeddings.transpose(0, 1))
            top_k_indices = torch.topk(similarities, k=3, dim=1).indices
        
        # Verify search results
        assert top_k_indices.shape == (1, 3)
        assert torch.all(top_k_indices >= 0)
        assert torch.all(top_k_indices < num_db_samples)
        
        if HAS_RICH:
            logger.info(f"✅ Multimodal search test passed: found top-3 matches")
        else:
            logger.info(f"Multimodal search test passed: found top-3 matches")

# Test Suite Summary
def run_priority_2_integration_tests():
    """Run all Priority 2 integration tests."""
    if not PRIORITY_2_AVAILABLE:
        print("❌ Priority 2 components not available - cannot run integration tests")
        return False
    
    print("🚀 Running Priority 2 Integration Tests...")
    
    # Run pytest with specific markers
    import subprocess
    import sys
    
    test_file = __file__
    cmd = [
        sys.executable, "-m", "pytest", test_file,
        "-v", "--tb=short", "--maxfail=5"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Stderr:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

if __name__ == "__main__":
    success = run_priority_2_integration_tests()
    if success:
        print("✅ All Priority 2 integration tests passed!")
    else:
        print("❌ Some Priority 2 integration tests failed!")
        exit(1)
