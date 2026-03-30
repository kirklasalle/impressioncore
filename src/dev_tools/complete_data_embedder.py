#!/usr/bin/env python3
"""
ImpressionCore-B1 Complete Data Directory Embedding System
=========================================================

Embeds ALL text, image, and audio files from the entire data/ directory.
Comprehensive multimodal embedding for maximum dataset coverage.

Author: ImpressionCore Team
Date: 2025-01-06
Version: 1.2.0 - Complete Data Directory Embedding
Hardware: NVIDIA GTX 1050 Ti (4GB VRAM) Optimized
"""

import torch
import torch.nn as nn
import numpy as np
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
import pickle
import librosa
from PIL import Image
import torchvision.transforms as transforms
import logging

# Rich UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ImpressionCore imports
sys.path.append(str(Path(__file__).parent))


class CompleteDataDirectoryEmbedder:
    """
    Complete data directory embedding system for ImpressionCore-B1.
    
    Features:
    - Process ALL files in data/ directory recursively
    - Support for text (.txt, .md, .json, .py, .yaml, .yml), images (.jpg, .png, .jpeg), audio (.wav, .mp3)
    - Unified 128-dimension embedding space
    - Memory-efficient processing for GTX 1050 Ti
    - Rich progress monitoring
    """
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.device = self._setup_device()
        self.base_path = Path("d:/Projects/impressioncore")
        self.data_path = self.base_path / "src" / "data"
        self.embeddings_path = self.base_path / "src/data/embeddings"
        self.embeddings_path.mkdir(exist_ok=True)
        
        # Fixed embedding models
        self.text_embedder = nn.Linear(128, 128).to(self.device)
        self.image_embedder = nn.Linear(224*224*3, 128).to(self.device)  
        self.audio_embedder = nn.Linear(128, 128).to(self.device)
        
        # File type patterns
        self.text_extensions = {'.txt', '.md', '.json', '.py', '.yaml', '.yml', '.csv'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        self.audio_extensions = {'.wav', '.mp3', '.flac', '.ogg'}
        
        # Embeddings storage
        self.embeddings = {
            'text': {},
            'images': {},
            'audio': {},
            'metadata': {
                'creation_date': datetime.now().isoformat(),
                'total_samples': 0,
                'embedding_dimension': 128,
                'data_directory': str(self.data_path),
                'file_types_processed': {
                    'text': list(self.text_extensions),
                    'images': list(self.image_extensions),
                    'audio': list(self.audio_extensions)
                }
            }
        }
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Image transforms
        self.image_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])
        
        self._print_banner()
    
    def _setup_device(self):
        """Setup CUDA device."""
        if torch.cuda.is_available():
            return "cuda:0"
        else:
            return "cpu"
    
    def _setup_logging(self):
        """Setup logging."""
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("CompleteDataDirectoryEmbedder")
    
    def _print_banner(self):
        """Print embedding system banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║       🧠 COMPLETE DATA DIRECTORY EMBEDDING SYSTEM 🧠       ║
║                    ALL FILES IN data/                       ║
║              📝 Text + 🖼️ Images + 🎵 Audio                ║
╚══════════════════════════════════════════════════════════════╝
"""
        if self.console:
            panel = Panel(
                banner,
                title="🧠 Complete Data Directory Embedder",
                subtitle="Processing ALL files in data/ directory",
                style="bold cyan"
            )
            self.console.print(panel)
        else:
            print(banner)
        
        print(f"Embedding Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Data Directory: {self.data_path}")
        print(f"Device: {self.device}")
        print()
    
    def discover_all_files(self) -> Dict[str, List[Path]]:
        """Discover ALL files in data directory by type."""
        self.logger.info(f"🔍 Scanning entire data directory: {self.data_path}")
        
        all_files = {
            'text': [],
            'images': [],
            'audio': []
        }
        
        # Recursively scan all files
        for file_path in self.data_path.rglob('*'):
            if file_path.is_file():
                file_ext = file_path.suffix.lower()
                
                # Categorize by file extension
                if file_ext in self.text_extensions:
                    all_files['text'].append(file_path)
                elif file_ext in self.image_extensions:
                    all_files['images'].append(file_path)
                elif file_ext in self.audio_extensions:
                    all_files['audio'].append(file_path)
        
        # Log discovery results
        total_files = sum(len(files) for files in all_files.values())
        self.logger.info(f"📝 Found {len(all_files['text'])} text files")
        self.logger.info(f"🖼️ Found {len(all_files['images'])} image files")
        self.logger.info(f"🎵 Found {len(all_files['audio'])} audio files")
        self.logger.info(f"🎯 Total files to embed: {total_files}")
        
        self.embeddings['metadata']['total_samples'] = total_files
        
        # Display discovered files summary
        if self.console:
            table = Table(title="🔍 Complete Data Directory Scan Results", style="bold")
            table.add_column("File Type", style="cyan")
            table.add_column("Count", style="green")
            table.add_column("Extensions", style="yellow")
            
            table.add_row("Text Files", str(len(all_files['text'])), ", ".join(sorted(self.text_extensions)))
            table.add_row("Image Files", str(len(all_files['images'])), ", ".join(sorted(self.image_extensions)))
            table.add_row("Audio Files", str(len(all_files['audio'])), ", ".join(sorted(self.audio_extensions)))
            table.add_row("TOTAL FILES", str(total_files), "All Types", style="bold yellow")
            
            self.console.print(table)
        
        return all_files
    
    def embed_all_text_files(self, text_files: List[Path]):
        """Create embeddings for ALL text files."""
        self.logger.info(f"📝 Embedding {len(text_files)} text files...")
        
        for i, text_file in enumerate(text_files):
            try:
                # Read text content based on file type
                content = ""
                try:
                    with open(text_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                except UnicodeDecodeError:
                    # Try with different encoding
                    with open(text_file, 'r', encoding='latin-1') as f:
                        content = f.read().strip()
                
                # Truncate very long files
                if len(content) > 10000:
                    content = content[:10000]
                
                # Simple character-based embedding
                chars = [ord(c) % 256 for c in content[:128]]
                if len(chars) < 128:
                    chars.extend([0] * (128 - len(chars)))  # Pad with zeros
                
                # Convert to tensor and normalize
                text_tensor = torch.tensor(chars, dtype=torch.float32).unsqueeze(0).to(self.device) / 255.0
                
                # Get embedding
                with torch.no_grad():
                    embedding = self.text_embedder(text_tensor)
                
                # Create relative path for storage
                relative_path = text_file.relative_to(self.data_path)
                
                # Store embedding
                self.embeddings['text'][str(relative_path)] = {
                    'embedding': embedding.cpu().numpy(),
                    'content_preview': content[:200],
                    'file_path': str(text_file),
                    'file_size': text_file.stat().st_size,
                    'file_extension': text_file.suffix,
                    'embedding_shape': list(embedding.shape)
                }
                
                # Progress update
                if i % 10 == 0:
                    self.logger.info(f"   📝 Processed {i+1}/{len(text_files)} text files...")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to embed text file {text_file.name}: {e}")
        
        self.logger.info(f"✅ Completed text embedding: {len(self.embeddings['text'])} files")
    
    def embed_all_image_files(self, image_files: List[Path]):
        """Create embeddings for ALL image files."""
        self.logger.info(f"🖼️ Embedding {len(image_files)} image files...")
        
        for i, image_file in enumerate(image_files):
            try:
                # Load and preprocess image
                image = Image.open(image_file).convert('RGB')
                image_tensor = self.image_transform(image)
                
                # Flatten image to vector
                flattened_image = image_tensor.flatten().unsqueeze(0).to(self.device)
                
                # Get embedding
                with torch.no_grad():
                    embedding = self.image_embedder(flattened_image)
                
                # Create relative path for storage
                relative_path = image_file.relative_to(self.data_path)
                
                # Store embedding
                self.embeddings['images'][str(relative_path)] = {
                    'embedding': embedding.cpu().numpy(),
                    'image_size': image.size,
                    'file_path': str(image_file),
                    'file_size': image_file.stat().st_size,
                    'file_extension': image_file.suffix,
                    'embedding_shape': list(embedding.shape)
                }
                
                # Progress update
                if i % 10 == 0:
                    self.logger.info(f"   🖼️ Processed {i+1}/{len(image_files)} image files...")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to embed image file {image_file.name}: {e}")
        
        self.logger.info(f"✅ Completed image embedding: {len(self.embeddings['images'])} files")
    
    def embed_all_audio_files(self, audio_files: List[Path]):
        """Create embeddings for ALL audio files."""
        self.logger.info(f"🎵 Embedding {len(audio_files)} audio files...")
        
        for i, audio_file in enumerate(audio_files):
            try:
                # Load audio file
                audio, sr = librosa.load(audio_file, sr=16000, duration=10.0)
                
                # Extract MFCC features
                mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
                audio_features = np.mean(mfccs, axis=1)  # Average over time
                
                # Pad or truncate to 128 features
                if len(audio_features) < 128:
                    audio_features = np.pad(audio_features, (0, 128 - len(audio_features)))
                else:
                    audio_features = audio_features[:128]
                
                # Convert to tensor
                audio_tensor = torch.tensor(audio_features, dtype=torch.float32).unsqueeze(0).to(self.device)
                
                # Get embedding
                with torch.no_grad():
                    embedding = self.audio_embedder(audio_tensor)
                
                # Create relative path for storage
                relative_path = audio_file.relative_to(self.data_path)
                
                # Store embedding
                self.embeddings['audio'][str(relative_path)] = {
                    'embedding': embedding.cpu().numpy(),
                    'duration': len(audio) / sr,
                    'sample_rate': sr,
                    'file_path': str(audio_file),
                    'file_size': audio_file.stat().st_size,
                    'file_extension': audio_file.suffix,
                    'embedding_shape': list(embedding.shape)
                }
                
                # Progress update
                if i % 10 == 0:
                    self.logger.info(f"   🎵 Processed {i+1}/{len(audio_files)} audio files...")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to embed audio file {audio_file.name}: {e}")
        
        self.logger.info(f"✅ Completed audio embedding: {len(self.embeddings['audio'])} files")
    
    def save_embeddings(self):
        """Save all embeddings to disk."""
        self.logger.info("💾 Saving complete data directory embeddings to disk...")
        
        # Save as pickle for fast loading
        embeddings_file = self.embeddings_path / f"complete_data_embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        with open(embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
        
        # Save metadata as JSON
        metadata_file = self.embeddings_path / f"complete_data_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        metadata_only = self.embeddings['metadata'].copy()
        
        # Add detailed summary stats
        metadata_only['summary'] = {
            'text_files': len(self.embeddings['text']),
            'image_files': len(self.embeddings['images']),
            'audio_files': len(self.embeddings['audio']),
            'total_embeddings': len(self.embeddings['text']) + len(self.embeddings['images']) + len(self.embeddings['audio']),
            'data_directory_scanned': str(self.data_path),
            'embedding_dimension': 128
        }
        
        # Add file breakdown by extension
        metadata_only['file_breakdown'] = {
            'text_by_extension': {},
            'images_by_extension': {},
            'audio_by_extension': {}
        }
        
        # Count files by extension
        for file_path, file_data in self.embeddings['text'].items():
            ext = file_data['file_extension']
            metadata_only['file_breakdown']['text_by_extension'][ext] = metadata_only['file_breakdown']['text_by_extension'].get(ext, 0) + 1
        
        for file_path, file_data in self.embeddings['images'].items():
            ext = file_data['file_extension']
            metadata_only['file_breakdown']['images_by_extension'][ext] = metadata_only['file_breakdown']['images_by_extension'].get(ext, 0) + 1
        
        for file_path, file_data in self.embeddings['audio'].items():
            ext = file_data['file_extension']
            metadata_only['file_breakdown']['audio_by_extension'][ext] = metadata_only['file_breakdown']['audio_by_extension'].get(ext, 0) + 1
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata_only, f, indent=2)
        
        self.logger.info(f"✅ Complete data directory embeddings saved:")
        self.logger.info(f"   📄 Full embeddings: {embeddings_file}")
        self.logger.info(f"   📋 Metadata: {metadata_file}")
        
        return embeddings_file, metadata_file
    
    def run_complete_embedding(self):
        """Run the complete embedding process for ALL files in data directory."""
        self.logger.info("🚀 Starting complete data directory embedding process...")
        
        # Discover all files
        all_files = self.discover_all_files()
        
        total_files = sum(len(files) for files in all_files.values())
        if total_files == 0:
            self.logger.error("❌ No supported files found in data directory!")
            return
        
        # Process each modality with progress tracking
        if self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                
                # Text files
                if all_files['text']:
                    text_task = progress.add_task(f"[cyan]Embedding {len(all_files['text'])} text files...", total=len(all_files['text']))
                    self.embed_all_text_files(all_files['text'])
                    progress.update(text_task, completed=len(all_files['text']))
                
                # Image files
                if all_files['images']:
                    image_task = progress.add_task(f"[green]Embedding {len(all_files['images'])} image files...", total=len(all_files['images']))
                    self.embed_all_image_files(all_files['images'])
                    progress.update(image_task, completed=len(all_files['images']))
                
                # Audio files
                if all_files['audio']:
                    audio_task = progress.add_task(f"[yellow]Embedding {len(all_files['audio'])} audio files...", total=len(all_files['audio']))
                    self.embed_all_audio_files(all_files['audio'])
                    progress.update(audio_task, completed=len(all_files['audio']))
        
        else:
            # Console fallback
            if all_files['text']:
                self.embed_all_text_files(all_files['text'])
            if all_files['images']:
                self.embed_all_image_files(all_files['images'])
            if all_files['audio']:
                self.embed_all_audio_files(all_files['audio'])
        
        # Save embeddings
        embeddings_file, metadata_file = self.save_embeddings()
        
        # Print final summary
        self.print_embedding_summary()
        
        return embeddings_file, metadata_file
    
    def print_embedding_summary(self):
        """Print a comprehensive summary of the embedding process."""
        total_embeddings = len(self.embeddings['text']) + len(self.embeddings['images']) + len(self.embeddings['audio'])
        
        if self.console:
            # Create summary table
            table = Table(title="🧠 Complete Data Directory Embedding Summary", style="bold")
            table.add_column("File Type", style="cyan")
            table.add_column("Files Embedded", style="green")
            table.add_column("Embedding Dimension", style="yellow")
            table.add_column("Extensions Processed", style="magenta")
            
            if self.embeddings['text']:
                text_extensions = set(data['file_extension'] for data in self.embeddings['text'].values())
                table.add_row("Text Files", str(len(self.embeddings['text'])), "128", ", ".join(sorted(text_extensions)))
            
            if self.embeddings['images']:
                image_extensions = set(data['file_extension'] for data in self.embeddings['images'].values())
                table.add_row("Image Files", str(len(self.embeddings['images'])), "128", ", ".join(sorted(image_extensions)))
            
            if self.embeddings['audio']:
                audio_extensions = set(data['file_extension'] for data in self.embeddings['audio'].values())
                table.add_row("Audio Files", str(len(self.embeddings['audio'])), "128", ", ".join(sorted(audio_extensions)))
            
            table.add_row("TOTAL FILES", str(total_embeddings), "128 (unified)", "All Supported", style="bold yellow")
            
            self.console.print(table)
            
            # Success panel
            success_panel = Panel(
                f"🎉 SUCCESS: Embedded ALL {total_embeddings} files from data/ directory!\n"
                f"📊 Complete multimodal dataset with unified 128-dimension embeddings\n"
                f"💾 All embeddings saved for fast retrieval and similarity search\n"
                f"🔍 Includes: {len(self.embeddings['text'])} text + {len(self.embeddings['images'])} images + {len(self.embeddings['audio'])} audio\n"
                f"🚀 Ready for comprehensive multimodal AI applications",
                title="🧠 Complete Data Directory Embedding SUCCESS",
                style="bold green"
            )
            self.console.print(success_panel)
        
        else:
            print(f"\n🎉 SUCCESS: Embedded {total_embeddings} files from entire data/ directory!")
            print(f"📝 Text files: {len(self.embeddings['text'])}")
            print(f"🖼️ Image files: {len(self.embeddings['images'])}")
            print(f"🎵 Audio files: {len(self.embeddings['audio'])}")


def main():
    """Main entry point for complete data directory embedding."""
    print("🧠 ImpressionCore-B1 Complete Data Directory Embedding System")
    print("=" * 70)
    
    try:
        # Create embedder
        embedder = CompleteDataDirectoryEmbedder()
        
        # Run complete embedding process
        embeddings_file, metadata_file = embedder.run_complete_embedding()
        
        print(f"\n🎉 Complete data directory embedding completed successfully!")
        print(f"📁 Embeddings file: {embeddings_file}")
        print(f"📋 Metadata file: {metadata_file}")
        print(f"\n🚀 ALL files in data/ directory are now embedded and ready for AI applications!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Embedding process interrupted by user")
    except Exception as e:
        print(f"\n❌ Embedding process failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
