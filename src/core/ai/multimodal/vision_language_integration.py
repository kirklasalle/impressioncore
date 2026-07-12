#!/usr/bin/env python3
"""
ImpressionCore: Vision-Language Integration Framework
Phase 8A.1: Advanced Multimodal AI Processing

Integrates visual and language processing with advanced utilities for optimal performance.

Created: June 1, 2025
Authors: GitHub Copilot & Kirk LaSalle
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import numpy as np

# Advanced ImpressionCore utilities integration
try:
    from src.core.utils.rich_enhancements import HAS_RICH, FallbackConsole
    from src.core.utils.rich_logging import setup_rich_logger
    from src.core.utils.rich_status_animation import StatusAnimation
    from src.core.utils.gpu_memory_manager import GPUMemoryManager, get_gpu_memory_info
    from dev_tools.performance_optimizer import PerformanceOptimizer
    from dev_tools.memory_manager import MemoryManager
    from src.core.utils.benchmarking import PerformanceBenchmark
    ADVANCED_UTILS_AVAILABLE = True
      # Initialize rich utilities - use real Rich Console when available
    if HAS_RICH:
        from rich.console import Console as _RichConsole
        console = _RichConsole()
    else:
        console = FallbackConsole()
    logger = setup_rich_logger(__name__)
    # status_animation = StatusAnimation()  # Disabled - requires parameters
    
    console.print("[bold green]🚀 Vision-Language Integration Framework initialized with advanced utilities[/bold green]")
    
except ImportError as e:
    # Fallback for environments without advanced utilities
    ADVANCED_UTILS_AVAILABLE = False
    console = None
    status_animation = None
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.warning(f"Advanced utilities not available: {e}")

# PyTorch integration for neural networks
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader
    TORCH_AVAILABLE = True
    
    # GPU setup with memory optimization
    if torch.cuda.is_available():
        device = torch.device("cuda")
        if console:
            console.print(f"[bold blue]🎮 GPU detected: {torch.cuda.get_device_name()}[/bold blue]")
        logger.info(f"Using GPU: {torch.cuda.get_device_name()}")
    else:
        device = torch.device("cpu")
        if console:
            console.print("[yellow]⚠️  Using CPU - GPU not available[/yellow]")
        logger.warning("CUDA not available, using CPU")
        
except ImportError:
    TORCH_AVAILABLE = False
    device = None
    logger.error("PyTorch not available - Vision-Language processing will be limited")

# Transformers integration for pretrained models
try:
    from transformers import AutoTokenizer, AutoModel, CLIPProcessor, CLIPModel
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
    logger.info("Transformers library available for pretrained models")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers library not available - using basic implementations")

# PIL for image processing
try:
    from PIL import Image
    import torchvision.transforms as transforms
    PIL_AVAILABLE = True
    logger.info("PIL available for image processing")
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL not available - image processing limited")


@dataclass
class VisionLanguageConfig:
    """Configuration for Vision-Language processing."""
    model_name: str = "openai/clip-vit-base-patch32"
    max_image_size: Tuple[int, int] = (224, 224)
    max_text_length: int = 77
    batch_size: int = 1  # GTX 1050 Ti optimization
    precision: str = "fp16"  # Memory optimization
    use_gpu_optimization: bool = True
    enable_rich_ui: bool = True
    performance_monitoring: bool = True


@dataclass
class VisionLanguageResult:
    """Result from vision-language processing."""
    text_features: Optional[torch.Tensor] = None
    image_features: Optional[torch.Tensor] = None
    similarity_scores: Optional[torch.Tensor] = None
    predictions: Optional[List[str]] = None
    confidence_scores: Optional[List[float]] = None
    processing_time: float = 0.0
    memory_usage: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class VisionLanguageProcessor:
    """
    Advanced Vision-Language Integration Processor
    
    Leverages ImpressionCore's advanced utilities for optimal performance:
    - GPU Memory Management for GTX 1050 Ti optimization
    - Rich UI for user feedback and progress tracking
    - Performance monitoring and benchmarking
    - Memory optimization for constrained environments
    """
    
    def __init__(self, config: VisionLanguageConfig = None):
        """Initialize the Vision-Language processor with advanced utilities."""
        self.config = config or VisionLanguageConfig()
        
        # Initialize advanced utilities
        self._init_advanced_utilities()
        
        # Model components
        self.clip_model = None
        self.clip_processor = None
        self.tokenizer = None
        
        # Performance tracking
        self.processing_stats = {
            "total_processed": 0,
            "average_time": 0.0,
            "memory_peaks": [],
            "error_count": 0
        }
        
        # State management
        self.is_initialized = False
        self.device_info = {}
        
        if console and self.config.enable_rich_ui:
            console.print("[bold cyan]🔗 Vision-Language Processor initialized[/bold cyan]")
        
        logger.info("VisionLanguageProcessor created with advanced utilities integration")
    
    def _init_advanced_utilities(self):
        """Initialize ImpressionCore advanced utilities."""
        try:
            if ADVANCED_UTILS_AVAILABLE:
                # GPU Memory Manager for optimization
                self.gpu_manager = GPUMemoryManager()
                logger.info("✅ GPU Memory Manager initialized")
                
                # Performance Optimizer for system optimization
                self.perf_optimizer = PerformanceOptimizer()
                logger.info("✅ Performance Optimizer initialized")
                
                # Memory Manager for memory optimization
                self.memory_manager = MemoryManager()
                logger.info("✅ Memory Manager initialized")
                
                # Performance Benchmark for monitoring
                self.benchmark = PerformanceBenchmark()
                logger.info("✅ Performance Benchmark initialized")
                
                if console:
                    console.print("[bold green]✅ All advanced utilities initialized successfully[/bold green]")
                    
            else:
                self.gpu_manager = None
                self.perf_optimizer = None
                self.memory_manager = None
                self.benchmark = None
                logger.warning("⚠️  Advanced utilities not available - using fallbacks")
                
        except Exception as e:
            logger.error(f"❌ Error initializing advanced utilities: {e}")
            self.gpu_manager = None
            self.perf_optimizer = None
            self.memory_manager = None
            self.benchmark = None
    
    async def initialize_models(self) -> bool:
        """Initialize vision-language models with GPU optimization."""
        if console and self.config.enable_rich_ui:
            with console.status("[bold blue]🔄 Initializing vision-language models...[/bold blue]") as status:
                return await self._initialize_models_internal(status)
        else:
            return await self._initialize_models_internal(None)
    
    async def _initialize_models_internal(self, status=None) -> bool:
        """Internal model initialization with progress tracking."""
        try:
            start_time = time.time()
            
            # Update status
            if status:
                status.update("[bold blue]📥 Loading CLIP model...[/bold blue]")
            
            # GPU memory optimization
            if self.gpu_manager and TORCH_AVAILABLE:
                memory_info = get_gpu_memory_info()
                if memory_info.get("free", 0) < 1000:  # Less than 1GB free
                    logger.warning("⚠️  Low GPU memory - applying aggressive optimization")
                    torch.cuda.empty_cache()  # Clear cache
            
            # Load models with memory optimization
            if TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE:
                # Load CLIP model with optimization
                self.clip_model = CLIPModel.from_pretrained(
                    self.config.model_name,
                    torch_dtype=torch.float16 if self.config.precision == "fp16" else torch.float32
                ).to(device)
                
                self.clip_processor = CLIPProcessor.from_pretrained(self.config.model_name)
                
                # Enable memory efficient attention if available
                if hasattr(self.clip_model, "gradient_checkpointing_enable"):
                    self.clip_model.gradient_checkpointing_enable()
                
                if status:
                    status.update("[bold green]✅ CLIP model loaded successfully[/bold green]")
                
                logger.info("✅ CLIP model loaded with memory optimization")
                
            else:
                logger.error("❌ Required libraries not available for model loading")
                return False
            
            # Get device information
            if TORCH_AVAILABLE:
                self.device_info = {
                    "device": str(device),
                    "cuda_available": torch.cuda.is_available(),
                    "gpu_memory": get_gpu_memory_info() if self.gpu_manager else {}
                }
            
            initialization_time = time.time() - start_time
            
            if status:
                status.update(f"[bold green]🎉 Models initialized in {initialization_time:.2f}s[/bold green]")
            
            logger.info(f"✅ Models initialized successfully in {initialization_time:.2f}s")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            error_msg = f"❌ Model initialization failed: {e}"
            logger.error(error_msg)
            if console:
                console.print(f"[bold red]{error_msg}[/bold red]")
            return False
    
    async def process_image_text_pair(
        self, 
        image: Union[str, Image.Image, np.ndarray], 
        text: str
    ) -> VisionLanguageResult:
        """
        Process an image-text pair and compute similarity.
        
        Args:
            image: Image path, PIL Image, or numpy array
            text: Text description
            
        Returns:
            VisionLanguageResult with features and similarity scores
        """
        if not self.is_initialized:
            await self.initialize_models()
        
        start_time = time.time()
        result = VisionLanguageResult()
        
        try:
            # Performance monitoring start
            if self.benchmark:
                self.benchmark.start_benchmark("image_text_processing")
            
            # Rich UI progress tracking
            if console and self.config.enable_rich_ui:
                with console.status("[bold blue]🔄 Processing image-text pair...[/bold blue]") as status:
                    result = await self._process_pair_internal(image, text, status, start_time)
            else:
                result = await self._process_pair_internal(image, text, None, start_time)
            
            # Performance monitoring end
            if self.benchmark:
                benchmark_result = self.benchmark.end_benchmark("image_text_processing")
                result.metadata["benchmark"] = benchmark_result
            
            # Update statistics
            self.processing_stats["total_processed"] += 1
            self.processing_stats["average_time"] = (
                (self.processing_stats["average_time"] * (self.processing_stats["total_processed"] - 1) + 
                 result.processing_time) / self.processing_stats["total_processed"]
            )
            
            return result
            
        except Exception as e:
            error_msg = f"❌ Processing failed: {e}"
            logger.error(error_msg)
            self.processing_stats["error_count"] += 1
            
            result.metadata["error"] = str(e)
            result.processing_time = time.time() - start_time
            return result
    
    async def _process_pair_internal(
        self, 
        image: Union[str, Image.Image, np.ndarray], 
        text: str, 
        status=None,
        start_time: float = None
    ) -> VisionLanguageResult:
        """Internal processing with progress tracking."""
        result = VisionLanguageResult()
        
        if start_time is None:
            start_time = time.time()
        
        try:
            # GPU memory check
            if self.gpu_manager and TORCH_AVAILABLE:
                memory_before = get_gpu_memory_info()
                result.memory_usage["gpu_before"] = memory_before
            
            # Update progress
            if status:
                status.update("[bold blue]📷 Processing image...[/bold blue]")
            
            # Load and preprocess image
            if isinstance(image, str):
                image = Image.open(image).convert("RGB")
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(image).convert("RGB")
            
            # Process with CLIP
            if status:
                status.update("[bold blue]🧠 Computing features...[/bold blue]")
            
            inputs = self.clip_processor(
                text=[text], 
                images=[image], 
                return_tensors="pt", 
                padding=True,
                truncation=True,
                max_length=self.config.max_text_length
            ).to(device)
            
            # Forward pass with memory optimization
            with torch.no_grad():
                if self.config.precision == "fp16":
                    with torch.autocast(device_type='cuda' if torch.cuda.is_available() else 'cpu'):
                        outputs = self.clip_model(**inputs)
                else:
                    outputs = self.clip_model(**inputs)
                
                # Extract features
                result.text_features = outputs.text_embeds
                result.image_features = outputs.image_embeds
                
                # Compute similarity
                similarity = torch.cosine_similarity(
                    result.text_features, 
                    result.image_features
                )
                result.similarity_scores = similarity
                
                # Convert to confidence scores
                confidence = torch.sigmoid(similarity * 2.5)  # Scale for better range
                result.confidence_scores = confidence.cpu().numpy().tolist()
            
            # GPU memory check after processing
            if self.gpu_manager and TORCH_AVAILABLE:
                memory_after = get_gpu_memory_info()
                result.memory_usage["gpu_after"] = memory_after
                result.memory_usage["gpu_used"] = memory_after.get("allocated", 0) - memory_before.get("allocated", 0)
            
            result.processing_time = time.time() - start_time
            
            if status:
                status.update(f"[bold green]✅ Processing complete in {result.processing_time:.2f}s[/bold green]")
            
            logger.info(f"✅ Image-text pair processed successfully in {result.processing_time:.2f}s")
            
            # Add metadata
            result.metadata.update({
                "device": str(device),
                "model_name": self.config.model_name,
                "precision": self.config.precision,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            result.processing_time = time.time() - start_time
            result.metadata["error"] = str(e)
            raise e
    
    async def batch_process_images(
        self,
        images: List[Union[str, Image.Image, np.ndarray]],
        texts: List[str]
    ) -> List[VisionLanguageResult]:
        """
        Process multiple image-text pairs in batch for efficiency.
        
        Args:
            images: List of images
            texts: List of corresponding texts
            
        Returns:
            List of VisionLanguageResult objects
        """
        if len(images) != len(texts):
            raise ValueError("Number of images and texts must match")
        
        results = []
        
        if console and self.config.enable_rich_ui:
            from rich.progress import Progress, TaskID
            
            with Progress() as progress:
                task = progress.add_task(
                    "[bold blue]🔄 Processing batch...", 
                    total=len(images)
                )
                
                for i, (image, text) in enumerate(zip(images, texts)):
                    result = await self.process_image_text_pair(image, text)
                    results.append(result)
                    
                    progress.update(
                        task, 
                        advance=1, 
                        description=f"[bold blue]🔄 Processed {i+1}/{len(images)} pairs"
                    )
        else:
            for image, text in zip(images, texts):
                result = await self.process_image_text_pair(image, text)
                results.append(result)
        
        logger.info(f"✅ Batch processing complete: {len(results)} pairs processed")
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        stats = {
            "processing_stats": self.processing_stats.copy(),
            "device_info": self.device_info.copy(),
            "config": {
                "model_name": self.config.model_name,
                "precision": self.config.precision,
                "batch_size": self.config.batch_size
            }
        }
        
        # Add GPU memory info if available
        if self.gpu_manager and TORCH_AVAILABLE:
            try:
                stats["current_gpu_memory"] = get_gpu_memory_info()
            except Exception as e:
                stats["gpu_memory_error"] = str(e)
        
        # Add performance benchmarks if available
        if self.benchmark:
            stats["benchmarks"] = self.benchmark.get_all_benchmarks()
        
        return stats
    
    def cleanup(self):
        """Clean up resources and free memory."""
        try:
            if self.clip_model:
                del self.clip_model
            if self.clip_processor:
                del self.clip_processor
            
            if TORCH_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            if console:
                console.print("[bold yellow]🧹 Vision-Language Processor cleaned up[/bold yellow]")
            
            logger.info("✅ Resources cleaned up successfully")
            
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")


# Example usage and demonstration
async def demo_vision_language_processing():
    """Demonstrate the Vision-Language Integration capabilities."""
    if console:
        console.print("[bold cyan]🚀 Starting Vision-Language Integration Demo[/bold cyan]")
    
    # Initialize processor
    processor = VisionLanguageProcessor()
    
    # Initialize models
    if await processor.initialize_models():
        if console:
            console.print("[bold green]✅ Models initialized successfully![/bold green]")
        
        # Example processing (would need actual image)
        # result = await processor.process_image_text_pair("image.jpg", "A beautiful sunset")
        
        # Show performance stats
        stats = processor.get_performance_stats()
        if console:
            console.print(f"[bold blue]📊 Performance Stats:[/bold blue]")
            console.print(json.dumps(stats, indent=2, default=str))
        
        # Cleanup
        processor.cleanup()
    else:
        if console:
            console.print("[bold red]❌ Model initialization failed![/bold red]")


if __name__ == "__main__":
    # Run demo if script is executed directly
    asyncio.run(demo_vision_language_processing())
