"""
Test suite for Audio-Language Integration Framework.

Tests the AudioLanguageProcessor with comprehensive mocking for dependencies.
Validates integration with existing audio framework and advanced utilities.

Created: 2025-06-01
Modified: 2025-06-01
Version: 1.0.0
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
import asyncio
import numpy as np
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from multimodal.audio_language_integration import (
        AudioLanguageProcessor,
        AudioLanguageConfig, 
        AudioLanguageResult,
        load_audio_file,
        create_audio_language_processor,
        AL_INTEGRATION_AVAILABLE
    )
    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False
    print(f"Import failed: {e}")

# Test data constants
SAMPLE_RATE = 16000
AUDIO_DURATION = 5.0  # seconds
SAMPLE_AUDIO_DATA = np.random.randn(int(SAMPLE_RATE * AUDIO_DURATION))
SAMPLE_TEXT = "This is a test transcription"

class TestAudioLanguageConfig:
    """Test AudioLanguageConfig configuration class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        config = AudioLanguageConfig()
        
        # Audio processing defaults
        assert config.model_name == "openai/whisper-base"
        assert config.sample_rate == 16000
        assert config.max_audio_duration == 30.0
        assert config.chunk_size == 1024
        
        # Feature extraction defaults
        assert config.n_mels == 80
        assert config.n_mfcc == 13
        assert config.n_fft == 512
        assert config.hop_length == 160
        
        # Hardware optimization defaults
        assert config.use_gpu_optimization is True
        assert config.max_memory_gb == 3.5
        
        # Advanced features defaults
        assert config.enable_rich_ui is True
        assert config.performance_monitoring is True
        assert config.enable_vad is True
        assert config.enable_emotion_recognition is False
        assert config.enable_speaker_identification is False
    
    def test_custom_config(self):
        """Test custom configuration values."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        config = AudioLanguageConfig(
            model_name="custom/model",
            sample_rate=22050,
            max_audio_duration=60.0,
            enable_emotion_recognition=True,
            enable_speaker_identification=True,
            max_memory_gb=8.0
        )
        
        assert config.model_name == "custom/model"
        assert config.sample_rate == 22050
        assert config.max_audio_duration == 60.0
        assert config.enable_emotion_recognition is True
        assert config.enable_speaker_identification is True
        assert config.max_memory_gb == 8.0

class TestAudioLanguageResult:
    """Test AudioLanguageResult structure."""
    
    def test_default_result(self):
        """Test default result values."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        result = AudioLanguageResult()
        
        assert result.transcription == ""
        assert result.language_detected == ""
        assert result.confidence_score == 0.0
        assert isinstance(result.audio_features, dict)
        assert isinstance(result.emotions, dict)
        assert isinstance(result.vad_segments, list)
        assert isinstance(result.metadata, dict)
    
    def test_result_with_data(self):
        """Test result with actual data."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        result = AudioLanguageResult(
            transcription="Test transcription",
            language_detected="en",
            confidence_score=0.95,
            processing_time=1.5,
            emotions={"happy": 0.8, "neutral": 0.2}
        )
        
        assert result.transcription == "Test transcription"
        assert result.language_detected == "en"
        assert result.confidence_score == 0.95
        assert result.processing_time == 1.5
        assert result.emotions["happy"] == 0.8

class TestAudioLanguageProcessor:
    """Test AudioLanguageProcessor main functionality."""
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        processor = AudioLanguageProcessor()
        
        assert processor.config is not None
        assert processor.is_initialized is False
        assert isinstance(processor.processing_stats, dict)
        assert processor.processing_stats["total_processed"] == 0
    
    def test_advanced_utilities_initialization(self):
        """Test advanced utilities initialization."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        config = AudioLanguageConfig(enable_rich_ui=True, performance_monitoring=True)
        
        with patch('multimodal.audio_language_integration.ADVANCED_UTILS_AVAILABLE', True):
            with patch('multimodal.audio_language_integration.GPUMemoryManager') as mock_gpu:
                with patch('core.utils.rich_status_animation.StatusAnimation') as mock_animation:
                    processor = AudioLanguageProcessor(config)
                    
                    # Should attempt to create advanced utilities
                    assert processor.config.enable_rich_ui is True
                    assert processor.config.performance_monitoring is True
    
    @pytest.mark.skipif(not AL_INTEGRATION_AVAILABLE, reason="Audio-Language integration not available")
    async def test_model_initialization_without_torch(self):
        """Test model initialization without PyTorch."""
        processor = AudioLanguageProcessor()
        
        with patch('multimodal.audio_language_integration.TORCH_AVAILABLE', False):
            result = await processor.initialize_models()
            assert result is False
    
    @pytest.mark.skipif(not AL_INTEGRATION_AVAILABLE, reason="Audio-Language integration not available")  
    async def test_model_initialization_with_mocked_torch(self):
        """Test model initialization with mocked PyTorch."""
        processor = AudioLanguageProcessor()
        
        with patch('multimodal.audio_language_integration.TORCH_AVAILABLE', True):
            with patch('multimodal.audio_language_integration.AUDIO_FRAMEWORK_AVAILABLE', True):
                with patch('multimodal.audio_language_integration.AdvancedAudioFeatureExtractor') as mock_extractor:
                    mock_extractor.return_value = Mock()
                    
                    result = await processor.initialize_models()
                    assert result is True
                    assert processor.is_initialized is True
    
    @pytest.mark.skipif(not AL_INTEGRATION_AVAILABLE, reason="Audio-Language integration not available")
    async def test_process_audio_text_pair_not_initialized(self):
        """Test processing without initialization."""
        processor = AudioLanguageProcessor()
        
        result = await processor.process_audio_text_pair(SAMPLE_AUDIO_DATA, "test text")
        
        assert "Error" in result.transcription
        assert result.confidence_score == 0.0
        assert "processor_not_initialized" in result.metadata
    
    @pytest.mark.skipif(not AL_INTEGRATION_AVAILABLE, reason="Audio-Language integration not available")
    async def test_process_audio_text_pair_mocked(self):
        """Test audio-text processing with mocks."""
        processor = AudioLanguageProcessor()
        processor.is_initialized = True
        
        # Mock audio extractor
        mock_extractor = Mock()
        mock_extractor.extract_all_features = AsyncMock(return_value={
            'mfcc': np.random.randn(13, 100),
            'mel_spectrogram': np.random.randn(80, 100),
            'embeddings': np.random.randn(512),
            'vad': np.random.randn(100)
        })
        processor.audio_extractor = mock_extractor
        
        # Mock private methods
        processor._transcribe_audio = AsyncMock(return_value="Mocked transcription")
        processor._detect_language = AsyncMock(return_value="en")
        processor._calculate_confidence = AsyncMock(return_value=0.85)
        
        result = await processor.process_audio_text_pair(SAMPLE_AUDIO_DATA, "test context")
        
        assert result.transcription == "Mocked transcription"
        assert result.language_detected == "en"
        assert result.confidence_score == 0.85
        assert isinstance(result.audio_features, dict)
    
    @pytest.mark.skipif(not AL_INTEGRATION_AVAILABLE, reason="Audio-Language integration not available")
    async def test_batch_processing(self):
        """Test batch processing functionality."""
        processor = AudioLanguageProcessor()
        processor.is_initialized = True
        
        # Mock the single processing method
        async def mock_process(audio, text, return_features=True):
            return AudioLanguageResult(
                transcription=f"Processed audio with {len(audio)} samples",
                confidence_score=0.8,
                processing_time=0.5
            )
        
        processor.process_audio_text_pair = mock_process
        
        # Test batch processing
        audio_inputs = [SAMPLE_AUDIO_DATA, SAMPLE_AUDIO_DATA]
        text_contexts = ["context 1", "context 2"]
        
        results = await processor.batch_process(audio_inputs, text_contexts)
        
        assert len(results) == 2
        assert all(isinstance(r, AudioLanguageResult) for r in results)
        assert all(r.confidence_score == 0.8 for r in results)
    
    @pytest.mark.skipif(not AL_INTEGRATION_AVAILABLE, reason="Audio-Language integration not available")
    async def test_batch_processing_mismatched_lengths(self):
        """Test batch processing with mismatched input lengths."""
        processor = AudioLanguageProcessor()
        
        audio_inputs = [SAMPLE_AUDIO_DATA, SAMPLE_AUDIO_DATA]
        text_contexts = ["context 1"]  # Mismatched length
        
        with pytest.raises(ValueError, match="Number of audio inputs must match"):
            await processor.batch_process(audio_inputs, text_contexts)
    
    def test_performance_stats(self):
        """Test performance statistics tracking."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        processor = AudioLanguageProcessor()
        stats = processor.get_performance_stats()
        
        assert isinstance(stats, dict)
        assert "total_processed" in stats
        assert "average_processing_time" in stats
        assert "success_rate" in stats
        assert "configuration" in stats
        
        # Check configuration info
        assert stats["configuration"]["model_name"] == processor.config.model_name
        assert stats["configuration"]["sample_rate"] == processor.config.sample_rate
    
    @pytest.mark.skipif(not AL_INTEGRATION_AVAILABLE, reason="Audio-Language integration not available")
    async def test_cleanup(self):
        """Test resource cleanup."""
        processor = AudioLanguageProcessor()
        processor.is_initialized = True
        
        # Mock GPU manager
        mock_gpu_manager = Mock()
        mock_gpu_manager.cleanup = Mock()
        processor.gpu_manager = mock_gpu_manager
        
        await processor.cleanup()
        
        assert processor.is_initialized is False
        assert processor.processing_stats["total_processed"] == 0
        mock_gpu_manager.cleanup.assert_called_once()

class TestAudioLanguageIntegration:
    """Test full Audio-Language integration scenarios."""
    
    @pytest.mark.skipif(not AL_INTEGRATION_AVAILABLE, reason="Audio-Language integration not available")
    async def test_full_pipeline_mock(self):
        """Test complete processing pipeline with mocks."""
        config = AudioLanguageConfig(
            enable_emotion_recognition=True,
            enable_vad=True,
            enable_rich_ui=False  # Disable for testing
        )
        
        processor = AudioLanguageProcessor(config)
        processor.is_initialized = True
        
        # Mock all dependencies
        mock_extractor = Mock()
        mock_features = {
            'mfcc': np.random.randn(13, 100),
            'mel_spectrogram': np.random.randn(80, 100),
            'embeddings': np.random.randn(512),
            'vad': np.random.randn(100),
            'emotion_logits': np.random.randn(8)
        }
        mock_extractor.extract_all_features = AsyncMock(return_value=mock_features)
        processor.audio_extractor = mock_extractor
        
        # Mock processing methods
        processor._transcribe_audio = AsyncMock(return_value="Complete transcription")
        processor._detect_language = AsyncMock(return_value="en")
        processor._extract_vad_segments = AsyncMock(return_value=[(0.0, 3.0), (4.0, 5.0)])
        processor._extract_emotions = AsyncMock(return_value={"happy": 0.7, "neutral": 0.3})
        processor._calculate_confidence = AsyncMock(return_value=0.92)
        
        # Process audio-text pair
        result = await processor.process_audio_text_pair(
            SAMPLE_AUDIO_DATA,
            "This is test context",
            return_features=True
        )
        
        # Verify results
        assert result.transcription == "Complete transcription"
        assert result.language_detected == "en"
        assert result.confidence_score == 0.92
        assert len(result.vad_segments) == 2
        assert "happy" in result.emotions
        assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in processing."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        config = AudioLanguageConfig(model_name="test/model")
        
        with patch('multimodal.audio_language_integration.ADVANCED_UTILS_AVAILABLE', False):
            processor = AudioLanguageProcessor(config)
            
            # Test with uninitialized processor
            result = await processor.process_audio_text_pair("test.wav", "test text")
            
            assert "Error" in result.transcription
            assert result.confidence_score == 0.0
            assert "error" in result.metadata
    
    def test_memory_optimization_features(self):
        """Test memory optimization configuration."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        config = AudioLanguageConfig(
            max_memory_gb=3.5,
            use_gpu_optimization=True,
            precision="fp16",
            max_audio_duration=30.0
        )
        
        assert config.max_memory_gb == 3.5
        assert config.use_gpu_optimization is True
        assert config.precision == "fp16"
        assert config.max_audio_duration == 30.0

