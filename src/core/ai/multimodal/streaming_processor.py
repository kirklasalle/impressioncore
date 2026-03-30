#!/usr/bin/env python3
"""
ImpressionCore: Streaming Multimodal Processor

Real-time streaming processor for multimodal data fusion with memory optimization.

File: src/core/ai/multimodal/streaming_processor.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-06
Modified: 2025-06-06
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [streaming, multimodal, memory-critical, production, 2025]
Dependencies: [torch, typing, collections]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Any
from collections import deque
import time
import logging


class StreamingBuffer:
    """
    Memory-efficient streaming buffer for multimodal data.
    
    Maintains sliding windows of data with automatic cleanup to prevent
    memory overflow on resource-constrained hardware.
    """
    
    def __init__(self, max_size: int = 1000, cleanup_threshold: float = 0.8):
        """
        Initialize streaming buffer.
        
        Args:
            max_size: Maximum number of items in buffer
            cleanup_threshold: Cleanup when buffer reaches this percentage of max_size
        """
        self.max_size = max_size
        self.cleanup_threshold = cleanup_threshold
        self.buffer = deque(maxlen=max_size)
        self.timestamps = deque(maxlen=max_size)
        
    def add(self, data: Any, timestamp: float = None) -> None:
        """
        Add data to the streaming buffer.
        
        Args:
            data: Data to add to buffer
            timestamp: Optional timestamp (uses current time if None)
        """
        if timestamp is None:
            timestamp = time.time()
            
        self.buffer.append(data)
        self.timestamps.append(timestamp)
        
        # Cleanup if needed
        if len(self.buffer) > self.max_size * self.cleanup_threshold:
            self._cleanup_old_data()
    
    def get_recent(self, count: int = None) -> List[Tuple[Any, float]]:
        """
        Get recent data from buffer.
        
        Args:
            count: Number of recent items to return (all if None)
            
        Returns:
            List of (data, timestamp) tuples
        """
        if count is None:
            return list(zip(self.buffer, self.timestamps))
        else:
            return list(zip(list(self.buffer)[-count:], list(self.timestamps)[-count:]))
    
    def get_time_window(self, window_seconds: float) -> List[Tuple[Any, float]]:
        """
        Get data within a time window.
        
        Args:
            window_seconds: Time window in seconds from current time
            
        Returns:
            List of (data, timestamp) tuples within the time window
        """
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        result = []
        for data, timestamp in zip(self.buffer, self.timestamps):
            if timestamp >= cutoff_time:
                result.append((data, timestamp))
        
        return result
    
    def _cleanup_old_data(self) -> None:
        """Remove old data to free memory."""
        # Remove oldest 20% of data
        remove_count = int(len(self.buffer) * 0.2)
        for _ in range(remove_count):
            if self.buffer:
                self.buffer.popleft()
                self.timestamps.popleft()


class StreamingMultimodalProcessor:
    """
    Real-time streaming processor for multimodal data fusion.
    
    Designed for memory-efficient processing on GTX 1050 Ti constraints.
    Handles continuous streams of text, audio, and video data.
    """
    
    def __init__(
        self,
        text_dim: int = 512,
        audio_dim: int = 512,
        vision_dim: int = 512,
        fusion_dim: int = 512,
        buffer_size: int = 1000,
        fusion_window: float = 2.0  # seconds
    ):
        """
        Initialize streaming multimodal processor.
        
        Args:
            text_dim: Text feature dimension
            audio_dim: Audio feature dimension
            vision_dim: Vision feature dimension
            fusion_dim: Fusion layer dimension
            buffer_size: Maximum buffer size for each modality
            fusion_window: Time window for multimodal fusion in seconds
        """
        self.text_dim = text_dim
        self.audio_dim = audio_dim
        self.vision_dim = vision_dim
        self.fusion_dim = fusion_dim
        self.fusion_window = fusion_window
        
        # Initialize buffers for each modality
        self.text_buffer = StreamingBuffer(max_size=buffer_size)
        self.audio_buffer = StreamingBuffer(max_size=buffer_size)
        self.vision_buffer = StreamingBuffer(max_size=buffer_size)
        
        # Feature alignment layers (memory-efficient)
        self.text_projector = nn.Linear(text_dim, fusion_dim)
        self.audio_projector = nn.Linear(audio_dim, fusion_dim)
        self.vision_projector = nn.Linear(vision_dim, fusion_dim)
        
        # Lightweight fusion layer
        self.fusion_layer = nn.Sequential(
            nn.Linear(fusion_dim * 3, fusion_dim),
            nn.ReLU(),
            nn.Linear(fusion_dim, fusion_dim)
        )
        
        # Temporal attention for alignment
        self.temporal_attention = nn.MultiheadAttention(
            embed_dim=fusion_dim,
            num_heads=4,  # Reduced for memory efficiency
            batch_first=True
        )
        
        self.logger = logging.getLogger(__name__)
    
    def add_text_features(self, features: torch.Tensor, timestamp: float = None) -> None:
        """
        Add text features to the streaming buffer.
        
        Args:
            features: Text features tensor
            timestamp: Optional timestamp
        """
        self.text_buffer.add(features.detach().cpu(), timestamp)
        self.logger.debug(f"Added text features: {features.shape}")
    
    def add_audio_features(self, features: torch.Tensor, timestamp: float = None) -> None:
        """
        Add audio features to the streaming buffer.
        
        Args:
            features: Audio features tensor
            timestamp: Optional timestamp
        """
        self.audio_buffer.add(features.detach().cpu(), timestamp)
        self.logger.debug(f"Added audio features: {features.shape}")
    
    def add_vision_features(self, features: torch.Tensor, timestamp: float = None) -> None:
        """
        Add vision features to the streaming buffer.
        
        Args:
            features: Vision features tensor
            timestamp: Optional timestamp
        """
        self.vision_buffer.add(features.detach().cpu(), timestamp)
        self.logger.debug(f"Added vision features: {features.shape}")
    
    def get_current_fusion(self, device: torch.device = None) -> Optional[torch.Tensor]:
        """
        Get current multimodal fusion based on recent data.
        
        Args:
            device: Device to move tensors to
            
        Returns:
            Fused multimodal representation or None if insufficient data
        """
        if device is None:
            device = torch.device("cpu")
        
        # Get recent data from each modality
        text_data = self.text_buffer.get_time_window(self.fusion_window)
        audio_data = self.audio_buffer.get_time_window(self.fusion_window)
        vision_data = self.vision_buffer.get_time_window(self.fusion_window)
        
        # Check if we have data from all modalities
        if not (text_data and audio_data and vision_data):
            self.logger.debug("Insufficient data for fusion")
            return None
        
        try:
            # Get most recent features from each modality
            latest_text = text_data[-1][0].to(device)
            latest_audio = audio_data[-1][0].to(device)
            latest_vision = vision_data[-1][0].to(device)
            
            # Project to common dimension
            text_proj = self.text_projector(latest_text)
            audio_proj = self.audio_projector(latest_audio)
            vision_proj = self.vision_projector(latest_vision)
            
            # Concatenate and fuse
            combined = torch.cat([text_proj, audio_proj, vision_proj], dim=-1)
            fused = self.fusion_layer(combined)
            
            return fused
            
        except Exception as e:
            self.logger.error(f"Error during fusion: {e}")
            return None
    
    def get_temporal_fusion(
        self, 
        window_seconds: float = None, 
        device: torch.device = None
    ) -> Optional[torch.Tensor]:
        """
        Get temporally-aligned multimodal fusion.
        
        Args:
            window_seconds: Time window for fusion (uses default if None)
            device: Device to move tensors to
            
        Returns:
            Temporally-aligned fused representation or None
        """
        if window_seconds is None:
            window_seconds = self.fusion_window
            
        if device is None:
            device = torch.device("cpu")
        
        # Get data from all modalities
        text_data = self.text_buffer.get_time_window(window_seconds)
        audio_data = self.audio_buffer.get_time_window(window_seconds)
        vision_data = self.vision_buffer.get_time_window(window_seconds)
        
        if not (text_data and audio_data and vision_data):
            return None
        
        try:
            # Align features temporally (simplified alignment)
            aligned_features = self._align_temporal_features(
                text_data, audio_data, vision_data, device
            )
            
            if aligned_features is None:
                return None
            
            text_aligned, audio_aligned, vision_aligned = aligned_features
            
            # Apply temporal attention
            all_features = torch.stack([text_aligned, audio_aligned, vision_aligned])
            attended_features, _ = self.temporal_attention(
                all_features, all_features, all_features
            )
            
            # Fuse attended features
            combined = attended_features.flatten()
            fused = self.fusion_layer(combined.unsqueeze(0))
            
            return fused.squeeze(0)
            
        except Exception as e:
            self.logger.error(f"Error during temporal fusion: {e}")
            return None
    
    def _align_temporal_features(
        self, 
        text_data: List[Tuple[torch.Tensor, float]],
        audio_data: List[Tuple[torch.Tensor, float]],
        vision_data: List[Tuple[torch.Tensor, float]],
        device: torch.device
    ) -> Optional[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """
        Align features from different modalities temporally.
        
        Simple alignment strategy: use most recent features from each modality.
        
        Args:
            text_data: List of (features, timestamp) for text
            audio_data: List of (features, timestamp) for audio
            vision_data: List of (features, timestamp) for vision
            device: Device to move tensors to
            
        Returns:
            Tuple of aligned features or None if alignment fails
        """
        try:
            # Simple alignment: use most recent from each modality
            latest_text = text_data[-1][0].to(device)
            latest_audio = audio_data[-1][0].to(device)
            latest_vision = vision_data[-1][0].to(device)
            
            # Project to common dimension
            text_proj = self.text_projector(latest_text)
            audio_proj = self.audio_projector(latest_audio)
            vision_proj = self.vision_projector(latest_vision)
            
            return text_proj, audio_proj, vision_proj
            
        except Exception as e:
            self.logger.error(f"Error during temporal alignment: {e}")
            return None
    
    def clear_buffers(self) -> None:
        """Clear all modality buffers to free memory."""
        self.text_buffer = StreamingBuffer(max_size=self.text_buffer.max_size)
        self.audio_buffer = StreamingBuffer(max_size=self.audio_buffer.max_size)
        self.vision_buffer = StreamingBuffer(max_size=self.vision_buffer.max_size)
        self.logger.info("Cleared all streaming buffers")
    
    def get_buffer_status(self) -> Dict[str, int]:
        """
        Get current buffer status.
        
        Returns:
            Dictionary with buffer sizes for each modality
        """
        return {
            "text_buffer_size": len(self.text_buffer.buffer),
            "audio_buffer_size": len(self.audio_buffer.buffer),
            "vision_buffer_size": len(self.vision_buffer.buffer),
            "total_buffer_size": (
                len(self.text_buffer.buffer) + 
                len(self.audio_buffer.buffer) + 
                len(self.vision_buffer.buffer)
            )
        }


def create_streaming_processor_small() -> StreamingMultimodalProcessor:
    """
    Create a small streaming processor optimized for GTX 1050 Ti.
    
    Returns:
        Configured StreamingMultimodalProcessor
    """
    return StreamingMultimodalProcessor(
        text_dim=256,
        audio_dim=256,
        vision_dim=256,
        fusion_dim=256,
        buffer_size=500,  # Smaller buffer for memory efficiency
        fusion_window=1.0  # Shorter window for responsiveness
    )


def create_streaming_processor_medium() -> StreamingMultimodalProcessor:
    """
    Create a medium streaming processor with balanced performance/memory.
    
    Returns:
        Configured StreamingMultimodalProcessor
    """
    return StreamingMultimodalProcessor(
        text_dim=512,
        audio_dim=512,
        vision_dim=512,
        fusion_dim=512,
        buffer_size=1000,
        fusion_window=2.0
    )


if __name__ == "__main__":
    # Test streaming processor
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    processor = create_streaming_processor_small()
    
    # Simulate streaming data
    for i in range(10):
        # Simulate multimodal features
        text_feat = torch.randn(256)
        audio_feat = torch.randn(256)
        vision_feat = torch.randn(256)
        
        # Add to processor
        processor.add_text_features(text_feat)
        processor.add_audio_features(audio_feat)
        processor.add_vision_features(vision_feat)
        
        # Get fusion
        fusion = processor.get_current_fusion(device)
        if fusion is not None:
            print(f"Step {i}: Fusion shape: {fusion.shape}")
        
        # Print buffer status
        status = processor.get_buffer_status()
        print(f"Step {i}: Buffer status: {status}")
        
        time.sleep(0.1)  # Simulate real-time delay
    
    print("Streaming processor test completed!")
