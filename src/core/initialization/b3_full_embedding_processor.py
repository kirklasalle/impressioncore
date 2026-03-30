#!/usr/bin/env python3
"""
**Created:** July 28, 2025
**Updated:** October 30, 2025
**Author:** Kirk LaSalle
**Tags:** #attention_mechanism #command_line #cuda #memory_management #multimodal #python #source_code #src/core/initialization/b3_full_embedding_processor.py #tokenization #transformer #web_interface
**Category:** Core Implementation
**Status:** Active
"""




import asyncio
import gc
import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Core imports
import torch
import torch.nn.functional as F
import torchaudio
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, CLIPModel, CLIPProcessor

# Import B3 architecture
from src.core.models.impressioncore_b3_architecture import (
    B3Config,
    ImpressionCoreB3Model,
    sacred_covenant_check,
    validate_environment,
)

# Rich enhancements with fallback
try:
    from src.core.utils.rich_enhancements import get_rich_logger, rich_print
    from src.core.utils.rich_status_animation import StatusAnimation
except ImportError:
    def get_rich_logger(name):
        import logging
        return logging.getLogger(name)

    def rich_print(*args, **kwargs):
        print(*args, **kwargs)

    class StatusAnimation:
        def __init__(self, message):
            self.message = message

        def __enter__(self):
            print(f"⏳ {self.message}")
            return self

        def __exit__(self, exc_type, exc, exc_tb):
            if exc_type is None:
                print("✅ Completed")
            else:
                print(f"❌ Failed: {exc}")

        def update(self, status):
            print(f"… {status}")


logger = get_rich_logger(__name__)


@dataclass
class EmbeddingProcessingStats:
    """Runtime statistics for embedding generation."""

    start_time: datetime
    current_phase: str = "Phase 1"
    total_files: int = 0
    files_processed: int = 0
    files_failed: int = 0
    embeddings_generated: int = 0
    processing_speed_fph: float = 0.0


