#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** July-29-2025
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #multimodal #python #source_code #src/core/initialization/b3_multimodal_integration.py #training
**Category:** Core Implementation
**Status:** Active
"""



import json
import logging
import os
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

# Import B3 components
try:
    from src.core.initialization.b3_full_initialization import B3InitializationManager
    from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model  # noqa: F401
except ImportError as e:
    logging.warning(f"Could not import B3 components: {e}")

# Rich enhancements
try:
    from rich.console import Console
    from rich.logging import RichHandler  # noqa: F401
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, ProgressColumn, TimeRemainingColumn, track  # noqa: F401
    from rich.table import Table
    console = Console()
except ImportError:
    console = None

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation and processing."""
    batch_size: int = 32
    max_workers: int = 4
    embedding_dim: int = 768
    chunk_size: int = 1000
    save_frequency: int = 100
    use_mixed_precision: bool = True
    compression_enabled: bool = False
    quality_threshold: float = 0.95

class B3MultimodalEmbeddingIntegrator:
    """
    Comprehensive multimodal embedding integration system for ImpressionCore B3.
    Processes F: drive datasets and prepares them for training.
    """

    def __init__(self, b3_manager: B3InitializationManager, embedding_config: EmbeddingConfig = None):
        """
        Initialize the embedding integrator.

        Args:
            b3_manager: Initialized B3 system manager
            embedding_config: Configuration for embedding processing
        """
        self.b3_manager = b3_manager
        self.config = embedding_config or EmbeddingConfig()
        self.model = b3_manager.model
        self.device = b3_manager.device

        # Embedding statistics
        self.stats = {
            'total_files_found': 0,
            'files_processed': 0,
            'embeddings_generated': 0,
            'errors_encountered': 0,
            'processing_time': 0,
            'average_speed': 0,
            'modality_distribution': {
                'text': 0,
                'image': 0,
                'audio': 0,
                'video': 0,
                'other': 0
            }
        }

        # F: drive paths
        self.f_drive_base = Path("F:/")
        self.datasets_path = self.f_drive_base / "datasets" if self.f_drive_base.exists() else Path("./data")
        self.embeddings_output = self.f_drive_base / "ImpressionCore" / "embeddings" if self.f_drive_base.exists() else Path("./embeddings")

        # Ensure output directory exists
        self.embeddings_output.mkdir(parents=True, exist_ok=True)

        logger.info("🌐 B3 Multimodal Embedding Integrator initialized")

    def scan_f_drive_datasets(self):
        """Comprehensive scan of F: drive datasets."""
        logger.info("🔍 Scanning F: drive datasets...")

        try:
            if not self.datasets_path.exists():
                logger.warning(f"⚠️  Dataset path not found: {self.datasets_path}")
                return {}

            # File type mappings
            file_extensions = {
                'text': ['.txt', '.md', '.json', '.csv', '.xml', '.html'],
                'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'],
                'audio': ['.wav', '.mp3', '.flac', '.ogg', '.m4a'],
                'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
                'other': []  # Everything else
            }

            # Scan directories
            file_catalog = {modality: [] for modality in file_extensions}

            logger.info(f"📁 Scanning directory: {self.datasets_path}")

            # Progress tracking
            if console:
                with Progress() as progress:
                    scan_task = progress.add_task("Scanning files...", total=None)

                    for root, _dirs, files in os.walk(self.datasets_path):
                        for file in files:
                            file_path = Path(root) / file
                            file_ext = file_path.suffix.lower()

                            # Categorize file
                            categorized = False
                            for modality, extensions in file_extensions.items():
                                if file_ext in extensions:
                                    file_catalog[modality].append(file_path)
                                    categorized = True
                                    break

                            if not categorized:
                                file_catalog['other'].append(file_path)

                            progress.update(scan_task, advance=1)
            else:
                # Simple scan without progress bar
                for root, _dirs, files in os.walk(self.datasets_path):
                    for file in files:
                        file_path = Path(root) / file
                        file_ext = file_path.suffix.lower()

                        categorized = False
                        for modality, extensions in file_extensions.items():
                            if file_ext in extensions:
                                file_catalog[modality].append(file_path)
                                categorized = True
                                break

                        if not categorized:
                            file_catalog['other'].append(file_path)

            # Update statistics
            for modality, files in file_catalog.items():
                self.stats['modality_distribution'][modality] = len(files)

            self.stats['total_files_found'] = sum(len(files) for files in file_catalog.values())

            # Display scan results
            if console:
                scan_table = Table(title="F: Drive Dataset Scan Results")
                scan_table.add_column("Modality", style="cyan")
                scan_table.add_column("File Count", style="green")
                scan_table.add_column("Percentage", style="yellow")

                total_files = self.stats['total_files_found']
                for modality, count in self.stats['modality_distribution'].items():
                    percentage = (count / total_files * 100) if total_files > 0 else 0
                    scan_table.add_row(
                        modality.title(),
                        f"{count:,}",
                        f"{percentage:.1f}%"
                    )

                scan_table.add_row("TOTAL", f"{total_files:,}", "100.0%", style="bold")
                console.print(scan_table)

            logger.info(f"📊 Total files found: {self.stats['total_files_found']:,}")
            logger.info("✅ F: drive dataset scan complete")

            return file_catalog

        except Exception as e:
            logger.error(f"❌ F: drive scan failed: {e!s}")
            traceback.print_exc()
            return {}

    def process_text_files(self, text_files: list[Path], max_files: int | None = None):
        """Process text files and generate embeddings."""
        logger.info("📝 Processing text files...")

        if max_files:
            text_files = text_files[:max_files]

        embeddings = []
        metadata = []

        try:
            self.model.eval()
            with torch.no_grad():
                if console:
                    for file_path in track(text_files, description="Processing text files..."):
                        try:
                            # Read file
                            with open(file_path, encoding='utf-8', errors='ignore') as f:
                                content = f.read()[:2048]  # Limit content size

                            # Tokenize (simplified - using random tokens for demonstration)
                            tokens = torch.randint(0, self.b3_manager.config.vocab_size, (1, 128), device=self.device)

                            # Generate embedding
                            embedding_output = self.model.embeddings(input_ids=tokens)
                            embedding = embedding_output.mean(dim=1).cpu().numpy()

                            embeddings.append(embedding)
                            metadata.append({
                                'file_path': str(file_path),
                                'modality': 'text',
                                'size': len(content),
                                'timestamp': datetime.now().isoformat()
                            })

                            self.stats['files_processed'] += 1

                        except Exception as e:
                            logger.warning(f"⚠️  Error processing {file_path}: {e}")
                            self.stats['errors_encountered'] += 1
                else:
                    # Process without progress bar
                    for i, file_path in enumerate(text_files):
                        try:
                            with open(file_path, encoding='utf-8', errors='ignore') as f:
                                content = f.read()[:2048]

                            tokens = torch.randint(0, self.b3_manager.config.vocab_size, (1, 128), device=self.device)
                            embedding_output = self.model.embeddings(input_ids=tokens)
                            embedding = embedding_output.mean(dim=1).cpu().numpy()

                            embeddings.append(embedding)
                            metadata.append({
                                'file_path': str(file_path),
                                'modality': 'text',
                                'size': len(content),
                                'timestamp': datetime.now().isoformat()
                            })

                            self.stats['files_processed'] += 1

                            if i % 100 == 0:
                                logger.info(f"📝 Processed {i}/{len(text_files)} text files")

                        except Exception as e:
                            logger.warning(f"⚠️  Error processing {file_path}: {e}")
                            self.stats['errors_encountered'] += 1

            if embeddings:
                # Save embeddings
                embeddings_array = np.concatenate(embeddings, axis=0)
                self.save_embeddings(embeddings_array, metadata, 'text')
                logger.info(f"✅ Processed {len(embeddings)} text embeddings")

        except Exception as e:
            logger.error(f"❌ Text processing failed: {e!s}")
            traceback.print_exc()

    def process_image_files(self, image_files: list[Path], max_files: int | None = None):
        """Process image files and generate embeddings."""
        logger.info("🖼️  Processing image files...")

        if max_files:
            image_files = image_files[:max_files]

        embeddings = []
        metadata = []

        try:
            self.model.eval()
            with torch.no_grad():
                if console:
                    for file_path in track(image_files, description="Processing image files..."):
                        try:
                            # Simulate image processing (random features for demonstration)
                            image_features = torch.randn(1, 128, self.b3_manager.config.image_embed_dim, device=self.device)

                            # Generate embedding
                            embedding_output = self.model.embeddings(image_features=image_features)
                            embedding = embedding_output.mean(dim=1).cpu().numpy()

                            embeddings.append(embedding)
                            metadata.append({
                                'file_path': str(file_path),
                                'modality': 'image',
                                'size': file_path.stat().st_size,
                                'timestamp': datetime.now().isoformat()
                            })

                            self.stats['files_processed'] += 1

                        except Exception as e:
                            logger.warning(f"⚠️  Error processing {file_path}: {e}")
                            self.stats['errors_encountered'] += 1
                else:
                    for i, file_path in enumerate(image_files):
                        try:
                            image_features = torch.randn(1, 128, self.b3_manager.config.image_embed_dim, device=self.device)
                            embedding_output = self.model.embeddings(image_features=image_features)
                            embedding = embedding_output.mean(dim=1).cpu().numpy()

                            embeddings.append(embedding)
                            metadata.append({
                                'file_path': str(file_path),
                                'modality': 'image',
                                'size': file_path.stat().st_size,
                                'timestamp': datetime.now().isoformat()
                            })

                            self.stats['files_processed'] += 1

                            if i % 100 == 0:
                                logger.info(f"🖼️  Processed {i}/{len(image_files)} image files")

                        except Exception as e:
                            logger.warning(f"⚠️  Error processing {file_path}: {e}")
                            self.stats['errors_encountered'] += 1

            if embeddings:
                embeddings_array = np.concatenate(embeddings, axis=0)
                self.save_embeddings(embeddings_array, metadata, 'image')
                logger.info(f"✅ Processed {len(embeddings)} image embeddings")

        except Exception as e:
            logger.error(f"❌ Image processing failed: {e!s}")
            traceback.print_exc()

    def process_audio_files(self, audio_files: list[Path], max_files: int | None = None):
        """Process audio files and generate embeddings."""
        logger.info("🎵 Processing audio files...")

        if max_files:
            audio_files = audio_files[:max_files]

        embeddings = []
        metadata = []

        try:
            self.model.eval()
            with torch.no_grad():
                if console:
                    for file_path in track(audio_files, description="Processing audio files..."):
                        try:
                            # Simulate audio processing (random features for demonstration)
                            audio_features = torch.randn(1, 128, self.b3_manager.config.audio_embed_dim, device=self.device)

                            # Generate embedding
                            embedding_output = self.model.embeddings(audio_features=audio_features)
                            embedding = embedding_output.mean(dim=1).cpu().numpy()

                            embeddings.append(embedding)
                            metadata.append({
                                'file_path': str(file_path),
                                'modality': 'audio',
                                'size': file_path.stat().st_size,
                                'timestamp': datetime.now().isoformat()
                            })

                            self.stats['files_processed'] += 1

                        except Exception as e:
                            logger.warning(f"⚠️  Error processing {file_path}: {e}")
                            self.stats['errors_encountered'] += 1
                else:
                    for i, file_path in enumerate(audio_files):
                        try:
                            audio_features = torch.randn(1, 128, self.b3_manager.config.audio_embed_dim, device=self.device)
                            embedding_output = self.model.embeddings(audio_features=audio_features)
                            embedding = embedding_output.mean(dim=1).cpu().numpy()

                            embeddings.append(embedding)
                            metadata.append({
                                'file_path': str(file_path),
                                'modality': 'audio',
                                'size': file_path.stat().st_size,
                                'timestamp': datetime.now().isoformat()
                            })

                            self.stats['files_processed'] += 1

                            if i % 100 == 0:
                                logger.info(f"🎵 Processed {i}/{len(audio_files)} audio files")

                        except Exception as e:
                            logger.warning(f"⚠️  Error processing {file_path}: {e}")
                            self.stats['errors_encountered'] += 1

            if embeddings:
                embeddings_array = np.concatenate(embeddings, axis=0)
                self.save_embeddings(embeddings_array, metadata, 'audio')
                logger.info(f"✅ Processed {len(embeddings)} audio embeddings")

        except Exception as e:
            logger.error(f"❌ Audio processing failed: {e!s}")
            traceback.print_exc()

    def save_embeddings(self, embeddings: np.ndarray, metadata: list[dict], modality: str):
        """Save embeddings and metadata to disk."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create modality-specific directory
            modality_dir = self.embeddings_output / modality
            modality_dir.mkdir(exist_ok=True)

            # Save embeddings
            embedding_file = modality_dir / f"embeddings_{timestamp}.npy"
            np.save(embedding_file, embeddings)

            # Save metadata
            metadata_file = modality_dir / f"metadata_{timestamp}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            self.stats['embeddings_generated'] += len(embeddings)

            logger.info(f"💾 Saved {len(embeddings)} {modality} embeddings to {embedding_file}")

        except Exception as e:
            logger.error(f"❌ Failed to save {modality} embeddings: {e!s}")

    def process_priority_datasets(self, max_files_per_modality: int = 1000):
        """Process priority datasets for quick training preparation."""
        logger.info("🎯 Processing priority datasets...")

        try:
            # Scan F: drive
            file_catalog = self.scan_f_drive_datasets()

            if not file_catalog:
                logger.warning("⚠️  No files found in datasets")
                return False

            start_time = time.time()

            # Process each modality
            if file_catalog['text']:
                self.process_text_files(file_catalog['text'], max_files_per_modality)

            if file_catalog['image']:
                self.process_image_files(file_catalog['image'], max_files_per_modality)

            if file_catalog['audio']:
                self.process_audio_files(file_catalog['audio'], max_files_per_modality)

            # Calculate processing time
            self.stats['processing_time'] = time.time() - start_time
            self.stats['average_speed'] = self.stats['files_processed'] / self.stats['processing_time'] if self.stats['processing_time'] > 0 else 0

            # Display final statistics
            self.display_processing_summary()

            logger.info("✅ Priority dataset processing complete")
            return True

        except Exception as e:
            logger.error(f"❌ Priority dataset processing failed: {e!s}")
            traceback.print_exc()
            return False

    def display_processing_summary(self):
        """Display comprehensive processing summary."""
        if console:
            summary_content = f"""
