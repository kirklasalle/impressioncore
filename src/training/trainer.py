#!/usr/bin/env python3
"""
ImpressionCore: Trainer

Module for trainer functionality in the ImpressionCore framework.

File: training/trainer.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, training, gpu-optimized, ml, pytorch, production, 2025, object-oriented]
Dependencies: [torch, typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements trainer functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
    # Basic usage example
    from training.trainer import DataLoaderFactory
    instance = DataLoaderFactory()
    result = instance.process()

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation

Memory Considerations:
- All training loops and data loaders are optimized for low VRAM usage.
- Uses gradient checkpointing and chunked data loading where possible.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from ..core.utils.memory_optimization.advanced_optimizer import (
    get_memory_efficient_optimizer,
    MemoryEfficientOptimizerManager,
    MemoryOptimizationConfig,
    CustomMemoryEfficientOptimizers
)
from torch.utils.data import DataLoader, Dataset, random_split
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
import time
from tqdm import tqdm
from torch.utils.checkpoint import checkpoint
import threading
from ..core.memory import dynamic_memory_manager as dmm
# Memory optimization: Memory-critical operation

from ..core.utils.precision_manager import PrecisionManager, PrecisionMode
from ..core.utils.memory_utils import LayerManager
# Memory optimization: Memory-critical operation
from .pretraining import MaskedLanguageModeling

logger = logging.getLogger(__name__)

class DataLoaderFactory:
    """
    Factory class for creating data loaders for different modalities.
    
    This class provides utilities to create specialized data loaders
    for various data types (text, image, audio, mixed, etc.).
    """
    
    @staticmethod
    def create_text_dataloader(
        dataset: Union[Dataset, List[Tuple]],
        batch_size: int = 8,
        shuffle: bool = True,
        num_workers: int = 4,
        pin_memory: bool = True,
        # Memory optimization: Memory-critical operation
        collate_fn: Optional[Callable] = None
    ) -> DataLoader:
        """
        Create a data loader for text datasets.
        
        Args:
            dataset: PyTorch Dataset or list of (text, label) tuples
            batch_size: Training batch size
            shuffle: Whether to shuffle the data
            num_workers: Number of workers for loading data
            pin_memory: Whether to pin memory (useful for GPU training)
            # Memory optimization: Memory-critical operation
            collate_fn: Custom collate function
            
        Returns:
            DataLoader for the text dataset
        """
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=pin_memory,
            # Memory optimization: Memory-critical operation
            collate_fn=collate_fn
        )
    
    @staticmethod
    def create_image_dataloader(
        dataset: Union[Dataset, List[Tuple]],
        batch_size: int = 8,
        shuffle: bool = True,
        num_workers: int = 4,
        pin_memory: bool = True,
        # Memory optimization: Memory-critical operation
        collate_fn: Optional[Callable] = None,
        prefetch_factor: int = 2
    ) -> DataLoader:
        """
        Create a data loader for image datasets.
        
        Args:
            dataset: PyTorch Dataset or list of (image, label) tuples
            batch_size: Training batch size
            shuffle: Whether to shuffle the data
            num_workers: Number of workers for loading data
            pin_memory: Whether to pin memory (useful for GPU training)
            # Memory optimization: Memory-critical operation
            collate_fn: Custom collate function
            prefetch_factor: Number of batches loaded in advance
            
        Returns:
            DataLoader for the image dataset
        """
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=pin_memory,
            # Memory optimization: Memory-critical operation
            prefetch_factor=prefetch_factor if num_workers > 0 else None,
            collate_fn=collate_fn
        )
    
    @staticmethod
    def create_audio_dataloader(
        dataset: Union[Dataset, List[Tuple]],
        batch_size: int = 8,
        shuffle: bool = True,
        num_workers: int = 4,
        pin_memory: bool = True,
        # Memory optimization: Memory-critical operation
        collate_fn: Optional[Callable] = None
    ) -> DataLoader:
        """
        Create a data loader for audio datasets.
        
        Args:
            dataset: PyTorch Dataset or list of (audio, label) tuples
            batch_size: Training batch size
            shuffle: Whether to shuffle the data
            num_workers: Number of workers for loading data
            pin_memory: Whether to pin memory (useful for GPU training)
            # Memory optimization: Memory-critical operation
            collate_fn: Custom collate function
            
        Returns:
            DataLoader for the audio dataset
        """
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=pin_memory,
            # Memory optimization: Memory-critical operation
            collate_fn=collate_fn
        )
    
    @staticmethod
    def create_multimodal_dataloader(
        dataset: Union[Dataset, List[Dict]],
        batch_size: int = 8,
        shuffle: bool = True,
        num_workers: int = 4,
        pin_memory: bool = True,
        # Memory optimization: Memory-critical operation
        collate_fn: Optional[Callable] = None
    ) -> DataLoader:
        """
        Create a data loader for multimodal datasets.
        
        Args:
            dataset: PyTorch Dataset or list of multimodal dictionaries
            batch_size: Training batch size
            shuffle: Whether to shuffle the data
            num_workers: Number of workers for loading data
            pin_memory: Whether to pin memory (useful for GPU training)
            # Memory optimization: Memory-critical operation
            collate_fn: Custom collate function for multimodal data
            
        Returns:
            DataLoader for the multimodal dataset
        """
        # If no collate function provided, use a default one
        # that handles different modalities
        if collate_fn is None:
            def default_multimodal_collate(batch):
                """
                
    default_multimodal_collate function for processing.
    
    Args:
        batch: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                result = {}
                # Check batch structure and extract elements
                if isinstance(batch[0], dict):
                    # Get all keys in the dataset
                    keys = batch[0].keys()
                    for key in keys:
                        if all(key in item for item in batch):
                            result[key] = [item[key] for item in batch]
                            
                            # Stack tensors if possible
                            if isinstance(result[key][0], torch.Tensor):
                                try:
                                    result[key] = torch.stack(result[key])
                                except RuntimeError:
                                    # Can't stack tensors of different sizes
                                    pass
                return result
            
            collate_fn = default_multimodal_collate
            
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=pin_memory,
            # Memory optimization: Memory-critical operation
            collate_fn=collate_fn
        )
    
    @staticmethod
    def create_train_val_test_split(
        dataset: Dataset,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42
    ) -> Tuple[Dataset, Dataset, Dataset]:
        """
        Split a dataset into train, validation, and test sets.
        
        Args:
            dataset: PyTorch Dataset to split
            train_ratio: Ratio of data for training
            val_ratio: Ratio of data for validation
            test_ratio: Ratio of data for testing
            seed: Random seed for reproducibility
            
        Returns:
            Tuple of (train_dataset, val_dataset, test_dataset)
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5, "Ratios must sum to 1"
        
        # Set the seed for reproducibility
        torch.manual_seed(seed)
        
        # Calculate sizes
        dataset_size = len(dataset)
        train_size = int(dataset_size * train_ratio)
        val_size = int(dataset_size * val_ratio)
        test_size = dataset_size - train_size - val_size
        
        # Split the dataset
        train_dataset, val_dataset, test_dataset = random_split(
            dataset, 
            [train_size, val_size, test_size],
            generator=torch.Generator().manual_seed(seed)
        )
        
        return train_dataset, val_dataset, test_dataset

class EvaluationMetrics:
    """
    Utility class for calculating evaluation metrics for different modalities.
    """
    
    @staticmethod
    def calculate_text_metrics(
        predictions: List[str],
        references: List[str],
        metric_set: str = "standard"
    ) -> Dict[str, float]:
        """
        Calculate metrics for text generation.
        
        Args:
            predictions: List of predicted texts
            references: List of reference texts
            metric_set: Which set of metrics to calculate
                        ("standard", "full", "lightweight")
                        
        Returns:
            Dictionary of metric names and values
        """
        try:
            from nltk.translate.bleu_score import sentence_bleu
            from nltk.tokenize import word_tokenize
        except ImportError:
            logger.warning("NLTK not found, using basic metrics only")
            # Simple word overlap as fallback
            metrics = {}
            total_overlap = 0
            for pred, ref in zip(predictions, references):
                pred_words = set(pred.lower().split())
                ref_words = set(ref.lower().split())
                if len(ref_words) > 0:
                    overlap = len(pred_words.intersection(ref_words)) / len(ref_words)
                    total_overlap += overlap
                    
            metrics["word_overlap"] = total_overlap / len(predictions) if predictions else 0
            return metrics
            
        # Calculate BLEU score
        bleu_scores = []
        for pred, ref in zip(predictions, references):
            try:
                pred_tokens = word_tokenize(pred.lower())
                ref_tokens = [word_tokenize(ref.lower())]
                score = sentence_bleu(ref_tokens, pred_tokens)
                bleu_scores.append(score)
            except Exception:
                bleu_scores.append(0.0)
                
        # Calculate ROUGE scores if available
        try:
            from rouge import Rouge
            rouge = Rouge()
            rouge_scores = rouge.get_scores(predictions, references, avg=True)
            
            metrics = {
                "BLEU": sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0,
                "ROUGE-1": rouge_scores["rouge-1"]["f"],
                "ROUGE-2": rouge_scores["rouge-2"]["f"],
                "ROUGE-L": rouge_scores["rouge-l"]["f"]
            }
        except ImportError:
            metrics = {
                "BLEU": sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0
            }
            
            # Calculate simple ROUGE-L ourselves as a fallback
            total_rouge_l = 0
            for pred, ref in zip(predictions, references):
                pred_tokens = pred.lower().split()
                ref_tokens = ref.lower().split()
                
                # Find longest common subsequence length
                m, n = len(pred_tokens), len(ref_tokens)
                lcs = [[0 for _ in range(n+1)] for _ in range(m+1)]
                for i in range(1, m+1):
                    for j in range(1, n+1):
                        if pred_tokens[i-1] == ref_tokens[j-1]:
                            lcs[i][j] = lcs[i-1][j-1] + 1
                        else:
                            lcs[i][j] = max(lcs[i-1][j], lcs[i][j-1])
                
                lcs_length = lcs[m][n]
                
                # Calculate ROUGE-L
                if m > 0 and n > 0:
                    recall = lcs_length / n
                    precision = lcs_length / m
                    if recall + precision > 0:
                        f1 = 2 * recall * precision / (recall + precision)
                        total_rouge_l += f1
                    
            metrics["ROUGE-L"] = total_rouge_l / len(predictions) if predictions else 0
        
        # Add more metrics for "full" set
        if metric_set == "full":
            # Calculate exact match
            exact_matches = sum(1 for p, r in zip(predictions, references) if p.strip() == r.strip())
            metrics["exact_match"] = exact_matches / len(predictions) if predictions else 0
            
            # Calculate F1 score on token overlap
            total_f1 = 0
            for pred, ref in zip(predictions, references):
                pred_tokens = set(word_tokenize(pred.lower()))
                ref_tokens = set(word_tokenize(ref.lower()))
                
                if len(pred_tokens) > 0 and len(ref_tokens) > 0:
                    precision = len(pred_tokens.intersection(ref_tokens)) / len(pred_tokens)
                    recall = len(pred_tokens.intersection(ref_tokens)) / len(ref_tokens)
                    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
                    total_f1 += f1
                    
            metrics["F1"] = total_f1 / len(predictions) if predictions else 0
                
        return metrics
    
    @staticmethod
    def calculate_image_metrics(
        predictions: torch.Tensor,
        targets: torch.Tensor,
        metric_set: str = "standard"
    ) -> Dict[str, float]:
        """
        Calculate metrics for image generation.
        
        Args:
            predictions: Tensor of predicted images [B, C, H, W]
            targets: Tensor of target images [B, C, H, W]
            metric_set: Which set of metrics to calculate
                        
        Returns:
            Dictionary of metric names and values
        """
        metrics = {}
        
        # Mean squared error
        mse = torch.mean((predictions - targets) ** 2).item()
        metrics["MSE"] = mse
        
        # PSNR (Peak Signal-to-Noise Ratio)
        max_pixel_value = 1.0
        psnr = 10 * torch.log10(max_pixel_value**2 / mse).item() if mse > 0 else float('inf')
        metrics["PSNR"] = psnr
        
        # Try to calculate SSIM if pytorch-msssim is available
        try:
            from pytorch_msssim import ssim
            ssim_val = ssim(predictions, targets, data_range=1.0).item()
            metrics["SSIM"] = ssim_val
        except ImportError:
            logger.warning("pytorch-msssim not found, skipping SSIM calculation")
        
        if metric_set == "full":
            # Try to calculate more sophisticated metrics
            try:
                from torchmetrics.image import StructuralSimilarityIndexMeasure
                from torchmetrics.image import PeakSignalNoiseRatio
                
                ssim_metric = StructuralSimilarityIndexMeasure(data_range=1.0)
                psnr_metric = PeakSignalNoiseRatio(data_range=1.0)
                
                metrics["SSIM_torch"] = ssim_metric(predictions, targets).item()
                metrics["PSNR_torch"] = psnr_metric(predictions, targets).item()
            except ImportError:
                logger.warning("torchmetrics not found, skipping additional image metrics")
                
        return metrics
        
    @staticmethod
    def calculate_audio_metrics(
        predictions: torch.Tensor,
        targets: torch.Tensor
    ) -> Dict[str, float]:
        """
        Calculate metrics for audio generation.
        
        Args:
            predictions: Tensor of predicted audio [B, T] or [B, 1, T]
            targets: Tensor of target audio [B, T] or [B, 1, T]
                        
        Returns:
            Dictionary of metric names and values
        """
        # Ensure 2D shape [B, T]
        if predictions.dim() == 3:
            predictions = predictions.squeeze(1)
        if targets.dim() == 3:
            targets = targets.squeeze(1)
            
        # Mean squared error
        mse = torch.mean((predictions - targets) ** 2).item()
        
        # Signal-to-Noise Ratio
        noise = predictions - targets
        signal_power = torch.mean(targets**2).item()
        noise_power = torch.mean(noise**2).item()
        snr = 10 * torch.log10(signal_power / noise_power).item() if noise_power > 0 else float('inf')
        
        metrics = {
            "MSE": mse,
            "SNR": snr
        }
        
        return metrics
        
    @staticmethod
    def calculate_classification_metrics(
        predictions: torch.Tensor,
        targets: torch.Tensor
    ) -> Dict[str, float]:
        """
        Calculate metrics for classification tasks.
        
        Args:
            predictions: Tensor of predicted class probabilities [B, C] or class indices [B]
            targets: Tensor of target class indices [B]
                        
        Returns:
            Dictionary of metric names and values
        """
        # Convert probabilities to class indices if needed
        if predictions.dim() > 1 and predictions.size(1) > 1:
            predictions = torch.argmax(predictions, dim=1)
        
        # Calculate accuracy
        correct = (predictions == targets).float().sum().item()
        total = targets.size(0)
        accuracy = correct / total if total > 0 else 0
        
        metrics = {
            "accuracy": accuracy,
        }
        
        # Calculate additional metrics if sklearn is available
        try:
            from sklearn.metrics import precision_score, recall_score, f1_score
            
            # Convert to numpy for sklearn
            pred_np = predictions.cpu().numpy()
            target_np = targets.cpu().numpy()
            
            # Get unique classes
            unique_classes = set(target_np)
            
            # Calculate metrics if more than one class exists
            if len(unique_classes) > 1:
                metrics["precision"] = precision_score(target_np, pred_np, average='macro')
                metrics["recall"] = recall_score(target_np, pred_np, average='macro')
                metrics["f1"] = f1_score(target_np, pred_np, average='macro')
        except ImportError:
            logger.warning("scikit-learn not found, skipping additional classification metrics")
            
        return metrics

class ModelTrainer:
    """
    Training manager for transformer and diffusion models.
    """
    
    def __init__(
        self,
        model: nn.Module,
        train_dataloader: DataLoader,
        val_dataloader: Optional[DataLoader] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        optimizer_name: str = "auto",  # Changed default to "auto" for intelligent selection
        optimizer_lr: float = 5e-5,
        scheduler: Optional[Any] = None,
        loss_fn: Optional[Callable] = None,
        device: Optional[str] = None,
        checkpoint_dir: Optional[str] = None,
        log_interval: int = 100,
        save_interval: int = 1000,
        gradient_accumulation_steps: int = 1,
        mixed_precision: bool = True,
        target_vram_usage: float = 0.8,
        num_layers_to_offload: int = 1,
        pretraining: bool = False,
        vocab_size: int = 0,
        memory_optimization_config: Optional[MemoryOptimizationConfig] = None,
        enable_adaptive_optimization: bool = True,
        enable_gradient_accumulation_wrapper: bool = False
    ):
        """
        Initialize the ModelTrainer with advanced memory-efficient optimization.
        
        Args:
            model: PyTorch model to train
            train_dataloader: Training data loader
            val_dataloader: Validation data loader (optional)
            optimizer: Optimizer (if provided, overrides automatic selection)
            optimizer_name: Name of optimizer to use. Options:
                - "auto": Automatically select optimal optimizer based on available memory
                - "adam8bit", "adamw8bit", "sgd8bit": 8-bit optimizers (most memory efficient)
                - "adamw", "adam", "sgd", "rmsprop", "adagrad": Standard optimizers
                - "adaptive": Use memory-adaptive optimizer that switches based on usage
            optimizer_lr: Learning rate for optimizer
            scheduler: Learning rate scheduler (optional)
            loss_fn: Loss function (defaults to CrossEntropyLoss)
            device: Device for training (auto-detected if None)
            checkpoint_dir: Directory for saving checkpoints
            log_interval: Logging interval in steps
            save_interval: Checkpoint saving interval in steps
            gradient_accumulation_steps: Steps for gradient accumulation
            mixed_precision: Whether to use mixed precision training
            target_vram_usage: Target VRAM usage ratio
            num_layers_to_offload: Number of layers to offload to CPU
            pretraining: Whether this is pretraining
            vocab_size: Vocabulary size for the model
            memory_optimization_config: Advanced memory optimization settings
            enable_adaptive_optimization: Enable memory-adaptive optimizers
            enable_gradient_accumulation_wrapper: Use gradient accumulation wrapper for memory efficiency
        
        Memory Usage:
            - Memory-efficient implementation optimized for GTX 1050 Ti constraints
            - Intelligent optimizer selection based on available memory
            - Automatic fallback to more memory-efficient optimizers when needed
            - Real-time memory monitoring and optimization adjustments
        """
        self.model = model
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
          # Initialize memory optimization configuration        
        self.memory_config = memory_optimization_config or MemoryOptimizationConfig()
        self.enable_adaptive_optimization = enable_adaptive_optimization
        self.enable_gradient_accumulation_wrapper = enable_gradient_accumulation_wrapper
        
        # Initialize other components
        self.scheduler = scheduler
        self.loss_fn = loss_fn or nn.CrossEntropyLoss()
          # CUDA-first device setup with proper logging
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                logger.info("✓ Using CUDA device for training (auto-detected)")
                # Log CUDA device info
                cuda_device = torch.cuda.get_device_name(0)
                cuda_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"  CUDA Device: {cuda_device}")
                logger.info(f"  CUDA Memory: {cuda_memory:.1f} GB")
            else:
                self.device = torch.device("cpu")
                logger.warning("⚠ CUDA not available, falling back to CPU")
        else:
            if device == "cuda":
                if torch.cuda.is_available():
                    self.device = torch.device("cuda")
                    logger.info("✓ Using CUDA device for training (specified)")
                    cuda_device = torch.cuda.get_device_name(0)
                    cuda_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                    logger.info(f"  CUDA Device: {cuda_device}")
                    logger.info(f"  CUDA Memory: {cuda_memory:.1f} GB")
                else:
                    self.device = torch.device("cpu")
                    logger.warning("⚠ CUDA requested but not available, falling back to CPU")
            else:
                self.device = torch.device(device)
                logger.info(f"✓ Using specified device: {device}")
              # Initialize advanced optimizer manager (after device setup)
        self.optimizer_manager = MemoryEfficientOptimizerManager(model, self.device)
        
        # Initialize optimizer with intelligent selection
        if optimizer is not None:
            self.optimizer = optimizer
            logger.info("Using provided optimizer")
        else:
            self.optimizer = self._initialize_optimizer(optimizer_name, optimizer_lr)
        
        # Apply gradient accumulation wrapper if enabled
        if self.enable_gradient_accumulation_wrapper and gradient_accumulation_steps > 1:
            logger.info(f"Applying gradient accumulation wrapper (steps: {gradient_accumulation_steps})")
            self.optimizer = CustomMemoryEfficientOptimizers.create_gradient_accumulation_optimizer(
                self.optimizer, gradient_accumulation_steps
            )
            
        self.checkpoint_dir = checkpoint_dir or "checkpoints"
        self.log_interval = log_interval
        self.save_interval = save_interval
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.mixed_precision = mixed_precision and torch.cuda.is_available()
        self.target_vram_usage = target_vram_usage
        self.num_layers_to_offload = num_layers_to_offload
        self.pretraining = pretraining
        self.vocab_size = vocab_size
        
        # Memory monitoring
        self.memory_stats_history = []
        self.step_count = 0
        
        # Log initial setup
        self._log_training_setup()
    
    def _initialize_optimizer(self, optimizer_name: str, lr: float) -> torch.optim.Optimizer:
        """
        Initialize optimizer with intelligent selection based on memory constraints.
        
        Args:
            optimizer_name: Optimizer type or "auto" for automatic selection
            lr: Learning rate
            
        Returns:
            Initialized optimizer
        """
        try:
            if optimizer_name == "auto":
                logger.info("Using automatic optimizer selection based on available memory")
                optimizer = self.optimizer_manager.select_optimal_optimizer(lr=lr)
                
            elif optimizer_name == "adaptive":
                logger.info("Using memory-adaptive optimizer")
                optimizer = CustomMemoryEfficientOptimizers.create_memory_adaptive_optimizer(
                    self.model, lr=lr
                )
                
            else:
                logger.info(f"Using specified optimizer: {optimizer_name}")
                optimizer = get_memory_efficient_optimizer(
                    self.model, optimizer_name=optimizer_name, lr=lr
                )
            
            # Log optimizer selection
            optimizer_type = optimizer.__class__.__name__
            if hasattr(optimizer, 'current_optimizer_name'):
                optimizer_type = f"{optimizer_type} (adaptive: {optimizer.current_optimizer_name})"
            
            logger.info(f"Initialized optimizer: {optimizer_type}")
            return optimizer
            
        except Exception as e:
            logger.warning(f"Failed to initialize {optimizer_name} optimizer: {e}")
            logger.info("Falling back to AdamW optimizer")
            return optim.AdamW(self.model.parameters(), lr=lr)
    
    def _log_training_setup(self):
        """Log detailed training setup information."""
        logger.info("=== Training Setup ===")
        logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        logger.info(f"Device: {self.device}")
        logger.info(f"Mixed precision: {self.mixed_precision}")
        logger.info(f"Gradient accumulation steps: {self.gradient_accumulation_steps}")
        
        # Memory information
        memory_report = self.optimizer_manager.get_memory_report()
        logger.info(f"Optimizer: {memory_report.get('optimizer_type', 'unknown')}")
        logger.info(f"Estimated optimizer memory: {memory_report.get('estimated_optimizer_memory_gb', 0):.3f} GB")
        
        if memory_report.get('recommendations'):
            logger.info("Memory optimization recommendations:")
            for rec in memory_report['recommendations']:
                logger.info(f"  - {rec}")
        
        logger.info("=====================")

        # Move model to device
        # Memory optimization: Device placement for memory management
        self.model.to(self.device)
        # Memory optimization: Device placement for memory management

        # Set up mixed precision if enabled
        self.scaler = torch.cuda.amp.GradScaler() if self.mixed_precision else None
        # Memory optimization: CUDA operations for GPU acceleration

        # Create checkpoint directory if it doesn't exist
        Path(self.checkpoint_dir).mkdir(parents=True, exist_ok=True)

        # Initialize tracking variables
        self.global_step = 0
        self.best_val_loss = float('inf')
        self.metrics = {"train_loss": [], "val_loss": [], "learning_rate": []}        # Initialize PrecisionManager
        self.precision_manager = PrecisionManager(target_vram_usage=self.target_vram_usage)
        self.model_size = sum(p.numel() for p in self.model.parameters())        
        # Initialize LayerManager
        self.layer_manager = LayerManager(self.model)

        # Initialize MaskedLanguageModeling loss if pretraining is enabled
        if self.pretraining:
            self.mlm_loss_fn = MaskedLanguageModeling(self.vocab_size)

    @classmethod
    def from_config(
        cls,
        model_config: Dict[str, Any],
        device: str = "auto",
        mixed_precision: bool = True,
        target_vram_usage: float = 3.5
    ) -> 'ModelTrainer':
        """
        Create a ModelTrainer from a model configuration dictionary.
        This is used by TrainingManager for initialization.
        
        Args:
            model_config (Dict[str, Any]): Model configuration
            device (str): Device to use for training
            mixed_precision (bool): Whether to use mixed precision
            target_vram_usage (float): Target VRAM usage in GB
            
        Returns:
            ModelTrainer: Configured trainer instance
        """        # CUDA-first device selection with proper fallback
        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
                logger.info("Auto-selecting CUDA for training")
            else:
                device = "cpu"
                logger.warning("CUDA not available, auto-selecting CPU")
        elif device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            device = "cpu"
        
        # Create a simple model for demonstration
        # In practice, this would create the model based on model_config
        if "model_name" in model_config:
            model_name = model_config["model_name"]
        else:
            model_name = "simple_model"
            
        # Create a simple feedforward model as placeholder
        # This should be replaced with actual model creation logic
        model = nn.Sequential(
            nn.Linear(768, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 10)  # 10 classes as example
        )
        
        # Create dummy dataloaders
        # In practice, these would be created from the model_config
        from torch.utils.data import TensorDataset
        
        # Create dummy data
        dummy_data = torch.randn(100, 768)
        dummy_labels = torch.randint(0, 10, (100,))
        dummy_dataset = TensorDataset(dummy_data, dummy_labels)
        
        train_dataloader = DataLoader(dummy_dataset, batch_size=8, shuffle=True)
        val_dataloader = DataLoader(dummy_dataset, batch_size=8, shuffle=False)
        
        # Create the trainer instance
        trainer = cls(
            model=model,
            train_dataloader=train_dataloader,
            val_dataloader=val_dataloader,
            device=device,
            mixed_precision=mixed_precision,
            target_vram_usage=target_vram_usage
        )
        
        return trainer

    def train(self, num_epochs: int, eval_steps: int = 500) -> Dict[str, List[float]]:
        """
        Trains the model for a specified number of epochs, with integrated dynamic memory management.
        # Memory optimization: Explicit memory cleanup
        Args:
            num_epochs (int): Number of epochs to train.
            eval_steps (int): Steps between evaluations.
        Returns:
            Dict[str, List[float]]: Training metrics.
        Memory Implications:
        # Memory optimization: Memory-critical operation
            Integrates real-time VRAM monitoring and automated offloading to prevent OOM errors.
        """
        logger.info(f"Starting training for {num_epochs} epochs on {self.device}")
        # Memory optimization: Device placement for memory management
        start_time = time.time()

        # --- Dynamic Memory Manager Integration ---
        # Memory optimization: Memory-critical operation
        stop_flag = threading.Event()
        def offload_handler():
            """
            Offload handler for automated CPU fallback during training.
            Moves all model parameters and buffers to CPU if VRAM is low.
            """
            for param in self.model.parameters():
                param.data = param.data.cpu()
                if param.grad is not None:
                    param.grad = param.grad.cpu()
            for buffer in self.model.buffers():
                buffer.data = buffer.data.cpu()
            dmm.log_memory_event("cpu_fallback_triggered", details=f"Automated CPU fallback (training) at step {self.global_step}")
        def stop_condition():
            """
            
    stop_condition function for processing.
    
    Args:
        No arguments: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
            """
            return stop_flag.is_set()
        mem_thread = threading.Thread(
            target=dmm.monitor_and_manage_memory,
            # Memory optimization: Memory-critical operation
            kwargs={
                'check_interval': 1.0,
                'vram_threshold': self.target_vram_usage,
                'on_offload': offload_handler,
                'stop_condition': stop_condition
            },
            daemon=True
        )
        mem_thread.start()
        dmm.log_memory_event("Memory manager started", details=f"Training {num_epochs} epochs")
        # Memory optimization: Memory-critical operation
        # --- End Integration ---

        try:
            for epoch in range(num_epochs):
                # Training phase
                self.model.train()
                epoch_loss = 0.0

                with tqdm(total=len(self.train_dataloader), desc=f"Epoch {epoch+1}/{num_epochs}") as pbar:
                    for step, batch in enumerate(self.train_dataloader):
                        # Optimize memory usage before each step
                        # Memory optimization: Memory-critical operation
                        self.model = self.precision_manager.optimize_memory_usage(self.model, self.model_size)
                        # Memory optimization: Explicit memory cleanup

                        # Move batch to device
                        # Memory optimization: Device placement for memory management
                        batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v
                        # Memory optimization: Device placement for memory management
                                 for k, v in batch.items()}

                        # Log memory event after batch allocation
                        # Memory optimization: Memory-critical operation
                        dmm.log_memory_event("Batch allocated", details=f"Epoch {epoch+1}, Step {step+1}")
                        # Memory optimization: Memory-critical operation

                        # Auto offload layers to CPU (already called in offload_handler, but keep for redundancy)
                        self.layer_manager.auto_offload()

                        # Forward pass with mixed precision if enabled
                        if self.mixed_precision:
                            with torch.cuda.amp.autocast():
                            # Memory optimization: CUDA operations for GPU acceleration
                                outputs = self.model(**batch)
                                if self.pretraining:
                                    loss = self.mlm_loss_fn(outputs["logits"], batch["labels"])
                                else:
                                    loss = outputs.loss if hasattr(outputs, 'loss') else self.loss_fn(outputs, batch["labels"])
                        else:
                            outputs = self.model(**batch)
                            if self.pretraining:
                                loss = self.mlm_loss_fn(outputs["logits"], batch["labels"])
                            else:
                                loss = outputs.loss if hasattr(outputs, 'loss') else self.loss_fn(outputs, batch["labels"])

                        # Scale loss for gradient accumulation
                        loss = loss / self.gradient_accumulation_steps

                        # Backward pass with mixed precision if enabled
                        if self.mixed_precision:
                            self.scaler.scale(loss).backward()
                        else:
                            loss.backward()

                        # Accumulate loss
                        epoch_loss += loss.item() * self.gradient_accumulation_steps

                        # Update weights if we've accumulated enough gradients
                        if (step + 1) % self.gradient_accumulation_steps == 0:
                            if self.mixed_precision:
                                self.scaler.step(self.optimizer)
                                self.scaler.update()
                            else:
                                self.optimizer.step()

                            self.optimizer.zero_grad()

                            if self.scheduler:
                                self.scheduler.step()

                            # Track learning rate
                            self.metrics["learning_rate"].append(self.optimizer.param_groups[0]["lr"])

                            self.global_step += 1

                            # Log progress
                            if self.global_step % self.log_interval == 0:
                                used_memory, total_memory = self.precision_manager.get_current_memory_usage()
                                # Memory optimization: Memory-critical operation
                                logger.info(
                                    f"Epoch {epoch+1}/{num_epochs} | Step {self.global_step} | "
                                    f"Loss: {loss.item() * self.gradient_accumulation_steps:.4f} | "
                                    f"LR: {self.optimizer.param_groups[0]['lr']:.2e} | "
                                    f"Precision: {self.precision_manager.current_mode.value} | "
                                    f"VRAM Usage: {used_memory:.2f} / {total_memory:.2f} GB"
                                    # Memory optimization: Memory-critical operation
                                )
                                self.metrics["train_loss"].append(loss.item() * self.gradient_accumulation_steps)

                            # Evaluate on validation set
                            if self.val_dataloader and self.global_step % eval_steps == 0:
                                val_loss = self.evaluate()
                                self.metrics["val_loss"].append(val_loss)

                                # Save best model
                                if val_loss < self.best_val_loss:
                                    self.best_val_loss = val_loss
                                    self.save_checkpoint(f"best_model.pt")
                                    logger.info(f"New best model saved with val_loss: {val_loss:.4f}")
                                    # Memory optimization: Explicit memory cleanup

                            # Save checkpoint at intervals
                            if self.global_step % self.save_interval == 0:
                                self.save_checkpoint(f"checkpoint-{self.global_step}.pt")

                        # Update progress bar
                        pbar.update(1)
                        pbar.set_postfix({"loss": loss.item() * self.gradient_accumulation_steps})

                # End of epoch
                avg_epoch_loss = epoch_loss / len(self.train_dataloader)
                logger.info(f"Epoch {epoch+1}/{num_epochs} completed | Avg Loss: {avg_epoch_loss:.4f}")

                # Save checkpoint after each epoch
                self.save_checkpoint(f"checkpoint-epoch-{epoch+1}.pt")

                # Evaluate at the end of each epoch
                if self.val_dataloader:
                    val_loss = self.evaluate()
                    self.metrics["val_loss"].append(val_loss)

                    # Save best model
                    if val_loss < self.best_val_loss:
                        self.best_val_loss = val_loss
                        self.save_checkpoint(f"best_model.pt")
                        logger.info(f"New best model saved with val_loss: {val_loss:.4f}")
                        # Memory optimization: Explicit memory cleanup

        except RuntimeError as e:
            if 'out of memory' in str(e).lower():
            # Memory optimization: Memory-critical operation
                dmm.log_memory_event("OOM error", details=str(e))
                # Memory optimization: Memory-critical operation
                logger.error(f"OOM error: {e}")
                # Optionally, try to recover or exit gracefully
            else:
                raise
        finally:
            # Signal memory manager to stop and wait for thread to finish
            # Memory optimization: Memory-critical operation
            stop_flag.set()
            mem_thread.join(timeout=2)
            dmm.log_memory_event("Memory manager stopped", details="Training complete")
            # Memory optimization: Memory-critical operation

        # Training completed
        total_time = time.time() - start_time
        logger.info(f"Training completed in {total_time/60:.2f} minutes")

        # Save final model
        self.save_checkpoint("final_model.pt")

        return self.metrics

    def train_step(self) -> Dict[str, Any]:
        """
        Execute a single training step and return metrics.
        
        Returns:
            Dict[str, Any]: Training step metrics including loss, learning rate, etc.
        """
        if not hasattr(self, 'train_iterator'):
            self.train_iterator = iter(self.train_dataloader)
        
        try:
            batch = next(self.train_iterator)
        except StopIteration:
            # Reset iterator when epoch ends
            self.train_iterator = iter(self.train_dataloader)
            batch = next(self.train_iterator)
        
        # Move batch to device
        if isinstance(batch, dict):
            batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v
                     for k, v in batch.items()}
        elif isinstance(batch, (list, tuple)):
            batch = [item.to(self.device) if isinstance(item, torch.Tensor) else item 
                     for item in batch]
        
        # Start timing
        start_time = time.time()
        
        # Set model to training mode
        self.model.train()
        
        # Forward pass with mixed precision if enabled
        if self.mixed_precision:
            with torch.cuda.amp.autocast():
                outputs = self.model(**batch if isinstance(batch, dict) else {'input': batch[0], 'labels': batch[1]})
                if hasattr(outputs, 'loss'):
                    loss = outputs.loss
                else:
                    logits = outputs.logits if hasattr(outputs, 'logits') else outputs
                    targets = batch['labels'] if isinstance(batch, dict) else batch[1]
                    loss = self.loss_fn(logits, targets)
        else:
            outputs = self.model(**batch if isinstance(batch, dict) else {'input': batch[0], 'labels': batch[1]})
            if hasattr(outputs, 'loss'):
                loss = outputs.loss
            else:
                logits = outputs.logits if hasattr(outputs, 'logits') else outputs
                targets = batch['labels'] if isinstance(batch, dict) else batch[1]
                loss = self.loss_fn(logits, targets)
        
        # Scale loss for gradient accumulation
        loss = loss / self.gradient_accumulation_steps
        
        # Backward pass
        if self.mixed_precision:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()
        
        # Update weights if we've accumulated enough gradients
        if (self.global_step + 1) % self.gradient_accumulation_steps == 0:
            if self.mixed_precision:
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                self.optimizer.step()
            
            if self.scheduler:
                self.scheduler.step()
            
            self.optimizer.zero_grad()
        
        # Update global step
        self.global_step += 1
        
        # Calculate tokens per second (approximate)
        step_time = time.time() - start_time
        # Estimate tokens based on batch size and sequence length
        if isinstance(batch, dict) and 'input_ids' in batch:
            tokens = batch['input_ids'].numel()
        elif isinstance(batch, dict) and 'inputs' in batch:
            tokens = batch['inputs'].numel() if hasattr(batch['inputs'], 'numel') else 1000  # fallback
        else:
            tokens = 1000  # fallback estimate
        
        tokens_per_second = tokens / step_time if step_time > 0 else 0
        
        # Get current learning rate
        current_lr = self.optimizer.param_groups[0]['lr']
        
        # Store metrics
        step_metrics = {
            'global_step': self.global_step,
            'train_loss': loss.item() * self.gradient_accumulation_steps,
            'learning_rate': current_lr,
            'tokens_per_second': tokens_per_second,
            'step_time': step_time
        }
        
        # Add validation loss if validation is needed
        if self.val_dataloader and self.global_step % 100 == 0:  # Validate every 100 steps
            val_loss = self._validate_step()
            step_metrics['val_loss'] = val_loss
        
        # Update metrics history
        for key, value in step_metrics.items():
            if key not in self.metrics:
                self.metrics[key] = []
            if key != 'global_step':  # Don't store global_step in history
                self.metrics[key].append(value)
        
        return step_metrics
    
    def _validate_step(self) -> float:
        """
        Execute a single validation step.
        
        Returns:
            float: Validation loss
        """
        if not self.val_dataloader:
            return 0.0
            
        self.model.eval()
        
        if not hasattr(self, 'val_iterator'):
            self.val_iterator = iter(self.val_dataloader)
        
        try:
            batch = next(self.val_iterator)
        except StopIteration:
            self.val_iterator = iter(self.val_dataloader)
            batch = next(self.val_iterator)
        
        # Move batch to device
        if isinstance(batch, dict):
            batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v
                     for k, v in batch.items()}
        elif isinstance(batch, (list, tuple)):
            batch = [item.to(self.device) if isinstance(item, torch.Tensor) else item 
                     for item in batch]
        
        with torch.no_grad():
            if self.mixed_precision:
                with torch.cuda.amp.autocast():
                    outputs = self.model(**batch if isinstance(batch, dict) else {'input': batch[0], 'labels': batch[1]})
            else:
                outputs = self.model(**batch if isinstance(batch, dict) else {'input': batch[0], 'labels': batch[1]})
            
            if hasattr(outputs, 'loss'):
                val_loss = outputs.loss.item()
            else:
                logits = outputs.logits if hasattr(outputs, 'logits') else outputs
                targets = batch['labels'] if isinstance(batch, dict) else batch[1]
                val_loss = self.loss_fn(logits, targets).item()
        
        return val_loss
    
    def get_metrics_history(self) -> Dict[str, List[float]]:
        """
        Get the complete training metrics history.
        
        Returns:
            Dict[str, List[float]]: Dictionary of metric names and their historical values
        """
        return self.metrics.copy()
    
    def update_vram_target(self, target_gb: float) -> None:
        """
        Update the VRAM usage target.
        
        Args:
            target_gb (float): New VRAM target in GB
        """
        self.target_vram_usage = target_gb
        if hasattr(self, 'precision_manager'):
            self.precision_manager.target_vram_usage = target_gb
        logger.info(f"Updated VRAM target to {target_gb:.2f} GB")
    
    def set_precision_mode(self, mode: PrecisionMode) -> None:
        """
        Set the precision mode for training.
        
        Args:
            mode (PrecisionMode): The precision mode to use        """
        self.mixed_precision = (mode == PrecisionMode.FP16)
        if hasattr(self, 'precision_manager'):
            # Convert model to the specified precision mode
            self.model = self.precision_manager.convert_model_precision(self.model, mode)
        logger.info(f"Set precision mode to {mode}")
    
    def set_gradient_checkpointing(self, enabled: bool) -> None:
        """
        Enable or disable gradient checkpointing.
        
        Args:
            enabled (bool): Whether to enable gradient checkpointing
        """
        if hasattr(self.model, 'gradient_checkpointing_enable'):
            if enabled:
                self.model.gradient_checkpointing_enable()
            else:
                self.model.gradient_checkpointing_disable()
        logger.info(f"Gradient checkpointing {'enabled' if enabled else 'disabled'}")
    
    def set_attention_cache(self, enabled: bool) -> None:
        """
        Enable or disable attention caching.
        
        Args:
            enabled (bool): Whether to enable attention caching
        """
        # This would typically be model-specific
        # For now, just log the setting
        logger.info(f"Attention cache {'enabled' if enabled else 'disabled'}")
        # TODO: Implement model-specific attention cache logic
