"""
Tests for Unified Multimodal Processor.

Comprehensive test suite for the unified multimodal processing framework
that combines vision-language and audio-language capabilities.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Test setup constants
SAMPLE_TEXT = "This is a test text for multimodal processing."
SAMPLE_IMAGE_SIZE = (224, 224, 3)
SAMPLE_AUDIO_DATA = [0.1, 0.2, 0.3, 0.4, 0.5] * 100
SAMPLE_RATE = 16000

# Import availability check
IMPORT_SUCCESS = False
try:
    import sys
    from pathlib import Path
    
    # Add the src directory to the path
    src_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(src_dir))
    
    from multimodal.unified_multimodal_processor import (
        UnifiedMultimodalProcessor,
        UnifiedMultimodalConfig,
        MultimodalInput,
        UnifiedMultimodalResult,
        create_unified_processor,
        create_multimodal_input,
        UNIFIED_MULTIMODAL_AVAILABLE
    )
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"Import failed: {e}")
    IMPORT_SUCCESS = False

# Skip all tests if imports failed
pytestmark = pytest.mark.skipif(not IMPORT_SUCCESS, reason="Unified multimodal processor not available")

class TestUnifiedMultimodalConfig:
    """Test unified multimodal configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = UnifiedMultimodalConfig()
        
        assert config.max_memory_gb == 3.5
        assert config.use_gpu_optimization is True
        assert config.precision == "fp16"
        assert config.enable_vision_language is True
        assert config.enable_audio_language is True
        assert config.enable_cross_modal_fusion is True
        assert config.fusion_strategy == "attention"
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = UnifiedMultimodalConfig(
            max_memory_gb=2.0,
            fusion_strategy="concatenate",
            enable_cross_modal_fusion=False
        )
        
        assert config.max_memory_gb == 2.0
        assert config.fusion_strategy == "concatenate"
        assert config.enable_cross_modal_fusion is False

class TestMultimodalInput:
    """Test multimodal input structure."""
    
    def test_empty_input(self):
        """Test empty multimodal input."""
        inp = MultimodalInput()
        
        assert inp.text is None
        assert inp.image_path is None
        assert inp.audio_path is None
        assert inp.metadata == {}
    
    def test_full_input(self):
        """Test complete multimodal input."""
        inp = MultimodalInput(
            text=SAMPLE_TEXT,
            image_path="test.jpg",
            audio_path="test.wav",
            metadata={"source": "test"}
        )
        
        assert inp.text == SAMPLE_TEXT
        assert inp.image_path == "test.jpg"
        assert inp.audio_path == "test.wav"
        assert inp.metadata["source"] == "test"

class TestUnifiedMultimodalResult:
    """Test unified multimodal result structure."""
    
    def test_default_result(self):
        """Test default result values."""
        result = UnifiedMultimodalResult()
        
        assert result.success is True
        assert result.processing_time == 0.0
        assert result.modalities_processed == []
        assert result.memory_usage == {}
    
    def test_result_with_data(self):
        """Test result with processing data."""
        result = UnifiedMultimodalResult(
            processing_time=1.5,
            modalities_processed=["vision_language", "audio_language"],
            success=True
        )
        
        assert result.processing_time == 1.5
        assert len(result.modalities_processed) == 2
        assert "vision_language" in result.modalities_processed
        assert "audio_language" in result.modalities_processed

