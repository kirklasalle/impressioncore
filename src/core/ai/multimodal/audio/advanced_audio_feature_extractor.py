#!/usr/bin/env python3
"""
ImpressionCore: Advanced Audio Feature Extractor

Module for advanced audio feature extraction in the ImpressionCore framework.

File: multimodal/audio/advanced_audio_feature_extractor.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-29
Modified: 2025-05-29
Version: 1.0.0

Authors:
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [priority-2, multimodal, audio, feature-extraction, 2025]
Dependencies: [torch, torchaudio, librosa, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements advanced audio feature extraction capabilities for enhanced
multimodal integration. Provides sophisticated audio processing including spectrograms,
MFCCs, mel-scale features, and other audio representations optimized for memory-
constrained environments.

Features:
- Multi-scale spectrogram extraction
- Enhanced MFCC computation
- Mel-scale feature extraction
- Audio embedding generation
- Real-time processing capabilities
- Memory-efficient implementation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
import warnings

# Audio processing imports
try:
    import torchaudio
    import torchaudio.transforms as T
    HAS_TORCHAUDIO = True
except ImportError:
    HAS_TORCHAUDIO = False
    warnings.warn("torchaudio not available, using fallback implementations")

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    warnings.warn("librosa not available, using basic implementations")

# Import rich enhancements if available
try:
    from src.core.utils.rich_enhancements import create_panel, create_progress_bar
    from src.core.utils.rich_logging import get_rich_logger
    HAS_RICH = True
    logger = get_rich_logger(__name__)
except ImportError:
    HAS_RICH = False
    logger = logging.getLogger(__name__)

@dataclass
class AudioFeatureConfig:
    """Configuration for advanced audio feature extraction."""
    
    # Basic audio parameters
    sample_rate: int = 16000
    n_fft: int = 2048
    hop_length: int = 512
    win_length: Optional[int] = None
    window: str = "hann"
    
    # Mel-scale parameters
    n_mels: int = 80
    fmin: float = 0.0
    fmax: Optional[float] = None
    
    # MFCC parameters
    n_mfcc: int = 13
    dct_type: int = 2
    norm: str = "ortho"
    
    # Spectrogram parameters
    power: float = 2.0
    normalized: bool = False
    
    # Advanced features
    enable_delta: bool = True
    enable_delta_delta: bool = True
    enable_energy: bool = True
    enable_pitch: bool = True
    
    # Memory optimization
    max_duration: float = 30.0  # Maximum audio duration in seconds
    chunk_size: int = 1024  # Processing chunk size
    enable_caching: bool = True
    device: str = "auto"  # auto, cuda, cpu

class AdvancedAudioFeatureExtractor(nn.Module):
    """
    Advanced audio feature extractor with multiple feature types and optimizations.
    
    This module provides comprehensive audio feature extraction capabilities
    optimized for GTX 1050 Ti and memory-constrained environments.
    """
    
    def __init__(self, config: AudioFeatureConfig):
        """
        Initialize the advanced audio feature extractor.
        
        Args:
            config: Configuration for audio feature extraction
        """
        super().__init__()
        self.config = config
        
        # Set device
        if config.device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(config.device)
            
        # Initialize feature extractors
        self._initialize_transforms()
        
        # Feature cache for efficiency
        self.feature_cache = {} if config.enable_caching else None
        
        # Memory optimization settings
        self.max_samples = int(config.max_duration * config.sample_rate)
        
        if HAS_RICH:
            logger.info(f"Advanced Audio Feature Extractor initialized with device: {self.device}")
        else:
            logger.info(f"Advanced Audio Feature Extractor initialized with device: {self.device}")
    
    def _initialize_transforms(self):
        """Initialize audio transformation components."""
        config = self.config
        
        if HAS_TORCHAUDIO:
            # Mel-scale spectrogram
            self.mel_spectrogram = T.MelSpectrogram(
                sample_rate=config.sample_rate,
                n_fft=config.n_fft,
                hop_length=config.hop_length,
                win_length=config.win_length,
                window_fn=torch.hann_window,
                n_mels=config.n_mels,
                f_min=config.fmin,
                f_max=config.fmax or config.sample_rate // 2,
                power=config.power,
                normalized=config.normalized
            ).to(self.device)
            
            # MFCC transform
            self.mfcc_transform = T.MFCC(
                sample_rate=config.sample_rate,
                n_mfcc=config.n_mfcc,
                dct_type=config.dct_type,
                norm=config.norm,
                melkwargs={
                    "n_fft": config.n_fft,
                    "hop_length": config.hop_length,
                    "n_mels": config.n_mels,
                    "f_min": config.fmin,
                    "f_max": config.fmax or config.sample_rate // 2,
                }
            ).to(self.device)
            
            # Spectrogram transform
            self.spectrogram = T.Spectrogram(
                n_fft=config.n_fft,
                hop_length=config.hop_length,
                win_length=config.win_length,
                window_fn=torch.hann_window,
                power=config.power,
                normalized=config.normalized
            ).to(self.device)
            
        else:
            # Fallback implementations without torchaudio
            logger.warning("TorchAudio not available, using fallback implementations")
            self.mel_spectrogram = None
            self.mfcc_transform = None
            self.spectrogram = None
    
    def extract_features(
        self, 
        waveform: torch.Tensor,
        feature_types: Optional[List[str]] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Extract multiple types of audio features from waveform.
        
        Args:
            waveform: Input audio waveform [channels, time] or [batch, channels, time]
            feature_types: List of feature types to extract. If None, extracts all.
                          Options: ['mel', 'mfcc', 'spectrogram', 'chroma', 'tonnetz']
        
        Returns:
            Dictionary containing extracted features
        """
        if feature_types is None:
            feature_types = ['mel', 'mfcc', 'spectrogram']
        
        # Ensure proper tensor format
        if waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)  # Add channel dimension
        if waveform.dim() == 2 and waveform.shape[0] > 2:
            # Assume [time, channels] and transpose
            waveform = waveform.transpose(0, 1)
        
        # Move to device and limit duration for memory efficiency
        waveform = waveform.to(self.device)
        if waveform.shape[-1] > self.max_samples:
            waveform = waveform[..., :self.max_samples]
        
        features = {}
        
        # Extract mel-scale spectrogram
        if 'mel' in feature_types and self.mel_spectrogram is not None:
            try:
                mel_spec = self.mel_spectrogram(waveform)
                # Convert to log scale
                mel_spec = torch.log(mel_spec + 1e-7)
                features['mel_spectrogram'] = mel_spec
            except Exception as e:
                logger.warning(f"Error extracting mel spectrogram: {e}")
        
        # Extract MFCC features
        if 'mfcc' in feature_types and self.mfcc_transform is not None:
            try:
                mfcc = self.mfcc_transform(waveform)
                features['mfcc'] = mfcc
                
                # Add delta and delta-delta features if enabled
                if self.config.enable_delta:
                    delta = self._compute_delta(mfcc)
                    features['mfcc_delta'] = delta
                    
                    if self.config.enable_delta_delta:
                        delta_delta = self._compute_delta(delta)
                        features['mfcc_delta_delta'] = delta_delta
                        
            except Exception as e:
                logger.warning(f"Error extracting MFCC: {e}")
        
        # Extract standard spectrogram
        if 'spectrogram' in feature_types and self.spectrogram is not None:
            try:
                spec = self.spectrogram(waveform)
                # Convert to log scale
                spec = torch.log(spec + 1e-7)
                features['spectrogram'] = spec
            except Exception as e:
                logger.warning(f"Error extracting spectrogram: {e}")
        
        # Extract advanced features if librosa is available
        if HAS_LIBROSA:
            waveform_np = waveform.cpu().numpy()
            if waveform_np.ndim > 1:
                waveform_np = waveform_np[0]  # Take first channel
            
            # Chroma features
            if 'chroma' in feature_types:
                try:
                    chroma = librosa.feature.chroma_stft(
                        y=waveform_np,
                        sr=self.config.sample_rate,
                        hop_length=self.config.hop_length
                    )
                    features['chroma'] = torch.from_numpy(chroma).to(self.device)
                except Exception as e:
                    logger.warning(f"Error extracting chroma: {e}")
            
            # Tonnetz features
            if 'tonnetz' in feature_types:
                try:
                    tonnetz = librosa.feature.tonnetz(
                        y=waveform_np,
                        sr=self.config.sample_rate
                    )
                    features['tonnetz'] = torch.from_numpy(tonnetz).to(self.device)
                except Exception as e:
                    logger.warning(f"Error extracting tonnetz: {e}")
        
        return features
    
    def _compute_delta(self, features: torch.Tensor, width: int = 9) -> torch.Tensor:
        """
        Compute delta (derivative) features.
        
        Args:
            features: Input features [batch, n_features, time]
            width: Width of the delta computation window
            
        Returns:
            Delta features with same shape as input
        """
        # Pad the features to handle boundaries
        pad_width = width // 2
        padded = F.pad(features, (pad_width, pad_width), mode='replicate')
        
        # Compute delta using convolution
        delta_filter = torch.arange(-pad_width, pad_width + 1, dtype=torch.float32, device=features.device)
        delta_filter = delta_filter / (2 * sum(i**2 for i in range(1, pad_width + 1)))
        delta_filter = delta_filter.view(1, 1, -1)
        
        # Apply convolution to compute deltas
        delta = F.conv1d(
            padded.view(-1, 1, padded.shape[-1]), 
            delta_filter, 
            padding=0
        )
        
        return delta.view(features.shape)
    
    def extract_embeddings(
        self, 
        waveform: torch.Tensor,
        embedding_dim: int = 512
    ) -> torch.Tensor:
        """
        Extract high-level audio embeddings suitable for multimodal fusion.
        
        Args:
            waveform: Input audio waveform
            embedding_dim: Desired embedding dimension
            
        Returns:
            Audio embeddings [batch, embedding_dim]
        """
        # Extract comprehensive features
        features = self.extract_features(waveform, ['mel', 'mfcc'])
        
        # Combine features for embedding generation
        feature_list = []
        
        if 'mel_spectrogram' in features:
            mel = features['mel_spectrogram']
            # Global average pooling across time dimension
            mel_pooled = torch.mean(mel, dim=-1)  # [batch, n_mels]
            feature_list.append(mel_pooled)
        
        if 'mfcc' in features:
            mfcc = features['mfcc']
            # Global average pooling across time dimension
            mfcc_pooled = torch.mean(mfcc, dim=-1)  # [batch, n_mfcc]
            feature_list.append(mfcc_pooled)
        
        # Concatenate all features
        if feature_list:
            combined = torch.cat(feature_list, dim=-1)
            
            # Project to desired embedding dimension
            if not hasattr(self, 'embedding_projection') or self.embedding_projection.out_features != embedding_dim:
                input_dim = combined.shape[-1]
                self.embedding_projection = nn.Linear(input_dim, embedding_dim).to(self.device)
            
            embeddings = self.embedding_projection(combined)
            embeddings = F.normalize(embeddings, p=2, dim=-1)  # L2 normalize
            
            return embeddings
        else:
            # Fallback: return zero embeddings
            batch_size = waveform.shape[0] if waveform.dim() > 1 else 1
            return torch.zeros(batch_size, embedding_dim, device=self.device)
    
    def process_streaming(
        self, 
        waveform_chunk: torch.Tensor,
        feature_types: Optional[List[str]] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Process audio in streaming fashion for real-time applications.
        
        Args:
            waveform_chunk: Audio chunk for processing
            feature_types: Types of features to extract
            
        Returns:
            Extracted features for the chunk
        """
        # Ensure chunk is properly sized for processing
        chunk_samples = self.config.chunk_size
        
        if waveform_chunk.shape[-1] < chunk_samples:
            # Pad short chunks
            pad_size = chunk_samples - waveform_chunk.shape[-1]
            waveform_chunk = F.pad(waveform_chunk, (0, pad_size))
        elif waveform_chunk.shape[-1] > chunk_samples:
            # Truncate long chunks
            waveform_chunk = waveform_chunk[..., :chunk_samples]
        
        # Extract features from chunk
        return self.extract_features(waveform_chunk, feature_types)
    
    def get_feature_shapes(self) -> Dict[str, Tuple[int, ...]]:
        """
        Get the expected shapes for different feature types.
        
        Returns:
            Dictionary mapping feature names to their expected shapes
        """
        # Calculate expected dimensions based on config
        time_steps = (self.max_samples // self.config.hop_length) + 1
        
        shapes = {
            'mel_spectrogram': (self.config.n_mels, time_steps),
            'mfcc': (self.config.n_mfcc, time_steps),
            'spectrogram': (self.config.n_fft // 2 + 1, time_steps),
        }
        
        if HAS_LIBROSA:
            shapes.update({
                'chroma': (12, time_steps),
                'tonnetz': (6, time_steps),
            })
        
        return shapes
    
    def clear_cache(self):
        """Clear the feature cache to free memory."""
        if self.feature_cache is not None:
            self.feature_cache.clear()
            
    def forward(self, waveform: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass for compatibility with nn.Module."""
        return self.extract_features(waveform)

# Factory function for easy instantiation
def create_advanced_audio_extractor(
    sample_rate: int = 16000,
    device: str = "auto",
    **kwargs
) -> AdvancedAudioFeatureExtractor:
    """
    Create an advanced audio feature extractor with optimized settings.
    
    Args:
        sample_rate: Audio sample rate
        device: Target device (auto, cuda, cpu)
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured AdvancedAudioFeatureExtractor instance
    """
    config = AudioFeatureConfig(
        sample_rate=sample_rate,
        device=device,
        **kwargs
    )
    
    return AdvancedAudioFeatureExtractor(config)

# Example usage and testing
if __name__ == "__main__":
    # Test the advanced audio feature extractor
    config = AudioFeatureConfig(sample_rate=16000, device="auto")
    extractor = AdvancedAudioFeatureExtractor(config)
    
    # Create dummy audio data
    duration = 3.0  # seconds
    sample_rate = 16000
    samples = int(duration * sample_rate)
    
    # Generate test waveform (sine wave)
    t = torch.linspace(0, duration, samples)
    frequency = 440  # A4 note
    waveform = torch.sin(2 * torch.pi * frequency * t).unsqueeze(0)
    
    print(f"Testing advanced audio feature extraction...")
    print(f"Input waveform shape: {waveform.shape}")
    
    # Extract features
    features = extractor.extract_features(waveform)
    print("\nExtracted features:")
    for name, feature in features.items():
        print(f"  {name}: {feature.shape}")
    
    # Extract embeddings
    embeddings = extractor.extract_embeddings(waveform, embedding_dim=512)
    print(f"\nAudio embeddings shape: {embeddings.shape}")
    
    # Test streaming processing
    chunk_size = 1024
    chunk = waveform[..., :chunk_size]
    streaming_features = extractor.process_streaming(chunk)
    print(f"\nStreaming features:")
    for name, feature in streaming_features.items():
        print(f"  {name}: {feature.shape}")
    
    print("\nAdvanced audio feature extraction test completed successfully!")