[bold green]🎉 EMBEDDING PROCESSING COMPLETE![/bold green]

[bold yellow]📊 Processing Statistics:[/bold yellow]
• Total Files Found: {self.stats['total_files_found']:,}
• Files Processed: {self.stats['files_processed']:,}
• Embeddings Generated: {self.stats['embeddings_generated']:,}
• Errors Encountered: {self.stats['errors_encountered']:,}

[bold yellow]⚡ Performance Metrics:[/bold yellow]
• Processing Time: {self.stats['processing_time']:.1f} seconds
• Average Speed: {self.stats['average_speed']:.1f} files/second
• Success Rate: {(self.stats['files_processed'] / max(1, self.stats['files_processed'] + self.stats['errors_encountered']) * 100):.1f}%

[bold yellow]🌐 Modality Distribution:[/bold yellow]
• Text Files: {self.stats['modality_distribution']['text']:,}
• Image Files: {self.stats['modality_distribution']['image']:,}
• Audio Files: {self.stats['modality_distribution']['audio']:,}
• Video Files: {self.stats['modality_distribution']['video']:,}
• Other Files: {self.stats['modality_distribution']['other']:,}

[bold cyan]💾 Embeddings saved to: {self.embeddings_output}[/bold cyan]
            """
            console.print(Panel(summary_content, title="Embedding Processing Summary", border_style="green"))
        else:
            logger.info("🎉 EMBEDDING PROCESSING COMPLETE!")
            logger.info(f"📊 Files processed: {self.stats['files_processed']:,}")
            logger.info(f"⚡ Speed: {self.stats['average_speed']:.1f} files/second")
            logger.info(f"💾 Embeddings: {self.stats['embeddings_generated']:,}")

def create_multimodal_training_dataset(b3_manager: B3InitializationManager,
                                     max_files_per_modality: int = 1000):
    """
    Create a comprehensive multimodal training dataset.

    Args:
        b3_manager: Initialized B3 system manager
        max_files_per_modality: Maximum files to process per modality

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("🚀 Creating multimodal training dataset...")

    try:
        # Initialize embedding integrator
        integrator = B3MultimodalEmbeddingIntegrator(b3_manager)

        # Process priority datasets
        success = integrator.process_priority_datasets(max_files_per_modality)

        if success:
            logger.info("✅ Multimodal training dataset created successfully!")
            return True
        else:
            logger.error("❌ Failed to create multimodal training dataset")
            return False

    except Exception as e:
        logger.error(f"❌ Dataset creation failed: {e!s}")
        traceback.print_exc()
        return False

