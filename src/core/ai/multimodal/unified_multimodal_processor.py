"""
Unified Multimodal Processor for ImpressionCore.

This module combines Vision-Language and Audio-Language processing into a 
unified architecture for comprehensive multimodal AI processing.

Optimized for GTX 1050 Ti (4GB VRAM) with efficient memory management.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
import warnings

# Core utilities
ADVANCED_UTILS_AVAILABLE = False
try:
    from core.utils.gpu_memory_manager import GPUMemoryManager
    from core.utils.rich_status_animation import StatusAnimation
    from src.dev_tools.performance_optimizer import PerformanceOptimizer
    from src.dev_tools.memory_manager import MemoryManager
    ADVANCED_UTILS_AVAILABLE = True
except ImportError:
    logging.warning("⚠️  Advanced utilities not available - using fallbacks")

# PyTorch and ML dependencies
TORCH_AVAILABLE = False
try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    logging.warning("⚠️  PyTorch not available - using fallbacks")

# Import our modality-specific processors
try:
    from .vision_language_integration import (
        VisionLanguageProcessor, VisionLanguageConfig, VisionLanguageResult
    )
    VISION_LANGUAGE_AVAILABLE = True
except ImportError:
    VISION_LANGUAGE_AVAILABLE = False
    logging.warning("⚠️  Vision-Language integration not available")

try:
    from .audio_language_integration import (
        AudioLanguageProcessor, AudioLanguageConfig, AudioLanguageResult
    )
    AUDIO_LANGUAGE_AVAILABLE = True
except ImportError:
    AUDIO_LANGUAGE_AVAILABLE = False
    logging.warning("⚠️  Audio-Language integration not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UnifiedMultimodalConfig:
    """Configuration for unified multimodal processing."""
    
    # Memory and performance settings
    max_memory_gb: float = 3.5  # GTX 1050 Ti safe limit
    use_gpu_optimization: bool = True
    precision: str = "fp16"  # Memory efficiency
    batch_size: int = 1  # Conservative for limited VRAM
    
    # Modality enablement
    enable_vision_language: bool = True
    enable_audio_language: bool = True
    enable_cross_modal_fusion: bool = True
    
    # Processing settings
    max_sequence_length: int = 512
    max_image_size: Tuple[int, int] = (224, 224)
    max_audio_duration: float = 30.0
    
    # Advanced features
    enable_rich_ui: bool = True
    performance_monitoring: bool = True
    memory_optimization: bool = True
    
    # Cross-modal fusion settings
    fusion_strategy: str = "attention"  # "attention", "concatenate", "weighted"
    attention_heads: int = 8
    fusion_hidden_dim: int = 512    # Individual modality configs
    vision_config: Optional['VisionLanguageConfig'] = None
    audio_config: Optional['AudioLanguageConfig'] = None
    
    def __post_init__(self):
        """Initialize sub-configs if not provided."""
        if self.vision_config is None and VISION_LANGUAGE_AVAILABLE:
            self.vision_config = VisionLanguageConfig(
                use_gpu_optimization=self.use_gpu_optimization,
                precision=self.precision
            )
        
        if self.audio_config is None and AUDIO_LANGUAGE_AVAILABLE:
            self.audio_config = AudioLanguageConfig(
                max_memory_gb=self.max_memory_gb,
                use_gpu_optimization=self.use_gpu_optimization,
                precision=self.precision
            )

@dataclass
class MultimodalInput:
    """Input structure for multimodal processing."""
    text: Optional[str] = None
    image_path: Optional[Union[str, Path]] = None
    audio_path: Optional[Union[str, Path]] = None
    image_data: Optional[Any] = None  # PIL Image or tensor
    audio_data: Optional[Any] = None  # Audio array or tensor
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UnifiedMultimodalResult:
    """Result structure for unified multimodal processing."""
    
    # Individual modality results
    vision_language_result: Optional[VisionLanguageResult] = None
    audio_language_result: Optional[AudioLanguageResult] = None
    
    # Unified features and outputs
    fused_features: Optional[Any] = None
    unified_embedding: Optional[Any] = None
    cross_modal_attention: Optional[Dict[str, Any]] = None
    
    # Performance metrics
    processing_time: float = 0.0
    memory_usage: Dict[str, float] = field(default_factory=dict)
    modalities_processed: List[str] = field(default_factory=list)
    
    # Metadata
    success: bool = True
    error_message: Optional[str] = None
    timestamp: Optional[str] = None

class UnifiedMultimodalProcessor:
    """
    Unified processor combining vision-language and audio-language capabilities.
    
    Optimized for GTX 1050 Ti with efficient memory management and cross-modal fusion.
    """
    
    def __init__(self, config: Optional[UnifiedMultimodalConfig] = None):
        """Initialize the unified multimodal processor."""
        self.config = config or UnifiedMultimodalConfig()
        self.initialized = False
        self.performance_stats = {}
        
        # Initialize advanced utilities if available
        self.gpu_manager = None
        self.status_animation = None
        self.performance_optimizer = None
        self.memory_manager = None
        
        if ADVANCED_UTILS_AVAILABLE and self.config.enable_rich_ui:
            try:
                self.gpu_manager = GPUMemoryManager()
                self.status_animation = StatusAnimation()
                self.performance_optimizer = PerformanceOptimizer()
                self.memory_manager = MemoryManager()
                logger.info("✅ Advanced utilities initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize advanced utilities: {e}")
        
        # Initialize modality processors
        self.vision_processor = None
        self.audio_processor = None
        
        if self.config.enable_vision_language and VISION_LANGUAGE_AVAILABLE:
            try:
                self.vision_processor = VisionLanguageProcessor(self.config.vision_config)
                logger.info("✅ Vision-Language processor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Vision-Language processor: {e}")
        
        if self.config.enable_audio_language and AUDIO_LANGUAGE_AVAILABLE:
            try:
                self.audio_processor = AudioLanguageProcessor(self.config.audio_config)
                logger.info("✅ Audio-Language processor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Audio-Language processor: {e}")
    
    async def initialize_models(self) -> bool:
        """Initialize all required models and components."""
        if self.initialized:
            return True
        
        try:
            if self.status_animation:
                await self.status_animation.start("Initializing unified multimodal models...")
            
            # Initialize individual processors
            initialization_tasks = []
            
            if self.vision_processor:
                initialization_tasks.append(self.vision_processor.initialize_models())
            
            if self.audio_processor:
                initialization_tasks.append(self.audio_processor.initialize_models())
            
            # Wait for all initializations
            if initialization_tasks:
                results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
                
                # Check for failures
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Model initialization failed: {result}")
                        return False
            
            self.initialized = True
            
            if self.status_animation:
                await self.status_animation.stop()
            
            logger.info("🎯 Unified multimodal models initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize unified models: {e}")
            if self.status_animation:
                await self.status_animation.stop()
            return False
    
    async def process_multimodal_input(
        self,
        multimodal_input: MultimodalInput
    ) -> UnifiedMultimodalResult:
        """
        Process multimodal input through all available modalities.
        
        Args:
            multimodal_input: Input containing text, image, and/or audio data
            
        Returns:
            Unified result with individual and fused features
        """
        start_time = time.time()
        result = UnifiedMultimodalResult()
        
        try:
            if not self.initialized:
                await self.initialize_models()
            
            if self.status_animation:
                await self.status_animation.start("Processing multimodal input...")
            
            # Track memory usage
            initial_memory = {}
            if self.gpu_manager and TORCH_AVAILABLE:
                initial_memory = self.gpu_manager.get_memory_stats()
            
            # Process individual modalities
            processing_tasks = []
            
            # Vision-Language processing
            if (self.vision_processor and 
                (multimodal_input.image_path or multimodal_input.image_data) and 
                multimodal_input.text):
                
                processing_tasks.append(
                    self._process_vision_language(multimodal_input)
                )
            
            # Audio-Language processing
            if (self.audio_processor and 
                (multimodal_input.audio_path or multimodal_input.audio_data) and 
                multimodal_input.text):
                
                processing_tasks.append(
                    self._process_audio_language(multimodal_input)
                )
            
            # Execute processing tasks
            if processing_tasks:
                individual_results = await asyncio.gather(*processing_tasks, return_exceptions=True)
                
                # Process results
                for i, individual_result in enumerate(individual_results):
                    if isinstance(individual_result, Exception):
                        logger.warning(f"Individual processing failed: {individual_result}")
                        continue
                    
                    modality_type, modality_result = individual_result
                    
                    if modality_type == "vision_language":
                        result.vision_language_result = modality_result
                        result.modalities_processed.append("vision_language")
                    elif modality_type == "audio_language":
                        result.audio_language_result = modality_result
                        result.modalities_processed.append("audio_language")
            
            # Cross-modal fusion if multiple modalities processed
            if (len(result.modalities_processed) > 1 and 
                self.config.enable_cross_modal_fusion):
                await self._perform_cross_modal_fusion(result)
            
            # Calculate performance metrics
            result.processing_time = time.time() - start_time
            
            if self.gpu_manager and TORCH_AVAILABLE:
                final_memory = self.gpu_manager.get_memory_stats()
                result.memory_usage = {
                    "initial_mb": initial_memory.get("allocated_mb", 0),
                    "final_mb": final_memory.get("allocated_mb", 0),
                    "peak_mb": final_memory.get("reserved_mb", 0)
                }
            
            result.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            if self.status_animation:
                await self.status_animation.stop()
            
            logger.info(f"✅ Multimodal processing completed in {result.processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.processing_time = time.time() - start_time
            
            logger.error(f"❌ Multimodal processing failed: {e}")
            
            if self.status_animation:
                await self.status_animation.stop()
            
            return result
    
    async def _process_vision_language(
        self, 
        multimodal_input: MultimodalInput
    ) -> Tuple[str, VisionLanguageResult]:
        """Process vision-language input."""
        try:
            if multimodal_input.image_path:
                result = await self.vision_processor.process_image_text_pair(
                    image_path=str(multimodal_input.image_path),
                    text=multimodal_input.text
                )
            else:
                result = await self.vision_processor.process_image_text_pair(
                    image_data=multimodal_input.image_data,
                    text=multimodal_input.text
                )
            
            return ("vision_language", result)
            
        except Exception as e:
            logger.error(f"Vision-Language processing failed: {e}")
            raise
    
    async def _process_audio_language(
        self, 
        multimodal_input: MultimodalInput
    ) -> Tuple[str, AudioLanguageResult]:
        """Process audio-language input."""
        try:
            if multimodal_input.audio_path:
                result = await self.audio_processor.process_audio_text_pair(
                    audio_path=str(multimodal_input.audio_path),
                    text=multimodal_input.text
                )
            else:
                result = await self.audio_processor.process_audio_text_pair(
                    audio_data=multimodal_input.audio_data,
                    text=multimodal_input.text
                )
            
            return ("audio_language", result)
            
        except Exception as e:
            logger.error(f"Audio-Language processing failed: {e}")
            raise
    
    async def _perform_cross_modal_fusion(self, result: UnifiedMultimodalResult) -> None:
        """Perform cross-modal fusion between different modalities."""
        try:
            fusion_features = []
            attention_weights = {}
            
            # Collect features from individual modalities
            if result.vision_language_result and hasattr(result.vision_language_result, 'features'):
                vision_features = result.vision_language_result.features
                if vision_features is not None:
                    fusion_features.append(("vision", vision_features))
            
            if result.audio_language_result and hasattr(result.audio_language_result, 'features'):
                audio_features = result.audio_language_result.features
                if audio_features is not None:
                    fusion_features.append(("audio", audio_features))
            
            if len(fusion_features) < 2:
                logger.warning("Insufficient features for cross-modal fusion")
                return
            
            # Simple concatenation fusion (fallback when PyTorch unavailable)
            if not TORCH_AVAILABLE or self.config.fusion_strategy == "concatenate":
                fused = self._concatenate_features(fusion_features)
                result.fused_features = fused
                return
            
            # Attention-based fusion (when PyTorch available)
            if self.config.fusion_strategy == "attention":
                fused, attention = self._attention_fusion(fusion_features)
                result.fused_features = fused
                result.cross_modal_attention = attention
            
        except Exception as e:
            logger.warning(f"Cross-modal fusion failed: {e}")
            # Don't fail the entire process, just skip fusion
    
    def _concatenate_features(self, features: List[Tuple[str, Any]]) -> Any:
        """Simple concatenation of features."""
        try:
            # Convert to lists if needed and concatenate
            feature_lists = []
            for modality, feat in features:
                if hasattr(feat, 'tolist'):
                    feature_lists.extend(feat.tolist())
                elif isinstance(feat, (list, tuple)):
                    feature_lists.extend(feat)
                else:
                    feature_lists.append(feat)
            
            return feature_lists
            
        except Exception as e:
            logger.warning(f"Feature concatenation failed: {e}")
            return None
    
    def _attention_fusion(self, features: List[Tuple[str, Any]]) -> Tuple[Any, Dict[str, Any]]:
        """Attention-based feature fusion (requires PyTorch)."""
        try:
            if not TORCH_AVAILABLE:
                return self._concatenate_features(features), {}
            
            # Convert features to tensors
            feature_tensors = []
            modality_names = []
            
            for modality, feat in features:
                if not isinstance(feat, torch.Tensor):
                    if hasattr(feat, 'tolist'):
                        feat = torch.tensor(feat.tolist())
                    else:
                        feat = torch.tensor([feat] if not isinstance(feat, (list, tuple)) else feat)
                
                feature_tensors.append(feat.flatten())
                modality_names.append(modality)
            
            # Stack features
            stacked_features = torch.stack(feature_tensors)  # [num_modalities, feature_dim]
            
            # Simple attention mechanism
            attention_weights = F.softmax(
                torch.sum(stacked_features * stacked_features, dim=-1), 
                dim=0
            )
            
            # Weighted fusion
            fused_features = torch.sum(
                stacked_features * attention_weights.unsqueeze(-1), 
                dim=0
            )
            
            attention_dict = {
                name: weight.item() 
                for name, weight in zip(modality_names, attention_weights)
            }
            
            return fused_features, attention_dict
            
        except Exception as e:
            logger.warning(f"Attention fusion failed: {e}")
            return self._concatenate_features(features), {}
    
    async def batch_process(
        self, 
        inputs: List[MultimodalInput]
    ) -> List[UnifiedMultimodalResult]:
        """Process multiple multimodal inputs efficiently."""
        if not inputs:
            return []
        
        results = []
        
        try:
            if self.status_animation:
                await self.status_animation.start(f"Processing {len(inputs)} multimodal inputs...")
            
            # Process in smaller batches to manage memory
            batch_size = min(self.config.batch_size, len(inputs))
            
            for i in range(0, len(inputs), batch_size):
                batch = inputs[i:i + batch_size]
                
                # Process batch
                batch_tasks = [
                    self.process_multimodal_input(inp) for inp in batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Batch processing error: {result}")
                        # Create error result
                        error_result = UnifiedMultimodalResult()
                        error_result.success = False
                        error_result.error_message = str(result)
                        results.append(error_result)
                    else:
                        results.append(result)
                
                # Memory cleanup between batches
                if self.gpu_manager and TORCH_AVAILABLE:
                    torch.cuda.empty_cache()
            
            if self.status_animation:
                await self.status_animation.stop()
            
            logger.info(f"✅ Batch processing completed: {len(results)} results")
            
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            if self.status_animation:
                await self.status_animation.stop()
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        stats = {
            "processor_type": "unified_multimodal",
            "modalities_available": [],
            "advanced_utilities": ADVANCED_UTILS_AVAILABLE,
            "torch_available": TORCH_AVAILABLE,
            "initialized": self.initialized,
            "config": {
                "max_memory_gb": self.config.max_memory_gb,
                "precision": self.config.precision,
                "fusion_strategy": self.config.fusion_strategy,
            }
        }
        
        if self.vision_processor:
            stats["modalities_available"].append("vision_language")
        if self.audio_processor:
            stats["modalities_available"].append("audio_language")
        
        if self.gpu_manager and TORCH_AVAILABLE:
            try:
                memory_info = self.gpu_manager.get_memory_stats()
                stats["memory_info"] = memory_info
            except Exception:
                pass
        
        return stats
    
    async def cleanup(self) -> None:
        """Clean up resources and models."""
        try:
            if self.vision_processor:
                await self.vision_processor.cleanup()
            
            if self.audio_processor:
                await self.audio_processor.cleanup()
            
            if self.gpu_manager and TORCH_AVAILABLE:
                torch.cuda.empty_cache()
            
            self.initialized = False
            logger.info("🧹 Unified processor cleaned up successfully")
            
        except Exception as e:
            logger.warning(f"⚠️  Cleanup warning: {e}")

# Utility functions
def create_unified_processor(config: Optional[UnifiedMultimodalConfig] = None) -> UnifiedMultimodalProcessor:
    """Create a unified multimodal processor with optimal settings."""
    if config is None:
        config = UnifiedMultimodalConfig()
    
    return UnifiedMultimodalProcessor(config)

def create_multimodal_input(
    text: Optional[str] = None,
    image_path: Optional[Union[str, Path]] = None,
    audio_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> MultimodalInput:
    """Create a multimodal input structure."""
    return MultimodalInput(
        text=text,
        image_path=image_path,
        audio_path=audio_path,
        **kwargs
    )

# Export availability flag
UNIFIED_MULTIMODAL_AVAILABLE = (VISION_LANGUAGE_AVAILABLE or AUDIO_LANGUAGE_AVAILABLE)

if __name__ == "__main__":
    # Simple test
    async def test_unified_processor():
        processor = create_unified_processor()
        stats = processor.get_performance_stats()
        print(f"🎯 Unified Multimodal Processor: {stats}")
    
    import asyncio
    asyncio.run(test_unified_processor())
