#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #gpu_optimization #inference #memory_management #multimodal #python #pytorch #source_code #src/core/initialization/b3_full_init.py #tokenization #training #web_interface
**Category:** Core Implementation
**Status:** Active
"""




import json
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

import torch

# Rich enhancements
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, track  # noqa: F401
    from rich.table import Table
    from rich.text import Text  # noqa: F401
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def setup_logging():
    """Setup logging with rich enhancements if available."""
    if HAS_RICH:
        from rich.logging import RichHandler
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(console=console, rich_tracebacks=True)]
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    return logging.getLogger(__name__)

logger = setup_logging()

class B3FullInitializer:
    """Complete B3 initialization with multimodal embedding integration."""

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # F: drive and model paths are referenced but not created or ensured here.
        self.f_drive_path = Path("F:/")
        self.dataset_path = self.f_drive_path / "dataset"
        self.embeddings_path = self.f_drive_path / "embeddings"
        self.models_path = self.f_drive_path / "models"
        # Model components
        self.model = None
        self.tokenizer = None
        self.config = None
        # Embedding statistics
        self.embedding_stats = {
            'text': {'count': 0, 'size_mb': 0},
            'image': {'count': 0, 'size_mb': 0},
            'audio': {'count': 0, 'size_mb': 0},
            'video': {'count': 0, 'size_mb': 0},
            'total': {'count': 0, 'size_mb': 0}
        }

    def print_system_status(self):
        """Print comprehensive system status."""
        if HAS_RICH:
            # System info table
            table = Table(title="🚀 ImpressionCore B3 System Status")
            table.add_column("Component", style="cyan", no_wrap=True)
            table.add_column("Status", style="green")
            table.add_column("Details", style="yellow")

            # PyTorch info
            table.add_row("PyTorch", "✅ Available", f"v{torch.__version__}")

            # CUDA info
            if torch.cuda.is_available():
                device_name = torch.cuda.get_device_name(0)
                memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
                table.add_row("CUDA", "✅ Available", f"{device_name} ({memory_gb:.1f}GB)")
            else:
                table.add_row("CUDA", "❌ Not Available", "CPU mode only")

            # F: drive info
            if self.f_drive_path.exists():
                import shutil
                total, used, free = shutil.disk_usage(self.f_drive_path)
                free_gb = free / 1024**3
                table.add_row("F: Drive", "✅ Available", f"{free_gb:.1f}GB free")
            else:
                table.add_row("F: Drive", "❌ Not Available", "Required for embeddings")

            # Memory info
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated() / 1024**2
                memory_cached = torch.cuda.memory_reserved() / 1024**2
                table.add_row("GPU Memory", "📊 Monitored", f"{memory_allocated:.1f}MB allocated, {memory_cached:.1f}MB cached")

            console.print(table)
        else:
            logger.info("🚀 ImpressionCore B3 System Status")
            logger.info(f"PyTorch: v{torch.__version__}")
            logger.info(f"CUDA: {'Available' if torch.cuda.is_available() else 'Not Available'}")
            logger.info(f"F: Drive: {'Available' if self.f_drive_path.exists() else 'Not Available'}")

    def initialize_b3_model(self):
        """Initialize the complete B3 model."""
        try:
            logger.info("🧠 Initializing ImpressionCore B3 Model...")

            # Add src to path for imports
            import os
            import sys
            src_path = os.path.join(os.path.dirname(__file__), '..', '..')
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            # Import B3 components
            from core.models.impressioncore_b3_architecture import (
                B3Config,
                B3Config3B,
                ImpressionCoreB3Model,
                ImpressionCoreB3Model3B,
                memory_profile,
                sacred_covenant_check,
                validate_environment,
            )

            # Environment validation
            _env_status = validate_environment()
            logger.info("✅ Environment validation complete")

            # Choose configuration based on available VRAM
            if torch.cuda.is_available():
                vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
                if vram_gb >= 8.0:
                    logger.info("🚀 Using B3-3B configuration (8GB+ VRAM)")
                    self.config = B3Config3B()
                    self.model = ImpressionCoreB3Model3B()
                else:
                    logger.info("🎯 Using B3 standard configuration (GTX 1050 Ti optimized)")
                    self.config = B3Config()
                    self.model = ImpressionCoreB3Model(self.config)
            else:
                logger.info("💻 Using B3 CPU configuration")
                self.config = B3Config()
                self.model = ImpressionCoreB3Model(self.config)

            # Move model to device
            self.model = self.model.to(self.device)

            # Memory profiling
            memory_profile(self.model)

            # Sacred Covenant compliance check
            sacred_covenant_check(self.model, self.config)

            logger.info("✅ B3 Model initialized successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ B3 Model initialization failed: {e!s}")
            traceback.print_exc()
            return False

    def scan_f_drive_data(self) -> dict[str, list[Path]]:
        """Scan F:/dataset/ for all available multimodal data."""
        logger.info("🔍 Scanning F:/dataset/ for multimodal data...")

        data_files = {
            'text': [],
            'image': [],
            'audio': [],
            'video': [],
            'other': []
        }

        if not self.dataset_path.exists():
            logger.warning("⚠️ F:/dataset/ directory not found, creating it...")
            self.dataset_path.mkdir(parents=True, exist_ok=True)
            return data_files

        # File extensions for each modality
        extensions = {
            'text': {'.txt', '.md', '.json', '.csv', '.tsv', '.jsonl'},
            'image': {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'},
            'audio': {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac'},
            'video': {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm', '.m4v'}
        }

        # Scan recursively
        total_files = 0
        for file_path in self.dataset_path.rglob('*'):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                categorized = False

                for modality, exts in extensions.items():
                    if suffix in exts:
                        data_files[modality].append(file_path)
                        categorized = True
                        break

                if not categorized:
                    data_files['other'].append(file_path)

                total_files += 1

        # Log statistics
        if HAS_RICH:
            table = Table(title="📊 F:/dataset/ Scan Results")
            table.add_column("Modality", style="cyan")
            table.add_column("File Count", style="green")
            table.add_column("Examples", style="yellow")

            for modality, files in data_files.items():
                examples = ", ".join([f.name for f in files[:3]])
                if len(files) > 3:
                    examples += f" (+{len(files)-3} more)"
                table.add_row(modality.title(), str(len(files)), examples or "None")

            console.print(table)
        else:
            logger.info("📊 F:/dataset/ Scan Results:")
            for modality, files in data_files.items():
                logger.info(f"  {modality.title()}: {len(files)} files")

        logger.info(f"✅ Scan complete: {total_files} total files found")
        return data_files

    def extract_embeddings_batch(self, data_files: dict[str, list[Path]], batch_size: int = 32):
        """Extract embeddings for all multimodal data in batches."""
        if self.model is None:
            logger.error("❌ Model not initialized! Call initialize_b3_model() first.")
            return False

        logger.info("🔄 Starting full multimodal embedding extraction...")

        total_files = sum(len(files) for files in data_files.values())
        if total_files == 0:
            logger.warning("⚠️ No data files found to process")
            return True

        try:
            from core.models.impressioncore_b3_architecture import (
                extract_audio_embedding,
                extract_image_embedding,
                extract_text_embedding,
                extract_video_embedding,
                save_embedding,
            )

            processed_count = 0

            # Process each modality
            for modality, files in data_files.items():
                if not files or modality == 'other':
                    continue

                logger.info(f"🔄 Processing {len(files)} {modality} files...")

                # Create modality-specific output directory
                output_dir = self.embeddings_path / modality
                output_dir.mkdir(exist_ok=True)

                # Process files in batches
                for i in range(0, len(files), batch_size):
                    batch_files = files[i:i+batch_size]

                    if HAS_RICH:
                        batch_files = track(batch_files, description=f"Processing {modality} batch {i//batch_size + 1}")

                    for file_path in batch_files:
                        try:
                            # Generate output path
                            relative_path = file_path.relative_to(self.dataset_path)
                            output_path = output_dir / f"{relative_path.stem}.pt"
                            output_path.parent.mkdir(parents=True, exist_ok=True)

                            # Skip if already processed
                            if output_path.exists():
                                continue

                            # Extract embedding based on modality
                            embedding = None
                            if modality == 'text':
                                embedding = extract_text_embedding(self.model, None, file_path)
                            elif modality == 'image':
                                embedding = extract_image_embedding(self.model, file_path)
                            elif modality == 'audio':
                                embedding = extract_audio_embedding(self.model, file_path)
                            elif modality == 'video':
                                embedding = extract_video_embedding(self.model, file_path)

                            if embedding is not None:
                                save_embedding(embedding, output_path)
                                processed_count += 1

                                # Update statistics
                                file_size_mb = output_path.stat().st_size / 1024**2
                                self.embedding_stats[modality]['count'] += 1
                                self.embedding_stats[modality]['size_mb'] += file_size_mb

                        except Exception as e:
                            logger.warning(f"⚠️ Failed to process {file_path.name}: {e!s}")
                            continue

                    # Memory cleanup after each batch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

            # Update total statistics
            self.embedding_stats['total']['count'] = sum(stats['count'] for stats in self.embedding_stats.values() if isinstance(stats, dict))
            self.embedding_stats['total']['size_mb'] = sum(stats['size_mb'] for stats in self.embedding_stats.values() if isinstance(stats, dict))

            logger.info(f"✅ Embedding extraction complete: {processed_count} embeddings generated")
            return True

        except Exception as e:
            logger.error(f"❌ Embedding extraction failed: {e!s}")
            traceback.print_exc()
            return False

    def save_initialization_report(self):
        """Save comprehensive initialization report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'pytorch_version': torch.__version__,
                'cuda_available': torch.cuda.is_available(),
                'device': str(self.device),
                'f_drive_available': self.f_drive_path.exists()
            },
            'model_config': self.config.to_dict() if self.config else None,
            'embedding_stats': self.embedding_stats,
            'paths': {
                'dataset': str(self.dataset_path),
                'embeddings': str(self.embeddings_path),
                'models': str(self.models_path)
            }
        }

        if torch.cuda.is_available():
            report['system_info']['gpu_name'] = torch.cuda.get_device_name(0)
            report['system_info']['gpu_memory_gb'] = torch.cuda.get_device_properties(0).total_memory / 1024**3

        # Save report
        report_path = Path("src/memlog") / f"b3_initialization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Initialization report saved: {report_path}")
        return report_path

    def run_full_initialization(self):
        """Run complete B3 initialization with multimodal embedding extraction."""
        logger.info("🚀 Starting ImpressionCore B3 Full Initialization...")

        if HAS_RICH:
            console.print(Panel.fit(
                "[bold green]ImpressionCore B3 Revolutionary Architecture[/bold green]\n"
                "[cyan]Full Multimodal Initialization Process[/cyan]\n"
                f"[yellow]Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/yellow]",
                title="🧠 Initialization Started"
            ))

        # Step 1: System status check
        self.print_system_status()

        # Step 2: Initialize B3 model
        if not self.initialize_b3_model():
            logger.error("❌ Model initialization failed, aborting...")
            return False

        # Step 3: Scan F:/dataset/ for data
        data_files = self.scan_f_drive_data()

        # Step 4: Extract embeddings
        if not self.extract_embeddings_batch(data_files):
            logger.error("❌ Embedding extraction failed")
            return False

        # Step 5: Save initialization report
        report_path = self.save_initialization_report()

        # Step 6: Final status
        if HAS_RICH:
            console.print(Panel.fit(
                "[bold green]✅ ImpressionCore B3 Initialization Complete![/bold green]\n"
                f"[cyan]Total Embeddings: {self.embedding_stats['total']['count']:,}[/cyan]\n"
                f"[yellow]Total Size: {self.embedding_stats['total']['size_mb']:.1f}MB[/yellow]\n"
                f"[magenta]Report: {report_path.name}[/magenta]",
                title="🎉 Success!"
            ))
        else:
            logger.info("✅ ImpressionCore B3 Initialization Complete!")
            logger.info(f"Total Embeddings: {self.embedding_stats['total']['count']:,}")
            logger.info(f"Total Size: {self.embedding_stats['total']['size_mb']:.1f}MB")

        return True

def main():
    """Main initialization function."""
    initializer = B3FullInitializer()
    success = initializer.run_full_initialization()

    if success:
        logger.info("🎯 ImpressionCore B3 is ready for training and inference!")
        sys.exit(0)
    else:
        logger.error("💥 Initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