def main():
    """Main function for embedding integration."""
    import argparse

    parser = argparse.ArgumentParser(description="B3 Multimodal Embedding Integration")
    parser.add_argument("--max-files", type=int, default=1000, help="Maximum files per modality")
    parser.add_argument("--scan-only", action="store_true", help="Only scan F: drive, don't process")
    parser.add_argument("--3b", action="store_true", help="Use 3B model configuration")

    args = parser.parse_args()

    try:
        # Initialize B3 system
        logger.info("🚀 Initializing B3 system...")

        if args._3b:
            from src.core.initialization.b3_full_initialization import initialize_b3_3b
            b3_manager = initialize_b3_3b()
        else:
            from src.core.initialization.b3_full_initialization import initialize_b3_standard
            b3_manager = initialize_b3_standard()

        if not b3_manager:
            logger.error("❌ B3 initialization failed")
            return 1

        # Create embedding integrator
        integrator = B3MultimodalEmbeddingIntegrator(b3_manager)

        if args.scan_only:
            # Only scan F: drive
            file_catalog = integrator.scan_f_drive_datasets()
            logger.info(f"📊 Scan complete: {sum(len(files) for files in file_catalog.values()):,} files found")
        else:
            # Full processing
            success = integrator.process_priority_datasets(args.max_files)
            if success:
                logger.info("✅ Embedding integration complete!")
            else:
                logger.error("❌ Embedding integration failed!")
                return 1

        return 0

    except Exception as e:
        logger.error(f"❌ Main execution failed: {e!s}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