class B3EmbeddingDataset(Dataset):
    """Dataset for B3 embedding processing."""

    def __init__(self, file_paths: list[Path], phase_config: dict[str, Any]):
        self.file_paths = file_paths
        self.phase_config = phase_config

        self.tokenizer: AutoTokenizer | None = None
        self.clip_model: CLIPModel | None = None
        self.clip_processor: CLIPProcessor | None = None
        self._init_processors()

    def __len__(self) -> int:
        return len(self.file_paths)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self._process_file(self.file_paths[index])

    def _init_processors(self) -> None:
        """Initialise text and image processors."""
        text_model_id = "microsoft/DialoGPT-small"
        local_text_path = Path("F:/models/teachers/dialogpt_small")
        tokenizer_kwargs = {"use_fast": True, "padding_side": "left"}

        try:
            if local_text_path.exists():
                logger.info("🔐 Loading DialoGPT-small tokenizer from local cache")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    str(local_text_path),
                    local_files_only=True,
                    **tokenizer_kwargs
                )
            else:
                logger.info("🌐 Loading DialoGPT-small tokenizer from Hugging Face")
                self.tokenizer = AutoTokenizer.from_pretrained(text_model_id, **tokenizer_kwargs)

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        except Exception as exc:
            logger.warning(f"⚠️  Failed to initialise tokenizer: {exc}")
            self.tokenizer = None

        clip_model_id = "openai/clip-vit-base-patch32"
        clip_local_path = Path("F:/models/base/clip-vit-base-patch32")

        try:
            if clip_local_path.exists():
                logger.info("🔐 Loading CLIP processor from local cache")
                self.clip_model = CLIPModel.from_pretrained(
                    str(clip_local_path),
                    local_files_only=True
                )
                self.clip_processor = CLIPProcessor.from_pretrained(
                    str(clip_local_path),
                    local_files_only=True
                )
            else:
                logger.info("🌐 Loading CLIP processor from Hugging Face (binary weights)")
                self.clip_model = CLIPModel.from_pretrained(clip_model_id)
                self.clip_processor = CLIPProcessor.from_pretrained(clip_model_id)
        except Exception as exc:
            logger.warning(f"⚠️  CLIP unavailable; image processing disabled: {exc}")
            self.clip_model = None
            self.clip_processor = None

    def _process_file(self, file_path: Path) -> dict[str, Any]:
        suffix = file_path.suffix.lower()
        if suffix in {".txt", ".md", ".csv", ".json", ".html", ".xml"}:
            return self._process_text_file(file_path)
        if suffix in {".png", ".jpg", ".jpeg", ".bmp", ".gif"}:
            return self._process_image_file(file_path)
        if suffix in {".wav", ".mp3", ".flac", ".ogg"}:
            return self._process_audio_file(file_path)
        if suffix in {".npy", ".npz"}:
            return self._process_embedding_file(file_path)
        return self._process_unknown_file(file_path)

    def _process_text_file(self, file_path: Path) -> dict[str, Any]:
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as handle:
                text = handle.read()

            if not text.strip():
                raise ValueError("empty text file")

            if self.tokenizer is None:
                raise RuntimeError("tokenizer not initialised")

            encoded = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            )

            return {
                "file_path": str(file_path),
                "modality": "text",
                "input_ids": encoded["input_ids"].squeeze(0),
                "attention_mask": encoded["attention_mask"].squeeze(0),
                "token_count": int(encoded["input_ids"].shape[-1])
            }
        except Exception as exc:
            logger.warning(f"⚠️  Text processing failed for {file_path}: {exc}")
            return {
                "file_path": str(file_path),
                "modality": "text",
                "embedding": torch.zeros(768),
                "error": str(exc)
            }

    def _process_image_file(self, file_path: Path) -> dict[str, Any]:
        try:
            image = Image.open(file_path).convert("RGB")

            if self.clip_processor and self.clip_model:
                inputs = self.clip_processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    image_features = self.clip_model.get_image_features(**inputs)

                image_features = image_features.squeeze(0)

                feature_dim = image_features.shape[-1]
                target_dim = 768
                if feature_dim < target_dim:
                    pad_width = target_dim - feature_dim
                    padding = torch.zeros(pad_width, dtype=image_features.dtype)
                    image_features = torch.cat([image_features, padding], dim=-1)
                elif feature_dim > target_dim:
                    image_features = image_features[..., :target_dim]

                return {
                    "file_path": str(file_path),
                    "modality": "image",
                    "image_features": image_features,
                    "image_size": image.size
                }

            return {
                "file_path": str(file_path),
                "modality": "image",
                "embedding": torch.randn(768),
                "image_size": image.size,
                "warning": "CLIP unavailable, using random embedding"
            }
        except Exception as exc:
            logger.warning(f"⚠️  Image processing failed for {file_path}: {exc}")
            return {
                "file_path": str(file_path),
                "modality": "image",
                "embedding": torch.zeros(768),
                "error": str(exc)
            }

    def _process_audio_file(self, file_path: Path) -> dict[str, Any]:
        try:
            waveform, sample_rate = torchaudio.load(str(file_path))

            if waveform.dim() == 2 and waveform.size(0) > 1:
                waveform = waveform.mean(dim=0, keepdim=True)

            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)

            mfcc_transform = torchaudio.transforms.MFCC(
                sample_rate=16000,
                n_mfcc=13,
                melkwargs={
                    "n_fft": 400,
                    "hop_length": 160,
                    "n_mels": 23,
                    "center": False
                }
            )
            mfcc = mfcc_transform(waveform)

            if mfcc.shape[-1] > 100:
                mfcc = mfcc[:, :, :100]
            else:
                pad_size = 100 - mfcc.shape[-1]
                mfcc = F.pad(mfcc, (0, pad_size))

            # Reshape MFCC output to (batch, time, features) and pad to audio_embed_dim
            mfcc = mfcc.squeeze(0).transpose(0, 1).unsqueeze(0).contiguous()

            feature_dim = mfcc.shape[-1]
            if feature_dim < 768:
                pad_width = 768 - feature_dim
                padding = torch.zeros((mfcc.size(0), mfcc.size(1), pad_width), dtype=mfcc.dtype)
                mfcc = torch.cat([mfcc, padding], dim=-1)
            elif feature_dim > 768:
                mfcc = mfcc[..., :768]

            return {
                "file_path": str(file_path),
                "modality": "audio",
                "audio_features": mfcc,
                "sample_rate": 16000,
                "duration": waveform.shape[-1] / 16000,
                "sequence_length": mfcc.shape[1]
            }
        except Exception as exc:
            logger.warning(f"⚠️  Audio processing failed for {file_path}: {exc}")
            return {
                "file_path": str(file_path),
                "modality": "audio",
                "embedding": torch.zeros(768),
                "error": str(exc)
            }

    def _process_embedding_file(self, file_path: Path) -> dict[str, Any]:
        try:
            if file_path.suffix == ".npy":
                embedding = np.load(file_path)
            else:
                data = np.load(file_path)
                first_key = next(iter(data.files))
                embedding = data[first_key]

            if embedding.ndim > 1:
                embedding = embedding.flatten()
            embedding = embedding.astype(np.float32)

            if embedding.size > 768:
                embedding = embedding[:768]
            elif embedding.size < 768:
                padding = np.zeros(768 - embedding.size, dtype=np.float32)
                embedding = np.concatenate([embedding, padding])

            return {
                "file_path": str(file_path),
                "modality": "embedding",
                "embedding": torch.from_numpy(embedding),
                "original_shape": str(embedding.shape)
            }
        except Exception as exc:
            logger.warning(f"⚠️  Embedding load failed for {file_path}: {exc}")
            return {
                "file_path": str(file_path),
                "modality": "embedding",
                "embedding": torch.zeros(768),
                "error": str(exc)
            }

    def _process_unknown_file(self, file_path: Path) -> dict[str, Any]:
        size = file_path.stat().st_size if file_path.exists() else 0
        return {
            "file_path": str(file_path),
            "modality": "unknown",
            "embedding": torch.randn(768) * 0.1,
            "file_size": size
        }


