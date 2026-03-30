
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #deployment #documentation #inference #multimodal #python #source_code #src/dev_tools/analysis/f_drive_datasets_organizer.py #testing #training #web_interface
**Category:** Development Tools
**Status:** Deprecated
"""









# !/usr/bin/env python3

**Created:** 2024-10-15
**Updated:** 2025-07-26 10_27_01
**Author:** ImpressionCore Team
**Tags:** #deployment #documentation #inference #multimodal #python #source_code #src/dev_tools/analysis/f_drive_datasets_organizer.py #testing #training #web_interface
**Category:** Development Tools
**Status:** Deprecated

"""
F: Drive Datasets Organizer

Comprehensive automation for organizing F:\datasets directory according to world-class
ML/AI data management standards. Implements intelligent file categorization, backup
creation, and comprehensive logging with Rich UI enhancements.

Author: GitHub Copilot
Date: 2025-07-24
Sacred Covenant: File Integrity Protected
Version: 2.0 - World-Class Edition
"""

import os
import sys
import json
import shutil
import logging
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter

# Rich imports (optional - graceful fallback)
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich library not available. Using basic output.")

class FDriveDatasetOrganizer:
    """World-class F: drive datasets organizer with comprehensive automation."""

    def __init__(self, f_drive_path: str = "F:\\", create_backup: bool = True):
        self.f_drive_path = Path(f_drive_path)
        self.datasets_path = self.f_drive_path / "datasets"
        self.create_backup = create_backup
        self.console = Console() if RICH_AVAILABLE else None

        # Statistics tracking
        self.stats = {
            "files_moved": 0,
            "files_failed": 0,
            "directories_created": 0,
            "total_size_moved": 0,
            "start_time": None,
            "end_time": None,
            "backup_created": False,
            "errors": []
        }

        # File categorization patterns with comprehensive rules
        self.categorization_rules = {
            # Academic papers and research
            "academic": {
                "patterns": [
                    r"^\d{4}\.\d{5}v\d+\.json$",  # ArXiv papers
                    r"arxiv_.*\.json$",
                    r".*paper.*\.pdf$",
                    r".*research.*\.pdf$",
                    r".*journal.*\.pdf$",
                    r".*conference.*\.pdf$"
                ],
                "keywords": ["arxiv", "paper", "research", "journal", "conference", "publication"],
                "subdirectory": "papers"
            },

            # Educational materials
            "educational": {
                "patterns": [
                    r".*grade.*",
                    r".*education.*",
                    r".*curriculum.*",
                    r".*lesson.*",
                    r".*course.*",
                    r".*tutorial.*"
                ],
                "keywords": ["grade", "education", "curriculum", "lesson", "course", "tutorial", "learning"],
                "subdirectory": "materials"
            },

            # Vision/Image datasets
            "vision": {
                "patterns": [
                    r".*\.(jpg|jpeg|png|gif|bmp|tiff|webp)$",
                    r".*lfw.*",
                    r".*celeba.*",
                    r".*fairface.*",
                    r".*imagenet.*",
                    r".*coco.*",
                    r".*mnist.*",
                    r".*cifar.*"
                ],
                "keywords": ["image", "vision", "photo", "picture", "face", "facial", "visual"],
                "subdirectory": "images"
            },

            # Audio datasets
            "audio": {
                "patterns": [
                    r".*\.(wav|mp3|flac|ogg|m4a|aac)$",
                    r".*audio.*",
                    r".*speech.*",
                    r".*voice.*",
                    r".*sound.*"
                ],
                "keywords": ["audio", "speech", "voice", "sound", "music", "acoustic"],
                "subdirectory": "raw"
            },

            # Text data
            "text": {
                "patterns": [
                    r".*\.(txt|md|doc|docx|rtf)$",
                    r".*text.*",
                    r".*corpus.*",
                    r".*nlp.*",
                    r".*language.*"
                ],
                "keywords": ["text", "corpus", "nlp", "language", "document", "literature"],
                "subdirectory": "raw"
            },

            # Embeddings and vectors
            "embeddings": {
                "patterns": [
                    r".*\.npy$",
                    r".*\.npz$",
                    r".*\.faiss$",
                    r".*\.pt$",
                    r".*\.pth$",
                    r".*embeddings?.*",
                    r".*vectors?.*",
                    r".*features?.*"
                ],
                "keywords": ["embedding", "vector", "feature", "representation", "encode"],
                "subdirectory": "embeddings"
            },

            # Structured data
            "structured": {
                "patterns": [
                    r".*\.(csv|tsv|xlsx|xls|parquet|feather)$",
                    r".*\.json$",
                    r".*\.jsonl$",
                    r".*database.*",
                    r".*table.*"
                ],
                "keywords": ["data", "table", "database", "structured", "tabular"],
                "subdirectory": "tabular"
            },

            # Configuration files
            "configurations": {
                "patterns": [
                    r".*config.*\.(json|yaml|yml|toml|ini)$",
                    r".*settings.*\.(json|yaml|yml)$",
                    r".*params.*\.(json|yaml|yml)$",
                    r".*hyperparams.*"
                ],
                "keywords": ["config", "configuration", "settings", "params", "hyperparams"],
                "subdirectory": "training"
            },

            # Tools and scripts
            "tools": {
                "patterns": [
                    r".*\.(py|sh|bat|ps1|r)$",
                    r".*script.*",
                    r".*tool.*",
                    r".*utility.*"
                ],
                "keywords": ["script", "tool", "utility", "processor", "converter"],
                "subdirectory": "processors"
            },

            # Metadata and documentation
            "metadata": {
                "patterns": [
                    r".*metadata.*",
                    r".*catalog.*",
                    r".*schema.*",
                    r".*readme.*",
                    r".*info.*\.json$",
                    r".*manifest.*"
                ],
                "keywords": ["metadata", "catalog", "schema", "readme", "info", "manifest"],
                "subdirectory": "catalogs"
            },

            # Synthetic/Generated data
            "synthetic": {
                "patterns": [
                    r".*synthetic.*",
                    r".*generated.*",
                    r".*artificial.*",
                    r".*fake.*",
                    r".*simulated.*"
                ],
                "keywords": ["synthetic", "generated", "artificial", "fake", "simulated"],
                "subdirectory": "text"  # Default to text, will be refined
            }
        }

        # World-class directory structure
        self.directory_structure = {
            "text": {
                "raw": "Raw text files and documents",
                "processed": "Cleaned and preprocessed text",
                "embeddings": "Text embeddings and vectors",
                "tokenized": "Tokenized text datasets",
                "annotations": "Labeled and annotated text",
                "multilingual": "Multi-language text datasets",
                "domain_specific": "Domain-specific text (medical, legal, etc.)",
                "synthetic": "AI-generated text data"
            },
            "vision": {
                "images": {
                    "datasets": {
                        "facial_recognition": "Face detection and recognition",
                        "object_detection": "Object detection datasets",
                        "classification": "Image classification datasets",
                        "segmentation": "Image segmentation datasets",
                        "medical": "Medical imaging datasets",
                        "satellite": "Satellite and aerial imagery"
                    },
                    "raw": "Unprocessed image files",
                    "processed": "Processed and augmented images"
                },
                "video": {
                    "raw": "Raw video files",
                    "processed": "Processed video data",
                    "frames": "Extracted video frames"
                },
                "embeddings": "Visual embeddings and features",
                "annotations": "Image/video annotations and labels",
                "synthetic": "AI-generated visual content"
            },
            "audio": {
                "raw": "Raw audio files",
                "processed": "Processed audio data",
                "embeddings": "Audio embeddings and features",
                "transcriptions": "Audio transcriptions and labels",
                "synthetic": "AI-generated audio content"
            },
            "multimodal": {
                "vision_text": "Image-text paired datasets",
                "audio_text": "Audio-text paired datasets",
                "audio_vision": "Audio-visual datasets",
                "all_modalities": "Datasets with 3+ modalities",
                "embeddings": "Multimodal embeddings",
                "annotations": "Multimodal annotations"
            },
            "structured": {
                "tabular": "CSV, Excel, and tabular data",
                "time_series": "Time-series datasets",
                "graphs": "Graph and network data",
                "knowledge_bases": "Structured knowledge",
                "embeddings": "Structured data embeddings"
            },
            "educational": {
                "materials": {
                    "k12": "K-12 educational content",
                    "higher_ed": "University-level materials",
                    "vocational": "Vocational training content",
                    "online_courses": "MOOC and online course data"
                },
                "assessments": "Tests, quizzes, and evaluations",
                "curricula": "Curriculum designs and standards",
                "tools": "Educational software and tools",
                "research": "Educational research data"
            },
            "academic": {
                "papers": {
                    "arxiv": "ArXiv preprints",
                    "journals": "Published journal articles",
                    "conferences": "Conference proceedings",
                    "theses": "Theses and dissertations"
                },
                "datasets": "Academic research datasets",
                "conferences": "Conference data and proceedings",
                "journals": "Journal articles and metadata",
                "preprints": "Preprint servers content"
            },
            "synthetic": {
                "text": "AI-generated text content",
                "images": "AI-generated images",
                "audio": "AI-generated audio",
                "multimodal": "AI-generated multimodal content",
                "structured": "AI-generated structured data"
            },
            "metadata": {
                "catalogs": "Data catalogs and inventories",
                "schemas": "Data schemas and structures",
                "lineage": "Data lineage and provenance",
                "quality": "Data quality reports",
                "documentation": "Dataset documentation"
            },
            "configurations": {
                "training": "ML training configurations",
                "inference": "Model inference settings",
                "preprocessing": "Data preprocessing configs",
                "evaluation": "Evaluation configurations",
                "deployment": "Deployment configurations"
            },
            "working": {
                "staging": "Files being processed",
                "preprocessing": "Preprocessing workspace",
                "experiments": "Experimental datasets",
                "temp": "Temporary files",
                "backups": "Working backups"
            },
            "archives": {
                "deprecated": "Deprecated datasets",
                "legacy": "Legacy format data",
                "backup_data": "Archived backups",
                "historical": "Historical datasets"
            },
            "tools": {
                "processors": "Data processing scripts",
                "validators": "Data validation tools",
                "converters": "Format conversion utilities",
                "utilities": "General utilities",
                "scripts": "Automation scripts"
            }
        }

    def setup_logging(self) -> None:
        """Setup comprehensive logging system."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"f_drive_organization_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"F: Drive Organization started - {timestamp}")

    def create_backup_if_requested(self) -> bool:
        """Create backup of datasets directory if requested."""
        if not self.create_backup:
            self.logger.info("Backup creation skipped by user request")
            return True

        if not self.datasets_path.exists():
            self.logger.info("No datasets directory to backup")
            return True

        # Create backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.f_drive_path / "backup" / f"datasets_backup_{timestamp}"

        try:
            backup_dir.mkdir(parents=True, exist_ok=True)

            if RICH_AVAILABLE and self.console:
                with self.console.status(f"[bold green]Creating backup at {backup_dir}..."):
                    shutil.copytree(self.datasets_path, backup_dir / "datasets", dirs_exist_ok=True)
            else:
                print(f"📦 Creating backup at {backup_dir}...")
                shutil.copytree(self.datasets_path, backup_dir / "datasets", dirs_exist_ok=True)

            self.stats["backup_created"] = True
            self.logger.info(f"Backup created successfully at: {backup_dir}")

            if RICH_AVAILABLE and self.console:
                self.console.print(f"✅ Backup created at: {backup_dir}", style="green")
            else:
                print(f"✅ Backup created at: {backup_dir}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            self.stats["errors"].append(f"Backup creation failed: {e}")

            if RICH_AVAILABLE and self.console:
                self.console.print(f"❌ Backup failed: {e}", style="red")
            else:
                print(f"❌ Backup failed: {e}")

            return False

    def create_directory_structure(self) -> bool:
        """Create the world-class directory structure."""
        try:
            created_dirs = []

            def create_nested_dirs(base_path: Path, structure: dict, level: int = 0):
                for name, content in structure.items():
                    current_path = base_path / name

                    if isinstance(content, dict):
                        current_path.mkdir(exist_ok=True)
                        if not current_path.exists():
                            created_dirs.append(str(current_path))
                        create_nested_dirs(current_path, content, level + 1)
                    else:
                        current_path.mkdir(exist_ok=True)
                        if not current_path.exists():
                            created_dirs.append(str(current_path))

            # Ensure base datasets directory exists
            self.datasets_path.mkdir(exist_ok=True)

            if RICH_AVAILABLE and self.console:
                with self.console.status("[bold green]Creating directory structure..."):
                    create_nested_dirs(self.datasets_path, self.directory_structure)
            else:
                print("🏗️  Creating directory structure...")
                create_nested_dirs(self.datasets_path, self.directory_structure)

            self.stats["directories_created"] = len(created_dirs)
            self.logger.info(f"Created {len(created_dirs)} directories")

            if RICH_AVAILABLE and self.console:
                self.console.print(f"✅ Created {len(created_dirs)} directories", style="green")
            else:
                print(f"✅ Created {len(created_dirs)} directories")

            return True

        except Exception as e:
            self.logger.error(f"Failed to create directory structure: {e}")
            self.stats["errors"].append(f"Directory creation failed: {e}")
            return False

    def categorize_file(self, file_path: Path) -> Tuple[str, str]:
        """Categorize a file and determine its destination."""
        filename = file_path.name.lower()
        filepath_str = str(file_path).lower()

        # Check each category
        for category, rules in self.categorization_rules.items():
            # Check patterns
            for pattern in rules["patterns"]:
                if re.search(pattern, filename) or re.search(pattern, filepath_str):
                    return category, rules["subdirectory"]

            # Check keywords
            for keyword in rules["keywords"]:
                if keyword in filename or keyword in filepath_str:
                    return category, rules["subdirectory"]

        # Smart defaults based on file extension
        extension = file_path.suffix.lower()

        if extension in ['.json', '.jsonl']:
            # Try to determine if it's academic content
            if any(term in filename for term in ['arxiv', 'paper', 'research']):
                return "academic", "papers"
            return "structured", "tabular"

        elif extension in ['.csv', '.tsv', '.xlsx', '.xls']:
            return "structured", "tabular"

        elif extension in ['.txt', '.md', '.doc', '.docx']:
            return "text", "raw"

        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            return "vision", "images/raw"

        elif extension in ['.wav', '.mp3', '.flac', '.ogg']:
            return "audio", "raw"

        elif extension in ['.py', '.sh', '.bat', '.r']:
            return "tools", "processors"

        elif extension in ['.npy', '.npz', '.pt', '.pth']:
            return "multimodal", "embeddings"  # Could be any modality

        else:
            # Default to working/staging for unknown files
            return "working", "staging"

    def get_destination_path(self, category: str, subdirectory: str) -> Path:
        """Get the full destination path for a categorized file."""
        if "/" in subdirectory:
            # Handle nested subdirectories
            parts = subdirectory.split("/")
            dest_path = self.datasets_path / category
            for part in parts:
                dest_path = dest_path / part
        else:
            dest_path = self.datasets_path / category / subdirectory

        return dest_path

    def move_file_safely(self, source: Path, destination: Path) -> bool:
        """Move a file safely with verification."""
        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Handle filename conflicts
            if destination.exists():
                base_name = destination.stem
                extension = destination.suffix
                counter = 1

                while destination.exists():
                    new_name = f"{base_name}_{counter}{extension}"
                    destination = destination.parent / new_name
                    counter += 1

            # Get file size for statistics
            file_size = source.stat().st_size

            # Move the file
            shutil.move(str(source), str(destination))

            # Verify the move
            if destination.exists() and not source.exists():
                self.stats["files_moved"] += 1
                self.stats["total_size_moved"] += file_size
                self.logger.debug(f"Moved: {source} -> {destination}")
                return True
            else:
                self.logger.error(f"Move verification failed: {source} -> {destination}")
                self.stats["files_failed"] += 1
                self.stats["errors"].append(f"Move verification failed: {source}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to move {source}: {e}")
            self.stats["files_failed"] += 1
            self.stats["errors"].append(f"Move failed: {source} - {e}")
            return False

    def organize_files(self) -> bool:
        """Organize all files in the datasets directory."""
        if not self.datasets_path.exists():
            self.logger.error("Datasets directory does not exist")
            return False

        # Collect all files to process
        files_to_process = []
        try:
            for item in self.datasets_path.rglob("*"):
                if item.is_file():
                    # Skip files already in organized structure
                    relative_path = item.relative_to(self.datasets_path)
                    if len(relative_path.parts) > 1:
                        # File is already in a subdirectory, might be organized
                        first_part = relative_path.parts[0]
                        if first_part in self.directory_structure:
                            continue

                    files_to_process.append(item)

        except Exception as e:
            self.logger.error(f"Error collecting files: {e}")
            return False

        if not files_to_process:
            self.logger.info("No files found to organize")
            if RICH_AVAILABLE and self.console:
                self.console.print("ℹ️ No files found to organize", style="blue")
            else:
                print("ℹ️ No files found to organize")
            return True

        # Process files with progress tracking
        if RICH_AVAILABLE and self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:

                task = progress.add_task("Organizing files...", total=len(files_to_process))

                for file_path in files_to_process:
                    # Categorize file
                    category, subdirectory = self.categorize_file(file_path)
                    destination_dir = self.get_destination_path(category, subdirectory)
                    destination_file = destination_dir / file_path.name

                    # Update progress description
                    progress.update(task, description=f"Moving {file_path.name}...")

                    # Move file
                    success = self.move_file_safely(file_path, destination_file)

                    if success:
                        progress.update(task, description=f"✅ Moved {file_path.name}")
                    else:
                        progress.update(task, description=f"❌ Failed {file_path.name}")

                    progress.advance(task)

        else:
            # Basic progress without Rich
            total_files = len(files_to_process)
            for i, file_path in enumerate(files_to_process, 1):
                print(f"Processing {i}/{total_files}: {file_path.name}")

                # Categorize file
                category, subdirectory = self.categorize_file(file_path)
                destination_dir = self.get_destination_path(category, subdirectory)
                destination_file = destination_dir / file_path.name

                # Move file
                self.move_file_safely(file_path, destination_file)

        return True

    def generate_organization_report(self) -> str:
        """Generate a comprehensive organization report."""
        end_time = datetime.now()
        duration = end_time - self.stats["start_time"]

        report = f"""
F: Drive Datasets Organization Report
===================================
Completion Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration}
Organizer: FDriveDatasetOrganizer v2.0

SUMMARY
=======
✅ Files Successfully Moved: {self.stats['files_moved']:,}
❌ Files Failed to Move: {self.stats['files_failed']:,}
🏗️  Directories Created: {self.stats['directories_created']:,}
💾 Total Data Moved: {self.stats['total_size_moved'] / (1024**3):.2f} GB
📦 Backup Created: {'✅ Yes' if self.stats['backup_created'] else '❌ No'}

PERFORMANCE METRICS
==================
Files/Second: {self.stats['files_moved'] / duration.total_seconds():.2f}
GB/Second: {(self.stats['total_size_moved'] / (1024**3)) / duration.total_seconds():.4f}

DIRECTORY STRUCTURE
==================
The following world-class structure has been implemented:

📁 F:\\datasets\\
├── 🔤 text/                    # Text data processing pipeline
├── 👁️ vision/                  # Image and video datasets
├── 🔊 audio/                   # Audio and speech data
├── 🔄 multimodal/              # Cross-modal datasets
├── 📊 structured/              # Tabular and time-series data
├── 🎓 educational/             # Educational materials
├── 📚 academic/                # Academic papers and research
├── 🤖 synthetic/               # AI-generated data
├── 📋 metadata/                # Data catalogs and schemas
├── ⚙️ configurations/          # Training and model configs
├── 💼 working/                 # Staging and temporary files
├── 📦 archives/                # Deprecated and legacy data
└── 🛠️ tools/                   # Data management scripts

ERRORS AND WARNINGS
==================
"""

        if self.stats["errors"]:
            for error in self.stats["errors"]:
                report += f"⚠️ {error}\n"
        else:
            report += "✅ No errors encountered\n"

        report += f"""
NEXT STEPS
==========
1. Run validation: python src/dev_tools/validation/validate_f_drive_structure.py
2. Update data pipelines to use new structure
3. Test integration with ImpressionCore components
4. Set up automated monitoring for structure compliance

END OF REPORT
=============
"""

        return report

    def save_organization_report(self, report: str) -> None:
        """Save the organization report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"f_drive_organization_report_{timestamp}.md")

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            self.logger.info(f"Organization report saved to: {report_file}")

            if RICH_AVAILABLE and self.console:
                self.console.print(f"📄 Report saved to: {report_file}", style="green")
            else:
                print(f"📄 Report saved to: {report_file}")

        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")

    def organize_datasets(self) -> bool:
        """Main organization function - orchestrates the entire process."""
        self.stats["start_time"] = datetime.now()

        # Setup logging
        self.setup_logging()

        if RICH_AVAILABLE and self.console:
            self.console.print(Panel.fit("🚀 F: Drive Datasets Organization", style="bold blue"))
        else:
            print("🚀 F: Drive Datasets Organization")
            print("=" * 50)

        try:
            # Step 1: Create backup if requested
            if not self.create_backup_if_requested():
                return False

            # Step 2: Create directory structure
            if not self.create_directory_structure():
                return False

            # Step 3: Organize files
            if not self.organize_files():
                return False

            # Step 4: Generate and save report
            self.stats["end_time"] = datetime.now()
            report = self.generate_organization_report()
            self.save_organization_report(report)

            # Display success summary
            if RICH_AVAILABLE and self.console:
                success_panel = Panel(
                    f"✅ Organization completed successfully!\n"
                    f"📄 Files moved: {self.stats['files_moved']:,}\n"
                    f"🏗️ Directories created: {self.stats['directories_created']:,}\n"
                    f"💾 Data organized: {self.stats['total_size_moved'] / (1024**3):.2f} GB",
                    title="🎉 Success!",
                    border_style="green"
                )
                self.console.print(success_panel)
            else:
                print("\n🎉 Organization completed successfully!")
                print(f"📄 Files moved: {self.stats['files_moved']:,}")
                print(f"🏗️ Directories created: {self.stats['directories_created']:,}")
                print(f"💾 Data organized: {self.stats['total_size_moved'] / (1024**3):.2f} GB")

            return True

        except Exception as e:
            self.logger.error(f"Organization failed: {e}")
            self.stats["errors"].append(f"Critical error: {e}")

            if RICH_AVAILABLE and self.console:
                self.console.print(f"❌ Organization failed: {e}", style="red")
            else:
                print(f"❌ Organization failed: {e}")

            return False

def main():
    """Main execution function."""
    try:
        # Parse command line arguments for backup option
        import argparse
        parser = argparse.ArgumentParser(description="F: Drive Datasets Organizer")
        parser.add_argument("--no-backup", action="store_true",
                          help="Skip backup creation")
        args = parser.parse_args()

        # Initialize organizer
        organizer = FDriveDatasetOrganizer(create_backup=not args.no_backup)

        # Run organization
        success = organizer.organize_datasets()

        return success

    except KeyboardInterrupt:
        print("\n⚠️ Organization interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Organization failed: {e}")
        logging.error(f"Organization failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
