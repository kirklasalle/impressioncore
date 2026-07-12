#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** July-28-2025
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #cuda #memory_management #multimodal #python #source_code #src/core/initialization/b3_full_embedding_strategy.py #web_interface
**Category:** Core Implementation
**Status:** Active
"""




import asyncio
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.core.models.impressioncore_b3_architecture import (
    B3Config,
    ImpressionCoreB3Model,
    extract_audio_embedding,
    extract_image_embedding,
    extract_text_embedding,
    extract_video_embedding,
    validate_environment,
)
from src.core.utils.rich_enhancements import get_rich_logger

logger = get_rich_logger(__name__)

@dataclass
class B3EmbeddingStrategy:
    """Comprehensive B3 Full Embedding Strategy Configuration"""

    # Dataset Information
    total_files: int = 1138399
    dataset_path: str = "F:/datasets"
    output_path: str = "F:/ImpressionCore/embeddings"

    # Processing Configuration
    batch_size: int = 32
    max_workers: int = 4
    memory_limit_gb: float = 3.5  # GTX 1050 Ti constraint

    # Modality Distribution Estimates
    text_files: int = 150000      # Academic papers, code, structured data
    image_files: int = 800000     # Images, facial recognition, satellite, medical
    audio_files: int = 100000     # LibriSpeech, speech data
    video_files: int = 50000      # Kinetics400, multimodal video
    other_files: int = 38399      # 3D models, metadata, configs

    # Processing Priorities
    priority_categories: list[str] = None

    def __post_init__(self):
        if self.priority_categories is None:
            self.priority_categories = [
                "academic",           # High-quality text embeddings
                "images/vision",      # Core visual processing
                "LibriSpeech",        # Clean audio data
                "multimodal",         # Cross-modal learning
                "b3_professional_dataset",  # B3-specific data
                "embeddings",         # Pre-computed embeddings
                "scientific_data",    # Research-quality data
                "educational",        # Learning materials
                "structured",         # Well-organized data
                "processed"           # Pre-processed data
            ]

@dataclass
class EmbeddingPipeline:
    """Full B3 Embedding Processing Pipeline"""

    strategy: B3EmbeddingStrategy
    model: ImpressionCoreB3Model = None
    config: B3Config = None

    def __post_init__(self):
        """Initialize B3 model and configuration"""
        if self.config is None:
            self.config = B3Config(
                embed_dim=768,
                num_heads=12,
                num_layers=8,
                vocab_size=50257,
                num_experts=8,
                expert_dim=2048,
                experts_per_token=2,
                image_embed_dim=768,
                audio_embed_dim=768,
                phoneme_vocab_size=256,
                dropout=0.1,
                use_gradient_checkpointing=True,
                use_mixed_precision=True
            )

        if self.model is None:
            self.model = ImpressionCoreB3Model(self.config)

    async def scan_dataset_structure(self) -> dict[str, list[Path]]:
        """Comprehensive dataset structure analysis"""
        logger.info("🔍 Analyzing F:/datasets structure...")

        structure = {
            "text": [],
            "image": [],
            "audio": [],
            "video": [],
            "embeddings": [],
            "metadata": [],
            "other": []
        }

        text_extensions = {'.txt', '.md', '.json', '.py', '.js', '.html', '.xml', '.csv'}
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
        audio_extensions = {'.wav', '.mp3', '.flac', '.m4a', '.ogg'}
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        embedding_extensions = {'.npy', '.npz', '.pkl', '.pt', '.pth'}

        dataset_path = Path(self.strategy.dataset_path)

        for file_path in dataset_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()

                if ext in text_extensions:
                    structure["text"].append(file_path)
                elif ext in image_extensions:
                    structure["image"].append(file_path)
                elif ext in audio_extensions:
                    structure["audio"].append(file_path)
                elif ext in video_extensions:
                    structure["video"].append(file_path)
                elif ext in embedding_extensions:
                    structure["embeddings"].append(file_path)
                elif ext in {'.json', '.yaml', '.yml', '.xml'}:
                    structure["metadata"].append(file_path)
                else:
                    structure["other"].append(file_path)

        logger.info("📊 Dataset Structure Analysis Complete:")
        for modality, files in structure.items():
            logger.info(f"   {modality.title()}: {len(files):,} files")

        return structure

    async def create_processing_plan(self, structure: dict[str, list[Path]]) -> dict[str, Any]:
        """Create optimized processing plan based on priorities and constraints"""
        logger.info("📋 Creating B3 Full Embedding Processing Plan...")

        # Calculate processing order based on priorities
        processing_phases = []

        # Phase 1: High-Priority Categories
        phase1_files = []
        for category in self.strategy.priority_categories[:5]:  # Top 5 priorities
            for modality, files in structure.items():
                if modality != "embeddings":  # Skip existing embeddings
                    category_files = [f for f in files if category.lower() in str(f).lower()]
                    phase1_files.extend(category_files[:1000])  # Limit per category

        # Phase 2: Remaining High-Quality Data
        phase2_files = []
        for modality in ["text", "image", "audio"]:
            remaining_files = [f for f in structure[modality] if f not in phase1_files]
            phase2_files.extend(remaining_files[:5000])  # 5k per modality

        # Phase 3: Video and Complex Multimodal
        phase3_files = structure["video"][:2000]  # Video is memory-intensive

        # Phase 4: Everything Else
        phase4_files = []
        all_processed = set(phase1_files + phase2_files + phase3_files)
        for modality, files in structure.items():
            if modality != "embeddings":
                remaining = [f for f in files if f not in all_processed]
                phase4_files.extend(remaining)

        processing_phases = [
            {"name": "Phase 1: Priority Categories", "files": phase1_files},
            {"name": "Phase 2: Core Multimodal Data", "files": phase2_files},
            {"name": "Phase 3: Video & Complex Data", "files": phase3_files},
            {"name": "Phase 4: Comprehensive Coverage", "files": phase4_files}
        ]

        # Calculate timing estimates
        total_files = sum(len(phase["files"]) for phase in processing_phases)
        estimated_time_hours = total_files / (self.strategy.batch_size * 60)  # Rough estimate

        plan = {
            "total_files": total_files,
            "estimated_time_hours": estimated_time_hours,
            "phases": processing_phases,
            "memory_strategy": "GTX 1050 Ti Optimized",
            "batch_size": self.strategy.batch_size,
            "max_workers": self.strategy.max_workers
        }

        logger.info("📈 Processing Plan Created:")
        logger.info(f"   Total Files: {total_files:,}")
        logger.info(f"   Estimated Time: {estimated_time_hours:.1f} hours")
        logger.info(f"   Processing Phases: {len(processing_phases)}")

        return plan

    async def process_embedding_batch(self, files: list[Path], batch_id: int) -> dict[str, Any]:
        """Process a batch of files for embedding extraction"""
        logger.info(f"🔄 Processing Batch {batch_id}: {len(files)} files")

        batch_results = {
            "batch_id": batch_id,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "embeddings_generated": 0,
            "total_size_mb": 0
        }

        for file_path in files:
            try:
                # Determine file type and extract appropriate embedding
                ext = file_path.suffix.lower()
                embedding = None

                if ext in {'.txt', '.md', '.json', '.py', '.js', '.html'}:
                    embedding = await self.extract_text_embedding_async(file_path)
                elif ext in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}:
                    embedding = await self.extract_image_embedding_async(file_path)
                elif ext in {'.wav', '.mp3', '.flac', '.m4a'}:
                    embedding = await self.extract_audio_embedding_async(file_path)
                elif ext in {'.mp4', '.avi', '.mov', '.mkv'}:
                    embedding = await self.extract_video_embedding_async(file_path)

                if embedding is not None:
                    # Save embedding
                    embedding_path = self.get_embedding_path(file_path)
                    await self.save_embedding_async(embedding, embedding_path)

                    batch_results["embeddings_generated"] += 1
                    batch_results["successful"] += 1
                else:
                    batch_results["failed"] += 1

                batch_results["processed"] += 1

            except Exception as e:
                logger.error(f"❌ Error processing {file_path}: {e}")
                batch_results["failed"] += 1
                batch_results["processed"] += 1

        return batch_results

    async def extract_text_embedding_async(self, file_path: Path):
        """Async text embedding extraction"""
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()[:10000]  # Limit content size
            return await extract_text_embedding(content, self.model)
        except Exception as e:
            logger.error(f"Text embedding error for {file_path}: {e}")
            return None

    async def extract_image_embedding_async(self, file_path: Path):
        """Async image embedding extraction"""
        try:
            return await extract_image_embedding(str(file_path), self.model)
        except Exception as e:
            logger.error(f"Image embedding error for {file_path}: {e}")
            return None

    async def extract_audio_embedding_async(self, file_path: Path):
        """Async audio embedding extraction"""
        try:
            return await extract_audio_embedding(str(file_path), self.model)
        except Exception as e:
            logger.error(f"Audio embedding error for {file_path}: {e}")
            return None

    async def extract_video_embedding_async(self, file_path: Path):
        """Async video embedding extraction"""
        try:
            return await extract_video_embedding(str(file_path), self.model)
        except Exception as e:
            logger.error(f"Video embedding error for {file_path}: {e}")
            return None

    def get_embedding_path(self, file_path: Path) -> Path:
        """Generate appropriate embedding storage path"""
        relative_path = file_path.relative_to(self.strategy.dataset_path)
        embedding_path = Path(self.strategy.output_path) / relative_path.with_suffix('.emb.npy')
        embedding_path.parent.mkdir(parents=True, exist_ok=True)
        return embedding_path

    async def save_embedding_async(self, embedding, embedding_path: Path):
        """Async embedding saving"""
        import numpy as np
        np.save(embedding_path, embedding)

    async def execute_full_embedding_plan(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Execute the complete B3 full embedding strategy"""
        logger.info("🚀 Executing ImpressionCore B3 Full Embedding Plan...")

        total_results = {
            "start_time": datetime.now().isoformat(),
            "phases_completed": 0,
            "total_processed": 0,
            "total_successful": 0,
            "total_failed": 0,
            "total_embeddings": 0,
            "total_size_mb": 0,
            "phase_results": []
        }

        for _phase_idx, phase in enumerate(plan["phases"]):
            logger.info(f"🔄 Starting {phase['name']}: {len(phase['files'])} files")

            phase_start = datetime.now()
            phase_results = {
                "phase_name": phase["name"],
                "start_time": phase_start.isoformat(),
                "batches_processed": 0,
                "files_processed": 0,
                "successful": 0,
                "failed": 0,
                "embeddings_generated": 0
            }

            # Process phase in batches
            files = phase["files"]
            batch_size = self.strategy.batch_size

            for i in range(0, len(files), batch_size):
                batch_files = files[i:i + batch_size]
                batch_id = i // batch_size + 1

                batch_results = await self.process_embedding_batch(batch_files, batch_id)

                # Update phase results
                phase_results["batches_processed"] += 1
                phase_results["files_processed"] += batch_results["processed"]
                phase_results["successful"] += batch_results["successful"]
                phase_results["failed"] += batch_results["failed"]
                phase_results["embeddings_generated"] += batch_results["embeddings_generated"]

                # Log progress
                if batch_id % 10 == 0:
                    logger.info(f"   Batch {batch_id}: {phase_results['files_processed']}/{len(files)} files")

            phase_end = datetime.now()
            phase_results["end_time"] = phase_end.isoformat()
            phase_results["duration_minutes"] = (phase_end - phase_start).total_seconds() / 60

            total_results["phase_results"].append(phase_results)
            total_results["phases_completed"] += 1
            total_results["total_processed"] += phase_results["files_processed"]
            total_results["total_successful"] += phase_results["successful"]
            total_results["total_failed"] += phase_results["failed"]
            total_results["total_embeddings"] += phase_results["embeddings_generated"]

            logger.info(f"✅ {phase['name']} Complete: {phase_results['embeddings_generated']} embeddings generated")

        total_results["end_time"] = datetime.now().isoformat()
        total_results["total_duration_hours"] = (
            datetime.fromisoformat(total_results["end_time"]) -
            datetime.fromisoformat(total_results["start_time"])
        ).total_seconds() / 3600

        # Save final results
        results_path = Path("src/memlog") / f"b3_full_embedding_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_path, 'w') as f:
            json.dump(total_results, f, indent=2)

        logger.info("🎉 B3 Full Embedding Complete!")
        logger.info(f"   Total Embeddings: {total_results['total_embeddings']:,}")
        logger.info(f"   Success Rate: {total_results['total_successful']/total_results['total_processed']*100:.1f}%")
        logger.info(f"   Duration: {total_results['total_duration_hours']:.1f} hours")
        logger.info(f"   Results saved: {results_path}")

        return total_results

async def main():
    """Main execution function for B3 Full Embedding Strategy"""
    try:
        # Initialize strategy and pipeline
        strategy = B3EmbeddingStrategy()
        pipeline = EmbeddingPipeline(strategy)

        logger.info("🧠 ImpressionCore B3 Full Embedding Strategy")
        logger.info("=" * 60)
        logger.info(f"📁 Dataset: {strategy.dataset_path}")
        logger.info(f"📊 Total Files: {strategy.total_files:,}")
        logger.info("🎯 Target: GTX 1050 Ti Optimized")
        logger.info(f"💾 Memory Limit: {strategy.memory_limit_gb:.1f}GB")
        logger.info("=" * 60)

        # Validate environment
        env_status = validate_environment()
        if not env_status.get('cuda_available', False):
            logger.warning("⚠️  CUDA not available - performance may be limited")

        # Execute full embedding pipeline
        structure = await pipeline.scan_dataset_structure()
        plan = await pipeline.create_processing_plan(structure)
        results = await pipeline.execute_full_embedding_plan(plan)

        return results

    except Exception as e:
        logger.error(f"❌ B3 Full Embedding Strategy failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