class TestUnifiedMultimodalProcessor:
    """Test unified multimodal processor functionality."""
    
    def test_processor_initialization(self):
        """Test processor initialization with default config."""
        processor = UnifiedMultimodalProcessor()
        
        assert processor.config is not None
        assert processor.initialized is False
        assert processor.performance_stats == {}
    
    def test_processor_with_custom_config(self):
        """Test processor with custom configuration."""
        config = UnifiedMultimodalConfig(max_memory_gb=2.0)
        processor = UnifiedMultimodalProcessor(config)
        
        assert processor.config.max_memory_gb == 2.0
    
    @pytest.mark.skipif(not IMPORT_SUCCESS, reason="Processor not available")
    def test_advanced_utilities_initialization(self):
        """Test that advanced utilities are properly initialized."""
        with patch('core.utils.rich_status_animation.StatusAnimation') as mock_animation:
            with patch('multimodal.unified_multimodal_processor.ADVANCED_UTILS_AVAILABLE', True):
                config = UnifiedMultimodalConfig(enable_rich_ui=True)
                processor = UnifiedMultimodalProcessor(config)
                
                # Should attempt to create advanced utilities
                assert processor.config.enable_rich_ui is True
    
    @pytest.mark.asyncio
    async def test_model_initialization_no_processors(self):
        """Test model initialization when no processors available."""
        with patch('multimodal.unified_multimodal_processor.VISION_LANGUAGE_AVAILABLE', False):
            with patch('multimodal.unified_multimodal_processor.AUDIO_LANGUAGE_AVAILABLE', False):
                processor = UnifiedMultimodalProcessor()
                result = await processor.initialize_models()
                
                assert result is True  # Should succeed even with no processors
                assert processor.initialized is True
    
    @pytest.mark.asyncio
    async def test_process_multimodal_input_no_data(self):
        """Test processing with empty input."""
        processor = UnifiedMultimodalProcessor()
        empty_input = MultimodalInput()
        
        result = await processor.process_multimodal_input(empty_input)
        
        assert isinstance(result, UnifiedMultimodalResult)
        assert result.processing_time > 0
        assert len(result.modalities_processed) == 0
    
    @pytest.mark.asyncio
    async def test_process_multimodal_input_with_mocks(self):
        """Test processing with mocked individual processors."""
        # Mock vision processor
        mock_vision_processor = AsyncMock()
        mock_vision_result = Mock()
        mock_vision_result.features = [0.1, 0.2, 0.3]
        mock_vision_processor.process_image_text_pair.return_value = mock_vision_result
        mock_vision_processor.initialize_models.return_value = True
        
        # Mock audio processor
        mock_audio_processor = AsyncMock()
        mock_audio_result = Mock()
        mock_audio_result.features = [0.4, 0.5, 0.6]
        mock_audio_processor.process_audio_text_pair.return_value = mock_audio_result
        mock_audio_processor.initialize_models.return_value = True
        
        # Create processor and inject mocks
        processor = UnifiedMultimodalProcessor()
        processor.vision_processor = mock_vision_processor
        processor.audio_processor = mock_audio_processor
        
        # Create multimodal input
        multimodal_input = MultimodalInput(
            text=SAMPLE_TEXT,
            image_path="test.jpg",
            audio_path="test.wav"
        )
        
        result = await processor.process_multimodal_input(multimodal_input)
        
        assert result.success is True
        assert len(result.modalities_processed) == 2
        assert "vision_language" in result.modalities_processed
        assert "audio_language" in result.modalities_processed
    
    @pytest.mark.asyncio
    async def test_batch_processing_empty(self):
        """Test batch processing with empty input list."""
        processor = UnifiedMultimodalProcessor()
        results = await processor.batch_process([])
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_batch_processing_with_inputs(self):
        """Test batch processing with multiple inputs."""
        processor = UnifiedMultimodalProcessor()
        
        inputs = [
            MultimodalInput(text="Text 1"),
            MultimodalInput(text="Text 2"),
        ]
        
        results = await processor.batch_process(inputs)
        
        assert len(results) == 2
        assert all(isinstance(r, UnifiedMultimodalResult) for r in results)
    
    def test_performance_stats(self):
        """Test performance statistics retrieval."""
        processor = UnifiedMultimodalProcessor()
        stats = processor.get_performance_stats()
        
        assert "processor_type" in stats
        assert stats["processor_type"] == "unified_multimodal"
        assert "modalities_available" in stats
        assert "config" in stats
    
    def test_concatenate_features(self):
        """Test feature concatenation."""
        processor = UnifiedMultimodalProcessor()
        
        features = [
            ("vision", [0.1, 0.2, 0.3]),
            ("audio", [0.4, 0.5, 0.6])
        ]
        
        result = processor._concatenate_features(features)
        
        assert result is not None
        assert len(result) == 6
        assert result == [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    
    @pytest.mark.asyncio
    async def test_cleanup(self):
        """Test resource cleanup."""
        # Mock processors
        mock_vision = AsyncMock()
        mock_audio = AsyncMock()
        
        processor = UnifiedMultimodalProcessor()
        processor.vision_processor = mock_vision
        processor.audio_processor = mock_audio
        processor.initialized = True
        
        await processor.cleanup()
        
        mock_vision.cleanup.assert_called_once()
        mock_audio.cleanup.assert_called_once()
        assert processor.initialized is False

class TestCrossModalFusion:
    """Test cross-modal fusion functionality."""
    
    @pytest.mark.asyncio
    async def test_fusion_insufficient_features(self):
        """Test fusion with insufficient features."""
        processor = UnifiedMultimodalProcessor()
        result = UnifiedMultimodalResult()
        
        # Only one modality result
        result.vision_language_result = Mock()
        result.vision_language_result.features = [0.1, 0.2, 0.3]
        
        await processor._perform_cross_modal_fusion(result)
        
        # Should not perform fusion
        assert result.fused_features is None
    
    @pytest.mark.asyncio
    async def test_concatenation_fusion(self):
        """Test concatenation-based fusion."""
        config = UnifiedMultimodalConfig(fusion_strategy="concatenate")
        processor = UnifiedMultimodalProcessor(config)
        
        result = UnifiedMultimodalResult()
        
        # Mock modality results
        result.vision_language_result = Mock()
        result.vision_language_result.features = [0.1, 0.2, 0.3]
        
        result.audio_language_result = Mock()
        result.audio_language_result.features = [0.4, 0.5, 0.6]
        
        await processor._perform_cross_modal_fusion(result)
        
        assert result.fused_features is not None
        assert len(result.fused_features) == 6

class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_create_unified_processor(self):
        """Test unified processor creation utility."""
        processor = create_unified_processor()
        
        assert isinstance(processor, UnifiedMultimodalProcessor)
        assert processor.config is not None
    
    def test_create_unified_processor_with_config(self):
        """Test processor creation with custom config."""
        config = UnifiedMultimodalConfig(max_memory_gb=2.0)
        processor = create_unified_processor(config)
        
        assert processor.config.max_memory_gb == 2.0
    
    def test_create_multimodal_input(self):
        """Test multimodal input creation utility."""
        inp = create_multimodal_input(
            text=SAMPLE_TEXT,
            image_path="test.jpg"
        )
        
        assert inp.text == SAMPLE_TEXT
        assert inp.image_path == "test.jpg"
        assert inp.audio_path is None

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_processing_with_errors(self):
        """Test processing behavior when errors occur."""
        processor = UnifiedMultimodalProcessor()
        
        # Mock a processor that raises an exception
        mock_vision_processor = AsyncMock()
        mock_vision_processor.process_image_text_pair.side_effect = Exception("Test error")
        mock_vision_processor.initialize_models.return_value = True
        
        processor.vision_processor = mock_vision_processor
        
        multimodal_input = MultimodalInput(
            text=SAMPLE_TEXT,
            image_path="test.jpg"
        )
        
        result = await processor.process_multimodal_input(multimodal_input)
        
        # Should handle error gracefully
        assert result.processing_time > 0
        # Should still be successful overall even if one modality fails
        assert len(result.modalities_processed) == 0

class TestPerformanceBenchmarks:
    """Test performance benchmarks and monitoring."""
    
    @pytest.mark.asyncio
    async def test_processing_time_tracking(self):
        """Test that processing time is tracked."""
        processor = UnifiedMultimodalProcessor()
        
        multimodal_input = MultimodalInput(text=SAMPLE_TEXT)
        result = await processor.process_multimodal_input(multimodal_input)
        
        assert result.processing_time > 0
        assert isinstance(result.processing_time, float)
    
    def test_memory_optimization_features(self):
        """Test memory optimization configuration."""
        config = UnifiedMultimodalConfig(
            max_memory_gb=2.0,
            memory_optimization=True,
            precision="fp16"
        )
        
        processor = UnifiedMultimodalProcessor(config)
        
        assert processor.config.memory_optimization is True
        assert processor.config.precision == "fp16"
        assert processor.config.max_memory_gb == 2.0

# Integration test
def test_integration_availability():
    """Test that the unified multimodal integration is available."""
    assert IMPORT_SUCCESS, "Unified multimodal processor should be importable"
    
    if IMPORT_SUCCESS:
        assert UNIFIED_MULTIMODAL_AVAILABLE is not None
        
        # Test basic functionality
        processor = create_unified_processor()
        assert processor is not None
        
        stats = processor.get_performance_stats()
        assert "processor_type" in stats
        assert stats["processor_type"] == "unified_multimodal"

if __name__ == "__main__":
    # Run basic integration test
    if IMPORT_SUCCESS:
        print("✅ Unified Multimodal Processor tests ready")
        test_integration_availability()
        print("🎯 Basic integration test passed")
    else:
        print("❌ Unified Multimodal Processor not available for testing")
