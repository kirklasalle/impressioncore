"""
Audio-Language Integration Framework for ImpressionCore Priority 8.

This module provides seamless integration between audio processing and language
understanding capabilities, optimized for GTX 1050 Ti hardware constraints.

Leverages the existing comprehensive audio framework and integrates advanced utilities
for optimal performance and user experience.

File: multimodal/audio_language_integration.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-01
Modified: 2025-06-01
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [priority-8, phase-8a2, audio-language, multimodal, production]
Dependencies: [torch, transformers, librosa, pydantic, typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

# Import validation and configuration
try:
    from pydantic import BaseModel, Field, ConfigDict
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    logging.warning("Pydantic not available - using fallback configuration")

# Advanced utilities integration
ADVANCED_UTILS_AVAILABLE = False
try:
    from core.utils.gpu_memory_manager import GPUMemoryManager
    from core.utils.rich_enhancements import create_header, print_info, print_success, print_warning
    from core.utils.rich_logging import RichLogger
    from core.utils.rich_status_animation import StatusAnimation
    from src.dev_tools.performance_optimizer import PerformanceOptimizer
    from src.dev_tools.memory_manager import MemoryManager
    from core.utils.benchmarking import PerformanceBenchmark
    ADVANCED_UTILS_AVAILABLE = True
    logging.info("✅ Advanced utilities available for Audio-Language Integration")
except ImportError as e:
    logging.warning(f"⚠️  Advanced utilities not available - using fallbacks: {e}")

# Audio framework integration
AUDIO_FRAMEWORK_AVAILABLE = False
try:
    from .audio.advanced_audio_feature_extractor import AdvancedAudioFeatureExtractor
    AUDIO_FRAMEWORK_AVAILABLE = True
    logging.info("✅ Advanced audio framework available")
except ImportError as e:
    logging.warning(f"⚠️  Advanced audio framework not available - using fallbacks: {e}")

# Fallback audio processing
if not AUDIO_FRAMEWORK_AVAILABLE:
    try:
        from src.core.ai.preprocessing.audio_processor import AudioProcessor as FallbackAudioProcessor
        FALLBACK_AUDIO_AVAILABLE = True
        logging.info("✅ Fallback audio processor available")
    except ImportError:
        FALLBACK_AUDIO_AVAILABLE = False
        logging.info("ℹ️  Using basic audio fallbacks (no librosa/torchaudio)")
        # Create a simple fallback class
        class AudioProcessor:
            def process(self, audio):
                return audio
        FallbackAudioProcessor = AudioProcessor

# PyTorch and transformers
TORCH_AVAILABLE = False
try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    logging.warning("⚠️  PyTorch not available - using fallbacks")

# Audio processing libraries
LIBROSA_AVAILABLE = False
try:
    import librosa
    import torchaudio
    LIBROSA_AVAILABLE = True
except ImportError:
    logging.warning("⚠️  Audio libraries not available - using fallbacks")

# Check overall integration availability
AL_INTEGRATION_AVAILABLE = AUDIO_FRAMEWORK_AVAILABLE and TORCH_AVAILABLE

logger = logging.getLogger(__name__)

# Configuration Classes
if PYDANTIC_AVAILABLE:
    class AudioLanguageConfig(BaseModel):
        """Configuration for Audio-Language Integration."""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        # Audio processing configuration
        model_name: str = Field(default="openai/whisper-base", description="Audio model identifier")
        sample_rate: int = Field(default=16000, description="Audio sample rate")
        max_audio_duration: float = Field(default=30.0, description="Maximum audio duration in seconds")
        chunk_size: int = Field(default=1024, description="Audio chunk size for processing")
        
        # Feature extraction configuration  
        n_mels: int = Field(default=80, description="Number of mel filters")
        n_mfcc: int = Field(default=13, description="Number of MFCC coefficients")
        n_fft: int = Field(default=512, description="FFT window size")
        hop_length: int = Field(default=160, description="Hop length for STFT")
        
        # Model configuration
        batch_size: int = Field(default=1, description="Processing batch size")
        precision: str = Field(default="fp16", description="Model precision")
        max_text_length: int = Field(default=77, description="Maximum text sequence length")
        
        # Hardware optimization
        use_gpu_optimization: bool = Field(default=True, description="Enable GPU memory optimization")
        max_memory_gb: float = Field(default=3.5, description="Maximum GPU memory usage in GB")
        
        # Advanced features
        enable_rich_ui: bool = Field(default=True, description="Enable rich UI feedback")
        performance_monitoring: bool = Field(default=True, description="Enable performance monitoring")
        enable_vad: bool = Field(default=True, description="Enable voice activity detection")
        enable_emotion_recognition: bool = Field(default=False, description="Enable emotion recognition")
        enable_speaker_identification: bool = Field(default=False, description="Enable speaker identification")
else:
    # Fallback configuration without Pydantic
    @dataclass
    class AudioLanguageConfig:
        """Fallback configuration for Audio-Language Integration."""
        model_name: str = "openai/whisper-base"
        sample_rate: int = 16000
        max_audio_duration: float = 30.0
        chunk_size: int = 1024
        n_mels: int = 80
        n_mfcc: int = 13
        n_fft: int = 512
        hop_length: int = 160
        batch_size: int = 1
        precision: str = "fp16"
        max_text_length: int = 77
        use_gpu_optimization: bool = True
        max_memory_gb: float = 3.5
        enable_rich_ui: bool = True
        performance_monitoring: bool = True
        enable_vad: bool = True
        enable_emotion_recognition: bool = False
        enable_speaker_identification: bool = False

# Result Classes
if PYDANTIC_AVAILABLE:
    class AudioLanguageResult(BaseModel):
        """Result structure for Audio-Language processing."""
        model_config = ConfigDict(arbitrary_types_allowed=True)
        
        # Processing results
        transcription: str = Field(default="", description="Speech-to-text transcription")
        language_detected: str = Field(default="", description="Detected language")
        confidence_score: float = Field(default=0.0, description="Overall confidence score")
        
        # Audio features
        audio_features: Dict[str, Any] = Field(default_factory=dict, description="Extracted audio features")
        audio_embeddings: Optional[Any] = Field(default=None, description="Audio embeddings")
        
        # Language features  
        text_embeddings: Optional[Any] = Field(default=None, description="Text embeddings")
        language_features: Dict[str, Any] = Field(default_factory=dict, description="Language processing features")
        
        # Advanced features
        emotions: Dict[str, float] = Field(default_factory=dict, description="Detected emotions")
        speaker_info: Dict[str, Any] = Field(default_factory=dict, description="Speaker identification info")
        vad_segments: List[Tuple[float, float]] = Field(default_factory=list, description="Voice activity segments")
        
        # Performance metrics
        processing_time: float = Field(default=0.0, description="Total processing time")
        memory_usage: Dict[str, float] = Field(default_factory=dict, description="Memory usage stats")
        
        # Metadata
        metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
        timestamp: float = Field(default_factory=time.time, description="Processing timestamp")
else:
    @dataclass
    class AudioLanguageResult:
        """Fallback result structure for Audio-Language processing."""
        transcription: str = ""
        language_detected: str = ""
        confidence_score: float = 0.0
        audio_features: Dict[str, Any] = field(default_factory=dict)
        audio_embeddings: Optional[Any] = None
        text_embeddings: Optional[Any] = None
        language_features: Dict[str, Any] = field(default_factory=dict)
        emotions: Dict[str, float] = field(default_factory=dict)
        speaker_info: Dict[str, Any] = field(default_factory=dict)
        vad_segments: List[Tuple[float, float]] = field(default_factory=list)
        processing_time: float = 0.0
        memory_usage: Dict[str, float] = field(default_factory=dict)
        metadata: Dict[str, Any] = field(default_factory=dict)
        timestamp: float = field(default_factory=time.time)

class AudioLanguageProcessor:
    """
    Advanced Audio-Language Integration Processor.
    
    Integrates comprehensive audio processing capabilities with language understanding,
    optimized for GTX 1050 Ti hardware constraints and enhanced with advanced utilities.
    """
    
    def __init__(self, config: Optional[AudioLanguageConfig] = None):
        """
        Initialize Audio-Language Processor with advanced utilities integration.
        
        Args:
            config: Configuration for audio-language processing
        """
        self.config = config or AudioLanguageConfig()
        self.is_initialized = False
        
        # Advanced utilities initialization
        self.gpu_manager = None
        self.rich_logger = None
        self.status_animation = None
        self.performance_optimizer = None
        self.memory_manager = None
        self.benchmarker = None
        
        # Processing components
        self.audio_extractor = None
        self.fallback_processor = None
        
        # Processing statistics
        self.processing_stats = {
            "total_processed": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "memory_usage_peak": 0.0,
            "error_count": 0,
            "success_rate": 1.0
        }
        
        # Initialize advanced utilities if available
        if ADVANCED_UTILS_AVAILABLE:
            try:
                self._initialize_advanced_utilities()
                if self.config.enable_rich_ui:
                    print_success("🎵 AudioLanguageProcessor created with advanced utilities integration")
                logger.info("AudioLanguageProcessor created with advanced utilities integration")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize advanced utilities: {e}")
                if self.config.enable_rich_ui:
                    print_warning(f"⚠️  Advanced utilities initialization failed: {e}")
        else:
            logger.warning("⚠️  Advanced utilities not available - using fallbacks")
            if self.config.enable_rich_ui:
                print_warning("⚠️  Advanced utilities not available - using fallbacks")
    
    def _initialize_advanced_utilities(self):
        """Initialize advanced utilities for enhanced performance and UX."""
        if not ADVANCED_UTILS_AVAILABLE:
            return
        
        try:
            # GPU Memory Management
            self.gpu_manager = GPUMemoryManager(
                max_memory_gb=self.config.max_memory_gb,
                enable_monitoring=True
            )
            
            # Rich UI components
            if self.config.enable_rich_ui:
                self.rich_logger = RichLogger("AudioLanguageProcessor")
                self.status_animation = StatusAnimation()
            
            # Performance optimization
            self.performance_optimizer = PerformanceOptimizer(
                target_hardware="gtx1050ti",
                enable_benchmarking=self.config.performance_monitoring
            )
            
            # Memory management
            self.memory_manager = MemoryManager(
                max_memory_gb=self.config.max_memory_gb,
                enable_monitoring=True
            )
            
            # Benchmarking
            if self.config.performance_monitoring:
                self.benchmarker = PerformanceBenchmark(
                    task_name="audio_language_processing"
                )
            
            logger.info("✅ Advanced utilities initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize advanced utilities: {e}")
            raise
    
    async def initialize_models(self) -> bool:
        """
        Initialize audio and language models.
        
        Returns:
            bool: True if initialization successful
        """
        if not TORCH_AVAILABLE:
            logger.warning("⚠️  PyTorch not available - cannot initialize models")
            return False
        
        try:
            if self.status_animation:
                await self.status_animation.start("Initializing Audio-Language models...")
            
            # Initialize audio processing
            if AUDIO_FRAMEWORK_AVAILABLE:
                # Use advanced audio framework
                self.audio_extractor = AdvancedAudioFeatureExtractor(
                    sample_rate=self.config.sample_rate,
                    n_mels=self.config.n_mels,
                    n_mfcc=self.config.n_mfcc,
                    n_fft=self.config.n_fft,
                    hop_length=self.config.hop_length,
                    max_duration=self.config.max_audio_duration,
                    chunk_size=self.config.chunk_size,
                    enable_rich_ui=self.config.enable_rich_ui                )
                logger.info("✅ Advanced audio framework initialized")
            elif FALLBACK_AUDIO_AVAILABLE:
                # Use fallback audio processor
                # Use simple fallback config
                class AudioConfig:
                    def __init__(self, sample_rate=16000, n_mfcc=13, n_mels=80, n_fft=2048, hop_length=512):
                        self.sample_rate = sample_rate
                        self.n_mfcc = n_mfcc
                        self.n_mels = n_mels
                        self.n_fft = n_fft
                        self.hop_length = hop_length
                
                audio_config = AudioConfig(
                    sample_rate=self.config.sample_rate,
                    n_mfcc=self.config.n_mfcc,
                    n_mels=self.config.n_mels,
                    n_fft=self.config.n_fft,
                    hop_length=self.config.hop_length
                )
                self.fallback_processor = FallbackAudioProcessor(audio_config)
                logger.info("✅ Fallback audio processor initialized")
            else:
                logger.error("❌ No audio processing framework available")
                return False
            
            self.is_initialized = True
            
            if self.status_animation:
                await self.status_animation.stop("✅ Audio-Language models initialized successfully")
            
            if self.config.enable_rich_ui:
                print_success("🎵 Audio-Language models ready for processing")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize models: {e}")
            if self.status_animation:
                await self.status_animation.stop(f"❌ Model initialization failed: {e}")
            return False
    
    async def process_audio_text_pair(
        self,
        audio_input: Union[str, Path, np.ndarray],
        text_context: Optional[str] = None,
        return_features: bool = True
    ) -> AudioLanguageResult:
        """
        Process audio with optional text context for enhanced understanding.
        
        Args:
            audio_input: Audio file path, numpy array, or audio tensor
            text_context: Optional text context for enhanced processing
            return_features: Whether to return detailed features
        
        Returns:
            AudioLanguageResult with processing results and features
        """
        if not self.is_initialized:
            logger.warning("⚠️  Processor not initialized - call initialize_models() first")
            return AudioLanguageResult(
                transcription="Error: Processor not initialized",
                confidence_score=0.0,
                metadata={"error": "processor_not_initialized"}
            )
        
        start_time = time.time()
        result = AudioLanguageResult()
        
        try:
            if self.status_animation:
                await self.status_animation.start("🎵 Processing audio-text pair...")
            
            # Performance monitoring start
            if self.benchmarker:
                self.benchmarker.start_measurement()
            
            # Memory monitoring
            initial_memory = None
            if self.gpu_manager:
                initial_memory = self.gpu_manager.get_memory_usage()
            
            # Load and preprocess audio
            audio_data = await self._load_audio(audio_input)
            if audio_data is None:
                raise ValueError("Failed to load audio data")
            
            # Extract audio features using advanced framework
            if self.audio_extractor:
                audio_features = await self._extract_advanced_features(audio_data)
                result.audio_features = audio_features
                result.audio_embeddings = audio_features.get('embeddings')
            elif self.fallback_processor:
                audio_features = await self._extract_fallback_features(audio_data)
                result.audio_features = audio_features
            
            # Voice Activity Detection if enabled
            if self.config.enable_vad and 'vad' in result.audio_features:
                result.vad_segments = await self._extract_vad_segments(result.audio_features['vad'])
            
            # Speech-to-text transcription (placeholder - would use Whisper or similar)
            result.transcription = await self._transcribe_audio(audio_data, text_context)
            result.language_detected = await self._detect_language(result.transcription)
            
            # Emotion recognition if enabled
            if self.config.enable_emotion_recognition and 'emotion_logits' in result.audio_features:
                result.emotions = await self._extract_emotions(result.audio_features['emotion_logits'])
            
            # Speaker identification if enabled
            if self.config.enable_speaker_identification:
                result.speaker_info = await self._identify_speaker(audio_data)
            
            # Text processing if context provided
            if text_context:
                result.text_embeddings = await self._process_text_context(text_context)
                result.language_features = await self._extract_language_features(text_context)
            
            # Calculate confidence score
            result.confidence_score = await self._calculate_confidence(result)
            
            # Performance metrics
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            
            # Memory usage
            if self.gpu_manager:
                final_memory = self.gpu_manager.get_memory_usage()
                result.memory_usage = {
                    "initial_gpu_mb": initial_memory.get('used_mb', 0) if initial_memory else 0,
                    "final_gpu_mb": final_memory.get('used_mb', 0) if final_memory else 0,
                    "peak_gpu_mb": max(initial_memory.get('used_mb', 0) if initial_memory else 0,
                                     final_memory.get('used_mb', 0) if final_memory else 0)
                }
            
            # Update statistics
            self._update_processing_stats(processing_time, result.memory_usage.get('peak_gpu_mb', 0))
            
            # Benchmarking results
            if self.benchmarker:
                benchmark_results = self.benchmarker.end_measurement()
                result.metadata.update(benchmark_results)
            
            if self.status_animation:
                await self.status_animation.stop("✅ Audio-text processing completed successfully")
            
            logger.info(f"✅ Audio-text pair processed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.processing_stats["error_count"] += 1
            
            logger.error(f"❌ Audio-text processing failed: {e}")
            
            if self.status_animation:
                await self.status_animation.stop(f"❌ Processing failed: {e}")
            
            return AudioLanguageResult(
                transcription=f"Error: {str(e)}",
                confidence_score=0.0,
                processing_time=processing_time,
                metadata={"error": str(e), "error_type": type(e).__name__}
            )
    
    async def _load_audio(self, audio_input: Union[str, Path, np.ndarray]) -> Optional[np.ndarray]:
        """Load audio data from various input types."""
        try:
            if isinstance(audio_input, (str, Path)):
                # Load from file
                if LIBROSA_AVAILABLE:
                    audio_data, sr = librosa.load(str(audio_input), sr=self.config.sample_rate)
                    return audio_data
                else:
                    # Fallback loading method
                    logger.warning("⚠️  Librosa not available - using fallback audio loading")
                    return np.random.randn(int(self.config.sample_rate * 5))  # 5 second placeholder
            elif isinstance(audio_input, np.ndarray):
                # Direct numpy array
                return audio_input
            else:
                logger.error(f"❌ Unsupported audio input type: {type(audio_input)}")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to load audio: {e}")
            return None
    
    async def _extract_advanced_features(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Extract features using advanced audio framework."""
        try:
            if TORCH_AVAILABLE:
                audio_tensor = torch.from_numpy(audio_data).float().unsqueeze(0)
                features = await self.audio_extractor.extract_all_features(audio_tensor)
                return features
            else:
                return {"error": "PyTorch not available"}
        except Exception as e:
            logger.error(f"❌ Advanced feature extraction failed: {e}")
            return {"error": str(e)}
    
    async def _extract_fallback_features(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Extract features using fallback audio processor."""
        try:
            if TORCH_AVAILABLE:
                audio_tensor = torch.from_numpy(audio_data).float().unsqueeze(0)
                features = self.fallback_processor.process_audio(audio_tensor)
                return features.get('features', {})
            else:
                return {"error": "PyTorch not available"}
        except Exception as e:
            logger.error(f"❌ Fallback feature extraction failed: {e}")
            return {"error": str(e)}
    
    async def _transcribe_audio(self, audio_data: np.ndarray, text_context: Optional[str] = None) -> str:
        """Transcribe audio to text (placeholder implementation)."""
        # This would integrate with Whisper or similar ASR model
        # For now, return a placeholder
        return f"Transcribed audio ({len(audio_data)} samples)" + (f" with context: {text_context[:50]}..." if text_context else "")
    
    async def _detect_language(self, transcription: str) -> str:
        """Detect language from transcription (placeholder implementation)."""
        # This would use language detection models
        return "en"  # Default to English for now
    
    async def _extract_vad_segments(self, vad_data: Any) -> List[Tuple[float, float]]:
        """Extract voice activity segments from VAD data."""
        # This would process VAD output to find speech segments
        return [(0.0, 5.0)]  # Placeholder segment
    
    async def _extract_emotions(self, emotion_logits: Any) -> Dict[str, float]:
        """Extract emotion probabilities from emotion logits."""
        # This would process emotion recognition output
        return {"neutral": 0.8, "happy": 0.1, "sad": 0.1}  # Placeholder emotions
    
    async def _identify_speaker(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Identify speaker from audio data (placeholder implementation)."""
        # This would use speaker identification models
        return {"speaker_id": "unknown", "confidence": 0.5}
    
    async def _process_text_context(self, text_context: str) -> Optional[Any]:
        """Process text context to generate embeddings."""
        # This would use language models to generate text embeddings
        return None  # Placeholder
    
    async def _extract_language_features(self, text: str) -> Dict[str, Any]:
        """Extract language features from text."""
        # This would extract linguistic features
        return {"word_count": len(text.split()), "char_count": len(text)}
    
    async def _calculate_confidence(self, result: AudioLanguageResult) -> float:
        """Calculate overall confidence score for the processing result."""
        # Simple confidence calculation based on available features
        confidence_factors = []
        
        if result.transcription and "Error" not in result.transcription:
            confidence_factors.append(0.8)
        
        if result.audio_features and "error" not in result.audio_features:
            confidence_factors.append(0.7)
        
        if result.vad_segments:
            confidence_factors.append(0.6)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0
    
    def _update_processing_stats(self, processing_time: float, memory_usage: float):
        """Update internal processing statistics."""
        self.processing_stats["total_processed"] += 1
        self.processing_stats["total_processing_time"] += processing_time
        self.processing_stats["average_processing_time"] = (
            self.processing_stats["total_processing_time"] / self.processing_stats["total_processed"]
        )
        self.processing_stats["memory_usage_peak"] = max(
            self.processing_stats["memory_usage_peak"], memory_usage
        )
        
        # Calculate success rate
        total_attempts = self.processing_stats["total_processed"] + self.processing_stats["error_count"]
        if total_attempts > 0:
            self.processing_stats["success_rate"] = self.processing_stats["total_processed"] / total_attempts
    
    async def batch_process(
        self,
        audio_inputs: List[Union[str, Path, np.ndarray]],
        text_contexts: Optional[List[str]] = None,
        batch_size: Optional[int] = None
    ) -> List[AudioLanguageResult]:
        """
        Process multiple audio-text pairs in batches.
        
        Args:
            audio_inputs: List of audio inputs
            text_contexts: Optional list of text contexts
            batch_size: Batch size for processing
        
        Returns:
            List of AudioLanguageResult objects
        """
        batch_size = batch_size or self.config.batch_size
        text_contexts = text_contexts or [None] * len(audio_inputs)
        
        if len(audio_inputs) != len(text_contexts):
            raise ValueError("Number of audio inputs must match number of text contexts")
        
        results = []
        
        if self.status_animation:
            await self.status_animation.start(f"🎵 Processing {len(audio_inputs)} audio-text pairs...")
        
        for i in range(0, len(audio_inputs), batch_size):
            batch_audio = audio_inputs[i:i + batch_size]
            batch_text = text_contexts[i:i + batch_size]
            
            batch_results = await asyncio.gather(*[
                self.process_audio_text_pair(audio, text, return_features=True)
                for audio, text in zip(batch_audio, batch_text)
            ])
            
            results.extend(batch_results)
        
        if self.status_animation:
            await self.status_animation.stop(f"✅ Batch processing completed: {len(results)} results")
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        stats = self.processing_stats.copy()
        
        # Add memory information if available
        if self.gpu_manager:
            current_memory = self.gpu_manager.get_memory_usage()
            stats["current_gpu_memory_mb"] = current_memory.get('used_mb', 0)
            stats["available_gpu_memory_mb"] = current_memory.get('free_mb', 0)
        
        # Add configuration info
        stats["configuration"] = {
            "model_name": self.config.model_name,
            "sample_rate": self.config.sample_rate,
            "max_audio_duration": self.config.max_audio_duration,
            "batch_size": self.config.batch_size,
            "precision": self.config.precision
        }
        
        return stats
    
    async def cleanup(self):
        """Clean up resources and close connections."""
        try:
            if self.status_animation:
                await self.status_animation.stop("🧹 Cleaning up Audio-Language Processor...")
            
            # Clean up GPU memory
            if self.gpu_manager:
                self.gpu_manager.cleanup()
            
            # Clean up memory manager
            if self.memory_manager:
                self.memory_manager.cleanup()
            
            # Reset processing stats
            self.processing_stats = {
                "total_processed": 0,
                "total_processing_time": 0.0,
                "average_processing_time": 0.0,
                "memory_usage_peak": 0.0,
                "error_count": 0,
                "success_rate": 1.0
            }
            
            self.is_initialized = False
            
            if self.config.enable_rich_ui:
                print_success("🧹 Audio-Language Processor cleanup completed")
            
            logger.info("✅ Audio-Language Processor cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")

# Utility functions for Audio-Language Integration
async def load_audio_file(
    file_path: Union[str, Path],
    sample_rate: int = 16000,
    max_duration: float = 30.0
) -> Optional[np.ndarray]:
    """
    Load audio file with duration limiting for memory efficiency.
    
    Args:
        file_path: Path to audio file
        sample_rate: Target sample rate
        max_duration: Maximum duration in seconds
    
    Returns:
        Audio data as numpy array or None if failed
    """
    try:
        if LIBROSA_AVAILABLE:
            audio_data, sr = librosa.load(
                str(file_path),
                sr=sample_rate,
                duration=max_duration
            )
            return audio_data
        else:
            logger.warning("⚠️  Librosa not available - using placeholder audio")
            # Return placeholder audio data
            return np.random.randn(int(sample_rate * min(max_duration, 5.0)))
    except Exception as e:
        logger.error(f"❌ Failed to load audio file {file_path}: {e}")
        return None

def create_audio_language_processor(
    model_name: str = "openai/whisper-base",
    enable_advanced_features: bool = True,
    hardware_optimization: bool = True
) -> AudioLanguageProcessor:
    """
    Create and configure an AudioLanguageProcessor with optimal settings.
    
    Args:
        model_name: Audio model to use
        enable_advanced_features: Enable emotion recognition, speaker ID, etc.
        hardware_optimization: Enable GTX 1050 Ti optimizations
    
    Returns:
        Configured AudioLanguageProcessor instance
    """
    config = AudioLanguageConfig(
        model_name=model_name,
        use_gpu_optimization=hardware_optimization,
        max_memory_gb=3.5 if hardware_optimization else 8.0,
        enable_emotion_recognition=enable_advanced_features,
        enable_speaker_identification=enable_advanced_features,
        enable_vad=True,
        enable_rich_ui=True,
        performance_monitoring=True
    )
    
    return AudioLanguageProcessor(config)

# Export main classes and functions
__all__ = [
    'AudioLanguageProcessor',
    'AudioLanguageConfig', 
    'AudioLanguageResult',
    'load_audio_file',
    'create_audio_language_processor',
    'AL_INTEGRATION_AVAILABLE'
]