class TestUtilityFunctions:
    """Test utility functions for Audio-Language integration."""    
    @pytest.mark.asyncio
    async def test_load_audio_file_mock(self):
        """Test audio file loading with mocks."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        # Skip if librosa not available for proper testing
        try:
            import librosa
        except ImportError:
            pytest.skip("librosa not available for mocking")
        
        with patch('multimodal.audio_language_integration.LIBROSA_AVAILABLE', True):
            with patch('librosa.load') as mock_load:
                mock_load.return_value = (SAMPLE_AUDIO_DATA, SAMPLE_RATE)
                
                result = await load_audio_file("test.wav", sample_rate=SAMPLE_RATE)
                
                assert result is not None
                assert len(result) == len(SAMPLE_AUDIO_DATA)
                mock_load.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_load_audio_file_fallback(self):
        """Test audio file loading fallback."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        with patch('multimodal.audio_language_integration.LIBROSA_AVAILABLE', False):
            result = await load_audio_file("test.wav", sample_rate=SAMPLE_RATE)
            
            assert result is not None
            assert len(result) > 0  # Should return placeholder data
    
    def test_create_audio_language_processor(self):
        """Test processor creation utility."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        processor = create_audio_language_processor(
            model_name="custom/model",
            enable_advanced_features=True,
            hardware_optimization=True
        )
        
        assert isinstance(processor, AudioLanguageProcessor)
        assert processor.config.model_name == "custom/model"
        assert processor.config.enable_emotion_recognition is True
        assert processor.config.enable_speaker_identification is True
        assert processor.config.use_gpu_optimization is True
        assert processor.config.max_memory_gb == 3.5

class TestPerformanceBenchmarks:
    """Test performance and benchmarking features."""
    
    def test_processing_time_tracking(self):
        """Test processing time tracking."""
        if not IMPORT_SUCCESS:
            pytest.skip("Audio-Language integration not available")
        
        config = AudioLanguageConfig(
            model_name="test/model",
            performance_monitoring=True
        )
        
        with patch('multimodal.audio_language_integration.ADVANCED_UTILS_AVAILABLE', False):
            processor = AudioLanguageProcessor(config)
            stats = processor.get_performance_stats()
            
            assert "total_processing_time" in stats
            assert "average_processing_time" in stats
            assert stats["total_processing_time"] == 0.0
    
    @pytest.mark.skipif(not AL_INTEGRATION_AVAILABLE, reason="Audio-Language integration not available")
    async def test_memory_usage_tracking(self):
        """Test memory usage tracking."""
        processor = AudioLanguageProcessor()
        processor.is_initialized = True
        
        # Mock GPU manager
        mock_gpu_manager = Mock()
        mock_gpu_manager.get_memory_usage.return_value = {
            'used_mb': 1500,
            'free_mb': 2500,
            'total_mb': 4000
        }
        processor.gpu_manager = mock_gpu_manager
        
        # Mock processing
        processor.audio_extractor = Mock()
        processor.audio_extractor.extract_all_features = AsyncMock(return_value={'embeddings': np.random.randn(512)})
        processor._transcribe_audio = AsyncMock(return_value="test")
        processor._detect_language = AsyncMock(return_value="en")
        processor._calculate_confidence = AsyncMock(return_value=0.8)
        
        result = await processor.process_audio_text_pair(SAMPLE_AUDIO_DATA)
        
        assert "memory_usage" in result.memory_usage
        stats = processor.get_performance_stats()
        assert "current_gpu_memory_mb" in stats

# Integration availability check
def test_integration_availability():
    """Test that integration availability is properly detected."""
    if IMPORT_SUCCESS:
        from multimodal.audio_language_integration import AL_INTEGRATION_AVAILABLE
        # AL_INTEGRATION_AVAILABLE should be boolean
        assert isinstance(AL_INTEGRATION_AVAILABLE, bool)
    else:
        pytest.skip("Audio-Language integration import failed")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