class B3EmbeddingProcessor:
    """Main B3 embedding processor."""

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path
        self.stats = EmbeddingProcessingStats(start_time=datetime.now())

        # Initialize B3 model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.config = None

        # Processing parameters
        self.batch_size = 8  # Conservative for GTX 1050 Ti
        self.max_files_per_phase = None

        # Dataset root (resolved during validation)
        self.dataset_root: Path | None = None

        # Results storage
        self.processed_embeddings = []
        self.processing_log = []

        # Initialize system
        self._validate_system()
        self._initialize_model()

    @staticmethod
    def _collate_items(batch: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return batch as-is to avoid key mismatches during collation."""
        return batch

    @staticmethod
    def _extract_item_from_batch(batch: dict[str, Any], index: int) -> dict[str, Any]:
        """Extract a single item from a collated batch."""
        item: dict[str, Any] = {}
        for key, value in batch.items():
            if isinstance(value, list) or torch.is_tensor(value):
                item[key] = value[index]
            else:
                item[key] = value
        return item

    def _validate_system(self):
        """Validate system requirements."""
        logger.info("🔧 Validating B3 embedding system...")

        # Environment validation
        env_status = validate_environment()
        if env_status['cuda_available']:
            logger.info(f"✅ CUDA available: {env_status['device_name']}")
            logger.info(f"✅ VRAM: {env_status['vram_gb']:.1f}GB")
        else:
            logger.warning("⚠️  CUDA not available - using CPU")

        # F: drive check (support both legacy and current layouts)
        dataset_roots = [Path("F:/datasets"), Path("F:/data/datasets")]
        self.dataset_root = next((root for root in dataset_roots if root.exists()), None)
        if self.dataset_root:
            logger.info(f"✅ F: drive datasets accessible at {self.dataset_root}")
        else:
            logger.warning("⚠️  F: drive dataset roots not accessible")
            raise RuntimeError("F: drive datasets not found")

    def _initialize_model(self):
        """Initialize B3 model."""
        logger.info("🧠 Initializing ImpressionCore B3 model...")

        try:
            # Create B3 configuration
            config_dict = {
                'embed_dim': 768,
                'num_heads': 12,
                'num_layers': 6,  # Reduced for GTX 1050 Ti
                'vocab_size': 50257,
                'num_experts': 4,  # Reduced for memory efficiency
                'expert_dim': 1024,  # Reduced for memory efficiency
                'experts_per_token': 2,
                'image_embed_dim': 768,
                'audio_embed_dim': 768,
                'phoneme_vocab_size': 256,
                'dropout': 0.1,
                'use_gradient_checkpointing': True  # Enable for memory efficiency
            }

            self.config = B3Config(**config_dict)
            self.model = ImpressionCoreB3Model(self.config)
            self.model = self.model.to(self.device)

            # Enable evaluation mode for embedding extraction
            self.model.eval()

            logger.info("✅ B3 model initialized successfully")

            # Sacred covenant check
            sacred_covenant_check(self.model, self.config)

        except Exception as e:
            logger.error(f"❌ B3 model initialization failed: {e}")
            raise

    def get_priority_files(self, max_files: int = 10000) -> list[Path]:
        """Get priority files for Phase 1 processing."""
        logger.info(f"📋 Identifying {max_files} priority files for Phase 1...")

        dataset_path = self.dataset_root or Path("F:/datasets")
        priority_patterns = [
            "**/academic/**",
            "**/arxiv/**",
            "**/papers/**",
            "**/b3_professional/**",
            "**/embeddings/**",
            "**/processed/**",
            "**/educational/**",
            "**/*.pdf",
            "**/*academic*",
            "**/*research*",
            "**/*paper*"
        ]

        priority_files = []

        # Search for priority files
        for pattern in priority_patterns:
            matches = list(dataset_path.glob(pattern))
            priority_files.extend([f for f in matches if f.is_file()])

            if len(priority_files) >= max_files:
                break

        # Remove duplicates and limit
        seen = set()
        unique_files = []
        for f in priority_files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)

        result_files = unique_files[:max_files]

        logger.info(f"✅ Found {len(result_files)} priority files")

        # Log file distribution
        file_types = defaultdict(int)
        for f in result_files:
            file_types[f.suffix.lower()] += 1

        logger.info("📊 Priority file distribution:")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {ext or 'no_ext'}: {count} files")

        return result_files

    async def process_batch(self, batch_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process a batch of files through B3 model."""
        try:
            batch_results = []

            with torch.no_grad():
                for item in batch_data:
                    try:
                        # Extract embeddings based on modality
                        if item['modality'] == 'text' and 'input_ids' in item:
                            # Process text through B3
                            input_ids = item['input_ids'].unsqueeze(0).to(self.device)
                            outputs = self.model(input_ids=input_ids)
                            embedding = outputs['logits'].mean(dim=1).squeeze(0).cpu()

                        elif item['modality'] == 'image' and 'image_features' in item:
                            # Process image through B3
                            image_features = item['image_features'].unsqueeze(0).to(self.device)
                            outputs = self.model(image_features=image_features)
                            embedding = outputs['logits'].mean(dim=1).squeeze(0).cpu()

                        elif item['modality'] == 'audio' and 'audio_features' in item:
                            # Process audio through B3; ensure batch dimension is present
                            audio_features = item['audio_features']
                            if audio_features.dim() == 2:
                                audio_features = audio_features.unsqueeze(0)
                            audio_features = audio_features.to(self.device)
                            outputs = self.model(audio_features=audio_features)
                            embedding = outputs['logits'].mean(dim=1).squeeze(0).cpu()

                        elif 'embedding' in item:
                            # Use existing embedding
                            embedding = item['embedding']

                        else:
                            # Fallback
                            embedding = torch.zeros(self.config.vocab_size)

                        # Store result
                        result = {
                            'file_path': item['file_path'],
                            'modality': item['modality'],
                            'embedding': embedding.numpy() if torch.is_tensor(embedding) else embedding,
                            'embedding_shape': embedding.shape if torch.is_tensor(embedding) else len(embedding),
                            'quality_score': getattr(outputs, 'quality_score', torch.tensor([0.0])).item() if 'outputs' in locals() else 0.0,
                            'processing_time': time.time()
                        }

                        batch_results.append(result)
                        self.stats.embeddings_generated += 1

                    except Exception as e:
                        logger.warning(f"⚠️  Batch item processing failed: {e}")
                        batch_results.append({
                            'file_path': item.get('file_path', 'unknown'),
                            'modality': item.get('modality', 'failed'),
                            'embedding': np.zeros(self.config.vocab_size),
                            'error': str(e)
                        })
                        self.stats.files_failed += 1

            return batch_results

        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            return []

    def save_embeddings(self, embeddings: list[dict[str, Any]], phase_name: str):
        """Save generated embeddings to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save to F: drive if available, otherwise local
        save_paths = [
            Path(f"F:/ImpressionCore/embeddings/b3_generated/{phase_name}_{timestamp}.npz"),
            Path(f"src/data/embeddings/{phase_name}_{timestamp}.npz")
        ]

        for save_path in save_paths:
            try:
                save_path.parent.mkdir(parents=True, exist_ok=True)

                # Prepare data for saving
                embedding_data = {}
                metadata = {}

                for i, emb_data in enumerate(embeddings):
                    embedding_data[f"embedding_{i}"] = emb_data['embedding']
                    metadata[f"metadata_{i}"] = {
                        'file_path': emb_data['file_path'],
                        'modality': emb_data['modality'],
                        'embedding_shape': emb_data.get('embedding_shape', 'unknown'),
                        'quality_score': emb_data.get('quality_score', 0.0)
                    }

                # Save embeddings
                np.savez_compressed(save_path, **embedding_data)

                # Save metadata
                metadata_path = save_path.with_suffix('.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2, default=str)

                logger.info(f"💾 Embeddings saved to: {save_path}")
                return save_path

            except Exception as e:
                logger.warning(f"⚠️  Failed to save to {save_path}: {e}")
                continue

        logger.error("❌ Failed to save embeddings to any location")
        return None

    async def execute_phase_1(self) -> bool:
        """Execute Phase 1: Priority Categories (10K files)."""
        logger.info("🚀 Starting Phase 1: Priority Categories")
        self.stats.current_phase = "Phase 1"

        try:
            # Get priority files
            priority_files = self.get_priority_files(max_files=10000)
            self.stats.total_files = len(priority_files)

            if not priority_files:
                logger.error("❌ No priority files found for Phase 1")
                return False

            # Create dataset
            dataset = B3EmbeddingDataset(priority_files, {'phase': 'priority'})
            dataloader = DataLoader(
                dataset,
                batch_size=self.batch_size,
                shuffle=False,
                num_workers=0,  # Single-threaded for stability
                collate_fn=self._collate_items
            )

            # Process batches
            all_embeddings = []
            batch_count = 0
            start_time = time.time()

            with StatusAnimation("Processing Priority Files"):
                for batch in dataloader:
                    batch_count += 1

                    # Process batch directly; custom collate keeps items as list
                    batch_results = await self.process_batch(batch)
                    all_embeddings.extend(batch_results)

                    # Update statistics
                    self.stats.files_processed += len(batch_results)
                    elapsed_time = time.time() - start_time
                    self.stats.processing_speed_fph = self.stats.files_processed / (elapsed_time / 3600)

                    # Memory management
                    if batch_count % 10 == 0:
                        torch.cuda.empty_cache() if torch.cuda.is_available() else None
                        gc.collect()

                        # Progress update
                        progress = (self.stats.files_processed / self.stats.total_files) * 100
                        logger.info(f"📊 Phase 1 Progress: {progress:.1f}% ({self.stats.files_processed}/{self.stats.total_files})")
                        logger.info(f"⚡ Speed: {self.stats.processing_speed_fph:.1f} files/hour")

            # Save Phase 1 results
            save_path = self.save_embeddings(all_embeddings, "phase1_priority")

            # Log completion
            total_time = time.time() - start_time
            logger.info("🎉 Phase 1 Complete!")
            logger.info(f"✅ Files Processed: {self.stats.files_processed}")
            logger.info(f"✅ Files Failed: {self.stats.files_failed}")
            logger.info(f"✅ Embeddings Generated: {self.stats.embeddings_generated}")
            logger.info(f"✅ Total Time: {total_time/3600:.2f} hours")
            logger.info(f"✅ Final Speed: {self.stats.processing_speed_fph:.1f} files/hour")

            if save_path:
                logger.info(f"💾 Results saved to: {save_path}")

            return True

        except Exception as e:
            logger.error(f"❌ Phase 1 execution failed: {e}")
            return False

    async def process_file_list(self, file_paths: list[Path], phase_name: str = "custom_phase",
                                status_message: str = "Processing manifest files") -> bool:
        """Process an explicit list of file paths through the embedding pipeline."""
        normalized_paths = [Path(p) for p in file_paths]
        existing_paths = [p for p in normalized_paths if p.exists()]

        if not existing_paths:
            logger.error("❌ Manifest file list is empty or all paths are missing")
            return False

        self.stats = EmbeddingProcessingStats(start_time=datetime.now(), current_phase=phase_name)
        self.stats.total_files = len(existing_paths)

        dataset = B3EmbeddingDataset(existing_paths, {'phase': phase_name})
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=0,
            collate_fn=self._collate_items
        )

        all_embeddings: list[dict[str, Any]] = []
        batch_count = 0
        start_time = time.time()

        with StatusAnimation(status_message):
            for batch in dataloader:
                batch_count += 1

                batch_results = await self.process_batch(batch)
                all_embeddings.extend(batch_results)

                self.stats.files_processed += len(batch_results)
                elapsed_time = max(time.time() - start_time, 1.0)
                self.stats.processing_speed_fph = self.stats.files_processed / (elapsed_time / 3600)

                if batch_count % 10 == 0:
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    gc.collect()

                    progress = (self.stats.files_processed / self.stats.total_files) * 100
                    logger.info(f"📊 {phase_name} Progress: {progress:.1f}% ({self.stats.files_processed}/{self.stats.total_files})")
                    logger.info(f"⚡ Speed: {self.stats.processing_speed_fph:.1f} files/hour")

        save_path = self.save_embeddings(all_embeddings, phase_name)

        total_time = time.time() - start_time
        logger.info(f"🎉 {phase_name} Complete!")
        logger.info(f"✅ Files Processed: {self.stats.files_processed}")
        logger.info(f"✅ Files Failed: {self.stats.files_failed}")
        logger.info(f"✅ Embeddings Generated: {self.stats.embeddings_generated}")
        logger.info(f"✅ Total Time: {total_time/3600:.2f} hours")
        logger.info(f"✅ Final Speed: {self.stats.processing_speed_fph:.1f} files/hour")

        if save_path:
            logger.info(f"💾 Results saved to: {save_path}")

        return True

async def main():
    """Main execution function."""
    logger.info("🧠 ImpressionCore B3 Full Embedding Processor")
    logger.info("=" * 60)
    logger.info("📁 Target: F:\\datasets (1,138,398 files)")
    logger.info("🎯 Phase 1: Priority Categories (10,000 files)")
    logger.info("💻 Hardware: GTX 1050 Ti Optimized")
    logger.info("🚀 Architecture: Revolutionary B3 Multimodal")
    logger.info("=" * 60)

    try:
        # Initialize processor
        processor = B3EmbeddingProcessor()

        # Execute Phase 1
        success = await processor.execute_phase_1()

        if success:
            logger.info("🎊 Phase 1 COMPLETED SUCCESSFULLY!")
            logger.info("🚀 Ready for Phase 2: Core Multimodal (50K files)")
            return True
        else:
            logger.error("❌ Phase 1 failed")
            return False

    except Exception as e:
        logger.error(f"❌ Full embedding process failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
